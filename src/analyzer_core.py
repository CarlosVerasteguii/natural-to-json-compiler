# analyzer_core.py
"""
Módulo central del analizador "Natural a JSON".

Este módulo contiene la lógica principal para procesar una cadena de entrada
en un lenguaje pseudo-natural, realizar el análisis léxico y sintáctico
utilizando ANTLR, y transformar la entrada en una representación JSON.
También se encarga de la gestión de errores, la generación de una lista de tokens,
la creación de un árbol de parseo (tanto en formato LISP como en un modelo
para QTreeView de PyQt5), y la recopilación de estadísticas del análisis.
"""
import sys
import json
import time
from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.tree.Trees import Trees
from antlr4.error.ErrorListener import ErrorListener

# Importaciones de PyQt5 para el modelo del árbol
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

# Add 'generated' to sys.path relative to this script's location
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(current_dir, 'generated')
if generated_dir not in sys.path:
    sys.path.append(generated_dir)

from NaturalToJsonLexer import NaturalToJsonLexer
from NaturalToJsonParser import NaturalToJsonParser
from NaturalToJsonListener import NaturalToJsonListener
from optimizer import optimize_ir

# --- Estructuras de Datos para Análisis Semántico ---

class SymbolEntry:
    """
    Representa una entrada en la tabla de símbolos.
    Almacena información sobre una entidad declarada (objeto o lista).
    """
    def __init__(self, nombre, tipo_entidad, linea, columna, metadatos=None):
        self.nombre = nombre
        self.tipo_entidad = tipo_entidad  # "objeto" o "lista"
        self.linea = linea
        self.columna = columna
        self.metadatos = metadatos or {}

class SymbolTable:
    """
    Gestiona la tabla de símbolos global.
    Permite declarar símbolos y verificar si existen o si son palabras reservadas.
    """
    def __init__(self):
        self.symbols = {}
        # Palabras reservadas del lenguaje (insensibles a mayúsculas/minúsculas)
        self.reserved_words = {
            "CREAR", "OBJETO", "LISTA", "CON", "ELEMENTOS", "VERDADERO", "FALSO"
        }

    def is_reserved(self, nombre):
        """Verifica si un nombre es una palabra reservada."""
        return nombre.upper() in self.reserved_words

    def lookup(self, nombre):
        """Busca un símbolo por nombre. Retorna SymbolEntry o None."""
        return self.symbols.get(nombre)

    def declare(self, nombre, tipo_entidad, linea, columna, metadatos=None):
        """
        Intenta declarar un nuevo símbolo.
        Retorna True si se declaró exitosamente.
        Retorna False si el símbolo ya existe (redefinición).
        """
        if nombre in self.symbols:
            return False
        
        entry = SymbolEntry(nombre, tipo_entidad, linea, columna, metadatos)
        self.symbols[nombre] = entry
        return True
    
    def get_debug_info(self):
        """
        Retorna una representación simplificada de la tabla de símbolos para depuración/tests.
        """
        debug_info = {}
        for name, entry in self.symbols.items():
            debug_info[name] = {
                "tipo_entidad": entry.tipo_entidad,
                "metadatos": entry.metadatos
            }
        return debug_info

# --- Helpers ---

def get_value_type(ctx:NaturalToJsonParser.ValorContext):
    """
    Determina el tipo lógico de un valor dado su contexto de parseo.
    Retorna: "STRING", "NUMBER", "BOOLEAN" o "UNKNOWN".
    """
    if ctx.STRING():
        return "STRING"
    elif ctx.NUMERO_ENTERO() or ctx.NUMERO_DECIMAL():
        return "NUMBER"
    elif ctx.KW_VERDADERO() or ctx.KW_FALSO():
        return "BOOLEAN"
    return "UNKNOWN"

# --- Listeners ---

class CustomErrorListener(ErrorListener):
    """
    Listener de errores personalizado para ANTLR.

    Captura errores léxicos y sintácticos, los traduce a mensajes más
    amigables en español y los almacena para su posterior visualización.
    Ahora también soporta errores semánticos.
    """
    def __init__(self, source_name="<input>"):
        """
        Inicializa el listener de errores.

        Args:
            source_name (str, optional): Nombre del archivo o fuente de entrada
                                         para incluir en los mensajes de error.
                                         Defaults to "<input>".
        """
        # Llamada al constructor de la clase base ErrorListener
        super().__init__()
        self.source_name = source_name
        self._lexer_errors = 0
        self._parser_errors = 0
        self._semantic_errors = 0 # Contador de errores semánticos
        self.error_messages = []

    @property
    def lexer_errors(self):
        """Retorna el número de errores léxicos detectados."""
        return self._lexer_errors
    @property
    def parser_errors(self):
        """Retorna el número de errores sintácticos detectados."""
        return self._parser_errors
    @property
    def semantic_errors(self):
        """Retorna el número de errores semánticos detectados."""
        return self._semantic_errors

    def add_semantic_error(self, line, column, message):
        """
        Registra un error semántico manualmente.
        """
        self._semantic_errors += 1
        final_error_message = f"Error Semántico en '{self.source_name}' (Línea {line}:Columna {column}): {message}"
        self.error_messages.append(final_error_message)

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Callback invocado por ANTLR cuando se detecta un error de sintaxis.

        Este método personaliza el mensaje de error, intentando traducirlo
        y hacerlo más comprensible para el usuario final.

        Args:
            recognizer: El objeto lexer o parser que detectó el error.
            offendingSymbol: El token que causó el error.
            line: El número de línea donde ocurrió el error.
            column: La posición de la columna donde ocurrió el error.
            msg: El mensaje de error original de ANTLR.
            e: La excepción de reconocimiento (RecognitionException) asociada.
        """
        error_type = "Desconocido"
        user_column = column + 1  # Ajustar columna para que sea 1-indexed
        detailed_msg = msg
        is_lexer_error = isinstance(recognizer, NaturalToJsonLexer)

        if is_lexer_error:
            self._lexer_errors += 1
            error_type = "Léxico"
            if "token recognition error at: '" in msg:
                # Intenta extraer el carácter problemático del mensaje de ANTLR
                try:
                    char_problem = msg.split("token recognition error at: '")[1][:-1]
                    detailed_msg = f"Carácter inesperado o no reconocido: '{char_problem}'."
                except IndexError: detailed_msg = "Error de reconocimiento de token no especificado."
            else: detailed_msg = f"Error léxico general: {msg}"
        else:
            # Es un error sintáctico (del parser)
            self._parser_errors += 1
            error_type = "Sintáctico"
            offending_text = offendingSymbol.text if offendingSymbol else ""
            if offending_text == '<EOF>': offending_text = "fin de la entrada"
            
            if "mismatched input" in msg and "expecting" in msg:
                try:
                    # Ej: "mismatched input 'X' expecting Y" -> "Se encontró 'X' pero se esperaba Y."
                    expected_tokens = msg.split("expecting ")[1]
                    detailed_msg = f"Se encontró '{offending_text}' pero se esperaba {expected_tokens}."
                except: detailed_msg = f"Entrada no coincide: '{offending_text}'. {msg}"
            elif "extraneous input" in msg and "expecting" in msg:
                try:
                    # Ej: "extraneous input 'X' expecting Y" -> "Entrada adicional 'X'. Se esperaba Y."
                    expected_tokens = msg.split("expecting ")[1]
                    detailed_msg = f"Entrada adicional o fuera de lugar: '{offending_text}'. Se esperaba {expected_tokens} antes o después."
                except: detailed_msg = f"Entrada sobrante: '{offending_text}'. {msg}"
            elif "missing" in msg and "at" in msg:
                try:
                    # Ej: "missing X at 'Y'" -> "Falta X cerca de 'Y'."
                    missing_token = msg.split("missing ")[1].split(" at")[0]
                    detailed_msg = f"Falta el símbolo/palabra clave '{missing_token}' cerca de '{offending_text}'."
                except: detailed_msg = f"Elemento faltante. {msg}"
            elif "no viable alternative at input" in msg:
                # Error genérico cuando el parser no puede encontrar una regla que coincida
                detailed_msg = f"No se reconoce la estructura del comando cerca de '{offending_text}'. Verifica la sintaxis."
            else: detailed_msg = f"Error de estructura cerca de '{offending_text}'. Detalle: {msg}"
        
        # Formateo final del mensaje de error
        final_error_message = f"Error {error_type} en '{self.source_name}' (Línea {line}:Columna {user_column}): {detailed_msg}"
        self.error_messages.append(final_error_message)

    def get_total_errors(self):
        """Retorna el número total de errores (léxicos + sintácticos + semánticos)."""
        return self._lexer_errors + self._parser_errors + self._semantic_errors

    def get_error_summary_string(self):
        """
        Genera una cadena formateada con el resumen de todos los errores detectados.

        Returns:
            str: Una cadena con el resumen de errores, o una cadena vacía
                 si no se detectaron errores.
        """
        if not self.error_messages: return ""
        # Construcción del encabezado y lista de errores
        summary = "╔═════════════════════════════════════╗\n"
        summary += "║     Resumen de Errores Detectados     ║\n"
        summary += "╚═════════════════════════════════════╝\n"
        summary += "\n".join([f"  ⚠️  {emsg}" for emsg in self.error_messages])
        return summary

class SemanticAnalyzer(NaturalToJsonListener):
    """
    Listener de ANTLR para el análisis semántico.
    Verifica reglas como unicidad de nombres y uso de palabras reservadas.
    También recolecta metadatos de tipos.
    """
    def __init__(self, error_listener, symbol_table):
        self.error_listener = error_listener
        self.symbol_table = symbol_table
        self.current_symbol_name = None # Para saber a qué símbolo asociar propiedades/elementos

    def enterCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        nombre = ctx.nombre_obj.text
        linea = ctx.start.line
        columna = ctx.start.column + 1

        # SEM002: Verificar palabra reservada
        if self.symbol_table.is_reserved(nombre):
            self.error_listener.add_semantic_error(
                linea, columna, 
                f"El nombre '{nombre}' es una palabra reservada del lenguaje y no puede usarse como identificador."
            )
            self.current_symbol_name = None
            return

        # SEM001: Verificar redefinición
        # Inicializamos metadatos con estructura para propiedades
        metadatos = {"propiedades": {}}
        exito = self.symbol_table.declare(nombre, "objeto", linea, columna, metadatos)
        
        if not exito:
            entry_prev = self.symbol_table.lookup(nombre)
            self.error_listener.add_semantic_error(
                linea, columna,
                f"Redefinición del símbolo '{nombre}'. Ya fue declarado como '{entry_prev.tipo_entidad}' en la línea {entry_prev.linea}."
            )
            self.current_symbol_name = None
        else:
            self.current_symbol_name = nombre

    def exitCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        self.current_symbol_name = None

    def enterPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        if self.current_symbol_name:
            clave = ctx.clave.text
            valor_ctx = ctx.valor()
            tipo_valor = get_value_type(valor_ctx)
            
            # Guardar tipo en metadatos del símbolo actual
            entry = self.symbol_table.lookup(self.current_symbol_name)
            if entry and entry.tipo_entidad == "objeto":
                entry.metadatos["propiedades"][clave] = tipo_valor

    def enterCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        nombre = ctx.nombre_lista.text
        linea = ctx.start.line
        columna = ctx.start.column + 1

        # SEM002: Verificar palabra reservada
        if self.symbol_table.is_reserved(nombre):
            self.error_listener.add_semantic_error(
                linea, columna, 
                f"El nombre '{nombre}' es una palabra reservada del lenguaje y no puede usarse como identificador."
            )
            self.current_symbol_name = None
            return

        # SEM001: Verificar redefinición
        # Inicializamos metadatos con estructura para elementos
        metadatos = {"tipos_elementos": []}
        exito = self.symbol_table.declare(nombre, "lista", linea, columna, metadatos)
        
        if not exito:
            entry_prev = self.symbol_table.lookup(nombre)
            self.error_listener.add_semantic_error(
                linea, columna,
                f"Redefinición del símbolo '{nombre}'. Ya fue declarado como '{entry_prev.tipo_entidad}' en la línea {entry_prev.linea}."
            )
            self.current_symbol_name = None
        else:
            self.current_symbol_name = nombre

    def exitCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        self.current_symbol_name = None

    def enterValor(self, ctx:NaturalToJsonParser.ValorContext):
        # Solo nos interesa si estamos dentro de una lista (para objetos lo manejamos en enterPropiedad)
        if self.current_symbol_name:
            entry = self.symbol_table.lookup(self.current_symbol_name)
            if entry and entry.tipo_entidad == "lista":
                # Verificar si el padre es items_lista para confirmar que es un elemento de lista
                # (aunque la estructura de la gramática lo garantiza si estamos en enterValor dentro de Crear_lista_cmd)
                 tipo_valor = get_value_type(ctx)
                 entry.metadatos["tipos_elementos"].append(tipo_valor)


# --- Estructuras para Representación Intermedia (IR) ---

class IRInstruction:
    """
    Representa una instrucción de la Representación Intermedia (IR).
    """
    def __init__(self, opcode, args):
        self.opcode = opcode
        self.args = args

    def to_dict(self):
        return {"opcode": self.opcode, "args": self.args}

class IRBuilderListener(NaturalToJsonListener):
    """
    Listener que construye la Representación Intermedia (IR) a partir del AST.
    Genera una lista lineal de instrucciones.
    """
    def __init__(self):
        self.ir_instructions = []
        self.current_obj_name = None
        self.current_list_name = None

    def get_instructions(self):
        return [instr.to_dict() for instr in self.ir_instructions]

    def enterCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        nombre = ctx.nombre_obj.text
        self.current_obj_name = nombre
        self.ir_instructions.append(IRInstruction("IR_CREATE_OBJECT", [nombre]))

    def exitCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        self.current_obj_name = None

    def exitPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        if self.current_obj_name:
            clave = ctx.clave.text
            valor_ctx = ctx.valor()
            tipo_valor = get_value_type(valor_ctx)
            
            # Extraer valor nativo de Python
            valor_nativo = None
            if valor_ctx.STRING():
                valor_nativo = valor_ctx.STRING().getText()[1:-1]
            elif valor_ctx.NUMERO_ENTERO():
                valor_nativo = int(valor_ctx.NUMERO_ENTERO().getText())
            elif valor_ctx.NUMERO_DECIMAL():
                valor_nativo = float(valor_ctx.NUMERO_DECIMAL().getText())
            elif valor_ctx.KW_VERDADERO():
                valor_nativo = True
            elif valor_ctx.KW_FALSO():
                valor_nativo = False
            
            self.ir_instructions.append(IRInstruction(
                "IR_SET_PROPERTY", 
                [self.current_obj_name, clave, tipo_valor, valor_nativo]
            ))

    def enterCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        nombre = ctx.nombre_lista.text
        self.current_list_name = nombre
        self.ir_instructions.append(IRInstruction("IR_CREATE_LIST", [nombre]))

    def exitCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        self.current_list_name = None

    def exitValor(self, ctx:NaturalToJsonParser.ValorContext):
        # Verificar si estamos dentro de una lista
        # El padre de un valor en una lista es Items_listaContext
        if self.current_list_name and isinstance(ctx.parentCtx, NaturalToJsonParser.Items_listaContext):
            tipo_valor = get_value_type(ctx)
            
            # Extraer valor nativo
            valor_nativo = None
            if ctx.STRING():
                valor_nativo = ctx.STRING().getText()[1:-1]
            elif ctx.NUMERO_ENTERO():
                valor_nativo = int(ctx.NUMERO_ENTERO().getText())
            elif ctx.NUMERO_DECIMAL():
                valor_nativo = float(ctx.NUMERO_DECIMAL().getText())
            elif ctx.KW_VERDADERO():
                valor_nativo = True
            elif ctx.KW_FALSO():
                valor_nativo = False
            
            self.ir_instructions.append(IRInstruction(
                "IR_APPEND_LIST",
                [self.current_list_name, tipo_valor, valor_nativo]
            ))

# --- Listener para Construir JSON ---
class JsonBuilderListener(NaturalToJsonListener):
    """
    Listener de ANTLR que construye una estructura de datos Python (diccionario)
    a partir del árbol de parseo, la cual luego se serializa a JSON.

    Este listener maneja el estado mientras recorre el árbol para crear
    objetos y listas anidadas según la gramática definida.
    """
    def __init__(self):
        """
        Inicializa el constructor de JSON.

        Configura las estructuras de datos internas para almacenar el JSON resultante.
        """
        self.result_data = {}
        self.current_object_name = None
        self.current_object_props = {}
        self.current_list_name = None
        self.current_list_items = []
        self.current_key = None

    def get_final_json_string(self):
        """
        Serializa la estructura de datos interna a una cadena JSON formateada.

        Returns:
            str: La representación JSON de los datos procesados.
        """
        return json.dumps(self.result_data, indent=2, ensure_ascii=False)

    def enterCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        """
        Invocado al entrar en la regla 'crear_objeto_cmd'.
        Prepara el estado para un nuevo objeto JSON.
        """
        self.current_object_name = ctx.nombre_obj.text
        self.current_object_props = {}

    def exitCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        """
        Invocado al salir de la regla 'crear_objeto_cmd'.
        Almacena el objeto JSON completado en el resultado final.
        """
        if self.current_object_name:
            self.result_data[self.current_object_name] = self.current_object_props
        # Resetea el nombre del objeto actual para el siguiente comando
        self.current_object_name = None

    def enterPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        """
        Invocado al entrar en la regla 'propiedad'.
        Establece la clave de la propiedad actual que se está procesando.
        """
        self.current_key = ctx.clave.text

    def exitPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        """
        Invocado al salir de la regla 'propiedad'.
        Asigna el valor procesado a la clave actual dentro del objeto JSON.
        El atributo 'valor_procesado' es añadido al contexto por 'exitValor'.
        """
        if self.current_key and hasattr(ctx, 'valor_procesado'):
             self.current_object_props[self.current_key] = ctx.valor_procesado
        # Resetea la clave actual
        self.current_key = None

    def enterCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        """
        Invocado al entrar en la regla 'crear_lista_cmd'.
        Prepara el estado para una nueva lista JSON.
        """
        self.current_list_name = ctx.nombre_lista.text
        self.current_list_items = []

    def exitCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        """
        Invocado al salir de la regla 'crear_lista_cmd'.
        Almacena la lista JSON completada en el resultado final.
        """
        if self.current_list_name:
            self.result_data[self.current_list_name] = self.current_list_items
        # Resetea el nombre de la lista actual
        self.current_list_name = None

    def exitValor(self, ctx:NaturalToJsonParser.ValorContext):
        processed_value = None
        if ctx.STRING():
            processed_value = ctx.STRING().getText()[1:-1]
        elif ctx.NUMERO_ENTERO():
            processed_value = int(ctx.NUMERO_ENTERO().getText())
        elif ctx.NUMERO_DECIMAL():
            processed_value = float(ctx.NUMERO_DECIMAL().getText())
        elif ctx.KW_VERDADERO():
            processed_value = True
        elif ctx.KW_FALSO():
            processed_value = False
        
        # Determina dónde debe ir el valor procesado (a una propiedad de objeto o a una lista)
        parent_ctx = ctx.parentCtx
        if isinstance(parent_ctx, NaturalToJsonParser.PropiedadContext):
            # Si el padre es una 'propiedad', el valor pertenece a esa propiedad.
            # Se añade 'valor_procesado' al contexto de la propiedad para que 'exitPropiedad' lo use.
            parent_ctx.valor_procesado = processed_value
        elif self.current_list_name is not None and isinstance(parent_ctx, NaturalToJsonParser.Items_listaContext):
            # Si estamos dentro de una lista (current_list_name está activo) y el padre es 'items_lista',
            # el valor es un elemento de esa lista.
             self.current_list_items.append(processed_value)
        elif isinstance(parent_ctx, NaturalToJsonParser.Items_listaContext):
            # Caso de respaldo si current_list_name no estuviera activo pero el contexto es items_lista
            # (esto podría indicar un estado inesperado, pero se maneja por seguridad).
            self.current_list_items.append(processed_value)


# ---  Listener para construir el QStandardItemModel para QTreeView ---
class ParseTreeModelBuilder(NaturalToJsonListener):
    """
    Listener de ANTLR que construye un QStandardItemModel para ser utilizado
    con un QTreeView en PyQt5. Este modelo representa la estructura jerárquica
    del árbol de parseo.
    """
    def __init__(self, parser_rule_names):
        """
        Inicializa el constructor del modelo del árbol de parseo.

        Args:
            parser_rule_names (list): Lista de nombres de las reglas del parser,
                                      obtenida de `NaturalToJsonParser.ruleNames`.
        """
        super().__init__()
        self.model = QStandardItemModel()
        self.parser_rule_names = parser_rule_names
        self.item_stack = []  # Pila para mantener el QStandardItem padre actual

    def get_model(self):
        """
        Retorna el QStandardItemModel construido.

        Returns:
            QStandardItemModel: El modelo del árbol de parseo para QTreeView.
        """
        return self.model

    def enterEveryRule(self, ctx:ParserRuleContext):
        """
        Invocado al entrar en cualquier regla del parser.

        Crea un nuevo QStandardItem para esta regla y lo añade al modelo,
        ya sea como un nodo raíz o como hijo del item actual en la cima
        de `item_stack`. Luego, empuja el nuevo item a la pila.
        """
        # Obtener el nombre de la regla
        rule_name_index = ctx.getRuleIndex()
        rule_name = self.parser_rule_names[rule_name_index]
        
        item_text = f"{rule_name}"
        current_item = QStandardItem(item_text)
        current_item.setEditable(False)  # Los nodos del árbol no deben ser editables por el usuario

        if not self.item_stack: # Si la pila está vacía, es un nodo raíz
            self.model.appendRow(current_item)
        else: # Añadir como hijo del item en el tope de la pila
            self.item_stack[-1].appendRow(current_item)
        
        self.item_stack.append(current_item)  # Empujar el item actual a la pila

    def exitEveryRule(self, ctx:ParserRuleContext):
        """
        Invocado al salir de cualquier regla del parser.

        Saca el item correspondiente de la pila `item_stack` para
        retroceder en la jerarquía del árbol.
        """
        if self.item_stack:
            self.item_stack.pop()

    def visitTerminal(self, node:TerminalNode):
        """
        Invocado al visitar un nodo terminal (un token) en el árbol de parseo.

        Crea un QStandardItem para el token y lo añade como hijo del
        item de regla actual en la cima de `item_stack`.
        Se omiten los tokens EOF y los del canal oculto (ej. comentarios, espacios).
        """
        if self.item_stack: # Solo añadir terminales si hay un item padre en la pila
            token = node.getSymbol()
            # No mostrar EOF o tokens de canal oculto en el árbol visual
            if token.type != Token.EOF and token.channel == Token.DEFAULT_CHANNEL:
                token_name = NaturalToJsonLexer.symbolicNames[token.type]
                terminal_text = f"{token_name}: '{node.getText()}'"
                terminal_item = QStandardItem(terminal_text)
                terminal_item.setEditable(False)
                # Opcional: Colorear los terminales de forma diferente para distinguirlos
                # terminal_item.setForeground(QColor("blue")) 
                self.item_stack[-1].appendRow(terminal_item)

# --- Funciones de Análisis (Modificada para devolver el QStandardItemModel) ---
def get_tokens_as_string(input_content_string):
    """
    Realiza un análisis léxico de la cadena de entrada y devuelve una
    representación textual de los tokens reconocidos.

    Args:
        input_content_string (str): La cadena de entrada a tokenizar.

    Returns:
        str: Una cadena multilínea formateada con la lista de tokens.
    """
    output_lines = ["--- Tokens Reconocidos por el Analizador Léxico ---"]
    lexer_instance = NaturalToJsonLexer(InputStream(input_content_string))    
    token_count = 0
    for token in lexer_instance.getAllTokens():
        if token.channel == Token.DEFAULT_CHANNEL:
            token_type_name = NaturalToJsonLexer.symbolicNames[token.type]
            output_lines.append(f"  ● Token #{token_count}: Tipo={token_type_name:<18} Texto='{token.text}' (L:{token.line}, C:{token.column+1})")
            token_count += 1
    if token_count == 0:
        output_lines.append("  No se reconocieron tokens del canal por defecto.")
    output_lines.append("-------------------------------------------------\n")
    return "\n".join(output_lines)


def analyze_and_transform(source_name, input_content):
    """
    Función principal que orquesta el proceso de análisis y transformación.

    Toma el contenido de entrada, lo procesa a través del lexer y parser,
    genera el JSON, la lista de tokens, el árbol de parseo (LISP y modelo Qt),
    un resumen de errores y estadísticas del proceso.

    Args:
        source_name (str): Nombre identificador de la fuente de entrada (ej. nombre de archivo).
        input_content (str): La cadena de texto con los comandos a analizar.

    Returns:
        tuple: Una tupla con 6 elementos:
            - json_output_string (str|None): Cadena JSON generada, o None si hay errores.
            - tokens_string_output (str): Representación textual de los tokens.
            - parsetree_lisp_string_output (str|None): Representación textual del árbol de parseo
                                                       en formato LISP, o None si no se pudo generar.
            - parsetree_qt_model (QStandardItemModel|None): Modelo del árbol de parseo para QTreeView,
                                                            o None si hay errores.
            - error_summary_output (str): Resumen de errores formateado.
            - stats (dict): Diccionario con estadísticas del análisis.
    """
    start_time = time.time()
    tokens_string_output = get_tokens_as_string(input_content)

    # Configuración del Lexer
    input_stream = InputStream(input_content)
    lexer = NaturalToJsonLexer(input_stream)
    error_listener = CustomErrorListener(source_name)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    # Configuración del Parser
    token_stream = CommonTokenStream(lexer)
    try:
        token_stream.fill() # Carga todos los tokens antes de pasarlos al parser
    except Exception as e:
        # Captura errores muy tempranos en la tokenización que podrían no ser manejados por el listener
        error_listener.error_messages.append(f"Error crítico durante la tokenización inicial: {e}")

    parser = NaturalToJsonParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.programa() # Ejecuta el parser y obtiene el árbol de parseo (AST)

    parsetree_qt_model = None # Modelo para QTreeView
    parsetree_lisp_string_output = None # Para LISP style tree
    json_output_string = None
    num_comandos = 0
    symbols_debug_info = {} # Información de depuración de la tabla de símbolos
    ir_output = [] # Representación Intermedia
    
    # 1. Verificar errores léxicos y sintácticos
    if error_listener.get_total_errors() == 0 and tree:
        # 2. Análisis Semántico
        symbol_table = SymbolTable()
        semantic_analyzer = SemanticAnalyzer(error_listener, symbol_table)
        walker = ParseTreeWalker()
        walker.walk(semantic_analyzer, tree)

        # Capturar información de depuración de la tabla de símbolos
        symbols_debug_info = symbol_table.get_debug_info()

        # 3. Generación de IR (Unidad 2) + Optimización (Unidad 4)
        if error_listener.semantic_errors == 0:
            ir_builder = IRBuilderListener()
            walker.walk(ir_builder, tree)
            ir_output = ir_builder.get_instructions()
            # Aplicar optimización de IR (Unidad 4)
            ir_output = optimize_ir(ir_output)

        # 4. Generación de JSON y estructuras del árbol (solo si no hay errores semánticos)
        if error_listener.semantic_errors == 0:
            # Construir el modelo para QTreeView
            model_builder = ParseTreeModelBuilder(list(NaturalToJsonParser.ruleNames))
            walker.walk(model_builder, tree)
            parsetree_qt_model = model_builder.get_model()
            
            # Construir JSON
            json_builder = JsonBuilderListener()
            walker.walk(json_builder, tree) # Reutilizar el ParseTreeWalker
            json_output_string = json_builder.get_final_json_string()
            num_comandos = len(json_builder.result_data)

            # Generar representación textual del árbol (estilo LISP)
            try:
                rule_names_list = list(NaturalToJsonParser.ruleNames)
                parsetree_lisp_s = Trees.toStringTree(tree, recog=parser, rule_names=rule_names_list)
                # Only create a meaningful string if the tree has actual content beyond just EOF
                if tree.getChildCount() > 1 or (tree.getChildCount() == 1 and tree.getChild(0).getSymbol().type != Token.EOF):
                    parsetree_lisp_string_output = (
                        "--- Árbol de Parseo (Estilo LISP) ---\n"
                        f"{parsetree_lisp_s}\n"
                        "---------------------------------------\n"
                    )
            except Exception as e_tree:
                parsetree_lisp_string_output = (
                    f"Advertencia: No se pudo generar la representación textual del árbol: {e_tree}"
                )
    
    # Recopilación de resultados y estadísticas
    error_summary_output = error_listener.get_error_summary_string()
    end_time = time.time()
    analysis_time = end_time - start_time
    # Contar tokens que realmente van al parser (excluyendo EOF y canal oculto)
    parser_tokens_count = sum(1 for t in token_stream.tokens if t.channel == Token.DEFAULT_CHANNEL and t.type != Token.EOF)

    # Diccionario de estadísticas
    stats = {
        "tiempo_analisis_seg": round(analysis_time, 4),
        "comandos_procesados": num_comandos,
        "tokens_al_parser": parser_tokens_count,
        "errores_lexicos": error_listener.lexer_errors,
        "errores_sintacticos": error_listener.parser_errors,
        "errores_semanticos": error_listener.semantic_errors, # NUEVO
        "symbols_debug": symbols_debug_info, # NUEVO: Para tests de tipos
        "ir": ir_output # NUEVO: Unidad 2
    }

    return json_output_string, tokens_string_output, parsetree_lisp_string_output, parsetree_qt_model, error_summary_output, stats
