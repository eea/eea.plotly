# pylint: disable=consider-using-with
""" eea.plotly Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

NAME = 'eea.plotly'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

setup(
    name=NAME,
    version=VERSION,
    description="volto-plotlycharts backend support",
    long_description_content_type="text/x-rst",
    long_description=(
        open("README.rst").read() + "\n" +
        open(os.path.join("docs", "HISTORY.txt")).read()
    ),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='EEA Add-ons Plone Zope',
    author='European Environment Agency: IDM2 A-Team',
    author_email='eea-edw-a-team-alerts@googlegroups.com',
    url='https://github.com/eea/eea.plotly',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['eea'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        "plone.volto",
        # -*- Extra requirements: -*-
        "collective.folderishtypes",
        'plotly==5.24.1',
        'kaleido==0.2.1',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
