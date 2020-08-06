from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class SingleTaskSummaryModel:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    updated_utc: Optional[str] = None
    state: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        updated_utc = self.updated_utc
        state = self.state

        return {
            "id": id,
            "name": name,
            "updated_utc": updated_utc,
            "state": state,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> SingleTaskSummaryModel:
        id = d.get("id")

        name = d.get("name")

        updated_utc = d.get("updated_utc")

        state = d.get("state")

        return SingleTaskSummaryModel(id=id, name=name, updated_utc=updated_utc, state=state, )
