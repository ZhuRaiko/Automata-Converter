# Automata Converter Program

*A web app that visualizes regular-language conversion and preset
CFG/PDA-style recognition flows.*

**Authors:** _[Your name(s)]_  
**Course / Section:** _[Code, section, semester]_  
**Date:** _[Submission date]_  
**Live application:** _[Insert your deployment URL here]_  
**Source:** <https://github.com/ZhuRaiko/Automata-Converter>

## Abstract

The project demonstrates automata-theory concepts through a Flask and
vanilla-JavaScript web application. The current Regex -> DFA page loads a
hardcoded minimized DFA for one of two preset regular languages, renders it,
and animates string acceptance. The CFG page presents two fixed converted CFG
presets and animates compact PDA-style recognition flows with a live stack
panel. General backend modules for regex conversion, CFG-to-PDA conversion,
and automata simulation are also included for extension and testing.

## 1. Background

| Representation | Machine | Language class |
|---|---|---|
| Regular expression | NFA / DFA | Regular |
| Context-free grammar | PDA | Context-free |

The regular-language backend is implemented as a complete pipeline:

```text
regex -> Thompson NFA -> subset-construction DFA -> Hopcroft minimum DFA
```

The current browser UI uses hardcoded DFA data for the regex presets rather
than calling that backend pipeline. The context-free side has two layers:

- reusable backend code for converting arbitrary CFG text to a top-down PDA
  and searching for an accepting PDA path
- the current browser page, which is a preset demonstration of two converted
  CFG languages using compact JavaScript flowcharts

## 2. Architecture

```text
Browser
|-- /regex: preset selector, DFA diagram, string rows, animation
|-- /cfg: converted CFG presets, compact flowchart, stack panel
|
Flask app.py
`-- algorithms/
    |-- thompson.py
    |-- subset_construction.py
    |-- string_checker_dfa.py
    |-- string_checker_nfa.py
    |-- cfg_to_pda.py
    `-- string_checker_pda.py
```

The frontend uses plain HTML, CSS, and JavaScript. Cytoscape.js is loaded from
a CDN, so no Node.js or npm build step is required. Flask is the only Python
dependency.

## 3. Implemented Algorithms

**Thompson's construction.** `thompson.py` parses regexes with recursive
descent and builds NFA fragments for symbols, epsilon, concatenation, union,
and Kleene star.

**Subset construction.** `subset_construction.py` turns reachable epsilon
closures of NFA states into DFA states. It adds a trap state only when needed.

**Hopcroft minimization.** The raw DFA is minimized by partition refinement,
then renumbered from the start state for stable display.

**DFA checking.** `string_checker_dfa.py` walks the DFA in linear time and
returns both acceptance and the visited state path.

**NFA checking.** `string_checker_nfa.py` uses BFS over `(state, input_index)`
configurations to reconstruct one accepting path. This backend endpoint is
available, although the current UI no longer has an NFA tab.

**CFG-to-PDA construction.** `cfg_to_pda.py` builds a three-state top-down PDA
from grammar text, with one transition per production and one matching
transition per terminal.

**PDA checking.** `string_checker_pda.py` uses BFS over
`(remaining_input, stack)` configurations. This replaced the older
deterministic LL-style heuristic and can find accepting paths that require
backtracking, subject to a search cap.

## 4. Current User Interface

The `/regex` page offers two preset regexes. The selected preset's DFA is
displayed automatically, and switching presets immediately replaces the
visualization. Five string rows can be checked and simulated. The animation
highlights the current state, the traversed edge, and the currently consumed
character.

The `/cfg` page offers two read-only converted CFG presets. The app renders a
compact flowchart automatically for the selected language. String checks and
animations are handled in `static/js/cfg.js` with a built-in DFA specification
and a visual stack.

## 5. Limitations

- Regex atoms are single alphanumeric characters.
- `+` means union, not "one or more".
- The current regex UI renders only the minimized DFA.
- The current CFG UI is limited to the two preset languages.
- The general backend PDA search can become expensive for ambiguous or
  left-recursive grammars.

## 6. Running Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask
python app.py
```

Open `http://127.0.0.1:5000/`.

## References

1. Sipser, M. *Introduction to the Theory of Computation*, 3rd ed.
2. Hopcroft, Motwani, Ullman. *Introduction to Automata Theory, Languages,
   and Computation*, 3rd ed.
3. Thompson, K. "Regular expression search algorithm." *CACM* 11.6 (1968).
4. Hopcroft, J. E. "An n log n algorithm for minimizing states in a finite
   automaton." Stanford TR STAN-CS-71-190, 1971.
5. Cytoscape.js documentation: <https://js.cytoscape.org/>

## Companion Docs

- [`overview.md`](./overview.md)
- [`algorithms.md`](./algorithms.md)
- [`user_manual.md`](./user_manual.md)
- [`presentation_guide.md`](./presentation_guide.md)
- [`reviewer.md`](./reviewer.md)
