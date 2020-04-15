import functools
import json
from datetime import datetime
from typing import Any, Dict

from .wikidatasession import WikidataSession


@functools.lru_cache()
def getPropertyType(propertyId: str):
    repo = WikidataSession()
    query = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": "Property:" + propertyId,
        "rvprop": "content",
    }
    DATA = repo.get(query)
    jsonstr = list(DATA["query"]["pages"].values())[0]["revisions"][0]["*"]
    content = json.loads(jsonstr)
    return content["datatype"]


def buildDataValue(datatype: str, value):
    if datatype in [
        "wikibase-lexeme",
        "wikibase-form",
        "wikibase-sense",
        "wikibase-item",
        "wikibase-property",
    ]:
        if type(value) == dict:
            return {"value": value, "type": "wikibase-entity"}
        elif type(value) == str:
            value = {"entity-type": datatype[9:], "id": value}
            return {"value": value, "type": "wikibase-entity"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype in [
        "string",
        "tabular-data",
        "geo-shape",
        "url",
        "musical-notation",
        "math",
        "commonsMedia",
    ]:
        if type(value) == dict:
            return {"value": value, "type": "string"}
        elif type(value) == str:
            return {"value": {"value": value}, "type": "string"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "monolingualtext":
        if type(value) == dict:
            return {"value": value, "type": "monolingualtext"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "globe-coordinate":
        if type(value) == dict:
            return {"value": value, "type": "globecoordinate"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "quantity":
        if type(value) == dict:
            return {"value": value, "type": "quantity"}
        if type(value) in [int, float]:
            valueObj = {
                "amount": "%+f" % value,
                "unit": "1",
            }
            return {"value": valueObj, "type": "time"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    elif datatype == "time":
        if type(value) == dict:
            return {"value": value, "type": "time"}
        if type(value) == datetime:
            cleanedDateTime = value.replace(hour=0, minute=0, second=0, microsecond=0)
            valueObj: Dict[str, Any] = {
                "time": "+" + cleanedDateTime.isoformat() + "Z",
                "timezone": 0,
                "before": 0,
                "after": 0,
                "precision": 11,
                "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
            }
            return {"value": valueObj, "type": "time"}
        else:
            raise TypeError(
                f"Can not convert type {type(value)} to datatype {datatype}"
            )
    else:
        raise NotImplementedError(f"Datatype {datatype} not implemented")


def buildSnak(propertyId: str, value):
    datatype = getPropertyType(propertyId)
    datavalue = buildDataValue(datatype, value)
    return {
        "snaktype": "value",
        "property": propertyId,
        "datavalue": datavalue,
        "datatype": datatype,
    }
