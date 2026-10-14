"""Benchmarks del modelo.                                            [Persona A]

Evidencia para las secciones §4.1, §4.5, §4.6, §4.7, §4.8 del Documento y
para el requisito de §5.2 (< 20 ms por ciclo entre decisiones del jugador).
Cada función devuelve un ``ResultadoMedicion``.
"""

from __future__ import annotations

from cripta.bench.runner import RegistroBenchmarks, ResultadoMedicion


def registrar(registro: RegistroBenchmarks) -> None:
    """Agrega todos los casos de este archivo al registro."""
    raise NotImplementedError


# --- §4.1 agenda ---------------------------------------------------------------

def bench_agenda_monticulo(eventos_simultaneos: int, operaciones: int) -> ResultadoMedicion:
    """Programar / extraer / cancelar con la agenda real (cientos de eventos, decenas de miles de extracciones)."""
    raise NotImplementedError


def bench_agenda_lista_lineal(eventos_simultaneos: int, operaciones: int) -> ResultadoMedicion:
    """ALTERNATIVA DESCARTADA: buscar el mínimo recorriendo una lista."""
    raise NotImplementedError


# --- §5.2 ciclo completo -------------------------------------------------------

def bench_ciclo_entre_decisiones(cantidad_salas: int, enemigos_activos: int) -> ResultadoMedicion:
    """Tiempo de resolver los eventos entre dos decisiones del jugador (meta < 20 ms)."""
    raise NotImplementedError


# --- §4.5 inventario -----------------------------------------------------------

def bench_inventario_lista_doble(tamano: int, operaciones: int) -> ResultadoMedicion:
    """Soltar en cualquier posición y mover al frente."""
    raise NotImplementedError


def bench_inventario_list_python(tamano: int, operaciones: int) -> ResultadoMedicion:
    """ALTERNATIVA: ``list`` con pop(i) / insert(0, x)."""
    raise NotImplementedError


# --- §4.6 historial ------------------------------------------------------------

def bench_historial_registrar_y_revertir(cambios_por_intervalo: int) -> ResultadoMedicion:
    raise NotImplementedError


# --- §4.7 rastro ---------------------------------------------------------------

def bench_rastreadores(cantidad_rastreadores: int, cantidad_salas: int) -> ResultadoMedicion:
    """Debe crecer linealmente con los rastreadores que actúan, no con el tamaño de la cripta."""
    raise NotImplementedError


# --- §4.8 bitácora -------------------------------------------------------------

def bench_bitacora_circular(mensajes: int) -> ResultadoMedicion:
    raise NotImplementedError


def bench_bitacora_list_pop0(mensajes: int) -> ResultadoMedicion:
    """ALTERNATIVA: ``list`` con append + pop(0)."""
    raise NotImplementedError
