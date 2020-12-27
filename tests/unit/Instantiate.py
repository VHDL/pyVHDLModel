from pathlib  import Path
from unittest import TestCase

from pyVHDLModel.VHDLModel import Design, Library, Document, Entity, Architecture, PackageBody, Package, Configuration, Context


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

	def test_Document(self):
		path = Path("tests.vhdl")
		document = Document(path)

	def test_Entity(self):
		entity = Entity("entity_1")

	def test_Architecture(self):
		architecture = Architecture("arch_1")

	def test_Package(self):
		package = Package("pack_1")

	def test_PackageBody(self):
		packageBody = PackageBody("pack_1")

	def test_Context(self):
		packageBody = Context("ctx_1")

	def test_Configuration(self):
		packageBody = Configuration("conf_1")
