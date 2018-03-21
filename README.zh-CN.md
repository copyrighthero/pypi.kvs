# KVS Project #

[README English](README.md)

## About the KVS Library ##

过几天再翻译...不好意思哦...

KVS library is created to easily handle most key-value stores. It supports `redis`, `memcached`, `leveldb` (`plyvel`), Python `dict`, or any other instances with any combinations of (`set`, `put`, `__setitem__`) methods for saving data, (`get`, `__getitem`) methods for getting data and (`delete`, `__delitem__`) methods for deleting data.

The constructor also takes in `str` as parameter. If one is provided as `':memory:'`, it will simply use a `dict` instance to store information; if strings other than `':memory:'` is provided, it will treat it as a path and use `anydbm` or `dbm` module to open either a `gdbm`, `ndbm` or `dumb` database for storage.

The module utilizes [SeCo](https://www.github.com/copyrighthero/SeCo) module for data serialization and compression when setting item into database. Since the result parsed by `SeCo` are `bytes` objects, it plays well with third party databases like `redis`, `memcached` and `plyvel`. You can change the default serializer when instantiating, making this library very flexible.

One might want to use this library to easily interface other databases, to create a in-memory cache, a on-disk cache, etc.

## How to Use KVS Library ##

After installing using `pip install KVS`, one can simply import kvs and start working.

```python
from kvs import KVS
from redis import Redis
from pymemcache.client import Client as Memcached
import plyvel, shelve, pickle, msgpack

# create databases
dict_db = {} # yes, simple Python `dict`
redis = Redis()
memcached = Memcached()
leveldb = plyvel('/tmp/testdb', create_if_missing = True)
shelf = shelve('/tmp/shelvedb')

# instantiate KVS using any one of the following
kvs = KVS() # default, using python `dict`
kvs = KVS(':memory:') # the same as above
kvs = KVS(dict_db) # using the created dict object
kvs = KVS(redis, pickle) # using redis, and serialize with pickle
kvs = KVS(memcached, serialize = pickle) # using memcached, serialize with pickle
kvs = KVS(leveldb, msgpack) # use plyvel and msgpack
kvs = KVS(shelf, msgpack) # use shelf and msgpack
# ...

# use the kvs!
#   use .set or .put to set item
kvs.set('test', 'case') # set an item
kvs.get('test') # 'case'
kvs.put('test', 'testcase') # set an item
#   use .get, [key]  or .<property> to get
kvs.get('test') # 'testcase'
kvs['test'] # 'testcase'
kvs.test # 'testcase`

# faster operation with __call__ method
kvs('test', 'call method') # set item
kvs('test') # 'call method'

# if key does not exist it returns None
kvs.get('non_exist') # None
kvs['non_exist'] # None
kvs.non_exist # None
kvs('non_exist') # None

# delete with any of the following
kvs.delete('test')
del kvs['test']
del kvs.test

# check if key exists
'test' in kvs # False
kvs('test', 'case')
'test' in kvs # True

# get all keys if possible
list(kvs.keys()) # ['test']
# get all values if possible
list(kvs.values()) # ['case']
# get all items if possible
list(kvs.items()) # [('test', 'case')]

# other operations
kvs.pop('test') # 'case'
kvs.pop('test') # None
kvs.clear() # clears all items stored in the database
kvs.sync() # only for `dbm`, otherwise noop
kvs.optimize() # only for `gdbm`, otherwise noop
kvs.close() # only for databases with `close` method

# all database attributes are still available,
#   so be careful when using properties to get/set items
```

## KVS Class API References ##

`KVS` is the only class exposed in this module, it is the manager and wrapper around actual databases. It takes two parameters, the first being `str` or database instance, the second being the serializer. The class is defaulted to use Python `dict` as database and `SeCo` as the serializer.

Signature: `KVS(database = ':memory:', serialize = None, **kwargs)`

### KVS Class ###

1. `database` parameter: if passed in as string ':memory:' it will use python `dict` as storage; if passed in as any other string, it will use `anydbm` or `dbm` to open the database; if passed in any other instances, it will use the instance as the database store.

2. `serialize` parameter: if nothing is passed in, the class will use `SeCo` library for data serialization and compression. If any other instance passed in, eg.: `pickle`, `msgpack` etc, it will use it as the serializer. Remember that most databases like `redis`, `memcached` or `leveldb|plyvel` stores only `bytes` objects, keep it in mind when choosing serializers. 

`__contains__`: implements the `in` operator.
`__setitem__`, `set`, `put` method: for setting items.
`__getitem__`, `get` method: for getting items.
`__call__`: get or set item depends on how many parameters passed in
`__delete__`, `delete` method: for deleting items.
`__setattr__`: almost the alias for `__setitem__`, like `set` or `put` method.
`__getattr__`: for getting attributes from database instance, if not found, attempts `__getitem__` on `self`.
`__delattr__`: almost the alias for `__delitem__`, like `delete` method.
`pop(key)`: pop an item from storage
`keys()`: keys iterator if possible. eg. not possible with `memcached`.
`values()`: values iterator if possible. Same reason.
`items()`: items iterator if possible. Same reason.
`sync()`: only available to databases with `sync` method, like `dbm` etc, otherwise noop.
`close()`: only avalable to databases with `close` method, like `plyvel` etc, otherwise noop.
`clear()`: will invoke database's `clear` or `flush_all`, `flushall` methods to clear the content.

Please refer to the usage for how to use them :-)

## Licenses ##

This project is licensed under two permissive licenses, please chose one or both of the licenses to your like. Although not necessary, bug reports or feature improvements, attributes to the author(s), information on how this program is used are welcome and appreciated :-) Happy coding 

[BSD-2-Clause License]

Copyright 2018 Hansheng Zhao

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[MIT License]

Copyright 2018 Hansheng Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
