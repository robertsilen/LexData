#!/usr/bin/env python3
from pathlib import Path

import pytest

import LexData


@pytest.fixture
def credentials():
    with open(Path.home() / ".wikipass") as f:
        userename, password, *_ = f.read().split("\n")
    return (userename, password)


@pytest.fixture
def repo(credentials):
    username, password = credentials
    return LexData.WikidataSession(username, password)


def test_auth(credentials):
    with pytest.raises(Exception):
        assert LexData.WikidataSession("Username", "Password")
    anon = LexData.WikidataSession()
    LexData.Lexeme(anon, "L2")
    # anon.maxlag = 1
    # LexData.Lexeme(anon, "L2")


def test_lexeme(repo):
    L2 = LexData.Lexeme(repo, "L2")

    assert L2.lemma == "first"
    assert L2.language == "en"
    claims = L2.claims
    assert isinstance(claims, dict)

    examples = claims.get("P5831", [])
    assert len(examples) >= 1
    example = examples[0]
    assert isinstance(repr(example), str)
    assert example.property == "P5831"
    assert example.rank == "normal"
    assert example.numeric_rank == 0
    assert example.type == "monolingualtext"
    assert example.pure_value == "He was first in line."
    assert example.value["text"] == "He was first in line."
    assert example.value["language"] == "en"


def test_sense(repo):
    L2 = LexData.Lexeme(repo, "L2")
    assert str(L2)
    assert repr(L2)

    senses = L2.senses
    assert isinstance(senses, list)
    for sense in senses:
        assert isinstance(repr(sense), str)
        assert isinstance(sense.glosse(), str)
        assert isinstance(sense.glosse("de"), str)
        assert sense.glosse("en") == sense.glosse()
        assert sense.glosse("XX") == sense.glosse()
        del sense["glosses"]["en"]
        assert isinstance(sense.glosse("XX"), str)
        assert isinstance(sense.claims, dict)


def test_form(repo):
    L2 = LexData.Lexeme(repo, "L2")
    forms = L2.forms
    assert isinstance(forms, list)
    for form in forms:
        assert isinstance(repr(form), str)
        assert isinstance(form.form, str)
        assert isinstance(form.claims, dict)


def test_writes(repo):
    # L123 is a sanbox lexeme, we can edit it
    L123 = LexData.Lexeme(repo, "L123")

    L123.createClaims({"P369": ["Q1"]})

    fid = L123.createForm("test", ["Q860"])

    L123.createSense({"de": "testtest", "en": "testtest"})
    L123.createSense({"de": "more tests", "en": "more tests"}, claims={})
    L123.createSense({"en": "even more tests"}, claims={"P369": ["Q1"]})


def test_search(repo):
    results = LexData.search_lexemes(repo, "first", LexData.language.en, "Q1084")
    assert len(results) == 1
    assert results[0].get("id") == "L2"

    result = LexData.get_or_create_lexeme(repo, "first", LexData.language.en, "Q1084")
    assert result["id"] == "L2"
