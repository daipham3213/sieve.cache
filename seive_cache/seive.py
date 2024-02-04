#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#  #
#          http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import logging
import threading
import typing as ty
from functools import _make_key as make_key
from functools import wraps

from seive_cache import node
from seive_cache.backends import base
from seive_cache.common import freeze

__all__ = ["Seive"]

_lock = threading.Lock()

LEN_KEY = "seive_len"

LOG = logging.getLogger(__name__)


class Seive:
    """Seive is a cache implementation that uses a combination of LRU and LFU
    algorithms to evict items from the cache.
    """

    def __init__(self, backend: base.CacheBackend):
        self.head: ty.Optional[node.Node] = None
        self.tail: ty.Optional[node.Node] = None
        self.hand: ty.Optional[node.Node] = None

        self._backend = backend

    def __len__(self):
        length = self._backend.get(LEN_KEY)
        if isinstance(length, int):
            return length
        return 0

    def _get(self, key: str) -> ty.Optional[node.Node]:
        """Get a node from the cache."""
        LOG.debug(f"Getting node with key {key}")
        cached: base.BackendFormatted = self._backend.get(key)
        if cached == base.NO_VALUE:
            return None
        return node.Node(**cached)

    def _set(self, key: str, value: ty.Any):
        """Set a node in the cache."""
        LOG.debug(f"Setting node with key {key}")
        n = node.Node(value=value, key=key)
        self._backend.set(key, n.to_dict())

        current_length = len(self) or 0
        self._backend.set(LEN_KEY, current_length + 1)

    def _delete(self, key: str):
        """Delete a node from the cache."""
        LOG.debug(f"Deleting node with key {key}")
        self._backend.delete(key)

        current_length = len(self) or 0
        self._backend.set(LEN_KEY, current_length - 1)

    def _evict(self):
        """Evict a node from the cache."""
        LOG.debug("Evicting node")
        obj = self.hand if self.hand else self.tail
        while obj and obj.visited:
            obj.visited = False
            obj = obj.prev if obj.prev else self.tail
        self.hand = obj.prev if obj.prev else None
        self._delete(obj.key)

    def cache(self, max_size: int = 128) -> ty.Callable:
        """Decorator to cache the result of a function call."""

        def decorator(func):
            @freeze.hash_dict
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = make_key(args, kwds=kwargs, typed=False)

                n = self._get(key)
                if n:
                    LOG.debug(f"Cache hit for key {key}")
                    n.visited = True
                    self._set(key, n)
                    return n.value

                LOG.debug(f"Cache miss for key {key}")
                result = func(*args, **kwargs)
                with _lock:
                    if self._backend.get(key):
                        pass
                    elif len(self) >= max_size:
                        self._evict()
                    self._set(key, result)
                return result

            return wrapper

        return decorator
