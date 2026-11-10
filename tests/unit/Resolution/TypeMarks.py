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
Type marks (IEEE Std 1076-2008, 6.3): the places of type marks, the forms of names, incomplete types and diagnostics.
"""
from pathlib                 import Path

from pyTooling.Testing       import Testcase
from pyTooling.Warning       import UnhandledCriticalWarningError

from pyVHDLModel             import Design, Document
from pyVHDLModel.Base        import Mode
from pyVHDLModel.Concurrent  import ProcessStatement
from pyVHDLModel.Declaration import Alias, Attribute
from pyVHDLModel.DesignUnit  import Architecture, Component, Entity, LibraryClause, Package, PackageBody
from pyVHDLModel.Exception   import DuplicateDeclarationWarning, IncompleteTypeWarning, UnresolvedNameWarning, \
                                    UnresolvedTypeMarkWarning
from pyVHDLModel.Interface   import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                    ParameterConstantInterfaceItem, PortSimpleSignalInterfaceItem
from pyVHDLModel.Name        import SelectedName, SimpleName
from pyVHDLModel.Object      import Constant, Variable
from pyVHDLModel.Subprogram  import Function, Procedure
from pyVHDLModel.Symbol      import LibraryReferenceSymbol, SimpleObjectOrFunctionCallSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Type        import AccessType, AnonymousType, ArrayType, FileType, ProtectedType, RecordType, \
                                    RecordTypeElement, Subtype

from tests.unit              import _entitySymbol, _signal, _subtypeSymbol
from tests.unit.Resolution   import _resolve
from tests.unit.Visibility   import _constant, _design, _enumeration, _packageSymbol, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _selectedSubtypeSymbol(*identifiers: str) -> SimpleSubtypeSymbol:
	"""A type mark by an expanded name, e.g. ``work.p.T``."""
	name = SimpleName(identifiers[0])
	for identifier in identifiers[1:]:
		name = SelectedName(identifier, name)

	return SimpleSubtypeSymbol(name)


class Places(Testcase):
	"""Every kind of declaration resolves its type marks."""

	def setUp(self) -> None:
		self._type =    _enumeration("T", "a", "b")
		self._package = Package("p", declaredItems=[self._type])

	def _architecture(self, *declaredItems, statements=()) -> Architecture:
		"""An architecture using ``work.p.all`` with the declared items; the design is analyzed and resolved."""
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p.all")], declaredItems, statements)
		self.assertListEqual([], _resolve(_design(self._package, Entity("e"), architecture, analyze=False)))
		return architecture

	def test_Objects(self) -> None:
		constant = _constant("c", "T")
		signal =   _signal("s", "T")
		self._architecture(constant, signal)

		self.assertIs(self._type, constant.Subtype.Reference)
		self.assertIs(self._type, signal.Subtype.Reference)

	def test_Variable_InProcess(self) -> None:
		variable = Variable(("v", ), _subtypeSymbol("T"))
		self._architecture(statements=[ProcessStatement("proc", declaredItems=[variable])])

		self.assertIs(self._type, variable.Subtype.Reference)

	def test_PortsAndGenerics(self) -> None:
		generic = GenericConstantInterfaceItem(("G", ), Mode.Default, _subtypeSymbol("T"))
		port =    PortSimpleSignalInterfaceItem(("i", ), Mode.In, _subtypeSymbol("T"))
		entity =  Entity("e", [_use("work.p.all")], [generic], [port])
		self.assertListEqual([], _resolve(_design(self._package, entity, analyze=False)))

		self.assertIs(self._type, generic.Subtype.Reference)
		self.assertIs(self._type, port.Subtype.Reference)

	def test_RecordElement(self) -> None:
		record = RecordType("R", [RecordTypeElement(("e1", ), _subtypeSymbol("T"))])
		self._architecture(record)

		self.assertIs(self._type, record.Elements[0].Subtype.Reference)

	def test_ArrayType(self) -> None:
		array = ArrayType("A", [_subtypeSymbol("T")], _subtypeSymbol("natural"))
		self._architecture(array)

		self.assertIs(self._type, array.Dimensions[0].Reference)
		self.assertEqual("natural", array.ElementType.Reference.Identifier)

	def test_AccessAndFileType(self) -> None:
		access = AccessType("AT", _subtypeSymbol("T"))
		file =   FileType("FT", _subtypeSymbol("T"))
		self._architecture(access, file)

		self.assertIs(self._type, access.DesignatedSubtype.Reference)
		self.assertIs(self._type, file.DesignatedSubtype.Reference)

	def test_Subtype_BaseType(self) -> None:
		"""A subtype of a subtype has the type as base type."""
		first =  Subtype("ST1", _subtypeSymbol("T"))
		second = Subtype("ST2", _subtypeSymbol("ST1"))
		self._architecture(first, second)

		self.assertIs(self._type, first.Type.Reference)
		self.assertIs(first, second.Type.Reference)
		self.assertIs(self._type, second.BaseType)

	def test_Subprogram(self) -> None:
		"""Parameter and return type marks."""
		parameter = ParameterConstantInterfaceItem(("x", ), Mode.In, _subtypeSymbol("T"))
		function =  Function("f", _subtypeSymbol("T"), parameterItems=[parameter])
		self._architecture(function)

		self.assertIs(self._type, function.ParameterItems[0].Subtype.Reference)
		self.assertIs(self._type, function.ReturnType.Reference)

	def test_Attribute(self) -> None:
		attribute = Attribute("att", _subtypeSymbol("T"))
		self._architecture(attribute)

		self.assertIs(self._type, attribute.Subtype.Reference)

	def test_Alias(self) -> None:
		"""Alias with a subtype indication, alias of a type as type mark."""
		constant =    _constant("c", "T")
		objectAlias = Alias("al", SimpleObjectOrFunctionCallSymbol(SimpleName("c")), _subtypeSymbol("T"))
		typeAlias =   Alias("AT", SimpleSubtypeSymbol(SimpleName("integer")))
		signal =      _signal("s", "AT")
		self._architecture(constant, objectAlias, typeAlias, signal)

		self.assertIs(self._type, objectAlias.Subtype.Reference)
		self.assertEqual("integer", typeAlias.Name.Reference.Identifier)
		self.assertIs(typeAlias.Name.Reference, signal.Subtype.Reference)

	def test_Component(self) -> None:
		port =         PortSimpleSignalInterfaceItem(("i", ), Mode.In, _subtypeSymbol("T"))
		component =    Component("comp", portItems=[port])
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p.all")], [component])
		self.assertListEqual([], _resolve(_design(self._package, Entity("e"), Entity("comp"), architecture, analyze=False)))

		self.assertIs(self._type, port.Subtype.Reference)

	def test_GenericType(self) -> None:
		"""A generic type is the target of a type mark."""
		genericType = GenericTypeInterfaceItem("GT")
		port =        PortSimpleSignalInterfaceItem(("i", ), Mode.In, _subtypeSymbol("GT"))
		entity =      Entity("e", genericItems=[genericType], portItems=[port])
		self.assertListEqual([], _resolve(_design(entity, analyze=False)))

		self.assertIs(genericType, port.Subtype.Reference)

	def test_ProtectedTypeMethod(self) -> None:
		"""A method's parameter sees the declarations around the protected type."""
		parameter = ParameterConstantInterfaceItem(("x", ), Mode.In, _subtypeSymbol("T"))
		method =    Procedure("set", parameterItems=[parameter])
		protected = ProtectedType("PT", [method])
		self._architecture(protected)

		self.assertIs(self._type, parameter.Subtype.Reference)

	def test_PackageBody(self) -> None:
		"""A package body sees the package declaration's types."""
		local =       _enumeration("LT", "x", "y")
		constant =    _constant("c", "LT")
		package =     Package("q", declaredItems=[local])
		packageBody = PackageBody(_packageSymbol("q"), declaredItems=[constant])
		self.assertListEqual([], _resolve(_design(package, packageBody, analyze=False)))

		self.assertIs(local, constant.Subtype.Reference)


class DeclarationTypeMarks(Testcase):
	"""Each declaration iterates its own type marks with the region and the place to look them up."""

	def setUp(self) -> None:
		self._region = Package("p")

	def test_Object(self) -> None:
		constant = _constant("c", "T")

		self.assertListEqual(
			[(self._region, constant, constant.Subtype)],
			list(constant.IterateTypeMarks(self._region))
		)

	def test_Subtype(self) -> None:
		subtype = Subtype("ST", _subtypeSymbol("T"))

		self.assertListEqual([(self._region, subtype, subtype.Type)], list(subtype.IterateTypeMarks(self._region)))

	def test_ArrayType(self) -> None:
		"""Index subtypes first, then the element subtype."""
		array = ArrayType("A", [_subtypeSymbol("I")], _subtypeSymbol("E"))

		self.assertListEqual(
			[(self._region, array, array.Dimensions[0]), (self._region, array, array.ElementType)],
			list(array.IterateTypeMarks(self._region))
		)

	def test_RecordType(self) -> None:
		record = RecordType("R", [
			RecordTypeElement(("e1", ), _subtypeSymbol("T")),
			RecordTypeElement(("e2", ), _subtypeSymbol("U"))
		])

		self.assertListEqual(
			[(self._region, record, record.Elements[0].Subtype), (self._region, record, record.Elements[1].Subtype)],
			list(record.IterateTypeMarks(self._region))
		)

	def test_AccessType(self) -> None:
		access = AccessType("AT", _subtypeSymbol("T"))

		self.assertListEqual(
			[(self._region, access, access.DesignatedSubtype)],
			list(access.IterateTypeMarks(self._region))
		)

	def test_FileType(self) -> None:
		file = FileType("FT", _subtypeSymbol("T"))

		self.assertListEqual(
			[(self._region, file, file.DesignatedSubtype)],
			list(file.IterateTypeMarks(self._region))
		)

	def test_Attribute(self) -> None:
		attribute = Attribute("att", _subtypeSymbol("T"))

		self.assertListEqual(
			[(self._region, attribute, attribute.Subtype)],
			list(attribute.IterateTypeMarks(self._region))
		)

	def test_Alias(self) -> None:
		"""Only an alias with a subtype indication has a type mark."""
		objectAlias = Alias("al", SimpleObjectOrFunctionCallSymbol(SimpleName("c")), _subtypeSymbol("T"))
		typeAlias =   Alias("AT", SimpleSubtypeSymbol(SimpleName("integer")))

		self.assertListEqual(
			[(self._region, objectAlias, objectAlias.Subtype)],
			list(objectAlias.IterateTypeMarks(self._region))
		)
		self.assertListEqual([], list(typeAlias.IterateTypeMarks(self._region)))

	def test_Component(self) -> None:
		"""None: generics and ports are declarations of the component's own region, each iterating its type marks."""
		genericType = GenericTypeInterfaceItem("GT")
		generic =     GenericConstantInterfaceItem(("G", ), Mode.Default, _subtypeSymbol("T"))
		port =        PortSimpleSignalInterfaceItem(("i", ), Mode.In, _subtypeSymbol("GT"))
		component =   Component("comp", genericItems=[genericType, generic], portItems=[port])

		self.assertListEqual([], list(component.IterateTypeMarks(self._region)))
		self.assertListEqual([(component, generic, generic.Subtype)], list(generic.IterateTypeMarks(component)))
		self.assertListEqual([(component, port, port.Subtype)], list(port.IterateTypeMarks(component)))

	def test_Function(self) -> None:
		"""The return type is looked up in the function's region, at its first declared item."""
		variable = Variable(("v", ), _subtypeSymbol("T"))
		function = Function("f", _subtypeSymbol("T"), declaredItems=[variable])

		self.assertListEqual(
			[(function, variable, function.ReturnType)], list(function.IterateTypeMarks(self._region))
		)

	def test_Function_WithoutDeclaredItems(self) -> None:
		"""Without declared items, the function itself is the place of its return type."""
		function = Function("f", _subtypeSymbol("T"))

		self.assertListEqual(
			[(function, function, function.ReturnType)], list(function.IterateTypeMarks(self._region))
		)

	def test_WithoutTypeMarks(self) -> None:
		enumeration = _enumeration("T", "a", "b")

		self.assertListEqual([], list(enumeration.IterateTypeMarks(self._region)))


class Names(Testcase):
	"""Simple names and expanded names."""

	def setUp(self) -> None:
		self._type =    _enumeration("T", "a", "b")
		self._package = Package("p", declaredItems=[self._type])

	def test_StdStandard(self) -> None:
		signal = _signal("s", "natural")
		design = _design(Entity("e", declaredItems=[signal]), analyze=False)
		self.assertListEqual([], _resolve(design))

		self.assertIs(design.GetPackage("std", "standard").Subtypes["natural"], signal.Subtype.Reference)

	def test_PredefinedPackages(self) -> None:
		"""The type marks of the predefined packages are resolved, e.g. ``natural`` is a subtype of ``integer``."""
		design = _design(analyze=False)
		self.assertListEqual([], _resolve(design))
		standard =     design.GetPackage("std", "standard")
		stdLogic1164 = design.GetPackage("ieee", "std_logic_1164")

		self.assertIs(standard.Types["integer"], standard.Subtypes["natural"].Type.Reference)
		self.assertIs(standard.Types["integer"], standard.Subtypes["natural"].BaseType)
		self.assertIs(stdLogic1164.Types["std_ulogic"], stdLogic1164.Subtypes["std_logic"].Type.Reference)

	def test_PackageName_ViaUsePackage(self) -> None:
		"""``use work.p; signal s : p.T;``."""
		constant = Constant(("c", ), _selectedSubtypeSymbol("p", "T"))
		entity =   Entity("e", [_use("work.p")], declaredItems=[constant])
		self.assertListEqual([], _resolve(_design(self._package, entity, analyze=False)))

		self.assertIs(self._type, constant.Subtype.Reference)

	def test_WorkPackage(self) -> None:
		"""``work.p.T`` without a use clause."""
		constant = Constant(("c", ), _selectedSubtypeSymbol("work", "p", "T"))
		self.assertListEqual([], _resolve(_design(self._package, Entity("e", declaredItems=[constant]), analyze=False)))

		self.assertIs(self._type, constant.Subtype.Reference)

	def test_LibraryPackage(self) -> None:
		"""``ieee.std_logic_1164.std_logic`` with a library clause."""
		constant = Constant(("c", ), _selectedSubtypeSymbol("ieee", "std_logic_1164", "std_logic"))
		entity =   Entity("e", [LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])], declaredItems=[constant])
		design =   _design(entity, analyze=False)
		self.assertListEqual([], _resolve(design))

		self.assertIs(design.GetPackage("ieee", "std_logic_1164").Subtypes["std_logic"], constant.Subtype.Reference)

	def test_LocalTypeHidesImported(self) -> None:
		"""A process' type hides the imported type."""
		local =        _enumeration("T", "x", "y")
		variable =     Variable(("v", ), _subtypeSymbol("T"))
		process =      ProcessStatement("proc", declaredItems=[local, variable])
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p.all")], statements=[process])
		self.assertListEqual([], _resolve(_design(self._package, Entity("e"), architecture, analyze=False)))

		self.assertIs(local, variable.Subtype.Reference)


class IncompleteTypes(Testcase):
	"""An incomplete type declaration and its full type declaration."""

	def test_Completed(self) -> None:
		incomplete =   AnonymousType("node")
		pointer =      AccessType("ptr", _subtypeSymbol("node"))
		node =         RecordType("node", [RecordTypeElement(("nextNode", ), _subtypeSymbol("ptr"))])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[incomplete, pointer, node])
		self.assertListEqual([], _resolve(_design(Entity("e"), architecture, analyze=False)))

		self.assertIs(node, pointer.DesignatedSubtype.Reference)
		self.assertIs(pointer, node.Elements[0].Subtype.Reference)

	def test_NotCompleted(self) -> None:
		incomplete =   AnonymousType("node")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[incomplete])
		warnings =     _resolve(_design(Entity("e"), architecture, analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], IncompleteTypeWarning)
		self.assertEqual("Incomplete type 'node' has no full type declaration in 'rtl'.", str(warnings[0]))
		self.assertIs(incomplete, warnings[0].IncompleteType)


class Diagnostics(Testcase):
	"""An unresolved type mark is an :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`."""

	def test_NotFound(self) -> None:
		signal =       _signal("s", "U")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[signal])
		warnings =     _resolve(_design(Entity("e"), architecture, analyze=False))

		self.assertEqual(1, len(warnings))
		warning = warnings[0]
		self.assertIsInstance(warning, UnresolvedTypeMarkWarning)
		self.assertEqual("Type mark 'U' not found in: rtl, e.", str(warning))
		self.assertIs(signal.Subtype, warning.Symbol)
		self.assertIs(signal, warning.Place)
		self.assertTupleEqual((architecture._namespace, architecture._namespace.ParentNamespace), warning.Namespaces)
		self.assertIsNone(signal.Subtype.Reference)

	def test_NotFound_UnlabeledProcess(self) -> None:
		process =      ProcessStatement(declaredItems=[Variable(("v", ), _subtypeSymbol("U"))])
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[process])
		warnings =     _resolve(_design(Entity("e"), architecture, analyze=False))

		self.assertEqual("Type mark 'U' not found in: ?, rtl, e.", str(warnings[0]))

	def test_DeclarationOrder(self) -> None:
		"""A type declared after the object isn't visible."""
		signal =       _signal("s", "LT")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[signal, _enumeration("LT", "x", "y")])
		warnings =     _resolve(_design(Entity("e"), architecture, analyze=False))

		self.assertEqual("Type mark 'LT' not found in: rtl, e.", str(warnings[0]))

	def test_Ambiguous(self) -> None:
		"""Two use clauses import a type ``T``."""
		signal =   _signal("s", "T")
		first =    Package("p1", declaredItems=[_enumeration("T", "a")])
		second =   Package("p2", declaredItems=[_enumeration("T", "b")])
		entity =   Entity("e", [_use("work.p1.all", "work.p2.all")], declaredItems=[signal])
		warnings = _resolve(_design(first, second, entity, analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual("Type mark 'T' is ambiguous: use clauses import conflicting declarations.", str(warnings[0]))
		self.assertEqual(2, len(warnings[0].Conflicts))

	def test_NotAType(self) -> None:
		"""``signal s : K;`` with a constant ``K``."""
		signal =       _signal("s", "K")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_constant("K", "integer"), signal])
		warnings =     _resolve(_design(Entity("e"), architecture, analyze=False))

		self.assertEqual("Type mark 'K' doesn't denote a type or subtype (found: Constant).", str(warnings[0]))

	def test_TypeAlias_Conflict(self) -> None:
		"""``use work.p1.all, work.p2.all;`` with ``alias T is work.p1.T;`` in ``p2`` (IEEE Std 1076-2008, 12.4 c))."""
		original = _enumeration("T", "a", "b")
		alias =    Alias("T", _selectedSubtypeSymbol("work", "p1", "T"))
		signal =   _signal("s", "T")
		entity =   Entity("e", [_use("work.p1.all", "work.p2.all")], declaredItems=[signal])
		warnings = _resolve(_design(
			Package("p1", declaredItems=[original]), Package("p2", declaredItems=[alias]), entity, analyze=False
		))

		self.assertEqual(1, len(warnings))
		self.assertEqual("Type mark 'T' is ambiguous: use clauses import conflicting declarations.", str(warnings[0]))
		self.assertTupleEqual((original, alias), tuple(imported.Element for imported in warnings[0].Conflicts))
		self.assertIs(original, alias.Name.Reference)
		self.assertIsNone(signal.Subtype.Reference)

	def test_LibraryName_NoLibraryClause(self) -> None:
		"""``constant c : lib.p.T;`` in library ``lib`` (GHDL: ``no declaration for "lib"``)."""
		constant = Constant(("c", ), _selectedSubtypeSymbol("lib", "p", "T"))
		entity =   Entity("e", declaredItems=[constant])
		warnings = _resolve(_design(Package("p", declaredItems=[_enumeration("T", "a", "b")]), entity, analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Prefix 'lib.p' of type mark 'lib.p.T' isn't a visible package or an enclosing region.",
			str(warnings[0])
		)
		self.assertIsNone(constant.Subtype.Reference)

	def test_LibraryName_LibraryClause(self) -> None:
		"""``library lib; constant c : lib.p.T;`` in library ``lib``."""
		enumeration =   _enumeration("T", "a", "b")
		constant =      Constant(("c", ), _selectedSubtypeSymbol("lib", "p", "T"))
		libraryClause = LibraryClause([LibraryReferenceSymbol(SimpleName("lib"))])
		entity =        Entity("e", [libraryClause], declaredItems=[constant])

		self.assertListEqual([], _resolve(_design(Package("p", declaredItems=[enumeration]), entity, analyze=False)))
		self.assertIs(enumeration, constant.Subtype.Reference)

	def test_PrefixNotAPackage(self) -> None:
		"""``work.nopkg.T``."""
		constant = Constant(("c", ), _selectedSubtypeSymbol("work", "nopkg", "T"))
		warnings = _resolve(_design(Entity("e", declaredItems=[constant]), analyze=False))

		self.assertEqual(
			"Prefix 'work.nopkg' of type mark 'work.nopkg.T' isn't a visible package or an enclosing region.",
			str(warnings[0])
		)

	def test_MemberMissing(self) -> None:
		"""``work.p.U``."""
		constant = Constant(("c", ), _selectedSubtypeSymbol("work", "p", "U"))
		warnings = _resolve(_design(Package("p"), Entity("e", declaredItems=[constant]), analyze=False))

		self.assertEqual("Type mark 'work.p.U' not found in: p.", str(warnings[0]))


class Reanalysis(Testcase):
	"""Resolving again and resetting an analysis."""

	def test_AnalyzeResolves(self) -> None:
		""":meth:`~pyVHDLModel.Design.Analyze` resolves the type marks (:meth:`~pyVHDLModel.Design.AnalyzeObjects`)."""
		signal = _signal("s", "integer")
		design = _design(Entity("e", declaredItems=[signal]))

		self.assertIs(design.GetPackage("std", "standard").Types["integer"], signal.Subtype.Reference)

	def test_ResetAnalysis(self) -> None:
		subtype = Subtype("ST", _subtypeSymbol("integer"))
		signal =  _signal("s", "ST")
		design =  _design(Entity("e", declaredItems=[subtype, signal]), analyze=False)
		_resolve(design)

		design.ResetAnalysis()

		self.assertIsNone(signal.Subtype.Reference)
		self.assertIsNone(subtype.BaseType)
		self.assertIs(
			design.GetPackage("std", "standard").Types["integer"],
			design.GetPackage("std", "standard").Subtypes["natural"].BaseType
		)

	def test_ResolveAgain(self) -> None:
		signal = _signal("s", "integer")
		design = _design(Entity("e", declaredItems=[signal]), analyze=False)
		_resolve(design)
		reference = signal.Subtype.Reference

		self.assertListEqual([], _resolve(design))
		self.assertIs(reference, signal.Subtype.Reference)

	def test_WithoutCollector(self) -> None:
		"""An unresolved type mark is a critical warning: the analysis isn't silently incomplete."""
		design = _design(Entity("e", declaredItems=[_signal("s", "U")]), analyze=False)

		with self.assertRaises(UnhandledCriticalWarningError):
			design.Analyze()


class ReviewFindings(Testcase):
	"""Several documents per library, return types, re-resolution, expanded names, components, incomplete types."""

	def test_SeveralDocuments(self) -> None:
		"""Two independent documents in one library: the compile order has no edge."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		signals = []
		for identifier in ("a", "b"):
			signal = _signal("s", "integer")
			signals.append(signal)
			document = Document(Path(f"{identifier}.vhdl"))
			document._AddDesignUnit(Entity(identifier, declaredItems=[signal]))
			design.AddDocument(document, design.GetLibrary("lib"))

		design.Analyze()

		self.assertListEqual([], _resolve(design))
		for signal in signals:
			self.assertEqual("integer", signal.Subtype.Reference.Identifier)

	def test_ReturnType_NotLocalType(self) -> None:
		"""``function f return T`` with a type ``T`` in its body: the return type is the package's ``T`` (GHDL)."""
		packageType = _enumeration("T", "a", "b")
		localType =   _enumeration("T", "x", "y")
		function =    Function("f", _subtypeSymbol("T"), declaredItems=[localType])
		design =      _design(Package("p", declaredItems=[packageType, function]), analyze=False)

		for _ in range(2):
			self.assertListEqual([], _resolve(design))
			self.assertIs(packageType, function.ReturnType.Reference)

	def test_ResolveAgain_AfterRemoval(self) -> None:
		"""A type mark, which doesn't resolve any more, has no reference."""
		enumeration = _enumeration("T", "a", "b")
		constant =    _constant("c", "T")
		package =     Package("p", declaredItems=[enumeration, constant])
		design =      _design(package, analyze=False)
		_resolve(design)

		package.RemoveDeclaredItem(enumeration)
		warnings = _resolve(design)

		self.assertEqual(1, len(warnings))
		self.assertIsNone(constant.Subtype.Reference)

	def test_ExpandedName_EnclosingPackage(self) -> None:
		"""``constant k : q.T`` inside package ``q`` (GHDL accepts)."""
		enumeration = _enumeration("T", "a", "b")
		constant =    Constant(("k", ), _selectedSubtypeSymbol("q", "T"))
		self.assertListEqual([], _resolve(_design(Package("q", declaredItems=[enumeration, constant]), analyze=False)))

		self.assertIs(enumeration, constant.Subtype.Reference)

	def test_Component_Generics(self) -> None:
		"""``component c generic (type GT); port (p : in GT);`` (GHDL accepts)."""
		genericType =  GenericTypeInterfaceItem("GT")
		port =         PortSimpleSignalInterfaceItem(("p", ), Mode.In, _subtypeSymbol("GT"))
		component =    Component("c", [genericType], [port])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[component])
		self.assertListEqual([], _resolve(_design(Entity("e"), Entity("c"), architecture, analyze=False)))

		self.assertIs(genericType, port.Subtype.Reference)

	def test_Component_Duplicate(self) -> None:
		"""``component c generic (g : integer); port (g : in bit);``: the analysis indexes the component (GHDL rejects)."""
		generic =   GenericConstantInterfaceItem(("g", ), Mode.Default, _subtypeSymbol("integer"))
		port =      PortSimpleSignalInterfaceItem(("g", ), Mode.In, _subtypeSymbol("bit"))
		component = Component("c", [generic], [port])
		warnings =  _resolve(_design(Package("p", declaredItems=[component]), Entity("c"), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], DuplicateDeclarationWarning)
		self.assertEqual("Identifier 'g' is already used for a declaration in 'c'.", str(warnings[0]))
		self.assertTrue(component._areDeclaredItemsIndexed)
		self.assertEqual("integer", generic.Subtype.Reference.Identifier)
		self.assertEqual("bit", port.Subtype.Reference.Identifier)

	def test_Component_GenericHidesOuterType(self) -> None:
		"""``type T ...; component c generic (type T); port (p : in T);``: the generic type hides ``T`` (GHDL accepts)."""
		outerType =    _enumeration("T", "a", "b")
		genericType =  GenericTypeInterfaceItem("T")
		port =         PortSimpleSignalInterfaceItem(("p", ), Mode.In, _subtypeSymbol("T"))
		component =    Component("c", [genericType], [port])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[outerType, component])
		self.assertListEqual([], _resolve(_design(Entity("e"), Entity("c"), architecture, analyze=False)))

		self.assertIs(genericType, port.Subtype.Reference)
		self.assertIs(architecture._namespace, component._namespace.ParentNamespace)

	def test_IncompleteType_ObjectBeforeFullType(self) -> None:
		"""``type node; signal s : node; type node is ...;``: only an access type may use an incomplete type."""
		incomplete =   AnonymousType("node")
		signal =       _signal("s", "node")
		node =         RecordType("node", [RecordTypeElement(("v", ), _subtypeSymbol("integer"))])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[incomplete, signal, node])
		warnings =     _resolve(_design(Entity("e"), architecture, analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Type mark 'node' denotes an incomplete type, which only an access type may use.",
			str(warnings[0])
		)
		self.assertIsNone(signal.Subtype.Reference)

	def test_AliasName_NotFound(self) -> None:
		"""``alias AT is nothere;``: the alias name is reported, the type mark using the alias too."""
		alias =    Alias("AT", SimpleObjectOrFunctionCallSymbol(SimpleName("nothere")))
		warnings = _resolve(_design(Package("q", declaredItems=[alias]), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], UnresolvedNameWarning)
		self.assertNotIsInstance(warnings[0], UnresolvedTypeMarkWarning)
		self.assertEqual("Name 'nothere' not found in: q.", str(warnings[0]))

	def test_PackageAndBody_SearchedOnce(self) -> None:
		"""A package body and its package share a name; the message names it once."""
		constant = _constant("c", "U")
		warnings = _resolve(_design(
			Package("q"), PackageBody(_packageSymbol("q"), declaredItems=[constant]), analyze=False
		))

		self.assertEqual("Type mark 'U' not found in: q.", str(warnings[0]))

	def test_AliasName_ImplicitOperation(self) -> None:
		"""``alias to_bstring is to_string [...];``: implicitly declared operations aren't represented, so not reported."""
		alias = Alias("to_bstring", SimpleObjectOrFunctionCallSymbol(SimpleName("to_string")))

		self.assertListEqual([], _resolve(_design(Package("q", declaredItems=[alias]), analyze=False)))
