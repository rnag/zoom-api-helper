from logging import NullHandler, basicConfig, getLogger, DEBUG, WARNING
from typing import Union


LOG = getLogger('zoom_api_helper')

# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
LOG.addHandler(NullHandler())

LEVEL_TYPE = Union[str, int]


def setup_logging(default_level: LEVEL_TYPE = DEBUG,
                  lib_level: LEVEL_TYPE = DEBUG,
                  urllib3_level: LEVEL_TYPE = WARNING):
    """
    Sets up logging for application (user) code.
    """
    basicConfig(level=default_level)

    LOG.setLevel(lib_level)
    getLogger('urllib3').setLevel(urllib3_level)
