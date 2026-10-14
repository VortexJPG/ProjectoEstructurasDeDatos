# Plan de trabajo — CRIPTA

El trabajo se divide en dos mitades con **poco acoplamiento** entre ellas. Se tocan solo en unos pocos archivos de *contrato* que ya están definidos en el esqueleto.

| | **Persona A — Motor del juego** | **Persona B — Datos, red y persistencia** |
|---|---|---|
| Idea | Todo lo que pasa *dentro* de la partida | Todo lo que entra y sale de la partida |
| Capas MVC | Modelo + Vista | Adaptadores + Controlador |
| Enunciado | §2 completo, §4.1, §4.5, §4.6, §4.7, §4.8, §5.2, §10.2 | §3, §4.2, §4.3, §4.4, §4.9, §4.10, §4.11, §5.1, §5.3, §6, §10.1 |
| Rúbrica (§11) | Juego funcional (20 %), retroceso, rendimiento del ciclo | Cliente y presupuesto de red (25 %), caché, persistencia, mediciones |
| Documento de Decisiones | Secciones §4.1, §4.5, §4.6, §4.7, §4.8 | Secciones §4.2, §4.3, §4.4, §4.9, §4.10, §4.11 |

Cada archivo dice en su primera línea quién es el responsable: `[Persona A]`, `[Persona B]` o `[CONTRATO A↔B]`.

---

## Persona A — Motor del juego

**Estructuras propias**
- `estructuras/monticulo.py`: `MonticuloMin` (agenda de eventos).
- `estructuras/lista_doble.py`: `ListaDoble` (inventario; también la usa la caché LRU de B).
- `estructuras/buffer_circular.py`: `BufferCircular` (últimos 20 mensajes y últimos 5 intervalos de retroceso).

**Modelo**
- `modelo/eventos.py`: `Agenda` con cancelación y reprogramación.
- `modelo/actores.py`, `modelo/objetos.py`, `modelo/mapa.py`: jugador, enemigos, objetos, trampas, salas, puertas y rastro.
- `modelo/inventario.py`: cursor, soltar en O(1), mover al frente y vistas ordenadas.
- `modelo/efectos.py`: veneno, velocidad, antorcha, regeneración, trampas y cierre de puertas.
- `modelo/comportamiento.py`: guardián, errante y rastreador.
- `modelo/historial.py`: pergaminos de retroceso (bitácora de deshacer).
- `modelo/mensajes.py`: bitácora en pantalla.
- `modelo/juego.py`: la fachada y el bucle de eventos.
- `constantes.indice_direccion`.

**Otros**
- `vista/vista_consola.py`: la interfaz de consola.
- `bench/bench_modelo.py`: agenda, ciclo de §5.2 (< 20 ms), inventario, historial, rastreadores y bitácora.

## Persona B — Datos, red y persistencia

**Estructuras propias**
- `estructuras/tabla_hash.py`: `TablaHash` y `ConjuntoHash`, el reemplazo de `dict` en todo el proyecto.
- `estructuras/cola.py`: `ColaEnlazada` (BFS de precarga y solicitudes pendientes en orden).
- `estructuras/ordenamiento.py`: inserción, mezcla, selector automático y búsqueda binaria.
- `estructuras/lru.py`: `CacheAcotada` con desalojo y fijado.

**Contratos (la parte de B)**
- `modelo/datos.py`: todos los `desde_json`.
- `modelo/acciones.py`: `a_linea` y `desde_linea`.

**Adaptadores**
- `adaptadores/fuente_datos.py`, `cliente_http.py`, `fuente_offline.py`: red con `X-Cripta-Client-Id`, manejo de 429 y presupuesto, y modo `--offline`.
- `adaptadores/almacen_disco.py`, `cache_catalogo.py`: caché persistente y resolución de catálogo por lotes.
- `adaptadores/guardado.py`: guardado binario propio, con JSON para comparar.
- `adaptadores/bitacora_replay.py`, `puntajes.py`.

**Controlador**
- `controlador/precarga.py`: precarga por lotes con orden determinista.
- `controlador/controlador.py`, `replay.py`, `aplicacion.py`: orquestación, `--replay` y banderas.

**Otros**
- `bench/runner.py`, `bench/sinteticos.py`, `bench/bench_datos.py`.
- `README.md`.

## Los dos
- `PROMPTS_LLM.md`: cada quien agrega sus prompts.
- Revisar las secciones del Documento que escribió el otro. En la defensa **cualquiera** puede tener que explicar **cualquier** decisión (§9).
- Pruebas de sus propias estructuras (se recomienda una carpeta `tests/` con `unittest`).

> Si una mitad avanza más rápido, la pieza más fácil de mover es la **vista de consola**: puede pasar de A a B sin tocar nada más.

---

## Orden sugerido

| Fase | Persona A | Persona B |
|---|---|---|
| **0. Arranque** (juntos) | Crear el repo en GitHub, subir este esqueleto y leer juntos los archivos `[CONTRATO]` | ← |
| **1. Estructuras base** + pruebas | `MonticuloMin`, `ListaDoble`, `BufferCircular`, `indice_direccion` | `TablaHash`, `ConjuntoHash`, `ColaEnlazada`, los `desde_json` de `datos.py` y `FichasEnMemoria` |
| **2. Núcleo por separado** | `Agenda`, `Mapa`, actores, `Juego` (mover, atacar, esperar y bucle), IA, rastro y vista mínima. Se prueba con `datos_ejemplo/` + `FichasEnMemoria`, sin red | `ClienteHTTP` (429 y presupuesto), `FuenteOffline`, almacenes, `CacheAcotada`, `CacheCatalogo`, `ordenamiento` y `aplicacion.py` |
| **3. Integración** | Atender lo que pida B en `Mapa.vecinos`, `incorporar_contenido` y la API de `Juego` | `Controlador`, `PlanificadorPrecarga` y `EscritorReplay`. Meta: jugar cripta-01 de punta a punta |
| **4. Completar** | Inventario completo con vistas ordenadas, efectos, historial/retroceso y `exportar_estado` / `desde_estado` | Guardado binario + JSON, `ReproductorReplay`, puntajes, `runner` y `sinteticos.generar_cripta` |
| **5. Evidencia** | `bench_modelo` + sus secciones del Documento | `bench_datos` + sus secciones del Documento + README |

### Qué necesita cada uno del otro (y cuándo)

| Quién lo necesita | Qué | Fase |
|---|---|---|
| A ← B | `TablaHash` (el modelo no puede usar `dict`) | 1 |
| A ← B | `desde_json` de `datos.py` y `FichasEnMemoria`, para probar con `datos_ejemplo/` | 1 |
| A ← B | `ordenamiento.ordenar` (vistas del inventario y orden de activación de enemigos) | 2 |
| B ← A | `ListaDoble` (la usa `CacheAcotada`) | 1 |
| B ← A | `Mapa.construir`, `Mapa.vecinos`, `Mapa.incorporar_contenido` y `Juego.ejecutar_accion` | 3 |
| B ← A | `Juego.exportar_estado` y `Juego.desde_estado` | 4 |

---

## Puntos de integración delicados

1. **Antes de mover.** El controlador pregunta `juego.sala_destino(dir)` y llama a `precarga.asegurar(sala)`, que trae el contenido y resuelve sus fichas. Recién entonces llama a `juego.ejecutar_accion`. Si el modelo responde `requiere_sala`, se asegura esa sala y se reintenta.
2. **Fijar y liberar fichas.** A decide *cuándo* (entrar o salir de una sala, recoger, soltar, morir, retroceder) y B decide *cómo* (`CacheCatalogo.fijar` / `liberar`). Si esto queda incoherente, la caché desaloja fichas en uso.
3. **Retroceso.** Toda mutación del estado del juego pasa por `Juego._asignar` (u otro helper que registre un `Cambio`). Los pergaminos y la caché quedan fuera.
4. **Determinismo**, sin el cual el replay deja de funcionar:
   - Toda aleatoriedad usa `juego.azar` (`random.Random(semilla)`).
   - Las salidas se recorren siempre en el orden N, S, E, O.
   - Nunca se itera una `TablaHash` para decidir algo del juego, porque `hash(str)` cambia entre ejecuciones.
   - Las respuestas HTTP se incorporan en el orden en que se solicitaron, y la incorporación no consume azar ni números de secuencia.
   - Los ids de los objetos se generan de forma determinista.
5. **Contratos.** Los archivos `[CONTRATO A↔B]` (`datos.py`, `acciones.py`, `puertos.py`, `guardable.py`, `comandos.py` y `constantes.py`) se pueden cambiar, pero **avisando** y en un commit aparte.

## Reglas para todo el código (§7, §9)

- Nada de `dict` como índice, caché o tabla de búsqueda: se usa `TablaHash` / `ConjuntoHash`. Leer el resultado de `respuesta.json()` sí está permitido.
- Nada de `sorted()` ni `list.sort()`: se usa `estructuras.ordenamiento.ordenar`.
- No se escriben en el código salas, ids, páginas, presupuestos ni estadísticas de una cripta.
- El modelo no importa `requests`, `json` ni `os`, no usa `open()` y no conoce la vista.
- Cada decisión de estructura se mide con `--bench` **mientras se implementa**, no al final. Eso es lo que pide el Documento de Decisiones (§8), incluida al menos una alternativa descartada medida.

## Hallazgos del API real (revisado 2026-10-02)

- Por ahora solo está publicada `cripta-01`, con 6 salas, presupuesto 9 e inventario de 10. Sus respuestas están en `datos_ejemplo/cripta-01/`.
- Las salidas son **dirigidas**: `2 →E→ 5` está cerrada con llave, pero `5 →O→ 2` no declara cierre. Hay que decidir si la puerta se comparte entre los dos sentidos (ver `modelo/mapa.py`).
- El enemigo `e-401` viene sin `vida`, así que se usa `vida_max`.
- Los objetos del contenido son solo ids de tipo. El modelo genera los ids de instancia.
- `abre` de una llave (`"puerta_2_7"`) no coincide con las salas. La regla del juego es `salida.llave == id de la llave`.
- El esquema de fichas **no** tiene veneno ni regeneración (`additionalProperties: false`), aunque §2.10 los menciona. Se leen como opcionales.
- Sin el encabezado `X-Cripta-Client-Id`, el servidor responde **400**.
