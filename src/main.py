# main.py
# ESTE ARCHIVO ES UNA VERSIÓN ANTERIOR/DE PRUEBAS Y DEPURACIÓN.
# NO ES LA INTERFAZ PRINCIPAL DE LA APLICACIÓN. Usar main_gui.py para la GUI.
import sys
import argparse
import json
import os
from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.tree.Trees import Trees
from antlr4.error.ErrorListener import ErrorListener

if './generated' not in sys.path:
    sys.path.append('./generated')

from NaturalToJsonLexer import NaturalToJsonLexer
from NaturalToJsonParser import NaturalToJsonParser
from NaturalToJsonListener import NaturalToJsonListener

# --- Listener Personalizado para Errores  ---
class CustomErrorListener(ErrorListener):
    def __init__(self, source_name="<input>"):
        super().__init__()
        self.source_name = source_name
        self._lexer_errors = 0
        self._parser_errors = 0
        self.error_messages = []

    @property
    def lexer_errors(self): return self._lexer_errors
    @property
    def parser_errors(self): return self._parser_errors

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_type = "Desconocido"
        is_lexer_error = isinstance(recognizer, NaturalToJsonLexer)

        if is_lexer_error:
            self._lexer_errors += 1
            error_type = "Léxico"
            translated_msg = msg
            if "token recognition error at: '" in msg:
                try:
                    char_problem = msg.split("token recognition error at: '")[1][:-1]
                    translated_msg = f"Carácter no reconocido: '{char_problem}'"
                except IndexError: pass
        else:
            self._parser_errors += 1
            error_type = "Sintáctico"
            translated_msg = msg
            if "mismatched input" in msg and "expecting" in msg:
                parts = msg.split("expecting")
                found = parts[0].replace("mismatched input", "Entrada inesperada").strip()
                expected = parts[1].strip()
                translated_msg = f"{found}, se esperaba {expected}"
            elif "extraneous input" in msg and "expecting" in msg:
                parts = msg.split("expecting")
                found = parts[0].replace("extraneous input", "Entrada sobrante").strip()
                expected = parts[1].strip()
                translated_msg = f"{found}, se esperaba {expected}"
            elif "missing" in msg and "at" in msg:
                parts = msg.split("at")
                missing_what = parts[0].replace("missing", "Falta").strip()
                at_where = parts[1].strip()
                translated_msg = f"{missing_what} en {at_where}"
        
        symbol_text = ""
        if offendingSymbol and offendingSymbol.text and offendingSymbol.text != '<EOF>':
             symbol_text = offendingSymbol.text
        
        formatted_msg = f"Error {error_type} en {self.source_name} (Línea {line}:Columna {column+1}): {translated_msg}"
        if symbol_text and not is_lexer_error :
             formatted_msg += f" (Cerca de: '{symbol_text}')"
        self.error_messages.append(formatted_msg)

    def get_total_errors(self): return self._lexer_errors + self._parser_errors

    def report_all_errors(self, output_stream=sys.stderr):
        if self.error_messages:
            print("\n╔═════════════════════════════════════╗", file=output_stream)
            print("║     Resumen de Errores Detectados      ║", file=output_stream)
            print("╚═════════════════════════════════════╝", file=output_stream)
            for emsg in self.error_messages:
                print(f"  ⚠️  {emsg}", file=output_stream) # Añadido emoji para destacar
            print("---------------------------------------\n", file=output_stream)
            return True
        return False

# --- Listener para Construir JSON ---
class JsonBuilderListener(NaturalToJsonListener):
    def __init__(self):
        self.result_data = {}
        self.current_object_name = None
        self.current_object_props = {}
        self.current_list_name = None
        self.current_list_items = []
        self.current_key = None

    def get_final_json(self):
        return json.dumps(self.result_data, indent=2, ensure_ascii=False)

    def enterCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        self.current_object_name = ctx.nombre_obj.text
        self.current_object_props = {}

    def exitCrear_objeto_cmd(self, ctx:NaturalToJsonParser.Crear_objeto_cmdContext):
        if self.current_object_name:
            self.result_data[self.current_object_name] = self.current_object_props
        self.current_object_name = None

    def enterPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        self.current_key = ctx.clave.text

    def exitPropiedad(self, ctx:NaturalToJsonParser.PropiedadContext):
        if self.current_key and hasattr(ctx, 'valor_procesado'):
             self.current_object_props[self.current_key] = ctx.valor_procesado
        self.current_key = None

    def enterCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        self.current_list_name = ctx.nombre_lista.text
        self.current_list_items = []

    def exitCrear_lista_cmd(self, ctx:NaturalToJsonParser.Crear_lista_cmdContext):
        if self.current_list_name:
            self.result_data[self.current_list_name] = self.current_list_items
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
        
        parent_ctx = ctx.parentCtx
        if isinstance(parent_ctx, NaturalToJsonParser.PropiedadContext):
            parent_ctx.valor_procesado = processed_value
        elif self.current_list_name is not None and isinstance(parent_ctx, NaturalToJsonParser.Items_listaContext):
             self.current_list_items.append(processed_value)
        elif isinstance(parent_ctx, NaturalToJsonParser.Items_listaContext):
            self.current_list_items.append(processed_value)

# --- Funciones Auxiliares ---
def print_section_header(title):
    """Imprime un encabezado de sección formateado."""
    width = 60
    print("\n" + "═" * width)
    print(f"║ {title.center(width-4)} ║")
    print("═" * width)

def display_tokens(lexer_class, input_string_for_lexing):
    print_section_header("Tokens Reconocidos por el Analizador Léxico")
    lexer_instance = lexer_class(InputStream(input_string_for_lexing))
    token_count = 0
    all_tokens = lexer_instance.getAllTokens()
    
    for token in all_tokens:
        if token.channel == Token.DEFAULT_CHANNEL:
            token_type_name = lexer_class.symbolicNames[token.type]
            print(f"  ● Token #{token_count}: Tipo={token_type_name:<18} Texto='{token.text}' (L:{token.line}, C:{token.column+1})")
            token_count += 1
    if token_count == 0: print("  No se reconocieron tokens del canal por defecto.")
    print("-" * 60 + "\n")

def analyze_input(source_name, input_content):
    print_section_header(f"Iniciando Análisis para: '{source_name}'")
    
    display_tokens(NaturalToJsonLexer, input_content)

    lexer_for_parser = NaturalToJsonLexer(InputStream(input_content))
    error_listener_lex = CustomErrorListener(source_name)
    lexer_for_parser.removeErrorListeners()
    lexer_for_parser.addErrorListener(error_listener_lex)

    token_stream = CommonTokenStream(lexer_for_parser)
    parser = NaturalToJsonParser(token_stream)
    error_listener_parser = CustomErrorListener(source_name)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener_parser)

    print_section_header("Parseando la Entrada (Construyendo Árbol)")
    tree = parser.programa()
    
    had_lex_errors = error_listener_lex.report_all_errors()
    had_parser_errors = error_listener_parser.report_all_errors()
    
    total_errors_detected = error_listener_lex.get_total_errors() + error_listener_parser.get_total_errors()

    if total_errors_detected > 0:
        print(f"Análisis completado con {total_errors_detected} error(es) total(es) detectado(s).", file=sys.stderr)
        return None, True
    else:
        print("Análisis léxico y sintáctico completado exitosamente.\n")
        print_section_header("Árbol de Parseo (Estilo LISP)")
        print(Trees.toStringTree(tree, recog=parser, ruleNames=list(NaturalToJsonParser.ruleNames)))
        print("-" * 60 + "\n")
        
        print_section_header("Procesando Árbol con Listener para generar JSON")
        builder_listener = JsonBuilderListener()
        walker = ParseTreeWalker()
        walker.walk(builder_listener, tree)
        
        final_json_output = builder_listener.get_final_json()
        print_section_header("JSON Generado")
        print(final_json_output)
        print("-" * 60)
        return final_json_output, False

# --- LÓGICA PARA SELECCIÓN INTERACTIVA ---
def list_and_select_test_file(test_files_dir="ejemplos_entrada", file_extension=".txt", processed_files=None):
    if processed_files is None:
        processed_files = set()

    if not os.path.exists(test_files_dir) or not os.path.isdir(test_files_dir):
        print(f"ADVERTENCIA: Directorio de pruebas '{test_files_dir}' no encontrado.", file=sys.stderr)
        return None, processed_files

    available_files = []
    try:
        all_entries = os.listdir(test_files_dir)
        for entry in all_entries:
            if entry.endswith(file_extension) and os.path.isfile(os.path.join(test_files_dir, entry)):
                available_files.append(entry)
    except OSError as e:
        print(f"Error listando archivos en '{test_files_dir}': {e}", file=sys.stderr)
        return None, processed_files


    if not available_files:
        print(f"No se encontraron archivos '{file_extension}' en '{test_files_dir}'.", file=sys.stderr)
        return None, processed_files

    print("\nArchivos de prueba disponibles en '{}':".format(test_files_dir))
    displayable_files = []
    for i, filename in enumerate(available_files):
        marker = "[✓]" if filename in processed_files else "[ ]"
        print(f"  {marker} {i+1}. {filename}")
        displayable_files.append(filename) # Guardamos el orden original para la selección
    
    if len(processed_files) == len(available_files) and available_files:
         print("Todos los archivos disponibles han sido procesados en esta sesión.")

    while True:
        try:
            choice = input(f"Selecciona un archivo por número (1-{len(displayable_files)}), 'todos', o 's' para salir: ").strip().lower()
            if choice == 's':
                return "salir", processed_files
            if choice == 'todos':
                return "todos", processed_files # Devolvemos una señal para procesar todos
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(displayable_files):
                selected_filename = displayable_files[choice_num - 1]
                processed_files.add(selected_filename) # Marcar como procesado
                return os.path.join(test_files_dir, selected_filename), processed_files
            else:
                print("Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número, 'todos' o 's'.")
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la selección: {e}")
            return None, processed_files


# --- Función Principal ---
def main():
    print("!"*70)
    print("!" + " ".center(68) + "!")
    print("!" + "ADVERTENCIA: MODO DE PRUEBA/DEPURACIÓN (main.py)".center(68) + "!")
    print("!" + "Esta es una versión de consola para desarrollo y pruebas.".center(68) + "!")
    print("!" + "Para la aplicación con interfaz gráfica, ejecute 'main_gui.py'.".center(68) + "!")
    print("!" + " ".center(68) + "!")
    print("!"*70)
    default_examples_dir = "ejemplos_entrada"
    if not os.path.exists(default_examples_dir):
        try:
            os.makedirs(default_examples_dir)
            print(f"INFO: Directorio '{default_examples_dir}' creado. Coloca tus archivos .txt de prueba aquí.")
        except OSError as e:
            print(f"ADVERTENCIA: No se pudo crear el directorio '{default_examples_dir}': {e}", file=sys.stderr)

    arg_parser = argparse.ArgumentParser(
        description='Analizador Léxico y Sintáctico para lenguaje "Natural a JSON".\n'
                    'Si no se especifica un archivo, se ofrecerá un menú interactivo.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    arg_parser.add_argument(
        'input_file', nargs='?', type=str, default=None,
        help='(Opcional) Archivo de entrada a procesar directamente.'
    )
    args = arg_parser.parse_args()

    processed_in_session = set() # Para rastrear archivos procesados en la sesión interactiva

    if args.input_file: # Si se pasa un archivo como argumento, procesarlo directamente
        source_display_name = args.input_file
        input_content_to_process = ""
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_content_to_process = f.read()
            print(f"Archivo '{source_display_name}' cargado para análisis.")
        except FileNotFoundError:
            print(f"Error Crítico: Archivo '{args.input_file}' no encontrado.", file=sys.stderr); sys.exit(1)
        except Exception as e:
            print(f"Error Crítico al leer archivo '{args.input_file}': {e}", file=sys.stderr); sys.exit(1)
        
        if input_content_to_process:
            analyze_input(source_display_name, input_content_to_process)
        else:
            print(f"El archivo '{source_display_name}' está vacío o no se pudo leer.", file=sys.stderr)

    else: # Modo interactivo
        while True:
            print("\n" + "="*70)
            print("MODO INTERACTIVO - SELECCIÓN DE ARCHIVO DE PRUEBA".center(70))
            print("="*70)
            
            selection_result, processed_in_session = list_and_select_test_file(default_examples_dir, processed_files=processed_in_session)

            if selection_result == "salir" or selection_result is None and not processed_in_session : # Si el usuario elige salir o no hay archivos
                print("Saliendo del modo interactivo.")
                break
            elif selection_result is None and processed_in_session: # No hay más archivos o error listando
                print("No hay más archivos para seleccionar o error al listar. Saliendo.")
                break
            elif selection_result == "todos":
                print("\nProcesando todos los archivos no procesados en '{}'...".format(default_examples_dir))
                all_files_in_dir = [os.path.join(default_examples_dir, f) 
                                    for f in os.listdir(default_examples_dir) 
                                    if f.endswith(".txt") and os.path.isfile(os.path.join(default_examples_dir, f))]
                
                any_processed_this_round = False
                for file_path_to_process in all_files_in_dir:
                    filename_only = os.path.basename(file_path_to_process)
                    if filename_only not in processed_in_session:
                        print(f"\n--- Procesando archivo: {filename_only} ---")
                        try:
                            with open(file_path_to_process, 'r', encoding='utf-8') as f:
                                content = f.read()
                            analyze_input(filename_only, content)
                            processed_in_session.add(filename_only)
                            any_processed_this_round = True
                        except Exception as e:
                            print(f"Error procesando '{filename_only}': {e}", file=sys.stderr)
                if not any_processed_this_round and all_files_in_dir:
                    print("Todos los archivos ya habían sido procesados en esta sesión.")
                elif not all_files_in_dir:
                     print(f"No se encontraron archivos .txt en '{default_examples_dir}'.")


            else: # Se seleccionó un archivo específico
                selected_file_path = selection_result
                source_display_name = selected_file_path
                input_content_to_process = ""
                try:
                    with open(selected_file_path, 'r', encoding='utf-8') as f:
                        input_content_to_process = f.read()
                    print(f"Archivo '{source_display_name}' cargado para análisis.")
                except FileNotFoundError:
                    print(f"Error: Archivo '{selected_file_path}' no encontrado.", file=sys.stderr)
                    continue # Volver al menú
                except Exception as e:
                    print(f"Error al leer archivo '{selected_file_path}': {e}", file=sys.stderr)
                    continue # Volver al menú
                
                if input_content_to_process:
                    analyze_input(source_display_name, input_content_to_process)
            
            # Preguntar si desea continuar después de procesar un archivo o todos
            if selection_result != "salir":
                cont = input("\n¿Desea procesar otro archivo? (s/n): ").strip().lower()
                if cont != 's':
                    print("Saliendo del modo interactivo.")
    parser.addErrorListener(error_listener_parser)

    print_section_header("Parseando la Entrada (Construyendo Árbol)")
    tree = parser.programa()
    
    had_lex_errors = error_listener_lex.report_all_errors()
    had_parser_errors = error_listener_parser.report_all_errors()
    
    total_errors_detected = error_listener_lex.get_total_errors() + error_listener_parser.get_total_errors()

    if total_errors_detected > 0:
        print(f"Análisis completado con {total_errors_detected} error(es) total(es) detectado(s).", file=sys.stderr)
        return None, True
    else:
        print("Análisis léxico y sintáctico completado exitosamente.\n")
        print_section_header("Árbol de Parseo (Estilo LISP)")
        print(Trees.toStringTree(tree, recog=parser, ruleNames=list(NaturalToJsonParser.ruleNames)))
        print("-" * 60 + "\n")
        
        print_section_header("Procesando Árbol con Listener para generar JSON")
        builder_listener = JsonBuilderListener()
        walker = ParseTreeWalker()
        walker.walk(builder_listener, tree)
        
        final_json_output = builder_listener.get_final_json()
        print_section_header("JSON Generado")
        print(final_json_output)
        print("-" * 60)
        return final_json_output, False

# --- LÓGICA PARA SELECCIÓN INTERACTIVA ---
def list_and_select_test_file(test_files_dir="ejemplos_entrada", file_extension=".txt", processed_files=None):
    if processed_files is None:
        processed_files = set()

    if not os.path.exists(test_files_dir) or not os.path.isdir(test_files_dir):
        print(f"ADVERTENCIA: Directorio de pruebas '{test_files_dir}' no encontrado.", file=sys.stderr)
        return None, processed_files

    available_files = []
    try:
        all_entries = os.listdir(test_files_dir)
        for entry in all_entries:
            if entry.endswith(file_extension) and os.path.isfile(os.path.join(test_files_dir, entry)):
                available_files.append(entry)
    except OSError as e:
        print(f"Error listando archivos en '{test_files_dir}': {e}", file=sys.stderr)
        return None, processed_files


    if not available_files:
        print(f"No se encontraron archivos '{file_extension}' en '{test_files_dir}'.", file=sys.stderr)
        return None, processed_files

    print("\nArchivos de prueba disponibles en '{}':".format(test_files_dir))
    displayable_files = []
    for i, filename in enumerate(available_files):
        marker = "[✓]" if filename in processed_files else "[ ]"
        print(f"  {marker} {i+1}. {filename}")
        displayable_files.append(filename) # Guardamos el orden original para la selección
    
    if len(processed_files) == len(available_files) and available_files:
         print("Todos los archivos disponibles han sido procesados en esta sesión.")

    while True:
        try:
            choice = input(f"Selecciona un archivo por número (1-{len(displayable_files)}), 'todos', o 's' para salir: ").strip().lower()
            if choice == 's':
                return "salir", processed_files
            if choice == 'todos':
                return "todos", processed_files # Devolvemos una señal para procesar todos
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(displayable_files):
                selected_filename = displayable_files[choice_num - 1]
                processed_files.add(selected_filename) # Marcar como procesado
                return os.path.join(test_files_dir, selected_filename), processed_files
            else:
                print("Selección inválida. Intenta de nuevo.")
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número, 'todos' o 's'.")
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la selección: {e}")
            return None, processed_files


# --- Función Principal ---
def main():
    print("!"*70)
    print("!" + " ".center(68) + "!")
    print("!" + "ADVERTENCIA: MODO DE PRUEBA/DEPURACIÓN (main.py)".center(68) + "!")
    print("!" + "Esta es una versión de consola para desarrollo y pruebas.".center(68) + "!")
    print("!" + "Para la aplicación con interfaz gráfica, ejecute 'main_gui.py'.".center(68) + "!")
    print("!" + " ".center(68) + "!")
    print("!"*70)
    default_examples_dir = "ejemplos_entrada"
    if not os.path.exists(default_examples_dir):
        try:
            os.makedirs(default_examples_dir)
            print(f"INFO: Directorio '{default_examples_dir}' creado. Coloca tus archivos .txt de prueba aquí.")
        except OSError as e:
            print(f"ADVERTENCIA: No se pudo crear el directorio '{default_examples_dir}': {e}", file=sys.stderr)

    arg_parser = argparse.ArgumentParser(
        description='Analizador Léxico y Sintáctico para lenguaje "Natural a JSON".\n'
                    'Si no se especifica un archivo, se ofrecerá un menú interactivo.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    arg_parser.add_argument(
        'input_file', nargs='?', type=str, default=None,
        help='(Opcional) Archivo de entrada a procesar directamente.'
    )
    args = arg_parser.parse_args()

    processed_in_session = set() # Para rastrear archivos procesados en la sesión interactiva

    if args.input_file: # Si se pasa un archivo como argumento, procesarlo directamente
        source_display_name = args.input_file
        input_content_to_process = ""
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_content_to_process = f.read()
            print(f"Archivo '{source_display_name}' cargado para análisis.")
        except FileNotFoundError:
            print(f"Error Crítico: Archivo '{args.input_file}' no encontrado.", file=sys.stderr); sys.exit(1)
        except Exception as e:
            print(f"Error Crítico al leer archivo '{args.input_file}': {e}", file=sys.stderr); sys.exit(1)
        
        if input_content_to_process:
            analyze_input(source_display_name, input_content_to_process)
        else:
            print(f"El archivo '{source_display_name}' está vacío o no se pudo leer.", file=sys.stderr)

    else: # Modo interactivo
        while True:
            print("\n" + "="*70)
            print("MODO INTERACTIVO - SELECCIÓN DE ARCHIVO DE PRUEBA".center(70))
            print("="*70)
            
            selection_result, processed_in_session = list_and_select_test_file(default_examples_dir, processed_files=processed_in_session)

            if selection_result == "salir" or selection_result is None and not processed_in_session : # Si el usuario elige salir o no hay archivos
                print("Saliendo del modo interactivo.")
                break
            elif selection_result is None and processed_in_session: # No hay más archivos o error listando
                print("No hay más archivos para seleccionar o error al listar. Saliendo.")
                break
            elif selection_result == "todos":
                print("\nProcesando todos los archivos no procesados en '{}'...".format(default_examples_dir))
                all_files_in_dir = [os.path.join(default_examples_dir, f) 
                                    for f in os.listdir(default_examples_dir) 
                                    if f.endswith(".txt") and os.path.isfile(os.path.join(default_examples_dir, f))]
                
                any_processed_this_round = False
                for file_path_to_process in all_files_in_dir:
                    filename_only = os.path.basename(file_path_to_process)
                    if filename_only not in processed_in_session:
                        print(f"\n--- Procesando archivo: {filename_only} ---")
                        try:
                            with open(file_path_to_process, 'r', encoding='utf-8') as f:
                                content = f.read()
                            analyze_input(filename_only, content)
                            processed_in_session.add(filename_only)
                            any_processed_this_round = True
                        except Exception as e:
                            print(f"Error procesando '{filename_only}': {e}", file=sys.stderr)
                if not any_processed_this_round and all_files_in_dir:
                    print("Todos los archivos ya habían sido procesados en esta sesión.")
                elif not all_files_in_dir:
                     print(f"No se encontraron archivos .txt en '{default_examples_dir}'.")


            else: # Se seleccionó un archivo específico
                selected_file_path = selection_result
                source_display_name = selected_file_path
                input_content_to_process = ""
                try:
                    with open(selected_file_path, 'r', encoding='utf-8') as f:
                        input_content_to_process = f.read()
                    print(f"Archivo '{source_display_name}' cargado para análisis.")
                except FileNotFoundError:
                    print(f"Error: Archivo '{selected_file_path}' no encontrado.", file=sys.stderr)
                    continue # Volver al menú
                except Exception as e:
                    print(f"Error al leer archivo '{selected_file_path}': {e}", file=sys.stderr)
                    continue # Volver al menú
                
                if input_content_to_process:
                    analyze_input(source_display_name, input_content_to_process)
            
            # Preguntar si desea continuar después de procesar un archivo o todos
            if selection_result != "salir":
                cont = input("\n¿Desea procesar otro archivo? (s/n): ").strip().lower()
                if cont != 's':
                    print("Saliendo del modo interactivo.")
                    break
            else: # Si la selección fue 'salir' directamente
                break


if __name__ == '__main__':
    main()