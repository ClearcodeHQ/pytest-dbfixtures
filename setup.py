# Copyright (C) 2013 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-dbfixtures.

# pytest-dbfixtures is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-dbfixtures is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-dbfixtures.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
from setuptools import setup, find_packages


here = os.path.dirname(__file__)
with open(
        os.path.join(here, 'src', 'pytest_dbfixtures', '__init__.py')
) as v_file:
    package_version = re.compile(
        r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


def read(fname):
    """
    Read file's content.

    :param str fname: name of file to read

    :returns: file content
    :rtype: str
    """
    return open(os.path.join(here, fname)).read()


setup(
    name='pytest-dbfixtures',
    version=package_version,
    description='Databases fixtures plugin for py.test.',
    long_description=(
        read('README.rst') + '\n\n' + read('CHANGES.rst')
    ),
    author='Clearcode - The A Room',
    author_email='thearoom@clearcode.cc',
    url='https://github.com/ClearcodeHQ/pytest-dbfixtures',
    install_requires=[
        'pytest>=2.3.4',
        'mirakuru>=0.2',  # test executors helpers
        'pyyaml>=3.10',
        'pymlconf>=0.2.10a,!=0.3.12,!=0.3.13,!=0.3.14,!=0.5.0',
        'path.py>=4.2',
        'port-for>=0.3.1',  # needed for random port selection
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    extras_require={
        'documentation': ['Sphinx', ],
        'tests': [
            'pytest-cov==2.4.0',
            'pytest-xdist==1.15.0',
            'Mock==2.0.0',
        ],
        'mysql': ['mysqlclient'],
        'postgresql': ['pytest-postgresql'],
        'mongodb': ['pytest-mongo'],
        'elasticsearch': ['pytest-elasticsearch'],
        'redis': ['redis'],
        'rabbitmq': ['rabbitpy'],
        'deploy': ['bumpversion'],
        'dynamodb': ['boto3'],
    },
    entry_points={
        'pytest11': [
            'pytest_dbfixtures = pytest_dbfixtures.plugin'
        ]},
    keywords='tests py.test pytest fixture redis mongo mongodb'
             ' rabbit rabbitmq mysql postgres postgresql'
             ' elasticsearch',
    license='LGPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'License :: OSI Approved :: '
        'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
