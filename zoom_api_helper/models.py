__all__ = [
    'Meeting',
]

from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    __all__ += ['RowType', 'ProcessRow', 'UpdateRow']

    from datetime import datetime
    from typing import Any

    try:
        from typing import Protocol
    except ImportError:  # Python 3.7
        from typing_extensions import Protocol

    RowType = dict[str, str | datetime | bool | int | float | dict | list | None]


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
