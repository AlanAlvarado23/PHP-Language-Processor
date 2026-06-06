class Token:
    """
    Represents a lexical token extracted from the source code.
    Contains the token type, its literal value, and the line number for error tracking.
    """
    class Type:
        # --- Data Types and Variables ---
        Number = "Number"            # 123, 4.56
        Variable = "Variable"        # $var, $index
        String = "String"            # "Hello World", 'Text'
        Boolean = "Boolean"          # true, false
        
        # --- Arithmetic Operators ---
        Addition = "Addition"        # +
        Subtraction = "Subtraction"  # -
        Multiplication = "Multiplication" # *
        Division = "Division"        # /
        Modulo = "Modulo"            # %
        Increment = "Increment"      # ++  
        Decrement = "Decrement"      # --  
        
        # --- Relational Operators ---
        Equality = "Equality"        # ==
        Inequality = "Inequality"    # !=
        GreaterThan = "GreaterThan"  # >
        LessThan = "LessThan"        # <
        GreaterOrEqual = "GreaterOrEqual" # >=
        LessOrEqual = "LessOrEqual"  # <=
        
        # --- Assignment Operators ---
        Assignment = "Assignment"    # =
        
        # --- Logical Operators ---
        And = "And"                  # &&
        Or = "Or"                    # ||
        Not = "Not"                  # !

        # --- Grouping Symbols and Delimiters ---
        LeftParen = "LeftParen"      # (
        RightParen = "RightParen"    # )
        LeftBrace = "LeftBrace"      # {
        RightBrace = "RightBrace"    # }
        LeftBracket = "LeftBracket"  # [
        RightBracket = "RightBracket"# ]
        Semicolon = "Semicolon"      # ;
        Colon = "Colon"              # :
        Comma = "Comma"              # ,

        # --- Reserved Words (Control Structures and Types) ---
        If = "If"                    # if
        ElseIf = "ElseIf"            # elseif
        Else = "Else"                # else
        Switch = "Switch"            # switch
        Case = "Case"                # case
        Default = "Default"          # default
        Break = "Break"              # break
        While = "While"              # while
        For = "For"                  # for
        Array = "Array"              # array  
        
        # --- Built-in Functions / I/O ---
        Echo = "Echo"                # echo
        Read = "Read"                # read
        Count = "Count"              # count  
        
        # --- PHP Tags ---
        PhpOpen = "PhpOpen"          # <?php
        PhpClose = "PhpClose"        # ?>

        # --- Special ---
        End = "EOF"                  # End of File
        Invalid = "Invalid"          # Unrecognized character

        # --- Intermediate Code and Virtual Machine (NEW) ---
        Temp = "Temp"                # Compiler temporary variables (t1, t2...)
        Label = "Label"              # Jump labels for loops and conditionals (L1, L2...)
        Goto = "Goto"                # Unconditional jump
        GotoIfFalse = "GotoIfFalse"  # Conditional jump if evaluation is false
        GotoIfTrue = "GotoIfTrue"    # Conditional jump if evaluation is true

    def __init__(self, token_type, value, line=0):
        # We rename 'type' to 'token_type' to avoid shadowing the built-in python type() function
        self.type = token_type
        self.value = value
        self.line = line

    def __str__(self):
        return f"Token({self.type}, '{self.value}', line {self.line})"