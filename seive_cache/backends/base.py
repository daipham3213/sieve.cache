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
import abc
import time
import typing as ty

MetaDataType = ty.Mapping[str, ty.Any]

KeyType = str
"""A cache key."""

ValuePayload = ty.Any
"""An object to be placed in the cache against a key."""

Serializer = ty.Callable[[ValuePayload], bytes]
Deserializer = ty.Callable[[bytes], ValuePayload]


class NoValue:
    """Describe a missing cache value.

    The :data:`.NO_VALUE` constant should be used.

    """

    @property
    def payload(self) -> "NoValue":
        return self

    def __repr__(self):
        """Ensure __repr__ is a consistent value in case NoValue is used to
        fill another cache key.

        """
        return "<seive_cache.backends.base.NoValue object>"

    def __bool__(self):  # pragma NO COVERAGE
        return False


# Represent a missing value in the cache.
NO_VALUE = NoValue()


class CachedValue(ty.NamedTuple):
    """Represent a value stored in the cache."""

    payload: ValuePayload
    """the actual cached value."""

    metadata: MetaDataType
    """Metadata dictionary for the cached value.

    Prefer using accessors such as :attr:`.CachedValue.cached_time` rather
    than accessing this mapping directly.

    """

    @property
    def cached_time(self) -> float:
        """The epoch (floating point time value) stored when this payload was
        cached.

        """
        return ty.cast(float, self.metadata["ct"])

    @property
    def age(self) -> float:
        """Returns the elapsed time in seconds as a `float` since the insertion
        of the value in the cache.

        This value is computed **dynamically** by subtracting the cached
        floating point epoch value from the value of ``time.time()``.

        """
        return time.time() - self.cached_time


CacheReturnType = ty.Union[CachedValue, NoValue]
"""The non-serialized form of what may be returned from a backend
get method.

"""

SerializedReturnType = ty.Union[bytes, NoValue]
"""the serialized form of what may be returned from a backend get method."""

BackendFormatted = ty.Union[CacheReturnType, SerializedReturnType]
"""Describes the type returned from the :meth:`.CacheBackend.get` method."""

BackendSetType = ty.Union[CachedValue, bytes]
"""Describes the value argument passed to the :meth:`.CacheBackend.set`
method."""

BackendArguments = ty.Mapping[str, ty.Any]


class CacheBackend:
    """Base class of persistence backends for storing and retrieving data"""

    serializer: ty.Union[None, Serializer] = None
    """Serializer function that will be used by default if not overridden
    by the region.

    """

    deserializer: ty.Union[None, Deserializer] = None
    """deserializer function that will be used by default if not overridden
    by the region.

    """

    @abc.abstractmethod
    def __init__(self,
                 arguments: ty.Optional[BackendArguments] = None) -> None:
        """Construct a new :class:`.CacheBackend`.

        Subclasses should override this to
        handle the given arguments.

        :param arguments: The ``arguments`` parameter
         passed to :func:`.make_registry`.

        """

    @abc.abstractmethod
    def get(self, key: KeyType) -> BackendFormatted:
        """Retrieve a value from the cache.

        :param key: the key to be retrieved.

        :return: a :class:`.CacheReturnType` object.

        """

    @abc.abstractmethod
    def set(self, key: KeyType, value: BackendSetType) -> None:
        """Set a value in the cache.

        :param key: the key to be set.
        :param value: the value to be set.

        """

    @abc.abstractmethod
    def delete(self, key: KeyType) -> None:
        """Delete a value from the cache.

        :param key: the key to be deleted.

        """

    @abc.abstractmethod
    def get_multi(self,
                  keys: ty.Sequence[KeyType]) -> ty.Sequence[BackendFormatted]:
        """Retrieve multiple values from the cache.

        :param keys: the keys to be retrieved.

        """

    @abc.abstractmethod
    def set_multi(self, mapping: ty.Mapping[KeyType, BackendSetType]) -> None:
        """Set multiple values in the cache.

        :param mapping: a dictionary of key/value pairs.

        """

    @abc.abstractmethod
    def delete_multi(self, keys: ty.Sequence[KeyType]) -> None:
        """Delete multiple values from the cache.

        :param keys: the keys to be deleted.

        """
