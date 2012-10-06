import collections
import cPickle
import itertools

from scipy.spatial import cKDTree
from scipy import inf


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