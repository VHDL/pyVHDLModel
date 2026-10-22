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
#
"""
Copy tests for expressions, literals and aggregates (:mod:`pyVHDLModel.Expression`).
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Expression as ExpressionModule
from pyVHDLModel.Base            import Direction, SimpleRange
from pyVHDLModel.Expression      import (
	NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral,
	PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BinaryBitStringLiteral, OctalBitStringLiteral,
	DecimalBitStringLiteral, HexadecimalBitStringLiteral,
	NegationExpression, IdentityExpression, InverseExpression, AbsoluteExpression, UnaryAndExpression,
	UnaryNandExpression, UnaryOrExpression, UnaryNorExpression, UnaryXorExpression, UnaryXnorExpression,
	TypeConversion, SubExpression,
	AscendingRangeExpression, DescendingRangeExpression, AdditionExpression, SubtractionExpression,
	ConcatenationExpression, MultiplyExpression, DivisionExpression, RemainderExpression, ModuloExpression,
	ExponentiationExpression, AndExpression, NandExpression, OrExpression, NorExpression, XorExpression,
	XnorExpression, EqualExpression, UnequalExpression, GreaterThanExpression, GreaterEqualExpression,
	LessThanExpression, LessEqualExpression, MatchingEqualExpression, MatchingUnequalExpression,
	MatchingGreaterThanExpression, MatchingGreaterEqualExpression, MatchingLessThanExpression,
	MatchingLessEqualExpression, ShiftRightLogicExpression, ShiftLeftLogicExpression, ShiftRightArithmeticExpression,
	ShiftLeftArithmeticExpression, RotateRightExpression, RotateLeftExpression,
	QualifiedExpression, WhenElseExpression, FunctionCall, SubtypeAllocation, QualifiedExpressionAllocation,
	SimpleAggregateElement, IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement,
	OthersAggregateElement, Aggregate
)
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Symbol          import RecordElementSymbol

from tests.unit                  import _Element, _subtypeSymbol
from tests.unit.Copy             import _object, _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _MirrorAdditionExpression(AdditionExpression):
	"""An addition of another package, constructed from an extra parameter (like a :mod:`pyGHDL.dom` class)."""

	_node: int  #: The extra constructor parameter.

	def __init__(self, node: int, leftOperand: IntegerLiteral, rightOperand: IntegerLiteral) -> None:
		super().__init__(leftOperand, rightOperand)
		self._node = node


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every expression class has a ``Copy()`` calling its own constructor."""
		classes = _concreteModelClasses(ExpressionModule)

		self.assertIn(Aggregate, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class Literals(Testcase):
	def test_Null(self) -> None:
		original = NullLiteral(_Element())

		copy = original.Copy()

		self.assertIs(NullLiteral, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertEqual("null", VHDLWriter().Format(copy))

	def test_Enumeration(self) -> None:
		original = EnumerationLiteral("Idle", _Element())

		copy = original.Copy()

		self.assertIs(EnumerationLiteral, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertEqual("Idle", copy.Value)

	def test_Integer(self) -> None:
		original = IntegerLiteral(42)
		original.Parent = _Element()

		copy = original.Copy()

		self.assertIs(IntegerLiteral, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertEqual(42, copy.Value)

	def test_FloatingPoint(self) -> None:
		original = FloatingPointLiteral(3.5)

		copy = original.Copy()

		self.assertIs(FloatingPointLiteral, type(copy))
		self.assertEqual(3.5, copy.Value)

	def test_PhysicalInteger(self) -> None:
		original = PhysicalIntegerLiteral(10, "ns")

		copy = original.Copy()

		self.assertIs(PhysicalIntegerLiteral, type(copy))
		self.assertEqual(10, copy.Value)
		self.assertEqual("ns", copy.UnitName)

	def test_PhysicalFloating(self) -> None:
		original = PhysicalFloatingLiteral(1.5, "ns")

		copy = original.Copy()

		self.assertIs(PhysicalFloatingLiteral, type(copy))
		self.assertEqual(1.5, copy.Value)
		self.assertEqual("ns", copy.UnitName)

	def test_Character(self) -> None:
		original = CharacterLiteral("a")

		copy = original.Copy()

		self.assertIs(CharacterLiteral, type(copy))
		self.assertEqual("'a'", VHDLWriter().Format(copy))

	def test_String(self) -> None:
		original = StringLiteral("text")

		copy = original.Copy()

		self.assertIs(StringLiteral, type(copy))
		self.assertEqual("\"text\"", VHDLWriter().Format(copy))

	def test_BitString(self) -> None:
		for cls in (BinaryBitStringLiteral, OctalBitStringLiteral, DecimalBitStringLiteral, HexadecimalBitStringLiteral):
			with self.subTest(cls.__name__):
				original = cls("10", 8)

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertEqual("10", copy.Value)
				self.assertEqual(8, copy.Length)
				self.assertIsNone(copy.IsSigned)
				self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_BitString_Signed(self) -> None:
		original = HexadecimalBitStringLiteral("A0", 8, True)

		copy = original.Copy()

		self.assertTrue(copy.IsSigned)
		self.assertEqual("8sx\"A0\"", VHDLWriter().Format(copy))


class UnaryExpressions(Testcase):
	def test_Copy(self) -> None:
		for cls in (
			NegationExpression,
			IdentityExpression,
			InverseExpression,
			AbsoluteExpression,
			UnaryAndExpression,
			UnaryNandExpression,
			UnaryOrExpression,
			UnaryNorExpression,
			UnaryXorExpression,
			UnaryXnorExpression,
			SubExpression
		):
			with self.subTest(cls.__name__):
				operand = _object("a")
				original = cls(operand, _Element())

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertIsNot(operand, copy.Operand)
				self.assertIsNot(operand.Name, copy.Operand.Name)
				self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_Copy_Parent(self) -> None:
		"""The operand of the copy has the copy as parent."""
		original = NegationExpression(IntegerLiteral(1))

		copy = original.Copy()

		self.assertIs(original, original.Operand.Parent)
		self.assertIs(copy, copy.Operand.Parent)

	def test_TypeConversion(self) -> None:
		subtype = _subtypeSymbol("integer")
		operand = IntegerLiteral(1)
		original = TypeConversion(subtype, operand, _Element())

		copy = original.Copy()

		self.assertIs(TypeConversion, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(subtype, copy.TargetSubtype)
		self.assertIsNot(subtype.Name, copy.TargetSubtype.Name)
		self.assertIsNot(operand, copy.Operand)
		self.assertIs(copy, copy.Operand.Parent)
		self.assertEqual("integer(1)", VHDLWriter().Format(copy))


class BinaryExpressions(Testcase):
	def test_Copy(self) -> None:
		for cls in (
			AscendingRangeExpression,
			DescendingRangeExpression,
			AdditionExpression,
			SubtractionExpression,
			ConcatenationExpression,
			MultiplyExpression,
			DivisionExpression,
			RemainderExpression,
			ModuloExpression,
			ExponentiationExpression,
			AndExpression,
			NandExpression,
			OrExpression,
			NorExpression,
			XorExpression,
			XnorExpression,
			EqualExpression,
			UnequalExpression,
			GreaterThanExpression,
			GreaterEqualExpression,
			LessThanExpression,
			LessEqualExpression,
			MatchingEqualExpression,
			MatchingUnequalExpression,
			MatchingGreaterThanExpression,
			MatchingGreaterEqualExpression,
			MatchingLessThanExpression,
			MatchingLessEqualExpression,
			ShiftRightLogicExpression,
			ShiftLeftLogicExpression,
			ShiftRightArithmeticExpression,
			ShiftLeftArithmeticExpression,
			RotateRightExpression,
			RotateLeftExpression
		):
			with self.subTest(cls.__name__):
				left = _object("a")
				right = IntegerLiteral(2)
				original = cls(left, right, _Element())

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertIsNot(left, copy.LeftOperand)
				self.assertIsNot(right, copy.RightOperand)
				self.assertIs(copy, copy.RightOperand.Parent)
				self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_Copy_Tree(self) -> None:
		"""Every level of an expression tree is copied."""
		original = MultiplyExpression(SubExpression(AdditionExpression(_object("a"), IntegerLiteral(1))), _object("b"))

		copy = original.Copy()

		self.assertEqual("(a + 1) * b", VHDLWriter().Format(copy))
		self.assertIsNot(original.LeftOperand, copy.LeftOperand)
		self.assertIs(copy, copy.LeftOperand.Parent)
		self.assertIsNot(original.LeftOperand.Operand, copy.LeftOperand.Operand)
		self.assertIs(copy.LeftOperand, copy.LeftOperand.Operand.Parent)
		self.assertIsNot(original.LeftOperand.Operand.LeftOperand, copy.LeftOperand.Operand.LeftOperand)
		self.assertIsNot(original.LeftOperand.Operand.RightOperand, copy.LeftOperand.Operand.RightOperand)
		self.assertIs(copy.LeftOperand.Operand, copy.LeftOperand.Operand.RightOperand.Parent)

	def test_Copy_Derived(self) -> None:
		"""A copy of an expression of a class derived outside pyVHDLModel is an expression of the pyVHDLModel class."""
		original = _MirrorAdditionExpression(42, IntegerLiteral(1), IntegerLiteral(2))

		copy = original.Copy()

		self.assertIs(AdditionExpression, type(copy))
		self.assertEqual("1 + 2", VHDLWriter().Format(copy))


class QualifiedExpressions(Testcase):
	def test_Copy(self) -> None:
		subtype = _subtypeSymbol("byte")
		operand = IntegerLiteral(5)
		original = QualifiedExpression(subtype, operand, _Element())

		copy = original.Copy()

		self.assertIs(QualifiedExpression, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(subtype, copy.Subtype)
		self.assertIsNot(operand, copy.Operand)
		self.assertIs(copy, copy.Operand.Parent)
		self.assertEqual("byte'(5)", VHDLWriter().Format(copy))


class TernaryExpressions(Testcase):
	def test_WhenElse(self) -> None:
		original = WhenElseExpression(_object("a"), _object("f"), _object("b"), _Element())

		copy = original.Copy()

		self.assertIs(WhenElseExpression, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.ThenValue, copy.ThenValue)
		self.assertIsNot(original.Condition, copy.Condition)
		self.assertIsNot(original.ElseValue, copy.ElseValue)
		self.assertEqual("a when f else b", VHDLWriter().Format(copy))


class FunctionCalls(Testcase):
	def test_Copy(self) -> None:
		original = FunctionCall(_Element())

		copy = original.Copy()

		self.assertIs(FunctionCall, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)


class Allocations(Testcase):
	def test_Subtype(self) -> None:
		subtype = _subtypeSymbol("node")
		original = SubtypeAllocation(subtype, _Element())

		copy = original.Copy()

		self.assertIs(SubtypeAllocation, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(subtype, copy.Subtype)
		self.assertEqual("new node", VHDLWriter().Format(copy))

	def test_QualifiedExpression(self) -> None:
		qualifiedExpression = QualifiedExpression(_subtypeSymbol("integer"), IntegerLiteral(5))
		original = QualifiedExpressionAllocation(qualifiedExpression, _Element())

		copy = original.Copy()

		self.assertIs(QualifiedExpressionAllocation, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(qualifiedExpression, copy.QualifiedExpression)
		self.assertIs(copy, copy.QualifiedExpression.Parent)
		self.assertEqual("new integer'(5)", VHDLWriter().Format(copy))


class Aggregates(Testcase):
	def test_Copy(self) -> None:
		simple = SimpleAggregateElement(CharacterLiteral("1"))
		indexed = IndexedAggregateElement(IntegerLiteral(0), CharacterLiteral("1"))
		rng = SimpleRange(IntegerLiteral(1), IntegerLiteral(3), Direction.To)
		ranged = RangedAggregateElement(rng, CharacterLiteral("0"))
		others = OthersAggregateElement(CharacterLiteral("1"))
		original = Aggregate([simple, indexed, ranged, others], _Element())

		copy = original.Copy()

		self.assertIs(Aggregate, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Elements, copy.Elements)
		self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))
		for element in copy.Elements:
			self.assertIs(copy, element.Parent)
			self.assertIs(element, element.Expression.Parent)

		self.assertIs(SimpleAggregateElement, type(copy.Elements[0]))
		self.assertIsNot(simple, copy.Elements[0])
		self.assertIsNot(simple.Expression, copy.Elements[0].Expression)
		self.assertIs(IndexedAggregateElement, type(copy.Elements[1]))
		self.assertIsNot(indexed, copy.Elements[1])
		self.assertIsNot(indexed.Index, copy.Elements[1].Index)
		self.assertIs(RangedAggregateElement, type(copy.Elements[2]))
		self.assertIsNot(ranged, copy.Elements[2])
		self.assertIsNot(ranged.Range, copy.Elements[2].Range)
		self.assertIs(copy.Elements[2], copy.Elements[2].Range.Parent)
		self.assertIs(OthersAggregateElement, type(copy.Elements[3]))
		self.assertIsNot(others, copy.Elements[3])

	def test_Copy_Named(self) -> None:
		name = RecordElementSymbol(SimpleName("a"))
		original = Aggregate([NamedAggregateElement(name, CharacterLiteral("1"))])

		copy = original.Copy()

		self.assertIs(NamedAggregateElement, type(copy.Elements[0]))
		self.assertIsNot(name, copy.Elements[0].Name)
		self.assertEqual("a", copy.Elements[0].Name.Name.Identifier)
		self.assertEqual("(a => '1')", VHDLWriter().Format(copy))

	def test_Copy_Modify(self) -> None:
		"""Changing the elements of the copy leaves the original unchanged."""
		original = Aggregate([IndexedAggregateElement(IntegerLiteral(0), CharacterLiteral("1"))])

		copy = original.Copy()
		copy.Elements.append(OthersAggregateElement(CharacterLiteral("0")))

		self.assertEqual("(0 => '1')", VHDLWriter().Format(original))
		self.assertEqual("(0 => '1', others => '0')", VHDLWriter().Format(copy))
