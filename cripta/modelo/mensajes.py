"""Bitácora de mensajes en pantalla.                                 [Persona A]

§4.8: la interfaz muestra solo los últimos 20 mensajes; la memoria debe ser
constante y agregar un mensaje no puede desplazar los 19 anteriores.
Implementar sobre ``BufferCircular``.

El modelo escribe aquí ("Rata gigante #1 te ataca: -4") y la vista solo lee.
"""

from __future__ import annotations

from typing import Iterator


class BitacoraMensajes:
    def __init__(self, capacidad: int) -> None:
        """``capacidad`` = constantes.MENSAJES_VISIBLES."""
        raise NotImplementedError

    def agregar(self, tiempo: int, texto: str) -> None:
        """O(1); sobrescribe el más antiguo si está llena."""
        raise NotImplementedError

    def ultimos(self) -> Iterator[tuple[int, str]]:
        """Pares (tiempo, texto) del más antiguo al más reciente."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
