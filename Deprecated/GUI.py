from tkinter import *
from tkinter import filedialog
import os


class GUI:

    def __init__(self):
        self.window_size = "700x400"
        self.title = "PHP Compiler"

        self.file_path = None
        self.file_name = None

        self.root = Tk()
        
        self.pw = PanedWindow(self.root, orient="vertical", sashwidth=5, bg="gray")
        self.pw.pack(fill="both", expand=True)
        self.top_frame = Frame(self.pw)
        self.bottom_frame = Frame(self.pw)
        self.pw.add(self.top_frame, height=250)
        self.pw.add(self.bottom_frame)

        self.font_style = ('consolas', 12)

        self.object = "salida.obj" 


# - - - - - - - - - - - - - - - - - - - - Menus - - - - - - - - - - - - - - - - - - - -

        self.menu_bar = Menu(self.root)

        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Abrir", command = self.open_file, accelerator="Ctrl+O")
        self.menu_file.add_command(label="Guardar", command = self.save_file, accelerator="Ctrl+S")
        self.menu_file.add_command(label="Guardar Como", command = self.save_file_as, accelerator="Ctrl+Shift+S")
        self.menu_bar.add_cascade(label="Archivo", menu=self.menu_file)

        self.menu_edit = Menu(self.menu_bar, tearoff=0)
        self.menu_edit.add_command(label="Copiar")
        self.menu_edit.add_command(label="Pegar")
        self.menu_edit.add_command(label="Cortar")
        self.menu_bar.add_cascade(label="Editar", menu=self.menu_edit)

        self.menu_find = Menu(self.menu_bar, tearoff=0)
        self.menu_find.add_command(label="Buscar")
        self.menu_find.add_command(label="Reemplazar")
        self.menu_bar.add_cascade(label="Buscar", menu=self.menu_find)

        self.menu_run = Menu(self.menu_bar, tearoff=0)
        self.menu_run.add_command(label="Correr parseo", command=self.parse, accelerator="Ctrl+P")
        self.menu_run.add_command(label="Analisis sintatico", command=self.syntax, accelerator="Ctrl+L")
        self.menu_bar.add_cascade(label="Ejecutar", menu=self.menu_run)



# - - - - - - - - - - - - - - - - - - - - Interface - - - - - - - - - - - - - - - - - - - -

        self.line_numbers = Text(self.top_frame, width=4, padx=4, takefocus=0, border=0,
                                 bg='#191919', fg='#FFFFFF', font=self.font_style, state='disabled')

        self.code_text = Text(self.top_frame, bg='#000020', fg='white', font=self.font_style, 
                              width=95, height=50, insertbackground='white')

        self.scrollbar_code = Scrollbar(self.top_frame, orient="vertical", command=self.sync_scroll_bar_code)
        
        self.code_text.config(yscrollcommand=self.update_scroll_views)
        self.line_numbers.config(yscrollcommand=self.update_scroll_views)

        self.label_salida = Label(self.bottom_frame, text='Salida:', bg='white', fg='black', font=('Arial', 10))
        self.console = Console(self.bottom_frame)

# - - - - - - - - - - - - - - - - - - - - Key Bindings - - - - - - - - - - - - - - - - - - - -

        self.code_text.bind('<KeyRelease>', self.update_line_numbers)
        self.code_text.bind('<MouseWheel>', self.update_line_numbers)
        self.code_text.bind('<Button-4>', self.update_line_numbers)
        self.code_text.bind('<Button-5>', self.update_line_numbers)

        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-S>', self.save_file_as)

        self.root.bind('<Control-p>', self.parse)
        self.root.bind('<Control-l>', self.syntax)

    def render(self):
        self.root.geometry(self.window_size)
        self.root.title(self.title)

        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_rowconfigure(0, weight=1)

        self.line_numbers.grid(row=0, column=0, sticky='ns')
        self.code_text.grid(row=0, column=1, sticky='nsew')
        self.scrollbar_code.grid(row=0, column=2, sticky='ns')

        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)
        
        self.label_salida.grid(row=0, column=0, sticky='w')

        self.console.create()
        

        self.root.config(menu=self.menu_bar)
        
        self.update_line_numbers()

        self.root.mainloop()

# - - - - - - - - - - - - - - - - Utils - - - - - - - - - - - - - - - -

    def update_scroll_views(self, *args):
        self.scrollbar_code.set(*args)
        self.line_numbers.yview_moveto(args[0])
        self.code_text.yview_moveto(args[0])

    def sync_scroll_bar_code(self, *args):
        """Comando que ejecuta la barra de desplazamiento física"""
        self.line_numbers.yview(*args)
        self.code_text.yview(*args)

    def update_line_numbers(self, event=None):
        """Calcula las líneas y redibuja los números"""
        lineas_totales = int(self.code_text.index('end-1c').split('.')[0])
        numeros_str = "\n".join(str(i) for i in range(1, lineas_totales + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', END)
        self.line_numbers.insert('1.0', numeros_str)
        self.line_numbers.config(state='disabled')
        
        self.line_numbers.yview_moveto(self.code_text.yview()[0])

# - - - - - - - - - - - - - - - - Menus - - - - - - - - - - - - - - - -
    def open_file(self, event=None):
        ruta_archivo = filedialog.askopenfilename(
            title="Abrir archivo",
            defaultextension=".",
            filetypes=[("Archivos PHP", "*.php"), ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if ruta_archivo:
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                    contenido = archivo.read()

                self.console.del_line()
                
                self.code_text.insert('1.0',contenido)
                
                self.update_line_numbers()
                
                self.file_path = ruta_archivo
                self.file_name = os.path.basename(ruta_archivo)
                self.root.title(f"{self.title} - {ruta_archivo}")
                self.console.print(f'- - - - - - - - Archivo abierto: {self.file_name} - - - - - - - -\n')
                
            except Exception as e:
                self.console.print(f"Error al abrir el archivo: {e}\n")

    def save_file_as(self, event=None):
        path = filedialog.asksaveasfilename(
            title="Guardar archivo como",
            defaultextension=".php",
            filetypes=[("Archivos PHP", "*.php"), ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if path:
            self.file_path = path # Actualizamos el archivo actual
            try:
                content = self.code_text.get('1.0', 'end-1c')
                
                # Escribimos el contenido en el archivo
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                # Actualizamos el título de la ventana
                self.file_name = os.path.basename(self.file_path)
                self.root.title(f"{self.title} - {self.file_name}")
                
                # Avisamos en la consola
                self.console.print(f"- - - - - - - - - - - - Archivo guardado: {self.file_name} - - - - - - - - - - - -\n")
                
            except Exception as e:
                self.console.print(f"Error al guardar el archivo: {e}\n")

    def save_file(self, event=None):
        # Si ya hay un archivo abierto, lo sobrescribimos
        if self.file_path:
            try:
                content = self.code_text.get('1.0', 'end-1c')
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.file_name = os.path.basename(self.file_path)
                self.console.print(f"- - - - - - - - - - - - Cambios guardados en {self.file_name} - - - - - - - - - - - -\n")
            except Exception as e:
                self.console.print(f"Error al guardar: {e}\n")
        else:
            # Si no hay ningún archivo abierto, actuamos como "Guardar como"
            self.save_file_as()


    def parse (self, event=None):
        pass
"""        self.console.print(f"- - - - - - - - Ejecutando: {self.file_name} - - - - - - - -")

        if self.file_name == None:
            self.console.print_alert("- - - - Error de ejecución - - - -")
            self.console.print_alert("No hay archivo abierto")
            self.console.print_alert("- - - - - - - - - - - - - - - - - - - - - - - - -")

        else:
            content = self.code_text.get('1.0', 'end-1c')
        
            lexer = Lexer(content.strip())
            parser = Parser(lexer)
            result = parser.parse()
            result.print_tree(self.console)"""

    def syntax (self, event=None):
        pass
        """
        self.console.print(f"- - - - - - - - Ejecutando: {self.file_name} - - - - - - - -")

        if self.file_name == None:
            self.console.print_alert("- - - - Error de ejecución - - - -")
            self.console.print_alert("No hay archivo abierto")
            self.console.print_alert("- - - - - - - - - - - - - - - - - - - - - - - - -")

        else:
            content = self.code_text.get('1.0', 'end-1c')

            traza = 1
        
            lexico_demo = sw.Lexico(content, traza, self.console)
    
            self.console.print("CLASIFICACION LEXICA")
            self.console.print(f"{'TOKEN':<15} | {'CATEGORIA':<20} | {'LINEA'}")
            self.console.print("-" * 45)
            for token, categoria, linea in lexico_demo.tokens_clasificados:
                self.console.print(f"{token:<15} | {categoria:<20} | {linea}")
            
            self.console.print("\n\nGENERACION DE CODIGO (Analisis Sintactico y Semantico)")
            compilador = sw.Sintactico(content, self.object, traza, self.console)

            self.console.print("\n\nTABLA DE SIMBOLOS")
            self.console.print(f"{'IDENTIFICADOR':<15} | {'TIPO':<15} | {'DIRECCION'}")
            self.console.print("-" * 45)
            for simbolo, info in compilador.lexico.tabla_simbolos.simbolos.items():
                self.console.print(f"{simbolo:<15} | {info['categoria']:<15} | {info['direccion']}")ç

        """