import Env
from Token import Token

class SemanticAnalyzer:
    def __init__(self, arbol, console=None):
        self.arbol = arbol
        self.console = console or Env.console
        # Tabla de Símbolos: nombre_variable -> {'tipo': str, 'linea': int, 'mem_id': int}
        self.tabla_simbolos = {} 
        self.errores = 0
        self.mem_counter = 0  

    def analizar(self):
        """Punto de entrada principal para iniciar el análisis semántico."""
        if self.console: 
            self.console.print_notification("\nINICIO DE ANALISIS SEMANTICO (Validación de Reglas y Asignación de Memoria)")
            
        self.visitar(self.arbol)
        
        if self.errores == 0:
            if self.console: 
                self.console.print_notification("ANALISIS SEMANTICO COMPLETADO: 0 Errores. AST anotado con éxito.")
            return True
        else:
            if self.console: 
                self.console.print_alert(f"ANALISIS SEMANTICO DETENIDO: {self.errores} error(es) encontrado(s).")
            return False

    def visitar(self, nodo):
        """Recorre recursivamente el Árbol de Sintaxis Abstracta (AST)."""
        if nodo is None:
            return

        t = nodo.token.type
        
        # 1. Bloque principal
        if t == Token.Type.PhpOpen:
            self.visitar(nodo.left)
            
        # 2. Sentencias de control
        elif t in [Token.Type.If, Token.Type.While]:
            self.visitar(nodo.left)   # Condición
            self.visitar(nodo.right)  # Bloque True
            if nodo.center: self.visitar(nodo.center) # Bloque Else/ElseIf
            
        elif t == Token.Type.For:
            self.visitar(nodo.left)   # Inicialización (ej. $i = 0)
            self.visitar(nodo.center) # Condición (ej. $i < 10)
            self.visitar(nodo.step)   # Incremento (ej. $i++)
            self.visitar(nodo.right)  # Cuerpo del bucle
            
        # 3. Operaciones matemáticas, relacionales y lógicas (¡AQUÍ ESTABA EL BUG!)
        elif t in [
            Token.Type.Suma, Token.Type.Resta, Token.Type.Multiplica, Token.Type.Divide, Token.Type.Modulo,
            Token.Type.MenorQue, Token.Type.MayorQue, Token.Type.MenorIgual, Token.Type.MayorIgual, 
            Token.Type.Igualdad, Token.Type.Desigualdad, Token.Type.And, Token.Type.Or
        ]:
            self.verificar_operacion(nodo)
            
        # 4. Asignaciones e Incrementos
        elif t == Token.Type.Asignacion:
            self.verificar_asignacion(nodo)
            
        elif t in [Token.Type.Incremento, Token.Type.Decremento]:
            self.verificar_incremento(nodo)
            
        # 5. Funciones nativas e Impresiones
        elif t == Token.Type.Echo:
            self.visitar(nodo.left)
            
        elif t == Token.Type.Count:
            self.verificar_count(nodo)
            
        # 6. Elementos finales (Hojas del árbol)
        elif t == Token.Type.Variable:
            self.verificar_variable_existe(nodo)
            
        elif t in [Token.Type.Numero, Token.Type.Cadena, Token.Type.Booleano]:
            nodo.eval_type = t 

        # Visitar la siguiente instrucción (Hermano)
        self.visitar(nodo.next)


    # --- REGLAS SEMANTICAS Y GESTIÓN DE MEMORIA ---

    def verificar_asignacion(self, nodo):
        var_node = nodo.left
        nombre_var = var_node.token.value
        linea = getattr(var_node.token, 'line', getattr(nodo, 'line', "N/A"))
        
        # Primero validamos el lado derecho
        self.visitar(nodo.right)
        
        if var_node.left is not None:
            if self.console: self.console.print(f"  > Validando asignación a índice del arreglo '{nombre_var}' (Línea {linea})")
            self.visitar(var_node.left) 
            if nombre_var not in self.tabla_simbolos:
                self.reportar_error(linea, f"El arreglo '{nombre_var}' no ha sido inicializado antes de asignarle un índice.")
            else:
                var_node.mem_id = self.tabla_simbolos[nombre_var]['mem_id']
                var_node.eval_type = self.tabla_simbolos[nombre_var]['tipo']
        else:
            tipo_inferido = "Variable"
            if nodo.right and nodo.right.token.type == Token.Type.Array:
                tipo_inferido = "Arreglo"
                
            if nombre_var not in self.tabla_simbolos:
                mem_asignada = self.mem_counter
                self.mem_counter += 1
                if self.console: self.console.print(f"  > Registrando: '{nombre_var}' (Tipo: {tipo_inferido}, MemID: {mem_asignada}) (Línea {linea})")
                
                self.tabla_simbolos[nombre_var] = {
                    'tipo': tipo_inferido, 
                    'linea': linea,
                    'mem_id': mem_asignada
                }
            
            var_node.mem_id = self.tabla_simbolos[nombre_var]['mem_id']
            var_node.eval_type = self.tabla_simbolos[nombre_var]['tipo']
            
        # Propagar el mem_id y el tipo al nodo padre de asignación (=)
        # Esto evita que el Generador de Código falle si busca el mem_id directamente en el nodo de asignación.
        nodo.mem_id = var_node.mem_id
        nodo.eval_type = var_node.eval_type

    def verificar_variable_existe(self, nodo):
        nombre_var = nodo.token.value
        linea = getattr(nodo.token, 'line', getattr(nodo, 'line', "N/A"))
        
        if self.console: self.console.print(f"  > Comprobando existencia y recuperando MemID de '{nombre_var}' (Línea {linea})")
        
        if nodo.left:
            self.visitar(nodo.left)
            
        if nombre_var not in self.tabla_simbolos:
            self.reportar_error(linea, f"Variable '{nombre_var}' usada sin haber sido inicializada previamente.")
        else:
            nodo.mem_id = self.tabla_simbolos[nombre_var]['mem_id']
            nodo.eval_type = self.tabla_simbolos[nombre_var]['tipo']

    def verificar_operacion(self, nodo):
        if self.console: self.console.print(f"  > Verificando operación '{nodo.token.value}'")
        self.visitar(nodo.left)
        self.visitar(nodo.right)
        nodo.eval_type = Token.Type.Numero

    def verificar_incremento(self, nodo):
        var_node = nodo.left
        nombre_var = var_node.token.value
        linea = getattr(var_node.token, 'line', getattr(nodo, 'line', "N/A"))
        
        if self.console: self.console.print(f"  > Validando incremento/decremento en '{nombre_var}' (Línea {linea})")
        
        if nombre_var not in self.tabla_simbolos:
            self.reportar_error(linea, f"Intento de alterar variable '{nombre_var}' no inicializada.")
        else:
            var_node.mem_id = self.tabla_simbolos[nombre_var]['mem_id']
            var_node.eval_type = self.tabla_simbolos[nombre_var]['tipo']
            nodo.mem_id = var_node.mem_id

    def verificar_count(self, nodo):
        if nodo.left:
            nombre_var = nodo.left.token.value
            linea = getattr(nodo.left.token, 'line', getattr(nodo, 'line', "N/A"))
            
            if self.console: self.console.print(f"  > Evaluando argumento de función count(): '{nombre_var}' (Línea {linea})")
            
            if nombre_var not in self.tabla_simbolos:
                self.reportar_error(linea, f"La función count() intenta medir '{nombre_var}', pero no existe.")
            elif self.tabla_simbolos[nombre_var]['tipo'] != "Arreglo":
                self.reportar_error(linea, f"La función count() espera un Arreglo, pero '{nombre_var}' es de tipo estándar.")
            else:
                nodo.left.mem_id = self.tabla_simbolos[nombre_var]['mem_id']
                nodo.left.eval_type = self.tabla_simbolos[nombre_var]['tipo']
                nodo.eval_type = Token.Type.Numero

    def reportar_error(self, linea, mensaje):
        self.errores += 1
        mensaje_completo = f"Línea {linea} - {mensaje}"
        if self.console:
            self.console.print_alert(f"  [!] ERROR SEMÁNTICO: {mensaje_completo}")
        else:
            print(f"ERROR SEMÁNTICO: {mensaje_completo}")