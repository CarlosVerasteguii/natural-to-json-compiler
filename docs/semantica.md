# Análisis Semántico – Lenguaje "Natural a JSON"

Este documento describe las reglas semánticas que se aplicarán al lenguaje "Natural a JSON" durante la fase de análisis semántico del compilador/traductor. Estas reglas van más allá del análisis léxico y sintáctico, verificando la coherencia lógica y el significado del programa.

---

## 1. Descripción General

### 1.1. ¿Qué es "Natural a JSON"?

"Natural a JSON" es un lenguaje de dominio específico (DSL) diseñado para describir estructuras de datos mediante comandos en pseudo-lenguaje natural y transformarlas automáticamente a formato JSON.

El lenguaje permite dos tipos de declaraciones principales:

- **Objetos JSON**: Mediante el comando `CREAR OBJETO nombre CON propiedad1:valor1, propiedad2:valor2, ...`
- **Listas JSON**: Mediante el comando `CREAR LISTA nombre CON ELEMENTOS valor1, valor2, ...`

**Ejemplo de entrada válida:**
```
CREAR OBJETO usuario CON nombre:"Ana", edad:25, activo:VERDADERO
CREAR LISTA colores CON ELEMENTOS "rojo", "verde", "azul"
```

**Salida JSON esperada:**
```json
{
  "usuario": {
    "nombre": "Ana",
    "edad": 25,
    "activo": true
  },
  "colores": ["rojo", "verde", "azul"]
}
```

### 1.2. Propósito del Análisis Semántico

Mientras que el análisis léxico verifica que los tokens sean válidos y el análisis sintáctico asegura que la estructura del programa cumpla con la gramática, el **análisis semántico** verifica que el programa tenga sentido lógico y sea coherente.

El análisis semántico para "Natural a JSON" se enfoca en:

1. **Gestión de símbolos**: Registrar todas las entidades (objetos y listas) declaradas y detectar redeclaraciones.
2. **Verificación de tipos**: Asegurar que los valores sean del tipo esperado y mantener coherencia cuando sea necesario.
3. **Reglas de alcance y visibilidad**: Verificar que los nombres utilizados sean válidos y no entren en conflicto con palabras reservadas.
4. **Detección de errores semánticos**: Reportar errores que no pueden detectarse en las fases léxica o sintáctica, como redefinición de nombres o incoherencias de tipos.

---

## 2. Tabla de Símbolos

### 2.1. Entidades Registradas

La tabla de símbolos registrará las siguientes entidades:

- **Objetos**: Cada declaración `CREAR OBJETO nombre ...` añade una entrada a la tabla.
- **Listas**: Cada declaración `CREAR LISTA nombre ...` añade una entrada a la tabla.

**Nota**: Las claves (propiedades) dentro de los objetos NO se registran como símbolos independientes en la tabla de símbolos global, ya que pertenecen al ámbito interno del objeto. Sin embargo, se pueden mantener metadatos sobre ellas para validaciones de tipo si es necesario.

### 2.2. Información Almacenada por Símbolo

Cada entrada en la tabla de símbolos contendrá:

| Campo          | Descripción                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| `nombre`       | El identificador del objeto o lista (ej: `usuario`, `colores`)                               |
| `tipo_entidad` | Tipo de entidad: `"objeto"` o `"lista"`                                                      |
| `linea`        | Número de línea donde se declaró (para mensajes de error)                                    |
| `columna`      | Número de columna donde se declaró (para mensajes de error)                                  |
| `metadatos`    | (Opcional) Información adicional como propiedades del objeto o tipo de elementos de la lista |

**Ejemplo de estructura interna:**
```python
{
  "usuario": {
    "nombre": "usuario",
    "tipo_entidad": "objeto",
    "linea": 1,
    "columna": 15,
    "metadatos": {
      "propiedades": {
        "nombre": "string",
        "edad": "number",
        "activo": "boolean"
      }
    }
  },
  "colores": {
    "nombre": "colores",
    "tipo_entidad": "lista",
    "linea": 2,
    "columna": 13,
    "metadatos": {}
  }
}
```

### 2.3. Errores Semánticos Relacionados con la Tabla de Símbolos

#### 2.3.1. Redefinición de Símbolo

**Regla**: No se permite redeclarar un objeto o lista con un nombre que ya existe en la tabla de símbolos.

**Ejemplo de error:**
```
CREAR OBJETO producto CON nombre:"Laptop", precio:1500
CREAR LISTA producto CON ELEMENTOS "A", "B", "C"  // ERROR: 'producto' ya existe
```

**Mensaje de error esperado:**
```
Error Semántico en '<archivo>' (Línea 2:Columna 13):
Redefinición del símbolo 'producto'. Ya fue declarado como 'objeto' en la línea 1.
```

#### 2.3.2. Uso de Nombres Reservados

**Regla**: No se permite usar palabras clave del lenguaje como nombres de objetos o listas.

Palabras reservadas: `CREAR`, `OBJETO`, `LISTA`, `CON`, `ELEMENTOS`, `VERDADERO`, `FALSO`

**Ejemplo de error:**
```
CREAR OBJETO CREAR CON valor:"test"  // ERROR: 'CREAR' es una palabra reservada
```

**Mensaje de error esperado:**
```
Error Semántico en '<archivo>' (Línea 1:Columna 15):
El nombre 'CREAR' es una palabra reservada y no puede usarse como identificador.
```

---

## 3. Reglas de Tipos

### 3.1. Tipos Básicos del Lenguaje

El lenguaje "Natural a JSON" maneja tres tipos básicos de valores, que se mapean directamente a los tipos JSON:

| Tipo en el Compilador | Representación en el Lenguaje | Tipo JSON Resultante | Ejemplo                      |
| --------------------- | ----------------------------- | -------------------- | ---------------------------- |
| `STRING`              | Cadena entre comillas dobles  | `string`             | `"Hola mundo"`               |
| `NUMBER`              | Número entero o decimal       | `number`             | `123`, `-45`, `3.14`, `-0.5` |
| `BOOLEAN`             | `VERDADERO` o `FALSO`         | `boolean`            | `VERDADERO`, `FALSO`         |

### 3.2. Detección de Tipos

El tipo de un valor se determina durante el recorrido del árbol de parseo según el token reconocido:

- **STRING**: Token `STRING` (cadena entre comillas dobles)
- **NUMBER**: Token `NUMERO_ENTERO` o `NUMERO_DECIMAL`
  - Subtipo `INTEGER`: Token `NUMERO_ENTERO`
  - Subtipo `DECIMAL`: Token `NUMERO_DECIMAL`
- **BOOLEAN**: Token `KW_VERDADERO` o `KW_FALSO`

**Nota sobre números**: Aunque internamente se distingue entre enteros y decimales para la representación JSON correcta (int vs float en Python), desde el punto de vista semántico ambos se consideran del tipo `NUMBER`.

### 3.3. Reglas de Coherencia de Tipos

#### 3.3.1. Coherencia de Tipos en Propiedades de Objetos

**Regla aplicada**: No se exigirá que todas las propiedades de un objeto sean del mismo tipo (esto es natural en JSON, donde un objeto puede tener propiedades de diferentes tipos).

**Ejemplo válido:**
```
CREAR OBJETO persona CON nombre:"Juan", edad:30, casado:VERDADERO
```

Resultado JSON esperado:
```json
{
  "persona": {
    "nombre": "Juan",
    "edad": 30,
    "casado": true
  }
}
```

#### 3.3.2. Heterogeneidad en Listas

**Regla aplicada**: Se permitirá que las listas contengan elementos de diferentes tipos (esto es válido en JSON).

**Ejemplo válido:**
```
CREAR LISTA mixta CON ELEMENTOS "texto", 123, VERDADERO, -45.6
```

Resultado JSON esperado:
```json
{
  "mixta": ["texto", 123, true, -45.6]
}
```

**Nota de diseño**: En esta versión inicial del análisis semántico, NO se implementarán restricciones de homogeneidad en listas. Si en el futuro se desea exigir que todos los elementos de una lista sean del mismo tipo, esta regla puede añadirse fácilmente consultando los metadatos de la lista.

### 3.4. Qué NO se Verificará (Alcance Limitado)

Para mantener el alcance de la Unidad 1 manejable, las siguientes verificaciones de tipos **NO** se implementarán:

- No se verificará que una misma clave usada en diferentes objetos mantenga el mismo tipo
- No se exigirá homogeneidad de tipos en listas (todos los elementos del mismo tipo)
- No se validarán rangos de valores numéricos (ej: edad > 0)
- No se validarán formatos de strings (ej: emails, URLs)
- No se verificarán estructuras anidadas (el lenguaje actual no soporta anidamiento)

---

## 4. Alcance y Visibilidad

### 4.1. Modelo de Alcance

El lenguaje "Natural a JSON" es fundamentalmente plano: todos los comandos `CREAR OBJETO` y `CREAR LISTA` se ejecutan en el mismo nivel, sin anidamiento ni bloques.

**Alcance implementado**: **Ámbito global único**

- Todos los objetos y listas declarados comparten un mismo espacio de nombres global.
- No existen ámbitos locales, bloques anidados ni jerarquías de scope.
- La tabla de símbolos mantiene un único diccionario global.

### 4.2. Reglas de Visibilidad

#### 4.2.1. Unicidad de Nombres

**Regla**: Dentro del ámbito global, cada nombre de objeto o lista debe ser único.

**Ejemplo de conflicto:**
```
CREAR OBJETO datos CON valor:100
CREAR LISTA datos CON ELEMENTOS 1, 2, 3  // ERROR: nombre duplicado
```

#### 4.2.2. Nombres Reservados

**Regla**: Las palabras clave del lenguaje no pueden usarse como identificadores de objetos o listas.

Palabras reservadas completas:
- `CREAR`
- `OBJETO`
- `LISTA`
- `CON`
- `ELEMENTOS`
- `VERDADERO`
- `FALSO`

**Nota**: La gramática actual ya es insensible a mayúsculas/minúsculas para palabras clave, por lo que `crear`, `Crear`, `CREAR` son todas equivalentes y reservadas.

#### 4.2.3. Identificadores Válidos

**Regla**: Los identificadores (nombres de objetos, listas y propiedades) deben:
- Comenzar con una letra (incluyendo caracteres Unicode como ñ, á, é, etc.) o guion bajo `_`
- Continuar con letras, dígitos o guiones bajos
- No ser palabras reservadas

**Ejemplos válidos:**
- `miObjeto`, `objeto_1`, `listaÑandú`, `_privado`, `año2024`

**Ejemplos inválidos:**
- `CREAR` (palabra reservada)
- `123inicio` (comienza con dígito - esto se detecta en análisis léxico)
- `objeto-con-guiones` (contiene guiones - esto se detecta en análisis léxico)

### 4.3. Preparación para Futuras Extensiones

Aunque actualmente el lenguaje solo requiere un ámbito global, la implementación de la tabla de símbolos debe diseñarse de forma que permita fácilmente extenderse a:

- **Ámbitos anidados**: Si en el futuro se permite crear objetos dentro de objetos.
- **Ámbitos por bloque**: Si se añaden estructuras de control (if, while, etc.).
- **Importación de módulos**: Si se permite importar definiciones de otros archivos.

**Diseño recomendado**: Implementar la tabla de símbolos con una estructura que soporte una pila de ámbitos (`ScopeStack`), aunque inicialmente solo se use un nivel.

---

## 5. Errores Semánticos y Mensajes Esperados

A continuación se listan todos los errores semánticos que se detectarán durante el análisis semántico, junto con ejemplos y el formato de mensaje esperado.

### 5.1. Error: Redefinición de Símbolo

**Código de error**: `SEM001`

**Descripción**: Se intenta declarar un objeto o lista con un nombre que ya existe en la tabla de símbolos.

**Condición de detección**: Al procesar un comando `CREAR OBJETO` o `CREAR LISTA`, si el nombre ya está en la tabla de símbolos.

**Ejemplo:**
```
CREAR OBJETO usuario CON nombre:"Ana", edad:25
CREAR OBJETO usuario CON email:"ana@example.com"  // ERROR SEM001
```

**Mensaje de error:**
```
Error Semántico en '<archivo>' (Línea 2:Columna 15):
Redefinición del símbolo 'usuario'. Ya fue declarado como 'objeto' en la línea 1.
```

**Formato del mensaje:**
```
Error Semántico en '{fuente}' (Línea {línea}:Columna {columna}):
Redefinición del símbolo '{nombre}'. Ya fue declarado como '{tipo_anterior}' en la línea {línea_anterior}.
```

---

### 5.2. Error: Uso de Palabra Reservada como Identificador

**Código de error**: `SEM002`

**Descripción**: Se intenta usar una palabra clave del lenguaje como nombre de objeto o lista.

**Condición de detección**: Al procesar un comando `CREAR OBJETO` o `CREAR LISTA`, si el nombre es una palabra reservada.

**Ejemplo:**
```
CREAR OBJETO VERDADERO CON valor:100  // ERROR SEM002
```

**Mensaje de error:**
```
Error Semántico en '<archivo>' (Línea 1:Columna 15):
El nombre 'VERDADERO' es una palabra reservada del lenguaje y no puede usarse como identificador.
```

**Formato del mensaje:**
```
Error Semántico en '{fuente}' (Línea {línea}:Columna {columna}):
El nombre '{nombre}' es una palabra reservada del lenguaje y no puede usarse como identificador.
```

---

### 5.3. Error: Objeto Vacío (Sin Propiedades)

**Código de error**: `SEM003`

**Descripción**: Se intenta crear un objeto sin ninguna propiedad.

**Condición de detección**: Al procesar un comando `CREAR OBJETO`, si la lista de propiedades está vacía.

**Nota**: Este error es más bien sintáctico según la gramática actual (ya que `propiedades` requiere al menos una `propiedad`), pero si la gramática se modifica para permitir objetos opcionales, este se convertiría en un error semántico.

**Ejemplo (si la gramática lo permitiera):**
```
CREAR OBJETO vacio CON   // ERROR SEM003
```

**Mensaje de error:**
```
Error Semántico en '<archivo>' (Línea 1:Columna 15):
El objeto 'vacio' debe tener al menos una propiedad. No se permiten objetos vacíos.
```

**Estado**: **OPCIONAL** - Solo implementar si la gramática se modifica para permitir objetos sin propiedades.

---

### 5.4. Error: Lista Vacía (Sin Elementos)

**Código de error**: `SEM004`

**Descripción**: Se intenta crear una lista sin ningún elemento.

**Condición de detección**: Al procesar un comando `CREAR LISTA`, si la lista de elementos está vacía.

**Nota**: Similar a SEM003, esto actualmente es un error sintáctico, pero podría convertirse en semántico.

**Ejemplo (si la gramática lo permitiera):**
```
CREAR LISTA vacia CON ELEMENTOS   // ERROR SEM004
```

**Mensaje de error:**
```
Error Semántico en '<archivo>' (Línea 1:Columna 13):
La lista 'vacia' debe tener al menos un elemento. No se permiten listas vacías.
```

**Estado**: **OPCIONAL** - Solo implementar si la gramática se modifica para permitir listas sin elementos.

---

### 5.5. Resumen de Errores Implementados

Para la Unidad 1, se implementarán **obligatoriamente**:

| Código | Error                          | Prioridad |
| ------ | ------------------------------ | --------- |
| SEM001 | Redefinición de símbolo        | Alta      |
| SEM002 | Uso de palabra reservada       | Alta      |
| SEM003 | Objeto vacío (sin propiedades) | Opcional  |
| SEM004 | Lista vacía (sin elementos)    | Opcional  |

---

## 6. Ejemplos de Entradas Válidas e Inválidas

### 6.1. Ejemplos Semánticamente Válidos

#### Ejemplo V1: Múltiples Objetos y Listas con Nombres Únicos

**Entrada:**
```
CREAR OBJETO libro CON titulo:"1984", autor:"George Orwell", año:1949
CREAR OBJETO persona CON nombre:"Ana", edad:30, activo:VERDADERO
CREAR LISTA numeros CON ELEMENTOS 10, 20, 30, 40, 50
CREAR LISTA estados CON ELEMENTOS VERDADERO, FALSO, VERDADERO
```

**Análisis semántico esperado:**
-  Todos los nombres son únicos: `libro`, `persona`, `numeros`, `estados`
-  Ningún nombre es palabra reservada
-  Todos los tipos de valores son válidos
-  No hay redefiniciones

**Salida JSON esperada:**
```json
{
  "libro": {
    "titulo": "1984",
    "autor": "George Orwell",
    "año": 1949
  },
  "persona": {
    "nombre": "Ana",
    "edad": 30,
    "activo": true
  },
  "numeros": [10, 20, 30, 40, 50],
  "estados": [true, false, true]
}
```

**Resultado del análisis semántico**: Sin errores semánticos. Se genera JSON correctamente.

---

#### Ejemplo V2: Uso de Diferentes Tipos en Objetos y Listas

**Entrada:**
```
CREAR OBJETO producto CON nombre:"Laptop", precio:1299.99, enStock:VERDADERO, cantidad:5
CREAR LISTA mixto CON ELEMENTOS "texto", 123, -45.67, FALSO
```

**Análisis semántico esperado:**
- El objeto `producto` tiene propiedades de diferentes tipos (string, decimal, boolean, entero)
- La lista `mixto` contiene elementos de diferentes tipos (heterogénea)
- Esto es válido según las reglas definidas

**Salida JSON esperada:**
```json
{
  "producto": {
    "nombre": "Laptop",
    "precio": 1299.99,
    "enStock": true,
    "cantidad": 5
  },
  "mixto": ["texto", 123, -45.67, false]
}
```

**Resultado del análisis semántico**: Sin errores semánticos. Se genera JSON correctamente.

---

#### Ejemplo V3: Nombres con Caracteres Unicode

**Entrada:**
```
CREAR OBJETO año_2024 CON descripción:"Año actual", válido:VERDADERO
CREAR LISTA ciudadesEspaña CON ELEMENTOS "Madrid", "Barcelona", "Ñuñoa"
```

**Análisis semántico esperado:**
- Los identificadores con acentos y ñ son válidos
- Los nombres son únicos
- No hay conflictos con palabras reservadas

**Salida JSON esperada:**
```json
{
  "año_2024": {
    "descripción": "Año actual",
    "válido": true
  },
  "ciudadesEspaña": ["Madrid", "Barcelona", "Ñuñoa"]
}
```

**Resultado del análisis semántico**: Sin errores semánticos. Se genera JSON correctamente.

---

### 6.2. Ejemplos Semánticamente Inválidos

#### Ejemplo I1: Redefinición de Objeto

**Entrada:**
```
CREAR OBJETO usuario CON nombre:"Juan", edad:25
CREAR OBJETO usuario CON email:"juan@example.com"
```

**Error semántico detectado:**
```
Error Semántico en '<input>' (Línea 2:Columna 15):
Redefinición del símbolo 'usuario'. Ya fue declarado como 'objeto' en la línea 1.
```

**Explicación**: El nombre `usuario` se usa dos veces para declarar objetos. Según la regla SEM001, no se permite redefinir símbolos.

**Resultado esperado del compilador**:
- Se reporta el error semántico
- No se genera JSON (o se genera parcialmente hasta el error)
- El proceso de análisis continúa para detectar otros posibles errores

---

#### Ejemplo I2: Conflicto entre Objeto y Lista con el Mismo Nombre

**Entrada:**
```
CREAR OBJETO datos CON valor:100, descripcion:"Test"
CREAR LISTA datos CON ELEMENTOS 1, 2, 3, 4, 5
```

**Error semántico detectado:**
```
Error Semántico en '<input>' (Línea 2:Columna 13):
Redefinición del símbolo 'datos'. Ya fue declarado como 'objeto' en la línea 1.
```

**Explicación**: Aunque uno es objeto y otro es lista, ambos comparten el mismo espacio de nombres global. No se permite usar el mismo nombre para entidades diferentes.

**Resultado esperado del compilador**:
- Se reporta el error semántico
- No se genera JSON válido

---

#### Ejemplo I3: Uso de Palabra Reservada como Nombre

**Entrada:**
```
CREAR OBJETO CREAR CON valor:"test", numero:123
CREAR LISTA ELEMENTOS CON ELEMENTOS "A", "B", "C"
```

**Errores semánticos detectados:**
```
Error Semántico en '<input>' (Línea 1:Columna 15):
El nombre 'CREAR' es una palabra reservada del lenguaje y no puede usarse como identificador.

Error Semántico en '<input>' (Línea 2:Columna 13):
El nombre 'ELEMENTOS' es una palabra reservada del lenguaje y no puede usarse como identificador.
```

**Explicación**: Las palabras `CREAR` y `ELEMENTOS` son palabras clave del lenguaje y no pueden reutilizarse como identificadores de usuario.

**Resultado esperado del compilador**:
- Se reportan ambos errores semánticos
- No se genera JSON

---

#### Ejemplo I4: Múltiples Redefiniciones

**Entrada:**
```
CREAR OBJETO config CON modo:"produccion", debug:FALSO
CREAR LISTA items CON ELEMENTOS 1, 2, 3
CREAR OBJETO config CON modo:"desarrollo"
CREAR LISTA items CON ELEMENTOS "A", "B"
```

**Errores semánticos detectados:**
```
Error Semántico en '<input>' (Línea 3:Columna 15):
Redefinición del símbolo 'config'. Ya fue declarado como 'objeto' en la línea 1.

Error Semántico en '<input>' (Línea 4:Columna 13):
Redefinición del símbolo 'items'. Ya fue declarado como 'lista' en la línea 2.
```

**Explicación**: Se intenta redeclarar tanto `config` como `items`, violando la regla SEM001 dos veces.

**Resultado esperado del compilador**:
- Se reportan ambos errores semánticos
- El análisis continúa para detectar todos los errores (no se detiene en el primero)
- No se genera JSON válido

---

### 6.3. Casos Límite (Edge Cases)

#### Caso Límite 1: Nombres Similares pero Diferentes

**Entrada:**
```
CREAR OBJETO usuario CON nombre:"Ana"
CREAR OBJETO Usuario CON nombre:"Juan"
```

**Análisis esperado:**
- Depende de si la comparación de identificadores es sensible a mayúsculas/minúsculas
- **Recomendación**: Hacer la comparación **insensible** a mayúsculas para consistencia con las palabras clave
- Si se implementa insensible: **ERROR SEM001** (redefinición)
- Si se implementa sensible: **SIN ERROR** (nombres diferentes)

**Decisión de diseño**: Se recomienda hacer la tabla de símbolos **insensible** a mayúsculas/minúsculas para evitar confusión del usuario, dado que las palabras clave ya son insensibles.

---

#### Caso Límite 2: Nombre con Solo Guiones Bajos

**Entrada:**
```
CREAR OBJETO _ CON valor:100
CREAR LISTA __ CON ELEMENTOS 1, 2, 3
```

**Análisis esperado:**
- Los identificadores `_` y `__` son sintácticamente válidos
- No hay conflicto entre ellos (nombres únicos)
- No son palabras reservadas

**Resultado**: Sin errores semánticos.

---

#### Caso Límite 3: Archivo Vacío

**Entrada:**
```
// Solo comentarios
// Nada más
```

**Análisis esperado:**
- No hay comandos, por lo tanto no hay símbolos que registrar
- La tabla de símbolos queda vacía
- No se generan errores semánticos

**Resultado**: Sin errores semánticos. JSON resultante: `{}`

---

## 7. Integración con el Sistema de Errores Actual

### 7.1. Formato de Mensajes de Error

Los mensajes de error semántico deben mantener el mismo formato que los errores léxicos y sintácticos existentes para consistencia:

```
Error {tipo} en '{fuente}' (Línea {línea}:Columna {columna}): {descripción_detallada}
```

**Componentes:**
- `{tipo}`: `"Semántico"` (para distinguirlo de `"Léxico"` y `"Sintáctico"`)
- `{fuente}`: Nombre del archivo o `"<input>"` si es entrada directa
- `{línea}`: Número de línea (1-indexed)
- `{columna}`: Número de columna (1-indexed)
- `{descripción_detallada}`: Mensaje específico del error en español

### 7.2. Gestión de Errores en `analyzer_core.py`

El sistema actual de errores en `CustomErrorListener` cuenta con:
- `error_messages`: Lista de mensajes de error
- `_lexer_errors`: Contador de errores léxicos
- `_parser_errors`: Contador de errores sintácticos

**Extensión necesaria**: Agregar un contador `_semantic_errors` y métodos para registrar errores semánticos:

```python
# Extensión sugerida (no implementar ahora, solo documentar)
class CustomErrorListener(ErrorListener):
    def __init__(self, source_name="<input>"):
        # ... código existente ...
        self._semantic_errors = 0  # NUEVO

    @property
    def semantic_errors(self):
        """Retorna el número de errores semánticos detectados."""
        return self._semantic_errors

    def add_semantic_error(self, line, column, message):
        """Registra un error semántico."""
        self._semantic_errors += 1
        formatted_msg = f"Error Semántico en '{self.source_name}' (Línea {line}:Columna {column}): {message}"
        self.error_messages.append(formatted_msg)
```

### 7.3. Orden de Ejecución de Fases de Análisis

El análisis semántico debe ejecutarse **después** de que el análisis léxico y sintáctico hayan completado exitosamente:

1. **Fase Léxica**: Genera tokens
2. **Fase Sintáctica**: Genera árbol de parseo (AST)
3. **Fase Semántica**: Recorre el AST, construye tabla de símbolos, valida reglas ← **NUEVA**
4. **Generación de Código**: Construye JSON

**Estrategia de manejo de errores:**
- Si hay errores léxicos o sintácticos, **NO ejecutar** el análisis semántico (no tiene sentido validar semántica en un árbol inválido)
- Si hay errores semánticos, **NO generar** JSON de salida (o generar con advertencia)
- Reportar **todos** los errores semánticos encontrados, no solo el primero

### 7.4. Actualización de Estadísticas

El diccionario `stats` debe incluir errores semánticos:

```python
stats = {
    "tiempo_analisis_seg": round(analysis_time, 4),
    "comandos_procesados": num_comandos,
    "tokens_al_parser": parser_tokens_count,
    "errores_lexicos": error_listener.lexer_errors,
    "errores_sintacticos": error_listener.parser_errors,
    "errores_semanticos": error_listener.semantic_errors  # NUEVO
}
```

---

## 8. Arquitectura de Implementación (Guía para la Siguiente Iteración)

Esta sección describe la arquitectura sugerida para implementar el análisis semántico. **No se implementará en esta iteración**, solo se documenta como guía.

### 8.1. Clases Principales

#### 8.1.1. `SymbolEntry`

Representa una entrada en la tabla de símbolos.

```python
class SymbolEntry:
    def __init__(self, nombre, tipo_entidad, linea, columna, metadatos=None):
        self.nombre = nombre
        self.tipo_entidad = tipo_entidad  # "objeto" o "lista"
        self.linea = linea
        self.columna = columna
        self.metadatos = metadatos or {}
```

#### 8.1.2. `SymbolTable`

Gestiona la tabla de símbolos y las operaciones de inserción/búsqueda.

```python
class SymbolTable:
    def __init__(self, case_sensitive=False):
        self.symbols = {}
        self.case_sensitive = case_sensitive

    def insert(self, entry):
        """Inserta un símbolo. Retorna True si exitoso, False si ya existe."""
        pass

    def lookup(self, nombre):
        """Busca un símbolo por nombre. Retorna SymbolEntry o None."""
        pass

    def is_reserved(self, nombre):
        """Verifica si un nombre es palabra reservada."""
        pass
```

#### 8.1.3. `SemanticAnalyzer` (Listener)

Listener de ANTLR que realiza el análisis semántico durante el recorrido del árbol.

```python
class SemanticAnalyzer(NaturalToJsonListener):
    def __init__(self, error_listener, symbol_table):
        self.error_listener = error_listener
        self.symbol_table = symbol_table

    def enterCrear_objeto_cmd(self, ctx):
        """Procesa la creación de un objeto."""
        # 1. Extraer nombre del objeto
        # 2. Verificar si es palabra reservada
        # 3. Intentar insertar en tabla de símbolos
        # 4. Si falla, reportar error semántico
        pass

    def enterCrear_lista_cmd(self, ctx):
        """Procesa la creación de una lista."""
        # Similar a enterCrear_objeto_cmd
        pass
```

### 8.2. Flujo de Integración en `analyze_and_transform()`

```python
def analyze_and_transform(source_name, input_content):
    # ... código existente de lexer y parser ...

    if error_listener.get_total_errors() == 0 and tree:
        # NUEVO: Análisis semántico
        symbol_table = SymbolTable(case_sensitive=False)
        semantic_analyzer = SemanticAnalyzer(error_listener, symbol_table)
        walker = ParseTreeWalker()
        walker.walk(semantic_analyzer, tree)

        # Solo generar JSON si no hay errores semánticos
        if error_listener.semantic_errors == 0:
            # Construir JSON (código existente)
            json_builder = JsonBuilderListener()
            walker.walk(json_builder, tree)
            json_output_string = json_builder.get_final_json_string()
        else:
            json_output_string = None

    # ... resto del código ...
```

---

## 9. Plan de Pruebas

### 9.1. Casos de Prueba Semánticos

Se deben crear archivos de prueba específicos para validar el análisis semántico:

#### Archivos de Prueba Válidos (Semánticamente)

- `examples/valid_semantic/valid_sem_01.txt`: Múltiples objetos y listas con nombres únicos
- `examples/valid_semantic/valid_sem_02.txt`: Diferentes tipos de valores mezclados
- `examples/valid_semantic/valid_sem_03.txt`: Nombres con Unicode

#### Archivos de Prueba Inválidos (Semánticamente)

- `examples/invalid_semantic/invalid_sem_01.txt`: Redefinición de objeto
- `examples/invalid_semantic/invalid_sem_02.txt`: Redefinición de lista
- `examples/invalid_semantic/invalid_sem_03.txt`: Conflicto objeto-lista
- `examples/invalid_semantic/invalid_sem_04.txt`: Uso de palabra reservada
- `examples/invalid_semantic/invalid_sem_05.txt`: Múltiples errores semánticos

### 9.2. Pruebas Automatizadas

Extender `tests/test_basic.py` o crear `tests/test_semantic.py` con pruebas como:

```python
def test_valid_semantic_01():
    """Prueba que entradas semánticamente válidas no generen errores."""
    content = """
    CREAR OBJETO libro CON titulo:"1984", año:1949
    CREAR LISTA numeros CON ELEMENTOS 1, 2, 3
    """
    json_out, tokens, tree, model, errors, stats = analyze_and_transform("<test>", content)
    assert stats["errores_semanticos"] == 0
    assert json_out is not None

def test_invalid_semantic_redefinition():
    """Prueba detección de redefinición de símbolo."""
    content = """
    CREAR OBJETO usuario CON nombre:"Ana"
    CREAR OBJETO usuario CON edad:25
    """
    json_out, tokens, tree, model, errors, stats = analyze_and_transform("<test>", content)
    assert stats["errores_semanticos"] == 1
    assert "Redefinición" in errors
```

### 9.3. Compatibilidad con Pruebas Existentes

**Criterio crítico**: Todas las pruebas existentes en `tests/test_basic.py` deben seguir pasando después de implementar el análisis semántico.

Si alguna prueba falla, verificar:
1. ¿Los ejemplos existentes violan alguna regla semántica nueva?
2. ¿El análisis semántico está causando side effects inesperados?
3. ¿El formato de salida JSON ha cambiado?

---

## 10. Resumen y Próximos Pasos

### 10.1. Resumen de Reglas Semánticas Definidas

| Aspecto                 | Regla Definida                                                             |
| ----------------------- | -------------------------------------------------------------------------- |
| **Tabla de Símbolos**   | Registra objetos y listas; detecta redefiniciones                          |
| **Tipos**               | String, Number (entero/decimal), Boolean; permite heterogeneidad           |
| **Alcance**             | Ámbito global único; nombres deben ser únicos                              |
| **Palabras Reservadas** | No se permiten como identificadores                                        |
| **Errores Detectados**  | SEM001 (redefinición), SEM002 (palabra reservada), SEM003/004 (opcionales) |

### 10.2. Errores Semánticos a Implementar

**Obligatorios (Prioridad Alta):**
1. **SEM001**: Redefinición de símbolo
2. **SEM002**: Uso de palabra reservada

**Opcionales (Prioridad Baja):**
3. **SEM003**: Objeto vacío
4. **SEM004**: Lista vacía

### 10.3. Relación entre Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     Análisis Semántico                       │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Listener   │────────▶│Tabla de      │                 │
│  │  Semántico   │  insert │Símbolos      │                 │
│  │              │  lookup │              │                 │
│  └──────┬───────┘         └──────────────┘                 │
│         │                                                    │
│         │ reporta errores                                    │
│         ▼                                                    │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │Error         │────────▶│Sistema de    │                 │
│  │Listener      │  append │Errores       │                 │
│  └──────────────┘         └──────────────┘                 │
│                                                              │
│  Reglas aplicadas:                                          │
│  - SEM001: Redefinición de símbolos                         │
│  - SEM002: Palabras reservadas                              │
│  - Tipos: STRING, NUMBER, BOOLEAN                           │
│  - Alcance: Global único                                    │
└─────────────────────────────────────────────────────────────┘
```

### 10.4. Siguiente Iteración (Paso 1 del Plan)

Con este documento de diseño completo, la siguiente iteración debe:

1. Implementar `SymbolEntry` y `SymbolTable` en `analyzer_core.py`
2. Implementar `SemanticAnalyzer` (Listener)
3. Integrar análisis semántico en `analyze_and_transform()`
4. Extender `CustomErrorListener` para errores semánticos
5. Ejecutar pruebas y verificar compatibilidad

---

## Apéndice A: Palabras Reservadas Completas

```
CREAR
OBJETO
LISTA
CON
ELEMENTOS
VERDADERO
FALSO
```

**Nota**: Todas son insensibles a mayúsculas/minúsculas.

---

## Apéndice B: Gramática de Tipos (Informal)

```
Tipo ::= STRING | NUMBER | BOOLEAN

STRING  ::= "cadena entre comillas"
NUMBER  ::= ENTERO | DECIMAL
ENTERO  ::= -?[0-9]+
DECIMAL ::= -?[0-9]+\.[0-9]+
BOOLEAN ::= VERDADERO | FALSO
```

---

## Apéndice C: Referencias

- **Archivo de plan**: `docs/plan_unidad1_semantica.md`
- **Gramática ANTLR**: `src/NaturalToJson.g4`
- **Núcleo del analizador**: `src/analyzer_core.py`
- **Pruebas básicas**: `tests/test_basic.py`

---

**Documento creado**: 2025 (Producto Integrador - Compiladores 2)
**Versión**: 1.0
**Estado**: Listo para implementación
