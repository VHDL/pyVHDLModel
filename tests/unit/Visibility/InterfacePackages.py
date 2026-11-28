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
Interface packages (IEEE Std 1076-2008, 6.5.5): their uninstantiated package, and use clauses naming them.

The analysis links the uninstantiated package of a generic package; a use clause naming the interface package makes the
declarations of the generic package potentially visible.
"""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import DependencyGraphEdgeKind
from pyVHDLModel.DesignUnit import LibraryClause, Package
from pyVHDLModel.Exception  import UnresolvedNameWarning
from pyVHDLModel.Interface  import GenericPackageInterfaceItem, GenericTypeInterfaceItem
from pyVHDLModel.Name       import SelectedName, SimpleName
from pyVHDLModel.Symbol     import LibraryReferenceSymbol, PackageReferenceSymbol

from tests.unit.Visibility  import _constant, _design, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _interfacePackage(identifier: str, library: str, package: str) -> GenericPackageInterfaceItem:
	"""``package <identifier> is new <library>.<package> generic map (<>)``."""
	return GenericPackageInterfaceItem(
		identifier,
		genericPackage=PackageReferenceSymbol(SelectedName(package, SimpleName(library)))
	)


def _libraryClause(identifier: str) -> LibraryClause:
	"""A library clause of one library."""
	return LibraryClause([LibraryReferenceSymbol(SimpleName(identifier))])


class Linking(Testcase):
	"""The analysis links the uninstantiated package of an interface package."""

	def test_Library(self) -> None:
		"""``library lib; package p is generic (package ip is new lib.gp generic map (<>)); ...``"""
		genericPackage =   Package("gp", genericItems=[GenericTypeInterfaceItem("GT")])
		interfacePackage = _interfacePackage("ip", "lib", "gp")
		package =          Package("p", [_libraryClause("lib")], genericItems=[interfacePackage])
		_design(genericPackage, package)

		self.assertIs(genericPackage, interfacePackage.PackageReference.Reference)

	def test_Work(self) -> None:
		"""``package ip is new work.gp generic map (<>)`` needs no library clause."""
		genericPackage =   Package("gp", genericItems=[GenericTypeInterfaceItem("GT")])
		interfacePackage = _interfacePackage("ip", "work", "gp")
		_design(genericPackage, Package("p", genericItems=[interfacePackage]))

		self.assertIs(genericPackage, interfacePackage.PackageReference.Reference)

	def test_DependencyGraph(self) -> None:
		"""The design unit depends on the generic package."""
		genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")])
		package =        Package("p", genericItems=[_interfacePackage("ip", "work", "gp")])
		_design(genericPackage, package)

		edges = [
			edge for edge in package.DependencyVertex.IterateOutboundEdges()
			if edge.Destination is genericPackage.DependencyVertex
		]
		self.assertEqual(1, len(edges))
		self.assertIs(DependencyGraphEdgeKind.PackageInstantiation, edges[0]["kind"])

	def test_IEEE(self) -> None:
		"""``package fixed_pkg is new IEEE.fixed_generic_pkg generic map (<>)``, as ``float_generic_pkg`` declares it."""
		interfacePackage = _interfacePackage("fixed_pkg", "IEEE", "fixed_generic_pkg")
		design =           _design(Package("p", [_libraryClause("ieee")], genericItems=[interfacePackage]))

		self.assertIs(
			design.Libraries["ieee"].Packages["fixed_generic_pkg"],
			interfacePackage.PackageReference.Reference
		)

	def test_NotFound(self) -> None:
		"""A package, which the library doesn't contain, is reported; the reference stays unset."""
		interfacePackage = _interfacePackage("ip", "work", "missing")
		with WarningCollector() as collector:
			_design(Package("p", genericItems=[interfacePackage]), analyze=False).Analyze()

		warnings = [warning for warning in collector.Warnings if isinstance(warning, UnresolvedNameWarning)]
		self.assertEqual(1, len(warnings))
		self.assertEqual("Library 'lib' has no package 'missing' for interface package 'ip'.", str(warnings[0]))
		self.assertIsNone(interfacePackage.PackageReference.Reference)

	def test_LibraryNotVisible(self) -> None:
		"""A library name without library clause is reported."""
		interfacePackage = _interfacePackage("ip", "other", "gp")
		with WarningCollector() as collector:
			_design(Package("p", genericItems=[interfacePackage]), analyze=False).Analyze()

		warnings = [warning for warning in collector.Warnings if isinstance(warning, UnresolvedNameWarning)]
		self.assertEqual(1, len(warnings))
		self.assertEqual("Library 'other' of interface package 'ip' isn't visible.", str(warnings[0]))

	def test_NotGeneric(self) -> None:
		"""A package without generics isn't an uninstantiated generic package."""
		interfacePackage = _interfacePackage("ip", "work", "q")
		with WarningCollector() as collector:
			_design(Package("q"), Package("p", genericItems=[interfacePackage]), analyze=False).Analyze()

		warnings = [warning for warning in collector.Warnings if isinstance(warning, UnresolvedNameWarning)]
		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Package 'q' of interface package 'ip' isn't an uninstantiated generic package.",
			str(warnings[0])
		)
		self.assertIsNone(interfacePackage.PackageReference.Reference)


class UseClauses(Testcase):
	"""A use clause naming an interface package imports the declarations of its generic package."""

	def setUp(self) -> None:
		self._constant =       _constant("K", "integer")
		self._genericPackage = Package("gp", genericItems=[GenericTypeInterfaceItem("GT")], declaredItems=[self._constant])

	def test_UseAll(self) -> None:
		"""``package p is generic (package ip is new work.gp generic map (<>)); use ip.all; ...``"""
		useClause = _use("ip.all")
		package =   Package("p", genericItems=[_interfacePackage("ip", "work", "gp")], declaredItems=[useClause])
		_design(self._genericPackage, package)

		self.assertTupleEqual((self._constant, ), package._namespace.Lookup("k").Declarations)

	def test_UseItem(self) -> None:
		"""``use ip.K;``: the prefix of the two-part name denotes the interface package, not a library (12.4)."""
		useClause = _use("ip.K")
		package =   Package("p", genericItems=[_interfacePackage("ip", "work", "gp")], declaredItems=[useClause])
		_design(self._genericPackage, package)

		self.assertTupleEqual((self._constant, ), package._namespace.Lookup("k").Declarations)
		self.assertFalse(package._namespace.Lookup("gt").IsVisible)

	def test_Symbol(self) -> None:
		"""The use clause's symbol references the interface package, which denotes the instance."""
		interfacePackage = _interfacePackage("ip", "work", "gp")
		useClause =        _use("ip.all")
		_design(self._genericPackage, Package("p", genericItems=[interfacePackage], declaredItems=[useClause]))

		self.assertIs(interfacePackage, useClause.Symbols[0].Reference)

	def test_Type(self) -> None:
		"""As in ``float_generic_pkg``: ``use fixed_pkg.all;`` makes ``ufixed`` of ``ieee.fixed_generic_pkg`` visible."""
		constant = _constant("C", "ufixed")
		package =  Package(
			"p",
			[_libraryClause("ieee")],
			genericItems=[_interfacePackage("fixed_pkg", "IEEE", "fixed_generic_pkg")],
			declaredItems=[_use("fixed_pkg.all"), constant]
		)
		with WarningCollector() as collector:
			design = _design(package, analyze=False)
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		self.assertIs(design.Libraries["ieee"].Packages["fixed_generic_pkg"].Subtypes["ufixed"], constant.Subtype.Reference)

	def test_NotLinked(self) -> None:
		"""An interface package without package reference (pyGHDL doesn't read it yet) is reported by the use clause."""
		package = Package("p", genericItems=[GenericPackageInterfaceItem("ip")], declaredItems=[_use("ip.all")])
		with WarningCollector() as collector:
			_design(package, analyze=False).Analyze()

		warnings = [warning for warning in collector.Warnings if isinstance(warning, UnresolvedNameWarning)]
		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Interface package 'ip' of use clause 'ip.all' isn't linked to an uninstantiated package.",
			str(warnings[0])
		)
