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
"""Instantiation tests for the language model."""
from pathlib  import Path
from unittest import TestCase

from pyTooling.Graph import Graph

from pyVHDLModel import Design, Library, Document
from pyVHDLModel.Base import Direction, Range
from pyVHDLModel.Name import SelectedName, SimpleName, AllName, AttributeName
from pyVHDLModel.Object import Constant, Signal
from pyVHDLModel.Symbol import LibraryReferenceSymbol, PackageReferenceSymbol, PackageMemberReferenceSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Symbol import AllPackageMembersReferenceSymbol, ContextReferenceSymbol, EntitySymbol
from pyVHDLModel.Symbol import ArchitectureSymbol, PackageSymbol, EntityInstantiationSymbol
from pyVHDLModel.Symbol import ComponentInstantiationSymbol, ConfigurationInstantiationSymbol
from pyVHDLModel.Expression import IntegerLiteral, FloatingPointLiteral
from pyVHDLModel.Type import Subtype, IntegerType, RealType, ArrayType, RecordType
from pyVHDLModel.DesignUnit import Package, PackageBody, Context, Entity, Architecture, Configuration


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Names(TestCase):
	def test_SimpleName(self):
		name = SimpleName("Lib")

		self.assertEqual("Lib", name.Identifier)
		self.assertEqual("lib", name.NormalizedIdentifier)
		self.assertIs(name, name.Root)
		self.assertIsNone(name.Prefix)
		self.assertFalse(name.HasPrefix)

		self.assertEqual("Name: 'Lib'", repr(name))
		self.assertEqual("Lib", str(name))

	def test_SelectedName_1(self):
		simpleName = SimpleName("Lib")
		name = SelectedName("Pack", simpleName)

		self.assertEqual("Pack", name.Identifier)
		self.assertEqual("pack", name.NormalizedIdentifier)
		self.assertIs(simpleName, name.Root)
		self.assertIs(simpleName, name.Prefix)
		self.assertTrue(name.HasPrefix)
		self.assertFalse(simpleName.HasPrefix)

		self.assertEqual("Name: 'Lib.Pack'", repr(name))
		self.assertEqual("Lib.Pack", str(name))

	def test_SelectedName_2(self):
		simpleName = SimpleName("Lib")
		selectedName = SelectedName("Pack", simpleName)
		name = SelectedName("Func", selectedName)

		self.assertEqual("Func", name.Identifier)
		self.assertEqual("func", name.NormalizedIdentifier)
		self.assertIs(simpleName, name.Root)
		self.assertIs(selectedName, name.Prefix)
		self.assertIs(simpleName, name.Prefix.Prefix)
		self.assertTrue(name.HasPrefix)
		self.assertTrue(selectedName.HasPrefix)
		self.assertFalse(simpleName.HasPrefix)

		self.assertEqual("Name: 'Lib.Pack.Func'", repr(name))
		self.assertEqual("Lib.Pack.Func", str(name))

	def test_AllName(self):
		simpleName = SimpleName("Lib")
		selectedName = SelectedName("Pack", simpleName)
		name = AllName(selectedName)

		# self.assertEqual("All", name.Identifier)
		self.assertEqual("all", name.NormalizedIdentifier)
		self.assertIs(simpleName, name.Root)
		self.assertIs(selectedName, name.Prefix)
		self.assertIs(simpleName, name.Prefix.Prefix)
		self.assertTrue(name.HasPrefix)
		self.assertTrue(selectedName.HasPrefix)
		self.assertFalse(simpleName.HasPrefix)

		self.assertEqual("Name: 'Lib.Pack.all'", repr(name))
		self.assertEqual("Lib.Pack.all", str(name))

	def test_AttributeName(self):
		simpleName = SimpleName("Sig")
		name = AttributeName("Length", simpleName)

		self.assertEqual("Length", name.Identifier)
		self.assertEqual("length", name.NormalizedIdentifier)
		self.assertIs(simpleName, name.Root)
		self.assertIs(simpleName, name.Prefix)
		self.assertTrue(name.HasPrefix)
		self.assertFalse(simpleName.HasPrefix)

		self.assertEqual("Name: 'Sig'Length'", repr(name))
		self.assertEqual("Sig'Length", str(name))


class Symbols(TestCase):
	def test_LibraryReferenceSymbol(self):
		name = SimpleName("Lib")
		symbol = LibraryReferenceSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Library)
		self.assertEqual("LibraryReferenceSymbol: 'Lib' -> unresolved", repr(symbol))
		self.assertEqual("Lib?", str(symbol))

		library = Library("liB")
		symbol.Library = library

		self.assertTrue(symbol.IsResolved)
		self.assertIs(library, symbol.Library)
		self.assertEqual("LibraryReferenceSymbol: 'Lib' -> Library: 'liB'", repr(symbol))
		self.assertEqual("Library: 'liB'", str(symbol))

	def test_PackageReferenceSymbol(self):
		name = SelectedName("Pack", SimpleName("Lib"))
		symbol = PackageReferenceSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Package)
		self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> unresolved", repr(symbol))
		self.assertEqual("Lib.Pack?", str(symbol))

		library = Library("liB")
		package = Package("pacK")
		package.Library = library
		symbol.Package = package

		self.assertTrue(symbol.IsResolved)
		self.assertIs(package, symbol.Package)
		self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> Package: 'liB.pacK'", repr(symbol))
		self.assertEqual("Package: 'liB.pacK'", str(symbol))

	def test_PackageMemberReferenceSymbol(self):
		name = SelectedName("Obj", SelectedName("Pack", SimpleName("Lib")))
		symbol = PackageMemberReferenceSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Member)
		self.assertEqual("PackageMemberReferenceSymbol: 'Lib.Pack.Obj' -> unresolved", repr(symbol))
		self.assertEqual("Lib.Pack.Obj?", str(symbol))

		library = Library("liB")
		package = Package("pacK")
		package.Library = library
		constant = Constant(("obJ", ), SimpleSubtypeSymbol(SimpleName("Bool")))
		for id in constant.Identifiers:
			package.DeclaredItems.append(constant)
			package.Constants[id] = constant

		symbol.Member = constant

		self.assertTrue(symbol.IsResolved)
		self.assertIs(constant, symbol.Member)
		# self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> Package: 'liB.pacK'", repr(symbol))
		# self.assertEqual("Constant: 'liB.pacK.obJ'", str(symbol))

	def test_AllPackageMembersReferenceSymbol(self):
		name = AllName(SelectedName("Pack", SimpleName("Lib")))
		symbol = AllPackageMembersReferenceSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Members)
		self.assertEqual("AllPackageMembersReferenceSymbol: 'Lib.Pack.all' -> unresolved", repr(symbol))
		self.assertEqual("Lib.Pack.all?", str(symbol))

		library = Library("liB")
		package = Package("pacK")
		package.Library = library
		constant = Constant(("obJ", ), SimpleSubtypeSymbol(SimpleName("Bool")))
		signal = Signal(("siG", ), SimpleSubtypeSymbol(SimpleName("Bit")))
		for id in constant.Identifiers:
			package.DeclaredItems.append(constant)
			package.Constants[id] = constant
		for id in signal.Identifiers:
			package.DeclaredItems.append(signal)
			package.Objects[id] = signal

		symbol.Members = (constant, signal)

		self.assertTrue(symbol.IsResolved)
		self.assertTupleEqual((constant, signal), symbol.Members)
		# self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> Package: 'liB.pacK'", repr(symbol))
		# self.assertEqual("Constant: 'liB.pacK.obJ'", str(symbol))

	def test_ContextReferenceSymbol(self):
		name = SelectedName("Ctx", SimpleName("Lib"))
		symbol = ContextReferenceSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Context)
		self.assertEqual("ContextReferenceSymbol: 'Lib.Ctx' -> unresolved", repr(symbol))
		self.assertEqual("Lib.Ctx?", str(symbol))

		library = Library("liB")
		context = Context("ctX")
		context.Library = library
		symbol.Context = context

		self.assertTrue(symbol.IsResolved)
		self.assertIs(context, symbol.Context)
		# self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> Package: 'liB.pacK'", repr(symbol))
		# self.assertEqual("Package: 'liB.pacK'", str(symbol))

	def test_SimpleEntitySymbol(self):
		name = SimpleName("Ent")
		symbol = EntitySymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Entity)
		self.assertEqual("EntitySymbol: 'Ent' -> unresolved", repr(symbol))
		self.assertEqual("Ent?", str(symbol))

		library = Library("liB")
		entity = Entity("enT")
		entity.Library = library
		symbol.Entity = entity

		self.assertTrue(symbol.IsResolved)
		self.assertIs(entity, symbol.Entity)
		# self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> Package: 'liB.pacK'", repr(symbol))
		# self.assertEqual("Package: 'liB.pacK'", str(symbol))

	def test_SelectedEntitySymbol(self):
		name = SelectedName("Ent", SimpleName("Work"))
		symbol = EntitySymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Entity)
		self.assertEqual("EntitySymbol: 'Work.Ent' -> unresolved", repr(symbol))
		self.assertEqual("Work.Ent?", str(symbol))

		library = Library("liB")
		entity = Entity("enT")
		entity.Library = library
		symbol.Entity = entity

		self.assertTrue(symbol.IsResolved)
		self.assertIs(entity, symbol.Entity)
		# self.assertEqual("PackageReferenceSymbol: 'Lib.Pack' -> Package: 'liB.pacK'", repr(symbol))
		# self.assertEqual("Package: 'liB.pacK'", str(symbol))

	# def test_ArchitectureSymbol(self):
	# 	symbol = ArchitectureSymbol("rtl")
	#
	# 	self.assertEqual("rtl", symbol.NormalizedIdentifier)

	# TODO: doe packages also support simple and selected names.
	def test_PackageSymbol(self):
		name = SimpleName("Pack")
		symbol = PackageSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Package)
		self.assertEqual("PackageSymbol: 'Pack' -> unresolved", repr(symbol))
		self.assertEqual("Pack?", str(symbol))

		library = Library("liB")
		package = Package("pacK")
		package.Library = library
		symbol.Package = package

		self.assertTrue(symbol.IsResolved)
		self.assertIs(package, symbol.Package)
		self.assertEqual("PackageSymbol: 'Pack' -> Package: 'liB.pacK'", repr(symbol))
		self.assertEqual("Package: 'liB.pacK'", str(symbol))

	def test_EntityInstantiationSymbol(self):
		name = SelectedName("Ent", SimpleName("Lib"))
		symbol = EntityInstantiationSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.Entity)
		self.assertEqual("EntityInstantiationSymbol: 'Lib.Ent' -> unresolved", repr(symbol))
		self.assertEqual("Lib.Ent?", str(symbol))

		library = Library("liB")
		entity = Entity("enT")
		entity.Library = library
		symbol.Entity = entity

		self.assertTrue(symbol.IsResolved)
		self.assertIs(entity, symbol.Entity)
		self.assertEqual("EntityInstantiationSymbol: 'Lib.Ent' -> Entity: 'liB.enT(%)'", repr(symbol))
		self.assertEqual("Entity: 'liB.enT(%)'", str(symbol))

	def test_ComponentInstantiationSymbol(self):
		symbol = ComponentInstantiationSymbol(SimpleName("comp"))

		self.assertEqual("comp", symbol.Name.NormalizedIdentifier)

	def test_ConfigurationInstantiationSymbol(self):
		symbol = ConfigurationInstantiationSymbol(SimpleName("cfg"))

		self.assertEqual("cfg", symbol.Name.NormalizedIdentifier)


class SimpleInstance(TestCase):
	def test_Design(self):
		design = Design()
		# design.Analyze()

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
		entitySymbol = EntitySymbol(SimpleName("entity_1"))
		architecture = Architecture("arch_1", entitySymbol)

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
		packageSymbol = PackageSymbol(SimpleName("pack_1"))
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

		entitySymbol = EntitySymbol(SimpleName("entity_1"))
		architecture = Architecture("arch_1", entitySymbol)
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

		packageSymbol = PackageSymbol(SimpleName("pack_1"))
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

		entitySymbol = Entity("entity_1")
		document._AddDesignUnit(entitySymbol)

		entitySymbol = EntitySymbol(SimpleName("entity_1"))
		architecture = Architecture("arch_1", entitySymbol)
		document._AddDesignUnit(architecture)

		package = Package("pack_1")
		document._AddDesignUnit(package)

		packageSymbol = PackageSymbol(SimpleName("pack_1"))
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
		document._AddDesignUnit(Architecture("arch_1", EntitySymbol(SimpleName("entity_1"))))
		document._AddDesignUnit(Package("pack_1"))
		document._AddDesignUnit(PackageBody(PackageSymbol(SimpleName("pack_1"))))
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

	def test_IeeeSynopsysLibrary(self):
		design = Design()
		ieeeLibrary = design.LoadIEEELibrary()
		ieeeLibrary.LoadSynopsysPackages()

		self.assertEqual(1, len(design.Libraries))
		self.assertEqual("ieee", ieeeLibrary.NormalizedIdentifier)
		self.assertEqual(14, len(ieeeLibrary.Packages))
		self.assertEqual(10, len(ieeeLibrary.PackageBodies))

		self.assertSetEqual(set(design.IterateDesignUnits()), set(ieeeLibrary.IterateDesignUnits()))
