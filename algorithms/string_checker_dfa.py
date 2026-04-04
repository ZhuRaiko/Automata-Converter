"""
string_checker_dfa.py

DFA string acceptance checker.

Given a DFA dict (as produced by `subset_construction.nfa_to_dfa`), this
module walks the DFA on an input string and returns whether it is accepted and
the ordered list of visited states for animation.

Return format:
{
  "valid": True|False,
  "path": [0,1,2,...]
}

All functions include docstrings and inline comments for clarity.
"""

from typing import Dict, List, Any


def check_string_dfa(dfa: Dict[str, Any], input_string: str) -> Dict[str, Any]:
    """Simulate `input_string` on `dfa` and return acceptance + visited path.

    Parameters:
        dfa: DFA dict with keys 'start_state', 'accept_states', 'transitions'
        input_string: string to check (characters are alphabet symbols)

    Returns:
        dict with keys 'valid' (bool) and 'path' (list of visited state ids)
    """
    # Retrieve structure with safe fallbacks
    start = dfa.get('start_state', 0)
    accept_states = set(dfa.get('accept_states', []))
    transitions = dfa.get('transitions', {})  # mapping: "state": {symbol: target}

    path: List[int] = [start]
    current = start

    for ch in input_string:
        # Find transition from current on symbol ch
        cur_trans = transitions.get(str(current), {})
        if ch not in cur_trans:
            # No transition for this input symbol -> reject
            return {"valid": False, "path": path}

        next_state = cur_trans[ch]
        path.append(next_state)
        current = next_state

    # After consuming all input, accept if current in accept_states
    valid = current in accept_states
    return {"valid": valid, "path": path}


# Exported function name expected by app.py
run_dfa_checker = check_string_dfa
