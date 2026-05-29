"""
subset_construction.py

Subset (powerset) construction: NFA -> DFA, followed by Hopcroft minimization.

Pipeline:
    NFA dict  -->  epsilon-closure / move BFS  -->  raw DFA
              -->  Hopcroft partition refinement  -->  minimal DFA dict

A trap (dead) state is added only when at least one transition would otherwise
be undefined, so simple regexes (e.g. `a`) do not get a dangling sink node in
the rendered diagram.

Public API:
    convert_nfa_to_dfa(nfa_dict) -> dfa_dict
        nfa_dict keys: states, transitions, start_state, final_state
        dfa_dict keys: states, alphabet, transitions, start_state, accept_states

Complexity:
    Subset construction: O(2^|N| * |Sigma|) worst case, much less in practice.
    Hopcroft minimization: O(|Q| * |Sigma| * log |Q|).
"""

from collections import deque
from typing import Dict, List, Set, FrozenSet, Tuple, Any


# ----------------------------- Core NFA helpers ----------------------------- #

def epsilon_closure(states, transitions):
    """All NFA states reachable from `states` via epsilon (None) transitions.

    Standard worklist DFS. Returns a Python set (not frozen) so callers can
    decide whether to freeze for use as a dict key.
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
    """States reachable from `states` by consuming exactly one `symbol` edge.

    Epsilon closure is NOT applied here; the caller wraps the result.
    """
    return {nxt for st in states for sym, nxt in transitions.get(st, []) if sym == symbol}


# --------------------------- Subset construction --------------------------- #

def _build_raw_dfa(nfa: Dict[str, Any]):
    """Run subset construction and return (ordered_states, alpha, d_trans, accept_state,
    accept_states_set, trap_needed) where d_trans maps frozenset -> {symbol: frozenset}.

    The trap state (empty frozenset) is NOT inserted here; the caller decides
    whether the final DFA needs it.
    """
    # Flatten the transition list into a per-state adjacency map.
    transitions: Dict[str, List[Tuple[Any, str]]] = {}
    for t in nfa['transitions']:
        sym = None if t['symbol'] == 'ε' else t['symbol']
        transitions.setdefault(t['from'], []).append((sym, t['to']))

    nfa_accept = nfa['final_state']

    # Input alphabet = all non-epsilon symbols that appear in any transition.
    alpha = sorted({sym for edges in transitions.values()
                    for sym, _ in edges if sym is not None})

    start = frozenset(epsilon_closure({nfa['start_state']}, transitions))
    ordered_states: List[FrozenSet[str]] = [start]
    seen: Set[FrozenSet[str]] = {start}
    d_trans: Dict[FrozenSet[str], Dict[str, FrozenSet[str]]] = {}
    queue = deque([start])

    trap_needed = False
    while queue:
        T = queue.popleft()
        d_trans[T] = {}
        for sym in alpha:
            U = frozenset(epsilon_closure(move(T, sym, transitions), transitions))
            if not U:
                # Undefined transition -> the DFA will need a trap state.
                trap_needed = True
            d_trans[T][sym] = U
            if U and U not in seen:
                seen.add(U)
                ordered_states.append(U)
                queue.append(U)

    accept_states = {T for T in ordered_states if nfa_accept in T}
    return ordered_states, alpha, d_trans, accept_states, trap_needed


# ----------------------------- Minimization ----------------------------- #

def _hopcroft_minimize(states: List[int],
                       alphabet: List[str],
                       trans: Dict[int, Dict[str, int]],
                       accepts: Set[int],
                       start: int) -> Tuple[List[int], Dict[int, Dict[str, int]], Set[int], int]:
    """Hopcroft's algorithm: partition states into equivalence classes.

    Returns the minimized DFA components keyed by NEW state ids (small ints,
    BFS-ordered from the new start state).
    """
    non_accepts = set(states) - accepts
    # Initial partition: accepting vs. non-accepting (drop empty groups).
    P: List[Set[int]] = [g for g in (accepts.copy(), non_accepts) if g]
    W: List[Set[int]] = [g.copy() for g in P]

    # Precompute inverse transitions: for each symbol, target -> set of sources.
    inverse: Dict[str, Dict[int, Set[int]]] = {a: {} for a in alphabet}
    for s in states:
        for a in alphabet:
            t = trans.get(s, {}).get(a)
            if t is not None:
                inverse[a].setdefault(t, set()).add(s)

    while W:
        A = W.pop()
        for a in alphabet:
            # X = states whose `a`-transition lands in A.
            X: Set[int] = set()
            for tgt in A:
                X |= inverse[a].get(tgt, set())
            if not X:
                continue
            new_P: List[Set[int]] = []
            for Y in P:
                inter = Y & X
                diff = Y - X
                if inter and diff:
                    new_P.append(inter)
                    new_P.append(diff)
                    # Replace Y in the worklist if present; otherwise add the smaller half.
                    if Y in W:
                        W.remove(Y)
                        W.append(inter)
                        W.append(diff)
                    else:
                        W.append(inter if len(inter) <= len(diff) else diff)
                else:
                    new_P.append(Y)
            P = new_P

    # Map each old state to its block representative.
    block_of: Dict[int, int] = {}
    for i, block in enumerate(P):
        for s in block:
            block_of[s] = i

    # Renumber blocks in BFS order starting from the block containing `start`
    # so the minimized DFA's start state is 0 and ids are stable/small.
    old_start_block = block_of[start]
    rename: Dict[int, int] = {old_start_block: 0}
    order = deque([old_start_block])
    counter = 1
    new_trans: Dict[int, Dict[str, int]] = {}
    while order:
        b = order.popleft()
        rep = next(iter(P[b]))
        new_trans[rename[b]] = {}
        for a in alphabet:
            tgt = trans.get(rep, {}).get(a)
            if tgt is None:
                continue
            tb = block_of[tgt]
            if tb not in rename:
                rename[tb] = counter
                counter += 1
                order.append(tb)
            new_trans[rename[b]][a] = rename[tb]

    # Any blocks not reached from the new start are unreachable and dropped.
    new_states = sorted(new_trans.keys())
    new_accepts = {rename[block_of[s]] for s in accepts if block_of[s] in rename}
    return new_states, new_trans, new_accepts, 0


# ------------------------------- Top-level API ------------------------------- #

def convert_nfa_to_dfa(nfa: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an NFA dict into a minimal DFA dict.

    Output schema:
        {
          "states":        [int, ...],
          "alphabet":      [str, ...],
          "transitions":   {"<state_id>": {symbol: target_id, ...}, ...},
          "start_state":   int,
          "accept_states": [int, ...]
        }
    """
    ordered_states, alpha, d_trans, accept_sets, trap_needed = _build_raw_dfa(nfa)

    # Assign integer ids to each reachable subset in discovery order.
    ids: Dict[FrozenSet[str], int] = {s: i for i, s in enumerate(ordered_states)}
    trap_id = None
    if trap_needed:
        trap_id = len(ordered_states)
        ids[frozenset()] = trap_id

    raw_states: List[int] = list(ids.values())
    raw_trans: Dict[int, Dict[str, int]] = {}
    for s, sid in ids.items():
        raw_trans[sid] = {}
        if s == frozenset():
            # Trap state loops to itself on every symbol.
            for a in alpha:
                raw_trans[sid][a] = trap_id
            continue
        for a in alpha:
            tgt = d_trans[s][a]
            raw_trans[sid][a] = ids[tgt] if tgt else trap_id  # type: ignore[arg-type]

    raw_accepts = {ids[s] for s in accept_sets}
    raw_start = ids[ordered_states[0]]

    # Hopcroft minimization on the integer-id DFA.
    states, trans, accepts, start = _hopcroft_minimize(
        raw_states, alpha, raw_trans, raw_accepts, raw_start
    )

    return {
        "states": states,
        "alphabet": alpha,
        "transitions": {str(s): trans[s] for s in states},
        "start_state": start,
        "accept_states": sorted(accepts),
    }
