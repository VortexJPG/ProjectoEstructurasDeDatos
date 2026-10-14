"""Instancias de objetos y trampas.                                   [Persona A]

La ficha (catálogo) es compartida; la instancia es la que está en el suelo o
en el inventario (§2.7). El contenido del servicio trae los objetos solo como
ids de TIPO, así que el modelo genera los ids de instancia. Deben ser
DETERMINISTAS (mismo id en cada ejecución y en el replay) y no depender del
orden de llegada de las respuestas HTTP.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cripta.modelo.datos import Ficha
    from cripta.modelo.eventos import Evento


class ClaseObjeto(Enum):
    ARMA = "arma"
    ARMADURA = "armadura"
    POCION = "pocion"
    ANTIDOTO = "antidoto"
    LLAVE = "llave"
    ANTORCHA = "antorcha"
    PERGAMINO = "pergamino_retroceso"

    @staticmethod
    def desde_texto(texto: str) -> ClaseObjeto:
        raise NotImplementedError


class InstanciaObjeto:
    """Un objeto concreto. Sus datos (peso, valor, bonos) están en la ficha."""

    __slots__ = ("id", "tipo_id", "clase")

    id: str
    tipo_id: str
    clase: ClaseObjeto

    def __init__(self, id: str, tipo_id: str, clase: ClaseObjeto) -> None:
        raise NotImplementedError

    def es_pergamino(self) -> bool:
        """Los pergaminos quedan FUERA del estado reversible (§2.11)."""
        raise NotImplementedError


class InstanciaTrampa:
    """Trampa colocada en una sala (§2.10)."""

    id: str
    tipo_id: str
    dano: int
    rearme: int  # intervalo de rearme (ficha o 300 por defecto)
    armada: bool
    evento_rearme: Evento | None

    def __init__(self, id: str, ficha: Ficha) -> None:
        raise NotImplementedError


def id_objeto_de_sala(sala_id: int, posicion: int) -> str:
    """Id determinista para el objeto en ``posicion`` del contenido de una sala.

    Ejemplo de formato: "o-2-0". Debe ser imposible que choque con otro id.
    """
    raise NotImplementedError


def id_objeto_soltado(enemigo_id: str, posicion: int) -> str:
    """Id determinista para un objeto que deja un enemigo al morir (campo ``suelta``)."""
    raise NotImplementedError
