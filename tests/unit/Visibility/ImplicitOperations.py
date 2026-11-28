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
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import Design, VHDLVersion
from pyVHDLModel.Base       import Direction, Mode, SimpleRange
from pyVHDLModel.DesignUnit import DesignUnit, Entity, LibraryClause, Package
from pyVHDLModel.Exception  import LibraryNotFoundError, UnresolvedTypeMarkWarning
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Subprogram import Operator
from pyVHDLModel.Symbol     import LibraryReferenceSymbol
from pyVHDLModel.Type       import IntegerType, Subtype

from tests.unit             import _subtypeSymbol, _warningsOfType
from tests.unit.Visibility  import _constant, _design, _distance, _use


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

	def test_ToString(self) -> None:
		"""A user entity finds ``TO_STRING`` of ``real`` with ``DIGITS`` and ``TO_HSTRING`` of ``bit_vector``."""
		entity =   Entity("e")
		design =   _design(entity)
		standard = design.Libraries["std"].Packages["standard"]

		self.assertIn(
			_operationsOf(standard.Types["real"], "to_string")[1],
			entity._namespace.Lookup("to_string").Declarations
		)
		self.assertIn(
			_operationsOf(standard.Types["bit_vector"], "to_hstring")[0],
			entity._namespace.Lookup("to_hstring").Declarations
		)


class Universal(Testcase):
	"""
	The operations of the anonymous types *universal_integer* and *universal_real* of ``std.standard`` (16.3).

	A use clause imports them; no name denotes the types (IEEE Std 1076-2008, 5.2.3.1, 5.2.5.1).
	"""

	def setUp(self) -> None:
		self._entity =         Entity("e")
		self._design =         _design(self._entity)
		self._standard =       self._design.Libraries["std"].Packages["standard"]
		self._anonymousTypes = self._standard.AnonymousTypes

	def test_Namespace(self) -> None:
		"""The analysis indexes the operations in the namespace of ``std.standard``; none is hidden."""
		namespace = self._standard._namespace

		for anonymousType in self._anonymousTypes.values():
			for operation in anonymousType.ImplicitOperations:
				self.assertIn(operation, namespace.ImplicitOperations[operation.NormalizedDesignator])

		self.assertSetEqual(set(), namespace.HiddenOperations)

	def test_ImplicitUse(self) -> None:
		"""A user entity finds ``"*"`` of *universal_real* and *universal_integer*, and ``TO_STRING`` of both."""
		multiplications = self._entity._namespace.Lookup("*").Declarations
		toStrings =       self._entity._namespace.Lookup("to_string").Declarations

		for operation in _operationsOf(self._anonymousTypes["universal_real"], "*"):
			self.assertIn(operation, multiplications)

		for anonymousType in self._anonymousTypes.values():
			self.assertIn(_operationsOf(anonymousType, "to_string")[0], toStrings)

	def test_UseAll(self) -> None:
		"""An explicit ``use std.standard.all;`` imports them too."""
		library = LibraryClause([LibraryReferenceSymbol(SimpleName("std"))])
		entity =  Entity("e2", [library, _use("std.standard.all")])
		design =  _design(entity)
		real =    design.Libraries["std"].Packages["standard"].AnonymousTypes["universal_real"]

		self.assertIn(_operationsOf(real, "/")[-1], entity._namespace.Lookup("/").Declarations)

	def test_NotVisibleByName(self) -> None:
		"""Neither a user entity nor ``std.standard`` finds a declaration of the pseudo-names."""
		for identifier in self._anonymousTypes:
			self.assertTupleEqual((), self._entity._namespace.Lookup(identifier).Declarations)
			self.assertTupleEqual((), self._standard._namespace.Lookup(identifier).Declarations)

	def test_UnresolvedTypeMark(self) -> None:
		"""A type mark ``universal_integer`` in a user package is reported."""
		constant = _constant("c", "universal_integer")
		design =   _design(Package("p", declaredItems=[constant]), analyze=False)
		with WarningCollector() as collector:
			design.Analyze()

		warnings = _warningsOfType(collector, UnresolvedTypeMarkWarning)
		self.assertEqual(1, len(warnings))
		self.assertIs(constant.Subtype, warnings[0].Symbol)

	def test_PhysicalType(self) -> None:
		"""``"/"`` of two values of a user-defined physical type returns *universal_integer* (9.2.7)."""
		distance =         _distance()
		design =           _design(Package("p", declaredItems=[distance]))
		universalInteger = design.Libraries["std"].Packages["standard"].AnonymousTypes["universal_integer"]
		division =         _operationsOf(distance, "/")[-1]

		self.assertIs(universalInteger, division.ReturnType.Reference)
		for item in division.ParameterItems:
			self.assertIs(distance, item.Subtype.Reference)

	def test_Reset(self) -> None:
		"""Resetting the analysis removes the operations from the namespace; the next analysis adds the same again."""
		universalInteger = self._anonymousTypes["universal_integer"]
		operations =       universalInteger.ImplicitOperations

		self._design.ResetAnalysis()

		self.assertNotIn("+", self._standard._namespace.ImplicitOperations)

		self._design.Analyze()

		self.assertIs(operations, universalInteger.ImplicitOperations)
		self.assertIn(operations[9], self._standard._namespace.ImplicitOperations["+"])


class PredefinedTypeMarks(Testcase):
	"""
	The type marks naming ``BOOLEAN``, ``INTEGER`` or ``STRING`` reference the types of ``std.standard`` (9.2), the one
	naming ``NATURAL`` its subtype (16.3).
	"""

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

	def test_Standard_VITAL(self) -> None:
		"""
		The analysis of ``std``, ``ieee`` and the VITAL packages raises no warning and resolves every type mark of the
		implicit operations; no operation of ``std.standard`` is hidden.
		"""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		design.LoadVITALPackages()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		for library in design.Libraries.values():
			for package in library.Packages.values():
				for fullType in package.Types.values():
					for operation in fullType.ImplicitOperations:
						for item in operation.ParameterItems:
							self.assertIsNotNone(item.Subtype.Reference, f"{package.Identifier}.{operation}")

						self.assertIsNotNone(operation.ReturnType.Reference, f"{package.Identifier}.{operation}")

		self.assertSetEqual(set(), design.Libraries["std"].Packages["standard"]._namespace.HiddenOperations)

	def test_Standard_VITAL_VHDL2019(self) -> None:
		"""
		The same with VHDL-2019: no warning, every type mark resolved; no operation of ``std.standard`` and ``std.env`` is
		hidden, ``ieee.numeric_std`` hides 20 as with VHDL-2008.
		"""
		design = Design("design")
		design.LoadStdLibrary(VHDLVersion.VHDL2019)
		design.LoadIEEELibrary(VHDLVersion.VHDL2019)
		design.LoadVITALPackages()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		for library in design.Libraries.values():
			for package in library.Packages.values():
				for fullType in package.Types.values():
					for operation in fullType.ImplicitOperations:
						for item in operation.ParameterItems:
							self.assertIsNotNone(item.Subtype.Reference, f"{package.Identifier}.{operation}")

						self.assertIsNotNone(operation.ReturnType.Reference, f"{package.Identifier}.{operation}")

		for identifier in ("standard", "env"):
			self.assertSetEqual(set(), design.Libraries["std"].Packages[identifier]._namespace.HiddenOperations)

		self.assertEqual(20, len(design.Libraries["ieee"].Packages["numeric_std"]._namespace.HiddenOperations))

	def test_Natural(self) -> None:
		"""``TO_STRING`` of ``REAL`` takes ``DIGITS`` of subtype ``NATURAL``, ``FORMAT`` of type ``STRING``."""
		design =     _design(Package("p"))
		standard =   design.Libraries["std"].Packages["standard"]
		toStrings =  _operationsOf(standard.Types["real"], "to_string")
		withDigits = toStrings[1]
		withFormat = toStrings[2]

		self.assertIs(standard.Subtypes["natural"], withDigits.ParameterItems[1].Subtype.Reference)
		self.assertIs(standard.Types["string"], withFormat.ParameterItems[1].Subtype.Reference)

	def test_NoStdLibrary(self) -> None:
		"""Indexing the implicit operations needs library ``std``."""
		with self.assertRaises(LibraryNotFoundError) as context:
			Design("design").IndexImplicitOperations()

		self.assertEqual("Library 'std' not found in design.", str(context.exception))
		self.assertListEqual(["Call 'LoadStdLibrary()' before analyzing a design."], context.exception.__notes__)


class Hidden(Testcase):
	"""An explicitly declared homograph hides the implicit operation in the type's region (IEEE Std 1076-2008, 12.3)."""

	def _analyze(self, left: str, right: str, *designUnits: DesignUnit) -> None:
		parameters = [
			ParameterConstantInterfaceItem(("L", ), Mode.In, _subtypeSymbol(left)),
			ParameterConstantInterfaceItem(("R", ), Mode.In, _subtypeSymbol(right))
		]
		self._type =     _integerType("I")
		self._equality = Operator("=", _subtypeSymbol("boolean"), parameterItems=parameters)
		self._package =  Package("p", declaredItems=[self._type, Subtype("S", _subtypeSymbol("I")), self._equality])
		_design(self._package, *designUnits)

	def test_Hidden(self) -> None:
		"""The implicit ``"="`` of ``I`` is hidden; a lookup finds the explicit one only."""
		self._analyze("I", "I")
		namespace = self._package._namespace
		implicit =  _operationsOf(self._type, "=")[0]

		self.assertSetEqual({implicit}, namespace.HiddenOperations)
		self.assertNotIn(implicit, namespace.ImplicitOperations.get("=", ()))
		self.assertIn(self._equality, namespace.Lookup("=").Declarations)
		self.assertNotIn(implicit, namespace.Lookup("=").Declarations)

	def test_Subtype(self) -> None:
		"""Parameters of a subtype of ``I`` have the base type ``I``: the same profile."""
		self._analyze("S", "I")

		self.assertSetEqual(set(_operationsOf(self._type, "=")), self._package._namespace.HiddenOperations)

	def test_OtherProfile(self) -> None:
		"""An explicit ``"="`` of another parameter type profile hides nothing."""
		self._analyze("I", "integer")
		declarations = self._package._namespace.Lookup("=").Declarations

		self.assertSetEqual(set(), self._package._namespace.HiddenOperations)
		self.assertIn(self._equality, declarations)
		self.assertIn(_operationsOf(self._type, "=")[0], declarations)

	def test_OtherDesignator(self) -> None:
		"""The implicit ``"/="`` stays visible."""
		self._analyze("I", "I")

		self.assertIn(_operationsOf(self._type, "/=")[0], self._package._namespace.Lookup("/=").Declarations)

	def test_Imported(self) -> None:
		"""A use clause imports the explicit ``"="``, but not the hidden implicit one."""
		entity = Entity("e", [_use("work.p.all")])
		self._analyze("I", "I", entity)
		declarations = entity._namespace.Lookup("=").Declarations

		self.assertIn(self._equality, declarations)
		self.assertNotIn(_operationsOf(self._type, "=")[0], declarations)

	def test_Reset(self) -> None:
		"""Resetting the analysis forgets the hidden operations; the next analysis finds them again."""
		self._analyze("I", "I")
		design = self._package.Library._parent

		design.ResetAnalysis()

		self.assertSetEqual(set(), self._package._namespace.HiddenOperations)

		design.Analyze()

		self.assertSetEqual(set(_operationsOf(self._type, "=")), self._package._namespace.HiddenOperations)

	def test_NumericStd(self) -> None:
		"""``ieee.numeric_std`` declares ``"="`` of ``unresolved_unsigned``: the implicit one isn't imported."""
		library =    LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])
		entity =     Entity("e", [library, _use("ieee.numeric_std.all")])
		design =     _design(entity)
		numericStd = design.Libraries["ieee"].Packages["numeric_std"]
		unsigned =   numericStd.Types["unresolved_unsigned"]
		implicit =   [operation for operation in unsigned.ImplicitOperations if operation.NormalizedDesignator == "="]

		self.assertEqual(1, len(implicit))
		self.assertIn(implicit[0], numericStd._namespace.HiddenOperations)
		self.assertNotIn(implicit[0], entity._namespace.Lookup("=").Declarations)
