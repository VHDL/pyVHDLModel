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
Mutation tests for namespaces (:class:`~pyVHDLModel.Namespace.Namespace`).
"""
from pathlib                import Path

from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document
from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.DesignUnit import Architecture, Component, Entity, Package, UseClause
from pyVHDLModel.Exception  import NotInNamespaceError
from pyVHDLModel.Name       import AllName, SelectedName, SimpleName
from pyVHDLModel.Namespace  import Namespace
from pyVHDLModel.Symbol     import AllPackageMembersReferenceSymbol, PackageReferenceSymbol, PossibleReference, Symbol

from tests.unit             import _entitySymbol
from tests.unit.Mutation    import _constant, _generic, _port


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Namespaces(Testcase):
	def test_RemoveElement(self) -> None:
		namespace = Namespace("rtl")
		bits = _generic("BITS")
		clock = _port("Clock")
		namespace.AddElement("bits", bits)
		namespace.AddElement("clock", clock)

		namespace.RemoveElement("bits", bits)

		self.assertDictEqual({"clock": clock}, namespace.Elements())

	def test_RemoveElement_NotDeclared(self) -> None:
		namespace = Namespace("rtl")

		with self.assertRaises(NotInNamespaceError) as context:
			namespace.RemoveElement("bits", _generic("BITS"))

		self.assertEqual("Namespace 'rtl' has no element 'bits'.", str(context.exception))
		self.assertFalse(context.exception.HasNotes)
		self.assertEqual("BITS", context.exception.Identifier)
		self.assertEqual("bits", context.exception.NormalizedIdentifier)
		self.assertIs(namespace, context.exception.Namespace)

	def test_RemoveElement_OtherElement(self) -> None:
		namespace = Namespace("rtl")
		clock = _port("bits")
		namespace.AddElement("bits", clock)

		with self.assertRaises(NotInNamespaceError) as context:
			namespace.RemoveElement("bits", _generic("BITS"))

		self.assertEqual("Namespace 'rtl' has another element for 'bits'.", str(context.exception))
		self.assertListEqual(
			["Found element of type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertEqual("BITS", context.exception.Identifier)
		self.assertEqual("bits", context.exception.NormalizedIdentifier)
		self.assertIs(namespace, context.exception.Namespace)
		self.assertDictEqual({"bits": clock}, namespace.Elements())

	def test_RemoveElement_KeyError(self) -> None:
		"""The error is caught like a missing key of a dictionary."""
		namespace = Namespace("rtl")

		with self.assertRaises(KeyError):
			namespace.RemoveElement("bits", _generic("BITS"))


class ParentNamespaces(Testcase):
	"""The link between a namespace and its parent namespace is two-sided."""

	def test_ParentNamespace(self) -> None:
		parent = Namespace("ent")
		namespace = Namespace("rtl")

		namespace.ParentNamespace = parent

		self.assertIs(parent, namespace.ParentNamespace)
		self.assertListEqual([namespace], parent.SubNamespaces)

	def test_ParentNamespace_Constructor(self) -> None:
		parent = Namespace("ent")

		namespace = Namespace("rtl", parent)

		self.assertIs(parent, namespace.ParentNamespace)
		self.assertListEqual([namespace], parent.SubNamespaces)

	def test_ParentNamespace_Change(self) -> None:
		oldParent = Namespace("ent1")
		newParent = Namespace("ent2")
		namespace = Namespace("rtl", oldParent)

		namespace.ParentNamespace = newParent

		self.assertIs(newParent, namespace.ParentNamespace)
		self.assertListEqual([], oldParent.SubNamespaces)
		self.assertListEqual([namespace], newParent.SubNamespaces)

	def test_ParentNamespace_Same(self) -> None:
		parent = Namespace("ent")
		namespace = Namespace("rtl", parent)

		namespace.ParentNamespace = parent

		self.assertListEqual([namespace], parent.SubNamespaces)

	def test_ParentNamespace_None(self) -> None:
		parent = Namespace("ent")
		namespace = Namespace("rtl", parent)

		namespace.ParentNamespace = None

		self.assertIsNone(namespace.ParentNamespace)
		self.assertListEqual([], parent.SubNamespaces)

	def test_ParentNamespace_Type(self) -> None:
		parent = Namespace("ent")
		namespace = Namespace("rtl", parent)

		with self.assertRaises(TypeError) as context:
			namespace.ParentNamespace = "ent"

		self.assertEqual("Parameter 'parentNamespace' is not of type 'Namespace'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertIs(parent, namespace.ParentNamespace)
		self.assertListEqual([namespace], parent.SubNamespaces)

	def test_ParentNamespace_Unnamed(self) -> None:
		"""Several sub-namespaces without a name are kept apart."""
		parent = Namespace("rtl")
		namespace1 = Namespace(None, parent)
		namespace2 = Namespace(None, parent)

		self.assertListEqual([namespace1, namespace2], parent.SubNamespaces)

	def test_UnlabeledProcesses(self) -> None:
		process1 = ProcessStatement()
		process2 = ProcessStatement()

		architecture = Architecture("rtl", _entitySymbol("ent"), statements=[process1, process2])

		self.assertListEqual([process1._namespace, process2._namespace], architecture._namespace.SubNamespaces)

	def test_MoveProcess(self) -> None:
		process = ProcessStatement("proc")
		architecture1 = Architecture("rtl1", _entitySymbol("ent"), statements=[process])
		architecture2 = Architecture("rtl2", _entitySymbol("ent"))

		architecture1.RemoveStatement(process)
		architecture2.AddStatement(process)

		self.assertIs(architecture2._namespace, process._namespace.ParentNamespace)
		self.assertListEqual([], architecture1._namespace.SubNamespaces)
		self.assertListEqual([process._namespace], architecture2._namespace.SubNamespaces)

	def test_LinkArchitectures(self) -> None:
		"""Linking an architecture to its entity links the namespaces on both sides."""
		design = _design(Entity("ent"), Architecture("rtl", _entitySymbol("ent")))
		entity = design.GetEntity("lib", "ent")
		architecture = entity.Architectures["rtl"]

		self.assertIs(entity._namespace, architecture._namespace.ParentNamespace)
		self.assertListEqual([architecture._namespace], entity._namespace.SubNamespaces)


class ImportedItems(Testcase):
	"""Items imported into a namespace by a use clause are kept apart from the declarations."""

	def test_AddImport(self) -> None:
		namespace = Namespace("rtl")
		imported = _constant("BITS")
		Package("pkg", declaredItems=[imported])

		namespace.AddImport("bits", imported)

		self.assertDictEqual({"bits": imported}, namespace.Imports())
		self.assertDictEqual({}, namespace.Elements())
		self.assertIs(imported, namespace.FindObject(Symbol(SimpleName("BITS"), PossibleReference.Constant)))

	def test_AddImport_Declared(self) -> None:
		"""A lookup finds a declaration before an imported item of the same identifier."""
		namespace = Namespace("rtl")
		imported = _constant("BITS")
		Package("pkg", declaredItems=[imported])
		constant = _constant("BITS")
		namespace.AddElement("bits", constant)

		namespace.AddImport("bits", imported)

		self.assertDictEqual({"bits": constant}, namespace.Elements())
		self.assertDictEqual({"bits": imported}, namespace.Imports())
		self.assertIs(constant, namespace.FindObject(Symbol(SimpleName("BITS"), PossibleReference.Constant)))

	def test_RemoveImport(self) -> None:
		namespace = Namespace("rtl")
		imported = _constant("BITS")
		constant = _constant("BITS")
		namespace.AddElement("bits", constant)
		namespace.AddImport("bits", imported)

		namespace.RemoveImport("bits", imported)

		self.assertDictEqual({}, namespace.Imports())
		self.assertDictEqual({"bits": constant}, namespace.Elements())

	def test_RemoveImport_NotImported(self) -> None:
		namespace = Namespace("rtl")
		constant = _constant("BITS")
		namespace.AddElement("bits", constant)

		with self.assertRaises(NotInNamespaceError) as context:
			namespace.RemoveImport("bits", constant)

		self.assertEqual("Namespace 'rtl' has no import 'bits'.", str(context.exception))
		self.assertFalse(context.exception.HasNotes)
		self.assertEqual("BITS", context.exception.Identifier)
		self.assertIs(namespace, context.exception.Namespace)
		self.assertDictEqual({"bits": constant}, namespace.Elements())

	def test_RemoveImport_OtherElement(self) -> None:
		namespace = Namespace("rtl")
		imported = _constant("BITS")
		namespace.AddImport("bits", imported)

		with self.assertRaises(NotInNamespaceError) as context:
			namespace.RemoveImport("bits", _generic("BITS"))

		self.assertEqual("Namespace 'rtl' has another import for 'bits'.", str(context.exception))
		self.assertListEqual(["Found element of type 'pyVHDLModel.Object.Constant'."], context.exception.__notes__)
		self.assertDictEqual({"bits": imported}, namespace.Imports())

	def test_ClearImports(self) -> None:
		namespace = Namespace("rtl")
		constant = _constant("BITS")
		namespace.AddElement("bits", constant)
		namespace.AddImport("bits", _constant("BITS"))
		namespace.AddImport("width", _constant("WIDTH"))

		namespace.ClearImports()

		self.assertDictEqual({}, namespace.Imports())
		self.assertDictEqual({"bits": constant}, namespace.Elements())

	def test_RemoveDeclaredItem(self) -> None:
		"""Removing a declaration makes the imported item of the same identifier visible again."""
		imported = _constant("BITS")
		Package("pkg", declaredItems=[imported])
		architecture = Architecture("rtl", _entitySymbol("ent"))
		architecture.IndexDeclaredItems()
		architecture._namespace.AddImport("bits", imported)
		constant = _constant("BITS")
		architecture.AddDeclaredItem(constant)

		architecture.RemoveDeclaredItem(constant)

		self.assertDictEqual({}, architecture._namespace.Elements())
		self.assertIs(imported, architecture._namespace.FindObject(Symbol(SimpleName("BITS"), PossibleReference.Constant)))

	def test_UseClause_Package(self) -> None:
		"""A use clause naming a package imports the package."""
		useClause = UseClause([PackageReferenceSymbol(SelectedName("pkg", SimpleName("work")))])
		design = _design(Package("pkg"), Entity("ent", [useClause]))
		package = design.GetPackage("lib", "pkg")
		entity = design.GetEntity("lib", "ent")

		self.assertDictEqual({"pkg": package}, entity._namespace.Imports())
		self.assertNotIn("pkg", entity._namespace.Elements())

	def test_UseClause_All(self) -> None:
		"""A use clause naming all members of a package imports the package's components."""
		component = Component("comp")
		useClause = UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName("pkg", SimpleName("work"))))])
		design = _design(Package("pkg", declaredItems=[component]), Entity("comp"), Entity("ent", [useClause]))
		entity = design.GetEntity("lib", "ent")

		self.assertDictEqual({"comp": component}, entity._namespace.Imports())
		self.assertDictEqual({}, entity._namespace.Elements())


def _design(*designUnits) -> Design:
	"""An analyzed design with library ``lib`` holding one document of the design units."""
	design = Design("design")
	design.LoadStdLibrary()
	design.LoadIEEELibrary()
	library = design.GetLibrary("lib")
	document = Document(Path("design.vhdl"))
	for designUnit in designUnits:
		document._AddDesignUnit(designUnit)

	design.AddDocument(document, library)
	design.Analyze()

	return design
