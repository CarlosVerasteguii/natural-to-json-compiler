import sys
import os
import unittest
import json

# Add src to sys.path to import analyzer_core
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)

from analyzer_core import analyze_and_transform

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.examples_dir = os.path.join(os.path.dirname(current_dir), 'examples')

    def test_valid_examples(self):
        valid_dir = os.path.join(self.examples_dir, 'valid')
        for filename in os.listdir(valid_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(valid_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"Testing valid file: {filename}")
                json_out, _, _, _, errors, _ = analyze_and_transform(filename, content)
                
                self.assertFalse(errors, f"Valid file {filename} produced errors: {errors}")
                self.assertIsNotNone(json_out, f"Valid file {filename} did not produce JSON")
                
                # Verify against expected output
                expected_filename = os.path.splitext(filename)[0] + '.json'
                expected_path = os.path.join(self.examples_dir, 'expected', expected_filename)
                
                if os.path.exists(expected_path):
                    with open(expected_path, 'r', encoding='utf-8') as f:
                        expected_json = json.load(f)
                    
                    try:
                        actual_json = json.loads(json_out)
                        self.assertEqual(actual_json, expected_json, f"Output for {filename} does not match expected JSON")
                    except json.JSONDecodeError:
                        self.fail(f"Output for {filename} is not valid JSON")
                else:
                    print(f"Warning: No expected JSON found for {filename} at {expected_path}")
                    # Fallback to just checking if it's valid JSON
                    try:
                        json.loads(json_out)
                    except json.JSONDecodeError:
                        self.fail(f"Output for {filename} is not valid JSON")

    def test_invalid_examples(self):
        invalid_dir = os.path.join(self.examples_dir, 'invalid')
        for filename in os.listdir(invalid_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(invalid_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"Testing invalid file: {filename}")
                _, _, _, _, errors, _ = analyze_and_transform(filename, content)
                
                self.assertTrue(errors, f"Invalid file {filename} should have produced errors but didn't")

if __name__ == '__main__':
    unittest.main()
