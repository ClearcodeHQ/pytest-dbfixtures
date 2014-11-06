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

from mirakuru import Executor


DEFAULT_TIMEOUT = 60  # in seconds


class StartTimeoutExecutor(Executor):

    def __init__(self, *args, **kwargs):
        """
        Overrides original initializator's `timeout` parameter:
        :param int timeout: number of seconds to wait for process to start
                            (default: 60)
        """
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = DEFAULT_TIMEOUT
        super(StartTimeoutExecutor, self).__init__(*args, **kwargs)
