"""Historial reversible para los pergaminos de retroceso.            [Persona A]

§2.11 y §4.6. PROHIBIDO guardar copias completas del estado. Se registra solo
lo necesario para INVERTIR cada cambio (patrón "bitácora de deshacer").

Un ``IntervaloReversible`` cubre desde justo antes de una acción del jugador
hasta su siguiente decisión: la acción, las acciones enemigas, los efectos, el
reloj, los eventos programados / extraídos / cancelados, rastro, vidas,
inventario, suelo, puertas, trampas... Revertir = deshacer sus cambios en
orden INVERSO.

Exclusiones obligatorias:
- La cantidad de pergaminos no se registra ni se restaura (en ninguno de los
  dos sentidos: ni el usado, ni los recogidos / soltados en el intervalo).
- La caché de catálogo es infraestructura, no juego: no se revierte.

Máximo 5 intervalos; al superar el límite se descarta el más antiguo
(``BufferCircular``). Dos pergaminos seguidos revierten dos intervalos.

Decisión a documentar: el estado del generador ``random.Random`` también
cambia dentro del intervalo; si se restaura (``getstate`` al abrir el
intervalo) repetir la misma acción da el mismo resultado.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cripta.modelo.acciones import Accion
    from cripta.modelo.actores import Enemigo
    from cripta.modelo.eventos import Evento
    from cripta.modelo.juego import Juego
    from cripta.modelo.mapa import Sala
    from cripta.modelo.objetos import InstanciaObjeto


class Cambio(ABC):
    """Un cambio atómico que sabe deshacerse."""

    @abstractmethod
    def revertir(self, juego: Juego) -> None:
        """Deja el estado como estaba antes de este cambio."""


class CambioAtributo(Cambio):
    """Genérico: ``objeto.atributo`` valía ``valor_anterior``.

    Cubre la mayoría de los casos: vida, reloj, rastro, ``puerta.cerrada``,
    ``trampa.armada``, ``tiempo_siguiente``, ``evento.cancelado``, contadores...
    """

    def __init__(self, objeto: object, atributo: str, valor_anterior: Any) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class CambioEventoProgramado(Cambio):
    """Se programó ``evento``; revertir lo anula (``Agenda.deshacer_programado``)."""

    def __init__(self, evento: Evento) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class CambioEventoExtraido(Cambio):
    """Se ejecutó ``evento``; revertir lo devuelve a la agenda con su misma secuencia."""

    def __init__(self, evento: Evento) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class CambioInventario(Cambio):
    """Un objeto entró, salió o se movió al frente del inventario.

    ``anterior_id`` = objeto que estaba antes de él (para restaurar la posición).
    """

    def __init__(self, objeto: InstanciaObjeto, operacion: str, anterior_id: str | None) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class CambioSuelo(Cambio):
    """Un objeto se agregó o se quitó del suelo de ``sala``."""

    def __init__(self, sala: Sala, objeto: InstanciaObjeto, agregado: bool) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class CambioUbicacionEnemigo(Cambio):
    """``enemigo`` se movió desde ``sala_anterior`` (o murió y salió de la lista)."""

    def __init__(self, enemigo: Enemigo, sala_anterior: Sala) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class CambioEstadoAzar(Cambio):
    """Estado de ``juego.azar`` al abrir el intervalo (si deciden restaurarlo)."""

    def __init__(self, estado: tuple) -> None:
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        raise NotImplementedError


class IntervaloReversible:
    """Cambios entre una decisión del jugador y la siguiente."""

    accion: Accion

    def __init__(self, accion: Accion) -> None:
        raise NotImplementedError

    def registrar(self, cambio: Cambio) -> None:
        """Apila el cambio. O(1)."""
        raise NotImplementedError

    def revertir(self, juego: Juego) -> None:
        """Deshace todos los cambios del más reciente al más antiguo."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class Historial:
    """Últimos 5 intervalos reversibles."""

    def __init__(self, maximo: int) -> None:
        """``maximo`` = constantes.MAX_ACCIONES_REVERSIBLES."""
        raise NotImplementedError

    @property
    def grabando(self) -> bool:
        """True si hay un intervalo abierto y no se está revirtiendo."""
        raise NotImplementedError

    def abrir_intervalo(self, accion: Accion) -> None:
        raise NotImplementedError

    def registrar(self, cambio: Cambio) -> None:
        """Agrega al intervalo abierto. Ignora si no se está grabando (p. ej. al revertir)."""
        raise NotImplementedError

    def cerrar_intervalo(self) -> None:
        """Guarda el intervalo; si ya hay 5, se descarta el más antiguo."""
        raise NotImplementedError

    def puede_retroceder(self) -> bool:
        raise NotImplementedError

    def retroceder(self, juego: Juego) -> bool:
        """Revierte el intervalo más reciente. False si no hay ninguno."""
        raise NotImplementedError

    def vaciar(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
