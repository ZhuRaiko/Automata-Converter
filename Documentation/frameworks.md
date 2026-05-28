# Frameworks and Libraries

The project uses a deliberately small stack.

## Flask

Flask serves the HTML pages and exposes JSON endpoints from `app.py`.

It is used because:

- `python app.py` starts the whole application
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
- it supports both automatic graph layouts and fixed-position flowcharts

The regex page uses Cytoscape for the minimized DFA. The CFG page uses it for
the preset READ/ACCEPT/REJECT flow diagrams.

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
- The backend CFG/PDA APIs remain available for extension and direct testing.
