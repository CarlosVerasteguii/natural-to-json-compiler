# Diseño de Representación Intermedia (IR)

Este documento define la **Representación Intermedia (IR)** para el compilador "Natural a JSON". La IR actúa como un puente entre el análisis sintáctico/semántico y la generación de código final (JSON o Python).

## 1. Descripción General

### 1.1. ¿Qué es una IR?
Una Representación Intermedia (IR) es una estructura de datos que representa el programa fuente de una manera independiente tanto del lenguaje de entrada como del lenguaje de máquina (o salida). En nuestro contexto, es una representación abstracta de las operaciones que el usuario quiere realizar (crear objetos, asignar propiedades) sin estar atada a la sintaxis específica del lenguaje "Natural" ni al formato final JSON.

### 1.2. ¿Por qué una IR explícita?
Actualmente, el compilador traduce directamente del Árbol de Parseo (AST) al JSON final. Introducir una IR explícita ofrece varios beneficios:

1.  **Desacoplamiento**: Separa el *frontend* (análisis) del *backend* (generación). Si mañana queremos generar XML o YAML en lugar de JSON, solo cambiamos el generador de código, no el analizador.
2.  **Optimización**: Permite realizar pasadas de optimización sobre la lista de instrucciones antes de generar el código final. Por ejemplo, detectar y eliminar asignaciones redundantes o fusionar operaciones.
3.  **Depuración y Didáctica**: Facilita ver *qué* está entendiendo el compilador paso a paso, lo cual es fundamental para un curso de Compiladores 2.
4.  **Validación**: Permite comprobaciones adicionales sobre una estructura más simple y lineal que el AST.

---

## 2. Decisión de Diseño: Lista de Instrucciones

Se ha decidido implementar una **IR basada en instrucciones lineales** (similar a un código de tres direcciones o bytecode de alto nivel), en lugar de usar el JSON final como IR o un AST decorado.

### Justificación
*   **Claridad**: Una lista secuencial de operaciones (`CREAR`, `ASIGNAR`, `AGREGAR`) es muy fácil de leer y depurar.
*   **Simplicidad**: Es más fácil escribir un intérprete o generador de código que recorra una lista plana que uno que recorra un árbol complejo.
*   **Extensibilidad**: Agregar nuevas operaciones es trivial.

### Estructura de la IR
La IR será una **lista de objetos de instrucción**. Cada instrucción tendrá:
*   **OpCode**: El código de operación (ej. `CREATE_OBJ`).
*   **Argumentos**: Los datos necesarios para la operación (ej. nombre, valor).

---

## 3. Especificación Formal de la IR

A continuación se definen las instrucciones (OpCodes) disponibles en la IR.

### 3.1. Instrucciones de Objetos

#### `IR_CREATE_OBJECT`
Crea un nuevo objeto vacío en el entorno.
*   **Argumentos**: `nombre` (string)
*   **Significado**: Inicializa un diccionario/objeto vacío asociado al identificador `nombre`.
*   **Ejemplo**: `IR_CREATE_OBJECT("usuario")`

#### `IR_SET_PROPERTY`
Asigna un valor a una propiedad de un objeto existente.
*   **Argumentos**: `nombre_objeto` (string), `clave` (string), `tipo_valor` (string), `valor` (any)
*   **Significado**: `objeto[clave] = valor`
*   **Tipos de valor**: "STRING", "NUMBER", "BOOLEAN".
*   **Ejemplo**: `IR_SET_PROPERTY("usuario", "edad", "NUMBER", 25)`

### 3.2. Instrucciones de Listas

#### `IR_CREATE_LIST`
Crea una nueva lista vacía en el entorno.
*   **Argumentos**: `nombre` (string)
*   **Significado**: Inicializa una lista/array vacío asociado al identificador `nombre`.
*   **Ejemplo**: `IR_CREATE_LIST("colores")`

#### `IR_APPEND_LIST`
Agrega un elemento al final de una lista existente.
*   **Argumentos**: `nombre_lista` (string), `tipo_valor` (string), `valor` (any)
*   **Significado**: `lista.push(valor)`
*   **Ejemplo**: `IR_APPEND_LIST("colores", "STRING", "rojo")`

---

## 4. Mapeo: Natural → IR

El proceso de traducción recorre el Árbol de Parseo y emite instrucciones IR.

### 4.1. Creación de Objetos
**Entrada Natural:**
```text
CREAR OBJETO miObj CON prop1:"val1", prop2:10
```

**Traducción a IR:**
1.  Al encontrar `CREAR OBJETO miObj`:
    *   Emitir: `IR_CREATE_OBJECT("miObj")`
2.  Al procesar `prop1:"val1"`:
    *   Emitir: `IR_SET_PROPERTY("miObj", "prop1", "STRING", "val1")`
3.  Al procesar `prop2:10`:
    *   Emitir: `IR_SET_PROPERTY("miObj", "prop2", "NUMBER", 10)`

### 4.2. Creación de Listas
**Entrada Natural:**
```text
CREAR LISTA miLista CON ELEMENTOS 1, 2
```

**Traducción a IR:**
1.  Al encontrar `CREAR LISTA miLista`:
    *   Emitir: `IR_CREATE_LIST("miLista")`
2.  Al procesar `1`:
    *   Emitir: `IR_APPEND_LIST("miLista", "NUMBER", 1)`
3.  Al procesar `2`:
    *   Emitir: `IR_APPEND_LIST("miLista", "NUMBER", 2)`

---

## 5. Relación IR ↔ JSON ↔ Código Objetivo

La IR sirve como paso intermedio. El flujo completo es:

1.  **Parser**: Natural → AST
2.  **IR Builder**: AST → **IR (Lista de Instrucciones)**
3.  **Code Generator**: **IR** → JSON Final (o Código Python)

### Generación de JSON desde IR
Para generar el JSON final, se recorre la lista de instrucciones y se ejecuta cada una sobre un entorno de datos en memoria:

*   `IR_CREATE_OBJECT(nom)`: `env[nom] = {}`
*   `IR_SET_PROPERTY(nom, k, t, v)`: `env[nom][k] = v`
*   `IR_CREATE_LIST(nom)`: `env[nom] = []`
*   `IR_APPEND_LIST(nom, t, v)`: `env[nom].append(v)`

Al final, `env` contiene la estructura que se serializa a JSON.

### Generación de Código Python (Unidad 3)
En la Unidad 3, en lugar de ejecutar las instrucciones, las traduciremos a código fuente Python:

*   `IR_CREATE_OBJECT("user")` → `user = {}`
*   `IR_SET_PROPERTY("user", "age", "NUMBER", 20)` → `user["age"] = 20`

---

## 6. Ejemplos Completos

### Ejemplo 1: Objeto Simple
**Entrada:**
```text
CREAR OBJETO coche CON marca:"Toyota", año:2020
```

**IR Resultante:**
```text
[
  IR_CREATE_OBJECT("coche"),
  IR_SET_PROPERTY("coche", "marca", "STRING", "Toyota"),
  IR_SET_PROPERTY("coche", "año", "NUMBER", 2020)
]
```

### Ejemplo 2: Lista Mixta
**Entrada:**
```text
CREAR LISTA flags CON ELEMENTOS VERDADERO, FALSO
```

**IR Resultante:**
```text
[
  IR_CREATE_LIST("flags"),
  IR_APPEND_LIST("flags", "BOOLEAN", True),
  IR_APPEND_LIST("flags", "BOOLEAN", False)
]
```

---

## 7. Guía de Implementación (Unidad 2)

### 7.1. Dónde generar la IR
Se debe crear una nueva clase `IRBuilderListener` en `src/analyzer_core.py` (o un módulo nuevo `src/ir_generator.py` si se prefiere modularidad) que herede de `NaturalToJsonListener`.

*   Esta clase mantendrá una lista `self.ir_instructions = []`.
*   En `enterCrear_objeto_cmd`, añadirá `IR_CREATE_OBJECT`.
*   En `exitPropiedad`, añadirá `IR_SET_PROPERTY`.
*   Y así sucesivamente.

### 7.2. Integración
En `analyze_and_transform`:
1.  Ejecutar Lexer y Parser.
2.  Ejecutar SemanticAnalyzer.
3.  Si no hay errores, ejecutar `IRBuilderListener`.
4.  La lista de instrucciones resultante se puede devolver en el diccionario `stats` o como un nuevo valor de retorno para visualización.

### 7.3. Pruebas
Crear `tests/test_ir.py`:
*   Parsear una entrada conocida.
*   Obtener la IR generada.
*   Verificar que la lista de instrucciones coincida exactamente con la esperada (orden y contenido).
