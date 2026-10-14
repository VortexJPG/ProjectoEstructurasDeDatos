"""Tabla hash propia.                          [Persona B — entregar PRIMERO]

§7 prohíbe usar ``dict`` como índice, caché o tabla de búsqueda. Esta tabla lo
reemplaza en TODO el programa.
"""

from __future__ import annotations

from typing import Generic, Hashable, Iterator, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class _Entrada(Generic[K, V]):
    __slots__ = ("clave", "valor")

    def __init__(self, clave: K, valor: V) -> None:
        self.clave = clave
        self.valor = valor


def _hash(clave: object) -> int:
    """Hash determinista para str/int y hashable en general."""
    if isinstance(clave, str):
        # FNV-1a de 64 bits: no depende de PYTHONHASHSEED.
        h = 0xCBF29CE484222325
        for byte in clave.encode("utf-8"):
            h ^= byte
            h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
        return h
    if isinstance(clave, int):
        return clave * 0x9E3779B97F4A7C15
    if isinstance(clave, bytes):
        h = 0xCBF29CE484222325
        for byte in clave:
            h ^= byte
            h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
        return h
    return hash(clave)


class TablaHash(Generic[K, V]):
    """Mapa clave → valor (encadenamiento separado) con rehashing."""

    FACTOR_CARGA_MAX = 0.75

    def __init__(self, capacidad_inicial: int = 16) -> None:
        if capacidad_inicial < 8:
            capacidad_inicial = 8
        self._capacidad = capacidad_inicial
        # redondear a potencia de dos para índice por máscara
        c = 1
        while c < self._capacidad:
            c <<= 1
        self._capacidad = c
        self._cubetas: list[list[_Entrada[K, V]]] = [[] for _ in range(self._capacidad)]
        self._tama = 0

    def insertar(self, clave: K, valor: V) -> None:
        indice = self._indice(clave)
        cubeta = self._cubetas[indice]
        for entrada in cubeta:
            if entrada.clave == clave:
                entrada.valor = valor
                return
        cubeta.append(_Entrada(clave, valor))
        self._tama += 1
        if self._tama / self._capacidad > self.FACTOR_CARGA_MAX:
            self._redimensionar(self._capacidad * 2)

    def obtener(self, clave: K, defecto: V | None = None) -> V | None:
        indice = self._indice(clave)
        for entrada in self._cubetas[indice]:
            if entrada.clave == clave:
                return entrada.valor
        return defecto

    def contiene(self, clave: K) -> bool:
        return self.obtener(clave, _NO_HAY) is not _NO_HAY  # type: ignore[comparison]

    def eliminar(self, clave: K) -> bool:
        indice = self._indice(clave)
        cubeta = self._cubetas[indice]
        for i, entrada in enumerate(cubeta):
            if entrada.clave == clave:
                del cubeta[i]
                self._tama -= 1
                return True
        return False

    def claves(self) -> Iterator[K]:
        for cubeta in self._cubetas:
            for entrada in cubeta:
                yield entrada.clave

    def valores(self) -> Iterator[V]:
        for cubeta in self._cubetas:
            for entrada in cubeta:
                yield entrada.valor

    def pares(self) -> Iterator[tuple[K, V]]:
        for cubeta in self._cubetas:
            for entrada in cubeta:
                yield (entrada.clave, entrada.valor)

    def __len__(self) -> int:
        return self._tama

    def __contains__(self, clave: object) -> bool:
        return self.obtener(clave, _CENTINELA) is not _CENTINELA  # type: ignore[arg-type]

    def _indice(self, clave: K) -> int:
        return _hash(clave) & (self._capacidad - 1)

    def _redimensionar(self, nueva_capacidad: int) -> None:
        viejas = self._cubetas
        nueva = 1
        while nueva < nueva_capacidad:
            nueva <<= 1
        self._capacidad = nueva
        self._cubetas = [[] for _ in range(self._capacidad)]
        self._tama = 0
        for cubeta in viejas:
            for entrada in cubeta:
                indice = self._indice(entrada.clave)
                self._cubetas[indice].append(entrada)
                self._tama += 1

    # Aliases solicitados en el prompt
    def poner(self, clave: K, valor: V) -> None:
        self.insertar(clave, valor)

    def get(self, clave: K, defecto: V | None = None) -> V | None:
        return self.obtener(clave, defecto)


class _Centinela:
    pass


_NO_HAY = object()
_CENTINELA = _Centinela()


class ConjuntoHash(Generic[K]):
    def __init__(self, capacidad_inicial: int = 16) -> None:
        self._tabla: TablaHash[K, None] = TablaHash(capacidad_inicial)

    def agregar(self, clave: K) -> bool:
        if clave in self._tabla:
            return False
        self._tabla.insertar(clave, None)
        return True

    def contiene(self, clave: K) -> bool:
        return self._tabla.contiene(clave)

    def eliminar(self, clave: K) -> bool:
        return self._tabla.eliminar(clave)

    def __len__(self) -> int:
        return len(self._tabla)

    def __contains__(self, clave: object) -> bool:
        return self._tabla.contiene(clave)  # type: ignore[arg-type]

    def __iter__(self) -> Iterator[K]:
        return self._tabla.claves()

    @property
    def items(self) -> Iterator[K]:
        return self._tabla.claves()
