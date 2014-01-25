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
    Trying to import module, if occurred error, then raise :class:`ImportError`.
    If not, imported module and :class:`pymlconf.ConfigManager` will be returned.

    :param str module: name of the module
    :param FixtureRequest request: fixture request object
    :param str pypi_package: name of the package on `<https://pypi.python.org/pypi>`_
    :rtype: tuple
    :returns: tuple with ``module`` and :class:`pymlconf.ConfigManager`
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
