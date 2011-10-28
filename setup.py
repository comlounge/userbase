from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='usermanager',
      version=version,
      description="Participate User Manager",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='COM.lounge',
      author_email='info@comlounge.net',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "pyyaml",
        "pymongo",
        "argparse",
        "starflyer",
        "markdown",
        "pytest",
        "colander",
        "wtforms",
      ],
      entry_points="""
        [console_scripts]
        run = starflyer.scripts:run
        [starflyer_app_factory]
        default = usermanager.main:app_factory
        [starflyer_setup]
        default = usermanager.setup:setup
      """,
      )
