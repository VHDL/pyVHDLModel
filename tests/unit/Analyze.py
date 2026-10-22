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

from pyVHDLModel import Design, Document, VHDLModelException
from pyVHDLModel.Name import Name, SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol import LibraryReferenceSymbol, PackageReferenceSymbol, AllPackageMembersReferenceSymbol
from pyVHDLModel.Symbol import ContextReferenceSymbol, EntitySymbol, PackageSymbol, EntityInstantiationSymbol
from pyVHDLModel.Symbol import SimpleSubtypeSymbol, Symbol, PossibleReference, ComponentInstantiationSymbol
from pyVHDLModel.DesignUnit import Package, PackageBody, Context, Entity, Architecture, Configuration, Component
from pyVHDLModel.DesignUnit import LibraryClause, UseClause, ContextReference
from pyVHDLModel.Configuration import BlockConfiguration
from pyVHDLModel.Concurrent import EntityInstantiation, ComponentInstantiation
from pyVHDLModel.Object import Variable
from pyVHDLModel.Exception import NotImplementedWarning, BlackboxWarning

from pyTooling.Warning         import WarningCollector
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

		with self.assertRaises(VHDLModelException) as context:
			design.Analyze()

		self.assertEqual(
			"Referenced library 'lib_2' in direct entity instantiation 'inst: entity lib_2.entity_A' not found in "
			"architecture 'lib_1.entity_B(arch_B)'.",
			str(context.exception)
		)


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

	def test_HierarchyNotYetComputed_RaisesVHDLModelException(self) -> None:
		design = Design("example")

		with self.assertRaises(VHDLModelException):
			design.TopLevel


class IndexDeclaredItems(Testcase):
	"""
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
