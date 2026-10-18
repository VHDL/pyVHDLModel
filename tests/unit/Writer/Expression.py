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
"""Tests for writing literals with pyVHDLModel.Formatting.VHDL."""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import (
	NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral,
	PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BinaryBitStringLiteral, OctalBitStringLiteral,
	DecimalBitStringLiteral, HexadecimalBitStringLiteral
)
from pyVHDLModel.Formatting.VHDL import VHDLWriter


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class NumericLiterals(Testcase):
	def test_Integer(self) -> None:
		self.assertEqual("42", VHDLWriter().Format(IntegerLiteral(42)))

	def test_Real(self) -> None:
		self.assertEqual("3.5", VHDLWriter().Format(FloatingPointLiteral(3.5)))

	def test_Real_Exponent(self) -> None:
		"""A real literal needs a decimal point, also with an exponent."""
		self.assertEqual("1.0e-09", VHDLWriter().Format(FloatingPointLiteral(1e-9)))
		self.assertEqual("2.5e+20", VHDLWriter().Format(FloatingPointLiteral(2.5e20)))

	def test_Real_Integer(self) -> None:
		self.assertEqual("2.0", VHDLWriter().Format(FloatingPointLiteral(2)))

	def test_Real_Infinite(self) -> None:
		literal = FloatingPointLiteral(float("inf"))

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(literal)

		self.assertEqual("Floating-point value has no VHDL notation.", str(context.exception))
		self.assertEqual(["Got value 'inf'."], context.exception.__notes__)

	def test_PhysicalInteger(self) -> None:
		self.assertEqual("10 ns", VHDLWriter().Format(PhysicalIntegerLiteral(10, "ns")))

	def test_PhysicalFloating(self) -> None:
		self.assertEqual("1.5 ns", VHDLWriter().Format(PhysicalFloatingLiteral(1.5, "ns")))


class CharacterLiterals(Testcase):
	def test_Character(self) -> None:
		self.assertEqual("'a'", VHDLWriter().Format(CharacterLiteral("a")))

	def test_Apostrophe(self) -> None:
		self.assertEqual("'''", VHDLWriter().Format(CharacterLiteral("'")))

	def test_ControlCharacter(self) -> None:
		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(CharacterLiteral("\n"))

		self.assertEqual("Character literal is not a single graphic character.", str(context.exception))


class StringLiterals(Testcase):
	def test_String(self) -> None:
		self.assertEqual("\"hello\"", VHDLWriter().Format(StringLiteral("hello")))

	def test_String_Empty(self) -> None:
		self.assertEqual("\"\"", VHDLWriter().Format(StringLiteral("")))

	def test_QuotationMark(self) -> None:
		self.assertEqual("\"say \"\"hi\"\"\"", VHDLWriter().Format(StringLiteral("say \"hi\"")))

	def test_ControlCharacter(self) -> None:
		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(StringLiteral("a\tb"))

		self.assertEqual("String literal contains a non-graphic character.", str(context.exception))
		self.assertEqual(["Got value 'a\\tb'."], context.exception.__notes__)


class BitStringLiterals(Testcase):
	def test_Binary(self) -> None:
		self.assertEqual("b\"1010\"", VHDLWriter().Format(BinaryBitStringLiteral("1010")))

	def test_Octal_Signed(self) -> None:
		self.assertEqual("so\"7\"", VHDLWriter().Format(OctalBitStringLiteral("7", isSigned=True)))

	def test_Decimal(self) -> None:
		self.assertEqual("8d\"160\"", VHDLWriter().Format(DecimalBitStringLiteral("160", 8)))

	def test_Hexadecimal_Unsigned(self) -> None:
		self.assertEqual("8ux\"A0\"", VHDLWriter().Format(HexadecimalBitStringLiteral("A0", 8, False)))

	def test_Decimal_Signed(self) -> None:
		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(DecimalBitStringLiteral("160", isSigned=True))

		self.assertEqual("Decimal bit string literal can't be signed or unsigned.", str(context.exception))

	def test_QuotationMark(self) -> None:
		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(BinaryBitStringLiteral("1\"0"))

		self.assertEqual(
			"Bit string literal contains a quotation mark or a non-graphic character.",
			str(context.exception)
		)


class OtherLiterals(Testcase):
	def test_Null(self) -> None:
		self.assertEqual("null", VHDLWriter().Format(NullLiteral()))

	def test_Enumeration(self) -> None:
		self.assertEqual("Idle", VHDLWriter().Format(EnumerationLiteral("Idle")))
