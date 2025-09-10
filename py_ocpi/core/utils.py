import urllib
import base64
from datetime import datetime, timezone

from fastapi import Response, Request
from pydantic import BaseModel

from py_ocpi.core.enums import ModuleID, RoleEnum
from py_ocpi.core.config import settings
from py_ocpi.modules.versions.enums import VersionNumber


def set_pagination_headers(response: Response, link: str, total: int, limit: int):
    response.headers['Link'] = link
    response.headers['X-Total-Count'] = str(total)
    response.headers['X-Limit'] = str(limit)
    return response


def get_auth_token(request: Request) -> str:
    headers = request.headers
    headers_token = headers.get('authorization', 'Token Null')
    token = headers_token.split()[1]
    if token == 'Null':  # nosec
        return None
    return decode_string_base64(token)


def to_ocpi_isoformat(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


async def get_list(response: Response, filters: dict, module: ModuleID, role: RoleEnum,
                   version: VersionNumber, crud, *args, **kwargs):
    data_list, total, is_last_page = await crud.list(module, role, filters, *args, version=version, **kwargs)
    cleaned_filters = {k: v for k, v in filters.items() if v is not None}

    params = {}
    try:
        for k, v in cleaned_filters.items():
            if isinstance(v, datetime):
                params[k] = to_ocpi_isoformat(v)
            else:
                params[k] = v
    except Exception:
        params = dict(**cleaned_filters)

    link = ''
    params['offset'] = filters['offset'] + filters['limit']
    if not is_last_page:
        link = (f'<https://{settings.OCPI_HOST}/{settings.OCPI_PREFIX}/cpo'
                f'/{version}/{module}/?{urllib.parse.urlencode(params)}>; rel="next"')

    set_pagination_headers(response, link, total, filters['limit'])

    return data_list


def partially_update_attributes(instance: BaseModel, attributes: dict):
    for key, value in attributes.items():
        setattr(instance, key, value)


def encode_string_base64(input: str) -> str:
    input_bytes = base64.b64encode(bytes(input, 'utf-8'))
    return input_bytes.decode('utf-8')


def decode_string_base64(input: str) -> str:
    input_bytes = base64.b64decode(bytes(input, 'utf-8'))
    return input_bytes.decode('utf-8')


def construct_response_header(request_header):
    response_header = {
        "OCPI-from-party-id": settings.PARTY_ID,
        "OCPI-from-countrycode": settings.COUNTRY_CODE,
    }
    request_from_pid = request_header.get('ocpi-from-party-id')
    request_from_cc = request_header.get('ocpi-from-country-code')
    if request_from_pid:
        response_header['OCPI-to-party-id'] = request_from_pid
    if request_from_cc:
        response_header['OCPI-to-country-code'] = request_from_cc
    return response_header


def construct_routing_headers(request_header):
    routing_header = {}
    request_from_pid = request_header.get('ocpi-from-party-id')
    request_from_cc = request_header.get('ocpi-from-country-code')
    request_to_pid = request_header.get('ocpi-to-party-id')
    request_to_cc = request_header.get('ocpi-to-country-code')
    if request_from_pid:
        routing_header['OCPI-from-party-id'] = request_from_pid
    if request_from_cc:
        routing_header['OCPI-from-country-code'] = request_from_cc
    if request_to_pid:
        routing_header['OCPI-to-party-id'] = request_to_pid
    if request_to_cc:
        routing_header['OCPI-to-country-code'] = request_to_cc
    return routing_header
