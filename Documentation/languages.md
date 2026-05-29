# Languages

This project uses Python for backend algorithms and vanilla JavaScript for the
browser interface.

## Python

Python is used for:

- Flask routing in `app.py`
- `(IRRELEVANT) thompson.py`: Thompson's regex-to-NFA construction
- `(IRRELEVANT) subset_construction.py`: subset construction and Hopcroft DFA minimization
- `(IRRELEVANT) string_checker_dfa.py` and `(IRRELEVANT) string_checker_nfa.py`: DFA and NFA string checking
- `(IRRELEVANT) cfg_to_pda.py`: general CFG-to-PDA construction
- `(IRRELEVANT) string_checker_pda.py`: BFS PDA simulation

Python fits the project because the code is readable, easy to run locally, and
well suited to classroom-size automata examples.

## JavaScript

JavaScript is used for:

- DOM interactions
- loading hardcoded DFA data for the current regex presets
- building Cytoscape graph elements
- animating DFA paths
- running the current preset CFG flow page
- updating the CFG input tape and active READ-flow visualization

The frontend is intentionally plain JavaScript, without React, Vite, or npm.
That keeps the project runnable with only Python and a browser.

## Tradeoffs

- Python is not the fastest possible implementation language, but the expected
  inputs are small.
- Vanilla JavaScript can become harder to organize in very large apps, but it
  keeps this project transparent and easy to inspect.
