# Sets, relations, functions, and counting

Everything in `umd_discrete.sets` and `umd_discrete.combinatorics` is finite.
Elements must be hashable. Python collapses duplicates, and it treats
`True` and `1` as equal, so those two values cannot both belong to one set.

## Sets

A set is a collection of distinct elements. Order does not matter, and
repetition does not matter. `∈` means membership. The **empty set** `∅`
has no elements. A **singleton** has exactly one.

### Worked example: empty set and singleton

```text
power_set(())  =  { ∅ }
power_set({1}) =  { ∅, {1} }
```

`∅` is a subset of every set, including itself, so it appears in both
power sets. The singleton `{1}` contributes one further subset, itself.
`|power_set({1})| = 2 = 2**1`.

## Union, intersection, and difference

For sets `A` and `B`:

- `A ∪ B` is the set of elements in `A` or in `B`.
- `A ∩ B` is the set of elements in both.
- `A − B` is the set of elements in `A` that are not in `B`.

The code names are `union`, `intersection`, and `difference`.

### Worked example

Let `A = {1, 2, 3}` and `B = {3, 4}`.

```text
A ∪ B = {1, 2, 3, 4}
A ∩ B = {3}
A − B = {1, 2}
B − A = {4}
```

The empty set is an identity for union and a zero for intersection:

```text
A ∪ ∅ = A
A ∩ ∅ = ∅
A − ∅ = A
∅ − A = ∅
```

A singleton calculation: `{1} ∪ ∅ = {1}`, `{1} ∩ {1} = {1}`, and
`{1} − {1} = ∅`.

Symmetric difference, the elements in exactly one of the sets, is
`(A − B) ∪ (B − A)`. On the example that is `{1, 2, 4}`. It is not a
separate function in the package; it is those two operations.

## Power set

The power set `P(S)` is the set of all subsets of `S`. If `|S| = n`, then
`|P(S)| = 2**n`, because each element is either in a subset or out of it.
That is `n` independent binary choices, the multiplication principle below.

### Worked example

```text
P({1, 2}) = { ∅, {1}, {2}, {1, 2} }
```

Four subsets, and `2**2 = 4`. For `{1, 2, 3}` the same rule gives 8
subsets; listing them is the same construction with one more bit.
`power_set` refuses more than `MAX_POWER_SET_ELEMENTS` (16), since the
output doubles with every added element. The cardinality claim does not
stop at 16. `2**n` and the sum of the binomial row still agree past the
enumeration cap, which is why `combination_count` is separate from
`power_set`.

## Relations

A **relation** `R` on a domain `A` is a set of ordered pairs from `A × A`.
`(a, b) ∈ R` is also written `a R b`. The pairs must use elements of the
stated domain; a stray element is an error, not a silent extra.

On a domain `A`:

- **Reflexive:** for every `a ∈ A`, `(a, a) ∈ R`.
- **Symmetric:** if `(a, b) ∈ R`, then `(b, a) ∈ R`.
- **Antisymmetric:** if `(a, b) ∈ R` and `(b, a) ∈ R`, then `a = b`.
- **Transitive:** if `(a, b) ∈ R` and `(b, c) ∈ R`, then `(a, c) ∈ R`.

An **equivalence relation** is reflexive, symmetric, and transitive. A
**partial order** is reflexive, antisymmetric, and transitive. Symmetry and
antisymmetry together force `a R b` to imply `a = b`. The relations that
are both equivalences and partial orders are exactly the equality
relations. The empty relation on the empty domain is one of them, because
every requirement is a universal quantifier and the domain has no
elements. See the quantifier notes in [logic](logic.md).

### Worked example: an equivalence

Domain `{1, 2, 3}`.

```text
R = {(1, 1), (2, 2), (3, 3), (1, 2), (2, 1)}
```

- Reflexive: the three loops are present.
- Symmetric: `(1, 2)` is matched by `(2, 1)`, and each loop matches itself.
- Transitive: `(1, 2)` then `(2, 1)` produces `(1, 1)`, which is present.
  The same check with the pair reversed produces `(2, 2)`. Nothing relates
  `1` or `2` to `3` except through loops that stay inside `{3}`.
- Antisymmetric: `(1, 2)` and `(2, 1)` are both present and `1 ≠ 2`, so no.

`R` is an equivalence and not a partial order. Its classes are `{1, 2}`
and `{3}`: `x` and `y` are in the same class when each is related to the
other. The classes partition the domain.

Drop the loops and keep `{(1, 2), (2, 1)}`. Symmetry survives. Reflexivity
fails. Transitivity fails because `(1, 2)` and `(2, 1)` require `(1, 1)`.
One missing pair is enough to lose a property. `profile_relation` reports
all six flags together so that failure is visible at once.

### Worked example: a partial order

On `{1, 2, 3}`, let `R` be numeric `<=`:

```text
{(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)}
```

Reflexive: the diagonal is present. Antisymmetric: the only mutual pairs
are the loops, where the two coordinates are equal. Transitive:
`(1, 2)` and `(2, 3)` produce `(1, 3)`, which is in the set; every other
chain is a loop or a shorter pair already listed. Symmetric: `(1, 2)` is
in and `(2, 1)` is out, so no.

`<=` is a partial order (in fact a total order, since every pair of
elements is comparable). It is not an equivalence.

The strict chain `{(1, 2), (2, 3), (1, 3)}` is transitive and
antisymmetric, and it is not reflexive, so it is not a partial order.
Delete `(1, 3)` and transitivity fails. That single missing pair is the
whole failure.

## Functions

A **function** `f: A → B` assigns each element of the domain `A` exactly
one element of the codomain `B`. In this package the mapping is a
dictionary. Its keys are the domain unless a domain is passed explicitly,
in which case the keys must be exactly that domain. A missing key is a
partial function, and the predicates reject it. A value outside the
codomain is also rejected: it is not a function into that codomain.

- **Injective:** if `f(a) = f(a')`, then `a = a'`. Distinct inputs have
  distinct outputs.
- **Surjective:** for every `b ∈ B` there is some `a ∈ A` with `f(a) = b`.
  The image is all of the codomain.
- **Bijective:** both. A bijection is a one-to-one correspondence, and it
  has an inverse function.

On finite sets, a function from `A` to `B` is bijective exactly when it is
injective and `|A| = |B|`, or exactly when it is surjective and
`|A| = |B|`. The codomain still has to be stated. A Python dict does not
remember the codomain it was supposed to hit.

The empty function is injective. It is surjective onto `∅` and not
surjective onto a non-empty codomain. The empty function `∅ → ∅` is a
bijection.

### Worked example

Domain `{1, 2, 3}` where the map uses those keys.

```text
f = {1 ↦ a, 2 ↦ b, 3 ↦ c}    onto {a, b, c}     bijective
g = {1 ↦ a, 2 ↦ a}           onto {a}           surjective, not injective
h = {1 ↦ a}                  onto {a, b}        injective, not surjective
k = {1 ↦ a, 2 ↦ a, 3 ↦ b}    onto {a, b, c}     neither
```

`g` hits every element of `{a}`, so it is onto that codomain, and it sends
two inputs to `a`, so it is not injective. Change the codomain of `g` to
`{a, b}` and surjectivity fails, because `b` is missed. The same mapping
is a different function when the codomain changes. `h` on the singleton
domain `{1}` onto the singleton codomain `{a}` is a bijection; the extra
codomain element `b` is what destroys surjectivity in the third line.

`profile_function` returns the three flags. Its constructor refuses a
triple in which "bijective" disagrees with "injective and surjective",
because that disagreement is not a possible classification.

## Counting principles

Counting here is exact enumeration of finite choices. The implementations
are `permutation_count`, `combination_count`, `permutations`,
`combinations`, and `pascal_triangle`.

### Addition principle

### Worked example

If a first character is either one of 26 letters or one of 10 digits, and
those possibilities do not overlap, there are `26 + 10 = 36` choices. The
sets of letter-strings and digit-strings of length 1 are disjoint, so the
size of the union is the sum of the sizes. Overlap would require inclusion
of the intersection once, not twice. Addition applies to a disjoint union.

### Multiplication principle

### Worked example

A code is two letters followed by one digit. Each position is chosen
independently. There are `26 * 26 * 10 = 6760` codes. In set language the
set of codes is a Cartesian product, and
`|A × B × C| = |A| |B| |C|`.

This is why a set of `n` elements has `2**n` subsets: `n` positions, and
each position has 2 choices, in or out.

### Permutations

A permutation is an arrangement. The number of ways to choose `k` ordered
positions from `n` distinct items is

```text
P(n, k) = n! / (n - k)! = n (n - 1) ... (n - k + 1).
```

`P(n, n) = n!`. `P(n, k) = 0` when `k > n`, because an injection from a
`k`-set into an `n`-set cannot exist when `k` is larger. That is the same
fact as injectivity: the outputs would have to be distinct elements of a
smaller set.

### Worked example

Three distinct books on a shelf can be ordered in
`3! = 6` ways:

```text
ABC, ACB, BAC, BCA, CAB, CBA
```

`permutations(("A", "B", "C"))` returns those tuples in that order.
`P(5, 2) = 5 * 4 = 20`: choose a first item in 5 ways and a different
second item in 4 ways.

Items are distinguished by index. `permutations(("a", "a"))` returns two
identical tuples, one for each way to order the two positions. The
mathematical set of distinct tuples has size 1. The function counts index
permutations, matching `P(2, 2) = 2`.

`k = 0` yields one empty arrangement. There is one way to choose nothing.

### Combinations

A combination is an unordered subset. The number of `k`-element subsets of
an `n`-element set is

```text
C(n, k) = n! / (k! (n - k)!) = P(n, k) / k!.
```

Dividing by `k!` forgets the order inside each subset. `C(n, k) = 0` when
`k > n`. The sum `C(n, 0) + ... + C(n, n)` equals `2**n`, because every
subset has some size.

### Worked example

Committees of 2 people from `{A, B, C, D}`:

```text
{A, B}, {A, C}, {A, D}, {B, C}, {B, D}, {C, D}
```

There are `C(4, 2) = 6` of them. `combinations(("A", "B", "C", "D"), 2)`
returns those pairs in that order, each pair keeping the original relative
order. `C(5, 2) = 10`.

### Pascal's triangle

Row `n` of Pascal's triangle is `C(n, 0)` through `C(n, n)`. The triangle
is built from the recurrence, not from the factorial formula:

```text
C(n, 0) = C(n, n) = 1
C(n, k) = C(n - 1, k - 1) + C(n - 1, k)    for 0 < k < n
```

The recurrence is Pascal's identity: a `k`-subset of `{1, ..., n}` either
contains `n`, in which case the rest is a `(k - 1)`-subset of the first
`n - 1` elements, or it does not, in which case it is a `k`-subset of
those `n - 1` elements. Those cases are disjoint and cover every
`k`-subset. That is a direct counting proof of the identity. Building the
triangle by adding the two parents is that proof turned into a loop.

### Worked example

The first five rows, with row 0 on top:

```text
1
1 1
1 2 1
1 3 3 1
1 4 6 4 1
```

The middle entry of row 4 is `C(4, 2) = 6`, which is the committee count
in the previous example with a renamed 4-element set. The two parents of
that 6 are `C(3, 1) = 3` and `C(3, 2) = 3`. The sum of row `n` is `2**n`.
Row 4 sums to 16, the number of subsets of a 4-element set.

`pascal_triangle(3)` is `((1,), (1, 1), (1, 2, 1))`.

### Pigeonhole principle

### Worked example

If 13 people each have a birth month, then at least two share a month.
There are 13 items and 12 months. If every month occurred at most once,
there would be at most 12 people. That is the principle: if more than `k`
items are placed into `k` boxes, some box contains at least two items.

The same counting fact limits finite automata. A machine with `k` states,
given `k + 1` different prefixes, must send two of those prefixes to the
same state. The [automata notes](automata.md) use that sentence to prove
that `{ 0ⁿ1ⁿ | n ≥ 0 }` is not regular.

## Recurrences in the counting module

`factorial`, `fibonacci`, and `sum_first_naturals` are the recurrences, not
only their closed forms.

```text
0! = 1,                         n! = n * (n - 1)!
F(0) = 0, F(1) = 1,             F(n) = F(n - 1) + F(n - 2)
S(0) = 0,                       S(n) = S(n - 1) + n
```

The first values of `F` are `0, 1, 1, 2, 3, 5, 8, 13`. The closed form
`S(n) = n(n + 1) / 2` is proved by induction in
[proof techniques](proof-techniques.md). `S(4) = 10` and `4 * 5 / 2 = 10`
is one check of that theorem, not the proof.
