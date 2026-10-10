"""Finite sets, relations, and functions.

Elements must be hashable. Duplicates collapse, and Python's rule that
``True == 1`` means those two values cannot both sit in one set.

A relation is a set of ordered pairs on a finite domain. A function is a
total mapping from a finite domain to a finite codomain. The predicates below
are the textbook definitions, evaluated by checking every required element.
On a finite input that check is a proof for that input, not a schema that
covers every set.
"""

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import Final

MAX_POWER_SET_ELEMENTS: Final = 16


def union[T: Hashable](left: Iterable[T], right: Iterable[T]) -> frozenset[T]:
    """Return the elements that belong to ``left`` or ``right``."""
    return frozenset(left) | frozenset(right)


def intersection[T: Hashable](left: Iterable[T], right: Iterable[T]) -> frozenset[T]:
    """Return the elements that belong to both ``left`` and ``right``."""
    return frozenset(left) & frozenset(right)


def difference[T: Hashable](left: Iterable[T], right: Iterable[T]) -> frozenset[T]:
    """Return the elements of ``left`` that are not elements of ``right``."""
    return frozenset(left) - frozenset(right)


def power_set[T: Hashable](elements: Iterable[T]) -> frozenset[frozenset[T]]:
    """Return every subset of ``elements``.

    The empty set has one subset, itself. A set of ``n`` elements has ``2**n``
    subsets. Enumeration stops above :data:`MAX_POWER_SET_ELEMENTS` because
    the output doubles with each added element.
    """
    unique = tuple(dict.fromkeys(elements))
    if len(unique) > MAX_POWER_SET_ELEMENTS:
        raise ValueError(
            "power set enumeration is limited to "
            f"{MAX_POWER_SET_ELEMENTS} elements; found {len(unique)}"
        )
    subsets = [
        frozenset(unique[index] for index in range(len(unique)) if mask & (1 << index))
        for mask in range(1 << len(unique))
    ]
    return frozenset(subsets)


def _checked_relation[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> tuple[set[T], set[tuple[T, T]]]:
    members = set(domain)
    pairs: set[tuple[T, T]] = set()
    for pair in relation:
        if isinstance(pair, str) or len(pair) != 2:
            raise ValueError("relation elements must be ordered pairs")
        pairs.add((pair[0], pair[1]))
    outside = {element for pair in pairs for element in pair if element not in members}
    if outside:
        rendered = ", ".join(repr(element) for element in sorted(outside, key=repr))
        raise ValueError(
            "relation pairs must use elements from the domain; found " + rendered
        )
    return members, pairs


def is_reflexive[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> bool:
    """Return whether every domain element is related to itself.

    Vacuously true when the domain is empty.
    """
    members, pairs = _checked_relation(relation, domain)
    return all((element, element) in pairs for element in members)


def is_symmetric[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> bool:
    """Return whether ``(b, a)`` is present whenever ``(a, b)`` is present."""
    _members, pairs = _checked_relation(relation, domain)
    return all((right, left) in pairs for left, right in pairs)


def is_antisymmetric[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> bool:
    """Return whether mutual relatedness forces the two elements to be equal.

    If ``(a, b)`` and ``(b, a)`` are both present, antisymmetry requires
    ``a == b``. Equality relations are antisymmetric. A non-trivial
    equivalence relation is not.
    """
    _members, pairs = _checked_relation(relation, domain)
    return all(left == right for left, right in pairs if (right, left) in pairs)


def is_transitive[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> bool:
    """Return whether ``(a, c)`` is present whenever ``(a, b)`` and ``(b, c)`` are."""
    _members, pairs = _checked_relation(relation, domain)
    for left, middle in pairs:
        for other, far in pairs:
            if middle == other and (left, far) not in pairs:
                return False
    return True


def is_equivalence_relation[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> bool:
    """Return whether ``relation`` is an equivalence relation on ``domain``.

    Equivalence means reflexive, symmetric, and transitive.
    """
    pairs = tuple(relation)
    members = tuple(domain)
    return (
        is_reflexive(pairs, members)
        and is_symmetric(pairs, members)
        and is_transitive(pairs, members)
    )


def is_partial_order[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> bool:
    """Return whether ``relation`` is reflexive, antisymmetric, and transitive."""
    pairs = tuple(relation)
    members = tuple(domain)
    return (
        is_reflexive(pairs, members)
        and is_antisymmetric(pairs, members)
        and is_transitive(pairs, members)
    )


@dataclass(frozen=True)
class RelationProfile:
    """The standard properties of one relation on one finite domain.

    ``equivalence`` is true exactly when the relation is reflexive, symmetric,
    and transitive. ``partial_order`` is true exactly when it is reflexive,
    antisymmetric, and transitive. The only relations that are both are the
    equality relations, including the empty relation on the empty domain.
    """

    reflexive: bool
    symmetric: bool
    antisymmetric: bool
    transitive: bool
    equivalence: bool
    partial_order: bool

    def __post_init__(self) -> None:
        if self.equivalence != (self.reflexive and self.symmetric and self.transitive):
            raise ValueError(
                "equivalence must mean reflexive, symmetric, and transitive"
            )
        if self.partial_order != (
            self.reflexive and self.antisymmetric and self.transitive
        ):
            raise ValueError(
                "partial_order must mean reflexive, antisymmetric, and transitive"
            )


def profile_relation[T: Hashable](
    relation: Iterable[tuple[T, T]],
    domain: Iterable[T],
) -> RelationProfile:
    """Classify ``relation`` on ``domain``."""
    pairs = tuple(relation)
    members = tuple(domain)
    reflexive = is_reflexive(pairs, members)
    symmetric = is_symmetric(pairs, members)
    antisymmetric = is_antisymmetric(pairs, members)
    transitive = is_transitive(pairs, members)
    return RelationProfile(
        reflexive=reflexive,
        symmetric=symmetric,
        antisymmetric=antisymmetric,
        transitive=transitive,
        equivalence=reflexive and symmetric and transitive,
        partial_order=reflexive and antisymmetric and transitive,
    )


def _total_function[A: Hashable, B: Hashable](
    function: Mapping[A, B],
    domain: Iterable[A] | None,
) -> dict[A, B]:
    table = dict(function)
    if domain is None:
        return table
    members = set(domain)
    keys = set(table)
    if keys != members:
        missing = ", ".join(
            repr(element) for element in sorted(members - keys, key=repr)
        )
        extra = ", ".join(repr(element) for element in sorted(keys - members, key=repr))
        raise ValueError(
            "function must be total on the domain; "
            f"missing {missing or 'nothing'}; extra {extra or 'nothing'}"
        )
    return table


def _image_inside[A: Hashable, B: Hashable](
    table: Mapping[A, B],
    codomain: set[B],
) -> None:
    outside = set(table.values()) - codomain
    if outside:
        rendered = ", ".join(repr(element) for element in sorted(outside, key=repr))
        raise ValueError(f"function values outside the codomain: {rendered}")


def is_injective[A: Hashable, B: Hashable](
    function: Mapping[A, B],
    *,
    domain: Iterable[A] | None = None,
) -> bool:
    """Return whether distinct domain elements have distinct images.

    The empty function is injective. When ``domain`` is given, ``function``
    must be total on it.
    """
    table = _total_function(function, domain)
    return len(set(table.values())) == len(table)


def is_surjective[A: Hashable, B: Hashable](
    function: Mapping[A, B],
    codomain: Iterable[B],
    *,
    domain: Iterable[A] | None = None,
) -> bool:
    """Return whether every element of ``codomain`` is ``function(a)`` for some ``a``.

    Values outside ``codomain`` are rejected. The empty function is surjective
    onto the empty codomain and not surjective onto a non-empty one.
    """
    table = _total_function(function, domain)
    targets = set(codomain)
    _image_inside(table, targets)
    return targets <= set(table.values())


def is_bijective[A: Hashable, B: Hashable](
    function: Mapping[A, B],
    codomain: Iterable[B],
    *,
    domain: Iterable[A] | None = None,
) -> bool:
    """Return whether ``function`` is injective and surjective onto ``codomain``."""
    members = None if domain is None else tuple(domain)
    targets = tuple(codomain)
    return is_injective(function, domain=members) and is_surjective(
        function,
        targets,
        domain=members,
    )


@dataclass(frozen=True)
class FunctionProfile:
    """Injectivity, surjectivity, and bijectivity of one finite function.

    Bijective means both injective and surjective. On finite sets of equal
    size those three properties coincide; the codomain still has to be stated,
    because a Python mapping does not store the codomain it was meant to hit.
    """

    injective: bool
    surjective: bool
    bijective: bool

    def __post_init__(self) -> None:
        if self.bijective != (self.injective and self.surjective):
            raise ValueError("bijective must mean injective and surjective")


def profile_function[A: Hashable, B: Hashable](
    function: Mapping[A, B],
    codomain: Iterable[B],
    *,
    domain: Iterable[A] | None = None,
) -> FunctionProfile:
    """Classify ``function`` as a map into ``codomain``."""
    members = None if domain is None else tuple(domain)
    targets = tuple(codomain)
    injective = is_injective(function, domain=members)
    surjective = is_surjective(function, targets, domain=members)
    return FunctionProfile(
        injective=injective,
        surjective=surjective,
        bijective=injective and surjective,
    )
