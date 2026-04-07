from tkinter import *

class Console:
    def __init__(self, root, font_style=('Consolas', 11)):
        # 1. Creamos un Frame contenedor para agrupar la barra lateral y la consola
        self.frame = Frame(root, bg='#1e1e1e')
        
        # 2. Creamos el "Gutter" (Barra lateral para los >>>)
        # Usamos un color de fondo un poco más claro para diferenciarlo (#252526)
        self.gutter = Text(self.frame, width=4, bg='#252526', fg='#858585', 
                           font=font_style, bd=0, highlightthickness=0, state=DISABLED)
        self.gutter.pack(side=LEFT, fill=Y) # Lo pegamos a la izquierda
        
        # 3. Consola principal
        self.console_text = Text(self.frame, bg='#1e1e1e', fg='#d4d4d4', 
                                 font=font_style, bd=0, highlightthickness=0, wrap=NONE)
        self.console_text.pack(side=LEFT, fill=BOTH, expand=True) # Ocupa el resto del espacio

        # 4. Scrollbar sincronizada para ambos
        self.scrollbar_console = Scrollbar(root, orient="vertical", command=self._on_scrollbar)
        self.console_text.config(yscrollcommand=self._on_textscroll)
        self.gutter.config(yscrollcommand=self._on_textscroll)

        # Configuración de colores (Tags)
        self.console_text.tag_config("alert", foreground="#f44747")   # Rojo error
        self.console_text.tag_config("notify", foreground="#569cd6")  # Azul info
        self.console_text.tag_config("success", foreground="#6a9955") # Verde éxito

    def create(self, grid):
        # En lugar de colocar el texto, colocamos el Frame que contiene ambos
        self.frame.grid(column=grid[0][0], row=grid[0][1], sticky='nsew')
        self.scrollbar_console.grid(column=grid[1][0], row=grid[1][1], sticky='ns')
        
        self.print_notification("Compilador PHP listo. Esperando entrada...")

    # --- Métodos de sincronización del Scroll ---
    def _on_scrollbar(self, *args):
        """Mueve ambos textos cuando se arrastra la barra"""
        self.console_text.yview(*args)
        self.gutter.yview(*args)

    def _on_textscroll(self, *args):
        """Actualiza la barra y la barra lateral si se usa la rueda del ratón"""
        self.scrollbar_console.set(*args)
        self.gutter.yview_moveto(args[0])

    def _insert_gutter(self):
        """Método interno para inyectar el >>> en la barra lateral"""
        self.gutter.config(state=NORMAL)
        self.gutter.insert(END, ">>>\n")
        self.gutter.config(state=DISABLED)

    # --- Métodos de Impresión ---
    def print(self, string):
        self._insert_gutter() # Agregamos la viñeta
        self.console_text.config(state=NORMAL)
        self.console_text.insert(END, str(string) + '\n')
        self.console_text.see(END) 
        self.gutter.see(END) # Sincronizamos la vista
        self.console_text.config(state=DISABLED)

    def print_alert(self, string):
        self._insert_gutter()
        self.console_text.config(state=NORMAL)
        self.console_text.insert(END, str(string) + '\n', "alert")
        self.console_text.see(END)
        self.gutter.see(END)
        self.console_text.config(state=DISABLED)

    def print_notification(self, string):
        self._insert_gutter()
        self.console_text.config(state=NORMAL)
        self.console_text.insert(END, str(string) + '\n', "notify")
        self.console_text.see(END)
        self.gutter.see(END)
        self.console_text.config(state=DISABLED)

    def clear(self):
        self.console_text.config(state=NORMAL)
        self.gutter.config(state=NORMAL)
        self.console_text.delete('1.0', END)
        self.gutter.delete('1.0', END) # Limpiamos también la barra lateral
        self.console_text.config(state=DISABLED)
        self.gutter.config(state=DISABLED)