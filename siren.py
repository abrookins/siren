import flask
import os

from flask.ext.cache import Cache

from crime_tracker import PortlandCrimeTracker
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


def get_point(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        flask.abort(404)

    return latitude, longitude


def get_crimes(latitude, longitude):
    point = get_point(latitude, longitude)
    filters = {}

    for filter, value in flask.request.args.items():
        if filter in ['callback', '_']:
            continue
        filters[filter] = value

    return _crimes.get_crimes_nearby(point, filters=filters)


@app.route('/crime/stats/<latitude>,<longitude>')
@jsonp
def crime_stats(latitude, longitude):
    nearby_crimes = get_crimes(latitude, longitude)
    stats = _crimes.get_stats_for_crimes(nearby_crimes)
    return flask.jsonify(result={'stats': stats})


@app.route('/crime/<latitude>,<longitude>')
@jsonp
def crimes(latitude, longitude):
    # Convert a dict with tuple-keys to a more JSON-friendly array of dicts.
    crimes = [dict(crime=c, point=','.join(str(p))) for p, c in
              get_crimes(latitude, longitude).items()]
    return flask.jsonify(result={'crimes': crimes})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
