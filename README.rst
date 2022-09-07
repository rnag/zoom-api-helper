===============
Zoom API Helper
===============


.. image:: https://img.shields.io/pypi/v/zoom-api-helper.svg
        :target: https://pypi.org/project/zoom-api-helper

.. image:: https://img.shields.io/pypi/pyversions/zoom-api-helper.svg
        :target: https://pypi.org/project/zoom-api-helper

.. image:: https://github.com/rnag/zoom-api-helper/actions/workflows/dev.yml/badge.svg
        :target: https://github.com/rnag/zoom-api-helper/actions/workflows/dev.yml

.. image:: https://readthedocs.org/projects/zoom-api-helper/badge/?version=latest
        :target: https://zoom-api-helper.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/rnag/zoom-api-helper/shield.svg
     :target: https://pyup.io/repos/github/rnag/zoom-api-helper/
     :alt: Updates


Utilities to interact with the Zoom API v2


* Free software: MIT license
* Documentation: https://zoom-api-helper.readthedocs.io.
* Zoom API Docs: https://marketplace.zoom.us/docs/api-reference/zoom-api.

Installation
------------

The Zoom API Helper library is available `on PyPI`_, and can be installed with ``pip``:

.. code-block:: shell

    $ pip install zoom-api-helper

You'll also need to create a Server-to-Server OAuth app as outlined `in the docs`_.

Features
--------

* `Zoom API v2`_: List users, create meetings, and bulk create meetings.
* Support for a `Server-to-Server OAuth`_ flow.
* Local caching of access token retrieved from OAuth process.

.. _Server-to-Server OAuth: https://marketplace.zoom.us/docs/guides/build/server-to-server-oauth-app/
.. _Zoom API v2: https://marketplace.zoom.us/docs/api-reference/introduction/


Quickstart
----------

Start by creating a helper
client (``ZoomAPI``) to interact with the Zoom API:

.. code-block:: python

    >>> from zoom_api_helper import ZoomAPI
    >>> zoom = ZoomAPI('<CLIENT ID>', '<CLIENT SECRET>',
    ...                # can also be specified via `ZOOM_ACCOUNT_ID` env variable
    ...                account_id='<ACCOUNT ID>')


Retrieve a list of users via ``ZoomAPI.list_users()``:

.. code-block:: python

    >>> zoom.list_users()
    {'page_count': 3, 'page_number': 1, 'page_size': 300, 'total_records': 700, 'users': [{'id': '-abc123', 'first_name': 'Jon', 'last_name': 'Doe', 'email': 'jdoe@email.org', 'timezone': 'America/New_York', ...}, ...]}


Or, a mapping of each Zoom user's *Email* to *User ID*:

.. code-block:: python

    >>> zoom.user_email_to_id(use_cache=True)
    {'jdoe@email.org': '-abc123', 'dsimms@email2.org': '-xyz321', ...}


Create an individual meeting via ``ZoomAPI.create_meeting()``:

.. code-block:: python

    >>> zoom.create_meeting(topic='My Awesome Meeting')
    {'uuid': 'T9SwnVWzQB2dD1zFQ7PxFA==', 'id': 91894643201, 'host_id': '...', 'host_email': 'me@email.org', 'topic': 'My Awesome Meeting', 'type': 2, ...}

To *bulk create* a list of meetings in a concurrent fashion, please see the
section on `Bulk Create Meetings`_ below.

Local Storage
-------------

This library uses a local storage for cache purposes, located under
the user home directory at ``~/.zoom/cache`` by default -- though this
can location be customized, via the ``CACHE_DIR`` environment variable.

The format of the filenames containing cached data will look something similar to this::

    {{ Purpose }}_{{ Zoom Account ID }}_{{ Zoom Client ID }}.json

Currently, the helper library utilizes the file cache for two purposes:

* Storing the access token retrieved from the OAuth step, so that the token
  only needs to be refreshed after *~1 hour*.

* Storing a cached mapping of Zoom User emails to User IDs, as generally
  the Zoom APIs only require the User ID's.

  * As otherwise, retrieving this mapping from the API can sometimes
    be expensive, especially for Zoom accounts that have a lot of Users (1000+).


Bulk Create Meetings
--------------------

In order to *bulk create meetings* -- for example, if you need to create 100+
meetings in a short span of time -- use the ``ZoomAPI.bulk_create_meetings()``
method.

This allows you to pass in an Excel (*.xlsx*) file containing the meetings to
create, or else pass in the ``rows`` with the meeting info directly.

Example
~~~~~~~

Suppose you have an Excel file (``meeting-info.xlsx``) with the following data:

+---------------------------+------------------+--------------------------------------------+---------------+---------------+--------------+---------------+--------------+-------------+-----------+
| Group Name                | Zoom Username    | Topic                                      | Meeting Date  | Meeting Time  | Duration Hr  | Duration Min  | Meeting URL  | Meeting ID  | Passcode  |
+===========================+==================+============================================+===============+===============+==============+===============+==============+=============+===========+
| A-BC:TEST:Sample Group 1  | host1@email.com  | TEST Meeting #1: Just an example           | 10/26/25      | 3:30 PM       | 1            | 30            |              |             |           |
+---------------------------+------------------+--------------------------------------------+---------------+---------------+--------------+---------------+--------------+-------------+-----------+
| A-BC:TEST:Sample Group 2  | host1@email.com  | TEST Meeting #2: Here's another one        | 11/27/25      | 7:00 PM       | 1            | 0             |              |             |           |
+---------------------------+------------------+--------------------------------------------+---------------+---------------+--------------+---------------+--------------+-------------+-----------+
| A-BC:TEST:Sample Group 3  | host2@email.com  | TEST Meeting #3: This is the last for now  | 9/29/25       | 9:00 PM       | 1            | 15            |              |             |           |
+---------------------------+------------------+--------------------------------------------+---------------+---------------+--------------+---------------+--------------+-------------+-----------+

Then, here is a sample code that would allow you to *bulk create* the specified
meetings in the Zoom Account.

    Note: replace the credentials such as ``<CLIENT ID>`` below as needed.

.. code-block:: python3

    from datetime import datetime

    from zoom_api_helper import ZoomAPI
    from zoom_api_helper.models import *


    def main():
        zoom = ZoomAPI('<CLIENT ID>', '<CLIENT SECRET>', '<ACCOUNT ID>')

        # (optional) column header to keyword argument
        col_name_to_kwarg = {'Group Name': 'agenda',
                             'Zoom Username': 'host_email'}

        # (optional) predicate function to initially process the row data
        def process_row(row: 'RowType', dt_format='%Y-%m-%d %I:%M %p'):
            start_time = f"{row['Meeting Date'][:10]} {row['Meeting Time']}"

            row.update(
                start_time=datetime.strptime(start_time, dt_format),
                # Zoom expects the `duration` value in seconds.
                duration=int(row['Duration Hr']) * 60 + int(row['Duration Min']),
            )

            return True

        # (optional) function to update row(s) with the API response
        def update_row(row: 'RowType', resp: dict):
            row['Meeting URL'] = resp['join_url']
            row['Meeting ID'] = resp['id']
            row['Passcode'] = resp['password']

        # create meetings with dry run enabled.
        zoom.bulk_create_meetings(
            col_name_to_kwarg,
            excel_file='./meeting-info.xlsx',
            default_timezone='America/New_York',
            process_row=process_row,
            update_row=update_row,
            # comment out below line to actually create the meetings.
            dry_run=True,
        )


    if __name__ == '__main__':
        main()

Credits
-------

This package was created with Cookiecutter_ and the `rnag/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`rnag/cookiecutter-pypackage`: https://github.com/rnag/cookiecutter-pypackage
.. _on PyPI: https://pypi.org/project/zoom-api-helper/
.. _in the docs: https://marketplace.zoom.us/docs/guides/build/server-to-server-oauth-app/
