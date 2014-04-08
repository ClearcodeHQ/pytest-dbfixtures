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
with open(os.path.join(here, 'pytest_dbfixtures', '__init__.py')) as v_file:
    package_version = re.compile(
        r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


setup(
    name='pytest-dbfixtures',
    version=package_version,
    description='Databases fixtures plugin for py.test.',
    author='Clearcode - The A Room',
    author_email='thearoom@clearcode.cc',
    url='https://github.com/clearcode/pytest-dbfixtures',
    packages=find_packages(),
    install_requires=[
        'pytest>=2.3.4',
        'summon_process>=0.1.3',
        'pyaml>=3.10',
        'pymlconf>=0.2.10a',
        'path.py>=4.2',
    ],
    include_package_data=True,
    extras_require={
        'documentation': [
            "Sphinx",
        ]
    },
    entry_points={
        'pytest11': [
            'pytest_dbfixtures = pytest_dbfixtures.plugin'
        ]},
    keywords='py.test pytest fixture redis mongo rabbitmq mysql postgresql',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7']
)
