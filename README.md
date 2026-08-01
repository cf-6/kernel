```markdown
# Kernel Language Translator

A complete custom programming language translator with 254+ syntax elements, OOP, exception handling, type checking, and Python/Shell code generation.

---

## SECURITY WARNING / LEGAL DISCLAIMER

**EDUCATIONAL PROJECT ONLY - NOT A HACKING TOOL**

This project is a programming language implementation (compiler/translator), NOT an attack tool or exploitation framework.

WHAT THIS PROJECT IS:
- A learning resource for compiler design and programming language implementation
- An educational tool for understanding lexical analysis, parsing, and code generation
- A Python programming showcase
- An academic/learning project

WHAT THIS PROJECT IS NOT:
- Not a hacking tool
- Not an exploit framework
- Not a penetration testing tool
- Not malware or virus
- Not designed for illegal activities

ALL "SECURITY-RELATED" KEYWORDS:
- Generate ONLY simulated code (print statements, logs)
- Do NOT perform any actual attacks
- Are for educational context only
- Are similar to how universities teach cybersecurity concepts

USER RESPONSIBILITY:
- Users must comply with all applicable laws and regulations
- Only use on systems you own or have explicit permission to test
- The author assumes NO LIABILITY for any misuse
- Users accept full responsibility for how they use this software

BY USING THIS SOFTWARE, YOU AGREE TO:
- NOT use it for malicious purposes
- NOT target systems without authorization
- NOT claim this tool performs actual attacks
- Use it ONLY for learning and education

---

## Features

CORE FEATURES:
- 160+ Keywords - Extensive keyword library for DSL design
- 32 Operators - Complete operator support including compound assignment
- 8 Data Types - int, float, bool, string, array, map, any, void
- 12 Control Flow - if/elif/else, while, for, match, break, continue, return
- 18 Statement Types - Comprehensive statement support
- 14 Expression Types - Rich expression grammar

ADVANCED FEATURES:
- Object-Oriented Programming - class, extends, implements, super, this
- Exception Handling - try/catch/finally/throw
- Type Checking - Static type inference and validation
- Syntax Highlighting - Color output in terminal
- Multi-Language Output - Python and Shell code generation
- Error Recovery - Graceful error handling and reporting
- Function Support - Functions with parameters and return types
- Built-in Functions - print, len, range, type, str, int, float, bool

---

## Language Statistics

+------------------+-------+
| Category         | Count |
+------------------+-------+
| Keywords         | 160+  |
| Operators        | 32    |
| Data Types       | 8     |
| Control Flow     | 12    |
| Statement Types  | 18    |
| Expression Types | 14    |
| Code Org         | 10    |
+------------------+-------+
| Total            | 254+  |
+------------------+-------+

---

## Installation

Clone the repository:
```
git clone https://github.com/yourusername/kernel-translator.git
cd kernel-translator
```

Requirements:
- Python 3.8 or higher
- No external dependencies required

Check your Python version:
```
python --version
```

---

## Quick Start

Translate a Kernel file and display output:
```
python kernel_translator.py examples/test.kernel
```

Translate and save to a file:
```
python kernel_translator.py examples/test.kernel -o output.py
```

Generate Shell script:
```
python kernel_translator.py examples/test.kernel --format shell -o output.sh
```

---

## Command Line Options

```
python kernel_translator.py [OPTIONS] INPUT

Required:
  INPUT                  Path to the .kernel file

Optional:
  -o OUTPUT, --output OUTPUT
                         Output file path
  --format {python,shell}
                         Output format (default: python)
  --no-type-check        Disable type checking
  --highlight            Enable syntax highlighting in output
  --list-keywords        List all supported keywords
  -h, --help             Show help message
```

---

## Writing Your First Kernel Program

Create a file named `hello.kernel`:

```
// My first Kernel program
log "Hello, Kernel World!"

let name = "Kernel"
log "Welcome to " + name

ping "google.com"
```

Translate and run:
```
python kernel_translator.py hello.kernel
```

Output:
```
[INFO] Hello, Kernel World!
[INFO] Welcome to Kernel
[PING] Pinging google.com...
[PING] google.com is ALIVE
```

---

## Syntax Guide

### Variables
```
let name = "Kernel"
let version: int = 2
const PI = 3.14159
```

### Functions
```
fn greet(name: string) -> string {
    return "Hello, " + name
}
```

### Classes
```
class Network {
    fn scan(target: string) {
        scan target
    }
}
```

### Control Flow
```
if version > 1 {
    ping "google.com"
} else {
    log "Version too old"
}
```

### Loops
```
for i in range(5) {
    log "Iteration: " + i
}

while condition {
    // do something
}
```

### Exception Handling
```
try {
    exploit "127.0.0.1" "CVE-2024-1234"
} catch e {
    log "Exploit failed: " + e
} finally {
    log "Cleanup done"
}
```

---

## Commands Reference

NETWORK COMMANDS:
```
ping "192.168.1.1"
scan "192.168.1.0/24"
sniff "eth0"
connect "google.com" 80
listen 8080
resolve "example.com"
```

SECURITY RESEARCH COMMANDS (SIMULATED ONLY):
```
exploit "127.0.0.1" "CVE-2024-1234"
exfil "data.txt" "remote.com"
root
payload "reverse_shell"
```

SYSTEM COMMANDS:
```
shell "ls -la"
log "System initialized"
guard
monitor
```

---

## Example Programs

### Network Scanner

Create `network.kernel`:

```
let target = "192.168.1.1"

log "Starting network scan..."
ping target

if target == "192.168.1.1" {
    scan "192.168.1.0/24"
    connect target 80
    connect target 443
} else {
    log "Target not found"
}

for ip in ["192.168.1.1", "192.168.1.2", "192.168.1.3"] {
    ping ip
    log "Scanned: " + ip
}
```

Run:
```
python kernel_translator.py network.kernel -o network.py
python network.py
```

### Object-Oriented Program

Create `oop.kernel`:

```
class Scanner {
    fn scan_network(ip: string) {
        log "Scanning: " + ip
        scan ip
    }
    
    fn ping_host(ip: string) {
        ping ip
    }
}

class AdvancedScanner extends Scanner {
    fn exploit_target(ip: string, vuln: string) {
        log "Exploiting " + ip + " with " + vuln
        exploit ip vuln
    }
}

let scanner = new AdvancedScanner()
scanner.scan_network("192.168.1.0/24")
scanner.ping_host("8.8.8.8")
```

### Exception Handling

Create `error.kernel`:

```
try {
    log "Trying to scan..."
    scan "invalid-target"
    connect "unknown-host" 80
} catch e {
    log "Error occurred: " + e
} finally {
    log "Cleanup completed"
}
```

---

## Generated Code Examples

### Python Output

Input (Kernel):
```
ping "google.com"
scan "192.168.1.1"
```

Output (Python):
```python
#!/usr/bin/env python3
print('[PING] Pinging google.com...')
result = shell_exec('ping -c 4 google.com 2>/dev/null')
if '1 received' in result or '4 received' in result:
    print('[PING] google.com is ALIVE')
else:
    print('[PING] google.com is DEAD')

print('[SCAN] Scanning 192.168.1.1...')
result = shell_exec('nmap -p- --open 192.168.1.1 2>/dev/null')
print('[SCAN] Results:\n' + result)
```

### Shell Output

Input (Kernel):
```
ping "google.com"
scan "192.168.1.1"
```

Output (Shell):
```bash
#!/bin/bash
ping -c 4 google.com
nmap -p- --open 192.168.1.1
```

---

## Batch Processing

Translate all .kernel files in a directory:
```bash
for file in *.kernel; do
    python kernel_translator.py "$file" -o "${file%.kernel}.py"
done
```

Translate and run all files:
```bash
for file in *.kernel; do
    python kernel_translator.py "$file" -o "${file%.kernel}.py"
    python "${file%.kernel}.py"
done
```

---

## Pipe Input/Output

Pipe from stdin:
```bash
cat input.kernel | python kernel_translator.py -
```

Pipe to file:
```bash
python kernel_translator.py input.kernel > output.py
```

---

## List All Keywords

View all supported keywords:
```bash
python kernel_translator.py --list-keywords
```

Partial output:
```
Supported keywords (160+):
!           ?           k           set         permust     space       import      export
if          else        elif        while       for         foreach     break       continue
return      match       case        default     pass        goto        label       λ
fn          rccode      call        addr        bind        callback    hook        cmper
ping        fromcP      send        recv        sniff       spoof       scan        listen
connect     resolve     proxy       hcp         kimax       sotxmax     exploit     payload
... and many more
```

---

## Common Errors and Solutions

+----------------------------------+------------------------------------------+
| Error                            | Solution                                 |
+----------------------------------+------------------------------------------+
| FileNotFoundError                | Check if input file path is correct      |
| SyntaxError at line X            | Check syntax (missing brackets, quotes)  |
| ModuleNotFoundError              | Run from project root directory          |
| PermissionError                  | Check write permission for output file   |
| TypeError                        | Use --no-type-check to disable checking  |
+----------------------------------+------------------------------------------+

---

## Tips and Best Practices

```
// Use meaningful variable names
let target_ip = "192.168.1.1"   // Good
let a = "192.168.1.1"           // Bad

// Add comments to explain your code
// Scan the target network
scan "192.168.1.0/24"

// Use try-catch for error handling
try {
    connect "example.com" 80
} catch e {
    log "Connection failed: " + e
}

// Use functions to organize code
fn scan_network(ip: string) {
    log "Scanning: " + ip
    scan ip
}

// Use const for values that don't change
const TIMEOUT = 30
const MAX_RETRIES = 3
```

---

## Project Structure

```
kernel-translator/
├── kernel_translator.py    # Main translator (2000+ lines)
├── README.md               # This file
├── LICENSE                 # MIT License
├── .gitignore             # Git ignore rules
├── examples/
│   ├── test.kernel         # Basic example
│   ├── network.kernel      # Network operations
│   ├── oop.kernel          # Object-oriented example
│   └── advanced.kernel     # Advanced features
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_generator.py
└── docs/
    ├── language_spec.md
    └── api_documentation.md
```

---

## Technical Architecture

```
Kernel Source Code
        |
    [Tokenizer]
    Lexical Analysis
        |
    Tokens
        |
    [Parser]
    Syntax Analysis (Recursive Descent)
        |
    AST (Abstract Syntax Tree)
        |
    [Type Checker]
    Type Validation
        |
    [Generator]
    Code Generation
        |
    Python/Shell Code
```

Components:
1. Tokenizer - Converts source code to tokens
2. Parser - Recursive descent parser, builds AST
3. Type Checker - Static type analysis
4. Generator - Python/Shell code emitter
5. Highlighter - Terminal syntax coloring

---

## Who Should Use This

- Students learning compiler design
- Python developers interested in language implementation
- Security researchers (for authorized testing only)
- Anyone curious about how programming languages work

What you will learn:
- How lexers work (regular expressions, tokenization)
- How parsers work (recursive descent, AST)
- How type checking works
- How code generation works
- Programming language design principles

---

## Testing

Run all tests:
```
python -m unittest discover tests -v
```

Run specific test:
```
python tests/test_lexer.py
```

Test with examples:
```
python kernel_translator.py examples/test.kernel
```

---

## License

MIT License - see LICENSE file for details.

---

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing`
5. Open a Pull Request

---

## Roadmap

v2.0 (Current):
- Complete lexer implementation
- Recursive descent parser
- Type checking
- Python code generation
- Shell code generation
- OOP support
- Exception handling
- Syntax highlighting

v2.1 (Planned):
- JavaScript code generation
- Web-based playground
- VSCode plugin
- Performance optimization
- More built-in functions

v3.0 (Future):
- JIT compilation
- Package manager
- Full IDE support
- Documentation generator

---

## Quick Reference Card

Most common commands:
```
python kernel_translator.py input.kernel
python kernel_translator.py input.kernel -o output.py
python kernel_translator.py input.kernel --format shell -o output.sh
python kernel_translator.py --list-keywords
python kernel_translator.py -h
```

Debugging:
```
python kernel_translator.py input.kernel --highlight
python kernel_translator.py input.kernel --no-type-check
```

---

Made for learning and education.

Use responsibly. Stay legal. Keep learning.

- 常见问题解决

直接复制到你的项目里就行！🚀
