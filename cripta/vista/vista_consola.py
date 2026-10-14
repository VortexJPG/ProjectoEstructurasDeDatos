"""Interfaz de consola.                                              [Persona A]

§10.2: debe permitir seleccionar cripta, moverse en 4 direcciones, abrir
puertas, atacar a un enemigo elegido, esperar, recoger / usar / equipar /
soltar, recorrer el inventario (también ordenado), usar pergamino, guardar,
cargar y salir. Debe mostrar: sala actual, salidas, enemigos (identificables:
"Rata gigante #1"), objetos del suelo, vida y estadísticas, efectos activos y
los últimos 20 mensajes.

La vista traduce lo que ve el usuario ("atacar 2") a ids de instancia reales
("e-202") ANTES de entregarlo: así el replay no depende de la pantalla.
Para mostrar nombres, peso, valor, etc. usa ``juego.fichas.obtener``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cripta.adaptadores.puntajes import RegistroPuntaje
    from cripta.controlador.comandos import ComandoUsuario
    from cripta.modelo.acciones import ResultadoAccion
    from cripta.modelo.datos import ResumenCripta
    from cripta.modelo.juego import Juego
    from cripta.modelo.objetos import InstanciaObjeto


class VistaConsola:
    def __init__(self) -> None:
        raise NotImplementedError

    # --- entrada ------------------------------------------------------------------

    def elegir_cripta(self, criptas: list[ResumenCripta]) -> str:
        """Devuelve el id de la cripta elegida."""
        raise NotImplementedError

    def pedir_nombre(self) -> str:
        raise NotImplementedError

    def pedir_comando(self, juego: Juego) -> ComandoUsuario:
        """Lee una línea y la convierte en comando; repite si no se entiende."""
        raise NotImplementedError

    def _interpretar(self, texto: str, juego: Juego) -> ComandoUsuario | None:
        """Texto → ComandoUsuario (None si no es válido)."""
        raise NotImplementedError

    # --- salida -------------------------------------------------------------------

    def mostrar_estado(self, juego: Juego) -> None:
        """Sala, salidas, enemigos, suelo, jugador, efectos y mensajes."""
        raise NotImplementedError

    def mostrar_inventario(self, juego: Juego, vista: list[InstanciaObjeto] | None = None, criterio: str | None = None) -> None:
        """Orden real con el cursor marcado, o una vista ordenada si se pasa."""
        raise NotImplementedError

    def mostrar_resultado(self, resultado: ResultadoAccion) -> None:
        raise NotImplementedError

    def mostrar_info(self, texto: str) -> None:
        raise NotImplementedError

    def mostrar_error(self, texto: str) -> None:
        raise NotImplementedError

    def mostrar_ayuda(self) -> None:
        raise NotImplementedError

    def mostrar_fin(self, juego: Juego, reporte_red: str) -> None:
        raise NotImplementedError

    def mostrar_puntajes(self, registros: list[RegistroPuntaje]) -> None:
        raise NotImplementedError
