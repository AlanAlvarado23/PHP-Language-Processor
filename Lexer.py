import re
import Env
from Token import Token


class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}

    def registrar(self, nombre, tipo="Variable"):
        if nombre not in self.simbolos:
            self.simbolos[nombre] = {"categoria": tipo, "direccion": len(self.simbolos)}

    def existe(self, nombre):
        return nombre in self.simbolos


class Lexer:
    def __init__(self, fuente, traza):
        # 1. Definimos el diccionario con los NUEVOS TIPOS (array, count, ++, --)
        self.words = {
            '<?php': Token.Type.PhpOpen,
            '?>': Token.Type.PhpClose,
            'echo': Token.Type.Echo,
            'read': Token.Type.Read,
            'if': Token.Type.If,
            'elseif': Token.Type.ElseIf,
            'else': Token.Type.Else,
            'switch': Token.Type.Switch,
            'case': Token.Type.Case,
            'default': Token.Type.Default,
            'break': Token.Type.Break,
            'while': Token.Type.While,
            'for': Token.Type.For,
            'array': Token.Type.Array,        # <-- ¡Añadido!
            'count': Token.Type.Count,        # <-- ¡Añadido!
            '+': Token.Type.Suma,
            '-': Token.Type.Resta,
            '*': Token.Type.Multiplica,
            '/': Token.Type.Divide,
            '%': Token.Type.Modulo,
            '++': Token.Type.Incremento,      # <-- ¡Añadido!
            '--': Token.Type.Decremento,      # <-- ¡Añadido!
            '==': Token.Type.Igualdad,
            '!=': Token.Type.Desigualdad,
            '<=': Token.Type.MenorIgual,
            '>=': Token.Type.MayorIgual,
            '<': Token.Type.MenorQue,
            '>': Token.Type.MayorQue,
            '=': Token.Type.Asignacion,
            ';': Token.Type.PuntoComa,
            '{': Token.Type.LlaveIzq,
            '}': Token.Type.LlaveDer,
            '(': Token.Type.ParIzq,
            ')': Token.Type.ParDer,
            '[': Token.Type.CorcheteIzq,
            ']': Token.Type.CorcheteDer,
            ':': Token.Type.DosPuntos,
            ',': Token.Type.Coma
        }

        self.fuente = fuente
        self.traza = traza
        self.linea = 1
        self.tabla_simbolos = TablaSimbolos()
        self.pos = 0
        self.pila_devueltos = []
        
        self.tokens = self.tokenizar(fuente)

    def clasificar_a_token(self, valor, linea_actual):
        if valor.startswith('$'): 
            return Token(Token.Type.Variable, valor, linea_actual)
        elif valor.isdigit(): 
            return Token(Token.Type.Numero, valor, linea_actual)
        
        elif valor in self.words: 
            return Token(self.words[valor], valor, linea_actual)
        
        return Token(Token.Type.Invalido, valor, linea_actual)

    def tokenizar(self, fuente):
        # 2. Expresión regular actualizada:
        # Se añaden 'array', 'count', '\+\+' y '--'
        # Nota: \+\+ y -- se evalúan ANTES que el bloque de caracteres individuales [=+\-*/...]
        patron = r'\n|(?P<COMENTARIO>//[^\n]*)|(?P<TOK><\?php|\?>|echo|read|if|elseif|else|switch|case|break|default|while|for|array|count|\$[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+|==|!=|<=|>=|<|>|\+\+|--|[=+\-*/%;(){}\[\]:,])'
        
        lista_tokens = []
        linea_actual = 1
        
        for match in re.finditer(patron, fuente):
            if match.group(0) == '\n':
                linea_actual += 1
            elif match.group('COMENTARIO'):
                pass 
            elif match.group('TOK'):
                valor = match.group('TOK')
                nuevo_token = self.clasificar_a_token(valor, linea_actual)
                lista_tokens.append(nuevo_token)
                
                # Registrar en la tabla de símbolos si es variable
                if nuevo_token.type == Token.Type.Variable:
                    self.tabla_simbolos.registrar(nuevo_token.value, "Identificador")
                    
        return lista_tokens

    def siguienteToken(self):
        """Retorna un objeto Token."""
        if self.pila_devueltos:
            return self.pila_devueltos.pop()
            
        if self.pos < len(self.tokens):
            token_actual = self.tokens[self.pos]
            self.linea = token_actual.line
            self.pos += 1
            return token_actual
            
        return Token(Token.Type.Fin, "$EOF$", self.linea)

    def devuelveToken(self, token_obj):
        """Recibe un objeto Token y lo regresa a la pila."""
        if token_obj.type != Token.Type.Fin:
            self.pila_devueltos.append(token_obj)

    def existeTraza(self):
        return self.traza == 1
        
    def lineaActual(self):
        return self.linea