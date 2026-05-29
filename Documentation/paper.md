# Automata Converter Program

*Regex -> DFA and CFG -> PDA-style visual simulation*

**Authors:** _[Member 1], [Member 2], [Member 3], [Member 4]_  
**Course / Section:** _[Course, section, semester]_  
**Date:** _[Submission date]_  
**Application Link:** _[Insert local, hosted, or repository link here]_  
**Source:** <https://github.com/ZhuRaiko/Automata-Converter>

## Introduction

The Automata Converter Program is an educational web application based on the
regular expressions assigned in the first part of our automata activity. Those
expressions were manually analyzed and converted into DFA structures, then
used as the basis for the hardcoded visualizations in the program. It focuses
on two classroom demonstrations:

1. converting the idea of a regular expression into a deterministic finite
   automaton (DFA) visualization
2. presenting converted context-free grammar (CFG) presets as compact
   PDA-style recognition flows

The current interface is intentionally preset-based because the program is
centered on the specific regex-to-DFA work completed for the activity. Instead
of asking the user to build an automaton step by step, the program immediately
renders the selected manually derived visualization and lets the user test
strings against it. 

The web app is built with Flask, HTML, CSS, vanilla JavaScript, and
Cytoscape.js. The frontend currently uses hardcoded automata data for the
two selected language families.

## Regular Expressions

Regular expressions are formal descriptions of regular languages. In this
program, the regular expressions define patterns over either `Σ = {a, b}`
or `Σ = {0, 1}`. The symbol `+` is used as union, not as the
programming-regex "one or more" operator.

### Regular Expression 1 -- `Σ = {a, b}`

(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*

This matches any string that opens with either `aba` or `bab`, has `bab`
somewhere in the middle, and wraps up with one of `a`, `b`, `ab`, or `ba`
followed by any trailing characters.

Think of it as:

specific start -> anything -> bab -> anything -> specific end

### Regular Expression 2 -- `Σ = {0, 1}`

((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*

This matches any binary string that starts with one of a handful of short
patterns (`101`, `111`, `1`, `0`, or `11`), then has a required block of either
`111`, `000`, or `101` somewhere in it, then ends however it wants.

Think of it as:

specific start -> anything -> required middle block -> anything

### Structural Parallel Between The Two Regexes

Both regular expressions follow the same general structure:

(fixed prefix choices) . Sigma* . (fixed middle block) . Sigma* . (constrained tail) . Sigma*

The shape is identical; only the alphabet and the specific anchor strings
differ.

## Deterministic Finite Automaton (DFA)

A deterministic finite automaton is a machine that reads one input symbol at a
time and always has exactly one next state for each valid transition. The DFA
does not use memory beyond its current state. Because the two regular
expressions define regular languages, they can be recognized by DFAs.

In the current program, the Regex -> DFA page uses hardcoded DFA
objects in `static/js/regex.js`. When the user selects a preset, the matching
DFA is rendered automatically in the browser.

### DFA for Regular Expression 1

The first DFA processes `Σ = {a, b}`. Its start state branches
depending on whether the input begins with `a` or `b`. Some paths move toward
the accepting route, while invalid paths enter a trapstate. This matches
the strict structure of the first regular expression, where the string must
begin with `aba` or `bab`, later include the required `bab` segment, and then
complete the required ending pattern.

The accepting state represents a completed match of the required structure.
Once the machine reaches acceptance, remaining suffix behavior follows the
allowed ending portion of the expression.

### DFA for Regular Expression 2

The second DFA processes `Σ = {0, 1}`. Its states track the
progress of a binary string through the required pattern groups. The automaton
uses transitions for `0` and `1` to determine whether the string has reached
the required checkpoint from `{111, 000, 101}` and can proceed to acceptance.

This DFA is useful for showing that even when an expression contains several
alternatives and repeated binary sections, the final machine still processes
the string one symbol at a time.

### Program-Specific DFA Features

The DFA page includes several features that make the simulation easier to
follow:

- the DFA appears immediately after selecting a preset
- five string rows can be tested without rebuilding the graph
- each row has its own `Simulate` button
- pressing `Simulate` automatically scrolls to the visualizer
- the current state pulses during animation
- the active transition is highlighted
- the input tape shows the current and verified characters
- accepted strings turn the diagram green
- rejected strings turn the diagram red
- `Pause` and `Resume` let the user slow down the runtime visualization
- `Reset` clears the path, tape, statuses, and step log

These details are not part of DFA theory itself, but they are important to the
program because they make the automaton easier to demonstrate in real time.

## Context-Free Grammar (CFG)

A context-free grammar describes how strings can be generated from production
rules. In this program, the CFG page uses two converted CFG presets that
correspond to the same language families as the regular-expression presets.
The CFG text area is read-only because the current browser page is designed
for fixed demonstrations rather than arbitrary grammar entry.

### CFG for Preset 1

S -> P A bab A Q R
P -> aba | bab
A -> aA | bA | epsilon
Q -> a | b | ab | ba
R -> aR | bR | aaR | epsilon

This grammar mirrors the structure of the first regular expression. `P`
handles the required initial choice between `aba` and `bab`. `A` represents a
free sequence over `Σ = {a, b}`. The fixed `bab` in the start production preserves
the required middle segment. `Q` handles the required final choice, and `R`
handles the final repeated suffix.

### CFG for Preset 2

S -> X Y Z W
X -> 101 | 111 | 1 | 0 | 11
Y -> 1Y | 0Y | 01Y | epsilon
Z -> 111 | 000 | 101
W -> 1W | 0W | epsilon

This grammar mirrors the structure of the second regular expression. `X`
handles the opening alternatives, `Y` handles the repeated middle pieces,
`Z` represents the required binary checkpoint, and `W` allows the remaining
binary suffix.

The current CFG page does not accept new grammar text from the user. Instead,
the user chooses between these two presets and observes the corresponding
PDA-style flow.

## Pushdown Automaton (PDA)

A pushdown automaton is a finite-state machine with a stack. In formal theory,
the stack allows a PDA to recognize context-free languages that cannot be
recognized by a DFA alone.

The current frontend uses a compact PDA-style flowchart for demonstration.
The UI focuses on READ states, active transitions, the current-character tape,
and the final ACCEPT or REJECT result.

This is an important accuracy point: the browser PDA page is best described as
a fixed PDA-style recognition visualization for the selected presets.

### PDA-Style Flow for Preset 1

For the first preset, the PDA-style flow reads symbols from `Σ = {a, b}`
and moves through READ nodes that correspond to the same recognition
structure used by the DFA. Invalid paths reach a reject state, while a valid
path reaches an ACCEPT state after the required expression structure is
completed.

### PDA-Style Flow for Preset 2

For the second preset, the PDA-style flow reads symbols from `Σ = {0, 1}` and
tracks the binary pattern through its READ nodes. The flow highlights the
current state and active transition so the user can see how the input is being
verified.

The transition into ACCEPT is labeled with the delta symbol `Δ`, marking the
final move from the READ flow into the accepting state.

## User Manual

### Running the Program

Install Flask, start the application, and open the local server:

pip install flask
python app.py

Then open:

http://127.0.0.1:5000/

The home page provides two modes:

- Regex -> DFA
- CFG -> PDA

### Regex -> DFA Page

1. Open `/regex`.
2. Select one of the two regex presets.
3. Enter test strings into the five input rows.
4. Use `Simulate` on a row to animate that specific string.
5. Use `Run` to animate the first string row.
6. Use `Pause` and `Resume` to control animation speed.
7. Use `Reset` to clear the visualization state.

During simulation, the DFA state lights up, the active edge is shown, and the
input tape tracks the current symbol.

### CFG -> PDA Page

1. Open `/cfg`.
2. Select one of the converted CFG presets.
3. Review the read-only CFG text.
4. Enter test strings into the input rows.
5. Use `Simulate` to scroll to the flowchart and animate the selected string.
6. Use `Pause`, `Resume`, and `Reset` as needed.

During simulation, the READ nodes and transitions show how the input is being
processed. The current-character tape shows which symbol is being verified.

## Sample Outputs

The following examples are intended for demonstration. The interface remains
the final authority because it uses the actual hardcoded transition tables.

### Sample Outputs for Preset 1

Sample accepted string: abababababa
Expected result: Accepted

This string follows the required structure of the first expression and reaches
the accepting state.

Sample rejected string: aaa
Expected result: Rejected

This string fails the required expression structure and enters a rejecting
path.

### Sample Outputs for Preset 2

Sample accepted string: 101111101
Expected result: Accepted

This binary string satisfies the required checkpoint behavior of the second
expression and reaches the accepting state.

Sample rejected string: 0011
Expected result: Rejected

This string does not complete the required binary recognition path and is
rejected by the current hardcoded automaton.

## Program Architecture

The application is organized as a Flask-served browser application.

Browser
|-- /regex: preset selector, DFA diagram, string rows, input tape
|-- /cfg: converted CFG presets, PDA-style READ flow, input tape
|
Flask app.py
`-- serves the pages and static frontend files

The current UI uses fixed JavaScript specifications for stable demonstrations.
The graph rendering and runtime animation are handled in the browser.

## Unique Features of the Current Program

- The DFA and PDA-style diagrams render automatically.
- Both pages use input tapes to make the current character easier to follow.
- The `Simulate` button scrolls directly to the visualization.
- `Pause` and `Resume` help users keep up with the animation.
- The PDA page keeps the flowchart design focused on READ-state progress.
- The visual design follows an academic notebook style with navy and teal
  accents.
- Cytoscape.js provides graph rendering without requiring a frontend build
  system.

## Troubleshooting

| Problem | Suggested Fix |
|---|---|
| Diagram does not appear | Check internet access because Cytoscape.js is loaded from a CDN. |
| String is rejected unexpectedly | Make sure the string uses the correct alphabet for the selected preset. |
| Animation is too fast | Use `Pause` and `Resume` during runtime. |
| CFG text cannot be edited | This is expected; the CFG page currently uses fixed presets. |
| App does not start | Install Flask and run `python app.py` from the project folder. |

## Limitations

- The frontend currently supports two fixed regex presets and two fixed CFG
  presets.
- The regex UI renders the minimized DFA only.
- The CFG UI is not an arbitrary grammar editor.
- The browser interface is hardcoded for stable demonstrations.

## References

1. Automata References: <https://www.tutorialspoint.com/automata_theory/automata_theory_applications.htm>
2. Cytoscape.js documentation: <https://js.cytoscape.org/>

