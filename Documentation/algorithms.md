# Current Program Logic

This document describes the logic used by the current visible application.
The app is now preset-based: the automata were manually derived for the
activity, then implemented as hardcoded browser visualizations.

## Active Logic

The current app has two active JavaScript-driven flows:

- `static/js/regex.js` powers the Regex -> DFA page.
- `static/js/cfg.js` powers the CFG -> PDA-style page.

`app.py` only serves the pages. It does not run the old Python algorithm
modules during the current frontend workflow.

## Regex -> DFA

The Regex -> DFA page loads one of two prepared DFA specifications. Each
specification contains:

- states
- alphabet
- transitions
- start state
- accepting states
- fixed diagram positions

When a user types a string, the page checks the string locally against the
selected DFA. During simulation, the same path is used to highlight states,
highlight transitions, update the input tape, and display the final accepted
or rejected result.

## CFG -> PDA-Style Flow

The CFG page loads one of two converted CFG presets. The page renders a compact
PDA-style READ flow that matches the selected preset language.

The active logic handles:

- preset selection
- read-only CFG display
- string validation
- current-character tape updates
- READ-state and transition highlighting
- CFG derivation feedback
- final ACCEPT or REJECT result

The derivation checker is included to help users see how the tested string
matches the grammar structure. Nullable grammar choices are shown with epsilon
so the derivation does not appear to skip a symbol without explanation.

## Legacy Reference Files

The renamed `(IRRELEVANT)` `.py` files in `algorithms/` are kept as legacy
reference code. They document earlier implementation work and may be useful if
the project is expanded again, but they are not part of the current visible
program flow.

The current documentation should treat those files as archived references,
not as active features.
