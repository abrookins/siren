from setuptools import setup, find_packages

setup(
    name='siren',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/abrookins/siren',
    license='MIT',
    author='Andrew Brookins',
    author_email='a.m.brookins@gmail.com',
    description='A web application that searches for crimes in Portland, Oregon near a given coordinate pair',
    requires=['numpy', 'scipy']
)
