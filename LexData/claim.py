from typing import Any, Dict, Tuple, Union


class Claim(dict):
    """Wrapper around a dict to represent a Claim"""

    # Hack needed to define a property called property
    property_decorator = property

    def __init__(self, claim: Dict[str, Any]):
        super().__init__()
        self.update(claim)

    @property_decorator
    def value(self) -> Dict[str, Any]:
        """
        Return the value of the claim. The type depends on the data type.
        """
        return self["mainsnak"]["datavalue"]["value"]

    @property_decorator
    def type(self) -> str:
        """
        Return the data type of the claim.

        :rtype: str
        """
        return self["mainsnak"]["datatype"]

    @property_decorator
    def property(self) -> str:
        """
        Return the property of the claim.

        :rtype: str
        """
        return self["mainsnak"]["property"]

    @property_decorator
    def rank(self) -> str:
        """
        Return the rank of the claim.

        :rtype: str
        """
        return self["rank"]

    @property_decorator
    def numeric_rank(self) -> int:
        """
        Return the rank of the claim as integer.

        :rtype: int
        """
        if self.rank == "normal":
            return 0
        elif self.rank == "preferred":
            return 1
        elif self.rank == "deprecated":
            return -1
        raise NotImplementedError("Unknown or invalid rank {}".format(self.rank))

    @property_decorator
    def pure_value(self) -> Union[str, int, float, Tuple[float, float]]:
        """
        Return just the 'pure' value, what this is depends on the type of the value:
        - wikibase-entity: the id, including 'L/Q/P'-prefix
        - string: the string
        - manolingualtext: the text as string
        - quantity: the amount as float
        - time: the timestamp as string in format ISO 8601
        - globecoordinate: tuple of latitude and longitude as floats

        Be aware that for most types this is not the full information stored in
        the value.
        """
        value = self.value
        vtype = self.type
        if vtype == "wikibase-entityid":
            return value["id"]
        if vtype == "string":
            return value
        if vtype == "monolingualtext":
            return value["text"]
        if vtype == "quantity":
            return float(value["amount"])
        if vtype == "time":
            return value["time"]
        if vtype == "globecoordinate":
            return (float(value["latitude"]), float(value["longitude"]))
        raise NotImplementedError

    def __repr__(self) -> str:
        return "<Claim '{}'>".format(repr(self.value))
