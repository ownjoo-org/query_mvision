import argparse
import logging

from json import loads, dumps
from typing import Optional, Generator

import http.client

from requests import HTTPError, Session, Response

http.client.HTTPConnection.debuglevel = 0  # 0 for off, > 0 for on

log_level: int = logging.ERROR
logging.basicConfig()
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(log_level)
requests_log.propagate = True
default_scopes: list = [
    'epo.admin',
    'epo.device.r',
    'epo.grps.r',
    'epo.evt.r',
    'epo.tags.r',
]
DEFAULT_SCOPES: str = ' '.join(default_scopes)


PAGE_SIZE: int = 100

URL_TRELLIX_TOKEN: str = 'https://iam.cloud.trellix.com/iam/v1.1/token'
URL_DEVICES: str = f'https://api.manage.trellix.com/epo/v2/devices'


def logon(session: Session, client_id: str, client_secret: str) -> str:
    params: dict = {
        'grant_type': 'client_credentials',
        'scope': DEFAULT_SCOPES,
    }
    resp_auth: Response = session.post(
        url=URL_TRELLIX_TOKEN,
        data=params,
        auth=(client_id, client_secret),
    )
    resp_auth.raise_for_status()
    resp_dict: dict = resp_auth.json()
    session.headers.update(
        {
            'Authorization': f'{resp_dict.get("access_token")} {resp_dict.get("token_type")}'
        },
    )


def list_devices(
        session: Session,
        page_size: Optional[int] = PAGE_SIZE,
        limit: Optional[int] = PAGE_SIZE,
) -> Generator[dict, None, None]:
    params: dict = {
        'page[offset]': 0,
        'page[limit]': page_size,
    }

    results: int = 0
    while results < limit:
        try:
            resp_accounts: Response = session.get(
                url=URL_DEVICES,
                params=params,
            )
            resp_accounts.raise_for_status()
            data: dict = resp_accounts.json()
            devices: list = data.get('data')
            yield from devices
            if len(devices) < PAGE_SIZE:
                break
            params['page[offset]'] += page_size
        except HTTPError as exc_http:
            requests_log.error(f'{exc_http}: {exc_http.response.request.headers}')
            break
        except Exception as exc_dev:
            requests_log.error(exc_dev)
            break


def main(
        client_id: str,
        client_secret: str,
        api_key: str,
        page_size: Optional[int] = PAGE_SIZE,
        limit: Optional[int] = PAGE_SIZE,
        proxies: Optional[dict] = None,
) -> Generator[dict, None, None]:
    session = Session()

    headers: dict = {
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json',
        'x-api-key': api_key,
    }
    session.headers = headers
    session.proxies = proxies

    try:
        token = logon(
            session=session,
            client_id=client_id,
            client_secret=client_secret,
        )
    except HTTPError as http_err:
        print(f'HTTPError during logon: {http_err}')
        raise
    except Exception as exc_auth:
        print(f'Unexpected error during logon: {exc_auth}')
        raise

    try:
        yield from list_devices(session=session, page_size=page_size, limit=limit)
    except HTTPError as http_err:
        print(f'HTTPError during accounts retrieval: {http_err}')
        raise
    except Exception as exc_auth:
        print(f'Unexpected error during accounts retrieval: {exc_auth}')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--client_id',
        default=None,
        type=str,
        required=True,
        help='The Client ID for yourmVisionadmin',
    )
    parser.add_argument(
        '--client_secret',
        default=None,
        type=str,
        required=True,
        help='The Client Secret for yourmVisionadmin',
    )
    parser.add_argument(
        '--api_key',
        type=str,
        required=True,
        help='The Client Secret for yourmVisionadmin',
    )
    parser.add_argument(
        '--page_size',
        type=int,
        default=PAGE_SIZE,
        help='The results page size',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=PAGE_SIZE,
        help='The results maximum devices limit',
    )
    parser.add_argument(
        '--proxies',
        type=str,
        required=False,
        help="JSON structure specifying 'http' and 'https' proxy URLs",
    )

    args = parser.parse_args()

    proxies: Optional[dict] = None
    if proxies:
        try:
            proxies: dict = loads(args.proxies)
        except Exception as exc_json:
            print(f'WARNING: failure parsing proxies: {exc_json}: proxies provided: {proxies}')

    for machine in main(
        client_id=args.client_id,
        client_secret=args.client_secret,
        api_key=args.api_key,
        page_size=args.page_size,
        limit=args.limit,
        proxies=proxies,
    ):
        print(dumps(machine, indent=4))
    else:
        print('End of results')
