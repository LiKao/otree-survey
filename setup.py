import os
from setuptools import setup
 
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
 
# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
 
setup(
    name = 'otree-survey',
    version = '0.1',
    packages = ['survey'],
    include_package_data = True,
    license = 'GPLv3',
    description = 'A simple oTree survey app.',
    long_description = README,
    url = 'http://www.example.com/',
    author = 'Tillmann Nett',
    author_email = 'tillmann.nett@fernuni-hagen.de',
    classifiers =[
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4'
    ]
)