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
"""Tests for pyVHDLModel.IEEE.StdLogicArith."""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import Design, IEEEFlavor
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.Symbol     import ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Type       import ArrayType, Subtype
from pyVHDLModel.IEEE       import Std_Logic_Arith_Synopsys


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class StdLogicArithSynopsys(Testcase):
	"""Synopsys package ``ieee.std_logic_arith``."""

	def test_Declarations(self) -> None:
		"""The types ``unsigned`` and ``signed``, the subtype ``small_int``, 134 functions; the package is the parent."""
		stdLogicArith = Std_Logic_Arith_Synopsys()
		declarations =  stdLogicArith.DeclaredItems

		self.assertEqual("std_logic_arith", stdLogicArith.NormalizedIdentifier)
		self.assertIsInstance(declarations[0], ArrayType)
		self.assertIsInstance(declarations[1], ArrayType)
		self.assertIsInstance(declarations[2], Subtype)
		self.assertEqual(134, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(137, len(declarations))
		for declaration in declarations:
			self.assertIs(stdLogicArith, declaration.Parent)

	def test_Types(self) -> None:
		"""``type UNSIGNED is array (NATURAL range <>) of STD_LOGIC;`` and ``subtype SMALL_INT is INTEGER range 0 to 1;``"""
		stdLogicArith = Std_Logic_Arith_Synopsys()
		unsigned =      stdLogicArith.Types["unsigned"]
		smallInt =      stdLogicArith.Subtypes["small_int"]

		self.assertEqual("natural", unsigned.Dimensions[0].Name.Identifier)
		self.assertEqual("std_logic", unsigned.ElementType.Name.Identifier)
		self.assertIsInstance(smallInt.Type, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("integer", smallInt.Type.Name.Identifier)
		self.assertEqual(1, smallInt.Type.Constraint.RightBound.Value)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{
				"+": 28, "-": 26, "abs": 2, "*": 8, "<": 8, "<=": 8, ">": 8, ">=": 8, "=": 8, "/=": 8, "shl": 2, "shr": 2,
				"conv_integer": 4, "conv_unsigned": 4, "conv_signed": 4, "conv_std_logic_vector": 4, "ext": 1, "sxt": 1
			},
			{identifier: len(overloads) for identifier, overloads in Std_Logic_Arith_Synopsys().Functions.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, ``shl`` ... ``sxt`` aren't."""
		stdLogicArith = Std_Logic_Arith_Synopsys()

		for identifier in ("+", "abs", "*", "/="):
			for function in stdLogicArith.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("shl", "conv_integer", "conv_std_logic_vector", "ext"):
			for function in stdLogicArith.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_ResultTypes(self) -> None:
		"""``"+"(L: UNSIGNED; R: UNSIGNED)`` returns ``UNSIGNED``, the 13th overload ``STD_LOGIC_VECTOR``."""
		additions = Std_Logic_Arith_Synopsys().Functions["+"]

		self.assertListEqual(
			[["unsigned", "unsigned"], ["unsigned", "unsigned"]],
			[[item.Subtype.Name.Identifier for item in additions[index].ParameterItems] for index in (0, 12)]
		)
		self.assertEqual("unsigned", additions[0].ReturnType.Name.Identifier)
		self.assertEqual("std_logic_vector", additions[12].ReturnType.Name.Identifier)
		self.assertEqual("std_logic_vector", additions[27].ReturnType.Name.Identifier)

	def test_Unary(self) -> None:
		"""The unary ``"+"``, ``"-"``, ``"ABS"`` return ``UNSIGNED``/``SIGNED``, then ``STD_LOGIC_VECTOR``."""
		absolute = Std_Logic_Arith_Synopsys().Functions["abs"]

		self.assertListEqual(["signed", "std_logic_vector"], [function.ReturnType.Name.Identifier for function in absolute])
		self.assertEqual(1, len(absolute[0].ParameterItems))

	def test_Conversions(self) -> None:
		"""``CONV_INTEGER(ARG: STD_ULOGIC) return SMALL_INT``, ``CONV_UNSIGNED(ARG: INTEGER; SIZE: INTEGER)``."""
		stdLogicArith = Std_Logic_Arith_Synopsys()

		self.assertEqual("small_int", stdLogicArith.Functions["conv_integer"][3].ReturnType.Name.Identifier)
		self.assertListEqual(
			[("ARG", ), ("SIZE", )],
			[item.Identifiers for item in stdLogicArith.Functions["conv_unsigned"][0].ParameterItems]
		)

	def test_Analyze(self) -> None:
		"""With the Synopsys flavor, every type mark resolves, e.g. ``SMALL_INT``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.Synopsys)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		stdLogicArith = design.Libraries["ieee"].Packages["std_logic_arith"]
		self.assertIsInstance(stdLogicArith, Std_Logic_Arith_Synopsys)
		self.assertIs(stdLogicArith.Subtypes["small_int"], stdLogicArith.Functions["conv_integer"][3].ReturnType.Reference)
