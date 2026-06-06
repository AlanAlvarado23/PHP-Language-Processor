import sys
import Env
from Token import Token

class Tree_Node:
    """
    Represents a node in the Abstract Syntax Tree (AST).
    Stores lexical information and logical hierarchy for the semantic and code generation phases.
    """
    def __init__(self, token):
        self.token = token
        self.left = None    # Left child (e.g., Condition, Operand 1, Variable)
        self.right = None   # Right child (e.g., True Block, Operand 2, Assigned value)
        self.center = None  # Center child (Used for Else/ElseIf blocks in an If statement)
        self.step = None    # Step child (Used EXCLUSIVELY for the increment/decrement in a FOR loop)
        self.next = None    # Next instruction (Sibling node)
        
        # --- Metadata for Intermediate Code and Virtual Machine ---
        self.line = getattr(token, 'line', 0)  # Preserves exact line for VM error reporting
        self.eval_type = None                  # Populated by Semantic.py (e.g., INT, FLOAT, ARRAY)
        self.mem_id = None                     # Memory Address ID

    def __repr__(self) -> str:
        return f"Tree_Node({self.token.type}, {self.token.value})"

    def print_tree(self, level: int = 0):
        """Recursively prints the AST structure to the console for debugging."""
        indent = "    " * level
        symbol = "| " if level > 0 else ""
        text = f"{indent}{symbol} {self.token.type}: {self.token.value}"
        
        if Env.console:
            Env.console.print(text)
        else:
            print(text)
        
        # Logical/mathematical and structural children
        if self.left: self.left.print_tree(level + 1)
        if self.center: self.center.print_tree(level + 1)
        if self.step: self.step.print_tree(level + 1)
        if self.right: self.right.print_tree(level + 1)
        
        # Next instruction (same level)
        if self.next:
            self.next.print_tree(level)

class Parser:
    """
    Syntactic Analyzer (Parser).
    Consumes tokens from the Lexer and constructs an Abstract Syntax Tree (AST) 
    based on the language's grammar rules.
    """
    def __init__(self, lexer, console=None):
        self.lexer = lexer
        self.console = console or Env.console
        self.current_token = self.lexer.next_token()
        self.last_was_block = False

    def parse(self) -> Tree_Node:
        """Entry point for parsing."""
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("[INFO] STARTING SYNTAX ANALYSIS (AST Generation)")
        return self.program()

    def program(self) -> Tree_Node:
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("SYNTAX ANALYSIS: <PROGRAM>")
        
        if self.current_token.type == Token.Type.PhpOpen:
            root = Tree_Node(self.current_token)
            self.eat(Token.Type.PhpOpen)
            root.left = self.instruction_list()
            
            if self.current_token.type == Token.Type.PhpClose:
                self.eat(Token.Type.PhpClose)
            elif self.current_token.type != Token.Type.End:
                self.report_error(2)
            return root
        else:
            self.report_error(8)
            return None

    def instruction_list(self) -> Tree_Node:
        # Base case for recursion stop
        stop_tokens = (Token.Type.PhpClose, Token.Type.End, Token.Type.RightBrace, Token.Type.Case, Token.Type.Default)
        if self.current_token.type in stop_tokens:
            return None
            
        instruction_node = self.statement()
        
        # Validate semicolon if the instruction was not a block (if, while, for, switch)
        if not self.last_was_block:
            if self.current_token.type == Token.Type.Semicolon:
                self.eat(Token.Type.Semicolon)
            else:
                self.report_error(1)
                
        if instruction_node:
            instruction_node.next = self.instruction_list()
            return instruction_node
        else:
            # If the statement returned None, try to continue parsing
            return self.instruction_list()

    def statement(self) -> Tree_Node:
        self.last_was_block = False 
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("SYNTAX ANALYSIS: <STATEMENT>")
        
        t = self.current_token.type
        
        if t == Token.Type.Variable: return self.assignment()
        elif t == Token.Type.Echo: return self.echo_statement()
        elif t == Token.Type.Read: return self.read_statement()
        elif t == Token.Type.If: return self.if_statement()
        elif t == Token.Type.While: return self.while_statement()
        elif t == Token.Type.For: return self.for_statement()
        elif t == Token.Type.Switch: return self.switch_statement()
        elif t == Token.Type.Break:
            break_node = Tree_Node(self.current_token)
            self.eat(Token.Type.Break)
            return break_node
        else:
            if t not in [Token.Type.PhpClose, Token.Type.RightBrace]:
                self.report_error(6)
            return None

    def assignment(self) -> Tree_Node:
        var_node = Tree_Node(self.current_token)
        self.eat(Token.Type.Variable)
        
        # Support for array index assignment: $arr[$i] = ...
        if self.current_token.type == Token.Type.LeftBracket:
            self.eat(Token.Type.LeftBracket)
            var_node.left = self.condition() # Save the index as the left child of the variable
            if self.current_token.type != Token.Type.RightBracket: self.report_error(16)
            self.eat(Token.Type.RightBracket)

        # Support for isolated increments/decrements: $i++; or $i--;
        if self.current_token.type in [Token.Type.Increment, Token.Type.Decrement]:
            op_node = Tree_Node(self.current_token)
            self.eat(self.current_token.type)
            op_node.left = var_node
            return op_node
        
        assign_node = Tree_Node(self.current_token)
        if self.current_token.type != Token.Type.Assignment: self.report_error(3)
        self.eat(Token.Type.Assignment)
        
        assign_node.left = var_node
        
        # Support for array declaration: $arr = array(1,2,3);
        if self.current_token.type == Token.Type.Array:
            assign_node.right = self.array_declaration()
        else:
            assign_node.right = self.condition() 
            
        return assign_node

    def array_declaration(self) -> Tree_Node:
        arr_node = Tree_Node(self.current_token)
        self.eat(Token.Type.Array)
        if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
        self.eat(Token.Type.LeftParen)
        
        arr_node.left = self.argument_list()
        
        if self.current_token.type != Token.Type.RightParen: self.report_error(4)
        self.eat(Token.Type.RightParen)
        return arr_node

    def argument_list(self) -> Tree_Node:
        if self.current_token.type == Token.Type.RightParen:
            return None # Empty array
            
        node = self.condition()
        
        if self.current_token.type == Token.Type.Comma:
            self.eat(Token.Type.Comma)
            node.next = self.argument_list()
            
        return node

    def echo_statement(self) -> Tree_Node:
        echo_node = Tree_Node(self.current_token)
        self.eat(Token.Type.Echo)
        
        # Echo now supports full expressions like variables, strings, or arrays
        echo_node.left = self.condition()
            
        return echo_node

    def read_statement(self) -> Tree_Node:
        read_node = Tree_Node(self.current_token)
        self.eat(Token.Type.Read)
        
        if self.current_token.type == Token.Type.Variable:
            read_node.left = Tree_Node(self.current_token)
            self.eat(Token.Type.Variable)
        else:
            self.report_error(5)
            
        return read_node

    def if_statement(self) -> Tree_Node:
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("SYNTAX ANALYSIS: <IF_STATEMENT>")
        if_node = Tree_Node(self.current_token)
        self.eat(Token.Type.If)
        
        if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
        self.eat(Token.Type.LeftParen)
        if_node.left = self.condition()
        if self.current_token.type != Token.Type.RightParen: self.report_error(4)
        self.eat(Token.Type.RightParen)
        
        if self.current_token.type != Token.Type.LeftBrace: self.report_error(9)
        self.eat(Token.Type.LeftBrace)
        if_node.right = self.instruction_list()
        if self.current_token.type != Token.Type.RightBrace: self.report_error(11)
        self.eat(Token.Type.RightBrace)
        
        current = if_node
        
        # Process ElseIf
        while self.current_token.type == Token.Type.ElseIf:
            if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
                self.console.print("SYNTAX ANALYSIS: <ELSEIF>")
            elseif_node = Tree_Node(self.current_token)
            self.eat(Token.Type.ElseIf)
            
            if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
            self.eat(Token.Type.LeftParen)
            elseif_node.left = self.condition()
            if self.current_token.type != Token.Type.RightParen: self.report_error(4)
            self.eat(Token.Type.RightParen)
            
            if self.current_token.type != Token.Type.LeftBrace: self.report_error(9)
            self.eat(Token.Type.LeftBrace)
            elseif_node.right = self.instruction_list()
            if self.current_token.type != Token.Type.RightBrace: self.report_error(11)
            self.eat(Token.Type.RightBrace)
            
            current.center = elseif_node
            current = elseif_node

        # Process Else
        if self.current_token.type == Token.Type.Else:
            if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
                self.console.print("SYNTAX ANALYSIS: <ELSE>")
            else_node = Tree_Node(self.current_token)
            self.eat(Token.Type.Else)
            
            if self.current_token.type != Token.Type.LeftBrace: self.report_error(9)
            self.eat(Token.Type.LeftBrace)
            else_node.right = self.instruction_list()
            if self.current_token.type != Token.Type.RightBrace: self.report_error(11)
            self.eat(Token.Type.RightBrace)
            
            current.center = else_node

        self.last_was_block = True
        return if_node

    def while_statement(self) -> Tree_Node:
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("SYNTAX ANALYSIS: <WHILE_STATEMENT>")
        while_node = Tree_Node(self.current_token)
        self.eat(Token.Type.While)
        
        if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
        self.eat(Token.Type.LeftParen)
        while_node.left = self.condition()
        if self.current_token.type != Token.Type.RightParen: self.report_error(4)
        self.eat(Token.Type.RightParen)
        
        if self.current_token.type != Token.Type.LeftBrace: self.report_error(9)
        self.eat(Token.Type.LeftBrace)
        while_node.right = self.instruction_list()
        if self.current_token.type != Token.Type.RightBrace: self.report_error(11)
        self.eat(Token.Type.RightBrace)
        
        self.last_was_block = True
        return while_node

    def for_statement(self) -> Tree_Node:
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("SYNTAX ANALYSIS: <FOR_STATEMENT>")
        for_node = Tree_Node(self.current_token)
        self.eat(Token.Type.For)
        
        if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
        self.eat(Token.Type.LeftParen)
        
        # 1. Initialization (e.g., $i = 0)
        for_node.left = self.assignment()
        if self.current_token.type != Token.Type.Semicolon: self.report_error(1)
        self.eat(Token.Type.Semicolon)
        
        # 2. Condition (e.g., $i < 10)
        for_node.center = self.condition()
        if self.current_token.type != Token.Type.Semicolon: self.report_error(1)
        self.eat(Token.Type.Semicolon)
        
        # 3. Step/Increment (e.g., $i++)
        for_node.step = self.assignment()
        
        if self.current_token.type != Token.Type.RightParen: self.report_error(4)
        self.eat(Token.Type.RightParen)
        
        # 4. Loop Body
        if self.current_token.type != Token.Type.LeftBrace: self.report_error(9)
        self.eat(Token.Type.LeftBrace)
        for_node.right = self.instruction_list()
        if self.current_token.type != Token.Type.RightBrace: self.report_error(11)
        self.eat(Token.Type.RightBrace)
        
        self.last_was_block = True
        return for_node

    def switch_statement(self) -> Tree_Node:
        if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
            self.console.print("SYNTAX ANALYSIS: <SWITCH_STATEMENT>")
        switch_node = Tree_Node(self.current_token)
        self.eat(Token.Type.Switch)
        
        if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
        self.eat(Token.Type.LeftParen)
        
        if self.current_token.type == Token.Type.Variable:
            switch_node.left = Tree_Node(self.current_token)
            self.eat(Token.Type.Variable)
        else:
            self.report_error(5)
            
        if self.current_token.type != Token.Type.RightParen: self.report_error(4)
        self.eat(Token.Type.RightParen)
        
        if self.current_token.type != Token.Type.LeftBrace: self.report_error(9)
        self.eat(Token.Type.LeftBrace)
        
        switch_node.right = self.case_list()
        
        if self.current_token.type != Token.Type.RightBrace: self.report_error(11)
        self.eat(Token.Type.RightBrace)
        
        self.last_was_block = True
        return switch_node

    def case_list(self) -> Tree_Node:
        if self.current_token.type not in [Token.Type.Case, Token.Type.Default]:
            return None
            
        case_node = Tree_Node(self.current_token)
        
        if self.current_token.type == Token.Type.Case:
            if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
                self.console.print("SYNTAX ANALYSIS: <CASE>")
            self.eat(Token.Type.Case)
            if self.current_token.type == Token.Type.Number:
                case_node.left = Tree_Node(self.current_token)
                self.eat(Token.Type.Number)
            else:
                self.report_error(7)
                
            if self.current_token.type != Token.Type.Colon: self.report_error(13)
            self.eat(Token.Type.Colon)
            case_node.right = self.instruction_list()
            
        elif self.current_token.type == Token.Type.Default:
            if hasattr(self.lexer, 'trace_exists') and self.lexer.trace_exists(): 
                self.console.print("SYNTAX ANALYSIS: <DEFAULT>")
            self.eat(Token.Type.Default)
            if self.current_token.type != Token.Type.Colon: self.report_error(13)
            self.eat(Token.Type.Colon)
            case_node.right = self.instruction_list()
            
        case_node.next = self.case_list()
        return case_node

    def condition(self) -> Tree_Node:
        left_node = self.expr()
        relational_ops = [
            Token.Type.Equality, Token.Type.Inequality, Token.Type.LessThan, 
            Token.Type.GreaterThan, Token.Type.LessOrEqual, Token.Type.GreaterOrEqual
        ]
                            
        if self.current_token.type in relational_ops:
            op_node = Tree_Node(self.current_token)
            self.eat(self.current_token.type)
            right_node = self.expr()
            op_node.left = left_node
            op_node.right = right_node
            return op_node
            
        return left_node

    def expr(self) -> Tree_Node: 
        node = self.term()
        while self.current_token.type in (Token.Type.Addition, Token.Type.Subtraction):
            token_op = self.current_token
            self.eat(token_op.type)
            new_node = Tree_Node(token_op)
            new_node.left = node
            new_node.right = self.term()
            node = new_node
        return node
    
    def term(self) -> Tree_Node: 
        node = self.factor()
        while self.current_token.type in (Token.Type.Multiplication, Token.Type.Division, Token.Type.Modulo):
            token_op = self.current_token
            self.eat(token_op.type)
            new_node = Tree_Node(token_op)
            new_node.left = node
            new_node.right = self.factor()
            node = new_node
        return node
    
    def factor(self) -> Tree_Node: 
        current = self.current_token
        
        if current.type == Token.Type.Number:
            self.eat(Token.Type.Number)
            return Tree_Node(current)

        elif current.type == Token.Type.String:
            self.eat(Token.Type.String)
            return Tree_Node(current)
            
        elif current.type == Token.Type.Variable:
            self.eat(Token.Type.Variable)
            # Support for reading array elements: $var[$i]
            if self.current_token.type == Token.Type.LeftBracket:
                self.eat(Token.Type.LeftBracket)
                idx = self.condition()
                if self.current_token.type != Token.Type.RightBracket: self.report_error(16)
                self.eat(Token.Type.RightBracket)
                n = Tree_Node(current)
                n.left = idx
                return n
            return Tree_Node(current)
            
        elif current.type == Token.Type.Count:
            self.eat(Token.Type.Count)
            count_node = Tree_Node(current)
            if self.current_token.type != Token.Type.LeftParen: self.report_error(10)
            self.eat(Token.Type.LeftParen)
            
            if self.current_token.type == Token.Type.Variable:
                count_node.left = Tree_Node(self.current_token)
                self.eat(Token.Type.Variable)
            else:
                self.report_error(5) # Expected variable inside count()
                
            if self.current_token.type != Token.Type.RightParen: self.report_error(4)
            self.eat(Token.Type.RightParen)
            return count_node
            
        elif current.type == Token.Type.LeftParen:
            self.eat(Token.Type.LeftParen)
            node = self.condition()
            if self.current_token.type != Token.Type.RightParen: self.report_error(4)
            self.eat(Token.Type.RightParen)
            return node
            
        else:
            self.report_error(6) # Unexpected factor
            return None
            
    def eat(self, token_type):
        """Consumes the expected token or raises a syntax alert."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            msg = f"Internal Syntax Error: Expected {token_type}, but got {self.current_token.type}"
            if Env.console: 
                Env.console.print_alert(msg)
            else: 
                print(msg)

    def report_error(self, code):
        """Maps specific error codes to human-readable parser alerts."""
        line = self.lexer.current_line() if hasattr(self.lexer, 'current_line') else "Unknown"
        error_messages = {
            1: " :EXPECTED A ;",
            2: " :EXPECTED A ?> AT THE END",
            3: " :EXPECTED AN =",
            4: " :EXPECTED A )",
            5: " :EXPECTED A PHP VARIABLE (EXAMPLE: $var)",
            6: " :UNKNOWN INSTRUCTION OR INVALID SYNTAX",
            7: " :EXPECTED A CONSTANT",
            8: " :EXPECTED THE <?php TAG",
            9: " :EXPECTED A {",
            10: " :EXPECTED A (",
            11: " :EXPECTED A }",
            12: " :EXPECTED A RELATIONAL OPERATOR (==, !=, <, >, <=, >=)",
            13: " :EXPECTED A : (COLON)",
            14: " :EXPECTED 'case' OR 'default'",
            15: " :BREAK OUTSIDE OF LOOP OR SWITCH",
            16: " :EXPECTED A ]"
        }
        message = error_messages.get(code, " :UNDOCUMENTED ERROR")
        self.console.print(f"LINE {line} SYNTAX ERROR {code}{message}")
        
        # THE CHANGE: Raise an exception instead of killing the app directly
        raise Exception(f"Syntax Analysis Aborted: Error {code}")