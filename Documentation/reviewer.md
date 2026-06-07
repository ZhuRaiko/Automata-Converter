# Reviewer Guide: Automata Converter Program

Use this guide to review the current version of the project. The program is a
Flask-based educational visualizer for manually derived automata examples.

## Project Summary

The Automata Converter Program demonstrates how selected formal-language
patterns can be represented as interactive automata visualizations. It focuses
on two prepared classroom examples:

- Regex -> DFA: two assigned regular expressions are represented as hardcoded
  minimized DFA diagrams.
- CFG -> PDA: two converted CFG presets are represented as compact PDA-style
  READ-flow diagrams.

The project is intentionally preset-based. The regular expressions and CFG
presets were analyzed ahead of time, and the browser loads the matching
hardcoded visualization so the demonstration is stable and easy to follow.

## Strongest Features

- Automatic diagram rendering after selecting a preset.
- Interactive string testing with accepted/rejected status per row.
- Animated state traversal using Cytoscape.js.
- Input tape that tracks the current symbol during simulation.
- Pause and resume controls for slower demonstrations.
- Simulate buttons that scroll directly to the visualizer.
- CFG derivation check that shows how the input follows the grammar structure.
- Academic notebook-inspired interface with navy and teal styling.

## What To Review

### Regex -> DFA Page

The regex page should show two preset expressions. Selecting a preset should
immediately render the corresponding DFA. A reviewer should test both valid
and invalid strings, then run the animation and observe:

- active state highlighting
- active transition highlighting
- current-character tape movement
- final green accepted state or red rejected result
- reset behavior returning the diagram and tape to the initial view

### CFG -> PDA Page

The CFG page should show two read-only converted CFG presets. Selecting a
preset should immediately render the matching PDA-style flowchart. A reviewer
should test valid and invalid strings, then observe:

- READ-node movement through the flowchart
- active transition highlighting
- input tape progress
- CFG derivation steps
- epsilon display when a nullable grammar part is chosen
- final ACCEPT or REJECT result

## CV-Ready Description

Automata Converter Program: Built an educational Flask web application for
visualizing manually derived automata from assigned regular expressions and
CFG presets. Implemented hardcoded DFA and PDA-style flow visualizations with
Cytoscape.js, interactive string testing, animated state transitions,
input-tape tracking, pause/resume simulation controls, and CFG derivation
feedback for classroom demonstrations.

## Likely Questions

**Is this a general automata converter?**  
No. The current version is a preset-based visualizer. It focuses on the
specific regular expressions and CFG presets used for the activity.

**Why are the automata hardcoded?**  
The assigned expressions were manually analyzed and converted into DFA
structures first. The hardcoded browser implementation keeps the final
demonstration consistent and avoids unexpected runtime conversion errors.

**Does the CFG page use a full stack simulation?**  
The current page is a compact PDA-style recognition visualization. It focuses
on READ-flow progress, input tracking, and derivation feedback instead of
displaying a general-purpose PDA stack.

**What makes the project useful for learning?**  
It turns static automata diagrams into step-by-step animations. Students can
see which state is active, which character is being read, and exactly where a
string is accepted or rejected.

## Files To Know

| File | Purpose |
|---|---|
| `app.py` | Serves the home page, Regex -> DFA page, and CFG -> PDA page. |
| `templates/index.html` | Mode selection screen. |
| `templates/regex.html` | Regex -> DFA page structure. |
| `templates/cfg.html` | CFG -> PDA page structure. |
| `static/js/regex.js` | Hardcoded DFA data, string checking, and DFA animation. |
| `static/js/cfg.js` | CFG presets, PDA-style flow, derivation check, and animation. |
| `static/css/style.css` | Shared academic notebook theme. |
| `static/css/regex.css` | Regex page styling. |
| `static/css/cfg.css` | CFG page styling. |

## Current Scope

- Supports two Regex -> DFA presets.
- Supports two CFG -> PDA-style presets.
- Does not accept arbitrary regex or CFG input in the current UI.
- Uses Cytoscape.js from a CDN for graph rendering.
- Runs locally with Flask and no frontend build step.
