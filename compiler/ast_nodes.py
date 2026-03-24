"""
Frankie AST Node Definitions
Each node represents a syntactic construct in the Frankie language.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


# ─── Base ────────────────────────────────────────────────────────────────────

class Node:
    pass


# ─── Literals ────────────────────────────────────────────────────────────────

@dataclass
class IntLiteral(Node):
    value: int

@dataclass
class FloatLiteral(Node):
    value: float

@dataclass
class StringLiteral(Node):
    """parts: list of ('literal', str) | ('interp', str_expr)"""
    parts: list

@dataclass
class BoolLiteral(Node):
    value: bool

@dataclass
class NilLiteral(Node):
    pass

@dataclass
class VectorLiteral(Node):
    elements: List[Node]

@dataclass
class HashLiteral(Node):
    pairs: List[tuple]  # list of (key_node, value_node)

@dataclass
class RangeLiteral(Node):
    start: Node
    end: Node
    inclusive: bool  # True = .., False = ...


# ─── Variables ───────────────────────────────────────────────────────────────

@dataclass
class Identifier(Node):
    name: str

@dataclass
class Assign(Node):
    name: str
    value: Node

@dataclass
class CompoundAssign(Node):
    """x += 1, x -= 2, x *= 3, x /= 4, x //= 5, x **= 6, x %= 7"""
    name: str
    op: str   # '+', '-', '*', '/', '//', '**', '%'
    value: Node

@dataclass
class IndexCompoundAssign(Node):
    """x[i] += 1  etc."""
    target: Node
    index: Node
    op: str
    value: Node

@dataclass
class IndexAccess(Node):
    target: Node
    index: Node

@dataclass
class IndexAssign(Node):
    target: Node
    index: Node
    value: Node


# ─── Operations ──────────────────────────────────────────────────────────────

@dataclass
class BinOp(Node):
    op: str
    left: Node
    right: Node

@dataclass
class UnaryOp(Node):
    op: str
    operand: Node

@dataclass
class PipeOp(Node):
    left: Node
    right: Node  # function name or call


# ─── Control Flow ────────────────────────────────────────────────────────────

@dataclass
class IfStmt(Node):
    condition: Node
    then_body: List[Node]
    elsif_clauses: List[tuple]  # list of (condition, body)
    else_body: Optional[List[Node]]

@dataclass
class UnlessStmt(Node):
    condition: Node
    then_body: List[Node]
    else_body: Optional[List[Node]]

@dataclass
class WhileStmt(Node):
    condition: Node
    body: List[Node]

@dataclass
class UntilStmt(Node):
    condition: Node
    body: List[Node]

@dataclass
class DoWhileStmt(Node):
    body: List[Node]
    condition: Node

@dataclass
class ForInStmt(Node):
    var: str
    iterable: Node
    body: List[Node]

@dataclass
class PostfixIf(Node):
    stmt: Node
    condition: Node
    negated: bool  # True = unless


# ─── Functions ───────────────────────────────────────────────────────────────

@dataclass
class FuncDef(Node):
    name: str
    params: List[str]          # parameter names
    defaults: List            # parallel list: None or default Node per param
    body: List[Node]

@dataclass
class FuncCall(Node):
    name: str
    args: List[Node]

@dataclass
class ReturnStmt(Node):
    value: Optional[Node]


# ─── Method Calls ────────────────────────────────────────────────────────────

@dataclass
class MethodCall(Node):
    receiver: Node
    method: str
    args: List[Node]
    block: Optional['Block'] = None

@dataclass
class SafeNavCall(Node):
    """receiver&.method(...) — returns nil if receiver is nil, otherwise calls method"""
    receiver: Node
    method: str
    args: List[Node]
    block: Optional['Block'] = None

@dataclass
class Block(Node):
    params: List[str]
    body: List[Node]


# ─── Iterator Sugar ──────────────────────────────────────────────────────────

@dataclass
class TimesLoop(Node):
    count: Node
    body: List[Node]
    var: Optional[str] = None  # optional |i| param

@dataclass
class EachLoop(Node):
    iterable: Node
    var: str
    body: List[Node]

@dataclass
class EachWithIndexLoop(Node):
    iterable: Node
    val_var: str
    idx_var: str
    body: List[Node]

@dataclass
class MapExpr(Node):
    iterable: Node
    var: str
    body: List[Node]


# ─── I/O ─────────────────────────────────────────────────────────────────────

@dataclass
class PrintStmt(Node):
    value: Node
    newline: bool  # puts=True, print=False

@dataclass
class DebugPrint(Node):
    value: Node

@dataclass
class InputExpr(Node):
    prompt: Optional[Node]
    cast: str  # 'str', 'int', 'float'


# ─── Program ─────────────────────────────────────────────────────────────────

@dataclass
class Program(Node):
    body: List[Node]

# ─── Error Handling ──────────────────────────────────────────────────────────

@dataclass
class RescueClause(Node):
    """A single rescue clause: rescue [TypeName] [=> e | e]"""
    error_type: Optional[str]   # None = catch-all; 'TypeError', 'RuntimeError', etc.
    rescue_var: Optional[str]   # variable bound to the error message
    body: List[Node]

@dataclass
class BeginRescue(Node):
    body: List[Node]
    rescue_clauses: List['RescueClause']   # one or more rescue clauses
    ensure_body: Optional[List[Node]]

    # Back-compat shims so existing code still works
    @property
    def rescue_var(self):
        return self.rescue_clauses[0].rescue_var if self.rescue_clauses else None
    @property
    def rescue_body(self):
        return self.rescue_clauses[0].body if self.rescue_clauses else []

@dataclass
class RaiseStmt(Node):
    message: Optional[Node]

# ─── Multi-file ───────────────────────────────────────────────────────────────

@dataclass
class RequireStmt(Node):
    path: Node

# ─── Regex ───────────────────────────────────────────────────────────────────

@dataclass
class RegexLiteral(Node):
    pattern: str
    flags: str

@dataclass
class MatchOp(Node):
    left: Node
    right: Node

# ─── Named Arguments ─────────────────────────────────────────────────────────

@dataclass
class NamedArg(Node):
    name: str
    value: Node

# ─── Case / When ─────────────────────────────────────────────────────────────

@dataclass
class CaseStmt(Node):
    subject: Optional[Node]           # case x  (or None for bare case)
    when_clauses: List[tuple]         # list of (values_list, body)
    else_body: Optional[List[Node]]

# ─── Destructuring Assignment ────────────────────────────────────────────────

@dataclass
class DestructAssign(Node):
    names: List[str]
    value: Node

# ─── Loop Control ─────────────────────────────────────────────────────────────

@dataclass
class NextStmt(Node):
    """next — skip to the next iteration (like Python's continue)"""
    pass

@dataclass
class BreakStmt(Node):
    """break / break value — exit a loop, optionally returning a value"""
    value: Optional[Node]

# ─── Constants ────────────────────────────────────────────────────────────────

@dataclass
class ConstAssign(Node):
    """UPPER_CASE = value — constant assignment with reassignment warning"""
    name: str
    value: Node

@dataclass
class LambdaLiteral(Node):
    """->( params ) { body }  — anonymous function / lambda value"""
    params: List[str]
    defaults: List        # parallel list: None or default Node per param
    body: List[Node]

@dataclass
class RecordDef(Node):
    """record Point(x, y) — lightweight named data object / struct"""
    name: str
    fields: List[str]
