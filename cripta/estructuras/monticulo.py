"""Montículo binario mínimo.                    [Persona A — entregar temprano]

Base de la agenda de eventos (§4.1): obtener el evento con menor
(tiempo, secuencia) sin examinar todos los eventos. Almacenamiento en
``list`` (permitido por §7): hijos de i en 2i+1 y 2i+2, padre en (i-1)//2.

Los elementos se comparan con ``<``; ``Evento`` define ``__lt__`` por
(tiempo, secuencia), lo que da un orden total y determinista.

Decisión a tomar y justificar (Documento §4.1): cómo soportar cancelación
(muerte de un actor, antídoto) y reprogramación (cambio de velocidad):
  a) Borrado perezoso: marcar el evento como cancelado y descartarlo cuando
     llegue a la cima. Simple; el montículo puede acumular basura.
  b) Montículo indexado: cada elemento conoce su posición y se puede quitar o
     actualizar en O(log n). Más trabajo; sin basura.
``eliminar_en`` y ``actualizar_en`` solo hacen falta con la opción b.
Alternativa a medir con --bench: lista sin ordenar con búsqueda lineal del
mínimo (lo que §4.1 prohíbe hacer en el juego, pero sirve como contraste).
"""

from __future__ import annotations

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class MonticuloMin(Generic[T]):
    """Montículo binario de mínimos sobre una ``list``."""

    def __init__(self) -> None:
        raise NotImplementedError

    def insertar(self, elemento: T) -> None:
        """Agrega ``elemento`` y lo sube a su lugar. O(log n)."""
        raise NotImplementedError

    def extraer_min(self) -> T:
        """Quita y devuelve el mínimo. O(log n). IndexError si está vacío."""
        raise NotImplementedError

    def ver_min(self) -> T | None:
        """Devuelve el mínimo sin quitarlo (None si está vacío). O(1)."""
        raise NotImplementedError

    def esta_vacio(self) -> bool:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def elementos(self) -> Iterator[T]:
        """Itera los elementos en el orden interno del arreglo (NO ordenado).

        Útil para guardar la partida y para --bench.
        """
        raise NotImplementedError

    # --- solo si eligen montículo indexado (opción b) ------------------------

    def eliminar_en(self, posicion: int) -> T:
        """Quita el elemento en ``posicion`` y restaura la propiedad de montículo."""
        raise NotImplementedError

    def actualizar_en(self, posicion: int) -> None:
        """Reubica el elemento en ``posicion`` después de que cambió su clave."""
        raise NotImplementedError

    # --- internos -------------------------------------------------------------

    def _subir(self, posicion: int) -> None:
        raise NotImplementedError

    def _bajar(self, posicion: int) -> None:
        raise NotImplementedError

    def _intercambiar(self, i: int, j: int) -> None:
        """Intercambia dos posiciones (y actualiza índices si es montículo indexado)."""
        raise NotImplementedError
