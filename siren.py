import flask
import os

from flask.ext.cache import Cache

from crime_tracker import PortlandCrimeTracker
from decorators import jsonp

app = flask.Flask(__name__)
app.config.from_object('default_settings')
app.config.from_envvar('SIREN_SETTINGS')
cache = Cache(app)


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
    ignore = ['callback', '_']

    for filter_name, value in flask.request.args.items():
        if filter_name in ignore:
            continue
        filters[filter_name] = value

    valid_filters, errors = _crimes.validate_filters(filters)

    return _crimes.get_crimes_nearby(point, filters=valid_filters), errors


@app.route('/crime/stats/<latitude>,<longitude>')
@cache.cached()
@jsonp
def crime_stats(latitude, longitude):
    nearby_crimes, errors = get_crimes(latitude, longitude)
    stats = _crimes.get_stats_for_crimes(nearby_crimes)
    data = {'stats': stats}

    if errors:
        data['errors'] = errors

    return flask.jsonify(result=data)


@app.route('/crime/<latitude>,<longitude>')
@cache.cached()
@jsonp
def crimes(latitude, longitude):
    crimes, errors = get_crimes(latitude, longitude)

    # JSON requires that object keys be strings, so convert tuples to strings.
    crimes = [dict(crime=c, point=','.join(str(p))) for p, c in crimes.items()]
    data = {'crimes': crimes}

    if errors:
        data['errors'] = errors

    return flask.jsonify(result=data)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
