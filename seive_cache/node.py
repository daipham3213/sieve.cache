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

from dataclasses import dataclass
import typing as ty

from seive_cache.backends import base


@dataclass
class Node:
    """Node class for storing data in a linked list."""

    value: base.ValuePayload
    key: str
    visited: bool = False
    next: ty.Optional[str] = None
    prev: ty.Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the node to a dictionary."""
        value = self.value
        if isinstance(self.value, Node):
            value = self.value.to_dict()
        if isinstance(self.value, ty.Sequence):
            value = [v.to_dict() if isinstance(v, Node) else v for v in value]
        return {
            "value": value,
            "key": self.key,
            "visited": self.visited,
            "next": self.next,
            "prev": self.prev,
        }

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(f"Node has no attribute {item}")

    def __setitem__(self, key, value):
        setattr(self, key, value)
