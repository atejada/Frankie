"""
Frankie Static Analyzer (v1.17) — finds problems before the program runs.

Used by `frankiec check`:
  * undefined variables and functions        (error)
  * wrong number of arguments                (error)
  * unused local variables                   (warning)

The analyzer is flow-insensitive within a scope: a name assigned anywhere
in a scope counts as defined for that whole scope. This deliberately avoids
false positives on loops and conditional assignment, at the cost of not
catching use-before-assignment.

require/stitch/import statements with literal paths are resolved and their
definitions collected, so multi-file programs check cleanly. If a path can't
be resolved (dynamic expression, missing file), the analyzer switches to
"open world" mode and downgrades undefined-name errors to warnings.
"""

import os
from .ast_nodes import *
from .lexer import Lexer, LexError
from .parser import Parser, ParseError


class Issue:
    """A single analyzer finding."""
    def __init__(self, severity, line, message):
        self.severity = severity   # 'error' | 'warning'
        self.line = line           # int or None
        self.message = message

    def __repr__(self):
        return f"Issue({self.severity}, L{self.line}, {self.message!r})"


# Names that codegen treats specially but that may not exist in the stdlib
_EXTRA_KNOWN = {
    'puts', 'print', 'p', 'pp', 'zip', 'times', 'test',
    'sum', 'mean', 'min', 'max', 'abs', 'sqrt', 'floor', 'ceil', 'round',
    'length', 'vec', 'to_int', 'to_float', 'to_str', 'range_vec',
    'input', 'input_int', 'input_float', 'shell', 'exec_cmd',
    'spawn', 'timeout', 'loop', 'dotenv', 'smtp_send',
}

_BUILTIN_ERROR_NAMES = {
    'RuntimeError', 'TypeError', 'ValueError', 'ZeroDivisionError',
    'IndexError', 'KeyError', 'IOError', 'FileNotFoundError',
    'OverflowError', 'NameError', 'AttributeError', 'StopIteration',
    'Exception', 'Error', 'TimeoutError',
}


class Analyzer:
    def __init__(self, source_path=None):
        self.issues = []
        self.source_path = source_path
        self.known = set(_EXTRA_KNOWN)
        self.func_sigs = {}       # name → (min_args, max_args)
        self.open_world = False   # True when a require/stitch can't be resolved
        self._visited_files = set()
        self._usage = set()       # every name referenced anywhere
        self._load_stdlib_names()

    # ── Setup ────────────────────────────────────────────────────────────────

    def _load_stdlib_names(self):
        """Every public stdlib symbol is a known global."""
        try:
            import sys
            frankie_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if frankie_dir not in sys.path:
                sys.path.insert(0, frankie_dir)
            import frankie_stdlib as _std
            for k in vars(_std):
                if not k.startswith('__'):
                    self.known.add(k)
        except Exception:
            # Analyzer must never crash the check command
            self.open_world = True

    # ── Public API ───────────────────────────────────────────────────────────

    def analyze(self, program):
        """Analyze a parsed Program; returns a list of Issue objects."""
        module_scope = {}
        self._collect_defs(program.body, module_scope)
        self._walk_body(program.body, [module_scope], line=None)
        self.issues.sort(key=lambda i: (i.line or 0))
        return self.issues

    # ── Definition collection (flow-insensitive, per scope) ─────────────────

    def _collect_defs(self, body, scope, into_blocks=True):
        """Collect every name defined anywhere in this scope.
        scope: dict name → first definition line (or None)."""
        for stmt in body:
            self._collect_one(stmt, scope, into_blocks)

    def _define(self, scope, name, node):
        if name not in scope:
            scope[name] = getattr(node, '_src_line', None)

    def _collect_one(self, node, scope, into_blocks):
        if node is None:
            return
        if isinstance(node, FuncDef):
            self._define(scope, node.name, node)
            n_required = sum(1 for d in node.defaults if d is None) \
                if node.defaults else len(node.params)
            self.func_sigs[node.name] = (n_required, len(node.params))
            return  # body is its own scope — handled in walk phase
        if isinstance(node, (Assign, CompoundAssign, OrAssign, ConstAssign)):
            self._define(scope, node.name, node)
            self._collect_expr_defs(node.value, scope, into_blocks)
            return
        if isinstance(node, DestructAssign):
            for n in node.names:
                self._define(scope, n, node)
            return
        if isinstance(node, HashDestructAssign):
            for k in node.keys:
                self._define(scope, k, node)
            return
        if isinstance(node, ForInStmt):
            self._define(scope, node.var, node)
            self._collect_defs(node.body, scope, into_blocks)
            return
        if isinstance(node, RecordDef):
            self._define(scope, node.name, node)
            self.func_sigs[node.name] = (len(node.fields), len(node.fields))
            return
        if isinstance(node, ErrorDef):
            self._define(scope, node.name, node)
            return
        if isinstance(node, EnumDef):
            self._define(scope, node.name, node)
            return
        if isinstance(node, BreakpointStmt):
            return
        if isinstance(node, ImportStmt):
            alias = node.alias
            if alias is None and isinstance(node.path, StringLiteral):
                raw = "".join(v for k, v in node.path.parts if k == 'literal')
                alias = raw.replace('\\', '/').rsplit('/', 1)[-1]
                alias = alias[:-3] if alias.endswith('.fk') else alias
            if alias:
                self._define(scope, alias, node)
            return
        if isinstance(node, RequireStmt):
            self._resolve_required_file(node.path, scope, kind='require')
            return
        if isinstance(node, StitchStmt):
            self._resolve_required_file(node.name, scope, kind='stitch')
            return
        if isinstance(node, BeginRescue):
            self._collect_defs(node.body, scope, into_blocks)
            for clause in node.rescue_clauses:
                if clause.rescue_var:
                    self._define(scope, clause.rescue_var, node)
                self._collect_defs(clause.body, scope, into_blocks)
            if node.ensure_body:
                self._collect_defs(node.ensure_body, scope, into_blocks)
            return
        if isinstance(node, IfStmt):
            self._collect_expr_defs(node.condition, scope, into_blocks)
            self._collect_defs(node.then_body, scope, into_blocks)
            for _, eb in node.elsif_clauses:
                self._collect_defs(eb, scope, into_blocks)
            if node.else_body:
                self._collect_defs(node.else_body, scope, into_blocks)
            return
        if isinstance(node, UnlessStmt):
            self._collect_defs(node.then_body, scope, into_blocks)
            if node.else_body:
                self._collect_defs(node.else_body, scope, into_blocks)
            return
        if isinstance(node, (WhileStmt, UntilStmt, DoWhileStmt, LoopStmt,
                             SpawnBlock)):
            self._collect_defs(node.body, scope, into_blocks)
            return
        if isinstance(node, TimeoutBlock):
            self._collect_defs(node.body, scope, into_blocks)
            return
        if isinstance(node, CaseStmt):
            for _, b in node.when_clauses:
                self._collect_defs(b, scope, into_blocks)
            if node.else_body:
                self._collect_defs(node.else_body, scope, into_blocks)
            return
        if isinstance(node, PostfixIf):
            self._collect_one(node.stmt, scope, into_blocks)
            return
        # Expression statements may carry blocks whose bodies assign in
        # the enclosing scope (e.g. .each do |x| total += x end)
        self._collect_expr_defs(node, scope, into_blocks)

    def _collect_expr_defs(self, node, scope, into_blocks):
        """Find assignments hiding inside expression trees (walrus-style
        Assign nodes, iterator blocks)."""
        if node is None or not isinstance(node, Node):
            return
        if isinstance(node, Assign):
            self._define(scope, node.name, node)
            self._collect_expr_defs(node.value, scope, into_blocks)
            return
        if isinstance(node, LambdaLiteral):
            return  # own scope
        if isinstance(node, Block):
            if into_blocks:
                self._collect_defs(node.body, scope, into_blocks)
            return
        for value in vars(node).values():
            if isinstance(value, Node):
                self._collect_expr_defs(value, scope, into_blocks)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, Node):
                        self._collect_expr_defs(item, scope, into_blocks)
                    elif isinstance(item, tuple):
                        for sub in item:
                            if isinstance(sub, Node):
                                self._collect_expr_defs(sub, scope, into_blocks)
                            elif isinstance(sub, list):
                                for s2 in sub:
                                    if isinstance(s2, Node):
                                        self._collect_expr_defs(s2, scope, into_blocks)

    # ── Multi-file resolution ────────────────────────────────────────────────

    def _literal_string(self, node):
        if isinstance(node, StringLiteral) and all(
                k == 'literal' for k, _ in node.parts):
            return "".join(v for _, v in node.parts)
        return None

    def _resolve_required_file(self, path_node, scope, kind):
        raw = self._literal_string(path_node)
        if raw is None:
            self.open_world = True
            return
        candidates = []
        if kind == 'stitch':
            candidates.append(os.path.join(os.getcwd(), 'stitches', raw + '.fk'))
            candidates.append(os.path.join(os.path.expanduser('~'),
                                           '.frankie', 'stitches', raw + '.fk'))
        else:
            fname = raw if raw.endswith('.fk') else raw + '.fk'
            if self.source_path:
                candidates.append(os.path.join(
                    os.path.dirname(os.path.abspath(self.source_path)), fname))
            candidates.append(os.path.join(os.getcwd(), fname))
        target = next((c for c in candidates if os.path.exists(c)), None)
        if target is None:
            self.open_world = True
            return
        abs_target = os.path.abspath(target)
        if abs_target in self._visited_files:
            return
        self._visited_files.add(abs_target)
        try:
            with open(abs_target, 'r', encoding='utf-8') as f:
                src = f.read()
            sub_ast = Parser(Lexer(src).tokenize()).parse()
        except (OSError, LexError, ParseError):
            self.open_world = True
            return
        # Merge the file's top-level definitions into the current scope
        old_source_path = self.source_path
        self.source_path = abs_target
        self._collect_defs(sub_ast.body, scope)
        self.source_path = old_source_path

    # ── Usage walk ───────────────────────────────────────────────────────────

    def _lookup(self, name, scopes):
        if name in self.known:
            return True
        return any(name in s for s in scopes)

    def _report_undefined(self, name, line, what='variable or function'):
        severity = 'warning' if self.open_world else 'error'
        self.issues.append(Issue(
            severity, line,
            f"Undefined {what}: {name!r}"))

    def _walk_body(self, body, scopes, line):
        for stmt in body:
            stmt_line = getattr(stmt, '_src_line', line)
            self._walk(stmt, scopes, stmt_line)

    def _walk(self, node, scopes, line):
        if node is None or not isinstance(node, Node):
            return
        line = getattr(node, '_src_line', line)

        if isinstance(node, Identifier):
            self._usage.add(node.name)
            if not self._lookup(node.name, scopes):
                self._report_undefined(node.name, line)
            return

        if isinstance(node, FuncDef):
            # New function scope: params + locals
            fn_scope = {p: line for p in node.params}
            for d in node.defaults or []:
                self._walk(d, scopes, line)
            local_defs = {}
            self._collect_defs(node.body, local_defs)
            fn_scope.update(local_defs)
            usage_before = set(self._usage)
            self._walk_body(node.body, scopes + [fn_scope], line)
            # Unused local variables (not params, not _-prefixed, not consts)
            for name, def_line in local_defs.items():
                if name.startswith('_') or name in node.params:
                    continue
                if name.upper() == name:
                    continue
                if name not in self._usage - usage_before and name not in usage_before:
                    self.issues.append(Issue(
                        'warning', def_line,
                        f"Unused variable {name!r} in function {node.name!r}"))
            return

        if isinstance(node, LambdaLiteral):
            lam_scope = {p: line for p in node.params}
            for d in node.defaults or []:
                if d is not None:
                    self._walk(d, scopes, line)
            local_defs = {}
            self._collect_defs(node.body, local_defs)
            lam_scope.update(local_defs)
            self._walk_body(node.body, scopes + [lam_scope], line)
            return

        if isinstance(node, Block):
            blk_scope = {p: line for p in node.params}
            self._walk_body(node.body, scopes + [blk_scope], line)
            return

        if isinstance(node, FuncCall):
            self._usage.add(node.name)
            n_args = len(node.args) + (1 if node.block is not None else 0)
            has_named = any(isinstance(a, NamedArg) for a in node.args)
            if node.name in self.func_sigs:
                lo, hi = self.func_sigs[node.name]
                if node.block is not None:
                    hi += 1   # the block is passed as an extra argument
                if has_named:
                    if n_args > hi:
                        self.issues.append(Issue(
                            'error', line,
                            f"{node.name}() takes at most {hi} argument(s), got {n_args}"))
                elif not (lo <= n_args <= hi):
                    expected = str(lo) if lo == hi else f"{lo}..{hi}"
                    self.issues.append(Issue(
                        'error', line,
                        f"{node.name}() expects {expected} argument(s), got {n_args}"))
            elif not self._lookup(node.name, scopes):
                self._report_undefined(node.name, line, what='function')
            for a in node.args:
                self._walk(a.value if isinstance(a, NamedArg) else a, scopes, line)
            if node.block:
                self._walk(node.block, scopes, line)
            return

        if isinstance(node, (MethodCall, SafeNavCall)):
            self._walk(node.receiver, scopes, line)
            for a in node.args:
                self._walk(a.value if isinstance(a, NamedArg) else a, scopes, line)
            if node.block:
                self._walk(node.block, scopes, line)
            return

        if isinstance(node, StringLiteral):
            for kind, val in node.parts:
                if kind == 'interp' and val.strip():
                    try:
                        sub = Parser(Lexer(val.strip()).tokenize()).parse_expr()
                        self._walk(sub, scopes, line)
                    except (LexError, ParseError):
                        pass   # malformed interp caught at compile time
            return

        if isinstance(node, PipeOp):
            self._walk(node.left, scopes, line)
            right = node.right
            if isinstance(right, Identifier):
                self._usage.add(right.name)
                if not self._lookup(right.name, scopes):
                    self._report_undefined(right.name, line, what='function')
            elif isinstance(right, FuncCall):
                # pipe target receives the left value as an extra first arg
                self._usage.add(right.name)
                if right.name in self.func_sigs:
                    lo, hi = self.func_sigs[right.name]
                    n_args = len(right.args) + 1
                    if not (lo <= n_args <= hi):
                        expected = str(lo) if lo == hi else f"{lo}..{hi}"
                        self.issues.append(Issue(
                            'error', line,
                            f"{right.name}() expects {expected} argument(s), "
                            f"got {n_args} (including piped value)"))
                elif not self._lookup(right.name, scopes):
                    self._report_undefined(right.name, line, what='function')
                for a in right.args:
                    self._walk(a, scopes, line)
            else:
                self._walk(right, scopes, line)
            return

        if isinstance(node, (RequireStmt, StitchStmt, ImportStmt,
                             RecordDef, ErrorDef, EnumDef, BreakpointStmt)):
            return   # handled during collection

        if isinstance(node, BeginRescue):
            self._walk_body(node.body, scopes, line)
            for clause in node.rescue_clauses:
                self._walk_body(clause.body, scopes, line)
            if node.ensure_body:
                self._walk_body(node.ensure_body, scopes, line)
            return

        # Generic fallback: walk all Node children
        for value in vars(node).values():
            if isinstance(value, Node):
                self._walk(value, scopes, line)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, Node):
                        self._walk(item, scopes, line)
                    elif isinstance(item, tuple):
                        for sub in item:
                            if isinstance(sub, Node):
                                self._walk(sub, scopes, line)
                            elif isinstance(sub, list):
                                self._walk_body(sub, scopes, line)


def analyze_source(source, source_path=None):
    """Convenience: lex + parse + analyze. Returns (issues, parse_error)."""
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    analyzer = Analyzer(source_path=source_path)
    return analyzer.analyze(program)
