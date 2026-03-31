# Algorithms

This document explains the algorithms implemented in this project: Thompson's
Construction (Regex → NFA), Subset Construction (NFA → DFA), CFG → PDA
conversion (top-down replacement), and PDA simulation (deterministic LL-style).
For each algorithm the file explains what the algorithm does, a step-by-step
outline, a short worked example, and why it was chosen for this school project.

---

## Thompson's Construction (Regex → NFA)

What it is
: A constructive algorithm that converts a regular expression into an
  equivalent nondeterministic finite automaton (NFA) using small fragment
  templates and combining them with epsilon transitions.

How it works (step-by-step)
: 1. Convert the infix regular expression to postfix (Reverse Polish Notation)
  to handle operator precedence (alternation `|`, concatenation, Kleene `*`).
  2. Evaluate the postfix expression with a stack of NFA fragments.
  3. When encountering an operand (symbol) push a two-state NFA for that
     symbol (start -> symbol -> accept).
  4. On concatenation, fuse the final state of the first fragment with the
     start of the second via an epsilon transition.
  5. On union (`|`), create a new start and final state with epsilon links to
     both fragments and from their finals to the new final.
  6. On Kleene star (`*`), create new start and final states and add epsilon
     loops that allow repetition and acceptance of the empty string.

Worked example
: Regex: `(a|b)*abb`
  - Tokenize and convert to postfix: e.g. `ab|*a.b.b.` (explicit concatenation)
  - Build base NFA fragments for `a` and `b`, apply union, Kleene, and
    concatenations accordingly. The final NFA has epsilon transitions that
    implement alternation and repetition.

Why chosen
: Thompson's construction is simple to teach, straightforward to
  implement, and it directly exposes epsilon-transitions and NFA structure,
  which makes it ideal for visualization in a school project.

---

## Subset Construction (NFA → DFA)

What it is
: A deterministic construction that converts an NFA into an equivalent
  deterministic finite automaton (DFA) by treating sets of NFA states as
  single DFA states (the "powerset").

How it works (step-by-step)
: 1. Compute the epsilon-closure of the NFA start state (all states reachable
  by epsilon transitions). This is the DFA start state.
  2. For each unprocessed DFA state (a set of NFA states), and for each input
  symbol in the NFA alphabet (excluding epsilon), compute the set of NFA
  states reachable by taking that symbol from any member and then taking the
  epsilon-closure of the result.
  3. Each distinct set encountered becomes a new DFA state. Record transitions
  from the source DFA state to the target DFA state on the symbol.
  4. If any DFA state contains the NFA final state, mark that DFA state as
  accepting.
  5. Optionally add a sink (dead) state to make the DFA total (one transition
  defined for every symbol in every state).

Worked example
: Starting from an NFA for `(a|b)*abb`, take the epsilon-closure of start,
  compute transitions on `a`, `b`, and iteratively discover all unique sets
  of NFA states. Each discovered set becomes a DFA node.

Why chosen
: Subset construction produces a fully deterministic machine and is the
  canonical algorithm for converting NFAs into DFAs. It lends itself to a
  step-by-step transition table representation that is easy to show and
  animate.

---

## CFG → PDA (Top-Down Replacement)

What it is
: A simple method to obtain a pushdown automaton (PDA) that simulates a
  top-down derivation (LL-style) from a given CFG by replacing nonterminals
  on the stack with the right-hand sides of productions and matching terminals
  with input characters.

How it works (step-by-step)
: 1. Start with a bottom marker `Z` on the stack; push the grammar start symbol
  above it using an initial epsilon transition.
  2. For each production `A -> α`, add an epsilon transition that replaces `A`
  on the stack with the sequence `α` (push `α` onto the stack, where an empty
  `α` models epsilon/`ε`).
  3. For each terminal `a` that appears in the grammar, add a transition that
  consumes `a` from the input when the top of the stack is also `a` (pop+consume).
  4. Accept when the input is entirely consumed and the stack is reduced to
  the bottom marker `Z` (an epsilon transition moves to an accept state).

Worked example
: For grammar `S -> a S b | ε` and input `aabb` the PDA will repeatedly
  expand `S` to `a S b`, match `a` with input, continue, and eventually match
  the `b` symbols while unwinding the stack.

Why chosen
: This top-down PDA is simple to implement and visualize for students. It
  clearly demonstrates the role of the stack and how productions expand
  nonterminals. While it does not attempt full LL(1) parsing table construction
  (which is out of scope), it is sufficient for small classroom grammars.

---

## PDA Simulation (Deterministic LL-style)

What it is
: A deterministic simulator that executes the PDA step-by-step and records
  each configuration (current state, remaining input, stack contents) for the
  frontend to animate.

How it works (step-by-step)
: 1. Apply the initial push that places the start symbol on top of `Z`.
  2. Repeatedly do one of the following until acceptance or failure:
     - If the top of the stack matches the next input character and there is a
       matching consume transition, pop and consume the character.
     - Otherwise, if the top is a nonterminal and there is at least one
       production for it, apply the first production (deterministic choice):
       pop the nonterminal and push the production body.
     - If none apply, the input is rejected.
  3. Accept when the stack is `['Z']` and the input has been fully consumed.

Why chosen
: Deterministic, step-recording simulation makes it straightforward to
  animate stack changes and to present a clear sequence of configurations to
  students, which is ideal for teaching and grading.

---

## Notes on correctness and limits

- The implementations are intentionally straightforward and designed for
  clarity rather than extreme performance. They are appropriate for typical
  homework examples and classroom demonstration grammars/regexes.
- The CFG→PDA approach uses a deterministic first-production policy to avoid
  ambiguous branching in the simulation. Students should provide grammars
  that are unambiguous or LL-friendly when using the simulator.

