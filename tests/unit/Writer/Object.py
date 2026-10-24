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
"""Tests for writing subtype indications and object declarations with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Direction, SimpleRange
from pyVHDLModel.Expression      import IntegerLiteral, CharacterLiteral, AscendingRangeExpression, \
                                        DescendingRangeExpression, SubtractionExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Object          import Constant, DeferredConstant, Variable, SharedVariable, Signal, File
from pyVHDLModel.Symbol          import ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, \
                                        ConstrainedRecordSubtypeSymbol, RecordElementSymbol

from tests.unit                  import _subtypeSymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _downto(left: int, right: int) -> DescendingRangeExpression:
	"""Descending range of two integer literals."""
	return DescendingRangeExpression(IntegerLiteral(left), IntegerLiteral(right))


class SubtypeIndications(Testcase):
	def test_Scalar(self) -> None:
		symbol = ConstrainedScalarSubtypeSymbol(
			SimpleName("integer"),
			SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
		)

		self.assertEqual("integer range 0 to 7", VHDLWriter().Format(symbol))

	def test_Scalar_Expression(self) -> None:
		symbol = ConstrainedScalarSubtypeSymbol(
			SimpleName("natural"),
			AscendingRangeExpression(IntegerLiteral(0), SubtractionExpression(_object("BITS"), IntegerLiteral(1)))
		)

		self.assertEqual("natural range 0 to BITS - 1", VHDLWriter().Format(symbol))

	def test_Array(self) -> None:
		symbol = ConstrainedArraySubtypeSymbol(SimpleName("std_logic_vector"), [_downto(7, 0)])

		self.assertEqual("std_logic_vector(7 downto 0)", VHDLWriter().Format(symbol))

	def test_Array_Dimensions(self) -> None:
		symbol = ConstrainedArraySubtypeSymbol(SimpleName("matrix"), [_downto(3, 0), _subtypeSymbol("state")])

		self.assertEqual("matrix(3 downto 0, state)", VHDLWriter().Format(symbol))

	def test_Record(self) -> None:
		symbol = ConstrainedRecordSubtypeSymbol(SimpleName("frame"), {
			RecordElementSymbol(SimpleName("data")): _downto(7, 0),
			RecordElementSymbol(SimpleName("mask")): _downto(3, 0),
		})

		self.assertEqual("frame(data(7 downto 0), mask(3 downto 0))", VHDLWriter().Format(symbol))

	def test_UpperCase(self) -> None:
		symbol = ConstrainedScalarSubtypeSymbol(
			SimpleName("integer"),
			SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		)

		self.assertEqual("integer RANGE 7 DOWNTO 0", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(symbol))


class Objects(Testcase):
	def test_Constant(self) -> None:
		constant = Constant(["BITS"], _subtypeSymbol("positive"), IntegerLiteral(8))

		self.assertEqual("constant BITS : positive := 8;\n", VHDLWriter().Format(constant))

	def test_Constant_Identifiers(self) -> None:
		constant = Constant(["A", "B"], _subtypeSymbol("natural"), IntegerLiteral(0))

		self.assertEqual("constant A, B : natural := 0;\n", VHDLWriter().Format(constant))

	def test_DeferredConstant(self) -> None:
		constant = DeferredConstant(["BITS"], _subtypeSymbol("positive"))

		self.assertEqual("constant BITS : positive;\n", VHDLWriter().Format(constant))

	def test_Variable(self) -> None:
		variable = Variable(["count"], _subtypeSymbol("natural"), IntegerLiteral(0))

		self.assertEqual("variable count : natural := 0;\n", VHDLWriter().Format(variable))

	def test_Variable_WithoutDefault(self) -> None:
		variable = Variable(["count"], _subtypeSymbol("natural"))

		self.assertEqual("variable count : natural;\n", VHDLWriter().Format(variable))

	def test_SharedVariable(self) -> None:
		variable = SharedVariable(["counter"], _subtypeSymbol("counter_t"))

		self.assertEqual("shared variable counter : counter_t;\n", VHDLWriter().Format(variable))

	def test_Signal(self) -> None:
		signal = Signal(
			["a", "b"],
			ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [_downto(3, 0)]),
			_object("ZERO")
		)

		self.assertEqual("signal a, b : bit_vector(3 downto 0) := ZERO;\n", VHDLWriter().Format(signal))

	def test_Signal_WithoutDefault(self) -> None:
		signal = Signal(["clk"], _subtypeSymbol("bit"))

		self.assertEqual("signal clk : bit;\n", VHDLWriter().Format(signal))

	def test_File(self) -> None:
		file = File(["input"], _subtypeSymbol("text"))

		self.assertEqual("file input : text;\n", VHDLWriter().Format(file))

	def test_UpperCase(self) -> None:
		writer = VHDLWriter(VHDLStyle(KeywordCase.Upper))

		self.assertEqual(dedent("""\
			SIGNAL clk : bit := '0';
			SHARED VARIABLE counter : counter_t;
			"""),
			writer.Format(Signal(["clk"], _subtypeSymbol("bit"), CharacterLiteral("0"))) +
			writer.Format(SharedVariable(["counter"], _subtypeSymbol("counter_t")))
		)
