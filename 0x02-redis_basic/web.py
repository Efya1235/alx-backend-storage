#!/usr/bin/env python3
"""implementing an expiring web cache and tracker"""
import redis
from functools import wraps
from typing import Callable
from datetime import datetime, timedelta


def count_requests(method: Callable) -> Callable:
    """counts how many times methods of the Cache class are called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def access_time(method: Callable) -> Callable:
    """stores the time of every function call"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        self._redis.setex(method.__qualname__, timedelta(seconds=10))
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """Cache class"""
    def __init__(self):
        """constructor"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_requests
    @access_time
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """generates a random key, stores the input data in Redis using
        the key and returns the key"""
        key = str(uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str,
                                                                    bytes,
                                                                    int,
                                                                    float]:
        """converts data to the desired format"""
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
