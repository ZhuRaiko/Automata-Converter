# Algorithms

This document describes the algorithm code that exists in the project and
how the current UI uses it.

## Current UI Versus Backend Scope

The backend contains general algorithm modules for both regular languages and
context-free grammars.

The current frontend is more focused:

- `/regex` uses two hardcoded minimized DFA objects in `static/js/regex.js`.
  The backend regex pipeline still exists, but the current UI does not call it.
- `/cfg` shows two fixed converted CFG presets and animates a compact
  PDA-style flowchart implemented in `static/js/cfg.js`. It does not currently
  call the general CFG/PDA backend endpoints.

The backend CFG/PDA modules are still useful as reusable algorithm code and as
an extension point if the UI is expanded again.

## Regex Notation

Supported by `algorithms/thompson.py`:

| Meaning | Forms | Example |
|---|---|---|
| Union | `|`, `U`, `+` | `a+b` means `a|b` |
| Concatenation | Juxtaposition | `abc` |
| Kleene star | `*` | `a*` |
| Epsilon | `epsilon character`, `E` | `(a+E)b` |
| Grouping | `( )` | `(a+b)*abb` |

`+` is algebraic union, not programming-regex "one or more". Multi-character
symbols, character classes, escapes, `?`, and repetition ranges are out of
scope.

## Thompson's Construction: Regex -> NFA

`thompson.py` parses the regex with recursive descent:

```text
union < concatenation < star < atom
```

Then it recursively builds NFA fragments:

| AST node | Fragment |
|---|---|
| Symbol | Two states with one labeled edge. |
| Epsilon | Two states with one epsilon edge. |
| Concat | Connect left accept to right start with epsilon. |
| Union | New start branches to both fragments; both accepts join a new final. |
| Star | New start has a bypass edge and an entry edge; child accept loops back. |

Each compiled NFA has one start state and one final state. State numbering is
reset on every compile, so the same regex gives stable state names.

## Subset Construction and Hopcroft Minimization

`subset_construction.py` converts an NFA dictionary to a minimized DFA.

1. Build epsilon closures from the NFA transition list.
2. Start with `epsilon_closure({start_state})`.
3. Use BFS over reachable subsets of NFA states.
4. For each subset and input symbol, compute
   `epsilon_closure(move(subset, symbol))`.
5. Add a trap state only if at least one transition would otherwise be
   undefined.
6. Mark every subset containing the NFA final state as accepting.
7. Run Hopcroft partition refinement.
8. Renumber the minimized DFA states in BFS order from the start state.

Returned DFA shape:

```json
{
  "states": [0, 1],
  "alphabet": ["a", "b"],
  "transitions": {
    "0": { "a": 1, "b": 0 }
  },
  "start_state": 0,
  "accept_states": [1]
}
```

## DFA String Checker

`string_checker_dfa.py` walks the DFA from its start state through the input
string.

If a transition is missing, the checker rejects immediately and returns the
path visited so far.

Return shape:

```json
{
  "valid": true,
  "path": [0, 1, 2]
}
```

The current `/regex` page now performs the same check locally in JavaScript
against its hardcoded DFA objects.

## NFA String Checker

`string_checker_nfa.py` performs BFS over configurations:

```text
(state, input_position)
```

It reconstructs one accepting path if the string is accepted. If no accepting
configuration is reachable, it reconstructs a path to the configuration that
consumed the most input.

This endpoint still exists as `POST /api/regex/nfa/check`, but the current
`/regex` page does not display an NFA tab.

## CFG -> PDA Construction

`cfg_to_pda.py` parses grammar text and creates a top-down PDA.

Accepted CFG forms:

| Meaning | Forms |
|---|---|
| Arrow | `->`, Unicode right arrow, Unicode double arrow |
| Alternative | `|` |
| Epsilon | Greek epsilon/lambda variants, `^`, `epsilon`, `lambda`, `null`, `nil`, `eps`, `n`, or an empty alternative |

One production is written per line. The first nonterminal encountered is the
start symbol.

The generated PDA has:

- `q0`: start state
- `q1`: work state
- `q2`: accept state
- a bottom marker of `Z`, or `$` if `Z` is already used by the grammar

Push convention:

```text
push[0] becomes the top of the stack
push[-1] becomes deepest among the pushed symbols
```

So `S -> aSb` is stored as `push = ["a", "S", "b"]`.

## PDA Simulator

`string_checker_pda.py` is now a BFS path finder, not a deterministic
LL(1)-scoring simulator.

It searches configurations of:

```text
(remaining_input, stack_tuple)
```

For each configuration it tries:

1. terminal-matching transitions that consume the next input character
2. production transitions that expand the stack top without consuming input

It tracks parents so it can reconstruct one successful accepting path. If no
accepting path is found, it returns a path to the configuration that consumed
the most input. A `max_steps` cap, currently `20000`, prevents unbounded
searches.

Return shape:

```json
{
  "valid": false,
  "steps": [
    {
      "state": "q1",
      "remaining_input": "abb",
      "stack": ["Z", "S"],
      "applied_idx": 3
    }
  ],
  "error": "optional message if the step cap is reached"
}
```

## CFG Page Flow

The current `/cfg` page is implemented separately from the general PDA
backend. It offers two fixed converted CFGs and uses `static/js/cfg.js` to:

- render a compact READ/ACCEPT/REJECT flowchart
- check strings with a built-in DFA specification for the selected language
- animate flowchart transitions with marching edges
- update a visual stack panel as characters are read and later popped

This is why the CFG UI looks like a compact recognition flow rather than the
full textbook three-state PDA generated by `cfg_to_pda.py`.

## Practical Limits

- Regex atoms are single alphanumeric characters.
- Regex whitespace is stripped by the current frontend before selecting the
  hardcoded DFA.
- `+` means union only.
- The backend PDA search can still run into very large searches for ambiguous
  or left-recursive grammars.
- The current CFG page is limited to the two preset languages in
  `static/js/cfg.js`.
