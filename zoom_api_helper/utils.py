from __future__ import annotations

__all__ = [
    'cached_property',
    'CustomEncoder',
    'log_time',
    'read_json_file_if_exists',
    'save_json_file',
    'write_to_csv',
]

from csv import DictWriter
from datetime import datetime
from json import load, dump, JSONEncoder
from time import time
from typing import TYPE_CHECKING, Any, TypeVar

from functools import wraps

try:
    from functools import cached_property
except ImportError:
    # noinspection PyUnresolvedReferences, PyPackageRequirements
    from backports.cached_property import cached_property

from .log import LOG


class CustomEncoder(JSONEncoder):

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()

        return JSONEncoder.default(self, o)


if TYPE_CHECKING:
    _F = TypeVar('_F')


def log_time(func: _F) -> _F:

    @wraps(func)
    def inner(*args, _fn_name=func.__name__, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        end = time()

        LOG.debug('[%s] completed in %.3fs', _fn_name, end - start)

        return ret

    return inner


def read_json_file_if_exists(filename: str) -> dict | list | None:
    try:
        with open(filename) as in_file:
            return load(in_file)

    except FileNotFoundError:
        return None


def save_json_file(filename: str, data: dict | list):
    with open(filename, 'w') as out_file:
        dump(data, out_file)


def write_to_csv(out_file: str, rows: list[dict]):
    with open(out_file, 'w') as output:
        writer = DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
