import sys
import os
import json
import pytest

# Add src to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)

from analyzer_core import analyze_and_transform
from codegen import generate_python_from_ir

def test_codegen_object():
    input_text = 'CREAR OBJETO usuario CON nombre:"Juan", edad:30, activo:VERDADERO'

    json_out, _, _, _, _, stats = analyze_and_transform("test_codegen_obj", input_text)
    assert json_out is not None

    ir = stats.get("ir", [])
    assert ir, "IR should not be empty"

    code = generate_python_from_ir(ir)

    env = {}
    exec(code, {}, env)  # Ejecutar código generado en entorno aislado

    # Verificar que se creó la variable 'usuario' correctamente
    assert "usuario" in env
    expected = json.loads(json_out)  # JSON a dict
    assert env["usuario"] == expected["usuario"]

def test_codegen_list():
    input_text = 'CREAR LISTA numeros CON ELEMENTOS 1, 2, 3'

    json_out, _, _, _, _, stats = analyze_and_transform("test_codegen_list", input_text)
    assert json_out is not None

    ir = stats.get("ir", [])
    code = generate_python_from_ir(ir)

    env = {}
    exec(code, {}, env)

    assert "numeros" in env
    expected = json.loads(json_out)
    assert env["numeros"] == expected["numeros"]

def test_codegen_mixed():
    input_text = '''
    CREAR OBJETO config CON debug:FALSO
    CREAR LISTA ips CON ELEMENTOS "192.168.1.1", "127.0.0.1"
    '''
    
    json_out, _, _, _, _, stats = analyze_and_transform("test_codegen_mixed", input_text)
    assert json_out is not None
    
    ir = stats.get("ir", [])
    code = generate_python_from_ir(ir)
    
    env = {}
    exec(code, {}, env)
    
    expected = json.loads(json_out)
    
    assert "config" in env
    assert env["config"] == expected["config"]
    
    assert "ips" in env
    assert env["ips"] == expected["ips"]

def test_codegen_string_escaping():
    # Test para asegurar que las comillas se escapan correctamente
    # Construimos IR manualmente porque el parser actual no soporta escapes en strings
    ir = [
        {"opcode": "IR_CREATE_OBJECT", "args": ["mensaje"]},
        {"opcode": "IR_SET_PROPERTY", "args": ["mensaje", "texto", "STRING", 'Hola "Mundo"']}
    ]
    
    code = generate_python_from_ir(ir)
    
    env = {}
    exec(code, {}, env)
    
    assert "mensaje" in env
    assert env["mensaje"]["texto"] == 'Hola "Mundo"'
