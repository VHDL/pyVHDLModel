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
Mutation tests for the context items of design units (:class:`~pyVHDLModel.DesignUnit.DesignUnit`).

A context item is a library clause, a use clause or a context reference. Besides the list of all context items in
declaration order, a design unit keeps one list per kind, in the same order.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.DesignUnit import Context, ContextReference, Entity, LibraryClause, UseClause
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError
from pyVHDLModel.IEEE       import Numeric_Std
from pyVHDLModel.Name       import AllName, SelectedName, SimpleName
from pyVHDLModel.Symbol     import AllPackageMembersReferenceSymbol, ContextReferenceSymbol, LibraryReferenceSymbol

from tests.unit.Mutation    import _signal


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _library(name: str) -> LibraryClause:
	return LibraryClause([LibraryReferenceSymbol(SimpleName(name))])


def _use(library: str, package: str) -> UseClause:
	return UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName(package, SimpleName(library))))])


def _context(library: str, context: str) -> ContextReference:
	return ContextReference([ContextReferenceSymbol(SelectedName(context, SimpleName(library)))])


class ContextItems(Testcase):
	def test_Add(self) -> None:
		entity = Entity("e")
		library = _library("ieee")
		use = _use("ieee", "std_logic_1164")
		context = _context("ieee", "ieee_std_context")

		entity.AddContextItem(library)
		entity.AddContextItem(use)
		entity.AddContextItem(context)

		self.assertListEqual([library, use, context], entity.ContextItems)
		self.assertListEqual([library], entity.LibraryReferences)
		self.assertListEqual([use], entity.PackageReferences)
		self.assertListEqual([context], entity.ContextReferences)
		self.assertIs(entity, library.Parent)
		self.assertIs(entity, use.Parent)
		self.assertIs(entity, context.Parent)

	def test_Add_Context(self) -> None:
		"""The context items of a context declaration are the clauses it declares."""
		existing = _library("ieee")
		context = Context("ctx", [existing])
		use = _use("ieee", "numeric_std")

		context.AddContextItem(use)

		self.assertListEqual([existing, use], context.ContextItems)
		self.assertListEqual([existing], context.LibraryReferences)
		self.assertListEqual([use], context.PackageReferences)
		self.assertIs(context, use.Parent)

	def test_Add_Repeated(self) -> None:
		"""A context clause may repeat a library clause or a use clause."""
		entity = Entity("e", [_library("ieee"), _use("ieee", "std_logic_1164")])
		library = _library("ieee")
		use = _use("ieee", "std_logic_1164")

		entity.AddContextItem(library)
		entity.AddContextItem(use)

		self.assertEqual(4, len(entity.ContextItems))
		self.assertIs(library, entity.LibraryReferences[1])
		self.assertIs(use, entity.PackageReferences[1])

	def test_Add_None(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.AddContextItem(None)

		self.assertEqual("Parameter 'contextItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.AddContextItem(_signal("s"))

		self.assertEqual(
			"Parameter 'contextItem' is not of type 'LibraryClause', 'UseClause' or 'ContextReference'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)

	def test_Add_AlreadyInDesign(self) -> None:
		library = _library("ieee")
		first = Entity("first", [library])
		entity = Entity("e")

		with self.assertRaises(AlreadyInDesignError) as context:
			entity.AddContextItem(library)

		self.assertEqual("LibraryClause already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Entity first."], context.exception.__notes__)
		self.assertIs(library, context.exception.Element)
		self.assertIs(first, context.exception.Parent)
		self.assertListEqual([], entity.ContextItems)
		self.assertListEqual([], entity.LibraryReferences)

	def test_Insert_Start(self) -> None:
		library = _library("ieee")
		use = _use("ieee", "std_logic_1164")
		entity = Entity("e", [library, use])
		std = _library("std")

		entity.InsertContextItem(0, std)

		self.assertListEqual([std, library, use], entity.ContextItems)
		self.assertListEqual([std, library], entity.LibraryReferences)
		self.assertIs(entity, std.Parent)

	def test_Insert_Middle(self) -> None:
		ieee = _library("ieee")
		logic = _use("ieee", "std_logic_1164")
		osvvm = _library("osvvm")
		common = _use("osvvm", "OsvvmCommonPkg")
		entity = Entity("e", [ieee, logic, osvvm, common])
		numeric = _use("ieee", "numeric_std")

		entity.InsertContextItem(2, numeric)

		self.assertListEqual([ieee, logic, numeric, osvvm, common], entity.ContextItems)
		self.assertListEqual([logic, numeric, common], entity.PackageReferences)
		self.assertListEqual([ieee, osvvm], entity.LibraryReferences)

	def test_Insert_End(self) -> None:
		library = _library("ieee")
		entity = Entity("e", [library])
		use = _use("ieee", "std_logic_1164")

		entity.InsertContextItem(1, use)

		self.assertListEqual([library, use], entity.ContextItems)
		self.assertListEqual([use], entity.PackageReferences)

	def test_Insert_Negative(self) -> None:
		ieee = _library("ieee")
		first = _use("ieee", "std_logic_1164")
		second = _use("ieee", "numeric_std")
		entity = Entity("e", [ieee, first, second])
		context = _context("ieee", "ieee_std_context")

		entity.InsertContextItem(-1, context)

		self.assertListEqual([ieee, first, context, second], entity.ContextItems)
		self.assertListEqual([context], entity.ContextReferences)
		self.assertListEqual([first, second], entity.PackageReferences)

	def test_Insert_Negative_Use(self) -> None:
		ieee = _library("ieee")
		first = _use("ieee", "std_logic_1164")
		second = _use("ieee", "numeric_std")
		entity = Entity("e", [ieee, first, second])
		middle = _use("ieee", "math_real")

		entity.InsertContextItem(-1, middle)

		self.assertListEqual([ieee, first, middle, second], entity.ContextItems)
		self.assertListEqual([first, middle, second], entity.PackageReferences)

	def test_Insert_IndexNone(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.InsertContextItem(None, _library("ieee"))

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Insert_IndexWrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.InsertContextItem(1.0, _library("ieee"))

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'float'."], context.exception.__notes__)

	def test_Insert_OutOfRange(self) -> None:
		entity = Entity("e", [_library("ieee")])
		library = _library("std")

		with self.assertRaises(ValueError) as context:
			entity.InsertContextItem(2, library)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)
		self.assertIsNone(library.Parent)

	def test_Insert_Negative_OutOfRange(self) -> None:
		entity = Entity("e", [_library("ieee")])
		library = _library("std")

		with self.assertRaises(ValueError) as context:
			entity.InsertContextItem(-2, library)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertIsNone(library.Parent)

	def test_Remove(self) -> None:
		library = _library("ieee")
		first = _use("ieee", "std_logic_1164")
		second = _use("ieee", "numeric_std")
		entity = Entity("e", [library, first, second])

		entity.RemoveContextItem(first)

		self.assertListEqual([library, second], entity.ContextItems)
		self.assertListEqual([second], entity.PackageReferences)
		self.assertListEqual([library], entity.LibraryReferences)
		self.assertIsNone(first.Parent)

	def test_Remove_Context(self) -> None:
		library = _library("ieee")
		context = Context("ctx", [library])

		context.RemoveContextItem(library)

		self.assertListEqual([], context.ContextItems)
		self.assertListEqual([], context.LibraryReferences)
		self.assertIsNone(library.Parent)

	def test_Remove_Reinsert(self) -> None:
		"""A removed context item can be inserted again, e.g. at another position or into another design unit."""
		library = _library("ieee")
		use = _use("ieee", "std_logic_1164")
		entity = Entity("e", [library, use])
		other = Entity("other")

		entity.RemoveContextItem(library)
		other.AddContextItem(library)

		self.assertListEqual([use], entity.ContextItems)
		self.assertListEqual([], entity.LibraryReferences)
		self.assertListEqual([library], other.ContextItems)
		self.assertListEqual([library], other.LibraryReferences)
		self.assertIs(other, library.Parent)

	def test_Remove_None(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.RemoveContextItem(None)

		self.assertEqual("Parameter 'contextItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.RemoveContextItem(_signal("s"))

		self.assertEqual(
			"Parameter 'contextItem' is not of type 'LibraryClause', 'UseClause' or 'ContextReference'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)

	def test_Remove_NotAChild(self) -> None:
		entity = Entity("e")
		use = _use("ieee", "std_logic_1164")

		with self.assertRaises(NotAChildError) as context:
			entity.RemoveContextItem(use)

		self.assertEqual("UseClause is not a context item of this Entity.", str(context.exception))
		self.assertIs(use, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)


class PredefinedContextItems(Testcase):
	def test_Package(self) -> None:
		"""A predefined package adds its context items with :meth:`~pyVHDLModel.DesignUnit.DesignUnit.AddContextItem`."""
		package = Numeric_Std()

		self.assertEqual(len(package.LibraryReferences) + len(package.PackageReferences), len(package.ContextItems))
		for item in package.ContextItems:
			self.assertIs(package, item.Parent)
