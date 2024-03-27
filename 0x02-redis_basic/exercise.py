#!/usr/bin/env python3
"""writing string to redis"""

import redis

from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """counts how many times methods of the Cache class are called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """stores the history of inputs and outputs for a particular
    function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)

        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)

        return output
    return wrapper


def replay(method: Callable):
    """displays the history of calls of a particular function"""
    r = redis.Redis()
    method_name = method.__qualname__
    count = r.get(method_name).decode('utf-8')
    inputs = r.lrange(method_name + ":inputs", 0, -1)
    outputs = r.lrange(method_name + ":outputs", 0, -1)

    print("{} was called {} times:".format(method_name, count))

    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(method_name, i.decode('utf-8'),
                                     o.decode('utf-8')))


class Cache:
    """Cache class"""
    def __init__(self):
        """constructor"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """generates a random key, stores the input data in Redis using
        the random key and returns the key"""
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str,
                                                                    bytes,
                                                                    int,
                                                                    float]:
        """takes a key string argument and an optional Callable argument
        named fn. This callable will be used to convert the data back to
        desired format"""
        data = self._redis.get(key)
        if fn:
            data = fn(data)
        return data

    def get_str(self, key: str) -> str:
        """automatically parametrize Cache.get to str"""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """automatically parametrize Cache.get to int"""
        return self.get(key, int)
