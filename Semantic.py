import Env
from Token import Token

class Semantic_Analyzer:
    """
    Performs semantic analysis on the Abstract Syntax Tree (AST).
    Validates semantic rules, checks variable initialization, enforces type rules,
    and handles memory address allocation for the Virtual Machine.
    """

    def __init__(self, tree, console=None):
        """
        Initializes the Semantic_Analyzer.

        Args:
            tree (Node): The root node of the Abstract Syntax Tree.
            console (Console, optional): Console interface for system logging. Defaults to Env.console.
        """
        self.tree = tree
        self.console = console or Env.console
        # Symbol Table: var_name -> {'type': str, 'line': int, 'mem_id': int}
        self.symbol_table = {} 
        self.errors = 0
        self.mem_counter = 0  

    def analyze(self) -> bool:
        """
        Main entry point to begin semantic analysis.

        Returns:
            bool: True if the analysis completes with 0 errors, False otherwise.
        """
        if self.console: 
            self.console.print_notification("\n[INFO] STARTING SEMANTIC ANALYSIS (Rule Validation and Memory Allocation)")
            
        self.visit(self.tree)
        
        if self.errors == 0:
            if self.console: 
                self.console.print_notification("[SUCCESS] SEMANTIC ANALYSIS COMPLETED: 0 Errors. AST successfully annotated.")
            return True
        else:
            if self.console: 
                self.console.print_alert(f"[ERROR] SEMANTIC ANALYSIS HALTED: {self.errors} error(s) found.")
            return False

    def visit(self, node):
        """
        Recursively traverses the Abstract Syntax Tree (AST) to apply semantic rules.

        Args:
            node (Node): The current AST node being evaluated.
        """
        if node is None:
            return

        token_type = node.token.type
        
        # 1. Main PHP block entry
        if token_type == Token.Type.PhpOpen:
            self.visit(node.left)
            
        # 2. Control flow statements
        elif token_type in [Token.Type.If, Token.Type.While]:
            self.visit(node.left)   # Evaluate condition
            self.visit(node.right)  # Evaluate True block
            if node.center: 
                self.visit(node.center) # Evaluate Else/ElseIf block
            
        elif token_type == Token.Type.For:
            self.visit(node.left)   # Initialization (e.g., $i = 0)
            self.visit(node.center) # Condition (e.g., $i < 10)
            self.visit(node.step)   # Step increment (e.g., $i++)
            self.visit(node.right)  # Loop body
            
        # 3. Mathematical, relational, and logical operations
        elif token_type in [
            Token.Type.Addition, Token.Type.Subtraction, Token.Type.Multiplication, Token.Type.Division, Token.Type.Modulo,
            Token.Type.LessThan, Token.Type.GreaterThan, Token.Type.LessOrEqual, Token.Type.GreaterOrEqual, 
            Token.Type.Equality, Token.Type.Inequality, Token.Type.And, Token.Type.Or
        ]:
            self.verify_operation(node)
            
        # 4. Assignments and Increments/Decrements
        elif token_type == Token.Type.Assignment:
            self.verify_assignment(node)
            
        elif token_type in [Token.Type.Increment, Token.Type.Decrement]:
            self.verify_increment(node)
            
        # 5. Native functions and Output
        elif token_type == Token.Type.Echo:
            self.visit(node.left)
            
        elif token_type == Token.Type.Count:
            self.verify_count(node)
            
        # 6. Leaf nodes (Variables, Literals)
        elif token_type == Token.Type.Variable:
            self.verify_variable_exists(node)
            
        elif token_type in [Token.Type.Number, Token.Type.String, Token.Type.Boolean]:
            node.eval_type = token_type 

        # Proceed to evaluate the next sibling node in the AST sequence
        self.visit(node.next)

    # --- SEMANTIC RULES AND MEMORY MANAGEMENT ---

    def verify_assignment(self, node):
        """
        Validates assignment operations, infers types, and allocates memory
        if the variable is being initialized for the first time.

        Args:
            node (Node): The assignment node in the AST.
        """
        var_node = node.left
        var_name = var_node.token.value
        line = getattr(var_node.token, 'line', getattr(node, 'line', "N/A"))
        
        # Validate the right-hand side of the assignment first
        self.visit(node.right)
        
        # Case A: Assigning to an array index ($array[$i] = ...)
        if var_node.left is not None:
            if self.console: 
                self.console.print(f"  > Validating assignment to array index '{var_name}' (Line {line})")
            
            self.visit(var_node.left) 
            
            if var_name not in self.symbol_table:
                self.report_error(line, f"Array '{var_name}' was not initialized before assigning an index.")
            else:
                var_node.mem_id = self.symbol_table[var_name]['mem_id']
                var_node.eval_type = self.symbol_table[var_name]['type']
                
        # Case B: Standard assignment or array initialization ($var = ...)
        else:
            inferred_type = "Variable"
            if node.right and node.right.token.type == Token.Type.Array:
                inferred_type = "Array"
                
            if var_name not in self.symbol_table:
                allocated_mem = self.mem_counter
                self.mem_counter += 1
                if self.console: 
                    self.console.print(f"  > Registering: '{var_name}' (Type: {inferred_type}, MemID: {allocated_mem}) (Line {line})")
                
                self.symbol_table[var_name] = {
                    'type': inferred_type, 
                    'line': line,
                    'mem_id': allocated_mem
                }
            
            var_node.mem_id = self.symbol_table[var_name]['mem_id']
            var_node.eval_type = self.symbol_table[var_name]['type']
            
        # Propagate mem_id and eval_type to the parent assignment node (=)
        # This prevents the Code_Generator from failing during memory retrieval.
        node.mem_id = var_node.mem_id
        node.eval_type = var_node.eval_type

    def verify_variable_exists(self, node):
        """
        Checks if a variable has been properly registered in the symbol table before usage.

        Args:
            node (Node): The variable node being accessed.
        """
        var_name = node.token.value
        line = getattr(node.token, 'line', getattr(node, 'line', "N/A"))
        
        if self.console: 
            self.console.print(f"  > Verifying existence and retrieving MemID for '{var_name}' (Line {line})")
        
        if node.left:
            self.visit(node.left)
            
        if var_name not in self.symbol_table:
            self.report_error(line, f"Variable '{var_name}' used without prior initialization.")
        else:
            node.mem_id = self.symbol_table[var_name]['mem_id']
            node.eval_type = self.symbol_table[var_name]['type']

    def verify_operation(self, node):
        """
        Recursively verifies binary operations (arithmetic, relational, logical)
        and enforces numerical evaluation types.

        Args:
            node (Node): The operation node.
        """
        if self.console: 
            self.console.print(f"  > Verifying operation '{node.token.value}'")
        
        self.visit(node.left)
        self.visit(node.right)
        node.eval_type = Token.Type.Number

    def verify_increment(self, node):
        """
        Validates unary increment/decrement operations (e.g., $i++).

        Args:
            node (Node): The increment or decrement node.
        """
        var_node = node.left
        var_name = var_node.token.value
        line = getattr(var_node.token, 'line', getattr(node, 'line', "N/A"))
        
        if self.console: 
            self.console.print(f"  > Validating increment/decrement operation on '{var_name}' (Line {line})")
        
        if var_name not in self.symbol_table:
            self.report_error(line, f"Attempted to mutate uninitialized variable '{var_name}'.")
        else:
            var_node.mem_id = self.symbol_table[var_name]['mem_id']
            var_node.eval_type = self.symbol_table[var_name]['type']
            node.mem_id = var_node.mem_id

    def verify_count(self, node):
        """
        Validates the native count() function, ensuring it receives an Array type.

        Args:
            node (Node): The count function node.
        """
        if node.left:
            var_name = node.left.token.value
            line = getattr(node.left.token, 'line', getattr(node, 'line', "N/A"))
            
            if self.console: 
                self.console.print(f"  > Evaluating count() function argument: '{var_name}' (Line {line})")
            
            if var_name not in self.symbol_table:
                self.report_error(line, f"The count() function attempted to evaluate '{var_name}', but it does not exist.")
            elif self.symbol_table[var_name]['type'] != "Array":
                self.report_error(line, f"The count() function expects an Array, but '{var_name}' is of standard type.")
            else:
                node.left.mem_id = self.symbol_table[var_name]['mem_id']
                node.left.eval_type = self.symbol_table[var_name]['type']
                node.eval_type = Token.Type.Number

    def report_error(self, line, message):
        """
        Logs a semantic error, increments the error counter, and outputs to the console.

        Args:
            line (int/str): The source code line where the error occurred.
            message (str): The detailed error message.
        """
        self.errors += 1
        full_message = f"Line {line} - {message}"
        if self.console:
            self.console.print_alert(f"  [!] SEMANTIC ERROR: {full_message}")
        else:
            print(f"SEMANTIC ERROR: {full_message}")