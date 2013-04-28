import cPickle
import collections
import csv
import ogr
import os


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")


def open_data_file(filename, mode='r'):
    return open(os.path.join(DATA_DIR, filename), mode)


def get_crime_data(filename):
    """
    Load Portland crime data from a CSV file ``filename``.

    Returns a tuple: header (list of string column names), crimes (a dict in
    which coordinate tuples map to lists of crimes, skipped (number of skipped
    rows).
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
    header = None

    for i, row in enumerate(r):
        if i == 0:
            header = row
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

    return header, crimes, skipped


def make_crimes_db(db_filename='db', data_filename='crime_incident_data.csv'):
    header, crimes, skipped = get_crime_data(data_filename)

    with open(db_filename, 'wb') as f:
        cPickle.dump({
            'header': header, 'crimes': crimes
        }, f)

    print 'Saved database to: %s. Skipped %s rows.' % (db_filename, skipped)
