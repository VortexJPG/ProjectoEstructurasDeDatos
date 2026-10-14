from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, List

from cripta.adaptadores.almacen_disco import AlmacenCripta
from cripta.adaptadores.cache_catalogo import CacheCatalogo
from cripta.adaptadores.fuente_datos import FuenteDatos
from cripta.estructuras.cola import ColaEnlazada
from cripta.estructuras.tabla_hash import ConjuntoHash
from cripta.modelo.datos import ContenidoSala


@dataclass(slots=True)
class SolicitudPendiente:
    salas: list[int]
    futuro: object


class PlanificadorPrecarga:
    def __init__(
        self,
        fuente: FuenteDatos,
        cripta_id: str,
        almacen: AlmacenCripta,
        catalogo: CacheCatalogo,
        vecinos: Callable[[int], list[int]],
        incorporar: Callable[[ContenidoSala], None],
    ) -> None:
        self.fuente = fuente
        self.cripta_id = cripta_id
        self.almacen = almacen
        self.catalogo = catalogo
        self.vecinos = vecinos
        self.incorporar = incorporar
        self._solicitadas: ConjuntoHash[int] = ConjuntoHash()
        self._incorporados: ConjuntoHash[int] = ConjuntoHash()
        self._pendientes: list[SolicitudPendiente] = []
        self._executor = ThreadPoolExecutor(max_workers=1)

    def _incorporar_contenido(self, contenidos: list[ContenidoSala]) -> None:
        ids: list[str] = []
        for c in contenidos:
            ids.extend(c.tipos_referenciados())
        self.catalogo.registrar_necesarios(ids)
        self.catalogo.resolver_pendientes()
        for c in contenidos:
            self.incorporar(c)
            self._incorporados.agregar(c.sala)
            self._solicitadas.agregar(c.sala)

    def planificar(self, sala_actual: int) -> None:
        seleccionadas = self._seleccionar_lote(sala_actual)
        if not seleccionadas:
            return
        de_disco = []
        de_red = []
        for sala in seleccionadas:
            if sala in self._solicitadas or sala in self._incorporados:
                continue
            if self.almacen.tiene_contenido(sala):
                de_disco.append(sala)
            else:
                de_red.append(sala)
        if de_disco:
            for sala in de_disco:
                c = self.almacen.cargar_contenido(sala)
                if c is not None:
                    self._incorporar_contenido([c])
        remaining = self.fuente.solicitudes_restantes()
        if de_red:
            if remaining is not None and remaining <= 0:
                return
            lote = de_red[:10]
            self._lanzar_solicitud(lote)
            for sala in lote:
                self._solicitadas.agregar(sala)

    def asegurar(self, sala_id: int) -> None:
        while sala_id not in self._incorporados:
            self.incorporar_disponibles()
            if sala_id in self._incorporados:
                break
            if self._pendientes:
                try:
                    self._pendientes[0].futuro.result()
                except Exception:
                    pass
                self.incorporar_disponibles()
                if sala_id in self._incorporados:
                    break
                continue
            # no hay pendientes: resolver desde disco o red
            if self.almacen.tiene_contenido(sala_id):
                c = self.almacen.cargar_contenido(sala_id)
                if c is not None:
                    self._incorporar_contenido([c])
                    continue
            remaining = self.fuente.solicitudes_restantes()
            if remaining is not None and remaining <= 0:
                # no se puede asegurar por red; esperar no ayuda
                break
            self._lanzar_solicitud([sala_id])
            if self._pendientes:
                try:
                    self._pendientes[-1].futuro.result()
                except Exception:
                    pass
                self.incorporar_disponibles()

    def incorporar_disponibles(self) -> int:
        incorporadas = 0
        while self._pendientes:
            pendiente = self._pendientes[0]
            if not getattr(pendiente.futuro, "done", lambda: True)():
                break
            try:
                resultado = pendiente.futuro.result()
            except Exception:
                self._pendientes.pop(0)
                continue
            if isinstance(resultado, list):
                contenidos = [x for x in resultado if isinstance(x, ContenidoSala)]
                if contenidos:
                    self._incorporar_contenido(contenidos)
                    incorporadas += len(contenidos)
            self._pendientes.pop(0)
        return incorporadas

    def esta_disponible(self, sala_id: int) -> bool:
        return sala_id in self._incorporados

    def cerrar(self) -> None:
        # incorporar lo que quede
        try:
            for p in list(self._pendientes):
                try:
                    p.futuro.result()
                except Exception:
                    pass
            self.incorporar_disponibles()
        finally:
            self._executor.shutdown(wait=True)

    def _seleccionar_lote(self, sala_actual: int) -> list[int]:
        cola: ColaEnlazada[int] = ColaEnlazada()
        cola.encolar(sala_actual)
        visitados: ConjuntoHash[int] = ConjuntoHash()
        visitados.agregar(sala_actual)
        seleccionados: list[int] = []
        while not cola.esta_vacia() and len(seleccionados) < 10:
            actual = cola.desencolar()
            for v in self.vecinos(actual) or []:
                if v in visitados:
                    continue
                visitados.agregar(v)
                if v not in self._solicitadas and v not in self._incorporados:
                    seleccionados.append(v)
                    if len(seleccionados) >= 10:
                        break
                cola.encolar(v)
            if len(seleccionados) >= 10:
                break
        return seleccionados

    def _lanzar_solicitud(self, salas: list[int]) -> None:
        future = self._executor.submit(self.fuente.contenido, self.cripta_id, salas)
        self._pendientes.append(SolicitudPendiente(salas=list(salas), futuro=future))

    def _recuperar_de_disco(self, salas: list[int]) -> list[int]:
        faltantes: list[int] = []
        for sala in salas:
            c = self.almacen.cargar_contenido(sala)
            if c is not None:
                self._incorporar_contenido([c])
            else:
                faltantes.append(sala)
        return faltantes
