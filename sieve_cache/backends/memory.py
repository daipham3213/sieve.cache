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
import typing as ty

from dogpile.cache import api

from sieve_cache.common import timeutils

__all__ = ['InMemoryDriver']

_NO_VALUE = api.NO_VALUE


class InMemoryDriver(api.CacheBackend):
    """A InMemoryDriver that based on dictionary.

    Arguments accepted in the arguments dictionary:

    :param expiration_time: interval in seconds to indicate maximum
        time-to-live value for each key in DictCacheBackend.
        Default expiration_time value is 0, that means that all keys have
        infinite time-to-live value.
    :type expiration_time: real
    """

    def __init__(self, arguments: api.BackendArguments):
        self.expiration_time = arguments.get('expiration_time', 0)
        self.cache = {}

    def get(self, key: api.KeyType) -> api.BackendFormatted:
        """Retrieves the value for a key.

        :param key: dictionary key
        :returns: value for a key or :data:`dogpile.backends.NO_VALUE`
            for nonexistent or expired keys.
        """
        (value, timeout) = self.cache.get(key, (_NO_VALUE, 0))
        if self.expiration_time > 0 and timeutils.utcnow_ts() >= timeout:
            self.cache.pop(key, None)
            return _NO_VALUE

        return value

    def get_multi(
        self,
        keys: ty.Sequence[api.KeyType]
    ) -> ty.Sequence[api.BackendFormatted]:
        """Retrieves the value for a list of keys."""
        yield from map(self.get, keys)

    def set(self, key: api.KeyType, value: api.BackendSetType) -> None:
        """Set a value in the backends.

        :param key: dictionary key
        :param value: value to be stored
        """
        self.set_multi({key: value})

    def set_multi(
        self,
        mapping: ty.Mapping[api.KeyType, api.BackendSetType]
    ) -> None:
        """Set multiple values in the backends.
        Expunges expired keys during each set.

        :param mapping: dictionary with key/value pairs
        """
        self._clear()
        timeout = 0
        if self.expiration_time > 0:
            timeout = timeutils.utcnow_ts() + self.expiration_time
        for key, value in mapping.items():
            self.cache[key] = (value, timeout)

    def delete(self, key: api.KeyType) -> None:
        """Delete a value from the backends.

        :param key: dictionary key
        """
        self.delete_multi([key])

    def delete_multi(self, keys: ty.Sequence[api.KeyType]) -> None:
        """Delete multiple values from the backends.

        :param keys: list of dictionary keys
        """
        for key in keys:
            self.cache.pop(key, None)

    def _clear(self):
        """Expunges expired keys."""
        now = timeutils.utcnow_ts()
        for k in list(self.cache):
            (_val, timeout) = self.cache[k]
            if 0 < timeout <= now:
                del self.cache[k]
