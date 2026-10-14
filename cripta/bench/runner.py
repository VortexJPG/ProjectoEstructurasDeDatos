from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class ResultadoMedicion:
    subsistema: str
    caso: str
    n: int
    repeticiones: int
    segundos_total: float

    def microsegundos_por_operacion(self) -> float:
        if self.repeticiones <= 0:
            return 0.0
        return (self.segundos_total / self.repeticiones) * 1_000_000.0


class RegistroBenchmarks:
    def __init__(self) -> None:
        self._casos: list[tuple[str, str, Callable[[], ResultadoMedicion]]] = []

    def agregar(self, subsistema: str, caso: str, funcion: Callable[[], ResultadoMedicion]) -> None:
        self._casos.append((subsistema, caso, funcion))

    def ejecutar(self, filtro: str | None = None) -> list[ResultadoMedicion]:
        resultados: list[ResultadoMedicion] = []
        for subsistema, caso, funcion in self._casos:
            if filtro is not None and filtro not in subsistema and filtro not in caso:
                continue
            try:
                resultados.append(funcion())
            except Exception as exc:
                print(f"[bench] error en {subsistema}/{caso}: {exc}")
        return resultados


def cronometrar(funcion: Callable[[], object], repeticiones: int) -> float:
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        funcion()
    return time.perf_counter() - inicio


def imprimir_tabla(resultados: list[ResultadoMedicion]) -> None:
    print(f"{'Subsistema':<22}{'Caso':<40}{'n':>8}{'reps':>8}{'us/op':>12}")
    for r in resultados:
        print(
            f"{r.subsistema:<22}{r.caso:<40}{r.n:>8}{r.repeticiones:>8}"
            f"{r.microsegundos_por_operacion():>12.3f}"
        )


def ejecutar_bench(filtro: str | None = None) -> int:
    from cripta.bench.bench_datos import registrar as registrar_bench_datos

    registro = RegistroBenchmarks()
    registrar_bench_datos(registro)
    resultados = registro.ejecutar(filtro)
    imprimir_tabla(resultados)
    return 0
