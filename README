# About

This is a prototype web service that finds crime data near a lat/long pair. It
returns the number of crimes by category within 1/2 mile of the point, with a
max of 250 crimes.

The service references crime data from the City of Portland, stored in a
k-d tree using `scipy.spatial.cKDTree`.


# Installing

Instructions for OS X using Homebrew (my local setup):

- Install gfortran `brew install gfortran`
- Install numpy and scipy: `pip install numpy` and `pip install scipy`
    Note: Installing numpy and scipy from pip doesn't always work for me.
- Install GDAL -- this always fails for me with Pip, so I use Homebrew:
    `brew install GDAL`
- Install Python requirements: `pip install -r requirements.txt`


# Running

You can run the app server locally with the Foreman gem:

    `foreman run web`

Defaults for $PORT and $WORKERS live in `.env`. You can also set those values
as environment variables, which is where Heroku will read them from.


# Deploying

To deploy, install Heroku's toolchain and push to your app.


# License

MIT. See LICENSE file.
