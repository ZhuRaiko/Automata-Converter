def compile_regex(regex):
    """Backward-compatible wrapper for old interface: builds NFA from regex string."""
    ast = Parser(regex).parse()
    return thompson(ast)
"""
thompson.py

Thompson's Construction (Regex -> NFA)

This module translates a regular expression into an NFA using Thompson's
construction algorithm. The implementation now uses a recursive descent parser
and AST-based construction, following the reference implementation provided.

All function names, parameters, and return value structures are preserved.
All docstrings are kept, and new inline comments are added for clarity.
"""
import itertools

# === AST Node Definitions ===
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

class Parser:
    def __init__(self, expr):
        self.tokens = list(expr)
        self.pos = 0

    def parse(self):
        return self._parse_union()

    def _parse_union(self):
        left = self._parse_concat()
        while self._peek() in ('U', '|'):
            self._next()
            right = self._parse_concat()
            left = Union(left, right)
        return left

    def _parse_concat(self):
        nodes = []
        while self._peek() not in (None, ')', 'U', '|'):
            nodes.append(self._parse_star())
        if not nodes:
            return Epsilon()
        node = nodes[0]
        for nxt in nodes[1:]:
            node = Concat(node, nxt)
        return node

    def _parse_star(self):
        node = self._parse_atom()
        if self._peek() == '*':
            self._next()
            node = Star(node)
        return node

    def _parse_atom(self):
        ch = self._peek()
        if ch == '(':  # Parenthesized subexpression
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
        raise SyntaxError(f"Unexpected character: {ch}")

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self):
        ch = self._peek()
        self.pos += 1
        return ch

class NFA:
    def __init__(self, start, accept, transitions):
        self.start = start
        self.accept = accept
        self.transitions = transitions

# Global counter used to generate unique NFA state names like s0, s1, s2, ...
state_counter = itertools.count()

# Reset the state counter before compiling a new regex.
# This prevents state names from continuing to increment across repeated conversions,
# which otherwise makes the same regex appear to have different NFA numbering after each run.
def reset_state_counter():
    global state_counter
    state_counter = itertools.count()


def new_state():
    return f"s{next(state_counter)}"

def thompson(node):
    if isinstance(node, Symbol):
        s, f = new_state(), new_state()
        return NFA(s, f, {s: [(node.value, f)], f: []})
    if isinstance(node, Epsilon):
        s, f = new_state(), new_state()
        return NFA(s, f, {s: [(None, f)], f: []})
    if isinstance(node, Concat):
        n1 = thompson(node.left)
        n2 = thompson(node.right)
        n1.transitions.setdefault(n1.accept, []).append((None, n2.start))
        merged = {**n1.transitions, **n2.transitions}
        return NFA(n1.start, n2.accept, merged)
    if isinstance(node, Union):
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
        n = thompson(node.child)
        s, f = new_state(), new_state()
        trans = {s: [(None, n.start), (None, f)], f: []}
        for st, edges in n.transitions.items():
            trans.setdefault(st, []).extend(edges)
        trans.setdefault(n.accept, []).extend([(None, n.start), (None, f)])
        return NFA(s, f, trans)
    raise ValueError("Unknown AST node")

def compile_regex(regex):
    # Start each regex compilation with a fresh state counter so NFA state IDs are stable.
    reset_state_counter()
    ast = Parser(regex).parse()
    return thompson(ast)

def nfa_to_dict(nfa):
    def state_sort_key(state):
        if state.startswith('s') and state[1:].isdigit():
            return int(state[1:])
        return state

    states = set(nfa.transitions.keys())
    for edges in nfa.transitions.values():
        for _, to_state in edges:
            states.add(to_state)
    states = sorted(states, key=state_sort_key)
    transitions = []
    for from_state in sorted(nfa.transitions.keys(), key=state_sort_key):
        for symbol, to_state in nfa.transitions[from_state]:
            transitions.append({
                "from": from_state,
                "to": to_state,
                "symbol": symbol if symbol is not None else "ε"
            })
    return {
        "states": states,
        "transitions": transitions,
        "start_state": nfa.start,
        "final_state": nfa.accept,
    }
