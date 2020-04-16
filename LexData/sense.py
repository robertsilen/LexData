from typing import Dict

from .entity import Entity
from .wikidatasession import WikidataSession


class Sense(Entity):
    """Wrapper around a dict to represent a Sense"""

    def __init__(self, repo: WikidataSession, form: Dict):
        super().__init__(repo)
        self.update(form)

    def glosse(self, lang: str = "en") -> str:
        """
        The gloss of the text in the specified language is available, otherwise
        in englisch, and if that's not set too in an arbitrary set language

        :param lang: language code of the wished language
        :type  lang: str
        :rtype: str
        """
        if lang not in self["glosses"]:
            if "en" in self["glosses"]:
                lang = "en"
            else:
                lang = list(self["glosses"].keys())[0]
        return self["glosses"][lang]["value"]

    def __repr__(self) -> str:
        return "<Sense '{}'>".format(self.glosse())
