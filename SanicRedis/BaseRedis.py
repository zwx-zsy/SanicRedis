#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
======================
@author: Vincent zhou
@contact: vincent321x@gmail.com
@decsription:
@time: 2018/6/5
"""
from aioredis import create_redis_pool
import datetime
import time as mod_time
from redis.exceptions import (
    ConnectionError,
    DataError,
    ExecAbortError,
    NoScriptError,
    PubSubError,
    RedisError,
    ResponseError,
    TimeoutError,
    WatchError,
)
_NOTSET = 'UTF-8'

try:
    from sanic.log import logger
except ImportError:
    from sanic.log import log as logger


__version__ = '0.1.2'


class BaseRedis:
    __coll__ = None  # KeyGroup name
    __dbkey__ = None  # which database connected to?
    __unique_fields__ = []
    __motor_redis_client__ = None
    __motor_redis_db__ = None
    __motor_redis_clients__ = {}
    __motor_redis_dbs__ = {}
    __app__ = None
    __apps__ = {}
    __timezone__ = None

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    async def Execute(cls, command, *args, **kwargs):
        kwargs['encoding'] = kwargs.pop('encoding', _NOTSET)
        return await cls.__motor_redis_client__.execute(command, *args, **kwargs)

    @staticmethod
    def init_app(app, open_listener='before_server_start',
                 close_listener='before_server_stop', name=None, uri=None):
        BaseRedis.__app__ = app
        BaseRedis.__apps__[name or app.name] = app

        if open_listener:
            @app.listener(open_listener)
            async def open_connection(app, loop):
                await BaseRedis.default_open_connection(app, loop, name, uri)

        if close_listener:
            @app.listener(close_listener)
            async def close_connection(app, loop):
                await BaseRedis.default_close_connection(app, loop)

    @staticmethod
    async def default_open_connection(app, loop, name=None, *args, **kwargs):
        if not name:
            name = app.name
        db = kwargs.pop('db', None)
        logger.info('opening motor connection for redis [{}]'.format(name))
        client = await create_redis_pool((app.config.redishost, app.config.redisport), db=db or app.config.redisdb,password=app.config.redispwd, loop=loop)
        app.motor_redis_client = client
        BaseRedis.__motor_redis_client__ = client
        BaseRedis.__motor_redis_db__ = db
        if not hasattr(app, 'motor_redis_clients'):
            app.motor_redis_clients = {}

        app.motor_redis_clients[name] = client
        BaseRedis.__motor_redis_clients__[name] = client
        BaseRedis.__motor_redis_dbs__[name] = db

    @staticmethod
    async def default_close_connection(app, loop):
        if hasattr(app, 'motor_clients'):
            for name, client in app.motor_redis_clients.items():
                logger.info('closing motor redis connection for [{}]'.format(name))
                client.close()
                await client.wait_closed()

    @classmethod
    async def set_keys(cls,dict_obj=None,*args,**kwargs):
        for key,item in dict_obj.items():
            await cls.set(key,item)
        return True

    def __delitem__(self, key):
        self.delete(key)

    @classmethod
    async def CustomPipeline(cls):
        return cls.__motor_redis_client__.pipeline()

    @classmethod
    async def delete(cls,*keys):
        keys = [cls.__coll__ + item for item in keys]
        return await cls.Execute('DEL', *keys)

    @classmethod
    async def exists(cls, name):
        "Returns a boolean indicating whether key ``name`` exists"
        key = cls.__coll__ + name
        return await cls.Execute('EXISTS', key)
    __contains__ = exists

    @classmethod
    async def expire(cls, name, time):
        """
        Set an expire flag on key ``name`` for ``time`` seconds. ``time``
        can be represented by an integer or a Python timedelta object.
        """
        name = cls.__coll__ + name
        if isinstance(time, datetime.timedelta):
            time = time.seconds + time.days * 24 * 3600
        return await cls.Execute('EXPIRE', name, time)

    @classmethod
    async def expireat(cls, name, when):
        """
        Set an expire flag on key ``name``. ``when`` can be represented
        as an integer indicating unix time or a Python datetime object.
        """
        name = cls.__coll__ + name
        if isinstance(when, datetime.datetime):
            when = int(mod_time.mktime(when.timetuple()))
        return await cls.Execute('EXPIREAT', name, when)

    @classmethod
    async def keys(cls, pattern='*'):
        "Returns a list of keys matching ``pattern``"
        return await cls.Execute('KEYS', *pattern,encoding='utf-8')

    # SERVER INFORMATION
    @classmethod
    async def bgrewriteaof(cls):
        "Tell the Redis server to rewrite the AOF file from data in memory."
        return cls.Execute('BGREWRITEAOF')

    @classmethod
    async def bgsave(cls):
        """
        Tell the Redis server to save its data to disk.  Unlike save(),
        this method is asynchronous and returns immediately.
        """
        return cls.Execute('BGSAVE')

    @classmethod
    async def client_kill(cls, address):
        "Disconnects the client at ``address`` (ip:port)"
        return cls.Execute('CLIENT KILL', address)

    @classmethod
    async def client_list(cls):
        "Returns a list of currently connected clients"
        return cls.Execute('CLIENT LIST')

    @classmethod
    async def client_getname(cls):
        "Returns the current connection name"
        return cls.Execute('CLIENT GETNAME')

    @classmethod
    async def client_setname(cls, name):
        "Sets the current connection name"
        return cls.Execute('CLIENT SETNAME', name)

    @classmethod
    async def config_get(cls, pattern="*"):
        "Return a dictionary of configuration based on the ``pattern``"
        return cls.Execute('CONFIG GET', *pattern,encoding='utf-8')

    @classmethod
    async def config_set(cls, name, value):
        "Set config item ``name`` with ``value``"
        return cls.Execute('CONFIG SET', name, value)

    @classmethod
    async def config_resetstat(self):
        "Reset runtime statistics"
        return self.Execute('CONFIG RESETSTAT')

    @classmethod
    async def config_rewrite(cls):
        "Rewrite config file with the minimal change to reflect running config"
        return await cls.Execute('CONFIG REWRITE')

    @classmethod
    async def dbsize(self):
        "Returns the number of keys in the current database"
        return self.Execute('DBSIZE')

    @classmethod
    async def debug_object(cls, key):
        "Returns version specific meta information about a given key"
        return await cls.Execute('DEBUG OBJECT', key)

    @classmethod
    async def echo(cls, value):
        "Echo the string back from the server"
        return await cls.Execute('ECHO', value)

    @classmethod
    async def flushall(cls):
        "Delete all keys in all databases on the current host"
        return await cls.Execute('FLUSHALL')


    @classmethod
    async def flushdb(cls):
        "Delete all keys in the current database"
        return await cls.Execute('FLUSHDB')

    @classmethod
    async def info(cls, section=None):
        """
        Returns a dictionary containing information about the Redis server

        The ``section`` option can be used to select a specific section
        of information

        The section option is not supported by older versions of Redis Server,
        and will generate ResponseError
        """
        if section is None:
            return await cls.Execute('INFO')
        else:
            return await cls.Execute('INFO', section)


    async def lastsave(self):
        """
        Return a Python datetime object representing the last time the
        Redis database was saved to disk
        """
        return await self.Execute('LASTSAVE')


    async def ping(self):
        "Ping the Redis server"
        return await self.Execute('PING')

    async def save(self):
        """
        Tell the Redis server to save its data to disk,
        blocking until the save is complete
        """
        return await self.Execute('SAVE')

    async def time(self):
        """
        Returns the server time as a 2-item tuple of ints:
        (seconds since epoch, microseconds into this second).
        """
        return await self.Execute('TIME')

    # BASIC KEY COMMANDS
    @classmethod
    async def append(cls, key, value):
        """
        Appends the string ``value`` to the value at ``key``. If ``key``
        doesn't already exist, create it with a value of ``value``.
        Returns the new length of the value at ``key``.
        """
        return await cls.Execute('APPEND', key, value)

    def bitcount(self, key, start=None, end=None):
        """
        Returns the count of set bits in the value of ``key``.  Optional
        ``start`` and ``end`` paramaters indicate which bytes to consider
        """
        params = [key]
        if start is not None and end is not None:
            params.append(start)
            params.append(end)
        elif (start is not None and end is None) or \
                (end is not None and start is None):
            raise RedisError("Both start and end must be specified")
        return self.Execute('BITCOUNT', *params)

    def bitop(self, operation, dest, *keys):
        """
        Perform a bitwise operation using ``operation`` between ``keys`` and
        store the result in ``dest``.
        """
        return self.Execute('BITOP', operation, dest, *keys)

    @classmethod
    async def bitpos(cls, key, bit, start=None, end=None):
        """
        Return the position of the first bit set to 1 or 0 in a string.
        ``start`` and ``end`` difines search range. The range is interpreted
        as a range of bytes and not a range of bits, so start=0 and end=2
        means to look at the first three bytes.
        """
        key = cls.__coll__ + key
        if bit not in (0, 1):
            raise RedisError('bit must be 0 or 1')
        params = [key, bit]

        start is not None and params.append(start)

        if start is not None and end is not None:
            params.append(end)
        elif start is None and end is not None:
            raise RedisError("start argument is not set, "
                             "when end is specified")

        return await cls.Execute('BITPOS', *params)

    @classmethod
    async def decr(cls, name, amount=1):
        """
        Decrements the value of ``key`` by ``amount``.  If no key exists,
        the value will be initialized as 0 - ``amount``
        """
        name = cls.__coll__ + name
        return await cls.Execute('DECRBY', name, amount)

    @classmethod
    async def dump(cls, name):
        """
        Return a serialized version of the value stored at the specified key.
        If key does not exist a nil bulk reply is returned.
        """
        name = cls.__coll__ + name
        return await cls.Execute('DUMP', name)


    @classmethod
    async def get(cls, name):
        """
        Return the value at key ``name``, or None if the key doesn't exist
        """
        name = cls.__coll__ + name
        return await cls.Execute('GET', name)

    def __getitem__(self, name):
        """
        Return the value at key ``name``, raises a KeyError if the key
        doesn't exist.
        """
        value = self.get(name)
        if value is not None:
            return value
        raise KeyError(name)

    @classmethod
    async def getbit(cls, name, offset):
        "Returns a boolean indicating the value of ``offset`` in ``name``"
        return await cls.Execute('GETBIT', name, offset)


    @classmethod
    async def getrange(cls, key, start, end):
        """
        Returns the substring of the string value stored at ``key``,
        determined by the offsets ``start`` and ``end`` (both are inclusive)
        """
        return await cls.Execute('GETRANGE', key, start, end)

    @classmethod
    async def getset(cls, name, value):
        """
        Sets the value at key ``name`` to ``value``
        and returns the old value at key ``name`` atomically.
        """
        return await cls.Execute('GETSET', name, value)

    @classmethod
    async def incr(cls, name, amount=1):
        """
        Increments the value of ``key`` by ``amount``.  If no key exists,
        the value will be initialized as ``amount``
        """
        return await cls.Execute('INCRBY', name, amount)
    @classmethod
    async def incrby(cls, name, amount=1):
        """
        Increments the value of ``key`` by ``amount``.  If no key exists,
        the value will be initialized as ``amount``
        """

        # An alias for ``incr()``, because it is already implemented
        # as INCRBY redis command.
        return await cls.incr(name, amount)


    @classmethod
    async def incrbyfloat(cls, name, amount=1.0):
        """
        Increments the value at key ``name`` by floating ``amount``.
        If no key exists, the value will be initialized as ``amount``
        """
        return await cls.Execute('INCRBYFLOAT', name, amount)

    @classmethod
    async def rename(cls, src, dst):
        """
        Rename key ``src`` to ``dst``
        """
        return await cls.Execute('RENAME', src, dst)

    @classmethod
    async def renamenx(cls, src, dst):
        "Rename key ``src`` to ``dst`` if ``dst`` doesn't already exist"
        return await cls.Execute('RENAMENX', src, dst)


    @classmethod
    async def restore(cls, name, ttl, value, replace=False):
        """
        Create a key using the provided serialized value, previously obtained
        using DUMP.
        """
        params = [name, ttl, value]
        if replace:
            params.append('REPLACE')
        return await cls.Execute('RESTORE', *params)

    @classmethod
    async def set(cls, name, value, ex=None, px=None, nx=False, xx=False):
        """
        Set the value at key ``name`` to ``value``

        ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds.

        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.

        ``nx`` if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist.

        ``xx`` if set to True, set the value at key ``name`` to ``value`` only
            if it already exists.
        """
        name = cls.__coll__ + name
        pieces = [name, value]
        if ex is not None:
            pieces.append('EX')
            if isinstance(ex, datetime.timedelta):
                ex = ex.seconds + ex.days * 24 * 3600
            pieces.append(ex)
        if px is not None:
            pieces.append('PX')
            if isinstance(px, datetime.timedelta):
                ms = int(px.microseconds / 1000)
                px = (px.seconds + px.days * 24 * 3600) * 1000 + ms
            pieces.append(px)

        if nx:
            pieces.append('NX')
        if xx:
            pieces.append('XX')

        return await cls.Execute('SET', *pieces,encoding='utf-8')

    def __setitem__(self, name, value):
        self.set(name, value)


    @classmethod
    async def setbit(cls, name, offset, value):
        """
        Flag the ``offset`` in ``name`` as ``value``. Returns a boolean
        indicating the previous value of ``offset``.
        """
        value = value and 1 or 0
        return await cls.Execute('SETBIT', name, offset, value)