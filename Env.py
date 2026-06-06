"""
Env.py
Global environment configuration for the PHP Compiler.
This module acts as a shared state container across different compiler phases
(Parser, Semantic Analyzer, Code Generator), avoiding tight coupling.
"""

console = None 
symbol_table = {}  # Global symbol table to share metadata and memory IDs (mem_id)

def set_console(instance):
    """
    Sets the global console instance for outputting messages across the IDE.
    
    Args:
        instance: The Console object used by the GUI.
    """
    global console
    console = instance