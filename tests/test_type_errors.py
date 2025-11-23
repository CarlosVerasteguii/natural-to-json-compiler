import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analyzer_core import analyze_and_transform

class TestTypeErrors(unittest.TestCase):
    def setUp(self):
        self.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples', 'invalid'))

    def test_domain_rule_edad(self):
        """
        Test SEM005: 'edad' must be a NUMBER.
        Input: CREAR OBJETO usuario CON edad:"veinte"
        """
        input_file = os.path.join(self.examples_dir, 'invalid_type_edad.txt')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        json_out, _, _, _, error_summary, stats = analyze_and_transform("invalid_type_edad.txt", content)
        
        self.assertIsNone(json_out, "JSON should not be generated for semantic errors")
        self.assertGreater(stats['errores_semanticos'], 0, "Should have semantic errors")
        self.assertIn("edad", error_summary)
        self.assertIn("NUMBER", error_summary)

    def test_domain_rule_activo(self):
        """
        Test SEM005: 'activo' must be a BOOLEAN.
        Input: CREAR OBJETO usuario CON activo:123
        """
        input_file = os.path.join(self.examples_dir, 'invalid_type_activo.txt')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        json_out, _, _, _, error_summary, stats = analyze_and_transform("invalid_type_activo.txt", content)
        
        self.assertIsNone(json_out, "JSON should not be generated for semantic errors")
        self.assertGreater(stats['errores_semanticos'], 0, "Should have semantic errors")
        self.assertIn("activo", error_summary)
        self.assertIn("BOOLEAN", error_summary)

    def test_consistency_rule_same_command(self):
        """
        Test SEM006: Duplicate property with different type in same command.
        Input: CREAR OBJETO usuario CON edad:30, edad:"treinta"
        """
        input_file = os.path.join(self.examples_dir, 'invalid_consistency.txt')
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        json_out, _, _, _, error_summary, stats = analyze_and_transform("invalid_consistency.txt", content)
        
        self.assertIsNone(json_out, "JSON should not be generated for semantic errors")
        self.assertGreater(stats['errores_semanticos'], 0, "Should have semantic errors")
        self.assertIn("edad", error_summary)
        self.assertIn("redefinirse", error_summary)

if __name__ == '__main__':
    unittest.main()
