from setuptools import find_packages, setup

setup(
    name='datawrappergraphics',
    packages=find_packages(include=["datawrappergraphics"]),
    include_package_data = True,
    package_data={'datawrappergraphics': ['assets/*.json']},
    version='0.2.35',
    description='A pythonic representation of Datawrapper graphics.',
    author='Dexter McMillan',
    license='MIT',
    install_requires=[
        "wheel",
        "pipwin",
        "numpy",
        "pandas",
        "shapely",
        "gdal",
        "fiona",
        "pyproj",
        "six",
        "rtree",
        "geopandas",
        "requests",
        ],
    setup_requires=[
        'pytest-runner'],
    tests_require=[
        'pytest',
        'pytest-runner'],
    test_suite='tests',
)