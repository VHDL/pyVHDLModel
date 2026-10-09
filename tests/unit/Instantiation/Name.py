# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |                                                    #
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |                                                    #
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |                                                    #
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|                                                    #
#  |_|    |___/                                                                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""Tests for pyVHDLModel.Name."""
from unittest import TestCase

from pyVHDLModel.Base        import ModelEntity
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Name        import (
	Name, SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, AttributeName, AllName, OpenName,
)


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Names(TestCase):
	def test_NoPrefixNoParent(self) -> None:
		name = Name("foo")

		self.assertEqual("foo", name.Identifier)
		self.assertEqual("foo", name.NormalizedIdentifier)
		self.assertIsNone(name.Prefix)
		self.assertFalse(name.HasPrefix)
		self.assertIs(name, name.Root)
		self.assertIsNone(name.Parent)
		self.assertEqual("foo", str(name))
		self.assertEqual("Name: 'foo'", repr(name))

	def test_IdentifierIsNormalized(self) -> None:
		name = Name("FOO")

		self.assertEqual("FOO", name.Identifier)
		self.assertEqual("foo", name.NormalizedIdentifier)

	def test_WithPrefix(self) -> None:
		"""``Root`` is inherited from the prefix's own root, so for a two-element chain it's simply the
		prefix itself; see ``test_RootIsTransitiveAcrossAChain`` for a longer chain."""
		prefix = Name("pkg")
		name = Name("member", prefix)

		self.assertIs(prefix, name.Prefix)
		self.assertTrue(name.HasPrefix)
		self.assertIs(prefix, name.Root)

	def test_RootIsTransitiveAcrossAChain(self) -> None:
		root = Name("a")
		middle = Name("b", root)
		leaf = Name("c", middle)

		self.assertIs(root, middle.Root)
		self.assertIs(root, leaf.Root)
		self.assertIs(middle, leaf.Prefix)

	def test_WithParent(self) -> None:
		parent = ModelEntity()
		name = Name("foo", parent=parent)

		self.assertIs(parent, name.Parent)


class SimpleNames(TestCase):
	def test_Construction(self) -> None:
		name = SimpleName("sig")

		self.assertEqual("sig", name.Identifier)
		self.assertFalse(name.HasPrefix)


class ParenthesisNames(TestCase):
	"""
	``arr(3)`` written through the generic ``ParenthesisName``.

	It is e.g. an indexed name, before it's disambiguated into an indexed name, slice, or function call.
	"""

	def test_Construction(self) -> None:
		prefix = SimpleName("arr")
		association = GenericAssociationItem(None, IntegerLiteral(3))
		name = ParenthesisName(prefix, [association])

		self.assertEqual(1, len(name.Associations))
		self.assertIs(association, name.Associations[0])
		self.assertIs(name, association.Parent)
		self.assertEqual("arr(3)", str(name))


class IndexedNames(TestCase):
	def test_Construction(self) -> None:
		prefix = SimpleName("arr")
		index = IntegerLiteral(3)
		name = IndexedName(prefix, [index])

		self.assertEqual(1, len(name.Indices))
		self.assertIs(index, name.Indices[0])
		self.assertIs(name, index.Parent)
		self.assertEqual("arr(3)", str(name))


class SlicedNames(TestCase):
	def test_Construction(self) -> None:
		prefix = SimpleName("v")
		name = SlicedName("", prefix)

		self.assertIs(prefix, name.Prefix)


class SelectedNames(TestCase):
	def test_Construction(self) -> None:
		prefix = SimpleName("pkg")
		name = SelectedName("member", prefix)

		self.assertEqual("member", name.Identifier)
		self.assertIs(prefix, name.Prefix)
		self.assertEqual("pkg.member", str(name))


class AttributeNames(TestCase):
	def test_Construction(self) -> None:
		prefix = SimpleName("sig")
		name = AttributeName("range", prefix)

		self.assertEqual("range", name.Identifier)
		self.assertEqual("sig'range", str(name))


class AllNames(TestCase):
	"""``use ieee.numeric_std.all;`` - ``AllName`` is a ``SelectedName`` fixed to the identifier
	``"all"``."""

	def test_Construction(self) -> None:
		prefix = SimpleName("numeric_std")
		name = AllName(prefix)

		self.assertEqual("all", name.Identifier)
		self.assertEqual("numeric_std.all", str(name))


class OpenNames(TestCase):
	"""Regression test: the ``parent`` argument was previously forwarded positionally into ``Name.
	__init__``'s ``prefix`` parameter instead of its ``parent`` parameter (``super().__init__("open",
	parent)``), so any ``OpenName(parent=...)`` call crashed with an ``AttributeError`` the moment
	``Name.__init__`` tried to read ``prefix._root`` off whatever non-``Name`` object had been passed
	as ``parent``."""

	def test_ConstructionWithoutParent(self) -> None:
		name = OpenName()

		self.assertEqual("open", name.Identifier)
		self.assertIsNone(name.Prefix)
		self.assertIsNone(name.Parent)
		self.assertEqual("open", str(name))

	def test_ConstructionWithParent(self) -> None:
		parent = ModelEntity()
		name = OpenName(parent)

		self.assertIs(parent, name.Parent)
		self.assertIsNone(name.Prefix)
