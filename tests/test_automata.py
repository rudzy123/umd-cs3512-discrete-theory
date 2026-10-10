"""Acceptance, rejection, and the two sample deterministic automata."""

import itertools

import pytest

from umd_discrete.automata import (
    DFA,
    AutomatonError,
    InvalidSymbolError,
    even_ones_dfa,
    identifier_dfa,
)

EVEN_ONES_STRINGS = tuple(
    "".join(bits)
    for length in range(7)
    for bits in itertools.product("01", repeat=length)
)


@pytest.mark.parametrize("text", EVEN_ONES_STRINGS)
def test_even_ones_invariant(text: str) -> None:
    machine = even_ones_dfa()
    state = machine.run(text)
    even = text.count("1") % 2 == 0
    assert state == ("even" if even else "odd")
    assert machine.accepts(text) == even


@pytest.mark.parametrize("text", ["", "0", "11", "101", "110", "0110"])
def test_even_ones_accepts_documented_strings(text: str) -> None:
    assert even_ones_dfa().accepts(text)


@pytest.mark.parametrize("text", ["1", "10", "111", "001"])
def test_even_ones_rejects_documented_strings(text: str) -> None:
    assert not even_ones_dfa().accepts(text)


@pytest.mark.parametrize("text", ["2", "a", " ", "01b"])
def test_even_ones_rejects_foreign_symbols(text: str) -> None:
    with pytest.raises(InvalidSymbolError):
        even_ones_dfa().accepts(text)


def test_complement_swaps_parity_and_double_complement_is_identity() -> None:
    even = even_ones_dfa()
    odd = even.complement()
    assert odd.accepts("1")
    assert not odd.accepts("")
    assert odd.complement() == even
    for text in EVEN_ONES_STRINGS:
        assert odd.accepts(text) != even.accepts(text)


@pytest.mark.parametrize("text", ["a", "Z", "_", "a0", "_A1", "if", "Ab_3"])
def test_identifier_acceptance(text: str) -> None:
    assert identifier_dfa().accepts(text)


@pytest.mark.parametrize("text", ["", "0", "9abc", "0_"])
def test_identifier_rejects_strings_over_its_alphabet(text: str) -> None:
    assert not identifier_dfa().accepts(text)


@pytest.mark.parametrize("text", ["a-b", "a b", "hello!", "é"])
def test_identifier_rejects_foreign_symbols(text: str) -> None:
    with pytest.raises(InvalidSymbolError):
        identifier_dfa().accepts(text)


def test_identifier_trace() -> None:
    machine = identifier_dfa()
    assert machine.run("") == "start"
    assert machine.run("a1") == "body"
    assert machine.run("1a") == "sink"
    assert machine.start == "start"
    assert machine.accepting == frozenset({"body"})


def test_invalid_symbol_error_is_an_automaton_error() -> None:
    assert issubclass(InvalidSymbolError, AutomatonError)


def test_sample_machines_are_stable() -> None:
    assert even_ones_dfa() == even_ones_dfa()
    assert identifier_dfa() == identifier_dfa()


def test_incomplete_transition_function_is_rejected() -> None:
    with pytest.raises(ValueError, match="missing"):
        DFA.from_table(
            states={"q"},
            alphabet={"a"},
            transitions={},
            start="q",
            accepting=set(),
        )


def test_duplicate_transition_is_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        DFA(
            states=frozenset({"q"}),
            alphabet=frozenset({"a", "b"}),
            transitions=(("q", "a", "q"), ("q", "a", "q"), ("q", "b", "q")),
            start="q",
            accepting=frozenset(),
        )


def test_multi_character_symbol_is_rejected() -> None:
    with pytest.raises(ValueError, match="single characters"):
        DFA.from_table(
            states={"q"},
            alphabet={"ab"},
            transitions={("q", "ab"): "q"},
            start="q",
            accepting=set(),
        )


def test_input_must_be_a_string() -> None:
    with pytest.raises(TypeError, match="string"):
        even_ones_dfa().accepts(None)  # type: ignore[arg-type]
