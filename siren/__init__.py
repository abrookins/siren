import flask
from flask.ext.cache import Cache
from siren import util, crime_tracker
from siren.decorators import jsonp


app = flask.Flask(__name__)
app.config.from_envvar('SIREN_SETTINGS', silent=True)
cache = Cache(app)
crime_db = crime_tracker.PortlandCrimeTracker()


# Save profiling data if running in debug mode.
if app.config['DEBUG']:
    from werkzeug.contrib.profiler import ProfilerMiddleware
    f = open('/tmp/profiler.log', 'a')
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, f)


def get_point(latitude, longitude):
    """
    Return a 400 status if ``latitude`` and ``longitude`` are not coercible to
    floats.
    """
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        flask.abort(400)

    return latitude, longitude


def get_crimes(latitude, longitude):
    """
    Return all crimes found within 1/2 mile of ``latitude`` and ``longitude``.
    """
    point = get_point(latitude, longitude)
    ignore = ['callback', '_']
    filters = {k: v for k, v in flask.request.args.items() if k not in ignore}
    return crime_db.get_crimes_nearby(point, filters)


@app.route('/crime/stats/<latitude>,<longitude>')
@cache.cached()
@jsonp
def crime_stats(latitude, longitude):
    """
    Return statistics -- as now, only sums by category -- of crimes within 1/2
    mile of ``latitude`` and ``longitude``.
    """
    nearby_crimes, errors = get_crimes(latitude, longitude)
    stats = crime_db.get_stats_for_crimes(nearby_crimes)
    data = {'stats': stats}

    if errors:
        data['errors'] = errors

    return flask.jsonify(result=data)


@app.route('/crime/<latitude>,<longitude>')
@cache.cached()
@jsonp
def crimes(latitude, longitude):
    """
    Return raw crime data for all crimes within 1/2 mile of ``latitude`` and
    ``longitude``.
    """
    crimes, errors = get_crimes(latitude, longitude)
    # JSON requires that object keys be strings, so convert tuples to strings
    # like "37.785834,-122.406417"
    crimes = [dict(crime=c, point=','.join(str(p))) for p, c in crimes.items()]
    data = {'crimes': crimes}

    if errors:
        data['errors'] = errors

    return flask.jsonify(result=data)
