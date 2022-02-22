#!/usr/bin/python3
import sys
import re

### Error reporting
def report_error(msg):
    print(f"\33[31;1mError:\33[0m {msg}", file=sys.stderr)

def report_info(msg):
    print(f"╰ {msg}", file=sys.stderr)

def report_source_error(ln, msg):
    print(f"\33[31;1mError, \33[33;1mline {ln}:\33[0m {msg}", file=sys.stderr)

### Get input file
args = sys.argv

# Check for input file
if len(args) != 2:
    report_error("No input file provided.")
    exit(1)

file_path = args[1]

# Ensure input file is using the correct file extension
if not file_path.endswith(".plop"):
    extension = file_path.split('.')[-1]
    report_error(f"Invalid file extension '.{extension}'.")
    report_info("Input file MUST use the '.plop' file extension.")
    exit(1)

# Attempt to open file
try:
    file = open(file_path, "r")
except:
    report_error("Failed to open file '{file_path}' for reading.")
    exit(1)

file_contents = file.read()
file.close()

### Tokenize file contents
class Token:
    lexemme = ""
    line = 0
    
    def __init__(self, lxm, ln):
        self.lexemme = lxm
        self.line = ln

# Collect tokens
tokens = []
for ln, content in enumerate(file_contents.splitlines()):
    # https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
    for lexemme in re.findall("(?:\".*?\"|\S)+", content):
        # Ignore comments
        if lexemme.startswith("#"):
            break

        token = Token(lexemme, ln)
        tokens.append(token)

### Parse tokens
# Keywords that do not take in sub-expressions
STANDALONE_KEYWORDS = [
    "drop", "dup", "swap", "rot", "over",
    "+", "-", "*", "/", "%", "=",
    "not", "and", "or", "xor",
    "exit", "print", "println",
]

# Keywords that DO take in sub-expressions
EXPR_KEYWORDS = [
    "var", "const", "if", "else", "while", "proc",
]

KEYWORDS = STANDALONE_KEYWORDS + EXPR_KEYWORDS

def is_keyword(lxm):
    return lxm in KEYWORDS

def is_literal(lxm):
    if lxm.isdecimal():
        return True
    if lxm.startswith('"') and lxm.endswith('"'):
        return True
    if lxm == "true" or lxm == "false":
        return True

    return False

class Expr:
    lexemme = ""
    line = 0
    sub_expr = None
    alt_sub_expr = None
    value = None

    def __init__(self, lxm, ln, sbexpr=None, altsbexpr=None, val=None):
        self.lexemme = lxm
        self.line = ln
        self.sub_expr = sbexpr
        self.alt_sub_expr = altsbexpr
        self.value = val

# Parse tokens
tokens.reverse()
names = []

def collect_expressions():
    exprs = []

    while len(tokens) != 0 and tokens[-1].lexemme != '}':
        token = tokens.pop()

        ln = token.line
        lxm = token.lexemme

        ### Check for literals
        # Integer literal
        # TODO: Parse floating-point literals as well, converting the 'integer'
        #   type to a more general 'number' type
        if lxm.isdecimal():
            exprs.append(Expr("push", ln, val=int(lxm)))
        # String literal
        elif lxm.startswith('"') and lxm.endswith('"'):
            strlit = lxm[1:-1]

            strlit = strlit.replace('\\n', '\n')
            strlit = strlit.replace('\\t', '\t')
            strlit = strlit.replace('\\r', '\r')
            
            exprs.append(Expr("push", ln, val=strlit))
        # Boolean literal: true
        elif lxm == "true":
            exprs.append(Expr("push", ln, val=True))
        # Boolean literal: false
        elif lxm == "false":
            exprs.append(Expr("push", ln, val=False))

        # Consume sub-expression
        elif lxm in EXPR_KEYWORDS:
            # var, const, proc. Consume name and continue
            if lxm == "var" or lxm == "const":
                # TODO: Check stack size before popping
                name_token = tokens.pop()
                name = name_token.lexemme

                if is_keyword(name) or is_literal(name) or name in names:
                    report_source_error(name_token.line, f"Name '{name}' is already in use.")
                    exit(1)

                names.append(name)
                exprs.append(Expr(lxm, ln, val=name))
            
            # if, while
            else:
                # TODO: This should really be handled somewhere else...
                if lxm == "else":
                    report_source_error(ln, "Else expressions MUST follow if expressions")

                expr = Expr(lxm, ln)

                if lxm == "proc":
                    # TODO: Check stack size before popping
                    name_token = tokens.pop()
                    name = name_token.lexemme

                    if is_keyword(name) or is_literal(name) or name in names:
                        report_source_error(name_token.line, f"Name '{name}' is already in use.")
                        exit(1)

                    expr.value = name
                    names.append(name)

                # TODO: report errors rather than tripping assertions
                assert tokens.pop().lexemme == '{'
                subexprs = collect_expressions()
                expr.sub_expr = subexprs
                # TODO: Report 'Mismatched open bracket' as error
                assert tokens.pop().lexemme == '}'
                
                if lxm == "if" and len(tokens) != 0 and tokens[-1].lexemme == "else":
                    tokens.pop()
                    assert tokens.pop().lexemme == '{'
                    subexprs = collect_expressions()
                    expr.alt_sub_expr = subexprs
                    # TODO: Report 'Mismatched open bracket' as error
                    assert tokens.pop().lexemme == '}'
                
                exprs.append(expr)

        elif lxm in STANDALONE_KEYWORDS:
            exprs.append(Expr(lxm, ln))

        elif not lxm in names:
            report_source_error(ln, f"Unknown word '{lxm}'")
            exit(1)

    return exprs

expressions = collect_expressions()

if len(tokens) != 0:
    line = tokens.pop().line
    report_source_error(line, "Mismatched closing bracket")
    exit(1)

### Interpret expressions
data_stack = []

variables = {}
constants = {}
procedures = {}

def evaluate_expression(expr: Expr):
    lxm = expr.lexemme

    # Push
    if lxm == "push":
        data_stack.append(expr.value)
    # Drop
    elif lxm == "drop":
        data_stack.pop()
    # Dup
    elif lxm == "dup":
        data_stack.append(data_stack[-1])
    # Swap
    elif lxm == "swap":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(a)
        data_stack.append(b)
    # Rot
    elif lxm == "rot":
        a = data_stack.pop()
        b = data_stack.pop()
        c = data_stack.pop()
        data_stack.append(b)
        data_stack.append(a)
        data_stack.append(c)
    # Over
    elif lxm == "over":
        data_stack.append(data_stack[-2])

    # Addition
    elif lxm == "+":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(b + a)
    # Subtraction
    elif lxm == "-":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(b - a)
    # Multiplication
    elif lxm == "*":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(b * a)
    # Division
    elif lxm == "/":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(b // a)
    # Modulo
    elif lxm == "%":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(b % a)
    # Equals
    elif lxm == "=":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(b == a)
    
    # Not
    elif lxm == "not":
        a = data_stack.pop()
        data_stack.append(not a)
    # And
    elif lxm == "and":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(a and b)
    # Or
    elif lxm == "or":
        a = data_stack.pop()
        b = data_stack.pop()
        data_stack.append(a or b)

    # Exit
    elif lxm == "exit":
        exit(data_stack.pop())

    # Print
    elif lxm == "print":
        print(data_stack.pop(), end="")
    # Println
    elif lxm == "println":
        print(data_stack.pop())

    # Var
    elif lxm == "var":
        variables[expr.value] = data_stack.pop()
    # Const
    elif lxm == "const":
        constants[expr.value] = data_stack.pop()
    # Proc
    elif lxm == "proc":
        procedures[expr.value] = expr.sub_expr
    # If
    # TODO: Else expressions
    elif lxm == "if":
        cond = data_stack.pop()
        if cond:
            for ex in expr.sub_expr:
                evaluate_expression(ex)
        elif expr.alt_sub_expr != None:
            for ex in expr.alt_sub_expr:
                evaluate_expression(ex)
    # Else
    elif lxm == "else":
        report_error("Loose else expression made it past parsing...")
        exit(1)

    # While
    elif lxm == "while":
        while data_stack.pop():
            for ex in expr.sub_expr:
                evaluate_expression(ex)
    # Report error
    else:
        report_source_error(expr.line, f"Unknown word '{lxm}'")
        exit(1)

for expr in expressions:
    evaluate_expression(expr)
