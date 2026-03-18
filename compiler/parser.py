"""
Frankie Parser — Builds an AST from a list of tokens produced by the Lexer.
"""

from typing import List, Optional
from .lexer import Token, TT
from .ast_nodes import *


class ParseError(Exception):
    def __init__(self, msg, token: Token):
        super().__init__(f"[Parse Error] Line {token.line}, Col {token.col}: {msg} (got {token.type.name} = {token.value!r})")
        self.token = token


class Parser:
    def __init__(self, tokens: List[Token]):
        # Strip all newlines between tokens for easier parsing — we handle
        # them selectively only where needed
        self.tokens = [t for t in tokens if t.type != TT.NEWLINE or True]
        self.pos = 0

    # ─── Helpers ─────────────────────────────────────────────────────────────

    def peek(self, offset=0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def current(self) -> Token:
        return self.peek(0)

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def check(self, *types) -> bool:
        return self.current().type in types

    def match(self, *types) -> bool:
        if self.check(*types):
            self.advance()
            return True
        return False

    def expect(self, ttype: TT, msg=None) -> Token:
        if self.current().type == ttype:
            return self.advance()
        raise ParseError(msg or f"Expected {ttype.name}", self.current())

    def skip_newlines(self):
        while self.check(TT.NEWLINE):
            self.advance()

    def error(self, msg):
        raise ParseError(msg, self.current())

    # ─── Entry Point ─────────────────────────────────────────────────────────

    def parse(self) -> Program:
        self.skip_newlines()
        body = []
        while not self.check(TT.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()
        return Program(body=body)

    # ─── Statements ──────────────────────────────────────────────────────────

    def parse_statement(self) -> Optional[Node]:
        self.skip_newlines()
        t = self.current()

        if t.type == TT.DEF:
            return self.parse_func_def()
        if t.type == TT.IF:
            return self.parse_if()
        if t.type == TT.UNLESS:
            return self.parse_unless()
        if t.type == TT.WHILE:
            return self.parse_while()
        if t.type == TT.UNTIL:
            return self.parse_until()
        if t.type == TT.FOR:
            return self.parse_for_in()
        if t.type == TT.DO:
            return self.parse_do_while()
        if t.type == TT.RETURN:
            return self.parse_return()
        if t.type in (TT.PRINT, TT.PUTS):
            stmt = self.parse_print()
            return self._maybe_postfix(stmt)
        if t.type == TT.P:
            # Only treat as debug-print if followed by an expression to print.
            # If followed by [ . = it's being used as a variable named 'p'.
            next_t = self.peek(1).type
            if next_t in (TT.LBRACKET, TT.DOT, TT.ASSIGN):
                # fall through to expression statement below
                pass
            else:
                stmt = self.parse_debug_print()
                return self._maybe_postfix(stmt)
        if t.type == TT.BEGIN_KW:
            return self.parse_begin_rescue()
        if t.type == TT.RAISE:
            return self._maybe_postfix(self.parse_raise())
        if t.type == TT.REQUIRE:
            return self.parse_require()
        if t.type == TT.CASE:
            return self.parse_case()
        if t.type == TT.NEXT:
            return self._maybe_postfix(self.parse_next())
        if t.type == TT.BREAK:
            return self._maybe_postfix(self.parse_break())
        if t.type == TT.EOF:
            return None

        # Expression statement (assignment, call, etc.)
        expr = self.parse_expr()
        return self._maybe_postfix(expr)

    def _maybe_postfix(self, stmt: Node) -> Node:
        """Wrap stmt in PostfixIf if a trailing if/unless follows on the same line."""
        if self.check(TT.IF):
            self.advance()
            cond = self.parse_expr()
            self.expect_end_of_stmt()
            return PostfixIf(stmt=stmt, condition=cond, negated=False)
        if self.check(TT.UNLESS):
            self.advance()
            cond = self.parse_expr()
            self.expect_end_of_stmt()
            return PostfixIf(stmt=stmt, condition=cond, negated=True)
        self.expect_end_of_stmt()
        return stmt

    def expect_end_of_stmt(self):
        """Consume a newline or EOF at end of statement."""
        if self.check(TT.NEWLINE) or self.check(TT.EOF):
            self.skip_newlines()
        # Also OK if next is 'end' / 'else' / 'elsif'
        # (don't consume, just leave for parent)

    def parse_body(self) -> List[Node]:
        """Parse statements until end/else/elsif/EOF."""
        self.skip_newlines()
        body = []
        while not self.check(TT.END, TT.ELSE, TT.ELSIF, TT.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()
        return body

    # ─── Function Def ────────────────────────────────────────────────────────

    def parse_func_def(self) -> FuncDef:
        self.expect(TT.DEF)
        name_tok = self.expect(TT.IDENT, "Expected function name after 'def'")
        name = name_tok.value
        params = []
        defaults = []
        if self.check(TT.LPAREN):
            self.advance()
            if not self.check(TT.RPAREN):
                pname = self._parse_param_name()
                params.append(pname)
                if self.match(TT.ASSIGN):
                    defaults.append(self.parse_expr())
                else:
                    defaults.append(None)
                while self.match(TT.COMMA):
                    pname = self._parse_param_name()
                    params.append(pname)
                    if self.match(TT.ASSIGN):
                        defaults.append(self.parse_expr())
                    else:
                        defaults.append(None)
            self.expect(TT.RPAREN)
        self.skip_newlines()
        body = self.parse_body()
        self.expect(TT.END, "Expected 'end' to close 'def'")
        return FuncDef(name=name, params=params, defaults=defaults, body=body)

    def _parse_param_name(self) -> str:
        """Accept any identifier-like token as a parameter name."""
        t = self.current()
        if t.type == TT.IDENT or t.type in (
            TT.TIMES, TT.EACH, TT.EACH_WITH_INDEX, TT.MAP,
            TT.IN, TT.AND, TT.OR, TT.NOT,
        ):
            return self.advance().value
        raise ParseError("Expected parameter name", t)

    # ─── Control Flow ────────────────────────────────────────────────────────

    def parse_if(self) -> IfStmt:
        self.expect(TT.IF)
        cond = self.parse_expr()
        self.skip_newlines()
        then_body = self.parse_body()

        elsif_clauses = []
        while self.check(TT.ELSIF):
            self.advance()
            ec = self.parse_expr()
            self.skip_newlines()
            eb = self.parse_body()
            elsif_clauses.append((ec, eb))

        else_body = None
        if self.match(TT.ELSE):
            self.skip_newlines()
            else_body = self.parse_body()

        self.expect(TT.END, "Expected 'end' to close 'if'")
        return IfStmt(condition=cond, then_body=then_body,
                      elsif_clauses=elsif_clauses, else_body=else_body)

    def parse_unless(self) -> UnlessStmt:
        self.expect(TT.UNLESS)
        cond = self.parse_expr()
        self.skip_newlines()
        then_body = self.parse_body()
        else_body = None
        if self.match(TT.ELSE):
            self.skip_newlines()
            else_body = self.parse_body()
        self.expect(TT.END, "Expected 'end' to close 'unless'")
        return UnlessStmt(condition=cond, then_body=then_body, else_body=else_body)

    def parse_while(self) -> WhileStmt:
        self.expect(TT.WHILE)
        cond = self.parse_expr()
        self.skip_newlines()
        body = self.parse_body()
        self.expect(TT.END, "Expected 'end' to close 'while'")
        return WhileStmt(condition=cond, body=body)

    def parse_until(self) -> UntilStmt:
        self.expect(TT.UNTIL)
        cond = self.parse_expr()
        self.skip_newlines()
        body = self.parse_body()
        self.expect(TT.END, "Expected 'end' to close 'until'")
        return UntilStmt(condition=cond, body=body)

    def parse_do_while(self) -> DoWhileStmt:
        self.expect(TT.DO)
        self.skip_newlines()
        body = self.parse_do_body()
        self.expect(TT.WHILE, "Expected 'while' after 'do' body")
        cond = self.parse_expr()
        self.skip_newlines()
        return DoWhileStmt(body=body, condition=cond)

    def parse_do_body(self) -> List[Node]:
        """Like parse_body but also stops at bare 'while' (for do..while)."""
        self.skip_newlines()
        body = []
        while not self.check(TT.END, TT.ELSE, TT.ELSIF, TT.WHILE, TT.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()
        return body

    def parse_rescue_body(self) -> List[Node]:
        """Parse body that stops at rescue/ensure/end."""
        self.skip_newlines()
        body = []
        while not self.check(TT.END, TT.RESCUE, TT.ENSURE, TT.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()
        return body

    def parse_begin_rescue(self) -> BeginRescue:
        self.expect(TT.BEGIN_KW)
        self.skip_newlines()
        body = self.parse_rescue_body()
        rescue_clauses = []
        ensure_body = None
        # One or more rescue clauses, each optionally typed
        while self.check(TT.RESCUE):
            self.advance()
            # Optional type name: rescue TypeError  rescue RuntimeError  etc.
            error_type = None
            rescue_var = None
            # A capitalised IDENT that is NOT immediately followed by NEWLINE/EOF
            # and is a known type hint is treated as the error type
            if (self.check(TT.IDENT)
                    and self.current().value[:1].isupper()
                    and self.peek(1).type not in (TT.NEWLINE, TT.EOF)):
                error_type = self.advance().value
            # Optional variable binding: rescue [Type] e  or  rescue [Type] => e
            if self.check(TT.IDENT):
                rescue_var = self.advance().value
            self.skip_newlines()
            clause_body = self.parse_rescue_body()
            rescue_clauses.append(RescueClause(
                error_type=error_type, rescue_var=rescue_var, body=clause_body))
        if self.check(TT.ENSURE):
            self.advance()
            self.skip_newlines()
            ensure_body = self.parse_rescue_body()
        self.expect(TT.END, "Expected 'end' to close 'begin'")
        # Always produce at least one (empty catch-all) clause so codegen
        # can iterate uniformly even when there is no rescue clause at all.
        if not rescue_clauses:
            rescue_clauses = [RescueClause(error_type=None, rescue_var=None, body=[])]
        return BeginRescue(body=body, rescue_clauses=rescue_clauses, ensure_body=ensure_body)

    def parse_raise(self) -> RaiseStmt:
        self.expect(TT.RAISE)
        if self.check(TT.NEWLINE) or self.check(TT.EOF):
            return RaiseStmt(message=None)
        msg = self.parse_expr()
        return RaiseStmt(message=msg)

    def parse_require(self) -> RequireStmt:
        self.expect(TT.REQUIRE)
        path = self.parse_expr()
        return RequireStmt(path=path)

    def parse_case(self) -> CaseStmt:
        self.expect(TT.CASE)
        # Optional subject: case x
        subject = None
        if not self.check(TT.NEWLINE) and not self.check(TT.EOF):
            subject = self.parse_expr()
        self.skip_newlines()

        when_clauses = []
        else_body = None

        while self.check(TT.WHEN):
            self.advance()
            # One or more values: when 1, 2, 3
            values = [self.parse_expr()]
            while self.match(TT.COMMA):
                values.append(self.parse_expr())
            self.skip_newlines()
            body = self.parse_when_body()
            when_clauses.append((values, body))

        if self.match(TT.ELSE):
            self.skip_newlines()
            else_body = self.parse_when_body()

        self.expect(TT.END, "Expected 'end' to close 'case'")
        return CaseStmt(subject=subject, when_clauses=when_clauses, else_body=else_body)

    def parse_when_body(self) -> List[Node]:
        """Parse body that stops at when/else/end."""
        self.skip_newlines()
        body = []
        while not self.check(TT.WHEN, TT.ELSE, TT.END, TT.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                body.append(stmt)
            self.skip_newlines()
        return body

    def parse_for_in(self) -> ForInStmt:
        self.expect(TT.FOR)
        var = self.expect(TT.IDENT, "Expected loop variable").value
        self.expect(TT.IN, "Expected 'in'")
        iterable = self.parse_expr()
        self.skip_newlines()
        body = self.parse_body()
        self.expect(TT.END, "Expected 'end' to close 'for'")
        return ForInStmt(var=var, iterable=iterable, body=body)

    def parse_return(self) -> ReturnStmt:
        self.expect(TT.RETURN)
        if self.check(TT.NEWLINE) or self.check(TT.EOF):
            return ReturnStmt(value=None)
        value = self.parse_expr()
        return ReturnStmt(value=value)

    def parse_next(self) -> 'NextStmt':
        self.expect(TT.NEXT)
        return NextStmt()

    def parse_break(self) -> 'BreakStmt':
        self.expect(TT.BREAK)
        # Optional value: break expr — but NOT if next token is a postfix if/unless
        if (self.check(TT.NEWLINE) or self.check(TT.EOF)
                or self.check(TT.IF) or self.check(TT.UNLESS)):
            return BreakStmt(value=None)
        return BreakStmt(value=self.parse_expr())

    def parse_print(self) -> PrintStmt:
        tok = self.advance()
        newline = (tok.type == TT.PUTS)
        value = self.parse_expr()
        return PrintStmt(value=value, newline=newline)

    def parse_debug_print(self) -> DebugPrint:
        self.expect(TT.P)
        value = self.parse_expr()
        return DebugPrint(value=value)

    # ─── Expressions ─────────────────────────────────────────────────────────

    def parse_expr(self) -> Node:
        return self.parse_pipe()

    def parse_pipe(self) -> Node:
        left = self.parse_assign()
        while self.check(TT.PIPE_ARROW):
            self.advance()
            right = self.parse_call_or_ident()
            left = PipeOp(left=left, right=right)
        return left

    def parse_assign(self) -> Node:
        # Destructuring: a, b, c = expr
        # Only applies when: IDENT COMMA ... ASSIGN  (pure identifiers, then =)
        # We must NOT consume tokens if this turns out not to be destructuring
        if self.check(TT.IDENT) and self.peek(1).type == TT.COMMA:
            # Scan ahead to confirm all commas lead to idents and end with =
            save_pos = self.pos
            names = [self.advance().value]  # first ident
            is_destruct = False
            while self.check(TT.COMMA):
                self.advance()
                if self.check(TT.IDENT):
                    names.append(self.advance().value)
                else:
                    break
            if self.check(TT.ASSIGN) and len(names) > 1:
                self.advance()  # consume =
                value = self.parse_expr()
                return DestructAssign(names=names, value=value)
            # Not destructuring — backtrack
            self.pos = save_pos

        # Constant assign: UPPER_CASE = expr
        if (self.check(TT.IDENT)
                and self.peek(1).type == TT.ASSIGN
                and self.current().value == self.current().value.upper()
                and self.current().value.replace('_', '').isalpha()):
            name = self.advance().value
            self.advance()  # consume =
            value = self.parse_expr()
            return ConstAssign(name=name, value=value)

        # Compound assign: IDENT op= expr  (+=, -=, *=, /=, //=, **=, %=)
        _COMPOUND_OPS = {
            TT.PLUS_ASSIGN: '+', TT.MINUS_ASSIGN: '-', TT.STAR_ASSIGN: '*',
            TT.SLASH_ASSIGN: '/', TT.DOUBLESLASH_ASSIGN: '//',
            TT.STARSTAR_ASSIGN: '**', TT.PERCENT_ASSIGN: '%',
        }
        if self.check(TT.IDENT) and self.peek(1).type in _COMPOUND_OPS:
            name = self.advance().value
            op = _COMPOUND_OPS[self.current().type]
            self.advance()  # consume op=
            value = self.parse_expr()
            return CompoundAssign(name=name, op=op, value=value)

        # Single assign: IDENT = expr
        if self.check(TT.IDENT) and self.peek(1).type == TT.ASSIGN:
            name = self.advance().value
            self.advance()  # consume =
            value = self.parse_expr()
            return Assign(name=name, value=value)
        node = self.parse_or()
        # Index assign: expr[idx] = val or expr[idx] op= val
        if isinstance(node, IndexAccess) and self.current().type in _COMPOUND_OPS:
            op = _COMPOUND_OPS[self.advance().type]
            value = self.parse_expr()
            return IndexCompoundAssign(target=node.target, index=node.index, op=op, value=value)
        if isinstance(node, IndexAccess) and self.check(TT.ASSIGN):
            self.advance()
            value = self.parse_expr()
            return IndexAssign(target=node.target, index=node.index, value=value)
        return node

    def parse_or(self) -> Node:
        left = self.parse_and()
        while self.check(TT.OR):
            self.advance()
            right = self.parse_and()
            left = BinOp(op='or', left=left, right=right)
        return left

    def parse_and(self) -> Node:
        left = self.parse_not()
        while self.check(TT.AND):
            self.advance()
            right = self.parse_not()
            left = BinOp(op='and', left=left, right=right)
        return left

    def parse_not(self) -> Node:
        if self.check(TT.NOT):
            self.advance()
            operand = self.parse_not()
            return UnaryOp(op='not', operand=operand)
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        left = self.parse_addition()
        while self.check(TT.EQ, TT.NEQ, TT.LT, TT.LTE, TT.GT, TT.GTE, TT.MATCH_OP):
            op = self.advance().value
            right = self.parse_addition()
            if op == '=~':
                left = MatchOp(left=left, right=right)
            else:
                left = BinOp(op=op, left=left, right=right)
        return left

    def parse_addition(self) -> Node:
        left = self.parse_multiplication()
        while self.check(TT.PLUS, TT.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_multiplication(self) -> Node:
        left = self.parse_unary()
        while self.check(TT.STAR, TT.SLASH, TT.DOUBLESLASH, TT.PERCENT, TT.STARSTAR):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOp(op=op, left=left, right=right)
        return left

    def parse_unary(self) -> Node:
        if self.check(TT.MINUS):
            self.advance()
            operand = self.parse_postfix()   # parse primary+postfix, NOT another unary range
            node = UnaryOp(op='-', operand=operand)
        else:
            node = self.parse_postfix()
        # Range check at unary level so -5..-1 parses as (-5)..(-1)
        if self.check(TT.RANGE_INC):
            self.advance()
            end_node = self.parse_unary()
            return RangeLiteral(start=node, end=end_node, inclusive=True)
        if self.check(TT.RANGE_EXC):
            self.advance()
            end_node = self.parse_unary()
            return RangeLiteral(start=node, end=end_node, inclusive=False)
        return node

    def parse_postfix(self) -> Node:
        node = self.parse_primary()

        # NOTE: Ranges are handled in parse_unary, not here, so that
        # negative starts like -5..-1 work correctly.

        while True:
            if self.check(TT.DOT):
                self.advance()
                method_tok = self.current()
                # method name can be IDENT or keywords like 'times', 'each', etc.
                if method_tok.type in (TT.IDENT, TT.TIMES, TT.EACH, TT.EACH_WITH_INDEX, TT.MAP):
                    method = self.advance().value
                else:
                    self.error("Expected method name after '.'")

                args = []
                if self.check(TT.LPAREN):
                    self.advance()
                    if not self.check(TT.RPAREN):
                        args.append(self.parse_expr())
                        while self.match(TT.COMMA):
                            args.append(self.parse_expr())
                    self.expect(TT.RPAREN)

                block = None
                if self.check(TT.DO):
                    block = self.parse_block()

                node = MethodCall(receiver=node, method=method, args=args, block=block)

            elif self.check(TT.LBRACKET):
                self.advance()
                index = self.parse_expr()
                self.expect(TT.RBRACKET)
                node = IndexAccess(target=node, index=index)
            else:
                break

        return node

    def _parse_block_param(self) -> str:
        """Accept any identifier-like token as a block parameter name."""
        t = self.current()
        if t.type in (TT.IDENT, TT.P, TT.TIMES, TT.EACH, TT.EACH_WITH_INDEX,
                      TT.MAP, TT.IN, TT.AND, TT.OR, TT.NOT,
                      TT.NEXT, TT.BREAK):
            return self.advance().value
        raise ParseError("Expected block param", t)

    def parse_block(self) -> Block:
        self.expect(TT.DO)
        params = []
        if self.check(TT.PIPE):
            self.advance()
            if not self.check(TT.PIPE):
                params.append(self._parse_block_param())
                while self.match(TT.COMMA):
                    params.append(self._parse_block_param())
            self.expect(TT.PIPE, "Expected '|' to close block params")
        self.skip_newlines()
        body = self.parse_body()
        self.expect(TT.END, "Expected 'end' to close block")
        return Block(params=params, body=body)

    def parse_call_or_ident(self) -> Node:
        """For pipe RHS — parse a function name or call."""
        if self.check(TT.IDENT):
            name = self.advance().value
            if self.check(TT.LPAREN):
                self.advance()
                args = []
                if not self.check(TT.RPAREN):
                    args.append(self.parse_expr())
                    while self.match(TT.COMMA):
                        args.append(self.parse_expr())
                self.expect(TT.RPAREN)
                return FuncCall(name=name, args=args)
            return Identifier(name=name)
        # puts/print as bare pipe targets — wrap as an identifier so the
        # PipeOp codegen can treat them like any other callable name.
        if self.check(TT.PUTS, TT.PRINT):
            name = self.advance().value
            return Identifier(name=name)
        # Could be a print/puts etc.
        return self.parse_primary()

    def parse_primary(self) -> Node:
        t = self.current()

        if t.type == TT.INTEGER:
            self.advance()
            return IntLiteral(value=t.value)

        if t.type == TT.FLOAT:
            self.advance()
            return FloatLiteral(value=t.value)

        if t.type == TT.STRING:
            self.advance()
            return StringLiteral(parts=t.value)

        if t.type == TT.BOOL:
            self.advance()
            return BoolLiteral(value=t.value)

        if t.type == TT.NIL:
            self.advance()
            return NilLiteral()

        if t.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT.RPAREN)
            return expr

        if t.type == TT.LBRACKET:
            return self.parse_vector()

        if t.type == TT.LBRACE:
            return self.parse_hash()

        if t.type in (TT.INPUT, TT.INPUT_INT, TT.INPUT_FLOAT):
            return self.parse_input()

        # Allow iterator/method keywords to be used as plain variable names
        # e.g.  def repeat(times=3)  then  i < times  should work
        if t.type in (TT.TIMES, TT.EACH, TT.EACH_WITH_INDEX, TT.MAP, TT.P):
            name = self.advance().value
            if self.check(TT.LPAREN):
                self.advance()
                args = []
                if not self.check(TT.RPAREN):
                    args.append(self.parse_arg())
                    while self.match(TT.COMMA):
                        if self.check(TT.RPAREN):
                            break
                        args.append(self.parse_arg())
                self.expect(TT.RPAREN)
                return FuncCall(name=name, args=args)
            return Identifier(name=name)

        if t.type == TT.IDENT:
            name = self.advance().value
            # Function call
            if self.check(TT.LPAREN):
                self.advance()
                args = []
                if not self.check(TT.RPAREN):
                    args.append(self.parse_arg())
                    while self.match(TT.COMMA):
                        if self.check(TT.RPAREN):
                            break
                        args.append(self.parse_arg())
                self.expect(TT.RPAREN)
                return FuncCall(name=name, args=args)
            return Identifier(name=name)

        self.error(f"Unexpected token in expression: {t.type.name}")

    def parse_arg(self) -> Node:
        """Parse a function argument, which may be named: name: value."""
        # Named arg: ident colon expr  (but not a hash — no { follows)
        if self.check(TT.IDENT) and self.peek(1).type == TT.COLON:
            arg_name = self.advance().value
            self.advance()  # consume ':'
            val = self.parse_expr()
            return NamedArg(name=arg_name, value=val)
        return self.parse_expr()

    def parse_vector(self) -> VectorLiteral:
        self.expect(TT.LBRACKET)
        elements = []
        self.skip_newlines()
        if not self.check(TT.RBRACKET):
            elements.append(self.parse_expr())
            while self.match(TT.COMMA):
                self.skip_newlines()
                if self.check(TT.RBRACKET):
                    break
                elements.append(self.parse_expr())
        self.skip_newlines()
        self.expect(TT.RBRACKET)
        return VectorLiteral(elements=elements)

    def parse_hash(self) -> HashLiteral:
        self.expect(TT.LBRACE)
        pairs = []
        self.skip_newlines()
        if not self.check(TT.RBRACE):
            key, val = self.parse_hash_pair()
            pairs.append((key, val))
            while self.match(TT.COMMA):
                self.skip_newlines()
                if self.check(TT.RBRACE):
                    break
                key, val = self.parse_hash_pair()
                pairs.append((key, val))
        self.skip_newlines()
        self.expect(TT.RBRACE)
        return HashLiteral(pairs=pairs)

    def parse_hash_pair(self):
        # key: value  OR  "key" => value
        if self.check(TT.IDENT) and self.peek(1).type == TT.COLON:
            key = StringLiteral(parts=[('literal', self.advance().value)])
            self.expect(TT.COLON)
            val = self.parse_expr()
            return key, val
        key = self.parse_expr()
        self.expect(TT.COLON, "Expected ':' in hash pair")
        val = self.parse_expr()
        return key, val

    def parse_input(self) -> InputExpr:
        tok = self.advance()
        cast_map = {TT.INPUT: 'str', TT.INPUT_INT: 'int', TT.INPUT_FLOAT: 'float'}
        cast = cast_map[tok.type]
        prompt = None
        if self.check(TT.LPAREN):
            self.advance()
            if not self.check(TT.RPAREN):
                prompt = self.parse_expr()
            self.expect(TT.RPAREN)
        return InputExpr(prompt=prompt, cast=cast)
