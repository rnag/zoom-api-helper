"""Tests for `zoom_api_helper` package."""
import ast
import os
from datetime import datetime
from pathlib import Path

import pytest

from zoom_api_helper import ZoomAPI, setup_logging
from zoom_api_helper.models import *

TEST_DIR = Path(__file__).parent


@pytest.fixture(scope='session', autouse=True)
def setup():
    setup_logging()


@pytest.fixture(scope='session')
def zoom_client():
    client_id = require_env('ZOOM_CLIENT_ID')
    client_secret = require_env('ZOOM_CLIENT_SECRET')
    account_id = require_env('ZOOM_ACCOUNT_ID')

    return ZoomAPI(client_id, client_secret, account_id)


def require_env(var_name: str):
    try:
        return os.environ[var_name]
    except KeyError:
        raise ValueError(f'Environment variable `{var_name}` is required '
                         f'for tests.`') from None


def test_list_users(zoom_client):
    res = zoom_client.list_users()
    print(res)


def test_create_meeting(zoom_client):
    res = zoom_client.create_meeting()
    print(res)


def test_create_bulk_meetings(zoom_client):
    """Sample pytest test function with the pytest fixture as an argument."""

    dry_run = not ast.literal_eval(os.getenv('NO_DRY_RUN', 'false').capitalize())

    # column header to keyword argument
    col_name_to_kwarg = {'Group Name': 'agenda',
                         'Zoom Username': 'host_email'}

    def process_row(row: 'RowType', dt_format='%Y-%m-%d %I:%M %p'):
        start_time = f"{row['Meeting Date'][:10]} {row['Meeting Time']}"

        row.update(
            start_time=datetime.strptime(start_time, dt_format),
            # Zoom expects the `duration` value in seconds.
            duration=int(row['Duration Hr']) * 60 + int(row['Duration Min']),
        )

        return True

    def update_row(row: 'RowType', resp: dict):
        row['Meeting URL'] = resp['join_url']
        row['Meeting ID'] = resp['id']
        row['Passcode'] = resp['password']

    zoom_client.bulk_create_meetings(
        col_name_to_kwarg,
        excel_file=TEST_DIR / '[DUMMY] Zoom Meeting Information.xlsx',
        default_timezone='America/New_York',
        process_row=process_row,
        update_row=update_row,
        dry_run=dry_run,
    )
