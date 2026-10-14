"""Lista doblemente enlazada con nodos expuestos.  [Persona A — entregar temprano]

Usos previstos:
- Inventario (§4.5): recorrer adelante / atrás desde un cursor, quitar el
  objeto que se está viendo en O(1) sin importar su posición, y mover al
  frente en O(1) al equipar.
- Caché LRU de Persona B (§4.4): orden de uso; mover al frente y quitar el
  menos reciente en O(1).
- Enemigos y objetos de una sala: quitar uno cuando se mueve / se recoge.

Las operaciones reciben y devuelven ``NodoDoble`` para que quien guarde el
nodo (p. ej. una TablaHash id → nodo) pueda operar en O(1).
Alternativa a medir con --bench: ``list`` de Python con ``pop(i)`` /
``insert(0, x)``, que cuestan O(n).
"""

from __future__ import annotations

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class NodoDoble(Generic[T]):
    """Nodo de la lista. Quien lo recibe puede guardarlo para operar en O(1)."""

    __slots__ = ("valor", "anterior", "siguiente")

    valor: T
    anterior: NodoDoble[T] | None
    siguiente: NodoDoble[T] | None

    def __init__(self, valor: T) -> None:
        raise NotImplementedError


class ListaDoble(Generic[T]):
    """Lista doblemente enlazada (con o sin centinela: decisión de Persona A)."""

    def __init__(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def esta_vacia(self) -> bool:
        raise NotImplementedError

    @property
    def primero(self) -> NodoDoble[T] | None:
        raise NotImplementedError

    @property
    def ultimo(self) -> NodoDoble[T] | None:
        raise NotImplementedError

    def agregar_al_frente(self, valor: T) -> NodoDoble[T]:
        """O(1). Devuelve el nodo creado."""
        raise NotImplementedError

    def agregar_al_final(self, valor: T) -> NodoDoble[T]:
        """O(1). Devuelve el nodo creado."""
        raise NotImplementedError

    def insertar_despues(self, referencia: NodoDoble[T] | None, valor: T) -> NodoDoble[T]:
        """Inserta ``valor`` justo después de ``referencia`` (None = al frente). O(1).

        Lo necesita el retroceso para devolver un objeto a su posición original.
        """
        raise NotImplementedError

    def quitar(self, nodo: NodoDoble[T]) -> T:
        """Desengancha ``nodo`` en O(1) y devuelve su valor."""
        raise NotImplementedError

    def mover_al_frente(self, nodo: NodoDoble[T]) -> None:
        """O(1). Usado al equipar (§2.7) y por la caché LRU."""
        raise NotImplementedError

    def mover_al_final(self, nodo: NodoDoble[T]) -> None:
        """O(1)."""
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """Recorre del frente al final."""
        raise NotImplementedError

    def iterar_reversa(self) -> Iterator[T]:
        """Recorre del final al frente."""
        raise NotImplementedError

    def a_lista(self) -> list[T]:
        """Copia los valores en orden a una ``list`` (p. ej. para ordenar una vista)."""
        raise NotImplementedError
