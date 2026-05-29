# Reviewer: Automata Converter Program

Use this as a defense-prep guide for the current codebase.

## What The Program Currently Shows

The app has two user-facing pages:

- `/regex`: select one of two regex presets, load the matching hardcoded DFA,
  render it, and animate string acceptance.
- `/cfg`: select one of two read-only converted CFG presets, render a compact
  PDA-style flowchart, and animate recognition with input-tape feedback.

Important distinction: the backend still includes general CFG-to-PDA and PDA
simulation code, but the current `/cfg` page does not call those endpoints.

## Backend Endpoints

| Endpoint | Function |
|---|---|
| `POST /api/regex/nfa` | Regex string -> NFA dict. |
| `POST /api/regex/dfa` | NFA dict -> minimized DFA dict. |
| `POST /api/regex/check` | DFA + string -> `{ valid, path }`. |
| `POST /api/regex/nfa/check` | NFA + string -> one path trace. |
| `POST /api/cfg/pda` | CFG text -> PDA dict. |
| `POST /api/cfg/check` | PDA + string -> BFS PDA trace. |

## Regex Pipeline

```text
regex
-> recursive-descent parser
-> Thompson NFA
-> subset construction DFA
-> Hopcroft minimization
-> DFA path checker
-> browser animation
```

`thompson.py` supports union as `|`, `U`, or `+`. The plus sign means union,
not programming-regex Kleene-plus.

`subset_construction.py` builds reachable DFA states from epsilon closures,
adds a trap state only when needed, and then minimizes with Hopcroft's
algorithm.

`string_checker_dfa.py` returns:

```json
{ "valid": true, "path": [0, 1, 2] }
```

The UI uses `path` to animate the DFA.

## NFA Checker

The NFA checker exists in the backend but is not shown in the current UI. It
uses BFS over `(state, input_position)` and returns one accepting path, or the
path that consumed the most input on rejection.

## CFG/PDA Backend

`cfg_to_pda.py` creates a top-down PDA with:

- `q0`: start
- `q1`: work state
- `q2`: accept state

It adds an initial transition, one transition per production, one terminal
match per terminal, and an accept transition. Its push convention is:

```text
push[0] becomes the top of the stack
```

`string_checker_pda.py` is BFS-based. It no longer uses the older
deterministic LL-style scoring heuristic. It searches configurations:

```text
(remaining_input, stack_tuple)
```

The default cap is `20000` explored configurations. If the cap is reached, the
result includes an error message warning about left recursion or unbounded
expansion.

## Current CFG Page

The current `static/js/cfg.js` implementation is preset-based:

- two converted CFG text blocks
- a matching built-in DFA specification for each selected language
- a compact flowchart with READ, ACCEPT, and REJECT nodes
- a current-character tape and step log that track the READ flow

This page is best described as a compact PDA-style recognition visualization,
not a full arbitrary CFG-to-PDA renderer.

## Likely Defense Questions

**Is the regex conversion real or hardcoded?**  
The current UI is hardcoded. It loads a fixed minimized DFA object for the
selected preset. The old backend regex conversion code still exists, but the
page no longer calls it.

**Why does the regex page only show a DFA?**  
The backend still builds an NFA first, but the current UI focuses on the
minimized DFA output and DFA path animation.

**Does the CFG page parse any grammar?**  
Not in the current UI. It uses two fixed converted CFG presets. The backend
has general CFG/PDA algorithms, but the page itself is preset-based.

**What changed in the PDA simulator?**  
The old documentation described a deterministic production-scoring heuristic.
The current `string_checker_pda.py` uses BFS over configurations, which can
find a path that requires backtracking, within a search cap.

**Why use a trap state only sometimes?**  
It keeps simple diagrams smaller. A trap state is added only if the DFA would
otherwise have an undefined transition.

## Key Limitations

- Regex atoms are single characters.
- No character classes, escapes, `?`, range counts, or programming
  Kleene-plus.
- `+` is union.
- Current regex UI has no NFA tab.
- Current CFG UI is limited to two presets.
- General PDA BFS can be expensive on difficult grammars.

## Files To Know

| File | Why it matters |
|---|---|
| `app.py` | Flask routes and API boundary. |
| `algorithms/thompson.py` | Regex parser and NFA construction. |
| `algorithms/subset_construction.py` | DFA construction and minimization. |
| `algorithms/string_checker_dfa.py` | DFA path checking. |
| `algorithms/cfg_to_pda.py` | General CFG-to-PDA construction. |
| `algorithms/string_checker_pda.py` | BFS PDA simulation. |
| `static/js/regex.js` | Current Regex -> DFA UI. |
| `static/js/cfg.js` | Current preset CFG flow UI. |
