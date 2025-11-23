
import unittest
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from optimizer import optimize_ir
from codegen import generate_python_from_ir
from analyzer_core import analyze_and_transform

class TestOptimizer(unittest.TestCase):
    
    def test_identity_empty(self):
        """Test que una lista vacía retorna lista vacía."""
        ir = []
        optimized = optimize_ir(ir)
        self.assertEqual(optimized, [])
        
    def test_identity_no_optimization(self):
        """Test que una IR sin redundancias ni desorden se mantiene igual."""
        ir = [
            {"opcode": "IR_CREATE_OBJECT", "args": ["obj1"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["obj1", "prop1", "NUMBER", 1]},
            {"opcode": "IR_CREATE_LIST", "args": ["list1"]},
            {"opcode": "IR_APPEND_LIST", "args": ["list1", "STRING", "val1"]}
        ]
        optimized = optimize_ir(ir)
        self.assertEqual(optimized, ir)
        
    def test_redundancy_elimination(self):
        """Test que elimina asignaciones redundantes (mismo objeto, misma clave)."""
        ir = [
            {"opcode": "IR_CREATE_OBJECT", "args": ["user"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["user", "name", "STRING", "Juan"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["user", "name", "STRING", "Pedro"]} # Sobrescribe
        ]
        
        optimized = optimize_ir(ir)
        
        # Debería quedar solo la creación y la última asignación
        expected = [
            {"opcode": "IR_CREATE_OBJECT", "args": ["user"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["user", "name", "STRING", "Pedro"]}
        ]
        self.assertEqual(optimized, expected)
        
    def test_grouping_interleaved(self):
        """Test que agrupa instrucciones intercaladas de diferentes objetos."""
        ir = [
            {"opcode": "IR_CREATE_OBJECT", "args": ["A"]},
            {"opcode": "IR_CREATE_OBJECT", "args": ["B"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["A", "x", "NUMBER", 1]},
            {"opcode": "IR_SET_PROPERTY", "args": ["B", "y", "NUMBER", 2]},
            {"opcode": "IR_SET_PROPERTY", "args": ["A", "z", "NUMBER", 3]}
        ]
        
        optimized = optimize_ir(ir)
        
        # Esperamos: Crear A, props de A, Crear B, props de B
        # Nota: El orden relativo de props de A se debe mantener (x antes que z)
        expected = [
            {"opcode": "IR_CREATE_OBJECT", "args": ["A"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["A", "x", "NUMBER", 1]},
            {"opcode": "IR_SET_PROPERTY", "args": ["A", "z", "NUMBER", 3]},
            {"opcode": "IR_CREATE_OBJECT", "args": ["B"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["B", "y", "NUMBER", 2]}
        ]
        self.assertEqual(optimized, expected)
        
    def test_integration_semantics(self):
        """
        Test de integración: Verifica que la optimización no rompe la semántica
        ejecutando el código generado.
        """
        # Caso con redundancia y desorden
        ir = [
            {"opcode": "IR_CREATE_OBJECT", "args": ["data"]},
            {"opcode": "IR_CREATE_LIST", "args": ["items"]},
            {"opcode": "IR_SET_PROPERTY", "args": ["data", "val", "NUMBER", 10]},
            {"opcode": "IR_SET_PROPERTY", "args": ["data", "val", "NUMBER", 20]}, # Redundante
            {"opcode": "IR_APPEND_LIST", "args": ["items", "NUMBER", 1]},
            {"opcode": "IR_APPEND_LIST", "args": ["items", "NUMBER", 2]}
        ]
        
        optimized = optimize_ir(ir)
        
        # Generar código Python desde la IR optimizada
        py_code = generate_python_from_ir(optimized)
        
        # Ejecutar
        env = {}
        exec(py_code, {}, env)
        
        # Verificar resultados en env
        self.assertEqual(env["data"]["val"], 20) # Debe tener el último valor
        self.assertEqual(env["items"], [1, 2])
        
    def test_no_mutation(self):
        """Asegura que la lista original no se modifica."""
        ir = [{"opcode": "IR_CREATE_OBJECT", "args": ["test"]}]
        ir_copy = list(ir)
        optimize_ir(ir)
        self.assertEqual(ir, ir_copy)

if __name__ == '__main__':
    unittest.main()
