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
"""Instantiation tests for the language model."""
from pathlib  import Path
from unittest import TestCase

from pyTooling.Graph import Graph

from pyVHDLModel.SyntaxModel import Design, Library, Document, Subtype, Range, IntegerLiteral, Direction, FloatingPointLiteral, PackageSymbol, EntitySymbol
from pyVHDLModel.SyntaxModel import Entity, Architecture, PackageBody, Package, Configuration, Context
from pyVHDLModel.SyntaxModel import IntegerType, RealType, ArrayType, RecordType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SimpleInstance(TestCase):
	def test_Design(self):
		design = Design()

		self.assertIsNotNone(design)
		self.assertEqual(0, len(design.Documents))
		self.assertEqual(0, len(design.Libraries))
		self.assertIsInstance(design.DependencyGraph, Graph)
		self.assertEqual(0, design.DependencyGraph.VertexCount)
		self.assertIsInstance(design.HierarchyGraph, Graph)
		self.assertEqual(0, design.HierarchyGraph.VertexCount)
		self.assertIsInstance(design.CompileOrderGraph, Graph)
		self.assertEqual(0, design.CompileOrderGraph.VertexCount)

	def test_Library(self):
		library = Library("lib_1")

		self.assertIsNotNone(library)
		self.assertEqual("lib_1", library.Identifier)
		self.assertEqual(0, len(library.Contexts))
		self.assertEqual(0, len(library.Entities))
		self.assertEqual(0, len(library.Packages))
		self.assertEqual(0, len(library.Configurations))

	def test_Document(self):
		path = Path("tests.vhdl")
		document = Document(path)

		self.assertIsNotNone(document)
		self.assertEqual(path, document.Path)
		self.assertEqual(0, len(document.Entities))
		self.assertEqual(0, len(document.Architectures))
		self.assertEqual(0, len(document.Packages))
		self.assertEqual(0, len(document.PackageBodies))
		self.assertEqual(0, len(document.Contexts))
		self.assertEqual(0, len(document.Configurations))

	def test_Entity(self):
		entity = Entity("entity_1")

		self.assertIsNotNone(entity)
		self.assertEqual("entity_1", entity.Identifier)
		self.assertEqual(0, len(entity.GenericItems))
		self.assertEqual(0, len(entity.PortItems))
		self.assertEqual(0, len(entity.DeclaredItems))
		self.assertEqual(0, len(entity.Statements))

	def test_Architecture(self):
		entity = EntitySymbol("entity_1")
		architecture = Architecture("arch_1", entity)

		self.assertIsNotNone(architecture)
		self.assertEqual("arch_1", architecture.Identifier)
		self.assertEqual(0, len(architecture.DeclaredItems))
		self.assertEqual(0, len(architecture.Statements))

	def test_Package(self):
		package = Package("pack_1")

		self.assertIsNotNone(package)
		self.assertEqual("pack_1", package.Identifier)
		self.assertEqual(0, len(package.DeclaredItems))

	def test_PackageBody(self):
		packageSymbol = PackageSymbol("pack_1")
		packageBody = PackageBody(packageSymbol)

		self.assertIsNotNone(packageBody)
		self.assertEqual("pack_1", packageBody.Identifier)
		self.assertEqual(0, len(packageBody.DeclaredItems))

	def test_Context(self):
		context = Context("ctx_1")

		self.assertIsNotNone(context)
		self.assertEqual("ctx_1", context.Identifier)

	def test_Configuration(self):
		configuration = Configuration("conf_1")

		self.assertIsNotNone(configuration)
		self.assertEqual("conf_1", configuration.Identifier)

	def test_Subtype(self):
		subtype = Subtype("bit")

		self.assertIsNotNone(subtype)
		self.assertEqual("bit", subtype.Identifier)

	def test_Integer(self):
		integer = IntegerType("integer", Range(IntegerLiteral(0), IntegerLiteral(7), Direction.To))

		self.assertIsNotNone(integer)
		self.assertEqual("integer", integer.Identifier)

	def test_Real(self):
		real =    RealType("real", Range(FloatingPointLiteral(0.0), FloatingPointLiteral(1.0), Direction.To))

		self.assertIsNotNone(real)
		self.assertEqual("real", real.Identifier)

	def test_Array(self):
		array =   ArrayType("bit_vector", [], None)

		self.assertIsNotNone(array)
		self.assertEqual("bit_vector", array.Identifier)

	def test_Record(self):
		record =  RecordType("rec", [])

		self.assertIsNotNone(record)
		self.assertEqual("rec", record.Identifier)


class VHDLDocument(TestCase):
	def test_Documentation(self):
		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Document' class.")

		self.assertEqual("Testing 'Document' class.", document.Documentation)

	def test_Entity(self):
		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Document' class.")

		entity = Entity("entity_1")
		document._AddEntity(entity)

		self.assertEqual(1, len(document.Entities))
		self.assertEqual(1, len(document.DesignUnits))

	def test_Architecture(self):
		path = Path("tests.vhdl")
		document = Document(path)

		entity = EntitySymbol("entity_1")
		architecture = Architecture("arch_1", entity)
		document._AddArchitecture(architecture)

		self.assertEqual(1, len(document.Architectures))
		self.assertEqual(1, len(document.DesignUnits))

	def test_Package(self):
		path = Path("tests.vhdl")
		document = Document(path)

		package = Package("pack_1")
		document._AddPackage(package)

		self.assertEqual(1, len(document.Packages))
		self.assertEqual(1, len(document.DesignUnits))

	def test_PackageBody(self):
		path = Path("tests.vhdl")
		document = Document(path)

		packageSymbol = PackageSymbol("pack_1")
		packageBody = PackageBody(packageSymbol)
		document._AddPackageBody(packageBody)

		self.assertEqual(1, len(document.PackageBodies))
		self.assertEqual(1, len(document.DesignUnits))

	def test_Context(self):
		path = Path("tests.vhdl")
		document = Document(path)

		context = Context("ctx_1")
		document._AddContext(context)

		self.assertEqual(1, len(document.Contexts))
		self.assertEqual(1, len(document.DesignUnits))

	def test_Configuration(self):
		path = Path("tests.vhdl")
		document = Document(path)

		configuration = Configuration("cfg_1")
		document._AddConfiguration(configuration)

		self.assertEqual(1, len(document.Configurations))
		self.assertEqual(1, len(document.DesignUnits))

	def test_DesignUnits(self):
		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Document' class.")

		entity = Entity("entity_1")
		document._AddDesignUnit(entity)

		entity = EntitySymbol("entity_1")
		architecture = Architecture("arch_1", entity)
		document._AddDesignUnit(architecture)

		package = Package("pack_1")
		document._AddDesignUnit(package)

		packageSymbol = PackageSymbol("pack_1")
		packageBody = PackageBody(packageSymbol)
		document._AddDesignUnit(packageBody)

		context = Context("ctx_1")
		document._AddDesignUnit(context)

		configuration = Configuration("cfg_1")
		document._AddDesignUnit(configuration)

		self.assertEqual(1, len(document.Entities))
		self.assertEqual(1, len(document.Architectures))
		self.assertEqual(1, len(document.Packages))
		self.assertEqual(1, len(document.PackageBodies))
		self.assertEqual(1, len(document.Contexts))
		self.assertEqual(1, len(document.Configurations))
		self.assertEqual(6, len(document.DesignUnits))


class VHDLLibrary(TestCase):
	def test_AddLibrary(self):
		design = Design()

		library1 = Library("lib_1")
		design.AddLibrary(library1)

		self.assertEqual(1, len(design.Libraries))
		self.assertEqual(design, library1.Parent)

		with self.assertRaises(Exception):
			design.AddLibrary(Library("lib_1"))

		with self.assertRaises(Exception):
			library2 = Library("lib_2")
			library2._parent = True
			design.AddLibrary(library2)

	def test_GetLibrary(self):
		design = Design()
		library = design.GetLibrary("lib_1")

		self.assertEqual(1, len(design.Libraries))
		self.assertEqual("lib_1", library.Identifier)

	def test_AddDocument(self):
		design = Design()
		library = design.GetLibrary("lib_1")

		path = Path("tests.vhdl")
		document = Document(path, documentation="Testing 'Library' class.")

		document._AddDesignUnit(Entity("entity_1"))
		document._AddDesignUnit(Architecture("arch_1", EntitySymbol("entity_1")))
		document._AddDesignUnit(Package("pack_1"))
		document._AddDesignUnit(PackageBody(PackageSymbol("pack_1")))
		document._AddDesignUnit(Context("ctx_1"))
		document._AddDesignUnit(Configuration("cfg_1"))

		design.AddDocument(document, library)

		self.assertEqual(1, len(design.Libraries))
		self.assertEqual(1, len(design.Documents))

		self.assertEqual(1, len(library.Entities))
		self.assertEqual(1, len(library.Architectures))
		self.assertEqual(1, len(library.Packages))
		self.assertEqual(1, len(library.PackageBodies))
		self.assertEqual(1, len(library.Contexts))
		self.assertEqual(1, len(library.Configurations))

		self.assertSetEqual(set(document.IterateDesignUnits()), set(library.IterateDesignUnits()))

	def test_StdLibrary(self):
		design = Design()
		stdLibrary = design.LoadStdLibrary()

		self.assertEqual(1, len(design.Libraries))
		self.assertEqual("std", stdLibrary.NormalizedIdentifier)
		self.assertEqual(3, len(stdLibrary.Packages))
		self.assertEqual(3, len(stdLibrary.PackageBodies))

		self.assertSetEqual(set(design.IterateDesignUnits()), set(stdLibrary.IterateDesignUnits()))

		with self.assertRaises(Exception):
			design.LoadStdLibrary()

	def test_IeeeLibrary(self):
		design = Design()
		ieeeLibrary = design.LoadIEEELibrary()

		self.assertEqual(1, len(design.Libraries))
		self.assertEqual("ieee", ieeeLibrary.NormalizedIdentifier)
		self.assertEqual(13, len(ieeeLibrary.Packages))
		self.assertEqual(9, len(ieeeLibrary.PackageBodies))

		self.assertSetEqual(set(design.IterateDesignUnits()), set(ieeeLibrary.IterateDesignUnits()))
