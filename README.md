# Proyecto Compiladores 2
Compilador/Traductor para el lenguaje "Natural a JSON".

Este proyecto extiende el trabajo de Compiladores 1 y está diseñado para incorporar análisis semántico, generación de código e optimización en las siguientes fases.

## Estado Actual del Proyecto
> [!NOTE]
> Actualmente, el proyecto implementa las fases de **Análisis Léxico** y **Análisis Sintáctico**.
> Las fases de Análisis Semántico, Generación de Código y Optimización están en desarrollo (ver Roadmap).

## Información del Curso

* **Materia:** Compiladores 2
* **Institución:** Universidad Autónoma de Tamaulipas
* **Semestre:** 2025-2
* **Profesor:** Dante Adolfo Muñoz Quintero

## Integrantes del Equipo

* Carlos - [Código Estudiante]
* Roberto - [Código Estudiante]

## Estructura del Proyecto

```text
ProyectoCompiladores2/
    src/                # Código fuente (Python + ANTLR)
        analyzer_core.py # Lógica principal del analizador
        main_gui.py      # Interfaz Gráfica (Punto de entrada recomendado)
        main_cli.py      # Interfaz de Línea de Comandos
        generated/       # Archivos generados por ANTLR
    docs/               # Documentación técnica
    examples/           # Fuente oficial de casos de prueba
        valid/          # Casos válidos (.txt)
        invalid/        # Casos con errores (.txt)
        expected/       # Salidas JSON esperadas (.json)
    tests/              # Pruebas automatizadas
    lib/                # Librerías externas
    README.md           
```

## Requisitos y Dependencias

* **Python 3.8+**
* **ANTLR 4.13.2** (Runtime de Python)
* **PyQt5** (Para la interfaz gráfica)

### Instalación de dependencias
```bash
pip install antlr4-python3-runtime PyQt5
```

## Instrucciones de Ejecución

Todas las instrucciones asumen que te encuentras en la **raíz del proyecto** (`ProyectoCompiladores2/`).

### 1. Interfaz Gráfica (Recomendado)
Para iniciar la aplicación con GUI:
```bash
python src/main_gui.py
```
*Por defecto, el diálogo de abrir archivo buscará en `examples/valid`.*

### 2. Interfaz de Línea de Comandos (CLI)
Para usar el modo interactivo en consola:
```bash
python src/main_cli.py
```
*El modo interactivo permite seleccionar archivos de `examples/valid` o `examples/invalid`.*

Para procesar un archivo específico directamente:
```bash
python src/main_cli.py examples/valid/valid_01.txt
```

### 3. Ejecutar Pruebas
Para verificar la estabilidad del analizador:
```bash
python tests/test_basic.py
```

### Sobre las Pruebas (`tests/`)
El script `tests/test_basic.py` realiza las siguientes verificaciones:
1.  **Casos Válidos:** Procesa los archivos de `examples/valid/`, verifica que no haya errores, y compara la salida JSON generada con la esperada en `examples/expected/`.
2.  **Casos Inválidos:** Procesa los archivos de `examples/invalid/` y asegura que el analizador reporte errores.

> **Nota:** La carpeta `src/ejemplos_entrada/` se mantiene por compatibilidad histórica, pero la fuente oficial para pruebas y desarrollo es `examples/`.
**Salida JSON:**
```json
{
  "libro": {
    "titulo": "Cien años de soledad",
    "autor": "Gabriel García Márquez"
  }
}
```
