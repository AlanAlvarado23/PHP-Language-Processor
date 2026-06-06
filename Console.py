from tkinter import *

class Console:
    """
    Provides a synchronized, read-only GUI console with a sidebar gutter.
    Supports styled text output (alerts, notifications) and synchronized scrolling.
    """
    
    def __init__(self, root, font_style=('Consolas', 11)):
        """
        Initializes the Console UI components.
        
        Args:
            root: The parent Tkinter widget.
            font_style (tuple): Font family and size for the console text.
        """
        self.frame = Frame(root, bg='#1e1e1e')
        
        # Gutter for prompt indicators (e.g., '>>>')
        self.gutter = Text(self.frame, width=4, bg='#252526', fg='#858585', 
                           font=font_style, bd=0, highlightthickness=0, state=DISABLED)
        self.gutter.pack(side=LEFT, fill=Y)
        
        # Main text display
        self.console_text = Text(self.frame, bg='#1e1e1e', fg='#d4d4d4', 
                                 font=font_style, bd=0, highlightthickness=0, wrap=NONE)
        self.console_text.pack(side=LEFT, fill=BOTH, expand=True)

        # Synchronized vertical scrollbar
        self.scrollbar_console = Scrollbar(root, orient="vertical", command=self._on_scrollbar)
        self.console_text.config(yscrollcommand=self._on_textscroll)
        self.gutter.config(yscrollcommand=self._on_textscroll)

        # Define text style tags
        self.console_text.tag_config("alert", foreground="#f44747")   
        self.console_text.tag_config("notify", foreground="#569cd6")  
        self.console_text.tag_config("success", foreground="#6a9955") 

    def create(self, grid):
        """
        Places the console and scrollbar within the parent grid layout.
        
        Args:
            grid (list): A 2D list specifying [[frame_col, frame_row], [scroll_col, scroll_row]].
        """
        self.frame.grid(column=grid[0][0], row=grid[0][1], sticky='nsew')
        self.scrollbar_console.grid(column=grid[1][0], row=grid[1][1], sticky='ns')
        
        self.print_notification("PHP Compiler ready. Waiting for input...")

    # --- Scroll Synchronization ---

    def _on_scrollbar(self, *args):
        """Synchronizes the vertical scrolling of both text widgets via the scrollbar."""
        self.console_text.yview(*args)
        self.gutter.yview(*args)

    def _on_textscroll(self, *args):
        """Updates the scrollbar and synchronizes the gutter when using the mouse wheel."""
        self.scrollbar_console.set(*args)
        self.gutter.yview_moveto(args[0])

    def _insert_gutter(self):
        """Injects the prompt indicator ('>>>') into the sidebar."""
        self.gutter.config(state=NORMAL)
        self.gutter.insert(END, ">>>\n")
        self.gutter.config(state=DISABLED)

    # --- Output Methods ---

    def print(self, string):
        """Outputs standard text to the console."""
        self._insert_gutter()
        self.console_text.config(state=NORMAL)
        self.console_text.insert(END, str(string) + '\n')
        self.console_text.see(END) 
        self.gutter.see(END)
        self.console_text.config(state=DISABLED)

    def print_alert(self, string):
        """Outputs error or alert messages with specific styling."""
        self._insert_gutter()
        self.console_text.config(state=NORMAL)
        self.console_text.insert(END, str(string) + '\n', "alert")
        self.console_text.see(END)
        self.gutter.see(END)
        self.console_text.config(state=DISABLED)

    def print_notification(self, string):
        """Outputs informational or notification messages with specific styling."""
        self._insert_gutter()
        self.console_text.config(state=NORMAL)
        self.console_text.insert(END, str(string) + '\n', "notify")
        self.console_text.see(END)
        self.gutter.see(END)
        self.console_text.config(state=DISABLED)

    def clear(self):
        """Clears all content from both the console and the gutter."""
        self.console_text.config(state=NORMAL)
        self.gutter.config(state=NORMAL)
        
        self.console_text.delete('1.0', END)
        self.gutter.delete('1.0', END)
        
        # Reset insertion point
        self.console_text.mark_set("insert", "1.0")
        
        self.console_text.config(state=DISABLED)
        self.gutter.config(state=DISABLED)