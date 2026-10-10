# Propositions, connectives, and quantifiers

A **proposition** is a statement that is true or false. "2 is even" is a
proposition, and it is true. "This sentence is false" is not a proposition
we can use: it does not sit cleanly in {true, false}. A **propositional
variable** stands for a proposition whose internal meaning we ignore. `P`
may be true or false. The formulas in `umd_discrete.logic` are built from
those variables.

A **predicate** is a statement with a free variable. "x is even" is not yet
true or false. It becomes a proposition when `x` is replaced by a value, or
when a quantifier binds `x`. Write `E(x)` for "x is even". Then `E(2)` is
the true proposition "2 is even", and `E(3)` is false.

The library decides propositional formulas. It does not search over the
values of a predicate. The quantifier section below is the pencil-and-paper
half of that distinction.

## Connectives

The five connectives are functions of truth values.

| Formula | True exactly when |
| --- | --- |
| `~A` | `A` is false |
| `A & B` | both are true |
| `A \| B` | at least one is true (inclusive or) |
| `A -> B` | `A` is false or `B` is true |
| `A <-> B` | `A` and `B` have the same value |

Python's `~`, `&`, and `|` build negation, conjunction, and disjunction.
Implication and the biconditional are methods, because `->` is not an
operator we can overload here:

```python
from umd_discrete import Variable

p = Variable("P")
q = Variable("Q")
formula = p.implies(q)  # P -> Q
same = (~p) | q  # same truth function
both = p.iff(q)  # P <-> Q
```

`&` binds tighter than `|`, and `~` binds tighter than both. So `p | q & r`
is `p | (q & r)`, and `~p & q` is `(~p) & q`. Parentheses, or the
constructors `And`, `Or`, `Not`, `Implies`, and `Iff`, make the tree
obvious.

### Worked example: the implication table

`P -> Q` is the claim "if P, then Q". The only way it fails is for the
promise to be broken: `P` true and `Q` false. `render_truth_table` prints
the four rows with `P` as the major bit:

```text
P Q | (P -> Q)
F F | T
F T | T
T F | F
T T | T
```

Read the third row as a counterexample to the implication, and the other
three rows as cases where the implication holds. A false premise yields a
true implication. That is why both rows with `P = F` are true.

The same four rows for the other connectives:

```text
P Q | ~P | P & Q | P | Q | P <-> Q
F F | T  | F     | F    | T
F T | T  | F     | T    | F
T F | F  | F     | T    | F
T T | F  | T     | T    | T
```

`P | Q` on the middle-right is inclusive or, so the row `T T` is true.

## Truth tables as a decision procedure

A formula with `n` variables has `2**n` assignments. `truth_table` builds
all of them. That finite exhaustion decides four questions:

- A **tautology** is true in every row. `P | ~P` is a tautology.
- A **contradiction** is false in every row. `P & ~P` is a contradiction.
- A formula is **satisfiable** when at least one row is true. Every
  tautology is satisfiable. A contradiction is not.
- Two formulas are **equivalent** when they agree on every assignment of
  the variables that appear in either one.

### Worked example: three classifications

`P | ~P` has rows `T, T`. It is a tautology, and it is satisfiable.

`P & ~P` has rows `F, F`. It is a contradiction. `satisfying_assignments`
returns the empty tuple.

`P & Q` has one true row, the assignment `P = T`, `Q = T`. It is
satisfiable. It is not a tautology, and it is not a contradiction. That
single true row is a witness: it is enough to show satisfiability, and the
three false rows are enough to show that it is not a tautology.

`==` does not mean equivalence. `P | Q` and `Q | P` are equivalent, and
they are different trees. Use `equivalent` for the semantic relation.

Constants need no variables, so their table has one empty assignment.
`TRUE` renders as `T | T`. A formula that ignores an extra variable is
still comparable: `P | ~P` is equivalent to `TRUE` because both sides are
true whether `P` is true or false.

The search stops after `MAX_TRUTH_TABLE_VARIABLES` (12). Forty-eight
variables would be `2**48` rows. The procedure is correct and exponential.
That limit is computational, not mathematical: the definition of tautology
does not change.

## De Morgan's laws

For any formulas `A` and `B`:

```text
~(A & B)  is equivalent to  ~A | ~B
~(A | B)  is equivalent to  ~A & ~B
```

### Worked example

The two sides of the first law depend only on the truth values of `A` and
`B`. It is enough to check the four combinations. Take `A = P` and `B = Q`:

```text
P Q | ~(P & Q) | (~P | ~Q)
F F | T        | T
F T | T        | T
T F | T        | T
T T | F        | F
```

The columns agree, so `equivalent(~(p & q), ~p | ~q)` is true. The same
four-row argument works for any formulas in place of `P` and `Q`, because
a compound formula still contributes only one truth value to the
connective. That is a proof of the schema, not only of the variable case.

Read the law as a way to push negation inward. "Not both" means "at least
one is false". "Not either" means "both are false". The second reading is
the inclusive or: negating it produces a conjunction.

Two related rewrites fall out of the same method:

```text
A -> B   is equivalent to   ~A | B
A -> B   is equivalent to   ~B -> ~A
```

The second is the **contrapositive**. It is the propositional fact used in
[proof by contrapositive](proof-techniques.md). The truth table of
`P -> Q` above matches `~P | Q` row for row: the only `F` is `T F`.

## Quantifiers

Fix a domain. `∀x φ(x)` says that every element of the domain satisfies
`φ`. `∃x φ(x)` says that at least one element does. These are propositions
once the domain and the predicate are fixed.

On an empty domain, `∀x φ(x)` is vacuously true: there is no counterexample.
`∃x φ(x)` is false: there is no witness. The relation predicates in the
sets module follow the same convention. The empty relation on the empty
domain is reflexive.

### Worked example

Let the domain be `{1, 2, 3, 4}`, and let `E(x)` mean "x is even".

- `∃x E(x)` is true. A witness is `x = 2`. Another witness is `x = 4`.
  One witness is enough.
- `∀x E(x)` is false. A counterexample is `x = 1`. One counterexample is
  enough.
- `∀x (E(x) | ~E(x))` is true. Each of 1, 2, 3, and 4 makes the inside
  true, because `E(x) | ~E(x)` is a tautology in the propositional
  skeleton.
- `∃x (E(x) & ~E(x))` is false. The inside is a contradiction, so no
  witness exists.

Negation swaps the quantifiers and negates the inside:

```text
~(∀x E(x))  is equivalent to  ∃x ~E(x)
~(∃x E(x))  is equivalent to  ∀x ~E(x)
```

On this domain the first line is true on both sides: it is not the case
that every element is even, and `x = 1` is a witness that some element is
not even. The second line is false on both sides: there is an even
element, so it is not true that every element fails to be even.

A finite domain turns a quantified statement into a finite conjunction or
disjunction. `∀x E(x)` on `{1, 2, 3, 4}` is `E(1) & E(2) & E(3) & E(4)`.
That is why a finite check can decide it. The same expansion is impossible
for "every integer" as a finite conjunction. First-order validity over all
domains is undecidable: Church and Turing proved there is no algorithm
that answers yes or no, correctly and in finite time, for every first-order
sentence. This package therefore decides propositional formulas by
enumerating a truth table, and it evaluates predicates only when the caller
hands it a finite domain, as the relation and function functions do.
