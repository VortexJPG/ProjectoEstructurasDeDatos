"""Comportamiento de los enemigos.                                   [Persona A]

§2.8: en su turno, si el enemigo comparte sala con el jugador, ataca y no se
mueve. Si no:
- Guardián: espera; nunca abandona su sala.
- Errante: elige al azar una salida abierta y transitable; si no hay, espera.
- Rastreador: mira SOLO las salas vecinas por salidas abiertas y va a la de
  rastro más fresco con antigüedad < 400; empate → menor id de sala; si no
  hay, espera. No conoce el mapa ni busca rutas (§2.9).
Atacar, moverse y esperar cuestan 100.

Determinismo: el errante debe armar sus candidatas SIEMPRE en el orden
N, S, E, O y usar ``juego.azar`` (nunca el ``random`` global).

§4.7: la decisión del rastreador cuesta O(salidas de su sala), no O(tamaño de
la cripta) ni O(recorrido del jugador).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cripta.modelo.actores import Enemigo
    from cripta.modelo.juego import Juego
    from cripta.modelo.mapa import Sala


class IAEnemigos:
    def __init__(self, juego: Juego) -> None:
        raise NotImplementedError

    def actuar(self, enemigo: Enemigo) -> None:
        """Ejecuta el turno completo de ``enemigo`` y programa el siguiente."""
        raise NotImplementedError

    def _actuar_guardian(self, enemigo: Enemigo) -> None:
        raise NotImplementedError

    def _actuar_errante(self, enemigo: Enemigo) -> None:
        raise NotImplementedError

    def _actuar_rastreador(self, enemigo: Enemigo) -> None:
        raise NotImplementedError

    def elegir_sala_por_rastro(self, sala: Sala, reloj: int) -> Sala | None:
        """Vecina accesible con el rastro vigente más fresco, o None. O(grado)."""
        raise NotImplementedError
