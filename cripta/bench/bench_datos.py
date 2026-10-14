from __future__ import annotations

import random
import tempfile
import os

from cripta.estructuras.tabla_hash import TablaHash, ConjuntoHash
from cripta.estructuras.cola import ColaEnlazada
from cripta.estructuras.ordenamiento import ordenar, ordenar_con_algoritmo
from cripta.estructuras.lru import CacheAcotada
# evitar import circular: se resuelve dentro de registrar()


def registrar(registro) -> None:
    from cripta.bench.runner import ResultadoMedicion, cronometrar
    global ResultadoMedicion, cronometrar
    # TablaHash vs búsqueda lineal en lista
    def caso_tabla_hash(n):
        claves = [f"k{i}" for i in range(n)]
        tabla = TablaHash()
        for c in claves:
            tabla.insertar(c, c)
        def buscar():
            for c in claves:
                tabla.obtener(c)
        secs = cronometrar(buscar, 5)
        return ResultadoMedicion("tabla_hash", f"buscar n={n}", n, 5, secs)

    def caso_lista_lineal(n):
        claves = [f"k{i}" for i in range(n)]
        lista = list(claves)
        def buscar():
            for c in claves:
                c in lista
        secs = cronometrar(buscar, 5)
        return ResultadoMedicion("tabla_hash", f"lineal n={n}", n, 5, secs)

    for n in (100, 1000, 5000):
        registro.agregar("tabla_hash", f"hash n={n}", lambda n=n: caso_tabla_hash(n))
        registro.agregar("tabla_hash", f"lineal n={n}", lambda n=n: caso_lista_lineal(n))

    # Cola enlazada vs list.pop(0)
    def caso_cola(n):
        def run():
            q = ColaEnlazada()
            for i in range(n):
                q.encolar(i)
            while not q.esta_vacia():
                q.desencolar()
        secs = cronometrar(run, 5)
        return ResultadoMedicion("cola", f"enlazada n={n}", n, 5, secs)

    def caso_lista_pop(n):
        def run():
            l = list(range(n))
            while l:
                l.pop(0)
        secs = cronometrar(run, 5)
        return ResultadoMedicion("cola", f"pop0 n={n}", n, 5, secs)

    for n in (100, 1000, 5000):
        registro.agregar("cola", f"enlazada n={n}", lambda n=n: caso_cola(n))
        registro.agregar("cola", f"pop0 n={n}", lambda n=n: caso_lista_pop(n))

    # Ordenamiento: inserción vs mezcla vs selector
    def caso_orden(n, patron, algoritmo):
        rng = random.Random(42)
        if patron == "aleatorio":
            datos = [rng.randint(0, 10**9) for _ in range(n)]
        elif patron == "casi_ordenado":
            datos = list(range(n))
            for _ in range(max(1, n // 100)):
                a = rng.randrange(n)
                b = rng.randrange(n)
                datos[a], datos[b] = datos[b], datos[a]
        elif patron == "inverso":
            datos = list(range(n, 0, -1))
        else:
            datos = list(range(n))

        def run():
            ordenar_con_algoritmo(datos, algoritmo)
        secs = cronometrar(run, 3)
        return ResultadoMedicion("ordenamiento", f"{algoritmo} {patron} n={n}", n, 3, secs)

    for n in (50, 500, 5000):
        for patron in ("aleatorio", "casi_ordenado", "inverso"):
            for algoritmo in ("insercion", "mezcla"):
                registro.agregar(
                    "ordenamiento",
                    f"{algoritmo} {patron} n={n}",
                    lambda n=n, p=patron, a=algoritmo: caso_orden(n, p, a),
                )

    # CacheAcotada hit/miss
    def caso_cache(n, patron):
        cache = CacheAcotada(n // 2 if n // 2 > 0 else 1)
        claves = [f"k{i}" for i in range(n)]
        for c in claves:
            cache.insertar(c, c)
        if patron == "hit":
            def run():
                for c in claves[: n // 2]:
                    cache.obtener(c)
        else:
            def run():
                for i in range(n // 2, n):
                    cache.obtener(f"k{i}")  # miss tras desalojo? simple
        secs = cronometrar(run, 5)
        return ResultadoMedicion("cache", f"{patron} n={n}", n, 5, secs)

    for n in (100, 1000):
        registro.agregar("cache", f"hit n={n}", lambda n=n: caso_cache(n, "hit"))
        registro.agregar("cache", f"miss n={n}", lambda n=n: caso_cache(n, "miss"))

    # Guardado binario vs JSON (tamaño/tiempo) usando sintético pequeño
    def caso_guardado(formato):
        from cripta.bench.sinteticos import generar_cripta
        from cripta.modelo.guardable import EstadoGuardable, RegistroJugador
        from cripta.adaptadores.guardado import GuardadoBinario, GuardadoJSON
        from dataclasses import asdict
        cs = generar_cripta(20, 0.3, 1)
        # construir estado mínimo
        estado = EstadoGuardable(
            cripta_id=cs.datos.id,
            version_cripta=cs.datos.version,
            version_catalogo="v1",
            semilla=1,
            estado_azar=tuple([1, 2, 3]),
            reloj=0,
            siguiente_secuencia=1,
            jugador=RegistroJugador(
                nombre="Tester", sala=1, vida=30, vida_max=30, ataque=6, defensa=2, velocidad=100,
                tiempo_siguiente=None, inventario=[], arma_equipada=None, armadura_equipada=None,
                acciones_ejecutadas=0, enemigos_derrotados=0, abrio_puerta_salida=False,
            ),
            salas=[],
            efectos=[],
            eventos=[],
        )
        fd, ruta = tempfile.mkstemp()
        os.close(fd)
        if formato == "binario":
            g = GuardadoBinario()
        else:
            g = GuardadoJSON()
            ruta = ruta + ".json"
        try:
            def run():
                g.guardar(ruta, estado)
                g.cargar(ruta)
            secs = cronometrar(run, 3)
            tam = os.path.getsize(ruta)
            return ResultadoMedicion("guardado", f"{formato} tam={tam}", 20, 3, secs)
        finally:
            try:
                os.remove(ruta)
            except OSError:
                pass

    for formato in ("binario", "json"):
        registro.agregar("guardado", formato, lambda f=formato: caso_guardado(f))
