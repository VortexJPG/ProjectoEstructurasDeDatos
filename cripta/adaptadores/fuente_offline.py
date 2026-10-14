from __future__ import annotations

import glob
import json
import os
from typing import Any

from cripta.adaptadores.fuente_datos import (
    ErrorFuenteDatos,
    EstadisticasRed,
    FuenteDatos,
)
from cripta.modelo.datos import (
    ContenidoSala,
    DatosCripta,
    Ficha,
    PaginaEsqueleto,
    ResumenCripta,
)


class FuenteOffline(FuenteDatos):
    def __init__(self, directorio: str) -> None:
        self.directorio = directorio
        self._presupuesto: int | None = None

    def _leer_json(self, ruta: str, operacion: str) -> Any:
        if not os.path.exists(ruta):
            raise ErrorFuenteDatos(operacion, f"archivo no encontrado: {ruta}")
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise ErrorFuenteDatos(operacion, str(exc)) from exc

    def _encontrar_archivo(self, nombre: str) -> str | None:
        # busca en directorio y subdirectorios de primer nivel
        candidatos = [os.path.join(self.directorio, nombre)]
        try:
            for entrada in os.listdir(self.directorio):
                sub = os.path.join(self.directorio, entrada)
                if os.path.isdir(sub):
                    candidatos.append(os.path.join(sub, nombre))
        except OSError:
            pass
        for ruta in candidatos:
            if os.path.exists(ruta):
                return ruta
        # búsqueda glob recursiva
        for ruta in glob.glob(os.path.join(self.directorio, "**", nombre), recursive=True):
            return ruta
        return None

    def _ruta_para(self, operacion: str, *argumentos: Any) -> str:
        # genérico: primer argumento puede ser nombre de archivo
        if argumentos and isinstance(argumentos[0], str) and os.path.exists(argumentos[0]):
            return argumentos[0]
        raise ErrorFuenteDatos(operacion, "ruta no resuelta")

    def _directorios_cripta(self, cripta_id: str) -> list[str]:
        bases = [self.directorio, os.path.join(self.directorio, cripta_id)]
        # subdirs que contienen la cripta
        try:
            for entrada in os.listdir(self.directorio):
                sub = os.path.join(self.directorio, entrada)
                if os.path.isdir(sub):
                    bases.append(sub)
        except OSError:
            pass
        return bases

    def listar_criptas(self) -> list[ResumenCripta]:
        ruta = self._encontrar_archivo("criptas.json")
        if ruta is None:
            raise ErrorFuenteDatos("listar_criptas", "no se encontró criptas.json")
        datos = self._leer_json(ruta, "listar_criptas")
        items = datos.get("criptas", datos) if isinstance(datos, dict) else datos
        return [ResumenCripta.desde_json(x) for x in (items or [])]

    def datos_cripta(self, cripta_id: str) -> DatosCripta:
        for base in self._directorios_cripta(cripta_id):
            ruta = os.path.join(base, "cripta.json")
            if os.path.exists(ruta):
                datos = self._leer_json(ruta, "datos_cripta")
                if isinstance(datos, dict) and datos.get("id") in (None, cripta_id):
                    return DatosCripta.desde_json(datos)
        # buscar cualquier cripta.json
        for ruta in glob.glob(os.path.join(self.directorio, "**", "cripta.json"), recursive=True):
            datos = self._leer_json(ruta, "datos_cripta")
            if isinstance(datos, dict) and datos.get("id") == cripta_id:
                return DatosCripta.desde_json(datos)
        raise ErrorFuenteDatos("datos_cripta", f"no se encontró cripta.json para {cripta_id}")

    def pagina_esqueleto(self, cripta_id: str, pagina: int) -> PaginaEsqueleto:
        patrones = [f"salas_pagina_{pagina}.json", f"salas_pagina_{pagina}.json"]
        for base in self._directorios_cripta(cripta_id):
            for nombre in patrones:
                ruta = os.path.join(base, nombre)
                if os.path.exists(ruta):
                    return PaginaEsqueleto.desde_json(self._leer_json(ruta, "pagina_esqueleto"))
        for ruta in glob.glob(os.path.join(self.directorio, "**", f"salas_pagina_{pagina}.json"), recursive=True):
            return PaginaEsqueleto.desde_json(self._leer_json(ruta, "pagina_esqueleto"))
        raise ErrorFuenteDatos("pagina_esqueleto", f"no se encontró página {pagina}")

    def _cargar_contenido_todo(self, cripta_id: str) -> list[ContenidoSala]:
        archivos = []
        for base in self._directorios_cripta(cripta_id):
            archivos.extend(glob.glob(os.path.join(base, "contenido*.json")))
        if not archivos:
            archivos = glob.glob(os.path.join(self.directorio, "**", "contenido*.json"), recursive=True)
        resultado: list[ContenidoSala] = []
        vistos: set[int] = set()
        for ruta in archivos:
            datos = self._leer_json(ruta, "contenido")
            items = datos.get("contenido", datos) if isinstance(datos, dict) else datos
            for item in items or []:
                cs = ContenidoSala.desde_json(item)
                if cs.sala not in vistos:
                    vistos.add(cs.sala)
                    resultado.append(cs)
        return resultado

    def contenido(self, cripta_id: str, salas: list[int]) -> list[ContenidoSala]:
        todos = self._cargar_contenido_todo(cripta_id)
        por_sala = {c.sala: c for c in todos}
        salida = []
        for sala in salas:
            if sala in por_sala:
                salida.append(por_sala[sala])
        return salida

    def _cargar_catalogo_todo(self) -> list[Ficha]:
        archivos = []
        archivos.extend(glob.glob(os.path.join(self.directorio, "catalogo*.json")))
        archivos.extend(glob.glob(os.path.join(self.directorio, "**", "catalogo*.json"), recursive=True))
        # dedup preserving order
        vistos_rutas: set[str] = set()
        unicos = []
        for r in archivos:
            if r in vistos_rutas:
                continue
            vistos_rutas.add(r)
            unicos.append(r)
        entidades: list[dict[str, Any]] = []
        for ruta in unicos:
            if "version" in os.path.basename(ruta):
                continue
            datos = self._leer_json(ruta, "catalogo")
            items = datos.get("entidades", datos) if isinstance(datos, dict) else datos
            for item in items or []:
                if isinstance(item, dict) and "id" in item and "clase" in item:
                    entidades.append(item)
        # dedup por id
        ids_vistos: set[str] = set()
        salida: list[Ficha] = []
        for ent in entidades:
            if ent["id"] in ids_vistos:
                continue
            ids_vistos.add(ent["id"])
            salida.append(Ficha.desde_json(ent))
        return salida

    def catalogo(self, ids: list[str]) -> list[Ficha]:
        todas = self._cargar_catalogo_todo()
        por_id = {f.id: f for f in todas}
        salida = []
        for ident in ids:
            if ident in por_id:
                salida.append(por_id[ident])
        return salida

    def version_cripta(self, cripta_id: str) -> str:
        try:
            return self.datos_cripta(cripta_id).version
        except Exception as exc:
            raise ErrorFuenteDatos("version_cripta", str(exc))

    def version_catalogo(self) -> str:
        ruta = self._encontrar_archivo("catalogo_version.json")
        if ruta is None:
            raise ErrorFuenteDatos("version_catalogo", "no se encontró catalogo_version.json")
        datos = self._leer_json(ruta, "version_catalogo")
        if isinstance(datos, dict):
            return str(datos.get("version", datos.get("catalogo_version", "")))
        return str(datos)

    def establecer_presupuesto(self, presupuesto: int) -> None:
        self._presupuesto = presupuesto

    def solicitudes_restantes(self) -> int | None:
        if self._presupuesto is None:
            return None
        return self._presupuesto

    def estadisticas(self) -> EstadisticasRed:
        return EstadisticasRed(solicitudes_realizadas=0, presupuesto=self._presupuesto)
