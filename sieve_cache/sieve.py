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
from functools import wraps

from dogpile.cache import api as base
from dogpile.cache import region

from sieve_cache import node as _n

__all__ = ["Sieve"]

_lock = threading.Lock()

LEN_KEY = "sieve_len"
DEFAULT_CACHE_SIZE = 128
DEFAULT_NAMESPACE = "sieve"

LOG = logging.getLogger(__name__)


class Sieve:
    """Caching is a method of storing temporary data for quick access to keep
    the online world running smoothly. But with limited space comes a critical
    decision: what to keep and discard. This is where eviction algorithms come
    into play.
    """

    def __init__(self,
                 backend: region.CacheRegion,
                 namespace: str = DEFAULT_NAMESPACE):
        self.head: ty.Optional[_n.Node] = None
        self.tail: ty.Optional[_n.Node] = None
        self.hand: ty.Optional[_n.Node] = None

        self._backend = backend
        self.namespace = namespace

    @property
    def length(self) -> int:
        """Return the length of the cache."""
        key = LEN_KEY
        value = self._backend.get(key)
        if value == base.NO_VALUE or not isinstance(value, int):
            return 0
        return int(value)

    @length.setter
    def length(self, value: int) -> None:
        key = LEN_KEY
        self._backend.set(key, value)

    def __len__(self):
        return self.length

    def _add(self, node: _n.Node) -> None:
        node.next = self.head
        node.prev = None
        if self.head:
            self.head.prev = node
        self.head = node
        if not self.tail:
            self.tail = node

    def _remove(self, node: _n.Node) -> None:
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def _evict(self) -> None:
        """Evict a node from the backends."""
        obj = self.hand if self.hand else self.tail
        while obj and obj.visited:
            obj.visited = False
            obj = obj.prev if obj.prev else self.tail
        self.hand = obj.prev if obj.prev else None
        self._backend.delete(obj.key)

        self._remove(obj)
        self.length -= 1

    def cache(self, max_size: int = DEFAULT_CACHE_SIZE) -> ty.Callable:
        """Decorator to backends the result of a function call."""

        def decorator(func) -> ty.Callable:
            key_generator = self._backend.function_key_generator(
                self.namespace, func
            )

            @wraps(func)
            def wrapper(*args, **kwargs):
                key = key_generator(*args, **kwargs)
                node = self._backend.get(key)
                if node:
                    node.visited = True
                    self._backend.set(key, node)
                    return node.value

                result = func(*args, **kwargs)
                with _lock:
                    if self._backend.get(key):
                        pass
                    elif len(self) >= max_size:
                        self._evict()
                    node = _n.Node(key=key, value=result, visited=False)
                    self._add(node)
                    self.length += 1
                    self._backend.set(key, node)
                return result

            return wrapper

        return decorator
