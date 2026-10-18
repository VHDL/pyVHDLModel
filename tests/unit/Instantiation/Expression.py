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
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Expression import (
	BaseExpression, Literal,
	NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral,
	PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral, StringLiteral,
	BinaryBitStringLiteral, OctalBitStringLiteral, DecimalBitStringLiteral, HexadecimalBitStringLiteral,
	UnaryExpression,
	NegationExpression, IdentityExpression, InverseExpression,
	UnaryAndExpression, UnaryNandExpression, UnaryOrExpression, UnaryNorExpression,
	UnaryXorExpression, UnaryXnorExpression, AbsoluteExpression, TypeConversion, SubExpression,
	BinaryExpression,
	AscendingRangeExpression, DescendingRangeExpression,
	AdditionExpression, SubtractionExpression, ConcatenationExpression,
	MultiplyExpression, DivisionExpression, RemainderExpression, ModuloExpression, ExponentiationExpression,
	AndExpression, NandExpression, OrExpression, NorExpression, XorExpression, XnorExpression,
	EqualExpression, UnequalExpression, GreaterThanExpression, GreaterEqualExpression,
	LessThanExpression, LessEqualExpression,
	MatchingEqualExpression, MatchingUnequalExpression, MatchingGreaterThanExpression,
	MatchingGreaterEqualExpression, MatchingLessThanExpression, MatchingLessEqualExpression,
	ShiftRightLogicExpression, ShiftLeftLogicExpression,
	ShiftRightArithmeticExpression, ShiftLeftArithmeticExpression,
	RotateRightExpression, RotateLeftExpression,
	QualifiedExpression, TernaryExpression, WhenElseExpression,
	FunctionCall, SubtypeAllocation, QualifiedExpressionAllocation,
	AggregateElement, SimpleAggregateElement, IndexedAggregateElement, RangedAggregateElement,
	NamedAggregateElement, OthersAggregateElement, Aggregate,
)


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
		literal = CharacterLiteral("'a'")

		self.assertEqual("'a'", literal.Value)
		self.assertEqual("'a'", str(literal))

	def test_StringLiteral(self) -> None:
		literal = StringLiteral("hello")

		self.assertEqual("hello", literal.Value)
		self.assertEqual("\"hello\"", str(literal))


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
	"""``BitStringLiteral`` itself is abstract in practice (``_base`` is only set by its four concrete
	subclasses as a ``ClassVar``); ``Length``/``Signed``/``BinaryValue``/``Bits`` are all still-open
	gaps beyond ``Value`` itself for ``BinaryValue``/``Bits`` (see the class's own ``.. todo``-less but
	clearly unfinished state - both always stay ``None``, there's no code anywhere that computes
	them yet)."""

	def test_Binary(self) -> None:
		literal = BinaryBitStringLiteral("101")

		self.assertEqual("101", literal.Value)
		self.assertIsNone(literal.BinaryValue)
		self.assertIsNone(literal.Bits)
		self.assertIsNone(literal.Length)
		self.assertIsNone(literal.IsSigned)
		self.assertEqual("b\"101\"", str(literal))

	def test_Octal(self) -> None:
		self.assertEqual("o\"17\"", str(OctalBitStringLiteral("17")))

	def test_Decimal(self) -> None:
		self.assertEqual("d\"9\"", str(DecimalBitStringLiteral("9")))

	def test_Hexadecimal(self) -> None:
		self.assertEqual("x\"FF\"", str(HexadecimalBitStringLiteral("FF")))

	def test_WithLength(self) -> None:
		"""``8x"F"`` - explicit-length metadata (C.2 in the gap analysis)."""
		literal = HexadecimalBitStringLiteral("F", length=8)

		self.assertEqual(8, literal.Length)
		self.assertEqual("8x\"F\"", str(literal))

	def test_Signed(self) -> None:
		"""``sx"F"`` - signed metadata (C.2 in the gap analysis)."""
		literal = HexadecimalBitStringLiteral("F", isSigned=True)

		self.assertTrue(literal.IsSigned)
		self.assertEqual("sx\"F\"", str(literal))

	def test_Unsigned(self) -> None:
		"""``ux"F"`` - unsigned metadata (C.2 in the gap analysis)."""
		literal = HexadecimalBitStringLiteral("F", isSigned=False)

		self.assertFalse(literal.IsSigned)
		self.assertEqual("ux\"F\"", str(literal))


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
	``_FORMAT`` and ``_direction`` are constants of the concrete expression class, not object fields.

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
				self.assertNotIn("_direction", slots)

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
		self.assertIs(Direction.To, AscendingRangeExpression._direction)
		self.assertIs(Direction.DownTo, DescendingRangeExpression._direction)
