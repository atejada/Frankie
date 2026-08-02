"""
frankie_lsp.py — Frankie Language Server (v1.18)

A Language Server Protocol implementation over stdio, built entirely on the
Python standard library — zero dependencies, like everything else in Frankie.

Capabilities:
  * live diagnostics  — lex/parse errors + the v1.17 static analyzer
                        (undefined names, wrong arity, unused variables)
  * completion        — keywords, stdlib functions, user-defined symbols
  * hover             — signatures + documentation for stdlib and user code

Start it with:  frankiec lsp

Editor setup examples live in docs/20_v118_features.md (VS Code, Neovim,
Helix, Zed — anything that speaks LSP).
"""

import sys
import os
import json
import re

FRANKIE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FRANKIE_DIR)

from compiler.lexer import Lexer, LexError
from compiler.parser import Parser, ParseError
from compiler.analyzer import Analyzer
from compiler import ast_nodes as A

_WORD_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_]*[?!]?')

KEYWORDS = [
    'def', 'end', 'if', 'elsif', 'else', 'unless', 'while', 'until', 'for',
    'in', 'do', 'return', 'puts', 'print', 'begin', 'rescue', 'ensure',
    'raise', 'require', 'stitch', 'case', 'when', 'next', 'break', 'record',
    'const', 'then', 'spawn', 'timeout', 'await', 'loop', 'true', 'false',
    'nil', 'and', 'or', 'not',
    # contextual keywords
    'import', 'error', 'test', 'enum', 'benchmark', 'breakpoint',
]

KEYWORD_DOCS = {
    'import':     'import "lib/math" as math — load a .fk file into its own namespace (v1.17)',
    'error':      'error TypeName — declare a user-defined error type (v1.17)',
    'test':       'test "name", tags: ["slow"] do ... end — named test group (v1.17)',
    'enum':       'enum Status(pending, active, done) — named set of symbolic values (v1.18)',
    'benchmark':  'benchmark ["label"] do ... end — time a block, returns elapsed ms (v1.18)',
    'breakpoint': 'breakpoint — pause into a scoped debug REPL (v1.18)',
    'record':     'record Point(x, y) — lightweight named data object',
    'puts':       'puts expr — print with a trailing newline',
    'print':      'print expr — print without a trailing newline',
    'p':          'p expr — debug-print with type information',
    'stitch':     'stitch "frankiecolor" — load a reusable library module',
    'require':    'require "lib/utils" — load a .fk file into the current scope',
    'spawn':      'spawn do ... end — run a block in a background thread',
    'loop':       'loop do ... end — infinite loop, exit with break',
}


def _load_stdlib_symbols():
    """name → (signature, first doc paragraph) for every public stdlib symbol."""
    symbols = {}
    try:
        import importlib.util, inspect
        spec = importlib.util.spec_from_file_location(
            'frankie_stdlib_lsp', os.path.join(FRANKIE_DIR, 'frankie_stdlib.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name, obj in vars(mod).items():
            if name.startswith('_'):
                continue
            if callable(obj):
                try:
                    sig = str(inspect.signature(obj))
                except (ValueError, TypeError):
                    sig = '(...)'
                doc = inspect.getdoc(obj) or ''
                symbols[name] = (f"{name}{sig}", doc)
            else:
                symbols[name] = (name, '')
    except Exception:
        pass
    return symbols


class Document:
    """One open file: text, last-good AST, current symbols."""
    def __init__(self, uri, text):
        self.uri = uri
        self.text = text
        self.ast = None          # last successfully parsed Program
        self.functions = {}      # name → (params, defaults, doc, line)
        self.symbols = set()     # every top-level defined name

    def update(self, text):
        self.text = text

    def reparse(self):
        """Parse; returns (parse_error_or_None). Keeps last-good AST."""
        try:
            tokens = Lexer(self.text).tokenize()
            self.ast = Parser(tokens).parse()
            self._collect_symbols()
            return None
        except (LexError, ParseError) as e:
            return e

    def _collect_symbols(self):
        self.functions = {}
        self.symbols = set()
        doc_comments = self._doc_comments()
        for node in self.ast.body:
            line = getattr(node, '_src_line', None)
            if isinstance(node, A.FuncDef):
                self.functions[node.name] = (
                    node.params, node.defaults,
                    doc_comments.get(line, ''), line)
                self.symbols.add(node.name)
            elif isinstance(node, (A.RecordDef, A.ErrorDef)):
                self.symbols.add(node.name)
            elif isinstance(node, A.EnumDef):
                self.symbols.add(node.name)
            elif isinstance(node, (A.Assign, A.ConstAssign, A.OrAssign,
                                   A.CompoundAssign)):
                self.symbols.add(node.name)
            elif isinstance(node, A.ImportStmt) and node.alias:
                self.symbols.add(node.alias)

    def _doc_comments(self):
        """Map def-line → ## doc-comment text immediately above it."""
        lines = self.text.splitlines()
        docs = {}
        block = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('##'):
                block.append(stripped.lstrip('#').strip())
            elif stripped.startswith('def ') and block:
                docs[i] = '\n'.join(block)
                block = []
            elif stripped and not stripped.startswith('#'):
                block = []
        return docs

    def word_at(self, line, character):
        """Identifier under the cursor (LSP 0-based position)."""
        lines = self.text.splitlines()
        if line >= len(lines):
            return None
        text = lines[line]
        for m in _WORD_RE.finditer(text):
            if m.start() <= character <= m.end():
                return m.group(0)
        return None


class FrankieLSP:
    def __init__(self, stdin=None, stdout=None):
        self.stdin = stdin or sys.stdin.buffer
        self.stdout = stdout or sys.stdout.buffer
        self.docs = {}           # uri → Document
        self.stdlib = _load_stdlib_symbols()
        self.running = True
        self.shutdown_requested = False

    # ── Wire protocol ────────────────────────────────────────────────────────

    def _read_message(self):
        headers = {}
        while True:
            line = self.stdin.readline()
            if not line:
                return None
            line = line.decode('ascii', errors='replace').strip()
            if not line:
                break
            if ':' in line:
                k, _, v = line.partition(':')
                headers[k.strip().lower()] = v.strip()
        length = int(headers.get('content-length', 0))
        if length <= 0:
            return None
        body = self.stdin.read(length)
        try:
            return json.loads(body.decode('utf-8'))
        except ValueError:
            return None

    def _send(self, payload):
        body = json.dumps(payload).encode('utf-8')
        self.stdout.write(f"Content-Length: {len(body)}\r\n\r\n".encode('ascii'))
        self.stdout.write(body)
        self.stdout.flush()

    def _respond(self, msg_id, result):
        self._send({'jsonrpc': '2.0', 'id': msg_id, 'result': result})

    def _respond_error(self, msg_id, code, message):
        self._send({'jsonrpc': '2.0', 'id': msg_id,
                    'error': {'code': code, 'message': message}})

    def _notify(self, method, params):
        self._send({'jsonrpc': '2.0', 'method': method, 'params': params})

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        while self.running:
            msg = self._read_message()
            if msg is None:
                break
            try:
                self._handle(msg)
            except Exception as e:
                if 'id' in msg:
                    self._respond_error(msg['id'], -32603, f"internal error: {e}")

    def _handle(self, msg):
        method = msg.get('method', '')
        params = msg.get('params', {}) or {}
        msg_id = msg.get('id')

        if method == 'initialize':
            self._respond(msg_id, {
                'capabilities': {
                    'textDocumentSync': 1,           # full document sync
                    'completionProvider': {'triggerCharacters': ['.']},
                    'hoverProvider': True,
                },
                'serverInfo': {'name': 'frankie-lsp', 'version': '1.20.0'},
            })
        elif method == 'initialized':
            pass
        elif method == 'shutdown':
            self.shutdown_requested = True
            self._respond(msg_id, None)
        elif method == 'exit':
            self.running = False
        elif method == 'textDocument/didOpen':
            doc_info = params['textDocument']
            doc = Document(doc_info['uri'], doc_info['text'])
            self.docs[doc.uri] = doc
            self._validate(doc)
        elif method == 'textDocument/didChange':
            uri = params['textDocument']['uri']
            doc = self.docs.get(uri)
            if doc and params.get('contentChanges'):
                doc.update(params['contentChanges'][-1]['text'])
                self._validate(doc)
        elif method == 'textDocument/didSave':
            doc = self.docs.get(params['textDocument']['uri'])
            if doc:
                self._validate(doc)
        elif method == 'textDocument/didClose':
            uri = params['textDocument']['uri']
            self.docs.pop(uri, None)
            self._notify('textDocument/publishDiagnostics',
                         {'uri': uri, 'diagnostics': []})
        elif method == 'textDocument/completion':
            self._respond(msg_id, self._completion(params))
        elif method == 'textDocument/hover':
            self._respond(msg_id, self._hover(params))
        elif method.startswith('$/'):
            pass                                     # cancellations etc.
        elif msg_id is not None:
            self._respond_error(msg_id, -32601, f"method not found: {method}")

    # ── Diagnostics ──────────────────────────────────────────────────────────

    def _validate(self, doc):
        diagnostics = []
        lines = doc.text.splitlines()

        def _line_range(line_1based, col_1based=None):
            ln = max(0, (line_1based or 1) - 1)
            text = lines[ln] if ln < len(lines) else ''
            if col_1based:
                start = max(0, col_1based - 1)
            else:
                start = len(text) - len(text.lstrip())
            return {'start': {'line': ln, 'character': start},
                    'end':   {'line': ln, 'character': max(len(text), start + 1)}}

        parse_error = doc.reparse()
        if parse_error is not None:
            if isinstance(parse_error, LexError):
                line, col = parse_error.line, parse_error.col
            else:
                line, col = parse_error.token.line, parse_error.token.col
            diagnostics.append({
                'range': _line_range(line, col),
                'severity': 1,
                'source': 'frankie',
                'message': str(parse_error),
            })
        else:
            fs_path = doc.uri[7:] if doc.uri.startswith('file://') else None
            try:
                issues = Analyzer(source_path=fs_path).analyze(doc.ast)
            except Exception:
                issues = []
            for issue in issues:
                diagnostics.append({
                    'range': _line_range(issue.line or 1),
                    'severity': 1 if issue.severity == 'error' else 2,
                    'source': 'frankie',
                    'message': issue.message,
                })

        # v1.19: surface uncovered lines from the last `frankiec test
        # --coverage` run (.frankie_coverage.json) as unobtrusive hints
        diagnostics.extend(self._coverage_hints(doc, lines))

        self._notify('textDocument/publishDiagnostics',
                     {'uri': doc.uri, 'diagnostics': diagnostics})

    def _coverage_hints(self, doc, lines):
        if not doc.uri.startswith('file://'):
            return []
        fs_path = doc.uri[7:]
        directory = os.path.dirname(fs_path)
        report = None
        for _ in range(4):                      # walk up a few levels
            candidate = os.path.join(directory, '.frankie_coverage.json')
            if os.path.exists(candidate):
                try:
                    with open(candidate, 'r', encoding='utf-8') as f:
                        report = (json.load(f), directory)
                except (OSError, ValueError):
                    report = None
                break
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
        if report is None:
            return []
        data, base = report
        entry = None
        for key, val in data.items():
            if key == '_overall' or not isinstance(val, dict):
                continue
            if os.path.abspath(os.path.join(base, key)) == os.path.abspath(fs_path):
                entry = val
                break
        if not entry or not entry.get('missing'):
            return []
        hints = []
        for ln in entry['missing']:
            idx = ln - 1
            text = lines[idx] if 0 <= idx < len(lines) else ''
            hints.append({
                'range': {'start': {'line': idx, 'character': 0},
                          'end': {'line': idx, 'character': max(len(text), 1)}},
                'severity': 4,                  # hint
                'source': 'frankie-coverage',
                'message': 'not executed in the last coverage run',
            })
        return hints

    # ── Completion ───────────────────────────────────────────────────────────

    def _completion(self, params):
        doc = self.docs.get(params['textDocument']['uri'])
        items = []
        seen = set()

        def add(label, kind, detail='', doc_text=''):
            if label in seen:
                return
            seen.add(label)
            item = {'label': label, 'kind': kind}
            if detail:
                item['detail'] = detail
            if doc_text:
                item['documentation'] = doc_text.split('\n\n')[0]
            items.append(item)

        if doc:
            for name, (fn_params, _d, fn_doc, _l) in doc.functions.items():
                add(name, 3, f"def {name}({', '.join(fn_params)})", fn_doc)
            for name in doc.symbols:
                add(name, 6)
        for name, (sig, doc_text) in self.stdlib.items():
            add(name, 3 if '(' in sig else 6, sig, doc_text)
        for kw in KEYWORDS:
            add(kw, 14, KEYWORD_DOCS.get(kw, ''))
        return {'isIncomplete': False, 'items': items}

    # ── Hover ────────────────────────────────────────────────────────────────

    def _hover(self, params):
        doc = self.docs.get(params['textDocument']['uri'])
        if doc is None:
            return None
        pos = params['position']
        word = doc.word_at(pos['line'], pos['character'])
        if not word:
            return None

        # 1. user-defined function in this file
        if word in doc.functions:
            fn_params, defaults, fn_doc, line = doc.functions[word]
            parts = []
            for i, p in enumerate(fn_params):
                d = defaults[i] if defaults and i < len(defaults) else None
                parts.append(f"{p} = …" if d is not None else p)
            md = f"```frankie\ndef {word}({', '.join(parts)})\n```"
            if fn_doc:
                md += f"\n\n{fn_doc}"
            return {'contents': {'kind': 'markdown', 'value': md}}

        # 2. stdlib
        if word in self.stdlib:
            sig, doc_text = self.stdlib[word]
            md = f"```frankie\n{sig}\n```"
            if doc_text:
                md += f"\n\n{doc_text}"
            return {'contents': {'kind': 'markdown', 'value': md}}

        # 3. keyword
        if word in KEYWORD_DOCS:
            return {'contents': {'kind': 'markdown',
                                 'value': f"**{word}** — {KEYWORD_DOCS[word]}"}}
        return None


def run_lsp():
    """Entry point for `frankiec lsp` — serve LSP over stdio."""
    FrankieLSP().run()


if __name__ == '__main__':
    run_lsp()
