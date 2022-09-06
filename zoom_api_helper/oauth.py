from time import time

import requests

from .constants import CACHE_DIR
from .utils import read_json_file_if_exists, save_json_file


def get_access_token(session: requests.Session,
                     account_id: str,
                     client_id: str,
                     client_secret: str) -> str:
    """Retrieve an access token, given credentials for a Server-to-Server OAuth app.

    To use account credentials to get an access token for your app, call the Zoom OAuth token API
    with the account_credentials `grant_type` and your `account_id`.

    The successful response will be the access token, which is a Bearer token type that expires
    in an hour, with the scopes that you chose in your app settings screen.

    Ref:
        - https://marketplace.zoom.us/docs/guides/build/server-to-server-oauth-app/


    :param session: (Optional) Requests Session
    :param account_id: Zoom Account ID
    :param client_id: OAuth app Client ID
    :param client_secret: OAuth app Client Secret

    :return: The access token for the app.
    """
    filename = CACHE_DIR / f'token_{account_id}_{client_id}.json'

    # first, check the cache for the access token.
    cache = read_json_file_if_exists(filename)
    if cache and cache['expires_at'] > round(time()):
        return cache['access_token']

    # else, we make a live API call to retrieve the token.
    params = {
        'grant_type': 'account_credentials',
        'account_id': account_id,
    }

    r = session.post(
        'https://zoom.us/oauth/token',
        auth=(client_id, client_secret),
        params=params
    )
    r.raise_for_status()

    data = r.json()

    token = data['access_token']
    # 5 minutes before the token actually expires
    expires_at = round(time()) + data['expires_in'] - (5 * 60)

    # save the access token to the cache.
    cache = {'access_token': token, 'expires_at': expires_at}
    save_json_file(filename, cache)

    return token
