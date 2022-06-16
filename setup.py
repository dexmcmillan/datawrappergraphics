from setuptools import find_packages, setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.rst").read_text()

setup(
    name='datawrappergraphics',
    packages=find_packages(include=["datawrappergraphics"]),
    version='0.3.33',
    url='https://github.com/dexmcmillan/datawrappergraphics',
    description='A package for interacting with Datawrapper maps, charts, and folders.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dexter McMillan',
    license='MIT',
    install_requires=[
        "numpy",
        "pandas",
        "geopandas",
        "requests",
        "geojson",
        "IPython"
        ],
    setup_requires=[
        'pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-runner',
        "geojson",],
    test_suite='tests',
)