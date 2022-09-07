"""Project-specific constant values."""

__all__ = [
    'API_USERS',
    'CACHE_DIR',
    'CREATE_MEETING_KWARGS',
]

from os import getenv
from pathlib import Path


API_USERS = 'https://api.zoom.us/v2/users'

# Cache Directory
CACHE_DIR = Path(getenv('CACHE_DIR', '~/.zoom/cache')).expanduser()

# Create Cache Directory if needed.
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Create Meeting API - valid keyword arguments
#
# Ref: https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/meetingCreate
CREATE_MEETING_KWARGS = {
    # Extras: used by our `create_meeting` method
    'host_id', 'host_email',
    # Zoom API keyword arguments
    'agenda', 'start_time', 'template_id', 'password', 'timezone', 'topic',
    'tracking_fields', 'duration', 'recurrence', 'default_password',
    'pre_schedule', 'settings', 'schedule_for', 'type'
}
