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

import seive_cache

MEMO = seive_cache.create_seive()

logging.basicConfig(level=logging.DEBUG)


@MEMO.cache(max_size=128)
def func_sieve(obj):
    return obj


@MEMO.cache(max_size=128)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


class TestSeive(TestCase):

    def test_seive(self):
        obj = {'a': 1, 'b': 2}

        # First call
        result = func_sieve(obj)
        self.assertEqual(result, obj)

        # Second call
        result = func_sieve(obj)
        self.assertEqual(result, obj)

    def test_fib_with_memo(self):
        memo_fib = MEMO.cache(max_size=128)(fib)

        result = memo_fib(40)
        self.assertEqual(result, 102334155)
