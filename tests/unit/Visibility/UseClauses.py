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
Use clauses (IEEE Std 1076-2008, 12.4): what ``use lib.pkg.all``, ``use lib.pkg.item``, ``use lib.pkg`` and
``use lib.all`` make potentially visible, and where.
"""
from pyTooling.Warning      import WarningCollector
from pyTooling.Testing      import Testcase

from pyVHDLModel.Concurrent import ConcurrentBlockStatement, ProcessStatement
from pyVHDLModel.DesignUnit import Architecture, Component, Context, ContextReference, Entity, LibraryClause, Package, \
                                   PackageBody
from pyVHDLModel.Exception  import UnresolvedNameWarning
from pyVHDLModel.Interface  import GenericTypeInterfaceItem
from pyVHDLModel.Name       import SelectedName, SimpleName
from pyVHDLModel.Symbol     import ContextReferenceSymbol, LibraryReferenceSymbol
from pyVHDLModel.Type       import Subtype

from tests.unit             import _entitySymbol, _signal, _subtypeSymbol
from tests.unit.Visibility  import _constant, _design, _distance, _enumeration, _function, _packageSymbol, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _libraryClause(identifier: str) -> LibraryClause:
	"""A library clause of one library."""
	return LibraryClause([LibraryReferenceSymbol(SimpleName(identifier))])


def _contextReference(library: str, identifier: str) -> ContextReference:
	"""A context reference ``library.identifier``."""
	return ContextReference([ContextReferenceSymbol(SelectedName(identifier, SimpleName(library)))])


class UseAll(Testcase):
	"""``use work.p.all;`` makes every declaration of ``p`` potentially visible (A001-A016)."""

	def setUp(self) -> None:
		self._type =      _enumeration("T", "a", "b", "'0'")
		self._subtype =   Subtype("ST", _subtypeSymbol("T"))
		self._constant =  _constant("K", "integer")
		self._f1 =        _function("f", "integer")
		self._f2 =        _function("f", "bit")
		self._distance =  _distance()
		self._component = Component("comp")
		package = Package(
			"p",
			declaredItems=[
				self._type, self._subtype, self._constant, self._f1, self._f2, self._distance, self._component,
				_use("work.q.all")
			]
		)
		self._q = _constant("Q", "integer")
		self._entity = Entity("e", [_use("work.p.all")])
		self._design = _design(Package("q", declaredItems=[self._q]), package, Entity("comp"), self._entity)
		self._namespace = self._entity._namespace

	def test_Type(self) -> None:
		self.assertTupleEqual((self._type, ), self._namespace.Lookup("t").Declarations)

	def test_Subtype(self) -> None:
		self.assertTupleEqual((self._subtype, ), self._namespace.Lookup("st").Declarations)

	def test_Constant(self) -> None:
		self.assertTupleEqual((self._constant, ), self._namespace.Lookup("k").Declarations)

	def test_Function_Overloads(self) -> None:
		self.assertTupleEqual((self._f1, self._f2), self._namespace.Lookup("f").Declarations)

	def test_EnumerationLiteral(self) -> None:
		self.assertTupleEqual((self._type.Literals[1], ), self._namespace.Lookup("b").Declarations)

	def test_CharacterLiteral(self) -> None:
		"""``'0'`` of ``T`` and of ``std.standard.bit`` and ``character`` are overloaded, so all are visible."""
		declarations = self._namespace.Lookup("'0'").Declarations

		self.assertIn(self._type.Literals[2], declarations)
		self.assertEqual(3, len(declarations))

	def test_PhysicalUnit(self) -> None:
		self.assertTupleEqual((self._distance.Units[1], ), self._namespace.Lookup("cm").Declarations)

	def test_Component(self) -> None:
		self.assertTupleEqual((self._component, ), self._namespace.Lookup("comp").Declarations)

	def test_UseClauseNotExported(self) -> None:
		"""A use clause of ``p`` imports into ``p`` only, ``Q`` isn't a declaration of ``p`` (A033)."""
		result = self._namespace.Lookup("q")

		self.assertFalse(result.IsVisible)

	def test_Origin(self) -> None:
		"""The import records the use clause."""
		result = self._namespace.Lookup("k")

		self.assertEqual(1, len(result.Imports))
		self.assertIs(self._entity.PackageReferences[0], result.Imports[0].UseClause)
		self.assertIs(self._constant, result.Imports[0].Element)

	def test_Symbol(self) -> None:
		"""The symbol of the use clause references the package."""
		symbol = self._entity.PackageReferences[0].Symbols[0]

		self.assertIs(self._design.GetPackage("lib", "p"), symbol.Reference)


class UseItem(Testcase):
	"""``use work.p.item;`` makes the declarations named ``item`` potentially visible (A019-A023, A083, A093)."""

	def setUp(self) -> None:
		self._type =     _enumeration("T", "a", "b")
		self._f1 =       _function("f", "integer")
		self._f2 =       _function("f", "bit")
		self._g =        _function("g", "integer")
		self._distance = _distance()
		self._package =  Package("p", declaredItems=[self._type, self._f1, self._f2, self._g, self._distance])

	def test_Function_AllOverloads(self) -> None:
		entity = Entity("e", [_use("work.p.f")])
		_design(self._package, entity)

		self.assertTupleEqual((self._f1, self._f2), entity._namespace.Lookup("f").Declarations)
		self.assertFalse(entity._namespace.Lookup("g").IsVisible)

	def test_Type_Literals(self) -> None:
		entity = Entity("e", [_use("work.p.t")])
		_design(self._package, entity)

		self.assertTupleEqual((self._type, ), entity._namespace.Lookup("t").Declarations)
		self.assertTupleEqual((self._type.Literals[0], ), entity._namespace.Lookup("a").Declarations)

	def test_PhysicalType_Units(self) -> None:
		entity = Entity("e", [_use("work.p.distance")])
		_design(self._package, entity)

		self.assertTupleEqual((self._distance.Units[1], ), entity._namespace.Lookup("cm").Declarations)

	def test_Subtype_BaseTypeLiterals(self) -> None:
		"""``use ieee.std_logic_1164.std_logic;`` brings the literals of ``std_ulogic`` along."""
		libraryClause = LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])
		entity = Entity("e", [libraryClause, _use("ieee.std_logic_1164.std_logic")])
		design = _design(entity)
		stdULogic = design.GetPackage("ieee", "std_logic_1164").Types["std_ulogic"]

		self.assertIn(stdULogic.Literals[4], entity._namespace.Lookup("'Z'").Declarations)

	def test_NotDeclared(self) -> None:
		entity = Entity("e", [_use("work.p.nothere")])

		with WarningCollector() as collector:
			_design(self._package, entity)

		self.assertEqual(1, len(collector.Warnings))
		warning = collector.Warnings[0]
		self.assertIsInstance(warning, UnresolvedNameWarning)
		self.assertEqual("Package 'p' has no declaration 'nothere'.", str(warning))
		self.assertIs(entity.PackageReferences[0].Symbols[0], warning.Symbol)
		self.assertTupleEqual((self._package._namespace, ), warning.Namespaces)


class UsePackage(Testcase):
	"""``use work.p;`` makes the package name potentially visible, not its declarations (A062, A063)."""

	def test_PackageName(self) -> None:
		constant = _constant("K", "integer")
		package = Package("p", declaredItems=[constant])
		entity = Entity("e", [_use("work.p")])
		_design(package, entity)

		self.assertTupleEqual((package, ), entity._namespace.Lookup("p").Declarations)
		self.assertFalse(entity._namespace.Lookup("k").IsVisible)

	def test_SimpleNamePrefix(self) -> None:
		"""``use work.p; use p.all;``: the prefix ``p`` denotes the visible package."""
		constant = _constant("K", "integer")
		package = Package("p", declaredItems=[constant])
		entity = Entity("e", [_use("work.p"), _use("p.all")])
		_design(package, entity)

		self.assertTupleEqual((constant, ), entity._namespace.Lookup("k").Declarations)

	def test_LocalPackage(self) -> None:
		"""A package declared in an architecture is used by a simple name (A088)."""
		localType = _enumeration("T", "a", "b")
		localPackage = Package("lp", declaredItems=[localType])
		signal = _signal("s", "T")
		useClause = _use("lp.all")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[localPackage, useClause, signal])
		_design(Entity("e"), architecture)

		self.assertTupleEqual((localType, ), architecture._namespace.Lookup("t", signal).Declarations)


class UseLibrary(Testcase):
	"""``use work.all;`` and ``use work.unit;`` make primary units of the library potentially visible (A060)."""

	def test_WorkAll(self) -> None:
		package = Package("p")
		other = Entity("other")
		entity = Entity("e", [_use("work.all")])
		_design(package, other, entity)

		self.assertTupleEqual((package, ), entity._namespace.Lookup("p").Declarations)
		self.assertTupleEqual((other, ), entity._namespace.Lookup("other").Declarations)

	def test_WorkUnit(self) -> None:
		other = Entity("other")
		entity = Entity("e", [_use("work.other")])
		_design(other, entity)

		self.assertTupleEqual((other, ), entity._namespace.Lookup("other").Declarations)


class DeclarativeRegions(Testcase):
	"""A use clause in a declarative part imports into its region; its scope is the rest of the region (A024-A039)."""

	def setUp(self) -> None:
		self._type =    _enumeration("T", "a", "b")
		self._package = Package("p", declaredItems=[self._type])

	def test_Architecture(self) -> None:
		signal = _signal("s", "T")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("work.p.all"), signal])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), architecture._namespace.Lookup("t", signal).Declarations)

	def test_Architecture_NotInEntity(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("work.p.all")])
		entity = Entity("e")
		_design(self._package, entity, architecture)

		self.assertFalse(entity._namespace.Lookup("t").IsVisible)

	def test_Entity_SeenByArchitecture(self) -> None:
		"""A use clause in the entity's declarative part is seen by its architecture (A039)."""
		signal = _signal("s", "T")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[signal])
		_design(self._package, Entity("e", declaredItems=[_use("work.p.all")]), architecture)

		self.assertTupleEqual((self._type, ), architecture._namespace.Lookup("t", signal).Declarations)

	def test_Process(self) -> None:
		process = ProcessStatement("proc", declaredItems=[_use("work.p.all")])
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[process])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), process._namespace.Lookup("t").Declarations)
		self.assertFalse(architecture._namespace.Lookup("t").IsVisible)

	def test_Block(self) -> None:
		"""A block's use clause isn't seen by a process beside the block (A027, A028)."""
		block = ConcurrentBlockStatement("blk", declaredItems=[_use("work.p.all")])
		process = ProcessStatement("proc")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[block, process])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), block._namespace.Lookup("t").Declarations)
		self.assertFalse(process._namespace.Lookup("t").IsVisible)

	def test_Subprogram(self) -> None:
		"""A subprogram's use clause isn't seen by its parameters, which precede it (A030, A031)."""
		function = _function("f", "T")
		function.AddDeclaredItem(_use("work.p.all"))
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[function])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), function._namespace.Lookup("t").Declarations)
		self.assertFalse(function._namespace.Lookup("t", function.ParameterItems[0]).IsVisible)

	def test_PackageBody(self) -> None:
		"""A use clause in a package body isn't seen by the package declaration (A034, A036)."""
		package = Package("q")
		packageBody = PackageBody(_packageSymbol("q"), declaredItems=[_use("work.p.all")])
		_design(self._package, package, packageBody)

		self.assertTupleEqual((self._type, ), packageBody._namespace.Lookup("t").Declarations)
		self.assertFalse(package._namespace.Lookup("t").IsVisible)

	def test_ContextOfPackage_SeenByBody(self) -> None:
		"""A use clause in the context clause of a package is seen by its body (A035)."""
		package = Package("q", [_use("work.p.all")])
		packageBody = PackageBody(_packageSymbol("q"))
		_design(self._package, package, packageBody)

		self.assertTupleEqual((self._type, ), packageBody._namespace.Lookup("t").Declarations)

	def test_ContextClause_NotNextUnit(self) -> None:
		"""A context clause belongs to one design unit (A041)."""
		first = Entity("e1", [_use("work.p.all")])
		second = Entity("e2")
		_design(self._package, first, second)

		self.assertFalse(second._namespace.Lookup("t").IsVisible)

	def test_ResetAnalysis(self) -> None:
		"""Resetting the analysis removes the imports of nested regions and the references of their use clauses."""
		useClause = _use("work.p.all")
		process = ProcessStatement("proc", declaredItems=[useClause])
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[process])
		design = _design(self._package, Entity("e"), architecture)

		design.ResetAnalysis()

		self.assertDictEqual({}, process._namespace.Imports())
		self.assertIsNone(useClause.Symbols[0].Reference)


class ContextReferences(Testcase):
	"""A context reference makes the declarations of the context's use clauses potentially visible (A079)."""

	def test_Context(self) -> None:
		libraryType = _enumeration("T", "a", "b")
		context = Context("ctx", [LibraryClause([LibraryReferenceSymbol(SimpleName("lib1"))]), _use("lib1.p.all")])
		entity = Entity("e", [ContextReference([ContextReferenceSymbol(SelectedName("ctx", SimpleName("work")))])])
		_design(context, entity, libraries=[("lib1", [Package("p", declaredItems=[libraryType])])])

		result = entity._namespace.Lookup("t")
		self.assertTupleEqual((libraryType, ), result.Declarations)
		self.assertIs(context.PackageReferences[0], result.Imports[0].UseClause)


class ImplicitUseClause(Testcase):
	"""Every primary unit is preceded by ``use std.standard.all;`` (A066)."""

	def test_StdStandard(self) -> None:
		entity = Entity("e")
		design = _design(entity)
		result = entity._namespace.Lookup("integer")

		self.assertTupleEqual((design.GetPackage("std", "standard").Types["integer"], ), result.Declarations)
		self.assertIsNone(result.Imports[0].UseClause)

	def test_StandardPackageName(self) -> None:
		"""The package name ``standard`` isn't made visible (A067)."""
		entity = Entity("e")
		_design(entity)

		self.assertFalse(entity._namespace.Lookup("standard").IsVisible)


class ContextDeclarations(Testcase):
	"""Context declarations: nested contexts, missing members, and a use clause after the context reference."""

	def setUp(self) -> None:
		self._type =    _enumeration("T", "a", "b")
		self._package = Package("p", declaredItems=[self._type])

	def test_NestedContexts(self) -> None:
		"""``context c2`` references ``context c1``, which uses ``lib1.p.all`` (GHDL accepts)."""
		first = Context("c1", [_libraryClause("lib1"), _use("lib1.p.all")])
		second = Context("c2", [_libraryClause("lib1"), _contextReference("lib1", "c1")])
		entity = Entity("e", [_libraryClause("lib1"), _contextReference("lib1", "c2")])
		_design(entity, libraries=[("lib1", [self._package, first, second])])

		self.assertTupleEqual((self._type, ), entity._namespace.Lookup("t").Declarations)
		self.assertTupleEqual((self._type.Literals[0], ), entity._namespace.Lookup("a").Declarations)

	def test_MissingMember(self) -> None:
		"""``use lib1.p.nothere;`` in a context declaration."""
		useClause = _use("lib1.p.nothere")
		context = Context("c1", [_libraryClause("lib1"), useClause])

		with WarningCollector() as collector:
			_design(Entity("e"), libraries=[("lib1", [self._package, context])])

		self.assertEqual(1, len(collector.Warnings))
		warning = collector.Warnings[0]
		self.assertIsInstance(warning, UnresolvedNameWarning)
		self.assertEqual("Package 'p' has no declaration 'nothere'.", str(warning))
		self.assertIs(useClause, warning.Place)

	def test_UseClauseAfterContextReference(self) -> None:
		"""``context lib1.ctx;`` imports ``T`` before ``signal s : T;``, a later use clause of ``p`` doesn't hide it."""
		context = Context("ctx", [_libraryClause("lib1"), _use("lib1.p.all")])
		signal = _signal("s", "T")
		contextItems = [_libraryClause("lib1"), _contextReference("lib1", "ctx")]
		architecture = Architecture("rtl", _entitySymbol("e"), contextItems, [signal, _use("lib1.p.all")])
		_design(Entity("e"), architecture, libraries=[("lib1", [self._package, context])])

		self.assertTupleEqual((self._type, ), architecture._namespace.Lookup("t", signal).Declarations)


class UseClauseDiagnostics(Testcase):
	"""Use clauses, which name nothing usable, are an :exc:`~pyVHDLModel.Exception.UnresolvedNameWarning`."""

	def test_PrefixNotAPackage(self) -> None:
		"""``use K.all;`` with a constant ``K``."""
		useClause = _use("k.all")
		entity = Entity("e", declaredItems=[_constant("K", "integer"), useClause])

		with WarningCollector() as collector:
			_design(entity)

		self.assertEqual(1, len(collector.Warnings))
		self.assertEqual("Prefix 'k' of use clause 'k.all' isn't a visible package.", str(collector.Warnings[0]))
		self.assertIs(useClause, collector.Warnings[0].Place)

	def test_PrimaryUnitMissing(self) -> None:
		"""``use work.nothere;``."""
		entity = Entity("e", [_use("work.nothere")])

		with WarningCollector() as collector:
			_design(entity)

		self.assertEqual(1, len(collector.Warnings))
		self.assertEqual("Library 'lib' has no primary unit 'nothere'.", str(collector.Warnings[0]))

	def test_GenericPackage(self) -> None:
		"""``use work.gp.all;`` with an uninstantiated generic package (A086)."""
		constant = _constant("K", "integer")
		genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")], declaredItems=[constant])
		entity = Entity("e", [_use("work.gp.all")])

		with WarningCollector() as collector:
			_design(genericPackage, entity)

		self.assertEqual(1, len(collector.Warnings))
		self.assertEqual(
			"Use clause 'work.gp.all' names the uninstantiated generic package 'gp'.",
			str(collector.Warnings[0])
		)
		self.assertFalse(entity._namespace.Lookup("k").IsVisible)


class UseItemSubtype(Testcase):
	"""``use work.p.ST;`` with a subtype of an enumerated type brings the base type's literals along (A093)."""

	def test_UserSubtype(self) -> None:
		enumeration = _enumeration("T", "a", "b")
		first = Subtype("ST1", _subtypeSymbol("T"))
		second = Subtype("ST2", _subtypeSymbol("ST1"))
		entity = Entity("e", [_use("work.p.ST2")])
		_design(Package("p", declaredItems=[enumeration, first, second]), entity)

		self.assertTupleEqual((enumeration.Literals[1], ), entity._namespace.Lookup("b").Declarations)
