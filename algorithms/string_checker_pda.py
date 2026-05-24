"""
string_checker_pda.py

Deterministic step-by-step simulator for the PDA produced by `cfg_to_pda.py`.
Used by the frontend to animate the stack and the current configuration.

Push convention (must match cfg_to_pda.py):
    `push[0]` ends up on TOP of the stack after the push, `push[-1]` ends up
    deepest. The simulator implements this by iterating `reversed(push)` and
    appending each symbol, so the last append (= push[0]) becomes stack[-1].

LL(1)-style production choice:
    When the top of the stack is a nonterminal with multiple productions, the
    simulator picks the production using a small lookahead heuristic:
        score 4:  the production starts with a terminal matching the next
                  input character (definite win for this step)
        score 3:  the production is an epsilon-production and input is empty
        score 2:  the production starts with a nonterminal (defer judgment)
        score 1:  the production is an epsilon-production but input remains
        score 0:  the production starts with a terminal that doesn't match
                  the next input character (will fail on the next step)
    The first production with the highest score wins.

Return shape:
    {
        "valid":  True | False,
        "steps":  [ {state, remaining_input, stack, applied_idx}, ... ],
        "error":  "<optional message when max_steps is hit>"
    }

`applied_idx` is the index of the transition in `pda["transitions"]` that
fired to produce this step (None for the very first frame at q0). The
frontend uses this to highlight the exact edge that was traversed — no more
guessing among the many self-loops on q1.
"""

from typing import Dict, List, Any, Optional


def _classify_nonterminals(transitions: List[Dict[str, Any]]) -> set:
    """Symbols that appear as `stack_top` on an epsilon q1->q1 transition are
    nonterminals (productions). `Z` is excluded — it is the bottom marker."""
    return {
        t['stack_top']
        for t in transitions
        if t['from'] == 'q1' and t['to'] == 'q1'
        and t['input'] == '' and t['stack_top'] != 'Z'
    }


def _score_production(t: Dict[str, Any], next_char: Optional[str], nt_set: set) -> int:
    """Heuristic LL(1)-style score (see module docstring)."""
    push = t.get('push', [])
    if not push:
        return 3 if next_char is None else 1
    first = push[0]
    if next_char is not None and first == next_char:
        return 4
    if first in nt_set:
        return 2
    return 0


def _apply_push(stack: List[str], push_list: List[str]) -> None:
    """Push so `push_list[0]` ends up on top. Mutates `stack` in place."""
    for sym in reversed(push_list):
        stack.append(sym)


def simulate_pda(pda: Dict[str, Any], input_string: str,
                 max_steps: int = 2000) -> Dict[str, Any]:
    """Simulate `pda` on `input_string` and return acceptance + step trace."""
    transitions = pda.get('transitions', [])
    bottom = pda.get('start_stack_symbol', 'Z')
    nt_set = _classify_nonterminals(transitions)

    # Index each transition by lookup key so we can recover its `applied_idx`
    # when we pick it. Cached lookups make the main loop cheap.
    initial_idx: Optional[int] = None
    accept_idx: Optional[int] = None
    prods_by_top: Dict[str, List[int]] = {}        # nonterminal -> [transition idx, ...]
    matches_by_top: Dict[str, List[int]] = {}      # terminal    -> [transition idx, ...]
    for i, t in enumerate(transitions):
        if t['from'] == 'q0' and t['input'] == '' and t['stack_top'] == bottom:
            initial_idx = i
        elif t['from'] == 'q1' and t['to'] == 'q2' and t['input'] == '' and t['stack_top'] == bottom:
            accept_idx = i
        elif t['from'] == 'q1' and t['to'] == 'q1':
            if t['input'] == '' and t['stack_top'] != bottom:
                prods_by_top.setdefault(t['stack_top'], []).append(i)
            elif t['input']:
                matches_by_top.setdefault(t['stack_top'], []).append(i)

    stack: List[str] = [bottom]
    remaining = input_string
    steps: List[Dict[str, Any]] = [
        # Frame 0: the machine sits at q0 with just Z on the stack — before any
        # transition has fired. Without this frame the animation starts with
        # the start symbol already pushed, which hides the initial move.
        {"state": "q0", "remaining_input": remaining,
         "stack": stack.copy(), "applied_idx": None},
    ]

    # Apply the initial transition (q0 -> q1, pushing the start symbol over Z).
    if initial_idx is not None:
        stack.pop()
        _apply_push(stack, transitions[initial_idx].get('push', []))
        steps.append({
            "state": "q1", "remaining_input": remaining,
            "stack": stack.copy(), "applied_idx": initial_idx,
        })

    valid = False
    error: Optional[str] = None

    for _ in range(max_steps):
        # Acceptance: only Z left and the input is consumed.
        if len(stack) == 1 and stack[0] == bottom and remaining == '':
            steps.append({
                "state": "q2", "remaining_input": remaining,
                "stack": stack.copy(), "applied_idx": accept_idx,
            })
            valid = True
            break

        if not stack:
            break  # ran out of stack with input remaining -> reject

        top = stack[-1]

        # (a) Consume a terminal on top of the stack.
        applied = False
        if remaining:
            next_char = remaining[0]
            for idx in matches_by_top.get(top, ()):
                t = transitions[idx]
                if t['input'] == next_char:
                    stack.pop()
                    _apply_push(stack, t.get('push', []))
                    remaining = remaining[1:]
                    steps.append({
                        "state": "q1", "remaining_input": remaining,
                        "stack": stack.copy(), "applied_idx": idx,
                    })
                    applied = True
                    break
            if applied:
                continue

        # (b) Apply a production expansion (epsilon transition).
        if not _try_production(top, remaining, stack, steps,
                               prods_by_top, transitions, nt_set):
            break
    else:
        error = (f"Simulation exceeded {max_steps} steps. "
                 "The grammar may contain left recursion or unbounded expansion.")

    return {"valid": valid, "steps": steps,
            **({"error": error} if error else {})}


def _try_production(top: str, remaining: str, stack: List[str],
                    steps: List[Dict[str, Any]],
                    prods_by_top: Dict[str, List[int]],
                    transitions: List[Dict[str, Any]],
                    nt_set: set) -> bool:
    """Pick the best production for `top`, apply it, and append a step.
    Returns False if no production applies (caller treats that as rejection)."""
    indices = prods_by_top.get(top)
    if not indices:
        return False
    next_char = remaining[0] if remaining else None
    chosen_idx = max(indices,
                     key=lambda i: _score_production(transitions[i], next_char, nt_set))
    t = transitions[chosen_idx]
    stack.pop()
    _apply_push(stack, t.get('push', []))
    steps.append({
        "state": "q1", "remaining_input": remaining,
        "stack": stack.copy(), "applied_idx": chosen_idx,
    })
    return True


# Name expected by app.py
run_pda_simulation = simulate_pda
