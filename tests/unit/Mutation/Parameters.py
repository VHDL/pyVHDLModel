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
"""
Mutation tests for parameter lists (:class:`~pyVHDLModel.Regions.WithParametersMixin`).

The mutators are tested on subprograms (declarative regions with a namespace) and a parameter group (no namespace).
"""
from pyTooling.MetaClasses  import UnfulfilledExpectationError
from pyTooling.Warning      import WarningCollector
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import ModelEntity
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicateParameterError, NotInNamespaceError
from pyVHDLModel.Interface  import ParameterGroup
from pyVHDLModel.Object     import Variable
from pyVHDLModel.Regions    import WithParametersMixin
from pyVHDLModel.Subprogram import Function, Procedure

from tests.unit             import _subtypeSymbol
from tests.unit.Mutation    import _generic, _parameter, _port


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Parameters(Testcase):
	def test_Add(self) -> None:
		group = ParameterGroup([])
		a = _parameter("a")
		b = _parameter("b")

		group.AddParameterItem(a)
		group.AddParameterItem(b)

		self.assertListEqual([a, b], group.ParameterItems)
		self.assertEqual(2, group.ParameterCount)
		self.assertIs(group, a.Parent)
		self.assertIs(group, b.Parent)

	def test_Add_Subprogram(self) -> None:
		function = Function("f", _subtypeSymbol("integer"))
		a = _parameter("a")

		function.AddParameterItem(a)

		self.assertListEqual([a], function.ParameterItems)
		self.assertEqual(1, function.ParameterCount)
		self.assertIs(function, a.Parent)

	def test_Add_None(self) -> None:
		group = ParameterGroup([])

		with self.assertRaises(ValueError) as context:
			group.AddParameterItem(None)

		self.assertEqual("Parameter 'parameterItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		group = ParameterGroup([])

		with self.assertRaises(TypeError) as context:
			group.AddParameterItem(_port("Clock"))

		self.assertEqual(
			"Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Add_AlreadyInDesign(self) -> None:
		a = _parameter("a")
		ParameterGroup([a])
		group = ParameterGroup([])

		with self.assertRaises(AlreadyInDesignError) as context:
			group.AddParameterItem(a)

		self.assertEqual("ParameterConstantInterfaceItem 'a' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its ParameterGroup first."], context.exception.__notes__)

	def test_Add_Duplicate(self) -> None:
		group = ParameterGroup([_parameter("a")])
		duplicate = _parameter("A")

		with self.assertRaises(DuplicateParameterError) as context:
			group.AddParameterItem(duplicate)

		self.assertEqual("ParameterGroup already has a parameter 'A'.", str(context.exception))
		self.assertEqual(1, group.ParameterCount)
		self.assertIsNone(duplicate.Parent)

	def test_Insert_Start(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		group = ParameterGroup([a, b])
		c = _parameter("c")

		group.InsertParameterItem(0, c)

		self.assertListEqual([c, a, b], group.ParameterItems)
		self.assertIs(group, c.Parent)

	def test_Insert_Middle(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		group = ParameterGroup([a, b])
		c = _parameter("c")

		group.InsertParameterItem(1, c)

		self.assertListEqual([a, c, b], group.ParameterItems)

	def test_Insert_End(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		group = ParameterGroup([a, b])
		c = _parameter("c")

		group.InsertParameterItem(2, c)

		self.assertListEqual([a, b, c], group.ParameterItems)

	def test_Insert_OutOfRange(self) -> None:
		group = ParameterGroup([_parameter("a")])
		c = _parameter("c")

		with self.assertRaises(ValueError) as context:
			group.InsertParameterItem(5, c)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '5'."], context.exception.__notes__)
		self.assertIsNone(c.Parent)

	def test_Insert_Negative(self) -> None:
		a = _parameter("a")
		c = _parameter("c")
		group = ParameterGroup([a, c])
		b = _parameter("b")

		group.InsertParameterItem(-1, b)

		self.assertListEqual([a, b, c], group.ParameterItems)
		self.assertIs(group, b.Parent)

	def test_Insert_Negative_OutOfRange(self) -> None:
		group = ParameterGroup([_parameter("a")])
		c = _parameter("c")

		with self.assertRaises(ValueError) as context:
			group.InsertParameterItem(-2, c)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertIsNone(c.Parent)

	def test_Remove(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		group = ParameterGroup([a, b])

		group.RemoveParameterItem(a)

		self.assertListEqual([b], group.ParameterItems)
		self.assertIsNone(a.Parent)
		self.assertTupleEqual(("a", ), a.Identifiers)

	def test_Remove_AddElsewhere(self) -> None:
		a = _parameter("a")
		group = ParameterGroup([a])
		other = ParameterGroup([])

		group.RemoveParameterItem(a)
		other.AddParameterItem(a)

		self.assertEqual(0, group.ParameterCount)
		self.assertListEqual([a], other.ParameterItems)
		self.assertIs(other, a.Parent)

	def test_Remove_None(self) -> None:
		group = ParameterGroup([])

		with self.assertRaises(ValueError) as context:
			group.RemoveParameterItem(None)

		self.assertEqual("Parameter 'parameterItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		group = ParameterGroup([])

		with self.assertRaises(TypeError) as context:
			group.RemoveParameterItem(_generic("BITS"))

		self.assertEqual(
			"Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.",
			str(context.exception)
		)

	def test_Remove_NotAChild(self) -> None:
		group = ParameterGroup([_parameter("a")])
		a = _parameter("a")

		with self.assertRaises(NotAChildError) as context:
			group.RemoveParameterItem(a)

		self.assertEqual(
			"ParameterConstantInterfaceItem 'a' is not a parameter of this ParameterGroup.",
			str(context.exception)
		)
		self.assertEqual(1, group.ParameterCount)

	def test_Move(self) -> None:
		"""A move within one parameter list is a remove followed by an insert."""
		a = _parameter("a")
		b = _parameter("b")
		c = _parameter("c")
		group = ParameterGroup([a, b, c])

		group.RemoveParameterItem(b)
		group.InsertParameterItem(0, b)

		self.assertListEqual([b, a, c], group.ParameterItems)
		self.assertIs(group, b.Parent)

	def test_Namespace(self) -> None:
		procedure = Procedure("p")
		procedure.IndexDeclaredItems()
		item = _parameter("a", "B")

		procedure.AddParameterItem(item)

		self.assertIs(item, procedure._namespace._elements["a"])
		self.assertIs(item, procedure._namespace._elements["b"])

		procedure.RemoveParameterItem(item)

		self.assertNotIn("a", procedure._namespace._elements)
		self.assertNotIn("b", procedure._namespace._elements)

	def test_Namespace_AddNotIndexed(self) -> None:
		"""A parameter added to a region, which wasn't indexed yet, enters the namespace when the region is indexed."""
		procedure = Procedure("p")
		a = _parameter("a")

		procedure.AddParameterItem(a)

		self.assertDictEqual({}, procedure._namespace._elements)

		procedure.IndexDeclaredItems()

		self.assertDictEqual({"a": a}, procedure._namespace._elements)

	def test_Namespace_OtherElement(self) -> None:
		"""Removing a parameter, whose identifier refers to a duplicate declaration in the namespace, is rejected."""
		a = _parameter("a")
		variable = Variable(["a"], _subtypeSymbol("integer"))
		procedure = Procedure("p", parameterItems=[a], declaredItems=[variable])
		with WarningCollector():
			procedure.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			procedure.RemoveParameterItem(a)

		self.assertEqual("Namespace 'p' has another element for 'a'.", str(context.exception))
		self.assertListEqual(["Found element of type 'pyVHDLModel.Object.Variable'."], context.exception.__notes__)
		self.assertListEqual([a], procedure.ParameterItems)
		self.assertIs(procedure, a.Parent)
		self.assertIs(variable, procedure._namespace._elements["a"])

	def test_Namespace_NotIndexed(self) -> None:
		"""Removing a parameter of a region, which wasn't indexed yet, leaves the namespace as is."""
		a = _parameter("a")
		procedure = Procedure("p", parameterItems=[a])

		procedure.RemoveParameterItem(a)

		self.assertEqual(0, procedure.ParameterCount)
		self.assertIsNone(a.Parent)
		self.assertDictEqual({}, procedure._namespace._elements)

	def test_Contract(self) -> None:
		"""A host class without the namespace methods expected by the mixin can't be instantiated."""
		class Host(ModelEntity, WithParametersMixin):
			def __init__(self) -> None:
				super().__init__()
				WithParametersMixin.__init__(self)

		with self.assertRaises(UnfulfilledExpectationError) as context:
			Host()

		self.assertEqual("Class 'Host' doesn't provide every expected member.", str(context.exception))
		self.assertListEqual(
			[
				"Missing '_AddToNamespace', expected by 'WithParametersMixin'.",
				"Missing '_RemoveFromNamespace', expected by 'WithParametersMixin'.",
			],
			context.exception.__notes__
		)
