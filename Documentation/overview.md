# Project Overview

This project is a lightweight educational web app that demonstrates two
independent pipelines used in automata theory and basic compiler design:

1. Regex → NFA → DFA → string acceptance
2. CFG → PDA → PDA simulation with stack visualization

Both pipelines are provided as separate pages and do not share diagram panels
or step viewers — they are intentionally independent for clarity and grading.

## How it works (high-level)

- The backend is a Flask app (`app.py`) that exposes JSON APIs. Each algorithm
  is implemented in `algorithms/` as pure Python modules with clear docstrings.
- The frontend uses plain HTML, CSS, and vanilla JavaScript. Diagrams are
  rendered with Cytoscape.js loaded from a CDN.
- The frontend sends POST requests to Flask endpoints carrying the user's
  input (regex or CFG text). The backend returns NFA/DFA/PDA data structures
  as JSON objects. The frontend converts those JSON objects to Cytoscape
  elements and displays them.

## File map (important files)

```
project/
├─ app.py                # Flask app + routes
├─ algorithms/           # Python algorithm implementations
├─ templates/            # HTML pages (index, regex, cfg)
├─ static/
│  ├─ css/               # style.css, regex.css, cfg.css
│  └─ js/                # regex.js, cfg.js
└─ Documentation/        # explanatory markdown files
```

## Dataflow ASCII diagram

The diagram below shows how user actions map to backend functions and
frontend updates:

```
[ Browser (regex.html) ]
      | POST /api/regex/nfa   (regex string)
      v                       (JSON: NFA dict)
[ Flask app -> thompson.compile_regex ]
      |
      | POST /api/regex/dfa   (NFA dict)
      v                       (JSON: DFA dict)
[ Flask app -> subset_construction ]
      |
      +-- frontend renders NFA and DFA (Cytoscape) --+
      |                                              |
  User clicks `Run` -> POST /api/regex/check          |
      |                        (DFA + test string)    |
      v                                              |
[ Flask app -> string_checker_dfa ]                   |
      |                                              |
      +----> returns { valid, path } ------------------+
             frontend animates DFA traversal using path


[ Browser (cfg.html) ]
      | POST /api/cfg/pda   (CFG text)
      v                     (JSON: PDA dict)
[ Flask app -> cfg_to_pda ]
      |
      +-- frontend renders PDA (Cytoscape) --+
      |                                      |
  User clicks `Run` -> POST /api/cfg/check   |
      |                  (PDA + test string) |
      v                                      |
[ Flask app -> string_checker_pda ]          |
      |                                      |
      +----> returns { valid, steps } -------+
             frontend animates PDA step-by-step
             and updates stack panel in sync
```

## Running locally

1. Install Flask: `pip install flask`
2. Run the app: `python app.py`
3. Open a browser at `http://127.0.0.1:5000/` and choose a mode.

## Final notes for graders / instructors

- The two modes are fully separated: `regex.html` and `cfg.html` each have
  their own diagrams, JS, and step viewers.
- The backend algorithms are intentionally commented and straightforward to
  follow. Each Python file contains docstrings and inline comments.
- The frontend contains comments explaining the event handlers and animation
  flow. Cytoscape is used only via CDN so no Node/npm is needed.
