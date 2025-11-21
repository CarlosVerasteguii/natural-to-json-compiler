# main_gui.py
# Este es el archivo principal para la interfaz gráfica de usuario (GUI) de la aplicación.
"""
Interfaz Gráfica de Usuario (GUI) para el Analizador "Natural a JSON".

Este script implementa la ventana principal de la aplicación utilizando PyQt5.
Permite al usuario ingresar texto en un lenguaje pseudo-natural, cargar archivos,
analizar el contenido (utilizando `analyzer_core`), visualizar los tokens,
el árbol de parseo (interactivo), el JSON resultante, y los errores.
También ofrece funcionalidades para guardar la entrada, el JSON generado,
y recordar la última carpeta utilizada y la geometría de la ventana.
Es el punto de entrada principal para la interacción del usuario con el analizador.
"""
import sys
import os
import time # Para el indicador de "Procesando..."
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLabel, QFileDialog,
                             QMessageBox, QSplitter, QGroupBox,
                             QSizePolicy, QCheckBox, QStatusBar, QMainWindow,
                             QDialog, QPlainTextEdit, QTreeView) # Añadido QTreeView
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QStandardItemModel
from PyQt5.QtCore import Qt, QSize, QRegExp, QSettings # QSettings para recordar directorio

# Importar desde analyzer_core
try:
    from analyzer_core import analyze_and_transform, NaturalToJsonLexer # Necesitamos Lexer para el Highlighter
except ImportError:
    if '..' not in sys.path:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        from analyzer_core import analyze_and_transform, NaturalToJsonLexer
    except ImportError as e_imp:
        QMessageBox.critical(None, "Error de Importación Crítico", 
                             f"No se pudo importar 'analyzer_core'. Asegúrate de que está en la ruta correcta.\nDetalle: {e_imp}")
        sys.exit(1)

# --- Constantes ---
APP_NAME = "Natural a JSON - Analizador PRO"
ORG_NAME = "MiProyecto" # Para QSettings

# Definir rutas relativas a la raíz del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DEFAULT_EXAMPLES_DIR = os.path.join(PROJECT_ROOT, 'examples', 'valid')
DEFAULT_OUTPUT_DIR = "salidas_json"

class NaturalSyntaxHighlighter(QSyntaxHighlighter):
    """
    Resaltador de sintaxis básico para el editor de entrada.

    Identifica palabras clave, identificadores, números, cadenas y comentarios
    basándose en expresiones regulares simples y les aplica formatos de texto
    (color, estilo de fuente) para mejorar la legibilidad del código de entrada.
    """
    def __init__(self, parent=None):
        """
        Inicializa el resaltador de sintaxis.

        Define las reglas de resaltado (patrones de expresiones regulares y
        formatos de texto asociados) para los diferentes elementos del lenguaje.
        """
        super().__init__(parent)
        # Lista para almacenar tuplas de (QRegExp, QTextCharFormat)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat(); keyword_format.setForeground(QColor("#000080")); keyword_format.setFontWeight(QFont.Bold)
        keywords = ["CREAR", "OBJETO", "LISTA", "CON", "ELEMENTOS", "VERDADERO", "FALSO"] # Insensible en lexer, aquí sensible
        # Añadir variantes en minúsculas y capitalizadas para el resaltado visual
        keywords_variants = []; [keywords_variants.extend([kw, kw.lower(), kw.capitalize()]) for kw in keywords]

        # Reglas para palabras clave
        for word in keywords_variants:
            pattern = QRegExp(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Regla para identificadores 
        identifier_format = QTextCharFormat(); identifier_format.setForeground(QColor("#006400"))
        # Nota: Esta es una simplificación. Un resaltador completo usaría el lexer de ANTLR.
        self.highlighting_rules.append((QRegExp("\\b[a-zA-Z_ñÑáéíóúÁÉÍÓÚüÜ][a-zA-Z0-9_ñÑáéíóúÁÉÍÓÚüÜ]*\\b"), identifier_format))
        
        # Regla para números (enteros y decimales)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#8B0000")) # Rojo oscuro
        self.highlighting_rules.append((QRegExp("\\b-?[0-9]+(\\.[0-9]+)?\\b"), number_format))

        # Regla para cadenas (strings entre comillas dobles)
        string_format = QTextCharFormat(); string_format.setForeground(QColor("#A52A2A"))
        self.highlighting_rules.append((QRegExp("\".*\""), string_format))

        # Regla para comentarios (líneas que empiezan con //)
        comment_format = QTextCharFormat(); comment_format.setForeground(QColor("#008080")); comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp("//[^\n]*"), comment_format))

    def highlightBlock(self, text):
        """
        Aplica las reglas de resaltado al bloque de texto actual.

        Este método es llamado por QSyntaxHighlighter para cada bloque de texto
        (generalmente una línea) que necesita ser resaltado.

        Args:
            text (str): El texto del bloque actual.
        """
        # Itera sobre cada regla de resaltado definida
        for pattern, format_rule in self.highlighting_rules:
            expression = QRegExp(pattern); index = expression.indexIn(text)
            # Mientras se encuentren coincidencias del patrón en el texto
            while index >= 0:
                length = expression.matchedLength(); self.setFormat(index, length, format_rule); index = expression.indexIn(text, index + length)
        # Establece el estado del bloque actual 
        self.setCurrentBlockState(0)

class NaturalToJsonApp(QMainWindow): # Cambiado a QMainWindow
    """
    Clase principal de la aplicación GUI "Natural a JSON".

    Hereda de QMainWindow y configura la interfaz de usuario, maneja los eventos
    de los widgets (botones, checkboxes, etc.), interactúa con el `analyzer_core`
    para procesar la entrada, y muestra los resultados.
    También gestiona la carga y guardado de archivos y la persistencia de
    configuraciones básicas como el último directorio usado y la geometría de la ventana.
    """
    def __init__(self):
        """
        Inicializa la ventana principal de la aplicación.
        Configura el título, la geometría inicial, carga las configuraciones guardadas,
        e inicializa la interfaz de usuario.
        """
        super().__init__()
        self.setWindowTitle("Natural a JSON - Analizador PRO v2")
        self.setGeometry(50, 50, 1440, 880)
        self.settings = QSettings("MiProyecto", "NaturalToJsonApp") 
        self.initUI()
        self.current_input_filepath = None
        # Initialize last_used_dir, defaulting to DEFAULT_EXAMPLES_DIR if not found in settings
        self.last_used_dir = self.settings.value("lastUsedDirectory", DEFAULT_EXAMPLES_DIR)
        # self.readSettings() # Cargar geometría al final de __init__ o después de mostrar

    def initUI(self):
        """
        Construye la interfaz gráfica de usuario.

        Organiza los widgets (editores de texto, botones, labels, tree view, etc.)
        en layouts y groupboxes. Configura los splitters para permitir
        el redimensionamiento de las áreas de salida. Conecta las señales de los
        widgets (ej. `clicked` de un botón) a sus respectivos slots (métodos manejadores).
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Menú (si se usa QMainWindow) ---
        # self.createActions()
        # self.createMenus() 

        # --- Grupo de Entrada ---
        input_groupbox = QGroupBox("Entrada de Comandos")
        input_groupbox.setFont(QFont("Arial", 11, QFont.Bold))
        input_layout = QVBoxLayout()
        self.input_text_edit = QTextEdit()
        self.input_text_edit.setFont(QFont("Consolas", 11))
        self.input_text_edit.setPlaceholderText("Ej: CREAR OBJETO miLibro CON titulo:\"El Quijote\"...")
        self.highlighter = NaturalSyntaxHighlighter(self.input_text_edit.document()) # Aplicar resaltador de sintaxis
        input_layout.addWidget(self.input_text_edit)
        
        # Layout para botones de acción de entrada
        action_buttons_layout = QHBoxLayout()
        self.load_button = QPushButton(" Cargar Archivo..."); self.load_button.clicked.connect(self.loadFile)
        action_buttons_layout.addWidget(self.load_button)
        self.save_input_button = QPushButton(" Guardar Entrada..."); self.save_input_button.clicked.connect(self.saveInputText)
        action_buttons_layout.addWidget(self.save_input_button)
        action_buttons_layout.addStretch()
        self.help_button = QPushButton(" Ayuda/Ejemplos"); self.help_button.clicked.connect(self.showHelp)
        action_buttons_layout.addWidget(self.help_button)
        self.clear_button = QPushButton(" Limpiar Todo"); self.clear_button.clicked.connect(self.clearAllFields)
        action_buttons_layout.addWidget(self.clear_button)
        self.analyze_button = QPushButton(" Analizar y Convertir")
        self.analyze_button.setStyleSheet("font-weight: bold; padding: 8px; background-color: #4CAF50; color: white;")
        self.analyze_button.clicked.connect(self.runAnalysis)
        action_buttons_layout.addWidget(self.analyze_button)
        
        input_layout.addLayout(action_buttons_layout)
        input_groupbox.setLayout(input_layout)

        # --- Grupo de Salida con Splitter y Checkboxes para visibilidad ---
        output_groupbox = QGroupBox("Resultados del Análisis")
        output_groupbox.setFont(QFont("Arial", 11, QFont.Bold))
        output_main_layout = QVBoxLayout()

        # Checkboxes para controlar la visibilidad de las secciones de salida
        visibility_layout = QHBoxLayout()
        self.cb_show_tokens = QCheckBox("Mostrar Tokens"); self.cb_show_tokens.setChecked(True); self.cb_show_tokens.toggled.connect(self.toggleOutputVisibility)
        visibility_layout.addWidget(self.cb_show_tokens)
        self.cb_show_tree = QCheckBox("Mostrar Árbol de Parseo"); self.cb_show_tree.setChecked(True); self.cb_show_tree.toggled.connect(self.toggleOutputVisibility)
        visibility_layout.addWidget(self.cb_show_tree)
        visibility_layout.addStretch()
        output_main_layout.addLayout(visibility_layout)

        # Splitter principal para dividir las áreas de salida horizontalmente
        self.output_splitter = QSplitter(Qt.Horizontal)

        # Columna Izquierda (Tokens y Árbol)
        self.left_output_widget = QWidget() # Contenedor para visibilidad
        left_column_layout = QVBoxLayout(self.left_output_widget)
        
        self.tokens_output_label = QLabel("Tokens Reconocidos:")
        self.tokens_output_text = QPlainTextEdit(); self.tokens_output_text.setReadOnly(True); 
        self.tokens_output_text.setFont(QFont("Consolas", 9)); self.tokens_output_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        left_column_layout.addWidget(self.tokens_output_label)
        left_column_layout.addWidget(self.tokens_output_text)

        # QTreeView para mostrar el árbol de parseo de forma interactiva
        self.parsetree_output_label = QLabel("Árbol de Parseo Interactivo:")
        self.parsetree_view = QTreeView()
        self.parsetree_view.setFont(QFont("Arial", 9))
        self.parsetree_view.setHeaderHidden(True) # No necesitamos encabezados de columna
        self.parsetree_view.setAlternatingRowColors(True)
        left_column_layout.addWidget(self.parsetree_output_label)
        left_column_layout.addWidget(self.parsetree_view)
        
        self.output_splitter.addWidget(self.left_output_widget)

        # Columna Derecha (JSON y Errores)
        right_column_widget = QWidget()
        right_column_layout = QVBoxLayout(right_column_widget)
        self.json_output_label = QLabel("JSON Generado:")
        self.json_output_text = QPlainTextEdit(); self.json_output_text.setReadOnly(True); 
        self.json_output_text.setFont(QFont("Consolas", 10)); self.json_output_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        right_column_layout.addWidget(self.json_output_label)
        right_column_layout.addWidget(self.json_output_text)

        # Área para mostrar errores
        self.errors_output_label = QLabel("Resumen de Errores:")
        self.errors_output_text = QPlainTextEdit()
        self.errors_output_text.setReadOnly(True)
        self.errors_output_text.setFont(QFont("Consolas", 9))
        self.errors_output_text.setStyleSheet("color: #B71C1C; background-color: #FFCDD2;")
        right_column_layout.addWidget(self.errors_output_label)
        right_column_layout.addWidget(self.errors_output_text)
        
        self.output_splitter.addWidget(right_column_widget)
        self.output_splitter.setSizes([self.width() // 2, self.width() // 2]) # Distribuir espacio equitativamente

        output_main_layout.addWidget(self.output_splitter)
        
        # Layout para estadísticas y botón de guardar JSON
        stats_and_save_layout = QHBoxLayout()
        self.stats_label = QLabel("Estadísticas: N/A")
        stats_and_save_layout.addWidget(self.stats_label, 1)
        self.save_json_button = QPushButton(" Guardar JSON...");
        self.save_json_button.clicked.connect(self.saveJsonOutput); self.save_json_button.setEnabled(False)
        stats_and_save_layout.addWidget(self.save_json_button)
        output_main_layout.addLayout(stats_and_save_layout)

        output_groupbox.setLayout(output_main_layout)

        # Barra de estado
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Listo.")

        main_layout.addWidget(input_groupbox, 2) # Ajustar stretch factors
        main_layout.addWidget(output_groupbox, 5) # Dar más espacio vertical al grupo de salida
        
        self.toggleOutputVisibility() # Aplicar visibilidad inicial de las secciones de salida

    def clearAllFields(self):
        """
        Limpia todos los campos de texto de entrada y salida, y resetea el estado.
        Esto incluye el editor de entrada, los visores de tokens, árbol de parseo,
        JSON, errores, y la etiqueta de estadísticas. También deshabilita el botón
        de guardar JSON y resetea la ruta del archivo actual.
        """
        self.input_text_edit.clear()
        self.tokens_output_text.clear()
        self.parsetree_view.setModel(QStandardItemModel()) # Asignar un modelo vacío para limpiar el QTreeView
        self.json_output_text.clear()
        self.errors_output_text.clear()
        self.save_json_button.setEnabled(False)
        self.current_input_filepath = None
        self.stats_label.setText("Estadísticas: N/A")
        self.statusBar.showMessage("Campos limpiados. Listo.")
        self.input_text_edit.setFocus()

    def toggleOutputVisibility(self):
        """
        Alterna la visibilidad de las secciones de Tokens y Árbol de Parseo
        basándose en el estado de sus respectivos checkboxes.
        Si ambas secciones (tokens y árbol) están ocultas, el widget contenedor
        de la columna izquierda también se oculta.
        """
        self.tokens_output_label.setVisible(self.cb_show_tokens.isChecked())
        self.tokens_output_text.setVisible(self.cb_show_tokens.isChecked())
        
        self.parsetree_output_label.setVisible(self.cb_show_tree.isChecked())
        self.parsetree_view.setVisible(self.cb_show_tree.isChecked())
        
        # Ocultar el widget contenedor de la columna izquierda si ambas secciones están desactivadas
        self.left_output_widget.setVisible(self.cb_show_tokens.isChecked() or self.cb_show_tree.isChecked())

    def showHelp(self):
        """
        Muestra una ventana de diálogo (QMessageBox) con información de ayuda
        sobre la sintaxis del lenguaje "Natural a JSON" y ejemplos de uso.
        """
        help_text = """
        <h2>Ayuda - Sintaxis "Natural a JSON"</h2>
        <p>Este analizador convierte comandos simples en español a formato JSON.</p>
        
        <h3>Comandos Soportados:</h3>
        <ol>
            <li><b>Crear Objeto:</b>
                <pre>CREAR OBJETO <nombreDelObjeto> CON <clave1>:<valor1>, <clave2>:<valor2>, ...</pre>
                <p>Ejemplo:</p>
                <pre>CREAR OBJETO libro CON titulo:"Cien Años", autor:"Gabo", publicado:1967, bestseller:VERDADERO</pre>
            </li>
            <li><b>Crear Lista:</b>
                <pre>CREAR LISTA <nombreDeLaLista> CON ELEMENTOS <valor1>, <valor2>, ...</pre>
                <p>Ejemplo:</p>
                <pre>CREAR LISTA compras CON ELEMENTOS "Leche", "Huevos", 12, 3.50, FALSO</pre>
            </li>
        </ol>

        <h3>Tipos de Valores Soportados:</h3>
        <ul>
            <li><b>Texto (String):</b> Entre comillas dobles. Ej: <code>"Hola Mundo"</code></li>
            <li><b>Número Entero:</b> Ej: <code>123</code>, <code>-45</code></li>
            <li><b>Número Decimal:</b> Ej: <code>3.14</code>, <code>-0.05</code></li>
            <li><b>Booleano:</b> <code>VERDADERO</code> o <code>FALSO</code> (insensible a mayúsculas)</li>
        </ul>
        """
        QMessageBox.about(self, "Ayuda - Natural a JSON", help_text)

    def loadFile(self):
        """
        Abre un diálogo QFileDialog para que el usuario seleccione un archivo de texto (.txt).
        Si se selecciona un archivo, su contenido se carga en el editor de entrada.
        Actualiza `current_input_filepath` y `last_used_dir` (que se guarda en QSettings).
        """
        options = QFileDialog.Options()
        
        # Determine initial directory: use last_used_dir if valid, otherwise DEFAULT_EXAMPLES_DIR
        initial_dir = self.last_used_dir if (self.last_used_dir and os.path.exists(self.last_used_dir)) else DEFAULT_EXAMPLES_DIR
        
        fileName, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo de Prueba", initial_dir, "Archivos de Texto (*.txt);;Todos los Archivos (*)", options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as f:
                    self.input_text_edit.setPlainText(f.read())
                self.current_input_filepath = fileName
                self.last_used_dir = os.path.dirname(fileName)
                self.settings.setValue("lastUsedDirectory", self.last_used_dir)
                self.statusBar.showMessage(f"Archivo '{os.path.basename(fileName)}' cargado.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error al Cargar", f"No se pudo cargar el archivo:\n{e}")
                self.statusBar.showMessage("Error al cargar archivo.", 5000)

    def saveInputText(self):
        """
        Guarda el contenido actual del editor de entrada en un archivo de texto.

        Abre un diálogo QFileDialog para que el usuario elija la ubicación y el nombre
        del archivo. Si el archivo actual tiene un nombre (porque fue cargado o guardado
        previamente), se sugiere ese nombre. Actualiza `current_input_filepath` y
        `last_used_dir`.
        Muestra mensajes en la barra de estado.
        """
        content = self.input_text_edit.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Guardar Entrada", "No hay contenido para guardar.")
            return

        options = QFileDialog.Options()
        suggested_name = os.path.basename(self.current_input_filepath) if self.current_input_filepath else "entrada.txt"
        # Sugerir guardar en el último directorio usado
        fileName, _ = QFileDialog.getSaveFileName(self, "Guardar Entrada como Archivo de Texto", 
                                                  os.path.join(self.last_used_dir, suggested_name),
                                                  "Archivos de Texto (*.txt);;Todos los Archivos (*)", options=options)
        if fileName:
            if not fileName.endswith(".txt"): fileName += ".txt"
            try:
                with open(fileName, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_input_filepath = fileName
                self.last_used_dir = os.path.dirname(fileName)
                self.settings.setValue("lastUsedDirectory", self.last_used_dir)
                self.statusBar.showMessage(f"Entrada guardada en '{os.path.basename(fileName)}'.", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar la entrada:\n{e}")
                self.statusBar.showMessage("Error al guardar entrada.", 5000)

    def runAnalysis(self):
        """
        Ejecuta el proceso de análisis del contenido del editor de entrada.

        Primero, limpia los campos de salida y muestra un mensaje de "Analizando...".
        Luego, llama a la función `analyze_and_transform` del `analyzer_core`.
        Los resultados (JSON, tokens, modelo del árbol de parseo, errores, estadísticas)
        se muestran en los widgets correspondientes de la GUI.
        Actualiza la barra de estado y la etiqueta de estadísticas.
        Habilita el botón "Guardar JSON" si el análisis fue exitoso y se generó JSON.
        Maneja excepciones críticas que puedan ocurrir durante el análisis.
        """
        # Obtener el contenido del editor de entrada
        input_content = self.input_text_edit.toPlainText()
        # Validar que haya contenido para analizar
        if not input_content.strip():
            QMessageBox.warning(self, "Entrada Vacía", "Por favor, ingresa comandos o carga un archivo.")
            self.statusBar.showMessage("Análisis cancelado: entrada vacía.", 5000)
            return

        self.tokens_output_text.clear()
        # self.parsetree_output_text.clear() # Ya no existe
        self.parsetree_view.setModel(QStandardItemModel()) # Limpiar vista de árbol asignando un modelo vacío
        self.json_output_text.clear()
        self.errors_output_text.clear()
        self.stats_label.setText("Estadísticas: N/A")
        self.save_json_button.setEnabled(False)
        self.statusBar.showMessage("Analizando... Por favor espera.", 3000) # Mensaje temporal
        QApplication.processEvents() # Asegurar que la GUI se actualice (ej. mensaje "Analizando...")

        # Determinar el nombre de la fuente para los mensajes de error
        source_name = os.path.basename(self.current_input_filepath) if self.current_input_filepath else "entrada_directa_gui"
        
        try:
            # Llamada al motor de análisis.
            # Devuelve: json_s, tokens_s, _parsetree_lisp, parsetree_qt_model, errors_s, stats
            json_s, tokens_s, _parsetree_lisp, parsetree_qt_model, errors_s, stats = analyze_and_transform(source_name, input_content)

            # Mostrar tokens
            self.tokens_output_text.setPlainText(tokens_s)
            
            # Mostrar errores si los hay
            if errors_s:
                self.errors_output_text.setPlainText(errors_s)
            
            # Si no hubo errores y se generó JSON y el modelo del árbol
            if json_s and parsetree_qt_model: # Si no hubo errores y se generó el modelo del árbol
                self.parsetree_view.setModel(parsetree_qt_model) # Asignar el modelo al QTreeView
                self.parsetree_view.expandAll() # Expandir todos los nodos por defecto
                self.json_output_text.setPlainText(json_s)
                self.save_json_button.setEnabled(True)
                self.statusBar.showMessage(f"Análisis completado para '{source_name}'. JSON generado.", 10000)
            elif errors_s: # Si hubo errores, incluso si algo se generó parcialmente
                self.statusBar.showMessage(f"Análisis para '{source_name}' completado con errores.", 10000)
            else: # Caso de entrada vacía o solo comentarios (sin errores, sin JSON)
                self.statusBar.showMessage(f"Análisis para '{source_name}' finalizado. No se generó JSON (entrada vacía o solo comentarios).", 10000)
            
            # Mostrar estadísticas
            if stats:
                stats_text = (f"Tiempo: {stats['tiempo_analisis_seg']}s | "
                              f"Comandos: {stats['comandos_procesados']} | "
                              f"Tokens (Parser): {stats['tokens_al_parser']} | "
                              f"Err.Léxicos: {stats['errores_lexicos']} | "
                              f"Err.Sintácticos: {stats['errores_sintacticos']}")
                self.stats_label.setText(stats_text)

        except Exception as e:
            critical_error_msg = f"Error Crítico en Motor de Análisis:\n{type(e).__name__}: {e}\n{e.__traceback__}"
            QMessageBox.critical(self, "Error Crítico en Análisis", critical_error_msg)
            self.errors_output_text.setPlainText(critical_error_msg)
            self.statusBar.showMessage("Error crítico durante el análisis.", 5000)

    def saveJsonOutput(self):
        """
        Guarda el JSON generado (contenido del `json_output_text`) en un archivo.

        Abre un diálogo QFileDialog para que el usuario elija la ubicación y el nombre
        del archivo JSON. Sugiere un nombre de archivo basado en el archivo de entrada
        original (si existe) y un subdirectorio `DEFAULT_OUTPUT_DIR`.
        Crea el directorio de salida si no existe.
        Muestra mensajes en la barra de estado.
        """
        json_content = self.json_output_text.toPlainText()
        if not json_content.strip():
            QMessageBox.warning(self, "Guardar JSON", "No hay JSON generado para guardar.")
            return
        
        options = QFileDialog.Options(); default_filename = "salida.json"
        # Sugerir un nombre de archivo basado en el archivo de entrada
        if self.current_input_filepath: base, _ = os.path.splitext(os.path.basename(self.current_input_filepath)); default_filename = base + "_output.json"
        
        # Intentar crear/usar un subdirectorio para las salidas JSON
        output_dir_to_try = os.path.join(self.last_used_dir, DEFAULT_OUTPUT_DIR)
        if not os.path.exists(output_dir_to_try):
            try: 
                os.makedirs(output_dir_to_try)
                # Si se crea el directorio, actualizar last_used_dir para que el diálogo se abra aquí
                # self.last_used_dir = output_dir_to_try # Opcional: ¿queremos que el diálogo se abra aquí la próxima vez?
            except OSError: output_dir_to_try = self.last_used_dir # Fallback al último directorio usado
        
        fileName, _ = QFileDialog.getSaveFileName(self, "Guardar JSON Generado", os.path.join(output_dir_to_try, default_filename),
                                                   "Archivos JSON (*.json);;Todos (*)", options=options)
        if fileName:
            if not fileName.endswith(".json"): fileName += ".json"
            try:
                with open(fileName, 'w', encoding='utf-8') as f: f.write(json_content)
                self.statusBar.showMessage(f"JSON guardado en '{os.path.basename(fileName)}'.", 5000)
                # Actualizar el último directorio usado si el guardado fue exitoso
                self.last_used_dir = os.path.dirname(fileName); self.settings.setValue("lastUsedDirectory", self.last_used_dir)
            except Exception as e: QMessageBox.critical(self, "Error al Guardar JSON", f"No se pudo guardar:\n{e}"); 
            self.statusBar.showMessage("Error al guardar JSON.", 5000)

    def closeEvent(self, event):
        """
        Manejador del evento de cierre de la ventana.

        Guarda la geometría actual de la ventana y el último directorio utilizado
        en QSettings antes de que la aplicación se cierre.
        """
        self.settings.setValue("lastUsedDirectory", self.last_used_dir)
        self.settings.setValue("windowGeometry", self.saveGeometry())
        super().closeEvent(event)

    def readSettings(self):
        """
        Carga las configuraciones guardadas al iniciar la aplicación.

        Restaura la geometría de la ventana y el último directorio utilizado
        desde QSettings. Se llama típicamente al final de `__init__` o
        justo antes de mostrar la ventana.
        """
        geometry = self.settings.value("windowGeometry")
        if geometry: self.restoreGeometry(geometry)
        self.last_used_dir = self.settings.value("lastUsedDirectory", os.path.expanduser("~"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NaturalToJsonApp()
    ex.readSettings() # Cargar geometría y último directorio antes de mostrar
    ex.show()
    sys.exit(app.exec_())