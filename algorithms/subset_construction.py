
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
