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
Mutation tests: moving a declared item to another position of its declarative region.

Each test checks the order of the declared items, and for an indexed region, that the lookup tables and the namespace
are the ones a fresh re-index yields.
"""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.DesignUnit import Architecture
from pyVHDLModel.Exception  import NotAChildError
from pyVHDLModel.Subprogram import Procedure
from pyVHDLModel.Type       import ProtectedType

from tests.unit             import _entitySymbol
from tests.unit.Mutation    import _constant, _function, _parameter, _procedure, _reindexed, _signal, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _architecture(*declaredItems) -> Architecture:
	return Architecture("rtl", _entitySymbol("e"), declaredItems=declaredItems)


class ConcurrentDeclaredItems(Testcase):
	def test_Move(self) -> None:
		a = _signal("a")
		b = _signal("b")
		c = _constant("c")
		architecture = _architecture(a, b, c)

		architecture.MoveDeclaredItem(c, 0)

		self.assertListEqual([c, a, b], architecture.DeclaredItems)
		self.assertIs(architecture, c.Parent)
		self.assertDictEqual({}, architecture.Signals)

	def test_Move_Indexed(self) -> None:
		a = _signal("a")
		b = _signal("b")
		c = _constant("c")
		architecture = _architecture(a, b, c)
		architecture.IndexDeclaredItems()

		architecture.MoveDeclaredItem(a, -1)

		self.assertListEqual([b, c, a], architecture.DeclaredItems)
		self.assertDictEqual({"a": a, "b": b}, architecture.Signals)
		self.assertDictEqual({"a": a, "b": b, "c": c}, architecture._namespace._elements)
		self.assertDictEqual(*_reindexed(architecture))

	def test_Move_Overloads(self) -> None:
		"""The overloads follow the declaration order; the namespace refers to the overload declared last."""
		overload1 = _function("f")
		overload2 = _function("f")
		overload3 = _function("f")
		architecture = _architecture(overload1, _signal("s"), overload2, overload3)
		architecture.IndexDeclaredItems()

		architecture.MoveDeclaredItem(overload3, 0)

		self.assertListEqual([overload3, overload1, overload2], architecture.Functions["f"])
		self.assertIs(overload2, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Move_Overloads_ToEnd(self) -> None:
		overload1 = _function("f")
		overload2 = _function("f")
		architecture = _architecture(overload1, overload2, _signal("s"))
		architecture.IndexDeclaredItems()

		architecture.MoveDeclaredItem(overload1, 2)

		self.assertListEqual([overload2, overload1], architecture.Functions["f"])
		self.assertIs(overload1, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Move_ProcedureAndFunction(self) -> None:
		function = _function("f")
		procedure = _procedure("f")
		architecture = _architecture(function, procedure)
		architecture.IndexDeclaredItems()

		architecture.MoveDeclaredItem(procedure, 0)

		self.assertListEqual([procedure, function], architecture.DeclaredItems)
		self.assertIs(function, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Move_Duplicate(self) -> None:
		"""Of two declarations read by a parser sharing an identifier, the one declared last is indexed."""
		signal1 = _signal("s")
		signal2 = _signal("s")
		architecture = _architecture(signal1, signal2)
		with WarningCollector():
			architecture.IndexDeclaredItems()

			architecture.MoveDeclaredItem(signal2, 0)

			self.assertIs(signal1, architecture.Signals["s"])
			self.assertIs(signal1, architecture._namespace._elements["s"])
			self.assertDictEqual(*_reindexed(architecture))

	def test_Before(self) -> None:
		a = _signal("a")
		b = _signal("b")
		c = _signal("c")
		architecture = _architecture(a, b, c)

		architecture.MoveDeclaredItemBefore(a, c)

		self.assertListEqual([b, a, c], architecture.DeclaredItems)

	def test_Before_Backward(self) -> None:
		a = _signal("a")
		b = _signal("b")
		c = _signal("c")
		architecture = _architecture(a, b, c)

		architecture.MoveDeclaredItemBefore(c, a)

		self.assertListEqual([c, a, b], architecture.DeclaredItems)

	def test_Before_Itself(self) -> None:
		a = _signal("a")
		b = _signal("b")
		architecture = _architecture(a, b)

		architecture.MoveDeclaredItemBefore(b, b)

		self.assertListEqual([a, b], architecture.DeclaredItems)

	def test_After(self) -> None:
		a = _signal("a")
		b = _signal("b")
		c = _signal("c")
		architecture = _architecture(a, b, c)

		architecture.MoveDeclaredItemAfter(a, b)

		self.assertListEqual([b, a, c], architecture.DeclaredItems)

	def test_After_Backward(self) -> None:
		a = _signal("a")
		b = _signal("b")
		c = _signal("c")
		architecture = _architecture(a, b, c)

		architecture.MoveDeclaredItemAfter(c, a)

		self.assertListEqual([a, c, b], architecture.DeclaredItems)

	def test_After_Itself(self) -> None:
		a = _signal("a")
		b = _signal("b")
		architecture = _architecture(a, b)

		architecture.MoveDeclaredItemAfter(a, a)

		self.assertListEqual([a, b], architecture.DeclaredItems)

	def test_After_Overloads(self) -> None:
		overload1 = _function("f")
		overload2 = _function("f")
		architecture = _architecture(overload1, overload2)
		architecture.IndexDeclaredItems()

		architecture.MoveDeclaredItemAfter(overload1, overload2)

		self.assertListEqual([overload2, overload1], architecture.Functions["f"])
		self.assertIs(overload1, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Move_None(self) -> None:
		architecture = _architecture(_signal("a"))

		with self.assertRaises(ValueError) as context:
			architecture.MoveDeclaredItem(None, 0)

		self.assertEqual("Parameter 'declaredItem' is None.", str(context.exception))

	def test_Move_WrongType(self) -> None:
		architecture = _architecture(_signal("a"))

		with self.assertRaises(TypeError) as context:
			architecture.MoveDeclaredItem("a", 0)

		self.assertEqual("Parameter 'declaredItem' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Move_NotAChild(self) -> None:
		architecture = _architecture(_signal("a"))
		clock = _signal("Clock")

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveDeclaredItem(clock, 0)

		self.assertEqual("Signal 'Clock' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(clock, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)

	def test_Move_IndexNone(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)

		with self.assertRaises(ValueError) as context:
			architecture.MoveDeclaredItem(a, None)

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Move_IndexWrongType(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)

		with self.assertRaises(TypeError) as context:
			architecture.MoveDeclaredItem(a, 0.0)

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'float'."], context.exception.__notes__)

	def test_Move_IndexOutOfRange(self) -> None:
		a = _signal("a")
		b = _signal("b")
		architecture = _architecture(a, b)

		with self.assertRaises(ValueError) as context:
			architecture.MoveDeclaredItem(a, 2)

		self.assertEqual("Parameter 'index' is out of range -2..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)
		self.assertListEqual([a, b], architecture.DeclaredItems)

	def test_Before_None(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)

		with self.assertRaises(ValueError) as context:
			architecture.MoveDeclaredItemBefore(a, None)

		self.assertEqual("Parameter 'before' is None.", str(context.exception))

	def test_Before_WrongType(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)

		with self.assertRaises(TypeError) as context:
			architecture.MoveDeclaredItemBefore(a, "a")

		self.assertEqual("Parameter 'before' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Before_NotAChild(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)
		clock = _signal("Clock")

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveDeclaredItemBefore(a, clock)

		self.assertEqual("Signal 'Clock' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(clock, context.exception.Element)

	def test_Before_ItemNotAChild(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)
		clock = _signal("Clock")

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveDeclaredItemBefore(clock, a)

		self.assertEqual("Signal 'Clock' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(clock, context.exception.Element)

	def test_After_None(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)

		with self.assertRaises(ValueError) as context:
			architecture.MoveDeclaredItemAfter(a, None)

		self.assertEqual("Parameter 'after' is None.", str(context.exception))

	def test_After_NotAChild(self) -> None:
		a = _signal("a")
		architecture = _architecture(a)
		clock = _signal("Clock")

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveDeclaredItemAfter(a, clock)

		self.assertEqual("Signal 'Clock' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(clock, context.exception.Element)

	def test_After_ItemNotAChild(self) -> None:
		"""Moving after the last declared item, the declared item is checked before the position."""
		a = _signal("a")
		architecture = _architecture(a)
		clock = _signal("Clock")

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveDeclaredItemAfter(clock, a)

		self.assertEqual("Signal 'Clock' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(clock, context.exception.Element)


class SequentialDeclaredItems(Testcase):
	def test_Move(self) -> None:
		a = _variable("a")
		b = _variable("b")
		process = ProcessStatement("p", declaredItems=[a, b])
		process.IndexDeclaredItems()

		process.MoveDeclaredItem(b, 0)

		self.assertListEqual([b, a], process.DeclaredItems)
		self.assertDictEqual({"a": a, "b": b}, process.Variables)
		self.assertDictEqual(*_reindexed(process))

	def test_Move_Overloads(self) -> None:
		overload1 = _procedure("q")
		overload2 = _procedure("q")
		process = ProcessStatement("p", declaredItems=[overload1, overload2])
		process.IndexDeclaredItems()

		process.MoveDeclaredItemBefore(overload2, overload1)

		self.assertListEqual([overload2, overload1], process.Procedures["q"])
		self.assertIs(overload1, process._namespace._elements["q"])
		self.assertDictEqual(*_reindexed(process))

	def test_Move_Subprogram(self) -> None:
		"""A subprogram's parameters precede its declared items."""
		a = _variable("a")
		b = _variable("b")
		procedure = Procedure("p", parameterItems=[_parameter("x")], declaredItems=[a, b])
		procedure.IndexDeclaredItems()

		procedure.MoveDeclaredItemAfter(a, b)

		self.assertListEqual([b, a], procedure.DeclaredItems)
		self.assertDictEqual(*_reindexed(procedure))


class ProtectedTypeDeclaredItems(Testcase):
	def test_Move_Overloads(self) -> None:
		overload1 = _procedure("increment")
		overload2 = _procedure("increment")
		function = _function("get")
		protectedType = ProtectedType("counter", declaredItems=[overload1, function, overload2])
		protectedType.IndexDeclaredItems()

		protectedType.MoveDeclaredItem(overload2, 0)

		self.assertListEqual([overload2, overload1, function], protectedType.DeclaredItems)
		self.assertListEqual([overload2, overload1], protectedType.Procedures["increment"])
		self.assertIs(overload1, protectedType._namespace._elements["increment"])
		self.assertDictEqual(*_reindexed(protectedType))
