import os

class Middle_Code_Generator:
    """
    Handles the generation and formatting of intermediate bytecode/assembly instructions.
    Outputs the instructions to a specified text file for later execution by the Virtual Machine.
    """

    def __init__(self, output_file: str, console):
        """
        Initializes the Middle_Code_Generator.

        Args:
            output_file (str): The path to the file where the generated assembly will be saved.
            console (Console): The console interface for outputting system logs.
        """
        self.output_file = output_file
        self.console = console
        self.label_counter = 0
        self.temp_counter = 0  # Added to support "Temp" synthetic tokens

        # Empty the file if it already exists to start with a clean slate
        with open(self.output_file, 'w') as f:
            f.write("")

    def _write(self, instruction: str, source_line: int = None):
        """
        Writes an instruction to the output file. Optionally appends the source PHP line as a comment.

        Args:
            instruction (str): The assembly instruction to write.
            source_line (int, optional): The original line number from the source code for traceability.
        """
        # If the line number is provided, append it as an assembly comment
        comment = f" \t; [PHP Line: {source_line}]" if source_line else ""
        full_line = f"{instruction}{comment}"
        
        with open(self.output_file, 'a') as f:
            f.write(full_line + "\n")
            
        # Uncomment the following line if you want to see the generated code in the console in real-time
        # self.console.print(f"[dim]{full_line}[/dim]")

    def new_label(self) -> str:
        """
        Generates a unique label identifier for control flow operations.

        Returns:
            str: A uniquely generated label string (e.g., L1, L2, L3).
        """
        self.label_counter += 1
        return f"L{self.label_counter}"

    def new_temp(self) -> str:
        """
        Generates a unique temporary variable identifier for complex calculations.

        Returns:
            str: A uniquely generated temporary variable string (e.g., T1, T2).
        """
        self.temp_counter += 1
        return f"T{self.temp_counter}"

    def label(self, label_name: str, line: int = None):
        """
        Writes a label definition instruction to the intermediate code.

        Args:
            label_name (str): The generated name of the label.
            line (int, optional): The original source line number.
        """
        # Using the reserved word LABEL to match the synthetic token structure
        self._write(f"LABEL {label_name}", line)

    def code(self):
        """
        Optional hook for an initial setup instruction if the Virtual Machine requires a starting block.
        """
        pass

    def end(self):
        """
        Writes the HALT instruction to signify the end of the program execution gracefully.
        """
        self._write("HALT")

    # --- Memory and Stack Operations ---
    
    def pusha(self, mem_id: int, line: int = None):
        """Pushes a memory address onto the stack."""
        # Now pushes absolute memory addresses instead of textual variable names
        self._write(f"PUSHA {mem_id}", line)

    def pushc(self, constant: str, line: int = None):
        """Pushes a literal constant value onto the stack."""
        self._write(f"PUSHC {constant}", line)

    def load(self, line: int = None):
        """Loads the value from the memory address currently at the top of the stack."""
        self._write("LOAD", line)

    def store(self, line: int = None):
        """Stores a value into the memory address specified on the stack."""
        self._write("STORE", line)

    # --- Arithmetic Operations ---
    
    def add(self, line: int = None): self._write("ADD", line)
    def neg(self, line: int = None): self._write("NEG", line)
    def mul(self, line: int = None): self._write("MUL", line)
    def div(self, line: int = None): self._write("DIV", line)
    def mod(self, line: int = None): self._write("MOD", line)

    # --- Control Flow and Jumps ---
    
    def goto(self, label_name: str, line: int = None):
        """Performs an unconditional jump to a specific label."""
        self._write(f"GOTO {label_name}", line)

    def goto_if_false(self, label_name: str, line: int = None):
        """Performs a conditional jump to a specific label if the top of the stack evaluates to false."""
        self._write(f"GOTO_IF_FALSE {label_name}", line)

    # --- Relational Operations ---
    
    def relational_op(self, operator: str, line: int = None):
        """
        Translates a logical or relational operator into its corresponding Virtual Machine instruction.

        Args:
            operator (str): The source code operator (e.g., '==', '!=').
            line (int, optional): The original source line number.
        """
        ops = {
            '==': 'EQ', '!=': 'NEQ', '<': 'LES',
            '>': 'GTR', '<=': 'LEQ', '>=': 'GEQ'
        }
        if operator in ops:
            self._write(ops[operator], line)

    # --- System Input / Output ---
    
    def input(self, mem_id: int, line: int = None):
        """Prompts the system for input and maps it to a specific memory ID."""
        self._write(f"IN {mem_id}", line)

    def output(self, line: int = None):
        """Outputs the evaluated value currently at the top of the stack to standard output."""
        self._write("OUT", line)

    # --- Array (Data Structure) Operations ---
    
    def alloc_array(self, mem_id: int, size: int, line: int = None):
        """Allocates a contiguous block of memory for an array structure."""
        self._write(f"ALLOC_ARRAY {mem_id} {size}", line)

    def store_index(self, mem_id: int, line: int = None):
        """Stores a stack value at a dynamically resolved index within an allocated array."""
        self._write(f"STORE_INDEX {mem_id}", line)

    def load_index(self, mem_id: int, line: int = None):
        """Retrieves a value from a dynamically resolved index within an allocated array."""
        self._write(f"LOAD_INDEX {mem_id}", line)

    def count_array(self, mem_id: int, line: int = None):
        """Pushes the total element count (size) of a given array onto the stack."""
        self._write(f"COUNT_ARRAY {mem_id}", line)