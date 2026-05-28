# Presentation Guide

Target: about 10-12 minutes of slides plus a short live demo.

## Slide Deck

### 1. Title

Project name, team members, course, date, and app link.

### 2. Motivation

- Automata conversions are hard to understand from static diagrams alone.
- This app lets students watch conversion results and acceptance paths in the
  browser.

### 3. What The App Does

| Page | Input | Output |
|---|---|---|
| Regex -> DFA | one of two regex presets | minimized DFA plus animated string acceptance |
| CFG -> PDA | one of two converted CFG presets | compact PDA-style flow plus stack animation |

### 4. Architecture

- Flask backend
- pure Python algorithm modules
- vanilla JavaScript frontend
- Cytoscape.js for graph rendering
- no Node/npm build step

### 5. Regex Visualization

- The current page uses two hardcoded minimized DFA objects.
- The frontend checks strings locally and returns `{ valid, path }`.
- The path drives the state and edge animation.
- The backend regex algorithms still exist, but are not used by the current UI.

### 6. CFG/PDA Code

Be clear about the current split:

- Backend: general CFG-to-PDA and BFS PDA simulator are available in Python.
- Frontend: current `/cfg` page uses two fixed converted CFG presets and a
  compact JavaScript flowchart for those languages.

### 7. Live Demo: Regex

1. Open `/regex`.
2. Choose a preset.
3. Enter several strings.
4. Use **Simulate** on an accepted string.
5. Use **Simulate** on a rejected string.

Point out the active state, edge highlight, current-character flash, and final
green/red result.

### 8. Live Demo: CFG

1. Open `/cfg`.
2. Choose a preset converted CFG.
3. Enter strings and simulate one.
4. Point out READ nodes, the active transition, and the stack panel.

### 9. Limitations

- Regex parser is intentionally small.
- `+` means union.
- Regex UI currently shows the DFA, not an NFA tab.
- CFG UI currently uses fixed presets rather than arbitrary editable CFGs.
- Backend PDA search can still hit large searches on difficult grammars.

### 10. Close

- Summarize the educational value.
- Mention the docs in `Documentation/`.
- Invite questions.

## Q&A Notes

**Why is there no NFA tab now?**  
The backend still builds the NFA first, but the current interface focuses on
the minimized DFA display and animation.

**Does the CFG page parse any grammar?**  
Not in the current UI. It shows two fixed converted CFG examples. The backend
still has general CFG-to-PDA and PDA simulation endpoints.

**What changed in the PDA simulator?**  
The Python simulator now uses BFS over configurations instead of the older
deterministic production-scoring heuristic.

**Why use Cytoscape.js?**  
It provides graph rendering and highlightable nodes/edges without needing a
frontend framework or build system.

## Demo Checklist

- [ ] `python app.py` starts the server.
- [ ] `/regex` converts both presets.
- [ ] Regex string rows update after conversion.
- [ ] Regex **Simulate** animates accepted and rejected strings.
- [ ] `/cfg` renders both preset flows.
- [ ] CFG **Simulate** updates the stack and final result.
