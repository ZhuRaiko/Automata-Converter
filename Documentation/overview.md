# Project Overview

This project is a lightweight educational web app for visualizing automata
recognition through prepared examples.

The current browser UI has two pages:

1. Regex -> DFA
2. CFG -> PDA-style flow

Both pages are intentionally preset-based. The automata were manually derived
for the activity and then implemented as hardcoded JavaScript visualizations
so the demonstration remains stable and easy to follow.

## How It Works

- `app.py` is the Flask application. It serves the home page, Regex -> DFA
  page, and CFG -> PDA-style page.
- `templates/` contains the HTML page structure.
- `static/css/` contains the shared academic notebook theme and page-specific
  styling.
- `static/js/regex.js` powers the hardcoded DFA visualization and simulation.
- `static/js/cfg.js` powers the converted CFG presets, PDA-style flow, input
  tape, and derivation checker.
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
      +-- checks strings locally
      +-- animates the DFA path


[ Browser: /cfg ]
      |
      | user chooses one of two converted CFG presets
      v
[ static/js/cfg.js ]
      |
      +-- renders a compact PDA-style flowchart
      +-- checks strings locally
      +-- updates the CFG derivation checker
      +-- animates READ states, transitions, and input progress
```

## Legacy Reference Code

The `algorithms/` folder contains renamed `(IRRELEVANT)` `.py` files from
earlier versions of the project. They are kept as legacy reference code because
they document previous implementation work and could help if the project is
expanded later.

They are not used by the current visible app.

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
|-- requirements.txt
|-- vercel.json
|-- algorithms/
|-- templates/
|-- static/
|   |-- css/
|   `-- js/
`-- Documentation/
```
