from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from cripta.adaptadores.almacen_disco import AlmacenCatalogo, AlmacenCripta
from cripta.adaptadores.bitacora_replay import EncabezadoReplay, EscritorReplay, LectorReplay
from cripta.adaptadores.cache_catalogo import CacheCatalogo
from cripta.adaptadores.fuente_datos import FuenteDatos
from cripta.adaptadores.guardado import GuardadoBinario, GuardadoJSON
from cripta.adaptadores.puntajes import RegistroPuntaje, TablaPuntajes
from cripta.controlador.comandos import ComandoUsuario, TipoComando
from cripta.controlador.precarga import PlanificadorPrecarga
from cripta.modelo.juego import Juego

if TYPE_CHECKING:
    from cripta.modelo.datos import ContenidoSala, DatosCripta
    from cripta.vista.vista_consola import VistaConsola
    from cripta.modelo.acciones import Accion, ResultadoAccion


@dataclass(slots=True)
class OpcionesEjecucion:
    directorio_datos: str
    cache_size: int
    offline: str | None = None
    cripta_id: str | None = None
    semilla: int | None = None
    nombre_jugador: str | None = None


class Controlador:
    def __init__(self, fuente: FuenteDatos, opciones: OpcionesEjecucion, vista: Any = None) -> None:
        self.fuente = fuente
        self.opciones = opciones
        self.vista = vista
        self.directorio_datos = opciones.directorio_datos
        self.cache_size = opciones.cache_size
        os.makedirs(self.directorio_datos, exist_ok=True)
        self._juego: Juego | None = None
        self._mapa: Any = None
        self._datos: Any = None
        self._catalogo: CacheCatalogo | None = None
        self._almacen_cripta: AlmacenCripta | None = None
        self.almacen_catalogo = AlmacenCatalogo(os.path.join(self.directorio_datos, "catalogo"))
        self._precarga: PlanificadorPrecarga | None = None
        self._escritor: EscritorReplay | None = None
        self._cripta_id = opciones.cripta_id
        self._version_catalogo: str | None = None
        self._semilla: int | None = None

    def ejecutar_interactivo(self) -> None:
        if self._cripta_id is None:
            criptas = self.fuente.listar_criptas()
            if self.vista is not None:
                self._cripta_id = self.vista.elegir_cripta(criptas)
            elif criptas:
                self._cripta_id = criptas[0].id
            else:
                raise RuntimeError("no hay criptas disponibles")
        assert self._cripta_id is not None
        self.preparar_cripta(self._cripta_id)
        nombre = self.opciones.nombre_jugador
        if nombre is None:
            if self.vista is not None:
                nombre = self.vista.pedir_nombre()
            else:
                nombre = "Jugador"
        semilla = self.opciones.semilla
        self.iniciar_partida(nombre, semilla, True)
        if self.vista is not None:
            try:
                self.vista.mostrar_info("Partida iniciada.")
            except Exception:
                pass
        while self._juego is not None and not self._juego.esta_terminada():
            if self.vista is not None:
                try:
                    self.vista.mostrar_estado(self._juego)
                except Exception:
                    pass
                comando = self.vista.pedir_comando(self._juego)
                continuar = self.procesar_comando(comando)
                if not continuar:
                    break
            else:
                break
        self.finalizar()

    def procesar_comando(self, comando: ComandoUsuario) -> bool:
        if self._juego is None:
            return True
        if comando.tipo is TipoComando.ACCION:
            if comando.accion is not None:
                resultado = self.ejecutar_accion(comando.accion)
                if self.vista is not None:
                    try:
                        self.vista.mostrar_resultado(resultado)
                    except Exception:
                        pass
            return True
        if comando.tipo is TipoComando.INVENTARIO_SIGUIENTE:
            return True
        if comando.tipo is TipoComando.INVENTARIO_ANTERIOR:
            return True
        if comando.tipo is TipoComando.VER_INVENTARIO:
            if self.vista is not None:
                try:
                    self.vista.mostrar_inventario(self._juego)
                except Exception:
                    pass
            return True
        if comando.tipo is TipoComando.VISTA_ORDENADA:
            if self.vista is not None:
                try:
                    self.vista.mostrar_inventario(self._juego)
                except Exception:
                    pass
            return True
        if comando.tipo is TipoComando.GUARDAR:
            ruta = comando.argumento or os.path.join(self.directorio_datos, "partida_guardada.bin")
            try:
                self.guardar_partida(ruta)
                if self.vista is not None:
                    self.vista.mostrar_info(f"Guardado en {ruta}")
            except Exception as exc:
                if self.vista is not None:
                    self.vista.mostrar_error(str(exc))
            return True
        if comando.tipo is TipoComando.CARGAR:
            ruta = comando.argumento or os.path.join(self.directorio_datos, "partida_guardada.bin")
            try:
                self.cargar_partida(ruta)
                if self.vista is not None:
                    self.vista.mostrar_info(f"Cargado {ruta}")
            except Exception as exc:
                if self.vista is not None:
                    self.vista.mostrar_error(str(exc))
            return True
        if comando.tipo is TipoComando.PUNTAJES:
            tabla = TablaPuntajes(os.path.join(self.directorio_datos, "puntajes.json"))
            registros = tabla.ordenados("tiempo")
            if self.vista is not None:
                try:
                    self.vista.mostrar_puntajes(registros)
                except Exception:
                    pass
            return True
        if comando.tipo is TipoComando.AYUDA:
            if self.vista is not None:
                try:
                    self.vista.mostrar_ayuda()
                except Exception:
                    pass
            return True
        if comando.tipo is TipoComando.SALIR:
            return False
        return True

    def preparar_cripta(self, cripta_id: str) -> None:
        self._cripta_id = cripta_id
        self._datos = self.fuente.datos_cripta(cripta_id)
        self.fuente.establecer_presupuesto(self._datos.presupuesto_solicitudes)
        self._almacen_cripta = AlmacenCripta(self.directorio_datos, cripta_id)
        cripta_version = self._datos.version
        self._almacen_cripta.validar_version(cripta_version)
        # esqueleto
        esqueleto = self._almacen_cripta.cargar_esqueleto()
        datos_generales_disco = self._almacen_cripta.cargar_datos_generales()
        if esqueleto is None:
            todas_salas: list[Any] = []
            for pagina in range(1, self._datos.paginas + 1):
                pg = self.fuente.pagina_esqueleto(cripta_id, pagina)
                todas_salas.extend(pg.salas)
            esqueleto = todas_salas
            self._almacen_cripta.guardar_esqueleto(esqueleto)
            self._almacen_cripta.guardar_datos_generales(self._datos)
        from cripta.modelo.mapa import Mapa

        self._mapa = Mapa.construir(self._datos, esqueleto)
        # catalogo
        self._catalogo = CacheCatalogo(self.fuente, self.almacen_catalogo, self.cache_size)
        version_cat = self.fuente.version_catalogo()
        self._catalogo.validar_version(version_cat)
        self._version_catalogo = version_cat
        # precarga
        def incorporar(contenido: Any) -> None:
            self._mapa.incorporar_contenido(contenido, self._catalogo)

        self._precarga = PlanificadorPrecarga(
            self.fuente, cripta_id, self._almacen_cripta, self._catalogo, self._mapa.vecinos, incorporar
        )
        # asegurar sala inicial
        self._precarga.asegurar(self._datos.sala_inicial)
        self._precarga.planificar(self._datos.sala_inicial)

    def iniciar_partida(self, nombre_jugador: str, semilla: int | None, registrar_replay: bool = True) -> None:
        if semilla is None:
            semilla = random.randrange(2**31)
        self._semilla = semilla
        data = self._datos
        mapa = self._mapa
        catalogo = self._catalogo
        assert data is not None and mapa is not None and catalogo is not None
        self._juego = Juego(data, mapa, catalogo, semilla, nombre_jugador)
        self._juego.iniciar()
        if registrar_replay:
            encabezado = EncabezadoReplay(
                cripta_id=data.id,
                version_cripta=data.version,
                version_catalogo=self._version_catalogo or "",
                semilla=semilla,
                nombre_jugador=nombre_jugador,
            )
            ruta_log = os.path.join(self.directorio_datos, "partida.log")
            self._escritor = EscritorReplay(ruta_log, encabezado)

    def ejecutar_accion(self, accion: Any) -> Any:
        juego = self._juego
        assert juego is not None
        # asegurar sala destino si aplica
        try:
            from cripta.modelo.acciones import TipoAccion

            if accion.tipo in (TipoAccion.MOVER, TipoAccion.ABRIR):
                destino = juego.sala_destino(accion.direccion)
                if destino is not None and self._precarga is not None:
                    self._precarga.asegurar(destino.id)
        except Exception:
            pass
        resultado = juego.ejecutar_accion(accion)
        if self._escritor is not None and getattr(resultado, "aceptada", False):
            self._escritor.registrar(accion)
        if self._precarga is not None:
            try:
                sala_actual = juego.jugador.sala
                self._precarga.planificar(sala_actual)
                self._precarga.incorporar_disponibles()
            except Exception:
                pass
        # manejar requires_sala
        if getattr(resultado, "requiere_sala", None) is not None and self._precarga is not None:
            sala_req = resultado.requiere_sala
            self._precarga.asegurar(sala_req)
            # retry once
            resultado = juego.ejecutar_accion(accion)
            if self._escritor is not None and getattr(resultado, "aceptada", False):
                self._escritor.registrar(accion)
        return resultado

    def guardar_partida(self, ruta: str) -> None:
        juego = self._juego
        assert juego is not None
        estado = juego.exportar_estado(self._version_catalogo or "")
        GuardadoBinario().guardar(ruta, estado)
        GuardadoJSON().guardar(ruta + ".json", estado)

    def cargar_partida(self, ruta: str) -> None:
        estado = GuardadoBinario().cargar(ruta)
        if self._datos is not None:
            if estado.version_cripta != self._datos.version:
                from cripta.adaptadores.fuente_datos import ErrorFuenteDatos

                raise ErrorFuenteDatos("cargar_partida", "versión de cripta incompatible")
            if self._version_catalogo is not None and estado.version_catalogo != self._version_catalogo:
                from cripta.adaptadores.fuente_datos import ErrorFuenteDatos

                raise ErrorFuenteDatos("cargar_partida", "versión de catálogo incompatible")
        from cripta.modelo.juego import Juego

        juego = Juego.desde_estado(estado, self._datos, self._mapa, self._catalogo)
        self._juego = juego

    def finalizar(self) -> None:
        if self._precarga is not None:
            try:
                self._precarga.cerrar()
            except Exception:
                pass
        if self._escritor is not None:
            try:
                self._escritor.cerrar()
            except Exception:
                pass
        if self._juego is not None:
            try:
                from cripta.adaptadores.puntajes import RegistroPuntaje, TablaPuntajes

                resumen = self._juego.resumen()
                registro = RegistroPuntaje.desde_resumen(resumen)
                TablaPuntajes(os.path.join(self.directorio_datos, "puntajes.json")).agregar(registro)
            except Exception:
                pass
        if self.vista is not None and self._juego is not None:
            try:
                self.vista.mostrar_fin(self._juego, self.reporte_red())
            except Exception:
                pass

    def reporte_red(self) -> str:
        stats = self.fuente.estadisticas()
        texto = (
            f"Solicitudes: {stats.solicitudes_realizadas}/"
            f"{stats.presupuesto if stats.presupuesto is not None else '?'}; "
            f"429: {stats.respuestas_429}; errores: {stats.errores}"
        )
        if self._catalogo is not None:
            st = self._catalogo.estadisticas()
            texto += (
                f"; caché memoria={st.aciertos_memoria}, disco={st.aciertos_disco}, "
                f"red={st.fallos_red}, desalojos={st.desalojos or self._catalogo.cache.desalojos}"
            )
        return texto

    def _asegurar_contenido(self, sala_id: int) -> None:
        if self._precarga is not None:
            self._precarga.asegurar(sala_id)
