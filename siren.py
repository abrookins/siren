import flask
import os

from flask.ext.cache import Cache

from util import PortlandCrimeTracker
from decorators import jsonp

app = flask.Flask(__name__)
app.config.from_object('default_settings')
app.config.from_envvar('SIREN_SETTINGS')
cache = Cache(app)


# Serve static files if in debug mode.
if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'public')
    })


_crimes = PortlandCrimeTracker()


@cache.memoize()
def _get_crimes_nearby(point):
    """
    A wrapper around `PortlandCrimeTracker.get_crimes_nearby` that we can
    memoize.
    """
    return _crimes.get_crimes_nearby(point)


@cache.memoize()
def _get_stats_for_crimes(crimes):
    """
    A wrapper around `PortlandCrimeTracker.get_stats_for_crimes` that we can
    memoize.
    """
    return _crimes.get_stats_for_crimes(crimes)


def _get_point():
    """
    Get a lat/long pair from the current request, passed as the `point` GET
    parameter.
    """
    return flask.request.args.get('point', '').split(',')


@app.route('/crime/stats')
@jsonp
def crime_stats():
    point = _get_point()
    nearby_crimes = _get_crimes_nearby(point)
    stats = _get_stats_for_crimes(nearby_crimes)
    return flask.jsonify(result={'stats': stats})


@app.route('/crime/nearby')
@jsonp
def crimes():
    point = _get_point()
    nearby_crimes = _get_crimes_nearby(point)
    return flask.jsonify(result={'nearby': nearby_crimes})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
