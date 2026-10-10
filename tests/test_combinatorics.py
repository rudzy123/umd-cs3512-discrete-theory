"""Counting functions, enumerations, and recurrence checks."""

from collections.abc import Callable

import pytest

from umd_discrete.combinatorics import (
    MAX_ENUMERATED_RESULTS,
    combination_count,
    combinations,
    factorial,
    fibonacci,
    pascal_triangle,
    permutation_count,
    permutations,
    sum_first_naturals,
)
from umd_discrete.sets import power_set


def test_small_permutations_and_combinations() -> None:
    assert permutations(()) == ((),)
    assert permutations(("A", "B", "C")) == (
        ("A", "B", "C"),
        ("A", "C", "B"),
        ("B", "A", "C"),
        ("B", "C", "A"),
        ("C", "A", "B"),
        ("C", "B", "A"),
    )
    assert permutations(("A", "B", "C"), 2) == (
        ("A", "B"),
        ("A", "C"),
        ("B", "A"),
        ("B", "C"),
        ("C", "A"),
        ("C", "B"),
    )
    assert permutations(("a", "a")) == (("a", "a"), ("a", "a"))
    assert combinations((), 0) == ((),)
    assert combinations((1, 2), 0) == ((),)
    assert combinations((1,), 2) == ()
    assert combinations(("A", "B", "C", "D"), 2) == (
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("B", "D"),
        ("C", "D"),
    )


@pytest.mark.parametrize(
    ("n", "k", "permutations_expected", "combinations_expected"),
    [
        (5, 2, 20, 10),
        (5, 0, 1, 1),
        (5, 5, 120, 1),
        (3, 5, 0, 0),
        (0, 0, 1, 1),
    ],
)
def test_counting_formulas(
    n: int,
    k: int,
    permutations_expected: int,
    combinations_expected: int,
) -> None:
    assert permutation_count(n, k) == permutations_expected
    assert combination_count(n, k) == combinations_expected
    assert permutation_count(n) == factorial(n)


def test_enumeration_matches_the_counting_formulas() -> None:
    items = (0, 1, 2, 3, 4)
    assert len(permutations(items, 2)) == permutation_count(5, 2)
    assert len(combinations(items, 2)) == combination_count(5, 2)
    assert len(permutations(("A", "B", "C"))) == factorial(3)


def test_enumeration_refuses_huge_outputs() -> None:
    with pytest.raises(ValueError, match=str(MAX_ENUMERATED_RESULTS)):
        permutations(range(8))
    with pytest.raises(ValueError, match=str(MAX_ENUMERATED_RESULTS)):
        combinations(range(16), 8)
    assert combination_count(16, 8) == 12_870


def test_pascal_triangle_rows() -> None:
    assert pascal_triangle(0) == ()
    assert pascal_triangle(5) == (
        (1,),
        (1, 1),
        (1, 2, 1),
        (1, 3, 3, 1),
        (1, 4, 6, 4, 1),
    )


@pytest.mark.parametrize("n", range(1, 8))
def test_pascal_recurrence(n: int) -> None:
    triangle = pascal_triangle(n + 1)
    previous = triangle[n - 1]
    current = triangle[n]
    assert current[0] == 1
    assert current[-1] == 1
    for index in range(1, n):
        assert current[index] == previous[index - 1] + previous[index]
    assert current == tuple(combination_count(n, k) for k in range(n + 1))
    assert sum(current) == 2**n


@pytest.mark.parametrize("n", range(9))
def test_subset_counts_agree(n: int) -> None:
    assert len(power_set(range(n))) == 2**n
    assert sum(combination_count(n, k) for k in range(n + 1)) == 2**n
    assert sum(pascal_triangle(n + 1)[n]) == 2**n


@pytest.mark.parametrize("n", range(1, 12))
def test_factorial_recurrence(n: int) -> None:
    assert factorial(0) == 1
    assert factorial(n) == n * factorial(n - 1)


@pytest.mark.parametrize("n", range(2, 20))
def test_fibonacci_recurrence(n: int) -> None:
    assert fibonacci(n) == fibonacci(n - 1) + fibonacci(n - 2)


def test_fibonacci_base_values() -> None:
    assert [fibonacci(n) for n in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13]


@pytest.mark.parametrize("n", range(31))
def test_sum_matches_closed_form(n: int) -> None:
    """Check the closed form on a finite sample. The proof is by induction."""
    assert sum_first_naturals(n) == n * (n + 1) // 2


def test_sum_follows_its_recurrence() -> None:
    assert sum_first_naturals(0) == 0
    for n in range(1, 15):
        assert sum_first_naturals(n) == sum_first_naturals(n - 1) + n


@pytest.mark.parametrize(
    "call",
    [
        lambda: factorial(-1),
        lambda: fibonacci(-1),
        lambda: pascal_triangle(-1),
        lambda: combination_count(-1, 1),
        lambda: permutation_count(3, -1),
        lambda: permutations((1, 2), -1),
        lambda: combinations((1, 2), -1),
    ],
)
def test_negative_counts_are_rejected(call: Callable[[], object]) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        call()


def test_bools_are_not_silent_integers() -> None:
    with pytest.raises(TypeError, match="int"):
        factorial(True)
    with pytest.raises(TypeError, match="int"):
        pascal_triangle(False)
