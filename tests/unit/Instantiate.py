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
		library = Library()

		self.assertIsNotNone(library)

	def test_Document(self):
		path = Path("tests.vhdl")
		document = Document(path)

		self.assertIsNotNone(document)

	def test_Entity(self):
		entity = Entity("entity_1")

		self.assertIsNotNone(entity)

	def test_Architecture(self):
		architecture = Architecture("arch_1")

		self.assertIsNotNone(architecture)

	def test_Package(self):
		package = Package("pack_1")

		self.assertIsNotNone(package)

	def test_PackageBody(self):
		packageBody = PackageBody("pack_1")

		self.assertIsNotNone(packageBody)

	def test_Context(self):
		context = Context("ctx_1")

		self.assertIsNotNone(context)

	def test_Configuration(self):
		configuration = Configuration("conf_1")

		self.assertIsNotNone(configuration)

	def test_SubType(self):
		subtype = SubType("bit")

		self.assertIsNotNone(subtype)

	def test_Integer(self):
		integer = IntegerType("integer")

		self.assertIsNotNone(integer)

	def test_Real(self):
		real =    RealType("real")

		self.assertIsNotNone(real)

	def test_Array(self):
		array =   ArrayType("bit_vector")

		self.assertIsNotNone(array)

	def test_Record(self):
		record =  RecordType("range_record")

		self.assertIsNotNone(record)
