from setuptools import find_packages, setup

setup(
    name='datawrappergraphics',
    packages=find_packages(include=['datawrappergraphics']),
    version='0.2.11',
    description='A pythonic representation of Datawrapper graphics.',
    author='Dexter McMillan',
    license='MIT',
    install_requires=[
        'pandas',
        'requests',
        'datawrapper',
        'geopandas',
        ],
    setup_requires=[
        'pytest-runner'],
    tests_require=[
        'pytest==4.4.1',
        'pandas',
        'requests',
        'datawrapper',
        'geopandas',
        'pytest-runner'],
    test_suite='tests',
)