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

from sieve_cache.node import Node


class TestNode(TestCase):
    def test_to_dict_handles_nested_nodes_and_sequences(self):
        child = Node(value=123, key="child")
        parent = Node(value=[child, "raw"], key="parent", visited=True)

        payload = parent.to_dict()

        self.assertEqual("parent", payload["key"])
        self.assertTrue(payload["visited"])
        self.assertEqual(123, payload["value"][0]["value"])
        self.assertEqual("raw", payload["value"][1])

    def test_dict_method_returns_serialized_payload(self):
        node = Node(value=1, key="k", next="n", prev="p")

        payload = node.__dict__()

        self.assertEqual("k", payload["key"])
        self.assertEqual("n", payload["next"])
        self.assertEqual("p", payload["prev"])

    def test_getitem_and_setitem(self):
        node = Node(value=1, key="k")

        self.assertEqual("k", node["key"])

        node["visited"] = True
        self.assertTrue(node.visited)

        with self.assertRaises(KeyError):
            node["missing"]
