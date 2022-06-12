from setuptools import find_packages, setup

setup(
    name='datawrappergraphics',
    packages=find_packages(include=["datawrappergraphics"]),
    version='0.3.27',
    url='https://github.com/dexmcmillan/datawrappergraphics',
    description='A package for interacting with Datawrapper maps, charts, and folders.',
    author='Dexter McMillan',
    license='MIT',
    install_requires=[
        "numpy",
        "pandas",
        "geopandas",
        "requests",
        "geojson"
        ],
    setup_requires=[
        'pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-runner',
        "geojson"],
    test_suite='tests',
)