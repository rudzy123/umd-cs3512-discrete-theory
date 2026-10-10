"""Paths, components, bipartiteness, degrees, and topological order."""

from dataclasses import dataclass

import pytest

from umd_discrete.graphs import CycleError, Graph, GraphError


@dataclass(frozen=True)
class GraphCase:
    """A small graph and the properties the algorithms should report."""

    name: str
    directed: bool
    vertices: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    bipartite: bool
    components: frozenset[frozenset[str]]
    paths: tuple[tuple[str, str, bool], ...]
    has_directed_cycle: bool


def _components(*groups: frozenset[str]) -> frozenset[frozenset[str]]:
    return frozenset(groups)


CASES = (
    GraphCase("empty", False, (), (), True, _components(), (), False),
    GraphCase("empty-directed", True, (), (), True, _components(), (), False),
    GraphCase(
        "singleton",
        False,
        ("a",),
        (),
        True,
        _components(frozenset({"a"})),
        (("a", "a", True),),
        False,
    ),
    GraphCase(
        "singleton-directed",
        True,
        ("a",),
        (),
        True,
        _components(frozenset({"a"})),
        (("a", "a", True),),
        False,
    ),
    GraphCase(
        "edge",
        False,
        ("a", "b"),
        (("a", "b"),),
        True,
        _components(frozenset({"a", "b"})),
        (("a", "b", True), ("b", "a", True)),
        False,
    ),
    GraphCase(
        "triangle",
        False,
        ("a", "b", "c"),
        (("a", "b"), ("b", "c"), ("c", "a")),
        False,
        _components(frozenset({"a", "b", "c"})),
        (("a", "c", True),),
        False,
    ),
    GraphCase(
        "square",
        False,
        ("a", "b", "c", "d"),
        (("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")),
        True,
        _components(frozenset({"a", "b", "c", "d"})),
        (("a", "c", True),),
        False,
    ),
    GraphCase(
        "disconnected",
        False,
        ("a", "b", "c", "d"),
        (("a", "b"), ("c", "d")),
        True,
        _components(frozenset({"a", "b"}), frozenset({"c", "d"})),
        (("a", "b", True), ("a", "c", False), ("c", "d", True)),
        False,
    ),
    GraphCase(
        "isolated-vertex",
        False,
        ("a", "b", "c"),
        (("a", "b"),),
        True,
        _components(frozenset({"a", "b"}), frozenset({"c"})),
        (("a", "b", True), ("a", "c", False), ("c", "c", True)),
        False,
    ),
    GraphCase(
        "undirected-loop",
        False,
        ("a",),
        (("a", "a"),),
        False,
        _components(frozenset({"a"})),
        (("a", "a", True),),
        False,
    ),
    GraphCase(
        "loop-plus-isolated",
        False,
        ("b", "a"),
        (("a", "a"),),
        False,
        _components(frozenset({"b"}), frozenset({"a"})),
        (("b", "a", False), ("a", "a", True)),
        False,
    ),
    GraphCase(
        "directed-cycle",
        True,
        ("a", "b", "c"),
        (("a", "b"), ("b", "c"), ("c", "a")),
        False,
        _components(frozenset({"a", "b", "c"})),
        (("a", "b", True), ("b", "a", True)),
        True,
    ),
    GraphCase(
        "directed-loop",
        True,
        ("a",),
        (("a", "a"),),
        False,
        _components(frozenset({"a"})),
        (("a", "a", True),),
        True,
    ),
    GraphCase(
        "diamond-dag",
        True,
        ("a", "b", "c", "d"),
        (("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")),
        True,
        _components(frozenset({"a", "b", "c", "d"})),
        (("a", "d", True), ("d", "a", False), ("b", "c", False)),
        False,
    ),
    GraphCase(
        "directed-disconnected",
        True,
        ("a", "b", "c"),
        (("a", "b"),),
        True,
        _components(frozenset({"a", "b"}), frozenset({"c"})),
        (("a", "b", True), ("b", "a", False), ("a", "c", False), ("c", "c", True)),
        False,
    ),
)


def _build(case: GraphCase) -> Graph[str]:
    graph: Graph[str] = Graph[str](directed=case.directed)
    for vertex in case.vertices:
        graph.add_vertex(vertex)
    for source, target in case.edges:
        graph.add_edge(source, target)
    return graph


def _case_id(case: GraphCase) -> str:
    return case.name


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_bipartite(case: GraphCase) -> None:
    assert _build(case).is_bipartite() == case.bipartite


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_connected_components(case: GraphCase) -> None:
    assert set(_build(case).connected_components()) == set(case.components)


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_paths(case: GraphCase) -> None:
    graph = _build(case)
    for source, target, expected in case.paths:
        assert graph.has_path(source, target) == expected


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_topological_sort(case: GraphCase) -> None:
    graph = _build(case)
    if not case.directed:
        with pytest.raises(GraphError):
            graph.topological_sort()
        return
    if case.has_directed_cycle:
        with pytest.raises(CycleError, match="directed cycle"):
            graph.topological_sort()
        return
    order = graph.topological_sort()
    assert set(order) == set(case.vertices)
    position = {vertex: index for index, vertex in enumerate(order)}
    for source, target in case.edges:
        assert position[source] < position[target]


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_handshaking_lemma(case: GraphCase) -> None:
    graph = _build(case)
    if case.directed:
        vertices = graph.vertices()
        assert sum(graph.in_degree(vertex) for vertex in vertices) == graph.edge_count()
        assert (
            sum(graph.out_degree(vertex) for vertex in vertices) == graph.edge_count()
        )
        return
    assert sum(graph.degree(vertex) for vertex in graph.vertices()) == (
        2 * graph.edge_count()
    )


def test_triangle_degrees() -> None:
    graph: Graph[str] = Graph[str]()
    graph.add_edge("a", "b")
    graph.add_edge("b", "c")
    graph.add_edge("c", "a")
    assert [graph.degree(vertex) for vertex in ("a", "b", "c")] == [2, 2, 2]


def test_self_loop_degree() -> None:
    undirected: Graph[str] = Graph[str]()
    undirected.add_edge("a", "a")
    assert undirected.degree("a") == 2
    assert undirected.edge_count() == 1

    directed: Graph[str] = Graph[str](directed=True)
    directed.add_edge("a", "b")
    directed.add_edge("b", "b")
    directed.add_edge("b", "c")
    assert directed.in_degree("a") == 0
    assert directed.out_degree("a") == 1
    assert directed.in_degree("b") == 2
    assert directed.out_degree("b") == 2
    assert directed.in_degree("c") == 1
    assert directed.out_degree("c") == 0


def test_neighbors_follow_insertion_order() -> None:
    graph: Graph[str] = Graph[str]()
    graph.add_edge("b", "a")
    graph.add_edge("b", "c")
    assert graph.neighbors("b") == ("a", "c")
    assert graph.neighbors("a") == ("b",)


def test_duplicate_edge_is_ignored() -> None:
    graph: Graph[str] = Graph[str]()
    graph.add_edge("a", "b")
    graph.add_edge("a", "b")
    assert graph.degree("a") == 1
    assert graph.edge_count() == 1


def test_topological_tie_break_follows_insertion_order() -> None:
    graph: Graph[str] = Graph[str](directed=True)
    graph.add_vertex("a")
    graph.add_vertex("b")
    graph.add_vertex("c")
    graph.add_vertex("d")
    graph.add_edge("a", "b")
    graph.add_edge("a", "c")
    graph.add_edge("b", "d")
    graph.add_edge("c", "d")
    assert graph.topological_sort() == ("a", "b", "c", "d")


def test_unknown_vertex_and_wrong_graph_kind() -> None:
    undirected: Graph[str] = Graph[str]()
    with pytest.raises(GraphError, match="unknown vertex"):
        undirected.degree("missing")
    with pytest.raises(GraphError, match="directed"):
        undirected.in_degree("missing")

    directed: Graph[str] = Graph[str](directed=True)
    directed.add_vertex("a")
    with pytest.raises(GraphError, match="undirected"):
        directed.degree("a")


def test_cycle_error_is_a_graph_error() -> None:
    assert issubclass(CycleError, GraphError)
