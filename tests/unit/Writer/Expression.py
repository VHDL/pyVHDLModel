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
Tests for writing expressions with pyVHDLModel.Formatting.VHDL.

Operator precedence and associativity follow IEEE Std 1076-2008, clause 9.1/9.2; :mod:`tests.unit.Writer.Oracle` checks
the written text with GHDL.
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Direction, SimpleRange, RangeFromName
from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, \
                                        PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral, \
                                        StringLiteral, BinaryBitStringLiteral, OctalBitStringLiteral, \
                                        DecimalBitStringLiteral, HexadecimalBitStringLiteral, NegationExpression, \
                                        IdentityExpression, InverseExpression, AbsoluteExpression, UnaryAndExpression, \
                                        UnaryNandExpression, UnaryOrExpression, UnaryNorExpression, \
                                        UnaryXorExpression, UnaryXnorExpression, TypeConversion, SubExpression, \
                                        AscendingRangeExpression, DescendingRangeExpression, AdditionExpression, \
                                        SubtractionExpression, ConcatenationExpression, MultiplyExpression, \
                                        DivisionExpression, RemainderExpression, ModuloExpression, \
                                        ExponentiationExpression, AndExpression, NandExpression, OrExpression, \
                                        NorExpression, XorExpression, XnorExpression, EqualExpression, \
                                        UnequalExpression, GreaterThanExpression, GreaterEqualExpression, \
                                        LessThanExpression, LessEqualExpression, MatchingEqualExpression, \
                                        MatchingUnequalExpression, MatchingGreaterThanExpression, \
                                        MatchingGreaterEqualExpression, MatchingLessThanExpression, \
                                        MatchingLessEqualExpression, ShiftRightLogicExpression, \
                                        ShiftLeftLogicExpression, ShiftRightArithmeticExpression, \
                                        ShiftLeftArithmeticExpression, RotateRightExpression, RotateLeftExpression, \
                                        QualifiedExpression, WhenElseExpression, SubtypeAllocation, \
                                        QualifiedExpressionAllocation, SimpleAggregateElement, \
                                        IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement, \
                                        OthersAggregateElement, Aggregate, CharacterEnumerationLiteral
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, AttributeName
from pyVHDLModel.Symbol          import RangeAttributeSymbol, RecordElementSymbol, SimpleSubtypeSymbol

from tests.unit.Writer           import _object


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

	def test_CharacterEnumeration(self) -> None:
		self.assertEqual("'0'", VHDLWriter().Format(CharacterEnumerationLiteral("0")))
		self.assertEqual("'''", VHDLWriter().Format(CharacterEnumerationLiteral("'")))


class UnaryExpressions(Testcase):
	def test_Sign(self) -> None:
		self.assertEqual("-a", VHDLWriter().Format(NegationExpression(_object("a"))))
		self.assertEqual("+a", VHDLWriter().Format(IdentityExpression(_object("a"))))

	def test_Miscellaneous(self) -> None:
		self.assertEqual("not a", VHDLWriter().Format(InverseExpression(_object("a"))))
		self.assertEqual("abs a", VHDLWriter().Format(AbsoluteExpression(_object("a"))))

	def test_Reduction(self) -> None:
		self.assertEqual("and v", VHDLWriter().Format(UnaryAndExpression(_object("v"))))
		self.assertEqual("nand v", VHDLWriter().Format(UnaryNandExpression(_object("v"))))
		self.assertEqual("or v", VHDLWriter().Format(UnaryOrExpression(_object("v"))))
		self.assertEqual("nor v", VHDLWriter().Format(UnaryNorExpression(_object("v"))))
		self.assertEqual("xor v", VHDLWriter().Format(UnaryXorExpression(_object("v"))))
		self.assertEqual("xnor v", VHDLWriter().Format(UnaryXnorExpression(_object("v"))))

	def test_Sign_Nested(self) -> None:
		self.assertEqual("-(-a)", VHDLWriter().Format(NegationExpression(NegationExpression(_object("a")))))

	def test_Sign_Term(self) -> None:
		"""A sign applies to a whole term: ``-a * b`` is ``-(a * b)``."""
		expression = NegationExpression(MultiplyExpression(_object("a"), _object("b")))

		self.assertEqual("-a * b", VHDLWriter().Format(expression))

	def test_Sign_Sum(self) -> None:
		expression = NegationExpression(AdditionExpression(_object("a"), _object("b")))

		self.assertEqual("-(a + b)", VHDLWriter().Format(expression))

	def test_Inverse_Binary(self) -> None:
		expression = InverseExpression(AndExpression(_object("a"), _object("b")))

		self.assertEqual("not (a and b)", VHDLWriter().Format(expression))

	def test_Inverse_Nested(self) -> None:
		self.assertEqual("not (not a)", VHDLWriter().Format(InverseExpression(InverseExpression(_object("a")))))

	def test_Absolute_Sign(self) -> None:
		self.assertEqual("abs (-a)", VHDLWriter().Format(AbsoluteExpression(NegationExpression(_object("a")))))


class BinaryExpressions(Testcase):
	def test_Logical(self) -> None:
		self.assertEqual("a and b", VHDLWriter().Format(AndExpression(_object("a"), _object("b"))))
		self.assertEqual("a nand b", VHDLWriter().Format(NandExpression(_object("a"), _object("b"))))
		self.assertEqual("a or b", VHDLWriter().Format(OrExpression(_object("a"), _object("b"))))
		self.assertEqual("a nor b", VHDLWriter().Format(NorExpression(_object("a"), _object("b"))))
		self.assertEqual("a xor b", VHDLWriter().Format(XorExpression(_object("a"), _object("b"))))
		self.assertEqual("a xnor b", VHDLWriter().Format(XnorExpression(_object("a"), _object("b"))))

	def test_Relational(self) -> None:
		self.assertEqual("a = b", VHDLWriter().Format(EqualExpression(_object("a"), _object("b"))))
		self.assertEqual("a /= b", VHDLWriter().Format(UnequalExpression(_object("a"), _object("b"))))
		self.assertEqual("a < b", VHDLWriter().Format(LessThanExpression(_object("a"), _object("b"))))
		self.assertEqual("a <= b", VHDLWriter().Format(LessEqualExpression(_object("a"), _object("b"))))
		self.assertEqual("a > b", VHDLWriter().Format(GreaterThanExpression(_object("a"), _object("b"))))
		self.assertEqual("a >= b", VHDLWriter().Format(GreaterEqualExpression(_object("a"), _object("b"))))

	def test_MatchingRelational(self) -> None:
		self.assertEqual("a ?= b", VHDLWriter().Format(MatchingEqualExpression(_object("a"), _object("b"))))
		self.assertEqual("a ?/= b", VHDLWriter().Format(MatchingUnequalExpression(_object("a"), _object("b"))))
		self.assertEqual("a ?< b", VHDLWriter().Format(MatchingLessThanExpression(_object("a"), _object("b"))))
		self.assertEqual("a ?<= b", VHDLWriter().Format(MatchingLessEqualExpression(_object("a"), _object("b"))))
		self.assertEqual("a ?> b", VHDLWriter().Format(MatchingGreaterThanExpression(_object("a"), _object("b"))))
		self.assertEqual("a ?>= b", VHDLWriter().Format(MatchingGreaterEqualExpression(_object("a"), _object("b"))))

	def test_Shift(self) -> None:
		self.assertEqual("a sll b", VHDLWriter().Format(ShiftLeftLogicExpression(_object("a"), _object("b"))))
		self.assertEqual("a srl b", VHDLWriter().Format(ShiftRightLogicExpression(_object("a"), _object("b"))))
		self.assertEqual("a sla b", VHDLWriter().Format(ShiftLeftArithmeticExpression(_object("a"), _object("b"))))
		self.assertEqual("a sra b", VHDLWriter().Format(ShiftRightArithmeticExpression(_object("a"), _object("b"))))
		self.assertEqual("a rol b", VHDLWriter().Format(RotateLeftExpression(_object("a"), _object("b"))))
		self.assertEqual("a ror b", VHDLWriter().Format(RotateRightExpression(_object("a"), _object("b"))))

	def test_Adding(self) -> None:
		self.assertEqual("a + b", VHDLWriter().Format(AdditionExpression(_object("a"), _object("b"))))
		self.assertEqual("a - b", VHDLWriter().Format(SubtractionExpression(_object("a"), _object("b"))))
		self.assertEqual("a & b", VHDLWriter().Format(ConcatenationExpression(_object("a"), _object("b"))))

	def test_Multiplying(self) -> None:
		self.assertEqual("a * b", VHDLWriter().Format(MultiplyExpression(_object("a"), _object("b"))))
		self.assertEqual("a / b", VHDLWriter().Format(DivisionExpression(_object("a"), _object("b"))))
		self.assertEqual("a mod b", VHDLWriter().Format(ModuloExpression(_object("a"), _object("b"))))
		self.assertEqual("a rem b", VHDLWriter().Format(RemainderExpression(_object("a"), _object("b"))))
		self.assertEqual("a ** b", VHDLWriter().Format(ExponentiationExpression(_object("a"), _object("b"))))


class Precedence(Testcase):
	def test_SumTimesFactor(self) -> None:
		expression = MultiplyExpression(AdditionExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("(a + b) * c", VHDLWriter().Format(expression))

	def test_SumOfProduct(self) -> None:
		expression = AdditionExpression(_object("a"), MultiplyExpression(_object("b"), _object("c")))

		self.assertEqual("a + b * c", VHDLWriter().Format(expression))

	def test_Subtraction_Left(self) -> None:
		expression = SubtractionExpression(SubtractionExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("a - b - c", VHDLWriter().Format(expression))

	def test_Subtraction_Right(self) -> None:
		expression = SubtractionExpression(_object("a"), SubtractionExpression(_object("b"), _object("c")))

		self.assertEqual("a - (b - c)", VHDLWriter().Format(expression))

	def test_Adding_Mixed(self) -> None:
		expression = AdditionExpression(ConcatenationExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("a & b + c", VHDLWriter().Format(expression))

	def test_Division_Right(self) -> None:
		expression = DivisionExpression(_object("a"), MultiplyExpression(_object("b"), _object("c")))

		self.assertEqual("a / (b * c)", VHDLWriter().Format(expression))

	def test_Exponentiation_Right(self) -> None:
		"""``a ** b ** c`` is illegal: both operands of ``**`` are primaries."""
		expression = ExponentiationExpression(_object("a"), ExponentiationExpression(_object("b"), _object("c")))

		self.assertEqual("a ** (b ** c)", VHDLWriter().Format(expression))

	def test_Exponentiation_Left(self) -> None:
		expression = ExponentiationExpression(ExponentiationExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("(a ** b) ** c", VHDLWriter().Format(expression))

	def test_Logical_Chain(self) -> None:
		expression = AndExpression(AndExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("a and b and c", VHDLWriter().Format(expression))

	def test_Logical_ChainRight(self) -> None:
		expression = OrExpression(_object("a"), OrExpression(_object("b"), _object("c")))

		self.assertEqual("a or (b or c)", VHDLWriter().Format(expression))

	def test_Logical_Mixed(self) -> None:
		"""Different logical operators can't be mixed without parentheses."""
		expression = OrExpression(AndExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("(a and b) or c", VHDLWriter().Format(expression))

	def test_Logical_Nand(self) -> None:
		"""``nand`` and ``nor`` are not associative: no chain."""
		expression = NandExpression(NandExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("(a nand b) nand c", VHDLWriter().Format(expression))

	def test_Relational_Logical(self) -> None:
		expression = AndExpression(
			EqualExpression(_object("a"), _object("b")),
			UnequalExpression(_object("c"), _object("d"))
		)

		self.assertEqual("a = b and c /= d", VHDLWriter().Format(expression))

	def test_Relational_Nested(self) -> None:
		expression = EqualExpression(EqualExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("(a = b) = c", VHDLWriter().Format(expression))

	def test_Shift_Adding(self) -> None:
		expression = ShiftLeftLogicExpression(AdditionExpression(_object("a"), _object("b")), IntegerLiteral(2))

		self.assertEqual("a + b sll 2", VHDLWriter().Format(expression))

	def test_Shift_Nested(self) -> None:
		expression = ShiftRightLogicExpression(ShiftLeftLogicExpression(_object("v"), IntegerLiteral(1)), IntegerLiteral(1))

		self.assertEqual("(v sll 1) srl 1", VHDLWriter().Format(expression))

	def test_Sign_Left(self) -> None:
		expression = AdditionExpression(NegationExpression(_object("a")), _object("b"))

		self.assertEqual("-a + b", VHDLWriter().Format(expression))

	def test_Sign_Right(self) -> None:
		"""A sign can only start a simple expression: ``a + -b`` is illegal."""
		expression = AdditionExpression(_object("a"), NegationExpression(_object("b")))

		self.assertEqual("a + (-b)", VHDLWriter().Format(expression))

	def test_Sign_Factor(self) -> None:
		expression = MultiplyExpression(NegationExpression(_object("a")), _object("b"))

		self.assertEqual("(-a) * b", VHDLWriter().Format(expression))

	def test_NegativeLiteral(self) -> None:
		"""A negative number is written with a sign, so it binds like a sign."""
		self.assertEqual("a - (-1)", VHDLWriter().Format(SubtractionExpression(_object("a"), IntegerLiteral(-1))))
		self.assertEqual("-1 + a", VHDLWriter().Format(AdditionExpression(IntegerLiteral(-1), _object("a"))))
		self.assertEqual("a * (-0.5)", VHDLWriter().Format(MultiplyExpression(_object("a"), FloatingPointLiteral(-0.5))))

	def test_SubExpression(self) -> None:
		"""Parentheses from the source are kept, even if not needed."""
		expression = AdditionExpression(_object("a"), SubExpression(MultiplyExpression(_object("b"), _object("c"))))

		self.assertEqual("a + (b * c)", VHDLWriter().Format(expression))

	def test_SubExpression_Needed(self) -> None:
		"""Source parentheses are not doubled."""
		expression = MultiplyExpression(SubExpression(AdditionExpression(_object("a"), _object("b"))), _object("c"))

		self.assertEqual("(a + b) * c", VHDLWriter().Format(expression))


class Ranges(Testcase):
	def test_Ascending(self) -> None:
		self.assertEqual("0 to 7", VHDLWriter().Format(AscendingRangeExpression(IntegerLiteral(0), IntegerLiteral(7))))

	def test_Descending(self) -> None:
		expression = DescendingRangeExpression(
			SubtractionExpression(_object("BITS"), IntegerLiteral(1)),
			IntegerLiteral(0)
		)

		self.assertEqual("BITS - 1 downto 0", VHDLWriter().Format(expression))

	def test_Descending_Shift(self) -> None:
		"""Range bounds are simple expressions."""
		expression = DescendingRangeExpression(ShiftLeftLogicExpression(_object("a"), _object("b")), IntegerLiteral(0))

		self.assertEqual("(a sll b) downto 0", VHDLWriter().Format(expression))

	def test_SimpleRange(self) -> None:
		rng = SimpleRange(IntegerLiteral(7), NegationExpression(IntegerLiteral(1)), Direction.DownTo)

		self.assertEqual("7 downto -1", VHDLWriter().Format(rng))

	def test_RangeFromName(self) -> None:
		rng = RangeFromName(RangeAttributeSymbol(AttributeName("range", SimpleName("v"))))

		self.assertEqual("v'range", VHDLWriter().Format(rng))


class Aggregates(Testcase):
	def test_Positional(self) -> None:
		aggregate = Aggregate([
			SimpleAggregateElement(CharacterLiteral("1")),
			SimpleAggregateElement(CharacterLiteral("0"))
		])

		self.assertEqual("('1', '0')", VHDLWriter().Format(aggregate))

	def test_Indexed(self) -> None:
		aggregate = Aggregate([
			IndexedAggregateElement(IntegerLiteral(0), CharacterLiteral("1")),
			OthersAggregateElement(CharacterLiteral("0"))
		])

		self.assertEqual("(0 => '1', others => '0')", VHDLWriter().Format(aggregate))

	def test_Indexed_Expression(self) -> None:
		aggregate = Aggregate([
			IndexedAggregateElement(AdditionExpression(_object("c"), IntegerLiteral(1)), CharacterLiteral("1")),
			OthersAggregateElement(CharacterLiteral("0"))
		])

		self.assertEqual("(c + 1 => '1', others => '0')", VHDLWriter().Format(aggregate))

	def test_Indexed_Shift(self) -> None:
		"""A choice is a simple expression."""
		aggregate = Aggregate([
			IndexedAggregateElement(ShiftLeftLogicExpression(_object("a"), _object("b")), CharacterLiteral("1")),
			OthersAggregateElement(CharacterLiteral("0"))
		])

		self.assertEqual("((a sll b) => '1', others => '0')", VHDLWriter().Format(aggregate))

	def test_Ranged(self) -> None:
		aggregate = Aggregate([
			RangedAggregateElement(AscendingRangeExpression(IntegerLiteral(1), IntegerLiteral(3)), CharacterLiteral("0")),
			OthersAggregateElement(CharacterLiteral("1"))
		])

		self.assertEqual("(1 to 3 => '0', others => '1')", VHDLWriter().Format(aggregate))

	def test_Named(self) -> None:
		aggregate = Aggregate([
			NamedAggregateElement(RecordElementSymbol(SimpleName("valid")), CharacterLiteral("1")),
			NamedAggregateElement(RecordElementSymbol(SimpleName("data")), HexadecimalBitStringLiteral("00"))
		])

		self.assertEqual("(valid => '1', data => x\"00\")", VHDLWriter().Format(aggregate))

	def test_Others(self) -> None:
		aggregate = Aggregate([OthersAggregateElement(CharacterLiteral("0"))])

		self.assertEqual("(others => '0')", VHDLWriter().Format(aggregate))

	def test_SinglePositional(self) -> None:
		"""``(x)`` is a parenthesized expression, not an aggregate."""
		aggregate = Aggregate([SimpleAggregateElement(CharacterLiteral("0"))])

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(aggregate)

		self.assertEqual("Aggregate with a single positional element has no VHDL notation.", str(context.exception))
		self.assertEqual(["Use a named element, e.g. 'others => value'."], context.exception.__notes__)

	def test_Empty(self) -> None:
		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(Aggregate([]))

		self.assertEqual("Aggregate has no elements.", str(context.exception))


class QualifiedExpressions(Testcase):
	def test_Operand(self) -> None:
		expression = QualifiedExpression(SimpleSubtypeSymbol(SimpleName("integer")), IntegerLiteral(5))

		self.assertEqual("integer'(5)", VHDLWriter().Format(expression))

	def test_Aggregate(self) -> None:
		expression = QualifiedExpression(
			SimpleSubtypeSymbol(SimpleName("byte")),
			Aggregate([OthersAggregateElement(CharacterLiteral("0"))])
		)

		self.assertEqual("byte'(others => '0')", VHDLWriter().Format(expression))

	def test_SubExpression(self) -> None:
		expression = QualifiedExpression(
			SimpleSubtypeSymbol(SimpleName("integer")),
			SubExpression(AdditionExpression(_object("a"), _object("b")))
		)

		self.assertEqual("integer'(a + b)", VHDLWriter().Format(expression))


class TypeConversions(Testcase):
	def test_Conversion(self) -> None:
		conversion = TypeConversion(SimpleSubtypeSymbol(SimpleName("integer")), _object("r"))

		self.assertEqual("integer(r)", VHDLWriter().Format(conversion))

	def test_Conversion_Operand(self) -> None:
		conversion = TypeConversion(
			SimpleSubtypeSymbol(SimpleName("integer")),
			AdditionExpression(_object("r"), FloatingPointLiteral(0.5))
		)

		self.assertEqual("integer(r + 0.5)", VHDLWriter().Format(conversion))

	def test_Conversion_Operator(self) -> None:
		conversion = TypeConversion(SimpleSubtypeSymbol(SimpleName("integer")), _object("r"))

		self.assertEqual("-integer(r)", VHDLWriter().Format(NegationExpression(conversion)))


class Allocations(Testcase):
	def test_Subtype(self) -> None:
		allocation = SubtypeAllocation(SimpleSubtypeSymbol(SimpleName("node")))

		self.assertEqual("new node", VHDLWriter().Format(allocation))

	def test_QualifiedExpression(self) -> None:
		allocation = QualifiedExpressionAllocation(
			QualifiedExpression(SimpleSubtypeSymbol(SimpleName("integer")), IntegerLiteral(5))
		)

		self.assertEqual("new integer'(5)", VHDLWriter().Format(allocation))


class ConditionalExpressions(Testcase):
	def test_WhenElse(self) -> None:
		expression = WhenElseExpression(_object("a"), _object("c"), _object("b"))

		self.assertEqual("a when c else b", VHDLWriter().Format(expression))

	def test_WhenElse_Chain(self) -> None:
		expression = WhenElseExpression(
			_object("a"),
			_object("c"),
			WhenElseExpression(_object("b"), _object("d"), _object("e"))
		)

		self.assertEqual("a when c else b when d else e", VHDLWriter().Format(expression))

	def test_WhenElse_Condition(self) -> None:
		expression = WhenElseExpression(_object("a"), OrExpression(_object("c"), _object("d")), _object("b"))

		self.assertEqual("a when c or d else b", VHDLWriter().Format(expression))

	def test_WhenElse_Operand(self) -> None:
		expression = AdditionExpression(WhenElseExpression(_object("a"), _object("c"), _object("b")), IntegerLiteral(1))

		self.assertEqual("(a when c else b) + 1", VHDLWriter().Format(expression))
