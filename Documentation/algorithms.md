# Algorithms

This document explains the algorithms implemented in this project:

1. Thompson's Construction (Regex -> NFA)
2. Subset Construction with Hopcroft Minimization (NFA -> minimal DFA)
3. CFG -> PDA conversion (top-down / LL-style)
4. PDA Simulation (deterministic with an LL(1)-style production heuristic)

## Notation cheat-sheet

The parsers accept a few synonyms so students can use whichever notation
their textbook prefers (algebraic, programming-regex, or hand-written).

**Regex page** (Thompson's construction):
| meaning       | accepted forms          | example          |
|---------------|-------------------------|------------------|
| union         | `\|`, `U`, `+`          | `a+b` = `a\|b`   |
| concatenation | (juxtaposition)         | `abc`            |
| Kleene star   | `*`                     | `a*`             |
| epsilon       | `ε`, `E`                | `(a+ε)b`         |

`+` is the algebraic-union notation from Hopcroft-Ullman (not the "one or
more" Kleene-plus from programming regex flavors — that operator isn't
supported).

**CFG page** (top-down PDA):
| meaning   | accepted forms                                                |
|-----------|---------------------------------------------------------------|
| arrow     | `->`, `→`, `⇒`                                                |
| alt       | `\|`                                                          |
| epsilon   | `ε`, `λ`, `Λ`, `Ε`, `^`, `epsilon`, `lambda`, `null`, `nil`, `eps`, `n`, (empty alt) |

Single-letter `n` is recognized as epsilon only when it's the ENTIRE
alternative (so `S -> n` means `S -> ε`, but inside `S -> an` the `n` stays a
terminal). Avoid `n` as a standalone terminal name if you also use it as the
null shortcut elsewhere in the same grammar.

Each section explains what the algorithm does, walks through it step by step,
shows a worked example, and notes the design choices behind the school-project
implementation.

---

## Thompson's Construction (Regex -> NFA)

**What it is.** A constructive algorithm that converts a regular expression
into an equivalent nondeterministic finite automaton (NFA) using small
fragment templates connected by epsilon transitions.

**Step-by-step.**

1. Parse the regex with a recursive-descent parser, producing an AST that
   respects precedence: `union (|)` < `concatenation` < `Kleene star (*)`
   < `atom`. Atoms are single alphanumeric characters, `ε` (or `E`), or a
   parenthesized subexpression.
2. Translate the AST bottom-up:
   - **Symbol `a`**: two fresh states with a single `a`-edge.
   - **Epsilon**: two fresh states with a single `ε`-edge.
   - **Concatenation**: glue `left.accept` to `right.start` with an `ε`-edge.
   - **Union**: new start branches to both children's starts; both children's
     accepts converge into a new accept state.
   - **Kleene star**: new start with a bypass edge (matches empty) plus an
     entry edge; child accept loops back to child start and to the new accept.

**Worked example.** `(a|b)*abb` produces an NFA of 14 states and 16 edges
(including epsilon edges that wire up the union and the star). Each fragment
has exactly one start and one accept, which keeps the construction uniform.

**Why this construction.** The fragment shape is simple to teach, the
epsilon structure is directly visible in the diagram, and it composes
recursively from the AST — the implementation mirrors the algorithm
description almost line for line.

---

## Subset Construction + Hopcroft Minimization (NFA -> DFA)

**What it is.** Subset (powerset) construction turns an NFA into an
equivalent DFA by treating sets of NFA states as single DFA states. We then
run Hopcroft's partition-refinement algorithm to produce the minimal
equivalent DFA so the rendered diagram is as small as possible.

**Step-by-step.**

1. Compute the epsilon-closure of the NFA start state — this is the first
   DFA state.
2. Worklist BFS: for each unprocessed DFA state `T` and each input symbol
   `a`, compute `epsilon_closure(move(T, a))`. Each new subset becomes a new
   DFA state; the transition is `T --a--> U`.
3. **Lazy trap state.** Only if at least one transition above is undefined
   (target set is empty) do we add the empty-set sink. Simple regexes like
   `a*` produce a single-state DFA with no dangling trap node.
4. Mark every DFA state that contains the NFA accept as an accepting DFA
   state.
5. **Hopcroft minimization.** Partition the DFA states into accepting and
   non-accepting blocks. Repeatedly split a block whenever some symbol takes
   different members of the block to different blocks. The resulting blocks
   are the states of the minimal DFA. Final ids are assigned in BFS order
   from the new start, dropping any unreachable blocks.

**Worked example.** The raw subset construction for `(a|b)*abb` produces 5
states (4 reachable + 1 trap). Hopcroft minimization recognizes that the
trap and the initial state are not equivalent — keeping 4 states, which is
the canonical minimal DFA for this language.

**Why this construction.** Subset construction is the canonical NFA->DFA
algorithm; Hopcroft minimization gives a clean, smaller diagram that's much
easier for students to read. Complexity: subset construction is exponential
in the worst case but tiny for classroom regexes; Hopcroft is
`O(|Q| * |Sigma| * log |Q|)`.

---

## Accepted epsilon notations

The CFG tokenizer treats any of these as the empty production (epsilon) so
students can use whichever convention their course or textbook prefers:

- Greek characters: `ε`, `λ`, `Λ`, `Ε`
- Case-insensitive words: `epsilon`, `lambda`, `null`, `nil`, `eps`
- An empty alternative after `|`, e.g. `S -> aSb |` treats the right side
  of the `|` as epsilon.

So `S -> aS | bS | null` and `S -> aS | bS | ε` produce the same PDA.

---

## CFG -> PDA (Top-Down / LL-style)

**What it is.** Converts a context-free grammar into a pushdown automaton
whose runs mimic a top-down derivation. Nonterminals on the stack are
replaced by production bodies; terminals on the stack are matched and popped
against input characters.

**PDA shape.** Three states `q0`, `q1`, `q2`. `q0` is the start, `q2` is the
sole accept state. All work happens in `q1`.

**Push convention (important).** In every transition's `push` list, `push[0]`
is the symbol that ends up on the TOP of the stack after the push, and
`push[-1]` ends up deepest. This matches how a production body reads
naturally: for `S -> aSb` we store `push = ["a", "S", "b"]`, and after the
push `a` is on top so the simulator can match it against the next input
character. The simulator implements this by iterating `reversed(push)` when
applying a transition.

**Transitions created.**

1. **Initial.** `q0 --epsilon, Z/[start, Z]--> q1` — pop the bottom marker
   `Z` and push `[start_symbol, Z]`, so the start symbol is now on top.
2. **Productions.** For each rule `A -> alpha`, add
   `q1 --epsilon, A/alpha--> q1`. An epsilon-production becomes
   `q1 --epsilon, A/[] --> q1` (just pop A).
3. **Terminal matches.** For each terminal `a` appearing in the grammar,
   add `q1 --a, a/[]--> q1` — consume the input character and pop the
   matching symbol off the stack.
4. **Accept.** `q1 --epsilon, Z/[Z]--> q2` — when only `Z` is on the stack
   and the input has been consumed.

**Worked example.** Grammar `S -> aSb | epsilon` on input `aabb`:

```
step  state  remaining  stack (bottom .. top)
 0    q1     aabb       [Z, S]
 1    q1     aabb       [Z, b, S, a]      -- apply S -> aSb
 2    q1     abb        [Z, b, S]         -- match 'a'
 3    q1     abb        [Z, b, b, S, a]   -- apply S -> aSb
 4    q1     bb         [Z, b, b, S]      -- match 'a'
 5    q1     bb         [Z, b, b]         -- apply S -> epsilon (pop S)
 6    q1     b          [Z, b]            -- match 'b'
 7    q1     ''         [Z]               -- match 'b'
 8    q2     ''         [Z]               -- accept
```

Notice the stack is written bottom-to-top: the last symbol in each list is
the top, which is what `stack[-1]` reads in the simulator.

**Why this construction.** Top-down PDAs make the connection between
productions and stack operations very concrete, which is the whole pedagogic
point. We do not try to construct an LL(1) parse table — that's out of scope.

---

## PDA Simulation (Deterministic, LL(1)-style)

**What it is.** A step-recording simulator that runs the PDA produced
above. Each step is one configuration `(state, remaining_input, stack)` so
the frontend can animate the trace.

**The hard part: which production to apply when the top of the stack is a
nonterminal with multiple rules.** A naive "always pick the first one"
strategy rejects valid strings (e.g. picks `S -> aSb` when the input has no
more `a`s and `S -> epsilon` was the right move). The simulator uses a
lightweight LL(1)-style score:

| Score | Situation |
|------:|-----------|
|  4    | Production starts with a terminal that matches the next input char (a definite win for this step). |
|  3    | Production is epsilon and the input is already empty (only this can lead to acceptance). |
|  2    | Production starts with a nonterminal (deferred — we'll find out after expansion). |
|  1    | Production is epsilon and input still remains (might help, but try anything else first). |
|  0    | Production starts with a terminal that does NOT match the next input char (will fail). |

The highest-scoring production wins; ties keep the order the user wrote.

**Main loop.**

1. If the stack is `[Z]` and the input is empty -> jump to `q2` and accept.
2. If the top of the stack equals the next input character and a matching
   transition exists, pop the stack and consume that character.
3. Otherwise apply the best-scoring production for the top nonterminal.
4. If neither move applies, reject.

**Step limit.** The simulator runs at most `max_steps` iterations (default
2000). If that limit is hit, the result includes an `error` field explaining
that the grammar may have left recursion or unbounded expansion. This
distinguishes "rejected by the grammar" from "ran out of steps".

---

## Correctness, limits, and what to expect

- **Regex pipeline** (`thompson` + `subset_construction`): correct on all
  supported regex forms. The DFA is minimal, so it matches the canonical
  textbook diagram for examples like `(a|b)*abb` (4 states).

- **CFG pipeline** (`cfg_to_pda` + `string_checker_pda`): correct for
  LL(1)-friendly grammars. The deterministic simulator with the lookahead
  heuristic handles the canonical patterns:
    - `S -> aSb | epsilon`              (a^n b^n)
    - `S -> aA; A -> bA | epsilon`      (a b*)
    - `S -> AB; A -> a; B -> b`         (concatenation across nonterminals)
    - `S -> (S)S | epsilon`             (balanced parens, LL(1) form)
  It will NOT solve genuinely ambiguous grammars such as `S -> SS | (S) | epsilon`
  or grammars with left recursion (`S -> Sa | a`) — those need either
  backtracking or grammar transformations (left-factoring, left-recursion
  removal), both out of scope for this project. Left recursion that can
  expand without consuming input will trigger the `max_steps` error.
