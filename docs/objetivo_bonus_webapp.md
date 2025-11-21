# Objetivo Bonus (Futuro): Versión Web y Target JavaScript

> Este objetivo **no es parte obligatoria** del producto integrador de Compiladores 2.
> Es una meta extra para el futuro, pensada como proyecto de portafolio una vez que
> el compilador en Python (CLI + pruebas + GUI) esté completamente terminado.

## Visión General

Tomar el compilador/traductor "Natural a JSON" desarrollado en Python con ANTLR4
y crear una versión **totalmente web**, capaz de ejecutarse en el navegador y
ser desplegada (por ejemplo) en **Vercel**.

La idea es que el usuario pueda abrir una página, escribir instrucciones en el
lenguaje "Natural a JSON" y ver:

- Tokens
- Árbol de análisis (parse tree / AST)
- JSON generado
- Representación intermedia (IR)
- Código final
- Mensajes de error (léxicos, sintácticos, semánticos)

Todo eso **sin necesidad de tener Python instalado**, porque el análisis correría
del lado del cliente (en JavaScript/TypeScript).

## Punto de Partida (Proyecto Actual)

El núcleo actual del proyecto está en Python:

- Gramática ANTLR: `NaturalToJson.g4`
- Generadores de Python en `src/generated/`
- Lógica principal en `src/analyzer_core.py`
- Interfaces:
  - CLI: `src/main_cli.py`
  - GUI (PyQt5): `src/main_gui.py`
- Ejemplos y pruebas:
  - `examples/valid`, `examples/invalid`, `examples/expected`
  - `tests/test_basic.py`

La idea es **no romper** este núcleo Python (es el que se califica en Compiladores 2),
sino construir encima de él una versión web como proyecto complementario.

## Objetivo Técnico Futuro

### 1. Generar Target JavaScript con ANTLR

Usar la misma gramática `NaturalToJson.g4` para generar el lexer/parser en
JavaScript:

- Generar código con ANTLR usando `-Dlanguage=JavaScript`.
- Guardar los archivos resultantes en una carpeta, por ejemplo:
  - `web/generated-js/`

Esto proporcionaría:

- `NaturalToJsonLexer.js`
- `NaturalToJsonParser.js`
- Listeners/Visitors en JS

### 2. Portar la Lógica de analyzer_core a JavaScript/TypeScript

Tomar las responsabilidades actuales de `analyzer_core.py` y replicarlas en JS/TS:

- Construir el lexer y parser ANTLR en JS.
- Ejecutar el análisis léxico y sintáctico.
- Recorrer el árbol (listener/visitor) para:
  - Construir el JSON de salida.
  - Construir la IR (cuando esté definida en el proyecto Python).
  - Construir el código final (cuando esté definido en el proyecto Python).
- Implementar un sistema de errores similar (mensajes claros en español).

Idealmente, seguir la misma estructura conceptual que en Python para poder
comparar resultados fácilmente entre ambas versiones.

### 3. Crear un Frontend Web (React/Next.js u otra tecnología)

Diseñar una interfaz web que permita:

- Escribir o pegar código "Natural a JSON" en un editor de texto.
- Cargar ejemplos predefinidos (basados en `examples/valid` e `invalid`).
- Mostrar:
  - Tokens
  - Árbol de análisis (por ejemplo, como árbol colapsable)
  - JSON generado
  - IR
  - Código final
  - Errores

Este frontend podría vivir en una carpeta como:

- `web/frontend/`

Y consumiría directamente los módulos JS generados por ANTLR (no necesitaría
backend si todo corre en el navegador).

### 4. Uso de los Mismos Ejemplos y Expected

Reutilizar los casos de prueba actuales:

- `examples/valid/*`
- `examples/invalid/*`
- `examples/expected/*.json`

Para validar que la versión JS produce **las mismas salidas** que la versión
Python:

- Comparar JSON generado en el navegador contra los archivos de `examples/expected`.
- Verificar que los casos inválidos produzcan errores en la versión web igual
  que en la versión Python.

### 5. Despliegue en Vercel

Una vez que el frontend esté listo:

- Empaquetar el proyecto web (por ejemplo, como una app de Next.js).
- Configurar el proyecto para **deploy en Vercel**:
  - Repositorio GitHub conectado a Vercel.
  - Build command y output directory según el framework elegido.
- Probar:
  - Acceso a la app desde cualquier navegador.
  - Ejecución del compilador en el cliente sin servidor Python.

## Beneficios de Este Objetivo Bonus

- Proyecto muy atractivo para portafolio:
  - Muestra conocimientos de compiladores (léxico, sintaxis, semántica, IR, código).
  - Muestra habilidades web (frontend, posiblemente TypeScript).
  - Muestra integración de herramientas (ANTLR en múltiples lenguajes, Vercel).
- Practicar el uso de una única gramática (`NaturalToJson.g4`) para múltiples
  targets (Python y JavaScript).
- Separar claramente:
  - Núcleo de compilador (Python, proyecto académico).
  - Experiencia de usuario web (JS/TS, proyecto de portafolio).

## Condición Importante

Este objetivo **solo se debe abordar** cuando:

1. El proyecto de Compiladores 2 en Python cumpla con todo lo requerido:
   - Análisis semántico
   - Representación intermedia (IR)
   - Código final
   - Optimizaciones
   - Ejemplos y documentación completos
2. Las pruebas actuales (y las que se agreguen) estén pasando y el núcleo sea
   estable.

Mientras tanto, este documento sirve como guía de alto nivel para un **Bonus Final**
que puede convertirse en un excelente proyecto adicional, pero sin poner en riesgo
la entrega principal del curso.

