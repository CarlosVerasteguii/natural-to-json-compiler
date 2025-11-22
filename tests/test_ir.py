import sys
import os

# Add src to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)

from analyzer_core import analyze_and_transform
import pytest

def test_ir_create_object():
    input_text = 'CREAR OBJETO usuario CON nombre : "Juan", edad : 30'
    _, _, _, _, error_summary, stats = analyze_and_transform("test_ir_obj", input_text)
    
    ir = stats.get("ir", [])
    if not ir:
        print(f"\nErrors found: {error_summary}")
    assert len(ir) == 3
    
    # 1. Create object
    assert ir[0]["opcode"] == "IR_CREATE_OBJECT"
    assert ir[0]["args"] == ["usuario"]
    
    # 2. Set property nombre
    assert ir[1]["opcode"] == "IR_SET_PROPERTY"
    assert ir[1]["args"][0] == "usuario"
    assert ir[1]["args"][1] == "nombre"
    assert ir[1]["args"][2] == "STRING"
    assert ir[1]["args"][3] == "Juan"
    
    # 3. Set property edad
    assert ir[2]["opcode"] == "IR_SET_PROPERTY"
    assert ir[2]["args"][0] == "usuario"
    assert ir[2]["args"][1] == "edad"
    assert ir[2]["args"][2] == "NUMBER"
    assert ir[2]["args"][3] == 30

def test_ir_create_list():
    input_text = 'CREAR LISTA numeros CON ELEMENTOS 1, 2, 3'
    _, _, _, _, _, stats = analyze_and_transform("test_ir_list", input_text)
    
    ir = stats.get("ir", [])
    assert len(ir) == 4
    
    # 1. Create list
    assert ir[0]["opcode"] == "IR_CREATE_LIST"
    assert ir[0]["args"] == ["numeros"]
    
    # 2. Append 1
    assert ir[1]["opcode"] == "IR_APPEND_LIST"
    assert ir[1]["args"][0] == "numeros"
    assert ir[1]["args"][1] == "NUMBER"
    assert ir[1]["args"][2] == 1
    
    # 3. Append 2
    assert ir[2]["opcode"] == "IR_APPEND_LIST"
    assert ir[2]["args"][2] == 2
    
    # 4. Append 3
    assert ir[3]["opcode"] == "IR_APPEND_LIST"
    assert ir[3]["args"][2] == 3

def test_ir_mixed():
    input_text = '''
    CREAR OBJETO config CON activo : VERDADERO
    CREAR LISTA tags CON ELEMENTOS "v1", "beta"
    '''
    _, _, _, _, _, stats = analyze_and_transform("test_ir_mixed", input_text)
    
    ir = stats.get("ir", [])
    assert len(ir) == 5 # 1 obj + 1 prop + 1 list + 2 appends
    
    assert ir[0]["opcode"] == "IR_CREATE_OBJECT"
    assert ir[0]["args"][0] == "config"
    
    assert ir[1]["opcode"] == "IR_SET_PROPERTY"
    assert ir[1]["args"][1] == "activo"
    assert ir[1]["args"][3] is True
    
    assert ir[2]["opcode"] == "IR_CREATE_LIST"
    assert ir[2]["args"][0] == "tags"
    
    assert ir[3]["opcode"] == "IR_APPEND_LIST"
    assert ir[3]["args"][2] == "v1"
    
    assert ir[4]["opcode"] == "IR_APPEND_LIST"
    assert ir[4]["args"][2] == "beta"
