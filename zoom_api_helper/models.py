__all__ = [
    'RowType',
    'ProcessRow',
    'UpdateRow',
    'Meeting',
]

from datetime import datetime
from enum import Enum
from typing import Protocol, Dict, Union, Any


RowType = Dict[str, Union[str, datetime, bool, int, float, dict, list, None]]


class ProcessRow(Protocol):

    def __call__(self, row: RowType) -> bool:
        ...


class UpdateRow(Protocol):

    def __call__(self, row: RowType, resp: dict[str, Any]) -> None:
        ...


class Meeting(Enum):
    """
    The type of Zoom meeting.
    """
    INSTANT = 1
    SCHEDULED = 2
    RECURRING = 3
    RECURRING_WITH_TIME = 8
