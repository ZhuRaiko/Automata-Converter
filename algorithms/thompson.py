"""
thompson.py

Thompson's construction: regex -> NFA.

The regex is parsed with a recursive-descent parser that respects the usual
precedence levels (lowest to highest):

    union (`|`, `U`, or `+`)   <   concatenation   <   Kleene star (`*`)   <   atom

`+` is accepted as a synonym for `|` to match the algebraic notation used in
many automata textbooks (Hopcroft-Ullman, Sipser appendix), where the
language operators are written as `L1 + L2` (union), `L1 L2` (concatenation),
and `L*` (Kleene star). It is NOT the "one or more" Kleene-plus from
programming regex flavors — that operator is intentionally out of scope.

Each AST node is then translated into a small NFA "fragment" with a single
start and single accept state, and the fragments are glued together with
epsilon (None) transitions.

Atoms supported: single alphanumeric character, epsilon (`ε` or `E`), and
parenthesized subexpressions. Multi-character symbols, character classes,
escapes, and quantifiers like `+`/`?` are intentionally out of scope.

Public API:
    compile_regex(regex_str) -> NFA            # NFA object for chaining
    nfa_to_dict(nfa)         -> dict           # JSON-serializable shape

State naming is reset per call to `compile_regex` so the same regex compiles
to the same state names every time (helpful for tests and reproducibility).
"""

import itertools


# ----------------------------- AST node types ----------------------------- #
# These are deliberately tiny: just data carriers consumed by `thompson()`.

class Symbol:
    def __init__(self, value):
        self.value = value


class Epsilon:
    pass


class Star:
    def __init__(self, child):
        self.child = child


class Concat:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Union:
    def __init__(self, left, right):
        self.left = left
        self.right = right


# ----------------------------- Recursive-descent parser ----------------------------- #

class Parser:
    """Recursive-descent parser. One method per precedence level."""

    def __init__(self, expr):
        self.tokens = list(expr)
        self.pos = 0

    def parse(self):
        return self._parse_union()

    # Union operators: standard `|`, algebraic `+`, and the legacy `U`.
    _UNION_OPS = ('U', '|', '+')

    def _parse_union(self):
        # union := concat (('|' | '+' | 'U') concat)*
        left = self._parse_concat()
        while self._peek() in self._UNION_OPS:
            self._next()
            right = self._parse_concat()
            left = Union(left, right)
        return left

    def _parse_concat(self):
        # concat := star+   (implicit concatenation, empty -> epsilon)
        nodes = []
        while self._peek() not in (None, ')', *self._UNION_OPS):
            nodes.append(self._parse_star())
        if not nodes:
            return Epsilon()
        node = nodes[0]
        for nxt in nodes[1:]:
            node = Concat(node, nxt)
        return node

    def _parse_star(self):
        # star := atom '*'?
        node = self._parse_atom()
        if self._peek() == '*':
            self._next()
            node = Star(node)
        return node

    def _parse_atom(self):
        # atom := '(' union ')' | epsilon | alnum-char
        ch = self._peek()
        if ch == '(':
            self._next()
            node = self._parse_union()
            if self._peek() != ')':
                raise SyntaxError("Missing closing parenthesis")
            self._next()
            return node
        if ch in ('ε', 'E'):
            self._next()
            return Epsilon()
        if ch and ch.isalnum():
            self._next()
            return Symbol(ch)
        raise SyntaxError(f"Unexpected character: {ch!r}")

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self):
        ch = self._peek()
        self.pos += 1
        return ch


# ----------------------------- NFA construction ----------------------------- #

class NFA:
    """Compact NFA: single start state, single accept state, adjacency dict.

    `transitions` maps each state to a list of (symbol, next_state) pairs,
    where `symbol is None` represents an epsilon transition.
    """

    def __init__(self, start, accept, transitions):
        self.start = start
        self.accept = accept
        self.transitions = transitions


# Module-level counter used by `new_state()`; reset on every compile_regex call.
_state_counter = itertools.count()


def _reset_state_counter():
    global _state_counter
    _state_counter = itertools.count()


def new_state():
    return f"s{next(_state_counter)}"


def thompson(node):
    """Translate one AST node into an NFA fragment (recursive)."""
    if isinstance(node, Symbol):
        # Two fresh states, one labeled edge.
        s, f = new_state(), new_state()
        return NFA(s, f, {s: [(node.value, f)], f: []})

    if isinstance(node, Epsilon):
        # Two fresh states joined by an epsilon edge.
        s, f = new_state(), new_state()
        return NFA(s, f, {s: [(None, f)], f: []})

    if isinstance(node, Concat):
        # Glue left.accept --ε--> right.start.
        n1 = thompson(node.left)
        n2 = thompson(node.right)
        n1.transitions.setdefault(n1.accept, []).append((None, n2.start))
        merged = {**n1.transitions, **n2.transitions}
        return NFA(n1.start, n2.accept, merged)

    if isinstance(node, Union):
        # New start branches into both children; both children's accepts
        # converge into a new final state.
        n1 = thompson(node.left)
        n2 = thompson(node.right)
        s, f = new_state(), new_state()
        trans = {s: [(None, n1.start), (None, n2.start)], f: []}
        for st, edges in itertools.chain(n1.transitions.items(), n2.transitions.items()):
            trans.setdefault(st, []).extend(edges)
        trans.setdefault(n1.accept, []).append((None, f))
        trans.setdefault(n2.accept, []).append((None, f))
        return NFA(s, f, trans)

    if isinstance(node, Star):
        # New start with a bypass edge (matches empty) and an entry to the
        # child. Child accept loops back to child start and to the new accept.
        n = thompson(node.child)
        s, f = new_state(), new_state()
        trans = {s: [(None, n.start), (None, f)], f: []}
        for st, edges in n.transitions.items():
            trans.setdefault(st, []).extend(edges)
        trans.setdefault(n.accept, []).extend([(None, n.start), (None, f)])
        return NFA(s, f, trans)

    raise ValueError(f"Unknown AST node: {type(node).__name__}")


# ----------------------------- Public API ----------------------------- #

def compile_regex(regex):
    """Parse `regex` and return the resulting NFA object.

    The internal state counter is reset on every call so that compiling the
    same regex repeatedly yields identical state names.
    """
    _reset_state_counter()
    ast = Parser(regex).parse()
    return thompson(ast)


def nfa_to_dict(nfa):
    """Serialize an NFA to a JSON-friendly dict for the frontend."""
    states = set(nfa.transitions.keys())
    for edges in nfa.transitions.values():
        for _, to_state in edges:
            states.add(to_state)
    states = sorted(states)

    transitions = []
    for from_state, edges in nfa.transitions.items():
        for symbol, to_state in edges:
            transitions.append({
                "from": from_state,
                "to": to_state,
                "symbol": symbol if symbol is not None else "ε",
            })

    return {
        "states": states,
        "transitions": transitions,
        "start_state": nfa.start,
        "final_state": nfa.accept,
    }
