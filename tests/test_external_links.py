"""Offline contracts for public external-link collection and checking."""

from __future__ import annotations

from http.cookiejar import Cookie
from io import BytesIO
import socket
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from scripts import external_links as links


COMMUNITY = 'https://github.com/markusthemaker/WSPRadar/discussions'
CATEGORY = COMMUNITY + '/categories/ask-a-question'
NEW_DISCUSSION = COMMUNITY + '/new?category=ask-a-question'


def github_html(url, categories=()):
    return ('<html><link rel="canonical" href="' + url + '">' + ''.join(
        '<a href="' + category + '">Category</a>' for category in categories) + '</html>').encode()


class Response(BytesIO):
    def __init__(self, status=200, body=b'ok', headers=None):
        super().__init__(body)
        self.status = status
        self.headers = headers or {}


class ExternalCollectionTests(unittest.TestCase):
    def test_html_entities_decode_once_and_css_queries_stay_literal(self):
        found = links.collect_external_links({
            'index.html': b'<a href="https://example.org/?value=&amp;quot;">entity</a>',
            'site.css': b'p{background:url("https://example.org/?value=&quot;")}',
        }, 'https://site.test')
        self.assertEqual(found, {'https://example.org/?value=&quot;': {'index.html', 'site.css'}})

    def test_malformed_external_url_identifies_its_source(self):
        with self.assertRaisesRegex(ValueError, 'Malformed URL in index.html'):
            links.collect_external_links({'index.html': b'<a href="https://example.org:bad/path">bad port</a>'}, 'https://site.test')

    def test_collects_html_css_and_srcset_and_retains_queries_and_locations(self):
        files = {
            'en/index.html': b'''<a href="https://EXAMPLE.org/a?q=1&amp;x=2#one">a</a>
                <a href="mailto:test@example.org">email</a><a href="/local">local</a>
                <a href="https://site.test:443/internal">same origin</a>
                <video poster="//media.test/poster.png" src="https://media.test/v.mp4"></video>
                <img srcset="https://img.test/a.png 1x, https://img.test/b.png 2x">
                <img srcset="data:image/png;base64,abc 1x, //img.test/c.png 2x">
                <div style="background: url('https://img.test/d.png')"></div>
                <style>@import "https://css.test/a.css"; p {background:url(//img.test/e.png)}</style>''',
            'assets/site.css': b'''/* url(https://ignored.test/a) */
                @import url("https://css.test/b.css"); @import 'https://css.test/c.css';
                p {background: url(https://EXAMPLE.org/a?q=1&x=2#two)}''',
            'de/index.html': b'<a href="https://example.org/a?q=2">other query</a>',
            'assets/ignored.js': b'"https://ignored.test/script"',
        }
        found = links.collect_external_links(files, 'https://site.test')
        self.assertEqual(found['https://example.org/a?q=1&x=2'], {'en/index.html', 'assets/site.css'})
        self.assertIn('https://example.org/a?q=2', found)
        for url in ('https://media.test/poster.png', 'https://media.test/v.mp4',
                    'https://img.test/a.png', 'https://img.test/b.png', 'https://img.test/c.png',
                    'https://img.test/d.png', 'https://img.test/e.png',
                    'https://css.test/a.css', 'https://css.test/b.css', 'https://css.test/c.css'):
            self.assertIn(url, found)
        self.assertEqual(len(found), 12)


class PublicFetchTests(unittest.TestCase):
    def setUp(self):
        self.public = patch.object(links, '_validate_public_destination')
        self.public_check = self.public.start()
        self.addCleanup(self.public.stop)
        self.opener_patch = patch.object(links, 'build_opener')
        self.opener = self.opener_patch.start().return_value
        self.addCleanup(self.opener_patch.stop)

    def test_get_has_no_authentication_or_cookies_and_closes_body(self):
        response = Response(body=b'x' * 5000)
        self.opener.open.return_value = response
        result = links._fetch('https://example.org/', timeout=3)
        request = self.opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertEqual(set(dict(request.header_items())), {'User-agent', 'Accept'})
        self.assertEqual(self.opener.open.call_args.kwargs, {'timeout': 3})
        self.assertTrue(response.closed)
        self.assertEqual(len(result.body), links.MAX_GENERIC_BYTES)

    def test_redirect_is_followed_checked_and_reported(self):
        first = Response(302, headers={'Location': '/current'})
        second = Response()
        self.opener.open.side_effect = [first, second]
        result = links._fetch('https://example.org/old', timeout=1)
        self.assertEqual(links._response_status(result)[0], 'redirected')
        self.assertEqual(result.final_url, 'https://example.org/current')
        self.assertEqual([call.args[0] for call in self.public_check.call_args_list],
                         ['https://example.org/old', 'https://example.org/current'])
        self.assertTrue(first.closed and second.closed)

    def test_successful_redirect_to_login_is_unverified(self):
        response = links._Response(200, 'https://example.org/users/sign_in', b'login', True)
        self.assertEqual(links._response_status(response)[0], 'unverified')

    def test_each_url_gets_a_fresh_empty_anonymous_cookie_jar(self):
        self.opener.open.side_effect = [Response(), Response()]
        links._fetch('https://example.org/first', timeout=1)
        links._fetch('https://example.org/second', timeout=1)
        cookie_processors = [next(handler for handler in call.args
                                  if isinstance(handler, links.HTTPCookieProcessor))
                             for call in links.build_opener.call_args_list]
        self.assertEqual(len(cookie_processors), 2)
        self.assertIsNot(cookie_processors[0].cookiejar, cookie_processors[1].cookiejar)
        self.assertTrue(all(type(processor.cookiejar) is links.CookieJar for processor in cookie_processors))
        self.assertEqual([len(processor.cookiejar) for processor in cookie_processors], [0, 0])

    def test_anonymous_cookie_handshake_can_revisit_the_same_url(self):
        def first_response(request, **kwargs):
            processor = next(handler for handler in links.build_opener.call_args.args
                             if isinstance(handler, links.HTTPCookieProcessor))
            processor.cookiejar.set_cookie(Cookie(
                0, 'session', 'anonymous', None, False, 'example.org', False,
                False, '/', True, False, None, True, None, None, {}))
            self.opener.open.side_effect = None
            self.opener.open.return_value = Response()
            return Response(302, headers={'Location': 'https://example.org/'})

        self.opener.open.side_effect = first_response
        response = links._fetch('https://example.org/', timeout=1)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.redirected)
        self.assertEqual(self.opener.open.call_count, 2)
        status, detail = links._response_status(response, requested_url='https://example.org/')
        self.assertEqual(status, 'available')
        self.assertNotIn('review', detail)

    def test_redirect_loop_and_limit_are_unverified_and_responses_close(self):
        loop = Response(301, headers={'Location': '/loop'})
        self.opener.open.return_value = loop
        with self.assertRaisesRegex(links._CheckFailure, 'loop') as caught:
            links._fetch('https://example.org/loop', timeout=1)
        self.assertEqual(caught.exception.status, 'unverified')
        self.assertTrue(loop.closed)
        responses = [Response(302, headers={'Location': f'/{i}'}) for i in range(links.MAX_REDIRECTS + 1)]
        self.opener.open.side_effect = responses
        with self.assertRaisesRegex(links._CheckFailure, 'More than') as caught:
            links._fetch('https://example.org/start', timeout=1)
        self.assertEqual(caught.exception.status, 'unverified')
        self.assertTrue(all(response.closed for response in responses))

    def test_http_error_resources_are_closed_and_statuses_are_distinct(self):
        for code, expected in ((404, 'broken'), (410, 'broken'), (401, 'unverified'),
                               (403, 'unverified'), (429, 'unverified'), (503, 'unverified')):
            with self.subTest(code=code):
                body = BytesIO(b'failure')
                self.opener.open.side_effect = HTTPError('https://example.org/', code, 'failed', {}, body)
                response = links._fetch('https://example.org/', timeout=1)
                self.assertEqual(links._response_status(response)[0], expected)
                self.assertTrue(body.closed)

    def test_network_failure_and_oversized_github_html_are_unverified(self):
        for error in (URLError('offline'), TimeoutError(), OSError('TLS failure')):
            with self.subTest(error=type(error).__name__):
                self.opener.open.side_effect = error
                with self.assertRaises(links._CheckFailure) as caught:
                    links._fetch('https://example.org/', timeout=1)
                self.assertEqual(caught.exception.status, 'unverified')
        response = Response(body=b'x' * (links.MAX_HTML_BYTES + 1))
        self.opener.open.side_effect = None
        self.opener.open.return_value = response
        with self.assertRaisesRegex(links._CheckFailure, 'size limit'):
            links._fetch(COMMUNITY, timeout=1, html=True)
        self.assertTrue(response.closed)

    def test_private_redirect_is_not_requested(self):
        self.public_check.side_effect = [None, links._CheckFailure('unverified', 'Non-public destination')]
        self.opener.open.return_value = Response(302, headers={'Location': 'http://127.0.0.1/admin'})
        with self.assertRaisesRegex(links._CheckFailure, 'Non-public'):
            links._fetch('https://example.org/', timeout=1)
        self.assertEqual(self.opener.open.call_count, 1)


class PublicAddressTests(unittest.TestCase):
    def test_literals_credentials_and_nonpublic_dns_are_rejected(self):
        for url in ('http://127.0.0.1/', 'http://10.0.0.2/', 'http://169.254.169.254/',
                    'http://[::1]/', 'http://localhost/', 'http://server.localhost/',
                    'https://user:password@example.org/'):
            with self.subTest(url=url), self.assertRaises(links._CheckFailure):
                links._validate_public_destination(url)
        with patch.object(socket, 'getaddrinfo', return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.1', 443))]):
            with self.assertRaisesRegex(links._CheckFailure, 'Non-public'):
                links._validate_public_destination('https://example.org/')

    def test_all_dns_answers_must_be_public(self):
        with patch.object(socket, 'getaddrinfo', return_value=[
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 443)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 443, 0, 0)),
        ]):
            with self.assertRaises(links._CheckFailure):
                links._validate_public_destination('https://example.org/')


class GitHubDiscussionTests(unittest.TestCase):
    def setUp(self):
        self.fetch_patch = patch.object(links, '_fetch')
        self.fetch = self.fetch_patch.start()
        self.addCleanup(self.fetch_patch.stop)
        self.responses = {
            COMMUNITY: links._Response(200, COMMUNITY, github_html(COMMUNITY, [CATEGORY]), False),
            CATEGORY: links._Response(200, CATEGORY, github_html(CATEGORY), False),
        }
        self.fetch.side_effect = lambda url, **kwargs: self.responses[url]

    def check(self, url=NEW_DISCUSSION):
        return links.check_external_links({url: {'en/report/index.html'}}, community_url=COMMUNITY)[0]

    def test_new_form_is_verified_using_public_category_and_never_login(self):
        result = self.check()
        self.assertEqual(result.status, 'available')
        self.assertEqual(result.url, NEW_DISCUSSION)
        self.assertEqual(result.locations, ('en/report/index.html',))
        self.assertIn('signed-in submission is not tested', result.detail)
        self.assertEqual([call.args[0] for call in self.fetch.call_args_list], [COMMUNITY, CATEGORY])

    def test_missing_category_is_broken_without_accepting_generic_200(self):
        self.responses[COMMUNITY] = links._Response(200, COMMUNITY, github_html(COMMUNITY), False)
        result = self.check()
        self.assertEqual(result.status, 'broken')
        self.assertIn('not listed', result.detail)
        self.assertEqual(self.fetch.call_count, 1)

    def test_changed_canonical_and_category_redirect_are_broken(self):
        for response in (links._Response(200, CATEGORY, github_html(COMMUNITY), False),
                         links._Response(200, CATEGORY + '-renamed', github_html(CATEGORY + '-renamed'), True)):
            with self.subTest(response=response):
                self.responses[CATEGORY] = response
                self.assertEqual(self.check().status, 'broken')

    def test_login_or_challenge_html_cannot_prove_category(self):
        self.responses[CATEGORY] = links._Response(200, CATEGORY, b'<html>Sign in</html>', False)
        self.assertEqual(self.check().status, 'unverified')

    def test_unavailable_index_propagates_unverified_not_missing_category(self):
        self.responses[COMMUNITY] = links._Response(429, COMMUNITY, b'rate limit', False)
        result = self.check()
        self.assertEqual(result.status, 'unverified')
        self.assertIn('429', result.detail)

    def test_invalid_new_form_category_is_rejected_before_request(self):
        for url in (COMMUNITY + '/new', COMMUNITY + '/new?category=a&category=b',
                    COMMUNITY + '/new?category=../other'):
            with self.subTest(url=url):
                self.assertEqual(self.check(url).status, 'broken')
        self.fetch.assert_not_called()

    def test_generic_url_uses_generic_status_without_github_probe(self):
        self.responses['https://example.org/'] = links._Response(200, 'https://example.org/', b'ok', False)
        result = self.check('https://example.org/')
        self.assertEqual(result.status, 'available')
        self.assertEqual(self.fetch.call_count, 1)

    def test_generic_handshake_returning_to_original_is_available_but_moved_url_is_redirected(self):
        url = 'https://example.org/'
        for destination, expected in ((url, 'available'), (url + 'moved', 'redirected'),
                                      (url + 'login', 'unverified')):
            with self.subTest(destination=destination):
                self.responses[url] = links._Response(200, destination, b'ok', True)
                self.assertEqual(self.check(url).status, expected)

    def test_category_aliases_reuse_one_index_and_one_category_request(self):
        results = links.check_external_links(
            {COMMUNITY: {'en/community/index.html'}, CATEGORY: {'en/index.html'},
             NEW_DISCUSSION: {'en/report/index.html'}}, community_url=COMMUNITY)
        self.assertEqual([result.status for result in results], ['available'] * 3)
        self.assertEqual([call.args[0] for call in self.fetch.call_args_list], [COMMUNITY, CATEGORY])


if __name__ == '__main__':
    unittest.main()
