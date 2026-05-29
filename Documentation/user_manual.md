# User Manual

## Run The App

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask
python app.py
```

Open `http://127.0.0.1:5000/`.

The home page links to two tools:

- Regex -> DFA
- CFG -> PDA

## Regex -> DFA Page

Open `http://127.0.0.1:5000/regex`.

The page currently provides two preset regex choices:

1. `(aba+bab)(a+b)*(bab)(a+b)*(a+b+ab+ba)(a+b+aa)*`
2. `((101+111+101)+(1+0+11))(1+0+01)*(111+000+101)(1+0)*`

The regex text is stored in a hidden input. Choose a preset and the page will
automatically:

1. load the matching hardcoded DFA from `static/js/regex.js`
2. render the DFA
3. check all five string rows locally

### Test Strings

There are five test-string rows. Each row has:

- a text input
- an accepted/rejected status
- a **Simulate** button

Typing in a row rechecks that string after a DFA has been built. Pressing
**Simulate** copies that row into the main run input and animates the DFA
path.

### Controls

| Button | Action |
|---|---|
| Run | Animate the first test string input. |
| Reset | Clear highlights, statuses, and step log. |
| Simulate | Animate the string from that specific row. |

### Animation

During a run:

- the current DFA state highlights and pulses
- the traversed edge becomes orange and dashed
- the current character flashes in the "Current char" indicator
- accepted runs turn the diagram green
- rejected runs turn the diagram red

## Regex Notation

| Meaning | Forms | Example |
|---|---|---|
| Union | `|`, `U`, `+` | `a+b` means `a|b` |
| Concatenation | Juxtaposition | `abc` |
| Kleene star | `*` | `a*` |
| Epsilon | Greek epsilon or `E` | `(a+E)b` |
| Grouping | `( )` | `(a+b)*abb` |

`+` is union, not the programming-regex "one or more" operator.

## CFG -> PDA Page

Open `http://127.0.0.1:5000/cfg`.

The current CFG page is a preset demonstration page. It shows two converted
CFG choices matching the same language families as the regex page:

1. A language based on the `aba` or `bab` prefix, a `bab` middle segment, and
   a required ending pattern.
2. A binary language based on the provided `101/111/...` expression.

The CFG text area is read-only. Choose one of the two presets and the page
automatically renders the matching flow.

The page renders a compact PDA-style flowchart rather than the full general
PDA from the backend. It focuses on READ states, active transitions, and input
progress for the selected preset.

### CFG Test Strings

The five string rows work the same way as the regex page:

- type strings to check them after conversion
- use **Simulate** to animate a specific row
- use **Run** to animate the first row

### CFG Animation

During a run:

- READ states light up as the string is consumed
- the active transition uses the orange dashed "marching" style
- the current character tape moves forward as input symbols are verified
- on an accepting run, the flow reaches an ACCEPT node
- rejected runs turn the diagram red

## Removed / Irrelevant Backend CFG/PDA APIs

The current app no longer exposes these endpoints from `app.py`. They are
irrelevant to the visible frontend workflow:

- `(IRRELEVANT) POST /api/cfg/pda`
- `(IRRELEVANT) POST /api/cfg/check`

The current `/cfg` page uses the fixed JavaScript flow in `static/js/cfg.js`.
The current `/regex` page uses hardcoded DFA data in `static/js/regex.js`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Diagram does not appear | Check browser console and network access. Cytoscape is loaded from a CDN. |
| Regex conversion fails | Check parentheses and unsupported operators. `+` is union only. |
| String rows stay "Not Checked" | Switch presets or type in a string row to trigger checking again. |
| CFG text cannot be edited | This is expected in the current UI; the CFG page uses fixed presets. |
| CFG result differs from an arbitrary grammar you expected | The current CFG page is not an arbitrary CFG parser; use the backend endpoints or extend the UI for that. |

## Related Docs

- [`overview.md`](./overview.md)
- [`algorithms.md`](./algorithms.md)
- [`paper.md`](./paper.md)
- [`presentation_guide.md`](./presentation_guide.md)
- [`reviewer.md`](./reviewer.md)
