import csv
import flask
import itertools
import ogr
import os

from scipy.spatial import cKDTree
from scipy import inf


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

app = flask.Flask(__name__)
app.config.from_object('default_settings')
#app.config.from_envvar('SIREN_SETTINGS')


def get_points_nearby(points, point):
    """
    Given a list of coordinate tuples in `points`, find the nearest 250 points
    within 1/2 a mile of the tuple `point`.
    """
    tree = cKDTree(points)
    # Find a maximum of 250 points with crimes within approximately 1/2 a mile.
    # Note: 1/4 mile is .005, 1/2 mile is .01, full mile is .02.
    distances, indices = tree.query(point, k=250, distance_upper_bound=0.01)
    point_neighbors = []
    for index, distance in zip(indices, distances):
        if distance == inf:
            break
        point_neighbors.append(points[index])

    return point_neighbors


class PortlandCrimeTracker(object):

    crimes = None

    def __init__(self):
        self.crimes,  self.skipped = self.get_crimes()

    def open_data_file(self, filename, mode='r'):
        return open(os.path.join(DATA_DIR, filename), mode)

    def get_crimes(self):
        """
        Load crime data.

        TODO: `from` and `to` coordinate systems as class variables?
        """
        crimes = {}
        skipped = 0

        # State Plane Coordinate System (Oregon North - EPSG:2269, alt: EPSG:2913).
        nad83 = ogr.osr.SpatialReference()
        nad83.ImportFromEPSG(2269)

        # Latitude/longitude (WGS84 - EPSG:4326)
        wgs84 = ogr.osr.SpatialReference()
        wgs84.ImportFromEPSG(4326)

        transformation = ogr.osr.CoordinateTransformation(nad83, wgs84)
        r = csv.reader(self.open_data_file("crime_incident_data.csv"))

        for i, row in enumerate(r):
            if not i:
                continue
            x, y = float(row[8]) if row[8] else 0, float(row[9] if row[9] else 0)
            if x and y:
                try:
                    coord = transformation.TransformPoint(x, y)
                    # The order here (1, 0) is intended.
                    point = (coord[1], coord[0])
                except TypeError:
                    skipped += 1
                else:
                    row.append(point)
                    if point in crimes:
                        crimes[point].append(row)
                    else:
                        crimes[point] = [row]

        return crimes, skipped

    def get_stats_for_crimes(self, crimes):
        """
        Return the sum of different types of crimes found in `crimes`, a
        dictionary of coordinate points mapped to a list of crimes for that
        point.

        Each crime is itself a list of values describing the crime. The value in
        the fourth position of the list is the category of the crime, a string.
        """
        sums = {}
        crimes_flat = itertools.chain.from_iterable(crimes.values())

        for c in crimes_flat:
            category = c[3]
            if category in sums:
                sums[category] += 1
            else:
                sums[category] = 1

        return sums

    def get_crimes_nearby(self, point):
        nearby_crimes = {}

        if len(point) == 2:
            nearby_points = get_points_nearby(self.crimes.keys(), point)

            for p in nearby_points:
                point = ' '.join([str(p[0]), str(p[1])])

                if point in nearby_crimes:
                    nearby_crimes[point].extend(self.crimes[p])
                else:
                    nearby_crimes[point] = self.crimes[p]

        return nearby_crimes


_crimes = PortlandCrimeTracker()


@app.route('/crime_stats')
def crime_stats():
    point = flask.request.args.get('point', '').split(',')
    nearby_crimes = _crimes.get_crimes_nearby(point)
    stats = _crimes.get_stats_for_crimes(nearby_crimes)
    return flask.jsonify(result={'stats': stats})


@app.route('/nearby_crimes')
def crimes():
    point = flask.request.args.get('point', '').split(',')
    nearby_crimes = _crimes.get_crimes_nearby(point)
    return flask.jsonify(result={'nearby': nearby_crimes})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
