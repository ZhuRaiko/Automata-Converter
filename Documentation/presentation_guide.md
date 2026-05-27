# Presentation Guide

Target: **~12 min slides + ~5 min live demo + Q&A.** Tight version — only
the points that have to make it on the slide.

Cross-refs: [`paper.md`](./paper.md), [`user_manual.md`](./user_manual.md),
[`reviewer.md`](./reviewer.md), [`presentation_script.md`](./presentation_script.md).

> Screenshot callouts use the same format as the user manual:
> > 📷 **Slide N.** Page → setup → capture → filename.

---

## Slide deck (10 slides)

### 1 — Title
Project name, your name(s), course, date. Footer: live app URL.

### 2 — Why
Two lines:
- Automata theory lives on chalkboards. Hard to *see* the algorithm.
- This tool runs it in the browser, step by step.

### 3 — What it does
| Pipeline | Input | Output |
|----------|-------|--------|
| Regex pipeline | regular expression | NFA → minimal DFA, animated string acceptance |
| CFG pipeline | context-free grammar | top-down PDA, animated derivation with live stack |

> 📷 **Slide 3.** Home page `/`. `slide03_home.png`

### 4 — Theory (one slide)
| Layer | Machine | Language class |
|-------|---------|----------------|
| Regex | NFA / DFA | Regular |
| CFG | PDA | Context-free |

### 5 — Algorithms used
- **Thompson** — regex → NFA.
- **Subset construction + Hopcroft** — NFA → minimal DFA.
- **JFLAP "fast run"** — single-path NFA animation (BFS over configurations).
- **3-state CFG → PDA** — top-down.
- **LL(1) heuristic PDA simulator** — picks the production whose first
  symbol matches the next input. Step cap catches left recursion.

### 6 — Live demo: regex
Setup line on the slide: `(a+b)*abb` on `aabb` then `abba`. Then **switch
to the browser** (script below).

> 📷 **Slide 6.** DFA tab green after Run. `slide06_dfa_accept.png`

### 7 — Live demo: CFG
Setup line: `S -> aSb | ε` on `aabb`. Then **switch to the browser**.

> 📷 **Slide 7.** PDA mid-run with multi-symbol stack. `slide07_pda_running.png`

### 8 — Animation details (one slide)
- Marching ants on the active edge = direction of travel.
- Char flash = which symbol was just consumed.
- `applied_idx` tagging = exact edge highlight, no guessing among self-loops on `q1`.
- Single-path NFA animation instead of parallel state set — JFLAP convention.

### 9 — Limitations (be honest)
- Single-character regex atoms only (no `[a-z]`, no `?`, no `{n,m}`).
- `+` is union, not Kleene-plus.
- PDA simulator is deterministic LL(1)-style — ambiguous and left-recursive
  grammars are detected (step cap) but not parsed.

### 10 — Close
- Live: `[Insert your deployment URL here]`
- Source: <https://github.com/ZhuRaiko/Automata-Converter>
- Questions?

---

## Live demo script (~5 min)

### Regex (≈2 min)
1. Open `/regex`.
2. Type `(a+b)*abb`, test `aabb`. **Convert**.
3. Switch to DFA tab — point out 4 states (textbook minimum).
4. **Run** on DFA tab. Narrate marching ants + char flash.
5. Reset, change test to `abba`. **Run** → red rejection.
6. Switch to NFA tab, **Run** with `aabb`. Same green result, single-path animation despite many states.

### CFG (≈3 min)
1. Open `/cfg`.
2. Grammar:
   ```
   S -> aSb | ε
   ```
   Test `aabb`. **Convert** → **Run**. Narrate stack growing then shrinking.
3. Reset, test `aab` → red.
4. (If time) Replace with:
   ```
   S -> aS | bS | n
   ```
   Test `abba` → accept. Highlight the `n` notation flexibility.
5. (If time) Replace with `S -> Sa | a`. Run → step viewer shows the
   left-recursion warning. Demonstrates the safety net.

---

## Q&A — likely questions

**Why is the DFA for `(a+b)*abb` only 4 states?**
Hopcroft minimization collapses equivalent states. The four are: haven't
started the suffix, just saw `a`, just saw `ab`, just saw `abb` (accept).

**Does the NFA show all parallel computations?**
No — we adopt JFLAP's "fast run." BFS over `(state, position)` configurations finds one accepting path; the animation shows it one state and one edge at a time. Same per-step shape as the DFA.

**How does the PDA simulator pick a production?**
Score each candidate: 4 if its first symbol matches the next input
character, 3 if it's ε and the input is empty, 2 if it starts with a
nonterminal, 1 if it's ε with input remaining, 0 if it's a terminal that
doesn't match. Highest score wins.

**Why `+` for union and not Kleene-plus?**
Hopcroft-Ullman's textbook uses `+` for union. Supporting both meanings
of `+` would be ambiguous; we picked algebraic-union and kept `*` for
Kleene star.

**Why `n` as epsilon?**
Pure typing convenience — `ε` is hard to type. Recognized as ε only when
it's the entire alternative, so `S -> an` still treats the `n` as a
terminal.

**Why three PDA states (not one)?**
Three states make the initial push a visible animation step (`q0 → q1`)
instead of implicit setup. `q2` is the unique accept so the green
"finished" frame is unambiguous.

**What if the input grammar is bad?**
Backend wraps every endpoint in `try/except` and returns a JSON error.
Step viewer prints it. Browser can't crash from a bad input.

---

## Night-before checklist

- [ ] `python app.py` works locally; both pages load.
- [ ] All four demo cases above run end-to-end.
- [ ] Screenshots from the user manual are captured (so you have
      fallback images if the projector / wifi fails).
- [ ] Deploy URL works from a phone.

---

*See also:* [`paper.md`](./paper.md), [`user_manual.md`](./user_manual.md),
[`reviewer.md`](./reviewer.md), [`presentation_script.md`](./presentation_script.md).
