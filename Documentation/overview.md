# Project Overview

This project is a lightweight educational web app for visualizing automata
conversions and string acceptance.

The current browser UI has two pages:

1. Regex -> DFA
2. Converted CFG -> compact PDA-style flow

The Python backend still contains the reusable algorithms for Thompson's
construction, subset construction, DFA checking, CFG-to-PDA conversion, and
PDA simulation. The current frontend no longer depends on those algorithms for
its visualizations: both the regex DFA page and CFG flow page use hardcoded
JavaScript specifications for the two preset languages.

## How It Works

- `app.py` is the Flask application. It serves the three pages and exposes
  JSON APIs for the algorithm modules.
- `algorithms/` contains the Python implementations:
  - `thompson.py`: regex -> NFA
  - `subset_construction.py`: NFA -> minimized DFA
  - `string_checker_dfa.py`: DFA string checker
  - `string_checker_nfa.py`: BFS single-path NFA checker
  - `cfg_to_pda.py`: general CFG -> PDA construction
  - `string_checker_pda.py`: BFS PDA path finder
- `templates/` contains the HTML pages.
- `static/js/regex.js` powers the Regex -> DFA page.
- `static/js/cfg.js` powers the converted CFG flow page.
- Cytoscape.js is loaded from a CDN for graph rendering. No Node/npm build
  step is needed.

## Current User-Facing Dataflow

```text
[ Browser: /regex ]
      |
      | user chooses one of two preset regexes
      v
[ static/js/regex.js ]
      |
      +-- loads the matching hardcoded DFA object
      +-- renders the DFA with Cytoscape
      +-- checks strings locally and returns { valid, path }
      +-- animates the DFA path


[ Browser: /cfg ]
      |
      | user chooses one of two converted CFG presets
      v
[ static/js/cfg.js ]
      |
      +-- renders a compact PDA-style flowchart for the selected language
      +-- checks strings with a matching built-in DFA specification
      +-- animates READ states and a stack panel
```

## Backend API Reference

These endpoints are available from `app.py`:

| Endpoint | Purpose |
|---|---|
| `POST /api/regex/nfa` | Compile a regex to an NFA dictionary. |
| `POST /api/regex/dfa` | Convert an NFA dictionary to a minimized DFA. |
| `POST /api/regex/check` | Check a string against a DFA and return the visited path. |
| `POST /api/regex/nfa/check` | Find one accepting NFA path, or the longest partial path on rejection. |
| `POST /api/cfg/pda` | Convert CFG text to a PDA dictionary. |
| `POST /api/cfg/check` | Run the PDA simulator and return a step trace. |

Note: the current `/cfg` browser page does not call `/api/cfg/pda` or
`/api/cfg/check`, and the current `/regex` browser page does not call the
regex API endpoints. Those general-purpose backend endpoints remain available
for testing, extension, and future UI work until they are removed.

## Running Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask
python app.py
```

Open `http://127.0.0.1:5000/`.

## File Map

```text
project/
|-- app.py
|-- algorithms/
|-- templates/
|-- static/
|   |-- css/
|   `-- js/
`-- Documentation/
```
