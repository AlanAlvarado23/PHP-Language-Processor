import Env
from Token import Token
from Middle_Code import GeneraCodigo

class Code_Generator:
    def __init__(self, arbol, archivo_salida="output.asm", console=None):
        self.arbol = arbol
        self.console = console or Env.console
        # Instanciamos la herramienta de escritura (Middle_Code)
        self.generador_instrucciones = GeneraCodigo(archivo_salida, self.console)

    def generar_codigo(self):
        """Inicia el proceso de traducción del AST a código de máquina virtual."""
        if self.console:
            self.console.print_notification("\n[SNAKE_CASE] INICIO DE GENERACIÓN DE CÓDIGO INTERMEDIO")
            
        self.visitar_nodo(self.arbol)
        
        # Finalizar programa
        self.generador_instrucciones.end() 
        
        if self.console:
            self.console.print_notification(f"ARCHIVO GENERADO: {self.generador_instrucciones.archivo_salida}")

    def visitar_nodo(self, nodo):
        """Recorrido recursivo del árbol para generar instrucciones de pila."""
        if nodo is None:
            return

        t = nodo.token.type
        linea = getattr(nodo.token, 'line', getattr(nodo, 'line', None))

        # --- 1. BLOQUE DE ENTRADA PHP ---
        if t == Token.Type.PhpOpen:
            self.visitar_nodo(nodo.left)

        # --- 2. ASIGNACIONES ($x = 10) ---
        elif t == Token.Type.Asignacion:
            nodo_var = nodo.left
            # Dirección de memoria de la variable
            self.generador_instrucciones.pusha(nodo_var.mem_id, linea)
            
            # Si es un arreglo ($a[$i]), calculamos la posición real
            if nodo_var.left:
                self.visitar_nodo(nodo_var.left)
                self.generador_instrucciones.add(linea)

            # Valor a asignar
            self.visitar_nodo(nodo.right)
            self.generador_instrucciones.store(linea)

        # --- 3. VALORES LITERALES ---
        elif t in [Token.Type.Numero, Token.Type.Cadena, Token.Type.Booleano]:
            self.generador_instrucciones.pushc(nodo.token.value, linea)
            
        # --- 4. USO DE VARIABLES ---
        elif t == Token.Type.Variable:
            self.generador_instrucciones.pusha(nodo.mem_id, linea)
            if nodo.left:
                self.visitar_nodo(nodo.left)
                self.generador_instrucciones.add(linea)
            self.generador_instrucciones.load(linea)

        # --- 5. ARITMÉTICA ---
        elif t in [Token.Type.Suma, Token.Type.Resta, Token.Type.Multiplica, Token.Type.Divide, Token.Type.Modulo]:
            self.visitar_nodo(nodo.left)
            self.visitar_nodo(nodo.right)
            
            if t == Token.Type.Suma: self.generador_instrucciones.add(linea)
            elif t == Token.Type.Resta: self.generador_instrucciones._escribir("SUB", linea)
            elif t == Token.Type.Multiplica: self.generador_instrucciones.mul(linea)
            elif t == Token.Type.Divide: self.generador_instrucciones.div(linea)
            elif t == Token.Type.Modulo: self.generador_instrucciones.mod(linea)

        # --- 6. COMPARACIONES ---
        elif t in [Token.Type.Igualdad, Token.Type.Desigualdad, Token.Type.MenorQue, 
                   Token.Type.MayorQue, Token.Type.MenorIgual, Token.Type.MayorIgual]:
            self.visitar_nodo(nodo.left)
            self.visitar_nodo(nodo.right)
            self.generador_instrucciones.op_relacional(nodo.token.value, linea)

        # --- 7. CONTROL DE FLUJO: IF ---
        elif t == Token.Type.If:
            self.visitar_nodo(nodo.left) # Condición
            
            etiq_falso = self.generador_instrucciones.nueva_etiqueta()
            etiq_fin = self.generador_instrucciones.nueva_etiqueta()
            
            self.generador_instrucciones.goto_if_false(etiq_falso, linea)
            self.visitar_nodo(nodo.right) # Bloque verdadero
            self.generador_instrucciones.goto(etiq_fin, linea)
            
            self.generador_instrucciones.label(etiq_falso, linea)
            if nodo.center: self.visitar_nodo(nodo.center) # Else
            self.generador_instrucciones.label(etiq_fin, linea)

        # --- 8. CONTROL DE FLUJO: WHILE ---
        elif t == Token.Type.While:
            etiq_inicio = self.generador_instrucciones.nueva_etiqueta()
            etiq_fin = self.generador_instrucciones.nueva_etiqueta()
            
            self.generador_instrucciones.label(etiq_inicio, linea)
            self.visitar_nodo(nodo.left) # Condición
            self.generador_instrucciones.goto_if_false(etiq_fin, linea)
            
            self.visitar_nodo(nodo.right) # Cuerpo
            self.generador_instrucciones.goto(etiq_inicio, linea)
            self.generador_instrucciones.label(etiq_fin, linea)

        # --- 9. OPERACIONES UNARIAS ($i++) ---
        elif t in [Token.Type.Incremento, Token.Type.Decremento]:
            nodo_var = nodo.left
            self.generador_instrucciones.pusha(nodo_var.mem_id, linea)
            if nodo_var.left:
                self.visitar_nodo(nodo_var.left)
                self.generador_instrucciones.add(linea)
                
            self.generador_instrucciones._escribir("CLON", linea) 
            self.generador_instrucciones.load(linea)
            self.generador_instrucciones.pushc("1", linea)
            
            if t == Token.Type.Incremento:
                self.generador_instrucciones.add(linea)
            else:
                self.generador_instrucciones._escribir("SUB", linea)
            self.generador_instrucciones.store(linea)

        # --- 10. SALIDA (ECHO) ---
        elif t == Token.Type.Echo:
            self.visitar_nodo(nodo.left)
            self.generador_instrucciones.output(linea)

        # Continuar con el siguiente nodo hermano
        self.visitar_nodo(nodo.next)