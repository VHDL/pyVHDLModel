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
# Copyright 2017-2022 Patrick Lehmann - Boetzingen, Germany                                                            #
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

from pyTooling.Graph import Graph

from pyVHDLModel import LibraryClause, UseClause, ContextReference
from pyVHDLModel.SyntaxModel import Design, Library, Document, Subtype, Range, IntegerLiteral, Direction, FloatingPointLiteral, PackageSymbol, EntitySymbol, \
	LibraryReferenceSymbol, AllPackageMembersReferenceSymbol, PackageReferenceSymbol, PackageMembersReferenceSymbol, ContextReferenceSymbol, EntityInstantiation, \
	EntityInstantiationSymbol
from pyVHDLModel.SyntaxModel import Entity, Architecture, PackageBody, Package, Configuration, Context
from pyVHDLModel.SyntaxModel import IntegerType, RealType, ArrayType, RecordType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VHDLLibrary(TestCase):
	def CreateDesign(self) -> Design:
		design = Design()
		library = design.GetLibrary("lib_1")

		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Library' class.")

		contextReferences = [
			LibraryClause([
				LibraryReferenceSymbol("ieee"),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(PackageReferenceSymbol("std_logic_1164", LibraryReferenceSymbol("ieee"))),
			])
		]
		context = Context("ctx_1", contextReferences, documentation="My first context.")
		document._AddDesignUnit(context)

		entityAReferences = [
			# UseClause([
			# 	PackageMembersReferenceSymbol("Stop", PackageReferenceSymbol("env", LibraryReferenceSymbol("std"))),
			# ]),
			LibraryClause([
				LibraryReferenceSymbol("ieee"),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(PackageReferenceSymbol("numeric_std", LibraryReferenceSymbol("ieee"))),
			]),
			UseClause([
				AllPackageMembersReferenceSymbol(PackageReferenceSymbol("pack_1", LibraryReferenceSymbol("work"))),
			])
		]
		entityA = Entity("entity_A", entityAReferences, documentation="My first entity.")
		document._AddDesignUnit(entityA)

		architectureAReferences = [
			UseClause([
				AllPackageMembersReferenceSymbol(PackageReferenceSymbol("textio", LibraryReferenceSymbol("std"))),
			]),
		]
		architectureA = Architecture("arch_A", EntitySymbol("entity_A"), architectureAReferences, documentation="My first entity implementation.")
		document._AddDesignUnit(architectureA)

		entityBReferences = [
			ContextReference([
				ContextReferenceSymbol("ctx_1", LibraryReferenceSymbol("work")),
			]),
		]
		entityB = Entity("entity_B", entityBReferences, documentation="My second entity.")
		document._AddDesignUnit(entityB)

		architectureBStatements = [
			EntityInstantiation("inst", EntityInstantiationSymbol("entity_A", LibraryReferenceSymbol("work")))
		]
		architectureB = Architecture("arch_B", EntitySymbol("entity_B"), None, architectureBStatements, documentation="My second entity implementation.")
		document._AddDesignUnit(architectureB)

		packageReferences = [
			ContextReference([
				ContextReferenceSymbol("ctx_1", LibraryReferenceSymbol("work")),
			]),
		]
		package = Package("pack_1", packageReferences, documentation="My first utility package.")
		document._AddDesignUnit(package)

		packageBody = PackageBody(PackageSymbol("pack_1"))
		document._AddDesignUnit(packageBody)

		configuration = Configuration("cfg_1")
		document._AddDesignUnit(configuration)

		design.AddDocument(document, library)

		design.LoadStdLibrary()
		design.LoadIEEELibrary()

		return design

	def test_CompileOrderGraph(self):
		design = self.CreateDesign()

		design.CreateCompilerOrderGraph()

		self.assertEqual(1, design.CompileOrderGraph.VertexCount)

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

	def test_LinkInstanziations(self):
		design = self.CreateDesign()

		design.LinkInstanziations()

	def test_CreateHierarchyGraph(self):
		design = self.CreateDesign()

		design.CreateHierarchyGraph()

	def test_Analyze(self):
		design = self.CreateDesign()

		design.Analyze()
