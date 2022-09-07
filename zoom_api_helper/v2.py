from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from .constants import *
from .log import LOG
from .models import *
from .oauth import get_access_token
from .utils import *


class ZoomAPI:
    # noinspection GrazieInspection
    """
    Helper client to interact with the `Zoom API v2`_

    .. _Zoom API v2: https://marketplace.zoom.us/docs/api-reference/zoom-api/

    """

    __slots__ = (
        # required for `@cached_property`
        '__dict__',
        # instance attributes
        '_session',
        '_account_id',
        '_access_token',
        '_client_id',
    )

    def __init__(self, client_id: str,
                 client_secret: str,
                 account_id: str = None,
                 local=False):

        self._session = session = requests.Session()
        self._account_id = account_id = account_id or os.getenv('ZOOM_ACCOUNT_ID')
        self._client_id = client_id

        if local:
            self._access_token = token = 'abc12345'
        else:
            self._access_token = token = get_access_token(
                session, account_id, client_id, client_secret,
            )

        session.headers['Authorization'] = f'Bearer {token}'
        session.headers['Content-Type'] = 'application/json'

    @classmethod
    def dummy_client(cls):
        """Create a dummy :class:`ZoomAPI` client, for testing purposes."""
        return cls('...', '...', local=True)

    def __repr__(self):
        cls_name = self.__class__.__name__
        masked_token = f'{self._access_token[:5]}***'
        return (f'{cls_name}(access_token={masked_token!r}, '
                f'account_id={self._account_id!r}, '
                f'client_id={self._client_id!r})')

    def _new_session(self) -> requests.Session:
        session = requests.Session()
        session.headers['Authorization'] = f'Bearer {self._access_token}'
        session.headers['Content-Type'] = 'application/json'

        return session

    def _get(self, url: str, params: dict = None, session: requests.Session | None = None):
        LOG.debug('GET %s, params=%s', url, params)
        return (session or self._session).get(url, params=params)

    def _post(self, url: str, data: dict = None, session: requests.Session | None = None):
        LOG.debug('POST %s, data=%s', url, data)
        return (session or self._session).post(url, json=data)

    @log_time
    def bulk_create_meetings(self, col_header_to_kwarg: dict[str, str] = None,
                             *,
                             rows: list[RowType] = None,
                             excel_file: str | os.PathLike[str] = None,
                             max_threads=10,
                             process_row: ProcessRow = None,
                             update_row: UpdateRow = None,
                             out_file: str | os.PathLike[str] = None,
                             default_timezone='UTC',
                             dry_run=False):
        # noinspection GrazieInspection
        """``POST /users/{userId}/meetings``: Use this API to *bulk*-create meetings, given
        a list of meetings to create.

        If the rows containing meetings to create lives in an Excel (.xlsx) file,
        then `excel_file` must be passed in, and contain the filepath of the Excel
        file to retrieve the meeting details from; else, `rows` must be passed in
        with a list of meetings to create.

        Note that to read from Excel, the ``sheet2dict`` library is required;
        this can be installed easily via::

            $ pip install zoom-api-helper[excel]

        ``col_header_to_kwarg`` is a mapping of column headers to keyword arguments,
        as accepted by the :meth:`create_meeting` method. If the header names are
        all title-cased versions of the keyword arguments, then this argument does
        *not* need to be passed in. See also, :attr:`constants.CREATE_MEETING_KWARGS`
        for a full list of acceptable keywords for the *Create Meeting* API; note
        that these are specified as *values* in the key-value pairing.

        ``process_row`` is an optional function or callable that will be called with
        a copy of each *row*, or individual meeting info. The function can modify
        the row in place as desired.

        ``update_row`` is an optional function or callable that will be called with
        the HTTP response data from the Create Meetings API, and the associated
        row from the Excel file. The function can modify the row in place as desired.

        If ``dry_run`` is enabled, then no API calls will be made, and this function
        will essentially be a no-op; however, useful logging output is printed for
        debugging purposes. Enable this parameter along with the :func:`setup_logging`
        helper function, in a debug environment.

        **How It Works**

        This function scans in a list of rows containing a list of meetings
        to create, either from a local file or from the ``rows`` parameter.
        Then, it calls ``process_row`` on each row, and also retrieves a
        mapping of column name to keyword argument via ``col_header_to_kwarg``.
        Then, it concurrently creates a list of meetings via the Zoom
        **Create Meetings** API. Finally, it calls ``update_row`` on each
        response and row pair, and writes out the updated meeting info to
        an output CSV file named ``out_file``, which defaults to
        ``{excel-file-name-without-ext}}.out.csv`` if an output filepath
        is not specified.

        **References**

        API documentation:
            - https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/meetingCreate

        If a naive `datetime` object is provided for ``start_time`` or any other field
        (i.e. one with no timezone information) the value for ``timezone`` will determine
        which timezone to associate with the `datetime` object - defaults to *UTC* time
        if not specified.

        For a list of supported timezones, please see:
            - https://marketplace.zoom.us/docs/api-reference/other-references/abbreviation-lists/#timezones

        """
        # noinspection PyUnresolvedReferences
        import sheet2dict

        def to_snake_case(s: str):
            return s.replace(' ', '_').replace('-', '_').lower()

        if rows:
            col_headers = rows[0].keys()
        else:
            ws = sheet2dict.Worksheet()
            ws.xlsx_to_dict(excel_file)
            col_headers = ws.sheet_items[0].keys()
            rows = ws.sheet_items

        header_to_kwarg = {kwarg: kwarg for kwarg in CREATE_MEETING_KWARGS}

        if not col_header_to_kwarg:
            col_header_to_kwarg = {h: to_snake_case(h) for h in col_headers}

        for h in col_headers:
            kwarg = col_header_to_kwarg.get(h) or to_snake_case(h)
            if kwarg in CREATE_MEETING_KWARGS:
                header_to_kwarg[h] = kwarg

        meetings_to_create = []

        if process_row is None:
            def do_nothing(_row): return True
            process_row = do_nothing

        for row in rows:
            # copy row so as not to modify it directly.
            copied_row = row.copy()

            # optional: process the row.
            is_valid = process_row(copied_row)
            if not is_valid:
                continue

            # retrieve meeting info.
            mtg = {header_to_kwarg[h]: copied_row[h] for h in header_to_kwarg
                   if h in copied_row}

            # add default fields.
            if 'timezone' not in mtg:
                mtg['timezone'] = default_timezone

            meetings_to_create.append(mtg)

        # if it's a dry run, print useful info for debugging purposes, then quit.
        if dry_run:
            print('Column Header to Keyword Argument:')
            print(json.dumps(header_to_kwarg, indent=2))
            print()
            print(f'Have {len(meetings_to_create)} Meetings to Create:')
            print(json.dumps(meetings_to_create, indent=2, cls=CustomEncoder))
            return

        LOG.debug('Column Header to Keyword Argument: %s', header_to_kwarg)

        if out_file is None:
            p = Path(excel_file)
            out_file = p.with_name(f'{p.stem}.out.csv')

        LOG.debug('Output File: %s', out_file.absolute())

        def create_meeting(mtg_: RowType):
            # use a separate session for each thread.
            session = self._new_session()
            return self.create_meeting(session=session, **mtg_)

        if update_row is None:
            update_row = dict.update

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Start the create meeting operations and mark each future with its row index
            future_to_row_idx = {executor.submit(create_meeting, mtg): i
                                 for i, mtg in enumerate(meetings_to_create)}

            for future in as_completed(future_to_row_idx):
                idx = future_to_row_idx[future]
                row = rows[idx]

                try:
                    resp = future.result()
                except Exception as exc:
                    LOG.error('[%d] %r generated an exception: %s', idx, row, exc)
                else:
                    update_row(row, resp)

        write_to_csv(out_file, rows)

    def create_meeting(self, *,
                       session: requests.Session | None = None,
                       host_id: str | None = None,
                       host_email: str | None = None,
                       topic: str = 'My Meeting',
                       agenda: str = 'My Description',
                       start_time: datetime | str | None = None,
                       timezone: str | None = 'UTC',
                       type: Meeting | None = None,
                       **request_data) -> dict[str, Any]:
        """``POST /users/{userId}/meetings``: Use this API to create a meeting for a user.

        Ref:
            - https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/meetingCreate

        If a naive `datetime` object is provided for `start_time` or any other field
        (i.e. one with no timezone information) the value for`timezone` will determine
        which timezone to associate with the `datetime` object - defaults to *UTC* time
        if not specified.

        For a list of supported timezones, please see:
            - https://marketplace.zoom.us/docs/api-reference/other-references/abbreviation-lists/#timezones

        :return:
        """
        if host_id:
            user_id = host_id
        elif host_email:
            user_id = self._user_email_to_id_cached[host_email]
        else:
            user_id = 'me'

        if agenda:
            request_data['agenda'] = agenda

        if topic:
            request_data['topic'] = topic

        if start_time:
            request_data['start_time'] = start_time.isoformat() \
                if isinstance(start_time, datetime) else start_time

        if timezone:
            request_data['timezone'] = timezone

        if type:
            request_data['type'] = type.value

        r = self._post(f'https://api.zoom.us/v2/users/{user_id}/meetings', request_data, session)
        r.raise_for_status()

        return r.json()

    @cached_property
    def _user_email_to_id_cached(self):
        return self.user_email_to_id(use_cache=True)

    def user_email_to_id(self, status: str | None = 'active', *, use_cache=False):
        filename = CACHE_DIR / f'users_{self._account_id}_{self._client_id}.json'

        if use_cache:
            users = read_json_file_if_exists(filename)
            if users:
                return users

        users = self.list_users(status)['users']
        email_to_id = {u['email']: u['id'] for u in users}

        # save list of users to cache
        save_json_file(filename, email_to_id)

        return email_to_id

    def list_users(self, status: str | None = 'active', page_size=300, page=1, all_pages=True):
        # noinspection GrazieInspection
        """``GET /users``: Use this API to list your account's users.

        Ref:
            - https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/users

        :param status: The user's status, one of: active, inactive, pending
        :param page_size: The number of records returned within a single API call.
        :param page: The page number of the current page in the returned records.
        :param all_pages: True to paginate and retrieve all records (pages).
        :return: A `dict` object, where the `users` key contains a list of users.

        """
        params = {'page_size': page_size, 'page_number': page}
        if status:
            params['status'] = status

        res = self._get(API_USERS, params=params)
        final_data = data = res.json()

        if all_pages:
            while data['page_count'] > data['page_number']:
                params['page_number'] += 1
                res = self._get(API_USERS, params=params)
                data = res.json()
                final_data['users'].extend(data['users'])

        return final_data
