# Plan Unidad 1 – Análisis Semántico

Este plan describe los pasos para implementar la **Unidad 1: Análisis Semántico**
del compilador/traductor "Natural a JSON" dentro del proyecto de Compiladores 2.

La idea es avanzar en iteraciones pequeñas, apoyándonos siempre en las pruebas
existentes para no romper el análisis léxico/sintáctico ni la generación de JSON.

---

## Objetivo general

Agregar una capa de **análisis semántico** sobre el lenguaje "Natural a JSON"
que permita detectar errores más allá de la sintaxis, mediante:

- Una **tabla de símbolos** para registrar objetos y listas declarados.
- Reglas de **tipos** para los valores (string, número, booleano).
- Reglas básicas de **alcance/visibilidad** y consistencia de nombres.

Todo esto debe integrarse con el sistema de errores existente y conservar la
compatibilidad con la salida JSON actual (las pruebas de `tests/test_basic.py`
deben seguir pasando).

---

## Paso 0 – Diseñar las reglas semánticas (documentación)

> Archivo: `docs/semantica.md` (a crear)

Definir por escrito, antes de programar, las reglas que se considerarán
errores semánticos. Por ejemplo:

- **Tabla de símbolos:**
  - Registrar cada *nombre de objeto* y *nombre de lista* declarados.
  - No permitir redefinir un objeto/lista con el mismo nombre en el mismo
    programa.

- **Reglas de tipos:**
  - Los valores pueden ser: string, número (entero/decimal) o booleano.
  - Una vez que una clave se usa con cierto tipo, opcionalmente se puede
    exigir coherencia en otras apariciones (decisión a documentar).

- **Alcance/visibilidad:**
  - Reportar error si se hace referencia a un objeto/lista no declarados
    (si se introduce alguna operación que lo requiera).

- **Ejemplos:**
  - Al menos 2–3 ejemplos de entradas válidas y 2–3 con errores semánticos,
    explicando qué regla se viola.

---

## Paso 1 – Tabla de símbolos en `analyzer_core.py`

> Archivo principal a modificar: `src/analyzer_core.py`

1.1. Diseñar estructuras de datos simples:

- Clases o estructuras como:
  - `SymbolEntry` (nombre, tipo de entidad: objeto/lista, metadatos).
  - `SymbolTable` (diccionario interno, operaciones de insertar/buscar,
    detección de redefiniciones).

1.2. Integración con el recorrido del árbol:

- Identificar en qué puntos del listener/visitor se crean objetos/listas
  (por ejemplo, reglas `crear_objeto_cmd`, `crear_lista_cmd`).
- En esos puntos:
  - Registrar la declaración en la tabla de símbolos.
  - Si el nombre ya existe, generar un **error semántico** y almacenarlo en
    la lista de errores (sin romper el resto del análisis).

---

## Paso 2 – Comprobación de tipos básicos

> Archivo principal a modificar: `src/analyzer_core.py`

2.1. Definir cómo representar tipos internamente:

- Enum simple (`STRING`, `NUMBER`, `BOOLEAN`) o cadenas constantes.

2.2. Asociar tipos a valores:

- Durante el recorrido del árbol, cuando se procesan valores:
  - Identificar si son string, número o booleano.
  - (Opcional) Guardar esta información asociada a cada clave/valor.

2.3. Reglas de tipo mínimas:

- Detectar casos evidentes de tipo incorrecto según las reglas que se
  documenten en `docs/semantica.md` (por ejemplo, si se define una clave
  que intencionalmente debe ser número y se pasa un string).

2.4. Manejo de errores de tipo:

- Agregar mensajes de error semántico descriptivos (en español) al
  sistema actual de errores, diferenciándolos de los errores léxicos y
  sintácticos.

---

## Paso 3 – Alcance/visibilidad (nivel básico)

> Archivo principal a modificar: `src/analyzer_core.py`

- Según las capacidades del lenguaje actual, agregar reglas sencillas de
  visibilidad, por ejemplo:
  - Evitar el uso de nombres reservados.
  - Detectar inconsistencias obvias de nombres (si se introduce alguna
    construcción que lo requiera).

> Nota: como el lenguaje actual es bastante plano (declaraciones de objetos
> y listas al mismo nivel), el alcance puede ser simple. Lo importante es
> dejar preparada la infraestructura para futuras extensiones.

---

## Paso 4 – Casos de prueba semánticos

> Archivos a modificar/agregar: `examples/` y `tests/`

4.1. Nuevos ejemplos:

- Agregar **casos válidos** que ejerciten las nuevas reglas semánticas,
  por ejemplo:
  - Declaraciones múltiples coherentes.
  - Uso de todos los tipos de valores.

- Agregar **casos inválidos** con errores semánticos, por ejemplo:
  - Redefinición de un mismo objeto/lista.
  - Valores de tipo claramente incorrecto respecto a lo documentado.

4.2. Pruebas automatizadas:

- Crear un archivo de pruebas adicional (por ejemplo `tests/test_semantic.py`)
  o extender `tests/test_basic.py` para que:
  - Verifique que los nuevos casos válidos **no** produzcan errores.
  - Verifique que los casos inválidos **sí** produzcan errores semánticos.

4.3. Mantener compatibilidad:

- Asegurarse de que `python tests/test_basic.py` siga en estado `OK`.
  Si cambian detalles menores del JSON, actualizar solamente los expected
  cuando sea estrictamente necesario.

---

## Paso 5 – Documentar el estado final de la Unidad 1

> Archivos: `docs/semantica.md`, `README.md`, `docs/walkthrough.md`

- Actualizar `docs/semantica.md` con lo realmente implementado (no solo lo
  planeado), incluyendo ejemplos antes/después.
- Añadir al README una breve sección que indique que la Unidad 1 está
  implementada y qué tipo de errores semánticos se detectan.
- Si es necesario, agregar una breve nota en `docs/walkthrough.md` para
  mencionar que, además del setup, ahora existe análisis semántico básico
  y cómo se prueba.

---

## Criterio de “Unidad 1 completada”

Se considerará que la Unidad 1 está razonablemente completa cuando:

- Exista una descripción clara de las reglas semánticas en `docs/semantica.md`.
- `src/analyzer_core.py` tenga:
  - Una tabla de símbolos funcional.
  - Manejo básico de tipos y nombres.
  - Reporte de errores semánticos integrado al flujo de errores actual.
- Haya ejemplos semánticos (válidos e inválidos) específicos en `examples/`.
- Haya pruebas automatizadas que cubran estos ejemplos y sigan pasando junto
  con `tests/test_basic.py`.

