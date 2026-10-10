# umd-cs3512-discrete-theory

Executable models for a discrete mathematics and automata refresher.
Propositional formulas, finite sets, counting, graphs, and deterministic
finite automata are small Python objects. The tests check the definitions.
The notes in `docs/` carry the proofs.

A check that exhausts a finite space decides that instance. A truth table
proves a propositional equivalence. A relation check proves the properties of
that relation. A test that samples Fibonacci numbers does not prove the
recurrence for every `n`. The distinction is spelled out in
[the learning log](docs/learning-log.md).

## Requirements

Python 3.12. The package uses the language's built-in generic syntax
(`Graph[str]`, `def union[T: Hashable]`).

## Install

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quick start

```python
from umd_discrete import Variable, equivalent, is_tautology

p = Variable("P")
q = Variable("Q")
assert equivalent(~(p & q), ~p | ~q)
assert is_tautology(p | ~p)
```

```python
from umd_discrete import is_equivalence_relation, power_set

assert power_set({"a"}) == {frozenset(), frozenset({"a"})}
relation = {(1, 1), (2, 2), (1, 2), (2, 1)}
assert is_equivalence_relation(relation, {1, 2})
```

```python
from umd_discrete import combination_count, pascal_triangle

assert combination_count(5, 2) == 10
assert pascal_triangle(3) == ((1,), (1, 1), (1, 2, 1))
```

```python
from umd_discrete import Graph

graph = Graph[str]()
graph.add_edge("a", "b")
graph.add_edge("b", "c")
assert graph.has_path("a", "c")
assert graph.connected_components() == (frozenset({"a", "b", "c"}),)
```

```python
from umd_discrete import even_ones_dfa, identifier_dfa

assert even_ones_dfa().accepts("110")
assert not even_ones_dfa().accepts("10")
assert identifier_dfa().accepts("a1")
assert not identifier_dfa().accepts("1a")
```

`&` binds tighter than `|` because those are Python operators. Implication
and the biconditional are methods: `p.implies(q)` and `p.iff(q)`. When the
tree matters, build it with `And`, `Or`, `Implies`, and `Iff`.

## Layout

```text
.
├── .github/workflows/ci.yml
├── docs/
│   ├── logic.md
│   ├── proof-techniques.md
│   ├── sets-relations-functions.md
│   ├── graph-theory.md
│   ├── automata.md
│   └── learning-log.md
├── src/umd_discrete/
│   ├── logic.py
│   ├── sets.py
│   ├── combinatorics.py
│   ├── graphs.py
│   └── automata.py
├── tests/
├── pyproject.toml
├── README.md
└── COMMIT_MESSAGE.md
```

Enumerations are capped so a teaching call cannot try to build `10!` tuples
or a truth table of dozens of variables. `permutation_count` and
`combination_count` still return the number. The caps are
`MAX_TRUTH_TABLE_VARIABLES`, `MAX_POWER_SET_ELEMENTS`, and
`MAX_ENUMERATED_RESULTS`.

## Reading order

1. [Propositions, predicates, and quantifiers](docs/logic.md)
2. [Direct proof, contradiction, contrapositive, and induction](docs/proof-techniques.md)
3. [Sets, relations, functions, and counting](docs/sets-relations-functions.md)
4. [Graph vocabulary and the basic algorithms](docs/graph-theory.md)
5. [Regular languages and finite automata](docs/automata.md)
6. [Learning log](docs/learning-log.md)

## Quality checks

The same commands run in GitHub Actions on Python 3.12:

```bash
ruff format --check .
ruff check .
mypy
pytest
```

## License

MIT. See [LICENSE](LICENSE).
