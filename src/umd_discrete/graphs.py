"""Adjacency-list graphs and the basic algorithms used in discrete mathematics.

Undirected edges are stored at both endpoints. Directed edges are stored at
the source. Duplicate edges are ignored. A self-loop contributes two to an
undirected degree and one each to directed in-degree and out-degree, which
keeps the handshaking identities exact.

Search uses breadth-first or depth-first traversal with a visited set, so a
cycle cannot cause an infinite walk. Topological order is Kahn's algorithm:
repeatedly take a vertex of in-degree zero. It succeeds exactly on directed
acyclic graphs.
"""

from collections import deque
from collections.abc import Hashable


class GraphError(Exception):
    """Raised when a graph operation does not apply to this graph."""


class CycleError(GraphError):
    """Raised when a topological sort meets a directed cycle."""


class Graph[T: Hashable]:
    """A finite graph stored as an adjacency list.

    Vertices must be hashable. ``directed=False`` builds an undirected graph.
    ``directed=True`` builds a directed graph. Vertices are created by
    :meth:`add_vertex` or as endpoints of :meth:`add_edge`. Insertion order is
    the order vertices were first seen.
    """

    def __init__(self, *, directed: bool = False) -> None:
        if type(directed) is not bool:
            raise TypeError("directed must be True or False")
        self.directed = directed
        # Inner dicts remember neighbor insertion order and ignore duplicates.
        self._adjacency: dict[T, dict[T, None]] = {}

    def add_vertex(self, vertex: T) -> None:
        """Add ``vertex`` if it is not already present."""
        self._adjacency.setdefault(vertex, {})

    def add_edge(self, source: T, target: T) -> None:
        """Add an edge from ``source`` to ``target``.

        Undirected graphs also store the opposite direction, except on a
        self-loop, which is stored once. Adding an existing edge does nothing.
        """
        self.add_vertex(source)
        self.add_vertex(target)
        self._adjacency[source][target] = None
        if not self.directed and source != target:
            self._adjacency[target][source] = None

    def __contains__(self, vertex: object) -> bool:
        return vertex in self._adjacency

    def vertices(self) -> tuple[T, ...]:
        """Return vertices in insertion order."""
        return tuple(self._adjacency)

    def neighbors(self, vertex: T) -> tuple[T, ...]:
        """Return the out-neighbors of ``vertex`` in insertion order.

        In an undirected graph those are the adjacent vertices.
        """
        self._require(vertex)
        return tuple(self._adjacency[vertex])

    def edges(self) -> tuple[tuple[T, T], ...]:
        """Return each edge once.

        Undirected edges are oriented from the endpoint that stored the edge
        first. A self-loop appears once.
        """
        if self.directed:
            return tuple(
                (source, target)
                for source, targets in self._adjacency.items()
                for target in targets
            )
        listed: list[tuple[T, T]] = []
        seen: set[frozenset[T]] = set()
        for source, targets in self._adjacency.items():
            for target in targets:
                key = frozenset((source, target))
                if key in seen:
                    continue
                seen.add(key)
                listed.append((source, target))
        return tuple(listed)

    def edge_count(self) -> int:
        """Return the number of edges, counting a self-loop once."""
        return len(self.edges())

    def degree(self, vertex: T) -> int:
        """Return the undirected degree of ``vertex``.

        A self-loop contributes two, matching the handshaking lemma
        ``sum(degree) = 2 * edge_count``. Directed graphs use :meth:`in_degree`
        and :meth:`out_degree` instead.
        """
        if self.directed:
            raise GraphError(
                "degree is defined for undirected graphs; use in_degree and out_degree"
            )
        self._require(vertex)
        adjacent = self._adjacency[vertex]
        loop_extra = 1 if vertex in adjacent else 0
        return len(adjacent) + loop_extra

    def out_degree(self, vertex: T) -> int:
        """Return the number of directed edges leaving ``vertex``."""
        self._require_directed()
        self._require(vertex)
        return len(self._adjacency[vertex])

    def in_degree(self, vertex: T) -> int:
        """Return the number of directed edges entering ``vertex``."""
        self._require_directed()
        self._require(vertex)
        return sum(1 for targets in self._adjacency.values() if vertex in targets)

    def has_path(self, source: T, target: T) -> bool:
        """Return whether a path from ``source`` to ``target`` exists.

        Every vertex has a trivial path to itself. Directed search follows
        edge direction. Undirected search uses either direction. Missing
        vertices raise :class:`GraphError`.
        """
        self._require(source)
        self._require(target)
        seen = {source}
        queue: deque[T] = deque([source])
        while queue:
            current = queue.popleft()
            if current == target:
                return True
            for neighbor in self._adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return False

    def connected_components(self) -> tuple[frozenset[T], ...]:
        """Return connected components in order of their first vertex.

        For a directed graph the components are weakly connected: two vertices
        are together when a path exists after edge direction is forgotten.
        Strong connectivity, where directed paths must run both ways, is a
        different relation and is not computed here.
        """
        adjacency = self._undirected_adjacency()
        seen: set[T] = set()
        components: list[frozenset[T]] = []
        for start in self.vertices():
            if start in seen:
                continue
            seen.add(start)
            stack = [start]
            members: list[T] = []
            while stack:
                current = stack.pop()
                members.append(current)
                for neighbor in adjacency[current]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        stack.append(neighbor)
            components.append(frozenset(members))
        return tuple(components)

    def is_bipartite(self) -> bool:
        """Return whether the vertices split into two independent sets.

        Direction is ignored. The empty graph and every graph with no odd
        cycle are bipartite. A self-loop is an odd cycle, so it is not
        bipartite. Disconnected graphs are bipartite when every component is.
        """
        colors: dict[T, int] = {}
        adjacency = self._undirected_adjacency()
        for start in self.vertices():
            if start in colors:
                continue
            colors[start] = 0
            queue: deque[T] = deque([start])
            while queue:
                current = queue.popleft()
                for neighbor in adjacency[current]:
                    if neighbor not in colors:
                        colors[neighbor] = 1 - colors[current]
                        queue.append(neighbor)
                    elif colors[neighbor] == colors[current]:
                        return False
        return True

    def topological_sort(self) -> tuple[T, ...]:
        """Return one topological order of a directed acyclic graph.

        Ties are broken by vertex insertion order, then by the order in which
        outgoing edges were added. The result is one valid order, not a claim
        that the order is unique. A directed cycle raises :class:`CycleError`.
        An undirected graph raises :class:`GraphError`.
        """
        self._require_directed()
        indegree = dict.fromkeys(self.vertices(), 0)
        for targets in self._adjacency.values():
            for target in targets:
                indegree[target] += 1
        ready: deque[T] = deque(
            vertex for vertex in self.vertices() if indegree[vertex] == 0
        )
        order: list[T] = []
        while ready:
            source = ready.popleft()
            order.append(source)
            for target in self._adjacency[source]:
                indegree[target] -= 1
                if indegree[target] == 0:
                    ready.append(target)
        if len(order) != len(indegree):
            raise CycleError("graph contains a directed cycle")
        return tuple(order)

    def _require(self, vertex: T) -> None:
        if vertex not in self._adjacency:
            raise GraphError(f"unknown vertex {vertex!r}")

    def _require_directed(self) -> None:
        if not self.directed:
            raise GraphError("operation requires a directed graph")

    def _undirected_adjacency(self) -> dict[T, tuple[T, ...]]:
        ordered: dict[T, dict[T, None]] = {vertex: {} for vertex in self._adjacency}
        for source, targets in self._adjacency.items():
            for target in targets:
                ordered[source].setdefault(target, None)
                ordered[target].setdefault(source, None)
        return {vertex: tuple(neighbors) for vertex, neighbors in ordered.items()}
