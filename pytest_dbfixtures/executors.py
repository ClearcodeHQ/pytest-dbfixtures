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

'''
Overrides summon_process executors to defaultly use wait=True parameter
which turns on waiting on process beeing actually closed and set default
timeout for process to start.
'''

from summon_process.executors import (
    SimpleExecutor,
    TCPCoordinatedExecutor,
    HTTPCoordinatedExecutor,
)


DEFAULT_TIMEOUT = 100


class BaseExecutor(SimpleExecutor):

    '''
        Set timeout=DEFAULT_TIMEOUT on __init__ and wait=True on stop()
        on executors inheriting from this class.
    '''

    def __init__(self, *args, **kwargs):
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = DEFAULT_TIMEOUT
        super(BaseExecutor, self).__init__(*args, **kwargs)

    def stop(self, *args, **kwargs):
        if 'wait' not in kwargs:
            kwargs['wait'] = True
        super(BaseExecutor, self).stop(*args, **kwargs)


class TCPExecutor(BaseExecutor, TCPCoordinatedExecutor):
    pass


class HTTPExecutor(BaseExecutor, HTTPCoordinatedExecutor):
    pass
