import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analyzer_core import analyze_and_transform

class TestTypeInfrastructure(unittest.TestCase):
    def setUp(self):
        self.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples', 'valid'))

    def test_type_metadata_population(self):
        """
        Verifies that type metadata is correctly populated in the symbol table
        and exposed via stats['symbols_debug'].
        """
        # Create a simple valid input directly
        input_content = """
        CREAR OBJETO usuario CON nombre:"Juan", edad:30, activo:VERDADERO
        CREAR LISTA numeros CON ELEMENTOS 1, 2, 3
        """
        
        json_out, _, _, _, _, stats = analyze_and_transform("test_input", input_content)
        
        self.assertIsNotNone(json_out, "JSON should be generated")
        self.assertIn('symbols_debug', stats, "stats should contain 'symbols_debug'")
        
        symbols = stats['symbols_debug']
        
        # Verify 'usuario' object
        self.assertIn('usuario', symbols)
        usuario = symbols['usuario']
        self.assertEqual(usuario['tipo_entidad'], 'objeto')
        self.assertIn('propiedades', usuario['metadatos'])
        props = usuario['metadatos']['propiedades']
        self.assertEqual(props['nombre'], 'STRING')
        self.assertEqual(props['edad'], 'NUMBER')
        self.assertEqual(props['activo'], 'BOOLEAN')
        
        # Verify 'numeros' list
        self.assertIn('numeros', symbols)
        numeros = symbols['numeros']
        self.assertEqual(numeros['tipo_entidad'], 'lista')
        self.assertIn('tipos_elementos', numeros['metadatos'])
        elements = numeros['metadatos']['tipos_elementos']
        self.assertEqual(elements, ['NUMBER', 'NUMBER', 'NUMBER'])

if __name__ == '__main__':
    unittest.main()
