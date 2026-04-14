console = None 
tabla_simbolos = {}  # Tabla de símbolos global para compartir metadatos y mem_id

def set_console(instance):
    global console
    console = instance