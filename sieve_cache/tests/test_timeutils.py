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

import datetime
from unittest import TestCase
from unittest import mock

import iso8601

from sieve_cache.common import timeutils


class TestTimeutils(TestCase):
    def tearDown(self):
        timeutils.utcnow.override_time = None

    def test_utcnow_ts_uses_time_module_when_no_override(self):
        with mock.patch("time.time", return_value=1700000000.75):
            self.assertEqual(1700000000, timeutils.utcnow_ts())
            self.assertEqual(
                1700000000.75, timeutils.utcnow_ts(microsecond=True)
            )

    def test_utcnow_ts_uses_override_time_and_microseconds(self):
        fixed = datetime.datetime(2024, 1, 1, 12, 0, 1, 500000)
        timeutils.utcnow.override_time = fixed

        self.assertEqual(1704110401, timeutils.utcnow_ts())
        self.assertEqual(1704110401.5, timeutils.utcnow_ts(microsecond=True))

    def test_utcnow_returns_timezone_aware_when_requested(self):
        value = timeutils.utcnow(with_timezone=True)

        self.assertIsNotNone(value.tzinfo)
        self.assertEqual(iso8601.iso8601.UTC, value.tzinfo)

    def test_utcnow_returns_naive_datetime_by_default(self):
        value = timeutils.utcnow()

        self.assertIsNone(value.tzinfo)

    def test_utcnow_uses_override_list(self):
        first = datetime.datetime(2024, 1, 1, 0, 0, 0)
        second = datetime.datetime(2024, 1, 1, 0, 0, 1)
        timeutils.utcnow.override_time = [first, second]

        self.assertEqual(first, timeutils.utcnow())
        self.assertEqual(second, timeutils.utcnow())
