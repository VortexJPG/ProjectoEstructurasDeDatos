from __future__ import annotations

import argparse
import os

from cripta.adaptadores.cliente_http import ClienteHTTP, BASE_URL
from cripta.adaptadores.fuente_offline import FuenteOffline
from cripta.controlador.controlador import Controlador, OpcionesEjecucion
from cripta.controlador.replay import ReproductorReplay


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cripta")
    parser.add_argument("--offline", type=str, default=None, help="directorio de respuestas offline")
    parser.add_argument("--replay", type=str, default=None, help="archivo de bitácora a reproducir")
    parser.add_argument("--bench", action="store_true", help="ejecutar benchmarks")
    parser.add_argument("--cache-size", type=int, default=25, dest="cache_size", help="fichas en memoria")
    parser.add_argument("--semilla", type=int, default=None, help="semilla de la partida")
    parser.add_argument("--cripta", type=str, default=None, dest="cripta_id", help="id de cripta")
    parser.add_argument("--datos", type=str, default="datos_locales", help="directorio de datos locales")
    parser.add_argument("--nombre", type=str, default=None, dest="nombre_jugador", help="nombre del jugador")
    return parser


def crear_fuente(argumentos: argparse.Namespace):
    if argumentos.offline:
        return FuenteOffline(argumentos.offline)
    return ClienteHTTP(BASE_URL)


def main(argv=None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    fuente = crear_fuente(args)
    opciones = OpcionesEjecucion(
        directorio_datos=args.datos,
        cache_size=args.cache_size,
        offline=args.offline,
        cripta_id=args.cripta_id,
        semilla=args.semilla,
        nombre_jugador=args.nombre_jugador,
    )
    if args.bench:
        from cripta.bench.runner import ejecutar_bench

        return ejecutar_bench()
    if args.replay:
        reproductor = ReproductorReplay(args.replay, fuente, opciones)
        resumen = reproductor.ejecutar()
        if resumen is not None:
            print("Replay completado:", resumen)
        return 0
    controlador = Controlador(fuente, opciones, None)
    controlador.ejecutar_interactivo()
    return 0
