# CRIPTA

Proyecto de Estructuras de Datos — II Ciclo 2026.

> **Estado:** esqueleto. Las clases y funciones están definidas, pero sin implementar (lanzan `NotImplementedError`). La división del trabajo está en [PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md).

## Requisitos

- Python 3.11 o superior
- Dependencias: `requests`

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Uso (pendiente de implementar)

```bash
python main.py                          # partida interactiva
python main.py --cripta cripta-01       # saltar la selección de cripta
python main.py --offline DIRECTORIO     # sin red, desde respuestas guardadas
python main.py --replay partida.log     # reproducir una partida sin interacción
python main.py --bench                  # mediciones por subsistema
python main.py --cache-size 25          # fichas de catálogo en memoria
```

## Archivos generados

| Qué | Dónde |
|---|---|
| Caché persistente (catálogo, esqueleto, contenido) | `datos_locales/` |
| Partidas guardadas (binario propio) | por definir |
| Bitácoras de replay | por definir |
| Tabla de puntajes | por definir |

## Estructura

```
main.py
cripta/
  constantes.py      reglas fijas del juego (§2)
  estructuras/       estructuras de datos propias (§7)
  modelo/            reglas del juego; no conoce red, disco ni vista
  adaptadores/       red, --offline, disco, guardado, replay, puntajes
  controlador/       orquestación, precarga, replay, argumentos
  vista/             consola
  bench/             --bench
datos_ejemplo/       respuestas reales de cripta-01, para desarrollo y pruebas
```
