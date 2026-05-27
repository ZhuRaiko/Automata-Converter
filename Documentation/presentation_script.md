# Presentation Script

Verbatim speaking notes, one block per slide of
[`presentation_guide.md`](./presentation_guide.md). Conversational tone — you
can read it as-is or paraphrase. Time budgets in parentheses are guides,
not hard limits. Total: ~12 min of slides + ~5 min demo + Q&A.

---

## Slide 1 — Title (~30 s)

> "Hi everyone, I'm _[name]_, and today I'll be presenting the **Automata
> Converter Program** — a web application built for our automata theory
> course. The idea behind it is simple: instead of seeing the finished
> NFA, DFA, or PDA drawn on a chalkboard, you watch the algorithm build
> it, step by step, in your browser."

---

## Slide 2 — Why (~60 s)

> "Here's the gap this project tries to close. When we learn this
> material, we see the *result* — the final NFA, the final minimal DFA, a
> static stack drawn next to a PDA. But the algorithms that build those
> machines — Thompson's construction, subset construction, the CFG-to-PDA
> conversion — those usually live in your head or on a whiteboard.
> Especially for the PDA, the *whole point* is that the stack grows and
> shrinks as the input is consumed, and that's almost impossible to
> convey on paper. So this tool runs the actual algorithms in Python,
> renders the diagrams in the browser, and animates the traversals
> frame by frame."

---

## Slide 3 — What it does (~45 s)

> "There are two independent pipelines. The **regex pipeline** takes a
> regular expression, builds an NFA, converts it to a minimal DFA, and
> lets you run a test string against either machine. The **CFG pipeline**
> takes a context-free grammar, builds a top-down pushdown automaton, and
> walks through a derivation with the stack updating live on the side.
> Both pipelines share the same three-area layout: input on top, the
> diagram in the middle, and a scrolling step log at the bottom."

---

## Slide 4 — Theory (~30 s)

> "Quick recap. Regular expressions, NFAs, and DFAs all describe the same
> class — the **regular languages**. Context-free grammars and pushdown
> automata describe a strictly larger class — the **context-free
> languages** — because a PDA has a stack, so it can count nested
> structure. The constructive equivalence theorems between these
> representations are exactly what this project demonstrates."

---

## Slide 5 — Algorithms used (~90 s)

> "Five algorithms are doing the work behind the scenes.
>
> **Thompson's construction** recursively turns the regex AST into NFA
> fragments — one for each operator: symbol, epsilon, concat, union, and
> star. Each fragment has exactly one start and one accept state, which
> keeps the recursion clean.
>
> **Subset construction** then converts that NFA into a DFA by treating
> sets of NFA states as single DFA states, with epsilon-closures handling
> the ε-transitions. On top of that we run **Hopcroft's algorithm** to
> minimize the DFA, so the diagram you see is the unique smallest one for
> the language.
>
> For the NFA tab we adapted **JFLAP's "fast run"** approach: instead of
> showing the full parallel computation — which is visually overwhelming
> — we BFS over configurations internally and replay just one accepting
> path. That way the NFA animation has the same per-step shape as the
> DFA.
>
> The **CFG-to-PDA** construction is a textbook 3-state top-down PDA. And
> the simulator picks productions with a small **LL(1) heuristic**, with
> a step-count safety cap that catches left recursion or unbounded
> expansion."

---

## Slide 6 — Live demo: regex

### Intro on the slide (~20 s)

> "Let me show you the regex pipeline live. I'll use the canonical
> Thompson example: `(a+b)*abb` — that's any string over `a` and `b`
> ending in `abb`. The `+` here is algebraic-union from Hopcroft-Ullman,
> but `|` works too. Test string: `aabb`. Switching to the browser."

### Browser narration (~2 min)

1. **Type `(a+b)*abb`** —
   > "First the regex."
2. **Type `aabb`** —
   > "Test string."
3. **Click Convert** —
   > "Watch the step log fill in: NFA built, DFA built, diagrams rendered."
4. **Stay on NFA tab** —
   > "This is the raw Thompson output. Lots of ε-transitions —
   > fourteen states for a six-character regex."
5. **Switch to DFA tab** —
   > "And here's the minimal DFA. **Four states** — the textbook
   > canonical minimum for this regex."
6. **Click Run** —
   > "Now I run `aabb`. The current state pulses, the edge marches with
   > the ants animation, the consumed character flashes up here. ...
   > and it's accepted. Everything turns green."
7. **Reset, change test to `abba`, Run** —
   > "Same regex, but the string ends in `a`, not `abb`. Red — rejected."
8. **Switch to NFA tab, Run with `aabb`** —
   > "And just so you see it, here's the NFA tab animating the same
   > string. Even though it has fourteen states, only one is active per
   > frame — that's the single-path simulator I mentioned earlier."

---

## Slide 7 — Live demo: CFG

### Intro on the slide (~20 s)

> "Now the context-free side. Grammar: `S -> aSb | epsilon`. That's the
> classic `a^n b^n` language — equal numbers of `a`s followed by `b`s,
> which is famously **not** regular. Test string: `aabb`. Switching."

### Browser narration (~3 min)

1. **Switch to `/cfg`.**
2. **Type the grammar** —
   > "Two productions, separated by `|`. The epsilon can be typed as
   > `ε`, but I'll mention that `^`, `n`, or the word `null` all work
   > too — the tokenizer is flexible."
3. **Type `aabb`** —
   > "Test string."
4. **Click Convert** —
   > "Three states: `q0`, `q1`, `q2`. `q0` is the start, `q1` does the
   > work — those self-loops are the productions and terminal matches —
   > and `q2` is the unique accept."
5. **Click Run** —
   > "Frame zero, the machine sits at `q0` with just `Z` on the stack —
   > that's the bottom marker."
6. **Pause around step 3** —
   > "Now we're in `q1`, we've applied `S -> aSb`, and look at the
   > stack on the right: top is `a`, then `S`, then `b`, then `Z`. The
   > push convention is that the **leftmost** symbol of the production
   > body ends up on top — that matches Sipser and Hopcroft-Ullman."
7. **Continue the animation** —
   > "Match `a`, expand `S` again, match `a`, apply the
   > epsilon-production to pop `S`, match `b`, match `b`. Stack reduced
   > to just `Z`, input consumed. Final frame jumps to `q2` — accepted."
8. **(If time) Reset, test `aab`** —
   > "Same grammar, missing a `b`. Rejected."
9. **(If time) Replace grammar with `S -> aS | bS | n`, test `abba`** —
   > "Generates `{a, b}*`. Note `n` here means epsilon — a convenience
   > for typing on a regular keyboard."

---

## Slide 8 — Animation details (~75 s)

> "A quick note on how the animation was designed, because there were
> real problems to solve. The NFA showing every parallel state at once
> was unreadable — so we switched to the JFLAP fast-run approach: BFS
> internally to find an accepting path, then animate just that path.
>
> On the PDA side, the issue was knowing **which edge** to light up.
> `q1` has many self-loops — one per production, one per terminal — and
> from `(input, stack-top)` alone, multiple edges can match. The fix was
> to have the simulator tag every step with the **index** of the
> transition that fired — we call it `applied_idx`. The frontend then
> highlights exactly that edge. Deterministic, no guessing.
>
> The visual cues are: **marching ants** on the active edge showing
> direction of travel, a **flash** on the consumed character, and
> **green/red flashes** on the stack panel when symbols are pushed or
> popped."

---

## Slide 9 — Limitations (~60 s)

> "I want to be upfront about what this tool **doesn't** do. The regex
> parser only handles single-character atoms — there are no character
> classes like `[a-z]`, no `?` quantifier, no programming-style
> Kleene-plus. We took `+` for union, deliberately.
>
> On the CFG side, the PDA simulator is a deterministic LL(1)-style
> simulator. Genuinely ambiguous grammars — like `S -> SS | (S) | ε` —
> won't work without backtracking, and left-recursive grammars need to
> be rewritten first. When the simulator detects unbounded expansion, it
> stops at a safety cap and reports an error in the step log.
>
> These were intentional decisions to keep the codebase small enough
> that a student can read it alongside the lecture."

---

## Slide 10 — Close (~30 s)

> "The live application is at _[URL]_, and the source is on GitHub at
> the link below. The documentation folder has a full paper, user
> manual, and a reviewer document if you want to dig deeper into any
> algorithm. Thank you — I'm happy to take questions."

---

*See also:* [`presentation_guide.md`](./presentation_guide.md),
[`paper.md`](./paper.md), [`user_manual.md`](./user_manual.md),
[`reviewer.md`](./reviewer.md).
