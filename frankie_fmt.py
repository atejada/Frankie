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
INLINE_THRESHOLD = 60   # max chars before hash/vector goes multi-line


class Formatter:
    def __init__(self, source: str = "", comments=None):
        self._depth = 0
        self._lines = []
        # Heredoc re-emission is only safe when the string is the whole
        # value of a statement (msg = <<~X / puts <<~X / return <<~X).
        # Inside argument lists or operators the terminator line would
        # swallow the trailing tokens — use escaped quotes there instead.
        self._heredoc_ok = False
        # Pre-compute set of line numbers that have a blank line immediately above them.
        # Line numbers are 1-based, matching Token.line.
        self._blank_before: set = set()
        self._src_lines = source.splitlines() if source else []
        if source:
            src_lines = self._src_lines
            for i, line in enumerate(src_lines):
                if line.strip() == "" and i + 2 <= len(src_lines):
                    # The line AFTER this blank line is (i+2) in 1-based numbering
                    self._blank_before.add(i + 2)

        # ── comment preservation (v1.22.3 bug fix) ──────────────────────────
        # The AST has no comment nodes — comments are trivia the lexer drops
        # during tokenization (see compiler/lexer.py) — so there is nothing
        # on the Program tree to walk here. Instead, every statement node
        # already carries the source line it started on (`_src_line`, set by
        # the parser), so comments are re-attached by line number: a
        # standalone `#`/`##` line is treated as a leading comment for
        # whatever statement follows it (skipping over blank lines), and a
        # `#` that trails real code on the same line is kept as a trailing
        # comment on that statement's own first emitted line.
        self._standalone_comments = {}   # line -> raw "#..." / "##..." text
        self._trailing_comments = {}     # line -> raw text (code precedes it)
        for (c_line, c_col, c_text) in (comments or []):
            line_text = self._src_lines[c_line - 1] if c_line - 1 < len(self._src_lines) else ""
            if line_text[:c_col - 1].strip() == "":
                self._standalone_comments[c_line] = c_text
            else:
                self._trailing_comments[c_line] = c_text
        self._consumed_comments: set = set()
        self._consumed_trailing: set = set()

    # ── output helpers ────────────────────────────────────────────────────────

    def _emit(self, text=""):
        if text:
            self._lines.append(INDENT * self._depth + text)
        elif self._lines and self._lines[-1] == "":
            # Never stack two blank lines — several independent rules can
            # each decide a blank belongs here (blank-after-FuncDef, a
            # preserved blank-before-statement, a preserved blank around a
            # re-attached comment block); collapsing to one keeps output
            # canonical and, importantly, keeps fmt idempotent on its own
            # output (re-running fmt on already-formatted source used to
            # compound these into ever-growing blank runs).
            return
        else:
            self._lines.append("")

    def _indent(self):  self._depth += 1
    def _dedent(self):  self._depth -= 1

    # ── comment re-attachment ────────────────────────────────────────────────

    def _is_blank_or_comment_line(self, line_no) -> bool:
        if line_no < 1 or line_no > len(self._src_lines):
            return False
        if line_no in self._standalone_comments:
            return True
        return self._src_lines[line_no - 1].strip() == ""

    def _collect_leading_comment_lines(self, stmt_line):
        """Line numbers of the standalone comment block immediately above
        stmt_line, tolerating blank lines in between but stopping at the
        first real line of code (or a comment already claimed by an earlier
        statement). Does not mark them consumed — callers decide that."""
        if stmt_line is None:
            return []
        collected = []
        line = stmt_line - 1
        while self._is_blank_or_comment_line(line):
            if line in self._standalone_comments and line not in self._consumed_comments:
                collected.append(line)
            line -= 1
        collected.reverse()
        return collected

    def _emit_stmt(self, stmt, allow_leading_blank=True):
        """Emit one statement, re-attaching any comment(s) that sat next to
        it in the original source. This is the single place `_fmt_stmt` gets
        called from (format() and _fmt_body()) so every nesting level gets
        comment support for free."""
        stmt_line = getattr(stmt, '_src_line', None)
        comment_lines = self._collect_leading_comment_lines(stmt_line)
        anchor_line = comment_lines[0] if comment_lines else stmt_line

        if allow_leading_blank and anchor_line is not None and anchor_line in self._blank_before:
            self._emit()
        for j, cl in enumerate(comment_lines):
            # Preserve a blank line the source had *between* two comment
            # paragraphs in this same leading block (distinct from the
            # blank-before-the-block and blank-after-the-block checks).
            if j > 0 and cl in self._blank_before:
                self._emit()
            self._emit(self._standalone_comments[cl])
        self._consumed_comments.update(comment_lines)
        # A blank line that separated the comment block from the code itself
        # (e.g. a file-header doc-comment followed by one blank line, then
        # the first real statement) is a second, independent blank-line fact.
        if comment_lines and stmt_line is not None and stmt_line in self._blank_before:
            self._emit()

        start_idx = len(self._lines)
        self._fmt_stmt(stmt)

        if (stmt_line is not None and stmt_line in self._trailing_comments
                and stmt_line not in self._consumed_trailing
                and start_idx < len(self._lines)):
            self._consumed_trailing.add(stmt_line)
            self._lines[start_idx] += "  " + self._trailing_comments[stmt_line]

    def unconsumed_comment_lines(self):
        """Comments that couldn't be re-attached anywhere — currently just
        a comment that's the last thing in a nested block, with nothing
        after it before the block's `end` to hang onto. Surfaced as a
        warning rather than silently dropped again."""
        missed = (set(self._standalone_comments) - self._consumed_comments) | \
                 (set(self._trailing_comments) - self._consumed_trailing)
        return sorted(missed)

    def _fmt_value(self, node) -> str:
        """Format a statement-level value, where heredoc form is safe."""
        if isinstance(node, StringLiteral):
            self._heredoc_ok = True
            try:
                return self._fmt_string(node)
            finally:
                self._heredoc_ok = False
        return self._fmt_expr(node)

    def format(self, program: Program) -> str:
        for i, node in enumerate(program.body):
            self._emit_stmt(node, allow_leading_blank=(i > 0))
            # Blank line after top-level function definitions for readability
            if isinstance(node, FuncDef) and i < len(program.body) - 1:
                if not isinstance(program.body[i + 1], FuncDef):
                    self._emit()
        # A standalone comment block after the very last statement (e.g. a
        # footer/license note) has no following statement to attach to —
        # flush it here instead of leaving it unconsumed.
        trailing = self._collect_leading_comment_lines(len(self._src_lines) + 1)
        if trailing:
            if trailing[0] in self._blank_before:
                self._emit()
            for j, cl in enumerate(trailing):
                if j > 0 and cl in self._blank_before:
                    self._emit()
                self._emit(self._standalone_comments[cl])
            self._consumed_comments.update(trailing)
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
        elif isinstance(node, Assign):        self._emit(f"{node.name} = {self._fmt_value(node.value)}")
        elif isinstance(node, ConstAssign):
            # Preserve the explicit const keyword for non-ALL_CAPS names
            # (ALL_CAPS assignment re-parses as a constant on its own)
            kw = "" if node.name == node.name.upper() else "const "
            self._emit(f"{kw}{node.name} = {self._fmt_expr(node.value)}")
        elif isinstance(node, OrAssign):      self._emit(f"{node.name} ||= {self._fmt_expr(node.value)}")
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
            names = ", ".join(
                ("*" + n if i == node.splat_index else n)
                for i, n in enumerate(node.names))
            self._emit(f"{names} = {self._fmt_expr(node.value)}")
        elif isinstance(node, HashDestructAssign):
            keys = ", ".join(node.keys)
            self._emit(f"{{{keys}}} = {self._fmt_expr(node.value)}")
        elif isinstance(node, PostfixIf):
            kw = "unless" if node.negated else "if"
            self._emit(f"{self._fmt_postfix_inner(node.stmt)} {kw} {self._fmt_expr(node.condition)}")
        elif isinstance(node, BeginRescue):   self._fmt_begin_rescue(node)
        elif isinstance(node, RaiseStmt):
            if getattr(node, 'error_type', None):
                if node.message is not None:
                    self._emit(f"raise {node.error_type}, {self._fmt_expr(node.message)}")
                else:
                    self._emit(f"raise {node.error_type}")
            elif node.message:
                self._emit(f"raise {self._fmt_expr(node.message)}")
            else:
                self._emit("raise")
        elif isinstance(node, RequireStmt):   self._emit(f"require {self._fmt_expr(node.path)}")
        elif isinstance(node, StitchStmt):    self._emit(f"stitch {self._fmt_expr(node.name)}")
        elif isinstance(node, ErrorDef):      self._emit(f"error {node.name}")
        elif isinstance(node, ImportStmt):
            alias = f" as {node.alias}" if node.alias else ""
            self._emit(f"import {self._fmt_expr(node.path)}{alias}")
        elif isinstance(node, RecordDef):
            self._emit(f"record {node.name}({', '.join(node.fields)})")
        elif isinstance(node, EnumDef):
            self._emit(f"enum {node.name}({', '.join(node.members)})")
        elif isinstance(node, BreakpointStmt):
            self._emit("breakpoint")
        elif isinstance(node, LoopStmt):
            label = self._fmt_label(getattr(node, 'label', None))
            self._emit(f"loop{label} do")
            self._indent()
            self._fmt_body(node.body)
            self._dedent()
            self._emit("end")
        elif isinstance(node, SpawnBlock):
            self._emit("spawn do")
            self._indent()
            self._fmt_body(node.body)
            self._dedent()
            self._emit("end")
        elif isinstance(node, TimeoutBlock):
            self._emit(f"timeout({self._fmt_expr(node.seconds)}) do")
            self._indent()
            self._fmt_body(node.body)
            self._dedent()
            self._emit("end")
        elif isinstance(node, CaseStmt):      self._fmt_case(node)
        elif isinstance(node, NextStmt):
            label = getattr(node, 'label', None)
            self._emit(f"next :{label}" if label else "next")
        elif isinstance(node, BreakStmt):
            label = getattr(node, 'label', None)
            if label:
                self._emit(f"break :{label}")
            elif node.value:
                self._emit(f"break {self._fmt_expr(node.value)}")
            else:
                self._emit("break")
        else:
            # Expression statement
            self._emit(self._fmt_expr(node))

    def _fmt_postfix_inner(self, stmt) -> str:
        """Render the statement half of `stmt if cond` (v1.19 fix —
        statements like return/break/raise used to collapse to 'nil')."""
        if isinstance(stmt, ReturnStmt):
            return f"return {self._fmt_expr(stmt.value)}" if stmt.value else "return"
        if isinstance(stmt, BreakStmt):
            label = getattr(stmt, 'label', None)
            if label:
                return f"break :{label}"
            return f"break {self._fmt_expr(stmt.value)}" if stmt.value else "break"
        if isinstance(stmt, NextStmt):
            label = getattr(stmt, 'label', None)
            return f"next :{label}" if label else "next"
        if isinstance(stmt, BreakpointStmt):
            return "breakpoint"
        if isinstance(stmt, RaiseStmt):
            if getattr(stmt, 'error_type', None):
                if stmt.message is not None:
                    return f"raise {stmt.error_type}, {self._fmt_expr(stmt.message)}"
                return f"raise {stmt.error_type}"
            return f"raise {self._fmt_expr(stmt.message)}" if stmt.message else "raise"
        if isinstance(stmt, PrintStmt):
            kw = "puts" if stmt.newline else "print"
            return f"{kw} {self._fmt_expr(stmt.value)}"
        if isinstance(stmt, DebugPrint):
            return f"p {self._fmt_expr(stmt.value)}"
        return self._fmt_expr(stmt)

    def _fmt_body(self, body):
        for i, stmt in enumerate(body):
            # Blank-line and comment preservation both live in _emit_stmt now;
            # never emit a leading blank before the very first stmt in a body.
            self._emit_stmt(stmt, allow_leading_blank=(i > 0))

    def _fmt_func_def(self, node: FuncDef):
        parts = []
        ptypes = getattr(node, 'param_types', None)
        for i, p in enumerate(node.params):
            d = node.defaults[i] if i < len(node.defaults) else None
            t = ptypes[i] if ptypes and i < len(ptypes) else None
            if t and d is not None:
                parts.append(f"{p}: {t} = {self._fmt_expr(d)}")
            elif t:
                parts.append(f"{p}: {t}")
            elif d is not None:
                parts.append(f"{p} = {self._fmt_expr(d)}")
            else:
                parts.append(p)
        params = f"({', '.join(parts)})" if parts else ""
        ret = getattr(node, 'return_type', None)
        ret_str = f" -> {ret}" if ret else ""
        self._emit(f"def {node.name}{params}{ret_str}")
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

    def _fmt_label(self, label) -> str:
        """v1.22: render an optional loop label as ' :name', else ''."""
        return f" :{label}" if label else ""

    def _fmt_while(self, node: WhileStmt):
        self._emit(f"while{self._fmt_label(getattr(node, 'label', None))} {self._fmt_expr(node.condition)}")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit("end")

    def _fmt_until(self, node: UntilStmt):
        self._emit(f"until{self._fmt_label(getattr(node, 'label', None))} {self._fmt_expr(node.condition)}")
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
        label = self._fmt_label(getattr(node, 'label', None))
        self._emit(f"for{label} {node.var} in {self._fmt_expr(node.iterable)}")
        self._indent()
        self._fmt_body(node.body)
        self._dedent()
        self._emit("end")

    def _fmt_return(self, node: ReturnStmt):
        if node.value:
            self._emit(f"return {self._fmt_value(node.value)}")
        else:
            self._emit("return")

    def _fmt_print(self, node: PrintStmt):
        kw = "puts" if node.newline else "print"
        self._emit(f"{kw} {self._fmt_value(node.value)}")

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
        if isinstance(node, FloatLiteral):  return repr(node.value)  # 1e-06 etc. lex fine since v1.18
        if isinstance(node, BoolLiteral):   return "true" if node.value else "false"
        if isinstance(node, NilLiteral):    return "nil"
        if isinstance(node, Identifier):    return node.name
        if isinstance(node, StringLiteral): return self._fmt_string(node)
        if isinstance(node, VectorLiteral):
            elem_strs = [self._fmt_expr(e) for e in node.elements]
            inline = "[" + ", ".join(elem_strs) + "]"
            if len(inline) <= INLINE_THRESHOLD:
                return inline
            indent = INDENT * (self._depth + 1)
            close  = INDENT * self._depth
            body   = (",\n" + indent).join(elem_strs)
            return "[\n" + indent + body + "\n" + close + "]"
        if isinstance(node, HashLiteral):   return self._fmt_hash(node)
        if isinstance(node, RangeLiteral):
            op = ".." if node.inclusive else "..."
            return f"{self._fmt_range_operand(node.start)}{op}{self._fmt_range_operand(node.end)}"
        if isinstance(node, BinOp):         return self._fmt_binop(node)
        if isinstance(node, UnaryOp):
            if node.op == '-':
                return f"-{self._fmt_expr(node.operand)}"
            return f"not {self._fmt_expr(node.operand)}"
        if isinstance(node, Assign):        return f"{node.name} = {self._fmt_expr(node.value)}"
        if isinstance(node, IndexAccess):
            t = self._fmt_receiver(node.target)   # parens around (a | b)["x"] etc.
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
        if isinstance(node, IfExpr):
            cond = self._fmt_expr(node.condition)
            then = self._fmt_expr(node.then_expr)
            els  = self._fmt_expr(node.else_expr) if node.else_expr is not None else "nil"
            return f"if {cond} then {then} else {els} end"
        if isinstance(node, TernaryExpr):
            cond = self._fmt_expr(node.condition)
            then = self._fmt_expr(node.then_expr)
            els  = self._fmt_expr(node.else_expr)
            return f"{cond} ? {then} : {els}"
        if isinstance(node, CompoundAssign):
            return f"{node.name} {node.op}= {self._fmt_expr(node.value)}"
        if isinstance(node, OrAssign):
            return f"{node.name} ||= {self._fmt_expr(node.value)}"
        if isinstance(node, IndexAssign):
            return (f"{self._fmt_expr(node.target)}[{self._fmt_expr(node.index)}]"
                    f" = {self._fmt_expr(node.value)}")
        if isinstance(node, IndexCompoundAssign):
            return (f"{self._fmt_expr(node.target)}[{self._fmt_expr(node.index)}]"
                    f" {node.op}= {self._fmt_expr(node.value)}")
        if isinstance(node, AwaitExpr):
            return f"await {self._fmt_expr(node.expr)}"
        # Fallback for statement nodes used as expressions
        return "nil"

    def _fmt_string(self, node: StringLiteral) -> str:
        # Check if this originated from a heredoc (multi-line literal with leading newline pattern)
        has_interp = any(k == 'interp' for k, _ in node.parts)
        raw_text = "".join(v for k, v in node.parts if k == 'literal')

        # Multi-line string in a nested position (call args, operators, ...):
        # heredoc form is unsafe there — emit an escaped quoted string.
        if '\n' in raw_text and not self._heredoc_ok:
            result = '"'
            for kind, val in node.parts:
                if kind == 'literal':
                    result += (val.replace('\\', '\\\\').replace('"', '\\"')
                                  .replace('\n', '\\n').replace('\t', '\\t'))
                else:
                    result += '#{' + val.strip() + '}'
            return result + '"'

        # Heredoc detection: literal content contains newlines and was indented
        # We preserve the body verbatim and re-emit as <<~HEREDOC
        if '\n' in raw_text and not has_interp:
            # Emit as a plain heredoc with indent-stripping form
            delim = "HEREDOC"
            lines = raw_text.split('\n')
            # Strip trailing empty line from heredoc body
            while lines and lines[-1] == '':
                lines.pop()
            body = '\n'.join('  ' + l for l in lines)
            return f"<<~{delim}\n{body}\n{delim}"

        if not has_interp:
            s = "".join(v for _, v in node.parts)
            return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

        # Interpolated: check for multiline
        if '\n' in raw_text:
            # Preserve as heredoc with interpolation
            delim = "HEREDOC"
            result_parts = []
            for kind, val in node.parts:
                if kind == 'literal':
                    result_parts.append(val)
                else:
                    result_parts.append('#{' + val.strip() + '}')
            body_raw = "".join(result_parts)
            lines = body_raw.split('\n')
            while lines and lines[-1] == '':
                lines.pop()
            body = '\n'.join('  ' + l for l in lines)
            return f"<<~{delim}\n{body}\n{delim}"

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
        pairs_strs = []
        for k, v in node.pairs:
            # Preserve symbol key syntax: host: "val" not "host": "val"
            if isinstance(k, StringLiteral) and k.is_symbol:
                key_str = k.parts[0][1] + ":"
            else:
                key_str = self._fmt_expr(k) + ":"
            pairs_strs.append(f"{key_str} {self._fmt_expr(v)}")
        inline = "{" + ", ".join(pairs_strs) + "}"
        if len(inline) <= INLINE_THRESHOLD:
            return inline
        # Multi-line: one pair per line, indented one level relative to current
        indent = INDENT * (self._depth + 1)
        close  = INDENT * self._depth
        body   = (",\n" + indent).join(pairs_strs)
        return "{\n" + indent + body + "\n" + close + "}"

    # Precedence levels, matching the parser's climb (compiler/parser.py:
    # parse_or → parse_and → parse_hash_merge('|') → parse_comparison →
    # parse_addition → parse_multiplication → parse_power). Higher binds
    # tighter. Anything not listed here that can appear as an operand
    # (ternary, if-expr, pipe, match, range, lambda, assign forms) is
    # looser than every operator, hence the -1 floor in _node_prec.
    _BINOP_PREC = {
        'or': 1, 'and': 2, '|': 3,
        '==': 4, '!=': 4, '<': 4, '<=': 4, '>': 4, '>=': 4,
        '+': 5, '-': 5,
        '*': 6, '/': 6, '//': 6, '%': 6,
        '**': 8,
    }

    def _node_prec(self, node) -> int:
        if isinstance(node, BinOp):
            return self._BINOP_PREC.get(node.op, 4)
        if isinstance(node, UnaryOp):
            return 2 if node.op == 'not' else 7
        if isinstance(node, (RangeLiteral, TernaryExpr, IfExpr, PipeOp, MatchOp,
                             Assign, CompoundAssign, OrAssign, LambdaLiteral)):
            return -1
        return 99   # atoms, calls, literals — never need parens as an operand

    def _fmt_range_operand(self, node) -> str:
        """Render one end of a RangeLiteral. A range's start/end are each
        parsed via parse_unary (compiler/parser.py) — i.e. they can only
        naturally be a unary-minus or tighter (power, postfix, primary)
        expression without parens; anything looser must be parenthesized
        or it silently regroups on re-parse. Same v1.22.2 bug class as
        _fmt_operand below, caught on stitches/frankiestring.fk's
        `0..(n - suffix.length - 1)`, which fmt was rendering as
        `0..n - suffix.length - 1` — parses back as `(0..n) - suffix.length
        - 1`, an entirely different expression."""
        text = self._fmt_expr(node)
        if self._node_prec(node) < 7:
            return f"({text})"
        return text

    def _fmt_operand(self, child, parent_prec: int, parent_op: str, is_right: bool) -> str:
        """Render one side of a BinOp, parenthesizing whenever leaving them
        out would let the operand's own operator silently re-bind to a
        different precedence on re-parse (e.g. `(budget - elapsed) / 1000.0`
        must never come back out as `budget - elapsed / 1000.0` — a real
        v1.22.2 bug this fixes: fmt was dropping exactly this kind of
        'redundant-looking' paren and quietly changing what the line did)."""
        text = self._fmt_expr(child)
        child_prec = self._node_prec(child)
        if child_prec < parent_prec:
            return f"({text})"
        if child_prec == parent_prec:
            # Same precedence: safe without parens only on the side that
            # matches the group's associativity — ** is right-associative
            # (its left side needs parens at equal precedence), every other
            # operator here is left-associative (its right side does).
            # `a - (b - c) != a - b - c`, `a ** (b ** c) != (a ** b) ** c`.
            needs = (not is_right) if parent_op == '**' else is_right
            if needs:
                return f"({text})"
        return text

    def _fmt_binop(self, node: BinOp) -> str:
        op_map = {
            'and': 'and', 'or': 'or',
            '+': '+', '-': '-', '*': '*', '/': '/',
            '//': '//', '%': '%', '**': '**',
            '==': '==', '!=': '!=', '<': '<', '<=': '<=',
            '>': '>', '>=': '>=', '|': '|',
        }
        op = op_map.get(node.op, node.op)
        my_prec = self._BINOP_PREC.get(node.op, 4)
        left  = self._fmt_operand(node.left, my_prec, node.op, is_right=False)
        right = self._fmt_operand(node.right, my_prec, node.op, is_right=True)
        return f"{left} {op} {right}"

    def _fmt_func_call(self, node: FuncCall) -> str:
        args = ", ".join(self._fmt_expr(a) for a in node.args)
        block = ""
        if node.block:
            block = self._fmt_block(node.block)
        # test "name" do / benchmark ["label"] do — keep paren-less form
        if (node.name == 'test' and node.args
                and isinstance(node.args[0], StringLiteral) and node.block):
            return f"test {args}{block}"
        if node.name == 'benchmark' and node.block:
            return f"benchmark {args}{block}" if args else f"benchmark{block}"
        return f"{node.name}({args}){block}"

    # Receivers that bind looser than `.` must be parenthesized:
    # (1..10).step(3), (a + b).abs, (cond ? x : y).to_s ...
    _PAREN_RECV = None  # populated below the class (needs node classes)

    def _fmt_receiver(self, receiver) -> str:
        recv = self._fmt_expr(receiver)
        if isinstance(receiver, (RangeLiteral, BinOp, UnaryOp, TernaryExpr,
                                 IfExpr, PipeOp, MatchOp, Assign, LambdaLiteral)):
            return f"({recv})"
        return recv

    def _fmt_method_call(self, node: MethodCall) -> str:
        recv = self._fmt_receiver(node.receiver)
        args = ""
        if node.args:
            args = "(" + ", ".join(self._fmt_expr(a) for a in node.args) + ")"
        block = ""
        if node.block:
            block = self._fmt_block(node.block)
        return f"{recv}.{node.method}{args}{block}"

    def _fmt_safe_nav(self, node: SafeNavCall) -> str:
        recv = self._fmt_receiver(node.receiver)
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
    """Return True if the node is a statement (not usable as an inline expression).

    v1.21 fix: this list was missing several statement kinds — Assign,
    PostfixIf, and friends — which meant a single-statement block body like
    `do |s| hit = true if collide?(...) end` fell through to _fmt_expr(),
    which doesn't know how to render a statement and silently emitted
    'nil', discarding the actual logic. Any statement type not safely
    representable via _fmt_expr must be listed here so the formatter falls
    back to the (correct) multi-line block form instead."""
    return isinstance(node, (
        FuncDef, IfStmt, UnlessStmt, WhileStmt, UntilStmt,
        DoWhileStmt, ForInStmt, BeginRescue, CaseStmt,
        PrintStmt, DebugPrint, ReturnStmt, RaiseStmt,
        RequireStmt, NextStmt, BreakStmt,
        PostfixIf, Assign, IndexAssign, CompoundAssign, IndexCompoundAssign,
        DestructAssign, HashDestructAssign, BreakpointStmt, LoopStmt,
        SpawnBlock, TimeoutBlock, StitchStmt, ImportStmt, ErrorDef,
        RecordDef, EnumDef,
    ))


def fmt_source(source: str) -> str:
    """Parse Frankie source and return canonically formatted source."""
    return fmt_source_with_warnings(source)[0]


def fmt_source_with_warnings(source: str):
    """Same as fmt_source, but also returns the (1-based) source line
    numbers of any comment that couldn't be re-attached to a statement —
    currently just a comment left dangling at the end of a nested block,
    with nothing after it before that block's `end`. Callers that don't
    care can use fmt_source(); frankiec fmt uses this to warn instead of
    silently dropping them the way it used to."""
    from compiler.lexer import Lexer
    from compiler.parser import Parser
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    ast = Parser(tokens).parse()
    fmt = Formatter(source, lexer.comments)
    formatted = fmt.format(ast)
    return formatted, fmt.unconsumed_comment_lines()


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
        formatted, unpreserved = fmt_source_with_warnings(original)
    except Exception as e:
        print(f"[fmt] Error formatting {fk_file}: {e}", file=sys.stderr)
        return False

    if unpreserved:
        lines = ", ".join(str(l) for l in unpreserved)
        print(f"[fmt] warning: {fk_file}: comment(s) on line(s) {lines} "
              f"are dangling at the end of a block and could not be "
              f"re-attached — left out of the formatted output", file=sys.stderr)

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
