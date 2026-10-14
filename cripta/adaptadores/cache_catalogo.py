from __future__ import annotations

from typing import Iterable

from cripta.adaptadores.almacen_disco import AlmacenCatalogo
from cripta.adaptadores.fuente_datos import FuenteDatos
from cripta.estructuras.cola import ColaEnlazada
from cripta.modelo.datos import Ficha
from cripta.modelo.puertos import FichaNoDisponible, ProveedorFichas
from cripta.estructuras.lru import CacheAcotada
from cripta.estructuras.ordenamiento import ordenar


class EstadisticasCache:
    def __init__(self) -> None:
        self.aciertos_memoria = 0
        self.aciertos_disco = 0
        self.fallos_red = 0
        self.desalojos = 0


class CacheCatalogo(ProveedorFichas):
    def __init__(self, fuente: FuenteDatos, almacen: AlmacenCatalogo, capacidad: int) -> None:
        self.fuente = fuente
        self.almacen = almacen
        self._capacidad = capacidad if capacidad > 0 else 1
        self.cache: CacheAcotada[str, Ficha] = CacheAcotada(self._capacidad)
        self.pendientes: set[str] = set()
        self._pendientes_orden: ColaEnlazada[str] = ColaEnlazada()
        self._estadisticas = EstadisticasCache()
        self._pendientes_set: set[str] = self.pendientes

    def validar_version(self, version_catalogo: str) -> None:
        vigente = self.almacen.validar_version(version_catalogo)
        if not vigente:
            # invalidar memoria
            self.cache = CacheAcotada(self._capacidad)
            self.pendientes.clear()
            self._pendientes_orden = ColaEnlazada()

    def registrar_necesarios(self, tipo_ids: Iterable[str]) -> None:
        for tipo_id in tipo_ids:
            if tipo_id in self.cache or self.cache.contiene(tipo_id):
                continue
            if self.almacen.contiene(tipo_id):
                continue
            if tipo_id not in self.pendientes:
                self.pendientes.add(tipo_id)
                self._pendientes_orden.encolar(tipo_id)

    def hay_pendientes(self) -> bool:
        return len(self.pendientes) > 0

    def resolver_pendientes(self) -> None:
        if not self.pendientes:
            return
        pendientes = list(self.pendientes)
        self.pendientes.clear()
        self._pendientes_orden = ColaEnlazada()
        # orden determinista para lotes
        pendientes = ordenar(pendientes)
        tamaño_lote = 10
        for inicio in range(0, len(pendientes), tamaño_lote):
            lote = pendientes[inicio:inicio + tamaño_lote]
            fichas = self.fuente.catalogo(lote)
            for ficha in fichas:
                self.almacen.escribir(ficha)
                self.cache.insertar(ficha.id, ficha)
                self._estadisticas.fallos_red += 1
        # los que no volvieron, re-encolar? asumimos que todos volvieron
        # stats desalojos
        self._estadisticas.desalojos = self.cache.desalojos

    def esta_resuelta(self, tipo_id: str) -> bool:
        return self.cache.contiene(tipo_id) or self.almacen.contiene(tipo_id)

    def estadisticas(self) -> EstadisticasCache:
        return self._estadisticas

    def obtener(self, tipo_id: str) -> Ficha:
        if self.cache.contiene(tipo_id):
            ficha = self.cache.obtener(tipo_id)
            if ficha is not None:
                self._estadisticas.aciertos_memoria += 1
                return ficha
        ficha = self.almacen.leer(tipo_id)
        if ficha is not None:
            self.cache.insertar(ficha.id, ficha)
            self._estadisticas.aciertos_disco += 1
            return ficha
        raise FichaNoDisponible(f"no resuelta: {tipo_id}")

    def fijar(self, tipo_id: str) -> None:
        if not self.cache.contiene(tipo_id):
            ficha = self.almacen.leer(tipo_id)
            if ficha is None:
                raise FichaNoDisponible(tipo_id)
            self.cache.insertar(ficha.id, ficha)
        self.cache.fijar(tipo_id)

    def liberar(self, tipo_id: str) -> None:
        self.cache.liberar(tipo_id)

    def _cargar_de_disco(self, tipo_id: str) -> Ficha | None:
        return self.almacen.leer(tipo_id)

    def _traer_de_red(self, lote: list[str]) -> None:
        self.resolver_pendientes()
