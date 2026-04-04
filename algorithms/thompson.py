<<<<<<< HEAD
def compile_regex(regex):
    """Backward-compatible wrapper for old interface: builds NFA from regex string."""
    ast = Parser(regex).parse()
    return thompson(ast)
=======
>>>>>>> 5b86f94d881866a8f7a5d41517aebf28a79cc26f
"""
thompson.py

Thompson's Construction (Regex -> NFA)

This module translates a regular expression into an NFA using Thompson's
<<<<<<< HEAD
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
    ast = Parser(regex).parse()
    return thompson(ast)

def nfa_to_dict(nfa):
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
                "symbol": symbol if symbol is not None else "ε"
            })
    return {
        "states": states,
        "transitions": transitions,
        "start_state": nfa.start,
        "final_state": nfa.accept,
=======
construction algorithm. The implementation follows the canonical stack-based
Thompson approach: convert infix regex to postfix with an explicit concatenation
operator, then evaluate the postfix expression to build NFA fragments.

Notes:
- Epsilon transitions use the symbol 'E'.
- The classes and functions are modeled after the Java structure described in
  the project specification: `Trans`, `NFA`, `kleene`, `concat`, `union`, and
  `compile_regex` (renamed from `compile`).

Every function and major block includes docstrings and inline comments to
ensure readability for students.
"""

from typing import List, Dict, Set, Tuple


class Trans:
    """Transition object representing a labeled edge in an NFA.

    Attributes:
        state_from (int): source state id
        state_to (int): destination state id
        trans_symbol (str): transition symbol (character or 'E' for epsilon)
    """

    def __init__(self, v1: int, v2: int, sym: str):
        self.state_from = v1
        self.state_to = v2
        self.trans_symbol = sym


class NFA:
    """Simple NFA representation used by Thompson's construction.

    Attributes:
        states (List[int]): list of state ids (0..n-1)
        transitions (List[Trans]): list of Trans objects
        final_state (int): id of the final (accepting) state

    The NFA's start state is always assumed to be state 0.
    """

    def __init__(self, size: int = None, char: str = None):
        # Initialize empty structure
        self.states: List[int] = []
        self.transitions: List[Trans] = []
        self.final_state: int = 0

        # Construct minimal NFA for a single character: 0 --c--> 1
        if char is not None:
            self.states = [0, 1]
            self.transitions = [Trans(0, 1, char)]
            self.final_state = 1
        # Initialize with a given number of states
        elif size is not None:
            self.states = list(range(size))
            self.transitions = []
            self.final_state = max(0, size - 1)

    def setStateSize(self, size: int):
        """Resize the state list to contain `size` states (0..size-1)."""
        self.states = list(range(size))
        self.final_state = max(0, size - 1)

    def display(self) -> None:
        """Prints a human-readable representation of the NFA."""
        print("States:", self.states)
        print("Transitions:")
        for t in self.transitions:
            print(f"  {t.state_from} --{t.trans_symbol}--> {t.state_to}")
        print("Final state:", self.final_state)


# ------------------------- Thompson primitives ------------------------- #


def _copy_transitions_with_offset(transitions: List[Trans], offset: int) -> List[Trans]:
    """Return a new list of transitions reindexed by `offset`.

    This helper is used when combining NFAs to avoid state id collisions.
    """
    return [Trans(t.state_from + offset, t.state_to + offset, t.trans_symbol) for t in transitions]


def kleene(n: NFA) -> NFA:
    """Apply Kleene star (*) to NFA `n` and return the new NFA.

    The construction creates two new states: a new start and a new final.
    Epsilon transitions connect the new start to the old start and new final,
    and the old final back to the old start and to the new final.
    """
    old_size = len(n.states)

    # New NFA will have two extra states (new start and new final)
    new_size = old_size + 2
    new_nfa = NFA(size=new_size)

    # Reindex old transitions by +1 so they sit between the new start (0)
    # and the new final (new_size-1)
    new_nfa.transitions.extend(_copy_transitions_with_offset(n.transitions, 1))

    # Epsilon transitions implementing the Kleene connections
    # newStart (0) -> oldStart (1)
    new_nfa.transitions.append(Trans(0, 1, 'E'))
    # oldFinal -> oldStart
    new_nfa.transitions.append(Trans(n.final_state + 1, 1, 'E'))
    # oldFinal -> newFinal
    new_nfa.transitions.append(Trans(n.final_state + 1, new_size - 1, 'E'))
    # newStart -> newFinal (allows empty string)
    new_nfa.transitions.append(Trans(0, new_size - 1, 'E'))

    new_nfa.final_state = new_size - 1
    return new_nfa


def concat(n: NFA, m: NFA) -> NFA:
    """Concatenate NFA `n` followed by NFA `m` and return the new NFA.

    The states of `m` are reindexed with an offset equal to the size of `n`.
    An epsilon transition is added from `n`'s final state to `m`'s start.
    """
    n_size = len(n.states)
    m_size = len(m.states)

    new_size = n_size + m_size
    new_nfa = NFA(size=new_size)

    # Copy n's transitions (no offset)
    new_nfa.transitions.extend([Trans(t.state_from, t.state_to, t.trans_symbol) for t in n.transitions])

    # Copy m's transitions with offset
    new_nfa.transitions.extend(_copy_transitions_with_offset(m.transitions, n_size))

    # Connect n.final -> m.start (which is n_size after offset)
    new_nfa.transitions.append(Trans(n.final_state, n_size, 'E'))

    # New final state is m.final_state shifted by n_size
    new_nfa.final_state = n_size + m.final_state

    return new_nfa


def union(n: NFA, m: NFA) -> NFA:
    """Return new NFA representing the union (alternation) of `n` and `m`.

    Creates a new start and new final; epsilon transitions connect the new
    start to both old starts and both old finals to the new final.
    """
    n_size = len(n.states)
    m_size = len(m.states)

    # new start + n + m + new final
    new_size = 1 + n_size + m_size + 1
    new_nfa = NFA(size=new_size)

    # Copy n transitions into offset 1
    new_nfa.transitions.extend(_copy_transitions_with_offset(n.transitions, 1))
    # Copy m transitions into offset 1 + n_size
    new_nfa.transitions.extend(_copy_transitions_with_offset(m.transitions, 1 + n_size))

    # Epsilon from new start (0) to n.start (1) and m.start (1 + n_size)
    new_nfa.transitions.append(Trans(0, 1, 'E'))
    new_nfa.transitions.append(Trans(0, 1 + n_size, 'E'))

    # Epsilon from n.final and m.final to new final
    new_final = new_size - 1
    new_nfa.transitions.append(Trans(n.final_state + 1, new_final, 'E'))
    new_nfa.transitions.append(Trans(m.final_state + 1 + n_size, new_final, 'E'))

    new_nfa.final_state = new_final
    return new_nfa


# ------------------------- Regex parsing / compilation ------------------------- #


def _is_symbol(c: str) -> bool:
    """Return True if character `c` should be treated as a symbol (operand).

    Symbols are any characters that are not the operators: '|', '*', '.', '(', ')'.
    """
    return c not in {'|', '*', '.', '(', ')'}


def _insert_concat(regex: str) -> str:
    """Insert explicit concatenation operator '.' where concatenation is implied.

    Example: 'ab' -> 'a.b', 'a(b)' -> 'a.(b', 'a* b' -> 'a*.b' depending on
    token adjacency. This makes the parsing to postfix simple.
    """
    out = []
    for i, c in enumerate(regex):
        out.append(c)
        if i + 1 < len(regex):
            d = regex[i + 1]
            # If c is symbol or '*' or ')', and d is symbol or '(', then we need '.'
            if ( (_is_symbol(c) or c == '*' or c == ')') and (_is_symbol(d) or d == '(') ):
                out.append('.')
    return ''.join(out)


def _infix_to_postfix(regex: str) -> str:
    """Convert an infix regex (with '.' concatenation) to postfix via shunting-yard.

    Operators precedence: '*' (3, unary, right), '.' (2), '|' (1)
    """
    prec = {'*': 3, '.': 2, '|': 1}
    output: List[str] = []
    stack: List[str] = []

    for c in regex:
        if _is_symbol(c):
            output.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
        else:
            # operator
            while stack and stack[-1] != '(' and prec.get(stack[-1], 0) >= prec.get(c, 0):
                output.append(stack.pop())
            stack.append(c)

    while stack:
        output.append(stack.pop())

    return ''.join(output)


def valid_regex(regex: str) -> bool:
    """Basic validation for balanced parentheses and allowed characters.

    Returns True if parentheses are balanced and regex is non-empty.
    This is conservative and intentionally simple for educational use.
    """
    if not regex:
        return False
    # Check parentheses balance
    balance = 0
    for ch in regex:
        if ch == '(':
            balance += 1
        elif ch == ')':
            balance -= 1
            if balance < 0:
                return False
    if balance != 0:
        return False
    return True


def compile_regex(regex: str) -> NFA:
    """Compile a regular expression string into an NFA using Thompson's method.

    Steps:
    1. Validate the regex (simple checks).
    2. Insert explicit concatenation '.' operators.
    3. Convert to postfix notation.
    4. Evaluate postfix and build NFA fragments using a stack.

    Supported operators: concatenation ('.' inserted automatically), alternation '|',
    kleene star '*', parentheses '(', ')'. Operands are any characters other than
    the operators above.

    Returns:
        NFA: an NFA object whose start state is 0 and whose final_state is set.
    """
    # Basic validation
    if not valid_regex(regex):
        raise ValueError("Invalid regular expression: parentheses mismatch or empty")

    # Preprocess: insert explicit concatenation
    with_concat = _insert_concat(regex)

    # Convert to postfix
    postfix = _infix_to_postfix(with_concat)

    # Evaluate postfix to build the NFA
    stack: List[NFA] = []
    for token in postfix:
        if _is_symbol(token):
            # Push single-character NFA
            stack.append(NFA(char=token))
        elif token == '*':
            # Kleene star: unary operator
            if not stack:
                raise ValueError("Malformed regex: '*' operator with no operand")
            nfa1 = stack.pop()
            stack.append(kleene(nfa1))
        elif token == '.':
            # Concatenation: binary operator
            if len(stack) < 2:
                raise ValueError("Malformed regex: '.' operator requires two operands")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(concat(nfa1, nfa2))
        elif token == '|':
            # Union: binary operator
            if len(stack) < 2:
                raise ValueError("Malformed regex: '|' operator requires two operands")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(union(nfa1, nfa2))
        else:
            raise ValueError(f"Unsupported token in postfix regex: {token}")

    if len(stack) != 1:
        raise ValueError("Malformed regular expression: leftover fragments after compilation")

    result_nfa = stack.pop()
    return result_nfa


def nfa_to_dict(nfa: NFA) -> Dict:
    """Convert an NFA object into a JSON-serializable Python dict.

    The output format matches the frontend's expectations:
    {
        "states": [...],
        "transitions": [{"from": int, "to": int, "symbol": str}, ...],
        "start_state": 0,
        "final_state": int
    }
    """
    return {
        "states": nfa.states,
        "transitions": [
            {"from": t.state_from, "to": t.state_to, "symbol": t.trans_symbol}
            for t in nfa.transitions
        ],
        "start_state": 0,
        "final_state": nfa.final_state,
>>>>>>> 5b86f94d881866a8f7a5d41517aebf28a79cc26f
    }
