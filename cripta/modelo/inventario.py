"""Inventario del jugador.                                           [Persona A]

§2.7 y §4.5:
- Recorrer hacia adelante y hacia atrás desde la posición actual (cursor).
- Soltar el objeto que se está viendo, en cualquier posición, sin que el costo
  dependa de la posición.
- Equipar mueve el objeto al FRENTE del orden real.
- Vistas ordenadas por peso, valor o nombre SIN alterar el orden real
  (usar ``estructuras.ordenamiento.ordenar`` de Persona B).
- Con ``inventario_max`` objetos, recoger queda prohibido.

Diseño sugerido: ``ListaDoble`` (orden real) + ``TablaHash`` id → nodo
(quitar / mover por id en O(1), necesario porque el replay identifica objetos
por id) + un nodo cursor.

Retroceso: para devolver un objeto a su posición original hay que registrar
quién estaba antes (``anterior_de``) y luego ``insertar_despues``. Cuidado si
ese vecino era un pergamino (los pergaminos no se revierten).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterator

if TYPE_CHECKING:
    from cripta.modelo.objetos import ClaseObjeto, InstanciaObjeto


class Inventario:
    """Orden real + cursor + índice por id."""

    def __init__(self, capacidad: int) -> None:
        """``capacidad`` = ``inventario_max`` de los datos de la cripta."""
        raise NotImplementedError

    @property
    def capacidad(self) -> int:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def esta_lleno(self) -> bool:
        raise NotImplementedError

    def __iter__(self) -> Iterator[InstanciaObjeto]:
        """Recorre en el orden real (frente → final)."""
        raise NotImplementedError

    # --- operaciones del juego -------------------------------------------------

    def agregar(self, objeto: InstanciaObjeto) -> None:
        """Agrega al final del orden real. ValueError si está lleno."""
        raise NotImplementedError

    def quitar(self, instancia_id: str) -> InstanciaObjeto:
        """Quita por id en O(1). Si era el del cursor, el cursor se mueve a un vecino."""
        raise NotImplementedError

    def contiene(self, instancia_id: str) -> bool:
        raise NotImplementedError

    def obtener(self, instancia_id: str) -> InstanciaObjeto | None:
        raise NotImplementedError

    def mover_al_frente(self, instancia_id: str) -> None:
        """O(1). Lo usa ``equipar`` (§2.7)."""
        raise NotImplementedError

    def buscar_por_tipo(self, tipo_id: str) -> InstanciaObjeto | None:
        """Primer objeto de ese tipo (p. ej. para saber si hay cierta llave)."""
        raise NotImplementedError

    def contar_clase(self, clase: ClaseObjeto) -> int:
        """Cuántos objetos de esa clase hay (p. ej. pergaminos disponibles)."""
        raise NotImplementedError

    # --- cursor (lo usa la vista) ------------------------------------------------

    def actual(self) -> InstanciaObjeto | None:
        """Objeto que se está viendo."""
        raise NotImplementedError

    def avanzar(self) -> InstanciaObjeto | None:
        raise NotImplementedError

    def retroceder(self) -> InstanciaObjeto | None:
        raise NotImplementedError

    def ir_a(self, instancia_id: str) -> None:
        raise NotImplementedError

    # --- vistas ------------------------------------------------------------------

    def vista_ordenada(
        self,
        clave: Callable[[InstanciaObjeto], Any],
        descendente: bool = False,
    ) -> list[InstanciaObjeto]:
        """Lista NUEVA ordenada con ``ordenamiento.ordenar``; el orden real no cambia.

        La ``clave`` la arma quien llama (necesita las fichas para peso / valor /
        nombre).
        """
        raise NotImplementedError

    # --- soporte para el retroceso -------------------------------------------------

    def anterior_de(self, instancia_id: str) -> str | None:
        """Id del objeto inmediatamente anterior en el orden real (None si es el primero)."""
        raise NotImplementedError

    def insertar_despues(self, anterior_id: str | None, objeto: InstanciaObjeto) -> None:
        """Reinserta ``objeto`` justo después de ``anterior_id`` (None = al frente)."""
        raise NotImplementedError
