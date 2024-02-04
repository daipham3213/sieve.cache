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
import calendar
import datetime
import time

import iso8601


def utcnow_ts(microsecond=False):
    """Timestamp version of our utcnow function.
    """
    if utcnow.override_time is None:
        # NOTE(kgriffs): This is several times faster
        # than going through calendar.timegm(...)
        timestamp = time.time()
        if not microsecond:
            timestamp = int(timestamp)
        return timestamp

    now = utcnow()
    timestamp = calendar.timegm(now.timetuple())

    if microsecond:
        timestamp += float(now.microsecond) / 1000000

    return timestamp


def utcnow(with_timezone=False):
    """Overridable version of utils.utcnow that can return a TZ-aware datetime.
    """
    if utcnow.override_time:
        try:
            return utcnow.override_time.pop(0)
        except AttributeError:
            return utcnow.override_time
    if with_timezone:
        return datetime.datetime.now(tz=iso8601.iso8601.UTC)
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


utcnow.override_time = None
