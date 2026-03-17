"""
Frankie Lexer — Tokenizes .fk source files into a stream of tokens.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TT(Enum):
    """Token Types"""
    # Literals
    INTEGER     = auto()
    FLOAT       = auto()
    STRING      = auto()
    BOOL        = auto()
    NIL         = auto()

    # Identifiers & Keywords
    IDENT       = auto()
    DEF         = auto()
    END         = auto()
    IF          = auto()
    ELSIF       = auto()
    ELSE        = auto()
    UNLESS      = auto()
    WHILE       = auto()
    UNTIL       = auto()
    FOR         = auto()
    IN          = auto()
    DO          = auto()
    RETURN      = auto()
    PRINT       = auto()
    PUTS        = auto()
    P           = auto()
    TIMES       = auto()
    EACH        = auto()
    EACH_WITH_INDEX = auto()
    MAP         = auto()
    AND         = auto()
    OR          = auto()
    NOT         = auto()
    INPUT       = auto()
    INPUT_INT   = auto()
    INPUT_FLOAT = auto()

    # Operators
    PLUS        = auto()
    MINUS       = auto()
    STAR        = auto()
    SLASH       = auto()
    DOUBLESLASH = auto()
    PERCENT     = auto()
    STARSTAR    = auto()
    PIPE_ARROW  = auto()   # |>
    RANGE_INC   = auto()   # ..
    RANGE_EXC   = auto()   # ...

    # Comparison
    EQ          = auto()   # ==
    NEQ         = auto()   # !=
    LT          = auto()
    LTE         = auto()
    GT          = auto()
    GTE         = auto()

    # Assignment
    ASSIGN      = auto()   # =

    # Delimiters
    LPAREN      = auto()
    RPAREN      = auto()
    LBRACKET    = auto()
    RBRACKET    = auto()
    LBRACE      = auto()
    RBRACE      = auto()
    COMMA       = auto()
    COLON       = auto()
    DOT         = auto()
    PIPE        = auto()   # | (block param delimiter)
    HASH        = auto()   # #

    # Structural
    NEWLINE     = auto()
    INDENT      = auto()
    DEDENT      = auto()
    EOF         = auto()

    # Special
    INTERP_START = auto()  # #{
    INTERP_END   = auto()  # }
    QUESTION     = auto()  # ? (for method names like include?)
    BANG         = auto()  # ! (for method names)
    BEGIN_KW     = auto()  # begin
    RESCUE       = auto()  # rescue
    ENSURE       = auto()  # ensure
    RAISE        = auto()  # raise
    REQUIRE      = auto()  # require
    MATCH_OP     = auto()  # =~
    CASE         = auto()  # case
    WHEN         = auto()  # when
    NEXT         = auto()  # next
    BREAK        = auto()  # break


KEYWORDS = {
    'def':              TT.DEF,
    'end':              TT.END,
    'if':               TT.IF,
    'elsif':            TT.ELSIF,
    'else':             TT.ELSE,
    'unless':           TT.UNLESS,
    'while':            TT.WHILE,
    'until':            TT.UNTIL,
    'for':              TT.FOR,
    'in':               TT.IN,
    'do':               TT.DO,
    'return':           TT.RETURN,
    'print':            TT.PRINT,
    'puts':             TT.PUTS,
    'p':                TT.P,
    'times':            TT.TIMES,
    'each':             TT.EACH,
    'each_with_index':  TT.EACH_WITH_INDEX,
    'map':              TT.MAP,
    'and':              TT.AND,
    'or':               TT.OR,
    'not':              TT.NOT,
    'true':             TT.BOOL,
    'false':            TT.BOOL,
    'nil':              TT.NIL,
    'input':            TT.INPUT,
    'input_int':        TT.INPUT_INT,
    'input_float':      TT.INPUT_FLOAT,
    'begin':            TT.BEGIN_KW,
    'rescue':           TT.RESCUE,
    'ensure':           TT.ENSURE,
    'raise':            TT.RAISE,
    'require':          TT.REQUIRE,
    'case':             TT.CASE,
    'when':             TT.WHEN,
    'next':             TT.NEXT,
    'break':            TT.BREAK,
}


@dataclass
class Token:
    type: TT
    value: object
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.col})"


class LexError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"[Lexer Error] Line {line}, Col {col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def error(self, msg):
        raise LexError(msg, self.line, self.col)

    def peek(self, offset=0) -> Optional[str]:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.advance()
            return True
        return False

    def add_token(self, ttype: TT, value=None):
        self.tokens.append(Token(ttype, value, self.line, self.col))

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in (' ', '\t', '\r'):
                self.advance()
            elif ch == '#':
                # comment — skip to end of line
                while self.pos < len(self.source) and self.peek() != '\n':
                    self.advance()
            else:
                break

    def read_string(self, quote_char: str) -> str:
        """Read a string literal, handling #{} interpolation markers."""
        parts = []
        current = []
        start_line = self.line
        start_col = self.col

        while self.pos < len(self.source):
            ch = self.peek()
            if ch is None or ch == '\n':
                raise LexError("Unterminated string literal", start_line, start_col)
            if ch == quote_char:
                self.advance()
                break
            if ch == '\\':
                self.advance()
                esc = self.advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                              '"': '"', "'": "'"}
                current.append(escape_map.get(esc, '\\' + esc))
            elif ch == '#' and quote_char == '"' and self.peek(1) == '{':
                # String interpolation
                self.advance()  # skip #
                self.advance()  # skip {
                parts.append(('literal', ''.join(current)))
                current = []
                # Collect expression until }
                depth = 1
                expr_chars = []
                while self.pos < len(self.source) and depth > 0:
                    c = self.peek()
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            self.advance()
                            break
                    expr_chars.append(self.advance())
                parts.append(('interp', ''.join(expr_chars)))
            else:
                current.append(self.advance())

        parts.append(('literal', ''.join(current)))
        return parts

    def read_multiline_string(self, quote_char: str) -> list:
        """Read a triple-quoted string (\"\"\"...\"\"\" or '''...''').
        Supports #{} interpolation in double-quoted variants.
        Newlines are preserved as-is."""
        parts = []
        current = []
        start_line = self.line

        while self.pos < len(self.source):
            ch = self.peek()
            if ch is None:
                raise LexError("Unterminated triple-quoted string", start_line, 1)
            # Check for closing triple quote
            if ch == quote_char and self.peek(1) == quote_char and self.peek(2) == quote_char:
                self.advance(); self.advance(); self.advance()
                break
            if ch == '\\':
                self.advance()
                esc = self.advance()
                escape_map = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
                              '"': '"', "'": "'"}
                current.append(escape_map.get(esc, '\\' + esc))
            elif ch == '#' and quote_char == '"' and self.peek(1) == '{':
                self.advance()  # skip #
                self.advance()  # skip {
                parts.append(('literal', ''.join(current)))
                current = []
                depth = 1
                expr_chars = []
                while self.pos < len(self.source) and depth > 0:
                    c = self.peek()
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            self.advance()
                            break
                    expr_chars.append(self.advance())
                parts.append(('interp', ''.join(expr_chars)))
            else:
                current.append(self.advance())

        parts.append(('literal', ''.join(current)))
        return parts

    def read_number(self):
        start = self.pos
        is_float = False
        while self.pos < len(self.source) and self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek(1) and self.peek(1).isdigit():
            is_float = True
            self.advance()  # consume dot
            while self.pos < len(self.source) and self.peek().isdigit():
                self.advance()
        raw = self.source[start:self.pos]
        if is_float:
            return TT.FLOAT, float(raw)
        return TT.INTEGER, int(raw)

    def read_ident(self):
        start = self.pos
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() in ('_',)):
            self.advance()
        # Allow trailing ? or ! for Ruby-style method names
        if self.peek() in ('?', '!'):
            self.advance()
        return self.source[start:self.pos]

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break

            ch = self.peek()
            line, col = self.line, self.col

            # Newline
            if ch == '\n':
                self.advance()
                self.add_token(TT.NEWLINE)
                continue

            # Numbers
            if ch.isdigit():
                ttype, value = self.read_number()
                self.tokens.append(Token(ttype, value, line, col))
                continue

            # Strings — single/double quoted, with triple-quote multiline support
            if ch in ('"', "'"):
                self.advance()
                # Check for triple quote  """ or '''
                if self.peek() == ch and self.peek(1) == ch:
                    self.advance(); self.advance()  # consume 2nd and 3rd quote
                    parts = self.read_multiline_string(ch)
                else:
                    parts = self.read_string(ch)
                self.tokens.append(Token(TT.STRING, parts, line, col))
                continue

            # Identifiers & keywords
            if ch.isalpha() or ch == '_':
                word = self.read_ident()
                ttype = KEYWORDS.get(word)
                if ttype is not None:
                    if ttype == TT.BOOL:
                        val = (word == 'true')
                        self.tokens.append(Token(TT.BOOL, val, line, col))
                    elif ttype == TT.NIL:
                        self.tokens.append(Token(TT.NIL, None, line, col))
                    else:
                        self.tokens.append(Token(ttype, word, line, col))
                else:
                    self.tokens.append(Token(TT.IDENT, word, line, col))
                continue

            # Symbol literal :name → treated as a string key
            if ch == ':' and self.peek(1) and (self.peek(1).isalpha() or self.peek(1) == '_'):
                self.advance()  # consume ':'
                start = self.pos
                while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
                    self.advance()
                sym = self.source[start:self.pos]
                self.tokens.append(Token(TT.STRING, [('literal', sym)], line, col))
                continue

            # Operators & punctuation
            self.advance()

            if ch == '+':
                self.add_token(TT.PLUS, '+')
            elif ch == '-':
                self.add_token(TT.MINUS, '-')
            elif ch == '*':
                if self.match('*'):
                    self.add_token(TT.STARSTAR, '**')
                else:
                    self.add_token(TT.STAR, '*')
            elif ch == '/':
                if self.match('/'):
                    self.add_token(TT.DOUBLESLASH, '//')
                else:
                    self.add_token(TT.SLASH, '/')
            elif ch == '%':
                self.add_token(TT.PERCENT, '%')
            elif ch == '=':
                if self.match('='):
                    self.add_token(TT.EQ, '==')
                elif self.match('~'):
                    self.add_token(TT.MATCH_OP, '=~')
                else:
                    self.add_token(TT.ASSIGN, '=')
            elif ch == '!':
                if self.match('='):
                    self.add_token(TT.NEQ, '!=')
                else:
                    self.add_token(TT.BANG, '!')
            elif ch == '<':
                if self.match('='):
                    self.add_token(TT.LTE, '<=')
                else:
                    self.add_token(TT.LT, '<')
            elif ch == '>':
                if self.match('='):
                    self.add_token(TT.GTE, '>=')
                else:
                    self.add_token(TT.GT, '>')
            elif ch == '.':
                if self.match('.'):
                    if self.match('.'):
                        self.add_token(TT.RANGE_EXC, '...')
                    else:
                        self.add_token(TT.RANGE_INC, '..')
                else:
                    self.add_token(TT.DOT, '.')
            elif ch == '|':
                if self.match('>'):
                    self.add_token(TT.PIPE_ARROW, '|>')
                else:
                    self.add_token(TT.PIPE, '|')
            elif ch == '(':
                self.add_token(TT.LPAREN, '(')
            elif ch == ')':
                self.add_token(TT.RPAREN, ')')
            elif ch == '[':
                self.add_token(TT.LBRACKET, '[')
            elif ch == ']':
                self.add_token(TT.RBRACKET, ']')
            elif ch == '{':
                self.add_token(TT.LBRACE, '{')
            elif ch == '}':
                self.add_token(TT.RBRACE, '}')
            elif ch == ',':
                self.add_token(TT.COMMA, ',')
            elif ch == ':':
                self.add_token(TT.COLON, ':')
            elif ch == '?':
                self.add_token(TT.QUESTION, '?')
            else:
                self.error(f"Unexpected character: {ch!r}")

        self.add_token(TT.EOF, None)
        return self.tokens
