def format_value(valor, tipo):
    """
    Formatea un valor para ser usado como literal en código Python.
    
    Args:
        valor: El valor a formatear.
        tipo: El tipo del valor ("STRING", "NUMBER", "BOOLEAN").
        
    Returns:
        str: Representación en string del valor válida para Python.
    """
    if tipo == "STRING":
        # Usamos repr() para manejar comillas internas y caracteres especiales de forma segura
        return repr(valor)
    elif tipo == "BOOLEAN":
        # Python usa True/False (con mayúscula inicial)
        return "True" if valor else "False"
    else: # NUMBER
        # Convertimos a string directamente
        return str(valor)

def generate_python_from_ir(ir_instructions):
    """
    Toma una lista de instrucciones IR y genera código Python.
    
    Args:
        ir_instructions (list): Lista de dicts con 'opcode' y 'args'.
        
    Returns:
        str: Código Python completo como string.
    """
    python_code = []
    python_code.append("# --- Codigo Generado ---")
    
    for instr in ir_instructions:
        opcode = instr["opcode"]
        args = instr["args"]
        
        if opcode == "IR_CREATE_OBJECT":
            nombre = args[0]
            python_code.append(f"{nombre} = {{}}")
            
        elif opcode == "IR_SET_PROPERTY":
            nombre, clave, tipo, valor = args
            valor_fmt = format_value(valor, tipo)
            python_code.append(f"{nombre}[\"{clave}\"] = {valor_fmt}")
            
        elif opcode == "IR_CREATE_LIST":
            nombre = args[0]
            python_code.append(f"{nombre} = []")
            
        elif opcode == "IR_APPEND_LIST":
            nombre, tipo, valor = args
            valor_fmt = format_value(valor, tipo)
            python_code.append(f"{nombre}.append({valor_fmt})")
            
    return "\n".join(python_code)
