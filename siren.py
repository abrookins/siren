import flask
import os

from flask.ext.cache import Cache

from crime_tracker import PortlandCrimeTracker, make_hour_filter
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


@app.route('/crimes/near/<latitude>,<longitude>/stats')
@jsonp
def crime_stats(latitude, longitude):
    point = get_point(latitude, longitude)
    nearby_crimes = _crimes.get_crimes_nearby(point)
    stats = _crimes.get_stats_for_crimes(nearby_crimes)
    return flask.jsonify(result={'stats': stats})


@app.route('/crimes/near/<latitude>,<longitude>/filter/hour/<int:hour>/stats')
@jsonp
def crime_stats_near_time(latitude, longitude, hour):
    """
    Get stats for crimes near a given point, around the time of a given hour.

    TODO: Consider a better approach, perhaps parsing dates from crime data into
    `datetime.datetime`.
    """
    point = get_point(latitude, longitude)
    time_filter = make_hour_filter(hour)
    nearby_crimes = _crimes.get_crimes_nearby(point, filters=[time_filter])
    stats = _crimes.get_stats_for_crimes(nearby_crimes)
    return flask.jsonify(result={'stats': stats})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
