"""
Zoom API Helper
~~~~~~~~~~~~~~~

Utilities to interact withh the Zoom API v2

Sample Usage:

    >>> import zoom_api_helper

For full documentation and more advanced usage, please see
<https://zoom-api-helper.readthedocs.io>.

:copyright: (c) 2022 by Ritvik Nag.
:license:MIT, see LICENSE for more details.
"""

__all__ = [

]

import logging


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger('zoom_api_helper').addHandler(logging.NullHandler())
