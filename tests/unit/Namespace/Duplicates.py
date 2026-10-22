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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Duplicate declarations: the same identifier declared **twice in one declarative region**.

This is not hiding. VHDL rejects it as *identifier already used for a declaration*, and a declarative
region can span more than one namespace in this model - an entity and its architecture are one region,
as are a package and its body - so the check follows those links.

Overloadable declarations are exempt: several subprograms may share a name. Signatures are not compared
yet, so any two subprograms sharing a name are accepted.

The expectations below were established with the GHDL analyzer (``ghdl -a --std=08``).
"""
from pathlib import Path

from pyTooling.Warning      import CriticalWarning, UnhandledCriticalWarningError, WarningCollector
from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document, Library
from pyVHDLModel.Base       import Mode
from pyVHDLModel.DesignUnit import Architecture, Entity, Package, PackageBody
from pyVHDLModel.Exception  import DuplicateDeclarationWarning, VHDLModelCriticalWarning
from pyVHDLModel.Interface  import PortSimpleSignalInterfaceItem
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Object     import Constant, Signal
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.Symbol     import EntitySymbol, PackageSymbol, SimpleSubtypeSymbol

from tests.unit             import _signal, _subtypeSymbol, _warningsOfType


if __name__ == "__main__":
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)



class OneDeclarativePart(Testcase):
	"""Two declarations in the same declarative part."""

	def test_TwoSignalsWithTheSameName(self) -> None:
		items = [_signal("s", "natural"), _signal("s", "natural")]
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=items)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		self.assertEqual(1, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_WarningFields(self) -> None:
		"""The warning carries the identifier, the namespace and both declarations."""
		items = [_signal("s", "natural"), _signal("S", "natural")]
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=items)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		warning = _warningsOfType(collector, DuplicateDeclarationWarning)[0]
		self.assertEqual("S", warning.Identifier)
		self.assertEqual("s", warning.NormalizedIdentifier)
		self.assertIs(architecture._namespace, warning.Namespace)
		self.assertIs(items[0], warning.Existing)
		self.assertIs(items[1], warning.Element)

	def test_WarningFields_MessageOnly(self) -> None:
		warning = DuplicateDeclarationWarning("Identifier is already used for a declaration.")

		self.assertIsNone(warning.Identifier)
		self.assertIsNone(warning.NormalizedIdentifier)
		self.assertIsNone(warning.Namespace)
		self.assertIsNone(warning.Element)
		self.assertIsNone(warning.Existing)

	def test_Critical(self) -> None:
		"""A duplicate declaration is a critical warning."""
		warning = DuplicateDeclarationWarning("Identifier is already used for a declaration.")

		self.assertIsInstance(warning, VHDLModelCriticalWarning)
		self.assertIsInstance(warning, CriticalWarning)

	def test_WithoutCollector(self) -> None:
		"""Without a collector, a duplicate declaration raises, caused by the warning."""
		items = [_signal("s", "natural"), _signal("s", "natural")]
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=items)

		with self.assertRaises(UnhandledCriticalWarningError) as context:
			architecture.IndexDeclaredItems()

		self.assertIsInstance(context.exception.__cause__, DuplicateDeclarationWarning)

	def test_SignalAndConstantWithTheSameName(self) -> None:
		"""Different kinds still collide - VHDL keys on the identifier, not the kind."""
		items = [_signal("s", "natural"), Constant(["s"], _subtypeSymbol("bit"))]
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=items)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		self.assertEqual(1, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_DistinctNamesAreAccepted(self) -> None:
		items = [_signal("a", "natural"), _signal("b", "natural")]
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=items)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_ReIndexingIsNotADuplicate(self) -> None:
		"""Indexing twice must not report the *same* item as a duplicate."""
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=[_signal("s", "natural")])

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()
			architecture.IndexDeclaredItems()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_DeclarationHidesVisiblePackage(self) -> None:
		"""A package made visible by 'use lib.pkg;' (its parent is a library) is hidden by a declaration of its name."""
		package = Package("pkg")
		package.Library = Library("lib")
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=[_signal("pkg", "natural")])
		architecture._namespace.AddImport("pkg", package)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))
		self.assertIs(architecture.DeclaredItems[0], architecture._namespace._elements["pkg"])

	def test_DeclarationHidesImportedItem(self) -> None:
		"""An item imported by a use clause is hidden by a declaration of the same identifier."""
		imported = Constant(["s"], _subtypeSymbol("bit"))
		Package("other", declaredItems=[imported])
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=[_signal("s", "natural")])
		architecture._namespace.AddImport("s", imported)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))
		self.assertIs(architecture.DeclaredItems[0], architecture._namespace._elements["s"])


class OverloadableDeclarations(Testcase):
	"""Subprograms may share a name; GHDL accepts them as long as the signatures differ."""

	def test_TwoProceduresSharingAName(self) -> None:
		package = Package("pk", declaredItems=[Procedure("foo"), Procedure("foo")])

		with WarningCollector() as collector:
			package.IndexDeclaredItems()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_FunctionAndProcedureSharingAName(self) -> None:
		package = Package("pk", declaredItems=[Procedure("foo"), Function("foo", _subtypeSymbol("bit"))])

		with WarningCollector() as collector:
			package.IndexDeclaredItems()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_SubprogramCollidesWithASignal(self) -> None:
		"""A subprogram is overloadable, but not against a non-overloadable declaration."""
		items = [_signal("foo", "natural"), Procedure("foo")]
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=items)

		with WarningCollector() as collector:
			architecture.IndexDeclaredItems()

		self.assertEqual(1, len(_warningsOfType(collector, DuplicateDeclarationWarning)))


class RegionsSpanningTwoNamespaces(Testcase):
	"""An entity and its architecture, and a package and its body, are each one declarative region."""

	def _design(self, entityItems, architectureItems, packageItems, bodyItems) -> Design:
		design = Design()
		library = Library("work")
		design.AddLibrary(library)
		document = Document(Path("virtual.vhdl"))

		document._AddDesignUnit(Entity("ent", declaredItems=entityItems))
		document._AddDesignUnit(Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=architectureItems))
		document._AddDesignUnit(Package("pk", declaredItems=packageItems))
		document._AddDesignUnit(PackageBody(PackageSymbol(SimpleName("pk")), declaredItems=bodyItems))

		design.AddDocument(document, library)
		design.CreateDependencyGraph()
		design.LinkArchitectures()
		design.LinkPackageBodies()
		return design

	def test_ArchitectureDeclarationDuplicatesEntityDeclaration(self) -> None:
		design = self._design([_signal("x", "natural")], [_signal("x", "natural")], [], [])

		with WarningCollector() as collector:
			design.IndexEntities()
			design.IndexArchitectures()

		self.assertEqual(1, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_ArchitectureDeclarationDuplicatesEntityPort(self) -> None:
		ports = [PortSimpleSignalInterfaceItem(["p"], Mode.In, _subtypeSymbol("bit"))]
		design = Design()
		library = Library("work")
		design.AddLibrary(library)
		document = Document(Path("virtual.vhdl"))
		document._AddDesignUnit(Entity("ent", portItems=ports))
		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=[_signal("p", "natural")])
		document._AddDesignUnit(architecture)
		design.AddDocument(document, library)
		design.CreateDependencyGraph()
		design.LinkArchitectures()

		with WarningCollector() as collector:
			design.IndexEntities()
			design.IndexArchitectures()

		self.assertEqual(1, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_PackageBodyDeclarationDuplicatesPackageDeclaration(self) -> None:
		design = self._design([], [], [Constant(["c"], _subtypeSymbol("bit"))], [Constant(["c"], _subtypeSymbol("bit"))])

		with WarningCollector() as collector:
			design.IndexPackages()
			design.IndexPackageBodies()

		self.assertEqual(1, len(_warningsOfType(collector, DuplicateDeclarationWarning)))

	def test_DistinctNamesAcrossTheRegionAreAccepted(self) -> None:
		design = self._design([_signal("a", "natural")], [_signal("b", "natural")], [], [])

		with WarningCollector() as collector:
			design.IndexEntities()
			design.IndexArchitectures()

		self.assertEqual(0, len(_warningsOfType(collector, DuplicateDeclarationWarning)))
