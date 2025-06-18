import json
import logging
from typing import Dict, List, Union

from .claim import Claim
from .utils import getPropertyType
from .wikidatasession import WikidataSession


class Entity(dict):
    """
    Base class for all types of entities – currently: Lexeme, Form, Sense.
    Not yet implemented: Item, Property.
    """

    def __init__(self, repo: WikidataSession):
        super().__init__()
        self.repo = repo

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

    def addClaims(self, claims: Union[List[Claim], Dict[str, List[str]]]):
        """
        Add claims to the entity.

        :param claims: The claims to be added to the entity.

                       There are two possibilities for this:

                       - A list of Objects of type Claim

                         Example: ``[Claim(propertyId="P31", value="Q1")]``

                       - A dictionary with the property id as key and lists of
                         string formated entity ids as values.

                         Example: ``{"P31": ["Q1", "Q2"]}``

                       The first supports all datatypes, whereas the later
                       currently only supports datatypes of kind Entity.
        """
        if isinstance(claims, list):
            self.__setClaims__(claims)
        elif isinstance(claims, dict):
            self.__createClaims__(claims)
        else:
            raise TypeError("Invalid argument type:", type(claims))

    def __setClaims__(self, claims: List[Claim]):
        """
        Add prebuild claims to the entity

        :param claims: The list of claims to be added
        """
        for claim in claims:
            pid = claim.property
            self.__setClaim__(pid, claim)

    def __createClaims__(self, claims: Dict[str, List[str]]):
        """
        Create and add new claims to the entity.

        Only properties of some entity type are implemented:
        Item, Property, Lexeme, Form and Sense

        :param claims: The set of claims to be added
        """
        for cle, values in claims.items():
            for value in values:
                self.__setEntityClaim__(cle, value)

    def __setEntityClaim__(self, idProp: str, idStr: str):
        """
        Add a claim of an entity-type to the entity.

        Supported types are Lexeme, Form, Sense, Item, Property.

        :param idProp: id of the property (example: "P31")
        :param idItem: id of the entity (example: "Q1")
        """
        # Check if this is an external-id property
        datatype = None
        try:
            datatype = getPropertyType(idProp)
        except Exception:
            # If we can't get the property type, assume it's an entity
            pass
        if datatype == "external-id":
            # For external-id properties, create a Claim object and use __setClaims__
            claim = Claim(propertyId=idProp, value=idStr)
            self.__setClaims__([claim])
            return
        # Handle entity-type properties as before
        if idStr.startswith(('Q', 'P', 'L')):
            entityId = int(idStr[1:])
            claim_value = json.dumps({"entity-type": "item", "numeric-id": entityId})
            self.__setClaim__(idProp, claim_value)
        else:
            raise ValueError(f"Invalid entity ID format: {idStr}. Expected Q, P, or L prefix.")

    def __setClaim__(self, idProp: str, claim_value):
        from .utils import getPropertyType
        import LexData.lexeme
        is_lexeme = isinstance(self, LexData.lexeme.Lexeme)
        if isinstance(claim_value, Claim):
            datatype = getPropertyType(idProp)
            if datatype == "external-id":
                claim_value = claim_value.pure_value
            else:
                snak_data = claim_value["mainsnak"]
                claim_value = json.dumps(snak_data["datavalue"])
        datatype = getPropertyType(idProp)
        if datatype == "external-id":
            claim_value_json = json.dumps(claim_value)
        else:
            claim_value_json = claim_value
        # Use wbcreateclaim for both lexemes and other entities
        PARAMS = {
            "action": "wbcreateclaim",
            "format": "json",
            "entity": self.id,
            "snaktype": "value",
            "bot": "1",
            "property": idProp,
            "value": claim_value_json,
            "token": "__AUTO__",
        }

        DATA = self.repo.post(PARAMS)
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

    @property
    def id(self) -> str:
        EntityId = self.get("id")
        assert isinstance(EntityId, str)
        return EntityId

    def __str__(self) -> str:
        return super().__repr__()
