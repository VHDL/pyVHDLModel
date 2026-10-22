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
This module contains the base-class of all visitors walking a VHDL language model.

A model element walks itself: :meth:`ModelEntity.Visit(visitor) <pyVHDLModel.Base.ModelEntity.Visit>` reports the
element and then its children in source order as events to the visitor. A parser's subclass of a model class (e.g. from
``pyGHDL.dom``) inherits the walk of that model class.

.. rubric:: Events

``Visit<Class>(element)``
   The walk enters an element of class ``<Class>``, before its first child.

``Depart<Class>(element)``
   The walk leaves an element of class ``<Class>``, after its last child.

``Visit<Token>(element)``
   The walk passes a token of the element between two of its parts, which is not a model element itself. The event is
   named after the token: a delimiter as IEEE Std 1076-2008 names it in clauses 15.2 and 15.3 (e.g. ``VisitArrow`` for
   ``=>``), a reserved word by itself (e.g. ``VisitWhen``), and a token depending on the element's class by its role
   (e.g. ``VisitOperator``).
"""
from __future__                import annotations

from typing                    import TYPE_CHECKING

from pyTooling.Decorators      import export
from pyTooling.MetaClasses     import ExtendedType, abstractclass

if TYPE_CHECKING:
	from pyVHDLModel.Association import AssociationItem
	from pyVHDLModel.Base        import SimpleRange, RangeFromName
	from pyVHDLModel.Expression  import (
		NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral,
		PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BitStringLiteral, UnaryExpression, NegationExpression,
		IdentityExpression, TypeConversion, SubExpression, BinaryExpression, RangeExpression, AddingExpression,
		MultiplyingExpression, ExponentiationExpression, LogicalExpression, RelationalExpression, ShiftExpression,
		QualifiedExpression, WhenElseExpression, SubtypeAllocation, QualifiedExpressionAllocation, SimpleAggregateElement,
		IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement, OthersAggregateElement, Aggregate
	)
	from pyVHDLModel.Name        import (
		SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, AttributeName, AllName, OpenName
	)
	from pyVHDLModel.Symbol      import Symbol


@export
@abstractclass
class Visitor(metaclass=ExtendedType, slots=True):
	"""
	Base-class of all visitors walking a VHDL language model.

	Every event does nothing: a visitor overrides the events it needs. The events are described in
	:mod:`pyVHDLModel.Visitor`.
	"""

	def VisitLeftParenthesis(self, element: IndexedName | ParenthesisName | TypeConversion) -> None:
		"""
		Visit the left parenthesis between the prefix and the parenthesized list of an element.

		:param element: The element enclosing the list.
		"""

	def VisitComma(self, element: IndexedName | ParenthesisName | Aggregate) -> None:
		"""
		Visit the comma between two items of a list.

		:param element: The element containing the list.
		"""

	def VisitArrow(
		self,
		element: AssociationItem | IndexedAggregateElement | RangedAggregateElement | NamedAggregateElement
	) -> None:
		"""
		Visit the arrow (``=>``) between a choice or formal and its value.

		:param element: The element containing the arrow.
		"""

	def VisitApostrophe(self, expression: QualifiedExpression) -> None:
		"""
		Visit the apostrophe between the subtype and the operand of a qualified expression.

		:param expression: The qualified expression.
		"""

	def VisitWhen(self, expression: WhenElseExpression) -> None:
		"""
		Visit the reserved word ``when`` between the value and the condition of a conditional expression.

		:param expression: The conditional expression.
		"""

	def VisitElse(self, expression: WhenElseExpression) -> None:
		"""
		Visit the reserved word ``else`` between the condition and the alternative value of a conditional expression.

		:param expression: The conditional expression.
		"""

	def VisitOperator(self, expression: BinaryExpression) -> None:
		"""
		Visit the operator between the operands of a binary expression.

		:param expression: The binary expression.
		"""

	def VisitDirection(self, rng: RangeExpression | SimpleRange) -> None:
		"""
		Visit the direction (``to`` or ``downto``) between the bounds of a range.

		:param rng: The range.
		"""

	def VisitNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Visit a null literal.

		:param literal: The null literal.
		"""

	def DepartNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Depart from a null literal.

		:param literal: The null literal.
		"""

	def VisitEnumerationLiteral(self, literal: EnumerationLiteral) -> None:
		"""
		Visit an enumeration literal.

		:param literal: The enumeration literal.
		"""

	def DepartEnumerationLiteral(self, literal: EnumerationLiteral) -> None:
		"""
		Depart from an enumeration literal.

		:param literal: The enumeration literal.
		"""

	def VisitIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Visit an integer literal.

		:param literal: The integer literal.
		"""

	def DepartIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Depart from an integer literal.

		:param literal: The integer literal.
		"""

	def VisitFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Visit a floating-point literal.

		:param literal: The floating-point literal.
		"""

	def DepartFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Depart from a floating-point literal.

		:param literal: The floating-point literal.
		"""

	def VisitPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Visit a physical literal with an integer value.

		:param literal: The physical literal.
		"""

	def DepartPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Depart from a physical literal with an integer value.

		:param literal: The physical literal.
		"""

	def VisitPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Visit a physical literal with a floating-point value.

		:param literal: The physical literal.
		"""

	def DepartPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Depart from a physical literal with a floating-point value.

		:param literal: The physical literal.
		"""

	def VisitCharacterLiteral(self, literal: CharacterLiteral) -> None:
		"""
		Visit a character literal.

		:param literal: The character literal.
		"""

	def DepartCharacterLiteral(self, literal: CharacterLiteral) -> None:
		"""
		Depart from a character literal.

		:param literal: The character literal.
		"""

	def VisitStringLiteral(self, literal: StringLiteral) -> None:
		"""
		Visit a string literal.

		:param literal: The string literal.
		"""

	def DepartStringLiteral(self, literal: StringLiteral) -> None:
		"""
		Depart from a string literal.

		:param literal: The string literal.
		"""

	def VisitBitStringLiteral(self, literal: BitStringLiteral) -> None:
		"""
		Visit a bit string literal.

		:param literal: The bit string literal.
		"""

	def DepartBitStringLiteral(self, literal: BitStringLiteral) -> None:
		"""
		Depart from a bit string literal.

		:param literal: The bit string literal.
		"""

	def VisitSimpleName(self, name: SimpleName) -> None:
		"""
		Visit a simple name.

		:param name: The simple name.
		"""

	def DepartSimpleName(self, name: SimpleName) -> None:
		"""
		Depart from a simple name.

		:param name: The simple name.
		"""

	def VisitSelectedName(self, name: SelectedName) -> None:
		"""
		Visit a selected name, before its prefix.

		:param name: The selected name.
		"""

	def DepartSelectedName(self, name: SelectedName) -> None:
		"""
		Depart from a selected name, after its prefix.

		:param name: The selected name.
		"""

	def VisitAllName(self, name: AllName) -> None:
		"""
		Visit a selected name with suffix ``all``, before its prefix.

		:param name: The ``all`` name.
		"""

	def DepartAllName(self, name: AllName) -> None:
		"""
		Depart from a selected name with suffix ``all``, after its prefix.

		:param name: The ``all`` name.
		"""

	def VisitAttributeName(self, name: AttributeName) -> None:
		"""
		Visit an attribute name, before its prefix.

		:param name: The attribute name.
		"""

	def DepartAttributeName(self, name: AttributeName) -> None:
		"""
		Depart from an attribute name, after its prefix.

		:param name: The attribute name.
		"""

	def VisitIndexedName(self, name: IndexedName) -> None:
		"""
		Visit an indexed name, before its prefix.

		:param name: The indexed name.
		"""

	def DepartIndexedName(self, name: IndexedName) -> None:
		"""
		Depart from an indexed name, after its last index.

		:param name: The indexed name.
		"""

	def VisitParenthesisName(self, name: ParenthesisName) -> None:
		"""
		Visit a name followed by a parenthesized association list, before its prefix.

		:param name: The parenthesis name.
		"""

	def DepartParenthesisName(self, name: ParenthesisName) -> None:
		"""
		Depart from a name followed by a parenthesized association list, after its last association.

		:param name: The parenthesis name.
		"""

	def VisitSlicedName(self, name: SlicedName) -> None:
		"""
		Visit a sliced name, before its prefix.

		:param name: The sliced name.
		"""

	def DepartSlicedName(self, name: SlicedName) -> None:
		"""
		Depart from a sliced name, after its prefix.

		:param name: The sliced name.
		"""

	def VisitOpenName(self, name: OpenName) -> None:
		"""
		Visit the reserved word ``open``.

		:param name: The ``open`` name.
		"""

	def DepartOpenName(self, name: OpenName) -> None:
		"""
		Depart from the reserved word ``open``.

		:param name: The ``open`` name.
		"""

	def VisitSymbol(self, symbol: Symbol) -> None:
		"""
		Visit a symbol, before its name.

		:param symbol: The symbol.
		"""

	def DepartSymbol(self, symbol: Symbol) -> None:
		"""
		Depart from a symbol, after its name.

		:param symbol: The symbol.
		"""

	def VisitAssociationItem(self, item: AssociationItem) -> None:
		"""
		Visit an association item, before its formal or, if positional, its actual.

		:param item: The association item.
		"""

	def DepartAssociationItem(self, item: AssociationItem) -> None:
		"""
		Depart from an association item, after its actual.

		:param item: The association item.
		"""

	def VisitUnaryExpression(self, expression: UnaryExpression) -> None:
		"""
		Visit a unary expression with a reserved word as operator, before its operand.

		Examples of such operators are ``not`` and ``abs``.

		:param expression: The unary expression.
		"""

	def DepartUnaryExpression(self, expression: UnaryExpression) -> None:
		"""
		Depart from a unary expression with a reserved word as operator, after its operand.

		Examples of such operators are ``not`` and ``abs``.

		:param expression: The unary expression.
		"""

	def VisitNegationExpression(self, expression: NegationExpression) -> None:
		"""
		Visit a negation (sign ``-``), before its operand.

		:param expression: The negation.
		"""

	def DepartNegationExpression(self, expression: NegationExpression) -> None:
		"""
		Depart from a negation (sign ``-``), after its operand.

		:param expression: The negation.
		"""

	def VisitIdentityExpression(self, expression: IdentityExpression) -> None:
		"""
		Visit an identity (sign ``+``), before its operand.

		:param expression: The identity.
		"""

	def DepartIdentityExpression(self, expression: IdentityExpression) -> None:
		"""
		Depart from an identity (sign ``+``), after its operand.

		:param expression: The identity.
		"""

	def VisitTypeConversion(self, conversion: TypeConversion) -> None:
		"""
		Visit a type conversion, before its target subtype.

		:param conversion: The type conversion.
		"""

	def DepartTypeConversion(self, conversion: TypeConversion) -> None:
		"""
		Depart from a type conversion, after its operand.

		:param conversion: The type conversion.
		"""

	def VisitSubExpression(self, expression: SubExpression) -> None:
		"""
		Visit a parenthesized sub-expression, before its operand.

		:param expression: The parenthesized sub-expression.
		"""

	def DepartSubExpression(self, expression: SubExpression) -> None:
		"""
		Depart from a parenthesized sub-expression, after its operand.

		:param expression: The parenthesized sub-expression.
		"""

	def VisitLogicalExpression(self, expression: LogicalExpression) -> None:
		"""
		Visit a binary logical expression, before its left operand.

		:param expression: The binary logical expression.
		"""

	def DepartLogicalExpression(self, expression: LogicalExpression) -> None:
		"""
		Depart from a binary logical expression, after its right operand.

		:param expression: The binary logical expression.
		"""

	def VisitRelationalExpression(self, expression: RelationalExpression) -> None:
		"""
		Visit a relational expression, before its left operand.

		:param expression: The relational expression.
		"""

	def DepartRelationalExpression(self, expression: RelationalExpression) -> None:
		"""
		Depart from a relational expression, after its right operand.

		:param expression: The relational expression.
		"""

	def VisitShiftExpression(self, expression: ShiftExpression) -> None:
		"""
		Visit a shift or rotate expression, before its left operand.

		:param expression: The shift or rotate expression.
		"""

	def DepartShiftExpression(self, expression: ShiftExpression) -> None:
		"""
		Depart from a shift or rotate expression, after its right operand.

		:param expression: The shift or rotate expression.
		"""

	def VisitAddingExpression(self, expression: AddingExpression) -> None:
		"""
		Visit an adding expression, before its left operand.

		:param expression: The adding expression.
		"""

	def DepartAddingExpression(self, expression: AddingExpression) -> None:
		"""
		Depart from an adding expression, after its right operand.

		:param expression: The adding expression.
		"""

	def VisitMultiplyingExpression(self, expression: MultiplyingExpression) -> None:
		"""
		Visit a multiplying expression, before its left operand.

		:param expression: The multiplying expression.
		"""

	def DepartMultiplyingExpression(self, expression: MultiplyingExpression) -> None:
		"""
		Depart from a multiplying expression, after its right operand.

		:param expression: The multiplying expression.
		"""

	def VisitExponentiationExpression(self, expression: ExponentiationExpression) -> None:
		"""
		Visit an exponentiation, before its left operand.

		:param expression: The exponentiation.
		"""

	def DepartExponentiationExpression(self, expression: ExponentiationExpression) -> None:
		"""
		Depart from an exponentiation, after its right operand.

		:param expression: The exponentiation.
		"""

	def VisitRangeExpression(self, expression: RangeExpression) -> None:
		"""
		Visit a range expression, before its left bound.

		:param expression: The range expression.
		"""

	def DepartRangeExpression(self, expression: RangeExpression) -> None:
		"""
		Depart from a range expression, after its right bound.

		:param expression: The range expression.
		"""

	def VisitWhenElseExpression(self, expression: WhenElseExpression) -> None:
		"""
		Visit a conditional expression, before its value.

		:param expression: The conditional expression.
		"""

	def DepartWhenElseExpression(self, expression: WhenElseExpression) -> None:
		"""
		Depart from a conditional expression, after its alternative value.

		:param expression: The conditional expression.
		"""

	def VisitQualifiedExpression(self, expression: QualifiedExpression) -> None:
		"""
		Visit a qualified expression, before its subtype.

		:param expression: The qualified expression.
		"""

	def DepartQualifiedExpression(self, expression: QualifiedExpression) -> None:
		"""
		Depart from a qualified expression, after its operand.

		:param expression: The qualified expression.
		"""

	def VisitSubtypeAllocation(self, allocation: SubtypeAllocation) -> None:
		"""
		Visit an allocation of a subtype, before its subtype.

		:param allocation: The allocation of a subtype.
		"""

	def DepartSubtypeAllocation(self, allocation: SubtypeAllocation) -> None:
		"""
		Depart from an allocation of a subtype, after its subtype.

		:param allocation: The allocation of a subtype.
		"""

	def VisitQualifiedExpressionAllocation(self, allocation: QualifiedExpressionAllocation) -> None:
		"""
		Visit an allocation initialized by a qualified expression, before its qualified expression.

		:param allocation: The allocation initialized by a qualified expression.
		"""

	def DepartQualifiedExpressionAllocation(self, allocation: QualifiedExpressionAllocation) -> None:
		"""
		Depart from an allocation initialized by a qualified expression, after its qualified expression.

		:param allocation: The allocation initialized by a qualified expression.
		"""

	def VisitAggregate(self, aggregate: Aggregate) -> None:
		"""
		Visit an aggregate, before its first element.

		:param aggregate: The aggregate.
		"""

	def DepartAggregate(self, aggregate: Aggregate) -> None:
		"""
		Depart from an aggregate, after its last element.

		:param aggregate: The aggregate.
		"""

	def VisitSimpleAggregateElement(self, element: SimpleAggregateElement) -> None:
		"""
		Visit a positional aggregate element, before its expression.

		:param element: The positional aggregate element.
		"""

	def DepartSimpleAggregateElement(self, element: SimpleAggregateElement) -> None:
		"""
		Depart from a positional aggregate element, after its expression.

		:param element: The positional aggregate element.
		"""

	def VisitIndexedAggregateElement(self, element: IndexedAggregateElement) -> None:
		"""
		Visit an aggregate element chosen by an index, before its index.

		:param element: The aggregate element chosen by an index.
		"""

	def DepartIndexedAggregateElement(self, element: IndexedAggregateElement) -> None:
		"""
		Depart from an aggregate element chosen by an index, after its expression.

		:param element: The aggregate element chosen by an index.
		"""

	def VisitRangedAggregateElement(self, element: RangedAggregateElement) -> None:
		"""
		Visit an aggregate element chosen by a range, before its range.

		:param element: The aggregate element chosen by a range.
		"""

	def DepartRangedAggregateElement(self, element: RangedAggregateElement) -> None:
		"""
		Depart from an aggregate element chosen by a range, after its expression.

		:param element: The aggregate element chosen by a range.
		"""

	def VisitNamedAggregateElement(self, element: NamedAggregateElement) -> None:
		"""
		Visit an aggregate element chosen by a record element name, before its name.

		:param element: The aggregate element chosen by a record element name.
		"""

	def DepartNamedAggregateElement(self, element: NamedAggregateElement) -> None:
		"""
		Depart from an aggregate element chosen by a record element name, after its expression.

		:param element: The aggregate element chosen by a record element name.
		"""

	def VisitOthersAggregateElement(self, element: OthersAggregateElement) -> None:
		"""
		Visit the ``others`` element of an aggregate, before its expression.

		:param element: The ``others`` element of an aggregate.
		"""

	def DepartOthersAggregateElement(self, element: OthersAggregateElement) -> None:
		"""
		Depart from the ``others`` element of an aggregate, after its expression.

		:param element: The ``others`` element of an aggregate.
		"""

	def VisitSimpleRange(self, rng: SimpleRange) -> None:
		"""
		Visit a range given by its bounds, before its left bound.

		:param rng: The range.
		"""

	def DepartSimpleRange(self, rng: SimpleRange) -> None:
		"""
		Depart from a range given by its bounds, after its right bound.

		:param rng: The range.
		"""

	def VisitRangeFromName(self, rng: RangeFromName) -> None:
		"""
		Visit a range denoted by a name, before its name.

		:param rng: The range.
		"""

	def DepartRangeFromName(self, rng: RangeFromName) -> None:
		"""
		Depart from a range denoted by a name, after its name.

		:param rng: The range.
		"""
