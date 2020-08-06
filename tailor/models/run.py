from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RunModel:
    """  """

    state: Optional[str] = None
    ended_utc: Optional[str] = None
    traceback: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        state = self.state
        ended_utc = self.ended_utc
        traceback = self.traceback
        error_message = self.error_message

        return {
            "state": state,
            "ended_utc": ended_utc,
            "traceback": traceback,
            "error_message": error_message,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> RunModel:
        state = d.get("state")

        ended_utc = d.get("ended_utc")

        traceback = d.get("traceback")

        error_message = d.get("error_message")

        return RunModel(state=state, ended_utc=ended_utc, traceback=traceback,
                        error_message=error_message, )
