import pytest

from api import Zabbix5


@pytest.fixture(scope='module')
def zabbix5():
    return Zabbix5('http://127.0.0.1', 'Admin', 'zabbix')


@pytest.fixture(scope='session')
def admin_id():
    return '1'


@pytest.fixture(scope='session')
def group_id():
    return '7'
