
"""
Módulo de optimización para la Representación Intermedia (IR).

Este módulo aplica transformaciones sobre la lista de instrucciones IR
para mejorar su eficiencia y estructura sin alterar la semántica del programa.
"""

def optimize_ir(ir_instructions):
    """
    Recibe una lista de instrucciones IR y devuelve una NUEVA lista optimizada.
    
    Aplica las siguientes optimizaciones:
    1. Eliminación de asignaciones redundantes (mismo objeto, misma clave).
    2. Agrupamiento de instrucciones por objeto/lista (localidad de referencia).
    
    Args:
        ir_instructions (list): Lista de diccionarios con 'opcode' y 'args'.
        
    Returns:
        list: Nueva lista de instrucciones optimizada.
    """
    if not ir_instructions:
        return []
        
    # Trabajamos sobre una copia para no mutar la original
    optimized = [instr.copy() for instr in ir_instructions]
    
    # Fase 1: Eliminación de redundancias
    optimized = _remove_redundant_sets(optimized)
    
    # Fase 2: Agrupamiento de instrucciones
    optimized = _group_instructions(optimized)
    
    return optimized

def _remove_redundant_sets(instructions):
    """
    Elimina instrucciones IR_SET_PROPERTY que son sobrescritas posteriormente
    por otra asignación a la misma clave del mismo objeto, sin lecturas intermedias.
    """
    # Identificamos las últimas escrituras para cada par (objeto, clave)
    # Como no hay lecturas intermedias ni dependencias complejas en este lenguaje,
    # podemos simplemente quedarnos con la última aparición.
    
    # Mapa para rastrear el índice de la última escritura: (obj_name, key) -> index
    last_writes = {}
    
    # Recorremos para encontrar la última escritura de cada propiedad
    for i, instr in enumerate(instructions):
        if instr["opcode"] == "IR_SET_PROPERTY":
            obj_name = instr["args"][0]
            key = instr["args"][1]
            last_writes[(obj_name, key)] = i
            
    # Construimos la nueva lista filtrando las escrituras que no son la última
    new_instructions = []
    for i, instr in enumerate(instructions):
        if instr["opcode"] == "IR_SET_PROPERTY":
            obj_name = instr["args"][0]
            key = instr["args"][1]
            # Si este índice es el de la última escritura registrada, lo conservamos
            if last_writes.get((obj_name, key)) == i:
                new_instructions.append(instr)
            # Si no, es redundante y se descarta (no se añade)
        else:
            # Otras instrucciones se conservan siempre
            new_instructions.append(instr)
            
    return new_instructions

def _group_instructions(instructions):
    """
    Reordena las instrucciones para agrupar las operaciones relacionadas con
    un mismo objeto o lista inmediatamente después de su creación.
    """
    # Separamos las instrucciones de creación del resto
    creations = []
    operations = []
    others = [] # Por si hubiera otros opcodes en el futuro
    
    for instr in instructions:
        opcode = instr["opcode"]
        if opcode in ("IR_CREATE_OBJECT", "IR_CREATE_LIST"):
            creations.append(instr)
        elif opcode in ("IR_SET_PROPERTY", "IR_APPEND_LIST"):
            operations.append(instr)
        else:
            others.append(instr)
            
    # Si hay instrucciones desconocidas, devolvemos la lista original para seguridad
    if others:
        return instructions
        
    # Construimos la lista agrupada
    grouped_instructions = []
    
    # Diccionario para acceso rápido a operaciones por nombre de entidad
    # Usamos una lista para mantener el orden relativo original de las operaciones
    ops_by_entity = {}
    for op in operations:
        entity_name = op["args"][0]
        if entity_name not in ops_by_entity:
            ops_by_entity[entity_name] = []
        ops_by_entity[entity_name].append(op)
        
    # Reconstruimos: Para cada creación, añadimos sus operaciones inmediatamente después
    processed_entities = set()
    
    for create_instr in creations:
        entity_name = create_instr["args"][0]
        grouped_instructions.append(create_instr)
        
        if entity_name in ops_by_entity:
            grouped_instructions.extend(ops_by_entity[entity_name])
            processed_entities.add(entity_name)
            
    # Manejo de operaciones huérfanas (si las hubiera, por robustez)
    # Esto podría pasar si hay operaciones sobre entidades no creadas explícitamente en este bloque
    # (aunque semánticamente no debería ocurrir en un programa válido)
    for op in operations:
        entity_name = op["args"][0]
        if entity_name not in processed_entities:
            grouped_instructions.append(op)
            
    return grouped_instructions
