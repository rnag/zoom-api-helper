"""
Zoom API Helper
~~~~~~~~~~~~~~~

Utilities to interact with the Zoom API v2

Sample Usage:

    >>> import zoom_api_helper

For full documentation and more advanced usage, please see
<https://zoom-api-helper.readthedocs.io>.

:copyright: (c) 2022 by Ritvik Nag.
:license: MIT, see LICENSE for more details.
"""

__all__ = [
    'ZoomAPI',
    'setup_logging',
]


from .v2 import ZoomAPI
from .log import setup_logging
