from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ValidationErrorModel:
    """  """

    loc: List[str]
    msg: str
    type: str

    def to_dict(self) -> Dict[str, Any]:
        loc = self.loc

        msg = self.msg
        type = self.type

        return {
            "loc": loc,
            "msg": msg,
            "type": type,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> ValidationErrorModel:
        loc = d["loc"]

        msg = d["msg"]

        type = d["type"]

        return ValidationErrorModel(loc=loc, msg=msg, type=type, )
