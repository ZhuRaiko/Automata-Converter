# Comprehensive Reviewer — Automata Converter Program

A study guide written as the document you would use to prepare for a
defense or final exam on this project. Organized as:

1. Definitions you must be able to recite
2. The two pipelines, end to end
3. Algorithms in detail (with worked traces)
4. Implementation decisions and *why*
5. Sample questions with full answers
6. Glossary

Cross-references:
[`paper.md`](./paper.md),
[`user_manual.md`](./user_manual.md),
[`presentation_guide.md`](./presentation_guide.md),
[`algorithms.md`](./algorithms.md).

---

## 1. Definitions you must know

### Regular expression (RE)
A string over the alphabet Σ ∪ { `(` `)` `*` `|` `ε` }. Inductive definition:

- `ε` (epsilon) and every `a ∈ Σ` are REs.
- If `R` and `S` are REs, so are `(R|S)` (union), `(RS)` (concatenation),
  and `(R*)` (Kleene star).

The language `L(R) ⊆ Σ*` is defined inductively to match.

### Finite automaton
A 5-tuple `(Q, Σ, δ, q₀, F)`:

- `Q` — finite set of states.
- `Σ` — input alphabet.
- `δ` — transition function. For a **DFA**, `δ : Q × Σ → Q` (total). For
  an **NFA**, `δ : Q × (Σ ∪ {ε}) → 2^Q`.
- `q₀ ∈ Q` — start state.
- `F ⊆ Q` — accepting (final) states.

A string `w` is **accepted** iff there's a computation that consumes all of
`w` and ends in some state in `F`.

### Context-free grammar (CFG)
A 4-tuple `(V, Σ, R, S)`:

- `V` — nonterminals.
- `Σ` — terminals (disjoint from `V`).
- `R ⊆ V × (V ∪ Σ)*` — productions, written `A → α`.
- `S ∈ V` — start symbol.

`L(G)` is the set of terminal strings derivable from `S` by repeatedly
applying productions.

### Pushdown automaton (PDA)
A 7-tuple `(Q, Σ, Γ, δ, q₀, Z₀, F)`:

- `Q, Σ, q₀, F` — as in a finite automaton.
- `Γ` — stack alphabet.
- `Z₀ ∈ Γ` — initial stack symbol (we use `Z`).
- `δ : Q × (Σ ∪ {ε}) × Γ → 2^(Q × Γ*)` — read an input symbol or ε, pop
  the top of stack, transition to a new state and push a string onto the
  stack.

Two equivalent acceptance criteria: by **final state** (used here) or by
**empty stack**.

### Equivalences (theorems)

| Class | Machine | Generator |
|-------|---------|-----------|
| Regular | NFA ≡ DFA | Regular expression |
| Context-free | PDA | Context-free grammar |

These equivalences are *constructive* — the algorithms in this project
literally build the machine from the generator.

---

## 2. The two pipelines

### 2.1 Regex pipeline

```
regex string
  → Parser builds AST (precedence: union < concat < star < atom)
  → Thompson's construction translates AST to NFA fragments
  → Subset construction expands NFA into DFA (with ε-closures)
  → Hopcroft minimization collapses equivalent DFA states
  → DFA simulator: O(|w|) walk for string acceptance
  → NFA simulator: BFS over (state, input position) configurations,
                   returns ONE accepting path
```

### 2.2 CFG pipeline

```
grammar text
  → Tokenizer: split into productions, recognize ε synonyms
  → CFG → PDA construction: 3 states, one transition per rule + one per terminal
  → PDA simulator: deterministic LL(1)-style; each step tagged with
                   applied_idx for exact edge highlight
```

---

## 3. Algorithms in detail

### 3.1 Thompson's construction (RE → NFA)

For each AST node:

| Node | NFA fragment |
|------|--------------|
| `Symbol(a)` | `s --a--> f`, two new states |
| `Epsilon` | `s --ε--> f`, two new states |
| `Concat(L, R)` | use both fragments, add `L.accept --ε--> R.start`, new start = `L.start`, new accept = `R.accept` |
| `Union(L, R)` | new `s, f`; `s --ε--> L.start`, `s --ε--> R.start`, `L.accept --ε--> f`, `R.accept --ε--> f` |
| `Star(L)` | new `s, f`; `s --ε--> L.start`, `s --ε--> f` (bypass empty), `L.accept --ε--> L.start`, `L.accept --ε--> f` |

**Invariant.** Every fragment has exactly one start and one accept state.

**Size.** For an RE of size `n`, the NFA has `O(n)` states and `O(n)`
transitions (each operator adds a constant number of states/edges).

### 3.2 Subset construction (NFA → DFA, before minimization)

```
start_DFA = ε-closure({start_NFA})           # the initial DFA state is a set
worklist = [start_DFA]
seen = {start_DFA}
while worklist:
    T = pop()
    for symbol a in Σ:
        U = ε-closure(move(T, a))
        if U not in seen:
            add U to seen and worklist
        record transition T --a--> U
add trap state IF any transition above is undefined
accept states = { T  |  any NFA accept ∈ T }
```

**Why ε-closure on both ends.** Because in an NFA, ε-moves are "free" —
before reading any symbol, the machine could already be in any of the
ε-reachable states; after reading a symbol, it could free-move again.

### 3.3 Hopcroft minimization (DFA → minimal DFA)

Partition refinement:

```
P = [accepts, non-accepts]                  # initial coarse partition
W = [accepts, non-accepts]                  # worklist
while W:
    A = pop a set from W
    for each symbol a:
        X = { states whose a-transition lands in A }
        for each block Y in P:
            inter = Y ∩ X
            diff  = Y \ X
            if inter and diff both non-empty:
                replace Y in P with inter, diff
                update W accordingly
```

When the worklist is empty, each block of P is one state in the minimal
DFA. The minimal DFA is unique up to renaming.

**Worked example: `(a+b)*abb`.**
- Raw subset construction produces 5 states (4 reachable + 1 trap).
- Hopcroft sees the trap is in its own block and the four others are
  pairwise distinguishable.
- Result: 4 states. This is the textbook minimum: "haven't seen `a`",
  "just saw `a`", "just saw `ab`", "just saw `abb`" (accepting).

### 3.4 NFA path-finding ("fast run")

```
BFS over configurations (state, pos):
  initial = (start_NFA, 0)
  for each config: try ε-edges and the labeled edge from input[pos]
  remember the parent of each new config
  stop when we reach (accept_NFA, len(input))
If no accept found, reconstruct path to the farthest-consumed config.
```

**Return:** one step per transition fire, each labeled with which edge
fired and what character (if any) was consumed. Animation shows one
active state at a time.

### 3.5 CFG → PDA (top-down construction)

Three states: `q0` (start), `q1` (work), `q2` (accept).

| Transition | Effect |
|------------|--------|
| `q0 --ε, Z / [S, Z]--> q1` | initial push: pop the bottom marker, push start symbol on top of `Z`. |
| `q1 --ε, A / α--> q1` for each rule `A → α` | replace the nonterminal `A` on top with the body `α`, with the leftmost symbol on top. |
| `q1 --a, a / ε--> q1` for each terminal `a` | match a terminal: consume the input character and pop. |
| `q1 --ε, Z / [Z]--> q2` | accept: input fully consumed and only `Z` left. |

**Push convention.** `push[0]` ends on top, `push[-1]` deepest. So for
`S → aSb` we write `push = [a, S, b]`, and the simulator iterates
`reversed(push)` to put `a` on top of the stack.

### 3.6 PDA simulator with LL(1)-style heuristic

```
loop:
    if stack == [Z] and remaining == "":   # accept
        emit q2 step; break
    top = stack[-1]
    if remaining:
        try terminal-match transition (top == remaining[0])
            pop, consume, emit step
            continue
    pick production whose first symbol best matches next input:
        score 4: starts with terminal == remaining[0]
        score 3: ε-prod AND remaining is empty
        score 2: starts with nonterminal
        score 1: ε-prod AND remaining non-empty
        score 0: terminal mismatch
    if no production for top: reject
    apply chosen production: pop, push reversed body, emit step
```

**Per-step output.**
```
{ "state": ..., "remaining_input": ..., "stack": [...], "applied_idx": K }
```
`applied_idx` is the position of the transition in `pda["transitions"]`.
The frontend uses it to highlight the exact edge `pe<K>` — no guessing.

**Safety cap.** `max_steps` (default 2000). On overflow the result
includes an `error` field: "Simulation exceeded N steps. The grammar may
contain left recursion or unbounded expansion."

---

## 4. Implementation decisions (and why)

| Decision | Why |
|----------|-----|
| Flask + vanilla JS, no build step | Project must be readable by students alongside the lecture; adding webpack would obscure the algorithms. |
| Dagre layout (LR direction) | Textbook diagrams flow left-to-right. `cose` (force-directed) sprawled — bigger and harder to follow. |
| Show one path, not the powerset, on the NFA tab | Real NFA semantics is parallel computation, but rendering every parallel state at once is visually chaotic. JFLAP's "fast run" is the standard pedagogical compromise. |
| Lazy trap state in subset construction | Simple regexes like `a*` should not get a dangling dead node in the diagram. |
| Hopcroft minimization always on | Matches the canonical textbook DFA. The cost (`O(|Q|·|Σ|·log|Q|)`) is negligible for classroom-size automata. |
| `applied_idx` per simulator step | Eliminates frontend heuristics that could light up the wrong self-loop edge on `q1`. |
| Step viewer scroll-capped + auto-scroll | Long traces (10+ steps is normal) shouldn't push the diagram off-screen. |
| Many epsilon synonyms | Different textbooks use `ε`, `λ`, `null`. Accepting all of them removes friction. |
| `+` as union (not Kleene-plus) | Algebraic notation matches Hopcroft-Ullman; supporting both meanings would create an unsolvable ambiguity. |
| 3-state PDA (q0, q1, q2) | Makes the *initial push* a visible animation step instead of an implicit setup. |
| Bottom marker `Z`, final-state acceptance | Simpler to teach than empty-stack acceptance. The accept transition keeps `Z` on the stack so the diagram never empties — easier to see "we're done". |

---

## 5. Sample defense questions (with full answers)

### Q1. Walk me through Thompson's construction on `(a+b)*abb`.

**Expected answer.**

1. Parse the regex into an AST. With our precedence (union < concat <
   star < atom):
   ```
   Concat(
     Star(Union(Symbol(a), Symbol(b))),
     Concat(Symbol(a), Concat(Symbol(b), Symbol(b)))
   )
   ```
2. Build bottom-up:
   - `Symbol(a)` → 2-state NFA `s0 --a--> s1`.
   - `Symbol(b)` → `s2 --b--> s3`.
   - `Union(...)` → fresh `s4, s5`; ε-edges `s4 → s0`, `s4 → s2`,
     `s1 → s5`, `s3 → s5`.
   - `Star(...)` → fresh `s6, s7`; ε-edges `s6 → s4`, `s6 → s7` (bypass),
     `s5 → s4` (loop), `s5 → s7` (done).
   - The trailing `abb` is built as three two-state fragments and
     concatenated with ε-edges.
3. The final NFA has 14 states and 16 transitions.

If asked: this *isn't* the minimum because Thompson's construction
inserts ε-edges aggressively. Minimization happens later, on the DFA.

### Q2. Why does the DFA for `(a+b)*abb` have exactly 4 states?

**Expected answer.**

Conceptually the DFA tracks "how much of the suffix `abb` have we just
seen". Four cases:

- **q0:** none of it (just saw something that isn't `a`, or just started).
- **q1:** the last character was `a` — could be the start of `abb`.
- **q2:** the last two characters were `ab` — need one more `b`.
- **q3:** the last three characters were `abb` — accepting.

Every other state the raw subset construction produces collapses into one
of these four under Hopcroft minimization. The trap (empty subset) is
unreachable in a complete DFA for this language because every input
character is in `{a, b}`, which the regex always handles.

### Q3. Explain `applied_idx` and why the frontend needs it.

**Expected answer.**

The PDA in the 3-state construction has many self-loops on `q1` — one for
each production and one for each terminal. From `(from, to, input,
stack_top)` alone, multiple transitions can match: `S → aS` and `S → ε`
both look like `(q1, q1, '', S)`. If the frontend tries to guess which
edge fired based on the step's stack change, it can get it wrong, or
light up multiple edges at once (visually noisy).

So the simulator records the index of the transition it applied — that
index is `applied_idx`. The frontend looks up the edge by id `pe<idx>`
because the edges are built in the same order as `pda["transitions"]`.
One transition fires → one edge gets `marching ants`. Deterministic.

### Q4. The grammar `S → aS | bS | ε` accepts `aa`. Trace the PDA.

**Expected answer.** Using our push convention (`push[0]` = top):

| Step | State | Remaining | Stack (bottom..top) | Transition |
|------|-------|-----------|---------------------|------------|
| 0 | q0 | aa | `[Z]` | (initial) |
| 1 | q1 | aa | `[Z, S]` | q0→q1: pop Z, push [S, Z] |
| 2 | q1 | aa | `[Z, S, a]` | S → aS: push [a, S] |
| 3 | q1 | a | `[Z, S]` | match `a` |
| 4 | q1 | a | `[Z, S, a]` | S → aS |
| 5 | q1 | "" | `[Z, S]` | match `a` |
| 6 | q1 | "" | `[Z]` | S → ε (pop S) |
| 7 | q2 | "" | `[Z]` | accept |

If asked which production wins at step 2: input is `a`, top is `S`. Score
`S → aS` = 4 (starts with terminal `a` matching input). Score `S → bS` =
0. Score `S → ε` = 1. `aS` wins.

### Q5. Show me a grammar your tool can't handle.

**Expected answer.** Two categories:

- **Left-recursive:** `S → Sa | a`. Top-down LL simulation can't handle
  left recursion. The simulator picks `S → Sa` (score 2, nonterminal-
  first) before `S → a` (score 4, terminal match) — actually wait, with
  the heuristic `S → a` would win at score 4 because `a` matches. Let me
  reconsider… If input is `aa`: pick `S → a`, match `a`, stack becomes
  `[Z]`, remaining `a` — reject. The right move would have been `S → Sa`.
  No way for a deterministic simulator to know that without backtracking.

- **Genuinely ambiguous:** `S → SS | (S) | ε`. The heuristic prefers
  `(S)` (terminal `(` matches `(`), but if the input has a `)` to match,
  it needs `ε` to pop `S` — without lookahead it picks `SS` (score 2)
  and loops until the step cap fires.

In both cases the safety cap returns an `error` line. The fix is
**grammar transformation** (left-recursion removal, left-factoring),
which is out of scope for this educational tool.

### Q6. Why is `+` allowed as union when programming regex uses it for "one or more"?

**Expected answer.** Two reasons:

1. **Source material.** Hopcroft-Ullman's *Introduction to Automata
   Theory* uses `+` for union, e.g. `L₁ + L₂`. Our students see this
   notation in lectures; supporting it removes friction when copying
   examples from the textbook.
2. **No collision risk in our grammar.** Our regex parser doesn't support
   the programming-style Kleene-plus *and* the algebraic union with the
   same symbol — that would be ambiguous. We picked one meaning and
   documented it. Kleene star `*` already covers the "zero or more" case,
   and we don't expose `+`-Kleene because it can always be desugared as
   `RR*`.

### Q7. Is your NFA simulation correct?

**Expected answer.** Yes, with a caveat: it shows *one* accepting path,
not the parallel semantics. Correctness:

- The BFS over configurations explores every reachable
  `(state, input_position)` pair.
- If any accepting configuration `(accept_state, len(input))` is
  reachable, BFS will find it.
- The simulator returns `valid = True` iff such a configuration exists —
  i.e., iff the string is in `L(NFA)`.

For visualization we pick one accepting path (the shortest in number of
transitions, since BFS); if the string is rejected, we show the path
that consumed the most input so the student sees how far the machine got
before getting stuck. This matches JFLAP's "fast run" feature in their
manual.

### Q8. What if the user's regex is invalid?

**Expected answer.** The parser raises `SyntaxError`. The Flask endpoint
catches every exception and returns `{"error": "..."}` with HTTP 400.
The frontend prints that error into the step viewer rather than crashing.
Invalid CFG lines (without `->`) are simply skipped during tokenization;
a truly empty grammar returns a trivial PDA that accepts only the empty
string.

### Q9. Walk through the stack panel during a CFG run.

**Expected answer.** The stack is rendered with top-of-stack at the
visual top. The box with the blue border highlights the current top.
When a push happens, the new top box flashes green for half a second;
when a pop happens, the box that was popped flashes red on its way out.
The bottom marker `Z` always lives at the bottom.

This corresponds 1:1 to the simulator's `stack` array: `stack[-1]` is the
top, `stack[0]` is `Z`. The CSS uses `flex-direction: column` and the JS
reverses the array so the top is the first child of the panel.

---

## 6. Glossary

- **Accepting state / final state.** A state in `F`. Reaching it with the
  input consumed means the string is in the language.
- **Active set.** In NFA simulation: the set of states the machine could
  be in at the current step. Our simulator shows only one active state at
  a time; the full active set is computed internally by BFS but not
  displayed.
- **`applied_idx`.** Index into `pda["transitions"]` of the transition
  that fired to produce a given step. Used by the frontend for exact
  edge highlighting.
- **Bottom marker.** A distinguished stack symbol (`Z` in our PDA) used
  to detect "empty stack" without literally emptying the stack.
- **CFG.** Context-free grammar.
- **Closure (ε-closure).** Set of states reachable by ε-transitions only.
- **Configuration.** A snapshot of a machine: (state, remaining input,
  stack contents). The unit of step in our PDA simulator.
- **DFA.** Deterministic finite automaton.
- **Dagre.** A layered DAG layout algorithm. The cytoscape-dagre
  extension uses it to draw left-to-right state machines.
- **Hopcroft minimization.** Partition-refinement algorithm that produces
  the unique smallest DFA equivalent to a given DFA.
- **LL(1).** A class of grammars parseable top-down with one symbol of
  lookahead. Our simulator approximates this with a per-production score.
- **Minimal DFA.** The unique (up to renaming) smallest DFA that accepts
  a given regular language.
- **NFA.** Nondeterministic finite automaton.
- **PDA.** Pushdown automaton.
- **Powerset construction / subset construction.** Algorithm that turns
  an NFA into a DFA by making DFA states correspond to sets of NFA
  states.
- **Production.** A grammar rule `A → α`. The body `α` can contain
  terminals, nonterminals, or be empty (ε-production).
- **Push convention.** Ours: `push[0]` is the new top of the stack; the
  simulator iterates `reversed(push)` and `append`s, so `push[0]` ends up
  at `stack[-1]`.
- **Self-loop.** An edge from a state to itself. The PDA has many on `q1`
  because productions and terminal matches don't change the state.
- **Thompson's construction.** Standard recursive translation from
  regex AST to NFA fragments.
- **Trap state / sink.** A non-accepting state with self-loops on every
  input. Catches "we already know the string is rejected."
- **Worklist BFS.** A common idiom in both subset construction and
  Hopcroft minimization: maintain a queue of items still to process,
  repeatedly pop and refine until the queue is empty.

---

*See also:
[`paper.md`](./paper.md) for the academic write-up,
[`user_manual.md`](./user_manual.md) for click-by-click usage,
[`presentation_guide.md`](./presentation_guide.md) for the slide outline,
[`algorithms.md`](./algorithms.md) for terse algorithm reference.*
