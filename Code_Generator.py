import Env
from Token import Token
from Middle_Code import Middle_Code_Generator

class Code_Generator:
    """
    Translates the Abstract Syntax Tree (AST) into intermediate code (assembly/bytecode)
    for execution in the Virtual_Machine.
    """

    def __init__(self, tree, output_file="output.asm", console=None):
        """
        Initializes the Code_Generator.

        Args:
            tree (Node): The root node of the Abstract Syntax Tree.
            output_file (str, optional): The path for the generated assembly output. Defaults to "output.asm".
            console (Console, optional): The console environment for system logging. Defaults to Env.console.
        """
        self.tree = tree
        self.console = console or Env.console
        # Instantiate the intermediate code writing utility
        self.instruction_generator = Middle_Code_Generator(output_file, self.console)

    def generate_code(self):
        """
        Starts the AST translation process to generate the virtual machine bytecode.
        
        This method triggers the traversal of the syntax tree and gracefully
        closes the file stream once the intermediate code generation is complete.
        """
        if self.console:
            self.console.print_notification("\n[INFO] STARTING INTERMEDIATE CODE GENERATION")
            
        self.visit_node(self.tree)
        
        # Finalize the program execution instructions
        self.instruction_generator.end() 
        
        if self.console:
            self.console.print_notification(f"[SUCCESS] FILE GENERATED: {self.instruction_generator.output_file}")

    def visit_node(self, node):
        """
        Recursively traverses the AST to generate stack-based virtual machine instructions.

        Args:
            node (Node): The current AST node being evaluated. Returns immediately if None.
        """
        if node is None:
            return

        token_type = node.token.type
        line = getattr(node.token, 'line', getattr(node, 'line', None))

        # --- 1. PHP OPEN TAG ---
        if token_type == Token.Type.PhpOpen:
            self.visit_node(node.left)

        # --- 2. ASSIGNMENTS ($x = 10, $a = array(), $a[$i] = 5) ---
        elif token_type == Token.Type.Assignment:
            var_node = node.left
            
            # CASE A: Creation of a new array structure ($data = array(...))
            if node.right.token.type == Token.Type.Array:
                # Step 1: Count array elements to allocate correct memory block
                element = node.right.left
                size = 0
                while element:
                    size += 1
                    element = element.next
                
                # Step 2: Allocate memory in the VM
                self.instruction_generator.alloc_array(var_node.mem_id, size, line)
                
                # Step 3: Iteratively store each element at its respective index
                element = node.right.left
                index = 0
                while element:
                    self.visit_node(element)  # PUSH the value
                    self.instruction_generator.pushc(str(index), line)  # PUSH the index
                    self.instruction_generator.store_index(var_node.mem_id, line)
                    index += 1
                    element = element.next

            # CASE B: Assignment to a specific existing array index ($data[$j] = ...)
            elif getattr(var_node, 'left', None):
                self.visit_node(node.right)  # PUSH the target value
                self.visit_node(var_node.left)  # PUSH the target index
                self.instruction_generator.store_index(var_node.mem_id, line)

            # CASE C: Standard scalar variable assignment ($n = 5)
            else:
                self.instruction_generator.pusha(var_node.mem_id, line)
                self.visit_node(node.right)
                self.instruction_generator.store(line)

        # --- 3. LITERAL VALUES ---
        elif token_type in [Token.Type.Number, Token.Type.String, Token.Type.Boolean]:
            self.instruction_generator.pushc(node.token.value, line)
            
        # --- 4. VARIABLE USAGE ---
        elif token_type == Token.Type.Variable:
            # If a left child exists, it represents an array index retrieval access ($data[$i])
            if getattr(node, 'left', None):
                self.visit_node(node.left)  # PUSH the index
                self.instruction_generator.load_index(node.mem_id, line)
            
            # Standard variable access
            else:
                self.instruction_generator.pusha(node.mem_id, line)
                self.instruction_generator.load(line)

        # --- 5. ARITHMETIC OPERATIONS ---
        elif token_type in [Token.Type.Addition, Token.Type.Subtraction, Token.Type.Multiplication, Token.Type.Division, Token.Type.Modulo]:
            self.visit_node(node.left)
            self.visit_node(node.right)
            
            if token_type == Token.Type.Addition: 
                self.instruction_generator.add(line)
            elif token_type == Token.Type.Subtraction: 
                self.instruction_generator._write("SUB", line)
            elif token_type == Token.Type.Multiplication: 
                self.instruction_generator.mul(line)
            elif token_type == Token.Type.Division: 
                self.instruction_generator.div(line)
            elif token_type == Token.Type.Modulo: 
                self.instruction_generator.mod(line)

        # --- 6. RELATIONAL COMPARISONS ---
        elif token_type in [Token.Type.Equality, Token.Type.Inequality, Token.Type.LessThan, 
                            Token.Type.GreaterThan, Token.Type.LessOrEqual, Token.Type.GreaterOrEqual]:
            self.visit_node(node.left)
            self.visit_node(node.right)
            self.instruction_generator.relational_op(node.token.value, line)

        # --- 7. CONTROL FLOW: IF STATEMENT ---
        elif token_type == Token.Type.If:
            self.visit_node(node.left)  # Evaluate boolean condition
            
            label_false = self.instruction_generator.new_label()
            label_end = self.instruction_generator.new_label()
            
            self.instruction_generator.goto_if_false(label_false, line)
            self.visit_node(node.right)  # Execution block if condition is TRUE
            self.instruction_generator.goto(label_end, line)
            
            self.instruction_generator.label(label_false, line)
            if node.center: 
                self.visit_node(node.center)  # Execution block for ELSE (if exists)
            self.instruction_generator.label(label_end, line)

        # --- 8. CONTROL FLOW: WHILE LOOP ---
        elif token_type == Token.Type.While:
            label_start = self.instruction_generator.new_label()
            label_end = self.instruction_generator.new_label()
            
            self.instruction_generator.label(label_start, line)
            self.visit_node(node.left)  # Evaluate loop condition
            self.instruction_generator.goto_if_false(label_end, line)
            
            self.visit_node(node.right)  # Loop body execution
            self.instruction_generator.goto(label_start, line)
            self.instruction_generator.label(label_end, line)

        # --- 9. UNARY OPERATIONS ($i++) ---
        elif token_type in [Token.Type.Increment, Token.Type.Decrement]:
            var_node = node.left
            self.instruction_generator.pusha(var_node.mem_id, line)
            
            # Resolve index if operating on an array element
            if getattr(var_node, 'left', None):
                self.visit_node(var_node.left)
                self.instruction_generator.add(line)
                
            self.instruction_generator._write("CLON", line) 
            self.instruction_generator.load(line)
            self.instruction_generator.pushc("1", line)
            
            if token_type == Token.Type.Increment:
                self.instruction_generator.add(line)
            else:
                self.instruction_generator._write("SUB", line)
            
            self.instruction_generator.store(line)

        # --- 10. SYSTEM I/O (ECHO) ---
        elif token_type == Token.Type.Echo:
            self.visit_node(node.left)
            self.instruction_generator.output(line)

        # --- 11. NATIVE SYSTEM FUNCTIONS (COUNT) ---
        elif token_type == Token.Type.Count:
            if node.left:
                array_mem_id = node.left.mem_id
                self.instruction_generator.count_array(array_mem_id, line)

        # Proceed to evaluate the next sibling node in the AST sequence
        self.visit_node(node.next)