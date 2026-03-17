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
from unittest import TestCase

import sieve_cache
from sieve_cache import create_region
from sieve_cache import sieve

logging.basicConfig(level=logging.DEBUG)


class TestSieve(TestCase):
    def test_create_sieve_rejects_invalid_backend(self):
        with self.assertRaises(sieve_cache.exceptions.SieveCacheException):
            sieve_cache.create_sieve(backend="invalid.backend")

    def test_cache_returns_cached_value_without_recompute(self):
        memo = sieve_cache.create_sieve(backend="dogpile.cache.memory")
        calls = {"count": 0}

        @memo.cache(max_size=8)
        def get_value(number):
            calls["count"] += 1
            return number * 10

        self.assertEqual(50, get_value(5))
        self.assertEqual(50, get_value(5))
        self.assertEqual(1, calls["count"])

    def test_sieve_eviction_gives_second_chance_to_visited_node(self):
        memo = sieve_cache.create_sieve(backend="dogpile.cache.memory")
        calls = {1: 0, 2: 0, 3: 0}

        @memo.cache(max_size=2)
        def load(number):
            calls[number] += 1
            return number

        self.assertEqual(1, load(1))
        self.assertEqual(2, load(2))
        self.assertEqual(1, load(1))
        self.assertEqual(3, load(3))

        self.assertEqual(1, load(1))
        self.assertEqual(2, load(2))

        self.assertEqual(1, calls[1])
        self.assertEqual(2, calls[2])
        self.assertEqual(1, calls[3])

    def test_cache_rejects_non_positive_max_size(self):
        memo = sieve_cache.create_sieve(backend="dogpile.cache.memory")

        with self.assertRaises(ValueError):

            @memo.cache(max_size=0)
            def invalid_size_cache():
                return "x"

    def test_cache_length_is_namespaced(self):
        region = create_region()
        region.configure(backend="dogpile.cache.memory")

        cache_a = sieve.Sieve(backend=region, namespace="a")
        cache_b = sieve.Sieve(backend=region, namespace="b")

        cache_a.length = 4
        cache_b.length = 1

        self.assertEqual(4, cache_a.length)
        self.assertEqual(1, cache_b.length)
