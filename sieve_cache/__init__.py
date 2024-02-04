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
import ssl

from dogpile.cache import region as _region
from dogpile.cache import util

from sieve_cache import sieve
from sieve_cache.common import exceptions

__all__ = ["sieve", "create_sieve"]

_BACKENDS = ['sieve_cache.memory',
             'dogpile.cache.pymemcache',
             'dogpile.cache.memcached',
             'dogpile.cache.pylibmc',
             'dogpile.cache.bmemcached',
             'dogpile.cache.dbm',
             'dogpile.cache.redis',
             'dogpile.cache.memory',
             'dogpile.cache.memory_pickle',
             'dogpile.cache.null']

_DEFAULT_BACKEND = 'dogpile.cache.null'


def create_sieve(backend=_DEFAULT_BACKEND,
                 *,
                 config_prefix="cache.sieve",
                 backend_arguments=None,
                 namespace=None,
                 **configs):
    """Create a new Sieve instance.

    :param backend: The backend to use. Default is 'memory'.
    :param config_prefix: The prefix to use for configuration options.
    :param namespace: The namespace to use for the cache.
    :param configs: Additional configuration options.
    :param backend_arguments: A dictionary of backend-specific arguments.
    :return: A new Sieve instance.
    """
    region = create_region()
    if backend not in _BACKENDS:
        raise exceptions.SieveCacheException(
            f"Invalid backend '{backend}'. Must be one of: {_BACKENDS}"
        )
    configs = _build_config_opts(backend=backend,
                                 prefix=config_prefix,
                                 backend_arguments=backend_arguments,
                                 **configs)
    region.configure_from_config(configs, prefix='%s.' % config_prefix)

    if region.key_mangler is None:
        region.key_mangler = _sha1_mangle_key

    return sieve.Sieve(backend=region, namespace=namespace)


def _build_config_opts(
    backend=_DEFAULT_BACKEND,
    prefix="cache.sieve",
    backend_arguments=None,
    **configs
):
    """Build configuration options for dogpile.backends.

    :param prefix: The prefix to use for configuration options.
    :param configs: Additional configuration options.
    :return: A dictionary of configuration options.
    """
    opts = {}
    opts.setdefault('%s.backend' % prefix, backend)
    opts.setdefault('%s.expiration_time' % prefix, 600)

    for arg in backend_arguments or {}:
        argname = '%s.arguments.%s' % (prefix, arg)
        argvalue = backend_arguments[arg]

        memcache_backends = ('dogpile.backends.memcached',)
        if backend in memcache_backends and arg == 'url':
            argvalue = argvalue.split(',')
        opts[argname] = argvalue

    memcache_servers = configs.get("memcache_servers") or ['localhost:11211']
    opts.setdefault('%s.arguments.url' % prefix, memcache_servers)

    for arg in ('dead_retry', 'socket_timeout', 'pool_maxsize',
                'pool_unused_timeout', 'pool_connection_get_timeout',
                'pool_flush_on_reconnect', 'sasl_enabled', 'username',
                'password'):
        value = configs.get(arg)
        opts['%s.arguments.%s' % (prefix, arg)] = value

    if configs.get('tls_enabled', False):
        tls_cafile = configs['tls_cafile']
        tls_context = ssl.create_default_context(cafile=tls_cafile)

        if configs.get("enforce_fips_mode", False):
            if hasattr(ssl, 'FIPS_mode'):
                ssl.FIPS_mode_set(1)
            else:
                raise exceptions.SieveCacheException(
                    "OpenSSL FIPS mode is not supported by your Python "
                    "version. You must either change the Python executable "
                    "used to a version with FIPS mode support or disable "
                    "FIPS mode by setting the 'enforce_fips_mode' "
                    "configuration option to 'False'."
                )
        tls_certfile = configs.get('tls_certfile')
        tls_context.load_cert_chain(
            tls_certfile,
            configs["tls_keyfile"]
        )

        tls_allowed_ciphers = configs.get('tls_allowed_ciphers')
        if tls_allowed_ciphers:
            tls_context.set_ciphers(tls_allowed_ciphers)
        opts['%s.arguments.tls_context' % prefix] = tls_context

    enable_socket_keepalive = configs.get('enable_socket_keepalive', False)
    if enable_socket_keepalive:
        if backend != "dogpile.backends.pymemcache":
            raise exceptions.SieveCacheException(
                "The 'enable_socket_keepalive' option is only supported "
                "for the 'pymemcache' backend."
            )
        import pymemcache
        socket_keepalive = pymemcache.KeepaliveOpts(
            idle=configs.get("socket_keepalive_idle", 7200),
            intvl=configs.get("socket_keepalive_interval", 75),
            cnt=configs.get("socket_keepalive_count", 9))
        opts['%s.arguments.socket_keepalive' % prefix] = socket_keepalive

    enable_retry_client = configs.get('enable_retry_client', False)
    if enable_retry_client:
        if backend != 'dogpile.cache.pymemcache':
            msg = (
                "Retry client is only supported by the "
                "'dogpile.cache.pymemcache' backend."
            )
            raise exceptions.SieveCacheException(msg)
        import pymemcache
        configs.setdefault('retry_attempts', 2)
        configs.setdefault('retry_delay', 0)
        configs.setdefault('dead_timeout', 60)
        configs.setdefault('hashclient_retry_attempts', 2)
        configs.setdefault('hashclient_retry_delay', 1)

        opts['%s.arguments.enable_retry_client' % prefix] = True
        opts['%s.arguments.retry_attempts' % prefix] = (
            configs['retry_attempts']
        )
        opts['%s.arguments.retry_delay' % prefix] = configs['retry_delay']
        opts['%s.arguments.hashclient_retry_attempts' % prefix] = (
            configs['hashclient_retry_attempts']
        )
        opts['%s.arguments.hashclient_retry_delay' % prefix] = (
            configs['hashclient_retry_delay']
        )
        opts['%s.arguments.dead_timeout' % prefix] = (
            configs['dead_timeout']
        )
    return opts


def _sha1_mangle_key(key):
    """Wrapper for dogpile's sha1_mangle_key.

    dogpile's sha1_mangle_key function expects an encoded string, so we
    should take steps to properly handle multiple inputs before passing
    the key through.
    """
    try:
        key = key.encode('utf-8', errors='xmlcharrefreplace')
    except (UnicodeError, AttributeError):
        # NOTE(stevemar): if encoding fails just continue anyway.
        pass
    return util.sha1_mangle_key(key)


def _key_generate_to_str(s):
    # NOTE: Since we need to stringify all arguments, attempt
    # to stringify and handle the Unicode error explicitly as needed.
    try:
        return str(s)
    except UnicodeEncodeError:
        return s.encode('utf-8')


def function_key_generator(namespace, fn, to_str=_key_generate_to_str):
    # NOTE: This wraps dogpile.backends's default
    # function_key_generator to change the default to_str mechanism.
    return util.function_key_generator(namespace, fn, to_str=to_str)


def kwarg_function_key_generator(namespace, fn, to_str=_key_generate_to_str):
    # NOTE: This wraps dogpile.backends's default
    # kwarg_function_key_generator to change the default to_str mechanism.
    return util.kwarg_function_key_generator(namespace, fn, to_str=to_str)


def create_region(function=function_key_generator):
    """Create a region.

    This is just dogpile.backends.make_region, but the key generator has a
    different to_str mechanism.


    :param function: function used to generate a unique key depending on the
                     arguments of the decorated function.
    :returns: The new region.
    :rtype: :class:`dogpile.cache.region.CacheRegion`

    """

    return _region.make_region(function_key_generator=function)
