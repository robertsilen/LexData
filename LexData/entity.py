import json
import logging
from typing import Dict, List

from .claim import Claim
from .wikidatasession import WikidataSession


class Entity(dict):
    @property
    def claims(self) -> Dict[str, List[Claim]]:
        """
        All the claims of the Entity

        :rtype: Dict[str, List[Claim]]
        """
        if self.get("claims", {}) != []:
            return {k: [Claim(c) for c in v] for k, v in self.get("claims", {}).items()}
        else:
            return {}

    # TODO: make compatible with type Claim
    def __setClaims__(self, repo: WikidataSession, claims: Dict[str, List[str]]):
        """
        Add claims to the entity (Lexeme, Form or Sense)

        :param repo: Wikidata Session to use
        :param claims: The set of claims to be added
        """
        for cle, values in claims.items():
            for value in values:
                self.__setClaim__(repo, cle, value)

    def __setClaim__(self, repo: WikidataSession, idProp: str, idItem: str):
        """
        Add a claim to the entity

        :param repo: Wikidata Session to use
        :param idProp: id of the property
        :param idItem: id of the Item
        """

        claim_value = json.dumps({"entity-type": "item", "numeric-id": idItem[1:]})

        PARAMS = {
            "action": "wbcreateclaim",
            "format": "json",
            "entity": self["id"],
            "snaktype": "value",
            "bot": "1",
            "property": idProp,
            "value": claim_value,
            "token": "__AUTO__",
        }

        DATA = repo.post(PARAMS)
        assert "claim" in DATA
        addedclaim = DATA["claim"]
        logging.info("Claim added")

        # Add the created claim to the local entity instance
        if self.get("claims", []) == []:
            self["claims"] = {idProp: addedclaim}
        elif idProp in self.claims:
            self.claims[idProp].append(addedclaim)
        else:
            self.claims[idProp] = [addedclaim]

    def __str__(self) -> str:
        return super().__repr__()
