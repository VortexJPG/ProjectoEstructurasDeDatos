from __future__ import annotations

from typing import Any, Callable, Sequence, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def _clave_por_defecto(x: Any) -> Any:
    return x


def _comparar(a: Any, b: Any, descendente: bool) -> int:
    if descendente:
        if a > b:
            return -1
        if a < b:
            return 1
        return 0
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def _ord_insercion(items: list[Any], clave: Callable[[Any], Any], descendente: bool) -> list[Any]:
    # Copia estable de la lista original (no se altera el argumento).
    salida = list(items)
    for i in range(1, len(salida)):
        actual = salida[i]
        valor_actual = clave(actual)
        j = i - 1
        while j >= 0 and _comparar(clave(salida[j]), valor_actual, descendente) > 0:
            salida[j + 1] = salida[j]
            j -= 1
        salida[j + 1] = actual
    return salida


def _fusionar(izquierda: list[Any], derecha: list[Any], clave: Callable[[Any], Any], descendente: bool) -> list[Any]:
    salida: list[Any] = []
    i = j = 0
    li, rd = len(izquierda), len(derecha)
    while i < li and j < rd:
        if _comparar(clave(izquierda[i]), clave(derecha[j]), descendente) <= 0:
            salida.append(izquierda[i])
            i += 1
        else:
            salida.append(derecha[j])
            j += 1
    if i < li:
        salida.extend(izquierda[i:])
    if j < rd:
        salida.extend(derecha[j:])
    return salida


def _ord_mezcla(items: list[Any], clave: Callable[[Any], Any], descendente: bool) -> list[Any]:
    if len(items) <= 1:
        return list(items)
    medio = len(items) // 2
    izq = _ord_mezcla(items[:medio], clave, descendente)
    der = _ord_mezcla(items[medio:], clave, descendente)
    return _fusionar(izq, der, clave, descendente)


def _es_casi_ordenado(items: list[Any], clave: Callable[[Any], Any]) -> bool:
    """Cuenta inversiones adyacentes O(n) para decidir inserción."""
    if len(items) < 2:
        return True
    inversiones = 0
    for i in range(len(items) - 1):
        if clave(items[i]) > clave(items[i + 1]):
            inversiones += 1
            if inversiones > len(items) // 10 + 3:
                return False
    return inversiones <= len(items) // 10 + 3


def _selector_algoritmo(cantidad: int, clave: Callable[[Any], Any], items: list[Any], descendente: bool) -> str:
    if cantidad <= 64:
        return "insercion"
    if _es_casi_ordenado(items, clave):
        return "insercion"
    return "mezcla"


def ordenar(
    lista: Sequence[Any],
    clave: Callable[[Any], Any] | None = None,
    descendente: bool = False,
) -> list[Any]:
    """Ordena sin alterar la lista original. Selector automático de algoritmo."""
    clave_final = clave if clave is not None else _clave_por_defecto
    items = list(lista)
    algoritmo = _selector_algoritmo(len(items), clave_final, items, descendente)
    if algoritmo == "insercion":
        return _ord_insercion(items, clave_final, descendente)
    return _ord_mezcla(items, clave_final, descendente)


def ordenar_con_algoritmo(
    lista: Sequence[Any],
    algoritmo: str,
    clave: Callable[[Any], Any] | None = None,
    descendente: bool = False,
) -> list[Any]:
    clave_final = clave if clave is not None else _clave_por_defecto
    items = list(lista)
    if algoritmo == "insercion":
        return _ord_insercion(items, clave_final, descendente)
    if algoritmo == "mezcla":
        return _ord_mezcla(items, clave_final, descendente)
    raise ValueError(f"algoritmo desconocido: {algoritmo}")


def busqueda_binaria(
    lista: Sequence[Any],
    objetivo: Any,
    clave: Callable[[Any], Any] | None = None,
    descendente: bool = False,
) -> int:
    clave_final = clave if clave is not None else _clave_por_defecto
    lo, hi = 0, len(lista) - 1
    while lo <= hi:
        medio = (lo + hi) // 2
        valor = clave_final(lista[medio])
        cmp = _comparar(valor, objetivo, descendente)
        if cmp == 0:
            return medio
        if cmp < 0:
            lo = medio + 1
        else:
            hi = medio - 1
    return -1
# Alias en español:
ordenar_insertar = "insercion"


def selector_algoritmo_mediciones(cantidad: int, descuentos: bool = False) -> str:
    return "insercion" if cantidad <= 64 else "mezcla"
