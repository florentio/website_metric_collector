#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   http_request.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------

import collections
import http.client
import re
import socket
import ssl
import timeit
from urllib.parse import urlparse

from metrics.utils.constants import HTTP_STATUS_CODES
from metrics.utils.helpers import print_message

HTTPRequests = collections.namedtuple(
    'HTTPRequests', ['urls', 'timeout']
)


class RequestResult:
    """
    A class to contains result of an URL check.
    The redirect attribute is a Result object that the URL was redirected to.

    ...

    Attributes
    ----------
    url : str
        The url of the website
    status : int
        The http response status
    desc : str
        The http response message
    latency : str
        The http response time converted int to st
    content : str
        The http response content
    content_pattern : str
        The regex pattern to search in http response
    page_content_ok : boolean
        if or not  content_pattern is found in the http content
    """

    def __init__(self, url, status=0, desc='', latency=0, content_pattern='', page_content_ok=True):
        """
        Parameters
        ----------
        url : str
            The url of the website
        status : int
            The http response status
        desc : str
            The http response message
        latency : str
            The http response time converted int to str
        content_pattern : str
            The regex pattern to search in http response
        page_content_ok : boolean
            if or not  content_pattern is found in the http content
        """

        self.url = url
        self.status = status
        self.desc = desc
        self.headers = None
        self.latency = latency
        self.content = ''
        self.content_pattern = content_pattern
        self.redirect = None,
        self.page_content_ok = page_content_ok

    def __repr__(self):
        if self.status == 0:
            return f'{self.url} ... {self.desc}'
        return f'{self.url} ... {self.status} {self.desc} ({self.latency}) ... ({self.page_content_ok})'

    def fill_headers(self, headers):
        """Takes a list of tuples and converts it a dictionary."""
        self.headers = {h[0]: h[1] for h in headers}


def parse_url(url):
    """Returns an object with properties representing

    scheme:   URL scheme specifier
    netloc:   Network location part
    path:     Hierarchical path
    params:   Parameters for last path element
    query:    Query component
    fragment: Fragment identifier
    username: User name
    password: Password
    hostname: Host name (lower case)
    port:     Port number as integer, if present
    """
    loc = urlparse(url)

    # if the scheme (http, https ...) is not available urlparse wont work
    if loc.scheme == "":
        url = 'http://' + url
        loc = urlparse(url)
    return loc


def _http_connect(loc, timeout):
    """Make the connection to the host and returns an HTTP or HTTPS connections."""
    if loc.scheme == "https":
        ssl_context = ssl.SSLContext()
        return http.client.HTTPSConnection(
            loc.netloc, context=ssl_context, timeout=timeout)
    return http.client.HTTPConnection(loc.netloc, timeout=timeout)


def _http_request(loc, timeout):
    """Performs a HTTP request and return response in a RequestResult object"""
    conn = _http_connect(loc, timeout)
    method = 'GET'

    conn.request(method, loc.path)
    resp = conn.getresponse()

    result = RequestResult(loc.geturl())
    result.status = resp.status
    result.desc = resp.reason
    result.fill_headers(resp.getheaders())

    # status code is not 204 (no content) and not a redirect
    if resp.status not in HTTP_STATUS_CODES:
        result.content = resp.read().decode('utf-8')

    conn.close()
    return result


def http_response(url, timeout, pattern=None):
    """Returns the HTTP response code.

    If the response code is a temporary or permanent redirect then it
    follows to the redirect URL and returns its response code.

    Returns an object RequestResult  HTTP response code and description etc... .
    """
    loc = parse_url(url)
    result = RequestResult(url=url)

    try:
        start = timeit.default_timer()
        result = _http_request(loc, timeout)
        result.latency = '{:2.3}'.format(timeit.default_timer() - start)
        if pattern:
            result.content_pattern = pattern

        if 400 <= result.status < 500:
            return result

        # if response code is a HTTP redirect then follow it recursively
        if result.status in HTTP_STATUS_CODES[1:]:
            # if URL in Location is a relative URL, ie starts with a /, then
            # reconstruct the new URL using the current one's scheme and host
            new_url = result.headers.get('Location')
            if new_url.startswith('/'):
                new_url = '{}://{}{}'.format(loc.scheme, loc.netloc, new_url)
            result.redirect = http_response(new_url, timeout, pattern)

        # check if the result content match the defined pattern
        if result.content and pattern and not pattern == '':
            result.page_content_ok = (re.search(pattern, result.content) is not None)

    except socket.gaierror as e:
        result.desc = 'Could not resolve the url'
        result.page_content_ok = False
        print_message(f'{result.desc} {url} , socket error is  {e}')
    except (TimeoutError, socket.timeout):
        result.desc = 'Operation timed out'
        result.page_content_ok = False
        print_message(f'{result.desc} {url}')
    except Exception as e:
        result.desc = 'Could not resolve the url'
        result.page_content_ok = False
        print_message(f'{result.desc} {url} , os error is  {e}')

    return result
