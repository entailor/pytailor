from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast

from .validation_error import ValidationErrorModel


@dataclass
class HTTPValidationErrorModel:
    """  """

    detail: Optional[List[ValidationErrorModel]] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.detail is None:
            detail = None
        else:
            detail = []
            for detail_item_data in self.detail:
                detail_item = detail_item_data.to_dict()

                detail.append(detail_item)

        return {
            "detail": detail,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> HTTPValidationErrorModel:
        detail = []
        for detail_item_data in d.get("detail") or []:
            detail_item = ValidationErrorModel.from_dict(detail_item_data)

            detail.append(detail_item)

        return HTTPValidationErrorModel(detail=detail, )
