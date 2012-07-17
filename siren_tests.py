import json
import unittest

import siren


class TestSiren(unittest.TestCase):

    def setUp(self):
        siren.app.config['TESTING'] = True
        self.app = siren.app.test_client()

    def test_with_valid_point(self):
        resp = self.app.get('/?point=45.521263,-122.698016')
        data = json.loads(resp.data)

        self.assertEqual(len(data['result']['nearby']), 194)
        self.assertEqual(len(data['result']['stats']), 22)

        self.assertEqual(data['result']['stats']['Homicide'], 1)
        self.assertEqual(data['result']['stats']['Larceny'], 801)
        self.assertEqual(data['result']['stats']['Motor Vehicle Theft'], 68)

    def test_with_invalid_point(self):
        # Try to get crimes for a point in San Francisco.
        resp = self.app.get('/?point=37.785834,-122.406417')
        data = json.loads(resp.data)
        self.assertEqual(len(data['result']['nearby']), 0)
        self.assertEqual(len(data['result']['stats']), 0)

if __name__ == '__main__':
    unittest.main()