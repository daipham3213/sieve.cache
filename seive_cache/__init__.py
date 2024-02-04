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

from seive_cache import seive
from seive_cache.common import exceptions
import stevedore

__all__ = ["seive", "create_seive"]

_DRIVER_NAMESPACE = "seive_cache.backends"


def create_seive(backend="memory", *args, **kwargs):
    """Create a new Seive instance.

    :param backend: The backend to use. Default is 'memory'.
    :param args: Additional arguments to pass to the backend.
    :param kwargs: Additional keyword arguments to pass to the backend.
    :return: A new Seive instance.
    """
    backend = _construct_backend(backend, *args, **kwargs)
    return seive.Seive(backend)


def _construct_backend(backend: str, *args, **kwargs):
    try:
        manager = stevedore.DriverManager(
            namespace=_DRIVER_NAMESPACE,
            name=backend,
            invoke_on_load=True,
            invoke_args=args,
            invoke_kwds=kwargs,
        )
        return manager.driver
    except Exception as e:
        raise exceptions.SieveCacheException(
            "Failed to load backend: %s" % e
        ) from e
