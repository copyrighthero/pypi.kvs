# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

try:
  from dbm import gnu as dbm
except ImportError:
  from dbm import dumb as dbm


# import directive
__all__ = (
  '__author__', '__license__', '__version__', 'KVS'
)
# package metadata
__author__ = 'Hansheng Zhao'
__license__ = 'BSD-2-Clause + MIT'
__version__ = '1.0.0'


class KVS(object):
  """ KVS class for K-V pair storage """

  # statically defined attributes
  __slots__ = ('_database', '_serialize')

  def __init__(
    self, database = ':memory:',
    serialize = None, **kwargs
  ):
    """
    KVStore class constructor
    :param database: object, database path or instance
    :param serialize: object|None, the serializer
    :param kwargs: other arguments
    """
    # import
    from seco import SeCo
    # check if using on-disk|in-memory|external store
    if isinstance(database, (str, bytes, bytearray)):
      # convert bytes and byte-array into string
      database = database.decode(encoding = 'UTF8') \
        if isinstance(database, (bytes, bytearray)) \
        else database
      # check if using in-memory storage
      if database.lower() == ':memory:':
        self._database = {}
      else:
        flag = kwargs['flag'] \
          if 'flag' in kwargs else 'c'
        self._database = \
          dbm.open(database, flag, **kwargs)
    # any object is now considered database
    elif isinstance(database, dict) or True:
      # using external storage
      self._database = database
    # initialize serializer
    if serialize is not None:
      self._serialize = serialize
    else:
      self._serialize = SeCo(
        serialize = 'json', compress = 'zlib'
      )

  def __call__(self, key, value = None, *args, **kwargs):
    """
    Call method for setting & getting item
    :param key: mixed, any hashable key
    :param value: mixed|None, any object
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None|mixed
    """
    if value is None:
      # read from kvstore if value not provided
      return self.__getitem__(key, *args, **kwargs)
    else:
      # set item into kvstore instead
      self.__setitem__(key, value, *args, **kwargs)

  def __del__(self):
    """
    Sync and close database connection if not in-memory
    :return: None
    """
    self.sync()
    self.close()

  @staticmethod
  def _convert(key):
    """
    Convert key to supported format
    :param key: mixed, any hashable object
    :return: bytes, bytes representation of key
    """
    # check if key is supported or hashable
    # supports only bytes by default
    if isinstance(key, bytes):
      return key
    # encode string type
    elif isinstance(key, str):
      return key.encode(encoding = 'UTF8')
    # change byte-array into bytes
    elif isinstance(key, bytearray):
      return bytes(key)
    # convert numeric into string
    elif isinstance(key, (int, float, complex)):
      return str(key).encode(encoding = 'UTF8')
    # convert hashable collections into string
    elif isinstance(key, (range, tuple, frozenset)):
      return str(key).encode(encoding = 'UTF8')
    # other types not supported
    else:
      raise TypeError('Unsupported type.')

  def __contains__(self, key):
    """
    Dict-like object contains method
    :param key: mixed, any hashable key
    :return: bool, whether item exists
    """
    database = self._database
    key = self._convert(key)
    return key in  database \
      if hasattr(database, '__contains__') \
      else self.__getitem__(key) is not None

  def __setitem__(self, key, value, *args, **kwargs):
    """
    Dict-like object setitem method
    :param key: mixed, any hashable key
    :param value: mixed, any object
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    # acquire database and lint key
    database = self._database
    key = self._convert(key)
    # check if value is not None
    if value is not None:
      # serialize and compress the value
      value = self._serialize.dumps(value)
      # set item into database
      database.set(key, value, *args, **kwargs) \
        if hasattr(database, 'set') \
        else database.__setitem__(key, value)
    else:
      # delete item from database instead
      self.__delitem__(key, *args, **kwargs)

  # aliases for setitem method
  set = put = __setitem__

  def __getitem__(self, key, *args, **kwargs):
    """
    Dict-like object getitem method
    :param key: mixed, any hashable key
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed
    """
    # acquire database and lint key
    database = self._database
    key = self._convert(key)
    # acquire item from database
    value = database.get(key, *args, **kwargs) \
      if hasattr(database, 'get') \
      else database.__getitem__(key)
    return self._serialize.loads(value) \
      if value else None

  # aliases for getitem method
  get = __getitem__

  def __delitem__(self, key, *args, **kwargs):
    """
    Dict-like object delitem method
    :param key: mixed, any hashable key
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    # acquire database and lint key
    database = self._database
    key = self._convert(key)
    # attempt to remove item from database
    try:
      return database.delete(
        key, *args, **kwargs
      ) if hasattr(database, 'delete') \
        else database.__delitem__(key)
    except KeyError:
      return None

  # aliases for delitem method
  delete = __delitem__

  def __setattr__(self, key, value):
    """
    Proxy for saving item to database
    :param key: str, the kv-pair key
    :param value: mixed, the value
    :return: None
    """
    try:
      # attempts to modify the object first
      super(KVS, self).__setattr__(key, value)
    except AttributeError:
      # set item into database instead
      self.__setitem__(key, value)

  def __getattr__(self, key):
    """
    Proxy for getting item from database
    :param key: str, the attribute name
    :return: mixed, function or value
    """
    try:
      # attempt to acquire attributes first
      return self._database.__getattribute__(key)
    except AttributeError:
      # return database item instead
      return self.__getitem__(key)

  def __delattr__(self, key):
    """
    Proxy for deleting item from database
    :param key: str, the kv-pair key
    :return: None
    """
    try:
      # attempt to delete attribute first
      super(KVS, self).__delattr__(key)
    except AttributeError:
      # delete from database
      self.__delitem__(key)

  def pop(self, key):
    """
    Pop a value from the kv-store
    :param key: mixed, any hashable key
    :return: mixed
    """
    value = self.__getitem__(key)
    self.__delitem__(key)
    return value

  def keys(self):
    """
    Acquire all the keys in database
    :return: collection|generator, keys
    """
    yield from self._database.keys() \
      if hasattr(self._database, 'keys') \
      else ()

  def values(self):
    """
    Acquire all the values in database
    :return: collection|generator, values
    """
    # check if method already exists
    if hasattr(self._database, 'values'):
      yield from map(
        lambda _: self._serialize.loads(_),
        self._database.values()
      )
    else:
      # create generator for values
      for key in self.keys():
        yield self.__getitem__(key)

  def items(self):
    """
    Acquire k-v pairs in database
    :return: collection| generator, tuples
    """
    # check if method already exists
    if hasattr(self._database, 'items'):
      yield from map(lambda _: (
        _[0], self._serialize.loads(_[1])
      ), self._database.items())
    else:
      # create generator for items
      for key in self.keys():
        yield (key, self.__getitem__(key))

  def sync(self):
    """
    Commit changes to disk
    :return: None
    """
    # check if is in-memory mode
    if hasattr(self._database, 'sync'):
      self._database.sync()

  def optimize(self):
    """
    Optimize GDBM database
    :return: None
    """
    if hasattr(self._database, 'reorganize'):
      self._database.reorganize()

  def close(self):
    """
    Close database connection
    :return: None
    """
    self.sync()
    if hasattr(self._database, 'close'):
      self._database.close()

  def clear(self):
    """
    Clear database content
    :return: None
    """
    if hasattr(self._database, 'clear'):
      self._database.clear()
    elif hasattr(self._database, 'flushall'):
      self._database.flushall()
    elif hasattr(self._database, 'flush_all'):
      self._database.flush_all()
    else:
      for key in self.keys():
        self.__delitem__(key)
      self.optimize()
