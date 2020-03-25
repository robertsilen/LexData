from typing import Dict

from .entity import Entity


class Form(Entity):
    """Wrapper around a dict to represent a From"""

    def __init__(self, form: Dict):
        super().__init__()
        self.update(form)

    @property
    def form(self) -> str:
        """
        String of the form value ("representation")

        :rtype: str
        """
        return list(self["representations"].values())[0]["value"]

    def __repr__(self) -> str:
        return "<Form '{}'>".format(self.form)
