"""Agenda de eventos: qué ocurre a continuación.                     [Persona A]

§2.3 y §4.1. El juego no tiene rondas: avanza sacando siempre el evento con
menor (tiempo, secuencia). La secuencia es un contador creciente asignado al
PROGRAMAR; toda reprogramación recibe una secuencia nueva.

Requisitos que esta clase debe cumplir:
- Obtener el siguiente evento sin examinar todos (montículo, §4.1).
- Cancelar en O(1) o O(log n) sin recorrer la agenda: muerte de un actor,
  antídoto, fin anticipado de un efecto (§2.10).
- Reprogramar por cambio de velocidad conservando el determinismo (§2.3).
- Poder revertir todo lo anterior (retroceso, §2.11).
"""

from __future__ import annotations

from enum import Enum
from typing import Iterator


class TipoEvento(Enum):
    TURNO_JUGADOR = "turno_jugador"  # punto de decisión del jugador
    TURNO_ENEMIGO = "turno_enemigo"
    PULSO_VENENO = "pulso_veneno"  # cada 80
    FIN_VENENO = "fin_veneno"  # a los 400
    FIN_VELOCIDAD = "fin_velocidad"
    APAGAR_ANTORCHA = "apagar_antorcha"
    PULSO_REGENERACION = "pulso_regeneracion"  # cada 200
    REARME_TRAMPA = "rearme_trampa"
    CIERRE_PUERTA = "cierre_puerta"


class Evento:
    """Un evento programado.

    Es un DATO (tipo + objetivo), no una función o lambda: así se puede
    guardar en el archivo de partida y revertir. ``Juego._despachar`` decide
    qué hacer según ``tipo``.
    """

    __slots__ = ("tiempo", "secuencia", "tipo", "objetivo", "cancelado")

    tiempo: int
    secuencia: int
    tipo: TipoEvento
    objetivo: object  # Actor, Efecto, InstanciaTrampa o Puerta
    cancelado: bool

    def __init__(self, tiempo: int, secuencia: int, tipo: TipoEvento, objetivo: object) -> None:
        raise NotImplementedError

    def __lt__(self, otro: Evento) -> bool:
        """Menor tiempo primero; empate → menor secuencia (§2.3)."""
        raise NotImplementedError


class Agenda:
    """Cola de prioridad de eventos sobre ``MonticuloMin``."""

    def __init__(self) -> None:
        raise NotImplementedError

    @property
    def siguiente_secuencia(self) -> int:
        """Número que recibirá el próximo evento programado."""
        raise NotImplementedError

    def programar(self, tiempo: int, tipo: TipoEvento, objetivo: object) -> Evento:
        """Crea un evento con la siguiente secuencia y lo inserta."""
        raise NotImplementedError

    def cancelar(self, evento: Evento) -> None:
        """Impide que ``evento`` se ejecute, sin recorrer la agenda.

        OJO con el retroceso: si se usa borrado perezoso y un evento cancelado
        ya fue descartado del montículo, "des-cancelarlo" al revertir exige
        volver a insertarlo.
        """
        raise NotImplementedError

    def reprogramar(self, evento: Evento, nuevo_tiempo: int) -> Evento:
        """Cancela ``evento`` y programa uno equivalente en ``nuevo_tiempo``.

        Recibe secuencia NUEVA (§2.3). Devuelve el evento nuevo: quien guardaba
        el anterior (p. ej. ``actor.evento_turno``) debe actualizar la referencia.
        """
        raise NotImplementedError

    def ver_siguiente(self) -> Evento | None:
        """Siguiente evento válido sin quitarlo (descarta cancelados de la cima)."""
        raise NotImplementedError

    def extraer_siguiente(self) -> Evento | None:
        """Quita y devuelve el siguiente evento válido."""
        raise NotImplementedError

    def pendientes(self) -> Iterator[Evento]:
        """Eventos no cancelados, sin orden garantizado (para guardar / --bench)."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Cantidad de eventos NO cancelados."""
        raise NotImplementedError

    # --- soporte para el retroceso (solo lo usa historial.py) ----------------

    def restaurar_extraido(self, evento: Evento) -> None:
        """Devuelve a la agenda un evento ya extraído, con su MISMA secuencia."""
        raise NotImplementedError

    def deshacer_programado(self, evento: Evento) -> None:
        """Anula un evento que se programó dentro del intervalo revertido."""
        raise NotImplementedError

    def establecer_secuencia(self, valor: int) -> None:
        """Restaura el contador de secuencia (retroceso y carga de partida)."""
        raise NotImplementedError
