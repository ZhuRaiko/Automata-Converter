# Languages

This project uses Python 3 for backend algorithm implementations and plain
JavaScript for frontend interactivity and diagram animation. Below are the
reasons, tradeoffs, and practical notes.

## Python (Backend)

- Role: Implement algorithms (Thompson, Subset Construction, CFG→PDA, PDA
  simulation) and host them behind simple REST endpoints using Flask.
- Why Python:
  - Readability: Python's syntax is terse and readable for students learning
    algorithms and data structures.
  - Rich standard library: file I/O, data structures, and simple JSON handling
    are available out-of-the-box.
  - Fast prototyping: algorithms can be implemented in fewer lines than lower
    level languages, which is valuable in a course where clarity matters.
- Tradeoffs:
  - Python is slower than compiled languages (e.g., C++), but the input sizes
    and examples used in coursework are small so performance is not a concern.
  - For production-scale tooling, a faster or more strongly-typed language
    might be preferred.

## JavaScript (Frontend)

- Role: Handle DOM interactions, send/receive JSON to/from the Flask backend,
  and render / animate diagrams via Cytoscape.js.
- Why plain JavaScript (no frameworks):
  - Simplicity: Students can run the project without installing Node.js or
    learning a framework like React.
  - Direct mapping: vanilla JS shows clearly how the browser and server
    communicate using `fetch` and JSON.
  - Compatibility: works in any modern browser without a build step.
- Tradeoffs:
  - For very large applications, frameworks provide structure; however, for
    this single-page academic tool, plain JS keeps things transparent.

## Final notes

- The combination of Python for algorithms and JavaScript for UI is typical in
  education: algorithmic code remains server-side and easily testable, while
  the UI remains lightweight and framework-free.
- Students can inspect and modify both the algorithmic logic (Python files)
  and the visualization/animation (JS files) without dealing with build tools.
