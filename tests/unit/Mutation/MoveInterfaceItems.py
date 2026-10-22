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
Mutation tests: moving a generic, a port or a parameter to another position of its interface list.

Each test checks the order of the interface list, and for an indexed region, that the namespace is the one a fresh
re-index yields.
"""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel.DesignUnit import Component, Entity
from pyVHDLModel.Exception  import NotAChildError, NotInNamespaceError
from pyVHDLModel.Interface  import GenericFunctionInterfaceItem
from pyVHDLModel.Subprogram import Procedure

from tests.unit             import _subtypeSymbol
from tests.unit.Mutation    import _function, _generic, _parameter, _port, _reindexed


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _genericFunction(identifier: str) -> GenericFunctionInterfaceItem:
	return GenericFunctionInterfaceItem(identifier, _subtypeSymbol("integer"))


class GenericItems(Testcase):
	def test_Move(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		width = _generic("WIDTH")
		entity = Entity("e", genericItems=[bits, depth, width])

		entity.MoveGenericItem(bits, 2)

		self.assertListEqual([depth, width, bits], entity.GenericItems)
		self.assertIs(entity, bits.Parent)

	def test_Move_Backward(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		width = _generic("WIDTH")
		entity = Entity("e", genericItems=[bits, depth, width])

		entity.MoveGenericItem(width, 0)

		self.assertListEqual([width, bits, depth], entity.GenericItems)

	def test_Move_Negative(self) -> None:
		"""A negative index counts from the end: ``-1`` moves the generic to the end."""
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		width = _generic("WIDTH")
		entity = Entity("e", genericItems=[bits, depth, width])

		entity.MoveGenericItem(bits, -1)

		self.assertListEqual([depth, width, bits], entity.GenericItems)

	def test_Move_SamePosition(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])

		entity.MoveGenericItem(depth, 1)

		self.assertListEqual([bits, depth], entity.GenericItems)

	def test_Move_Indexed(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])
		entity.IndexDeclaredItems()

		entity.MoveGenericItem(depth, 0)

		self.assertListEqual([depth, bits], entity.GenericItems)
		self.assertDictEqual({"bits": bits, "depth": depth}, entity._namespace._elements)
		self.assertDictEqual(*_reindexed(entity))

	def test_Move_Overloads(self) -> None:
		"""The namespace refers to the generic subprogram declared last."""
		overload1 = _genericFunction("f")
		overload2 = _genericFunction("f")
		entity = Entity("e", genericItems=[overload1, overload2])
		entity.IndexDeclaredItems()

		entity.MoveGenericItem(overload2, 0)

		self.assertListEqual([overload2, overload1], entity.GenericItems)
		self.assertIs(overload1, entity._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(entity))

	def test_Move_OverloadsAndDeclaredItem(self) -> None:
		"""A declared subprogram follows the generic subprograms: the namespace keeps referring to it."""
		overload1 = _genericFunction("f")
		overload2 = _genericFunction("f")
		function = _function("f")
		entity = Entity("e", genericItems=[overload1, overload2], declaredItems=[function])
		entity.IndexDeclaredItems()

		entity.MoveGenericItem(overload1, 1)

		self.assertListEqual([overload2, overload1], entity.GenericItems)
		self.assertIs(function, entity._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(entity))

	def test_Move_Component(self) -> None:
		"""A component has no namespace."""
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		component = Component("c", genericItems=[bits, depth])

		component.MoveGenericItem(bits, 1)

		self.assertListEqual([depth, bits], component.GenericItems)

	def test_Move_Shadowed(self) -> None:
		"""A generic subprogram shadowed by a duplicate declaration read by a parser isn't in the namespace."""
		function = _genericFunction("f")
		constant = _generic("f")
		entity = Entity("e", genericItems=[function, constant, _generic("BITS")])
		with WarningCollector():
			entity.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			entity.MoveGenericItem(function, 2)

		self.assertEqual("Namespace 'e' has another element for 'f'.", str(context.exception))
		self.assertIs(function, entity.GenericItems[0])

	def test_Move_None(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])

		with self.assertRaises(ValueError) as context:
			entity.MoveGenericItem(None, 0)

		self.assertEqual("Parameter 'genericItem' is None.", str(context.exception))

	def test_Move_WrongType(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])

		with self.assertRaises(TypeError) as context:
			entity.MoveGenericItem(_port("Clock"), 0)

		self.assertEqual("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Move_NotAChild(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])
		depth = _generic("DEPTH")

		with self.assertRaises(NotAChildError) as context:
			entity.MoveGenericItem(depth, 0)

		self.assertEqual(
			"GenericConstantInterfaceItem 'DEPTH' is not a generic of this Entity.",
			str(context.exception)
		)
		self.assertIs(depth, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)

	def test_Move_IndexNone(self) -> None:
		bits = _generic("BITS")
		entity = Entity("e", genericItems=[bits])

		with self.assertRaises(ValueError) as context:
			entity.MoveGenericItem(bits, None)

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Move_IndexWrongType(self) -> None:
		bits = _generic("BITS")
		entity = Entity("e", genericItems=[bits])

		with self.assertRaises(TypeError) as context:
			entity.MoveGenericItem(bits, "0")

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Move_IndexOutOfRange(self) -> None:
		"""The last position is the number of generics minus one: a moved generic isn't added."""
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])

		with self.assertRaises(ValueError) as context:
			entity.MoveGenericItem(bits, 2)

		self.assertEqual("Parameter 'index' is out of range -2..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)
		self.assertListEqual([bits, depth], entity.GenericItems)

	def test_Move_IndexOutOfRange_Negative(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])

		with self.assertRaises(ValueError) as context:
			entity.MoveGenericItem(bits, -3)

		self.assertEqual("Parameter 'index' is out of range -2..1.", str(context.exception))
		self.assertListEqual(["Got value '-3'."], context.exception.__notes__)


class PortItems(Testcase):
	def test_Move(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		data = _port("Data")
		entity = Entity("e", portItems=[clock, reset, data])

		entity.MovePortItem(data, 0)

		self.assertListEqual([data, clock, reset], entity.PortItems)
		self.assertIs(entity, data.Parent)

	def test_Move_Negative(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		data = _port("Data")
		entity = Entity("e", portItems=[clock, reset, data])

		entity.MovePortItem(clock, -2)

		self.assertListEqual([reset, clock, data], entity.PortItems)

	def test_Move_Indexed(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		entity = Entity("e", portItems=[clock, reset])
		entity.IndexDeclaredItems()

		entity.MovePortItem(clock, 1)

		self.assertListEqual([reset, clock], entity.PortItems)
		self.assertDictEqual({"clock": clock, "reset": reset}, entity._namespace._elements)
		self.assertDictEqual(*_reindexed(entity))

	def test_Move_Component(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		component = Component("c", portItems=[clock, reset])

		component.MovePortItem(reset, 0)

		self.assertListEqual([reset, clock], component.PortItems)

	def test_Move_None(self) -> None:
		entity = Entity("e", portItems=[_port("Clock")])

		with self.assertRaises(ValueError) as context:
			entity.MovePortItem(None, 0)

		self.assertEqual("Parameter 'portItem' is None.", str(context.exception))

	def test_Move_WrongType(self) -> None:
		entity = Entity("e", portItems=[_port("Clock")])

		with self.assertRaises(TypeError) as context:
			entity.MovePortItem(_generic("BITS"), 0)

		self.assertEqual("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Move_NotAChild(self) -> None:
		entity = Entity("e", portItems=[_port("Clock")])
		reset = _port("Reset")

		with self.assertRaises(NotAChildError) as context:
			entity.MovePortItem(reset, 0)

		self.assertEqual("PortSimpleSignalInterfaceItem 'Reset' is not a port of this Entity.", str(context.exception))
		self.assertIs(reset, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)

	def test_Move_IndexOutOfRange(self) -> None:
		clock = _port("Clock")
		entity = Entity("e", portItems=[clock])

		with self.assertRaises(ValueError) as context:
			entity.MovePortItem(clock, 1)

		self.assertEqual("Parameter 'index' is out of range -1..0.", str(context.exception))
		self.assertListEqual(["Got value '1'."], context.exception.__notes__)


class ParameterItems(Testcase):
	def test_Move(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		c = _parameter("c")
		procedure = Procedure("p", parameterItems=[a, b, c])

		procedure.MoveParameterItem(a, 1)

		self.assertListEqual([b, a, c], procedure.ParameterItems)
		self.assertIs(procedure, a.Parent)

	def test_Move_Indexed(self) -> None:
		a = _parameter("a")
		b = _parameter("b")
		procedure = Procedure("p", parameterItems=[a, b])
		procedure.IndexDeclaredItems()

		procedure.MoveParameterItem(b, -2)

		self.assertListEqual([b, a], procedure.ParameterItems)
		self.assertDictEqual({"a": a, "b": b}, procedure._namespace._elements)
		self.assertDictEqual(*_reindexed(procedure))

	def test_Move_None(self) -> None:
		procedure = Procedure("p", parameterItems=[_parameter("a")])

		with self.assertRaises(ValueError) as context:
			procedure.MoveParameterItem(None, 0)

		self.assertEqual("Parameter 'parameterItem' is None.", str(context.exception))

	def test_Move_WrongType(self) -> None:
		procedure = Procedure("p", parameterItems=[_parameter("a")])

		with self.assertRaises(TypeError) as context:
			procedure.MoveParameterItem(_port("Clock"), 0)

		self.assertEqual(
			"Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Move_NotAChild(self) -> None:
		procedure = Procedure("p", parameterItems=[_parameter("a")])
		b = _parameter("b")

		with self.assertRaises(NotAChildError) as context:
			procedure.MoveParameterItem(b, 0)

		self.assertEqual(
			"ParameterConstantInterfaceItem 'b' is not a parameter of this Procedure.",
			str(context.exception)
		)
		self.assertIs(b, context.exception.Element)
		self.assertIs(procedure, context.exception.Parent)

	def test_Move_IndexOutOfRange(self) -> None:
		a = _parameter("a")
		procedure = Procedure("p", parameterItems=[a, _parameter("b")])

		with self.assertRaises(ValueError) as context:
			procedure.MoveParameterItem(a, -3)

		self.assertEqual("Parameter 'index' is out of range -2..1.", str(context.exception))
		self.assertListEqual(["Got value '-3'."], context.exception.__notes__)
