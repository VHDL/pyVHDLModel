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
Mutation tests for the declared items of sequential declaration regions
(:class:`~pyVHDLModel.Regions.SequentialDeclarationRegionMixin`).

The mutators are tested on a process, a function and a protected type body.
"""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.DesignUnit import Component
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicateVariableError, NotInNamespaceError
from pyVHDLModel.Object     import File, SharedVariable
from pyVHDLModel.Type       import FullType, ProtectedTypeBody, Subtype

from tests.unit             import _subtypeSymbol
from tests.unit.Mutation    import _constant, _function, _procedure, _signal, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SequentialDeclaredItems(Testcase):
	def test_Add(self) -> None:
		process = ProcessStatement("proc")
		process.IndexDeclaredItems()
		variable = _variable("v", "w")
		constant = _constant("C")
		file = File(["f"], _subtypeSymbol("text"))

		process.AddDeclaredItem(variable)
		process.AddDeclaredItem(constant)
		process.AddDeclaredItem(file)

		self.assertListEqual([variable, constant, file], process.DeclaredItems)
		self.assertIs(process, variable.Parent)
		self.assertDictEqual({"v": variable, "w": variable}, process.Variables)
		self.assertDictEqual({"c": constant}, process.Constants)
		self.assertDictEqual({"f": file}, process.Files)
		self.assertDictEqual({"v": variable, "w": variable, "c": constant, "f": file}, process._namespace._elements)

	def test_Add_Types(self) -> None:
		process = ProcessStatement("proc")
		process.IndexDeclaredItems()
		fullType = FullType("T")
		subtype = Subtype("S", _subtypeSymbol("bit"))

		process.AddDeclaredItem(fullType)
		process.AddDeclaredItem(subtype)

		self.assertDictEqual({"t": fullType}, process.Types)
		self.assertDictEqual({"s": subtype}, process.Subtypes)

	def test_Add_Subprogram(self) -> None:
		"""A subprogram declared in a process nests its namespace in the process' namespace."""
		process = ProcessStatement("proc")
		process.IndexDeclaredItems()
		procedure = _procedure("p")

		process.AddDeclaredItem(procedure)

		self.assertDictEqual({"p": [procedure]}, process.Procedures)
		self.assertIs(process._namespace, procedure._namespace.ParentNamespace)

	def test_Add_Function(self) -> None:
		function = _function("f")
		function.IndexDeclaredItems()
		variable = _variable("v")

		function.AddDeclaredItem(variable)

		self.assertListEqual([variable], function.DeclaredItems)
		self.assertIs(function, variable.Parent)
		self.assertDictEqual({"v": variable}, function.Variables)

	def test_Add_ProtectedTypeBody(self) -> None:
		body = ProtectedTypeBody("counter")
		body.IndexDeclaredItems()
		variable = _variable("count")
		method = _procedure("increment")

		body.AddDeclaredItem(variable)
		body.AddDeclaredItem(method)

		self.assertListEqual([method], body.Methods)
		self.assertDictEqual({"count": variable}, body.Variables)
		self.assertDictEqual({"increment": [method]}, body.Procedures)

	def test_Add_Overloads(self) -> None:
		process = ProcessStatement("proc")
		process.IndexDeclaredItems()
		overload1 = _procedure("p")
		overload2 = _procedure("p")

		process.AddDeclaredItem(overload1)
		process.AddDeclaredItem(overload2)

		self.assertDictEqual({"p": [overload1, overload2]}, process.Procedures)
		self.assertIs(overload2, process._namespace._elements["p"])

	def test_Add_WrongType(self) -> None:
		process = ProcessStatement("proc")

		with self.assertRaises(TypeError) as context:
			process.AddDeclaredItem(_signal("s"))

		self.assertEqual(
			"Parameter 'declaredItem' is not a declaration allowed in ProcessStatement.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)

	def test_Add_WrongType_SharedVariable(self) -> None:
		process = ProcessStatement("proc")

		with self.assertRaises(TypeError) as context:
			process.AddDeclaredItem(SharedVariable(["sv"], _subtypeSymbol("natural")))

		self.assertEqual(
			"Parameter 'declaredItem' is not a declaration allowed in ProcessStatement.",
			str(context.exception)
		)

	def test_Add_WrongType_Component(self) -> None:
		function = _function("f")

		with self.assertRaises(TypeError) as context:
			function.AddDeclaredItem(Component("c"))

		self.assertEqual("Parameter 'declaredItem' is not a declaration allowed in Function.", str(context.exception))

	def test_Add_AlreadyInDesign(self) -> None:
		variable = _variable("v")
		first = ProcessStatement("p1", declaredItems=[variable])
		process = ProcessStatement("p2")

		with self.assertRaises(AlreadyInDesignError) as context:
			process.AddDeclaredItem(variable)

		self.assertEqual("Variable 'v' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its ProcessStatement first."], context.exception.__notes__)
		self.assertIs(variable, context.exception.Element)
		self.assertIs(first, context.exception.Parent)

	def test_Add_Duplicate(self) -> None:
		constant = _constant("x")
		process = ProcessStatement("proc", declaredItems=[constant])
		variable = _variable("X")

		with self.assertRaises(DuplicateVariableError) as context:
			process.AddDeclaredItem(variable)

		self.assertEqual("ProcessStatement already declares 'X'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Object.Constant'."],
			context.exception.__notes__
		)
		self.assertEqual("x", context.exception.Identifier)
		self.assertIs(process._namespace, context.exception.Namespace)
		self.assertIs(variable, context.exception.Element)
		self.assertIs(constant, context.exception.Existing)

	def test_Insert_Middle(self) -> None:
		first = _variable("a")
		last = _variable("c")
		process = ProcessStatement("proc", declaredItems=[first, last])
		process.IndexDeclaredItems()
		middle = _variable("b")

		process.InsertDeclaredItem(1, middle)

		self.assertListEqual([first, middle, last], process.DeclaredItems)
		self.assertIs(middle, process.Variables["b"])

	def test_InsertBefore(self) -> None:
		first = _variable("a")
		process = ProcessStatement("proc", declaredItems=[first])
		before = _constant("C")

		process.InsertDeclaredItemBefore(before, first)

		self.assertListEqual([before, first], process.DeclaredItems)

	def test_InsertAfter(self) -> None:
		first = _variable("a")
		last = _variable("c")
		process = ProcessStatement("proc", declaredItems=[first, last])
		middle = _variable("b")

		process.InsertDeclaredItemAfter(middle, first)

		self.assertListEqual([first, middle, last], process.DeclaredItems)

	def test_Remove(self) -> None:
		variable = _variable("v", "w")
		constant = _constant("C")
		process = ProcessStatement("proc", declaredItems=[variable, constant])
		process.IndexDeclaredItems()

		process.RemoveDeclaredItem(variable)

		self.assertListEqual([constant], process.DeclaredItems)
		self.assertIsNone(variable.Parent)
		self.assertDictEqual({}, process.Variables)
		self.assertDictEqual({"c": constant}, process._namespace._elements)

	def test_Remove_NotIndexed(self) -> None:
		"""A region not indexed yet has no namespace entry to remove."""
		variable = _variable("v")
		constant = _constant("C")
		process = ProcessStatement("proc", declaredItems=[variable, constant])

		process.RemoveDeclaredItem(variable)

		self.assertListEqual([constant], process.DeclaredItems)
		self.assertIsNone(variable.Parent)
		self.assertDictEqual({}, process.Variables)
		self.assertDictEqual({}, process._namespace._elements)

	def test_Remove_ParsedDuplicate_Shadowed(self) -> None:
		"""A declaration shadowed by a duplicate declaration read by a parser isn't in the namespace: it stays attached."""
		variable1 = _variable("v")
		variable2 = _variable("v")
		process = ProcessStatement("proc", declaredItems=[variable1, variable2])
		with WarningCollector():
			process.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			process.RemoveDeclaredItem(variable1)

		self.assertEqual("Namespace 'proc' has another element for 'v'.", str(context.exception))
		self.assertListEqual(["Found element of type 'pyVHDLModel.Object.Variable'."], context.exception.__notes__)
		self.assertEqual("v", context.exception.Identifier)
		self.assertIs(process._namespace, context.exception.Namespace)
		self.assertListEqual([variable1, variable2], process.DeclaredItems)
		self.assertIs(process, variable1.Parent)
		self.assertDictEqual({"v": variable2}, process.Variables)
		self.assertDictEqual({"v": variable2}, process._namespace._elements)

	def test_Remove_Overload(self) -> None:
		overload1 = _procedure("p")
		overload2 = _procedure("p")
		process = ProcessStatement("proc", declaredItems=[overload1, overload2])
		process.IndexDeclaredItems()

		process.RemoveDeclaredItem(overload2)

		self.assertDictEqual({"p": [overload1]}, process.Procedures)
		self.assertIs(overload1, process._namespace._elements["p"])

	def test_Remove_NotAChild(self) -> None:
		process = ProcessStatement("proc")
		variable = _variable("v")

		with self.assertRaises(NotAChildError) as context:
			process.RemoveDeclaredItem(variable)

		self.assertEqual("Variable 'v' is not a declared item of this ProcessStatement.", str(context.exception))
		self.assertIs(variable, context.exception.Element)
		self.assertIs(process, context.exception.Parent)
