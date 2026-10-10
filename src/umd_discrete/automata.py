"""Deterministic finite automata and two sample languages.

A DFA is a finite set of states, a finite alphabet of single characters, a
total transition function, a start state, and a set of accepting states. On
an input string the machine reads one character at a time and follows the
unique transition for its current state and that character. The string is
accepted when the run ends in an accepting state. The empty string is
accepted exactly when the start state is accepting.

A symbol that is not in the alphabet is not an input of the machine.
:meth:`DFA.accepts` raises :class:`InvalidSymbolError` for it. A string over
the alphabet that ends in a non-accepting state is rejected, which is an
ordinary ``False`` result, not an error. Sample machines include a dead
state when they need one so the transition function stays total.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from typing import Self


class AutomatonError(Exception):
    """Raised when a string is not an input of a DFA."""


class InvalidSymbolError(AutomatonError):
    """Raised when a character is outside the automaton's alphabet."""


@dataclass(frozen=True)
class DFA:
    """Deterministic finite automaton over single-character symbols.

    Build machines with :meth:`from_table`. The stored ``transitions`` tuple
    lists triples ``(state, symbol, target)``. Equality compares that stored
    structure. :meth:`from_table` sorts triples so two tables with the same
    function compare equal.
    """

    states: frozenset[str]
    alphabet: frozenset[str]
    transitions: tuple[tuple[str, str, str], ...]
    start: str
    accepting: frozenset[str]

    def __post_init__(self) -> None:
        if not self.states:
            raise ValueError("a DFA must have at least one state")
        for state in self.states:
            if type(state) is not str or state == "":
                raise ValueError("state names must be non-empty strings")
        if self.start not in self.states:
            raise ValueError("start state must belong to the state set")
        if not self.accepting <= self.states:
            raise ValueError("accepting states must be a subset of the states")
        for symbol in self.alphabet:
            if type(symbol) is not str or len(symbol) != 1:
                raise ValueError(
                    f"alphabet symbols must be single characters; found {symbol!r}"
                )
        seen: dict[tuple[str, str], str] = {}
        for state, symbol, target in self.transitions:
            if state not in self.states:
                raise ValueError(f"transition state {state!r} is not in the state set")
            if symbol not in self.alphabet:
                raise ValueError(f"transition symbol {symbol!r} is not in the alphabet")
            if target not in self.states:
                raise ValueError(
                    f"transition target {target!r} is not in the state set"
                )
            key = (state, symbol)
            if key in seen:
                raise ValueError(
                    f"duplicate transition for state {state!r} and symbol {symbol!r}"
                )
            seen[key] = target
        expected = {
            (state, symbol) for state in self.states for symbol in self.alphabet
        }
        missing = expected - set(seen)
        if missing:
            sample = sorted(missing)[:3]
            raise ValueError(
                "transition function must be total; "
                f"missing {len(missing)} pair(s), including {sample!r}"
            )

    @classmethod
    def from_table(
        cls,
        *,
        states: Iterable[str],
        alphabet: Iterable[str],
        transitions: Mapping[tuple[str, str], str],
        start: str,
        accepting: Iterable[str],
    ) -> Self:
        """Build a DFA from a total map ``(state, symbol) -> state``."""
        state_set = frozenset(states)
        alphabet_set = frozenset(alphabet)
        table = dict(transitions)
        expected = {(state, symbol) for state in state_set for symbol in alphabet_set}
        if set(table) != expected:
            missing = sorted(expected - set(table))
            extra = sorted(set(table) - expected)
            raise ValueError(
                "transition function must assign each state-symbol pair one target; "
                f"missing {missing!r}; extra {extra!r}"
            )
        triples = tuple(
            (state, symbol, table[(state, symbol)])
            for state in sorted(state_set)
            for symbol in sorted(alphabet_set)
        )
        return cls(
            states=state_set,
            alphabet=alphabet_set,
            transitions=triples,
            start=start,
            accepting=frozenset(accepting),
        )

    def transition(self, state: str, symbol: str) -> str:
        """Return the unique successor of ``state`` on ``symbol``."""
        if state not in self.states:
            raise ValueError(f"unknown state {state!r}")
        if symbol not in self.alphabet:
            raise InvalidSymbolError(f"symbol {symbol!r} is not in the alphabet")
        return _index(self.transitions)[(state, symbol)]

    def run(self, text: str) -> str:
        """Return the state reached by reading ``text`` from the start state."""
        if type(text) is not str:
            raise TypeError("DFA input must be a string")
        state = self.start
        for symbol in text:
            state = self.transition(state, symbol)
        return state

    def accepts(self, text: str) -> bool:
        """Return whether the run of ``text`` ends in an accepting state."""
        return self.run(text) in self.accepting

    def complement(self) -> "DFA":
        """Return a DFA for the complement language over the same alphabet.

        Accepting and non-accepting states are swapped. Symbols outside the
        alphabet still raise :class:`InvalidSymbolError`. Applying complement
        twice restores the original machine.
        """
        return DFA(
            states=self.states,
            alphabet=self.alphabet,
            transitions=self.transitions,
            start=self.start,
            accepting=self.states - self.accepting,
        )


@cache
def _index(
    transitions: tuple[tuple[str, str, str], ...],
) -> dict[tuple[str, str], str]:
    return {(state, symbol): target for state, symbol, target in transitions}


def even_ones_dfa() -> DFA:
    """Return a DFA for binary strings with an even number of ``1`` symbols.

    The state records the parity of the ones read so far. ``even`` is the
    start state and the only accepting state, so the empty string is accepted.
    Reading ``1`` flips the state. Reading ``0`` keeps it. The invariant proof
    that this decides the language is in ``docs/automata.md``.
    """
    return DFA.from_table(
        states={"even", "odd"},
        alphabet={"0", "1"},
        transitions={
            ("even", "0"): "even",
            ("even", "1"): "odd",
            ("odd", "0"): "odd",
            ("odd", "1"): "even",
        },
        start="even",
        accepting={"even"},
    )


def identifier_dfa() -> DFA:
    """Return a DFA for identifiers shaped like ``[A-Za-z_][A-Za-z0-9_]*``.

    The machine checks lexical shape only. It does not treat keywords as
    reserved words, so ``if`` is accepted. A digit in the start state moves
    to the rejecting sink ``sink``, because a DFA must have a transition for
    every symbol in its alphabet. The empty string is rejected. Characters
    such as ``-`` or a space are outside the alphabet and raise
    :class:`InvalidSymbolError`.
    """
    starters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
    digits = "0123456789"
    alphabet = set(starters + digits)
    transitions: dict[tuple[str, str], str] = {}
    for symbol in alphabet:
        transitions[("start", symbol)] = "body" if symbol in starters else "sink"
        transitions[("body", symbol)] = "body"
        transitions[("sink", symbol)] = "sink"
    return DFA.from_table(
        states={"start", "body", "sink"},
        alphabet=alphabet,
        transitions=transitions,
        start="start",
        accepting={"body"},
    )
