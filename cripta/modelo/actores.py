"""Actores: jugador y enemigos.                                      [Persona A]

§2.2. Dos enemigos del mismo tipo comparten la ficha de catálogo pero son
actores distintos: cada uno tiene su vida, sala, id de instancia y tiempo de
próxima acción.

Decisión a documentar: el enemigo COPIA sus estadísticas base de la ficha al
crearse (no vuelve a consultar la caché en cada turno) o las consulta cada
vez. Copiar evita búsquedas en la simulación; consultar mantiene una sola
fuente de verdad. Midan y elijan.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cripta.estructuras.lista_doble import NodoDoble
    from cripta.modelo.datos import EstadisticasIniciales, Ficha
    from cripta.modelo.efectos import Efecto
    from cripta.modelo.eventos import Evento
    from cripta.modelo.inventario import Inventario
    from cripta.modelo.mapa import Sala
    from cripta.modelo.objetos import InstanciaObjeto


class Comportamiento(Enum):
    GUARDIAN = "guardián"
    ERRANTE = "errante"
    RASTREADOR = "rastreador"

    @staticmethod
    def desde_texto(texto: str) -> Comportamiento:
        """Convierte el texto de la ficha. ValueError si no es válido."""
        raise NotImplementedError


class Actor:
    """Base común. ``vida`` nunca supera ``vida_max``; en 0 el actor muere."""

    id: str
    vida: int
    vida_max: int
    ataque_base: int
    defensa_base: int
    velocidad_base: int
    sala: Sala
    tiempo_siguiente: int | None
    evento_turno: Evento | None  # para cancelar / reprogramar en O(1)
    modificador_velocidad: int  # suma de los efectos de velocidad activos

    def __init__(
        self,
        id: str,
        vida: int,
        vida_max: int,
        ataque: int,
        defensa: int,
        velocidad: int,
        sala: Sala,
    ) -> None:
        raise NotImplementedError

    @property
    def ataque(self) -> int:
        """Ataque efectivo (base + bonos)."""
        raise NotImplementedError

    @property
    def defensa(self) -> int:
        """Defensa efectiva (base + bonos)."""
        raise NotImplementedError

    @property
    def velocidad(self) -> int:
        """Velocidad efectiva (base + modificadores). Definir un mínimo > 0."""
        raise NotImplementedError

    def esta_vivo(self) -> bool:
        raise NotImplementedError

    def etiqueta(self) -> str:
        """Nombre que se muestra en la interfaz."""
        raise NotImplementedError


class Jugador(Actor):
    """El jugador. Sus estadísticas iniciales vienen de los datos de la cripta."""

    nombre: str
    inventario: Inventario
    arma: InstanciaObjeto | None
    armadura: InstanciaObjeto | None
    bono_ataque: int  # ataque_bonus del arma equipada (se fija al equipar)
    bono_defensa: int  # defensa_bonus de la armadura equipada
    veneno: Efecto | None
    efecto_velocidad: Efecto | None
    antorcha: Efecto | None
    acciones_ejecutadas: int  # solo acciones que consumen tiempo (§2.12)
    enemigos_derrotados: int
    abrio_puerta_salida: bool  # condición de victoria (§2.12)

    def __init__(
        self,
        nombre: str,
        estadisticas: EstadisticasIniciales,
        sala: Sala,
        inventario: Inventario,
    ) -> None:
        raise NotImplementedError

    def tiene_llave(self, llave_id: str) -> bool:
        """True si hay en el inventario un objeto de clase llave con ese id de tipo."""
        raise NotImplementedError


class Enemigo(Actor):
    """Instancia concreta de enemigo."""

    tipo_id: str
    nombre_tipo: str
    numero: int  # para mostrar "Rata gigante #2"; asignado de forma determinista
    comportamiento: Comportamiento
    activo: bool  # se activa cuando el jugador entra a su sala (§2.4)
    suelta: list[str]  # ids de tipo que deja en el suelo al morir
    regeneracion: Efecto | None
    nodo_en_sala: NodoDoble[Enemigo] | None  # para sacarlo de su sala en O(1)

    def __init__(
        self,
        instancia: str,
        ficha: Ficha,
        vida_inicial: int | None,
        numero: int,
        sala: Sala,
    ) -> None:
        """``vida_inicial`` None → empieza con ``vida_max`` (API real, e-401)."""
        raise NotImplementedError

    def etiqueta(self) -> str:
        """Por ejemplo "Rata gigante #1"."""
        raise NotImplementedError
