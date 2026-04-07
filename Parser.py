import sys
import Env
from Token import Token

class TreeNode:
    def __init__(self, token):
        self.token = token
        self.left = None    # Hijo izquierdo (ej. Condición, Operando 1, Variable)
        self.right = None   # Hijo derecho (ej. Bloque True, Operando 2, Valor asignado)
        self.center = None  # Hijo central (Usado para el Else/ElseIf en el If)
        self.step = None    # Hijo de paso (Usado EXCLUSIVAMENTE para el incremento del FOR)
        self.next = None    # Siguiente instrucción (Hermano)
    
    def __repr__(self):
        return f"TreeNode({self.token.type}, {self.token.value})"

    def print_tree(self, level=0):
        indent = "    " * level
        simbolo = "| " if level > 0 else ""
        text = f"{indent}{simbolo} {self.token.type}: {self.token.value}"
        
        if Env.console:
            Env.console.print(text)
        else:
            print(text)
        
        # Hijos lógicos/matemáticos y de estructura
        if self.left: self.left.print_tree(level + 1)
        if self.center: self.center.print_tree(level + 1)
        if self.step: self.step.print_tree(level + 1)
        if self.right: self.right.print_tree(level + 1)
        
        # Instrucción siguiente (mismo nivel)
        if self.next:
            self.next.print_tree(level)

class Parser:
    def __init__(self, lexer, console=None):
        self.lexer = lexer
        self.console = console or Env.console
        self.token_actual = self.lexer.siguienteToken()
        self.ultimo_fue_bloque = False

    def parse(self):
        if self.lexer.existeTraza(): 
            self.console.print("INICIO DE ANALISIS SINTACTICO (Generación de AST)")
        return self.programa()

    def programa(self):
        if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <PROGRAMA>")
        
        if self.token_actual.type == Token.Type.PhpOpen:
            raiz = TreeNode(self.token_actual)
            self.eat(Token.Type.PhpOpen)
            raiz.left = self.lista_instrucciones()
            
            if self.token_actual.type == Token.Type.PhpClose:
                self.eat(Token.Type.PhpClose)
            elif self.token_actual.type != Token.Type.Fin:
                self.errores(2)
            return raiz
        else:
            self.errores(8)
            return None

    def lista_instrucciones(self):
        # Condición de parada para la recursividad de instrucciones
        if self.token_actual.type in (Token.Type.PhpClose, Token.Type.Fin, Token.Type.LlaveDer, Token.Type.Case, Token.Type.Default):
            return None
            
        nodo_instruccion = self.sentencia()
        
        # Validar el punto y coma si la instrucción no fue un bloque (if, while, for, switch)
        if not self.ultimo_fue_bloque:
            if self.token_actual.type == Token.Type.PuntoComa:
                self.eat(Token.Type.PuntoComa)
            else:
                self.errores(1)
                
        if nodo_instruccion:
            nodo_instruccion.next = self.lista_instrucciones()
            return nodo_instruccion
        else:
            # Si la sentencia devolvió None, intentamos seguir parseando
            return self.lista_instrucciones()

    def sentencia(self):
        self.ultimo_fue_bloque = False 
        if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA>")
        
        t = self.token_actual.type
        
        if t == Token.Type.Variable: return self.asignacion()
        elif t == Token.Type.Echo: return self.instruccion_echo()
        elif t == Token.Type.Read: return self.instruccion_read()
        elif t == Token.Type.If: return self.instruccion_if()
        elif t == Token.Type.While: return self.instruccion_while()
        elif t == Token.Type.For: return self.instruccion_for()
        elif t == Token.Type.Switch: return self.instruccion_switch()
        elif t == Token.Type.Break:
            nodo_break = TreeNode(self.token_actual)
            self.eat(Token.Type.Break)
            return nodo_break
        else:
            if t not in [Token.Type.PhpClose, Token.Type.LlaveDer]:
                self.errores(6)
            return None

    def asignacion(self):
        nodo_var = TreeNode(self.token_actual)
        self.eat(Token.Type.Variable)
        
        # Soporte para asignación a índices de arreglos: $arr[$i] = ...
        if self.token_actual.type == Token.Type.CorcheteIzq:
            self.eat(Token.Type.CorcheteIzq)
            nodo_var.left = self.condicion() # Guardamos el índice como hijo izquierdo de la variable
            if self.token_actual.type != Token.Type.CorcheteDer: self.errores(16)
            self.eat(Token.Type.CorcheteDer)

        # Soporte para Incrementos/Decrementos aislados: $i++; o $i--;
        if self.token_actual.type in [Token.Type.Incremento, Token.Type.Decremento]:
            nodo_op = TreeNode(self.token_actual)
            self.eat(self.token_actual.type)
            nodo_op.left = nodo_var
            return nodo_op
        
        nodo_asig = TreeNode(self.token_actual)
        if self.token_actual.type != Token.Type.Asignacion: self.errores(3)
        self.eat(Token.Type.Asignacion)
        
        nodo_asig.left = nodo_var
        
        # Soporte para declaración de arreglos: $arr = array(1,2,3);
        if self.token_actual.type == Token.Type.Array:
            nodo_asig.right = self.declaracion_array()
        else:
            nodo_asig.right = self.condicion() 
            
        return nodo_asig

    def declaracion_array(self):
        nodo_arr = TreeNode(self.token_actual)
        self.eat(Token.Type.Array)
        if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
        self.eat(Token.Type.ParIzq)
        
        nodo_arr.left = self.lista_argumentos()
        
        if self.token_actual.type != Token.Type.ParDer: self.errores(4)
        self.eat(Token.Type.ParDer)
        return nodo_arr

    def lista_argumentos(self):
        if self.token_actual.type == Token.Type.ParDer:
            return None # Arreglo vacío
            
        nodo = self.condicion()
        
        if self.token_actual.type == Token.Type.Coma:
            self.eat(Token.Type.Coma)
            nodo.next = self.lista_argumentos()
            
        return nodo

    def instruccion_echo(self):
        nodo_echo = TreeNode(self.token_actual)
        self.eat(Token.Type.Echo)
        
        # Echo ahora soporta expresiones completas como variables, cadenas o arreglos
        nodo_echo.left = self.condicion()
            
        return nodo_echo

    def instruccion_read(self):
        nodo_read = TreeNode(self.token_actual)
        self.eat(Token.Type.Read)
        
        if self.token_actual.type == Token.Type.Variable:
            nodo_read.left = TreeNode(self.token_actual)
            self.eat(Token.Type.Variable)
        else:
            self.errores(5)
            
        return nodo_read

    def instruccion_if(self):
        if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_IF>")
        nodo_if = TreeNode(self.token_actual)
        self.eat(Token.Type.If)
        
        if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
        self.eat(Token.Type.ParIzq)
        nodo_if.left = self.condicion()
        if self.token_actual.type != Token.Type.ParDer: self.errores(4)
        self.eat(Token.Type.ParDer)
        
        if self.token_actual.type != Token.Type.LlaveIzq: self.errores(9)
        self.eat(Token.Type.LlaveIzq)
        nodo_if.right = self.lista_instrucciones()
        if self.token_actual.type != Token.Type.LlaveDer: self.errores(11)
        self.eat(Token.Type.LlaveDer)
        
        actual = nodo_if
        
        # Procesar ElseIf
        while self.token_actual.type == Token.Type.ElseIf:
            if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <ELSEIF>")
            nodo_elseif = TreeNode(self.token_actual)
            self.eat(Token.Type.ElseIf)
            
            if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
            self.eat(Token.Type.ParIzq)
            nodo_elseif.left = self.condicion()
            if self.token_actual.type != Token.Type.ParDer: self.errores(4)
            self.eat(Token.Type.ParDer)
            
            if self.token_actual.type != Token.Type.LlaveIzq: self.errores(9)
            self.eat(Token.Type.LlaveIzq)
            nodo_elseif.right = self.lista_instrucciones()
            if self.token_actual.type != Token.Type.LlaveDer: self.errores(11)
            self.eat(Token.Type.LlaveDer)
            
            actual.center = nodo_elseif
            actual = nodo_elseif

        # Procesar Else
        if self.token_actual.type == Token.Type.Else:
            if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <ELSE>")
            nodo_else = TreeNode(self.token_actual)
            self.eat(Token.Type.Else)
            
            if self.token_actual.type != Token.Type.LlaveIzq: self.errores(9)
            self.eat(Token.Type.LlaveIzq)
            nodo_else.right = self.lista_instrucciones()
            if self.token_actual.type != Token.Type.LlaveDer: self.errores(11)
            self.eat(Token.Type.LlaveDer)
            
            actual.center = nodo_else

        self.ultimo_fue_bloque = True
        return nodo_if

    def instruccion_while(self):
        if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_WHILE>")
        nodo_while = TreeNode(self.token_actual)
        self.eat(Token.Type.While)
        
        if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
        self.eat(Token.Type.ParIzq)
        nodo_while.left = self.condicion()
        if self.token_actual.type != Token.Type.ParDer: self.errores(4)
        self.eat(Token.Type.ParDer)
        
        if self.token_actual.type != Token.Type.LlaveIzq: self.errores(9)
        self.eat(Token.Type.LlaveIzq)
        nodo_while.right = self.lista_instrucciones()
        if self.token_actual.type != Token.Type.LlaveDer: self.errores(11)
        self.eat(Token.Type.LlaveDer)
        
        self.ultimo_fue_bloque = True
        return nodo_while

    def instruccion_for(self):
        if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_FOR>")
        nodo_for = TreeNode(self.token_actual)
        self.eat(Token.Type.For)
        
        if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
        self.eat(Token.Type.ParIzq)
        
        # 1. Inicialización (Ej: $i = 0)
        nodo_for.left = self.asignacion()
        if self.token_actual.type != Token.Type.PuntoComa: self.errores(1)
        self.eat(Token.Type.PuntoComa)
        
        # 2. Condición (Ej: $i < 10)
        nodo_for.center = self.condicion()
        if self.token_actual.type != Token.Type.PuntoComa: self.errores(1)
        self.eat(Token.Type.PuntoComa)
        
        # 3. Paso/Incremento (Ej: $i++)
        nodo_for.step = self.asignacion()
        
        if self.token_actual.type != Token.Type.ParDer: self.errores(4)
        self.eat(Token.Type.ParDer)
        
        # 4. Cuerpo del Bucle
        if self.token_actual.type != Token.Type.LlaveIzq: self.errores(9)
        self.eat(Token.Type.LlaveIzq)
        nodo_for.right = self.lista_instrucciones()
        if self.token_actual.type != Token.Type.LlaveDer: self.errores(11)
        self.eat(Token.Type.LlaveDer)
        
        self.ultimo_fue_bloque = True
        return nodo_for

    def instruccion_switch(self):
        if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_SWITCH>")
        nodo_switch = TreeNode(self.token_actual)
        self.eat(Token.Type.Switch)
        
        if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
        self.eat(Token.Type.ParIzq)
        
        if self.token_actual.type == Token.Type.Variable:
            nodo_switch.left = TreeNode(self.token_actual)
            self.eat(Token.Type.Variable)
        else:
            self.errores(5)
            
        if self.token_actual.type != Token.Type.ParDer: self.errores(4)
        self.eat(Token.Type.ParDer)
        
        if self.token_actual.type != Token.Type.LlaveIzq: self.errores(9)
        self.eat(Token.Type.LlaveIzq)
        
        nodo_switch.right = self.lista_cases()
        
        if self.token_actual.type != Token.Type.LlaveDer: self.errores(11)
        self.eat(Token.Type.LlaveDer)
        
        self.ultimo_fue_bloque = True
        return nodo_switch

    def lista_cases(self):
        if self.token_actual.type not in [Token.Type.Case, Token.Type.Default]:
            return None
            
        nodo_case = TreeNode(self.token_actual)
        
        if self.token_actual.type == Token.Type.Case:
            if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <CASE>")
            self.eat(Token.Type.Case)
            if self.token_actual.type == Token.Type.Numero:
                nodo_case.left = TreeNode(self.token_actual)
                self.eat(Token.Type.Numero)
            else:
                self.errores(7)
                
            if self.token_actual.type != Token.Type.DosPuntos: self.errores(13)
            self.eat(Token.Type.DosPuntos)
            nodo_case.right = self.lista_instrucciones()
            
        elif self.token_actual.type == Token.Type.Default:
            if self.lexer.existeTraza(): self.console.print("ANALISIS SINTACTICO: <DEFAULT>")
            self.eat(Token.Type.Default)
            if self.token_actual.type != Token.Type.DosPuntos: self.errores(13)
            self.eat(Token.Type.DosPuntos)
            nodo_case.right = self.lista_instrucciones()
            
        nodo_case.next = self.lista_cases()
        return nodo_case

    def condicion(self):
        nodo_izq = self.expr()
        ops_relacionales = [Token.Type.IgualQue, Token.Type.DiferenteQue, Token.Type.MenorQue, 
                            Token.Type.MayorQue, Token.Type.MenorIgual, Token.Type.MayorIgual]
                            
        if self.token_actual.type in ops_relacionales:
            nodo_op = TreeNode(self.token_actual)
            self.eat(self.token_actual.type)
            nodo_der = self.expr()
            nodo_op.left = nodo_izq
            nodo_op.right = nodo_der
            return nodo_op
            
        return nodo_izq

    def expr(self): 
        node = self.termino()
        while self.token_actual.type in (Token.Type.Suma, Token.Type.Resta):
            token_op = self.token_actual
            self.eat(token_op.type)
            new_node = TreeNode(token_op)
            new_node.left = node
            new_node.right = self.termino()
            node = new_node
        return node
    
    def termino(self): 
        node = self.factor()
        while self.token_actual.type in (Token.Type.Multiplica, Token.Type.Divide, Token.Type.Modulo):
            token_op = self.token_actual
            self.eat(token_op.type)
            new_node = TreeNode(token_op)
            new_node.left = node
            new_node.right = self.factor()
            node = new_node
        return node
    
    def factor(self): 
        token_actual = self.token_actual
        
        if token_actual.type == Token.Type.Numero:
            self.eat(Token.Type.Numero)
            return TreeNode(token_actual)
            
        elif token_actual.type == Token.Type.Variable:
            self.eat(Token.Type.Variable)
            # Soporte para lectura de arreglos: $var[$i]
            if self.token_actual.type == Token.Type.CorcheteIzq:
                self.eat(Token.Type.CorcheteIzq)
                idx = self.condicion()
                if self.token_actual.type != Token.Type.CorcheteDer: self.errores(16)
                self.eat(Token.Type.CorcheteDer)
                n = TreeNode(token_actual)
                n.left = idx
                return n
            return TreeNode(token_actual)
            
        elif token_actual.type == Token.Type.Count:
            self.eat(Token.Type.Count)
            nodo_count = TreeNode(token_actual)
            if self.token_actual.type != Token.Type.ParIzq: self.errores(10)
            self.eat(Token.Type.ParIzq)
            
            if self.token_actual.type == Token.Type.Variable:
                nodo_count.left = TreeNode(self.token_actual)
                self.eat(Token.Type.Variable)
            else:
                self.errores(5) # Esperaba variable dentro del count
                
            if self.token_actual.type != Token.Type.ParDer: self.errores(4)
            self.eat(Token.Type.ParDer)
            return nodo_count
            
        elif token_actual.type == Token.Type.ParIzq:
            self.eat(Token.Type.ParIzq)
            node = self.condicion()
            if self.token_actual.type != Token.Type.ParDer: self.errores(4)
            self.eat(Token.Type.ParDer)
            return node
            
        else:
            self.errores(6) # Factor inesperado
            return None
            
    def eat(self, token_type):
        if self.token_actual.type == token_type:
            self.token_actual = self.lexer.siguienteToken()
        else:
            msg = f"Error Interno de Sintaxis: Se esperaba {token_type}, se obtuvo {self.token_actual.type}"
            if Env.console: Env.console.print_alert(msg)
            else: print(msg)

    def errores(self, codigo):
        linea = self.lexer.lineaActual() if hasattr(self.lexer, 'lineaActual') else "Desconocida"
        self.console.print(f"LINEA {linea} ERROR SINTACTICO {codigo}")
        error_messages = {
            1: " :ESPERABA UN ;", 2: " :ESPERABA UN ?> AL FINAL", 3: " :ESPERABA UN =",
            4: " :ESPERABA UN )", 5: " :ESPERABA UNA VARIABLE PHP (EJEMPLO: $var)",
            6: " :INSTRUCCION DESCONOCIDA O SINTAXIS INVALIDA", 7: " :ESPERABA UNA CONSTANTE",
            8: " :ESPERABA LA ETIQUETA <?php", 9: " :ESPERABA UNA {", 10: " :ESPERABA UN (",
            11: " :ESPERABA UNA }", 12: " :ESPERABA UN OPERADOR RELACIONAL (==, !=, <, >, <=, >=)",
            13: " :ESPERABA UN : (DOS PUNTOS)",
            14: " :ESPERABA 'case' O 'default'",
            15: " :BREAK FUERA DE UN CICLO O SWITCH",
            16: " :ESPERABA UN ]"
        }
        self.console.print(error_messages.get(codigo, " :NO DOCUMENTADO"))
        sys.exit(-(codigo + 100))