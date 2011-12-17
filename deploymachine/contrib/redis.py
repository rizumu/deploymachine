import os

from fabric.api import run
from fabric.api import settings as fab_settings
from fabric.decorators import task

import deploymachine_settings as settings


@task
def redis_flushdb(db):
    run("redis-cli -n {0} FLUSHDB".format(db))


@task
def redis_keys_all(db):
    run("redis-cli -n {0} KEYS '*'".format(db))


@task
def redis_keys_search(db, match):
    run("redis-cli -n {0} KEYS '{1}'".format(db, match))
