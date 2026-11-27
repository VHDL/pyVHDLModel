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
from pyTooling.Testing       import Testcase
"""Tests for pyVHDLModel.IEEE.FixedFloatTypes."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design
from pyVHDLModel.Type        import EnumeratedType
from pyVHDLModel.IEEE        import Fixed_Float_Types


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class FixedFloatTypes(Testcase):
	"""Package ``ieee.fixed_float_types`` (IEEE Std 1076-2008, 16.10 and 16.11)."""

	def test_Declarations(self) -> None:
		"""Three enumerated types in order, with the package as parent."""
		fixedFloatTypes = Fixed_Float_Types()
		declarations =    fixedFloatTypes.DeclaredItems

		self.assertListEqual(
			["fixed_round_style_type", "fixed_overflow_style_type", "round_type"],
			[declaration.Identifier for declaration in declarations]
		)
		for declaration in declarations:
			self.assertIsInstance(declaration, EnumeratedType)
			self.assertIs(fixedFloatTypes, declaration.Parent)
			self.assertIs(declaration, fixedFloatTypes.Types[declaration.NormalizedIdentifier])

	def test_Literals(self) -> None:
		"""``type round_type is (round_nearest, round_inf, round_neginf, round_zero);`` and the two fixed-point types."""
		types = Fixed_Float_Types().Types

		self.assertListEqual(
			["fixed_round", "fixed_truncate"],
			[literal.Value for literal in types["fixed_round_style_type"].Literals]
		)
		self.assertListEqual(
			["fixed_saturate", "fixed_wrap"],
			[literal.Value for literal in types["fixed_overflow_style_type"].Literals]
		)
		self.assertListEqual(
			["round_nearest", "round_inf", "round_neginf", "round_zero"],
			[literal.Value for literal in types["round_type"].Literals]
		)

	def test_Analyze(self) -> None:
		"""The types declare their implicit operations, e.g. ``"="`` of ``round_type``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		roundType = design.Libraries["ieee"].Packages["fixed_float_types"].Types["round_type"]
		self.assertIn("=", [operation.Identifier for operation in roundType.ImplicitOperations])
