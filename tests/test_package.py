"""Test if package can be properly build."""
from pytest_dbfixtures.plugin import pytest_load_initial_conftests


def test_config_files(request):
    """Check if package is properly configured to build."""
    pytest_load_initial_conftests(request.config, None, None)
