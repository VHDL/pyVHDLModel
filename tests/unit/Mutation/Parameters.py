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

The mutators are tested on subprograms (declarative regions with a namespace). The parameter groups of the subprogram
stay a partition of its parameter list.
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
		procedure = Procedure("p")
		a = _parameter("a")
		b = _parameter("b")

		procedure.AddParameterItem(a)
		procedure.AddParameterItem(b)

		self.assertListEqual([a, b], procedure.ParameterItems)
		self.assertEqual(2, procedure.ParameterCount)
		self.assertIs(procedure, a.Parent)
		self.assertIs(procedure, b.Parent)

	def test_Add_Subprogram(self) -> None:
		function = Function("f", _subtypeSymbol("integer"))
		a = _parameter("a")

		function.AddParameterItem(a)

		self.assertListEqual([a], function.ParameterItems)
		self.assertEqual(1, function.ParameterCount)
		self.assertIs(function, a.Parent)

	def test_Add_None(self) -> None:
		procedure = Procedure("p")

		with self.assertRaises(ValueError) as context:
			procedure.AddParameterItem(None)

		self.assertEqual("Parameter 'parameterItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		procedure = Procedure("p")

		with self.assertRaises(TypeError) as context:
			procedure.AddParameterItem(_port("Clock"))

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
		first = Procedure("q", parameterItems=[a])
		procedure = Procedure("p")

		with self.assertRaises(AlreadyInDesignError) as context:
			procedure.AddParameterItem(a)

		self.assertEqual("ParameterConstantInterfaceItem 'a' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Procedure first."], context.exception.__notes__)
		self.assertIs(a, context.exception.Element)
		self.assertIs(first, context.exception.Parent)

	def test_Add_Duplicate(self) -> None:
		a = _parameter("a")
		procedure = Procedure("p", parameterItems=[a])
		duplicate = _parameter("A")

		with self.assertRaises(DuplicateParameterError) as context:
			procedure.AddParameterItem(duplicate)

		self.assertEqual("Procedure already declares 'A'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Interface.ParameterConstantInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertEqual("A", context.exception.Identifier)
		self.assertEqual("a", context.exception.NormalizedIdentifier)
		self.assertIs(procedure, context.exception.Parent)
		self.assertIs(duplicate, context.exception.Element)
		self.assertIs(a, context.exception.Existing)
		self.assertEqual(1, procedure.ParameterCount)
		self.assertIsNone(duplicate.Parent)

	def test_Insert_Start(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		procedure = Procedure("p", parameterItems=[a, b])
		c = _parameter("c")

		procedure.InsertParameterItem(0, c)

		self.assertListEqual([c, a, b], procedure.ParameterItems)
		self.assertIs(procedure, c.Parent)

	def test_Insert_Middle(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		procedure = Procedure("p", parameterItems=[a, b])
		c = _parameter("c")

		procedure.InsertParameterItem(1, c)

		self.assertListEqual([a, c, b], procedure.ParameterItems)

	def test_Insert_End(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		procedure = Procedure("p", parameterItems=[a, b])
		c = _parameter("c")

		procedure.InsertParameterItem(2, c)

		self.assertListEqual([a, b, c], procedure.ParameterItems)

	def test_Insert_OutOfRange(self) -> None:
		procedure = Procedure("p", parameterItems=[_parameter("a")])
		c = _parameter("c")

		with self.assertRaises(ValueError) as context:
			procedure.InsertParameterItem(5, c)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '5'."], context.exception.__notes__)
		self.assertIsNone(c.Parent)

	def test_Insert_Negative(self) -> None:
		a = _parameter("a")
		c = _parameter("c")
		procedure = Procedure("p", parameterItems=[a, c])
		b = _parameter("b")

		procedure.InsertParameterItem(-1, b)

		self.assertListEqual([a, b, c], procedure.ParameterItems)
		self.assertIs(procedure, b.Parent)

	def test_Insert_Negative_OutOfRange(self) -> None:
		procedure = Procedure("p", parameterItems=[_parameter("a")])
		c = _parameter("c")

		with self.assertRaises(ValueError) as context:
			procedure.InsertParameterItem(-2, c)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertIsNone(c.Parent)

	def test_Remove(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		procedure = Procedure("p", parameterItems=[a, b])

		procedure.RemoveParameterItem(a)

		self.assertListEqual([b], procedure.ParameterItems)
		self.assertIsNone(a.Parent)
		self.assertTupleEqual(("a", ), a.Identifiers)

	def test_Remove_AddElsewhere(self) -> None:
		a = _parameter("a")
		procedure = Procedure("p", parameterItems=[a])
		other = Procedure("q")

		procedure.RemoveParameterItem(a)
		other.AddParameterItem(a)

		self.assertEqual(0, procedure.ParameterCount)
		self.assertListEqual([a], other.ParameterItems)
		self.assertIs(other, a.Parent)

	def test_Remove_None(self) -> None:
		procedure = Procedure("p")

		with self.assertRaises(ValueError) as context:
			procedure.RemoveParameterItem(None)

		self.assertEqual("Parameter 'parameterItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		procedure = Procedure("p")

		with self.assertRaises(TypeError) as context:
			procedure.RemoveParameterItem(_generic("BITS"))

		self.assertEqual(
			"Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.",
			str(context.exception)
		)

	def test_Remove_NotAChild(self) -> None:
		procedure = Procedure("p", parameterItems=[_parameter("a")])
		a = _parameter("a")

		with self.assertRaises(NotAChildError) as context:
			procedure.RemoveParameterItem(a)

		self.assertEqual(
			"ParameterConstantInterfaceItem 'a' is not a parameter of this Procedure.",
			str(context.exception)
		)
		self.assertIs(a, context.exception.Element)
		self.assertIs(procedure, context.exception.Parent)
		self.assertEqual(1, procedure.ParameterCount)

	def test_Move(self) -> None:
		"""A move within one parameter list is a remove followed by an insert."""
		a = _parameter("a")
		b = _parameter("b")
		c = _parameter("c")
		procedure = Procedure("p", parameterItems=[a, b, c])

		procedure.RemoveParameterItem(b)
		procedure.InsertParameterItem(0, b)

		self.assertListEqual([b, a, c], procedure.ParameterItems)
		self.assertIs(procedure, b.Parent)

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
		self.assertEqual("a", context.exception.Identifier)
		self.assertEqual("a", context.exception.NormalizedIdentifier)
		self.assertIs(procedure._namespace, context.exception.Namespace)
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
		"""A host class without the methods expected by the mixin can't be instantiated."""
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
				"Missing '_ClashingDeclarations', expected by 'WithParametersMixin'.",
				"Missing '_ParameterItemsChanged', expected by 'WithParametersMixin'.",
			],
			context.exception.__notes__
		)


class ParameterGroups(Testcase):
	def _Procedure(self) -> tuple[Procedure, ParameterGroup, ParameterGroup, ParameterGroup]:
		"""Return a procedure with the parameter groups ``a, b | in_valid, in_data | err``."""
		first =     ParameterGroup([_parameter("a"), _parameter("b")])
		middle =    ParameterGroup([_parameter("in_valid"), _parameter("in_data")], name="In")
		last =      ParameterGroup([_parameter("err")])
		procedure = Procedure("p", parameterItems=[*first, *middle, *last], parameterGroups=[first, middle, last])

		return procedure, first, middle, last

	def assertPartition(self, procedure: Procedure) -> None:
		"""Assert the parameter groups list every parameter once, in declaration order, and each refers to its group."""
		self.assertListEqual(
			procedure.ParameterItems,
			[parameter for group in procedure.ParameterGroups for parameter in group]
		)
		for group in procedure.ParameterGroups:
			self.assertIs(procedure, group.Parent)
			self.assertGreater(len(group), 0)
			for parameter in group:
				self.assertIs(group, parameter.Group)

	def test_Add(self) -> None:
		procedure, first, middle, last = self._Procedure()
		warn = _parameter("warn")

		procedure.AddParameterItem(warn)

		self.assertIs(last, warn.Group)
		self.assertListEqual([first, middle, last], procedure.ParameterGroups)
		self.assertPartition(procedure)

	def test_Add_NoParameters(self) -> None:
		procedure = Procedure("p")
		a = _parameter("a")

		procedure.AddParameterItem(a)

		self.assertEqual(1, len(procedure.ParameterGroups))
		self.assertIsNone(procedure.ParameterGroups[0].Identifier)
		self.assertListEqual([a], procedure.ParameterGroups[0].ParameterItems)
		self.assertPartition(procedure)

	def test_Add_Group(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inAck = _parameter("in_ack")

		procedure.AddParameterItem(inAck, middle)

		self.assertIs(middle, inAck.Group)
		self.assertIs(inAck, middle.ParameterItems[-1])
		self.assertIs(inAck, procedure.ParameterItems[4])
		self.assertPartition(procedure)

	def test_Add_Group_Foreign(self) -> None:
		procedure, first, middle, last = self._Procedure()
		other, _, otherMiddle, _ = self._Procedure()
		inAck = _parameter("in_ack")

		with self.assertRaises(NotAChildError) as context:
			procedure.AddParameterItem(inAck, otherMiddle)

		self.assertEqual("ParameterGroup 'In' is not a parameter group of this Procedure.", str(context.exception))
		self.assertIs(otherMiddle, context.exception.Element)
		self.assertIs(procedure, context.exception.Parent)
		self.assertIsNone(inAck.Parent)
		self.assertIsNone(inAck.Group)

	def test_Insert_Middle(self) -> None:
		"""Without a parameter group, the parameter joins the parameter group of the parameter before it."""
		procedure, first, middle, last = self._Procedure()
		en = _parameter("en")

		procedure.InsertParameterItem(2, en)

		self.assertIs(first, en.Group)
		self.assertListEqual(["a", "b", "en"], [parameter.Identifiers[0] for parameter in first])
		self.assertPartition(procedure)

	def test_Insert_Start(self) -> None:
		"""At index 0, the parameter joins the parameter group of the first parameter."""
		procedure, first, middle, last = self._Procedure()
		en = _parameter("en")

		procedure.InsertParameterItem(0, en)

		self.assertIs(first, en.Group)
		self.assertIs(en, first.ParameterItems[0])
		self.assertPartition(procedure)

	def test_Insert_Negative(self) -> None:
		procedure, first, middle, last = self._Procedure()
		en = _parameter("en")

		procedure.InsertParameterItem(-1, en)

		self.assertIs(middle, en.Group)
		self.assertIs(en, procedure.ParameterItems[4])
		self.assertPartition(procedure)

	def test_Insert_Group(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inAck = _parameter("in_ack")

		procedure.InsertParameterItem(3, inAck, middle)

		self.assertIs(middle, inAck.Group)
		self.assertListEqual(["in_valid", "in_ack", "in_data"], [parameter.Identifiers[0] for parameter in middle])
		self.assertPartition(procedure)

	def test_Insert_Group_Start(self) -> None:
		"""A parameter group given takes a parameter at its start, although the parameter before is in another group."""
		procedure, first, middle, last = self._Procedure()
		inAck = _parameter("in_ack")

		procedure.InsertParameterItem(2, inAck, middle)

		self.assertIs(middle, inAck.Group)
		self.assertIs(inAck, middle.ParameterItems[0])
		self.assertPartition(procedure)

	def test_Insert_Group_End(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inAck = _parameter("in_ack")

		procedure.InsertParameterItem(4, inAck, middle)

		self.assertIs(middle, inAck.Group)
		self.assertIs(inAck, middle.ParameterItems[-1])
		self.assertPartition(procedure)

	def test_Insert_Group_Outside(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inAck = _parameter("in_ack")

		with self.assertRaises(ValueError) as context:
			procedure.InsertParameterItem(5, inAck, middle)

		self.assertEqual("Parameter 'index' is outside of parameter 'group' at 2..4.", str(context.exception))
		self.assertListEqual(["Got value '5'."], context.exception.__notes__)
		self.assertIsNone(inAck.Parent)
		self.assertIsNone(inAck.Group)
		self.assertEqual(5, procedure.ParameterCount)

	def test_Insert_Group_Foreign(self) -> None:
		procedure, first, middle, last = self._Procedure()
		group = ParameterGroup([_parameter("x")])
		inAck = _parameter("in_ack")

		with self.assertRaises(NotAChildError) as context:
			procedure.InsertParameterItem(0, inAck, group)

		self.assertEqual("ParameterGroup is not a parameter group of this Procedure.", str(context.exception))
		self.assertIs(group, context.exception.Element)
		self.assertIsNone(inAck.Parent)

	def test_Insert_Group_WrongType(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inAck = _parameter("in_ack")

		with self.assertRaises(TypeError) as context:
			procedure.InsertParameterItem(0, inAck, "In")

		self.assertEqual("Parameter 'group' is not of type 'ParameterGroup'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertIsNone(inAck.Parent)

	def test_Remove(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inData = middle.ParameterItems[1]

		procedure.RemoveParameterItem(inData)

		self.assertIsNone(inData.Group)
		self.assertListEqual(["in_valid"], [parameter.Identifiers[0] for parameter in middle])
		self.assertListEqual([first, middle, last], procedure.ParameterGroups)
		self.assertPartition(procedure)

	def test_Remove_LastParameterOfGroup(self) -> None:
		"""A parameter group, which becomes empty, is removed from the language construct."""
		procedure, first, middle, last = self._Procedure()
		err = last.ParameterItems[0]

		procedure.RemoveParameterItem(err)

		self.assertIsNone(err.Group)
		self.assertIsNone(last.Parent)
		self.assertListEqual([first, middle], procedure.ParameterGroups)
		self.assertPartition(procedure)

	def test_Remove_AddElsewhere(self) -> None:
		procedure, first, middle, last = self._Procedure()
		err = last.ParameterItems[0]
		other = Procedure("q")

		procedure.RemoveParameterItem(err)
		other.AddParameterItem(err)

		self.assertIs(other.ParameterGroups[0], err.Group)
		self.assertPartition(other)

	def test_Move(self) -> None:
		"""A moved parameter leaves its parameter group and joins the one of the parameter before its new position."""
		procedure, first, middle, last = self._Procedure()
		b = first.ParameterItems[1]

		procedure.MoveParameterItem(b, 2)

		self.assertIs(middle, b.Group)
		self.assertListEqual(["a"], [parameter.Identifiers[0] for parameter in first])
		self.assertListEqual(["in_valid", "b", "in_data"], [parameter.Identifiers[0] for parameter in middle])
		self.assertPartition(procedure)

	def test_Move_Start(self) -> None:
		procedure, first, middle, last = self._Procedure()
		inData = middle.ParameterItems[1]

		procedure.MoveParameterItem(inData, 0)

		self.assertIs(first, inData.Group)
		self.assertIs(inData, first.ParameterItems[0])
		self.assertPartition(procedure)

	def test_Move_LastParameterOfGroup(self) -> None:
		"""Moving the only parameter of a parameter group removes the parameter group."""
		procedure, first, middle, last = self._Procedure()
		err = last.ParameterItems[0]

		procedure.MoveParameterItem(err, 0)

		self.assertIs(first, err.Group)
		self.assertIsNone(last.Parent)
		self.assertListEqual([first, middle], procedure.ParameterGroups)
		self.assertPartition(procedure)

	def test_Move_SamePosition(self) -> None:
		"""A move to the parameter's current position keeps its parameter group."""
		procedure, first, middle, last = self._Procedure()
		inValid = middle.ParameterItems[0]

		procedure.MoveParameterItem(inValid, 2)

		self.assertIs(middle, inValid.Group)
		self.assertPartition(procedure)

	def test_Signature(self) -> None:
		"""A parameter inserted into a parameter group changes the subprogram's signature."""
		procedure, first, middle, last = self._Procedure()
		signature = procedure.Signature
		inAck = _parameter("in_ack")

		procedure.InsertParameterItem(4, inAck, middle)

		self.assertIsNot(signature, procedure.Signature)
		self.assertEqual(6, len(procedure.Signature.ParameterTypes))
