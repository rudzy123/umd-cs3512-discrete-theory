# Proof techniques

A proof is a finite argument that a claim holds for every object in its
domain, from definitions and previously proved facts. An example can
support a claim or kill it. An example cannot, by itself, prove a claim
about every integer.

The [logic notes](logic.md) already contain one complete kind of proof: a
truth table that inspects every row. The techniques below are what remains
when the domain is infinite or when the statement is not propositional.

Tests in this repository play two different roles.

- `equivalent(~(p & q), ~p | ~q)` is a proof of that equivalence, because
  the function evaluates all four assignments.
- `test_sum_matches_closed_form` checks `S(n) = n(n + 1) / 2` for
  `n <= 30`. That is evidence. The induction in this note is the proof.
- `sum_first_naturals` itself follows the recurrence
  `S(n) = S(n - 1) + n`. It computes the sum defined that way. It does not,
  by running, prove the closed form.

## Direct proof

Assume the hypothesis. Apply definitions. Reach the conclusion.

### Worked example

**Theorem.** If `m` and `n` are even integers, then `m + n` is even.

**Proof.** Suppose `m` and `n` are even. By the definition of even, there
are integers `a` and `b` such that `m = 2a` and `n = 2b`. Then

```text
m + n = 2a + 2b = 2(a + b).
```

`a + b` is an integer, so `m + n` is even.

The hypothesis was used, the definition was used, and the conclusion is
the definition of even applied to `m + n`. That is the whole proof.

## Proof by contrapositive

`A -> B` is equivalent to `~B -> ~A`. The truth table in the logic notes
checks every case of that rewrite. To prove "if A, then B", it is valid to
prove "if not B, then not A" instead. Choose the direction whose hypothesis
is easier to unpack.

### Worked example

**Theorem.** Let `n` be an integer. If `n²` is even, then `n` is even.

The contrapositive is: if `n` is odd, then `n²` is odd.

**Proof of the contrapositive.** Suppose `n` is odd. Then `n = 2k + 1` for
some integer `k`.

```text
n² = (2k + 1)² = 4k² + 4k + 1 = 2(2k² + 2k) + 1.
```

`2k² + 2k` is an integer, so `n²` is odd.

The contrapositive is true, and it is equivalent to the original
implication, so the theorem is true.

The propositional skeleton `(P -> Q) <-> (~Q -> ~P)` does not mention
integers. The truth table proves the skeleton. The algebra above proves
the number-theoretic statement. Both are required, and they are not the
same argument.

## Proof by contradiction

Assume the claim is false. Derive a statement that is impossible. Conclude
that the assumption is false, so the claim is true.

Use contradiction when the negation has a useful shape, such as "there
exists a counterexample" or "this number is rational".

### Worked example

**Theorem.** `√2` is irrational.

**Proof.** Suppose, for a contradiction, that `√2` is rational. Then there
are positive integers `p` and `q` with `√2 = p / q` and `gcd(p, q) = 1`.
Squaring both sides gives `p² = 2q²`, so `p²` is even. By the previous
theorem, `p` is even. Write `p = 2k` for an integer `k`. Substitute:

```text
(2k)² = 2q²
4k² = 2q²
q² = 2k².
```

So `q²` is even, and therefore `q` is even. Then `p` and `q` share a factor
of 2, which contradicts `gcd(p, q) = 1`.

The assumption that `√2` is rational is false. Therefore `√2` is irrational.

The impossible sentence is "a fraction in lowest terms has two even
parts". The proof is finished when that sentence has been derived from the
negation. Do not add a second, unrelated contradiction.

## Mathematical induction

Induction proves a statement `S(n)` for every integer `n` at least some
base `n0`.

1. **Base.** Prove `S(n0)` directly.
2. **Inductive step.** Assume `S(k)` for an arbitrary `k >= n0`. This
   assumption is the inductive hypothesis. Prove `S(k + 1)` from it.

Then `S(n0)` is true, hence `S(n0 + 1)`, hence `S(n0 + 2)`, and so on
through every larger integer. The hypothesis is not a guess about the
final theorem. It is the assumption the step is allowed to use, and only
for that one `k`.

### Worked example

**Theorem.** For every integer `n >= 0`,

```text
S(n) = 0 + 1 + ... + n = n(n + 1) / 2.
```

`S(0)` is the empty sum, which is 0. For `n >= 1` the left side is the sum
of the first `n` positive integers. `sum_first_naturals` computes the left
side from the recurrence `S(0) = 0` and `S(n) = S(n - 1) + n`.

**Proof.**

Base `n = 0`. The empty sum is 0, and `0 * 1 / 2 = 0`.

Inductive hypothesis. Fix `k >= 0` and assume `S(k) = k(k + 1) / 2`.

Then

```text
S(k + 1) = S(k) + (k + 1)
         = k(k + 1) / 2 + (k + 1)
         = k(k + 1) / 2 + 2(k + 1) / 2
         = (k(k + 1) + 2(k + 1)) / 2
         = (k + 1)(k + 2) / 2.
```

That is the claimed formula at `n = k + 1`. By induction the formula holds
for every integer `n >= 0`.

Checking `n` from 0 through 30, which the test suite does, is consistent
with the theorem and would have caught an algebra error in a small case.
It leaves `n = 31` and every larger `n` untouched. The induction does not.

The same shape appears anywhere a definition has a base and a step.
`factorial` uses `0! = 1` and `n! = n * (n - 1)!`. `fibonacci` uses
`F(0) = 0`, `F(1) = 1`, and `F(n) = F(n - 1) + F(n - 2)`. Pascal's triangle
uses `C(n, 0) = C(n, n) = 1` and
`C(n, k) = C(n - 1, k - 1) + C(n - 1, k)`. Each of those is a recurrence.
Proving a closed form for one of them is a separate induction.

An inductive argument on the length of a string is the same technique with
a different base. The parity automaton in the
[automata notes](automata.md) is proved that way: the state invariant
holds for the empty string, and reading one more symbol preserves it.
