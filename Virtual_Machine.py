import sys
import re

class Virtual_Machine:
    def __init__(self, archivo_entrada="output.asm", tamano_memoria=1000):
        self.archivo_entrada = archivo_entrada
        self.memoria = [0] * tamano_memoria  # Nuestra RAM simulada
        self.pila = []                       # La pila de ejecución
        self.instrucciones = []              # Lista de instrucciones a ejecutar
        self.etiquetas = {}                  # Diccionario para saber a qué línea saltar (ej. 'L1': 15)
        self.ip = 0                          # Instruction Pointer (Puntero de instrucción actual)
        self.corriendo = False

    def cargar_codigo(self):
        """Primera pasada: Carga el código, limpia comentarios y mapea las etiquetas."""
        try:
            with open(self.archivo_entrada, 'r') as f:
                lineas = f.readlines()
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.archivo_entrada}")
            sys.exit(1)

        indice_instruccion = 0
        for linea in lineas:
            # Quitamos los comentarios (todo lo que esté después de ';')
            linea_limpia = linea.split(';')[0].strip()
            
            if not linea_limpia:
                continue # Saltamos líneas vacías

            partes = linea_limpia.split(' ')
            operacion = partes[0].upper()

            # Si es una etiqueta, guardamos a qué instrucción apunta y NO la agregamos a la lista
            if operacion == "LABEL":
                nombre_etiqueta = partes[1]
                self.etiquetas[nombre_etiqueta] = indice_instruccion
            else:
                self.instrucciones.append(partes)
                indice_instruccion += 1

    def _convertir_valor(self, valor_str):
        """Intenta convertir un string a int, luego a float, o lo deja como string."""
        if valor_str.startswith('"') and valor_str.endswith('"'):
            return valor_str[1:-1] # Es una cadena, le quitamos las comillas
        if valor_str.startswith("'") and valor_str.endswith("'"):
            return valor_str[1:-1]

        try:
            return int(valor_str)
        except ValueError:
            try:
                return float(valor_str)
            except ValueError:
                # Si es 'true' o 'false'
                if valor_str.lower() == 'true': return 1
                if valor_str.lower() == 'false': return 0
                return valor_str

    def ejecutar(self):
        """Segunda pasada: Ejecuta el código cargado en memoria."""
        self.cargar_codigo()
        self.corriendo = True
        self.ip = 0
        
        print("\n--- INICIO DE EJECUCIÓN (MÁQUINA VIRTUAL) ---\n")

        while self.corriendo and self.ip < len(self.instrucciones):
            instruccion = self.instrucciones[self.ip]
            op = instruccion[0]

            try:
                # --- MEMORIA Y PILA ---
                if op == "PUSHC":
                    valor = self._convertir_valor(instruccion[1])
                    self.pila.append(valor)
                    
                elif op == "PUSHA":
                    direccion = int(instruccion[1])
                    self.pila.append(direccion)
                    
                elif op == "LOAD":
                    direccion = self.pila.pop()
                    self.pila.append(self.memoria[direccion])
                    
                elif op == "STORE":
                    valor = self.pila.pop()
                    direccion = self.pila.pop()
                    self.memoria[direccion] = valor
                    
                elif op == "CLON":
                    tope = self.pila[-1]
                    self.pila.append(tope)

                # --- ARITMÉTICA ---
                elif op in ["ADD", "SUB", "MUL", "DIV", "MOD"]:
                    b = self.pila.pop()
                    a = self.pila.pop()
                    
                    if op == "ADD": self.pila.append(a + b)
                    elif op == "SUB": self.pila.append(a - b)
                    elif op == "MUL": self.pila.append(a * b)
                    elif op == "DIV": 
                        if b == 0: raise ZeroDivisionError("División por cero en la VM")
                        self.pila.append(a / b)
                    elif op == "MOD": self.pila.append(a % b)

                # --- RELACIONALES ---
                elif op in ["EQ", "NEQ", "LES", "GTR", "LEQ", "GEQ"]:
                    b = self.pila.pop()
                    a = self.pila.pop()
                    
                    if op == "EQ": self.pila.append(1 if a == b else 0)
                    elif op == "NEQ": self.pila.append(1 if a != b else 0)
                    elif op == "LES": self.pila.append(1 if a < b else 0)
                    elif op == "GTR": self.pila.append(1 if a > b else 0)
                    elif op == "LEQ": self.pila.append(1 if a <= b else 0)
                    elif op == "GEQ": self.pila.append(1 if a >= b else 0)

                # --- CONTROL DE FLUJO ---
                elif op == "GOTO":
                    etiqueta = instruccion[1]
                    self.ip = self.etiquetas[etiqueta]
                    continue # Saltamos el autoincremento del IP
                    
                elif op == "GOTO_IF_FALSE":
                    etiqueta = instruccion[1]
                    condicion = self.pila.pop()
                    # En la VM, un 0, False o string vacío es falso
                    if not condicion:
                        self.ip = self.etiquetas[etiqueta]
                        continue

                # --- ENTRADA / SALIDA ---
                elif op == "OUT":
                    valor = self.pila.pop()
                    print(valor)
                    
                elif op == "IN":
                    direccion = int(instruccion[1])
                    entrada = input(f"Entrada requerida (Mem {direccion}): ")
                    self.memoria[direccion] = self._convertir_valor(entrada)

                # --- CONTROL DEL SISTEMA ---
                elif op == "HALT":
                    self.corriendo = False
                    break
                    
                else:
                    print(f"Instrucción desconocida: {op} en la línea {self.ip}")
                    self.corriendo = False

            except IndexError:
                print(f"\n[!] ERROR FATAL VM: Intento de POP en pila vacía (Stack Underflow) en IP {self.ip} ({op})")
                self.corriendo = False
            except Exception as e:
                print(f"\n[!] ERROR FATAL VM: {str(e)} en IP {self.ip} ({op})")
                self.corriendo = False

            # Pasamos a la siguiente instrucción
            self.ip += 1

        print("\n--- FIN DE EJECUCIÓN ---")