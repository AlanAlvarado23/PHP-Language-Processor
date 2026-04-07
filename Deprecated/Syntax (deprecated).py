import sys
from Lexer import Lexer
from Middle_Code import GeneraCodigo
from Token import Token

class Sintactico:
    def __init__(self, fuente: str, objeto: str, traza: int, console):
        self.console = console
        self.lexico = Lexer(fuente, traza) # Actualizado para no pasar console al Lexer según tu última versión
        self.generaCodigo = GeneraCodigo(objeto, self.console)
        
        # Pilas para manejar etiquetas de saltos (útil para bucles anidados y switch)
        self.pila_etiq_inicio_ciclo = []
        self.pila_etiq_fin_ciclo = []
        self.etiq_fin_switch_actual = None 
        
        self.ultimo_fue_bloque = False  

        if self.lexico.existeTraza(): 
            self.console.print("INICIO DE ANALISIS SINTACTICO")
        self.programa()

    def programa(self):
        if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <PROGRAMA>")
        token = self.lexico.siguienteToken()
        
        if token.type == Token.Type.PhpOpen: 
            self.generaCodigo.code()
        else: 
            self.errores(8)
            
        self.bloque()
        
        token = self.lexico.siguienteToken()
        if token.type == Token.Type.PhpClose: 
            self.generaCodigo.end()
        elif token.type != Token.Type.Fin:
            self.errores(2)

    def bloque(self):
        if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <BLOQUE>")
        self.sentencia()
        self.otra_sentencia()

    def otra_sentencia(self):
        token = self.lexico.siguienteToken()
        
        if token.type == Token.Type.Fin:
            return

        if token.type == Token.Type.PuntoComa:
            self.ultimo_fue_bloque = False 
            if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <OTRA_SENTENCIA>")
            siguiente = self.lexico.siguienteToken()
            
            if siguiente.type in [Token.Type.Case, Token.Type.Default, Token.Type.LlaveDer, Token.Type.PhpClose, Token.Type.Fin]:
                self.lexico.devuelveToken(siguiente)
            else:
                self.lexico.devuelveToken(siguiente)
                self.sentencia()
                self.otra_sentencia()
                
        # Si la instrucción anterior fue un bloque {}, podemos seguir sin punto y coma
        elif self.ultimo_fue_bloque and (token.type in [Token.Type.If, Token.Type.While, Token.Type.Switch, Token.Type.Echo, Token.Type.Read, Token.Type.Break] or token.type == Token.Type.Variable):
            self.lexico.devuelveToken(token)
            self.sentencia()
            self.otra_sentencia()
            
        else:
            self.lexico.devuelveToken(token)

    def sentencia(self):
        self.ultimo_fue_bloque = False 
        token = self.lexico.siguienteToken()
        if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA>")
        
        if token.type == Token.Type.Variable:
            self.lexico.devuelveToken(token)
            self.asignacion()
        elif token.type == Token.Type.Read: self.lectura()
        elif token.type == Token.Type.Echo: self.escritura()
        elif token.type == Token.Type.If: self.sentencia_if()
        elif token.type == Token.Type.While: self.sentencia_while()
        elif token.type == Token.Type.Switch: self.sentencia_switch()
        elif token.type == Token.Type.Break:
            if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <BREAK>")
            # El break puede salir de un switch o de un ciclo
            if self.pila_etiq_fin_ciclo:
                self.generaCodigo.jmp(self.pila_etiq_fin_ciclo[-1])
            elif self.etiq_fin_switch_actual:
                self.generaCodigo.jmp(self.etiq_fin_switch_actual)
            else:
                self.errores(15)
        else:
            if token.type in [Token.Type.PhpClose, Token.Type.LlaveDer]: 
                 self.lexico.devuelveToken(token)
            else:
                 self.errores(6)

    def sentencia_while(self):
        if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_WHILE>")
        
        etiq_inicio = self.generaCodigo.nueva_etiqueta()
        self.generaCodigo.label(etiq_inicio)
        self.pila_etiq_inicio_ciclo.append(etiq_inicio)
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.ParIzq: self.errores(10)
        
        self.condicion()
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.ParDer: self.errores(4)
        
        etiq_fin = self.generaCodigo.nueva_etiqueta()
        self.pila_etiq_fin_ciclo.append(etiq_fin)
        self.generaCodigo.jmpf(etiq_fin)
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.LlaveIzq: self.errores(9)
        
        self.bloque()
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.LlaveDer: self.errores(11)
        
        self.generaCodigo.jmp(etiq_inicio)
        self.generaCodigo.label(etiq_fin)
        
        self.pila_etiq_inicio_ciclo.pop()
        self.pila_etiq_fin_ciclo.pop()
        
        self.ultimo_fue_bloque = True

    def sentencia_switch(self):
        if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_SWITCH>")
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.ParIzq: self.errores(10)
        
        var_token = self.lexico.siguienteToken()
        if var_token.type != Token.Type.Variable: self.errores(5)
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.ParDer: self.errores(4)
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.LlaveIzq: self.errores(9)
        
        # Guardar el switch anterior si hay anidados (opcional, pero buena práctica)
        switch_anterior = self.etiq_fin_switch_actual
        self.etiq_fin_switch_actual = self.generaCodigo.nueva_etiqueta()
        etiq_siguiente_caso = None
        
        token = self.lexico.siguienteToken()
        while token.type in [Token.Type.Case, Token.Type.Default]:
            if etiq_siguiente_caso:
                self.generaCodigo.label(etiq_siguiente_caso)
                
            if token.type == Token.Type.Case:
                if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <CASE>")
                val_token = self.lexico.siguienteToken()
                if val_token.type != Token.Type.Numero: self.errores(7)
                
                tok_dos_puntos = self.lexico.siguienteToken()
                if tok_dos_puntos.type != Token.Type.DosPuntos: self.errores(13)
                
                self.generaCodigo.pusha(var_token.value)
                self.generaCodigo.load()
                self.generaCodigo.pushc(val_token.value)
                self.generaCodigo.op_relacional('==')
                
                etiq_siguiente_caso = self.generaCodigo.nueva_etiqueta()
                self.generaCodigo.jmpf(etiq_siguiente_caso)
                
                self.bloque() 
                
            elif token.type == Token.Type.Default:
                if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <DEFAULT>")
                tok_dos_puntos = self.lexico.siguienteToken()
                if tok_dos_puntos.type != Token.Type.DosPuntos: self.errores(13)
                
                etiq_siguiente_caso = self.generaCodigo.nueva_etiqueta()
                self.bloque()
                
            token = self.lexico.siguienteToken()
            
        if token.type != Token.Type.LlaveDer: self.errores(11)
        
        if etiq_siguiente_caso:
            self.generaCodigo.label(etiq_siguiente_caso)
            
        self.generaCodigo.label(self.etiq_fin_switch_actual)
        self.etiq_fin_switch_actual = switch_anterior # Restaurar
        
        self.ultimo_fue_bloque = True 

    def sentencia_if(self):
        if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <SENTENCIA_IF>")
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.ParIzq: self.errores(10)
        
        self.condicion()
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.ParDer: self.errores(4)
        
        etiq_falso = self.generaCodigo.nueva_etiqueta()
        self.generaCodigo.jmpf(etiq_falso)
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.LlaveIzq: self.errores(9)
        
        self.bloque()
        
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.LlaveDer: self.errores(11)
        
        etiq_fin = None # Etiqueta para saltar al final de toda la estructura
        
        token = self.lexico.siguienteToken()
        
        # --- NUEVO: Procesamos múltiples elseif encadenados ---
        while token.type == Token.Type.ElseIf:
            if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <ELSEIF>")
            
            if not etiq_fin: 
                etiq_fin = self.generaCodigo.nueva_etiqueta()
            
            # Si el bloque anterior fue verdadero, saltamos al final
            self.generaCodigo.jmp(etiq_fin) 
            
            # Aquí cae si la condición anterior fue falsa
            self.generaCodigo.label(etiq_falso) 
            
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.ParIzq: self.errores(10)
            self.condicion()
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.ParDer: self.errores(4)
            
            etiq_falso = self.generaCodigo.nueva_etiqueta()
            self.generaCodigo.jmpf(etiq_falso)
            
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.LlaveIzq: self.errores(9)
            self.bloque()
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.LlaveDer: self.errores(11)
            
            token = self.lexico.siguienteToken()

        # --- Procesamos el else final ---
        if token.type == Token.Type.Else:
            if self.lexico.existeTraza(): self.console.print("ANALISIS SINTACTICO: <ELSE>")
            
            if not etiq_fin: 
                etiq_fin = self.generaCodigo.nueva_etiqueta()
                
            self.generaCodigo.jmp(etiq_fin)
            self.generaCodigo.label(etiq_falso)
            
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.LlaveIzq: self.errores(9)
            
            self.bloque()
            
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.LlaveDer: self.errores(11)
            
            self.generaCodigo.label(etiq_fin)
            self.ultimo_fue_bloque = True 
            
        else:
            # Si no hay else ni elseif, devolvemos el token
            self.lexico.devuelveToken(token)
            self.generaCodigo.label(etiq_falso)
            
            if etiq_fin:
                self.generaCodigo.label(etiq_fin)
                
            self.ultimo_fue_bloque = True

    def condicion(self):
        self.expresion()
        token = self.lexico.siguienteToken()
        # Verificamos si es un operador relacional
        if token.type in [Token.Type.IgualQue, Token.Type.DiferenteQue, Token.Type.MenorQue, Token.Type.MayorQue, Token.Type.MenorIgual, Token.Type.MayorIgual]:
            self.expresion()
            self.generaCodigo.op_relacional(token.value)
        else:
            self.errores(12)

    def asignacion(self):
        self.variable()
        token = self.lexico.siguienteToken()
        if token.type != Token.Type.Asignacion: self.errores(3)
        self.expresion()
        self.generaCodigo.store()

    def variable(self):
        token = self.lexico.siguienteToken()
        if token.type == Token.Type.Variable: 
            self.generaCodigo.pusha(token.value)
        else: 
            self.errores(5)

    def expresion(self):
        self.termino()
        self.mas_terminos()

    def termino(self):
        self.factor()
        self.mas_factores()

    def mas_terminos(self):
        token = self.lexico.siguienteToken()
        if token.type == Token.Type.Suma:
            self.termino()
            self.generaCodigo.add()
            self.mas_terminos()
        elif token.type == Token.Type.Resta:
            self.termino()
            self.generaCodigo.neg()
            self.generaCodigo.add()
            self.mas_terminos()
        else:
            self.lexico.devuelveToken(token)

    def factor(self):
        token = self.lexico.siguienteToken()
        if token.type == Token.Type.Numero:
            self.lexico.devuelveToken(token)
            self.constante()
        elif token.type == Token.Type.ParIzq:
            self.expresion()
            token = self.lexico.siguienteToken()
            if token.type != Token.Type.ParDer: self.errores(4)
        else:
            self.lexico.devuelveToken(token)
            self.variable()
            self.generaCodigo.load()

    def mas_factores(self):
        token = self.lexico.siguienteToken()
        if token.type in [Token.Type.Multiplica, Token.Type.Divide, Token.Type.Modulo]:
            self.factor()
            if token.type == Token.Type.Multiplica: self.generaCodigo.mul()
            elif token.type == Token.Type.Divide: self.generaCodigo.div()
            elif token.type == Token.Type.Modulo: self.generaCodigo.mod()
            self.mas_factores()
        else:
            self.lexico.devuelveToken(token)

    def lectura(self):
        token = self.lexico.siguienteToken() 
        if token.type != Token.Type.Variable: self.errores(5)
        self.generaCodigo.input(token.value)

    def escritura(self):
        token = self.lexico.siguienteToken() 
        # Ahora aceptamos Variables (ej. $var) y Números (ej. 1)
        if token.type not in [Token.Type.Variable, Token.Type.Numero]: 
            self.errores(5) # Nota: Podrías cambiar el texto del error 5 en tu diccionario a "ESPERABA VARIABLE O CONSTANTE"
        self.generaCodigo.output(token.value)

    def constante(self):
        token = self.lexico.siguienteToken()
        if token.type == Token.Type.Numero: 
            self.generaCodigo.pushc(token.value)
        else: 
            self.errores(7)

    def errores(self, codigo):
        # Usar la línea del Lexer de forma segura
        linea = self.lexico.lineaActual() if hasattr(self.lexico, 'lineaActual') else "Desconocida"
        self.console.print(f"LINEA {linea} ERROR SINTACTICO {codigo}")
        error_messages = {
            1: " :ESPERABA UN ;", 2: " :ESPERABA UN ?> AL FINAL", 3: " :ESPERABA UN =",
            4: " :ESPERABA UN )", 5: " :ESPERABA UNA VARIABLE PHP (EJEMPLO: $var)",
            6: " :INSTRUCCION DESCONOCIDA O SINTAXIS INVALIDA", 7: " :ESPERABA UNA CONSTANTE",
            8: " :ESPERABA LA ETIQUETA <?php", 9: " :ESPERABA UNA {", 10: " :ESPERABA UN (",
            11: " :ESPERABA UNA }", 12: " :ESPERABA UN OPERADOR RELACIONAL (==, !=, <, >, <=, >=)",
            13: " :ESPERABA UN : (DOS PUNTOS)",
            14: " :ESPERABA 'case' O 'default'",
            15: " :BREAK FUERA DE UN CICLO O SWITCH"
        }
        self.console.print(error_messages.get(codigo, " :NO DOCUMENTADO"))
        sys.exit(-(codigo + 100))