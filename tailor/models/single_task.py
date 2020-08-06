from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast

from .run import RunModel


@dataclass
class SingleTaskModel:
    """  """

    id: Optional[str] = None
    name: Optional[str] = None
    updated_utc: Optional[str] = None
    state: Optional[str] = None
    created_utc: Optional[str] = None
    runs: Optional[List[RunModel]] = None
    definition: Optional[Dict[Any, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        updated_utc = self.updated_utc
        state = self.state
        created_utc = self.created_utc
        if self.runs is None:
            runs = None
        else:
            runs = []
            for runs_item_data in self.runs:
                runs_item = runs_item_data.to_dict()

                runs.append(runs_item)

        definition = self.definition

        return {
            "id": id,
            "name": name,
            "updated_utc": updated_utc,
            "state": state,
            "created_utc": created_utc,
            "runs": runs,
            "definition": definition,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> SingleTaskModel:
        id = d.get("id")

        name = d.get("name")

        updated_utc = d.get("updated_utc")

        state = d.get("state")

        created_utc = d.get("created_utc")

        runs = []
        for runs_item_data in d.get("runs") or []:
            runs_item = RunModel.from_dict(runs_item_data)

            runs.append(runs_item)

        definition = d.get("definition")

        return SingleTaskModel(
            id=id,
            name=name,
            updated_utc=updated_utc,
            state=state,
            created_utc=created_utc,
            runs=runs,
            definition=definition,
        )
