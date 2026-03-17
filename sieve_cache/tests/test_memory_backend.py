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

from unittest import TestCase
from unittest import mock

from dogpile.cache import api

from sieve_cache.backends.memory import InMemoryDriver


class TestInMemoryDriver(TestCase):
    def _make_backend(self, expiration_time):
        backend = InMemoryDriver.__new__(InMemoryDriver)
        backend.expiration_time = expiration_time
        backend.cache = {}
        return backend

    def test_set_and_get_without_expiration(self):
        backend = self._make_backend(expiration_time=0)

        backend.set("a", 1)

        self.assertEqual(1, backend.get("a"))
        self.assertEqual(api.NO_VALUE, backend.get("missing"))

    def test_get_multi_and_delete_methods(self):
        backend = self._make_backend(expiration_time=0)
        backend.set_multi({"a": 1, "b": 2})

        values = list(backend.get_multi(["a", "b", "c"]))

        self.assertEqual([1, 2, api.NO_VALUE], values)

        backend.delete("a")
        backend.delete_multi(["b", "missing"])
        self.assertEqual(api.NO_VALUE, backend.get("a"))
        self.assertEqual(api.NO_VALUE, backend.get("b"))

    def test_get_returns_no_value_for_expired_keys(self):
        backend = self._make_backend(expiration_time=10)

        with mock.patch(
            "sieve_cache.backends.memory.timeutils.utcnow_ts"
        ) as now:
            now.return_value = 100
            backend.set("a", 1)

            now.return_value = 105
            self.assertEqual(1, backend.get("a"))

            now.return_value = 110
            self.assertEqual(api.NO_VALUE, backend.get("a"))
            self.assertNotIn("a", backend.cache)

    def test_set_multi_clears_expired_keys(self):
        backend = self._make_backend(expiration_time=10)

        with mock.patch(
            "sieve_cache.backends.memory.timeutils.utcnow_ts"
        ) as now:
            now.return_value = 100
            backend.set("old", "value")

            now.return_value = 500
            backend.set_multi({"new": "value"})

        self.assertIn("new", backend.cache)
        self.assertNotIn("old", backend.cache)
