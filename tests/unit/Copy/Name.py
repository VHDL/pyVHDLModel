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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
#
"""
Copy tests for names (:mod:`pyVHDLModel.Name`).
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Name as NameModule
from pyVHDLModel.Association     import ParameterAssociationItem
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, \
                                        AttributeName, AllName, OpenName

from tests.unit                  import _Element
from tests.unit.Copy             import _object, _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _DerivedSimpleName(SimpleName):
	"""A name of a class derived outside pyVHDLModel, with the constructor of its base-class."""


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every name class has a ``Copy()`` calling its own constructor."""
		classes = _concreteModelClasses(NameModule)

		self.assertIn(OpenName, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class SimpleNames(Testcase):
	def test_Copy(self) -> None:
		original = SimpleName("Clock", parent=_Element())

		copy = original.Copy()

		self.assertIs(SimpleName, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertEqual("Clock", copy.Identifier)
		self.assertEqual("clock", copy.NormalizedIdentifier)
		self.assertIsNone(copy.Prefix)
		self.assertIs(copy, copy.Root)
		self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_Copy_Derived(self) -> None:
		"""A copy of a name of a derived class is an instance of that class."""
		original = _DerivedSimpleName("Clock")

		copy = original.Copy()

		self.assertIs(_DerivedSimpleName, type(copy))
		self.assertEqual("Clock", copy.Identifier)


class SelectedNames(Testcase):
	def test_Copy(self) -> None:
		original = SelectedName("numeric_std", SimpleName("ieee"), parent=_Element())

		copy = original.Copy()

		self.assertIs(SelectedName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertEqual("numeric_std", copy.Identifier)
		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertEqual("ieee", copy.Prefix.Identifier)
		self.assertIs(copy.Prefix, copy.Root)
		self.assertIs(original.Prefix, original.Root)
		self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_Copy_Chain(self) -> None:
		original = SelectedName("unsigned", SelectedName("numeric_std", SimpleName("ieee")))

		copy = original.Copy()

		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertIsNot(original.Prefix.Prefix, copy.Prefix.Prefix)
		self.assertIs(copy.Prefix.Prefix, copy.Root)
		self.assertEqual("ieee.numeric_std.unsigned", VHDLWriter().Format(copy))


class AllNames(Testcase):
	def test_Copy(self) -> None:
		original = AllName(SelectedName("numeric_std", SimpleName("ieee")), parent=_Element())

		copy = original.Copy()

		self.assertIs(AllName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertIsNot(original.Prefix.Prefix, copy.Prefix.Prefix)
		self.assertEqual("ieee.numeric_std.all", VHDLWriter().Format(copy))


class AttributeNames(Testcase):
	def test_Copy(self) -> None:
		original = AttributeName("range", SimpleName("v"), parent=_Element())

		copy = original.Copy()

		self.assertIs(AttributeName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertEqual("range", copy.Identifier)
		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertEqual("v'range", VHDLWriter().Format(copy))


class OpenNames(Testcase):
	def test_Copy(self) -> None:
		original = OpenName(parent=_Element())

		copy = original.Copy()

		self.assertIs(OpenName, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertEqual("open", VHDLWriter().Format(copy))


class SlicedNames(Testcase):
	def test_Copy(self) -> None:
		original = SlicedName("", SimpleName("v"), parent=_Element())

		copy = original.Copy()

		self.assertIs(SlicedName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertEqual("v", copy.Prefix.Identifier)


class IndexedNames(Testcase):
	def test_Copy(self) -> None:
		original = IndexedName(SimpleName("m"), [IntegerLiteral(1), _object("j")], parent=_Element())

		copy = original.Copy()

		self.assertIs(IndexedName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertIsNot(original.Indices, copy.Indices)
		self.assertEqual(2, len(copy.Indices))
		self.assertIsNot(original.Indices[0], copy.Indices[0])
		self.assertIs(copy, copy.Indices[0].Parent)
		self.assertIsNot(original.Indices[1], copy.Indices[1])
		self.assertIsNot(original.Indices[1].Name, copy.Indices[1].Name)
		self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_Copy_Modify(self) -> None:
		"""Changing the indices of the copy leaves the original unchanged."""
		original = IndexedName(SimpleName("m"), [IntegerLiteral(1)])

		copy = original.Copy()
		copy.Indices.append(IntegerLiteral(2))

		self.assertEqual("m(1)", VHDLWriter().Format(original))
		self.assertEqual("m(1, 2)", VHDLWriter().Format(copy))


class ParenthesisNames(Testcase):
	def test_Copy(self) -> None:
		association = ParameterAssociationItem(None, _object("a"))
		original = ParenthesisName(SimpleName("resize"), [association], parent=_Element())

		copy = original.Copy()

		self.assertIs(ParenthesisName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Prefix, copy.Prefix)
		self.assertIsNot(original.Associations, copy.Associations)
		self.assertIsNot(association, copy.Associations[0])
		self.assertIs(ParameterAssociationItem, type(copy.Associations[0]))
		self.assertIs(copy, copy.Associations[0].Parent)
		self.assertIsNot(association.Actual, copy.Associations[0].Actual)
		self.assertEqual("resize(a)", VHDLWriter().Format(copy))
