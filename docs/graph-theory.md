# Graph vocabulary and the basic algorithms

A **graph** is a finite set of **vertices** together with a set of **edges**
joining them. `umd_discrete.graphs.Graph` stores an adjacency list: each
vertex names the vertices it points to. Vertices must be hashable.
Duplicate calls to `add_edge` do not create a second copy of the same edge.

An **undirected** edge `{u, v}` is stored at both endpoints. A **directed**
edge `(u, v)` is stored only at `u`. Pass `directed=True` to build the
second kind. A **self-loop** is an edge from a vertex to itself.

The running undirected graph in this note is

```text
A —— B —— C
|
D
```

with edges `{A, B}`, `{B, C}`, and `{A, D}`. Its adjacency lists are

```text
A: B, D
B: A, C
C: B
D: A
```

```python
from umd_discrete import Graph

graph = Graph[str]()
graph.add_edge("A", "B")
graph.add_edge("B", "C")
graph.add_edge("A", "D")
```

## Degree

The **degree** of a vertex is the number of edge ends that touch it. In the
running graph:

```text
deg(A) = 2,  deg(B) = 2,  deg(C) = 1,  deg(D) = 1.
```

`C` and `D` are leaves. `A` and `B` are not.

### Worked example: the handshaking lemma

Each edge has two ends, so the sum of the degrees equals twice the number
of edges:

```text
2 + 2 + 1 + 1 = 6 = 2 * 3.
```

A self-loop has two ends at the same vertex. The implementation counts it
once as an edge and twice in the degree: a lone loop on `A` has
`edge_count() == 1` and `degree("A") == 2`, and the lemma still reads
`2 = 2 * 1`.

In a directed graph the same double count splits. The **out-degree** is
the number of edges leaving a vertex. The **in-degree** is the number
entering it. A loop contributes one to each. The sums equal the number of
directed edges:

```text
sum of in-degrees = sum of out-degrees = number of directed edges.
```

On the directed graph `A → B`, `B → B`, `B → C` the degrees are

```text
in(A) = 0, out(A) = 1
in(B) = 2, out(B) = 2
in(C) = 1, out(C) = 0
```

and both sums are 3, the number of edges. `degree` is reserved for
undirected graphs so those two conventions are not mixed in one method.

## Walks, paths, and cycles

A **walk** is a sequence of vertices in which each consecutive pair is an
edge. A **path** is a walk that does not repeat a vertex. A **cycle** is a
walk of length at least 1 that returns to its start and does not repeat
other vertices. Length counts edges.

`has_path(source, target)` reports whether any path exists. Every vertex
has a trivial path to itself, the path of length 0, including an isolated
vertex. Directed search follows arrows. Undirected search may use an edge
in either direction. Search marks visited vertices, so a cycle cannot make
the walk run forever.

### Worked example

In the running graph, `D, A, B, C` is a path from `D` to `C`. It is a walk,
and the vertices are distinct. There is no cycle: every walk that tries to
return has to repeat `A` or `B` and then stop, and no edge closes a loop.
`has_path("D", "C")` is true.

The triangle `A—B—C—A` does contain a cycle, `A, B, C, A`. The path
`A, B, C` is still a path; the extra edge `{C, A}` is what creates the
cycle. Existence of a path and existence of a cycle are different
questions. The package answers the first directly. The second shows up
below as a failed 2-coloring, and, for directed graphs, as a failed
topological sort.

## Connectedness and components

An undirected graph is **connected** when a path joins every pair of
vertices. A **connected component** is a maximal connected piece. Isolated
vertices are components of size one. The empty graph has no components.

### Worked example

The running graph is connected. It has one component, `{A, B, C, D}`.

The graph

```text
A —— B      C —— D
```

has two components, `{A, B}` and `{C, D}`. `has_path("A", "B")` is true.
`has_path("A", "C")` is false. Adding an isolated vertex beside one edge
produces the same picture at a smaller scale: `{A, B}` and `{C}`.

For a directed graph the method returns **weak** components. Direction is
forgotten, and then the undirected components are computed. In

```text
A → B      C
```

the weak components are `{A, B}` and `{C}`. There is a directed path from
`A` to `B` and none from `B` to `A`. Weak connectivity does not claim
directed reachability.

**Strong connectivity** is the other relation: every vertex can reach
every other vertex by a directed path. A directed 3-cycle is strongly
connected. The graph `A → B` with an isolated `C` is not. Strong
components are not computed here. The path method is the directed question
the package does answer, one pair at a time.

## Bipartite graphs

A graph is **bipartite** when its vertices split into two sets such that
every edge has one end in each set. Equivalently, the vertices can be
colored with two colors so that every edge joins different colors.
Equivalently, there is no odd cycle. The empty graph is bipartite. A
self-loop is a cycle of length 1, so a graph with a loop is not bipartite.
A disconnected graph is bipartite exactly when every component is.

Direction is ignored. The algorithm is breadth-first 2-coloring, restarted
on each new component.

### Worked example

Color the 4-cycle `A—B—C—D—A`:

```text
A color 0,  B color 1,  C color 0,  D color 1.
```

The parts are `{A, C}` and `{B, D}`. No edge stays inside a part. The
square is bipartite.

Now the triangle `A—B—C—A`. Start `A` at color 0. Then `B` and the coloring
forced along the path put `C` at color 0 if `C` is reached from `A`, or the
edge `{B, C}` joins two vertices that both had to take color 1. Either way
the last edge joins equals. The triangle is not bipartite. One odd cycle
is a complete obstruction.

The running tree is bipartite even though it is not a single edge. Color
`A` and `C` with 0, and `B` and `D` with 1. The parts `{A, C}` and `{B, D}`
have no internal edge.

## Directed acyclic graphs and topological order

A **directed acyclic graph** (DAG) is a directed graph with no directed
cycle. A **topological order** is a list of all the vertices such that
every directed edge goes forward in the list: if `u → v` is an edge, then
`u` appears before `v`.

A directed graph has a topological order exactly when it is a DAG. Kahn's
algorithm builds one. Repeatedly take a vertex of in-degree zero, append
it, and delete its outgoing edges (by decreasing the in-degrees of its
successors). If every vertex is appended, the list is a topological order.
If some vertices remain and none of them has in-degree zero, those vertices
sit on a directed cycle, and the method raises `CycleError`. An undirected
graph has no direction for "forward", so topological sort raises
`GraphError` there.

When several vertices have in-degree zero, this implementation takes the
one that was inserted earlier. The mathematical order need not be unique.
The algorithm returns one valid order.

### Worked example

```text
A → B → D
↓       ↑
C ——————
```

Edges: `A → B`, `A → C`, `B → D`, `C → D`. There is no directed cycle.
`A` must come first. `D` must come last. `B` and `C` may swap. Both of
these lists are topological orders:

```text
A, B, C, D
A, C, B, D
```

If the vertices are inserted in the order `A, B, C, D` and the edges are
added as listed above, Kahn's algorithm returns `("A", "B", "C", "D")`.
`has_path("A", "D")` is true. `has_path("D", "A")` is false. `has_path("B", "C")`
is false: the diamond meets at `D` and does not cross from `B` to `C`.

Add `D → A`. The graph is now a directed cycle through all four vertices.
In-degrees never fall in a way that releases every vertex, and topological
sort raises `CycleError`. A single loop `A → A` is already a directed
cycle, and it fails the same way.

The underlying undirected graph of the diamond is the 4-cycle
`A—B—D—C—A`, which is bipartite. Acyclic as a directed graph and cyclic
as an undirected graph are compatible. Topological sort cares about the
directed reading only.
