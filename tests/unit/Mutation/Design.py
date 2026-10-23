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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
Mutation tests for documents, design units and libraries of a design (:class:`~pyVHDLModel.Design`).
"""
from pathlib                import Path

from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document, Library
from pyVHDLModel.DesignUnit import Architecture, Entity, Package, PackageBody
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicateDesignUnitError
from pyVHDLModel.Exception  import DuplicateDocumentError, LibraryInUseError, LibraryNotRegisteredError
from pyVHDLModel.Exception  import EntityExistsInLibraryError, ArchitectureExistsInLibraryError
from pyVHDLModel.Exception  import PackageExistsInLibraryError
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.PSLModel   import VerificationUnit
from pyVHDLModel.Symbol     import PackageSymbol

from tests.unit             import _entitySymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _document(*designUnits, path: str = "design.vhdl") -> Document:
	"""A document of the design units."""
	document = Document(Path(path))
	for designUnit in designUnits:
		document.AddDesignUnit(designUnit)

	return document


def _design(*documents: Document) -> Design:
	"""A design with library ``lib`` holding the documents."""
	design = Design("design")
	library = design.GetLibrary("lib")
	for document in documents:
		design.AddDocument(document, library)

	return design


class DesignUnits(Testcase):
	"""Adding, inserting and removing design units of a document."""

	def test_AddDesignUnit(self) -> None:
		document = Document(Path("design.vhdl"))
		entity = Entity("ent")
		architecture = Architecture("rtl", _entitySymbol("ent"))
		package = Package("pkg")

		document.AddDesignUnit(entity)
		document.AddDesignUnit(architecture)
		document.AddDesignUnit(package)

		self.assertListEqual([entity, architecture, package], document.DesignUnits)
		self.assertDictEqual({"ent": entity}, document.Entities)
		self.assertDictEqual({"ent": {"rtl": architecture}}, document.Architectures)
		self.assertDictEqual({"pkg": package}, document.Packages)
		self.assertIs(document, entity.Document)
		self.assertIsNone(entity.Parent)

	def test_AddDesignUnit_PSL(self) -> None:
		document = Document(Path("design.vhdl"))
		verificationUnit = VerificationUnit("vu")

		document.AddDesignUnit(verificationUnit)

		self.assertListEqual([verificationUnit], document.DesignUnits)
		self.assertDictEqual({"vu": verificationUnit}, document.VerificationUnits)

	def test_InsertDesignUnit(self) -> None:
		entity = Entity("ent")
		document = _document(entity)
		package = Package("pkg")

		document.InsertDesignUnit(0, package)

		self.assertListEqual([package, entity], document.DesignUnits)

	def test_InsertDesignUnit_Negative(self) -> None:
		entity1 = Entity("ent1")
		entity2 = Entity("ent2")
		document = _document(entity1, entity2)
		package = Package("pkg")

		document.InsertDesignUnit(-1, package)

		self.assertListEqual([entity1, package, entity2], document.DesignUnits)

	def test_InsertDesignUnit_IndexNone(self) -> None:
		document = Document(Path("design.vhdl"))

		with self.assertRaises(ValueError) as context:
			document.InsertDesignUnit(None, Entity("ent"))

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_InsertDesignUnit_IndexType(self) -> None:
		document = Document(Path("design.vhdl"))

		with self.assertRaises(TypeError) as context:
			document.InsertDesignUnit("0", Entity("ent"))

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_InsertDesignUnit_IndexRange(self) -> None:
		document = _document(Entity("ent"))

		with self.assertRaises(ValueError) as context:
			document.InsertDesignUnit(2, Package("pkg"))

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)

	def test_AddDesignUnit_None(self) -> None:
		document = Document(Path("design.vhdl"))

		with self.assertRaises(ValueError) as context:
			document.AddDesignUnit(None)

		self.assertEqual("Parameter 'designUnit' is None.", str(context.exception))

	def test_AddDesignUnit_Type(self) -> None:
		document = Document(Path("design.vhdl"))

		with self.assertRaises(TypeError) as context:
			document.AddDesignUnit(Library("lib"))

		self.assertEqual("Parameter 'designUnit' is not of type 'DesignUnit'.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Library'."], context.exception.__notes__)

	def test_AddDesignUnit_AlreadyInDocument(self) -> None:
		entity = Entity("ent")
		otherDocument = _document(entity, path="other.vhdl")
		document = Document(Path("design.vhdl"))

		with self.assertRaises(AlreadyInDesignError) as context:
			document.AddDesignUnit(entity)

		self.assertEqual("Entity 'ent' is already a design unit of a document.", str(context.exception))
		self.assertListEqual(["Remove it from document 'other.vhdl' first."], context.exception.__notes__)
		self.assertIs(entity, context.exception.Element)
		self.assertIs(otherDocument, context.exception.Parent)
		self.assertListEqual([], document.DesignUnits)

	def test_AddDesignUnit_Duplicate(self) -> None:
		existing = Entity("ent")
		document = _document(existing)
		entity = Entity("Ent")

		with self.assertRaises(DuplicateDesignUnitError) as context:
			document.AddDesignUnit(entity)

		self.assertEqual("Document 'design.vhdl' already contains Entity 'ent'.", str(context.exception))
		self.assertListEqual(
			["Existing design unit is of type 'pyVHDLModel.DesignUnit.Entity'."],
			context.exception.__notes__
		)
		self.assertEqual("Ent", context.exception.Identifier)
		self.assertEqual("ent", context.exception.NormalizedIdentifier)
		self.assertIs(document, context.exception.Parent)
		self.assertIs(entity, context.exception.Element)
		self.assertIs(existing, context.exception.Existing)
		self.assertListEqual([existing], document.DesignUnits)
		self.assertIsNone(entity.Document)

	def test_AddDesignUnit_DuplicateArchitecture(self) -> None:
		"""An architecture is a duplicate for the same entity only."""
		document = _document(Architecture("rtl", _entitySymbol("ent1")))
		architecture = Architecture("rtl", _entitySymbol("ent2"))

		document.AddDesignUnit(architecture)

		with self.assertRaises(DuplicateDesignUnitError):
			document.AddDesignUnit(Architecture("rtl", _entitySymbol("ent2")))

		self.assertIs(architecture, document.Architectures["ent2"]["rtl"])

	def test_AddDesignUnit_Library(self) -> None:
		"""A document registered in a design adds the design unit to its library too."""
		document = Document(Path("design.vhdl"))
		design = _design(document)
		library = design.GetLibrary("lib")
		entity = Entity("ent")
		architecture = Architecture("rtl", _entitySymbol("ent"))

		document.AddDesignUnit(entity)
		document.AddDesignUnit(architecture)

		self.assertDictEqual({"ent": entity}, library.Entities)
		self.assertDictEqual({"ent": {"rtl": architecture}}, library.Architectures)
		self.assertIs(library, entity.Library)
		self.assertIs(library, architecture.Library)

	def test_AddDesignUnit_LibraryPSL(self) -> None:
		"""A PSL verification unit enters no library."""
		document = Document(Path("design.vhdl"))
		_design(document)
		verificationUnit = VerificationUnit("vu")

		document.AddDesignUnit(verificationUnit)

		self.assertIsNone(verificationUnit.Parent)

	def test_AddDesignUnit_LibraryDuplicate(self) -> None:
		existing = Entity("ent")
		document = Document(Path("design.vhdl"))
		design = _design(_document(existing, path="other.vhdl"), document)
		library = design.GetLibrary("lib")
		entity = Entity("ent")

		with self.assertRaises(EntityExistsInLibraryError) as context:
			document.AddDesignUnit(entity)

		self.assertEqual("Entity 'ent' already exists in library 'lib'.", str(context.exception))
		self.assertIs(entity, context.exception.Entity)
		self.assertIs(library, context.exception.Library)
		self.assertListEqual([], document.DesignUnits)
		self.assertIs(existing, library.Entities["ent"])
		self.assertIsNone(entity.Parent)

	def test_AddDesignUnit_LibraryDuplicateArchitecture(self) -> None:
		document = Document(Path("design.vhdl"))
		design = _design(_document(Entity("ent"), Architecture("rtl", _entitySymbol("ent")), path="other.vhdl"), document)

		with self.assertRaises(ArchitectureExistsInLibraryError) as context:
			document.AddDesignUnit(Architecture("rtl", _entitySymbol("ent")))

		self.assertIs(design.GetLibrary("lib").Entities["ent"], context.exception.Entity)
		self.assertDictEqual({}, document.Architectures)

	def test_RemoveDesignUnit(self) -> None:
		entity = Entity("ent")
		package = Package("pkg")
		document = _document(entity, package)

		document.RemoveDesignUnit(entity)

		self.assertListEqual([package], document.DesignUnits)
		self.assertDictEqual({}, document.Entities)
		self.assertIsNone(entity.Document)

	def test_RemoveDesignUnit_Library(self) -> None:
		"""A document registered in a design removes the design unit from its library too."""
		entity = Entity("ent")
		architecture = Architecture("rtl", _entitySymbol("ent"))
		document = _document(entity, architecture)
		design = _design(document)
		library = design.GetLibrary("lib")

		document.RemoveDesignUnit(architecture)

		self.assertDictEqual({}, document.Architectures)
		self.assertDictEqual({}, library.Architectures)
		self.assertDictEqual({"ent": entity}, library.Entities)
		self.assertIsNone(architecture.Parent)
		self.assertIsNone(architecture.Document)

	def test_RemoveDesignUnit_Move(self) -> None:
		"""A removed design unit can be added to another document."""
		packageBody = PackageBody(PackageSymbol(SimpleName("pkg")))
		document1 = _document(Package("pkg"), packageBody, path="a.vhdl")
		document2 = Document(Path("b.vhdl"))
		design = _design(document1, document2)

		document1.RemoveDesignUnit(packageBody)
		document2.AddDesignUnit(packageBody)

		self.assertListEqual([packageBody], document2.DesignUnits)
		self.assertIs(document2, packageBody.Document)
		self.assertIs(packageBody, design.GetLibrary("lib").PackageBodies["pkg"])

	def test_RemoveDesignUnit_None(self) -> None:
		document = Document(Path("design.vhdl"))

		with self.assertRaises(ValueError) as context:
			document.RemoveDesignUnit(None)

		self.assertEqual("Parameter 'designUnit' is None.", str(context.exception))

	def test_RemoveDesignUnit_Type(self) -> None:
		document = Document(Path("design.vhdl"))

		with self.assertRaises(TypeError) as context:
			document.RemoveDesignUnit("ent")

		self.assertEqual("Parameter 'designUnit' is not of type 'DesignUnit'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_RemoveDesignUnit_NotAChild(self) -> None:
		document = Document(Path("design.vhdl"))
		entity = Entity("ent")

		with self.assertRaises(NotAChildError) as context:
			document.RemoveDesignUnit(entity)

		self.assertEqual("Entity 'ent' is not a design unit of document 'design.vhdl'.", str(context.exception))
		self.assertIs(entity, context.exception.Element)
		self.assertIs(document, context.exception.Parent)


class Documents(Testcase):
	"""Adding and removing documents of a design."""

	def test_AddDocument_Duplicate(self) -> None:
		existing = Document(Path("design.vhdl"))
		design = _design(existing)
		document = Document(Path("design.vhdl"))

		with self.assertRaises(DuplicateDocumentError) as context:
			design.AddDocument(document, design.GetLibrary("lib"))

		self.assertEqual("Design already contains a document of path 'design.vhdl'.", str(context.exception))
		self.assertEqual(Path("design.vhdl"), context.exception.Path)
		self.assertIs(design, context.exception.Parent)
		self.assertIs(document, context.exception.Element)
		self.assertIs(existing, context.exception.Existing)
		self.assertListEqual([existing], design.Documents)
		self.assertIsNone(document.Parent)

	def test_AddDocument_AlreadyInDesign(self) -> None:
		document = Document(Path("design.vhdl"))
		otherDesign = _design(document)
		design = Design("design")

		with self.assertRaises(AlreadyInDesignError) as context:
			design.AddDocument(document, design.GetLibrary("lib"))

		self.assertEqual("Document 'design.vhdl' is already a document of a design.", str(context.exception))
		self.assertIs(otherDesign, context.exception.Parent)
		self.assertListEqual([], design.Documents)

	def test_AddDocument_LibraryNotRegistered(self) -> None:
		"""A library of the same name, which isn't the design's library, is rejected."""
		design = Design("design")
		design.GetLibrary("lib")

		with self.assertRaises(LibraryNotRegisteredError):
			design.AddDocument(Document(Path("design.vhdl")), Library("lib"))

		self.assertListEqual([], design.Documents)

	def test_AddDocument_Clash(self) -> None:
		"""A clash of the last design unit leaves the design and the library unchanged."""
		design = _design(_document(Package("pkg"), path="other.vhdl"))
		library = design.GetLibrary("lib")
		entity = Entity("ent")
		document = _document(entity, Package("pkg"))

		with self.assertRaises(PackageExistsInLibraryError):
			design.AddDocument(document, library)

		self.assertEqual(1, len(design.Documents))
		self.assertDictEqual({}, library.Entities)
		self.assertIsNone(entity.Parent)
		self.assertIsNone(document.Library)

	def test_RemoveDocument(self) -> None:
		entity = Entity("ent")
		architecture = Architecture("rtl", _entitySymbol("ent"))
		package = Package("pkg")
		document = _document(entity, architecture, package)
		design = _design(document)
		library = design.GetLibrary("lib")

		design.RemoveDocument(document)

		self.assertListEqual([], design.Documents)
		self.assertDictEqual({}, library.Entities)
		self.assertDictEqual({}, library.Architectures)
		self.assertDictEqual({}, library.Packages)
		self.assertIsNone(document.Parent)
		self.assertIsNone(document.Library)
		self.assertIsNone(entity.Parent)
		self.assertListEqual([entity, architecture, package], document.DesignUnits)
		self.assertIs(document, entity.Document)

	def test_RemoveDocument_AddAgain(self) -> None:
		entity = Entity("ent")
		document = _document(entity)
		design = _design(document)
		library = design.GetLibrary("lib")
		design.RemoveDocument(document)

		design.AddDocument(document, library)

		self.assertListEqual([document], design.Documents)
		self.assertIs(entity, library.Entities["ent"])
		self.assertIs(library, entity.Library)

	def test_RemoveDocument_None(self) -> None:
		design = Design("design")

		with self.assertRaises(ValueError) as context:
			design.RemoveDocument(None)

		self.assertEqual("Parameter 'document' is None.", str(context.exception))

	def test_RemoveDocument_Type(self) -> None:
		design = Design("design")

		with self.assertRaises(TypeError) as context:
			design.RemoveDocument(Path("design.vhdl"))

		self.assertEqual("Parameter 'document' is not of type 'Document'.", str(context.exception))

	def test_RemoveDocument_PathFreed(self) -> None:
		"""After a document is removed, another document of the same path can be added."""
		document = _document(Entity("ent"))
		design =   _design(document)
		other =    _document(Entity("other"))
		design.RemoveDocument(document)

		design.AddDocument(other, design.GetLibrary("lib"))

		self.assertListEqual([other], design.Documents)

	def test_RemoveDocument_SamePath(self) -> None:
		"""A document of the same path as a document of the design, but another object, isn't a document of the design."""
		document = _document(Entity("ent"))
		design =   _design(document)
		other =    _document(Entity("other"))

		with self.assertRaises(NotAChildError):
			design.RemoveDocument(other)

		self.assertListEqual([document], design.Documents)

	def test_RemoveDocument_Order(self) -> None:
		"""Removing a document keeps the order of the others."""
		first =  _document(Entity("a"), path="a.vhdl")
		second = _document(Entity("b"), path="b.vhdl")
		third =  _document(Entity("c"), path="c.vhdl")
		design = _design(first, second, third)

		design.RemoveDocument(second)

		self.assertListEqual([first, third], design.Documents)

	def test_RemoveDocument_NotAChild(self) -> None:
		design = Design("design")
		document = Document(Path("design.vhdl"))

		with self.assertRaises(NotAChildError) as context:
			design.RemoveDocument(document)

		self.assertEqual("Document 'design.vhdl' is not a document of this design.", str(context.exception))
		self.assertIs(document, context.exception.Element)
		self.assertIs(design, context.exception.Parent)


class Libraries(Testcase):
	"""Removing libraries of a design."""

	def test_RemoveLibrary(self) -> None:
		design = Design("design")
		library = design.GetLibrary("lib")

		design.RemoveLibrary(library)

		self.assertDictEqual({}, design.Libraries)
		self.assertIsNone(library.Parent)

	def test_RemoveLibrary_AddAgain(self) -> None:
		design = Design("design")
		library = design.GetLibrary("lib")
		design.RemoveLibrary(library)

		design.AddLibrary(library)

		self.assertDictEqual({"lib": library}, design.Libraries)
		self.assertIs(design, library.Parent)

	def test_RemoveLibrary_InUse(self) -> None:
		document1 = Document(Path("a.vhdl"))
		document2 = Document(Path("b.vhdl"))
		design = _design(document1, document2)
		library = design.GetLibrary("lib")

		with self.assertRaises(LibraryInUseError) as context:
			design.RemoveLibrary(library)

		self.assertEqual("Library 'lib' is used by 2 document(s).", str(context.exception))
		self.assertListEqual(
			["Used by: 'a.vhdl', 'b.vhdl'.", "Remove the documents from the design first."],
			context.exception.__notes__
		)
		self.assertIs(library, context.exception.Element)
		self.assertTupleEqual((document1, document2), context.exception.Users)
		self.assertIs(design, library.Parent)

	def test_RemoveLibrary_AfterRemoveDocument(self) -> None:
		document = _document(Entity("ent"))
		design = _design(document)
		library = design.GetLibrary("lib")
		design.RemoveDocument(document)

		design.RemoveLibrary(library)

		self.assertDictEqual({}, design.Libraries)

	def test_RemoveLibrary_None(self) -> None:
		design = Design("design")

		with self.assertRaises(ValueError) as context:
			design.RemoveLibrary(None)

		self.assertEqual("Parameter 'library' is None.", str(context.exception))

	def test_RemoveLibrary_Type(self) -> None:
		design = Design("design")

		with self.assertRaises(TypeError) as context:
			design.RemoveLibrary("lib")

		self.assertEqual("Parameter 'library' is not of type 'Library'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_RemoveLibrary_NotAChild(self) -> None:
		"""A library of the same name, which isn't the design's library, is no child."""
		design = Design("design")
		design.GetLibrary("lib")
		library = Library("lib")

		with self.assertRaises(NotAChildError) as context:
			design.RemoveLibrary(library)

		self.assertEqual("Library 'lib' is not a library of this design.", str(context.exception))
		self.assertIs(library, context.exception.Element)
		self.assertIs(design, context.exception.Parent)
