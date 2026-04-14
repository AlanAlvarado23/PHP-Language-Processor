class Token:
    class Type:
        # --- Tipos de Datos y Variables ---
        Numero = "Numero"            # 123, 4.56
        Variable = "Variable"        # $var, $indice
        Cadena = "Cadena"            # "Hola Mundo", 'Texto'
        Booleano = "Booleano"        # true, false
        
        # --- Operadores Aritméticos ---
        Suma = "Suma"                # +
        Resta = "Resta"              # -
        Multiplica = "Multiplica"    # *
        Divide = "Divide"            # /
        Modulo = "Modulo"            # %
        Incremento = "Incremento"    # ++  
        Decremento = "Decremento"    # --  
        
        # --- Operadores Relacionales ---
        Igualdad = "Igualdad"        # ==
        Desigualdad = "Diferente"   # !=
        MayorQue = "MayorQue"        # >
        MenorQue = "MenorQue"        # <
        MayorIgual = "MayorIgual"    # >=
        MenorIgual = "MenorIgual"    # <=
        
        # --- Operadores de Asignación ---
        Asignacion = "Asignacion"    # =
        
        # --- Operadores Lógicos ---
        And = "And"                  # &&
        Or = "Or"                    # ||
        Not = "Not"                  # !

        # --- Símbolos de Agrupación y Delimitadores ---
        ParIzq = "ParIzq"            # (
        ParDer = "ParDer"            # )
        LlaveIzq = "LlaveIzq"        # {
        LlaveDer = "LlaveDer"        # }
        CorcheteIzq = "CorcheteIzq"  # [
        CorcheteDer = "CorcheteDer"  # ]
        PuntoComa = "PuntoComa"      # ;
        DosPuntos = "DosPuntos"      # :
        Coma = "Coma"                # ,

        # --- Palabras Reservadas (Estructuras de Control y Tipos) ---
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
        
        # --- Funciones Integradas / I/O ---
        Echo = "Echo"                # echo
        Read = "Read"                # read
        Count = "Count"              # count  
        
        # --- Etiquetas PHP ---
        PhpOpen = "PhpOpen"          # <?php
        PhpClose = "PhpClose"        # ?>

        # --- Especiales ---
        Fin = "EOF"                  # Fin de archivo
        Invalido = "Invalido"        # Cualquier caracter no reconocido

        # --- Código Intermedio y Máquina Virtual (NUEVOS) ---
        Temp = "Temp"                # Variables temporales del compilador (t1, t2...)
        Label = "Label"              # Etiquetas de salto para ciclos y condicionales (L1, L2...)
        Goto = "Goto"                # Salto incondicional
        GotoIfFalse = "GotoIfFalse"  # Salto condicional si la evaluación es falsa
        GotoIfTrue = "GotoIfTrue"    # Salto condicional si la evaluación es verdadera

    def __init__(self, type, value, line=0):
        self.type = type
        self.value = value
        self.line = line

    def __str__(self):
        return f"Token({self.type}, '{self.value}', linea {self.line})"