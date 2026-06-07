# Frameworks and Libraries

The project uses a deliberately small set of tools.

## Flask

Flask serves the HTML pages from `app.py`.

It is used because:

- `python app.py` starts the local application
- the route code is easy to read
- it is enough for a small educational web app
- it avoids heavier framework structure

The only Python dependency is Flask.

## Cytoscape.js

Cytoscape.js renders the DFA diagrams and the compact CFG flowcharts.

It is used because:

- it handles graph nodes and directed edges cleanly
- elements can be highlighted during animation
- it works from a CDN
- it supports fixed-position diagrams

The regex page uses Cytoscape for DFA diagrams. The CFG page uses it for
PDA-style READ/ACCEPT/REJECT flow diagrams.

## Vanilla HTML, CSS, And JavaScript

The UI avoids frontend build tools. This keeps setup simple:

```bash
pip install flask
python app.py
```

No Node.js, npm, webpack, or Vite step is required.

## How The Pieces Fit

- Flask serves `/`, `/regex`, and `/cfg`.
- The regex frontend loads a hardcoded DFA object and renders it directly.
- The CFG frontend renders one of two preset flows in JavaScript.
- The renamed `(IRRELEVANT)` `.py` files are kept only as legacy reference
  code and are not used by the current visible app.
