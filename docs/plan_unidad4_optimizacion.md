# Unidad 4: Optimización

## Objetivo
El objetivo de la Unidad 4 es mejorar la calidad de la Representación Intermedia (IR) generada por el compilador antes de que sea traducida al código final (Python/JSON). Esto se logra mediante un módulo de optimización que aplica transformaciones semánticamente seguras para eliminar ineficiencias y mejorar la estructura del código.

## Descripción de la IR
La IR es una lista lineal de instrucciones que abstrae las operaciones del lenguaje fuente. Los opcodes actuales son:
- `IR_CREATE_OBJECT`: Crea un objeto vacío.
- `IR_SET_PROPERTY`: Asigna un valor a una propiedad de un objeto.
- `IR_CREATE_LIST`: Crea una lista vacía.
- `IR_APPEND_LIST`: Agrega un elemento a una lista.

## Optimizaciones Implementadas

### 1. Eliminación de Asignaciones Redundantes (Nivel 1)
Esta optimización detecta cuando se asigna valor a una misma propiedad de un objeto múltiples veces. Dado que en este lenguaje no hay lecturas intermedias, solo el último valor asignado es relevante para el resultado final.

**Ejemplo:**
*   **Antes:**
    ```
    IR_SET_PROPERTY("usuario", "edad", "NUMBER", 20)
    IR_SET_PROPERTY("usuario", "edad", "NUMBER", 25)
    ```
*   **Después:**
    ```
    IR_SET_PROPERTY("usuario", "edad", "NUMBER", 25)
    ```

### 2. Agrupamiento de Instrucciones (Nivel 2)
Esta optimización reordena las instrucciones para mejorar la localidad de referencia. Agrupa todas las operaciones relacionadas con un objeto o lista inmediatamente después de su instrucción de creación.

**Ejemplo:**
*   **Antes:**
    ```
    IR_CREATE_OBJECT("A")
    IR_CREATE_OBJECT("B")
    IR_SET_PROPERTY("A", "x", "NUMBER", 1)
    IR_SET_PROPERTY("B", "y", "NUMBER", 2)
    ```
*   **Después:**
    ```
    IR_CREATE_OBJECT("A")
    IR_SET_PROPERTY("A", "x", "NUMBER", 1)
    IR_CREATE_OBJECT("B")
    IR_SET_PROPERTY("B", "y", "NUMBER", 2)
    ```

## API y Uso
El módulo de optimización se encuentra en `src/optimizer.py`.

```python
from optimizer import optimize_ir

# ir_original es una lista de diccionarios
ir_optimizada = optimize_ir(ir_original)
```

La función `optimize_ir` devuelve una **nueva lista** y no modifica la original.

## Pruebas
Las pruebas unitarias para el optimizador se encuentran en `tests/test_optimizer.py`. Cubren:
- Identidad (IR vacía o sin optimizaciones).
- Eliminación de redundancias.
- Agrupamiento de instrucciones intercaladas.
- Integración semántica (verificación de resultados con `exec`).

Para ejecutar las pruebas:
```bash
pytest tests/test_optimizer.py
```

## Compatibilidad
La implementación de la Unidad 4 es totalmente compatible con las unidades anteriores. Todos los tests existentes (`test_basic`, `test_semantic`, `test_types`, `test_ir`, `test_codegen`) siguen pasando sin modificaciones, asegurando que la optimización es transparente para el usuario final.
