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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
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
"""Analysis tests for the language model."""
from pathlib import Path

from pyVHDLModel import DependencyGraphVertexKind, Design, Document, VHDLModelException
from pyVHDLModel.Name import Name, SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol import LibraryReferenceSymbol, PackageReferenceSymbol, AllPackageMembersReferenceSymbol, \
                               ContextReferenceSymbol, EntitySymbol, PackageSymbol, EntityInstantiationSymbol, \
                               SimpleSubtypeSymbol, Symbol, PossibleReference, ComponentInstantiationSymbol
from pyVHDLModel.DesignUnit import DesignUnit, Package, PackageBody, Context, Entity, Architecture, Configuration, \
                                   Component, LibraryClause, UseClause, ContextReference
from pyVHDLModel.Configuration import BlockConfiguration
from pyVHDLModel.Concurrent import EntityInstantiation, ComponentInstantiation
from pyVHDLModel.Object import Variable
from pyVHDLModel.Exception import NotImplementedWarning, BlackboxWarning, DuplicateDeclarationWarning, \
                                  LibraryNotFoundError, PackageNotFoundError, LibraryNotVisibleError, \
                                  EntityInstantiationLibraryNotVisibleError, DesignUnitNotFoundError, \
                                  ComponentEntityNotFoundError, InstantiatedEntityNotFoundError, \
                                  ArchitectureEntityNotFoundError, PackageBodyPackageNotFoundError, NotLinkedError, \
                                  UseClauseNotLinkedError, NotComputedError, HierarchyNotComputedError, \
                                  CompileOrderNotComputedError

from pyTooling.Warning         import UnhandledCriticalWarningError, WarningCollector
from pyTooling.Testing         import Testcase

from tests.unit                import _warningsOfType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VHDLLibrary(Testcase):
	def CreateDesign(self) -> Design:
		design = Design("example")
		library = design.GetLibrary("lib_1")

		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Library' class.", parent=None)

		contextReferences = [
			LibraryClause([
				LibraryReferenceSymbol(SimpleName("ieee")),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(AllName(SelectedName("std_logic_1164", SimpleName("ieee")))),
			])
		]
		context = Context("ctx_1", contextReferences, documentation="My first context.", parent=None)
		document._AddDesignUnit(context)

		entityAReferences = [
			# UseClause([
			# 	PackageMemberReferenceSymbol("Stop", PackageReferenceSymbol("env", LibraryReferenceSymbol("std"))),
			# ]),
			LibraryClause([
				LibraryReferenceSymbol(SimpleName("ieee")),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(AllName(SelectedName("numeric_std", SimpleName("ieee")))),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(AllName(SelectedName("pack_1", SimpleName("work")))),
			])
		]
		entityA = Entity("entity_A", entityAReferences, documentation="My first entity.", parent=None)
		document._AddDesignUnit(entityA)

		architectureAReferences = [
			UseClause([
				AllPackageMembersReferenceSymbol(AllName(SelectedName("textio", SimpleName("std")))),
			]),
		]
		architectureA = Architecture("arch_A", EntitySymbol(SimpleName("entity_A")), architectureAReferences, documentation="My first entity implementation.",
																 parent=None)
		document._AddDesignUnit(architectureA)

		entityBReferences = [
			LibraryClause([
				LibraryReferenceSymbol(SimpleName("lib_1")),
			]),
			ContextReference([
				ContextReferenceSymbol(SelectedName("ctx_1", SimpleName("work"))),
			]),
		]
		entityB = Entity("entity_B", entityBReferences, documentation="My second entity.", parent=None)
		document._AddDesignUnit(entityB)

		architectureBStatements = [
			EntityInstantiation("instWork", EntityInstantiationSymbol(SelectedName("entity_A", SimpleName("work")))),
			EntityInstantiation("instLib", EntityInstantiationSymbol(SelectedName("entity_A", SimpleName("lib_1")))),
		]
		architectureB = Architecture("arch_B", EntitySymbol(SimpleName("entity_B")), None, None, architectureBStatements,
																 documentation="My second entity implementation.", parent=None)
		document._AddDesignUnit(architectureB)

		packageReferences = [
			ContextReference([
				ContextReferenceSymbol(SelectedName("ctx_1", SimpleName("work"))),
			]),
		]
		package = Package("pack_1", packageReferences, documentation="My first utility package.", parent=None)
		document._AddDesignUnit(package)

		packageBody = PackageBody(PackageSymbol(SimpleName("pack_1")), parent=None)
		document._AddDesignUnit(packageBody)

		configuration = Configuration(
			"cfg_1",
			EntitySymbol(SimpleName("entity_A")),
			BlockConfiguration(Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label)),
			parent=None
		)
		document._AddDesignUnit(configuration)

		design.AddDocument(document, library)

		design.LoadStdLibrary()
		design.LoadIEEELibrary()

		return design

	def test_DependencyGraph(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()

		self.assertEqual(39, design.DependencyGraph.VertexCount)

	def test_LinkContexts(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkContexts()

	def test_LinkArchitectures(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()

	def test_LinkPackageBodies(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkPackageBodies()

	def test_LinkLibraryReferences(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		design.LinkLibraryReferences()

	def test_LinkPackageReferences(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		design.LinkLibraryReferences()
		design.LinkPackageReferences()

	def test_LinkContextReferences(self) -> None:
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkContexts()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		design.LinkLibraryReferences()
		design.LinkPackageReferences()
		design.LinkContextReferences()

	def test_IndexPackages(self) -> None:
		design = self.CreateDesign()

		design.IndexPackages()

	def test_IndexArchitectures(self) -> None:
		design = self.CreateDesign()

		design.IndexArchitectures()

	def test_LinkInstantiations(self) -> None:
		design = self.CreateDesign()

		design.LinkInstantiations()

	def test_CreateHierarchyGraph(self) -> None:
		design = self.CreateDesign()

		design.CreateHierarchyGraph()

	def test_Analyze(self) -> None:
		design = self.CreateDesign()

		design.Analyze()


class LinkInstantiations(Testcase):
	@staticmethod
	def _designWithEntityInstantiation(entityName: Name) -> Design:
		design = Design("example")
		library = design.GetLibrary("lib_1")

		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(Entity("entity_A", parent=None))
		document._AddDesignUnit(Architecture("arch_A", EntitySymbol(SimpleName("entity_A")), parent=None))
		document._AddDesignUnit(Entity("entity_B", parent=None))

		statements = [EntityInstantiation("inst", EntityInstantiationSymbol(entityName))]
		architecture = Architecture("arch_B", EntitySymbol(SimpleName("entity_B")), statements=statements, parent=None)
		document._AddDesignUnit(architecture)

		design.AddDocument(document, library)
		design.LoadStdLibrary()
		design.LoadIEEELibrary()

		return design

	def test_EntityInstantiation_WorkLibrary(self) -> None:
		design = self._designWithEntityInstantiation(SelectedName("entity_A", SimpleName("work")))

		design.Analyze()

		library = design.Libraries["lib_1"]
		instance = library.Architectures["entity_b"]["arch_b"].Statements[0]
		self.assertIs(library.Entities["entity_a"], instance.Entity.Entity)

	def test_EntityInstantiation_NoLibraryPrefix(self) -> None:
		design = self._designWithEntityInstantiation(SimpleName("entity_A"))

		with self.assertRaises(VHDLModelException) as context:
			design.Analyze()

		self.assertEqual("Direct entity instantiation 'inst' has no library prefix.", str(context.exception))
		self.assertEqual(
			["Use a selected name like 'work.entity_A'.", "Entities made visible by a use clause aren't supported."],
			context.exception.__notes__
		)

	def test_EntityInstantiation_LibraryNotReferenced(self) -> None:
		design = self._designWithEntityInstantiation(SelectedName("entity_A", SimpleName("lib_2")))

		with self.assertRaises(EntityInstantiationLibraryNotVisibleError) as context:
			design.Analyze()

		self.assertEqual(
			"Referenced library 'lib_2' in direct entity instantiation 'inst: entity lib_2.entity_A' not found in "
			"architecture 'lib_1.entity_B(arch_B)'.",
			str(context.exception)
		)
		self.assertIsInstance(context.exception, LibraryNotVisibleError)
		self.assertIsInstance(context.exception, VHDLModelException)

	def test_EntityInstantiation_EntityNotFound(self) -> None:
		design = self._designWithEntityInstantiation(SelectedName("entity_C", SimpleName("work")))

		with self.assertRaises(InstantiatedEntityNotFoundError) as context:
			design.Analyze()

		self.assertEqual(
			"Referenced entity 'entity_C' in direct entity instantiation 'inst: entity work.entity_C' not found in "
			"working library 'lib_1'.",
			str(context.exception)
		)
		self.assertEqual("entity_C", context.exception.DesignUnitName)
		self.assertEqual("lib_1", context.exception.LibraryName)
		self.assertEqual("inst", context.exception.Instantiation.Label)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)


class StdLibraryNotLoaded(Testcase):
	"""The implicit ``library std; use std.standard.all;`` needs the predefined library."""

	@staticmethod
	def _design(*designUnits: DesignUnit) -> Design:
		design =   Design("example")
		document = Document(Path("tests.vhdl"), parent=None)
		for designUnit in designUnits:
			document._AddDesignUnit(designUnit)

		design.AddDocument(document, design.GetLibrary("lib_1"))

		return design

	def test_Library(self) -> None:
		design = self._design(Entity("entity_A", parent=None))

		with self.assertRaises(LibraryNotFoundError) as context:
			design.Analyze()

		self.assertEqual("Library 'std' not found in design.", str(context.exception))
		self.assertListEqual(["Call 'LoadStdLibrary()' before analyzing a design."], context.exception.__notes__)
		self.assertEqual("std", context.exception.LibraryName)
		self.assertIsInstance(context.exception.__cause__, KeyError)

	def test_Package(self) -> None:
		design = self._design(Entity("entity_A", parent=None))
		design.GetLibrary("std")

		with self.assertRaises(PackageNotFoundError) as context:
			design.Analyze()

		self.assertEqual("Package 'standard' not found in library 'std'.", str(context.exception))
		self.assertListEqual(["Call 'LoadStdLibrary()' before analyzing a design."], context.exception.__notes__)
		self.assertEqual("standard", context.exception.DesignUnitName)
		self.assertEqual("std", context.exception.LibraryName)
		self.assertIsInstance(context.exception.__cause__, KeyError)


class LinkLibraryReferences(Testcase):
	"""The libraries a design unit references implicitly."""

	@staticmethod
	def _libraryEdges(designUnit: DesignUnit) -> list[str]:
		return sorted(
			edge.Destination.Value.NormalizedIdentifier
			for edge in designUnit.DependencyVertex.IterateOutboundEdges()
			if edge.Destination["kind"] is DependencyGraphVertexKind.Library
		)

	def test_WorkingLibrary(self) -> None:
		design =   Design("example")
		library =  design.GetLibrary("lib_1")
		entity =   Entity("entity_A", parent=None)
		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(entity)
		design.AddDocument(document, library)
		design.LoadStdLibrary()

		design.Analyze()

		self.assertDictEqual({"std": design.GetLibrary("std"), "lib_1": library}, entity.ReferencedLibraries)
		self.assertListEqual(["lib_1", "std"], self._libraryEdges(entity))

	def test_LibraryStd(self) -> None:
		"""A primary unit in library ``std`` references ``std`` once."""
		design =  Design("example")
		library = design.LoadStdLibrary()

		design.Analyze()

		for package in library.Packages.values():
			self.assertDictEqual({"std": library}, package.ReferencedLibraries)
			self.assertListEqual(["std"], self._libraryEdges(package))

	def test_SecondaryUnit(self) -> None:
		"""An architecture inherits the referenced libraries of its entity, and keeps its own."""
		design =           Design("example")
		library =          design.GetLibrary("lib_1")
		ieee =             design.LoadIEEELibrary()
		std =              design.LoadStdLibrary()
		entityReferences = [LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])]
		architecture =     Architecture("arch_A", EntitySymbol(SimpleName("entity_A")), parent=None)
		document =         Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(Entity("entity_A", entityReferences, parent=None))
		document._AddDesignUnit(architecture)
		design.AddDocument(document, library)

		design.Analyze()

		self.assertDictEqual({"std": std, "lib_1": library, "ieee": ieee}, architecture.ReferencedLibraries)
		self.assertIsNot(architecture.Entity.Entity.ReferencedLibraries, architecture.ReferencedLibraries)


class LinkContextReferences(Testcase):
	"""A context hands its references to the units referencing it, among them contexts."""

	def test_NestedContexts(self) -> None:
		"""``entity_A`` references ``ctx_2``, which references ``ctx_1``, which uses ``ieee.std_logic_1164.all``."""
		design =  Design("example")
		library = design.GetLibrary("lib_1")
		ieee =    design.LoadIEEELibrary()
		design.LoadStdLibrary()

		first = Context(
			"ctx_1",
			[
				LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))]),
				UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName("std_logic_1164", SimpleName("ieee"))))])
			],
			parent=None
		)
		second = Context(
			"ctx_2",
			[ContextReference([ContextReferenceSymbol(SelectedName("ctx_1", SimpleName("work")))])],
			parent=None
		)
		entity = Entity(
			"entity_A",
			[ContextReference([ContextReferenceSymbol(SelectedName("ctx_2", SimpleName("work")))])],
			parent=None
		)
		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(first)
		document._AddDesignUnit(second)
		document._AddDesignUnit(entity)
		design.AddDocument(document, library)

		design.Analyze()

		package = ieee.Packages["std_logic_1164"]
		self.assertIs(ieee, second.ReferencedLibraries["ieee"])
		self.assertDictEqual({"std_logic_1164": package}, second.ReferencedPackages["ieee"])
		self.assertIs(ieee, entity.ReferencedLibraries["ieee"])
		self.assertDictEqual({"std_logic_1164": package}, entity.ReferencedPackages["ieee"])

	def test_UseClauseNotLinked(self) -> None:
		"""``LinkContextReferences()`` before ``LinkContexts()``."""
		design =  Design("example")
		library = design.GetLibrary("lib_1")
		design.LoadIEEELibrary()
		design.LoadStdLibrary()

		symbol =  AllPackageMembersReferenceSymbol(AllName(SelectedName("std_logic_1164", SimpleName("ieee"))))
		context = Context(
			"ctx_1",
			[LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))]), UseClause([symbol])],
			parent=None
		)
		entity = Entity(
			"entity_A",
			[ContextReference([ContextReferenceSymbol(SelectedName("ctx_1", SimpleName("work")))])],
			parent=None
		)
		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(context)
		document._AddDesignUnit(entity)
		design.AddDocument(document, library)
		design.CreateDependencyGraph()

		with self.assertRaises(UseClauseNotLinkedError) as ex:
			design.LinkContextReferences()

		self.assertEqual("Use clause 'ieee.std_logic_1164.all' of context 'ctx_1' isn't linked.", str(ex.exception))
		self.assertListEqual(["Call 'LinkContexts()' before 'LinkContextReferences()'."], ex.exception.__notes__)
		self.assertIs(symbol, ex.exception.Symbol)
		self.assertIs(context, ex.exception.Context)
		self.assertIsInstance(ex.exception, NotLinkedError)
		self.assertIsInstance(ex.exception, VHDLModelException)


class LinkPackageBodies(Testcase):
	"""A package has one package body."""

	def setUp(self) -> None:
		self._design =      Design("example")
		self._library =     self._design.GetLibrary("lib_1")
		self._package =     Package("pack_1", parent=None)
		self._packageBody = PackageBody(PackageSymbol(SimpleName("pack_1")), parent=None)
		document =          Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(self._package)
		document._AddDesignUnit(self._packageBody)
		self._design.AddDocument(document, self._library)
		self._design.CreateDependencyGraph()

	def test_FirstBody(self) -> None:
		with WarningCollector() as collector:
			self._library.LinkPackageBodies()

		self.assertListEqual([], collector.Warnings)
		self.assertIs(self._packageBody, self._package.PackageBody)

	def test_SameBody(self) -> None:
		self._package._packageBody = self._packageBody

		with WarningCollector() as collector:
			self._library.LinkPackageBodies()

		self.assertListEqual([], collector.Warnings)
		self.assertIs(self._packageBody, self._package.PackageBody)

	def test_SecondBody(self) -> None:
		existing =                   PackageBody(PackageSymbol(SimpleName("pack_1")), parent=None)
		self._package._packageBody = existing

		with WarningCollector() as collector:
			self._library.LinkPackageBodies()

		self.assertEqual(1, len(collector.Warnings))
		warning = collector.Warnings[0]
		self.assertIsInstance(warning, DuplicateDeclarationWarning)
		self.assertEqual(
			"Package 'pack_1' in library 'lib_1' already has a package body, which is replaced.",
			str(warning)
		)
		self.assertEqual("pack_1", warning.Identifier)
		self.assertIs(self._packageBody, warning.Element)
		self.assertIs(existing, warning.Existing)
		self.assertIs(self._packageBody, self._package.PackageBody)

	def test_SecondBody_NoCollector(self) -> None:
		self._package._packageBody = PackageBody(PackageSymbol(SimpleName("pack_1")), parent=None)

		with self.assertRaises(UnhandledCriticalWarningError):
			self._library.LinkPackageBodies()

	def test_NoPackage(self) -> None:
		design =   Design("example")
		library =  design.GetLibrary("lib_1")
		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(PackageBody(PackageSymbol(SimpleName("pack_2")), parent=None))
		design.AddDocument(document, library)
		design.CreateDependencyGraph()

		with self.assertRaises(PackageBodyPackageNotFoundError) as context:
			library.LinkPackageBodies()

		self.assertEqual(
			"Package 'pack_2' referenced by package body 'pack_2' doesn't exist in library 'lib_1'.",
			str(context.exception)
		)
		self.assertEqual("pack_2", context.exception.DesignUnitName)
		self.assertEqual("lib_1", context.exception.LibraryName)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)


class LinkArchitectures(Testcase):
	"""An architecture is linked to its entity."""

	def test_NoEntity(self) -> None:
		design =   Design("example")
		library =  design.GetLibrary("lib_1")
		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(Architecture("arch_1", EntitySymbol(SimpleName("entity_1")), parent=None))
		document._AddDesignUnit(Architecture("arch_2", EntitySymbol(SimpleName("entity_1")), parent=None))
		design.AddDocument(document, library)
		design.CreateDependencyGraph()

		with self.assertRaises(ArchitectureEntityNotFoundError) as context:
			library.LinkArchitectures()

		self.assertEqual(
			"Entity 'entity_1' referenced by architecture(s) 'arch_1', 'arch_2' doesn't exist in library 'lib_1'.",
			str(context.exception)
		)
		self.assertEqual("entity_1", context.exception.DesignUnitName)
		self.assertEqual("lib_1", context.exception.LibraryName)
		self.assertTupleEqual(("arch_1", "arch_2"), context.exception.ArchitectureNames)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)


class Blackboxes(Testcase):
	"""A component without an entity becomes a blackbox, where the design allows blackboxes."""

	@staticmethod
	def _design() -> tuple[Design, Component, ComponentInstantiation]:
		design = Design("example", allowBlackbox=True)
		library = design.GetLibrary("lib_1")

		component = Component("primitive")
		instance = ComponentInstantiation("inst", ComponentInstantiationSymbol(SimpleName("primitive")))

		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(Entity("top", parent=None))
		architecture = Architecture(
			"rtl", EntitySymbol(SimpleName("top")), declaredItems=[component], statements=[instance], parent=None
		)
		document._AddDesignUnit(architecture)

		design.AddDocument(document, library)
		design.LoadStdLibrary()
		design.LoadIEEELibrary()

		return design, component, instance

	def test_WithoutCollector(self) -> None:
		"""A blackbox is a non-critical warning: without a collector, the analysis completes."""
		design, component, _ = self._design()

		design.Analyze()

		self.assertTrue(component.IsBlackbox)

	def test_Collected(self) -> None:
		"""A collector receives the blackbox warning with the instantiation and the component."""
		design, component, instance = self._design()

		with WarningCollector() as collector:
			design.Analyze()

		warnings = _warningsOfType(collector, BlackboxWarning)
		self.assertEqual(1, len(warnings))
		self.assertIs(instance, warnings[0].Instance)
		self.assertIs(component, warnings[0].Component)

	def test_NotAllowed(self) -> None:
		"""A component without an entity, where the design doesn't allow blackboxes."""
		design, component, _ = self._design()
		design.AllowBlackbox = False

		with self.assertRaises(ComponentEntityNotFoundError) as context:
			design.Analyze()

		self.assertEqual(
			"Entity 'primitive' not found for component 'primitive' in library 'lib_1'.",
			str(context.exception)
		)
		self.assertEqual("primitive", context.exception.DesignUnitName)
		self.assertEqual("lib_1", context.exception.LibraryName)
		self.assertIs(component, context.exception.Component)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertIsInstance(context.exception, VHDLModelException)


class CompileOrderGraph(Testcase):
	def test_Documents_SameFileName(self) -> None:
		"""Documents with the same file name in different directories get one vertex each."""
		design = Design("example")
		library = design.GetLibrary("lib_1")

		document1 = Document(Path("a/top.vhdl"), parent=None)
		document1._AddDesignUnit(Entity("entity_1", parent=None))
		design.AddDocument(document1, library)

		document2 = Document(Path("b/top.vhdl"), parent=None)
		document2._AddDesignUnit(Entity("entity_2", parent=None))
		design.AddDocument(document2, library)

		design.CreateDependencyGraph()
		design.CreateCompileOrderGraph()

		self.assertIs(document1, design.CompileOrderGraph.GetVertexByID(str(Path("a/top.vhdl"))).Value)
		self.assertIs(document2, design.CompileOrderGraph.GetVertexByID(str(Path("b/top.vhdl"))).Value)

	def test_CompileOrderNotComputed(self) -> None:
		design =  Design("example")
		library = design.GetLibrary("lib_1")
		for name in ("a", "b"):
			document = Document(Path(f"{name}.vhdl"), parent=None)
			document._AddDesignUnit(Entity(f"entity_{name}", parent=None))
			design.AddDocument(document, library)

		design.CreateDependencyGraph()
		design.CreateCompileOrderGraph()

		with self.assertRaises(CompileOrderNotComputedError) as context:
			list(design.IterateDocumentsInCompileOrder())

		self.assertEqual("Compile order is not yet computed from dependency graph.", str(context.exception))
		self.assertListEqual(
			["Call 'Analyze()' or 'AnalyzeDependencies()' before 'IterateDocumentsInCompileOrder()'."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception, NotComputedError)
		self.assertIsInstance(context.exception, VHDLModelException)


class TopLevel(Testcase):
	def test_SingleEntityWithoutArchitecture_IsNotMistakenForUncomputedHierarchy(self) -> None:
		"""
		A design consisting of a single entity without any (yet analyzed) architecture produces a hierarchy graph with
		exactly one vertex and zero edges. This must not be mistaken for "hierarchy not yet computed".
		"""
		design = Design("example")
		library = design.GetLibrary("lib_1")

		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(Entity("entity_1", parent=None))
		design.AddDocument(document, library)

		design.CreateDependencyGraph()
		design.CreateHierarchyGraph()

		self.assertEqual(0, design.HierarchyGraph.EdgeCount)
		self.assertEqual(1, design.HierarchyGraph.VertexCount)
		self.assertIs(library.Entities["entity_1"], design.TopLevel)

	def test_HierarchyNotComputed(self) -> None:
		design = Design("example")

		with self.assertRaises(HierarchyNotComputedError) as context:
			design.TopLevel

		self.assertEqual("Hierarchy is not yet computed from dependency graph.", str(context.exception))
		self.assertListEqual(
			["Call 'Analyze()' or 'AnalyzeDependencies()' before accessing 'TopLevel'."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception, NotComputedError)
		self.assertIsInstance(context.exception, VHDLModelException)


class IndexDeclaredItems(Testcase):
	"""
	``IndexDeclaredItems`` reports an unsupported declared item as ``NotImplementedWarning``.

	Regression tests for replacing a stray ``print()`` with ``WarningCollector.Raise(NotImplementedWarning(...))`` in
	``IndexDeclaredItems``, consistent with the same warning idiom used elsewhere in this codebase and mirrored by
	pyGHDL.dom's own ``WarningCollector`` usage (both build on ``pyTooling.Warning``).
	"""

	@staticmethod
	def _designWithVariableInArchitecture() -> Design:
		design = Design("example")
		library = design.GetLibrary("lib_1")

		document = Document(Path("tests.vhdl"), parent=None)
		document._AddDesignUnit(Entity("entity_1", parent=None))

		variable = Variable(["v"], SimpleSubtypeSymbol(SimpleName("natural")))
		architecture = Architecture("arch_1", EntitySymbol(SimpleName("entity_1")), declaredItems=[variable], parent=None)
		document._AddDesignUnit(architecture)

		design.AddDocument(document, library)

		return design

	def test_WarningIsCollected_WhenCollectorIsInScope(self) -> None:
		design = self._designWithVariableInArchitecture()

		with WarningCollector() as collector:
			design.IndexArchitectures()

		self.assertEqual(1, len(collector))
		self.assertIsInstance(collector[0], NotImplementedWarning)
		self.assertIsInstance(collector[0].Item, Variable)

	def test_NotImplementedWarning_MessageOnly(self) -> None:
		self.assertIsNone(NotImplementedWarning("Not modelled yet.").Item)

	def test_DoesNotCrash_WhenNoCollectorIsInScope(self) -> None:
		"""
		Previously raised ``TypeError: category must be a Warning subclass, not 'type'`` due to a broken
		``warnings.warn(...)`` call. Must not raise here at all, since ``NotImplementedWarning`` is a *non-critical*
		``pyTooling.Warning.Warning`` and is silently dropped when unhandled - exactly like every other
		``NotImplementedWarning`` call site in this codebase.
		"""
		design = self._designWithVariableInArchitecture()

		design.IndexArchitectures()
