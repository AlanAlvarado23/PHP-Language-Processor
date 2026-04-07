import os

class GeneraCodigo:
    def __init__(self, archivo_salida: str, console):
        self.archivo_salida = archivo_salida
        self.console = console
        self.contador_etiquetas = 0
        
        # Vaciamos el archivo si ya existe para empezar limpio
        with open(self.archivo_salida, 'w') as f:
            f.write("")

    def _escribir(self, instruccion: str):
        """Método interno para escribir la instrucción en el archivo y opcionalmente mostrarla."""
        with open(self.archivo_salida, 'a') as f:
            f.write(instruccion + "\n")
        # Descomenta la siguiente línea si quieres ver el código generado en la consola en tiempo real
        # self.console.print(f"[dim]{instruccion}[/dim]")

    def nueva_etiqueta(self) -> str:
        """Genera un nombre de etiqueta único (ej. L1, L2, L3)."""
        self.contador_etiquetas += 1
        return f"L{self.contador_etiquetas}"

    def label(self, etiqueta: str):
        self._escribir(f"{etiqueta}:")

    def code(self):
        # Opcional: Instrucción inicial si tu máquina virtual lo requiere
        pass

    def end(self):
        self._escribir("HALT")

    # --- Operaciones de Memoria y Pila ---
    def pusha(self, variable: str):
        self._escribir(f"PUSHA {variable}")

    def pushc(self, constante: str):
        self._escribir(f"PUSHC {constante}")

    def load(self):
        self._escribir("LOAD")

    def store(self):
        self._escribir("STORE")

    # --- Operaciones Aritméticas ---
    def add(self):
        self._escribir("ADD")

    def neg(self):
        self._escribir("NEG")

    def mul(self):
        self._escribir("MUL")

    def div(self):
        self._escribir("DIV")

    def mod(self):
        self._escribir("MOD")

    # --- Saltos y Control de Flujo ---
    def jmp(self, etiqueta: str):
        self._escribir(f"JMP {etiqueta}")

    def jmpf(self, etiqueta: str):
        self._escribir(f"JMPF {etiqueta}")

    # --- Operaciones Relacionales ---
    def op_relacional(self, operador: str):
        if operador == '==':
            self._escribir("EQ")
        elif operador == '!=':
            self._escribir("NEQ")
        elif operador == '<':
            self._escribir("LES")
        elif operador == '>':
            self._escribir("GTR")
        elif operador == '<=':
            self._escribir("LEQ")
        elif operador == '>=':
            self._escribir("GEQ")

    # --- Entrada / Salida ---
    def input(self, variable: str):
        # Dependiendo de tu máquina virtual, IN puede recibir la variable directo o usar la pila
        self._escribir(f"IN {variable}")

    def output(self, variable: str):
        # Opcionalmente puedes cargar el valor y hacer un print genérico
        # PUSHA var -> LOAD -> OUT
        self._escribir(f"OUT {variable}")