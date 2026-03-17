# sieve.cache

`sieve.cache` is a lightweight Python cache utility that implements the
SIEVE eviction algorithm on top of `dogpile.cache` backends.

## Project Summary

- Implements a `Sieve` cache with a decorator-based API.
- Uses a doubly linked list (`head`, `tail`, `hand`) to track entries.
- Applies SIEVE eviction using a `visited` bit on each node.
- Integrates with `dogpile.cache` regions and key generation.
- Includes an in-memory backend adapter (`sieve_cache.memory`).

## How It Works

When a decorated function is called:

1. A cache key is generated from function arguments.
2. If the key exists, the node is marked as visited and returned.
3. On a miss, the function is executed and result cached.
4. If cache size reaches `max_size`, an item is evicted by SIEVE.

The eviction pointer (`hand`) scans backward, clears `visited=True` nodes,
and removes the first unvisited candidate.

## Installation

Install from source:

```bash
pip install sieve-cache
```

## Quick Usage

```python
import sieve_cache

cache = sieve_cache.create_sieve(backend="sieve_cache.memory")

@cache.cache(max_size=128)
def expensive_call(x: int) -> int:
    return x * x

print(expensive_call(5))
print(expensive_call(5))  # cached
```

## Project Layout

- `sieve_cache/sieve.py`: Core SIEVE cache implementation and decorator.
- `sieve_cache/node.py`: Cache node model used by linked-list structure.
- `sieve_cache/backends/memory.py`: In-memory `dogpile.cache` backend.
- `sieve_cache/__init__.py`: Region/backend configuration and factory helpers.

## References

- [SIEVE is Simpler than LRU: an Efficient Turn-Key Eviction Algorithm for Web Caches](https://cachemon.github.io/SIEVE-website/)
