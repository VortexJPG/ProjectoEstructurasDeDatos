"""Datos sintéticos para --bench y pruebas sin red.                  [Persona B]
"""

from __future__ import annotations

from dataclasses import dataclass

from cripta.modelo.datos import ContenidoSala, DatosCripta, DatosSala, Ficha
from cripta.modelo.puertos import FichaNoDisponible, ProveedorFichas
from cripta.estructuras.tabla_hash import TablaHash


@dataclass(slots=True)
class CriptaSintetica:
    datos: DatosCripta
    salas: list[DatosSala]
    contenido: list[ContenidoSala]
    fichas: list[Ficha]


def generar_cripta(cantidad_salas: int, enemigos_por_sala: float, semilla: int) -> CriptaSintetica:
    """Cripta conexa y aleatoria (reproducible con ``semilla``)."""
    import random
    azar = random.Random(semilla)
    # datos generales mínimos
    datos = DatosCripta(
        id="cripta-sintetica",
        version="v1",
        salas_total=cantidad_salas,
        paginas=1,
        salas_por_pagina=cantidad_salas if cantidad_salas > 0 else 1,
        sala_inicial=1,
        sala_salida=cantidad_salas,
        llave_salida="itm_llave_negra",
        presupuesto_solicitudes=max(9, cantidad_salas + 3),
        inventario_max=10,
        jugador=__import__("cripta.modelo.datos", fromlist=["EstadisticasIniciales"]).EstadisticasIniciales(
            vida_max=30, ataque=6, defensa=2, velocidad=100
        ),
    )
    salas: list[DatosSala] = []
    contenido: list[ContenidoSala] = []
    for i in range(1, cantidad_salas + 1):
        vecinos = []
        if i > 1:
            vecinos.append(("S", i - 1))
        if i < cantidad_salas:
            vecinos.append(("N", i + 1))
        salidas = []
        for d, dest in vecinos:
            salidas.append(__import__("cripta.modelo.datos", fromlist=["DatosSalida"]).DatosSalida(direccion=d, sala_destino=dest))
        salas.append(DatosSala(id=i, nombre=f"Sala {i}", salidas=salidas))
        enemigos = []
        if azar.random() < enemigos_por_sala:
            enemigos.append(__import__("cripta.modelo.datos", fromlist=["ColocacionEnemigo"]).ColocacionEnemigo(
                instancia=f"e-{i}01", tipo="ent_rata_gigante"
            ))
        contenido.append(
            ContenidoSala(sala=i, enemigos=enemigos, objetos=[], trampas=[])
        )
    fichas = [
        Ficha(id="ent_rata_gigante", clase="enemigo", nombre="Rata", vida_max=12, ataque=5, defensa=1, velocidad=150, comportamiento="rastreador", suelta=["itm_pocion_menor"]),
        Ficha(id="itm_pocion_menor", clase="pocion", nombre="Pocion", peso=1, valor=10, cura=8),
    ]
    return CriptaSintetica(datos=datos, salas=salas, contenido=contenido, fichas=fichas)


class FichasEnMemoria(ProveedorFichas):
    def __init__(self, fichas: list[Ficha]) -> None:
        self._tabla: TablaHash[str, Ficha] = TablaHash()
        for f in fichas:
            self._tabla.insertar(f.id, f)

    def obtener(self, tipo_id: str) -> Ficha:
        valor = self._tabla.obtener(tipo_id)
        if valor is None:
            raise FichaNoDisponible(tipo_id)
        return valor

    def fijar(self, tipo_id: str) -> None:
        return None

    def liberar(self, tipo_id: str) -> None:
        return None
