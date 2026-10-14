from __future__ import annotations

from cripta.adaptadores.bitacora_replay import LectorReplay, ErrorReplayIncompatible
from cripta.adaptadores.fuente_datos import ErrorFuenteDatos
from cripta.controlador.controlador import Controlador, OpcionesEjecucion


class ReproductorReplay:
    def __init__(self, ruta_log: str, fuente, opciones: OpcionesEjecucion) -> None:
        self.ruta_log = ruta_log
        self.fuente = fuente
        self.opciones = opciones
        self._lector = LectorReplay(ruta_log)
        encabezado = self._lector.encabezado()
        self._encabezado = encabezado
        self._controlador = Controlador(fuente, opciones, None)

    def verificar_compatibilidad(self, encabezado) -> None:
        # versiones disponibles desde la fuente
        try:
            version_cripta = self.fuente.version_cripta(encabezado.cripta_id)
        except Exception as exc:
            raise ErrorReplayIncompatible(f"no se pudo verificar versión de cripta: {exc}")
        try:
            version_catalogo = self.fuente.version_catalogo()
        except Exception as exc:
            raise ErrorReplayIncompatible(f"no se pudo verificar versión de catálogo: {exc}")
        if version_cripta != encabezado.version_cripta:
            raise ErrorReplayIncompatible(
                f"versión de cripta incompatible: log={encabezado.version_cripta}, disponible={version_cripta}"
            )
        if version_catalogo != encabezado.version_catalogo:
            raise ErrorReplayIncompatible(
                f"versión de catálogo incompatible: log={encabezado.version_catalogo}, disponible={version_catalogo}"
            )

    def ejecutar(self):
        encabezado = self._encabezado
        self.verificar_compatibilidad(encabezado)
        self._controlador.preparar_cripta(encabezado.cripta_id)
        self._controlador.iniciar_partida(encabezado.nombre_jugador, encabezado.semilla, False)
        for accion in self._lector.acciones():
            self._controlador.ejecutar_accion(accion)
        juego = self._controlador._juego
        return juego.resumen() if juego is not None else None
