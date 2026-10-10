# Learning log

## 2026-10-10 — Executable discrete mathematics

This refresher connects five finite models. Each one is small enough to
read in an afternoon and strict enough that a wrong definition fails a
test.

### What the models are

- **Logic.** Formulas are trees. `truth_table` enumerates every assignment.
  Tautology, contradiction, satisfiability, and equivalence are readings of
  that table. De Morgan, the implication rewrite `P -> Q` as `~P | Q`, and
  the contrapositive are identities the table decides in full.
- **Proof.** Direct proof, contrapositive, contradiction, and induction are
  written out in `docs/proof-techniques.md`. The sum
  `0 + ... + n = n(n + 1) / 2` is the induction example. The code computes
  the sum from the recurrence. The note proves the closed form.
- **Sets and counting.** Union, intersection, difference, and power set are
  the set operations. Relation flags are the universal statements
  "reflexive", "symmetric", "antisymmetric", and "transitive", checked on
  one finite domain. Equivalence relations and partial orders are those
  flags composed. Functions are total maps into a stated codomain.
  Permutations, combinations, and Pascal's triangle are the counting
  companion, including the recurrence that builds each Pascal row from the
  row above.
- **Graphs.** An adjacency list supports degree, path existence, weak
  components, 2-coloring, and Kahn's topological sort. The handshaking
  lemma is the checksum: degree sums match twice the edges, and directed
  in-degrees match out-degrees.
- **Automata.** A DFA is states, alphabet, a total transition function, a
  start state, and accepting states. The even-ones machine is proved by
  induction on string length. The identifier machine separates "rejected
  string" from "symbol outside the alphabet". The language `0ⁿ1ⁿ` is proved
  non-regular by the pigeonhole principle.

### Evidence and proof

Use this test when reading a result in the repository:

| Question | What settles it |
| --- | --- |
| Is `~(P & Q)` equivalent to `~P \| ~Q`? | The four-row table. `equivalent` is a proof of that instance, and the schema argument in the logic note extends it to compound formulas. |
| Is this finite relation an equivalence? | `profile_relation` on that domain. The answer is about that relation only. |
| Does `S(n) = n(n + 1) / 2` for every `n`? | The induction. `test_sum_matches_closed_form` checks `n <= 30`. |
| Does the even-ones DFA accept the right language? | The state invariant, proved for every length. The exhaustive test through length 6 is the sample. |
| Is `0ⁿ1ⁿ` regular? | The pigeonhole argument. No test of one automaton can prove that every automaton fails. |

A finite exhaustive check is a decision procedure for the instance it
enumerates. A sample is not. An implementation of a recurrence matches the
recurrence by construction; a closed form still needs a proof.

### Checks to rerun

From the repository root, with the package installed:

```bash
pytest tests/test_logic.py::test_logical_identities -q
pytest tests/test_sets.py::test_relation_properties -q
pytest tests/test_sets.py::test_function_classifications -q
pytest tests/test_sets.py::test_empty_and_singleton_power_sets -q
pytest tests/test_graphs.py::test_topological_sort -q
pytest tests/test_graphs.py::test_connected_components -q
pytest tests/test_automata.py::test_even_ones_invariant -q
pytest tests/test_automata.py::test_identifier_acceptance -q
pytest tests/test_automata.py::test_identifier_rejects_foreign_symbols -q
```

`test_topological_sort` covers both acyclic graphs and directed cycles.
`test_connected_components` covers the disconnected examples, including a
directed edge that does not reach backward and an isolated vertex.

### Exercises

1. Print `render_truth_table(Variable("P").implies(Variable("Q")))` and
   mark the single row where the implication fails. That row is the
   definition of a broken promise.
2. Start from the equivalence
   `{(1, 1), (2, 2), (3, 3), (1, 2), (2, 1)}` on `{1, 2, 3}` and delete
   `(2, 2)`. Which flags in `profile_relation` change? Transitivity should
   fail, and reflexivity should fail. Symmetry should survive.
3. Trace `"110"` on the even-ones machine by hand, then compare with
   `even_ones_dfa().run("110")`. The state should be `even`.
4. Explain why `identifier_dfa().accepts("1a")` is false, while
   `identifier_dfa().accepts("a-b")` raises. One string is in the alphabet
   and ends in `sink`. The other leaves the alphabet at `-`.
5. Build a triangle, compute the three degrees by hand, and check that
   they sum to twice the number of edges. Then add a self-loop and do the
   arithmetic again. The loop contributes 2.
6. Name one result in the test suite that is an exhaustive proof and one
   that is only a sample. The table above is the answer key.

### Limits that are intentional

Predicate logic has no decision procedure that covers every sentence. This
package does not pretend to search infinite domains. Nondeterministic
automata, regular expressions, and automaton minimization are the usual
next constructions; only deterministic acceptance and complement are
implemented. Shortest paths, weights, and strong components are not in the
graph module. The topological sort and the path search are the directed
algorithms that are.

Enumeration caps (`MAX_TRUTH_TABLE_VARIABLES` is 12,
`MAX_POWER_SET_ELEMENTS` is 16, `MAX_ENUMERATED_RESULTS` is 10000) keep a
teaching call from allocating a huge table. Counting functions still
return the integer when the list of tuples would be too long.

### Next questions

- Where does the truth-table decision procedure become the wrong tool even
  though it is still correct? (When the number of variables grows. The
  answer stays defined. The table does not stay cheap.)
- Which graph relation is stronger than a weak component, and which
  example in the graph note separates them? (`A → B` with `C` beside it:
  `B` does not reach `A`, and they are still weakly connected.)
- Why does swapping accepting states complement a DFA, while "swap the
  start state" does not complement the language?
- The even-ones proof is an induction. Which sentence is the inductive
  hypothesis, and which sentence is the claim for one extra symbol?
