"""Check public external resources referenced by a generated static website.

Checks use unauthenticated, bounded HTTP requests. They neither crawl linked
pages nor prove that a signed-in form can be submitted. Each checked URL gets a
fresh in-memory cookie jar for server-issued anonymous session cookies; browser
cookies, saved cookies, and user credentials are never loaded.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from html.parser import HTMLParser
from http.client import HTTPException
from http.cookiejar import CookieJar
import ipaddress
import re
import socket
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urldefrag, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPCookieProcessor, HTTPRedirectHandler, ProxyHandler, Request, build_opener


MAX_REDIRECTS = 5
MAX_HTML_BYTES = 2 * 1024 * 1024
MAX_GENERIC_BYTES = 1024
_CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_CSS_URL = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s)]*))\s*\)", re.IGNORECASE)
_CSS_IMPORT = re.compile(r"@import\s+(?:\"([^\"]*)\"|'([^']*)')", re.IGNORECASE)


@dataclass(frozen=True)
class ExternalLinkResult:
    url: str
    status: str
    detail: str
    locations: tuple[str, ...]


@dataclass(frozen=True)
class _Response:
    status: int
    final_url: str
    body: bytes
    redirected: bool


class _CheckFailure(Exception):
    def __init__(self, status: str, detail: str):
        super().__init__(detail)
        self.status = status


def _normalize_url(value: str, base: str) -> str | None:
    value = value.strip()
    if not value or value.startswith('#'):
        return None
    parsed = urlsplit(urljoin(base, value))
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.netloc:
        return None
    # Host/scheme are case-insensitive; preserve path and query exactly.
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or '/', parsed.query, ''))


def _origin(url: str) -> tuple[str, str | None, int | None]:
    parsed = urlsplit(url)
    return parsed.scheme.lower(), parsed.hostname, parsed.port or (443 if parsed.scheme.lower() == 'https' else 80)


def _css_links(text: str):
    text = _CSS_COMMENT.sub('', text)
    for expression in (_CSS_URL, _CSS_IMPORT):
        for match in expression.finditer(text):
            yield next(group for group in match.groups() if group is not None)


def _srcset_links(value: str):
    # URLs in srcset cannot contain literal whitespace. Commas inside data URLs
    # belong to the URL; descriptors are skipped until the next candidate.
    position = 0
    while position < len(value):
        while position < len(value) and (value[position].isspace() or value[position] == ','):
            position += 1
        start = position
        while position < len(value) and not value[position].isspace():
            position += 1
        candidate = value[start:position]
        if not candidate:
            break
        yield candidate.rstrip(',')
        if candidate.endswith(','):
            continue
        while position < len(value) and value[position] != ',':
            position += 1


class _ResourceInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self._inside_style = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.links.extend(attrs[name] for name in ('href', 'src', 'poster') if attrs.get(name))
        if attrs.get('srcset'):
            self.links.extend(_srcset_links(attrs['srcset']))
        if attrs.get('style'):
            self.links.extend(_css_links(attrs['style']))
        if tag == 'style':
            self._inside_style = True

    def handle_endtag(self, tag):
        if tag == 'style':
            self._inside_style = False

    def handle_data(self, data):
        if self._inside_style:
            self.links.extend(_css_links(data))


def collect_external_links(files: dict[str, bytes], site_url: str) -> dict[str, set[str]]:
    """Collect external HTML/CSS resources, retaining every referring filename."""
    links: dict[str, set[str]] = {}
    site_origin = _origin(site_url)
    for name, content in files.items():
        suffix = name.rsplit('.', 1)[-1].lower()
        if suffix not in ('html', 'css'):
            continue
        source = content.decode('utf-8')
        if suffix == 'html':
            inventory = _ResourceInventory()
            inventory.feed(source)
            candidates = inventory.links
        else:
            candidates = _css_links(source)
        base = urljoin(site_url.rstrip('/') + '/', name)
        for candidate in candidates:
            try:
                url = _normalize_url(candidate, base)
                if url is not None and _origin(url) != site_origin:
                    links.setdefault(url, set()).add(name)
            except ValueError as error:
                raise ValueError(f'Malformed URL in {name}: {candidate}') from error
    return links


def _validate_public_destination(url: str) -> None:
    """Reject credentials and local addresses before every request/redirect."""
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            raise _CheckFailure('unverified', 'Destination is not an HTTP(S) URL.')
        if parsed.username is not None or parsed.password is not None:
            raise _CheckFailure('unverified', 'URLs containing credentials are not requested.')
        if parsed.hostname.lower() == 'localhost' or parsed.hostname.lower().endswith('.localhost'):
            raise _CheckFailure('unverified', 'Local destinations are not requested.')
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        try:
            addresses = [ipaddress.ip_address(parsed.hostname)]
        except ValueError:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(parsed.hostname, port, type=socket.SOCK_STREAM)]
        if not addresses or any(not address.is_global for address in addresses):
            raise _CheckFailure('unverified', 'Non-public network destinations are not requested.')
    except (OSError, ValueError) as error:
        raise _CheckFailure('unverified', f'Destination resolution failed: {type(error).__name__}.') from error


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _fetch(url: str, *, timeout: float, html: bool = False) -> _Response:
    # Anonymous cookies support public session handshakes. The fresh jar is
    # isolated to this URL's redirect chain and is never persisted or reused.
    anonymous_cookies = CookieJar()
    opener = build_opener(ProxyHandler({}), HTTPCookieProcessor(anonymous_cookies), _NoRedirect())
    current = url
    visited = set()
    for redirect_count in range(MAX_REDIRECTS + 1):
        # A public cookie handshake may return to the same URL with a new
        # anonymous session. Only repeated URL + cookie state proves a loop.
        cookie_state = tuple(sorted((cookie.domain, cookie.path, cookie.name, cookie.value)
                                    for cookie in anonymous_cookies))
        visit = (current, cookie_state)
        if visit in visited:
            raise _CheckFailure('unverified', 'Redirect loop detected; a session-dependent flow or server behavior prevents public verification.')
        visited.add(visit)
        _validate_public_destination(current)
        request = Request(current, headers={'User-Agent': 'WSPRadar-LinkCheck/1.0', 'Accept': 'text/html, */*;q=0.8'})
        try:
            try:
                response = opener.open(request, timeout=timeout)
            except HTTPError as error:
                response = error
            with response:
                status = response.status
                if status in (301, 302, 303, 307, 308):
                    location = response.headers.get('Location')
                    if not location:
                        raise _CheckFailure('broken', f'HTTP {status} redirect has no destination.')
                    if redirect_count == MAX_REDIRECTS:
                        raise _CheckFailure('unverified', f'More than {MAX_REDIRECTS} redirects; the public destination could not be established.')
                    current = urldefrag(urljoin(current, location))[0]
                    continue
                limit = MAX_HTML_BYTES if html else MAX_GENERIC_BYTES
                body = response.read(limit + 1)
                if html and len(body) > limit:
                    raise _CheckFailure('unverified', 'Public HTML exceeds the verification size limit.')
                return _Response(status, current, body[:limit], redirect_count > 0)
        except _CheckFailure:
            raise
        except (URLError, OSError, HTTPException, ValueError) as error:
            raise _CheckFailure('unverified', f'HTTP request failed: {type(error).__name__}.') from error
    raise AssertionError('Redirect loop must return or fail within the bound.')


def _response_status(response: _Response, *, requested_url: str | None = None) -> tuple[str, str]:
    if 200 <= response.status < 300:
        if response.redirected:
            destination = urlsplit(response.final_url)
            if re.search(r'/(?:login|log-in|signin|sign-in|sign_in|servicelogin)(?:/|$)', destination.path, re.IGNORECASE):
                return 'unverified', f'Redirected to a sign-in page: {response.final_url}; public availability is unverified.'
            if response.final_url == requested_url:
                return 'available', f'HTTP {response.status}; anonymous session handshake returned to the configured URL.'
            return 'redirected', f'Available after redirect to {response.final_url}; review the configured URL.'
        return 'available', f'HTTP {response.status}.'
    if response.status in (404, 410):
        return 'broken', f'HTTP {response.status}: resource is missing.'
    return 'unverified', f'HTTP {response.status}: public availability could not be verified.'


class _GitHubInventory(HTMLParser):
    def __init__(self, base: str):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.canonical: set[str] = set()
        self.links: set[str] = set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if not attrs.get('href'):
            return
        url = _normalize_url(attrs['href'], self.base)
        if url is None:
            return
        if tag == 'a':
            self.links.add(url)
        if tag == 'link' and 'canonical' in attrs.get('rel', '').lower().split():
            self.canonical.add(url)


def _github_page(url: str, timeout: float, *, fetch=None) -> _GitHubInventory:
    response = (fetch or _fetch)(url, timeout=timeout, html=True)
    status, detail = _response_status(response)
    if response.redirected:
        raise _CheckFailure('broken', f'GitHub discussion URL redirects to {response.final_url}; update the configured URL.')
    if status != 'available':
        raise _CheckFailure(status, detail)
    if response.status != 200:
        raise _CheckFailure('unverified', f'Expected public GitHub HTML, received HTTP {response.status}.')
    inventory = _GitHubInventory(url)
    inventory.feed(response.body.decode('utf-8', errors='replace'))
    if not inventory.canonical:
        raise _CheckFailure('unverified', 'Public GitHub page has no canonical URL; a login, challenge, or changed page cannot prove availability.')
    if inventory.canonical != {url}:
        raise _CheckFailure('broken', 'GitHub canonical URL differs: ' + ', '.join(sorted(inventory.canonical)))
    return inventory


def _github_target(url: str, community_url: str) -> str | None:
    parsed, community = urlsplit(url), urlsplit(community_url)
    if _origin(url) != _origin(community_url):
        return None
    if parsed.path == community.path and not parsed.query:
        return community_url
    if parsed.path == community.path + '/new':
        categories = parse_qs(parsed.query).get('category', [])
        if len(categories) != 1 or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', categories[0]):
            raise _CheckFailure('broken', 'New-discussion link must select one valid category slug.')
        return community_url + '/categories/' + categories[0]
    if parsed.path.startswith(community.path + '/categories/'):
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))
    return None


def check_external_links(links: dict[str, set[str]], *, community_url: str,
                         timeout: float = 10, workers: int = 4) -> list[ExternalLinkResult]:
    """Return availability results without printing, writing, or authenticating.

New-discussion links are checked through public category pages and current
category membership. This proves the destination, not signed-in submission.
"""
    if timeout <= 0 or not 1 <= workers <= 4:
        raise ValueError('Use a positive timeout and one to four workers.')
    community_url = _normalize_url(community_url, community_url)
    if community_url is None or urlsplit(community_url).hostname != 'github.com':
        raise ValueError('community_url must be a public github.com URL.')
    responses: dict[tuple[str, bool], Future] = {}
    response_lock = Lock()

    def fetch_once(url: str, *, timeout: float, html: bool = False) -> _Response:
        key = (url, html)
        with response_lock:
            owner = key not in responses
            if owner:
                responses[key] = Future()
            response = responses[key]
        if owner:
            try:
                response.set_result(_fetch(url, timeout=timeout, html=html))
            except Exception as error:
                # Share failures as failures; unexpected errors still propagate.
                response.set_exception(error)
        return response.result()

    targets: dict[str, str | None] = {}
    failures: dict[str, _CheckFailure] = {}
    for url in links:
        try:
            targets[url] = _github_target(url, community_url)
        except _CheckFailure as error:
            failures[url] = error
    community_page = None
    community_error = None
    if any(target is not None for target in targets.values()):
        try:
            community_page = _github_page(community_url, timeout, fetch=fetch_once)
        except _CheckFailure as error:
            community_error = error

    def check_one(url: str) -> ExternalLinkResult:
        try:
            if url in failures:
                raise failures[url]
            target = targets[url]
            if target is not None:
                if community_error is not None:
                    raise _CheckFailure(community_error.status, 'Community index: ' + str(community_error))
                if target != community_url:
                    if target not in community_page.links:
                        raise _CheckFailure('broken', f'Category is not listed by the current community index: {target}')
                    _github_page(target, timeout, fetch=fetch_once)
                detail = 'Public GitHub community verified.' if target == community_url else f'Public category and current membership verified: {target}'
                if urlsplit(url).path.endswith('/new'):
                    detail += '; signed-in submission is not tested.'
                status = 'available'
            else:
                status, detail = _response_status(fetch_once(url, timeout=timeout), requested_url=url)
        except _CheckFailure as error:
            status, detail = error.status, str(error)
        return ExternalLinkResult(url, status, detail, tuple(sorted(links[url])))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(check_one, sorted(links)))
