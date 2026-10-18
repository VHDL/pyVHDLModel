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
Mutation tests for the declared items of protected type declarations
(:class:`~pyVHDLModel.Regions.ProtectedTypeDeclarationRegionMixin`).
"""
from pyTooling.Testing     import Testcase

from pyVHDLModel.Exception import AlreadyInDesignError, NotAChildError
from pyVHDLModel.Type      import ProtectedType

from tests.unit.Mutation   import _constant, _function, _procedure


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ProtectedTypeDeclaredItems(Testcase):
	def test_Add(self) -> None:
		protectedType = ProtectedType("counter")
		protectedType.IndexDeclaredItems()
		function = _function("get")
		procedure = _procedure("increment")

		protectedType.AddDeclaredItem(function)
		protectedType.AddDeclaredItem(procedure)

		self.assertListEqual([function, procedure], protectedType.Methods)
		self.assertIs(protectedType, function.Parent)
		self.assertDictEqual({"get": [function]}, protectedType.Functions)
		self.assertDictEqual({"increment": [procedure]}, protectedType.Procedures)
		self.assertDictEqual({"get": function, "increment": procedure}, protectedType._namespace._elements)
		self.assertIs(protectedType._namespace, procedure._namespace.ParentNamespace)

	def test_Add_Overloads(self) -> None:
		protectedType = ProtectedType("counter")
		protectedType.IndexDeclaredItems()
		overload1 = _procedure("increment")
		overload2 = _procedure("increment")

		protectedType.AddDeclaredItem(overload1)
		protectedType.AddDeclaredItem(overload2)

		self.assertDictEqual({"increment": [overload1, overload2]}, protectedType.Procedures)
		self.assertIs(overload2, protectedType._namespace._elements["increment"])

	def test_Add_WrongType(self) -> None:
		protectedType = ProtectedType("counter")

		with self.assertRaises(TypeError) as context:
			protectedType.AddDeclaredItem(_constant("C"))

		self.assertEqual("Parameter 'declaredItem' is not a declaration allowed in ProtectedType.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Object.Constant'."], context.exception.__notes__)

	def test_Add_AlreadyInDesign(self) -> None:
		procedure = _procedure("increment")
		ProtectedType("counter1", [procedure])
		protectedType = ProtectedType("counter2")

		with self.assertRaises(AlreadyInDesignError) as context:
			protectedType.AddDeclaredItem(procedure)

		self.assertEqual("Procedure 'increment' already has a parent.", str(context.exception))

	def test_Insert_Start(self) -> None:
		procedure = _procedure("increment")
		protectedType = ProtectedType("counter", [procedure])
		function = _function("get")

		protectedType.InsertDeclaredItem(0, function)

		self.assertListEqual([function, procedure], protectedType.DeclaredItems)

	def test_InsertBefore(self) -> None:
		procedure = _procedure("increment")
		protectedType = ProtectedType("counter", [procedure])
		function = _function("get")

		protectedType.InsertDeclaredItemBefore(function, procedure)

		self.assertListEqual([function, procedure], protectedType.DeclaredItems)

	def test_Remove(self) -> None:
		function = _function("get")
		procedure = _procedure("increment")
		protectedType = ProtectedType("counter", [function, procedure])
		protectedType.IndexDeclaredItems()

		protectedType.RemoveDeclaredItem(procedure)

		self.assertListEqual([function], protectedType.Methods)
		self.assertIsNone(procedure.Parent)
		self.assertDictEqual({}, protectedType.Procedures)
		self.assertDictEqual({"get": function}, protectedType._namespace._elements)

	def test_Remove_NotAChild(self) -> None:
		protectedType = ProtectedType("counter")

		with self.assertRaises(NotAChildError) as context:
			protectedType.RemoveDeclaredItem(_function("get"))

		self.assertEqual("Function 'get' is not a declared item of this ProtectedType.", str(context.exception))
