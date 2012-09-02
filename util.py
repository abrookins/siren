import collections
import cPickle
import csv
import itertools
import ogr
import os


from scipy.spatial import cKDTree
from scipy import inf


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")


def open_data_file(filename, mode='r'):
    return open(os.path.join(DATA_DIR, filename), mode)


def get_crime_data(filename):
    """
    Load Portland crime data.
    """
    crimes = collections.defaultdict(list)
    skipped = 0

    # State Plane Coordinate System (Oregon North - EPSG:2269, alt: EPSG:2913).
    nad83 = ogr.osr.SpatialReference()
    nad83.ImportFromEPSG(2269)

    # Latitude/longitude (WGS84 - EPSG:4326)
    wgs84 = ogr.osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)

    transformation = ogr.osr.CoordinateTransformation(nad83, wgs84)

    r = csv.reader(open_data_file(filename))

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
                crimes[point].append(row)

    return crimes, skipped


def make_crimes_db(filename='db'):
    crimes,  skipped = get_crime_data('crime_incident_data.csv')

    with open(filename, 'wb') as f:
        cPickle.dump(crimes, f)


def load_crimes_db(filename='db'):
    with open(filename) as f:
        return cPickle.load(f)


class PortlandCrimeTracker(object):

    def __init__(self, db_filename='db'):
        self.crimes = load_crimes_db(db_filename)
        self.points = self.crimes.keys()
        self.crime_kdtree = cKDTree(self.points)

    def get_stats_for_crimes(self, crimes):
        """
        Return the sum of different types of crimes found in `crimes`, a
        dictionary of coordinate points mapped to a list of crimes for that
        point.

        Each crime is itself a list of values describing the crime. The value in
        the fourth position of the list is the category of the crime, a string.
        """
        sums = collections.defaultdict(int)
        crimes_flat = itertools.chain.from_iterable(crimes.values())

        for c in crimes_flat:
            category = c[3]
            sums[category] += 1

        return sorted([(category, cat_sum) for category, cat_sum in sums.items()],
                      key=lambda x: x[1], reverse=True)

    def get_points_nearby(self, point, distance=250):
        """
        Given a list of coordinate tuples in `points`, find the nearest 250 points
        within 1/2 a mile of the tuple `point`.
        """

        # Find a maximum of 250 points with crimes within approximately 1/2 a mile.
        # Note: 1/4 mile is .005, 1/2 mile is .01, full mile is .02.
        distances, indices = self.crime_kdtree.query(point, k=distance,
                                                     distance_upper_bound=0.01)
        point_neighbors = []
        for index, distance in zip(indices, distances):
            if distance == inf:
                break
            point_neighbors.append(self.points[index])

        return point_neighbors

    def get_crimes_nearby(self, point):
        nearby_crimes = collections.defaultdict(list)

        if len(point) == 2:
            nearby_points = self.get_points_nearby(point)

            for p in nearby_points:
                point = ' '.join([str(p[0]), str(p[1])])
                nearby_crimes[point].extend(self.crimes[p])

        return nearby_crimes
