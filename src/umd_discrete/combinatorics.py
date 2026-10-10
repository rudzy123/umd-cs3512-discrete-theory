"""Permutations, combinations, Pascal's triangle, and small recurrences.

Counting functions return a number and accept large arguments.
Enumerations return every generated tuple and refuse outputs that would be
too large to teach from. ``n!`` grows faster than any exponential of fixed
base, so the guard is on the result count rather than on ``n`` alone.
"""

import itertools
import math
from collections.abc import Sequence
from typing import Final

MAX_ENUMERATED_RESULTS: Final = 10_000


def _require_non_negative_int(value: int, label: str) -> None:
    if type(value) is not int:
        raise TypeError(f"{label} must be an int")
    if value < 0:
        raise ValueError(f"{label} must be non-negative")


def permutation_count(n: int, k: int | None = None) -> int:
    """Return ``P(n, k) = n! / (n - k)!``.

    ``k`` defaults to ``n``. The value is ``0`` when ``k > n``.
    ``P(n, k)`` is the number of injections from a ``k``-element set into an
    ``n``-element set, which is also the number of ways to choose ``k``
    ordered positions from ``n`` distinct items.
    """
    _require_non_negative_int(n, "n")
    chosen = n
    if k is not None:
        _require_non_negative_int(k, "k")
        chosen = k
    return math.perm(n, chosen)


def combination_count(n: int, k: int) -> int:
    """Return ``C(n, k) = n! / (k! (n - k)!)``.

    The value is the number of ``k``-element subsets of an ``n``-element set.
    It is ``0`` when ``k > n``. The sum of ``C(n, 0)`` through ``C(n, n)``
    is ``2**n``, the number of subsets.
    """
    _require_non_negative_int(n, "n")
    _require_non_negative_int(k, "k")
    return math.comb(n, k)


def _guard_enumeration(count: int, kind: str) -> None:
    if count > MAX_ENUMERATED_RESULTS:
        raise ValueError(
            f"refusing to enumerate more than {MAX_ENUMERATED_RESULTS} {kind}"
        )


def permutations[T](
    items: Sequence[T],
    k: int | None = None,
) -> tuple[tuple[T, ...], ...]:
    """Return the ``k``-permutations of ``items`` in lexicographic index order.

    Items are distinguished by position. A repeated value is repeated in the
    output once for every index permutation, so ``permutations(("a", "a"))``
    contains two identical tuples. ``k`` defaults to the length of ``items``.
    ``k == 0`` yields one empty tuple. ``k`` larger than the length yields none.
    """
    pool = tuple(items)
    chosen = len(pool) if k is None else k
    _require_non_negative_int(chosen, "k")
    _guard_enumeration(permutation_count(len(pool), chosen), "permutations")
    return tuple(itertools.permutations(pool, chosen))


def combinations[T](items: Sequence[T], k: int) -> tuple[tuple[T, ...], ...]:
    """Return the ``k``-combinations of ``items``, preserving relative order.

    ``combinations(("A", "B", "C"), 2)`` is ``(("A", "B"), ("A", "C"), ("B", "C"))``.
    ``k == 0`` yields one empty tuple. Repeated values are distinguished by
    index, matching :func:`permutations`.
    """
    pool = tuple(items)
    _require_non_negative_int(k, "k")
    _guard_enumeration(combination_count(len(pool), k), "combinations")
    return tuple(itertools.combinations(pool, k))


def pascal_triangle(n_rows: int) -> tuple[tuple[int, ...], ...]:
    """Return the first ``n_rows`` of Pascal's triangle, starting at row 0.

    Row ``n`` is ``C(n, 0), ..., C(n, n)``. Each interior entry is the sum of
    the two entries above it:

    ``C(n, k) = C(n - 1, k - 1) + C(n - 1, k)``,

    with ``C(n, 0) = C(n, n) = 1``. The sum of row ``n`` is ``2**n``.
    """
    _require_non_negative_int(n_rows, "n_rows")
    if n_rows == 0:
        return ()
    rows: list[tuple[int, ...]] = [(1,)]
    for _ in range(1, n_rows):
        previous = rows[-1]
        middle = tuple(
            previous[index] + previous[index + 1] for index in range(len(previous) - 1)
        )
        rows.append((1, *middle, 1))
    return tuple(rows)


def factorial(n: int) -> int:
    """Return ``n!``.

    Base: ``0! = 1``. Recurrence: ``n! = n * (n - 1)!`` for ``n > 0``.
    """
    _require_non_negative_int(n, "n")
    product = 1
    for value in range(2, n + 1):
        product *= value
    return product


def fibonacci(n: int) -> int:
    """Return the ``n``-th Fibonacci number.

    Base: ``F(0) = 0`` and ``F(1) = 1``.
    Recurrence: ``F(n) = F(n - 1) + F(n - 2)`` for ``n > 1``.
    """
    _require_non_negative_int(n, "n")
    if n == 0:
        return 0
    previous = 0
    current = 1
    for _ in range(1, n):
        # F(i) = F(i - 1) + F(i - 2)
        previous, current = current, previous + current
    return current


def sum_first_naturals(n: int) -> int:
    """Return ``0 + 1 + ... + n``.

    Base: ``S(0) = 0``. Recurrence: ``S(n) = S(n - 1) + n`` for ``n > 0``.
    Induction shows ``S(n) = n * (n + 1) / 2``. See
    ``docs/proof-techniques.md``. This function follows the recurrence.
    """
    _require_non_negative_int(n, "n")
    total = 0
    for value in range(1, n + 1):
        total += value
    return total
