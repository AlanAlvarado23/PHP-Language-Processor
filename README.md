# PHP Compiler & Virtual Machine

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

A lightweight, custom compiler and virtual machine designed to parse, analyze, and execute a subset of the PHP programming language. Built entirely in Python, this project implements standard compiler design principles, taking raw PHP source code through Lexical Analysis, Syntactic Analysis, and Abstract Syntax Tree (AST) generation, paving the way for Semantic Analysis and Intermediate Code execution.

## Features

* **Lexical Analysis (`Lexer.py`):** Robust regex-based tokenizer that categorizes PHP keywords, operators, variables, and literal values while maintaining line tracking for precise error reporting.
* **Symbol Table Management:** Dynamic tracking of variables, memory addresses, and identifier types throughout the compilation lifecycle.
* **Syntactic Analysis (`Parser.py`):** A recursive-descent parser that enforces language grammar rules and handles syntax error recovery/reporting.
* **Abstract Syntax Tree (`Tree_Node`):** Constructs a logical hierarchy of the code, ready for semantic validation and three-address code (TAC) generation.
* **Supported PHP Constructs:**
    * Variables and Data Types (Integers, Strings, Booleans).
    * Control Structures (`if`, `elseif`, `else`, `switch`, `case`, `default`).
    * Loops (`while`, `for`, `break`).
    * Arrays and Indexing (`array()`, `$arr[$i]`).
    * I/O Operations (`echo`, `read`).
    * Built-in Functions (`count()`).

## Architecture

The pipeline follows a standard multi-pass compiler architecture:

1.  **Source Code:** Raw `.php` script input.
2.  **Lexer:** Scans the source code and produces a stream of `Token` objects.
3.  **Parser:** Consumes tokens and builds the **AST** using `Tree_Node` structures.
4.  **Semantic Analyzer (Planned/WIP):** Traverses the AST for type checking and populates the `eval_type` metadata.
5.  **Virtual Machine (Planned/WIP):** Generates intermediate instructions (`Temp`, `Label`, `Goto`) and executes them in a sandboxed environment.

## Repository Structure

```text
├── Env.py             # Environment configuration and console handling
├── Lexer.py           # Lexical Analyzer and Symbol Table implementation
├── Parser.py          # Recursive-descent parser and AST (Tree_Node) definition
├── Token.py           # Token types, definitions, and intermediate code flags
├── main.py            # Application entry point
└── README.md          # Project documentation

```

## Getting Started

### Prerequisites

* Python 3.8 or higher.
* A terminal or command-line interface.

### Installation

1. Clone the repository:
```bash
git clone [https://github.com/yourusername/php-compiler.git](https://github.com/yourusername/php-compiler.git)
cd php-compiler

```


2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```



### Usage

Run the compiler by passing a PHP file to the main script.

```bash
python main.py input.php

```

To enable the debugging trace (which prints the AST generation steps and Token stream to the console), use the `--trace` flag (or configure it in your `Env.py`):

```bash
python main.py input.php --trace

```

## Code Example

The compiler can successfully parse and generate an AST for PHP code like the following:

```php
<?php
    $limit = 10;
    $numbers = array();

    for($i = 0; $i < $limit; $i++) {
        $numbers[$i] = $i * 2;
    }

    echo "Finished processing array.";
?>

```

## Contributing

Contributions are welcome! If you'd like to improve the Virtual Machine, add semantic rules, or expand the PHP grammar subset:

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

This project is distributed under the MIT License. See `LICENSE` for more information.
