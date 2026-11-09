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
from pathlib                   import Path

from pyTooling.Warning         import WarningCollector
from pyTooling.Testing         import Testcase

from pyVHDLModel               import Design, Document
from pyVHDLModel.Concurrent    import ConcurrentBlockStatement, EntityInstantiation, ProcessStatement
from pyVHDLModel.DesignUnit    import Architecture, Component, Context, ContextReference, Entity, LibraryClause, \
                                      Package, PackageBody, UseClause
from pyVHDLModel.Exception     import InstantiationNotLinkedError, LibraryNotFoundError, \
                                      PackageInstantiationNotLinkedError, UnresolvedNameWarning, \
                                      UnresolvedTypeMarkWarning, VHDLModelException, \
                                      LibraryNotVisibleError, UseClauseLibraryNotVisibleError, \
                                      ContextReferenceLibraryNotVisibleError, \
                                      PackageInstantiationLibraryNotVisibleError, \
                                      EntityInstantiationLibraryNotVisibleError, LibraryNotInDesignError, \
                                      ReferencedLibraryNotExistingError, LibraryClauseLibraryNotFoundError, \
                                      PackageInstantiationLibraryNotFoundError, \
                                      EntityInstantiationLibraryNotFoundError, DesignUnitNotFoundError, \
                                      PackageNotFoundError, ContextNotFoundError, NotLinkedError, \
                                      LibraryReferenceNotLinkedError, UnknownKindError, UnknownSymbolKindError, \
                                      NotAGenericPackageError
from pyVHDLModel.Instantiation import PackageInstantiation
from pyVHDLModel.Interface     import GenericTypeInterfaceItem
from pyVHDLModel.Name          import SelectedName, SimpleName
from pyVHDLModel.Symbol        import ContextReferenceSymbol, EntityInstantiationSymbol, LibraryReferenceSymbol, \
                                      PackageReferenceSymbol
from pyVHDLModel.Type          import Subtype

from tests.unit                import _entitySymbol, _signal, _subtypeSymbol
from tests.unit.Resolution     import _resolve
from tests.unit.Visibility     import _constant, _design, _distance, _enumeration, _function, _packageSymbol, _use


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
	"""``use work.p.all;`` makes every declaration of ``p`` potentially visible."""

	def setUp(self) -> None:
		self._type =      _enumeration("T", "a", "b", "'0'")
		self._subtype =   Subtype("ST", _subtypeSymbol("T"))
		self._constant =  _constant("K", "integer")
		self._f1 =        _function("f", "integer")
		self._f2 =        _function("f", "bit")
		self._distance =  _distance()
		self._component = Component("comp")
		package =         Package(
			"p",
			declaredItems=[
				self._type, self._subtype, self._constant, self._f1, self._f2, self._distance, self._component,
				_use("work.q.all")
			]
		)
		self._q =         _constant("Q", "integer")
		self._entity =    Entity("e", [_use("work.p.all")])
		self._design =    _design(Package("q", declaredItems=[self._q]), package, Entity("comp"), self._entity)
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
		self.assertTupleEqual((self._distance.SecondaryUnits[0], ), self._namespace.Lookup("cm").Declarations)

	def test_Component(self) -> None:
		self.assertTupleEqual((self._component, ), self._namespace.Lookup("comp").Declarations)

	def test_UseClauseNotExported(self) -> None:
		"""A use clause of ``p`` imports into ``p`` only, ``Q`` isn't a declaration of ``p``."""
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
	"""``use work.p.item;`` makes the declarations named ``item`` potentially visible."""

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

		self.assertTupleEqual((self._distance.SecondaryUnits[0], ), entity._namespace.Lookup("cm").Declarations)

	def test_Subtype_BaseTypeLiterals(self) -> None:
		"""``use ieee.std_logic_1164.std_logic;`` brings the literals of ``std_ulogic`` along."""
		libraryClause = LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])
		entity =        Entity("e", [libraryClause, _use("ieee.std_logic_1164.std_logic")])
		design =        _design(entity)
		stdULogic =     design.GetPackage("ieee", "std_logic_1164").Types["std_ulogic"]

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
	"""``use work.p;`` makes the package name potentially visible, not its declarations."""

	def test_PackageName(self) -> None:
		constant = _constant("K", "integer")
		package =  Package("p", declaredItems=[constant])
		entity =   Entity("e", [_use("work.p")])
		_design(package, entity)

		self.assertTupleEqual((package, ), entity._namespace.Lookup("p").Declarations)
		self.assertFalse(entity._namespace.Lookup("k").IsVisible)

	def test_SimpleNamePrefix(self) -> None:
		"""``use work.p; use p.all;``: the prefix ``p`` denotes the visible package."""
		constant = _constant("K", "integer")
		package =  Package("p", declaredItems=[constant])
		entity =   Entity("e", [_use("work.p"), _use("p.all")])
		_design(package, entity)

		self.assertTupleEqual((constant, ), entity._namespace.Lookup("k").Declarations)

	def test_LocalPackage(self) -> None:
		"""A package declared in an architecture is used by a simple name."""
		localType =    _enumeration("T", "a", "b")
		localPackage = Package("lp", declaredItems=[localType])
		signal =       _signal("s", "T")
		useClause =    _use("lp.all")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[localPackage, useClause, signal])
		_design(Entity("e"), architecture)

		self.assertTupleEqual((localType, ), architecture._namespace.Lookup("t", signal).Declarations)


class UseLibrary(Testcase):
	"""``use work.all;`` and ``use work.unit;`` make primary units of the library potentially visible."""

	def test_WorkAll(self) -> None:
		package = Package("p")
		other =   Entity("other")
		entity =  Entity("e", [_use("work.all")])
		_design(package, other, entity)

		self.assertTupleEqual((package, ), entity._namespace.Lookup("p").Declarations)
		self.assertTupleEqual((other, ), entity._namespace.Lookup("other").Declarations)

	def test_WorkUnit(self) -> None:
		other =  Entity("other")
		entity = Entity("e", [_use("work.other")])
		_design(other, entity)

		self.assertTupleEqual((other, ), entity._namespace.Lookup("other").Declarations)


class DeclarativeRegions(Testcase):
	"""A use clause in a declarative part imports into its region; its scope is the rest of the region."""

	def setUp(self) -> None:
		self._type =    _enumeration("T", "a", "b")
		self._package = Package("p", declaredItems=[self._type])

	def test_Architecture(self) -> None:
		signal =       _signal("s", "T")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("work.p.all"), signal])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), architecture._namespace.Lookup("t", signal).Declarations)

	def test_Architecture_NotInEntity(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("work.p.all")])
		entity =       Entity("e")
		_design(self._package, entity, architecture)

		self.assertFalse(entity._namespace.Lookup("t").IsVisible)

	def test_Entity_SeenByArchitecture(self) -> None:
		"""A use clause in the entity's declarative part is seen by its architecture."""
		signal =       _signal("s", "T")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[signal])
		_design(self._package, Entity("e", declaredItems=[_use("work.p.all")]), architecture)

		self.assertTupleEqual((self._type, ), architecture._namespace.Lookup("t", signal).Declarations)

	def test_Process(self) -> None:
		process =      ProcessStatement("proc", declaredItems=[_use("work.p.all")])
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[process])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), process._namespace.Lookup("t").Declarations)
		self.assertFalse(architecture._namespace.Lookup("t").IsVisible)

	def test_Block(self) -> None:
		"""A block's use clause isn't seen by a process beside the block."""
		block =        ConcurrentBlockStatement("blk", declaredItems=[_use("work.p.all")])
		process =      ProcessStatement("proc")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[block, process])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._type, ), block._namespace.Lookup("t").Declarations)
		self.assertFalse(process._namespace.Lookup("t").IsVisible)

	def test_IterateDeclarationRegions(self) -> None:
		"""The architecture, its declared function, then its statements: the block, the process nested in it."""
		function =     _function("f", "T")
		process =      ProcessStatement("proc")
		block =        ConcurrentBlockStatement("blk", statements=[process])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[function], statements=[block])

		self.assertListEqual([architecture, function, block, process], list(architecture.IterateDeclarationRegions()))

	def test_Subprogram(self) -> None:
		"""A subprogram's use clause isn't seen by its parameters, which precede it."""
		function = _function("f", "T")
		function.AddDeclaredItem(_use("work.p.all"))
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[function])
		warnings =     _resolve(_design(self._package, Entity("e"), architecture, analyze=False))

		self.assertTupleEqual((self._type, ), function._namespace.Lookup("t").Declarations)
		self.assertFalse(function._namespace.Lookup("t", function.ParameterItems[0]).IsVisible)
		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], UnresolvedTypeMarkWarning)
		self.assertIs(function.ParameterItems[0].Subtype, warnings[0].Symbol)

	def test_PackageBody(self) -> None:
		"""A use clause in a package body isn't seen by the package declaration."""
		package =     Package("q")
		packageBody = PackageBody(_packageSymbol("q"), declaredItems=[_use("work.p.all")])
		_design(self._package, package, packageBody)

		self.assertTupleEqual((self._type, ), packageBody._namespace.Lookup("t").Declarations)
		self.assertFalse(package._namespace.Lookup("t").IsVisible)

	def test_ContextOfPackage_SeenByBody(self) -> None:
		"""A use clause in the context clause of a package is seen by its body."""
		package =     Package("q", [_use("work.p.all")])
		packageBody = PackageBody(_packageSymbol("q"))
		_design(self._package, package, packageBody)

		self.assertTupleEqual((self._type, ), packageBody._namespace.Lookup("t").Declarations)

	def test_ContextClause_NotNextUnit(self) -> None:
		"""A context clause belongs to one design unit."""
		first =  Entity("e1", [_use("work.p.all")])
		second = Entity("e2")
		_design(self._package, first, second)

		self.assertFalse(second._namespace.Lookup("t").IsVisible)

	def test_ResetAnalysis(self) -> None:
		"""Resetting the analysis removes the imports of nested regions and the references of their use clauses."""
		useClause =    _use("work.p.all")
		process =      ProcessStatement("proc", declaredItems=[useClause])
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[process])
		design =       _design(self._package, Entity("e"), architecture)

		design.ResetAnalysis()

		self.assertDictEqual({}, process._namespace.Imports)
		self.assertIsNone(useClause.Symbols[0].Reference)


class ContextReferences(Testcase):
	"""A context reference makes the declarations of the context's use clauses potentially visible."""

	def test_Context(self) -> None:
		libraryType = _enumeration("T", "a", "b")
		context =     Context("ctx", [LibraryClause([LibraryReferenceSymbol(SimpleName("lib1"))]), _use("lib1.p.all")])
		entity =      Entity("e", [ContextReference([ContextReferenceSymbol(SelectedName("ctx", SimpleName("work")))])])
		_design(context, entity, libraries=[("lib1", [Package("p", declaredItems=[libraryType])])])

		result = entity._namespace.Lookup("t")
		self.assertTupleEqual((libraryType, ), result.Declarations)
		self.assertIs(context.PackageReferences[0], result.Imports[0].UseClause)

	def test_PackageNamedLikeItsLibrary(self) -> None:
		"""``context c is library foo; use foo.foo.all; end context;``: a package may have its library's name."""
		constant = _constant("K", "integer")
		package =  Package("foo", declaredItems=[constant])
		entity =   Entity("e", [_libraryClause("foo"), _contextReference("foo", "c")])
		_design(entity, libraries=[("foo", [package, Context("c", [_libraryClause("foo"), _use("foo.foo.all")])])])

		self.assertDictEqual({"foo": package}, entity.ReferencedPackages["foo"])
		self.assertTupleEqual((constant, ), entity._namespace.Lookup("k").Declarations)

	def test_PackageReferencedTwice(self) -> None:
		"""A package referenced by the design unit's use clause and by a context: ``use lib1.p.all; context lib1.c;``."""
		package = Package("p", declaredItems=[_constant("K", "integer")])
		entity =  Entity("e", [_libraryClause("lib1"), _use("lib1.p.all"), _contextReference("lib1", "c")])
		_design(entity, libraries=[("lib1", [package, Context("c", [_libraryClause("lib1"), _use("lib1.p.all")])])])

		self.assertDictEqual({"p": package}, entity.ReferencedPackages["lib1"])


class ImplicitUseClause(Testcase):
	"""Every primary unit is preceded by ``use std.standard.all;``."""

	def test_StdStandard(self) -> None:
		entity = Entity("e")
		design = _design(entity)
		result = entity._namespace.Lookup("integer")

		self.assertTupleEqual((design.GetPackage("std", "standard").Types["integer"], ), result.Declarations)
		self.assertIsNone(result.Imports[0].UseClause)

	def test_StandardPackageName(self) -> None:
		"""The package name ``standard`` isn't made visible."""
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
		first =  Context("c1", [_libraryClause("lib1"), _use("lib1.p.all")])
		second = Context("c2", [_libraryClause("lib1"), _contextReference("lib1", "c1")])
		entity = Entity("e", [_libraryClause("lib1"), _contextReference("lib1", "c2")])
		_design(entity, libraries=[("lib1", [self._package, first, second])])

		self.assertTupleEqual((self._type, ), entity._namespace.Lookup("t").Declarations)
		self.assertTupleEqual((self._type.Literals[0], ), entity._namespace.Lookup("a").Declarations)

	def test_MissingMember(self) -> None:
		"""``use lib1.p.nothere;`` in a context declaration."""
		useClause = _use("lib1.p.nothere")
		context =   Context("c1", [_libraryClause("lib1"), useClause])

		with WarningCollector() as collector:
			_design(Entity("e"), libraries=[("lib1", [self._package, context])])

		self.assertEqual(1, len(collector.Warnings))
		warning = collector.Warnings[0]
		self.assertIsInstance(warning, UnresolvedNameWarning)
		self.assertEqual("Package 'p' has no declaration 'nothere'.", str(warning))
		self.assertIs(useClause, warning.Place)

	def test_UseClauseAfterContextReference(self) -> None:
		"""``context lib1.ctx;`` imports ``T`` before ``signal s : T;``, a later use clause of ``p`` doesn't hide it."""
		context =      Context("ctx", [_libraryClause("lib1"), _use("lib1.p.all")])
		signal =       _signal("s", "T")
		contextItems = [_libraryClause("lib1"), _contextReference("lib1", "ctx")]
		architecture = Architecture("rtl", _entitySymbol("e"), contextItems, [signal, _use("lib1.p.all")])
		_design(Entity("e"), architecture, libraries=[("lib1", [self._package, context])])

		self.assertTupleEqual((self._type, ), architecture._namespace.Lookup("t", signal).Declarations)


class LibraryNames(Testcase):
	"""
	Only the names ``work`` and ``std`` are implicitly visible, not the real name of the working library (IEEE Std
	1076-2008, 13.2; GHDL: ``no declaration for "lib"``).
	"""

	def setUp(self) -> None:
		self._constant = _constant("K", "integer")
		self._package =  Package("p", declaredItems=[self._constant])

	def test_LibraryClause_Contains(self) -> None:
		"""``library ieee, osvvm;`` names ``ieee`` and ``osvvm``, by normalized identifier."""
		libraryClause = LibraryClause([
			LibraryReferenceSymbol(SimpleName("IEEE")),
			LibraryReferenceSymbol(SimpleName("osvvm"))
		])

		self.assertIn("ieee", libraryClause)
		self.assertIn("osvvm", libraryClause)
		self.assertNotIn("std", libraryClause)

	def test_IsLibraryVisible(self) -> None:
		"""``work`` and ``std`` are visible, a library with a library clause too, not the working library's real name."""
		entity = Entity("e", [_libraryClause("ieee")])
		_design(entity)

		self.assertTrue(entity.IsLibraryVisible("work"))
		self.assertTrue(entity.IsLibraryVisible("std"))
		self.assertTrue(entity.IsLibraryVisible("ieee"))
		self.assertFalse(entity.IsLibraryVisible("lib"))

	def test_IsLibraryVisible_Architecture(self) -> None:
		"""An architecture sees the library clauses of its entity."""
		architecture = Architecture("rtl", _entitySymbol("e"))
		_design(Entity("e", [_libraryClause("ieee")]), architecture)

		self.assertTrue(architecture.IsLibraryVisible("ieee"))

	def test_IsLibraryVisible_Context(self) -> None:
		"""A context declaration has no implicit ``library std;`` (13.2)."""
		context = Context("c")
		_design(context)

		self.assertTrue(context.IsLibraryVisible("work"))
		self.assertFalse(context.IsLibraryVisible("std"))

	def test_UseClause_NoLibraryClause(self) -> None:
		"""``use lib.p.all;`` in library ``lib``."""
		with self.assertRaises(UseClauseLibraryNotVisibleError) as context:
			_design(self._package, Entity("e", [_use("lib.p.all")]))

		self.assertEqual(
			"Use clause references library 'lib', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertListEqual(["Add a library clause like: 'library lib;'."], context.exception.__notes__)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_UseClause_LibraryClause(self) -> None:
		"""``library lib; use lib.p.all;`` in library ``lib``."""
		entity = Entity("e", [_libraryClause("lib"), _use("lib.p.all")])
		_design(self._package, entity)

		self.assertTupleEqual((self._constant, ), entity._namespace.Lookup("k").Declarations)
		self.assertDictEqual({"p": self._package}, entity.ReferencedPackages["lib"])

	def test_UseClause_Work(self) -> None:
		"""``use work.p.all;`` in library ``lib``."""
		entity = Entity("e", [_use("work.p.all")])
		_design(self._package, entity)

		self.assertTupleEqual((self._constant, ), entity._namespace.Lookup("k").Declarations)

	def test_UseClause_DeclarativePart(self) -> None:
		"""``architecture rtl of e is use lib.p.all;`` in library ``lib``."""
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("lib.p.all")])

		with self.assertRaises(UseClauseLibraryNotVisibleError) as context:
			_design(self._package, Entity("e"), architecture)

		self.assertEqual(
			"Use clause references library 'lib', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_UseClause_LibraryClauseOfPrimaryUnit(self) -> None:
		"""``library lib; entity e ...; architecture rtl of e is use lib.p.all;`` (GHDL accepts)."""
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("lib.p.all")])
		_design(self._package, Entity("e", [_libraryClause("lib")]), architecture)

		self.assertTupleEqual((self._constant, ), architecture._namespace.Lookup("k").Declarations)

	def test_UseClause_LibraryClauseOfContext(self) -> None:
		"""``context c is library lib; end context; context work.c; use lib.p.all;`` (GHDL accepts)."""
		entity = Entity("e", [_contextReference("work", "c"), _use("lib.p.all")])
		_design(self._package, Context("c", [_libraryClause("lib")]), entity)

		self.assertTupleEqual((self._constant, ), entity._namespace.Lookup("k").Declarations)
		self.assertDictEqual({"p": self._package}, entity.ReferencedPackages["lib"])

	def test_UseClause_LibraryClauseOfNestedContext(self) -> None:
		"""``c2`` references ``c1``, which has ``library lib1;``; ``context work.c2; use lib1.p.all;`` (GHDL accepts)."""
		first =  Context("c1", [_libraryClause("lib1")])
		second = Context("c2", [_libraryClause("lib"), _contextReference("lib", "c1")])
		entity = Entity("e", [_contextReference("work", "c2"), _use("lib1.p.all")])
		_design(first, second, entity, libraries=[("lib1", [self._package])])

		self.assertTupleEqual((self._constant, ), entity._namespace.Lookup("k").Declarations)

	def test_UseAll_NoLibraryClause(self) -> None:
		"""``use lib.all;`` in library ``lib``: the prefix isn't visible."""
		entity = Entity("e", [_use("lib.all")])

		with WarningCollector() as collector:
			_design(self._package, entity)

		self.assertEqual(1, len(collector.Warnings))
		self.assertIsInstance(collector.Warnings[0], UnresolvedNameWarning)
		self.assertEqual("Prefix 'lib' of use clause 'lib.all' isn't a visible package.", str(collector.Warnings[0]))

	def test_UseUnit_NoLibraryClause(self) -> None:
		"""``use lib.p;`` in library ``lib``: the prefix isn't visible."""
		entity = Entity("e", [_use("lib.p")])

		with self.assertRaises(UseClauseLibraryNotVisibleError) as context:
			_design(self._package, entity)

		self.assertEqual(
			"Use clause references library 'lib', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_UseStd_NoLibraryClause(self) -> None:
		"""``use std.textio.all;`` in an entity."""
		entity = Entity("e", [_use("std.textio.all")])
		_design(entity)

		self.assertTrue(entity._namespace.Lookup("line").IsVisible)

	def test_ContextDeclaration_UseStd_NoLibraryClause(self) -> None:
		"""``context c is use std.textio.all; end context;``: a context has no implicit ``library std;`` (13.2)."""
		with self.assertRaises(UseClauseLibraryNotVisibleError) as context:
			_design(Context("c", [_use("std.textio.all")]))

		self.assertEqual(
			"Use clause references library 'std', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertListEqual(["Add a library clause like: 'library std;'."], context.exception.__notes__)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextDeclaration_UseStd_LibraryClause(self) -> None:
		"""``context c is library std; use std.textio.all; end context;``."""
		referencedContext = Context("c", [_libraryClause("std"), _use("std.textio.all")])
		design =            _design(referencedContext)

		self.assertDictEqual(
			{"textio": design.GetLibrary("std")._packages["textio"]},
			referencedContext.ReferencedPackages["std"]
		)

	def test_ContextDeclaration_NestedLibraryNotInDesign(self) -> None:
		"""``c0`` references ``c1``, which has ``library nolib;``; ``c0`` uses ``nolib.p.all``."""
		first =  Context("c0", [_libraryClause("lib"), _contextReference("lib", "c1"), _use("nolib.p.all")])
		second = Context("c1", [_libraryClause("nolib")])

		with self.assertRaises(LibraryNotFoundError) as context:
			_design(first, second)

		self.assertEqual("Library 'nolib' not found in design.", str(context.exception))
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, LibraryNotInDesignError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextDeclaration_LibraryClauseNotInDesign(self) -> None:
		"""``context c is library nolib; end context;``: the library doesn't exist."""
		with self.assertRaises(ReferencedLibraryNotExistingError) as context:
			_design(Context("c", [_libraryClause("nolib")]))

		self.assertEqual(
			"Library 'nolib' referenced by library clause of context 'c' doesn't exist in design.",
			str(context.exception)
		)
		self.assertEqual("nolib", context.exception.LibraryName)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, LibraryNotInDesignError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_LibraryClause_NotInDesign(self) -> None:
		"""``library nolib; entity e ...;``: the library doesn't exist."""
		entity = Entity("e", [_libraryClause("nolib")])

		with self.assertRaises(LibraryClauseLibraryNotFoundError) as context:
			_design(entity)

		self.assertEqual(
			"Library 'nolib' referenced by library clause of design unit 'e' doesn't exist in design.",
			str(context.exception)
		)
		self.assertListEqual(["Known libraries: 'std', 'ieee', 'lib'"], context.exception.__notes__)
		self.assertEqual("nolib", context.exception.LibraryName)
		self.assertIs(entity, context.exception.DesignUnit)
		self.assertIs(entity._libraryReferences[0]._symbols[0], context.exception.LibrarySymbol)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, LibraryNotInDesignError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextDeclaration_NoLibraryClause(self) -> None:
		"""``context c is use lib.p.all; end context;`` in library ``lib``."""
		with self.assertRaises(UseClauseLibraryNotVisibleError) as context:
			_design(self._package, Context("c", [_use("lib.p.all")]))

		self.assertEqual(
			"Use clause references library 'lib', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertListEqual(["Add a library clause like: 'library lib;'."], context.exception.__notes__)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextReference_NoLibraryClause(self) -> None:
		"""``context lib.c;`` in library ``lib``."""
		with self.assertRaises(ContextReferenceLibraryNotVisibleError) as context:
			_design(Context("c"), Entity("e", [_contextReference("lib", "c")]))

		self.assertEqual(
			"Context reference references library 'lib', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertListEqual(["Add a library clause like: 'library lib;'."], context.exception.__notes__)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextReference_LibraryClause(self) -> None:
		"""``library lib; context lib.c;`` in library ``lib``."""
		referencedContext = Context("c")
		entity =            Entity("e", [_libraryClause("lib"), _contextReference("lib", "c")])
		_design(referencedContext, entity)

		self.assertDictEqual({"c": referencedContext}, entity.ReferencedContexts["lib"])

	def test_ContextReference_Architecture(self) -> None:
		"""``context work.c;`` in the context clause of an architecture (GHDL accepts)."""
		referencedContext = Context("c", [_libraryClause("ieee")])
		architecture =      Architecture("rtl", _entitySymbol("e"), [_contextReference("work", "c")])
		_design(referencedContext, Entity("e"), architecture)

		self.assertDictEqual({"c": referencedContext}, architecture.ReferencedContexts["lib"])

	def test_ContextReference_KeepsReferencedPackages(self) -> None:
		"""A context reference keeps the packages the design unit's use clauses referenced before."""
		entity = Entity(
			"e",
			[_libraryClause("ieee"), _use("ieee.std_logic_1164.all"), _use("work.p.all"), _contextReference("work", "c")]
		)
		design = _design(self._package, Context("c", [_libraryClause("ieee")]), entity)

		self.assertDictEqual({"p": self._package}, entity.ReferencedPackages["lib"])
		self.assertDictEqual(
			{"std_logic_1164": design.GetLibrary("ieee")._packages["std_logic_1164"]},
			entity.ReferencedPackages["ieee"]
		)

	def test_PackageInstantiation_NoLibraryClause(self) -> None:
		"""``package i is new lib.gp generic map (...);`` in library ``lib``."""
		genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")])
		instantiation =  PackageInstantiation("i", PackageReferenceSymbol(SelectedName("gp", SimpleName("lib"))))

		with self.assertRaises(PackageInstantiationLibraryNotVisibleError) as context:
			_design(genericPackage, instantiation)

		self.assertEqual(
			"Package instantiation of 'i' references library 'lib', which was not referenced by a library clause.",
			str(context.exception)
		)
		self.assertListEqual(["Add a library clause like: 'library lib;'."], context.exception.__notes__)
		self.assertEqual("lib", context.exception.LibraryName)
		self.assertIs(instantiation, context.exception.DesignUnit)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_PackageInstantiation_LibraryClause(self) -> None:
		"""``library lib; package i is new lib.gp generic map (...);`` in library ``lib``."""
		genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")])
		symbol =         PackageReferenceSymbol(SelectedName("gp", SimpleName("lib")))
		_design(genericPackage, PackageInstantiation("i", symbol, [_libraryClause("lib")]))

		self.assertIs(genericPackage, symbol.Package)

	def test_PackageInstantiation_NotInDesign(self) -> None:
		"""``package i is new nolib.gp generic map (...);``: the library doesn't exist."""
		instantiation = PackageInstantiation("i", PackageReferenceSymbol(SelectedName("gp", SimpleName("nolib"))))

		with self.assertRaises(PackageInstantiationLibraryNotFoundError) as context:
			_design(instantiation)

		self.assertEqual(
			"Package instantiation of 'i' references library 'nolib', which cannot be found in design.",
			str(context.exception)
		)
		self.assertEqual("nolib", context.exception.LibraryName)
		self.assertIs(instantiation, context.exception.PackageInstantiation)
		self.assertIsInstance(context.exception, LibraryNotInDesignError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_EntityInstantiation_NoLibraryClause(self) -> None:
		"""``inst: entity lib.e1;`` in library ``lib``."""
		instantiation = EntityInstantiation("inst", EntityInstantiationSymbol(SelectedName("e1", SimpleName("lib"))))
		architecture =  Architecture("rtl", _entitySymbol("e2"), statements=[instantiation])

		with self.assertRaises(EntityInstantiationLibraryNotVisibleError) as context:
			_design(Entity("e1"), Entity("e2"), architecture)

		self.assertEqual(
			f"Referenced library 'lib' in direct entity instantiation 'inst: entity lib.e1' not found in architecture "
			f"'{architecture!r}'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Add a library reference to the architecture or entity using a library clause like: 'library lib;'."],
			context.exception.__notes__
		)
		self.assertEqual("lib", context.exception.LibraryName)
		self.assertIs(architecture, context.exception.DesignUnit)
		self.assertIs(instantiation, context.exception.Instantiation)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_EntityInstantiation_NotInDesign(self) -> None:
		"""``library nolib; entity e2 ...; inst: entity nolib.e1;``: linking instantiations before library clauses."""
		instantiation = EntityInstantiation("inst", EntityInstantiationSymbol(SelectedName("e1", SimpleName("nolib"))))
		architecture =  Architecture("rtl", _entitySymbol("e2"), statements=[instantiation])
		design =        _design(Entity("e2", [_libraryClause("nolib")]), architecture, analyze=False)
		design.CreateDependencyGraph()
		design.IndexArchitectures()
		design.LinkArchitectures()

		with self.assertRaises(EntityInstantiationLibraryNotFoundError) as context:
			design.LinkInstantiations()

		self.assertEqual(
			"Referenced library 'nolib' in direct entity instantiation 'inst: entity nolib.e1' not found in design.",
			str(context.exception)
		)
		self.assertListEqual(
			["No design units were parsed into library 'nolib'. Thus it doesn't exist in design."],
			context.exception.__notes__
		)
		self.assertEqual("nolib", context.exception.LibraryName)
		self.assertIs(instantiation, context.exception.Instantiation)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, LibraryNotInDesignError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_EntityInstantiation_LibraryClause(self) -> None:
		"""``library lib; entity e2 ...; inst: entity lib.e1;`` in library ``lib``."""
		instantiation = EntityInstantiation("inst", EntityInstantiationSymbol(SelectedName("e1", SimpleName("lib"))))
		architecture =  Architecture("rtl", _entitySymbol("e2"), statements=[instantiation])
		entity =        Entity("e1")
		_design(entity, Entity("e2", [_libraryClause("lib")]), architecture)

		self.assertIs(entity, instantiation.Entity.Entity)


class UseClauseDiagnostics(Testcase):
	"""Use clauses, which name nothing usable, are an :exc:`~pyVHDLModel.Exception.UnresolvedNameWarning`."""

	def test_PrefixNotAPackage(self) -> None:
		"""``use K.all;`` with a constant ``K``."""
		useClause = _use("k.all")
		entity =    Entity("e", declaredItems=[_constant("K", "integer"), useClause])

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
		"""``use work.gp.all;`` with an uninstantiated generic package."""
		constant =       _constant("K", "integer")
		genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")], declaredItems=[constant])
		entity =         Entity("e", [_use("work.gp.all")])

		with WarningCollector() as collector:
			_design(genericPackage, entity)

		self.assertEqual(1, len(collector.Warnings))
		self.assertEqual(
			"Use clause 'work.gp.all' names the uninstantiated generic package 'gp'.",
			str(collector.Warnings[0])
		)
		self.assertFalse(entity._namespace.Lookup("k").IsVisible)


class DesignUnitsNotFound(Testcase):
	"""A use clause, a context reference or a package instantiation naming a design unit, which doesn't exist."""

	def test_UseClause(self) -> None:
		"""``library lib; use lib.nothere.all;``."""
		entity = Entity("e", [_libraryClause("lib"), _use("lib.nothere.all")])

		with self.assertRaises(PackageNotFoundError) as context:
			_design(entity)

		self.assertEqual("Package 'nothere' not found in library 'lib'.", str(context.exception))
		self.assertListEqual(
			[f"Caused in design unit '{entity}' in file '{entity.Document}'."],
			context.exception.__notes__
		)
		self.assertEqual("nothere", context.exception.DesignUnitName)
		self.assertEqual("lib", context.exception.LibraryName)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_UseClause_Work(self) -> None:
		"""``use work.nothere.all;`` in library ``lib``."""
		entity = Entity("e", [_use("work.nothere.all")])

		with self.assertRaises(PackageNotFoundError) as context:
			_design(entity)

		self.assertEqual("Package 'nothere' not found in working library 'lib'.", str(context.exception))
		self.assertListEqual(
			[
				"Library 'work' is the working library 'lib'.",
				f"Caused in design unit '{entity}' in file '{entity.Document}'."
			],
			context.exception.__notes__
		)

	def test_ContextDeclaration_UseClause_Work(self) -> None:
		"""``context c is use work.nothere.all; end context;`` in library ``lib``."""
		with self.assertRaises(PackageNotFoundError) as context:
			_design(Context("c", [_use("work.nothere.all")]))

		self.assertEqual("Package 'nothere' not found in working library 'lib'.", str(context.exception))
		self.assertListEqual(["Library 'work' is the working library 'lib'."], context.exception.__notes__)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextReference_Work(self) -> None:
		"""``context work.nothere;`` in library ``lib``."""
		with self.assertRaises(ContextNotFoundError) as context:
			_design(Entity("e", [_contextReference("work", "nothere")]))

		self.assertEqual("Context 'nothere' not found in working library 'lib'.", str(context.exception))
		self.assertListEqual(["Library 'work' is the working library 'lib'."], context.exception.__notes__)
		self.assertEqual("nothere", context.exception.DesignUnitName)
		self.assertEqual("lib", context.exception.LibraryName)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_PackageInstantiation_Work(self) -> None:
		"""``package i is new work.nothere generic map (...);`` in library ``lib``."""
		instantiation = PackageInstantiation("i", PackageReferenceSymbol(SelectedName("nothere", SimpleName("work"))))

		with self.assertRaises(PackageNotFoundError) as context:
			_design(instantiation)

		self.assertEqual("Package 'nothere' not found in working library 'lib'.", str(context.exception))
		self.assertListEqual(
			[
				"Library 'work' is the working library 'lib'.",
				f"Caused in library '{instantiation.Library}' in file '{instantiation.Document}'."
			],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, KeyError)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)


class GenericPackages(Testcase):
	"""A package instantiation referencing a package, which isn't a generic package."""

	def test_NotAGenericPackage(self) -> None:
		"""``package i is new work.p generic map (...);`` with a package ``p`` without generics."""
		package =       Package("p")
		instantiation = PackageInstantiation("i", PackageReferenceSymbol(SelectedName("p", SimpleName("work"))))

		with self.assertRaises(NotAGenericPackageError) as context:
			_design(package, instantiation)

		self.assertEqual("Package 'work.p' referenced by 'lib.i' is not a generic package.", str(context.exception))
		self.assertIs(instantiation, context.exception.PackageInstantiation)
		self.assertIs(package, context.exception.Package)
		self.assertIsInstance(context.exception, VHDLModelException)


class SymbolKinds(Testcase):
	"""A use clause with a symbol, which isn't a package reference symbol the model supports."""

	def test_UseClause(self) -> None:
		"""A use clause of an entity with a library reference symbol."""
		symbol = LibraryReferenceSymbol(SimpleName("lib"))

		with self.assertRaises(UnknownSymbolKindError) as context:
			_design(Entity("e", [UseClause([symbol])]))

		self.assertEqual("Unknown package reference symbol type in design unit 'e'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Symbol.LibraryReferenceSymbol'."],
			context.exception.__notes__
		)
		self.assertIs(symbol, context.exception.Element)
		self.assertEqual("e", context.exception.DesignUnit.Identifier)
		self.assertIsInstance(context.exception, UnknownKindError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_ContextDeclaration(self) -> None:
		"""A use clause of a context declaration with a package reference symbol naming a package member."""
		symbol = PackageReferenceSymbol(SelectedName("x", SelectedName("p", SimpleName("work"))))

		with self.assertRaises(UnknownSymbolKindError) as context:
			_design(Package("p"), Context("c", [UseClause([symbol])]))

		self.assertEqual("Unknown package reference symbol type in design unit 'c'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Symbol.PackageReferenceSymbol'."],
			context.exception.__notes__
		)
		self.assertIs(symbol, context.exception.Element)
		self.assertIsInstance(context.exception, UnknownKindError)
		self.assertIsInstance(context.exception, VHDLModelException)


class UseItemSubtype(Testcase):
	"""``use work.p.ST;`` with a subtype of an enumerated type brings the base type's literals along."""

	def test_UserSubtype(self) -> None:
		enumeration = _enumeration("T", "a", "b")
		first =       Subtype("ST1", _subtypeSymbol("T"))
		second =      Subtype("ST2", _subtypeSymbol("ST1"))
		entity =      Entity("e", [_use("work.p.ST2")])
		_design(Package("p", declaredItems=[enumeration, first, second]), entity)

		self.assertTupleEqual((enumeration.Literals[1], ), entity._namespace.Lookup("b").Declarations)


class PackageDeclarations(Testcase):
	"""The declarations of a package a use clause can make potentially visible."""

	def test_IterateDeclarations(self) -> None:
		"""A declared item, then the enumeration literals of an enumerated type."""
		constant =   _constant("K", "integer")
		enumerated = _enumeration("T", "a", "'b'")
		package =    Package("p", declaredItems=[constant, enumerated])

		self.assertListEqual(
			[("k", constant), ("t", enumerated), ("a", enumerated.Literals[0]), ("'b'", enumerated.Literals[1])],
			list(package.IterateDeclarations())
		)

	def test_IterateMemberDeclarations(self) -> None:
		"""The member with its identifier, and the enumeration literals of a type."""
		enumerated = _enumeration("T", "a")
		package =    Package("p", declaredItems=[_constant("K", "integer"), enumerated])

		self.assertListEqual(
			[("t", enumerated), ("a", enumerated.Literals[0])],
			list(package.IterateMemberDeclarations("t"))
		)


class LinkingOrder(Testcase):
	"""Linking steps called out of order raise an exception with a message."""

	def test_PackageInstantiation_NotLinked(self) -> None:
		"""The declarations of a package instantiation, which isn't linked to its generic package."""
		instantiation = PackageInstantiation("inst", PackageReferenceSymbol(SelectedName("gp", SimpleName("work"))))

		with self.assertRaises(PackageInstantiationNotLinkedError) as context:
			list(instantiation.IterateDeclarations())

		self.assertEqual(
			"Package instantiation 'inst' isn't linked to its generic package 'work.gp'.",
			str(context.exception)
		)
		self.assertListEqual(["Call 'LinkPackageInstances()' before linking use clauses."], context.exception.__notes__)
		self.assertIsInstance(context.exception, InstantiationNotLinkedError)
		self.assertIsInstance(context.exception, VHDLModelException)
		self.assertEqual("inst", context.exception.InstantiationName)
		self.assertEqual("work.gp", context.exception.GenericName)

	def test_LinkPackageReferences_WithoutLibraries(self) -> None:
		"""``LinkPackageReferences()`` before ``LinkLibraryReferences()``."""
		design =   Design("design")
		document = Document(Path("design.vhdl"))
		document._AddDesignUnit(Entity("e"))
		design.AddDocument(document, design.GetLibrary("lib"))
		design.CreateDependencyGraph()

		with self.assertRaises(LibraryReferenceNotLinkedError) as context:
			design.LinkPackageReferences()

		self.assertEqual("Design unit 'e' doesn't reference library 'std'.", str(context.exception))
		self.assertListEqual(
			[
				"Every primary unit references library 'std' implicitly.",
				"Call 'LinkLibraryReferences()' before 'LinkPackageReferences()'."
			],
			context.exception.__notes__
		)
		self.assertEqual("std", context.exception.LibraryName)
		self.assertEqual("e", context.exception.DesignUnit.Identifier)
		self.assertIsInstance(context.exception, NotLinkedError)
		self.assertIsInstance(context.exception, VHDLModelException)


class ContextGenericPackage(Testcase):
	"""A use clause of a context declaration naming an uninstantiated generic package."""

	def test_Warning(self) -> None:
		constant =       _constant("K", "integer")
		genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")], declaredItems=[constant])
		context =        Context("c1", [_libraryClause("lib1"), _use("lib1.gp.all")])
		entity =         Entity("e", [_libraryClause("lib1"), _contextReference("lib1", "c1")])

		with WarningCollector() as collector:
			_design(entity, libraries=[("lib1", [genericPackage, context])])

		self.assertEqual(1, len(collector.Warnings))
		self.assertEqual(
			"Use clause 'lib1.gp.all' names the uninstantiated generic package 'gp'.",
			str(collector.Warnings[0])
		)
		self.assertFalse(entity._namespace.Lookup("k").IsVisible)
