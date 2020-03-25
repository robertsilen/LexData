"""
This module simply contains a few common Languages with their language-codes
and QIDs for easier use.
"""
from dataclasses import dataclass


@dataclass
class Language:
    """Dataclass representing a language"""

    short: str
    qid: str


# feel free to add more languages
en = Language("en", "Q1860")
de = Language("de", "Q188")
fr = Language("fr", "Q150")
