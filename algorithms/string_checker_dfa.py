"""
string_checker_dfa.py

DFA string-acceptance checker.

Given a DFA dict (the shape produced by `subset_construction.convert_nfa_to_dfa`),
this module walks the DFA on an input string and reports both acceptance and
the ordered list of visited state ids — the frontend uses that path to
highlight nodes during animation.

Return shape:
    { "valid": bool, "path": [state_id, ...] }

Complexity: O(|input|) time, O(|input|) space (the path).
"""

from typing import Dict, List, Any


def check_string_dfa(dfa: Dict[str, Any], input_string: str) -> Dict[str, Any]:
    """Run `input_string` through `dfa` and return (valid, visited path).

    The DFA may be partial: if no transition exists for the current symbol,
    we stop immediately and reject (the path includes states visited so far).
    """
    start = dfa.get('start_state', 0)
    accept_states = set(dfa.get('accept_states', []))
    transitions = dfa.get('transitions', {})  # "state_id" -> {symbol: target_id}

    path: List[int] = [start]
    current = start

    for ch in input_string:
        cur_trans = transitions.get(str(current), {})
        if ch not in cur_trans:
            return {"valid": False, "path": path}
        current = cur_trans[ch]
        path.append(current)

    return {"valid": current in accept_states, "path": path}


# Name expected by app.py
run_dfa_checker = check_string_dfa
