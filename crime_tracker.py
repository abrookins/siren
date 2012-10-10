import collections
import cPickle
import itertools

from scipy.spatial import cKDTree
from scipy import inf


def make_hour_filter(hour):
    """
    Return True if the hour a crime was committed is within `hour`. For use
    with the `filter()` builtin.
    """
    def inner(crime):
        crime_hour = crime[2].split(':')[0]
        return int(crime_hour) == hour
    return inner


class PortlandCrimeTracker(object):

    DEFAULT_DATABASE_NAME = 'db'

    def __init__(self, db_filename=DEFAULT_DATABASE_NAME):
        self.crimes = self.load_crimes_db(db_filename)
        self.points = self.crimes.keys()
        self.crime_kdtree = cKDTree(self.points)

    def load_crimes_db(self, filename='db'):
        with open(filename) as f:
            return cPickle.load(f)

    def get_stats_for_crimes(self, crimes):
        """
        Return the sums of different types of crimes found in `crimes`, a
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

    def filter(self, crimes, filters):
        if filters:
            for f in filters:
                crimes = filter(f, crimes)
        return crimes

    def get_crimes_nearby(self, point, filters=None):
        """
        Return crimes near `point`, an iterable of (x, y) coordinates.

        The result is a dictionary of crimes whose keys are the coordinates of
        crime locations and values are lists of crimes, e.g.:

            {
                (1.2343, 34.2343): [crime1, crime2, crime3],
                (2.3676 55.2341): [crime2, crime2]
            }

        If an iterable of callables is passed in `filters`, they will be applied
        in order using a `filter()` to the resulting lists of crimes.
        """
        nearby_crimes = collections.defaultdict(list)

        if 2 > len(point) < 2:
            raise RuntimeError("Point must be an iterable of (x, y) coordinates")

        nearby_points = self.get_points_nearby(point)

        for point in nearby_points:
            crimes = self.crimes[point]
            if filters:
                crimes = self.filter(crimes, filters)
            nearby_crimes[point].extend(crimes)

        return nearby_crimes