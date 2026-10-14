from __future__ import annotations

import json
import os
from typing import Any

from cripta.estructuras.ordenamiento import ordenar
from cripta.modelo.juego import ResumenPartida

CRITERIOS = {
    "acciones": lambda r: r.acciones,
    "tiempo": lambda r: r.tiempo_final,
    "enemigos": lambda r: r.enemigos_derrotados,
}


from dataclasses import dataclass


@dataclass(slots=True)
class RegistroPuntaje:
    nombre: str
    cripta_id: str
    version_cripta: str
    acciones: int
    enemigos_derrotados: int
    tiempo_final: int
    resultado: str

    @staticmethod
    def desde_resumen(resumen: ResumenPartida) -> "RegistroPuntaje":
        return RegistroPuntaje(
            nombre=resumen.nombre_jugador,
            cripta_id=resumen.cripta_id,
            version_cripta=resumen.version_cripta,
            acciones=resumen.acciones_ejecutadas,
            enemigos_derrotados=resumen.enemigos_derrotados,
            tiempo_final=resumen.tiempo_final,
            resultado=resumen.estado.value,
        )


class TablaPuntajes:
    def __init__(self, ruta: str) -> None:
        self.ruta = ruta

    def _cargar_raw(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.ruta):
            return []
        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list):
                return datos
            if isinstance(datos, dict) and isinstance(datos.get("puntajes"), list):
                return datos["puntajes"]
        except (OSError, ValueError):
            pass
        return []

    def cargar(self) -> list[RegistroPuntaje]:
        salida: list[RegistroPuntaje] = []
        for d in self._cargar_raw():
            try:
                salida.append(
                    RegistroPuntaje(
                        nombre=d["nombre"],
                        cripta_id=d["cripta_id"],
                        version_cripta=d["version_cripta"],
                        acciones=int(d["acciones"]),
                        enemigos_derrotados=int(d["enemigos_derrotados"]),
                        tiempo_final=int(d["tiempo_final"]),
                        resultado=d["resultado"],
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return salida

    def agregar(self, registro: RegistroPuntaje) -> None:
        datos = self._cargar_raw()
        datos.append(
            {
                "nombre": registro.nombre,
                "cripta_id": registro.cripta_id,
                "version_cripta": registro.version_cripta,
                "acciones": registro.acciones,
                "enemigos_derrotados": registro.enemigos_derrotados,
                "tiempo_final": registro.tiempo_final,
                "resultado": registro.resultado,
            }
        )
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True) if os.path.dirname(self.ruta) else None
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def ordenados(self, criterio: str) -> list[RegistroPuntaje]:
        lista = self.cargar()
        clave = CRITERIOS.get(criterio)
        if clave is None:
            raise ValueError(f"criterio desconocido: {criterio}")
        descendente = criterio in ("enemigos",)
        # por defecto orden descendente por puntaje? documentar: más acciones mejor? 
        # Se ordena ascendente para tiempo (menor mejor) y descendente para acciones/enemigos
        if criterio == "tiempo":
            descendente = False
        else:
            descendente = True
        return ordenar(lista, clave=clave, descendente=descendente)
