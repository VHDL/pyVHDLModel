# =============================================================================
#             __     ___   _ ____  _     __  __           _      _
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|
#  |_|    |___/
# ==============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Instantiation tests for the language model.
#
# License:
# ==============================================================================
# Copyright 2017-2021 Patrick Lehmann - Boetzingen, Germany
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ==============================================================================
#
from pathlib  import Path
from unittest import TestCase

from pyVHDLModel.SyntaxModel import Design, Library, Document, Subtype, Range, IntegerLiteral, Direction, FloatingPointLiteral
from pyVHDLModel.SyntaxModel import Entity, Architecture, PackageBody, Package, Configuration, Context
from pyVHDLModel.SyntaxModel import IntegerType, RealType, ArrayType, RecordType


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Instantiate(TestCase):
	def test_Design(self):
		design = Design()

		self.assertIsNotNone(design)
		self.assertEqual(0, len(design.Documents))
		self.assertEqual(0, len(design.Libraries))

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
		entity = Entity("entity_1")
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
		packageBody = PackageBody("pack_1")

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
