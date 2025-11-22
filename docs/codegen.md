# Diseño de Generación de Código Final (Unidad 3)

Este documento define el diseño para la **Unidad 3** del proyecto, que consiste en transformar la Representación Intermedia (IR) generada en la Unidad 2 en código ejecutable final.

## 1. Descripción General

El objetivo de esta unidad es tomar la lista de instrucciones IR y producir un programa equivalente en un lenguaje de programación real.

### 1.1. Lenguaje Objetivo: Python
Se ha seleccionado **Python** como el lenguaje objetivo para la generación de código.

**Justificación:**
*   **Simplicidad**: La sintaxis de Python para diccionarios y listas es muy similar a la estructura semántica de nuestro lenguaje "Natural".
*   **Legibilidad**: El código generado será fácil de leer y verificar por humanos (profesor/alumnos).
*   **Facilidad de Prueba**: Podemos usar la función `exec()` de Python para ejecutar el código generado dentro de nuestros tests y verificar que los objetos en memoria sean correctos.

### 1.2. Estilo de Código Generado
El código generado será un **script lineal** (sin clases ni funciones envolventes complejas) que declara variables globales para cada objeto o lista creado en el lenguaje original.

Ejemplo conceptual:
```python
# Código generado automáticamente
usuario = {}
usuario["nombre"] = "Juan"
numeros = []
numeros.append(1)
```

---

## 2. Mapeo: IR → Código Python

La traducción se realizará iterando sobre la lista de instrucciones IR y emitiendo líneas de código Python según la siguiente tabla:

### 2.1. Instrucciones de Objetos

| Instrucción IR | Argumentos | Código Python Generado | Notas |
| :--- | :--- | :--- | :--- |
| `IR_CREATE_OBJECT` | `nombre` | `nombre = {}` | Inicializa un diccionario vacío. |
| `IR_SET_PROPERTY` | `obj`, `clave`, `tipo`, `valor` | `obj["clave"] = valor_fmt` | `valor_fmt` depende del tipo (ver 2.3). |

### 2.2. Instrucciones de Listas

| Instrucción IR | Argumentos | Código Python Generado | Notas |
| :--- | :--- | :--- | :--- |
| `IR_CREATE_LIST` | `nombre` | `nombre = []` | Inicializa una lista vacía. |
| `IR_APPEND_LIST` | `lista`, `tipo`, `valor` | `lista.append(valor_fmt)` | `valor_fmt` depende del tipo. |

### 2.3. Formateo de Valores (Literales)

Es crucial formatear correctamente los valores según su tipo para que sean literales válidos en Python:

*   **STRING**: Debe ir entre comillas. Se deben escapar las comillas internas si existen.
    *   IR: `"Hola"` → Python: `"Hola"`
*   **NUMBER**: Se escribe tal cual.
    *   IR: `10` → Python: `10`
    *   IR: `3.14` → Python: `3.14`
*   **BOOLEAN**: Se traduce a `True` o `False` (Python usa mayúsculas).
    *   IR: `True` → Python: `True`
    *   IR: `False` → Python: `False`

---

## 3. Estructura del Módulo de Generación

Se implementará un nuevo módulo o función en `src/codegen.py` (o integrado en `analyzer_core.py` si se prefiere).

### 3.1. Función Principal

```python
def generate_python_from_ir(ir_instructions):
    """
    Toma una lista de instrucciones IR y genera código Python.
    
    Args:
        ir_instructions (list): Lista de dicts con 'opcode' y 'args'.
        
    Returns:
        str: Código Python completo como string.
    """
    python_code = []
    python_code.append("# --- Codigo Generado ---")
    
    for instr in ir_instructions:
        opcode = instr["opcode"]
        args = instr["args"]
        
        if opcode == "IR_CREATE_OBJECT":
            nombre = args[0]
            python_code.append(f"{nombre} = {{}}")
            
        elif opcode == "IR_SET_PROPERTY":
            nombre, clave, tipo, valor = args
            valor_fmt = format_value(valor, tipo)
            python_code.append(f"{nombre}[\"{clave}\"] = {valor_fmt}")
            
        elif opcode == "IR_CREATE_LIST":
            nombre = args[0]
            python_code.append(f"{nombre} = []")
            
        elif opcode == "IR_APPEND_LIST":
            nombre, tipo, valor = args
            valor_fmt = format_value(valor, tipo)
            python_code.append(f"{nombre}.append({valor_fmt})")
            
    return "\n".join(python_code)
```

### 3.2. Helper de Formateo

```python
def format_value(valor, tipo):
    if tipo == "STRING":
        return f'"{valor}"' # Idealmente usar repr(valor) para seguridad
    elif tipo == "BOOLEAN":
        return "True" if valor else "False"
    else: # NUMBER
        return str(valor)
```

---

## 4. Ejemplos Completos

### Ejemplo 1: Objeto Simple

**Entrada Natural:**
```text
CREAR OBJETO usuario CON nombre:"Juan", edad:30, activo:VERDADERO
```

**IR (Entrada al generador):**
```python
[
  {"opcode": "IR_CREATE_OBJECT", "args": ["usuario"]},
  {"opcode": "IR_SET_PROPERTY", "args": ["usuario", "nombre", "STRING", "Juan"]},
  {"opcode": "IR_SET_PROPERTY", "args": ["usuario", "edad", "NUMBER", 30]},
  {"opcode": "IR_SET_PROPERTY", "args": ["usuario", "activo", "BOOLEAN", True]}
]
```

**Código Python Generado (Salida):**
```python
# --- Codigo Generado ---
usuario = {}
usuario["nombre"] = "Juan"
usuario["edad"] = 30
usuario["activo"] = True
```

### Ejemplo 2: Lista de Números

**Entrada Natural:**
```text
CREAR LISTA notas CON ELEMENTOS 10, 8, 9
```

**IR:**
```python
[
  {"opcode": "IR_CREATE_LIST", "args": ["notas"]},
  {"opcode": "IR_APPEND_LIST", "args": ["notas", "NUMBER", 10]},
  {"opcode": "IR_APPEND_LIST", "args": ["notas", "NUMBER", 8]},
  {"opcode": "IR_APPEND_LIST", "args": ["notas", "NUMBER", 9]}
]
```

**Código Python Generado:**
```python
# --- Codigo Generado ---
notas = []
notas.append(10)
notas.append(8)
notas.append(9)
```

### Ejemplo 3: Mixto (Variables Múltiples)

**Entrada Natural:**
```text
CREAR OBJETO config CON debug:FALSO
CREAR LISTA ips CON ELEMENTOS "192.168.1.1", "127.0.0.1"
```

**Código Python Generado:**
```python
# --- Codigo Generado ---
config = {}
config["debug"] = False
ips = []
ips.append("192.168.1.1")
ips.append("127.0.0.1")
```

---

## 5. Estrategia de Pruebas

Para validar que la generación de código es correcta, no basta con comparar strings (que es frágil ante cambios de espaciado). Ejecutaremos el código generado.

### 5.1. Nuevo Archivo de Tests: `tests/test_codegen.py`

Se creará un archivo de pruebas que realice el siguiente flujo para cada caso de prueba:

1.  **Analizar**: Convertir código Natural a IR (usando `analyze_and_transform`).
2.  **Generar**: Convertir IR a Código Python (usando la nueva función `generate_python_from_ir`).
3.  **Ejecutar**: Usar `exec()` para correr el código generado en un entorno aislado.
4.  **Verificar**: Comprobar que las variables en el entorno de `exec` coinciden con lo esperado.

### 5.2. Ejemplo de Test

```python
def test_codegen_object():
    # 1. Setup
    input_text = 'CREAR OBJETO p1 CON x:10, y:20'
    
    # 2. Obtener IR
    _, _, _, _, _, stats = analyze_and_transform("test_code", input_text)
    ir = stats["ir"]
    
    # 3. Generar Python
    code = generate_python_from_ir(ir)
    
    # 4. Ejecutar
    env = {}
    exec(code, {}, env)
    
    # 5. Verificar
    assert "p1" in env
    assert env["p1"] == {"x": 10, "y": 20}
```

### 5.3. Ventajas de esta estrategia
*   **Validación Semántica**: Asegura que el código generado *hace* lo que debe hacer, no solo que *parece* correcto.
*   **Independencia del JSON**: Comparamos el resultado de la ejecución del código Python generado contra la verdad esperada, cerrando el ciclo completo del compilador.
