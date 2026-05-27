# Automata Converter Program

*A web app that visualizes two pipelines from formal language theory:
regex → NFA → minimized DFA, and CFG → PDA, with animated string acceptance.*

**Authors:** _[Your name(s)]_  
**Course / Section:** _[Code, section, semester]_  
**Date:** _[Submission date]_  
**Live application:** _[Insert your deployment URL here]_  
**Source:** <https://github.com/ZhuRaiko/Automata-Converter>

---

## Abstract

Builds an NFA from a regular expression (Thompson's construction), converts
it to a minimal DFA (subset construction + Hopcroft minimization), and
animates string acceptance on either machine. Builds a top-down PDA from a
context-free grammar and animates an LL(1)-style derivation with a live
stack panel. The UI can check multiple strings and simulate any selected
row. Pure Python + vanilla JS + Cytoscape.js — no build step.

## 1. Background

| Layer | Machine    | Language class |
|-------|------------|----------------|
| Regex | NFA / DFA  | Regular        |
| CFG   | PDA        | Context-free   |

- **RE → NFA → DFA.** Every regular expression has an equivalent NFA
  (Thompson, 1968); every NFA has an equivalent DFA (Rabin-Scott, 1959);
  every DFA has a unique minimum (Hopcroft, 1971).
- **CFG ↔ PDA.** Pushdown automata accept exactly the context-free
  languages. The constructive proof is the basis of every parser
  generator.

## 2. Architecture

```
Browser  (regex.html, cfg.html  +  vanilla JS  +  Cytoscape.js + dagre)
   │ JSON over fetch()
Flask app (app.py)
   └─ algorithms/
        thompson.py            (regex → NFA)
        subset_construction.py (NFA → minimal DFA; Hopcroft)
        string_checker_dfa.py
        string_checker_nfa.py  (BFS single-path)
        cfg_to_pda.py
        string_checker_pda.py  (LL(1) heuristic; applied_idx)
```

Pure Python on the server, no third-party libs. CDN for Cytoscape + dagre;
no `npm` step. The point is for a student to read the source alongside the
lecture.

## 3. Algorithms

**Thompson's construction (RE → NFA).** Recursive translation of the regex
AST into small NFA fragments (symbol, ε, concat, union, star). Each
fragment has exactly one start and one accept. ~O(n) states for an O(n)
regex.

**Subset construction + Hopcroft (NFA → minimal DFA).** Worklist BFS turns
ε-closures of NFA-state sets into DFA states. A trap state is added only
if some transition would otherwise be undefined. Hopcroft's partition
refinement collapses behaviorally equivalent states; result is the unique
minimum DFA. For `(a+b)*abb` the minimum has 4 states.

**NFA simulation (JFLAP "fast run").** BFS over `(state, input position)`
configurations; reconstruct one accepting path (or the longest partial
path on rejection). The animation therefore shows one active state and one
edge at a time — same shape as the DFA animation.

**CFG → PDA.** Three states. `q0` is start, `q1` does the work (one
self-loop per production, one per terminal), `q2` is the unique accept.
The initial transition pops `Z` and pushes `[start_symbol, Z]`; the accept
transition is `q1 --ε, Z--> q2`.

**Push convention.** `push[0]` ends on top of the stack. For `S → aSb` we
store `push = [a, S, b]` and the simulator iterates `reversed(push)` so
`a` is on top — matches Sipser / UTEP / Hopcroft-Ullman conventions.

**PDA simulator (LL(1)-style).** Per step, the simulator picks the
production whose first symbol matches the next input character (score 4);
falls back to ε on empty input (3), then to nonterminal-first expansion
(2), then to ε with input remaining (1). Every step is tagged with
`applied_idx` so the frontend lights up the exact edge — no guessing.
`max_steps = 2000` catches left recursion; the response includes an
explanatory `error` line.

Full algorithm reference: [`algorithms.md`](./algorithms.md).

## 4. User Manual (summary)

Two pages, same three-area layout (input, diagram, scrolling step viewer).
Both pages include five test-string rows with accepted/rejected status and
a **Simulate** button.

- **`/regex`** — accepts union `|`, `U`, `+`; Kleene `*`; epsilon `ε`, `E`.
  Click Convert, then Run on the active tab.
- **`/cfg`** — accepts arrows `->`, `→`, `⇒`; alternatives `|`; epsilon
  `ε`, `λ`, `Λ`, `Ε`, `^`, `epsilon`, `lambda`, `null`, `nil`, `eps`, `n`,
  or an empty alternative.

Full walkthroughs: [`user_manual.md`](./user_manual.md).

## 5. Sample Outputs

> Capture each screenshot exactly as described, save under
> `Documentation/images/`. Filenames are suggestions.

| # | Page | Setup | Capture | File |
|---|------|-------|---------|------|
| 1 | `/` | Open in browser | Landing page with two cards | `fig01_home.png` |
| 2 | `/regex` | `(a+b)*abb`, test `aabb`, click Convert | NFA tab + step viewer | `fig02_nfa.png` |
| 3 | `/regex` | Same, switch to DFA tab | 4-state minimal DFA | `fig03_dfa.png` |
| 4 | `/regex` | DFA tab, click Run, wait for finish | All elements green | `fig04_accept.png` |
| 5 | `/regex` | Reset, test `abba`, click Run | Red rejection | `fig05_reject.png` |
| 6 | `/regex` | NFA tab, click Run, pause mid-animation | One yellow state, one orange marching edge | `fig06_nfa_run.png` |
| 7 | `/cfg` | `S -> aSb \| ε`, test `aabb`, click Convert | PDA + empty stack panel; q2 final | `fig07_pda.png` |
| 8 | `/cfg` | Click Run, pause around step 5 | Multi-symbol stack, marching edge | `fig08_pda_running.png` |
| 9 | `/cfg` | Let it finish | Green accept, stack = `[Z]`, q2 active | `fig09_pda_accept.png` |
| 10 | `/cfg` | `S -> aS \| bS \| n` on `aa` | Accept — `n` recognized as ε | `fig10_n_epsilon.png` |
| 11 | `/cfg` | `S -> Sa \| a`, any input | Step viewer shows "Simulation exceeded N steps" | `fig11_left_recursion.png` |

## 6. App Link

> _Replace before submission._
> Live: `[Insert your deployment URL here]`
> Local: `python app.py` then `http://127.0.0.1:5000/`.

## 7. Conclusion

The visualizations match the way these constructions are taught:
single-path NFA traces, minimal DFAs, a stack panel that grows and shrinks
on cue, and exact edge highlighting from `applied_idx`. The codebase is
small enough to read in one sitting, which is part of the pedagogy.

## References

1. Sipser, M. *Introduction to the Theory of Computation*, 3rd ed. Cengage, 2012.
2. Hopcroft, Motwani, Ullman. *Introduction to Automata Theory, Languages,
   and Computation*, 3rd ed. Pearson, 2006.
3. Hopcroft, J. E. "An n log n algorithm for minimizing states in a finite
   automaton." Stanford TR STAN-CS-71-190, 1971.
4. Thompson, K. "Regular expression search algorithm." *CACM* 11.6 (1968): 419–422.
5. Rodger, S. H. *JFLAP — Interactive Formal Languages and Automata
   Package*. <https://www.jflap.org/jflapbook/jflapbook2006.pdf>.
6. Sipser, M. MIT 18.404J Fall 2020, Lecture 4 *PDA ↔ CFG*.
   <https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/>.
7. Cytoscape.js + cytoscape-dagre. <https://js.cytoscape.org/>,
   <https://github.com/cytoscape/cytoscape.js-dagre>.

---

*Companion docs:* [`user_manual.md`](./user_manual.md),
[`presentation_guide.md`](./presentation_guide.md),
[`reviewer.md`](./reviewer.md),
[`algorithms.md`](./algorithms.md).
