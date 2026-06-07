# Languages

This project uses Python to serve the app and vanilla JavaScript to run the
interactive automata visualizations in the browser.

## Python

Python is used for Flask routing in `app.py`.

The current app uses Python only to serve:

- `/`
- `/regex`
- `/cfg`

The renamed `(IRRELEVANT)` `.py` files in `algorithms/` are kept as legacy
reference code. They are not used by the current visible frontend workflow.

## JavaScript

JavaScript is used for:

- DOM interactions
- loading hardcoded DFA data for the regex presets
- building Cytoscape graph elements
- animating DFA paths
- rendering the current preset CFG flow page
- updating the CFG input tape
- updating the CFG derivation checker
- highlighting active READ-flow transitions

The frontend is intentionally plain JavaScript, without React, Vite, or npm.
That keeps the project runnable with only Python and a browser.

## Tradeoffs

- Python keeps the local server simple and readable.
- Vanilla JavaScript keeps the frontend transparent, but larger future
  features may benefit from stronger organization.
