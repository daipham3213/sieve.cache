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

from importlib import metadata


class _VersionInfo:
    def __init__(self, package_name):
        self.package_name = package_name

    def version_string(self):
        for package_name in (self.package_name, "sieve_cache"):
            try:
                return metadata.version(package_name)
            except metadata.PackageNotFoundError:
                continue
        return "0.0.0"


version_info = _VersionInfo("seive_cache")
version_string = version_info.version_string
