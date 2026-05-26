# Automata Converter — User Manual

This manual walks a first-time user through both pages of the application:
**Regex → NFA / DFA** and **CFG → PDA**. Every section includes the exact
clicks to reproduce a recommended screenshot.

**Live application:** _[Insert your deployment URL here]_

> All screenshot callouts use this format:
> > 📷 **Figure N — Title.**
> > - Page: which URL to visit
> > - Steps: what to type and click
> > - What the picture should show
> > - Suggested filename: save the picture under `Documentation/images/`

---

## 1. Getting Started

### 1.1 Running locally

Prerequisites: Python 3.11 or 3.12.

```bash
# from the project root
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell / cmd
# or:  source .venv/bin/activate  on macOS / Linux
pip install flask
python app.py
```

The terminal will say `Running on http://127.0.0.1:5000/`. Open that URL.

### 1.2 The home page

The landing page has two cards — **Regex → NFA / DFA** and **CFG → PDA**.
Click whichever pipeline you want to explore.

> 📷 **Figure UM-1 — Home page.**
> - Page: `/`
> - Steps: open the URL in a fresh browser tab.
> - Capture: the full window with the two cards visible.
> - File: `um01_home.png`

---

## 2. Regex → NFA / DFA Page

URL: `/regex`. The page has four areas, top to bottom:

1. **Input panel** — the regular expression, the test string, and the
   buttons **Convert**, **Run**, **Reset**.
2. **Diagram panel** — two tabs (**NFA** and **DFA**) with the Cytoscape
   diagram in each. Above the tabs there is a **Current char** indicator
   that flashes during a Run.
3. **Step viewer** — a scrollable list of algorithm-step lines that grows
   during Convert and Run. Capped in height so it never pushes the diagram
   off-screen.

### 2.1 Notation accepted

| Meaning       | Accepted forms          | Example          |
|---------------|-------------------------|------------------|
| Union         | `\|`, `U`, `+`          | `a+b` ≡ `a\|b`   |
| Concatenation | (juxtaposition)         | `abc`            |
| Kleene star   | `*`                     | `a*`             |
| Epsilon       | `ε`, `E`                | `(a+ε)b`         |
| Grouping      | `( )`                   | `(a+b)*abb`      |

`+` is algebraic-union notation from Hopcroft-Ullman (it is **not** the
"one or more" Kleene-plus from programming regex; that operator isn't
supported).

### 2.2 Walkthrough: `(a+b)*abb` on `aabb`

This is the canonical example from any automata textbook — strings over
{a, b} ending in `abb`.

**Step 1.** Type `(a+b)*abb` into the **Regular expression** field.
**Step 2.** Type `aabb` into the **Test string** field.
**Step 3.** Click **Convert**. The step viewer fills with three lines
("Compiling regex to NFA...", "Converting NFA to DFA...", "Diagrams
rendered."). Both diagrams appear in their respective tabs.

> 📷 **Figure UM-2 — Convert finished.**
> - Page: `/regex`
> - Done with Steps 1–3 above.
> - Capture: full input panel + the active diagram (NFA tab).
> - File: `um02_regex_converted.png`

**Step 4.** Click the **DFA** tab. The diagram swaps to a 4-state DFA — the
canonical minimum equivalent to `(a+b)*abb`. The accepting state has a
double-border.

> 📷 **Figure UM-3 — Minimal DFA.**
> - Capture: just the diagram area on the DFA tab.
> - The DFA should have 4 states; one of them has a double border.
> - File: `um03_dfa.png`

**Step 5.** Click **Run** while on the DFA tab. The animation:
- The current state lights up yellow and briefly pulses larger.
- The edge being traversed turns orange and shows "marching ants" (the
  dashes flow toward the target).
- The **Current char** indicator flashes amber on each consumed symbol.
- The step viewer scrolls so the most recent line stays visible.

At the end, every element turns green — the string is accepted.

> 📷 **Figure UM-4 — Accepted run (final frame).**
> - All elements green, the active state is the accepting state.
> - File: `um04_dfa_accept.png`

**Step 6.** Click **Reset**. Highlights clear, the char indicator returns
to `-`, the step viewer says "Reset complete."

**Step 7.** Change the test string to `abba` (note the trailing `a`).
Click **Run**. The animation traces three states, then turns red — the
string is rejected because the regex requires the string to *end* in `abb`.

> 📷 **Figure UM-5 — Rejected run.**
> - Red coloring on all elements, the step viewer shows
>   "Result: INVALID".
> - File: `um05_dfa_reject.png`

### 2.3 Walkthrough: NFA tab animation

Reset, click the **NFA** tab, leave `(a+b)*abb` and test string `aabb`, and
click **Run**. The NFA has 14 states with many ε-transitions, but the
animation shows only **one** state and **one** edge active at a time — the
simulator backs out an accepting path with BFS and replays it. Each step
either consumes a real character or fires an ε-edge (the **Current char**
indicator shows `ε` for those steps).

> 📷 **Figure UM-6 — NFA mid-animation.**
> - Steps: as above; pause the animation around step 5–7.
> - Capture: one yellow active state, one marching orange edge, and the
>   char indicator showing either a consumed letter or `ε`.
> - File: `um06_nfa_run.png`

### 2.4 Tips

- **Don't see the `+` symbol render an edge label correctly?** The diagram
  uses Cytoscape, which draws to canvas — labels render with the same
  characters you typed. `+` shows as `+`, `ε` as `ε`.
- **Want to see the original (non-minimal) DFA?** Hopcroft minimization
  is enabled by default. Disabling it would require an edit to
  [`algorithms/subset_construction.py`](../algorithms/subset_construction.py)
  (call `_build_raw_dfa` directly without the `_hopcroft_minimize` step).

---

## 3. CFG → PDA Page

URL: `/cfg`. Same three-area layout: input on top, diagram + stack in the
middle, step viewer below.

### 3.1 Notation accepted

| Meaning       | Accepted forms                                                |
|---------------|---------------------------------------------------------------|
| Arrow         | `->`, `→`, `⇒`                                                |
| Alternative   | `\|`                                                          |
| Epsilon       | `ε`, `λ`, `Λ`, `Ε`, `^`, `epsilon`, `lambda`, `null`, `nil`, `eps`, `n`, or an empty alternative |
| Terminals     | any single non-whitespace character not used as a nonterminal |
| Nonterminals  | the LHS of any production (typically uppercase letters)       |

One production per line. Multiple alternatives on one line are separated by
`|`. The first nonterminal seen is the start symbol.

**Single-letter `n` as epsilon — conflict note.** Because `n` is recognized
as epsilon when it is the *entire* alternative, `S -> n` means `S -> ε`.
Inside a longer alternative like `S -> an` the `n` is still a terminal.
Avoid using `n` as a *standalone* terminal alternative if your grammar
relies on it elsewhere.

### 3.2 Walkthrough: `S -> aSb | ε` on `aabb`

The classical context-free language `aⁿbⁿ`.

**Step 1.** Type the grammar:
```
S -> aSb | ε
```
(or `S -> aSb | n`, `S -> aSb | ^`, `S -> aSb | epsilon` — all equivalent.)

**Step 2.** Type `aabb` into the test string.
**Step 3.** Click **Convert**. The step viewer says "PDA constructed."
The diagram shows three states (`q0`, `q1`, `q2`) with several self-loops
on `q1` — every production and every terminal-match becomes a self-loop.

> 📷 **Figure UM-7 — PDA after Convert.**
> - The diagram shows q0, q1, q2 laid out left-to-right (dagre layout).
> - The stack panel on the right says "Empty Stack".
> - File: `um07_pda_built.png`

**Step 4.** Click **Run**. The animation:
- **Frame 0** sits at `q0` (the bottom marker `Z` is the only thing in the
  stack panel) — this is the machine before the initial transition.
- **Frame 1** transitions to `q1`, the initial transition's edge marches,
  and the stack panel grows to show `S` on top, `Z` below.
- Every subsequent frame applies one production (`S → aSb` or `S → ε`) or
  one terminal match. The stack top flashes green on a push and red on a
  pop.
- The last frame jumps to `q2`. Everything turns green — accepted.

> 📷 **Figure UM-8 — PDA mid-derivation.**
> - Pause around step 5: the stack should look like `[Z, b, b, S]`
>   (top is at top of the stack panel, so `S` is on top, then `b`, then `b`,
>   then `Z` at the bottom).
> - Capture: full diagram + stack panel.
> - File: `um08_pda_running.png`

> 📷 **Figure UM-9 — PDA final accept frame.**
> - All elements green, active state is `q2`, stack shows only `Z`.
> - File: `um09_pda_accept.png`

### 3.3 Walkthrough: User's `S → aS | bS | n`

This grammar generates `{a, b}*` — every string over `{a, b}`.

**Step 1.** Type:
```
S -> aS | bS | n
```
**Step 2.** Test with `aa`, then `bb`, then `abab`, then `''` (empty test
string). All should be accepted.

> 📷 **Figure UM-10 — `n` notation accepted.**
> - Same setup; capture after `aa` accepts.
> - The point is to demonstrate the `n` notation. File: `um10_n_accepted.png`

### 3.4 Understanding the stack panel

The stack panel renders **top-of-stack at the visual top** of the column.
The blue-bordered box is always the top. Each push flashes the top green
for ~0.5 s; each pop flashes red.

**Why this matters.** Earlier versions of the program had a display bug
where the bottom marker `Z` appeared at the top of the panel. The current
version correctly shows the stack growing upward as you push — this matches
how you would draw it on paper.

### 3.5 Known limits (deterministic LL(1) heuristic)

The simulator chooses ONE production per step using a small lookahead
heuristic (see [`algorithms.md`](./algorithms.md) §"PDA Simulation"). It
handles:

- `S → aSb | ε`                    (a^n b^n)
- `S → aA; A → bA | ε`             (ab*)
- `S → AB; A → a; B → b`           (concat across nonterminals)
- `S → (S)S | ε`                   (balanced parens, LL(1) form)

It will **not** solve:

- **Genuinely ambiguous grammars** like `S → SS | (S) | ε` — needs full
  backtracking, which is out of scope for this educational tool.
- **Left-recursive grammars** like `S → Sa | a` (or any rule where a
  nonterminal can expand without consuming input). These trigger the
  `max_steps` safety cap; the result includes an `error` line in the step
  viewer explaining the situation.

To use a left-recursive grammar, rewrite it via standard left-recursion
removal: `E → E+T | T` becomes `E → TE'; E' → +TE' | ε`.

### 3.6 Tips

- **Long step lists scroll inside their box.** The step viewer is capped
  at ~220 px tall; the newest line is always scrolled into view. The
  diagram stays at full size regardless of how long the trace is.
- **Multiple grammars at once.** You can paste any number of lines into
  the textarea. The first nonterminal seen on the left side becomes the
  start symbol. Lines without `->` are ignored.

---

## 4. Troubleshooting

| Problem                                                          | Fix |
|------------------------------------------------------------------|-----|
| Diagram doesn't appear after Convert.                            | Make sure both CDN scripts loaded — open the browser console and look for `cytoscape is not defined`. The page uses the `cytoscape-dagre` extension; the JS falls back to the built-in `cose` layout if dagre fails to load, so worst case the layout is messier but still works. |
| `(a*b)*` works but `(a+b)*` doesn't.                             | Double-check spelling — there must be no spaces inside the parentheses on the regex page. The CFG page strips spaces; the regex page does not. |
| `S -> aSb \| null` reports the string is rejected when you expect it to accept. | Look at the step viewer: the simulator may have hit `max_steps` on a left-recursive expansion. Confirm the grammar isn't accidentally left-recursive. |
| The stack panel looks empty even though the trace has stack frames. | Reload the page. The stack panel resets on **Reset**; if you launched a Run before Convert finished, the state may be inconsistent. |
| Step viewer is full of stale lines.                              | Click **Reset**. |

---

## 5. Submitting / sharing

To share a deployment, replace _[Insert your deployment URL here]_ at the
top of this manual with your live URL (PythonAnywhere, Render, etc.). The
project is pure Flask + static assets so any WSGI host will run it.

---

*See also:
[`paper.md`](./paper.md) (full project paper),
[`presentation_guide.md`](./presentation_guide.md) (slide-by-slide outline),
[`reviewer.md`](./reviewer.md) (Q&A study guide),
[`algorithms.md`](./algorithms.md) (algorithm reference).*
