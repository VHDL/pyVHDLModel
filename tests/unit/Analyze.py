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
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
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
from pathlib  import Path
from unittest import TestCase

from pyVHDLModel import Design, Document
from pyVHDLModel.Name import SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol import LibraryReferenceSymbol, PackageReferenceSymbol, AllPackageMembersReferenceSymbol
from pyVHDLModel.Symbol import ContextReferenceSymbol, EntitySymbol, PackageSymbol, EntityInstantiationSymbol
from pyVHDLModel.DesignUnit import Package, PackageBody, Context, Entity, Architecture, Configuration
from pyVHDLModel.DesignUnit import LibraryClause, UseClause, ContextReference
from pyVHDLModel.Concurrent import EntityInstantiation


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VHDLLibrary(TestCase):
	def CreateDesign(self) -> Design:
		design = Design("example")
		library = design.GetLibrary("lib_1")

		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Library' class.")

		contextReferences = [
			LibraryClause([
				LibraryReferenceSymbol(SimpleName("ieee")),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(AllName(SelectedName("std_logic_1164", SimpleName("ieee")))),
			])
		]
		context = Context("ctx_1", contextReferences, documentation="My first context.")
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
		entityA = Entity("entity_A", entityAReferences, documentation="My first entity.")
		document._AddDesignUnit(entityA)

		architectureAReferences = [
			UseClause([
				AllPackageMembersReferenceSymbol(AllName(SelectedName("textio", SimpleName("std")))),
			]),
		]
		architectureA = Architecture("arch_A", EntitySymbol(SimpleName("entity_A")), architectureAReferences, documentation="My first entity implementation.")
		document._AddDesignUnit(architectureA)

		entityBReferences = [
			ContextReference([
				ContextReferenceSymbol(SelectedName("ctx_1", SimpleName("work"))),
			]),
		]
		entityB = Entity("entity_B", entityBReferences, documentation="My second entity.")
		document._AddDesignUnit(entityB)

		architectureBStatements = [
			EntityInstantiation("instWork", EntityInstantiationSymbol(SelectedName("entity_A", SimpleName("work")))),
			EntityInstantiation("instLib", EntityInstantiationSymbol(SelectedName("entity_A", SimpleName("lib_1")))),
		]
		architectureB = Architecture("arch_B", EntitySymbol(SimpleName("entity_B")), None, None, architectureBStatements, documentation="My second entity implementation.")
		document._AddDesignUnit(architectureB)

		packageReferences = [
			ContextReference([
				ContextReferenceSymbol(SelectedName("ctx_1", SimpleName("work"))),
			]),
		]
		package = Package("pack_1", packageReferences, documentation="My first utility package.")
		document._AddDesignUnit(package)

		packageBody = PackageBody(PackageSymbol(SimpleName("pack_1")))
		document._AddDesignUnit(packageBody)

		configuration = Configuration("cfg_1")
		document._AddDesignUnit(configuration)

		design.AddDocument(document, library)

		design.LoadStdLibrary()
		design.LoadIEEELibrary()

		return design

	def test_DependencyGraph(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()

		self.assertEqual(39, design.DependencyGraph.VertexCount)

	def test_LinkContexts(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkContexts()

	def test_LinkArchitectures(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()

	def test_LinkPackageBodies(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkPackageBodies()

	def test_LinkLibraryReferences(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		design.LinkLibraryReferences()

	def test_LinkPackageReferences(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		design.LinkLibraryReferences()
		design.LinkPackageReferences()

	def test_LinkContextReferences(self):
		design = self.CreateDesign()

		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		design.LinkLibraryReferences()
		design.LinkPackageReferences()
		design.LinkContextReferences()

	def test_IndexPackages(self):
		design = self.CreateDesign()

		design.IndexPackages()

	def test_IndexArchitectures(self):
		design = self.CreateDesign()

		design.IndexArchitectures()

	def test_LinkInstantiations(self):
		design = self.CreateDesign()

		design.LinkInstantiations()

	def test_CreateHierarchyGraph(self):
		design = self.CreateDesign()

		design.CreateHierarchyGraph()

	def test_Analyze(self):
		design = self.CreateDesign()

		design.Analyze()
