# User Manual

**Live application:** _[Insert your deployment URL here]_

> Screenshot callout format used below:
> > 📷 **Figure N.** Page → setup → capture → suggested filename
> Save under `Documentation/images/`.

---

## 1. Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install flask
python app.py
```

Open `http://127.0.0.1:5000/`. Two cards — pick a pipeline.

> 📷 **UM-1.** `/` — Home page with the two cards. `um01_home.png`

---

## 2. Regex page (`/regex`)

Three areas: input on top, NFA/DFA tabs in the middle (with a shared
**Current char** indicator above), step viewer at the bottom.

### Notation accepted

| Meaning       | Forms                 | Example      |
|---------------|-----------------------|--------------|
| Union         | `\|`, `U`, `+`        | `a+b` ≡ `a\|b` |
| Concatenation | juxtaposition         | `abc`        |
| Kleene star   | `*`                   | `a*`         |
| Epsilon       | `ε`, `E`              | `(a+ε)b`     |
| Grouping      | `( )`                 | `(a+b)*abb`  |

`+` is algebraic union (Hopcroft-Ullman). The programming-regex
"one-or-more" Kleene-plus is **not** supported — `*` is the only Kleene
operator.

### Walkthrough — `(a+b)*abb` on `aabb`

1. Type the regex and one or more test strings.
2. Click **Convert**. Both diagrams render.
3. Switch tabs to compare. DFA should be 4 states. Each test row shows
   whether that string is accepted for the currently selected tab.
4. Click **Run** or a row's **Simulate** button on the DFA tab. The active state pulses; the traversed
   edge marches; the consumed char flashes. End: everything green.
5. Reset, change test to `abba`, Run. Ends red — regex requires the
   string to end in `abb`.

> 📷 **UM-2.** After Convert, NFA tab. `um02_regex_nfa.png`  
> 📷 **UM-3.** Same, DFA tab — 4 states. `um03_regex_dfa.png`  
> 📷 **UM-4.** Final green frame on `aabb`. `um04_regex_accept.png`  
> 📷 **UM-5.** Red rejection on `abba`. `um05_regex_reject.png`

### NFA animation

Same Run flow on the NFA tab. The simulator finds **one** accepting path
(BFS over `(state, position)` configurations) and animates it — one
active state, one edge at a time. ε-steps show `ε` in the char indicator.

> 📷 **UM-6.** NFA mid-animation. `um06_nfa_run.png`

---

## 3. CFG page (`/cfg`)

Same layout, plus a stack panel on the right of the PDA diagram.

### Notation accepted

| Meaning       | Forms                                                                |
|---------------|----------------------------------------------------------------------|
| Arrow         | `->`, `→`, `⇒`                                                       |
| Alternative   | `\|`                                                                 |
| Epsilon       | `ε`, `λ`, `Λ`, `Ε`, `^`, `epsilon`, `lambda`, `null`, `nil`, `eps`, `n`, or empty alt |

One production per line. First nonterminal seen is the start symbol.
**Conflict note:** `n` is recognized as epsilon only when it's the *entire*
alternative (`S -> n` ≡ `S -> ε`). Inside `S -> an` the `n` is still a
terminal.

### Walkthrough — `S -> aSb | ε` on `aabb`

1. Type the grammar and one or more test strings.
2. Click **Convert**. Three states (`q0`, `q1`, `q2`) appear with several
   self-loops on `q1`. Stack panel: "Empty Stack". Each test row shows
   whether that string is accepted by the PDA.
3. Click **Run** or a row's **Simulate** button. Frame 0 sits at `q0` (stack `[Z]`); frame 1 transitions
   to `q1` with the start symbol pushed. Stack top flashes **green on
   push**, **red on pop**. Around step 5 the stack looks like
   `[Z, b, b, S]` (top is `S`, at the visual top). The animation finishes
   at `q2` — all green.

> 📷 **UM-7.** After Convert. `um07_pda_built.png`  
> 📷 **UM-8.** Mid-derivation, multi-symbol stack. `um08_pda_running.png`  
> 📷 **UM-9.** Final accept frame. `um09_pda_accept.png`

### Walkthrough — `S -> aS | bS | n` on `aa`

Demonstrates the `n`-as-epsilon shortcut. Grammar generates `{a, b}*` —
every string of `a`s and `b`s. All inputs over the alphabet accept.

> 📷 **UM-10.** Accept on `aa` with `n` notation. `um10_n_accept.png`

### What the simulator can / can't handle

Handles classroom-friendly LL(1)-style grammars:

- `S -> aSb | ε`            (aⁿbⁿ)
- `S -> aA; A -> bA | ε`    (ab*)
- `S -> AB; A -> a; B -> b` (concat across nonterminals)
- `S -> (S)S | ε`           (balanced parens, LL(1) form)

Won't handle without rewriting:

- **Ambiguous**, e.g. `S -> SS | (S) | ε`.
- **Left-recursive**, e.g. `S -> Sa | a`. These hit the `max_steps`
  safety cap; the step viewer prints "Simulation exceeded N steps".
  Standard fix: left-recursion removal (`E → E+T | T` becomes
  `E → TE'; E' → +TE' | ε`).

---

## 4. Troubleshooting

| Problem | Fix |
|---------|-----|
| Diagram is missing | Open browser console. If `cytoscape is not defined`, the CDN didn't load — check network. The dagre extension falls back to `cose` automatically if it can't load. |
| `(a+b)*` rejects something you expected to accept | Verify there are no spaces inside the regex — the regex page doesn't strip them. |
| Grammar with `n` rejects | Check that `n` is the *entire* alternative; inside a longer alt it's still a terminal. |
| Step viewer shows "Simulation exceeded N steps" | The grammar is left-recursive or unbounded. Rewrite it. |
| Stack panel looks empty mid-run | Click **Reset**, then Convert, then Run in order. |

---

*See also:* [`paper.md`](./paper.md), [`presentation_guide.md`](./presentation_guide.md),
[`reviewer.md`](./reviewer.md), [`algorithms.md`](./algorithms.md).
