"""Buffer circular de capacidad fija.                                [Persona A]

Usos previstos:
- Bitácora en pantalla (§4.8): últimos 20 mensajes, memoria constante, y
  agregar sin desplazar físicamente los anteriores (se sobrescribe la ranura
  del más antiguo).
- Historial de retroceso (§4.6): últimos 5 intervalos. Al superar el límite
  se descarta el más antiguo, y deshacer saca el más reciente (pila acotada).

Alternativa a medir con --bench: ``list`` con ``append`` + ``pop(0)``.
"""

from __future__ import annotations

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class BufferCircular(Generic[T]):
    """Arreglo de tamaño fijo con índices que dan la vuelta (módulo capacidad)."""

    def __init__(self, capacidad: int) -> None:
        raise NotImplementedError

    @property
    def capacidad(self) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def esta_lleno(self) -> bool:
        raise NotImplementedError

    def esta_vacio(self) -> bool:
        raise NotImplementedError

    def agregar(self, elemento: T) -> T | None:
        """Agrega al extremo reciente. O(1).

        Si estaba lleno, sobrescribe el más antiguo y lo devuelve (si no, None).
        """
        raise NotImplementedError

    def extraer_reciente(self) -> T | None:
        """Quita y devuelve el elemento más reciente (None si está vacío). O(1)."""
        raise NotImplementedError

    def ver_reciente(self) -> T | None:
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """Recorre del más antiguo al más reciente."""
        raise NotImplementedError

    def limpiar(self) -> None:
        raise NotImplementedError
