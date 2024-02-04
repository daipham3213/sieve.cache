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

from seive_cache.backends import base


class InMemoryDriver(base.CacheBackend):
    """In-memory storage driver for storing data directly into memory."""

    def __init__(self, *args, **kwargs):
        self._cache = kwargs.pop("cache_dict", {})

    def get(self, key: base.KeyType) -> base.BackendFormatted:
        return self._cache.get(key, base.NO_VALUE)

    def set(self, key: base.KeyType, value: base.BackendSetType) -> None:
        self._cache[key] = value

    def delete(self, key: base.KeyType) -> None:
        self._cache.pop(key, base.NO_VALUE)

    def set_multi(
        self,
        mapping: ty.Dict[base.KeyType, base.BackendSetType]
    ) -> None:
        self._cache.update(mapping)

    def delete_multi(self, keys: ty.List[base.KeyType]) -> None:
        for k in keys:
            self._cache.pop(k, base.NO_VALUE)

    def get_multi(
        self, keys: ty.Sequence[base.KeyType]
    ) -> ty.Sequence[base.BackendFormatted]:
        yield from map(lambda k: self.get(key=k), keys)
