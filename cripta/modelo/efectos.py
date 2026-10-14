"""Efectos temporales y del entorno.                                 [Persona A]

§2.10. Cada efecto es un objeto con referencias a SUS eventos en la agenda,
para poder cancelarlo sin recorrer todos los eventos pendientes (§4.1).

| Efecto       | Regla                                                           |
|--------------|-----------------------------------------------------------------|
| Veneno       | daño cada 80; dura 400 desde que se aplica; antídoto lo cancela |
| Velocidad    | cambia la velocidad; al empezar y al terminar se reajusta la    |
|              | próxima acción con la fórmula de §2.3 (secuencia nueva)         |
| Antorcha     | al encenderse programa su apagado tras ``duracion``             |
| Regeneración | el enemigo recupera N cada 200 sin pasar de vida_max            |
| Trampa       | al activarse aplica daño, se desarma y programa su rearme       |
|              | (300 o lo que diga la ficha)                                    |
| Cierre       | puerta con cierre automático programa su cierre al abrirse      |

Pendientes de interpretación (documentarlas): de dónde sale el veneno (el
esquema actual no lo trae) y si ``modificador_velocidad`` es aditivo o
multiplicativo.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cripta.modelo.actores import Actor, Enemigo, Jugador
    from cripta.modelo.eventos import Evento
    from cripta.modelo.juego import Juego
    from cripta.modelo.mapa import Puerta
    from cripta.modelo.objetos import InstanciaTrampa


class TipoEfecto(Enum):
    VENENO = "veneno"
    VELOCIDAD = "velocidad"
    ANTORCHA = "antorcha"
    REGENERACION = "regeneracion"


class Efecto:
    """Efecto activo sobre un actor."""

    tipo: TipoEfecto
    portador: Actor
    inicio: int
    fin: int | None
    magnitud: int  # daño por pulso, cambio de velocidad, vida por pulso...
    evento_pulso: Evento | None
    evento_fin: Evento | None
    activo: bool

    def __init__(self, tipo: TipoEfecto, portador: Actor, inicio: int, fin: int | None, magnitud: int) -> None:
        raise NotImplementedError


class GestorEfectos:
    """Aplica, ejecuta y cancela efectos. Usa reloj, agenda e historial del Juego.

    Toda mutación debe registrarse en el historial (vía ``juego._asignar`` o
    equivalente) para que el retroceso la pueda invertir.
    """

    def __init__(self, juego: Juego) -> None:
        raise NotImplementedError

    # --- veneno -------------------------------------------------------------------

    def aplicar_veneno(self, actor: Actor, dano_por_pulso: int) -> None:
        raise NotImplementedError

    def pulso_veneno(self, efecto: Efecto) -> None:
        """Aplica el daño y programa el siguiente pulso si el efecto sigue activo."""
        raise NotImplementedError

    def cancelar_veneno(self, actor: Actor) -> None:
        """Antídoto: los pulsos futuros cancelados no hacen daño (Apéndice B)."""
        raise NotImplementedError

    # --- velocidad ----------------------------------------------------------------

    def aplicar_velocidad(self, actor: Actor, modificador: int, duracion: int) -> None:
        raise NotImplementedError

    def terminar_velocidad(self, efecto: Efecto) -> None:
        raise NotImplementedError

    def reajustar_turno(self, actor: Actor, velocidad_anterior: int, velocidad_nueva: int) -> None:
        """§2.3: restante_nuevo = max(1, (tiempo_siguiente - t) * v_ant // v_nueva).

        Reprograma ``actor.evento_turno`` con secuencia NUEVA.
        """
        raise NotImplementedError

    # --- antorcha -----------------------------------------------------------------

    def encender_antorcha(self, jugador: Jugador, duracion: int) -> None:
        raise NotImplementedError

    def apagar_antorcha(self, efecto: Efecto) -> None:
        raise NotImplementedError

    # --- regeneración -------------------------------------------------------------

    def iniciar_regeneracion(self, enemigo: Enemigo, cantidad: int) -> None:
        raise NotImplementedError

    def pulso_regeneracion(self, efecto: Efecto) -> None:
        """La vida regenerada nunca supera vida_max (Apéndice B)."""
        raise NotImplementedError

    # --- trampas ------------------------------------------------------------------

    def activar_trampa(self, trampa: InstanciaTrampa, jugador: Jugador) -> None:
        """Al entrar el jugador, inmediatamente tras el movimiento (§2.10)."""
        raise NotImplementedError

    def rearmar_trampa(self, trampa: InstanciaTrampa) -> None:
        raise NotImplementedError

    # --- puertas ------------------------------------------------------------------

    def programar_cierre(self, puerta: Puerta) -> None:
        raise NotImplementedError

    def cerrar_puerta(self, puerta: Puerta) -> None:
        """Si hay un actor del otro lado, se queda ahí (Apéndice B)."""
        raise NotImplementedError

    # --- muerte -------------------------------------------------------------------

    def cancelar_efectos_de(self, actor: Actor) -> None:
        """Cancela todos los efectos del actor (al morir), en O(cantidad de efectos)."""
        raise NotImplementedError
