# -*- coding: utf-8 -*-
import pprint
import logging
logger=logging.getLogger(__name__)
from .exceptions import RequestError, AuthentificationError,\
                        AutorisationError, PathNotFoundError, \
                        ConflictError, UploadExceedLimit, InternalError

def pretty_print_format(data={}, indent=8, width=80, depth=10):
    dict_string=pprint.pformat(data, indent=indent, width=width, depth=depth)
    return dict_string

def to_string_url(value=None):
    """
    Convert value to string url convention

    :param      value:  The value to convert
    :type       value:  number

    :returns:   The value converted
    :rtype:     string
    """
    return str(value).lower()

def evaluate(response=None):
    """
    Evaluate request response

    :param      response:        The response
    :type       response:        Response object

    :returns:   True if succeed
    :rtype:     boolean

    :raises     RuntimeError:  "error" value from response
    """
    status_code=response.status_code
    url=response.url
    logger.debug('Evaluate request response : status_code : %s / url : %s', status_code, url)
    if status_code == 200:
        return True
    elif status_code==400:
        raise RequestError(response)
    elif status_code==401:
        raise AuthentificationError(response)
    elif status_code==403:
        raise AutorisationError(response)
    elif status_code==404:
        raise PathNotFoundError(response)
    elif status_code==409:
        raise ConflictError(response)
    elif status_code==413:
        raise UploadExceedLimit(response)
    elif status_code==500:
        raise InternalError(response)
    else:
        raise RuntimeError('code {0} : {1} url:{2}'.format(
            status_code, response, url))

