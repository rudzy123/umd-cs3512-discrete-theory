"""Set algebra, relation properties, and finite function classification."""

from collections.abc import Iterable
from typing import cast

import pytest

from umd_discrete.sets import (
    MAX_POWER_SET_ELEMENTS,
    FunctionProfile,
    RelationProfile,
    difference,
    intersection,
    is_antisymmetric,
    is_bijective,
    is_equivalence_relation,
    is_injective,
    is_partial_order,
    is_reflexive,
    is_surjective,
    is_symmetric,
    is_transitive,
    power_set,
    profile_function,
    profile_relation,
    union,
)


@pytest.mark.parametrize(
    ("left", "right", "united", "common", "removed"),
    [
        (set(), {1}, {1}, set(), set()),
        ({1}, set(), {1}, set(), {1}),
        ({1}, {1}, {1}, {1}, set()),
        ({1, 2, 3}, {2}, {1, 2, 3}, {2}, {1, 3}),
        ({1, 2}, {2, 3}, {1, 2, 3}, {2}, {1}),
    ],
)
def test_set_operations(
    left: set[int],
    right: set[int],
    united: set[int],
    common: set[int],
    removed: set[int],
) -> None:
    assert union(left, right) == united
    assert intersection(left, right) == common
    assert difference(left, right) == removed


def test_empty_and_singleton_power_sets() -> None:
    assert power_set(()) == frozenset({frozenset()})
    assert power_set({1}) == frozenset({frozenset(), frozenset({1})})
    assert power_set({1, 2}) == frozenset(
        {
            frozenset(),
            frozenset({1}),
            frozenset({2}),
            frozenset({1, 2}),
        }
    )
    assert power_set((1, 1)) == power_set({1})


@pytest.mark.parametrize("size", range(9))
def test_power_set_has_two_to_the_n_subsets(size: int) -> None:
    assert len(power_set(range(size))) == 2**size


def test_power_set_refuses_large_inputs() -> None:
    with pytest.raises(ValueError, match=str(MAX_POWER_SET_ELEMENTS)):
        power_set(range(MAX_POWER_SET_ELEMENTS + 1))


class RelationCase:
    """One finite relation and the properties it should have."""

    def __init__(
        self,
        name: str,
        relation: frozenset[tuple[int, int]],
        domain: frozenset[int],
        *,
        reflexive: bool,
        symmetric: bool,
        antisymmetric: bool,
        transitive: bool,
    ) -> None:
        self.name = name
        self.relation = relation
        self.domain = domain
        self.reflexive = reflexive
        self.symmetric = symmetric
        self.antisymmetric = antisymmetric
        self.transitive = transitive
        self.equivalence = reflexive and symmetric and transitive
        self.partial_order = reflexive and antisymmetric and transitive


def _relation(*pairs: tuple[int, int]) -> frozenset[tuple[int, int]]:
    return frozenset(pairs)


def _at_most(domain: frozenset[int]) -> frozenset[tuple[int, int]]:
    return frozenset(
        (left, right) for left in domain for right in domain if left <= right
    )


RELATION_CASES = (
    RelationCase(
        "empty-domain",
        _relation(),
        frozenset[int](),
        reflexive=True,
        symmetric=True,
        antisymmetric=True,
        transitive=True,
    ),
    RelationCase(
        "empty-on-singleton",
        _relation(),
        frozenset({1}),
        reflexive=False,
        symmetric=True,
        antisymmetric=True,
        transitive=True,
    ),
    RelationCase(
        "singleton-loop",
        _relation((1, 1)),
        frozenset({1}),
        reflexive=True,
        symmetric=True,
        antisymmetric=True,
        transitive=True,
    ),
    RelationCase(
        "equality",
        _relation((1, 1), (2, 2)),
        frozenset({1, 2}),
        reflexive=True,
        symmetric=True,
        antisymmetric=True,
        transitive=True,
    ),
    RelationCase(
        "two-blocks",
        _relation((1, 1), (2, 2), (3, 3), (1, 2), (2, 1)),
        frozenset({1, 2, 3}),
        reflexive=True,
        symmetric=True,
        antisymmetric=False,
        transitive=True,
    ),
    RelationCase(
        "numeric-order",
        _at_most(frozenset({1, 2, 3})),
        frozenset({1, 2, 3}),
        reflexive=True,
        symmetric=False,
        antisymmetric=True,
        transitive=True,
    ),
    RelationCase(
        "mutual-without-loops",
        _relation((1, 2), (2, 1)),
        frozenset({1, 2}),
        reflexive=False,
        symmetric=True,
        antisymmetric=False,
        transitive=False,
    ),
    RelationCase(
        "strict-chain",
        _relation((1, 2), (2, 3), (1, 3)),
        frozenset({1, 2, 3}),
        reflexive=False,
        symmetric=False,
        antisymmetric=True,
        transitive=True,
    ),
    RelationCase(
        "broken-chain",
        _relation((1, 2), (2, 3)),
        frozenset({1, 2, 3}),
        reflexive=False,
        symmetric=False,
        antisymmetric=True,
        transitive=False,
    ),
    RelationCase(
        "single-pair",
        _relation((1, 2)),
        frozenset({1, 2}),
        reflexive=False,
        symmetric=False,
        antisymmetric=True,
        transitive=True,
    ),
)


def _relation_id(case: RelationCase) -> str:
    return case.name


@pytest.mark.parametrize("case", RELATION_CASES, ids=_relation_id)
def test_relation_properties(case: RelationCase) -> None:
    assert is_reflexive(case.relation, case.domain) == case.reflexive
    assert is_symmetric(case.relation, case.domain) == case.symmetric
    assert is_antisymmetric(case.relation, case.domain) == case.antisymmetric
    assert is_transitive(case.relation, case.domain) == case.transitive
    assert is_equivalence_relation(case.relation, case.domain) == case.equivalence
    assert is_partial_order(case.relation, case.domain) == case.partial_order
    assert profile_relation(case.relation, case.domain) == RelationProfile(
        reflexive=case.reflexive,
        symmetric=case.symmetric,
        antisymmetric=case.antisymmetric,
        transitive=case.transitive,
        equivalence=case.equivalence,
        partial_order=case.partial_order,
    )


def test_equality_is_both_an_equivalence_and_a_partial_order() -> None:
    profile = profile_relation(_relation((1, 1), (2, 2)), frozenset({1, 2}))
    assert profile.equivalence
    assert profile.partial_order


def test_relation_rejects_elements_outside_the_domain() -> None:
    with pytest.raises(ValueError, match="domain"):
        is_reflexive([(1, 2)], [1])


def test_relation_rejects_a_string_posing_as_a_pair() -> None:
    pairs = cast("Iterable[tuple[str, str]]", ["ab"])
    with pytest.raises(ValueError, match="ordered pairs"):
        is_symmetric(pairs, {"a", "b"})


class FunctionCase:
    """One finite function and the classification it should receive."""

    def __init__(
        self,
        name: str,
        function: dict[int, str],
        codomain: frozenset[str],
        *,
        injective: bool,
        surjective: bool,
    ) -> None:
        self.name = name
        self.function = function
        self.codomain = codomain
        self.injective = injective
        self.surjective = surjective
        self.bijective = injective and surjective


FUNCTION_CASES = (
    FunctionCase(
        "empty-to-empty",
        {},
        frozenset[str](),
        injective=True,
        surjective=True,
    ),
    FunctionCase(
        "empty-to-singleton",
        {},
        frozenset({"a"}),
        injective=True,
        surjective=False,
    ),
    FunctionCase(
        "singleton-bijection",
        {1: "a"},
        frozenset({"a"}),
        injective=True,
        surjective=True,
    ),
    FunctionCase(
        "injective-only",
        {1: "a"},
        frozenset({"a", "b"}),
        injective=True,
        surjective=False,
    ),
    FunctionCase(
        "surjective-only",
        {1: "a", 2: "a"},
        frozenset({"a"}),
        injective=False,
        surjective=True,
    ),
    FunctionCase(
        "three-bijection",
        {1: "a", 2: "b", 3: "c"},
        frozenset({"a", "b", "c"}),
        injective=True,
        surjective=True,
    ),
    FunctionCase(
        "neither",
        {1: "a", 2: "a", 3: "b"},
        frozenset({"a", "b", "c"}),
        injective=False,
        surjective=False,
    ),
    FunctionCase(
        "two-bijection",
        {1: "a", 2: "b"},
        frozenset({"a", "b"}),
        injective=True,
        surjective=True,
    ),
)


def _function_id(case: FunctionCase) -> str:
    return case.name


@pytest.mark.parametrize("case", FUNCTION_CASES, ids=_function_id)
def test_function_classifications(case: FunctionCase) -> None:
    assert is_injective(case.function) == case.injective
    assert is_surjective(case.function, case.codomain) == case.surjective
    assert is_bijective(case.function, case.codomain) == case.bijective
    assert profile_function(case.function, case.codomain) == FunctionProfile(
        injective=case.injective,
        surjective=case.surjective,
        bijective=case.bijective,
    )


def test_function_must_be_total_on_a_stated_domain() -> None:
    with pytest.raises(ValueError, match="total"):
        is_injective({1: "a"}, domain={1, 2})


def test_function_values_must_land_in_the_codomain() -> None:
    with pytest.raises(ValueError, match="codomain"):
        is_surjective({1: "a"}, {"b"})


def test_profile_invariants_reject_inconsistent_flags() -> None:
    with pytest.raises(ValueError, match="bijective"):
        FunctionProfile(injective=True, surjective=False, bijective=True)
    with pytest.raises(ValueError, match="equivalence"):
        RelationProfile(
            reflexive=True,
            symmetric=True,
            antisymmetric=True,
            transitive=True,
            equivalence=False,
            partial_order=True,
        )
