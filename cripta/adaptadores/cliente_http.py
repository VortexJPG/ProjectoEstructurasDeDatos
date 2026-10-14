from __future__ import annotations

import time
import uuid
from typing import Any

import requests

from cripta.adaptadores.fuente_datos import (
    ErrorFuenteDatos,
    EstadisticasRed,
    FuenteDatos,
    PresupuestoAgotado,
)
from cripta.constantes import TIMEOUT_HTTP_SEGUNDOS
from cripta.modelo.datos import (
    ContenidoSala,
    DatosCripta,
    Ficha,
    PaginaEsqueleto,
    ResumenCripta,
)

BASE_URL = "https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/v1"


class ClienteHTTP(FuenteDatos):
    def __init__(self, base_url: str = BASE_URL, timeout: float = TIMEOUT_HTTP_SEGUNDOS) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client_id = str(uuid.uuid4())
        self._presupuesto: int | None = None
        self._realizadas = 0
        self._cuatrocientos_veintinueve = 0
        self._errores = 0
        self._max_reintentos_429 = 5

    def _url(self, ruta: str) -> str:
        if not ruta.startswith("/"):
            ruta = "/" + ruta
        return self.base_url + ruta

    def _get(self, ruta: str, params: Any = None, operacion: str = "") -> Any:
        if self._presupuesto is not None and self._realizadas >= self._presupuesto:
            raise PresupuestoAgotado(
                operacion, "presupuesto agotado", codigo_http=None
            )
        for intento in range(self._max_reintentos_429 + 1):
            if self._presupuesto is not None and self._realizadas >= self._presupuesto:
                raise PresupuestoAgotado(operacion, "presupuesto agotado")
            self._realizadas += 1
            headers = {"X-Cripta-Client-Id": self.client_id}
            try:
                respuesta = requests.get(
                    self._url(ruta), params=params, headers=headers, timeout=self.timeout
                )
            except requests.RequestException as exc:
                self._errores += 1
                raise ErrorFuenteDatos(operacion, str(exc)) from exc
            if respuesta.status_code == 429:
                self._cuatrocientos_veintinueve += 1
                if intento >= self._max_reintentos_429:
                    self._errores += 1
                    raise ErrorFuenteDatos(
                        operacion, "demasiados 429", respuesta.status_code
                    )
                try:
                    cuerpo = respuesta.json()
                except ValueError:
                    cuerpo = {}
                espera = int(cuerpo.get("reintentar_en", 1)) if isinstance(cuerpo, dict) else 1
                time.sleep(max(0, espera))
                continue
            if respuesta.status_code < 200 or respuesta.status_code >= 300:
                self._errores += 1
                detalle = respuesta.text
                try:
                    detalle = str(respuesta.json())
                except ValueError:
                    pass
                raise ErrorFuenteDatos(operacion, detalle, respuesta.status_code)
            try:
                return respuesta.json()
            except ValueError as exc:
                self._errores += 1
                raise ErrorFuenteDatos(operacion, f"JSON inválido: {exc}") from exc
        raise ErrorFuenteDatos(operacion, "no se pudo completar la solicitud")

    def _esperar_reintento(self, respuesta: Any, operacion: str) -> None:
        try:
            cuerpo = respuesta.json()
            espera = int(cuerpo.get("reintentar_en", 1))
        except Exception:
            espera = 1
        time.sleep(max(0, espera))

    def _extraer_version(self, datos: Any) -> str:
        if isinstance(datos, dict):
            for clave in ("version", "version_catalogo", "version_cripta"):
                if clave in datos:
                    return str(datos[clave])
            if len(datos) == 1:
                return str(next(iter(datos.values())))
        return str(datos)

    def _lista(self, datos: Any, clave: str) -> list[Any]:
        if isinstance(datos, list):
            return datos
        if isinstance(datos, dict):
            if clave in datos and isinstance(datos[clave], list):
                return datos[clave]
            # buscar primer valor lista
            for valor in datos.values():
                if isinstance(valor, list):
                    return valor
        return []

    def listar_criptas(self) -> list[ResumenCripta]:
        datos = self._get("/criptas", None, "listar_criptas")
        return [ResumenCripta.desde_json(x) for x in self._lista(datos, "criptas")]

    def datos_cripta(self, cripta_id: str) -> DatosCripta:
        datos = self._get(f"/criptas/{cripta_id}", None, "datos_cripta")
        return DatosCripta.desde_json(datos)

    def pagina_esqueleto(self, cripta_id: str, pagina: int) -> PaginaEsqueleto:
        datos = self._get(f"/criptas/{cripta_id}/salas", {"pagina": pagina}, "pagina_esqueleto")
        return PaginaEsqueleto.desde_json(datos)

    def contenido(self, cripta_id: str, salas: list[int]) -> list[ContenidoSala]:
        params = {"salas": ",".join(str(x) for x in salas)}
        datos = self._get(f"/criptas/{cripta_id}/contenido", params, "contenido")
        return [ContenidoSala.desde_json(x) for x in self._lista(datos, "contenido")]

    def catalogo(self, ids: list[str]) -> list[Ficha]:
        params = {"ids": ",".join(ids)}
        datos = self._get("/catalogo", params, "catalogo")
        return [Ficha.desde_json(x) for x in self._lista(datos, "entidades")]

    def version_cripta(self, cripta_id: str) -> str:
        datos = self._get(f"/criptas/{cripta_id}/version", None, "version_cripta")
        return self._extraer_version(datos)

    def version_catalogo(self) -> str:
        datos = self._get("/catalogo/version", None, "version_catalogo")
        return self._extraer_version(datos)

    def establecer_presupuesto(self, presupuesto: int) -> None:
        self._presupuesto = presupuesto

    def solicitudes_restantes(self) -> int | None:
        if self._presupuesto is None:
            return None
        return self._presupuesto - self._realizadas

    def estadisticas(self) -> EstadisticasRed:
        return EstadisticasRed(
            solicitudes_realizadas=self._realizadas,
            presupuesto=self._presupuesto,
            respuestas_429=self._cuatrocientos_veintinueve,
            errores=self._errores,
        )
