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
"""
Implicit operations in namespaces: indexed by the analysis after the type marks are resolved, imported by use clauses.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design
from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.DesignUnit import Entity, Package
from pyVHDLModel.Exception  import LibraryNotFoundError
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Type       import IntegerType, Subtype

from tests.unit             import _subtypeSymbol
from tests.unit.Visibility  import _constant, _design, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _integerType(identifier: str) -> IntegerType:
	"""An integer type ``range 0 to 9``."""
	return IntegerType(identifier, SimpleRange(IntegerLiteral(0), IntegerLiteral(9), Direction.To))


def _operationsOf(fullType: IntegerType, designator: str) -> list:
	"""The implicit operations of a type with one designator."""
	return [operation for operation in fullType.ImplicitOperations if operation.NormalizedDesignator == designator]


class Declared(Testcase):
	"""The implicit operations of a type declared in a package."""

	def setUp(self) -> None:
		self._type =    _integerType("I")
		self._package = Package("p", declaredItems=[self._type])
		self._design =  _design(self._package)

	def test_Namespace(self) -> None:
		"""The analysis indexes the operations in the namespace of the type's region."""
		self.assertListEqual(_operationsOf(self._type, "+"), self._package._namespace.ImplicitOperations["+"])

	def test_Lookup(self) -> None:
		"""A lookup in the package finds the type's operations."""
		declarations = self._package._namespace.Lookup("+").Declarations

		for operation in _operationsOf(self._type, "+"):
			self.assertIn(operation, declarations)

	def test_Reset(self) -> None:
		"""Resetting the analysis removes the operations; the next analysis creates them again."""
		operations = self._type.ImplicitOperations

		self._design.ResetAnalysis()

		self.assertDictEqual({}, self._package._namespace.ImplicitOperations)
		self.assertIsNone(self._type._implicitOperations)

		self._design.Analyze()

		self.assertIsNot(operations, self._type.ImplicitOperations)
		self.assertListEqual(_operationsOf(self._type, "+"), self._package._namespace.ImplicitOperations["+"])

	def test_RemoveType(self) -> None:
		"""Removing the type removes its operations from the namespace."""
		self._package.RemoveDeclaredItem(self._type)

		for operations in self._package._namespace.ImplicitOperations.values():
			for operation in operations:
				self.assertIsNot(self._type, operation.Parent)


class NotAnalyzed(Testcase):
	def test_Indexed(self) -> None:
		"""Indexing the declared items adds no operations: they wait for the type marks to be resolved."""
		package = Package("p", declaredItems=[_integerType("I")])
		package.IndexDeclaredItems()

		self.assertDictEqual({}, package._namespace.ImplicitOperations)


class Imported(Testcase):
	"""The implicit operations a use clause imports with a type (IEEE Std 1076-2008, 12.4)."""

	def _lookup(self, *useClause: str) -> tuple:
		self._type = _integerType("I")
		package =    Package("p", declaredItems=[self._type, Subtype("S", _subtypeSymbol("I")), _constant("K", "I")])
		entity =     Entity("e", [_use(*useClause)])
		_design(package, entity)

		return entity._namespace.Lookup("+").Declarations

	def test_UseAll(self) -> None:
		declarations = self._lookup("work.p.all")

		for operation in _operationsOf(self._type, "+"):
			self.assertIn(operation, declarations)

	def test_UseType(self) -> None:
		declarations = self._lookup("work.p.I")

		for operation in _operationsOf(self._type, "+"):
			self.assertIn(operation, declarations)

	def test_UseSubtype(self) -> None:
		"""A use clause naming a subtype imports the operations of its base type."""
		declarations = self._lookup("work.p.S")

		for operation in _operationsOf(self._type, "+"):
			self.assertIn(operation, declarations)

	def test_UseConstant(self) -> None:
		"""A use clause naming another member imports no operations of the type."""
		declarations = self._lookup("work.p.K")

		for declaration in declarations:
			self.assertIsNot(self._type, declaration.Parent)


class Standard(Testcase):
	def test_ImplicitUse(self) -> None:
		"""The implicit ``use std.standard.all;`` imports the operations of its types, e.g. ``"and"`` of ``bit``."""
		entity = Entity("e")
		design = _design(entity)
		bit =    design.Libraries["std"].Packages["standard"].Types["bit"]

		declarations = entity._namespace.Lookup("and").Declarations

		for operation in _operationsOf(bit, "and"):
			self.assertIn(operation, declarations)

	def test_BitVector(self) -> None:
		"""``bit_vector`` declares ``"and"`` (4 forms) once ``bit`` is resolved; a user entity finds them."""
		entity =     Entity("e")
		design =     _design(entity)
		bitVector =  design.Libraries["std"].Packages["standard"].Types["bit_vector"]
		operations = _operationsOf(bitVector, "and")

		self.assertEqual(4, len(operations))

		declarations = entity._namespace.Lookup("and").Declarations

		for operation in operations:
			self.assertIn(operation, declarations)


class PredefinedTypeMarks(Testcase):
	"""The type marks naming ``BOOLEAN``, ``INTEGER`` or ``STRING`` reference the types of ``std.standard`` (9.2)."""

	def test_Boolean(self) -> None:
		"""``"="`` of a user-defined integer type returns ``std.standard.BOOLEAN``."""
		integerType = _integerType("I")
		design =      _design(Package("p", declaredItems=[integerType]))
		boolean =     design.Libraries["std"].Packages["standard"].Types["boolean"]

		for operation in _operationsOf(integerType, "="):
			self.assertIs(boolean, operation.ReturnType.Reference)

	def test_IntegerAndString(self) -> None:
		"""``"**"`` takes ``INTEGER``, ``TO_STRING`` returns ``STRING``; the marks of the type itself stay."""
		integerType = _integerType("I")
		design =      _design(Package("p", declaredItems=[integerType]))
		standard =    design.Libraries["std"].Packages["standard"]
		power =       _operationsOf(integerType, "**")[0]

		self.assertIs(integerType, power.ParameterItems[0].Subtype.Reference)
		self.assertIs(standard.Types["integer"], power.ParameterItems[1].Subtype.Reference)
		self.assertIs(standard.Types["string"], _operationsOf(integerType, "to_string")[0].ReturnType.Reference)

	def test_LocalBoolean(self) -> None:
		"""A type ``boolean`` declared beside the type doesn't capture the type marks of its implicit operations."""
		localBoolean = _integerType("boolean")
		integerType =  _integerType("I")
		design =       _design(Package("p", declaredItems=[localBoolean, integerType]))
		boolean =      design.Libraries["std"].Packages["standard"].Types["boolean"]

		for operation in _operationsOf(integerType, "/="):
			self.assertIs(boolean, operation.ReturnType.Reference)
			self.assertIsNot(localBoolean, operation.ReturnType.Reference)

	def test_Standard(self) -> None:
		"""Every type mark of the implicit operations of the types of ``std.standard`` and ``ieee`` is resolved."""
		design = _design(Package("p"))

		for library in (design.Libraries["std"], design.Libraries["ieee"]):
			for package in library.Packages.values():
				for fullType in package.Types.values():
					for operation in fullType.ImplicitOperations:
						for item in operation.ParameterItems:
							self.assertIsNotNone(item.Subtype.Reference, f"{package.Identifier}.{operation}")

						self.assertIsNotNone(operation.ReturnType.Reference, f"{package.Identifier}.{operation}")

	def test_NoStdLibrary(self) -> None:
		"""Indexing the implicit operations needs library ``std``."""
		with self.assertRaises(LibraryNotFoundError) as context:
			Design("design").IndexImplicitOperations()

		self.assertEqual("Library 'std' not found in design.", str(context.exception))
		self.assertListEqual(["Call 'LoadStdLibrary()' before analyzing a design."], context.exception.__notes__)
