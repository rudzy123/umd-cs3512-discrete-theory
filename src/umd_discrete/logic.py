"""Propositional formulas, truth tables, and semantic checks.

A formula is a finite tree built from variables, the constants true and false,
and the connectives not, and, or, implication, and biconditional. Each formula
of ``n`` variables has ``2**n`` truth assignments. Exhaustive evaluation is
therefore a decision procedure for tautology, contradiction, satisfiability,
and equivalence of the formulas this module can build.

The procedure is exponential in the number of variables. It answers
propositional questions only. It does not decide predicate logic.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

MAX_TRUTH_TABLE_VARIABLES: Final = 12


class Formula(ABC):
    """A propositional formula that can be evaluated under a truth assignment."""

    def variables(self) -> tuple[str, ...]:
        """Return variable names in left-to-right order of first appearance."""
        found: dict[str, None] = {}
        self._collect_variables(found)
        return tuple(found)

    @abstractmethod
    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        """Return the truth value of this formula under ``assignment``."""

    @abstractmethod
    def _collect_variables(self, found: dict[str, None]) -> None:
        """Insert variable names into ``found`` in order of first appearance."""

    def __invert__(self) -> "Not":
        return Not(self)

    def __and__(self, other: "Formula") -> "And":
        return And(self, _ensure_formula(other))

    def __or__(self, other: "Formula") -> "Or":
        return Or(self, _ensure_formula(other))

    def implies(self, other: "Formula") -> "Implies":
        """Return the implication ``self -> other``."""
        return Implies(self, _ensure_formula(other))

    def iff(self, other: "Formula") -> "Iff":
        """Return the biconditional ``self <-> other``."""
        return Iff(self, _ensure_formula(other))


def _ensure_formula(value: object) -> Formula:
    if not isinstance(value, Formula):
        raise TypeError("logical operands must be formulas")
    return value


@dataclass(frozen=True)
class Variable(Formula):
    """A propositional variable, such as ``P``."""

    name: str

    def __post_init__(self) -> None:
        if type(self.name) is not str or not self.name.isidentifier():
            raise ValueError("variable name must be an identifier, for example P or q1")

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        try:
            return assignment[self.name]
        except KeyError as exc:
            raise KeyError(f"no truth value for variable {self.name!r}") from exc

    def _collect_variables(self, found: dict[str, None]) -> None:
        found.setdefault(self.name, None)

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Constant(Formula):
    """The constant true or the constant false."""

    value: bool

    def __post_init__(self) -> None:
        if type(self.value) is not bool:
            raise TypeError("constant value must be True or False")

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        # The value does not depend on the assignment.
        return self.value

    def _collect_variables(self, found: dict[str, None]) -> None:
        # A constant contributes no variables.
        return

    def __str__(self) -> str:
        return "T" if self.value else "F"


TRUE: Constant = Constant(True)
FALSE: Constant = Constant(False)


@dataclass(frozen=True)
class Not(Formula):
    """Negation. ``~A`` is true exactly when ``A`` is false."""

    operand: Formula

    def __post_init__(self) -> None:
        _ensure_formula(self.operand)

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return not self.operand.evaluate(assignment)

    def _collect_variables(self, found: dict[str, None]) -> None:
        self.operand._collect_variables(found)

    def __str__(self) -> str:
        return f"~{self.operand}"


@dataclass(frozen=True)
class And(Formula):
    """Conjunction. ``A & B`` is true exactly when both operands are true."""

    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _ensure_formula(self.left)
        _ensure_formula(self.right)

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return self.left.evaluate(assignment) and self.right.evaluate(assignment)

    def _collect_variables(self, found: dict[str, None]) -> None:
        self.left._collect_variables(found)
        self.right._collect_variables(found)

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


@dataclass(frozen=True)
class Or(Formula):
    """Inclusive disjunction. ``A | B`` is false only when both are false."""

    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _ensure_formula(self.left)
        _ensure_formula(self.right)

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return self.left.evaluate(assignment) or self.right.evaluate(assignment)

    def _collect_variables(self, found: dict[str, None]) -> None:
        self.left._collect_variables(found)
        self.right._collect_variables(found)

    def __str__(self) -> str:
        return f"({self.left} | {self.right})"


@dataclass(frozen=True)
class Implies(Formula):
    """Implication. ``A -> B`` is false only when ``A`` is true and ``B`` is false."""

    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _ensure_formula(self.left)
        _ensure_formula(self.right)

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return (not self.left.evaluate(assignment)) or self.right.evaluate(assignment)

    def _collect_variables(self, found: dict[str, None]) -> None:
        self.left._collect_variables(found)
        self.right._collect_variables(found)

    def __str__(self) -> str:
        return f"({self.left} -> {self.right})"


@dataclass(frozen=True)
class Iff(Formula):
    """Biconditional. ``A <-> B`` is true exactly when the operands agree."""

    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _ensure_formula(self.left)
        _ensure_formula(self.right)

    def evaluate(self, assignment: Mapping[str, bool]) -> bool:
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)

    def _collect_variables(self, found: dict[str, None]) -> None:
        self.left._collect_variables(found)
        self.right._collect_variables(found)

    def __str__(self) -> str:
        return f"({self.left} <-> {self.right})"


@dataclass(frozen=True)
class TruthTableRow:
    """One truth assignment together with the formula's value."""

    assignment: tuple[tuple[str, bool], ...]
    value: bool


@dataclass(frozen=True)
class TruthTable:
    """Every truth assignment of a formula, in binary counting order.

    The first variable is the most significant bit. The first row assigns
    false to every variable.
    """

    variables: tuple[str, ...]
    rows: tuple[TruthTableRow, ...]

    def values(self) -> tuple[bool, ...]:
        """Return the formula column from top to bottom."""
        return tuple(row.value for row in self.rows)


def _assignment_maps(variables: tuple[str, ...]) -> tuple[dict[str, bool], ...]:
    if len(variables) > MAX_TRUTH_TABLE_VARIABLES:
        raise ValueError(
            "truth tables are limited to "
            f"{MAX_TRUTH_TABLE_VARIABLES} variables; found {len(variables)}"
        )
    width = len(variables)
    maps: list[dict[str, bool]] = []
    for mask in range(1 << width):
        maps.append(
            {
                name: bool(mask & (1 << (width - 1 - index)))
                for index, name in enumerate(variables)
            }
        )
    return tuple(maps)


def truth_table(formula: Formula) -> TruthTable:
    """Build the full truth table of ``formula``.

    A formula with no variables has one row: the empty assignment.
    """
    names = formula.variables()
    rows = tuple(
        TruthTableRow(tuple(assignment.items()), formula.evaluate(assignment))
        for assignment in _assignment_maps(names)
    )
    return TruthTable(names, rows)


def render_truth_table(formula: Formula) -> str:
    """Return ``formula``'s truth table as aligned text.

    ``T`` and ``F`` stand for true and false. A constant formula is one line
    of the form ``T | T`` or ``F | F``.
    """
    table = truth_table(formula)
    formula_text = str(formula)
    if not table.variables:
        value = "T" if table.rows[0].value else "F"
        return f"{formula_text} | {value}"
    widths = [len(name) for name in table.variables]
    header = " ".join(
        name.ljust(width) for name, width in zip(table.variables, widths, strict=True)
    )
    lines = [f"{header} | {formula_text}"]
    for row in table.rows:
        cells = " ".join(
            ("T" if bit else "F").ljust(width)
            for (_, bit), width in zip(row.assignment, widths, strict=True)
        )
        lines.append(f"{cells} | {'T' if row.value else 'F'}")
    return "\n".join(lines)


def is_tautology(formula: Formula) -> bool:
    """Return whether ``formula`` is true under every assignment.

    ``P | ~P`` is a tautology. The variable ``P`` is not.
    """
    return all(row.value for row in truth_table(formula).rows)


def is_contradiction(formula: Formula) -> bool:
    """Return whether ``formula`` is false under every assignment.

    ``P & ~P`` is a contradiction. A contradiction is not satisfiable.
    """
    return not any(row.value for row in truth_table(formula).rows)


def is_satisfiable(formula: Formula) -> bool:
    """Return whether at least one assignment makes ``formula`` true.

    Every tautology is satisfiable. A contradiction is not.
    """
    return any(row.value for row in truth_table(formula).rows)


def satisfying_assignments(
    formula: Formula,
) -> tuple[tuple[tuple[str, bool], ...], ...]:
    """Return the assignments that make ``formula`` true."""
    return tuple(row.assignment for row in truth_table(formula).rows if row.value)


def equivalent(left: Formula, right: Formula) -> bool:
    """Return whether ``left`` and ``right`` agree on every shared assignment.

    The checked variables are the union of the two variable sets. A formula
    ignores variables it does not contain, so ``P | ~P`` is equivalent to the
    constant ``TRUE``. Structural equality (``==``) is a different relation:
    ``P | Q`` and ``Q | P`` are equivalent and not the same tree.
    """
    names = tuple(dict.fromkeys((*left.variables(), *right.variables())))
    return all(
        left.evaluate(assignment) == right.evaluate(assignment)
        for assignment in _assignment_maps(names)
    )
