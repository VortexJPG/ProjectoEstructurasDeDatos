from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Hashable, TypeVar

from cripta.estructuras.tabla_hash import TablaHash

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


@dataclass
class _NodoLRU:
    clave: K
    anterior: "_NodoLRU | None" = None
    siguiente: "_NodoLRU | None" = None


@dataclass
class _Entrada(Generic[V]):
    valor: V
    refs: int = 0
    nodo: _NodoLRU | None = None


class CacheAcotada(Generic[K, V]):
    def __init__(self, capacidad: int) -> None:
        if capacidad < 1:
            capacidad = 1
        self._capacidad = capacidad
        self._tabla: TablaHash[K, _Entrada[V]] = TablaHash()
        self._cabeza: _NodoLRU | None = None
        self._cola: _NodoLRU | None = None
        self._aciertos = 0
        self._fallos = 0
        self._desalojos = 0

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def __len__(self) -> int:
        return len(self._tabla)

    def _quitar_nodo(self, nodo: _NodoLRU) -> None:
        if nodo.anterior is None:
            self._cabeza = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente
        if nodo.siguiente is None:
            self._cola = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior
        nodo.anterior = nodo.siguiente = None

    def _poner_frente(self, nodo: _NodoLRU) -> None:
        nodo.anterior = None
        nodo.siguiente = self._cabeza
        if self._cabeza is not None:
            self._cabeza.anterior = nodo
        self._cabeza = nodo
        if self._cola is None:
            self._cola = nodo

    def obtener(self, clave: K) -> V | None:
        entrada = self._tabla.obtener(clave)
        if entrada is None:
            self._fallos += 1
            return None
        self._aciertos += 1
        if entrada.refs == 0 and entrada.nodo is not None:
            self._quitar_nodo(entrada.nodo)
            self._poner_frente(entrada.nodo)
        return entrada.valor

    def contiene(self, clave: K) -> bool:
        return self._tabla.contiene(clave)

    def __contains__(self, clave: object) -> bool:
        return self._tabla.contiene(clave)  # type: ignore[arg-type]

    def insertar(self, clave: K, valor: V) -> list[K]:
        entrada = self._tabla.obtener(clave)
        if entrada is not None:
            entrada.valor = valor
            if entrada.refs == 0 and entrada.nodo is not None:
                self._quitar_nodo(entrada.nodo)
                self._poner_frente(entrada.nodo)
            return []
        nodo = _NodoLRU(clave)
        nueva = _Entrada(valor=valor, refs=0, nodo=nodo)
        self._tabla.insertar(clave, nueva)
        self._poner_frente(nodo)
        nueva.nodo = nodo
        return self._desalojar_si_excede()

    def fijar(self, clave: K) -> None:
        entrada = self._tabla.obtener(clave)
        if entrada is None:
            raise KeyError(clave)
        entrada.refs += 1
        if entrada.refs == 1 and entrada.nodo is not None:
            self._quitar_nodo(entrada.nodo)
            entrada.nodo = None

    def liberar(self, clave: K) -> None:
        entrada = self._tabla.obtener(clave)
        if entrada is None:
            return
        if entrada.refs > 0:
            entrada.refs -= 1
        if entrada.refs == 0 and entrada.nodo is None:
            nodo = _NodoLRU(clave)
            entrada.nodo = nodo
            self._poner_frente(nodo)

    def esta_fijada(self, clave: K) -> bool:
        entrada = self._tabla.obtener(clave)
        return entrada is not None and entrada.refs > 0

    def eliminar(self, clave: K) -> bool:
        entrada = self._tabla.obtener(clave)
        if entrada is None:
            return False
        if entrada.nodo is not None:
            self._quitar_nodo(entrada.nodo)
        return self._tabla.eliminar(clave)

    @property
    def aciertos(self) -> int:
        return self._aciertos

    @property
    def fallos(self) -> int:
        return self._fallos

    @property
    def desalojos(self) -> int:
        return self._desalojos

    def _desalojar_si_excede(self) -> list[K]:
        desalojadas: list[K] = []
        while len(self._tabla) > self._capacidad:
            # Buscar último candidato no fijado (cola LRU)
            nodo = self._cola
            # encontrar último no-nulo nodo (la cola siempre es candidato si existe)
            if nodo is None:
                break
            # El nodo cola debería representar no fijado por invariantes.
            clave = nodo.clave
            entrada = self._tabla.obtener(clave)
            if entrada is None or entrada.refs > 0 or entrada.nodo is None:
                # No hay candidatas no fijadas.
                break
            self._quitar_nodo(nodo)
            self._tabla.eliminar(clave)
            self._desalojos += 1
            desalojadas.append(clave)
        return desalojadas
