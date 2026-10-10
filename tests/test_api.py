"""The public package surface and the examples in the README."""

import umd_discrete
from umd_discrete import (
    Graph,
    Variable,
    combination_count,
    equivalent,
    even_ones_dfa,
    identifier_dfa,
    is_equivalence_relation,
    is_tautology,
    pascal_triangle,
    power_set,
)


def test_public_names_are_exported() -> None:
    assert umd_discrete.__version__ == "0.1.0"
    for name in umd_discrete.__all__:
        assert hasattr(umd_discrete, name)


def test_readme_logic_example() -> None:
    p = Variable("P")
    q = Variable("Q")
    assert equivalent(~(p & q), ~p | ~q)
    assert is_tautology(p | ~p)


def test_readme_sets_example() -> None:
    assert power_set({"a"}) == {frozenset(), frozenset({"a"})}
    relation = {(1, 1), (2, 2), (1, 2), (2, 1)}
    assert is_equivalence_relation(relation, {1, 2})


def test_readme_counting_example() -> None:
    assert combination_count(5, 2) == 10
    assert pascal_triangle(3) == ((1,), (1, 1), (1, 2, 1))


def test_readme_graph_example() -> None:
    graph: Graph[str] = Graph[str]()
    graph.add_edge("a", "b")
    graph.add_edge("b", "c")
    assert graph.has_path("a", "c")
    assert graph.connected_components() == (frozenset({"a", "b", "c"}),)


def test_readme_automata_example() -> None:
    assert even_ones_dfa().accepts("110")
    assert not even_ones_dfa().accepts("10")
    assert identifier_dfa().accepts("a1")
    assert not identifier_dfa().accepts("1a")
