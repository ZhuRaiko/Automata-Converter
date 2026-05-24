"""
string_checker_nfa.py

NFA path-finding simulator (JFLAP "fast run" style).

Rather than show every configuration in parallel (which is what an NFA
*really* does but is visually overwhelming), this module performs BFS over
configurations `(state, input_position)` and reconstructs ONE accepting path
through the NFA. If the string is rejected, we return the path to the
configuration that consumed the most input so the student can see where the
NFA got stuck.

Each "step" in the returned trace is a single transition fire — either an
epsilon move or a character-consuming move — so the frontend can animate the
NFA exactly like the DFA: one active state at a time, one edge at a time.

Return shape:
    {
        "valid": bool,
        "steps": [
            {
                "state":           str,    # state ID after this step
                "char":            str|None,  # consumed char or 'ε' (None on initial step)
                "remaining_input": str,
                "edge":            {"from", "to", "symbol"} | None  # transition that fired
            },
            ...
        ]
    }
"""

from collections import deque
from typing import Dict, List, Any, Tuple, Optional


def _build_adj(nfa: Dict[str, Any]) -> Dict[str, List[Tuple[Optional[str], str]]]:
    """state -> list of (symbol_or_None_for_epsilon, next_state)."""
    adj: Dict[str, List[Tuple[Optional[str], str]]] = {}
    for t in nfa['transitions']:
        sym = None if t['symbol'] == 'ε' else t['symbol']
        adj.setdefault(t['from'], []).append((sym, t['to']))
    return adj


def check_string_nfa(nfa: Dict[str, Any], input_string: str) -> Dict[str, Any]:
    """Find an accepting path for `input_string` through `nfa`.

    Algorithm: BFS over (state, input_position) configurations. BFS guarantees
    the returned accepting path is among the shortest in number of transitions.
    If no accepting configuration is reachable, fall back to the configuration
    that consumed the most input characters (so the animation at least shows
    where the run got stuck).
    """
    adj = _build_adj(nfa)
    start = nfa['start_state']
    accept = nfa['final_state']
    n = len(input_string)

    # Parent map: config -> (parent_config, transition_used).
    # `transition_used` is the {from,to,symbol} dict the frontend will animate.
    start_cfg: Tuple[str, int] = (start, 0)
    parent: Dict[Tuple[str, int], Optional[Tuple[Tuple[str, int], Dict[str, Any]]]] = {start_cfg: None}
    queue = deque([start_cfg])

    accepting_cfg: Optional[Tuple[str, int]] = None
    if start == accept and n == 0:
        accepting_cfg = start_cfg

    # Track the farthest-consumed config for the rejection fallback.
    longest_cfg = start_cfg

    while queue:
        cfg = queue.popleft()
        st, pos = cfg

        if pos > longest_cfg[1]:
            longest_cfg = cfg

        if st == accept and pos == n:
            accepting_cfg = cfg
            break

        for sym, nxt in adj.get(st, []):
            if sym is None:
                new_cfg = (nxt, pos)
                edge_sym = "ε"
            elif pos < n and sym == input_string[pos]:
                new_cfg = (nxt, pos + 1)
                edge_sym = sym
            else:
                continue
            if new_cfg in parent:
                continue
            parent[new_cfg] = (cfg, {"from": st, "to": nxt, "symbol": edge_sym})
            queue.append(new_cfg)

    target = accepting_cfg if accepting_cfg is not None else longest_cfg

    # Reconstruct path back to the start config.
    transitions_taken: List[Tuple[Tuple[str, int], Dict[str, Any]]] = []
    cur = target
    while parent.get(cur) is not None:
        prev_cfg, edge = parent[cur]  # type: ignore[misc]
        transitions_taken.append((cur, edge))
        cur = prev_cfg
    transitions_taken.reverse()

    # Build the step list. First frame is the initial configuration with no edge.
    steps: List[Dict[str, Any]] = [{
        "state": start,
        "char": None,
        "remaining_input": input_string,
        "edge": None,
    }]
    for (new_cfg, edge) in transitions_taken:
        new_st, new_pos = new_cfg
        steps.append({
            "state": new_st,
            "char": edge["symbol"],  # 'ε' for epsilon moves, the consumed char otherwise
            "remaining_input": input_string[new_pos:],
            "edge": edge,
        })

    return {"valid": accepting_cfg is not None, "steps": steps}


# Name expected by app.py
run_nfa_checker = check_string_nfa
