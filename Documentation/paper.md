# Automata Converter Program

*A web-based educational tool for visualizing two pipelines of automata theory:
regular expression → NFA → minimized DFA → string acceptance, and
context-free grammar → pushdown automaton → step-by-step simulation.*

**Authors:** _[Your name(s) here]_
**Course / Section:** _[Course code, section, semester]_
**Date:** _[Submission date]_
**Live application:** _[Insert your deployment URL here]_
**Source repository:** [https://github.com/ZhuRaiko/Automata-Converter](https://github.com/ZhuRaiko/Automata-Converter)

---

## Abstract

This project implements an interactive web application that teaches two of the
core constructions in formal language theory by letting students see them
happen. From a regular expression, the program builds a nondeterministic
finite automaton (NFA) using Thompson's construction, converts it to a
deterministic finite automaton (DFA) via subset construction, minimizes the
DFA with Hopcroft's algorithm, and animates string acceptance on either
machine. From a context-free grammar (CFG), the program builds a top-down
pushdown automaton (PDA) and animates an LL(1)-style derivation with live
stack updates. Diagrams use a layered dagre layout so the geometry matches
how state machines are typically drawn in textbooks. The implementation is
deliberately small (Flask + vanilla JS + Cytoscape.js from a CDN) so students
can read the source alongside the lecture material.

---

## 1. Introduction

Formal language theory is mostly taught on paper: a chalkboard NFA, a
hand-traced subset construction, a stack drawn next to a PDA. Students who
have not yet built the algorithms themselves often have trouble connecting
the textbook diagrams with what the machine is "doing" step by step. This
project closes that gap by exposing every intermediate object — the AST of
the regular expression, the NFA, the DFA before and after minimization, the
PDA's transition list — as a click-through visualization in the browser.

Two independent pipelines are supported:

1. **Regex pipeline.** Regular expression → NFA → DFA → animated string test.
2. **CFG pipeline.** Context-free grammar → PDA → animated string test.

The deliverable is one Flask application with two pages plus a landing page.
All algorithms run in Python; the frontend uses vanilla JavaScript and the
Cytoscape.js library (loaded from a CDN) to render diagrams and animate
traversals.

## 2. Theoretical Background

### 2.1 Regular Expressions (RE)

A regular expression over an alphabet Σ is a finite string built from the
operators **union** (`|`, `+`, or `U`), **concatenation** (juxtaposition),
**Kleene star** (`*`), and atoms (a single symbol, the empty string `ε`, or a
parenthesized subexpression). The set of regular expressions denotes exactly
the **regular languages**. The standard precedence is

```
union  <  concatenation  <  Kleene star  <  atom
```

Examples used throughout this paper:

- `a*` — zero or more `a`s.
- `(a+b)*abb` — any string over {a, b} ending in `abb`. (Hopcroft-Ullman's
  algebraic notation `+` is supported as an alias for `|`.)

### 2.2 Nondeterministic and Deterministic Finite Automata (NFA, DFA)

A **finite automaton** is a 5-tuple (Q, Σ, δ, q₀, F): finite set of states,
input alphabet, transition function, start state, set of accepting states.

- In an **NFA**, δ(q, a) may return a set of states, and ε-transitions
  (moves that consume no input) are allowed. A string is accepted iff some
  computation reaches an accepting state with all input consumed.
- In a **DFA**, δ(q, a) is a single state, ε-transitions are not allowed,
  and the transition function is total (defined for every (state, symbol)
  pair).

Every NFA has an equivalent DFA (Rabin–Scott, 1959), proved constructively
by the **subset construction**: DFA states are subsets of NFA states, and
the DFA transitions correspond to the union of moves available to all NFA
states in the subset (after taking ε-closures). The minimum DFA equivalent
to a given DFA is unique up to renaming and can be computed in
O(|Q|·|Σ|·log|Q|) time by **Hopcroft's algorithm**.

### 2.3 Context-Free Grammars (CFG)

A **context-free grammar** is a 4-tuple (V, Σ, R, S): set of nonterminals,
set of terminals, set of productions of the form `A → α` with `A ∈ V` and
`α ∈ (V ∪ Σ)*`, and a designated start symbol `S`. The language generated
by a CFG is the set of terminal strings derivable from `S`.

Example: `S → aSb | ε` generates the language `{ aⁿbⁿ | n ≥ 0 }`, which is
not regular (it requires unbounded memory).

### 2.4 Pushdown Automata (PDA)

A **pushdown automaton** is a finite automaton augmented with a stack. The
class of languages a PDA accepts is exactly the class of **context-free
languages**. A PDA transition reads the next input symbol (or ε), pops the
top of the stack, and pushes a string of stack symbols.

Two equivalent acceptance criteria exist: by **final state** (reach an
accepting state with the input consumed) and by **empty stack** (consume the
input and reduce the stack to empty). This project uses *final state*
acceptance with a bottom-marker `Z`, which makes the visualization clearer.

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser                                                        │
│  ┌─────────────┐    ┌─────────────────────┐    ┌─────────────┐  │
│  │ regex.html  │    │  cfg.html           │    │ index.html  │  │
│  │ + regex.js  │    │  + cfg.js           │    │             │  │
│  │ + Cytoscape │    │  + Cytoscape+dagre  │    │             │  │
│  └──────┬──────┘    └──────────┬──────────┘    └─────────────┘  │
│         │ JSON over fetch()    │                                │
└─────────┼──────────────────────┼────────────────────────────────┘
          │                      │
┌─────────▼──────────────────────▼─────────┐
│  Flask app (app.py)                      │
│  ┌─────────────────────────────────────┐ │
│  │  algorithms/                        │ │
│  │    thompson.py            (RE→NFA)  │ │
│  │    subset_construction.py (NFA→DFA, │ │
│  │                           Hopcroft) │ │
│  │    string_checker_dfa.py            │ │
│  │    string_checker_nfa.py (BFS path) │ │
│  │    cfg_to_pda.py                    │ │
│  │    string_checker_pda.py (LL(1)+    │ │
│  │                           applied_idx) │
│  └─────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

**Stack rationale.** Flask + vanilla JS keeps the project Python-only on the
server and zero-build on the client. Cytoscape.js + the dagre extension are
both loaded from CDNs, so there is no `npm install` step. This is
intentional: the goal is for a student reader to be able to open any source
file and follow it without first learning a tool chain.

## 4. Algorithms

### 4.1 Thompson's Construction (RE → NFA)

The regex is parsed with a recursive-descent parser that respects the
precedence stated above, producing an AST whose node types are `Symbol`,
`Epsilon`, `Star`, `Concat`, and `Union`. Each node is translated into a
small NFA fragment with a single start and a single accept state:

- **Symbol `a`** — two fresh states linked by an `a`-edge.
- **Epsilon** — two fresh states linked by an ε-edge.
- **Concat(L, R)** — glue `L.accept` to `R.start` with an ε-edge.
- **Union(L, R)** — new start branches to both children's starts; both
  children's accepts converge into a new accept via ε-edges.
- **Star(L)** — new start with a bypass edge (matches empty) plus an entry
  edge to `L.start`; `L.accept` loops back to `L.start` and to the new
  accept.

The construction guarantees every fragment has exactly one start and one
accept state, which makes the recursion clean. For `(a+b)*abb` the result
has 14 states and 16 transitions.

### 4.2 Subset Construction + Hopcroft Minimization (NFA → DFA)

A worklist BFS turns the NFA into a DFA by treating sets of NFA states as
single DFA states:

1. The initial DFA state is the ε-closure of the NFA start.
2. For each unprocessed DFA state `T` and each input symbol `a`,
   compute `U = ε-closure(move(T, a))`. Each new subset becomes a new DFA
   state.
3. A trap (sink) state is added **only if** some transition would otherwise
   be undefined, so simple regexes like `a*` do not get a spurious dead
   node.

The result is then minimized with Hopcroft's partition refinement: states
are partitioned into accepting vs. non-accepting blocks; each block is
repeatedly split whenever some symbol takes its members to different blocks.
The blocks of the fixed point are the states of the minimal DFA.

For `(a+b)*abb` the raw subset construction yields 5 states (4 reachable +
1 trap), and minimization keeps 4 — the canonical textbook minimal DFA.

### 4.3 NFA String Simulation (JFLAP "fast run" style)

A naïve NFA simulator highlights every active state at every step. With
many ε-transitions that becomes unreadable, so the simulator instead
performs BFS over `(state, input_position)` configurations and reconstructs
**one accepting path** if the string is in the language, or the path that
consumed the most input otherwise. The trace returned to the frontend has
the same per-step shape as the DFA trace — one active state, one edge that
just fired — so the NFA tab animates exactly like the DFA tab.

### 4.4 CFG → PDA Conversion (Top-Down / LL-style)

The PDA has 3 states. `q0` is the start, `q2` the unique accept state, and
all work happens in `q1`. The construction:

1. **Initial transition** `q0 --ε, Z / [S, Z]--> q1` pops the bottom marker
   and pushes the start symbol on top of `Z`.
2. **Production transitions** `q1 --ε, A / α--> q1` for every rule `A → α`.
3. **Terminal matches** `q1 --a, a / ε--> q1` for every terminal `a` that
   appears in the grammar.
4. **Accept** `q1 --ε, Z / [Z]--> q2` once the input is consumed and only
   `Z` remains.

**Push convention.** In every transition, `push[0]` is the symbol that ends
up on top of the stack after the push, `push[-1]` deepest. This is the
standard textbook convention (`push Xₙ first, then Xₙ₋₁, ...`, so `X₁`
emerges on top — UTEP CS 3350, MIT 18.404 Lecture 4). The simulator
implements this by iterating `reversed(push)` when applying a transition.

### 4.5 PDA Simulation with LL(1)-style Heuristic

A simple "first matching production wins" strategy is too weak: for
`S → aSb | ε` on input `aabb`, picking `aSb` blindly fails as soon as no `a`
remains. The simulator instead scores each candidate production:

| Score | Situation |
|------:|-----------|
| 4 | Production starts with a terminal that matches the next input character. |
| 3 | Production is ε and the input is already empty (only this can accept). |
| 2 | Production starts with a nonterminal (defer judgment). |
| 1 | Production is ε but input still remains. |
| 0 | Production starts with a terminal that doesn't match the next input character. |

The highest-scoring production wins; ties resolve by user-written order.
Every step in the trace carries `applied_idx`, the index of the transition
that fired, so the frontend lights up the exact edge — no guessing among
the many self-loops on `q1`. A `max_steps` cap (default 2000) catches
left-recursive grammars that would otherwise expand forever; in that case
the result carries an explanatory `error` field.

## 5. User's Manual (summary)

The full manual is in [`user_manual.md`](./user_manual.md). Quick reference:

**Regex page (`/regex`).** Type a regular expression and a test string,
click **Convert** to build the NFA + minimal DFA, click **Run** to animate
acceptance on the active tab (NFA or DFA).

Accepted regex notation: union `|` / `U` / `+`, Kleene `*`, epsilon `ε` / `E`,
parentheses, single-character atoms.

**CFG page (`/cfg`).** Type the grammar (one production per line), click
**Convert** to build the PDA, click **Run** to animate the derivation.

Accepted CFG notation: arrows `->` / `→` / `⇒`, alternatives `|`, and any of
`ε`, `λ`, `Λ`, `Ε`, `^`, `epsilon`, `lambda`, `null`, `nil`, `eps`, `n`, or
the empty alternative for the empty production.

## 6. Sample Outputs

> **Photo guidance.** For each subsection below, capture the screenshot
> exactly as described and save it under `Documentation/images/`. The
> suggested filename is given in each callout.

### 6.1 Home page

> 📷 **Figure 1 — Landing page.**
> - Page: `/`
> - Action: Open the app in a browser at the live URL.
> - File: `fig01_home.png`

### 6.2 Regex pipeline — `(a+b)*abb`

> 📷 **Figure 2 — Regex input and step viewer after Convert.**
> - Page: `/regex`
> - Regex: `(a+b)*abb`
> - Test string: `aabb`
> - Click **Convert** but not yet **Run**.
> - Capture: input panel + diagram area (NFA tab active) + step viewer.
> - File: `fig02_regex_converted.png`

> 📷 **Figure 3 — NFA diagram.**
> - Same state as Figure 2, NFA tab active.
> - Capture: only the diagram area, full NFA visible (14 states).
> - File: `fig03_nfa.png`

> 📷 **Figure 4 — Minimal DFA diagram.**
> - Switch to DFA tab.
> - Capture: only the diagram area (4 states, canonical minimum).
> - File: `fig04_dfa_minimized.png`

> 📷 **Figure 5 — Accepting run on the DFA.**
> - With DFA tab active, click **Run**. Wait until the animation finishes.
> - Capture: the green "valid" coloring on states + edges, char display
>   showing the last consumed character.
> - File: `fig05_dfa_accept.png`

> 📷 **Figure 6 — Rejecting run.**
> - Reset, change the test string to `abba`, click **Run**.
> - Capture: red "invalid" coloring with the path that was traversed before
>   rejection.
> - File: `fig06_dfa_reject.png`

> 📷 **Figure 7 — NFA single-path animation.**
> - Reset, switch back to NFA tab, test string `aabb`, click **Run**. Pause
>   the recording mid-animation.
> - Capture: one orange edge marching (line-dash flow), one yellow active
>   state, char display showing `ε` or the consumed character.
> - File: `fig07_nfa_animation.png`

### 6.3 CFG pipeline — `S -> aSb | ε`

> 📷 **Figure 8 — CFG input and PDA diagram.**
> - Page: `/cfg`
> - Grammar:
>     ```
>     S -> aSb | ε
>     ```
> - Test string: `aabb`
> - Click **Convert** only.
> - Capture: input panel + PDA diagram + empty stack panel.
> - File: `fig08_pda_built.png`

> 📷 **Figure 9 — PDA mid-derivation with stack populated.**
> - Click **Run**. Pause when the stack visibly has multiple symbols, e.g.
>   around step 5 (`[Z, b, b, S]`).
> - Capture: PDA diagram with one orange marching edge, the active state
>   (`q1`) highlighted, and the stack panel showing top-of-stack at the top.
> - File: `fig09_pda_running.png`

> 📷 **Figure 10 — PDA accept.**
> - Let the animation finish on the same `aabb` run.
> - Capture: green "valid" coloring on all elements, stack showing just `Z`,
>   active state on `q2`.
> - File: `fig10_pda_accept.png`

### 6.4 Notation flexibility

> 📷 **Figure 11 — Algebraic union `+` produces the same DFA.**
> - Regex: `(a+b)*abb`
> - Capture only the DFA tab after Convert — must be 4 states, identical to
>   Figure 4.
> - File: `fig11_plus_union.png`

> 📷 **Figure 12 — Epsilon shortcuts on the CFG page.**
> - Grammar: `S -> aS | bS | n`
> - Test string: `aa`
> - Click Convert, then Run, let it finish (accepts).
> - Capture: full page; the grammar shows `n` and the run accepts.
> - File: `fig12_n_epsilon.png`

### 6.5 Error / edge cases

> 📷 **Figure 13 — Left-recursion warning.**
> - Grammar: `S -> Sa | a`
> - Test string: any (e.g. `aa`)
> - Click Convert, then Run.
> - Capture: the step viewer at the end. It should display the
>   "Simulation exceeded N steps" warning.
> - File: `fig13_left_recursion_warning.png`

## 7. Web Application Link

> _Replace this with the deployed app URL before submission._
>
> **Live application:** `[Insert your deployment URL here]`

If hosted locally during defense, run `python app.py` and open
`http://127.0.0.1:5000/`.

## 8. Conclusion

The project demonstrates the two canonical pipelines of formal language
theory side by side. By tagging every animation frame with the exact
transition fired, by minimizing the DFA before display, and by collapsing
the NFA's parallel reality into a single textbook-style path, the
visualizations match the way these constructions are taught — which is the
whole point of the tool. The codebase is small enough to read in one
sitting, which is itself part of the pedagogy.

## References

1. Sipser, M. *Introduction to the Theory of Computation* (3rd ed.). Cengage,
   2012. — Used as the canonical reference for the CFG → PDA construction
   and PDA semantics.
2. Hopcroft, J. E., Motwani, R., Ullman, J. D. *Introduction to Automata
   Theory, Languages, and Computation* (3rd ed.). Pearson, 2006. — Source
   of the algebraic regex notation (`+` for union) and the subset
   construction.
3. Hopcroft, J. E. "An n log n algorithm for minimizing states in a finite
   automaton." Tech. Rep. STAN-CS-71-190, Stanford, 1971. — DFA
   minimization algorithm.
4. Thompson, K. "Programming Techniques: Regular expression search
   algorithm." *Comm. ACM* 11.6 (1968): 419–422. — Original Thompson's
   construction.
5. Rodger, S. H. *JFLAP — An Interactive Formal Languages and Automata
   Package*. <https://www.jflap.org/jflapbook/jflapbook2006.pdf>. — Source
   of the "fast run" idea for single-path NFA visualization.
6. Sipser, M. (Lecturer). MIT 18.404J *Theory of Computation*, Fall 2020,
   Lecture 4 "Pushdown Automata, CFG ↔ PDA."
   <https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/>.
7. Kreutzer, V. (UTEP). CS 3350 lecture notes, *CFG to PDA construction*.
   <https://www.cs.utep.edu/vladik/cs3350.20a/CFGtoPDA.pdf>.
8. Cytoscape.js library and the cytoscape-dagre extension.
   <https://js.cytoscape.org/> and
   <https://github.com/cytoscape/cytoscape.js-dagre>.

---

*Related project documents in this folder:
[`user_manual.md`](./user_manual.md),
[`presentation_guide.md`](./presentation_guide.md),
[`reviewer.md`](./reviewer.md),
[`algorithms.md`](./algorithms.md).*
