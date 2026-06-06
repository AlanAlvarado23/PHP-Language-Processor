from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import sys
import io

from Console import Console
import Env

from Lexer import Lexer
from Parser import Parser
from Semantic import Semantic_Analyzer
from Code_Generator import Code_Generator
from Virtual_Machine import Virtual_Machine


class GUI:
    """
    Main Graphical User Interface for the PHP Compiler IDE.
    Manages the code editor tabs, file explorer, output console, 
    and the execution pipeline (Parsing, Semantic Analysis, Code Generation, and VM).
    """

    def __init__(self):
        self.window_size = "1100x700"
        self.title = "PHP Compiler"

        self.current_directory = os.getcwd()

        # IntelliJ (Darcula) style color palette
        self.bg_editor = "#2b2b2b"
        self.bg_panel = "#3c3f41"
        self.bg_tab_active = "#4e5254"
        self.fg_text = "#a9b7c6"
        self.fg_ui = "#bbbbbb"
        self.line_num_fg = "#606366"
        
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) 
        
        self.setup_styles()
        
        # Main layout structure (PanedWindows)
        self.main_pw = PanedWindow(self.root, orient="horizontal", sashwidth=2, bg="#2d2f30", bd=0, sashrelief=FLAT)
        self.main_pw.pack(fill="both", expand=True)

        self.left_pw = PanedWindow(self.main_pw, orient="vertical", sashwidth=2, bg="#2d2f30", bd=0, sashrelief=FLAT)
        
        self.top_frame = Frame(self.left_pw, bg=self.bg_editor, bd=0, highlightthickness=0)
        self.bottom_frame = Frame(self.left_pw, bg=self.bg_panel, bd=0, highlightthickness=0)

        self.console = Console(self.bottom_frame)
        Env.set_console(self.console)
        
        self.left_pw.add(self.top_frame, height=500, stretch="always")
        self.left_pw.add(self.bottom_frame, stretch="always")

        self.right_frame = Frame(self.main_pw, bg=self.bg_panel, bd=0, highlightthickness=0)
        
        self.main_pw.add(self.right_frame, width=250, stretch="never") 
        self.main_pw.add(self.left_pw, stretch="always")

        self.font_code = ('Consolas', 12)
        self.font_ui = ('Segoe UI', 10)

        self.tabs = {} 

        # Compiler State Variables
        self.ast = None
        self.is_semantic_approved = False
        self.output_asm_path = None

        self.setup_menus()
        self.setup_statusbar()
        self.setup_console()
        self.setup_explorer()
        self.setup_editor()
        self.bind_events()

    def setup_styles(self):
        """Configures the ttk themes and styles to match the Darcula palette."""
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        style.configure("Treeview", background=self.bg_panel, foreground=self.fg_ui, 
                        fieldbackground=self.bg_panel, font=('Segoe UI', 10), borderwidth=0, relief=FLAT)
        style.map("Treeview", background=[('selected', '#2f65ca')], foreground=[('selected', 'white')])
        
        style.configure("TEntry", fieldbackground=self.bg_editor, foreground=self.fg_text, borderwidth=0, padding=4, relief=FLAT)
        style.configure("TButton", background="#4c5052", foreground=self.fg_ui, borderwidth=0, padding=4, relief=FLAT)
        style.map("TButton", background=[('active', '#5c6164')])

        style.configure("TNotebook", background=self.bg_panel, borderwidth=0, relief=FLAT)
        style.layout('TNotebook.Tab', []) 

    def setup_menus(self):
        """Builds the application's top menu bar."""
        self.menu_bar = Menu(self.root, bg=self.bg_panel, fg=self.fg_ui, relief=FLAT, bd=0)

        self.menu_file = Menu(self.menu_bar, tearoff=0, bg=self.bg_panel, fg=self.fg_ui, activebackground="#2f65ca", bd=0)
        self.menu_file.add_command(label="New File", command=self.new_file, accelerator="Ctrl+N")
        self.menu_file.add_command(label="Open File", command=self.open_file, accelerator="Ctrl+O")
        self.menu_file.add_command(label="Open Folder", command=self.open_folder)
        self.menu_file.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.menu_file.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.on_closing)
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)

        self.menu_edit = Menu(self.menu_bar, tearoff=0, bg=self.bg_panel, fg=self.fg_ui, activebackground="#2f65ca", bd=0)
        self.menu_edit.add_command(label="Copy")
        self.menu_edit.add_command(label="Paste")
        self.menu_edit.add_command(label="Cut")
        self.menu_edit.add_command(label="Clear Console", command=lambda: Env.console.clear())
        self.menu_bar.add_cascade(label="Edit", menu=self.menu_edit)

        self.menu_run = Menu(self.menu_bar, tearoff=0, bg=self.bg_panel, fg=self.fg_ui, activebackground="#2f65ca", bd=0)
        self.menu_run.add_command(label="1. Syntax Analysis (Parser)", command=self.parse, accelerator="Ctrl+P")
        self.menu_run.add_command(label="2. Semantic Analysis", command=self.semantic, accelerator="Ctrl+L")
        self.menu_run.add_separator()
        self.menu_run.add_command(label="3. Generate Code (VM Stack)", command=self.generate_code, accelerator="Ctrl+G")
        self.menu_run.add_command(label="4. Run in Virtual Machine", command=self.run_vm, accelerator="Ctrl+R")
        self.menu_bar.add_cascade(label="Run", menu=self.menu_run)
        self.menu_run.add_separator()
        self.menu_run.add_command(label="Run All", command=self.run_all, accelerator="Ctrl+M")

    def setup_editor(self):
        """Initializes the notebook and tab bar for the code editor."""
        self.tab_bar = Frame(self.top_frame, bg=self.bg_panel, bd=0)
        self.tab_bar.pack(side=TOP, fill=X)

        self.notebook = ttk.Notebook(self.top_frame)
        self.notebook.pack(side=TOP, fill=BOTH, expand=True)
        
        self.add_tab(None, "") 

    def setup_console(self):
        """Initializes the output console component."""
        self.output_label = Label(self.bottom_frame, text='Output Console', bg=self.bg_panel, fg='#8a9094', font=('Segoe UI', 9, 'bold'), bd=0, highlightthickness=0)
        self.console.create(((0, 1), (1, 1)))

    def setup_explorer(self):
        """Initializes the project file explorer tree and path entry."""
        self.tree_label = Label(self.right_frame, text="PROJECT", bg=self.bg_panel, fg='#8a9094', font=('Segoe UI', 9, 'bold'), anchor='w', bd=0, highlightthickness=0)
        self.tree_label.pack(fill='x', pady=(10, 5), padx=10)
        
        self.path_frame = Frame(self.right_frame, bg=self.bg_panel, bd=0, highlightthickness=0)
        self.path_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.path_var = StringVar(value=self.current_directory)
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.path_var, font=('Segoe UI', 9))
        self.path_entry.pack(side=LEFT, fill='x', expand=True)
        self.path_entry.bind('<Return>', self.on_path_entry_changed)
        
        self.btn_refresh = ttk.Button(self.path_frame, text="↻", width=3, command=self.refresh_explorer)
        self.btn_refresh.pack(side=RIGHT, padx=(5, 0))

        self.btn_browse = ttk.Button(self.path_frame, text="...", width=3, command=self.open_folder)
        self.btn_browse.pack(side=RIGHT, padx=(5, 0))

        self.tree = ttk.Treeview(self.right_frame, show="tree")
        self.tree_scrollbar = Scrollbar(self.right_frame, orient="vertical", command=self.tree.yview,
                                        bg=self.bg_panel, activebackground="#4e5254", troughcolor=self.bg_panel, bd=0, highlightthickness=0, relief=FLAT)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        
        self.tree_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=(0, 10))
        
        self.populate_file_explorer(self.current_directory)

    def setup_statusbar(self):
        """Initializes the bottom status bar for cursor position tracking."""
        self.status_bar = Label(self.root, text=" Ready", bg=self.bg_panel, fg=self.fg_ui, font=self.font_ui, anchor=W, pady=4, bd=0, highlightthickness=0, relief=FLAT)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def bind_events(self):
        """Binds global keyboard shortcuts and mouse events."""
        self.tree.bind('<Double-1>', self.on_tree_double_click) 
        self.tree.bind('<<TreeviewOpen>>', self.on_tree_open) 

        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-N>', self.new_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-S>', self.save_file_as)
        
        self.root.bind('<Control-p>', self.parse)
        self.root.bind('<Control-l>', self.semantic)
        self.root.bind('<Control-g>', self.generate_code)
        self.root.bind('<Control-r>', self.run_vm)

        self.root.bind('<Control-m>', self.run_all)
        
        self.root.bind('<Control-w>', self.close_current_tab)
        self.root.bind('<Control-Tab>', self.next_tab)

        self.root.bind('<Control-l>', lambda e: Env.console.clear())

    def render(self):
        """Renders the main window and starts the Tkinter event loop."""
        self.root.geometry(self.window_size)
        self.root.title(self.title)
        self.root.configure(bg=self.bg_panel)

        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)
        self.output_label.grid(row=0, column=0, sticky='nw', padx=10, pady=5)

        self.root.config(menu=self.menu_bar)
        self.root.mainloop()

    # --- Window and Tab Management ---

    def on_closing(self):
        """Handles application shutdown, prompting to save unsaved files."""
        tabs_to_check = list(self.tabs.keys())
        for tab_id in tabs_to_check:
            data = self.tabs.get(tab_id)
            if data and data['is_modified']:
                self.select_tab(tab_id)
                resp = messagebox.askyesnocancel("Exit IDE", f"Do you want to save changes to '{data['name']}' before exiting?")
                if resp: 
                    self.save_file()
                    if self.tabs[tab_id]['is_modified']: 
                        return 
                elif resp is None: 
                    return 
        
        self.root.destroy()

    def add_tab(self, file_path=None, content=""):
        """Creates a new editor tab with synchronized line numbers."""
        name = os.path.basename(file_path) if file_path else "Untitled"
        tab_frame = Frame(self.notebook, bg=self.bg_editor, bd=0, highlightthickness=0)
        tab_id = str(tab_frame)
        
        tab_frame.grid_columnconfigure(1, weight=1)
        tab_frame.grid_rowconfigure(0, weight=1)
        
        line_numbers = Text(tab_frame, width=5, padx=5, takefocus=0, bd=0, highlightthickness=0, relief=FLAT,
                            bg=self.bg_editor, fg=self.line_num_fg, font=self.font_code, state='disabled')
        code_text = Text(tab_frame, bg=self.bg_editor, fg=self.fg_text, font=self.font_code, 
                         width=95, height=50, insertbackground='#ffffff', bd=0, highlightthickness=0, relief=FLAT, undo=True, wrap="none")
        
        v_scrollbar = Scrollbar(tab_frame, orient="vertical", 
                              bg=self.bg_panel, activebackground="#4e5254", troughcolor=self.bg_editor, bd=0, highlightthickness=0, relief=FLAT)
        
        h_scrollbar = Scrollbar(tab_frame, orient="horizontal", 
                              bg=self.bg_panel, activebackground="#4e5254", troughcolor=self.bg_editor, bd=0, highlightthickness=0, relief=FLAT)
        
        def sync_scroll(*args):
            line_numbers.yview_moveto(args[0])
            v_scrollbar.set(*args)

        def sync_scrollbar(*args):
            code_text.yview(*args)
            line_numbers.yview(*args)

        code_text.config(yscrollcommand=sync_scroll, xscrollcommand=h_scrollbar.set)
        line_numbers.config(yscrollcommand=sync_scroll)
        v_scrollbar.config(command=sync_scrollbar)
        h_scrollbar.config(command=code_text.xview)
        
        line_numbers.grid(row=0, column=0, sticky='ns')
        code_text.grid(row=0, column=1, sticky='nsew', pady=5)
        v_scrollbar.grid(row=0, column=2, sticky='ns')
        h_scrollbar.grid(row=1, column=1, sticky='ew')
        
        code_text.insert('1.0', content)
        code_text.edit_modified(False) 
        
        self.notebook.add(tab_frame, text=name)
        
        ui_frame = Frame(self.tab_bar, bg=self.bg_panel)
        ui_frame.pack(side=LEFT, padx=(0, 1))
        
        btn_name = Button(ui_frame, text=f"  {name}  ", font=self.font_ui, bg=self.bg_panel, fg=self.fg_ui, 
                          bd=0, relief=FLAT, activebackground=self.bg_tab_active, activeforeground="#ffffff",
                          command=lambda t=tab_id: self.select_tab(t))
        btn_name.pack(side=LEFT, ipady=4)
        
        btn_close = Button(ui_frame, text="✖", font=self.font_ui, bg=self.bg_panel, fg=self.fg_ui, 
                           bd=0, relief=FLAT, activebackground="#c42b1c", activeforeground="#ffffff", 
                           command=lambda t=tab_id: self.close_tab(t))
        btn_close.pack(side=LEFT, padx=(0, 4), ipady=4)
        
        btn_name.bind('<B1-Motion>', lambda e, t=tab_id: self.on_tab_drag(e, t))
        ui_frame.bind('<B1-Motion>', lambda e, t=tab_id: self.on_tab_drag(e, t))
        
        self.tabs[tab_id] = {
            'path': file_path,
            'name': name,
            'frame': tab_frame,
            'text': code_text,
            'lines': line_numbers,
            'is_modified': False,
            'ui_frame': ui_frame,
            'btn_name': btn_name,
            'btn_close': btn_close
        }
        
        code_text.bind('<KeyRelease>', self.on_key_release)
        code_text.bind('<ButtonRelease-1>', self.update_status_bar)
        code_text.bind('<<Modified>>', self.on_text_modified)
        
        self.update_line_numbers()
        self.select_tab(tab_id)

    def select_tab(self, tab_id):
        self.notebook.select(tab_id)
        
        for tid, data in self.tabs.items():
            color = self.bg_tab_active if tid == tab_id else self.bg_panel
            data['ui_frame'].config(bg=color)
            data['btn_name'].config(bg=color)
            data['btn_close'].config(bg=color)
            
        data = self.tabs.get(tab_id)
        if data:
            data['text'].focus_set()
            self.update_status_bar()

    def next_tab(self, event=None):
        slaves = self.tab_bar.pack_slaves()
        if not slaves or len(slaves) <= 1:
            return "break"
            
        current_tab_id = self.notebook.select()
        if not current_tab_id:
            return "break"
            
        current_ui = self.tabs[current_tab_id]['ui_frame']
        try:
            current_idx = slaves.index(current_ui)
            next_idx = (current_idx + 1) % len(slaves)
            next_ui = slaves[next_idx]
            
            for tid, data in self.tabs.items():
                if data['ui_frame'] == next_ui:
                    self.select_tab(tid)
                    break
        except ValueError:
            pass
            
        return "break"

    def on_tab_drag(self, event, drag_tab_id):
        """Allows reordering of tabs via drag-and-drop."""
        x_root = event.widget.winfo_rootx() + event.x
        for tab_id, data in self.tabs.items():
            if tab_id != drag_tab_id:
                target_ui = data['ui_frame']
                cx = target_ui.winfo_rootx()
                cw = target_ui.winfo_width()
                
                if cx < x_root < cx + cw:
                    slaves = self.tab_bar.pack_slaves()
                    try:
                        drag_idx = slaves.index(self.tabs[drag_tab_id]['ui_frame'])
                        target_idx = slaves.index(target_ui)
                        
                        slaves.insert(target_idx, slaves.pop(drag_idx))
                        for s in slaves: s.pack_forget()
                        for s in slaves: s.pack(side=LEFT, padx=(0, 1))
                        
                        self.notebook.insert(target_idx, self.tabs[drag_tab_id]['frame'])
                    except ValueError:
                        pass
                    break

    def close_current_tab(self, event=None):
        current_tab_id = self.notebook.select()
        if current_tab_id:
            self.close_tab(current_tab_id)

    def close_tab(self, tab_id=None):
        if not tab_id: return
        
        data = self.tabs[tab_id]
        if data['is_modified']:
            self.select_tab(tab_id) 
            resp = messagebox.askyesnocancel("Save changes", f"Do you want to save changes to '{data['name']}' before closing?")
            if resp: 
                self.save_file()
                if self.tabs[tab_id]['is_modified']: 
                    return
            elif resp is None: 
                return
        
        data['ui_frame'].destroy()
        self.notebook.forget(tab_id)
        del self.tabs[tab_id]
        
        remaining_tabs = self.tab_bar.pack_slaves()
        if remaining_tabs:
            for tid, d in self.tabs.items():
                if d['ui_frame'] == remaining_tabs[-1]:
                    self.select_tab(tid)
                    break
        else:
            self.add_tab(None, "")

    def get_current_tab_data(self):
        current_tab_id = self.notebook.select()
        if current_tab_id:
            return self.tabs.get(current_tab_id)
        return None

    # --- Editor Events ---

    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.update_status_bar()

    def on_text_modified(self, event):
        text_widget = event.widget
        if text_widget.edit_modified():
            for tab_id, data in self.tabs.items():
                if data['text'] == text_widget:
                    if not data['is_modified']:
                        data['is_modified'] = True
                        data['btn_name'].config(text=f" * {data['name']}  ")
                    break

    def update_status_bar(self, event=None):
        data = self.get_current_tab_data()
        if not data:
            self.status_bar.config(text=" Ready")
            self.root.title(self.title)
            return

        cursor_pos = data['text'].index(INSERT)
        line, col = cursor_pos.split('.')
        self.status_bar.config(text=f"  Line: {line}  |  Column: {col}  |  File: {data['name']}")
        
        status_mod = " (Modified)" if data['is_modified'] else ""
        self.root.title(f"{self.title} - {data['name']}{status_mod}")

    def update_line_numbers(self, event=None):
        data = self.get_current_tab_data()
        if not data: return

        code_text = data['text']
        line_numbers = data['lines']

        total_lines = int(code_text.index('end-1c').split('.')[0])
        numbers_str = "\n".join(str(i) for i in range(1, total_lines + 1))
        
        line_numbers.config(state='normal')
        line_numbers.delete('1.0', END)
        line_numbers.insert('1.0', numbers_str)
        line_numbers.config(state='disabled')
        line_numbers.yview_moveto(code_text.yview()[0])

    # --- File Explorer Methods ---

    def on_path_entry_changed(self, event=None):
        new_path = self.path_var.get()
        if os.path.isdir(new_path):
            self.current_directory = new_path
            self.populate_file_explorer(self.current_directory)
        else:
            messagebox.showerror("Error", "The specified path does not exist or is not a valid directory.")
            self.path_var.set(self.current_directory)

    def populate_file_explorer(self, path):
        """Populates the treeview with directories and compatible files."""
        self.tree.delete(*self.tree.get_children()) 
        self._populate_node('', path) 

    def _populate_node(self, parent_node, path):
        try:
            items = os.listdir(path)
            folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
            files = [f for f in items if os.path.isfile(os.path.join(path, f))]
            
            for folder in sorted(folders):
                abspath = os.path.join(path, folder)
                oid = self.tree.insert(parent_node, 'end', text=f" 📁 {folder}", values=[abspath])
                self.tree.insert(oid, 'end', text="dummy")
                
            for file in sorted(files):
                if file.endswith(('.php', '.txt', '.py', '.json', '.html', '.css', '.js', '.asm')): 
                    abspath = os.path.join(path, file)
                    self.tree.insert(parent_node, 'end', text=f" 📄 {file}", values=[abspath])
        except PermissionError:
            pass

    def on_tree_open(self, event):
        """Lazy-loads subdirectories when expanded in the treeview."""
        node = self.tree.focus()
        children = self.tree.get_children(node)
        
        if len(children) == 1 and self.tree.item(children[0], 'text') == "dummy":
            self.tree.delete(children[0]) 
            folder_path = self.tree.item(node, 'values')[0]
            self._populate_node(node, folder_path)

    def refresh_explorer(self):
        """Reloads the file tree based on the current directory."""
        if os.path.isdir(self.current_directory):
            self.populate_file_explorer(self.current_directory)
            if Env.console:
                Env.console.print_notification("File explorer updated.")
        else:
            messagebox.showerror("Error", "The current directory no longer exists.")

    def open_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Folder", initialdir=self.current_directory)
        if folder_selected:
            self.current_directory = folder_selected
            self.path_var.set(self.current_directory)
            self.populate_file_explorer(self.current_directory)

    def on_tree_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        
        item_values = self.tree.item(selected_item[0], 'values')
        if item_values:
            file_path = item_values[0]
            if os.path.isfile(file_path):
                self._load_file_content(file_path)

    def _load_file_content(self, file_path):
        for tab_id, data in self.tabs.items():
            if data['path'] == file_path:
                self.select_tab(tab_id)
                return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.add_tab(file_path, content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read the file:\n{e}")

    # --- File Operations ---

    def new_file(self, event=None):
        self.add_tab(None, "")

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Open File",
            defaultextension=".php",
            filetypes=[("PHP Files", "*.php"), ("Assembly", "*.asm"), ("All files", "*.*")]
        )
        if file_path:
            self._load_file_content(file_path)

    def save_file_as(self, event=None):
        data = self.get_current_tab_data()
        if not data: return

        path = filedialog.asksaveasfilename(
            title="Save File As",
            defaultextension=".php",
            filetypes=[("PHP Files", "*.php"), ("All files", "*.*")]
        )
        if path:
            try:
                content = data['text'].get('1.0', 'end-1c')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                data['path'] = path
                data['name'] = os.path.basename(path)
                data['is_modified'] = False
                data['text'].edit_modified(False)
                
                data['btn_name'].config(text=f"  {data['name']}  ")
                self.update_status_bar()
                
                if os.path.dirname(path) == self.current_directory:
                    self.populate_file_explorer(self.current_directory)
                    self.refresh_explorer()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file:\n{e}")

    def save_file(self, event=None):
        data = self.get_current_tab_data()
        if not data: return

        if data['path']:
            try:
                content = data['text'].get('1.0', 'end-1c')
                with open(data['path'], 'w', encoding='utf-8') as file:
                    file.write(content)
                
                data['is_modified'] = False
                data['text'].edit_modified(False)
                
                data['btn_name'].config(text=f"  {data['name']}  ") 
                self.update_status_bar()
                self.refresh_explorer()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file:\n{e}")
        else:
            self.save_file_as()

    # --- Compiler Pipeline Methods ---

    def parse(self, event=None):
        """Phase 1: Lexical and Syntax Analysis -> Generates AST."""
        tab_data = self.get_current_tab_data()
        
        if not tab_data:
            Env.console.print_alert("Error: No file open to compile.")
            return

        code = tab_data['text'].get("1.0", "end-1c")

        if not code.strip():
            Env.console.print("Warning: The file is empty.")
            return

        Env.console.print_notification(f"- - - - - - STARTING PARSE: {tab_data['name']}")
        
        # Reset global state before compiling new code
        self.ast = None
        self.is_semantic_approved = False
        self.output_asm_path = None
        
        trace = 1
        
        try:
            self.lexer = Lexer(code, trace)
            self.parser = Parser(self.lexer) 
            self.ast = self.parser.parse()
            
            if self.ast:
                Env.console.print("--- Abstract Syntax Tree (AST) ---")
                self.ast.print_tree()
                Env.console.print_notification("- - - - - - PARSING COMPLETED SUCCESSFULLY")
            else:
                Env.console.print_alert("Error: The parser could not generate the tree.")
                
        except SystemExit as e:
            Env.console.print_alert(f"Process stopped due to a syntax error (Exit code: {e.code})")
            
        except Exception as e:
            Env.console.print_alert(f"Unexpected exception during parsing: {str(e)}")
            
    def semantic(self, event=None):
        """Phase 2: Semantic Analysis -> Validates types, scopes, and context."""
        if not getattr(self, 'ast', None):
            Env.console.print_alert("Error: No Abstract Syntax Tree (AST) in memory. Run the Parser first.")
            return

        Env.console.print_notification(f"- - - - - - STARTING SEMANTIC ANALYSIS")
        
        self.is_semantic_approved = False
        
        try:
            semantic_analyzer = Semantic_Analyzer(self.ast)
            semantic_success = semantic_analyzer.analyze()
            
            if semantic_success:
                Env.console.print_notification("- - - - - - SEMANTIC ANALYSIS PASSED ALL TESTS")
                self.is_semantic_approved = True 
            else:
                Env.console.print_alert("- - - - - - SEMANTIC ANALYSIS FINISHED WITH ERRORS")
                
        except Exception as e:
            Env.console.print_alert(f"Unexpected exception during semantic analysis: {str(e)}")

    def generate_code(self, event=None):
        """Phase 3: Intermediate Code Generation -> Emits Assembly/VM Code."""
        if not getattr(self, 'is_semantic_approved', False):
            Env.console.print_alert("Error: You must run and approve the Semantic Analysis first.")
            return
            
        Env.console.print_notification(f"- - - - - - STARTING INTERMEDIATE CODE GENERATION")
        try:
            output_file = os.path.join(self.current_directory, "Output/" + self.get_current_tab_data()['name'] + "_output.asm")
            
            generator = Code_Generator(self.ast, output_file, Env.console)
            generator.generate_code()
            
            self.output_asm_path = output_file
            self.refresh_explorer()
            
        except Exception as e:
            Env.console.print_alert(f"Error in code generation: {str(e)}")

    def run_vm(self, event=None):
        """Phase 4: Virtual Machine Execution -> Runs the generated .asm file."""
        if not getattr(self, 'output_asm_path', None) or not os.path.exists(self.output_asm_path):
            Env.console.print_alert("Error: Intermediate code (.asm) not found. Generate the code first.")
            return

        Env.console.print_notification(f"- - - - - - EXECUTING VIRTUAL MACHINE")
        
        # Redirect sys.stdout temporarily to capture VM prints
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            vm = Virtual_Machine(self.output_asm_path)
            vm.execute()
            
            vm_output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            for line in vm_output.split('\n'):
                if line.strip():
                    Env.console.print(line)
                    
        except Exception as e:
            sys.stdout = old_stdout
            Env.console.print_alert(f"Error during Virtual Machine execution: {str(e)}")

    def run_all(self, event=None):
        """Executes the entire compiler pipeline automatically."""
        Env.console.clear()
        Env.console.print_notification("=== FULL EXECUTION STARTED ===")
        
        # 1. Parse
        self.parse()
        if getattr(self, 'ast', None) is None:
            Env.console.print_alert("Aborted: Parser Error.")
            return

        # 2. Semantic Analysis
        self.semantic()
        if not getattr(self, 'is_semantic_approved', False):
            Env.console.print_alert("Aborted: Semantic Error.")
            return

        # 3. Code Generation
        self.generate_code()
        if not getattr(self, 'output_asm_path', None) or not os.path.exists(self.output_asm_path):
            Env.console.print_alert("Aborted: Could not generate the .asm code.")
            return

        # 4. Execute VM
        self.run_vm()
        Env.console.print_notification("=== EXECUTION FINISHED ===")