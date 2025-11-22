import sys
import os
sys.path.append('src')
from analyzer_core import analyze_and_transform

input_text = 'CREAR OBJETO mensaje CON texto:"Hola \\"Mundo\\""'
print(f"Input: {input_text}")
json_out, _, _, _, error_summary, stats = analyze_and_transform("debug_esc", input_text)

if json_out is None:
    print("Parsing failed!")
    print(error_summary)
else:
    print("Parsing success!")
    print(json_out)
