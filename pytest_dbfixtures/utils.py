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
