# Presentation Guide

A slide-by-slide plan, a live-demo script, and talking points for defending
the **Automata Converter Program**. Target length: **12–15 minutes** of
slides + **5 minutes** of live demo + **5 minutes** of Q&A.

Cross-references:
[`paper.md`](./paper.md),
[`user_manual.md`](./user_manual.md),
[`reviewer.md`](./reviewer.md).

> Photo callouts use the same format as [`user_manual.md`](./user_manual.md):
> > 📷 **Slide N image.** Page → Steps → What to capture → Suggested filename.

---

## 1. Recommended slide deck (15 slides)

### Slide 1 — Title

- Project name: **Automata Converter Program**
- Subtitle: "Visualizing the two pipelines of formal language theory"
- Your name(s), course, date, instructor.
- (Optional) the live app URL as a small footer.

**Talking time:** 30 s.

---

### Slide 2 — Why this exists

- Automata theory is taught with diagrams on a chalkboard.
- Students see the final NFA or the final DFA, but rarely the algorithm
  building it step by step.
- The PDA's stack is even worse — drawn on paper it's a static column;
  watching it grow and shrink is what makes parsing click.
- **Goal:** see the constructions happen, in the browser, with the actual
  algorithm.

**Talking time:** 60 s.

---

### Slide 3 — What it does (one diagram)

Embed this overview as a graphic on the slide:

```
Regex pipeline:
  regex string → NFA → minimal DFA → animated string acceptance

CFG pipeline:
  grammar text → PDA → animated LL(1)-style derivation with live stack
```

> 📷 **Slide 3 image — Home page.** Page `/`. Just open the URL.
> Capture: the two cards side by side.
> File: `slide03_home.png`

**Talking time:** 45 s.

---

### Slide 4 — Theory recap (one slide, three rows)

| Layer | Machine | Language class |
|-------|---------|----------------|
| Regex | NFA / DFA | Regular |
| CFG   | PDA | Context-free |

One sentence per row. The audience knows this; just orient them.

**Talking time:** 30 s.

---

### Slide 5 — Algorithms used

Bullet list (no math on this slide):

- **Thompson's construction** — regex → NFA, ~14 states for a 6-character
  regex.
- **Subset construction + Hopcroft minimization** — NFA → DFA, dropping
  unreachable states and merging equivalent ones.
- **NFA single-path simulator (JFLAP "fast run" style)** — BFS over
  configurations, returns one accepting path so the animation isn't
  visually overwhelmed by parallel ε-moves.
- **CFG → PDA (3-state top-down construction)** — initial push of start
  symbol; production transitions; terminal matches; accept move.
- **PDA simulator with LL(1)-style heuristic** — picks the production whose
  first symbol matches the next input.

**Talking time:** 90 s. Mention the sources (Hopcroft-Ullman, Sipser,
JFLAP) but don't dwell.

---

### Slide 6 — Live demo: regex pipeline (intro)

Setup slide before switching to the browser.

- "Watch the DFA being built from a regex."
- Regex you'll demo: `(a+b)*abb`. Test string: `aabb`.
- Mention: `+` is algebraic-union (Hopcroft-Ullman style), `|` works too.

**Talking time:** 30 s.

**Action:** switch to the browser. Demo:

1. Type the regex.
2. Click Convert. Show the NFA tab — point out the ε-edges and how many
   states there are.
3. Switch to the DFA tab — point out it's 4 states, the textbook minimum.
4. Click Run on the DFA tab. Narrate as the green coloring fills in.
5. Reset, change to `abba`, click Run, get red. Explain *why*: the regex
   wants strings ending in `abb`.
6. (Optional) Reset, switch to the NFA tab, Run again. Point out that the
   NFA animates the same way despite having many more states — the
   simulator picks one accepting path.

> 📷 **Slide 6 images (have these ready as fallbacks).**
> - `slide06a_nfa.png` — NFA tab right after Convert.
> - `slide06b_dfa.png` — DFA tab right after Convert (4 states).
> - `slide06c_accept.png` — DFA tab green after Run on `aabb`.
> - `slide06d_reject.png` — DFA tab red after Run on `abba`.

**Demo time:** 2–3 minutes.

---

### Slide 7 — Why minimization matters

Two screenshots side by side:

- Left: a raw subset-construction DFA (5 states including a trap).
- Right: the Hopcroft-minimized version (4 states, no trap).

Caption: "Same language. One fewer state. Same diagram you'd draw on
paper."

If you don't have the raw version handy: the [paper.md](./paper.md) §4.2
explains the worked example numbers.

**Talking time:** 60 s.

---

### Slide 8 — Live demo: CFG → PDA (intro)

- "Now the context-free side."
- Grammar: `S -> aSb | ε`. Test string: `aabb`.

**Action:**

1. Switch to `/cfg`.
2. Type the grammar (use whichever epsilon notation you like — `ε`, `n`,
   `^`, `null`, etc. — and briefly mention the flexibility).
3. Click Convert. Point out the three states `q0`, `q1`, `q2` and the
   self-loops on `q1`.
4. Click Run. Narrate the stack panel as it grows and shrinks.
5. End on the green accept frame.

> 📷 **Slide 8 images.**
> - `slide08a_pda_built.png` — after Convert, stack empty.
> - `slide08b_pda_mid.png` — pause around step 5, multi-symbol stack.
> - `slide08c_pda_accept.png` — final accept frame.

**Demo time:** 2 minutes.

---

### Slide 9 — Stack: top-of-stack at the top

A single picture of the stack panel during a multi-step trace. Annotate:

- The box with the blue border is **top of stack**.
- Push flashes green; pop flashes red.
- Bottom marker `Z` lives at the bottom.

This is the slide where you mention that an earlier version had the
display inverted and we fixed it — a small but real bug squashed during
development. Honest history is fine in an academic talk.

> 📷 **Slide 9 image.** Same `slide08b_pda_mid.png` works; add annotation
> overlays in your slide software.

**Talking time:** 45 s.

---

### Slide 10 — Notation flexibility

Two-column slide:

| Regex page | CFG page |
|------------|----------|
| Union: `\|` `U` `+` | Arrow: `->` `→` `⇒` |
| Kleene: `*` | Alt: `\|` |
| Epsilon: `ε` `E` | Epsilon: `ε` `λ` `Λ` `Ε` `^` `epsilon` `lambda` `null` `nil` `eps` `n`, empty alt |

Note: "Whichever notation your textbook uses, it works."

**Talking time:** 30 s.

---

### Slide 11 — Animation details

Short list:

- **Marching ants** on the active edge (animated line-dash-offset) → shows
  direction of travel.
- **Char flash** on the current consumed symbol.
- **Pulse** on the new active state.
- **Self-loops don't flicker** — when the PDA stays in `q1`, the active
  class isn't toggled.
- **Deterministic edge highlight** — the simulator stamps every step with
  `applied_idx`, so the frontend lights up the *exact* edge that fired,
  not a heuristic guess.

> 📷 **Slide 11 image.** A frame mid-animation with one marching edge and
> the char display showing a letter. File: `slide11_animation.png`.

**Talking time:** 60 s.

---

### Slide 12 — Limitations (honest)

- The PDA simulator is deterministic LL(1)-style. **Ambiguous grammars and
  left-recursive grammars are out of scope.** The tool detects unbounded
  expansion via a step cap and shows a clear warning.
- Regex parser is single-character only — no character classes `[a-z]`, no
  Kleene plus `+` (we use `+` for union — also no quantifiers `?`, `{n,m}`).
- Multi-character nonterminal names in CFG aren't supported (the tokenizer
  takes each character as a symbol).

These are intentional decisions to keep the project teachable. Mention
them before the audience asks.

**Talking time:** 60 s.

---

### Slide 13 — Architecture (one diagram)

Insert the ASCII architecture diagram from [`paper.md`](./paper.md) §3, or
redraw it cleanly in the slide tool.

Key points:

- **Backend:** Flask + pure Python, no third-party scientific libraries.
- **Frontend:** vanilla JavaScript + Cytoscape.js + cytoscape-dagre — all
  from CDNs, no build step.
- **Why:** the project is meant to be read alongside the lecture, so the
  source has to be approachable.

**Talking time:** 60 s.

---

### Slide 14 — References (just the names)

- Sipser, *Introduction to the Theory of Computation*.
- Hopcroft, Motwani, Ullman, *Introduction to Automata Theory*.
- Thompson 1968, *Regular Expression Search Algorithm*.
- Hopcroft 1971, *An n log n algorithm for minimizing states in a finite automaton*.
- JFLAP (Rodger), *Interactive Formal Languages and Automata Package*.
- MIT 18.404 Lecture 4 (Sipser) — CFG ↔ PDA.

Full URLs and bibliographic info in [`paper.md`](./paper.md).

**Talking time:** 20 s.

---

### Slide 15 — Closing + app link

- Live app: _[Insert your deployment URL here]_
- Source: <https://github.com/ZhuRaiko/Automata-Converter>
- "Questions?"

**Talking time:** 20 s, then Q&A.

---

## 2. Live demo script (cheat sheet)

This is the order to run things if your slides die or you're allowed only
to demo. ~5 minutes if you talk steadily.

### Regex demo (2 minutes)

1. Open `/regex`.
2. Regex: `(a+b)*abb`. Test string: `aabb`. **Convert** → **Run** on DFA.
3. Switch to NFA tab, **Run** there too. Same result, different sized
   diagram.
4. Reset → test string `abba` → **Run** → reject (red).

### CFG demo (3 minutes)

1. Open `/cfg`.
2. Grammar:
   ```
   S -> aSb | ε
   ```
   Test string: `aabb`. **Convert** → **Run** → accept (watch stack grow
   and shrink).
3. Reset → test string `aab` → **Run** → reject.
4. (Optional bonus.) Replace grammar with:
   ```
   S -> aS | bS | n
   ```
   Note the `n` notation. Test `abba` → accept. Demonstrates language `{a,b}*`.
5. (Optional bonus.) Show the safety net for bad grammars:
   ```
   S -> Sa | a
   ```
   Test anything; the step viewer shows the "Simulation exceeded N steps"
   warning. Honest limit.

---

## 3. Demo cases ranked

If you only have time for two demos, do these:

1. **Regex `(a+b)*abb` on `aabb` / `abba`.** Classic Thompson example; the
   DFA is minimal at 4 states; you get one accept and one reject.
2. **CFG `S -> aSb | ε` on `aabb` / `aab`.** Classic `aⁿbⁿ` example; the
   stack visibly grows then shrinks.

If you have more time, in priority order:

3. The `+` and `n` notation demonstration — flexibility.
4. A left-recursion grammar to show the safety net.
5. NFA tab animation on the same regex to show single-path simulation.

---

## 4. Q&A preparation

The likely questions, with one-paragraph answers:

**Q. Why is the DFA only 4 states for `(a+b)*abb`?**
> Because Hopcroft minimization (the partition-refinement algorithm we run
> after subset construction) recognizes that several intermediate subsets
> are behaviorally identical. The 4-state DFA — "haven't seen a yet",
> "just saw a", "just saw ab", "just saw abb" — is the canonical minimum.

**Q. Does the NFA simulation really show every parallel computation?**
> No, and that's deliberate. An NFA on `(a+b)*abb` can have dozens of
> states active at once because of the ε-closures around the star. That
> looks chaotic. We adopt JFLAP's "fast run" idea: build the full
> configuration tree internally with BFS, then return one accepting path.
> The animation shows one active state and one edge at a time — same
> per-step shape as the DFA.

**Q. How does the PDA simulator pick a production?**
> It uses a small LL(1)-style heuristic. Each candidate production gets a
> score based on whether its first symbol matches the next input
> character. Highest score wins; ties resolve by user-written order. This
> handles classroom-friendly grammars like `S → aSb | ε`. Ambiguous and
> left-recursive grammars are detected — a step cap stops the run and the
> result includes an explanatory error.

**Q. Why `+` for union and not Kleene-plus?**
> Hopcroft-Ullman's textbook uses `+` for union (algebraic notation: "L₁ +
> L₂"), and our students often see that notation in lectures. We don't
> support Kleene-plus because we already have `*`, and supporting both
> would create an ambiguity with the union notation. The docstring on the
> regex parser spells this out.

**Q. Why `n` as epsilon? Doesn't that conflict with `n` as a terminal?**
> Recognized as epsilon only when `n` is the *entire* alternative. Inside
> `an` the `n` is still a terminal. The synonym list also includes the
> Greek `ε`, `λ`, `Λ`, `Ε`, `^`, and the words `epsilon`, `lambda`, `null`,
> `nil`, `eps`. Pick whichever your textbook uses.

**Q. Why is the stack panel rendered top-to-bottom?**
> Because that's how PDAs are drawn on paper: top of stack at the top of
> the column. (Earlier we had a CSS bug that flipped it; we explicitly
> verified this against textbook conventions and fixed it.)

**Q. Why three states in the PDA? Sipser uses one or two.**
> Three states make the animation clearer: `q0` is where the machine
> starts before any moves, `q1` is where all real work happens, `q2` is
> the final accept. The student sees the initial push as a move from `q0`
> to `q1`, which makes "initialize the stack" feel like a step instead of
> happening implicitly.

**Q. Can it handle a real programming-language grammar?**
> No, and it's not supposed to. The simulator is a deterministic
> LL(1)-style toy. Real parsers use LR or full PEG with backtracking. The
> educational value here is seeing the stack work for small classroom
> grammars.

**Q. What if the user types something weird?**
> The backend wraps every endpoint in a `try/except` and returns a JSON
> error message. The frontend prints those errors into the step viewer.
> Crashing isn't possible from the browser.

---

## 5. Rehearsal checklist (the night before)

- [ ] Run `python app.py` locally and confirm both pages load.
- [ ] Verify all five demo cases work end-to-end.
- [ ] Take the screenshots listed in [`user_manual.md`](./user_manual.md)
      so you have fallback images if the live demo fails.
- [ ] Check the deploy URL works from a phone/tablet — instructors may
      try to follow along.
- [ ] Read the limitations slide (Slide 12) out loud — make sure the
      phrasing sounds confident, not defensive.

---

*See also: [`paper.md`](./paper.md), [`user_manual.md`](./user_manual.md),
[`reviewer.md`](./reviewer.md).*
