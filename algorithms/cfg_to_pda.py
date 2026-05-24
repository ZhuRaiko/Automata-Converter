"""
cfg_to_pda.py

Convert a context-free grammar (CFG) into a pushdown automaton (PDA) that
simulates a top-down (LL-style) derivation.

Construction:
  - Stack bottom marker is `Z`. An initial epsilon transition from q0 to q1
    replaces Z with [start_symbol, Z] so the start symbol is on top.
  - For each production `A -> alpha` we add an epsilon transition from q1 to
    itself that pops A and pushes alpha. Empty alpha (epsilon production)
    means "just pop A".
  - For each terminal `a` that appears in the grammar we add a matching
    transition q1 -> q1 with input `a` and stack_top `a` (pop + consume).
  - An epsilon transition q1 -> q2 with stack_top `Z` lets the machine reach
    the accept state when the input is fully consumed and only Z is on stack.

PUSH ORDER CONVENTION (important):
  In every transition, `push[0]` is the symbol that ends up on TOP of the
  stack after the push, and `push[-1]` is the symbol that ends up at the
  BOTTOM of the pushed group. With this convention, a production `S -> aSb`
  stores `push = ["a", "S", "b"]`, matching the natural reading of the rule
  and putting `a` on top of the stack so the simulator can consume it next.
  The simulator (see string_checker_pda.py) implements the push by iterating
  `reversed(push)`.
"""

from typing import Dict, List, Set


_EPSILON_WORDS = frozenset({'epsilon', 'lambda', 'null', 'nil', 'eps', 'n'})
_EPSILON_CHARS = frozenset({'ε', 'λ', 'Λ', 'Ε', '^'})


def _tokenize_rhs(rhs: str) -> List[str]:
    """Tokenize the right-hand side of a production into symbol tokens.

    Convention (school-project scope):
      - Each non-space character is a single symbol.
      - Recognized as the empty production (epsilon, -> []) when the WHOLE
        alternative equals one of these:
            ε  λ  Λ  Ε  ^                  (Greek + ASCII shortcut)
            "epsilon" / "lambda" / "null"
            "nil" / "eps" / "n"            (single-letter shortcut for "null")
            ""                             (empty alt, e.g. `S -> aSb |`)
        All word forms are case-insensitive.

    Conflict note: because the single letter `n` is treated as epsilon when it
    is the ENTIRE alternative, students who need `n` as a terminal should
    avoid writing it as a standalone alternative — write `S -> Xn` etc., or
    pick a different terminal letter.
    """
    rhs = rhs.strip()
    if not rhs:
        return []
    if rhs in _EPSILON_CHARS or rhs.lower() in _EPSILON_WORDS:
        return []
    rhs = rhs.replace(' ', '')
    return list(rhs)


def cfg_to_pda(cfg_text: str) -> Dict:
    """Parse CFG text and build the PDA dict consumed by the frontend.

    Input format: one production per line, e.g.
        S -> aSb | ε
        S -> a S b | epsilon

    Returns a PDA dict shaped like:
        {
          "states":              ["q0", "q1", "q2"],
          "stack_alphabet":      [<nonterminals>, <terminals>, "Z"],
          "transitions":         [ {from, input, stack_top, to, push}, ... ],
          "start_state":         "q0",
          "start_stack_symbol":  "Z",
          "accept_states":       ["q2"]
        }
    """
    # Normalize arrow variants and split into non-empty trimmed lines.
    text = cfg_text.replace('→', '->').replace('⇒', '->')
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    productions: Dict[str, List[List[str]]] = {}
    nonterminals: List[str] = []  # preserves insertion order; first one is start

    for ln in lines:
        if '->' not in ln:
            continue
        left, right = ln.split('->', 1)
        left = left.strip()
        if not left:
            continue
        if left not in productions:
            nonterminals.append(left)
            productions[left] = []
        for alt in right.split('|'):
            productions[left].append(_tokenize_rhs(alt))

    # Degenerate grammar -> trivial PDA that accepts only the empty string.
    if not productions:
        return {
            "states": ["q0", "q1", "q2"],
            "stack_alphabet": ["Z"],
            "transitions": [
                {"from": "q0", "input": "", "stack_top": "Z", "to": "q1", "push": ["Z"]},
                {"from": "q1", "input": "", "stack_top": "Z", "to": "q2", "push": ["Z"]},
            ],
            "start_state": "q0",
            "start_stack_symbol": "Z",
            "accept_states": ["q2"],
        }

    nt_set = set(productions.keys())
    terminals: Set[str] = set()
    for rhss in productions.values():
        for rhs in rhss:
            for sym in rhs:
                if sym and sym not in nt_set:
                    terminals.add(sym)

    transitions: List[Dict] = []

    # (1) Initial transition: pop Z, push [start_symbol, Z] so start_symbol is on top.
    start_symbol = nonterminals[0]
    transitions.append({
        "from": "q0",
        "input": "",
        "stack_top": "Z",
        "to": "q1",
        "push": [start_symbol, "Z"],
    })

    # (2) Production transitions: pop A, push the body in natural order.
    # push[0] is the leftmost symbol of the body and ends up on top.
    for A, rhss in productions.items():
        for body in rhss:
            transitions.append({
                "from": "q1",
                "input": "",
                "stack_top": A,
                "to": "q1",
                "push": list(body),
            })

    # (3) Terminal-matching transitions: consume the terminal from input AND stack.
    for term in sorted(terminals):
        transitions.append({
            "from": "q1",
            "input": term,
            "stack_top": term,
            "to": "q1",
            "push": [],
        })

    # (4) Accept move: stack has Z on top and input is empty -> jump to q2.
    transitions.append({
        "from": "q1",
        "input": "",
        "stack_top": "Z",
        "to": "q2",
        "push": ["Z"],
    })

    return {
        "states": ["q0", "q1", "q2"],
        "stack_alphabet": sorted(nt_set) + sorted(terminals) + ["Z"],
        "transitions": transitions,
        "start_state": "q0",
        "start_stack_symbol": "Z",
        "accept_states": ["q2"],
    }


# Name expected by app.py
convert_cfg_to_pda = cfg_to_pda
