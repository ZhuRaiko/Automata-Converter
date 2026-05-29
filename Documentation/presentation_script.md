# Presentation Script

These notes match the current version of the app.

## Slide 1: Title

"Good day everyone. This is the Automata Converter Program, a small web app
for demonstrating automata conversions and string acceptance animations."

## Slide 2: Motivation

"In automata theory, a lot of the learning happens through diagrams: NFAs,
DFAs, and PDAs. Static diagrams are useful, but they do not show how a
string moves through the machine. This project turns those ideas into an
interactive browser tool."

## Slide 3: What It Does

"The app has two main pages. The Regex page takes one of our preset regular
expressions, renders the matching minimized DFA, and animates strings through
it. The CFG page shows two converted CFG presets and animates a compact
PDA-style READ flow for those fixed examples."

## Slide 4: Architecture

"The backend is Flask. The algorithms are plain Python modules under the
`algorithms` folder. The frontend is plain HTML, CSS, and JavaScript, and the
diagrams are rendered with Cytoscape.js from a CDN. There is no Node or npm
build step."

## Slide 5: Regex Algorithms

"For the current regular-expression page, the two preset languages have
hardcoded minimized DFA objects in JavaScript. The frontend checks the string
locally, records the path through the DFA, and uses that path for animation.
The backend still contains Thompson construction and subset construction code,
but the current UI no longer depends on it."

## Slide 6: CFG/PDA Code

"For the CFG side, there are two things to distinguish. The backend still has
general CFG-to-PDA conversion and a BFS PDA simulator. The current browser page
is more focused: it uses two fixed converted CFG presets and renders compact
recognition flows for those languages."

## Slide 7: Regex Demo

"Now I will open the Regex page. The DFA appears automatically for the selected
preset. I can choose another preset and the visualization swaps immediately.
When I simulate a string, the active state pulses, the edge is highlighted, and
the current character is shown. If the string is accepted the diagram turns
green; otherwise it turns red."

## Slide 8: CFG Demo

"Now I will open the CFG page. I choose one converted CFG preset and the app
shows its compact PDA-style flow automatically. During simulation, the READ
states light up, the active edge is highlighted, and the current-character tape
tracks input progress."

## Slide 9: Limitations

"The regex parser is intentionally small: single-character atoms, union,
concatenation, star, grouping, and epsilon. The plus sign means union, not
Kleene-plus. The current CFG page is preset-based, so it is not an arbitrary
grammar editor in the browser, although the backend algorithm modules remain
available."

## Slide 10: Close

"The goal is to make the theory easier to see. The code is small enough to
read, the algorithms are separated into clear modules, and the UI gives an
animated view of acceptance instead of only a final answer. Thank you."
