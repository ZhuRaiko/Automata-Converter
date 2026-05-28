"""
string_checker_pda.py

Path-finding simulator for the PDA produced by `cfg_to_pda.py`.
Used by the frontend to animate the stack and the current configuration.

Push convention (must match cfg_to_pda.py):
    `push[0]` ends up on TOP of the stack after the push, `push[-1]` ends up
    deepest. The simulator implements this by iterating `reversed(push)` and
    appending each symbol, so the last append (= push[0]) becomes stack[-1].

The simulator searches configurations instead of committing to the first
matching production. This lets it handle regular grammars with shared prefixes
or nullable loops, while still returning one concrete path for animation.

Return shape:
    {
        "valid":  True | False,
        "steps":  [ {state, remaining_input, stack, applied_idx}, ... ],
        "error":  "<optional message when max_steps is hit>"
    }
"""

from collections import deque
from typing import Any, Dict, List, Optional, Tuple


Configuration = Tuple[str, Tuple[str, ...]]


def _apply_push(stack: List[str], push_list: List[str]) -> None:
    """Push so `push_list[0]` ends up on top. Mutates `stack` in place."""
    for sym in reversed(push_list):
        stack.append(sym)


def _pushed_stack(stack: Tuple[str, ...], push_list: List[str]) -> Tuple[str, ...]:
    next_stack = list(stack[:-1])
    _apply_push(next_stack, push_list)
    return tuple(next_stack)


def simulate_pda(
    pda: Dict[str, Any], input_string: str, max_steps: int = 20000
) -> Dict[str, Any]:
    """Find one accepting PDA path for `input_string`, if one exists."""
    transitions = pda.get("transitions", [])
    bottom = pda.get("start_stack_symbol", "Z")

    initial_idx: Optional[int] = None
    accept_idx: Optional[int] = None
    prods_by_top: Dict[str, List[int]] = {}
    matches_by_top: Dict[str, List[int]] = {}

    for i, t in enumerate(transitions):
        if t["from"] == "q0" and t["input"] == "" and t["stack_top"] == bottom:
            initial_idx = i
        elif (
            t["from"] == "q1"
            and t["to"] == "q2"
            and t["input"] == ""
            and t["stack_top"] == bottom
        ):
            accept_idx = i
        elif t["from"] == "q1" and t["to"] == "q1":
            if t["input"] == "" and t["stack_top"] != bottom:
                prods_by_top.setdefault(t["stack_top"], []).append(i)
            elif t["input"]:
                matches_by_top.setdefault(t["stack_top"], []).append(i)

    initial_stack: List[str] = [bottom]
    prefix_steps: List[Dict[str, Any]] = [
        {
            "state": "q0",
            "remaining_input": input_string,
            "stack": initial_stack.copy(),
            "applied_idx": None,
        }
    ]

    if initial_idx is not None:
        initial_stack.pop()
        _apply_push(initial_stack, transitions[initial_idx].get("push", []))
        prefix_steps.append(
            {
                "state": "q1",
                "remaining_input": input_string,
                "stack": initial_stack.copy(),
                "applied_idx": initial_idx,
            }
        )

    start: Configuration = (input_string, tuple(initial_stack))
    queue = deque([start])
    seen = {start}
    parent: Dict[Configuration, Tuple[Configuration, int]] = {}
    best = start
    explored = 0

    while queue and explored < max_steps:
        remaining, stack = queue.popleft()
        explored += 1

        if len(remaining) < len(best[0]):
            best = (remaining, stack)

        if len(stack) == 1 and stack[0] == bottom and remaining == "":
            return {
                "valid": True,
                "steps": _reconstruct_steps(
                    start, (remaining, stack), parent, prefix_steps, accept_idx
                ),
            }

        if not stack:
            continue

        top = stack[-1]
        candidates: List[Tuple[Configuration, int]] = []
        
        if remaining:
            next_char = remaining[0]
            for idx in matches_by_top.get(top, ()):
                t = transitions[idx]
                if t["input"] == next_char:
                    candidates.append(
                        ((remaining[1:], _pushed_stack(stack, t.get("push", []))), idx)
                    )

        for idx in prods_by_top.get(top, ()):
            t = transitions[idx]
            candidates.append(((remaining, _pushed_stack(stack, t.get("push", []))), idx))

        for nxt, idx in candidates:
            if nxt in seen:
                continue
            seen.add(nxt)
            parent[nxt] = ((remaining, stack), idx)
            queue.append(nxt)

    error = None
    if explored >= max_steps:
        error = (
            f"Simulation exceeded {max_steps} configurations. "
            "The grammar may contain left recursion or unbounded expansion."
        )

    return {
        "valid": False,
        "steps": _reconstruct_steps(start, best, parent, prefix_steps, None),
        **({"error": error} if error else {}),
    }


def _reconstruct_steps(
    start: Configuration,
    goal: Configuration,
    parent: Dict[Configuration, Tuple[Configuration, int]],
    prefix_steps: List[Dict[str, Any]],
    accept_idx: Optional[int],
) -> List[Dict[str, Any]]:
    chain: List[Tuple[Configuration, int]] = []
    cur = goal

    while cur != start and cur in parent:
        prev, idx = parent[cur]
        chain.append((cur, idx))
        cur = prev

    chain.reverse()
    steps = [dict(step) for step in prefix_steps]

    for (remaining, stack), idx in chain:
        steps.append(
            {
                "state": "q1",
                "remaining_input": remaining,
                "stack": list(stack),
                "applied_idx": idx,
            }
        )

    if accept_idx is not None:
        remaining, stack = goal
        steps.append(
            {
                "state": "q2",
                "remaining_input": remaining,
                "stack": list(stack),
                "applied_idx": accept_idx,
            }
        )

    return steps


# Name expected by app.py
run_pda_simulation = simulate_pda
