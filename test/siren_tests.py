import json
import siren
import unittest


class SirenTests(unittest.TestCase):

    def setUp(self):
        siren.app.config['TESTING'] = True
        self.app = siren.app.test_client()

    def test_stats_with_valid_point(self):
        resp = self.app.get('/crime/stats/45.521263,-122.698016')
        data = json.loads(resp.data)
        stats = data['result']['stats']

        self.assertEqual(len(stats), 22)
        self.assertEqual(stats[-1][0], 'Arson')
        self.assertEqual(stats[-1][1], 1)
        self.assertEqual(stats[0][0], 'Larceny')
        self.assertEqual(stats[0][1], 801)
        self.assertEqual(stats[5][0], 'Motor Vehicle Theft')
        self.assertEqual(stats[5][1], 68)

    def test_stats_with_invalid_point(self):
        # Try to get crimes for a point in San Francisco.
        resp = self.app.get('/crime/stats/37.785834,-122.406417')
        data = json.loads(resp.data)
        self.assertEqual(len(data['result']['stats']), 0)

    def test_stats_with_valid_point(self):
        resp = self.app.get('/crime/stats/45.521263,-122.698016')
        data = json.loads(resp.data)
        stats = data['result']['stats']

        # TODO: Expand on this test.
        self.assertEqual(stats[0][0], 'Larceny')
        self.assertEqual(stats[0][1], 801)

    def test_crimes_with_valid_point(self):
        resp = self.app.get('/crime/45.521263,-122.698016')
        data = json.loads(resp.data)
        crimes = data['result']['crimes']

        self.assertEqual(len(crimes), 194)

    def test_stats_with_valid_point_and_filter(self):
        resp = self.app.get('/crime/stats/45.521263,-122.698016?hour=1')
        data = json.loads(resp.data)
        stats = data['result']['stats']

        self.assertFalse('errors' in data['result'])

        self.assertEqual(len(stats), 9)
        self.assertEqual(stats[0][0], 'Larceny')
        self.assertEqual(stats[0][1], 7)
        self.assertEqual(stats[7][0], 'Trespass')
        self.assertEqual(stats[7][1], 1)
        self.assertEqual(stats[8][0], 'Aggravated Assault')
        self.assertEqual(stats[8][1], 1)

    def test_crimes_with_invalid_point(self):
        # Try to get crimes for a point in San Francisco.
        resp = self.app.get('/crime/37.785834,-122.406417')
        data = json.loads(resp.data)
        self.assertEqual(len(data['result']['crimes']), 0)


if __name__ == '__main__':
    unittest.main()
