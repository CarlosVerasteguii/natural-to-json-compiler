# Walkthrough: Migración a Compiladores 2

Este documento resume cómo se migró el proyecto **"Natural a JSON"** (desarrollado en
Sistemas de Base 1 / Compiladores 1) a la estructura requerida para **Compiladores 2**,
y cómo verificar que el setup está correcto antes de continuar con la Unidad 1
(Análisis Semántico).

## Objetivos de la migración

1. Establecer una estructura de directorios profesional y escalable.
2. Separar claramente:
   - Código fuente (`src/`)
   - Documentación (`docs/`)
   - Ejemplos (`examples/`)
   - Pruebas automatizadas (`tests/`)
3. Unificar los ejemplos en una ubicación oficial (`examples/`).
4. Proteger el comportamiento actual del analizador mediante pruebas automatizadas.

## Cambios realizados

### 1. Reestructuración de directorios

- Todo el código fuente se movió a la carpeta `src/`.
- Se creó `examples/` como **fuente oficial de casos de prueba**:
  - `examples/valid/`: archivos de entrada correctos del lenguaje.
  - `examples/invalid/`: archivos con errores léxicos y/o sintácticos.
  - `examples/expected/`: salidas JSON esperadas para algunos casos válidos.
- Se creó `tests/` para alojar las pruebas automatizadas del compilador.
- Se creó `docs/` para documentación técnica y planes futuros.
- La carpeta `src/ejemplos_entrada/` se mantiene como material histórico y de
  referencia adicional, pero no es la fuente principal de pruebas.

### 2. Ajustes en el código

- `src/analyzer_core.py`:
  - Ahora localiza la carpeta `src/generated/` de forma **relativa a su propia ruta**,
    permitiendo ejecutar el proyecto desde la raíz sin problemas de `sys.path`.

- `src/main_cli.py`:
  - Implementa un **menú interactivo** que permite trabajar con:
    - `examples/valid/` (casos válidos)
    - `examples/invalid/` (casos inválidos)
  - Admite procesar directamente un archivo pasado como argumento, por ejemplo:
    - `python src/main_cli.py examples/valid/valid_01.txt`
  - Usa rutas relativas a la raíz del proyecto para encontrar la carpeta `examples/`.

- `src/main_gui.py`:
  - Usa `examples/valid/` como **directorio inicial por defecto** al pulsar
    el botón *"Cargar Archivo..."*.
  - Recuerda el último directorio utilizado mediante `QSettings`, de modo que
    el diálogo de apertura resulta cómodo en sesiones sucesivas.

### 3. Pruebas automatizadas

- `tests/test_basic.py`:
  - Procesa todos los archivos en `examples/valid/` y verifica que:
    - No se reporten errores.
    - La salida JSON generada coincida exactamente con los archivos de referencia
      en `examples/expected/` (por ejemplo, `valid_01.json`).
  - Procesa todos los archivos en `examples/invalid/` y verifica que **sí**
    se reporten errores.
- Estas pruebas sirven como **red de seguridad** cuando se agreguen nuevas fases
  (análisis semántico, IR, código final, optimizaciones), evitando regresiones en
  la funcionalidad léxico/sintáctica ya implementada.

## Checklist de Setup (estado actual)

- [x] Código migrado a `src/` con rutas relativas robustas.
- [x] Estructura `examples/` completa (`valid`, `invalid`, `expected`).
- [x] Pruebas automatizadas (`tests/test_basic.py`) verificando salida JSON exacta.
- [x] GUI y CLI configuradas para usar `examples/` por defecto.
- [x] Documentación actualizada (`README.md`, `docs/walkthrough.md`,
      `docs/objetivo_bonus_webapp.md`).

## Cómo verificar la migración

Todas las instrucciones asumen que estás en la raíz del proyecto:
`ProyectoCompiladores2/`.

1. **Instalar dependencias**

```bash
pip install antlr4-python3-runtime PyQt5
```

2. **Ejecutar pruebas automatizadas**

```bash
python tests/test_basic.py
```

- Debe mostrar `OK` y, en la salida, los nombres de los archivos válidos e inválidos
  que se están probando.

3. **Probar la interfaz GUI**

```bash
python src/main_gui.py
```

- En la aplicación:
  - Pulsar *"Cargar Archivo..."*.
  - Verificar que el diálogo de apertura se sitúe en `examples/valid/` (o en el
    último directorio utilizado).
  - Cargar un archivo de prueba y ejecutar el análisis.

4. **Probar la interfaz CLI**

```bash
python src/main_cli.py examples/valid/valid_01.txt
```

o, para modo interactivo:

```bash
python src/main_cli.py
```

- En modo interactivo:
  - Elegir `1` para ejemplos válidos o `2` para ejemplos inválidos.
  - Seleccionar un archivo por número o usar la opción `todos`.

## Siguientes pasos

Con esta migración completada y protegida por pruebas, el proyecto está listo
para comenzar la **Unidad 1: Análisis Semántico**.

## Estado Actual (Unidad 1: Análisis Semántico)

### Cambios Realizados
1.  **Tabla de Símbolos:**
    *   Se implementaron las clases `SymbolEntry` y `SymbolTable` en `src/analyzer_core.py`.
    *   Se soporta la declaración de objetos y listas en un ámbito global.

2.  **Detección de Errores Semánticos:**
    *   Se implementó el listener `SemanticAnalyzer`.
    *   **SEM001 (Redefinición):** Se detecta si un símbolo se declara más de una vez.
    *   **SEM002 (Palabras Reservadas):** Se detecta si se intenta usar una palabra clave como identificador (cuando no es capturado por el parser).
    *   Se integró el conteo de errores semánticos en `CustomErrorListener` y en las estadísticas finales.

3.  **Integración:**
    *   El análisis semántico se ejecuta automáticamente después del análisis sintáctico exitoso.
    *   Si se detectan errores semánticos, **se bloquea la generación de JSON**.

### Verificación
- [x] `python tests/test_basic.py` sigue pasando (sin regresiones).
- [x] **NUEVO**: Se creó `tests/test_semantic.py` para verificar errores semánticos.
    - **SEM001 (Redefinición)**: Verificado exitosamente (bloquea JSON).
    - **SEM002 (Palabras Reservadas)**: Verificado que el uso de palabras clave como identificadores bloquea la generación de JSON (aunque actualmente es detectado como error sintáctico por la precedencia del parser).
- [x] Se añadieron 4 archivos de prueba inválidos en `examples/invalid/` cubriendo estos casos.
- [x] **NUEVO (Paso 2)**: Se implementó la infraestructura de tipos.
    - Se identifican tipos `STRING`, `NUMBER`, `BOOLEAN`.
    - Se almacenan metadatos de tipos en la Tabla de Símbolos.
    - Se verificó con `tests/test_types.py` que la información se registra correctamente.

### Siguientes Pasos
- **Paso 3:** Validaciones avanzadas (opcional).
A partir de este punto, cualquier cambio en el compilador deberá mantener
`python tests/test_basic.py` en estado `OK` para asegurar que no se rompa la
funcionalidad de análisis léxico/sintáctico ni la generación actual de JSON.
