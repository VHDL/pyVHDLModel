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
"""Tests for pyVHDLModel.IEEE.FloatPkg."""
from pyTooling.Testing         import Testcase
from pyTooling.Warning         import WarningCollector

from pyVHDLModel               import Design, VHDLVersion
from pyVHDLModel.Name          import SimpleName
from pyVHDLModel.Symbol        import LibraryReferenceSymbol, IndexedObjectOrFunctionCallSymbol, \
                                      SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression    import IntegerLiteral
from pyVHDLModel.DesignUnit    import LibraryClause, Package
from pyVHDLModel.Instantiation import PackageInstantiation
from pyVHDLModel.IEEE          import Float_Pkg

from tests.unit.Visibility     import _constant, _design, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class FloatPkgs(Testcase):
	"""Package instantiation ``ieee.float_pkg`` (IEEE Std 1076-2008, 16.11)."""

	def test_Instantiation(self) -> None:
		"""``package float_pkg is new IEEE.float_generic_pkg generic map (...)`` with ``library ieee;``."""
		floatPkg = Float_Pkg()

		self.assertIsInstance(floatPkg, PackageInstantiation)
		self.assertEqual("float_pkg", floatPkg.NormalizedIdentifier)
		self.assertEqual("IEEE.float_generic_pkg", str(floatPkg.PackageReference.Name))
		self.assertIs(floatPkg, floatPkg.PackageReference.Parent)
		self.assertIs(VHDLVersion.VHDL2008, floatPkg.VHDLVersion)
		self.assertIsInstance(floatPkg.ContextItems[0], LibraryClause)
		self.assertEqual(0, len(floatPkg.DeclaredItems))

	def test_GenericMap(self) -> None:
		"""The eight associations, the last one the package ``IEEE.fixed_pkg`` for the package generic ``fixed_pkg``."""
		associations = Float_Pkg().GenericAssociationItems

		self.assertListEqual(
			[
				"float_exponent_width", "float_fraction_width", "float_round_style", "float_denormalize",
				"float_check_error", "float_guard_bits", "no_warning", "fixed_pkg"
			],
			[association.Formal.Identifier for association in associations]
		)
		self.assertIsInstance(associations[0].Actual, IntegerLiteral)
		self.assertEqual(8, associations[0].Actual.Value)
		self.assertEqual(23, associations[1].Actual.Value)
		self.assertIsInstance(associations[2].Actual, IndexedObjectOrFunctionCallSymbol)
		self.assertEqual("IEEE.fixed_float_types.round_nearest", str(associations[2].Actual.Name))
		self.assertIsInstance(associations[3].Actual, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("true", associations[3].Actual.Name.Identifier)
		self.assertEqual(3, associations[5].Actual.Value)
		self.assertEqual("false", associations[6].Actual.Name.Identifier)
		self.assertEqual("IEEE.fixed_pkg", str(associations[7].Actual.Name))

	def test_Analyze(self) -> None:
		"""The analysis links the instantiation to ``ieee.float_generic_pkg``, whose declarations it provides."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		ieee =            design.Libraries["ieee"]
		floatPkg =        ieee.Packages["float_pkg"]
		floatGenericPkg = ieee.Packages["float_generic_pkg"]
		self.assertIs(floatGenericPkg, floatPkg.PackageReference.Reference)
		self.assertListEqual(list(floatGenericPkg.IterateDeclarations()), list(floatPkg.IterateDeclarations()))

	def test_UseClause(self) -> None:
		"""``use ieee.float_pkg.all;`` makes ``float32`` and ``to_float`` visible."""
		constant = _constant("C", "float32")
		package =  Package(
			"p",
			contextItems=[LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))]), _use("ieee.float_pkg.all")],
			declaredItems=[constant]
		)
		with WarningCollector() as collector:
			design = _design(package, analyze=False)
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		floatGenericPkg = design.Libraries["ieee"].Packages["float_generic_pkg"]
		self.assertIs(floatGenericPkg.Subtypes["float32"], constant.Subtype.Reference)
		self.assertIn(floatGenericPkg.Functions["to_float"][0], package._namespace.Lookup("to_float").Declarations)
