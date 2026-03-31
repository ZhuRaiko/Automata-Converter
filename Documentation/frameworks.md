# Frameworks and Libraries

This project purposefully uses a minimal set of frameworks and libraries to
keep the code easy to understand, run, and grade. Below are the chosen
components and reasons for their selection.

## Flask (Backend)

- Role: Lightweight Python web framework used to expose simple REST endpoints
  that run the algorithms and return JSON to the frontend.
- Why Flask:
  - Very small learning curve and minimal boilerplate.
  - Ideal for single-file run: `python app.py` starts the whole application.
  - Sufficient for serving a small number of HTML pages and JSON APIs used by
    the frontend.
- Alternatives considered: Django (too heavy for a small teaching project),
  FastAPI (nice, but adds complexity and dependency for students unfamiliar
  with ASGI).

## Cytoscape.js (Frontend diagrams)

- Role: Render directed graphs (states and transitions) for NFAs, DFAs and
  PDAs in the browser, and provide an API for programmatic highlighting and
  basic animation.
- Why Cytoscape.js:
  - Designed for graph visualization with a small, easy-to-use API.
  - Loads from CDN — no Node/npm required.
  - Offers graph layout algorithms (e.g., `cose`) useful for automatic layout.
- Alternatives considered: D3.js (more general-purpose but requires much more
  work to draw nodes/edges and handle force layouts), mxGraph (heavier).

## Plain HTML + CSS + Vanilla JavaScript

- Role: Build the web UI without front-end build tools.
- Why plain JS/CSS:
  - Matches the requirement to avoid Node.js, npm, React, or Vite.
  - Keeps the project runnable with only Python installed.
  - Teaches students how frontend and backend communicate via JSON APIs.

## Notes on dependency management

- The only Python dependency is `Flask` (install with `pip install flask`).
- Cytoscape.js is loaded from a CDN URL in the HTML templates — no local
  package installation is required.

## How the pieces fit together

- Flask runs the algorithms when the frontend POSTs JSON requests.
- The frontend (vanilla JS) fetches JSON, constructs Cytoscape graph elements,
  and uses Cytoscape's API to render nodes/edges and apply highlight classes
  during animations.

This minimal-stack approach was chosen to maximize portability and clarity for
academic use.
