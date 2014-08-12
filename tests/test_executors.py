from pytest_dbfixtures.executors.extensions import GentleKillingExecutor


def test_kill_executor():
    """
    We should be able to kill process.
    """
    executor = GentleKillingExecutor('sleep 300')
    executor.start()
    assert executor.running() is True
    executor.kill()
