"""Groups factories to be importable from one place."""
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

from pytest_dbfixtures.factories.redis import redis_proc, redisdb
from pytest_dbfixtures.factories.postgresql import postgresql_proc, postgresql
from pytest_dbfixtures.factories.mysql import mysql_proc
from pytest_dbfixtures.factories.mysqldb import mysqldb
from pytest_dbfixtures.factories.rabbitmq import rabbitmq, rabbitmq_proc
from pytest_dbfixtures.factories.mongo import mongodb, mongo_proc
from pytest_dbfixtures.factories.elasticsearch import (
    elasticsearch,
    elasticsearch_proc,
)


__all__ = [
    redis_proc, redisdb,
    postgresql, postgresql_proc,
    mysql_proc, mysqldb,
    rabbitmq, rabbitmq_proc,
    mongodb, mongo_proc,
    elasticsearch_proc, elasticsearch
]
