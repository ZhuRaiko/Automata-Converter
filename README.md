# Automata Converter Program

An educational web application for visualizing manually derived automata from
assigned regular expressions and converted CFG presets.

The project is built for classroom demonstrations: choose a preset, test
strings, and watch the automaton move through its states step by step.

## CV Description

Built an educational Flask web application for visualizing manually derived
automata from assigned regular expressions and CFG presets. Implemented
hardcoded DFA and PDA-style flow visualizations with Cytoscape.js, interactive
string testing, animated state transitions, input-tape tracking, pause/resume
simulation controls, and CFG derivation feedback for classroom demonstrations.

## Prominent Features

- Regex -> DFA visualization for two prepared regular-expression languages.
- CFG -> PDA-style visualization for two converted grammar presets.
- Automatic diagram rendering when a preset is selected.
- Interactive string validation with accepted/rejected results.
- Animated state and transition highlighting.
- Input tape that tracks the current character during simulation.
- Pause, resume, reset, and per-string simulate controls.
- CFG derivation checker that updates with the tested string.
- Academic notebook-inspired interface using a deep navy and teal theme.

## Tech Stack

- Python
- Flask
- HTML
- CSS
- Vanilla JavaScript
- Cytoscape.js

## Run Locally

Install Flask:

```bash
pip install flask
```

Start the app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Pages

| Page | Purpose |
|---|---|
| `/` | Home screen for choosing a mode. |
| `/regex` | Regex -> DFA visualization and simulation. |
| `/cfg` | CFG -> PDA-style flow visualization and simulation. |

## Current Scope

This version is intentionally preset-based. The automata were manually derived
for the activity and then implemented as hardcoded browser visualizations for
a stable, presentation-ready demonstration.
