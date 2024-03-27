#!/usr/bin/env python3
"""
create a Cache class that will implement a simple cache using Redis
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Method that returns a count of times the class Cache
    was called """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper for counting calls"""
        self._redis.incr(method.__qualname__, 1)
        result = method(self, *args, **kwargs)
        return result
    return wrapper


def call_history(method: Callable) -> Callable:
    """stores record of method calls"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper for recording calls"""
        self._redis.rpush(method.__qualname__ + ":all_inputs", str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(method.__qualname__ + ":outputs", str(result))
        return result
    return wrapper


class Cache:
    """
    a class that stores redis instance as a private variable
    """

    def __init__(self):
        """
        constructor for Cache class
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        store the input data in redis using a random key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[callable] = None) -> Union[str, bytes,
                                                    int, float]:
        """
        method that take a key string argument and an
        optional Callable argument named fn. This callable will be used
        to convert the data back to the desired format
        """
        if not self._redis.exists(key):
            return None
        if fn is None:
            return self._redis.get(key)
        else:
            return fn(self._redis.get(key))

    def get_str(self, key: str) -> str:
        """
        Method that converts the data back into a string
        """
        if not self._redis.exists(key):
            return None
        return str(self._redis.get(key))

    def get_int(self, key):
        """Method used to convert data back into an int"""
        if not self._redis.exists(key):
            return None
        return int.from_bytes(self._redis.get(key), "big")


def replay(store):
    """
    displays the history of calls of a particular function
    """
    r = redis.Redis()
    call_count = r.get(store.__qualname__).decode("utf-8")
    inputs = r.lrange("{}:inputs".format(store.__qualname__), 0, -1)
    outputs = r.lrange("{}:outputs".format(store.__qualname__), 0, -1)

    print(f"Cache.store was called {call_count} times:")
    for value, key in zip(inputs, outputs):
        print(f"Cache.store(*{value.decode('utf-8')}) -> \
{key.decode('utf-8')}")
