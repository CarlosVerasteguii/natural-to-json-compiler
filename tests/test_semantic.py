import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analyzer_core import analyze_and_transform

class TestSemanticAnalysis(unittest.TestCase):
    def setUp(self):
        self.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples', 'invalid'))

    def _run_semantic_test(self, filename, expected_error_fragment, expect_semantic_error=True):
        filepath = os.path.join(self.examples_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        json_out, tokens, lisp_tree, qt_model, error_summary, stats = analyze_and_transform(filename, content)
        
        # 1. JSON should be None (blocked by error)
        self.assertIsNone(json_out, f"JSON should not be generated for {filename}")
        
        if expect_semantic_error:
            # 2. Should have semantic errors
            self.assertGreater(stats['errores_semanticos'], 0, f"Should have semantic errors in {filename}")
            # 3. Should NOT have lexical or syntax errors
            self.assertEqual(stats['errores_lexicos'], 0, f"Should have 0 lexical errors in {filename}")
            self.assertEqual(stats['errores_sintacticos'], 0, f"Should have 0 syntax errors in {filename}")
            # 4. Error summary should contain specific text
            self.assertIn(expected_error_fragment, error_summary, f"Error message should contain '{expected_error_fragment}'")
        else:
            # For cases where syntax error preempts semantic error (e.g. reserved words)
            self.assertTrue(stats['errores_sintacticos'] > 0 or stats['errores_semanticos'] > 0, 
                            f"Should have syntax or semantic errors in {filename}")

    def test_sem001_redef_objeto(self):
        """Test SEM001: Redefinition of object"""
        self._run_semantic_test('invalid_sem_redef_objeto.txt', "Redefinición del símbolo", expect_semantic_error=True)

    def test_sem001_redef_lista(self):
        """Test SEM001: Redefinition of list"""
        self._run_semantic_test('invalid_sem_redef_lista.txt', "Redefinición del símbolo", expect_semantic_error=True)

    def test_sem002_reserved_objeto(self):
        """Test SEM002: Reserved word as object name (Preempted by Syntax Error)"""
        # Note: This triggers a syntax error because 'CREAR' is a keyword, not an identifier.
        # The semantic check is effectively unreachable for keywords defined in the grammar.
        self._run_semantic_test('invalid_sem_reserved_objeto.txt', "palabra reservada", expect_semantic_error=False)

    def test_sem002_reserved_lista(self):
        """Test SEM002: Reserved word as list name (Preempted by Syntax Error)"""
        # Note: This triggers a syntax error because 'ELEMENTOS' is a keyword.
        self._run_semantic_test('invalid_sem_reserved_lista.txt', "palabra reservada", expect_semantic_error=False)

if __name__ == '__main__':
    unittest.main()
