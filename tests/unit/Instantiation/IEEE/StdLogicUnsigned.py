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
"""Tests for pyVHDLModel.IEEE.StdLogicUnsignedPkg."""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import Design, IEEEFlavor
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.IEEE       import Std_Logic_Unsigned


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class StdLogicUnsigneds(Testcase):
	"""Synopsys package ``ieee.std_logic_unsigned``."""

	def test_Declarations(self) -> None:
		"""33 functions with the package as parent."""
		stdLogicUnsigned = Std_Logic_Unsigned()
		declarations =     stdLogicUnsigned.DeclaredItems

		self.assertEqual(33, len(declarations))
		for declaration in declarations:
			self.assertIsInstance(declaration, Function)
			self.assertIs(stdLogicUnsigned, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{
				"+": 6, "-": 5, "*": 1, "<": 3, "<=": 3, ">": 3, ">=": 3, "=": 3, "/=": 3, "shl": 1, "shr": 1,
				"conv_integer": 1
			},
			{identifier: len(overloads) for identifier, overloads in Std_Logic_Unsigned().Functions.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, ``shl``, ``shr`` and ``conv_integer`` aren't."""
		stdLogicUnsigned = Std_Logic_Unsigned()

		for identifier in ("+", "*", "<", "/="):
			for function in stdLogicUnsigned.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("shl", "shr", "conv_integer"):
			for function in stdLogicUnsigned.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_Operands(self) -> None:
		"""``"+"(L: STD_LOGIC_VECTOR; R: STD_LOGIC_VECTOR)``: two interface items, as the package writes them."""
		additions = Std_Logic_Unsigned().Functions["+"]

		self.assertListEqual([("L", ), ("R", )], [item.Identifiers for item in additions[0].ParameterItems])
		self.assertListEqual(
			[["std_logic_vector", "std_logic_vector"], ["std_logic_vector", "integer"], ["integer", "std_logic_vector"],
			 ["std_logic_vector", "std_logic"], ["std_logic", "std_logic_vector"], ["std_logic_vector"]],
			[[item.Subtype.Name.Identifier for item in function.ParameterItems] for function in additions]
		)

	def test_Relational(self) -> None:
		"""``"<"(L: STD_LOGIC_VECTOR; R: INTEGER) return BOOLEAN``"""
		for function in Std_Logic_Unsigned().Functions["<"]:
			self.assertEqual("boolean", function.ReturnType.Name.Identifier)

	def test_ShlConvInteger(self) -> None:
		"""``SHL(ARG: STD_LOGIC_VECTOR; COUNT: STD_LOGIC_VECTOR)``; ``CONV_INTEGER`` returns ``INTEGER``."""
		stdLogicUnsigned = Std_Logic_Unsigned()
		shl =              stdLogicUnsigned.Functions["shl"][0]
		convInteger =      stdLogicUnsigned.Functions["conv_integer"][0]

		self.assertListEqual([("ARG", ), ("COUNT", )], [item.Identifiers for item in shl.ParameterItems])
		self.assertEqual("integer", convInteger.ReturnType.Name.Identifier)

	def test_Analyze(self) -> None:
		"""With the Synopsys flavor, every type mark resolves."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.Synopsys)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		stdLogicUnsigned = design.Libraries["ieee"].Packages["std_logic_unsigned"]
		stdLogic1164 =     design.Libraries["ieee"].Packages["std_logic_1164"]
		self.assertIs(stdLogic1164.Subtypes["std_logic_vector"], stdLogicUnsigned.Functions["+"][0].ReturnType.Reference)
