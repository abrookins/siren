import flask
import os

from util import PortlandCrimeTracker
from decorators import jsonp

app = flask.Flask(__name__)
app.config.from_object('default_settings')
app.config.from_envvar('SIREN_SETTINGS')


# Serve static files if in debug mode.
if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'public')
    })


_crimes = PortlandCrimeTracker()


@app.route('/crime/stats')
@jsonp
def crime_stats():
    point = flask.request.args.get('point', '').split(',')
    nearby_crimes = _crimes.get_crimes_nearby(point)
    stats = _crimes.get_stats_for_crimes(nearby_crimes)
    return flask.jsonify(result={'stats': stats})


@app.route('/crime/nearby')
@jsonp
def crimes():
    point = flask.request.args.get('point', '').split(',')
    nearby_crimes = _crimes.get_crimes_nearby(point)
    return flask.jsonify(result={'nearby': nearby_crimes})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
