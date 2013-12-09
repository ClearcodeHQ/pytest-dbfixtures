from pymlconf import ConfigManager

__all__ = ['get_config']


def get_config(request):
    config_name = request.config.getvalue('db_conf')
    return ConfigManager(files=[config_name])
