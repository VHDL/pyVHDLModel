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

``Visit<Part>(element)`` and ``Depart<Part>(element)``
   The walk enters or leaves a part of the element, which is not a model element itself, e.g. the generic clause of a
   component. The events are named after the part's production in IEEE Std 1076-2008 (e.g. ``VisitGenericClause``).

``Visit<Token>(element)``
   The walk passes a token of the element between two of its parts, which is not a model element itself. The event is
   named after the token: a delimiter as IEEE Std 1076-2008 names it in clauses 15.2 and 15.3 (e.g. ``VisitArrow`` for
   ``=>``), a reserved word by itself (e.g. ``VisitWhen``), and a token depending on the element's class by its role
   (e.g. ``VisitOperator``).
"""
from __future__                  import annotations

from typing                      import TYPE_CHECKING

from pyTooling.Decorators        import export
from pyTooling.MetaClasses       import ExtendedType, abstractclass

if TYPE_CHECKING:
	from pyVHDLModel               import Document
	from pyVHDLModel.Association   import AssociationItem, GenericMapAspectMixin, PortMapAspectMixin
	from pyVHDLModel.Base          import SimpleRange, RangeFromName, WaveformElement, ReportStatementMixin
	from pyVHDLModel.Common        import ProcedureCallMixin, SignalAssignmentMixin, WaveformMixin, ConditionalWaveform, \
	                                      SelectedWaveform, OthersSelectedWaveform, ConditionalWaveformsMixin, \
	                                      SelectedWaveformsMixin
	from pyVHDLModel.Concurrent    import ProcessStatement, ConcurrentProcedureCall, ConcurrentSimpleSignalAssignment, \
	                                      ConcurrentSelectedSignalAssignment, ConcurrentConditionalSignalAssignment, \
	                                      ConcurrentAssertStatement
	from pyVHDLModel.Configuration import EntityAspectEntity, EntityAspectConfiguration, EntityAspectOpen, \
	                                      BindingIndication, AllInstantiationList, OthersInstantiationList, \
	                                      ComponentConfiguration, BlockConfiguration
	from pyVHDLModel.Declaration   import Attribute, AttributeSpecification, Alias
	from pyVHDLModel.DesignUnit    import Reference, LibraryClause, UseClause, ContextReference, DesignUnit, Context, \
	                                      Package, PackageBody, Entity, Architecture, Configuration, Component
	from pyVHDLModel.Expression    import NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, \
	                                      PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral, \
	                                      StringLiteral, BitStringLiteral, UnaryExpression, NegationExpression, \
	                                      IdentityExpression, TypeConversion, SubExpression, BinaryExpression, \
	                                      RangeExpression, AddingExpression, MultiplyingExpression, \
	                                      ExponentiationExpression, LogicalExpression, RelationalExpression, \
	                                      ShiftExpression, QualifiedExpression, WhenElseExpression, SubtypeAllocation, \
	                                      QualifiedExpressionAllocation, SimpleAggregateElement, \
	                                      IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement, \
	                                      OthersAggregateElement, Aggregate
	from pyVHDLModel.Interface     import ModeViewDeclaration, SimpleModeViewElement, CompositeModeViewElement, \
	                                      GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
	                                      PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
	                                      ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
	                                      ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
	                                      ParameterFileInterfaceItem, GenericProcedureInterfaceItem, \
	                                      GenericFunctionInterfaceItem
	from pyVHDLModel.Instantiation import ProcedureInstantiation, FunctionInstantiation, PackageInstantiation
	from pyVHDLModel.Name          import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, \
	                                      AttributeName, AllName, OpenName
	from pyVHDLModel.Object        import WithDefaultExpressionMixin, Constant, DeferredConstant, Variable, \
	                                      SharedVariable, Signal, File
	from pyVHDLModel.Regions       import WithGenericsMixin, WithPortsMixin, WithParametersMixin
	from pyVHDLModel.Sequential    import IndexedChoice, RangedChoice
	from pyVHDLModel.Subprogram    import Subprogram, Procedure, Function
	from pyVHDLModel.Symbol        import Symbol, ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, \
	                                      ConstrainedRecordSubtypeSymbol
	from pyVHDLModel.Type          import AnonymousType, Subtype, EnumeratedType, IntegerType, RealType, PhysicalType, \
	                                      ArrayType, RecordTypeElement, RecordType, AccessType, FileType, ProtectedType, \
	                                      ProtectedTypeBody


@export
@abstractclass
class Visitor(metaclass=ExtendedType, slots=True):
	"""
	Base-class of all visitors walking a VHDL language model.

	Every event does nothing: a visitor overrides the events it needs. The events are described in
	:mod:`pyVHDLModel.Visitor`.
	"""

	def VisitLeftParenthesis(self, element: IndexedName | ParenthesisName | TypeConversion | EntityAspectEntity) -> None:
		"""
		Visit the left parenthesis between the prefix and the parenthesized list of an element.

		:param element: The element enclosing the list.
		"""

	def VisitComma(
		self,
		element: IndexedName | ParenthesisName | Aggregate | ConstrainedArraySubtypeSymbol |
		         ConstrainedRecordSubtypeSymbol | EnumeratedType | ArrayType | AttributeSpecification |
		         GenericMapAspectMixin | PortMapAspectMixin | Reference | ComponentConfiguration | ProcessStatement |
		         ProcedureCallMixin | WaveformMixin | SelectedWaveformsMixin
	) -> None:
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

	def VisitWhen(
		self,
		element: WhenElseExpression | ConditionalWaveform | SelectedWaveform | OthersSelectedWaveform
	) -> None:
		"""
		Visit the reserved word ``when`` before the condition of a conditional expression or waveform, or before the
		choices of a selected waveform.

		:param element: The conditional expression, the conditional waveform or the selected waveform.
		"""

	def VisitElse(self, element: WhenElseExpression | ConditionalWaveformsMixin) -> None:
		"""
		Visit the reserved word ``else`` before the alternative of a conditional expression or conditional waveforms.

		:param element: The conditional expression or the element with conditional waveforms.
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

	def VisitSemicolon(self, element: WithGenericsMixin | WithPortsMixin | WithParametersMixin) -> None:
		"""
		Visit the semicolon between two items of an interface list.

		:param element: The element containing the interface list.
		"""

	def VisitVariableAssignment(self, element: WithDefaultExpressionMixin) -> None:
		"""
		Visit the variable assignment delimiter (``:=``) before a default expression.

		:param element: The element with the default expression.
		"""

	def VisitIs(
		self,
		element: ModeViewDeclaration | Alias | AttributeSpecification | Subprogram | Architecture | Configuration |
		         ProcessStatement
	) -> None:
		"""
		Visit the reserved word ``is`` between the header and the body of a declaration.

		:param element: The declaration.
		"""

	def VisitBox(self, arrayType: ArrayType) -> None:
		"""
		Visit the box (``<>``) after the type mark of an unbounded index of an array type.

		:param arrayType: The array type.
		"""

	def VisitOf(self, arrayType: ArrayType) -> None:
		"""
		Visit the reserved word ``of`` between the index ranges and the element subtype of an array type.

		:param arrayType: The array type.
		"""

	def VisitUnits(self, physicalType: PhysicalType) -> None:
		"""
		Visit the reserved word ``units`` between the range and the secondary units of a physical type.

		:param physicalType: The physical type.
		"""

	def VisitBegin(self, element: Subprogram | Entity | Architecture | ProcessStatement) -> None:
		"""
		Visit the reserved word ``begin`` between the declarative part and the statement part of an element.

		:param element: The element.
		"""

	def VisitReturn(self, function: Function | GenericFunctionInterfaceItem) -> None:
		"""
		Visit the reserved word ``return`` before the return type of a function.

		:param function: The function.
		"""

	def VisitSignalAssignment(self, element: SignalAssignmentMixin) -> None:
		"""
		Visit the signal assignment delimiter (``<=``) between the target and the waveform of a signal assignment.

		:param element: The signal assignment.
		"""

	def VisitAfter(self, element: WaveformElement) -> None:
		"""
		Visit the reserved word ``after`` between the value and the delay of a waveform element.

		:param element: The waveform element.
		"""

	def VisitSelect(self, element: ConcurrentSelectedSignalAssignment) -> None:
		"""
		Visit the reserved word ``select`` between the selector and the target of a selected assignment.

		:param element: The selected assignment.
		"""

	def VisitBar(self, element: SelectedWaveform) -> None:
		"""
		Visit the vertical line (``|``) between two choices.

		:param element: The element with the choices.
		"""

	def VisitReport(self, element: ReportStatementMixin) -> None:
		"""
		Visit the reserved word ``report`` before the message of an assertion or report.

		:param element: The assertion or report.
		"""

	def VisitSeverity(self, element: ReportStatementMixin) -> None:
		"""
		Visit the reserved word ``severity`` before the severity level of an assertion or report.

		:param element: The assertion or report.
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

	def VisitRangeConstraint(self, symbol: ConstrainedScalarSubtypeSymbol) -> None:
		"""
		Visit the range constraint of a subtype indication, before its range.

		:param symbol: The constrained subtype symbol.
		"""

	def DepartRangeConstraint(self, symbol: ConstrainedScalarSubtypeSymbol) -> None:
		"""
		Depart from the range constraint of a subtype indication, after its range.

		:param symbol: The constrained subtype symbol.
		"""

	def VisitIndexConstraint(
		self,
		element: ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol | ArrayType
	) -> None:
		"""
		Visit the index constraint of a subtype indication, of a record element or of an array type, before its first range.

		:param element: The constrained subtype symbol or the array type.
		"""

	def DepartIndexConstraint(
		self,
		element: ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol | ArrayType
	) -> None:
		"""
		Depart from the index constraint of a subtype indication, of a record element or of an array type, after its last
		range.

		:param element: The constrained subtype symbol or the array type.
		"""

	def VisitRecordConstraint(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Visit the record constraint of a subtype indication, before its first record element constraint.

		:param symbol: The constrained subtype symbol.
		"""

	def DepartRecordConstraint(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Depart from the record constraint of a subtype indication, after its last record element constraint.

		:param symbol: The constrained subtype symbol.
		"""

	def VisitGenericClause(self, element: WithGenericsMixin) -> None:
		"""
		Visit the generic clause of an element, before its first generic.

		:param element: The element with generics.
		"""

	def DepartGenericClause(self, element: WithGenericsMixin) -> None:
		"""
		Depart from the generic clause of an element, after its last generic.

		:param element: The element with generics.
		"""

	def VisitPortClause(self, element: WithPortsMixin) -> None:
		"""
		Visit the port clause of an element, before its first port.

		:param element: The element with ports.
		"""

	def DepartPortClause(self, element: WithPortsMixin) -> None:
		"""
		Depart from the port clause of an element, after its last port.

		:param element: The element with ports.
		"""

	def VisitConstrainedScalarSubtypeSymbol(self, symbol: ConstrainedScalarSubtypeSymbol) -> None:
		"""
		Visit a constrained scalar subtype symbol, before its name.

		:param symbol: The constrained subtype symbol.
		"""

	def DepartConstrainedScalarSubtypeSymbol(self, symbol: ConstrainedScalarSubtypeSymbol) -> None:
		"""
		Depart from a constrained scalar subtype symbol, after its range constraint.

		:param symbol: The constrained subtype symbol.
		"""

	def VisitConstrainedArraySubtypeSymbol(self, symbol: ConstrainedArraySubtypeSymbol) -> None:
		"""
		Visit a constrained array subtype symbol, before its name.

		:param symbol: The constrained subtype symbol.
		"""

	def DepartConstrainedArraySubtypeSymbol(self, symbol: ConstrainedArraySubtypeSymbol) -> None:
		"""
		Depart from a constrained array subtype symbol, after its index constraint.

		:param symbol: The constrained subtype symbol.
		"""

	def VisitConstrainedRecordSubtypeSymbol(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Visit a constrained record subtype symbol, before its name.

		:param symbol: The constrained subtype symbol.
		"""

	def DepartConstrainedRecordSubtypeSymbol(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Depart from a constrained record subtype symbol, after its record constraint.

		:param symbol: The constrained subtype symbol.
		"""

	def VisitConstant(self, constant: Constant) -> None:
		"""
		Visit a constant declaration, before its subtype.

		:param constant: The constant declaration.
		"""

	def DepartConstant(self, constant: Constant) -> None:
		"""
		Depart from a constant declaration, after its default expression.

		:param constant: The constant declaration.
		"""

	def VisitDeferredConstant(self, constant: DeferredConstant) -> None:
		"""
		Visit a deferred constant declaration, before its subtype.

		:param constant: The deferred constant declaration.
		"""

	def DepartDeferredConstant(self, constant: DeferredConstant) -> None:
		"""
		Depart from a deferred constant declaration, after its subtype.

		:param constant: The deferred constant declaration.
		"""

	def VisitVariable(self, variable: Variable) -> None:
		"""
		Visit a variable declaration, before its subtype.

		:param variable: The variable declaration.
		"""

	def DepartVariable(self, variable: Variable) -> None:
		"""
		Depart from a variable declaration, after its default expression.

		:param variable: The variable declaration.
		"""

	def VisitSharedVariable(self, variable: SharedVariable) -> None:
		"""
		Visit a shared variable declaration, before its subtype.

		:param variable: The shared variable declaration.
		"""

	def DepartSharedVariable(self, variable: SharedVariable) -> None:
		"""
		Depart from a shared variable declaration, after its subtype.

		:param variable: The shared variable declaration.
		"""

	def VisitSignal(self, signal: Signal) -> None:
		"""
		Visit a signal declaration, before its subtype.

		:param signal: The signal declaration.
		"""

	def DepartSignal(self, signal: Signal) -> None:
		"""
		Depart from a signal declaration, after its default expression.

		:param signal: The signal declaration.
		"""

	def VisitFile(self, file: File) -> None:
		"""
		Visit a file declaration, before its subtype.

		:param file: The file declaration.
		"""

	def DepartFile(self, file: File) -> None:
		"""
		Depart from a file declaration, after its subtype.

		:param file: The file declaration.
		"""

	def VisitGenericConstantInterfaceItem(self, item: GenericConstantInterfaceItem) -> None:
		"""
		Visit a generic constant, before its subtype.

		:param item: The generic constant.
		"""

	def DepartGenericConstantInterfaceItem(self, item: GenericConstantInterfaceItem) -> None:
		"""
		Depart from a generic constant, after its default expression.

		:param item: The generic constant.
		"""

	def VisitGenericTypeInterfaceItem(self, item: GenericTypeInterfaceItem) -> None:
		"""
		Visit a generic type.

		:param item: The generic type.
		"""

	def DepartGenericTypeInterfaceItem(self, item: GenericTypeInterfaceItem) -> None:
		"""
		Depart from a generic type.

		:param item: The generic type.
		"""

	def VisitPortSimpleSignalInterfaceItem(self, item: PortSimpleSignalInterfaceItem) -> None:
		"""
		Visit a port with a mode, before its subtype.

		:param item: The port.
		"""

	def DepartPortSimpleSignalInterfaceItem(self, item: PortSimpleSignalInterfaceItem) -> None:
		"""
		Depart from a port with a mode, after its default expression.

		:param item: The port.
		"""

	def VisitPortViewSignalInterfaceItem(self, item: PortViewSignalInterfaceItem) -> None:
		"""
		Visit a port with a mode view, before its mode view indication.

		:param item: The port.
		"""

	def DepartPortViewSignalInterfaceItem(self, item: PortViewSignalInterfaceItem) -> None:
		"""
		Depart from a port with a mode view, after its mode view indication.

		:param item: The port.
		"""

	def VisitParameterConstantInterfaceItem(self, item: ParameterConstantInterfaceItem) -> None:
		"""
		Visit a constant parameter, before its subtype.

		:param item: The constant parameter.
		"""

	def DepartParameterConstantInterfaceItem(self, item: ParameterConstantInterfaceItem) -> None:
		"""
		Depart from a constant parameter, after its default expression.

		:param item: The constant parameter.
		"""

	def VisitParameterVariableInterfaceItem(self, item: ParameterVariableInterfaceItem) -> None:
		"""
		Visit a variable parameter, before its subtype.

		:param item: The variable parameter.
		"""

	def DepartParameterVariableInterfaceItem(self, item: ParameterVariableInterfaceItem) -> None:
		"""
		Depart from a variable parameter, after its default expression.

		:param item: The variable parameter.
		"""

	def VisitParameterSimpleSignalInterfaceItem(self, item: ParameterSimpleSignalInterfaceItem) -> None:
		"""
		Visit a signal parameter with a mode, before its subtype.

		:param item: The signal parameter.
		"""

	def DepartParameterSimpleSignalInterfaceItem(self, item: ParameterSimpleSignalInterfaceItem) -> None:
		"""
		Depart from a signal parameter with a mode, after its default expression.

		:param item: The signal parameter.
		"""

	def VisitParameterViewSignalInterfaceItem(self, item: ParameterViewSignalInterfaceItem) -> None:
		"""
		Visit a signal parameter with a mode view, before its mode view indication.

		:param item: The signal parameter.
		"""

	def DepartParameterViewSignalInterfaceItem(self, item: ParameterViewSignalInterfaceItem) -> None:
		"""
		Depart from a signal parameter with a mode view, after its mode view indication.

		:param item: The signal parameter.
		"""

	def VisitParameterFileInterfaceItem(self, item: ParameterFileInterfaceItem) -> None:
		"""
		Visit a file parameter, before its subtype.

		:param item: The file parameter.
		"""

	def DepartParameterFileInterfaceItem(self, item: ParameterFileInterfaceItem) -> None:
		"""
		Depart from a file parameter, after its subtype.

		:param item: The file parameter.
		"""

	def VisitModeViewDeclaration(self, declaration: ModeViewDeclaration) -> None:
		"""
		Visit a mode view declaration, before its subtype.

		:param declaration: The mode view declaration.
		"""

	def DepartModeViewDeclaration(self, declaration: ModeViewDeclaration) -> None:
		"""
		Depart from a mode view declaration, after its last element.

		:param declaration: The mode view declaration.
		"""

	def VisitSimpleModeViewElement(self, element: SimpleModeViewElement) -> None:
		"""
		Visit an element of a mode view with a mode.

		:param element: The mode view element.
		"""

	def DepartSimpleModeViewElement(self, element: SimpleModeViewElement) -> None:
		"""
		Depart from an element of a mode view with a mode.

		:param element: The mode view element.
		"""

	def VisitCompositeModeViewElement(self, element: CompositeModeViewElement) -> None:
		"""
		Visit an element of a mode view with a mode view, before its mode view name.

		:param element: The mode view element.
		"""

	def DepartCompositeModeViewElement(self, element: CompositeModeViewElement) -> None:
		"""
		Depart from an element of a mode view with a mode view, after its mode view name.

		:param element: The mode view element.
		"""

	def VisitComponent(self, component: Component) -> None:
		"""
		Visit a component declaration, before its generic clause.

		:param component: The component declaration.
		"""

	def DepartComponent(self, component: Component) -> None:
		"""
		Depart from a component declaration, after its port clause.

		:param component: The component declaration.
		"""

	def VisitSecondaryUnitDeclaration(self, physicalType: PhysicalType, identifier: str) -> None:
		"""
		Visit a secondary unit declaration of a physical type, before its value.

		:param physicalType: The physical type.
		:param identifier:   The identifier of the secondary unit.
		"""

	def DepartSecondaryUnitDeclaration(self, physicalType: PhysicalType, identifier: str) -> None:
		"""
		Depart from a secondary unit declaration of a physical type, after its value.

		:param physicalType: The physical type.
		:param identifier:   The identifier of the secondary unit.
		"""

	def VisitEntitySpecification(self, specification: AttributeSpecification) -> None:
		"""
		Visit the entity specification of an attribute specification, before its first name.

		:param specification: The attribute specification.
		"""

	def DepartEntitySpecification(self, specification: AttributeSpecification) -> None:
		"""
		Depart from the entity specification of an attribute specification, after its last name.

		:param specification: The attribute specification.
		"""

	def VisitAnonymousType(self, declaration: AnonymousType) -> None:
		"""
		Visit an incomplete type declaration.

		:param declaration: The incomplete type declaration.
		"""

	def DepartAnonymousType(self, declaration: AnonymousType) -> None:
		"""
		Depart from an incomplete type declaration.

		:param declaration: The incomplete type declaration.
		"""

	def VisitSubtype(self, subtype: Subtype) -> None:
		"""
		Visit a subtype declaration, before its subtype indication.

		:param subtype: The subtype declaration.
		"""

	def DepartSubtype(self, subtype: Subtype) -> None:
		"""
		Depart from a subtype declaration, after its subtype indication.

		:param subtype: The subtype declaration.
		"""

	def VisitEnumeratedType(self, enumeratedType: EnumeratedType) -> None:
		"""
		Visit an enumerated type declaration, before its first literal.

		:param enumeratedType: The enumerated type.
		"""

	def DepartEnumeratedType(self, enumeratedType: EnumeratedType) -> None:
		"""
		Depart from an enumerated type declaration, after its last literal.

		:param enumeratedType: The enumerated type.
		"""

	def VisitIntegerType(self, integerType: IntegerType) -> None:
		"""
		Visit an integer type declaration, before its range.

		:param integerType: The integer type.
		"""

	def DepartIntegerType(self, integerType: IntegerType) -> None:
		"""
		Depart from an integer type declaration, after its range.

		:param integerType: The integer type.
		"""

	def VisitRealType(self, realType: RealType) -> None:
		"""
		Visit a floating-point type declaration, before its range.

		:param realType: The floating-point type.
		"""

	def DepartRealType(self, realType: RealType) -> None:
		"""
		Depart from a floating-point type declaration, after its range.

		:param realType: The floating-point type.
		"""

	def VisitPhysicalType(self, physicalType: PhysicalType) -> None:
		"""
		Visit a physical type declaration, before its range.

		:param physicalType: The physical type.
		"""

	def DepartPhysicalType(self, physicalType: PhysicalType) -> None:
		"""
		Depart from a physical type declaration, after its last secondary unit.

		:param physicalType: The physical type.
		"""

	def VisitArrayType(self, arrayType: ArrayType) -> None:
		"""
		Visit an array type declaration, before its index ranges.

		:param arrayType: The array type.
		"""

	def DepartArrayType(self, arrayType: ArrayType) -> None:
		"""
		Depart from an array type declaration, after its element subtype.

		:param arrayType: The array type.
		"""

	def VisitRecordTypeElement(self, element: RecordTypeElement) -> None:
		"""
		Visit an element declaration of a record type, before its subtype.

		:param element: The record element declaration.
		"""

	def DepartRecordTypeElement(self, element: RecordTypeElement) -> None:
		"""
		Depart from an element declaration of a record type, after its subtype.

		:param element: The record element declaration.
		"""

	def VisitRecordType(self, recordType: RecordType) -> None:
		"""
		Visit a record type declaration, before its first element declaration.

		:param recordType: The record type.
		"""

	def DepartRecordType(self, recordType: RecordType) -> None:
		"""
		Depart from a record type declaration, after its last element declaration.

		:param recordType: The record type.
		"""

	def VisitAccessType(self, accessType: AccessType) -> None:
		"""
		Visit an access type declaration, before its designated subtype.

		:param accessType: The access type.
		"""

	def DepartAccessType(self, accessType: AccessType) -> None:
		"""
		Depart from an access type declaration, after its designated subtype.

		:param accessType: The access type.
		"""

	def VisitFileType(self, fileType: FileType) -> None:
		"""
		Visit a file type declaration, before its designated subtype.

		:param fileType: The file type.
		"""

	def DepartFileType(self, fileType: FileType) -> None:
		"""
		Depart from a file type declaration, after its designated subtype.

		:param fileType: The file type.
		"""

	def VisitAlias(self, alias: Alias) -> None:
		"""
		Visit an alias declaration, before its subtype or name.

		:param alias: The alias declaration.
		"""

	def DepartAlias(self, alias: Alias) -> None:
		"""
		Depart from an alias declaration, after its name.

		:param alias: The alias declaration.
		"""

	def VisitAttribute(self, attribute: Attribute) -> None:
		"""
		Visit an attribute declaration, before its subtype.

		:param attribute: The attribute declaration.
		"""

	def DepartAttribute(self, attribute: Attribute) -> None:
		"""
		Depart from an attribute declaration, after its subtype.

		:param attribute: The attribute declaration.
		"""

	def VisitAttributeSpecification(self, specification: AttributeSpecification) -> None:
		"""
		Visit an attribute specification, before its attribute.

		:param specification: The attribute specification.
		"""

	def DepartAttributeSpecification(self, specification: AttributeSpecification) -> None:
		"""
		Depart from an attribute specification, after its expression.

		:param specification: The attribute specification.
		"""

	def VisitFormalParameterList(self, element: WithParametersMixin) -> None:
		"""
		Visit the formal parameter list of a subprogram, before its first parameter.

		:param element: The element with parameters.
		"""

	def DepartFormalParameterList(self, element: WithParametersMixin) -> None:
		"""
		Depart from the formal parameter list of a subprogram, after its last parameter.

		:param element: The element with parameters.
		"""

	def VisitGenericMapAspect(self, element: GenericMapAspectMixin) -> None:
		"""
		Visit the generic map aspect of an element, before its first association.

		:param element: The element with a generic map aspect.
		"""

	def DepartGenericMapAspect(self, element: GenericMapAspectMixin) -> None:
		"""
		Depart from the generic map aspect of an element, after its last association.

		:param element: The element with a generic map aspect.
		"""

	def VisitProcedure(self, procedure: Procedure) -> None:
		"""
		Visit a procedure declaration or body, before its generic clause.

		:param procedure: The procedure.
		"""

	def DepartProcedure(self, procedure: Procedure) -> None:
		"""
		Depart from a procedure declaration or body, after its statements.

		:param procedure: The procedure.
		"""

	def VisitFunction(self, function: Function) -> None:
		"""
		Visit a function declaration or body, before its generic clause.

		:param function: The function.
		"""

	def DepartFunction(self, function: Function) -> None:
		"""
		Depart from a function declaration or body, after its statements.

		:param function: The function.
		"""

	def VisitGenericProcedureInterfaceItem(self, item: GenericProcedureInterfaceItem) -> None:
		"""
		Visit a generic procedure, before its parameters.

		:param item: The generic procedure.
		"""

	def DepartGenericProcedureInterfaceItem(self, item: GenericProcedureInterfaceItem) -> None:
		"""
		Depart from a generic procedure, after its parameters.

		:param item: The generic procedure.
		"""

	def VisitGenericFunctionInterfaceItem(self, item: GenericFunctionInterfaceItem) -> None:
		"""
		Visit a generic function, before its parameters.

		:param item: The generic function.
		"""

	def DepartGenericFunctionInterfaceItem(self, item: GenericFunctionInterfaceItem) -> None:
		"""
		Depart from a generic function, after its return type.

		:param item: The generic function.
		"""

	def VisitProcedureInstantiation(self, instantiation: ProcedureInstantiation) -> None:
		"""
		Visit a procedure instantiation, before its generic procedure.

		:param instantiation: The procedure instantiation.
		"""

	def DepartProcedureInstantiation(self, instantiation: ProcedureInstantiation) -> None:
		"""
		Depart from a procedure instantiation, after its generic map aspect.

		:param instantiation: The procedure instantiation.
		"""

	def VisitFunctionInstantiation(self, instantiation: FunctionInstantiation) -> None:
		"""
		Visit a function instantiation, before its generic function.

		:param instantiation: The function instantiation.
		"""

	def DepartFunctionInstantiation(self, instantiation: FunctionInstantiation) -> None:
		"""
		Depart from a function instantiation, after its generic map aspect.

		:param instantiation: The function instantiation.
		"""

	def VisitProtectedType(self, protectedType: ProtectedType) -> None:
		"""
		Visit a protected type declaration, before its first method.

		:param protectedType: The protected type.
		"""

	def DepartProtectedType(self, protectedType: ProtectedType) -> None:
		"""
		Depart from a protected type declaration, after its last method.

		:param protectedType: The protected type.
		"""

	def VisitProtectedTypeBody(self, body: ProtectedTypeBody) -> None:
		"""
		Visit a protected type body, before its first declared item.

		:param body: The protected type body.
		"""

	def DepartProtectedTypeBody(self, body: ProtectedTypeBody) -> None:
		"""
		Depart from a protected type body, after its last declared item.

		:param body: The protected type body.
		"""

	def VisitPortMapAspect(self, element: PortMapAspectMixin) -> None:
		"""
		Visit the port map aspect of an element, before its first association.

		:param element: The element with a port map aspect.
		"""

	def DepartPortMapAspect(self, element: PortMapAspectMixin) -> None:
		"""
		Depart from the port map aspect of an element, after its last association.

		:param element: The element with a port map aspect.
		"""

	def VisitContextClause(self, designUnit: DesignUnit) -> None:
		"""
		Visit the context clause of a design unit, before its first context item.

		:param designUnit: The design unit.
		"""

	def DepartContextClause(self, designUnit: DesignUnit) -> None:
		"""
		Depart from the context clause of a design unit, after its last context item.

		:param designUnit: The design unit.
		"""

	def VisitInstantiationList(self, configuration: ComponentConfiguration) -> None:
		"""
		Visit the instantiation list of a component configuration, before its first label.

		:param configuration: The component configuration.
		"""

	def DepartInstantiationList(self, configuration: ComponentConfiguration) -> None:
		"""
		Depart from the instantiation list of a component configuration, after its last label.

		:param configuration: The component configuration.
		"""

	def VisitBlockSpecification(self, configuration: BlockConfiguration) -> None:
		"""
		Visit the block specification of a block configuration, before its block name.

		:param configuration: The block configuration.
		"""

	def DepartBlockSpecification(self, configuration: BlockConfiguration) -> None:
		"""
		Depart from the block specification of a block configuration, after its block name.

		:param configuration: The block configuration.
		"""

	def VisitLibraryClause(self, clause: LibraryClause) -> None:
		"""
		Visit a library clause, before its first library name.

		:param clause: The library clause.
		"""

	def DepartLibraryClause(self, clause: LibraryClause) -> None:
		"""
		Depart from a library clause, after its last library name.

		:param clause: The library clause.
		"""

	def VisitUseClause(self, clause: UseClause) -> None:
		"""
		Visit a use clause, before its first selected name.

		:param clause: The use clause.
		"""

	def DepartUseClause(self, clause: UseClause) -> None:
		"""
		Depart from a use clause, after its last selected name.

		:param clause: The use clause.
		"""

	def VisitContextReference(self, reference: ContextReference) -> None:
		"""
		Visit a context reference, before its first context name.

		:param reference: The context reference.
		"""

	def DepartContextReference(self, reference: ContextReference) -> None:
		"""
		Depart from a context reference, after its last context name.

		:param reference: The context reference.
		"""

	def VisitContext(self, context: Context) -> None:
		"""
		Visit a context declaration, before its first context item.

		:param context: The context declaration.
		"""

	def DepartContext(self, context: Context) -> None:
		"""
		Depart from a context declaration, after its last context item.

		:param context: The context declaration.
		"""

	def VisitPackage(self, package: Package) -> None:
		"""
		Visit a package declaration, before its generic clause.

		:param package: The package declaration.
		"""

	def DepartPackage(self, package: Package) -> None:
		"""
		Depart from a package declaration, after its last declared item.

		:param package: The package declaration.
		"""

	def VisitPackageBody(self, body: PackageBody) -> None:
		"""
		Visit a package body, before its first declared item.

		:param body: The package body.
		"""

	def DepartPackageBody(self, body: PackageBody) -> None:
		"""
		Depart from a package body, after its last declared item.

		:param body: The package body.
		"""

	def VisitPackageInstantiation(self, instantiation: PackageInstantiation) -> None:
		"""
		Visit a package instantiation, before its generic package.

		:param instantiation: The package instantiation.
		"""

	def DepartPackageInstantiation(self, instantiation: PackageInstantiation) -> None:
		"""
		Depart from a package instantiation, after its generic map aspect.

		:param instantiation: The package instantiation.
		"""

	def VisitEntity(self, entity: Entity) -> None:
		"""
		Visit an entity declaration, before its generic clause.

		:param entity: The entity declaration.
		"""

	def DepartEntity(self, entity: Entity) -> None:
		"""
		Depart from an entity declaration, after its last statement.

		:param entity: The entity declaration.
		"""

	def VisitArchitecture(self, architecture: Architecture) -> None:
		"""
		Visit an architecture body, before its entity name.

		:param architecture: The architecture body.
		"""

	def DepartArchitecture(self, architecture: Architecture) -> None:
		"""
		Depart from an architecture body, after its last statement.

		:param architecture: The architecture body.
		"""

	def VisitConfiguration(self, configuration: Configuration) -> None:
		"""
		Visit a configuration declaration, before its entity name.

		:param configuration: The configuration declaration.
		"""

	def DepartConfiguration(self, configuration: Configuration) -> None:
		"""
		Depart from a configuration declaration, after its block configuration.

		:param configuration: The configuration declaration.
		"""

	def VisitBlockConfiguration(self, configuration: BlockConfiguration) -> None:
		"""
		Visit a block configuration, before its block specification.

		:param configuration: The block configuration.
		"""

	def DepartBlockConfiguration(self, configuration: BlockConfiguration) -> None:
		"""
		Depart from a block configuration, after its last nested configuration.

		:param configuration: The block configuration.
		"""

	def VisitComponentConfiguration(self, configuration: ComponentConfiguration) -> None:
		"""
		Visit a component configuration, before its instantiation list.

		:param configuration: The component configuration.
		"""

	def DepartComponentConfiguration(self, configuration: ComponentConfiguration) -> None:
		"""
		Depart from a component configuration, after its binding indication.

		:param configuration: The component configuration.
		"""

	def VisitBindingIndication(self, indication: BindingIndication) -> None:
		"""
		Visit a binding indication, before its entity aspect.

		:param indication: The binding indication.
		"""

	def DepartBindingIndication(self, indication: BindingIndication) -> None:
		"""
		Depart from a binding indication, after its port map aspect.

		:param indication: The binding indication.
		"""

	def VisitEntityAspectEntity(self, aspect: EntityAspectEntity) -> None:
		"""
		Visit an entity aspect naming an entity, before its entity name.

		:param aspect: The entity aspect.
		"""

	def DepartEntityAspectEntity(self, aspect: EntityAspectEntity) -> None:
		"""
		Depart from an entity aspect naming an entity, after its architecture name.

		:param aspect: The entity aspect.
		"""

	def VisitEntityAspectConfiguration(self, aspect: EntityAspectConfiguration) -> None:
		"""
		Visit an entity aspect naming a configuration, before its configuration name.

		:param aspect: The entity aspect.
		"""

	def DepartEntityAspectConfiguration(self, aspect: EntityAspectConfiguration) -> None:
		"""
		Depart from an entity aspect naming a configuration, after its configuration name.

		:param aspect: The entity aspect.
		"""

	def VisitEntityAspectOpen(self, aspect: EntityAspectOpen) -> None:
		"""
		Visit an open entity aspect.

		:param aspect: The entity aspect.
		"""

	def DepartEntityAspectOpen(self, aspect: EntityAspectOpen) -> None:
		"""
		Depart from an open entity aspect.

		:param aspect: The entity aspect.
		"""

	def VisitAllInstantiationList(self, instantiationList: AllInstantiationList) -> None:
		"""
		Visit an ``all`` instantiation list.

		:param instantiationList: The instantiation list.
		"""

	def DepartAllInstantiationList(self, instantiationList: AllInstantiationList) -> None:
		"""
		Depart from an ``all`` instantiation list.

		:param instantiationList: The instantiation list.
		"""

	def VisitOthersInstantiationList(self, instantiationList: OthersInstantiationList) -> None:
		"""
		Visit an ``others`` instantiation list.

		:param instantiationList: The instantiation list.
		"""

	def DepartOthersInstantiationList(self, instantiationList: OthersInstantiationList) -> None:
		"""
		Depart from an ``others`` instantiation list.

		:param instantiationList: The instantiation list.
		"""

	def VisitDocument(self, document: Document) -> None:
		"""
		Visit a document, before its first design unit.

		:param document: The document.
		"""

	def DepartDocument(self, document: Document) -> None:
		"""
		Depart from a document, after its last design unit.

		:param document: The document.
		"""

	def VisitSensitivityList(self, process: ProcessStatement) -> None:
		"""
		Visit the sensitivity list of a process, before its first name.

		:param process: The process.
		"""

	def DepartSensitivityList(self, process: ProcessStatement) -> None:
		"""
		Depart from the sensitivity list of a process, after its last name.

		:param process: The process.
		"""

	def VisitActualParameterPart(self, call: ProcedureCallMixin) -> None:
		"""
		Visit the actual parameter part of a procedure call, before its first association.

		:param call: The procedure call.
		"""

	def DepartActualParameterPart(self, call: ProcedureCallMixin) -> None:
		"""
		Depart from the actual parameter part of a procedure call, after its last association.

		:param call: The procedure call.
		"""

	def VisitWaveformElement(self, element: WaveformElement) -> None:
		"""
		Visit a waveform element, before its value.

		:param element: The waveform element.
		"""

	def DepartWaveformElement(self, element: WaveformElement) -> None:
		"""
		Depart from a waveform element, after its delay.

		:param element: The waveform element.
		"""

	def VisitConditionalWaveform(self, waveform: ConditionalWaveform) -> None:
		"""
		Visit a conditional waveform, before its waveform.

		:param waveform: The conditional waveform.
		"""

	def DepartConditionalWaveform(self, waveform: ConditionalWaveform) -> None:
		"""
		Depart from a conditional waveform, after its condition.

		:param waveform: The conditional waveform.
		"""

	def VisitSelectedWaveform(self, waveform: SelectedWaveform) -> None:
		"""
		Visit a selected waveform, before its waveform.

		:param waveform: The selected waveform.
		"""

	def DepartSelectedWaveform(self, waveform: SelectedWaveform) -> None:
		"""
		Depart from a selected waveform, after its last choice.

		:param waveform: The selected waveform.
		"""

	def VisitOthersSelectedWaveform(self, waveform: OthersSelectedWaveform) -> None:
		"""
		Visit the ``others`` selected waveform, before its waveform.

		:param waveform: The selected waveform.
		"""

	def DepartOthersSelectedWaveform(self, waveform: OthersSelectedWaveform) -> None:
		"""
		Depart from the ``others`` selected waveform, after its waveform.

		:param waveform: The selected waveform.
		"""

	def VisitIndexedChoice(self, choice: IndexedChoice) -> None:
		"""
		Visit a choice given by a value, before its value.

		:param choice: The choice.
		"""

	def DepartIndexedChoice(self, choice: IndexedChoice) -> None:
		"""
		Depart from a choice given by a value, after its value.

		:param choice: The choice.
		"""

	def VisitRangedChoice(self, choice: RangedChoice) -> None:
		"""
		Visit a choice given by a range, before its range.

		:param choice: The choice.
		"""

	def DepartRangedChoice(self, choice: RangedChoice) -> None:
		"""
		Depart from a choice given by a range, after its range.

		:param choice: The choice.
		"""

	def VisitProcessStatement(self, process: ProcessStatement) -> None:
		"""
		Visit a process statement, before its sensitivity list.

		:param process: The process.
		"""

	def DepartProcessStatement(self, process: ProcessStatement) -> None:
		"""
		Depart from a process statement, after its last statement.

		:param process: The process.
		"""

	def VisitConcurrentProcedureCall(self, call: ConcurrentProcedureCall) -> None:
		"""
		Visit a concurrent procedure call, before its procedure.

		:param call: The procedure call.
		"""

	def DepartConcurrentProcedureCall(self, call: ConcurrentProcedureCall) -> None:
		"""
		Depart from a concurrent procedure call, after its parameters.

		:param call: The procedure call.
		"""

	def VisitConcurrentSimpleSignalAssignment(self, assignment: ConcurrentSimpleSignalAssignment) -> None:
		"""
		Visit a concurrent simple signal assignment, before its target.

		:param assignment: The signal assignment.
		"""

	def DepartConcurrentSimpleSignalAssignment(self, assignment: ConcurrentSimpleSignalAssignment) -> None:
		"""
		Depart from a concurrent simple signal assignment, after its waveform.

		:param assignment: The signal assignment.
		"""

	def VisitConcurrentSelectedSignalAssignment(self, assignment: ConcurrentSelectedSignalAssignment) -> None:
		"""
		Visit a concurrent selected signal assignment, before its selector.

		:param assignment: The signal assignment.
		"""

	def DepartConcurrentSelectedSignalAssignment(self, assignment: ConcurrentSelectedSignalAssignment) -> None:
		"""
		Depart from a concurrent selected signal assignment, after its last alternative.

		:param assignment: The signal assignment.
		"""

	def VisitConcurrentConditionalSignalAssignment(self, assignment: ConcurrentConditionalSignalAssignment) -> None:
		"""
		Visit a concurrent conditional signal assignment, before its target.

		:param assignment: The signal assignment.
		"""

	def DepartConcurrentConditionalSignalAssignment(self, assignment: ConcurrentConditionalSignalAssignment) -> None:
		"""
		Depart from a concurrent conditional signal assignment, after its last alternative.

		:param assignment: The signal assignment.
		"""

	def VisitConcurrentAssertStatement(self, assertion: ConcurrentAssertStatement) -> None:
		"""
		Visit a concurrent assertion, before its condition.

		:param assertion: The assertion.
		"""

	def DepartConcurrentAssertStatement(self, assertion: ConcurrentAssertStatement) -> None:
		"""
		Depart from a concurrent assertion, after its severity.

		:param assertion: The assertion.
		"""
