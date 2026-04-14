import os

class GeneraCodigo:
    def __init__(self, archivo_salida: str, console):
        self.archivo_salida = archivo_salida
        self.console = console
        self.contador_etiquetas = 0
        self.contador_temporales = 0  # Agregado para soportar los tokens "Temp"
        
        # Vaciamos el archivo si ya existe para empezar limpio
        with open(self.archivo_salida, 'w') as f:
            f.write("")

    def _escribir(self, instruccion: str, linea_origen: int = None):
        """Escribe la instrucción en el archivo. Opcionalmente añade la línea origen como comentario para la VM."""
        # Si se pasa la línea, la agregamos como un comentario de ensamblador (traza)
        comentario = f" \t; [Línea PHP: {linea_origen}]" if linea_origen else ""
        linea_completa = f"{instruccion}{comentario}"
        
        with open(self.archivo_salida, 'a') as f:
            f.write(linea_completa + "\n")
            
        # Descomenta la siguiente línea si quieres ver el código generado en la consola en tiempo real
        # self.console.print(f"[dim]{linea_completa}[/dim]")

    def nueva_etiqueta(self) -> str:
        """Genera un nombre de etiqueta único (ej. L1, L2, L3)."""
        self.contador_etiquetas += 1
        return f"L{self.contador_etiquetas}"
        
    def nuevo_temporal(self) -> str:
        """Genera una variable temporal única (ej. T1, T2) para cálculos complejos."""
        self.contador_temporales += 1
        return f"T{self.contador_temporales}"

    def label(self, etiqueta: str, linea: int = None):
        # Usamos la palabra reservada LABEL para coincidir con tu token sintético
        self._escribir(f"LABEL {etiqueta}", linea)

    def code(self):
        # Opcional: Instrucción inicial si tu máquina virtual lo requiere
        pass

    def end(self):
        self._escribir("HALT")

    # --- Operaciones de Memoria y Pila ---
    def pusha(self, mem_id: int, linea: int = None):
        # Ahora empuja direcciones de memoria en lugar de nombres de texto
        self._escribir(f"PUSHA {mem_id}", linea)

    def pushc(self, constante: str, linea: int = None):
        self._escribir(f"PUSHC {constante}", linea)

    def load(self, linea: int = None):
        self._escribir("LOAD", linea)

    def store(self, linea: int = None):
        self._escribir("STORE", linea)

    # --- Operaciones Aritméticas ---
    def add(self, linea: int = None): self._escribir("ADD", linea)
    def neg(self, linea: int = None): self._escribir("NEG", linea)
    def mul(self, linea: int = None): self._escribir("MUL", linea)
    def div(self, linea: int = None): self._escribir("DIV", linea)
    def mod(self, linea: int = None): self._escribir("MOD", linea)

    # --- Saltos y Control de Flujo (Ajustados a los tokens sintéticos) ---
    def goto(self, etiqueta: str, linea: int = None):
        self._escribir(f"GOTO {etiqueta}", linea)

    def goto_if_false(self, etiqueta: str, linea: int = None):
        self._escribir(f"GOTO_IF_FALSE {etiqueta}", linea)

    # --- Operaciones Relacionales ---
    def op_relacional(self, operador: str, linea: int = None):
        ops = {
            '==': 'EQ', '!=': 'NEQ', '<': 'LES', 
            '>': 'GTR', '<=': 'LEQ', '>=': 'GEQ'
        }
        if operador in ops:
            self._escribir(ops[operador], linea)

    # --- Entrada / Salida ---
    def input(self, mem_id: int, linea: int = None):
        # Modificado para trabajar con ID de memoria
        self._escribir(f"IN {mem_id}", linea)

    def output(self, linea: int = None):
        # Ahora OUT no recibe parámetros, asume que el valor a imprimir ya se hizo LOAD en la pila tope
        # PUSHA mem_id -> LOAD -> OUT
        self._escribir("OUT", linea)