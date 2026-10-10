"""Propositional identities, truth tables, and semantic classification."""

import pytest

from umd_discrete.logic import (
    FALSE,
    MAX_TRUTH_TABLE_VARIABLES,
    TRUE,
    And,
    Constant,
    Formula,
    Not,
    Or,
    Variable,
    equivalent,
    is_contradiction,
    is_satisfiable,
    is_tautology,
    render_truth_table,
    satisfying_assignments,
    truth_table,
)

p = Variable("P")
q = Variable("Q")
r = Variable("R")


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (~(p & q), ~p | ~q),
        (~(p | q), ~p & ~q),
        (p.implies(q), ~p | q),
        (p.iff(q), p.implies(q) & q.implies(p)),
        (p.implies(q), (~q).implies(~p)),
        (~~p, p),
        (p & p, p),
        (p | p, p),
        (p & q, q & p),
        (p | q, q | p),
        ((p & q) & r, p & (q & r)),
        ((p | q) | r, p | (q | r)),
        (p & (q | r), (p & q) | (p & r)),
        (p | (q & r), (p | q) & (p | r)),
        (p & (p | q), p),
        (p | (p & q), p),
        (p | FALSE, p),
        (p & TRUE, p),
        (p | TRUE, TRUE),
        (p & FALSE, FALSE),
        (p | ~p, TRUE),
        (p & ~p, FALSE),
        (~TRUE, FALSE),
    ],
)
def test_logical_identities(left: Formula, right: Formula) -> None:
    assert equivalent(left, right)


@pytest.mark.parametrize(
    ("formula", "expected"),
    [
        (p & q, (False, False, False, True)),
        (p | q, (False, True, True, True)),
        (p.implies(q), (True, True, False, True)),
        (p.iff(q), (True, False, False, True)),
        (~p, (True, False)),
        (TRUE, (True,)),
        (FALSE, (False,)),
        (~TRUE, (False,)),
    ],
)
def test_truth_table_columns(formula: Formula, expected: tuple[bool, ...]) -> None:
    assert truth_table(formula).values() == expected


def test_truth_table_lists_every_assignment() -> None:
    table = truth_table(p & q)
    assert table.variables == ("P", "Q")
    assert len(table.rows) == 4
    assert table.rows[0].assignment == (("P", False), ("Q", False))
    assert table.rows[3].assignment == (("P", True), ("Q", True))
    assert (p & p).variables() == ("P",)
    assert len(truth_table(p & p).rows) == 2
    assert TRUE.variables() == ()


def test_implication_table_renders_in_textbook_order() -> None:
    assert render_truth_table(p.implies(q)) == "\n".join(
        [
            "P Q | (P -> Q)",
            "F F | T",
            "F T | T",
            "T F | F",
            "T T | T",
        ]
    )
    assert render_truth_table(TRUE) == "T | T"
    assert render_truth_table(FALSE) == "F | F"


def test_excluded_middle_is_a_satisfiable_tautology() -> None:
    formula = p | ~p
    assert is_tautology(formula)
    assert is_satisfiable(formula)
    assert not is_contradiction(formula)
    assert len(satisfying_assignments(formula)) == 2


def test_contradiction_is_not_satisfiable() -> None:
    formula = p & ~p
    assert is_contradiction(formula)
    assert not is_satisfiable(formula)
    assert not is_tautology(formula)
    assert satisfying_assignments(formula) == ()


def test_contingency_is_satisfiable_and_not_a_tautology() -> None:
    assert is_satisfiable(p)
    assert not is_tautology(p)
    assert not is_contradiction(p)
    assert satisfying_assignments(p & q) == ((("P", True), ("Q", True)),)


def test_syntactic_equality_is_not_equivalence() -> None:
    assert (p | q) != (q | p)
    assert equivalent(p | q, q | p)


def test_operator_precedence_matches_python() -> None:
    assert (~p & q) == And(Not(p), q)
    assert (p | q & r) == Or(p, And(q, r))
    assert str(~(p & q)) == "~(P & Q)"
    assert str(~~p) == "~~P"


def test_truth_table_rejects_too_many_variables() -> None:
    formula: Formula = Variable("v0")
    for index in range(1, MAX_TRUTH_TABLE_VARIABLES + 1):
        formula = formula & Variable(f"v{index}")
    with pytest.raises(ValueError, match=str(MAX_TRUTH_TABLE_VARIABLES)):
        truth_table(formula)


def test_missing_assignment_names_the_variable() -> None:
    with pytest.raises(KeyError, match="P"):
        p.evaluate({})


@pytest.mark.parametrize("name", ["", "1P", "P Q", "P-Q"])
def test_variable_name_must_be_an_identifier(name: str) -> None:
    with pytest.raises(ValueError, match="identifier"):
        Variable(name)


def test_constant_rejects_non_bool() -> None:
    with pytest.raises(TypeError, match="True or False"):
        Constant(1)  # type: ignore[arg-type]
