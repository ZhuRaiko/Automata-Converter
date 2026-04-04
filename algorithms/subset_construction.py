<<<<<<< HEAD

import itertools

def epsilon_closure(states, transitions):
    """
    Compute the epsilon-closure of a set of NFA states.
    Args:
        states: set of NFA state names (strings)
        transitions: dict mapping state -> list of (symbol, state) pairs
    Returns:
        Set of states reachable from the input set via epsilon (None) transitions.
    """
    closure = set(states)
    stack = list(states)
    while stack:
        st = stack.pop()
        for sym, nxt in transitions.get(st, []):
            if sym is None and nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure

def move(states, symbol, transitions):
    """
    Compute the set of states reachable from 'states' via a given symbol.
    Args:
        states: set of NFA state names
        symbol: transition symbol (string)
        transitions: dict mapping state -> list of (symbol, state) pairs
    Returns:
        Set of states reachable via the given symbol.
    """
    return {nxt for st in states for sym, nxt in transitions.get(st, []) if sym == symbol}

def convert_nfa_to_dfa(nfa):
    """
    Subset construction: Convert an NFA (in dict format) to a DFA (dict format).
    Args:
        nfa: dict with keys 'states', 'transitions', 'start_state', 'final_state'
    Returns:
        DFA dict with keys 'states', 'alphabet', 'transitions', 'start_state', 'accept_states'
    """
    # Convert NFA dict to internal NFA object for easier handling
    class NFA:
        def __init__(self, start, accept, transitions):
            self.start = start
            self.accept = accept
            self.transitions = transitions
    # Build transitions dict: state -> list of (symbol, state)
    transitions = {}
    for t in nfa['transitions']:
        # Use None for epsilon transitions
        transitions.setdefault(t['from'], []).append((t['symbol'] if t['symbol'] != 'ε' else None, t['to']))
    nfa_obj = NFA(nfa['start_state'], nfa['final_state'], transitions)

    # Subset construction algorithm
    start = frozenset(epsilon_closure({nfa_obj.start}, nfa_obj.transitions))
    d_states = set()
    ordered_states = []
    queue = [start]
    d_states.add(start)
    d_trans = {}
    # Compute input alphabet (all non-epsilon symbols)
    alpha = sorted({sym for edges in nfa_obj.transitions.values() for sym, _ in edges if sym is not None})
    while queue:
        T = queue.pop(0)
        ordered_states.append(T)
        d_trans[T] = {}
        for sym in sorted(alpha):
            # For each symbol, compute the epsilon-closure of the move
            U = frozenset(epsilon_closure(move(T, sym, nfa_obj.transitions), nfa_obj.transitions))
            d_trans[T][sym] = U
            if U not in d_states:
                d_states.add(U)
                queue.append(U)
    # Add trap state if needed (empty set)
    trap = frozenset()
    if trap not in d_states:
        d_states.add(trap)
        ordered_states.append(trap)
    # Ensure all transitions are defined for every symbol
    for T in list(d_states):
        for sym in alpha:
            d_trans.setdefault(T, {})
            d_trans[T].setdefault(sym, trap)
    # Accepting DFA states are those containing the NFA accept state
    accepts = {T for T in d_states if nfa_obj.accept in T}
    # Assign state names (q0, q1, ...) in BFS order
    names = {}
    names[start] = "q0"
    counter = 1
    for state in ordered_states:
        if state != start:
            names[state] = f"q{counter}"
            counter += 1
    # Build DFA dict for frontend
    state_ids = {state: i for i, state in enumerate(ordered_states)}
    transitions_json = {str(state_ids[s]): {sym: state_ids[t] for sym, t in d_trans[s].items()} for s in ordered_states}
    accept_ids = [state_ids[s] for s in accepts]
    return {
        "states": list(range(len(ordered_states))),
        "alphabet": alpha,
        "transitions": transitions_json,
        "start_state": 0,
        "accept_states": accept_ids,
    }

def epsilon_closure(states, transitions):
    closure = set(states)
    stack = list(states)
    while stack:
        st = stack.pop()
        for sym, nxt in transitions.get(st, []):
            if sym is None and nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure

def move(states, symbol, transitions):
    return {nxt for st in states for sym, nxt in transitions.get(st, []) if sym == symbol}

def convert_nfa_to_dfa(nfa):
    # Convert NFA dict to internal NFA object
    class NFA:
        def __init__(self, start, accept, transitions):
            self.start = start
            self.accept = accept
            self.transitions = transitions
    # Build transitions dict
    transitions = {}
    for t in nfa['transitions']:
        transitions.setdefault(t['from'], []).append((t['symbol'] if t['symbol'] != 'ε' else None, t['to']))
    nfa_obj = NFA(nfa['start_state'], nfa['final_state'], transitions)

    # Subset construction
    start = frozenset(epsilon_closure({nfa_obj.start}, nfa_obj.transitions))
    d_states = set()
    ordered_states = []
    queue = [start]
    d_states.add(start)
    d_trans = {}
    alpha = sorted({sym for edges in nfa_obj.transitions.values() for sym, _ in edges if sym is not None})
    while queue:
        T = queue.pop(0)
        ordered_states.append(T)
        d_trans[T] = {}
        for sym in sorted(alpha):
            U = frozenset(epsilon_closure(move(T, sym, nfa_obj.transitions), nfa_obj.transitions))
            d_trans[T][sym] = U
            if U not in d_states:
                d_states.add(U)
                queue.append(U)
    trap = frozenset()
    if trap not in d_states:
        d_states.add(trap)
        ordered_states.append(trap)
    for T in list(d_states):
        for sym in alpha:
            d_trans.setdefault(T, {})
            d_trans[T].setdefault(sym, trap)
    accepts = {T for T in d_states if nfa_obj.accept in T}
    names = {}
    names[start] = "q0"
    counter = 1
    for state in ordered_states:
        if state != start:
            names[state] = f"q{counter}"
            counter += 1
    # Build DFA dict
    state_ids = {state: i for i, state in enumerate(ordered_states)}
    transitions_json = {str(state_ids[s]): {sym: state_ids[t] for sym, t in d_trans[s].items()} for s in ordered_states}
    accept_ids = [state_ids[s] for s in accepts]
    return {
        "states": list(range(len(ordered_states))),
        "alphabet": alpha,
        "transitions": transitions_json,
        "start_state": 0,
        "accept_states": accept_ids,
    }
=======
"""
subset_construction.py

Subset Construction algorithm: converts an NFA (as produced by
`thompson.nfa_to_dict`) into a deterministic DFA. The DFA is represented as a
JSON-serializable dict suitable for the frontend.

Key points:
- Epsilon-closure is computed by following 'E' transitions recursively.
- A sink (dead) state is added if a move leads to the empty set to ensure the
  DFA is total (one transition per symbol from every state).

All functions include docstrings explaining inputs and outputs.
"""

from typing import Dict, List, Set, Tuple
from collections import defaultdict


def epsilon_closure(state_set: Set[int], trans_map: Dict[int, Dict[str, List[int]]]) -> Set[int]:
    """Compute the epsilon-closure of `state_set` given the NFA transition map.

    trans_map: mapping state -> symbol -> list of destination states
    'E' is treated as the epsilon symbol.

    Returns a set of NFA states reachable from `state_set` by following only
    epsilon ('E') transitions (including the original states).
    """
    stack = list(state_set)
    closure = set(state_set)

    while stack:
        s = stack.pop()
        # Follow epsilon transitions from s
        for t in trans_map.get(s, {}).get('E', []):
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def build_transition_map(nfa: Dict) -> Dict[int, Dict[str, List[int]]]:
    """Create a convenient transition map from the NFA dict.

    Result: { state: { symbol: [dest, ...], ... }, ... }
    """
    tmap = defaultdict(lambda: defaultdict(list))
    for t in nfa.get('transitions', []):
        src = t['from']
        sym = t['symbol']
        dst = t['to']
        tmap[src][sym].append(dst)
    return tmap


def nfa_to_dfa(nfa: Dict) -> Dict:
    """Convert an NFA (dict) to a DFA (dict) via subset construction.

    Input NFA format matches `nfa_to_dict` from `thompson.py`:
    {
      "states": [...],
      "transitions": [{"from": int, "to": int, "symbol": str}, ...],
      "start_state": 0,
      "final_state": int
    }

    Output DFA format:
    {
      "states": [0,1,2,...],
      "alphabet": ["a","b",...],
      "transitions": { "0": {"a": 1, "b": 2}, ... },
      "start_state": 0,
      "accept_states": [2,3]
    }
    """
    # Build quick lookup map for NFA transitions
    tmap = build_transition_map(nfa)

    # Compute input alphabet (exclude epsilon 'E')
    alphabet = sorted({t['symbol'] for t in nfa.get('transitions', []) if t['symbol'] != 'E'})

    # Start from epsilon-closure of the NFA start state
    start0 = nfa.get('start_state', 0)
    start_closure = frozenset(epsilon_closure({start0}, tmap))

    # Map each DFA state (a frozenset of NFA states) to an integer id
    dstate_id_map = {start_closure: 0}
    id_dstate_map = {0: start_closure}
    queue = [start_closure]

    dtrans = {}  # state_id -> { symbol: target_id }
    accept_states = set()
    next_id = 1

    # If the start closure contains the NFA final state, mark it accepting
    nfa_final = nfa.get('final_state')
    if nfa_final in start_closure:
        accept_states.add(0)

    # Process unprocessed DFA states
    while queue:
        current = queue.pop(0)
        cur_id = dstate_id_map[current]
        dtrans[cur_id] = {}

        # For each alphabet symbol compute move and epsilon-closure
        for sym in alphabet:
            move_set = set()
            # For each NFA state in the current DFA-state, follow sym transitions
            for s in current:
                for dst in tmap.get(s, {}).get(sym, []):
                    move_set.add(dst)
            # Compute epsilon-closure of the moved set
            target_closure = frozenset(epsilon_closure(move_set, tmap))

            # If target_closure not yet seen, assign new id and enqueue
            if target_closure not in dstate_id_map:
                dstate_id_map[target_closure] = next_id
                id_dstate_map[next_id] = target_closure
                # If this new DFA-state contains the NFA final, mark accepting
                if nfa_final in target_closure:
                    accept_states.add(next_id)
                queue.append(target_closure)
                next_id += 1

            # Record transition (use integer ids)
            dtrans[cur_id][sym] = dstate_id_map[target_closure]

    # Ensure totality: if any transition leads to the empty set, create a sink state
    # Represent the empty frozenset() as a state if it appears in the map
    # (the loop above already created it if encountered)

    # Convert dtrans keys to strings for JSON-friendly structure
    transitions_json = {str(sid): {sym: tid for sym, tid in trans.items()} for sid, trans in dtrans.items()}

    # Build DFA dict as required
    dfa = {
        "states": list(range(len(dtrans))) ,
        "alphabet": alphabet,
        "transitions": transitions_json,
        "start_state": 0,
        "accept_states": sorted(list(accept_states)),
    }

    return dfa


# For convenience expose a single function name expected by app.py
convert_nfa_to_dfa = nfa_to_dfa
>>>>>>> 5b86f94d881866a8f7a5d41517aebf28a79cc26f
