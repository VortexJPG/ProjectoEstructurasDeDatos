import os
import tempfile
import unittest

from cripta.estructuras.tabla_hash import TablaHash, ConjuntoHash
from cripta.estructuras.cola import ColaEnlazada
from cripta.estructuras.ordenamiento import ordenar, busqueda_binaria
from cripta.estructuras.lru import CacheAcotada
from cripta.modelo.acciones import Accion, TipoAccion
from cripta.modelo.datos import Ficha, ContenidoSala
from cripta.adaptadores.fuente_offline import FuenteOffline


class TestTablaHash(unittest.TestCase):
    def test_basico(self):
        t = TablaHash()
        t.insertar("a", 1)
        t.insertar("b", 2)
        self.assertEqual(t.obtener("a"), 1)
        self.assertTrue(t.contiene("b"))
        self.assertTrue(t.eliminar("a"))
        self.assertFalse(t.contiene("a"))


class TestConjuntoHash(unittest.TestCase):
    def test_agregar(self):
        s = ConjuntoHash()
        self.assertTrue(s.agregar(1))
        self.assertFalse(s.agregar(1))
        self.assertEqual(len(s), 1)


class TestCola(unittest.TestCase):
    def test_fifo(self):
        q = ColaEnlazada()
        q.encolar(1)
        q.encolar(2)
        self.assertEqual(q.desencolar(), 1)
        self.assertEqual(q.desencolar(), 2)
        with self.assertRaises(IndexError):
            q.desencolar()


class TestOrdenamiento(unittest.TestCase):
    def test_estabilidad(self):
        datos = [(1, "b"), (2, "a"), (1, "a")]
        res = ordenar(datos, clave=lambda x: x[0])
        self.assertEqual([x[1] for x in res if x[0] == 1], ["b", "a"])

    def test_binaria(self):
        lista = [1, 3, 5, 7]
        self.assertEqual(busqueda_binaria(lista, 5), 2)
        self.assertEqual(busqueda_binaria(lista, 4), -1)


class TestLRU(unittest.TestCase):
    def test_desalojo_y_fijado(self):
        c = CacheAcotada(2)
        c.insertar("a", 1)
        c.insertar("b", 2)
        c.fijar("a")
        c.insertar("c", 3)
        self.assertTrue(c.contiene("a"))
        self.assertTrue(c.contiene("c"))
        self.assertFalse(c.contiene("b"))


class TestAcciones(unittest.TestCase):
    def test_roundtrip(self):
        for a in [
            Accion(TipoAccion.MOVER, direccion="N"),
            Accion(TipoAccion.ATACAR, objetivo="e-1"),
            Accion(TipoAccion.ESPERAR),
            Accion(TipoAccion.RETROCEDER),
        ]:
            self.assertEqual(Accion.desde_linea(a.a_linea()), a)


class TestOffline(unittest.TestCase):
    def test_parse(self):
        base = os.path.join(os.path.dirname(__file__), "..", "datos_ejemplo", "cripta-01")
        f = FuenteOffline(base)
        self.assertEqual(len(f.catalogo(["itm_antidoto"])), 1)
        cs = f.contenido("cripta-01", [2])[0]
        self.assertEqual(cs.sala, 2)


if __name__ == "__main__":
    unittest.main()
