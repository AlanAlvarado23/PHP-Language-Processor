import re
import Env
from Token import Token


class Symbol_Table:
    """
    Maintains a record of identified variables and their assigned memory addresses.
    """
    def __init__(self):
        self.symbols = {}

    def register(self, name, symbol_type="Variable"):
        """Registers a new symbol if it hasn't been added yet."""
        if name not in self.symbols:
            self.symbols[name] = {"category": symbol_type, "address": len(self.symbols)}

    def exists(self, name) -> bool:
        """Checks if a symbol is already registered."""
        return name in self.symbols


class Lexer:
    """
    Lexical Analyzer (Scanner).
    Reads the raw source code and converts it into a stream of Tokens.
    """
    def __init__(self, source_code, trace):
        # 1. Define the dictionary mapping string literals to their Token Types.
        # Aligned with the English names expected by Parser.py
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
            'array': Token.Type.Array,        
            'count': Token.Type.Count,        
            '+': Token.Type.Addition,
            '-': Token.Type.Subtraction,
            '*': Token.Type.Multiplication,
            '/': Token.Type.Division,
            '%': Token.Type.Modulo,
            '++': Token.Type.Increment,      
            '--': Token.Type.Decrement,      
            '==': Token.Type.Equality,
            '!=': Token.Type.Inequality,
            '<=': Token.Type.LessOrEqual,
            '>=': Token.Type.GreaterOrEqual,
            '<': Token.Type.LessThan,
            '>': Token.Type.GreaterThan,
            '=': Token.Type.Assignment,
            ';': Token.Type.Semicolon,
            '{': Token.Type.LeftBrace,
            '}': Token.Type.RightBrace,
            '(': Token.Type.LeftParen,
            ')': Token.Type.RightParen,
            '[': Token.Type.LeftBracket,
            ']': Token.Type.RightBracket,
            ':': Token.Type.Colon,
            ',': Token.Type.Comma
        }

        self.source_code = source_code
        self.trace = trace
        self.line = 1
        self.symbol_table = Symbol_Table()
        self.pos = 0
        self.returned_stack = []
        
        # Tokenize the entire source code upon initialization
        self.tokens = self.tokenize(source_code)

    def classify_token(self, value: str, current_line: int) -> Token:
        """Determines the specific Token type based on the extracted string value."""
        if value.startswith('$'): 
            return Token(Token.Type.Variable, value, current_line)
        elif value.isdigit(): 
            return Token(Token.Type.Number, value, current_line)
            
        # --- Detect String literals ---
        elif value.startswith('"') or value.startswith("'"):
            return Token(Token.Type.String, value, current_line)
        # ----------------------------------------
            
        elif value in self.words: 
            return Token(self.words[value], value, current_line)
        
        return Token(Token.Type.Invalid, value, current_line)

    def tokenize(self, source_code) -> list:
        """
        Scans the source code using a Regular Expression to identify valid lexemes.
        Returns a list of classified Token objects.
        """
        # 2. Updated Regular Expression:
        # Added 'array', 'count', '\+\+' and '--'
        # Note: \+\+ and -- are evaluated BEFORE the individual character block [=+\-*/...] to avoid conflicts.
        pattern = r'\n|(?P<COMMENT>//[^\n]*)|(?P<TOK>\"[^\"]*\"|\'[^\']*\'|<\?php|\?>|echo|read|if|elseif|else|switch|case|break|default|while|for|array|count|\$[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+|==|!=|<=|>=|<|>|\+\+|--|[=+\-*/%;(){}\[\]:,])'
        
        token_list = []
        current_line = 1
        
        for match in re.finditer(pattern, source_code):
            if match.group(0) == '\n':
                current_line += 1
            elif match.group('COMMENT'):
                pass # Ignore comments entirely
            elif match.group('TOK'):
                value = match.group('TOK')
                new_token = self.classify_token(value, current_line)
                token_list.append(new_token)
                
                # Register in the symbol table if it's a variable
                if new_token.type == Token.Type.Variable:
                    self.symbol_table.register(new_token.value, "Identifier")
                    
        return token_list

    def next_token(self) -> Token:
        """
        Returns the next Token in the sequence. 
        Pops from the returned_stack first if any tokens were pushed back.
        """
        if self.returned_stack:
            return self.returned_stack.pop()
            
        if self.pos < len(self.tokens):
            current_token = self.tokens[self.pos]
            self.line = current_token.line
            self.pos += 1
            return current_token
            
        # Return an End Of File (EOF) token when the list is exhausted
        return Token(Token.Type.End, "$EOF$", self.line)

    def return_token(self, token_obj: Token):
        """Pushes a Token back into the stack so it can be read again."""
        if token_obj.type != Token.Type.End:
            self.returned_stack.append(token_obj)

    def trace_exists(self) -> bool:
        """Checks if the tracing/debugging flag is enabled."""
        return self.trace == 1
        
    def current_line(self) -> int:
        """Returns the current line number being processed."""
        return self.line