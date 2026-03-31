"""
string_checker_pda.py

Simulate the PDA produced by `cfg_to_pda.py` in a deterministic, step-by-step
fashion suitable for animation in the frontend. The simulator applies a simple
LL-style strategy:

- Apply the initial q0 -> q1 transition that pushes the start symbol over Z.
- Repeatedly either match and consume a terminal (if top-of-stack equals the
  next input symbol) or apply the first available production (epsilon transition
  replacing a nonterminal on the stack).
- The simulation records each configuration (state, remaining input, current
  stack) as a step for the frontend to animate.

The simulator intentionally chooses the first applicable production to remain
deterministic for classroom examples (students should keep ambiguous grammars
out of scope).
"""

from typing import Dict, List, Any


def simulate_pda(pda: Dict[str, Any], input_string: str, max_steps: int = 2000) -> Dict[str, Any]:
    """Run the PDA on `input_string` and return acceptance plus step trace.

    Parameters:
        pda: PDA dict created by `cfg_to_pda.cfg_to_pda`
        input_string: the input string to simulate
        max_steps: safety bound to avoid infinite loops

    Returns:
        { "valid": bool, "steps": [ {state, remaining_input, stack}, ... ] }
    """
    # Extract transitions and helpful info
    transitions = pda.get('transitions', [])
    start_stack_symbol = pda.get('start_stack_symbol', 'Z')

    # Find and apply the initial transition from q0 -> q1 that pushes start symbol
    initial_trans = None
    for t in transitions:
        if t['from'] == 'q0' and t['input'] == '' and t['stack_top'] == start_stack_symbol:
            initial_trans = t
            break

    # Initialize stack with bottom marker
    stack: List[str] = [start_stack_symbol]
    steps: List[Dict[str, Any]] = []
    remaining = input_string

    # Apply initial transition if present
    if initial_trans:
        # Pop the stack top (Z) then push the provided sequence
        stack.pop()
        for sym in initial_trans.get('push', []):
            stack.append(sym)
        # Move to q1
        steps.append({"state": "q1", "remaining_input": remaining, "stack": stack.copy()})
    else:
        # No initial transition: still record the starting configuration at q1
        steps.append({"state": "q1", "remaining_input": remaining, "stack": stack.copy()})

    # Helper to find transitions of a certain kind
    def find_prod_trans(stack_top: str):
        # Return list of epsilon (production) transitions whose stack_top matches
        return [t for t in transitions if t['from'] == 'q1' and t['input'] == '' and t['stack_top'] == stack_top]

    def find_match_trans(stack_top: str, next_char: str):
        # Return list of matching transitions that consume next_char
        return [t for t in transitions if t['from'] == 'q1' and t['input'] == next_char and t['stack_top'] == stack_top]

    steps_count = 0
    valid = False

    while steps_count < max_steps:
        steps_count += 1

        # If stack reduced to ['Z'] and no remaining input -> accept
        if len(stack) == 1 and stack[0] == start_stack_symbol and remaining == '':
            # Move to accept state q2 for final step
            steps.append({"state": "q2", "remaining_input": remaining, "stack": stack.copy()})
            valid = True
            break

        if not stack:
            # Nothing to do and input remains -> reject
            valid = False
            break

        top = stack[-1]

        # Attempt to match a terminal (consume input)
        if remaining:
            next_char = remaining[0]
            match_trans = find_match_trans(top, next_char)
            if match_trans:
                # deterministic: take the first matching transition
                t = match_trans[0]
                stack.pop()  # pop the matched terminal
                # push list should be empty for matching transitions, but honor if present
                for sym in t.get('push', []):
                    stack.append(sym)
                # consume input char
                remaining = remaining[1:]
                steps.append({"state": "q1", "remaining_input": remaining, "stack": stack.copy()})
                continue

        # Otherwise attempt to apply a production (epsilon transition) for the top
        prod_trans = find_prod_trans(top)
        if prod_trans:
            t = prod_trans[0]
            stack.pop()
            # push symbols in order: left-most first, so the final pushed symbol becomes top
            for sym in t.get('push', []):
                stack.append(sym)
            steps.append({"state": "q1", "remaining_input": remaining, "stack": stack.copy()})
            continue

        # No applicable transition -> reject
        valid = False
        break

    # Safety fallback if max steps reached
    if steps_count >= max_steps and not valid:
        # Treat as reject to avoid infinite loops; include a final step to show configuration
        steps.append({"state": "q1", "remaining_input": remaining, "stack": stack.copy()})
        valid = False

    return {"valid": valid, "steps": steps}


# Export default function name expected by app.py
run_pda_simulation = simulate_pda
