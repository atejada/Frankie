"""
frankie_fmt.py — Frankie source code auto-formatter.

Walks the AST produced by the parser and emits canonical, consistently-indented
Frankie source code.  Zero new dependencies — uses the same lexer/parser already
in the compiler.

Usage (via frankiec):
    frankiec fmt <file.fk>          # print formatted output
    frankiec fmt --write <file.fk>  # overwrite file in-place
    frankiec fmt --check <file.fk>  # exit 1 if file is not already formatted
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler.ast_nodes import *

INDENT = "  "   # 2-space canonical indent


class Formatter:
    def __init__(self):
        self._depth = 0
        self._lines = []

    # ── output helpers ────────────────────────────────────────────────────────

    def _emit(self, text=""):
        if text:
            self._lines.append(INDENT * self._depth + text)
        else:
            self._lines.append("")

    def _indent(self):  self._depth += 1
    def _dedent(self):  self._depth -= 1

    def format(self, program: Program) -> str:
        for i, node in enumerate(program.body):
            self._fmt_stmt(node)
            # Blank line after top-level function definitions for readability
            if isinstance(node, FuncDef) and i < len(program.body) - 1:
                if not isinstance(program.body[i + 1], FuncDef):
                    self._emit()
        # Strip trailing blank lines, then add a single trailing newline
        result = "\n".join(self._lines).rstrip() + "\n"
        return result

    # ── statements ────────────────────────────────────────────────────────────

    def _fmt_stmt(self, node):
        if isinstance(node, FuncDef):        self._fmt_func_def(node)
        elif isinstance(node, IfStmt):        self._fmt_if(node)
        elif isinstance(node, UnlessStmt):    self._fmt_unless(node)
        elif isinstance(node, WhileStmt):     self._fmt_while(node)
        elif isinstance(node, UntilStmt):     self._fmt_until(node)
        elif isinstance(node, DoWhileStmt):   self._fmt_do_while(node)
        elif isinstance(node, ForInStmt):     self._fmt_for_in(node)
        elif isinstance(node, ReturnStmt):    self._fmt_return(node)
        elif isinstance(node, PrintStmt):     self._fmt_print(node)
        elif isinstance(node, DebugPrint):    self._emit(f"p {self._fmt_expr(node.value)}")
        elif isinstance(node, Assign):        self._emit(f"{node.name} = {self._fmt_expr(node.value)}")
        elif isinstance(node, ConstAssign):   self._emit(f"{node.name} = {self._fmt_expr(node.value)}")
        elif isinstance(node, CompoundAssign):self._emit(f"{node.name} {node.op}= {self._fmt_expr(node.value)}")
        elif isinstance(node, IndexAssign):
            t = self._fmt_expr(node.target)
            i = self._fmt_expr(node.index)
            v = self._fmt_expr(node.value)
            self._emit(f"{t}[{i}] = {v}")
        elif isinstance(node, IndexCompoundAssign):
            t = self._fmt_expr(node.target)
            i = self._fmt_expr(node.index)
            v = self._fmt_expr(node.value)
            self._emit(f"{t}[{i}] {node.op}= {v}")
        elif isinstance(node, DestructAssign):
            names = ", ".join(node.names)
            self._emit(f"{names} = {self._fmt_expr(node.value)}")
        elif isinstance(node, PostfixIf):
            kw = "unless" if node.negated else "if"
            self._emit(f"{self._fmt_expr(node.stmt)} {kw} {self._fmt_expr(node.condition)}")
        elif isinstance(node, BeginRescue):   self._fmt_begin_rescue(node)
        elif isinstance(node, RaiseStmt):
            if node.message:
                self._emit(f"raise {self._fmt_expr(node.message)}")
            else:
                self._emit("raise")
        elif isinstance(node, RequireStmt):   self._emit(f"require {self._fmt_expr(node.path)}")
        elif isinstance(node, CaseStmt):      self._fmt_case(node)
        elif isinstance(node, NextStmt):      self._emit("next")
        elif isinstance(node, BreakStmt):
            if node.value:
                self._emit(f"break {self._fmt_expr(node.value)}")
            else:
                self._emit("break")
        else:
            # Expression statement
            self._emit(self._fmt_expr(node))

    def _fmt_body(self, body):
        for stmt in body:
            self._fmt_stmt(stmt)

    def _fmt_func_def(self, node: FuncDef):
        parts = []
        for i, p in enumerate(node.params):
            d = node.defaults[i] if i < len(node.defaults) else None
            parts.append(f"{p} = {self._fmt_expr(d)}" if d else p)
        params = f"({', '.join(parts)})" if parts else ""
        self._emit(f"def {node.name}{params}")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit("end")

    def _fmt_if(self, node: IfStmt):
        self._emit(f"if {self._fmt_expr(node.condition)}")
        self._indent()
        self._fmt_body(node.then_body)
        self._dedent()
        for cond, body in node.elsif_clauses:
            self._emit(f"elsif {self._fmt_expr(cond)}")
            self._indent()
            self._fmt_body(body)
            self._dedent()
        if node.else_body is not None:
            self._emit("else")
            self._indent()
            self._fmt_body(node.else_body)
            self._dedent()
        self._emit("end")

    def _fmt_unless(self, node: UnlessStmt):
        self._emit(f"unless {self._fmt_expr(node.condition)}")
        self._indent()
        self._fmt_body(node.then_body)
        self._dedent()
        if node.else_body:
            self._emit("else")
            self._indent()
            self._fmt_body(node.else_body)
            self._dedent()
        self._emit("end")

    def _fmt_while(self, node: WhileStmt):
        self._emit(f"while {self._fmt_expr(node.condition)}")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit("end")

    def _fmt_until(self, node: UntilStmt):
        self._emit(f"until {self._fmt_expr(node.condition)}")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit("end")

    def _fmt_do_while(self, node: DoWhileStmt):
        self._emit("do")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit(f"while {self._fmt_expr(node.condition)}")

    def _fmt_for_in(self, node: ForInStmt):
        self._emit(f"for {node.var} in {self._fmt_expr(node.iterable)}")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit("end")

    def _fmt_return(self, node: ReturnStmt):
        if node.value:
            self._emit(f"return {self._fmt_expr(node.value)}")
        else:
            self._emit("return")

    def _fmt_print(self, node: PrintStmt):
        kw = "puts" if node.newline else "print"
        self._emit(f"{kw} {self._fmt_expr(node.value)}")

    def _fmt_begin_rescue(self, node: BeginRescue):
        self._emit("begin")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        for clause in node.rescue_clauses:
            parts = ["rescue"]
            if clause.error_type:
                parts.append(clause.error_type)
            if clause.rescue_var:
                parts.append(clause.rescue_var)
            self._emit(" ".join(parts))
            self._indent()
            self._fmt_body(clause.body)
            self._dedent()
        if node.ensure_body:
            self._emit("ensure")
            self._indent()
            self._fmt_body(node.ensure_body)
            self._dedent()
        self._emit("end")

    def _fmt_case(self, node: CaseStmt):
        if node.subject:
            self._emit(f"case {self._fmt_expr(node.subject)}")
        else:
            self._emit("case")
        for values, body in node.when_clauses:
            vals = ", ".join(self._fmt_expr(v) for v in values)
            self._emit(f"when {vals}")
            self._indent()
            self._fmt_body(body)
            self._dedent()
        if node.else_body is not None:
            self._emit("else")
            self._indent()
            self._fmt_body(node.else_body)
            self._dedent()
        self._emit("end")

    # ── expressions ───────────────────────────────────────────────────────────

    def _fmt_expr(self, node) -> str:
        if node is None:
            return "nil"
        if isinstance(node, IntLiteral):    return str(node.value)
        if isinstance(node, FloatLiteral):  return repr(node.value)
        if isinstance(node, BoolLiteral):   return "true" if node.value else "false"
        if isinstance(node, NilLiteral):    return "nil"
        if isinstance(node, Identifier):    return node.name
        if isinstance(node, StringLiteral): return self._fmt_string(node)
        if isinstance(node, VectorLiteral):
            elems = ", ".join(self._fmt_expr(e) for e in node.elements)
            return f"[{elems}]"
        if isinstance(node, HashLiteral):   return self._fmt_hash(node)
        if isinstance(node, RangeLiteral):
            op = ".." if node.inclusive else "..."
            return f"{self._fmt_expr(node.start)}{op}{self._fmt_expr(node.end)}"
        if isinstance(node, BinOp):         return self._fmt_binop(node)
        if isinstance(node, UnaryOp):
            if node.op == '-':
                return f"-{self._fmt_expr(node.operand)}"
            return f"not {self._fmt_expr(node.operand)}"
        if isinstance(node, Assign):        return f"{node.name} = {self._fmt_expr(node.value)}"
        if isinstance(node, IndexAccess):
            t = self._fmt_expr(node.target)
            i = self._fmt_expr(node.index)
            return f"{t}[{i}]"
        if isinstance(node, FuncCall):      return self._fmt_func_call(node)
        if isinstance(node, MethodCall):    return self._fmt_method_call(node)
        if isinstance(node, SafeNavCall):   return self._fmt_safe_nav(node)
        if isinstance(node, PipeOp):
            return f"{self._fmt_expr(node.left)} |> {self._fmt_expr(node.right)}"
        if isinstance(node, MatchOp):
            return f"{self._fmt_expr(node.left)} =~ {self._fmt_expr(node.right)}"
        if isinstance(node, InputExpr):     return self._fmt_input(node)
        if isinstance(node, NamedArg):      return f"{node.name}: {self._fmt_expr(node.value)}"
        if isinstance(node, LambdaLiteral): return self._fmt_lambda(node)
        if isinstance(node, RegexLiteral):  return f"/{node.pattern}/{node.flags}"
        # Fallback for statement nodes used as expressions
        return "nil"

    def _fmt_string(self, node: StringLiteral) -> str:
        has_interp = any(k == 'interp' for k, _ in node.parts)
        if not has_interp:
            s = "".join(v for _, v in node.parts)
            # Use double quotes canonically
            return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
        result = '"'
        for kind, val in node.parts:
            if kind == 'literal':
                result += val.replace('\\', '\\\\').replace('"', '\\"')
            else:
                result += '#{' + val.strip() + '}'
        result += '"'
        return result

    def _fmt_hash(self, node: HashLiteral) -> str:
        if not node.pairs:
            return "{}"
        pairs = ", ".join(
            f"{self._fmt_expr(k)}: {self._fmt_expr(v)}"
            for k, v in node.pairs
        )
        return "{" + pairs + "}"

    def _fmt_binop(self, node: BinOp) -> str:
        op_map = {
            'and': 'and', 'or': 'or',
            '+': '+', '-': '-', '*': '*', '/': '/',
            '//': '//', '%': '%', '**': '**',
            '==': '==', '!=': '!=', '<': '<', '<=': '<=',
            '>': '>', '>=': '>=', '|': '|',
        }
        op = op_map.get(node.op, node.op)
        left  = self._fmt_expr(node.left)
        right = self._fmt_expr(node.right)
        return f"{left} {op} {right}"

    def _fmt_func_call(self, node: FuncCall) -> str:
        args = ", ".join(self._fmt_expr(a) for a in node.args)
        return f"{node.name}({args})"

    def _fmt_method_call(self, node: MethodCall) -> str:
        recv = self._fmt_expr(node.receiver)
        args = ""
        if node.args:
            args = "(" + ", ".join(self._fmt_expr(a) for a in node.args) + ")"
        block = ""
        if node.block:
            block = self._fmt_block(node.block)
        return f"{recv}.{node.method}{args}{block}"

    def _fmt_safe_nav(self, node: SafeNavCall) -> str:
        recv = self._fmt_expr(node.receiver)
        args = ""
        if node.args:
            args = "(" + ", ".join(self._fmt_expr(a) for a in node.args) + ")"
        block = ""
        if node.block:
            block = self._fmt_block(node.block)
        return f"{recv}&.{node.method}{args}{block}"

    def _fmt_block(self, block: Block) -> str:
        """Format a block. Single-body blocks get inline formatting."""
        params = ""
        if block.params:
            params = " |" + ", ".join(block.params) + "|"

        # Single-statement, no-nested-blocks: try inline
        if len(block.body) == 1 and not _has_nested_blocks(block.body[0]):
            inner = self._fmt_expr(block.body[0]) if not _is_stmt_only(block.body[0]) else None
            if inner:
                return f" do{params} {inner} end"

        # Multi-statement: emit on separate lines (caller handles indentation)
        # We build a mini-formatted block as a string with embedded newlines.
        lines = [f" do{params}"]
        old_depth = self._depth
        old_lines = self._lines
        self._lines = []
        self._depth = 0
        self._indent()
        self._fmt_body(block.body)
        self._dedent()
        body_lines = self._lines
        self._lines = old_lines
        self._depth = old_depth
        indent_str = INDENT * self._depth
        for bl in body_lines:
            lines.append("\n" + indent_str + bl)
        lines.append("\n" + indent_str + "end")
        return "".join(lines)

    def _fmt_lambda(self, node: LambdaLiteral) -> str:
        parts = []
        for i, p in enumerate(node.params):
            d = node.defaults[i] if i < len(node.defaults) else None
            parts.append(f"{p} = {self._fmt_expr(d)}" if d else p)
        params = ", ".join(parts)
        if len(node.body) == 1 and not _is_stmt_only(node.body[0]):
            body = self._fmt_expr(node.body[0])
            return f"->({params}) {{ {body} }}"
        # Multi-statement
        lines = [f"->({params}) do"]
        old_depth = self._depth
        old_lines = self._lines
        self._lines = []
        self._depth = 0
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        body_lines = self._lines
        self._lines = old_lines
        self._depth = old_depth
        indent_str = INDENT * self._depth
        for bl in body_lines:
            lines.append("\n" + indent_str + bl)
        lines.append("\n" + indent_str + "end")
        return "".join(lines)

    def _fmt_input(self, node: InputExpr) -> str:
        kw_map = {'str': 'input', 'int': 'input_int', 'float': 'input_float'}
        kw = kw_map[node.cast]
        if node.prompt:
            return f"{kw}({self._fmt_expr(node.prompt)})"
        return kw


def _has_nested_blocks(node) -> bool:
    """Return True if the node contains any block-bearing method calls."""
    if isinstance(node, MethodCall) and node.block:
        return True
    if isinstance(node, SafeNavCall) and node.block:
        return True
    return False


def _is_stmt_only(node) -> bool:
    """Return True if the node is a statement (not usable as an inline expression)."""
    return isinstance(node, (
        FuncDef, IfStmt, UnlessStmt, WhileStmt, UntilStmt,
        DoWhileStmt, ForInStmt, BeginRescue, CaseStmt,
        PrintStmt, DebugPrint, ReturnStmt, RaiseStmt,
        RequireStmt, NextStmt, BreakStmt,
    ))


def fmt_source(source: str) -> str:
    """Parse Frankie source and return canonically formatted source."""
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    return Formatter().format(ast)


def fmt_file(fk_file: str, write: bool = False, check: bool = False) -> bool:
    """
    Format a .fk file.
    - write=True: overwrite in-place.
    - check=True: return False (and print a message) if not already formatted.
    Returns True on success.
    """
    with open(fk_file, 'r', encoding='utf-8') as f:
        original = f.read()

    try:
        formatted = fmt_source(original)
    except Exception as e:
        print(f"[fmt] Error formatting {fk_file}: {e}", file=sys.stderr)
        return False

    if check:
        if formatted == original:
            print(f"[fmt] ✓  {fk_file}")
            return True
        else:
            print(f"[fmt] ✗  {fk_file} — not formatted (run: frankiec fmt --write {fk_file})")
            return False

    if write:
        with open(fk_file, 'w', encoding='utf-8') as f:
            f.write(formatted)
        print(f"[fmt] ✓  {fk_file}")
    else:
        print(formatted, end='')

    return True
