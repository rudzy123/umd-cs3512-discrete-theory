# Regular languages and deterministic finite automata

An **alphabet** is a finite set of symbols. Here each symbol is one
character. A **string** is a finite sequence of those symbols. The **empty
string** `ε` has length 0 and is a string over every alphabet. A
**language** is a set of strings.

A language is **regular** when some deterministic finite automaton accepts
exactly its strings. The even-parity language below is regular because the
automaton is written down and proved correct. The language
`{ 0ⁿ1ⁿ | n ≥ 0 }` is not regular because the argument further down shows
that no such automaton exists.

## The five parts of a DFA

A deterministic finite automaton consists of:

1. a finite set of **states** `Q`,
2. a finite **alphabet** `Σ`,
3. a **transition function** `δ` that assigns exactly one next state to
   each pair `(state, symbol)`,
4. a **start state** `q0 ∈ Q`,
5. a set `F ⊆ Q` of **accepting states**.

`DFA.from_table` takes those five pieces. The transition function must be
total. A missing pair is a construction error, not a rejected string. The
machine is deterministic because a mapping stores only one target for each
pair.

On an input string the machine starts at `q0` and reads one character at a
time, replacing the current state `q` by `δ(q, symbol)`. `run` returns the
state at the end. `accepts` returns whether that state is in `F`. The
empty string is accepted exactly when the start state is accepting,
because no symbol is read.

A character outside `Σ` is not an input of this machine. `accepts` raises
`InvalidSymbolError`. A string that uses only the alphabet and ends outside
`F` is **rejected**, which is the ordinary result `False`. Those are
different events. A total transition function is what makes the second
event possible: the machine always moves, and acceptance is decided only
at the end.

## Worked example: even number of ones

Let `Σ = {0, 1}` and let `L` be the set of strings with an even number of
`1` symbols. Zero is even, so `ε` and `"0"` and `"00"` are in `L`. `"1"`,
`"10"`, and `"111"` are not. `"11"` and `"101"` are.

Two states are enough, because the only fact the rest of the string needs
is the parity so far.

```text
states:     even, odd
alphabet:   0, 1
start:      even
accepting:  {even}

even --0--> even      odd --0--> odd
even --1--> odd       odd --1--> even
```

`even_ones_dfa()` builds that table.

### A trace

Read `"110"`:

```text
even --1--> odd --1--> even --0--> even
```

The run ends in `even`, so `"110"` is accepted. Two `1` symbols is even.

Read `"10"`:

```text
even --1--> odd --0--> odd
```

The run ends in `odd`, so `"10"` is rejected. One `1` is odd.

### Proof that the automaton decides L

**Claim.** After reading a binary string `w`, the state is `even` if `w`
has an even number of `1` symbols, and `odd` otherwise.

**Proof by induction on `n = |w|`.** This is the same induction shape as
in the [proof notes](proof-techniques.md), with string length as the
induction variable.

Base `n = 0`. The string is `ε`. The machine is still in `even`. The
number of `1` symbols is 0, which is even.

Inductive hypothesis. Fix `n ≥ 0` and assume the claim for every binary
string of length `n`. (Using it for one arbitrary `w` of length `n` is
enough.) Let `w` be such a string, and let `a` be `0` or `1`. Write
`w' = w` followed by `a`.

- If `a = 0`, the number of `1` symbols is unchanged. Both states have a
  `0`-transition to themselves, so the state does not change either. The
  claim remains true.
- If `a = 1`, the number of `1` symbols changes parity. Both states have a
  `1`-transition to the other state, so the recorded parity flips too.

By induction the claim holds for every finite binary string. The machine
accepts exactly when the final state is `even`, which is exactly when the
number of `1` symbols is even. Therefore it recognizes `L`, and `L` is
regular.

The tests that run every binary string of length at most 6 check the
claim on a finite sample. The induction covers the rest. Both are useful,
and only the induction is a proof for every string.

### Complement

Swap accepting and non-accepting states and leave the transitions alone.
The new machine accepts exactly the strings over the same alphabet that
the old machine rejects. `complement` does that. The complement of the
even-ones machine is the odd-ones machine: `"1"` is accepted and `ε` is
rejected. Doing it twice restores the original accepting set, just as
`~~P` is equivalent to `P`.

Symbols outside `{0, 1}` are still errors. Complement does not enlarge
the alphabet.

Closure of the regular languages under union and intersection uses a
product of state sets. That construction is not implemented here. The
complement construction is the one the code carries, because it is a
one-line change to `F` and it is easy to prove: a run ends in `F` exactly
when it does not end in `Q − F`.

## Worked example: identifiers

An identifier, for this refresher, is a string that matches

```text
[A-Za-z_][A-Za-z0-9_]*
```

A letter or an underscore, then any number of letters, digits, or
underscores. The empty string does not match. A string that starts with a
digit does not match. The language does not reserve keywords: `if` matches
the shape, so the automaton accepts it. Keyword filtering is a later pass.

The alphabet is the 26 letters of each case, the 10 digits, and `_`.
Three states make the transition function total:

```text
start   the state before any character; not accepting
body    a well-formed prefix; the only accepting state
sink    a digit was read first; not accepting, and it stays there
```

From `start`, a letter or `_` goes to `body`, and a digit goes to `sink`.
From `body`, every alphabet symbol stays in `body`. From `sink`, every
alphabet symbol stays in `sink`. `identifier_dfa()` builds the 189
transitions that this description names.

### Traces

`"a1"`:

```text
start --a--> body --1--> body
```

Accepted.

`"1a"`:

```text
start --1--> sink --a--> sink
```

Rejected. Both characters are in the alphabet. Rejection is `False`, not
an exception. The sink exists so that a bad but legal symbol still has a
transition.

`""` stays in `start` and is rejected.

`"a-b"` raises `InvalidSymbolError` when `-` is read. The hyphen is not in
the alphabet, so there is no transition to consult. That is the difference
between "a string the language excludes" and "a string the machine does
not read".

## The transition graph

Forget the labels for a moment and the states are vertices. Each
transition is a directed edge. A run is a walk in that graph. Acceptance
is ending in a vertex that belongs to `F`. The even-ones graph is a
2-cycle on the symbol `1`, with a loop labeled `0` at each state. The
graph algorithms in [graph theory](graph-theory.md) do not store edge
labels, so the automaton keeps its own transition table. The vocabulary
is the same: state, move, walk, cycle.

## Limits of finite-state machines

A DFA has finitely many states, so it has finitely many possible memories.
Any information it keeps about the input so far must be one of those
states. It can remember parity. It cannot remember an arbitrary integer.

### Worked example: equal blocks of zeros and ones

Let `M = { 0ⁿ1ⁿ | n ≥ 0 }`. So `ε`, `01`, `0011`, and `000111` are in `M`,
while `0`, `1`, `001`, and `011` are not. `M` is not regular.

**Proof.** Suppose some DFA with state set `Q` recognizes `M`. Let
`k = |Q|`. Consider the `k + 1` prefixes

```text
ε, 0, 00, ..., 0ᵏ.
```

By the pigeonhole principle there are only `k` states for `k + 1`
strings, so two prefixes `0ᵃ` and `0ᵇ` with `0 ≤ a < b ≤ k` end in the
same state `q`.

The string `0ᵃ1ᵃ` is in `M`, so from `q` the continuation `1ᵃ` ends in an
accepting state. The string `0ᵇ1ᵃ` reaches that same `q` after `0ᵇ`, then
reads the same continuation `1ᵃ`, and therefore ends in the same accepting
state. The machine accepts `0ᵇ1ᵃ`. But `b ≠ a`, so `0ᵇ1ᵃ` is not in `M`.

That contradiction means no such DFA exists. `M` is not regular.

The same counting obstruction applies to balanced parentheses. A machine
with `k` states, reading `k + 1` different depths of `(`, must confuse two
depths, and the number of closing parentheses that finishes one of them
fails the other. Unbounded nesting is unbounded memory.

Even parity does not need that memory. The invariant above stores one bit.
Adding a third state cannot make the two-state even-ones machine "more
correct"; two states already decide the language. Extra states become
necessary only when the language distinguishes more than two histories,
and they become insufficient exactly when the number of histories that
must be told apart is unbounded, as with the exponent `n` in `0ⁿ1ⁿ`.

Finite-state machines also cannot, for the same reason, decide
`{ ww | w is a binary string }` or the set of strings whose parentheses
are balanced to every depth. Those are standard next examples. The proof
pattern is the one given for `M`: force two different histories into one
state, then append a continuation that one history deserves and the other
does not.
