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

import time

from summon_process.executors import SimpleExecutor


DEFAULT_TIMEOUT = 60  # in seconds


class StartTimeoutExecutor(SimpleExecutor):

    def __init__(self, *args, **kwargs):
        '''
        Overrides original initializator's `timeout` parameter:
        :param int timeout: number of seconds to wait for process to start
                            (default: 60)
        '''
        if kwargs.get('timeout') is None:
            kwargs['timeout'] = DEFAULT_TIMEOUT
        super(StartTimeoutExecutor, self).__init__(*args, **kwargs)


class StopWaitingExecutor(SimpleExecutor):

    def stop(self, *args, **kwargs):
        '''
        Overrides original stop()'s method `wait` parameter.
        :param int timeout: if True current process waits for subprocess
                            actually exit  (default: True)
        '''
        if 'wait' not in kwargs:
            kwargs['wait'] = True
        super(StopWaitingExecutor, self).stop(*args, **kwargs)


class GentleKillingExecutor(SimpleExecutor):

    def kill(self, wait_for_exit=True, wait_for_kill=10):
        """
        Overrides SimpleExecutor's `kill()` behaviour with a try of more
        gentle terminating subprocess before killing it. Also now we wait
        for subprocess to exit by default.

        :param bool wait_for_exit: set to `True` to wait (OS call)
                              for the process to end. (default: True)
        :param int wait_for_kill: seconds to wait after terminate call
                                  failed and before we actually kill()
                                  a subprocess. (default: 10)
        """
        if not self.running():
            return

        self._process.terminate()

        exited = False
        for x in xrange(wait_for_kill):
            if self._process.poll() is None:
                time.sleep(1)
                continue
            exited = True
            break

        if not exited:
            super(GentleKillingExecutor, self).kill(wait_for_exit)
            return

        self._process = None
        self._endtime = None


class ExtendedExecutor(StartTimeoutExecutor, StopWaitingExecutor,
                       GentleKillingExecutor):
    pass
