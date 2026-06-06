import sys
import Env

class Virtual_Machine:
    """
    Stack-based Virtual Machine for executing generated Assembly/Bytecode.
    """
    def __init__(self, input_file="Output/output.asm", memory_size=1000):
        self.console = Env.console
        self.input_file = input_file
        self.memory = [0] * memory_size      # Simulated RAM
        self.stack = []                      # Execution stack
        self.instructions = []               # List of parsed instructions
        self.labels = {}                     # Label resolution map (e.g., 'L1': 15)
        self.ip = 0                          # Instruction Pointer
        self.is_running = False

    def load_code(self):
        """First pass: Loads code, strips comments, and maps label addresses."""
        try:
            with open(self.input_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            self.console.print(f"Error: Could not find file {self.input_file}")
            sys.exit(1)

        instruction_index = 0
        for line in lines:
            # Strip comments (everything after ';') and whitespace
            clean_line = line.split(';')[0].strip()
            
            if not clean_line:
                continue  # Skip empty lines

            parts = clean_line.split(' ')
            operation = parts[0].upper()

            # Map labels to the current instruction index without adding them to the instruction list
            if operation == "LABEL":
                label_name = parts[1]
                self.labels[label_name] = instruction_index
            else:
                self.instructions.append(parts)
                instruction_index += 1

    def _convert_value(self, val_str):
        """Attempts to parse a string into an int, float, boolean, or leaves it as a string."""
        if (val_str.startswith('"') and val_str.endswith('"')) or \
           (val_str.startswith("'") and val_str.endswith("'")):
            return val_str[1:-1]

        try:
            return int(val_str)
        except ValueError:
            try:
                return float(val_str)
            except ValueError:
                lower_val = val_str.lower()
                if lower_val == 'true': return 1
                if lower_val == 'false': return 0
                return val_str

    def execute(self, debug=True):
        """Second pass: Executes the loaded instructions."""
        self.load_code()
        self.is_running = True
        self.ip = 0
        
        self.console.print("- " * 25 + "\n")
        self.console.print("   VM EXECUTION STARTED\n")
        self.console.print("- " * 25 + "\n")

        while self.is_running and self.ip < len(self.instructions):
            instruction = self.instructions[self.ip]
            op = instruction[0]

            # --- EXECUTION TRACE ---
            if debug:
                str_inst = " ".join(instruction)
                self.console.print(f"[IP: {self.ip:03d}] Cmd: {str_inst:<18} | Stack: {self.stack}")

            try:
                match op:
                    # --- MEMORY AND STACK ---
                    case "PUSHC":
                        val = self._convert_value(instruction[1])
                        self.stack.append(val)
                    case "PUSHA":
                        addr = int(instruction[1])
                        self.stack.append(addr)
                    case "LOAD":
                        addr = self.stack.pop()
                        self.stack.append(self.memory[addr])
                    case "STORE":
                        val = self.stack.pop()
                        addr = self.stack.pop()
                        self.memory[addr] = val
                    case "CLON":
                        self.stack.append(self.stack[-1])

                    # --- ARRAYS ---
                    case "ALLOC_ARRAY":
                        mem_id = int(instruction[1])
                        size = int(instruction[2])
                        self.memory[mem_id] = [0] * size
                    case "STORE_INDEX":
                        mem_id = int(instruction[1])
                        index = int(self.stack.pop())
                        val = self.stack.pop()
                        self.memory[mem_id][index] = val
                    case "LOAD_INDEX":
                        mem_id = int(instruction[1])
                        index = int(self.stack.pop())
                        self.stack.append(self.memory[mem_id][index])
                    case "COUNT_ARRAY":
                        mem_id = int(instruction[1])
                        self.stack.append(len(self.memory[mem_id]))

                    # --- ARITHMETIC ---
                    case "ADD" | "SUB" | "MUL" | "DIV" | "MOD":
                        b = self.stack.pop()
                        a = self.stack.pop()
                        if op == "ADD": self.stack.append(a + b)
                        elif op == "SUB": self.stack.append(a - b)
                        elif op == "MUL": self.stack.append(a * b)
                        elif op == "DIV": 
                            if b == 0: raise ZeroDivisionError("VM Zero Division Error")
                            self.stack.append(a / b)
                        elif op == "MOD": self.stack.append(a % b)

                    # --- RELATIONAL ---
                    case "EQ" | "NEQ" | "LES" | "GTR" | "LEQ" | "GEQ":
                        b = self.stack.pop()
                        a = self.stack.pop()
                        if op == "EQ": self.stack.append(1 if a == b else 0)
                        elif op == "NEQ": self.stack.append(1 if a != b else 0)
                        elif op == "LES": self.stack.append(1 if a < b else 0)
                        elif op == "GTR": self.stack.append(1 if a > b else 0)
                        elif op == "LEQ": self.stack.append(1 if a <= b else 0)
                        elif op == "GEQ": self.stack.append(1 if a >= b else 0)

                    # --- CONTROL FLOW ---
                    case "GOTO":
                        label = instruction[1]
                        self.ip = self.labels[label]
                        if debug: self.console.print(f"         >>> Jumping to {label} (Line {self.ip})")
                        continue  # Skip the IP auto-increment
                    
                    case "GOTO_IF_FALSE":
                        label = instruction[1]
                        condition = self.stack.pop()
                        # In this VM: 0, False, or empty string evaluates to false
                        if not condition:
                            self.ip = self.labels[label]
                            if debug: self.console.print(f"         >>> Cond FALSE: Jumping to {label} (Line {self.ip})")
                            continue
                        else:
                            if debug: self.console.print("         >>> Cond TRUE: No jump.")

                    # --- I/O ---
                    case "OUT":
                        val = self.stack.pop()
                        if debug:
                            self.console.print(f"\n[STDOUT] >>> {val}\n")
                        else:
                            self.console.print(val)
                    case "IN":
                        addr = int(instruction[1])
                        user_input = input(f"Input required (Mem {addr}): ")
                        self.memory[addr] = self._convert_value(user_input)

                    # --- SYSTEM CONTROL ---
                    case "HALT":
                        self.is_running = False
                        if debug: self.console.print(f"[IP: {self.ip:03d}] Cmd: HALT              | Halting machine...")
                        break
                    
                    case _:
                        self.console.print(f"\n[!] Unknown instruction: {op} at line {self.ip}")
                        self.is_running = False

            except IndexError:
                self.console.print(f"\n[!] FATAL VM ERROR: Stack Underflow at IP {self.ip} ({op})")
                self.console.print(f"Stack state before error: {self.stack}")
                self.is_running = False
            except Exception as e:
                self.console.print(f"\n[!] FATAL VM ERROR: {str(e)} at IP {self.ip} ({op})")
                self.is_running = False

            # Auto-increment Instruction Pointer
            self.ip += 1

        self.console.print("\n" + "=" * 50)
        self.console.print("   VM EXECUTION FINISHED")
        self.console.print("=" * 50 + "\n")