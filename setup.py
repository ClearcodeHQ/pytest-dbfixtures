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

from setuptools import setup

setup(
    name='pytest-dbfixtures',
    version='0.3.6.5',
    description='dbfixtures plugin for py.test.',
    author='Clearcode - The A Room',
    author_email='thearoom@clearcode.cc',
    url='https://github.com/clearcode/pytest-dbfixtures',
    packages=['pytest_dbfixtures'],
    install_requires=[
        'pytest',
        'summon_process>=0.1.2',
        'pyaml',
        'pymlconf',
        'path.py>=4.3',
    ],
    include_package_data=True,
    entry_points={
        'pytest11': [
            'pytest_dbfixtures = pytest_dbfixtures.pytest_dbfixtures'
        ]},
    keywords='py.test pytest fixture redis mongo rabbitmq',
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
