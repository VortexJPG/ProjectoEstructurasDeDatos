"""Mapa de la cripta: salas, salidas, puertas y rastro.              [Persona A]

Se construye con el esqueleto completo (§3.2) y se completa sala por sala a
medida que llega el contenido (``incorporar_contenido``).

Decisión pendiente: el API declara salidas DIRIGIDAS y a veces solo un lado
trae ``cerrada`` / ``llave`` (cripta-01: 2 →E→ 5 cerrada, 5 →O→ 2 abierta).
¿Una ``Puerta`` compartida por los dos sentidos o una por salida? La
recomendación es compartida (abrir / cerrar afecta a ambos lados; Apéndice B:
"solo se impide atravesar de nuevo hasta abrir"). Documentar la decisión.

Rastro (§2.9, §4.7): cada sala guarda el instante en que el jugador estuvo
ahí por última vez. Decidan si un rastro viejo (>= 400) se elimina
activamente o se detecta al consultarlo; justificarlo en el Documento.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from cripta.estructuras.lista_doble import ListaDoble
    from cripta.estructuras.tabla_hash import TablaHash
    from cripta.modelo.actores import Enemigo
    from cripta.modelo.datos import ContenidoSala, DatosCripta, DatosSala
    from cripta.modelo.eventos import Evento
    from cripta.modelo.objetos import InstanciaObjeto, InstanciaTrampa
    from cripta.modelo.puertos import ProveedorFichas


class Puerta:
    """Estado VIVO de una puerta (el esqueleto solo trae el estado inicial)."""

    id: str
    cerrada: bool
    llave: str | None  # id de tipo de la llave que la abre
    cierre_automatico: int | None  # unidades hasta cerrarse tras abrirla
    evento_cierre: Evento | None

    def __init__(self, id: str, cerrada: bool, llave: str | None, cierre_automatico: int | None) -> None:
        raise NotImplementedError


class Salida:
    """Salida de una sala en una dirección."""

    direccion: str
    destino: Sala
    puerta: Puerta | None  # None = paso libre, nunca se cierra

    def __init__(self, direccion: str, destino: Sala, puerta: Puerta | None) -> None:
        raise NotImplementedError

    def es_transitable(self) -> bool:
        """True si no hay puerta o está abierta."""
        raise NotImplementedError


class Sala:
    """Una sala. Los actores ocupan la sala completa (no hay cuadrícula)."""

    id: int
    nombre: str
    salidas: list[Salida | None]  # 4 posiciones, índice = indice_direccion()
    rastro: int | None  # último instante en que el jugador estuvo aquí
    contenido_cargado: bool
    visitada: bool  # el jugador ya entró (sus enemigos dormidos se activaron)
    enemigos: ListaDoble[Enemigo]  # dormidos y activos que están aquí
    objetos_suelo: ListaDoble[InstanciaObjeto]
    trampas: list[InstanciaTrampa]

    def __init__(self, id: int, nombre: str) -> None:
        raise NotImplementedError

    def salida(self, direccion: str) -> Salida | None:
        """Salida en ``direccion`` o None. O(1)."""
        raise NotImplementedError

    def salidas_transitables(self) -> Iterator[Salida]:
        """Salidas abiertas, SIEMPRE en el orden N, S, E, O (determinismo)."""
        raise NotImplementedError

    def rastro_vigente(self, reloj: int) -> bool:
        """True si hay rastro con antigüedad < 400 (§2.9)."""
        raise NotImplementedError

    def enemigos_dormidos(self) -> list[Enemigo]:
        """Enemigos sin activar de esta sala (para activarlos al entrar el jugador)."""
        raise NotImplementedError


class Mapa:
    """Todas las salas, indexadas por id con una TablaHash (no dict, §7)."""

    salas: TablaHash[int, Sala]
    sala_inicial: Sala
    sala_salida: Sala
    llave_salida: str

    def __init__(self) -> None:
        raise NotImplementedError

    @staticmethod
    def construir(datos: DatosCripta, salas: list[DatosSala]) -> Mapa:
        """Crea todas las salas y salidas a partir del esqueleto completo.

        Dos pasadas: primero crear salas, después enlazar salidas (el destino
        puede venir en otra página). Aquí se decide cómo se comparten las
        puertas entre salidas dirigidas.
        """
        raise NotImplementedError

    def sala(self, sala_id: int) -> Sala:
        """Sala por id en O(1) promedio. KeyError con contexto si no existe."""
        raise NotImplementedError

    def vecinos(self, sala_id: int) -> list[int]:
        """Ids de salas vecinas por cualquier salida (abierta o cerrada).

        La usa la precarga de Persona B para el BFS. Solo depende del
        esqueleto, nunca del estado de juego.
        """
        raise NotImplementedError

    def incorporar_contenido(self, contenido: ContenidoSala, fichas: ProveedorFichas) -> None:
        """Agrega enemigos (dormidos), objetos y trampas de una sala.

        Reglas:
        - No activa enemigos (§2.4) ni consume el azar ni números de secuencia:
          así el momento en que llega la respuesta HTTP no altera la partida.
        - Si la sala ya tiene objetos soltados o enemigos activos que llegaron
          antes que su contenido, se conservan.
        - Ids de instancia de objetos: ``objetos.id_objeto_de_sala``.
        - Las fichas de todos los tipos ya deben estar resueltas en ``fichas``.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
