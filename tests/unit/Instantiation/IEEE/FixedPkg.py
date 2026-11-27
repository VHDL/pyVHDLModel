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
"""Tests for pyVHDLModel.IEEE.NumericBitUnsigned."""
from pyTooling.Testing         import Testcase
"""Tests for pyVHDLModel.IEEE.FixedPkg."""
from pyTooling.Testing         import Testcase
from pyTooling.Warning         import WarningCollector

from pyVHDLModel               import Design, VHDLVersion
from pyVHDLModel.Name          import SimpleName
from pyVHDLModel.Symbol        import LibraryReferenceSymbol, IndexedObjectOrFunctionCallSymbol, \
                                      SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression    import IntegerLiteral
from pyVHDLModel.DesignUnit    import LibraryClause, Package
from pyVHDLModel.Instantiation import PackageInstantiation
from pyVHDLModel.IEEE          import Fixed_Pkg

from tests.unit.Visibility     import _constant, _design, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class FixedPkgs(Testcase):
	"""Package instantiation ``ieee.fixed_pkg`` (IEEE Std 1076-2008, 16.10)."""

	def test_Instantiation(self) -> None:
		"""``package fixed_pkg is new IEEE.fixed_generic_pkg generic map (...)`` with ``library IEEE;``."""
		fixedPkg = Fixed_Pkg()

		self.assertIsInstance(fixedPkg, PackageInstantiation)
		self.assertEqual("fixed_pkg", fixedPkg.NormalizedIdentifier)
		self.assertEqual("IEEE.fixed_generic_pkg", str(fixedPkg.PackageReference.Name))
		self.assertIs(fixedPkg, fixedPkg.PackageReference.Parent)
		self.assertIs(VHDLVersion.VHDL2008, fixedPkg.VHDLVersion)
		self.assertIsInstance(fixedPkg.ContextItems[0], LibraryClause)
		self.assertEqual(0, len(fixedPkg.DeclaredItems))

	def test_GenericMap(self) -> None:
		"""The four associations: two literals of ``fixed_float_types``, ``3`` and ``false``."""
		associations = Fixed_Pkg().GenericAssociationItems

		self.assertListEqual(
			["fixed_round_style", "fixed_overflow_style", "fixed_guard_bits", "no_warning"],
			[association.Formal.Identifier for association in associations]
		)
		self.assertIsInstance(associations[0].Actual, IndexedObjectOrFunctionCallSymbol)
		self.assertEqual("IEEE.fixed_float_types.fixed_round", str(associations[0].Actual.Name))
		self.assertEqual("IEEE.fixed_float_types.fixed_saturate", str(associations[1].Actual.Name))
		self.assertIsInstance(associations[2].Actual, IntegerLiteral)
		self.assertEqual(3, associations[2].Actual.Value)
		self.assertIsInstance(associations[3].Actual, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("false", associations[3].Actual.Name.Identifier)

	def test_Analyze(self) -> None:
		"""The analysis links the instantiation to ``ieee.fixed_generic_pkg``, whose declarations it provides."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		ieee =            design.Libraries["ieee"]
		fixedPkg =        ieee.Packages["fixed_pkg"]
		fixedGenericPkg = ieee.Packages["fixed_generic_pkg"]
		self.assertIs(fixedGenericPkg, fixedPkg.PackageReference.Reference)
		self.assertListEqual(list(fixedGenericPkg.IterateDeclarations()), list(fixedPkg.IterateDeclarations()))

	def test_UseClause(self) -> None:
		"""``use ieee.fixed_pkg.all;`` makes ``ufixed`` and ``to_ufixed`` visible."""
		constant = _constant("C", "ufixed")
		package =  Package(
			"p",
			contextItems=[LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))]), _use("ieee.fixed_pkg.all")],
			declaredItems=[constant]
		)
		with WarningCollector() as collector:
			design = _design(package, analyze=False)
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		fixedGenericPkg = design.Libraries["ieee"].Packages["fixed_generic_pkg"]
		self.assertIs(fixedGenericPkg.Subtypes["ufixed"], constant.Subtype.Reference)
		self.assertIn(fixedGenericPkg.Functions["to_ufixed"][0], package._namespace.Lookup("to_ufixed").Declarations)
