from typing import Any, Dict, Optional

import requests

from .version import user_agent


class WikidataSession:
    """Wikidata network and authentication session. Needed for everything this
    framework does.


    """

    URL = "https://www.wikidata.org/w/api.php"
    assertUser = None

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        auth: Optional[str] = None,
        user_agent=user_agent,
    ):
        """
        Create a wikidata session by logging in and getting the token
        """
        self.username = username
        self.password = password
        self.auth = auth
        self.headers = {"User-Agent": user_agent}
        self.S = requests.Session()
        if username is not None and password is not None:
            self.login()
        if token is not None:
            self.CSRF_TOKEN = token
        # After logging in enable 'assertUser'-feature of the Mediawiki-API to
        # make sure to never edit accidentally as IP
        if username is not None:
            self.assertUser = username

    def login(self):
        # Ask for a token
        PARAMS_1 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json",
        }
        DATA = self.get(PARAMS_1)
        LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]

        # connexion request
        PARAMS_2 = {
            "action": "login",
            "lgname": self.username,
            "lgpassword": self.password,
            "format": "json",
            "lgtoken": LOGIN_TOKEN,
        }
        self.post(PARAMS_2)

        PARAMS_3 = {"action": "query", "meta": "tokens", "format": "json"}
        DATA = self.get(PARAMS_3)
        self.CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]

    def post(self, data: Dict[str, str]) -> Any:
        """Send data to wikidata by POST request. The CSRF token is automatically
        filled in if __AUTO__ is given instead.

        :param data: Parameters to send via POST
        :type  data: Dict[str, str])
        :returns: Answer form the server as Objekt
        :rtype: Any

        """
        if data.get("token") == "__AUTO__":
            data["token"] = self.CSRF_TOKEN
        if "assertuser" not in data and self.assertUser is not None:
            data["assertuser"] = self.assertUser
        R = self.S.post(self.URL, data=data, headers=self.headers, auth=self.auth)
        if R.status_code != 200:
            raise Exception(
                "POST was unsuccessfull ({}): {}".format(R.status_code, R.text)
            )
        DATA = R.json()
        if "error" in DATA:
            raise PermissionError("API returned error: " + str(DATA["error"]))
        return DATA

    def get(self, data: Dict[str, str]) -> Any:
        """Send a GET request to wikidata

        :param data: Parameters to send via GET
        :type  data: Dict[str, str]
        :returns: Answer form the server as Objekt
        :rtype: Any

        """
        R = self.S.get(self.URL, params=data, headers=self.headers)
        if R.status_code != 200:
            raise Exception(
                "GET was unsuccessfull ({}): {}".format(R.status_code, R.text)
            )
        return R.json()
