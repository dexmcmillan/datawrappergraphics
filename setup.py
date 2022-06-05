from setuptools import find_packages, setup

setup(
    name='datawrappergraphics',
    packages=find_packages(include=["datawrappergraphics"]),
    include_package_data = True,
    package_data={'datawrappergraphics': ['assets/*.json']},
    version='0.2.38',
    description='A pythonic representation of Datawrapper graphics.',
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