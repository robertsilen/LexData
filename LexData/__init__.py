# -*-coding:utf-8-*
import json
import logging

from .claim import Claim
from .form import Form
from .language import Language
from .lexeme import Lexeme
from .sense import Sense
from .wikidatasession import WikidataSession


def get_or_create_lexeme(repo, lemma: str, lang: Language, catLex: str) -> Lexeme:
    """Search for a lexeme in wikidata if not found, create it

    :param repo: Wikidata Session
    :type  repo: WikidataSession
    :param lemma: the lemma of the lexeme
    :type  lemma: str
    :param lang: language of the lexeme
    :type  lang: Language
    :param catLex: lexical Category of the lexeme
    :type  catLex: str
    :returns: Lexeme with the specified properties (created or found)
    :rtype: Lexeme

    """

    # the language we search in actually doesn't really matter
    # set it nevertheless, except if it is a Language without ISO code
    if lang.short[:3] == "mis":
        searchlang = "en"
    else:
        searchlang = lang.short

    PARAMS = {
        "action": "wbsearchentities",
        "language": searchlang,
        "type": "lexeme",
        "search": lemma,
        "format": "json",
    }

    DATA = repo.get(PARAMS)

    if "error" in DATA:
        raise Exception(DATA["error"])

    for item in DATA["search"]:
        # if the lexeme exists
        if item["label"] == lemma:
            idLex = item["id"]
            lexeme = Lexeme(repo, idLex)
            if lexeme["language"] == lang.qid and lexeme["lexicalCategory"] == catLex:
                logging.info("--Found lexeme, id = %s", idLex)
                return lexeme

    # Not found, create the lexeme
    return create_lexeme(repo, lemma, lang, catLex)


def create_lexeme(repo, lemma: str, lang: Language, catLex: str, claims=None) -> Lexeme:
    """Creates a lexeme

    :param repo: Wikidata Session
    :type  repo: WikidataSession
    :param lemma: value of the lexeme
    :type  lemma: str
    :param lang: language
    :type  lang: Language
    :param catLex: lexicographical category
    :param claims: claims to add to the lexeme (Default value = None) -> Lexem)
    :type  catLex: str
    :returns: The created Lexeme
    :rtype: Lexeme

    """

    # Create the json with the lexeme's data
    data_lex = json.dumps(
        {
            "type": "lexeme",
            "lemmas": {lang.short: {"value": lemma, "language": lang.short}},
            "language": lang.qid,
            "lexicalCategory": catLex,
            "forms": [],
        }
    )

    # Send a post to edit a lexeme
    PARAMS = {
        "action": "wbeditentity",
        "format": "json",
        "bot": "1",
        "new": "lexeme",
        "token": "__AUTO__",
        "data": data_lex,
    }

    DATA = repo.post(PARAMS)
    # Get the id of the new lexeme
    idLex = DATA["entity"]["id"]

    logging.info("--Created lexeme : idLex = %s", idLex)
    lexeme = Lexeme(repo, idLex)

    if claims:
        lexeme.createClaims(claims)

    return lexeme


def overwrite_lexeme_by_json(repo, idLex: int, data_lex: str):
    """Overwrite the lexeme with a new version supplied as json-string"""
    PARAMS = {
        "action": "wbeditentity",
        "format": "json",
        "bot": "1",
        "id": idLex,
        "token": "__AUTO__",
        "data": data_lex,
    }
    repo.post(PARAMS)
