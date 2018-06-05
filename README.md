SanicRedis
==============
Redis support for sanic.

Built on top of [aioredis](https://github.com/aio-libs/aioredis).

Installation
------------

You can install this package as usual with pip:

    pip install SanicRedis

Example

```python
from sanic import Sanic
from sanic.response import json
from SanicRedis import BaseRedis

app = Sanic(__name__)
redisdb = dict(redisdb=8, redishost='localhost', redisport=6379, redispwd='password')

app.config.update(redisdb)
BaseRedis.init_app(app)


# group key of redis
class GroupKey(BaseRedis):
    __coll__ = 'GroupKey_'  # GroupKey + key


@app.route('/test1')
async def test1(request):
    await GroupKey.set('testkey', 'value') # key is GroupKey_testkey
    result = await GroupKey.get('testkey')  # get value of GroupKey_testkey
    return json(result)


if __name__ == '__main__':
    app.run(debug=True)
```

Resources
---------

- [PyPI](https://pypi.org/project/SanicRedis)
