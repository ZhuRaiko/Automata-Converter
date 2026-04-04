"""
cfg_to_pda.py

Convert a user-provided context-free grammar (CFG) into a simple PDA suited
for a top-down (LL-style) simulation. The conversion here creates a PDA that
implements the following idea:

- The stack initially contains a bottom marker 'Z'. An initial transition pushes
  the grammar's start symbol on top of Z.
- For each production A -> alpha, the PDA has an epsilon transition that
  replaces A on the stack with the sequence alpha (push order preserves left->right).
- For each terminal 'a' there is a transition that consumes the input 'a' when
  the top of the stack is also 'a' (pop+consume).
- Acceptance is modeled by reaching a special accept state with the stack at Z
  and no remaining input.

Output PDA format matches the project's frontend expectations.
"""

from typing import Dict, List, Tuple, Set


def _tokenize_rhs(rhs: str) -> List[str]:
    """Convert a production RHS string into a list of symbol tokens.

    This tokenizer is intentionally simple and assumes productions like
    `aSb` or `a S b` where nonterminals are uppercase letters (e.g., 'S') and
    terminals are other characters (lowercase letters, digits, punctuation).

    The function removes spaces and then treats each remaining character as a
    token. The special epsilon symbol 'ε' (or the literal 'epsilon') yields an
    empty list meaning the production produces the empty string.
    """
    rhs = rhs.strip()
    if not rhs:
        return []
    # Accept both the Greek epsilon and the ASCII 'epsilon'
    if rhs == 'ε' or rhs.lower() == 'epsilon':
        return []
    # Remove spaces and treat each character as a token for simplicity
    rhs = rhs.replace(' ', '')
    return [ch for ch in rhs]


def cfg_to_pda(cfg_text: str) -> Dict:
    """Parse user-entered CFG text and construct a PDA dict.

    Input format: one rule per line. Example:
        S -> aSb | ε

    Returns a PDA dict with fields:
      - states: ["q0","q1","q2"]
      - stack_alphabet: [nonterminals..., terminals..., "Z"]
      - transitions: [ {from, input, stack_top, to, push}, ... ]
      - start_state: "q0"
      - start_stack_symbol: "Z"
      - accept_states: ["q2"]
    """
    # Normalize arrows and split lines
    text = cfg_text.replace('→', '->')
    text = text.replace('→', '->')
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    productions = {}  # nonterminal -> list of RHS token lists
    nonterminals: List[str] = []

    for ln in lines:
        # Support variants like 'S -> aSb | ε' or 'S->aSb|ε'
        if '->' not in ln:
            continue
        left, right = ln.split('->', 1)
        left = left.strip()
        if not left:
            continue
        # Record first LHS as start symbol if not set
        if left not in productions:
            nonterminals.append(left)
            productions[left] = []

        # Split alternatives by '|'
        alts = [alt.strip() for alt in right.split('|')]
        for alt in alts:
            tokens = _tokenize_rhs(alt)
            productions[left].append(tokens)

    if not productions:
        # Empty grammar: return a trivial PDA that accepts only the empty string
        pda = {
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
        return pda

    # Build terminal set: any symbol that is not listed as a nonterminal
    nt_set = set(productions.keys())
    terminals: Set[str] = set()
    for lhs, rhss in productions.items():
        for rhs in rhss:
            for sym in rhs:
                if sym and sym not in nt_set:
                    terminals.add(sym)

    # Compose transitions
    transitions = []

    # Initial transition: push start symbol on top of Z
    start_symbol = nonterminals[0]
    transitions.append({
        "from": "q0",
        "input": "",
        "stack_top": "Z",
        "to": "q1",
        "push": ["Z", start_symbol],
    })

    # For each production A -> alpha, add epsilon transition that replaces A
    for A, rhss in productions.items():
        for body in rhss:
            # body is a list of symbols; pushing an empty list means pop A only
            push_list = body[:] if body else []
            transitions.append({
                "from": "q1",
                "input": "",
                "stack_top": A,
                "to": "q1",
                "push": push_list,
            })

    # For each terminal, add a matching transition that consumes the input character
    for term in sorted(terminals):
        transitions.append({
            "from": "q1",
            "input": term,
            "stack_top": term,
            "to": "q1",
            "push": [],
        })

    # Accept transition: when stack has only Z and input is empty, go to q2
    transitions.append({
        "from": "q1",
        "input": "",
        "stack_top": "Z",
        "to": "q2",
        "push": ["Z"],
    })

    pda = {
        "states": ["q0", "q1", "q2"],
        "stack_alphabet": sorted(list(nt_set)) + sorted(list(terminals)) + ["Z"],
        "transitions": transitions,
        "start_state": "q0",
        "start_stack_symbol": "Z",
        "accept_states": ["q2"],
    }

    return pda


# Export the function expected by app.py
convert_cfg_to_pda = cfg_to_pda
