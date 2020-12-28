from pathlib  import Path
from unittest import TestCase

from pyVHDLModel.VHDLModel import Design, Library, Document, Entity, Architecture, PackageBody, Package, Configuration, Context, SubType, IntegerType, RealType, \
	ArrayType, RecordType


if __name__ == "__main__":
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Instantiate(TestCase):
	def test_Design(self):
		design = Design()

		self.assertIsNotNone(design)
		self.assertTrue(len(design.Documents) == 0)
		self.assertTrue(len(design.Libraries) == 0)

	def test_Library(self):
		library = Library("lib_1")

		self.assertIsNotNone(library)
		self.assertTrue(library.Name == "lib_1")
		self.assertTrue(len(library.Contexts) == 0)
		self.assertTrue(len(library.Entities) == 0)
		self.assertTrue(len(library.Packages) == 0)
		self.assertTrue(len(library.Configurations) == 0)

	def test_Document(self):
		path = Path("tests.vhdl")
		document = Document(path)

		self.assertIsNotNone(document)
		self.assertTrue(document.Path == path)
		self.assertTrue(len(document.Entities) == 0)
		self.assertTrue(len(document.Architectures) == 0)
		self.assertTrue(len(document.Packages) == 0)
		self.assertTrue(len(document.PackageBodies) == 0)
		self.assertTrue(len(document.Contexts) == 0)
		self.assertTrue(len(document.Configurations) == 0)

	def test_Entity(self):
		entity = Entity("entity_1")

		self.assertIsNotNone(entity)
		self.assertTrue(entity.Name == "entity_1")
		self.assertTrue(len(entity.GenericItems) == 0)
		self.assertTrue(len(entity.PortItems) == 0)
		self.assertTrue(len(entity.DeclaredItems) == 0)
		self.assertTrue(len(entity.BodyItems) == 0)

	def test_Architecture(self):
		architecture = Architecture("arch_1")

		self.assertIsNotNone(architecture)
		self.assertTrue(architecture.Name == "arch_1")
		self.assertTrue(len(architecture.DeclaredItems) == 0)
		self.assertTrue(len(architecture.BodyItems) == 0)

	def test_Package(self):
		package = Package("pack_1")

		self.assertIsNotNone(package)
		self.assertTrue(package.Name == "pack_1")
		self.assertTrue(len(package.DeclaredItems) == 0)

	def test_PackageBody(self):
		packageBody = PackageBody("pack_1")

		self.assertIsNotNone(packageBody)
		self.assertTrue(packageBody.Name == "pack_1")
		self.assertTrue(len(packageBody.DeclaredItems) == 0)

	def test_Context(self):
		context = Context("ctx_1")

		self.assertIsNotNone(context)
		self.assertTrue(context.Name == "ctx_1")

	def test_Configuration(self):
		configuration = Configuration("conf_1")

		self.assertIsNotNone(configuration)
		self.assertTrue(configuration.Name == "conf_1")

	def test_SubType(self):
		subtype = SubType("bit")

		self.assertIsNotNone(subtype)
		self.assertTrue(subtype.Name == "bit")

	def test_Integer(self):
		integer = IntegerType("integer")

		self.assertIsNotNone(integer)
		self.assertTrue(integer.Name == "integer")

	def test_Real(self):
		real =    RealType("real")

		self.assertIsNotNone(real)
		self.assertTrue(real.Name == "real")

	def test_Array(self):
		array =   ArrayType("bit_vector")

		self.assertIsNotNone(array)
		self.assertTrue(array.Name == "bit_vector")

	def test_Record(self):
		record =  RecordType("range_record")

		self.assertIsNotNone(record)
		self.assertTrue(record.Name == "range_record")
