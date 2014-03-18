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

import importlib

from pymlconf import ConfigManager


def get_config(request):
    """
    Get config from ``db_conf`` param.

    :param FixtureRequest request: fixture request object
    :rtype: pymlconf.ConfigManager
    :returns: :class:`pymlconf.ConfigManager`
    """
    config_name = request.config.getvalue('db_conf')
    return ConfigManager(files=[config_name])


def try_import(module, request, pypi_package=None):
    """
    Try to import module.

    :param str module: name of the module
    :param FixtureRequest request: fixture request object
    :param str pypi_package: name of the package on
        `pypi <https://pypi.python.org/pypi>`_
    :returns: tuple with ``module`` and :class:`pymlconf.ConfigManager`
    :rtype: tuple

    :raises: ImportError

    """
    try:
        i = importlib.import_module(module)
    except ImportError:
        raise ImportError(
            'Please install {0} package.\n'
            'pip install -U {0}'.format(
                pypi_package or module
            )
        )
    else:

        return i, get_config(request)
