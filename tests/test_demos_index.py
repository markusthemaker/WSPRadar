"""Focused contracts for the website-owned guided-demo discovery renderer."""

from copy import deepcopy
from html.parser import HTMLParser
import re
from types import SimpleNamespace
import unittest

from scripts.demos_index import render_demos_index


class Inventory(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        self.elements.append((tag, dict(attributes)))


class DemosIndexRendererTests(unittest.TestCase):
    def setUp(self):
        mode_ids = ('rx-benchmark', 'tx-benchmark', 'rx-performance', 'tx-performance')
        self.content = {
            'text': {
                'title': 'Choose <em>your question.</em>', 'mode_definition': '<strong>Benchmark</strong> compares.',
                'recommended': 'Recommended first demo', 'placeholder_accessible': 'Thumbnail placeholder:',
                'placeholder': 'THUMBNAIL PLACEHOLDER', 'learn': 'What you’ll learn', 'open_demo': 'Explore guided demo',
                'demo_singular': 'guided demo', 'demo_plural': 'guided demos',
                'collection_description': 'Choose a question.', 'unavailable': 'No guided demo yet',
            },
            'modes': [{'id': mode, 'label': mode.upper(), 'description': 'Description of ' + mode,
                       'question': 'Question about ' + mode} for mode in mode_ids],
            'cards': [],
        }
        for identity, modes in (('receiver', ['rx-benchmark']),
                                ('both', ['rx-benchmark', 'tx-benchmark']),
                                ('performance', ['rx-performance'])):
            self.content['cards'].append({
                'id': identity, 'modes': modes, 'title': identity.title(), 'context': 'Study context',
                'band': '40 m', 'stations': 'EXAMPLE', 'topic': 'Question topic',
                'question': 'What does the evidence show?', 'learn': ['Read the evidence.', 'Check the context.'],
                'thumb_icon': 'placeholder', 'thumb_title': 'Evidence view', 'thumb_text': 'Keep the original scale.',
            })
        self.published = [{'id': card['id']} for card in self.content['cards']]
        icons = {name: f'web/icons/{name}.svg' for name in
                 (*mode_ids, 'placeholder', 'wspr-database', 'try-demo', 'evidence-chart', 'analysis-laptop')}
        self.assets = {'icons': icons, 'publish_files': list(icons.values())}
        self.template = SimpleNamespace(read_text=lambda encoding:
            '${cards}${rx_benchmark}${tx_benchmark}${rx_performance}${tx_performance}')

    def render(self, content=None):
        return render_demos_index(content or self.content, self.published, self.assets, self.template,
                                  'en', lambda language, suffix: f'/{language}/{suffix}')

    def test_card_inventory_matches_each_published_demo_exactly_once(self):
        for change in ('duplicate', 'missing', 'unknown'):
            with self.subTest(change=change):
                content = deepcopy(self.content)
                if change == 'duplicate':
                    content['cards'].append(deepcopy(content['cards'][0]))
                elif change == 'missing':
                    content['cards'].pop()
                else:
                    content['cards'][0]['id'] = 'unpublished'
                with self.assertRaisesRegex(ValueError, 'cover each published demo exactly once'):
                    self.render(content)

    def test_card_mode_membership_rejects_empty_duplicate_and_unknown_modes(self):
        for modes in ([], ['rx-benchmark', 'rx-benchmark'], ['unknown-mode']):
            with self.subTest(modes=modes):
                content = deepcopy(self.content)
                content['cards'][0]['modes'] = modes
                with self.assertRaisesRegex(ValueError, 'Invalid demo discovery modes: receiver'):
                    self.render(content)

    def test_duplicate_mode_definitions_are_rejected(self):
        content = deepcopy(self.content)
        content['modes'].append(deepcopy(content['modes'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate demo discovery mode'):
            self.render(content)

    def test_relative_routes_preserve_canonical_identities_without_search(self):
        source = self.render()
        elements = Inventory(source).elements
        links = [attrs for tag, attrs in elements if tag == 'a']
        self.assertEqual([link['href'] for link in links],
                         ['/en/demos/receiver/', '/en/demos/both/', '/en/demos/performance/'])
        self.assertTrue(all('target' not in link for link in links))
        cards = [attrs for tag, attrs in elements if tag == 'article']
        self.assertEqual([card['id'] for card in cards], ['demo-' + demo['id'] for demo in self.published])
        self.assertTrue(all('data-demo-search-text' not in card for card in cards))
        self.assertNotIn('data-filter-text=', source)
        self.assertTrue(all('hidden' not in card for card in cards), 'cards are visible before JavaScript runs')

    def test_mode_counts_include_shared_membership_and_leave_unavailable_mode_inactive(self):
        source = self.render()
        elements = Inventory(source).elements
        buttons = [attrs for tag, attrs in elements if tag == 'button']
        self.assertEqual([button['data-filter'] for button in buttons],
                         ['rx-benchmark', 'tx-benchmark', 'rx-performance'])
        for mode, count in (('rx-benchmark', 2), ('tx-benchmark', 1), ('rx-performance', 1)):
            match = re.search(r'<button[^>]*data-filter="' + mode + r'".*?<span class="use-count">(\d+) ', source)
            self.assertIsNotNone(match)
            self.assertEqual(int(match[1]), count)
        inactive = [attrs for tag, attrs in elements if attrs.get('aria-disabled') == 'true']
        self.assertEqual(len(inactive), 1)
        self.assertNotIn('data-filter', inactive[0])
        self.assertIn('No guided demo yet', source)
        shared = next(attrs for tag, attrs in elements if attrs.get('id') == 'demo-both')
        self.assertEqual(shared['data-modes'].split(), ['rx-benchmark', 'tx-benchmark'])

    def test_evidence_preview_retains_original_link_and_responsive_images(self):
        card = self.content['cards'][0]
        card['subtitle'] = 'Direction & distance'
        card['thumb_alt'] = 'Measured evidence <with context>'
        card['thumbnail'] = {
            'images': [{'path': 'web/example-480.webp', 'width': 480, 'height': 270},
                       {'path': 'web/example-960.webp', 'width': 960, 'height': 540}],
            'original': '/assets/demos/example/original.png',
        }
        self.content['text']['open_original'] = 'Open original figure'
        self.assets['publish_files'].extend(item['path'] for item in card['thumbnail']['images'])
        source = self.render()
        elements = Inventory(source).elements
        link = next(attrs for tag, attrs in elements if attrs.get('href') == card['thumbnail']['original'])
        self.assertEqual(link['target'], '_blank')
        self.assertEqual(set(link['rel'].split()), {'noopener', 'noreferrer'})
        preview = next(attrs for tag, attrs in elements if attrs.get('alt') == card['thumb_alt'])
        self.assertEqual(preview['src'], '/assets/landing/web/example-960.webp')
        self.assertEqual(preview['srcset'], '/assets/landing/web/example-480.webp 480w, /assets/landing/web/example-960.webp 960w')
        self.assertEqual((preview['width'], preview['height']), ('960', '540'))
        self.assertEqual(preview['loading'], 'lazy')
        self.assertIn('<p class="card-subtitle">Direction &amp; distance</p>', source)
        self.assets['publish_files'].remove('web/example-480.webp')
        with self.assertRaisesRegex(ValueError, 'Unpublished demo discovery thumbnail: receiver'):
            self.render()

    def test_unpublished_icons_are_rejected(self):
        self.assets['publish_files'].remove(self.assets['icons']['placeholder'])
        with self.assertRaisesRegex(ValueError, 'Unpublished demo discovery icon: placeholder'):
            self.render()


if __name__ == '__main__':
    unittest.main()
