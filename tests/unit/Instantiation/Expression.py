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
Tests for pyVHDLModel.Expression.

Most of this module is dozens of leaf subclasses that only fix a ``_FORMAT`` class variable
(``AdditionExpression``, ``EqualExpression``, ``RotateLeftExpression``, ...). Their shared
construction/parent-wiring behaviour is tested once via the immediate base class
(``UnaryExpression``/``BinaryExpression``), then every leaf subclass's ``_FORMAT`` is checked
table-driven in one ``str()``-formatting test rather than one hand-written test per class.
"""
from pickle import dumps, loads

from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Exception  import VHDLModelException, LiteralError
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Expression import OperatorPrecedence, BaseExpression, Literal, NullLiteral, EnumerationLiteral, \
                                   IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral, \
                                   PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BinaryBitStringLiteral, \
                                   OctalBitStringLiteral, DecimalBitStringLiteral, HexadecimalBitStringLiteral, \
                                   UnaryExpression, NegationExpression, IdentityExpression, InverseExpression, \
                                   UnaryAndExpression, UnaryNandExpression, UnaryOrExpression, UnaryNorExpression, \
                                   UnaryXorExpression, UnaryXnorExpression, AbsoluteExpression, TypeConversion, \
                                   SubExpression, BinaryExpression, AscendingRangeExpression, \
                                   DescendingRangeExpression, AdditionExpression, SubtractionExpression, \
                                   ConcatenationExpression, MultiplyExpression, DivisionExpression, \
                                   RemainderExpression, ModuloExpression, ExponentiationExpression, AndExpression, \
                                   NandExpression, OrExpression, NorExpression, XorExpression, XnorExpression, \
                                   EqualExpression, UnequalExpression, GreaterThanExpression, GreaterEqualExpression, \
                                   LessThanExpression, LessEqualExpression, MatchingEqualExpression, \
                                   MatchingUnequalExpression, MatchingGreaterThanExpression, \
                                   MatchingGreaterEqualExpression, MatchingLessThanExpression, \
                                   MatchingLessEqualExpression, ShiftRightLogicExpression, ShiftLeftLogicExpression, \
                                   ShiftRightArithmeticExpression, ShiftLeftArithmeticExpression, \
                                   RotateRightExpression, RotateLeftExpression, QualifiedExpression, \
                                   TernaryExpression, WhenElseExpression, FunctionCall, SubtypeAllocation, \
                                   QualifiedExpressionAllocation, AggregateElement, SimpleAggregateElement, \
                                   IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement, \
                                   OthersAggregateElement, Aggregate


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Literals(Testcase):
	"""
	``BaseExpression`` itself (``class BaseExpression(ModelEntity): pass``) is never instantiated directly here.

	This matches the same reasoning as ``Allocation``/``Type`` (see tests/unit/Type.py): it has no ``__init__`` override
	of its own (so there's no independent forwarding-bug risk to check, unlike e.g. the type classes), no VHDL construct
	is ever "just a BaseExpression", and its ``Parent``-wiring behaviour is already covered via plain ``ModelEntity`` in
	tests/unit/Base.py - every concrete literal/operator/etc. class tested below already exercises it transitively.
	"""


	def test_NullLiteral(self) -> None:
		self.assertEqual("null", str(NullLiteral()))

	def test_EnumerationLiteral(self) -> None:
		literal = EnumerationLiteral("'1'")

		self.assertEqual("'1'", literal.Value)
		self.assertEqual("'1'", str(literal))

	def test_IntegerLiteral(self) -> None:
		literal = IntegerLiteral(42)

		self.assertEqual(42, literal.Value)
		self.assertEqual("42", str(literal))

	def test_FloatingPointLiteral(self) -> None:
		literal = FloatingPointLiteral(4.2)

		self.assertEqual(4.2, literal.Value)
		self.assertEqual("4.2", str(literal))

	def test_CharacterLiteral(self) -> None:
		literal = CharacterLiteral("a")

		self.assertEqual("a", literal.Value)
		self.assertEqual("a", str(literal))

	def test_StringLiteral(self) -> None:
		literal = StringLiteral("hello")

		self.assertEqual("hello", literal.Value)
		self.assertEqual("\"hello\"", str(literal))


class CharacterLiterals(Testcase):
	def test_Apostrophe(self) -> None:
		literal = CharacterLiteral("'")

		self.assertEqual("'", literal.Value)
		self.assertEqual("'", str(literal))

	def test_Value_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			CharacterLiteral(None)

		self.assertEqual("Parameter 'value' is None.", str(context.exception))

	def test_Value_Integer(self) -> None:
		with self.assertRaises(TypeError) as context:
			CharacterLiteral(1)

		self.assertEqual("Parameter 'value' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Value_WithApostrophes(self) -> None:
		with self.assertRaises(ValueError) as context:
			CharacterLiteral("'a'")

		self.assertEqual("Parameter 'value' is not a single character.", str(context.exception))
		self.assertEqual(["Got value ''a''.", "Pass the character without apostrophes."], context.exception.__notes__)


class PhysicalLiterals(Testcase):
	"""``PhysicalLiteral`` itself is never instantiated directly - its own ``_value`` is only declared
	by ``PhysicalIntegerLiteral``/``PhysicalFloatingLiteral``, so it's exercised only through those two
	concrete subclasses."""

	def test_PhysicalIntegerLiteral(self) -> None:
		literal = PhysicalIntegerLiteral(5, "ns")

		self.assertEqual(5, literal.Value)
		self.assertEqual("ns", literal.UnitName)
		self.assertEqual("5 ns", str(literal))

	def test_PhysicalFloatingLiteral(self) -> None:
		literal = PhysicalFloatingLiteral(2.5, "ns")

		self.assertEqual(2.5, literal.Value)
		self.assertEqual("ns", literal.UnitName)
		self.assertEqual("2.5 ns", str(literal))


class BitStringLiterals(Testcase):
	def test_Value_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			BinaryBitStringLiteral(None)

		self.assertEqual("Parameter 'value' is None.", str(context.exception))

	def test_Value_Integer(self) -> None:
		with self.assertRaises(TypeError) as context:
			BinaryBitStringLiteral(1)

		self.assertEqual("Parameter 'value' is not of type 'str'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Length_String(self) -> None:
		with self.assertRaises(TypeError) as context:
			BinaryBitStringLiteral("1", "8")

		self.assertEqual("Parameter 'length' is not of type 'int'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Length_Negative(self) -> None:
		with self.assertRaises(ValueError) as context:
			BinaryBitStringLiteral("1", -1)

		self.assertEqual("Parameter 'length' is negative.", str(context.exception))
		self.assertEqual(["Got value '-1'."], context.exception.__notes__)

	def test_IsSigned_Integer(self) -> None:
		with self.assertRaises(TypeError) as context:
			BinaryBitStringLiteral("1", None, 1)

		self.assertEqual("Parameter 'isSigned' is not of type 'bool'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Underscore_Leading(self) -> None:
		literal = BinaryBitStringLiteral("_1")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal has a leading, trailing or double underscore.", str(context.exception))
		self.assertEqual(["Got value 'b\"_1\"'."], context.exception.__notes__)

	def test_Underscore_Trailing(self) -> None:
		literal = HexadecimalBitStringLiteral("1_")

		with self.assertRaises(LiteralError) as context:
			_ = literal.Bits

		self.assertEqual("Bit string literal has a leading, trailing or double underscore.", str(context.exception))

	def test_Underscore_Double(self) -> None:
		literal = DecimalBitStringLiteral("1__0")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal has a leading, trailing or double underscore.", str(context.exception))

	def test_NonGraphic(self) -> None:
		literal = OctalBitStringLiteral("1\t2")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal contains a non-graphic character.", str(context.exception))
		self.assertEqual(["Got value 'o\"1\\t2\"'."], context.exception.__notes__)

	def test_LiteralError(self) -> None:
		literal = BinaryBitStringLiteral("2")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertIsInstance(context.exception, VHDLModelException)
		self.assertIsInstance(context.exception, ValueError)
		self.assertIs(literal, context.exception.Literal)

	def test_LiteralError_KeywordOnly(self) -> None:
		literal = BinaryBitStringLiteral("2")

		ex = LiteralError("Message.", literal=literal)
		self.assertEqual("Message.", str(ex))
		self.assertIs(literal, ex.Literal)

		with self.assertRaises(TypeError):
			_ = LiteralError("Message.", literal)

	def test_LiteralError_Required(self) -> None:
		with self.assertRaises(TypeError):
			_ = LiteralError("Message.")

	def test_Cached(self) -> None:
		literal = HexadecimalBitStringLiteral("A5")

		self.assertIs(literal.BinaryValue, literal.BinaryValue)
		self.assertEqual(8, literal.Bits)

	def test_Copy(self) -> None:
		literal = HexadecimalBitStringLiteral("F5", 12, True)
		_ = literal.BinaryValue

		copy = literal.Copy()

		self.assertEqual("12sx\"F5\"", str(copy))
		self.assertEqual("111111110101", copy.BinaryValue)


class BinaryBitStringLiterals(Testcase):
	def test_Plain(self) -> None:
		literal = BinaryBitStringLiteral("1010")

		self.assertEqual("1010", literal.Value)
		self.assertEqual("1010", literal.BinaryValue)
		self.assertEqual(4, literal.Bits)
		self.assertIsNone(literal.Length)
		self.assertIsNone(literal.IsSigned)
		self.assertEqual("b\"1010\"", str(literal))

	def test_Underscores(self) -> None:
		literal = BinaryBitStringLiteral("1_0_1")

		self.assertEqual("1_0_1", literal.Value)
		self.assertEqual("101", literal.BinaryValue)
		self.assertEqual(3, literal.Bits)

	def test_Empty(self) -> None:
		literal = BinaryBitStringLiteral("")

		self.assertEqual("", literal.BinaryValue)
		self.assertEqual(0, literal.Bits)

	def test_GraphicCharacters(self) -> None:
		literal = BinaryBitStringLiteral("1Z-a ")

		self.assertEqual("1Z-a ", literal.BinaryValue)

	def test_InvalidDigit(self) -> None:
		literal = BinaryBitStringLiteral("012")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal contains a digit not allowed in base 2.", str(context.exception))
		self.assertEqual(["Got digit '2' in value 'b\"012\"'."], context.exception.__notes__)


class OctalBitStringLiterals(Testcase):
	def test_Plain(self) -> None:
		literal = OctalBitStringLiteral("17")

		self.assertEqual("17", literal.Value)
		self.assertEqual("001111", literal.BinaryValue)
		self.assertEqual(6, literal.Bits)
		self.assertEqual("o\"17\"", str(literal))

	def test_GraphicCharacters(self) -> None:
		literal = OctalBitStringLiteral("7U")

		self.assertEqual("111UUU", literal.BinaryValue)

	def test_HexadecimalLetter(self) -> None:
		literal = OctalBitStringLiteral("A")

		self.assertEqual("AAA", literal.BinaryValue)

	def test_InvalidDigit(self) -> None:
		literal = OctalBitStringLiteral("8")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal contains a digit not allowed in base 8.", str(context.exception))
		self.assertEqual(["Got digit '8' in value 'o\"8\"'."], context.exception.__notes__)


class DecimalBitStringLiterals(Testcase):
	def test_Plain(self) -> None:
		literal = DecimalBitStringLiteral("160")

		self.assertEqual("160", literal.Value)
		self.assertEqual("10100000", literal.BinaryValue)
		self.assertEqual(8, literal.Bits)
		self.assertEqual("d\"160\"", str(literal))

	def test_Underscores(self) -> None:
		literal = DecimalBitStringLiteral("1_000")

		self.assertEqual("1111101000", literal.BinaryValue)

	def test_LeadingZeros(self) -> None:
		literal = DecimalBitStringLiteral("0010")

		self.assertEqual("1010", literal.BinaryValue)

	def test_Zero(self) -> None:
		literal = DecimalBitStringLiteral("0")

		self.assertEqual("", literal.BinaryValue)
		self.assertEqual(0, literal.Bits)

	def test_Empty(self) -> None:
		literal = DecimalBitStringLiteral("")

		self.assertEqual("", literal.BinaryValue)

	def test_Large(self) -> None:
		literal = DecimalBitStringLiteral("18446744073709551616")

		self.assertEqual("1" + "0" * 64, literal.BinaryValue)
		self.assertEqual(65, literal.Bits)

	def test_Length(self) -> None:
		literal = DecimalBitStringLiteral("5", 10)

		self.assertEqual("0000000101", literal.BinaryValue)
		self.assertEqual("10d\"5\"", str(literal))

	def test_Length_Truncated(self) -> None:
		literal = DecimalBitStringLiteral("15", 4)

		self.assertEqual("1111", literal.BinaryValue)

	def test_Length_TooShort(self) -> None:
		literal = DecimalBitStringLiteral("16", 4)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal's length 4 truncates significant characters.", str(context.exception))
		self.assertEqual(
			["Got value '4d\"16\"' expanded to '10000'.", "Only leading '0' characters can be truncated."],
			context.exception.__notes__
		)

	def test_Letter(self) -> None:
		literal = DecimalBitStringLiteral("1X")

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Decimal bit string literal contains a character other than a digit.", str(context.exception))
		self.assertEqual(["Got character 'X' in value 'd\"1X\"'."], context.exception.__notes__)

	def test_Signed(self) -> None:
		literal = DecimalBitStringLiteral("5", None, True)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Decimal bit string literal can't be signed or unsigned.", str(context.exception))
		self.assertEqual(["Got value 'sd\"5\"'."], context.exception.__notes__)

	def test_Unsigned(self) -> None:
		literal = DecimalBitStringLiteral("5", None, False)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Decimal bit string literal can't be signed or unsigned.", str(context.exception))


class HexadecimalBitStringLiterals(Testcase):
	def test_Plain(self) -> None:
		literal = HexadecimalBitStringLiteral("A5")

		self.assertEqual("A5", literal.Value)
		self.assertEqual("10100101", literal.BinaryValue)
		self.assertEqual(8, literal.Bits)
		self.assertEqual("x\"A5\"", str(literal))

	def test_LowerCase(self) -> None:
		literal = HexadecimalBitStringLiteral("aB")

		self.assertEqual("10101011", literal.BinaryValue)

	def test_Underscores(self) -> None:
		literal = HexadecimalBitStringLiteral("A_5")

		self.assertEqual("A_5", literal.Value)
		self.assertEqual("10100101", literal.BinaryValue)

	def test_GraphicCharacters(self) -> None:
		literal = HexadecimalBitStringLiteral("XZ")

		self.assertEqual("XXXXZZZZ", literal.BinaryValue)

	def test_GraphicCharacters_LowerCase(self) -> None:
		literal = HexadecimalBitStringLiteral("z-")

		self.assertEqual("zzzz----", literal.BinaryValue)

	def test_GraphicCharacters_Letter(self) -> None:
		literal = HexadecimalBitStringLiteral("G")

		self.assertEqual("GGGG", literal.BinaryValue)


class BitStringLiteralLengths(Testcase):
	def test_Equal(self) -> None:
		literal = HexadecimalBitStringLiteral("A5", 8)

		self.assertEqual("10100101", literal.BinaryValue)
		self.assertEqual(8, literal.Length)
		self.assertEqual("8x\"A5\"", str(literal))

	def test_Extended(self) -> None:
		literal = HexadecimalBitStringLiteral("", 4)

		self.assertEqual("0000", literal.BinaryValue)

	def test_Extended_GraphicCharacter(self) -> None:
		literal = HexadecimalBitStringLiteral("Z", 8)

		self.assertEqual("0000ZZZZ", literal.BinaryValue)

	def test_Extended_Unsigned(self) -> None:
		literal = HexadecimalBitStringLiteral("F5", 12, False)

		self.assertEqual("000011110101", literal.BinaryValue)
		self.assertEqual("12ux\"F5\"", str(literal))

	def test_Extended_Signed(self) -> None:
		literal = HexadecimalBitStringLiteral("F5", 12, True)

		self.assertEqual("111111110101", literal.BinaryValue)
		self.assertEqual(12, literal.Bits)
		self.assertEqual("12sx\"F5\"", str(literal))

	def test_Extended_Signed_Positive(self) -> None:
		literal = BinaryBitStringLiteral("01", 4, True)

		self.assertEqual("0001", literal.BinaryValue)

	def test_Extended_Signed_GraphicCharacter(self) -> None:
		literal = HexadecimalBitStringLiteral("Z", 8, True)

		self.assertEqual("ZZZZZZZZ", literal.BinaryValue)

	def test_Extended_Signed_Empty(self) -> None:
		literal = BinaryBitStringLiteral("", 4, True)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Signed bit string literal with an empty value can't be extended.", str(context.exception))
		self.assertEqual(["Got value '4sb\"\"'."], context.exception.__notes__)

	def test_Truncated(self) -> None:
		literal = HexadecimalBitStringLiteral("0F", 7)

		self.assertEqual("0001111", literal.BinaryValue)
		self.assertEqual(7, literal.Bits)

	def test_Truncated_Zero(self) -> None:
		literal = HexadecimalBitStringLiteral("0", 0)

		self.assertEqual("", literal.BinaryValue)

	def test_Truncated_Signed(self) -> None:
		literal = HexadecimalBitStringLiteral("F0", 6, True)

		self.assertEqual("110000", literal.BinaryValue)

	def test_Truncated_Signed_GraphicCharacter(self) -> None:
		literal = HexadecimalBitStringLiteral("ZF", 7, True)

		self.assertEqual("ZZZ1111", literal.BinaryValue)

	def test_TooShort(self) -> None:
		literal = HexadecimalBitStringLiteral("FF", 7)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal's length 7 truncates significant characters.", str(context.exception))
		self.assertEqual(
			["Got value '7x\"FF\"' expanded to '11111111'.", "Only leading '0' characters can be truncated."],
			context.exception.__notes__
		)

	def test_TooShort_GraphicCharacter(self) -> None:
		literal = HexadecimalBitStringLiteral("Z0", 7)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal's length 7 truncates significant characters.", str(context.exception))

	def test_TooShort_Signed(self) -> None:
		literal = HexadecimalBitStringLiteral("7F", 7, True)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal's length 7 truncates significant characters.", str(context.exception))
		self.assertEqual(
			[
				"Got value '7sx\"7F\"' expanded to '01111111'.",
				"Only copies of the leftmost remaining character can be truncated."
			],
			context.exception.__notes__
		)

	def test_TooShort_Signed_Zero(self) -> None:
		literal = HexadecimalBitStringLiteral("0", 0, True)

		with self.assertRaises(LiteralError) as context:
			_ = literal.BinaryValue

		self.assertEqual("Bit string literal's length 0 truncates significant characters.", str(context.exception))


class UnaryExpressions(Testcase):
	"""Regression test: ``operand.Parent = self`` was previously commented out
	(``# FIXME: operand is provided as None``) - confirmed stale in the gap analysis (every real
	construction site always provides a real operand) and now re-enabled. Tested once here via
	``NegationExpression``; every other unary subclass shares the identical, unoverridden
	constructor."""

	def test_Construction(self) -> None:
		operand = IntegerLiteral(1)
		expression = NegationExpression(operand)

		self.assertIs(operand, expression.Operand)
		self.assertIs(expression, operand.Parent)


_UNARY_FORMATS = (
	(NegationExpression,   "-1"),
	(IdentityExpression,   "+1"),
	(InverseExpression,    "not 1"),
	(UnaryAndExpression,   "and 1"),
	(UnaryNandExpression,  "nand 1"),
	(UnaryOrExpression,    "or 1"),
	(UnaryNorExpression,   "nor 1"),
	(UnaryXorExpression,   "xor 1"),
	(UnaryXnorExpression,  "xnor 1"),
	(AbsoluteExpression,   "abs 1"),
	(SubExpression,        "(1)"),
)


class UnaryExpressionFormats(Testcase):
	def test_AllVariants(self) -> None:
		for expressionClass, expected in _UNARY_FORMATS:
			with self.subTest(expression=expressionClass.__name__):
				self.assertEqual(expected, str(expressionClass(IntegerLiteral(1))))

	def test_SubExpression_IsAlsoAParenthesisExpression(self) -> None:
		"""``SubExpression`` mixes in ``ParenthesisExpression``, whose own ``Operand`` hardcodes
		``return None`` - but MRO puts ``UnaryExpression`` first, so the real operand wins and
		``ParenthesisExpression.Operand`` is never actually reached through this class."""
		operand = IntegerLiteral(1)
		expression = SubExpression(operand)

		self.assertIs(operand, expression.Operand)


class TypeConversions(Testcase):
	"""Regression test: ``TypeConversion`` previously had no field for the target type at all (just
	``pass``, inheriting ``UnaryExpression`` unchanged) - unlike every other ``UnaryExpression``
	subclass, its "operator" is the target type name itself, not a fixed ``_FORMAT`` string, so
	``str()`` always raised ``AttributeError``. Fixed by adding ``_targetSubtype`` (mirroring
	``QualifiedExpression._subtype``) and a dedicated ``__str__``."""

	def test_Construction(self) -> None:
		"""``natural(x)``"""
		targetSubtype = SimpleSubtypeSymbol(SimpleName("natural"))
		operand = IntegerLiteral(1)
		expression = TypeConversion(targetSubtype, operand)

		self.assertIs(targetSubtype, expression.TargetSubtype)
		self.assertIs(expression, targetSubtype.Parent)
		self.assertIs(operand, expression.Operand)
		self.assertIs(expression, operand.Parent)
		self.assertEqual("natural?(1)", str(expression))


class BinaryExpressions(Testcase):
	"""Both operands' ``Parent`` wiring is already active (no FIXME here, unlike
	``UnaryExpression``) - tested once via ``AdditionExpression``; every other binary subclass shares
	the identical, unoverridden constructor."""

	def test_Construction(self) -> None:
		left = IntegerLiteral(1)
		right = IntegerLiteral(2)
		expression = AdditionExpression(left, right)

		self.assertIs(left, expression.LeftOperand)
		self.assertIs(right, expression.RightOperand)
		self.assertIs(expression, left.Parent)
		self.assertIs(expression, right.Parent)


_BINARY_FORMATS = (
	(AdditionExpression,               "1 + 2"),
	(SubtractionExpression,            "1 - 2"),
	(ConcatenationExpression,          "1 & 2"),
	(MultiplyExpression,               "1 * 2"),
	(DivisionExpression,               "1 / 2"),
	(RemainderExpression,              "1 rem 2"),
	(ModuloExpression,                 "1 mod 2"),
	(ExponentiationExpression,         "1**2"),
	(AndExpression,                    "1 and 2"),
	(NandExpression,                   "1 nand 2"),
	(OrExpression,                     "1 or 2"),
	(NorExpression,                    "1 nor 2"),
	(XorExpression,                    "1 xor 2"),
	(XnorExpression,                   "1 xnor 2"),
	(EqualExpression,                  "1 = 2"),
	(UnequalExpression,                "1 /= 2"),
	(GreaterThanExpression,            "1 > 2"),
	(GreaterEqualExpression,           "1 >= 2"),
	(LessThanExpression,               "1 < 2"),
	(LessEqualExpression,              "1 <= 2"),
	(MatchingEqualExpression,          "1 ?= 2"),
	(MatchingUnequalExpression,        "1 ?/= 2"),
	(MatchingGreaterThanExpression,    "1 ?> 2"),
	(MatchingGreaterEqualExpression,   "1 ?>= 2"),
	(MatchingLessThanExpression,       "1 ?< 2"),
	(MatchingLessEqualExpression,      "1 ?<= 2"),
	(ShiftRightLogicExpression,        "1 srl 2"),
	(ShiftLeftLogicExpression,         "1 sll 2"),
	(ShiftRightArithmeticExpression,   "1 sra 2"),
	(ShiftLeftArithmeticExpression,    "1 sla 2"),
	(RotateRightExpression,            "1 ror 2"),
	(RotateLeftExpression,             "1 rol 2"),
)


class BinaryExpressionFormats(Testcase):
	def test_AllVariants(self) -> None:
		for expressionClass, expected in _BINARY_FORMATS:
			with self.subTest(expression=expressionClass.__name__):
				self.assertEqual(expected, str(expressionClass(IntegerLiteral(1), IntegerLiteral(2))))


class RangeExpressions(Testcase):
	"""``AscendingRangeExpression``/``DescendingRangeExpression`` additionally expose ``Direction``
	over the plain ``BinaryExpression`` shape."""

	def test_Ascending(self) -> None:
		expression = AscendingRangeExpression(IntegerLiteral(0), IntegerLiteral(7))

		self.assertIs(Direction.To, expression.Direction)
		self.assertEqual("0 to 7", str(expression))

	def test_Descending(self) -> None:
		expression = DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))

		self.assertIs(Direction.DownTo, expression.Direction)
		self.assertEqual("7 downto 0", str(expression))


class QualifiedExpressions(Testcase):
	def test_Construction(self) -> None:
		subtype = SimpleSubtypeSymbol(SimpleName("bit_vector"))
		operand = IntegerLiteral(1)
		expression = QualifiedExpression(subtype, operand)

		self.assertIs(operand, expression.Operand)
		self.assertIs(subtype, expression.Subtype)
		self.assertIs(expression, operand.Parent)
		self.assertIs(expression, subtype.Parent)
		self.assertEqual("bit_vector?'(1)", str(expression))


class TernaryExpressions(Testcase):
	"""Regression test: the constructor previously never accepted or set its three operands at all
	(``# FIXME: parameters and initializers are missing !!``), and ``__str__`` separately indexed past
	the end of the 4-element ``_FORMAT`` tuple (``self._FORMAT[4]``). Both fixed together - the
	constructor now takes the three operands (wiring ``Parent`` for each), and ``__str__`` reads
	``_FORMAT[3]``.

	``TernaryExpression`` itself deliberately exposes no public ``FirstOperand``/``SecondOperand``/
	``ThirdOperand`` properties (see its class docstring) - only ``WhenElseExpression``'s own
	``ThenValue``/``Condition``/``ElseValue`` are public, so this is tested only through that concrete
	subclass."""

	def test_Construction(self) -> None:
		"""``thenValue when condition else elseValue``"""
		thenValue = IntegerLiteral(1)
		condition = IntegerLiteral(2)
		elseValue = IntegerLiteral(3)
		expression = WhenElseExpression(thenValue, condition, elseValue)

		self.assertIs(thenValue, expression.ThenValue)
		self.assertIs(expression, thenValue.Parent)
		self.assertIs(condition, expression.Condition)
		self.assertIs(expression, condition.Parent)
		self.assertIs(elseValue, expression.ElseValue)
		self.assertIs(expression, elseValue.Parent)
		self.assertEqual("1 when 2 else 3", str(expression))


class FunctionCallAndAllocation(Testcase):
	"""``Allocation`` itself (``class Allocation(BaseExpression): pass``) is never instantiated
	directly anywhere - real VHDL always uses one of its two concrete subclasses below (``new T`` or
	``new T'(expr)``), so unlike ``FunctionCall`` (which *is* the real, direct class for a function
	call expression - there's no further subclass to move it to), there's no bare ``Allocation()``
	test here."""

	def test_FunctionCall(self) -> None:
		call = FunctionCall()

		self.assertIsInstance(call, BaseExpression)

	def test_SubtypeAllocation(self) -> None:
		subtype = SimpleSubtypeSymbol(SimpleName("integer"))
		allocation = SubtypeAllocation(subtype)

		self.assertIs(subtype, allocation.Subtype)
		self.assertIs(allocation, subtype.Parent)
		self.assertEqual("new integer?", str(allocation))

	def test_QualifiedExpressionAllocation(self) -> None:
		subtype = SimpleSubtypeSymbol(SimpleName("integer"))
		qualifiedExpression = QualifiedExpression(subtype, IntegerLiteral(1))
		allocation = QualifiedExpressionAllocation(qualifiedExpression)

		self.assertIs(qualifiedExpression, allocation.QualifiedExpression)
		self.assertIs(allocation, qualifiedExpression.Parent)
		self.assertEqual("new integer?'(1)", str(allocation))


class AggregateElements(Testcase):
	def test_SimpleAggregateElement(self) -> None:
		expression = IntegerLiteral(1)
		element = SimpleAggregateElement(expression)

		self.assertIs(expression, element.Expression)
		self.assertIs(element, expression.Parent)
		self.assertEqual("1", str(element))

	def test_IndexedAggregateElement(self) -> None:
		index = IntegerLiteral(0)
		expression = IntegerLiteral(1)
		element = IndexedAggregateElement(index, expression)

		self.assertIs(index, element.Index)
		self.assertIs(expression, element.Expression)
		self.assertIs(element, expression.Parent)
		self.assertEqual("0 => 1", str(element))

	def test_RangedAggregateElement(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		expression = IntegerLiteral(1)
		element = RangedAggregateElement(rng, expression)

		self.assertIs(rng, element.Range)
		self.assertIs(element, rng.Parent)
		self.assertIs(element, expression.Parent)
		self.assertEqual("0 to 3 => 1", str(element))

	def test_NamedAggregateElement(self) -> None:
		name = SimpleSubtypeSymbol(SimpleName("field"))
		expression = IntegerLiteral(1)
		element = NamedAggregateElement(name, expression)

		self.assertIs(name, element.Name)
		self.assertIs(element, name.Parent)
		self.assertEqual("field? => 1", str(element))

	def test_OthersAggregateElement(self) -> None:
		expression = IntegerLiteral(1)
		element = OthersAggregateElement(expression)

		self.assertIs(expression, element.Expression)
		self.assertEqual("others => 1", str(element))


class Aggregates(Testcase):
	def test_Construction(self) -> None:
		element1 = SimpleAggregateElement(IntegerLiteral(1))
		element2 = SimpleAggregateElement(IntegerLiteral(2))
		aggregate = Aggregate([element1, element2])

		self.assertEqual(2, len(aggregate.Elements))
		self.assertIs(aggregate, element1.Parent)
		self.assertIs(aggregate, element2.Parent)
		self.assertEqual("(1, 2)", str(aggregate))


class ClassVariables(Testcase):
	"""
	``_FORMAT`` and ``_DIRECTION`` are constants of the concrete expression class, not object fields.

	They used to be declared as bare annotations, so ``ExtendedType`` made them slots and the concrete
	subclasses' class-level assignment shadowed the slot descriptor. Reading worked, but assigning on an
	instance raised, and that made **every** model containing an expression unpicklable - ``pickle``'s
	default ``__setstate__`` writes each slot back and hit the same error.
	"""

	def test_NotASlot(self) -> None:
		"""A class constant must not appear in any ``__slots__`` along the hierarchy."""
		for expressionClass in (
			UnaryExpression, NegationExpression,
			BinaryExpression, AdditionExpression,
			AscendingRangeExpression, DescendingRangeExpression,
			TernaryExpression, WhenElseExpression,
		):
			with self.subTest(expressionClass=expressionClass.__name__):
				slots = set()
				for cls in expressionClass.__mro__:
					slots.update(getattr(cls, "__slots__", ()))

				self.assertNotIn("_FORMAT", slots)
				self.assertNotIn("_DIRECTION", slots)
				self.assertNotIn("_PRECEDENCE", slots)

	def test_Picklable(self) -> None:
		"""An expression of every arity round-trips through :mod:`pickle`."""
		for expression in (
			NegationExpression(IntegerLiteral(1)),
			AdditionExpression(IntegerLiteral(1), IntegerLiteral(2)),
			AscendingRangeExpression(IntegerLiteral(0), IntegerLiteral(3)),
			DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0)),
			WhenElseExpression(IntegerLiteral(1), IntegerLiteral(0), IntegerLiteral(2)),
		):
			with self.subTest(expression=type(expression).__name__):
				self.assertEqual(str(expression), str(loads(dumps(expression))))

	def test_DirectionIsPerClass(self) -> None:
		"""The two range expressions carry their direction as a class constant, readable without an instance."""
		self.assertIs(Direction.To, AscendingRangeExpression._DIRECTION)
		self.assertIs(Direction.DownTo, DescendingRangeExpression._DIRECTION)


class Precedences(Testcase):
	"""Each operator class names its precedence level of IEEE Std 1076-2008, clause 9.2."""

	def test_Range(self) -> None:
		for expressionClass in (AscendingRangeExpression, DescendingRangeExpression):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Range, expressionClass._PRECEDENCE)

	def test_Conditional(self) -> None:
		self.assertIs(OperatorPrecedence.Conditional, WhenElseExpression._PRECEDENCE)

	def test_Logical(self) -> None:
		for expressionClass in (AndExpression, NandExpression, OrExpression, NorExpression, XorExpression, XnorExpression):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Logical, expressionClass._PRECEDENCE)

	def test_Relational(self) -> None:
		for expressionClass in (
			EqualExpression, UnequalExpression, GreaterThanExpression, GreaterEqualExpression, LessThanExpression,
			LessEqualExpression, MatchingEqualExpression, MatchingUnequalExpression, MatchingGreaterThanExpression,
			MatchingGreaterEqualExpression, MatchingLessThanExpression, MatchingLessEqualExpression
		):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Relational, expressionClass._PRECEDENCE)

	def test_Shift(self) -> None:
		for expressionClass in (
			ShiftRightLogicExpression, ShiftLeftLogicExpression, ShiftRightArithmeticExpression,
			ShiftLeftArithmeticExpression, RotateRightExpression, RotateLeftExpression
		):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Shift, expressionClass._PRECEDENCE)

	def test_Adding(self) -> None:
		"""The adding operators and the signs share a level."""
		for expressionClass in (
			AdditionExpression, SubtractionExpression, ConcatenationExpression, NegationExpression, IdentityExpression
		):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Adding, expressionClass._PRECEDENCE)

	def test_Multiplying(self) -> None:
		for expressionClass in (MultiplyExpression, DivisionExpression, RemainderExpression, ModuloExpression):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Multiplying, expressionClass._PRECEDENCE)

	def test_Miscellaneous(self) -> None:
		for expressionClass in (
			ExponentiationExpression, AbsoluteExpression, InverseExpression, UnaryAndExpression, UnaryNandExpression,
			UnaryOrExpression, UnaryNorExpression, UnaryXorExpression, UnaryXnorExpression
		):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Miscellaneous, expressionClass._PRECEDENCE)

	def test_Primary(self) -> None:
		"""A parenthesized sub-expression and a type conversion are primaries."""
		for expressionClass in (SubExpression, TypeConversion):
			with self.subTest(expressionClass=expressionClass.__name__):
				self.assertIs(OperatorPrecedence.Primary, expressionClass._PRECEDENCE)
