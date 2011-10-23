import os

from fabric.api import run
from fabric.api import settings as fab_settings

from deploymachine.conf import settings


def redis_flushdb(db):
    run("redis-cli -n {0} FLUSHDB".format(db))


def redis_keys_all(db):
    run("redis-cli -n {0} KEYS '*'".format(db))


def redis_keys_search(db, match):
    run("redis-cli -n {0} KEYS '{1}'".format(db, match))
