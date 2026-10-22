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
This module contains a writer, which formats a VHDL language model as VHDL source text.

The writer is a :class:`~pyVHDLModel.Visitor.Visitor`: a model element walks itself and the writer appends the VHDL
source text of each event to a buffer. A parser's subclass of a model class (e.g. from ``pyGHDL.dom``) is written like
that model class. Writing is a re-format: comments, blank lines and the letter case of reserved words in a parsed source
are not preserved.
"""
from __future__              import annotations

from enum                    import Enum, unique
from math                    import copysign, isfinite
from typing                  import ClassVar, Optional as Nullable

from pyTooling.Common        import getFullyQualifiedName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Association import AssociationItem
from pyVHDLModel.Base        import ModelElementUnion, ModelEntity, Direction, Mode, SimpleRange, RangeFromName
from pyVHDLModel.Declaration import EntityClass, Attribute, AttributeSpecification, Alias
from pyVHDLModel.DesignUnit  import Component
from pyVHDLModel.Exception   import VHDLWriterError
from pyVHDLModel.Expression  import (
	OperatorPrecedence, NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral,
	PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BitStringBase,
	BitStringLiteral, UnaryExpression, NegationExpression, IdentityExpression, TypeConversion, SubExpression,
	BinaryExpression, RangeExpression, AddingExpression, MultiplyingExpression, ExponentiationExpression,
	LogicalExpression, AndExpression, OrExpression, XorExpression, XnorExpression, RelationalExpression,
	ShiftExpression, QualifiedExpression, WhenElseExpression, SubtypeAllocation, QualifiedExpressionAllocation,
	SimpleAggregateElement, IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement,
	OthersAggregateElement, Aggregate
)
from pyVHDLModel.Name        import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, AttributeName
from pyVHDLModel.Interface   import (
	ModeViewDeclaration, SimpleModeViewElement, CompositeModeViewElement, GenericConstantInterfaceItem,
	GenericTypeInterfaceItem, PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem,
	ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, ParameterSimpleSignalInterfaceItem,
	ParameterViewSignalInterfaceItem, ParameterFileInterfaceItem
)
from pyVHDLModel.Name        import AllName, OpenName
from pyVHDLModel.Object      import Obj, WithDefaultExpressionMixin, Constant, DeferredConstant, Variable
from pyVHDLModel.Object      import SharedVariable, Signal, File
from pyVHDLModel.Regions     import WithGenericsMixin, WithPortsMixin
from pyVHDLModel.Symbol      import (
	Symbol, ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, ConstrainedRecordSubtypeSymbol
)
from pyVHDLModel.Type        import (
	AnonymousType, FullType, Subtype, EnumeratedType, IntegerType, RealType, PhysicalType, ArrayType, RecordTypeElement,
	RecordType, AccessType, FileType
)
from pyVHDLModel.Visitor     import Visitor


@export
@unique
class KeywordCase(Enum):
	"""
	An enumeration of letter cases for VHDL reserved words in the written source text.
	"""

	Lower = 0  #: Lower case, e.g. ``downto``.
	Upper = 1  #: Upper case, e.g. ``DOWNTO``.


@export
@unique
class IndentStyle(Enum):
	"""
	An enumeration of indentation styles of the written source text, as vhdl-style-guide's option ``indent_style``.
	"""

	Spaces =    0  #: Spaces, ``indent_size`` per indentation level (VSG: ``spaces``).
	SmartTabs = 1  #: One tab per indentation level (VSG: ``smart_tabs`` - tabs indent, spaces align).


@export
class VHDLStyle(metaclass=ExtendedType, slots=True):
	"""
	Represents the formatting options of the :class:`VHDL writer <VHDLWriter>`.
	"""

	_keywordCase: KeywordCase  #: Letter case of reserved words.
	_indentStyle: IndentStyle  #: Indentation style.
	_indentSize:  int          #: Number of spaces per indentation level.

	def __init__(
		self,
		keywordCase: KeywordCase = KeywordCase.Lower,
		indentStyle: IndentStyle = IndentStyle.Spaces,
		indentSize:  int =         2
	) -> None:
		"""
		Initializes the formatting options.

		:param keywordCase: Optional, letter case of reserved words. Default: ``KeywordCase.Lower``.
		:param indentStyle: Optional, indentation style. Default: ``IndentStyle.Spaces``.
		:param indentSize:  Optional, number of spaces per indentation level. Default: ``2``.
		:raises ValueError: If parameter 'keywordCase' is None.
		:raises TypeError:  If parameter 'keywordCase' is not of type :class:`KeywordCase`.
		:raises ValueError: If parameter 'indentStyle' is None.
		:raises TypeError:  If parameter 'indentStyle' is not of type :class:`IndentStyle`.
		:raises ValueError: If parameter 'indentSize' is None.
		:raises TypeError:  If parameter 'indentSize' is not of type :class:`int`.
		:raises ValueError: If parameter 'indentSize' is less than 1.
		"""
		if keywordCase is None:
			raise ValueError("Parameter 'keywordCase' is None.")
		elif not isinstance(keywordCase, KeywordCase):
			ex = TypeError("Parameter 'keywordCase' is not of type 'KeywordCase'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(keywordCase)}'.")
			raise ex

		if indentStyle is None:
			raise ValueError("Parameter 'indentStyle' is None.")
		elif not isinstance(indentStyle, IndentStyle):
			ex = TypeError("Parameter 'indentStyle' is not of type 'IndentStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(indentStyle)}'.")
			raise ex

		if indentSize is None:
			raise ValueError("Parameter 'indentSize' is None.")
		elif not isinstance(indentSize, int) or isinstance(indentSize, bool):
			ex = TypeError("Parameter 'indentSize' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(indentSize)}'.")
			raise ex
		elif indentSize < 1:
			ex = ValueError("Parameter 'indentSize' is less than 1.")
			ex.add_note(f"Got value '{indentSize}'.")
			raise ex

		self._keywordCase = keywordCase
		self._indentStyle = indentStyle
		self._indentSize =  indentSize

	@readonly
	def KeywordCase(self) -> KeywordCase:
		"""
		Read-only property to access the letter case of reserved words (:attr:`_keywordCase`).

		:returns: The letter case of reserved words.
		"""
		return self._keywordCase

	@readonly
	def IndentStyle(self) -> IndentStyle:
		"""
		Read-only property to access the indentation style (:attr:`_indentStyle`).

		:returns: The indentation style.
		"""
		return self._indentStyle

	@readonly
	def IndentSize(self) -> int:
		"""
		Read-only property to access the number of spaces per indentation level (:attr:`_indentSize`).

		:returns: The number of spaces per indentation level.
		"""
		return self._indentSize




@export
class VHDLWriter(Visitor):
	"""
	A writer formatting VHDL language model elements as VHDL source text.

	The writer handles the :mod:`visitor events <pyVHDLModel.Visitor>` of each supported model class. An element of a
	class without a walk of its own raises :exc:`NotImplementedError`; nothing is skipped.

	Expressions are written with the parentheses VHDL's operator precedence requires (IEEE Std 1076-2008, clause 9.2).
	Parentheses from the source (:class:`~pyVHDLModel.Expression.SubExpression`) are kept. Symbols are written from their
	:attr:`~pyVHDLModel.Symbol.Symbol.Name`, whether resolved or not.
	"""

	_BASE_SPECIFIERS: ClassVar[dict[BitStringBase, str]] = {
		BitStringBase.Binary:      "b",
		BitStringBase.Octal:       "o",
		BitStringBase.Decimal:     "d",
		BitStringBase.Hexadecimal: "x",
	}  #: Dictionary of base specifiers, indexed by bit string base.

	_style:       VHDLStyle                              #: Formatting options.
	_buffer:      list[str]                              #: Fragments of the VHDL source text written by :meth:`Format`.
	_minimum:     OperatorPrecedence                     #: Loosest precedence of the next operand without parentheses.
	_frames:      list[tuple[OperatorPrecedence, bool]]  #: Stack of entered operands: precedence and if in parentheses.
	_indentation: int                                    #: Indentation level of the next line.

	def __init__(self, style: Nullable[VHDLStyle] = None) -> None:
		"""
		Initializes a VHDL writer.

		:param style:      Optional, formatting options. Default: ``VHDLStyle()``.
		:raises TypeError: If parameter 'style' is not of type :class:`VHDLStyle`.
		"""
		super().__init__()

		if style is None:
			style = VHDLStyle()
		elif not isinstance(style, VHDLStyle):
			ex = TypeError("Parameter 'style' is not of type 'VHDLStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(style)}'.")
			raise ex

		self._style =       style
		self._buffer =      []
		self._minimum =     OperatorPrecedence.Range
		self._frames =      []
		self._indentation = 0

	@readonly
	def Style(self) -> VHDLStyle:
		"""
		Read-only property to access the formatting options (:attr:`_style`).

		:returns: The formatting options.
		"""
		return self._style

	def Format(self, element: ModelElementUnion) -> str:
		"""
		Format a model element as VHDL source text.

		Each call starts with an empty buffer at indentation level 0. A declaration, a statement or a design unit ends with
		a newline.

		:param element:              The model element to format.
		:returns:                    The VHDL source text.
		:raises ValueError:          If parameter 'element' is None.
		:raises TypeError:           If parameter 'element' is not of type :class:`~pyVHDLModel.Base.ModelEntity` or
		                             :class:`~pyVHDLModel.Symbol.Symbol`.
		:raises NotImplementedError: If the class of the element or of one of its children has no walk of its own.
		:raises VHDLWriterError:     If the element or one of its children has no VHDL notation.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, (ModelEntity, Symbol)):
			ex = TypeError("Parameter 'element' is not of type 'ModelEntity' or 'Symbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		self._buffer =      []
		self._minimum =     OperatorPrecedence.Range
		self._frames =      []
		self._indentation = 0
		element.Visit(self)
		return "".join(self._buffer)

	def VisitLeftParenthesis(self, element: IndexedName | ParenthesisName | TypeConversion) -> None:
		"""
		Write the left parenthesis opening a parenthesized list.

		:param element: The element enclosing the list.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def _Write(self, text: str) -> None:
		"""
		Append VHDL source text to the buffer.

		:param text: The VHDL source text.
		"""
		self._buffer.append(text)

	def VisitComma(
		self,
		element: IndexedName | ParenthesisName | Aggregate | ConstrainedArraySubtypeSymbol |
		         ConstrainedRecordSubtypeSymbol | EnumeratedType | ArrayType | AttributeSpecification
	) -> None:
		"""
		Write the comma between two items of a list.

		:param element: The element containing the list.
		"""
		self._Write(", ")
		self._minimum = OperatorPrecedence.Range

	def VisitArrow(
		self,
		element: AssociationItem | IndexedAggregateElement | RangedAggregateElement | NamedAggregateElement
	) -> None:
		"""
		Write the arrow (``=>``) between a choice or formal and its value.

		:param element: The element containing the arrow.
		"""
		self._Write(" => ")
		self._minimum = OperatorPrecedence.Range

	def VisitApostrophe(self, expression: QualifiedExpression) -> None:
		"""
		Write the apostrophe of a qualified expression and, unless the operand brings its own, a left parenthesis.

		An aggregate or a parenthesized sub-expression brings its own parentheses.

		:param expression: The qualified expression.
		"""
		if isinstance(expression.Operand, (Aggregate, SubExpression)):
			self._Write("'")
		else:
			self._Write("'(")

		self._minimum = OperatorPrecedence.Range

	def VisitWhen(self, expression: WhenElseExpression) -> None:
		"""
		Write the reserved word ``when`` of a conditional expression.

		:param expression: The conditional expression.
		"""
		self._Write(f" {self._Keyword('when')} ")
		self._minimum = OperatorPrecedence.Logical

	def _Keyword(self, word: str) -> str:
		"""
		Apply the keyword case of the formatting options to a reserved word.

		:param word: The reserved word in lower case.
		:returns:    The reserved word in the configured letter case.
		"""
		if self._style.KeywordCase is KeywordCase.Upper:
			return word.upper()

		return word

	def VisitElse(self, expression: WhenElseExpression) -> None:
		"""
		Write the reserved word ``else`` of a conditional expression.

		:param expression: The conditional expression.
		"""
		self._Write(f" {self._Keyword('else')} ")
		self._minimum = OperatorPrecedence.Conditional

	def VisitOperator(self, expression: BinaryExpression) -> None:
		"""
		Write the operator of a binary expression.

		The right operand binds tighter than the operator, unless it's a primary.

		:param expression: The binary expression.
		"""
		precedence, _ = self._frames[-1]
		self._Write(f" {self._Keyword(expression._FORMAT[1].strip())} ")
		self._minimum = OperatorPrecedence(min(precedence + 1, OperatorPrecedence.Primary))

	def VisitDirection(self, rng: RangeExpression | SimpleRange) -> None:
		"""
		Write the direction of a range.

		:param rng: The range.
		"""
		direction = "to" if rng.Direction is Direction.To else "downto"
		self._Write(f" {self._Keyword(direction)} ")
		self._minimum = OperatorPrecedence.Adding

	def VisitNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Write a null literal.

		**Format:** ``null``

		:param literal: The null literal.
		"""
		self._Write(self._Keyword("null"))

	def VisitEnumerationLiteral(self, literal: EnumerationLiteral) -> None:
		"""
		Write an enumeration literal.

		**Format:** ``Idle``

		:param literal: The enumeration literal.
		"""
		self._Write(literal.Value)

	def VisitIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Write an integer literal.

		**Format:** ``42``

		A negative value is written with a sign, so it binds like a sign.

		:param literal: The integer literal.
		"""
		self._Enter(OperatorPrecedence.Adding if literal.Value < 0 else OperatorPrecedence.Primary)
		self._Write(str(literal.Value))

	def _Enter(self, precedence: OperatorPrecedence) -> None:
		"""
		Enter an operand and write a left parenthesis, if it binds looser than its position allows.

		:param precedence: The precedence level of the operand.
		"""
		parenthesized = precedence < self._minimum
		if parenthesized:
			self._Write("(")

		self._frames.append((precedence, parenthesized))

	def DepartIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Leave an integer literal.

		:param literal: The integer literal.
		"""
		self._Leave()

	def _Leave(self) -> None:
		"""
		Leave an operand and write a right parenthesis, if it was entered with a left parenthesis.
		"""
		_, parenthesized = self._frames.pop()
		if parenthesized:
			self._Write(")")

	def VisitFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Write a floating-point literal.

		**Format:** ``3.5``

		A negative value is written with a sign, so it binds like a sign.

		:param literal: The floating-point literal.
		"""
		self._Enter(self._PrecedenceOfReal(literal.Value))
		self._Write(self._FormatReal(literal, literal.Value))

	def DepartFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Leave a floating-point literal.

		:param literal: The floating-point literal.
		"""
		self._Leave()

	@staticmethod
	def _PrecedenceOfReal(value: float) -> OperatorPrecedence:
		"""
		Determine how tight a floating-point value binds as an operand.

		A negative value, ``-0.0`` included, is written with a sign, so it binds like a sign.

		:param value: The floating-point value.
		:returns:     The precedence level.
		"""
		if copysign(1.0, value) < 0.0:
			return OperatorPrecedence.Adding

		return OperatorPrecedence.Primary

	def _FormatReal(self, element: ModelEntity, value: float) -> str:
		"""
		Format a floating-point value as VHDL abstract literal with a decimal point.

		**Format:** ``1.0e-09``

		:param element:          The model element carrying the value.
		:param value:            The floating-point value.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If the value is infinite or not a number.
		"""
		if not isfinite(value):
			ex = VHDLWriterError("Floating-point value has no VHDL notation.", element)
			ex.add_note(f"Got value '{value}'.")
			raise ex

		mantissa, separator, exponent = repr(float(value)).partition("e")
		if "." not in mantissa:
			mantissa = f"{mantissa}.0"

		return f"{mantissa}{separator}{exponent}"

	def VisitPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Write a physical literal with an integer value.

		**Format:** ``10 ns``

		:param literal: The physical literal.
		"""
		self._Enter(OperatorPrecedence.Adding if literal.Value < 0 else OperatorPrecedence.Primary)
		self._Write(f"{literal.Value} {literal.UnitName}")

	def DepartPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Leave a physical literal with an integer value.

		:param literal: The physical literal.
		"""
		self._Leave()

	def VisitPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Write a physical literal with a floating-point value.

		**Format:** ``1.5 ns``

		:param literal: The physical literal.
		"""
		self._Enter(self._PrecedenceOfReal(literal.Value))
		self._Write(f"{self._FormatReal(literal, literal.Value)} {literal.UnitName}")

	def DepartPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Leave a physical literal with a floating-point value.

		:param literal: The physical literal.
		"""
		self._Leave()

	def VisitCharacterLiteral(self, literal: CharacterLiteral) -> None:
		"""
		Write a character literal.

		**Format:** ``'a'``

		:param literal:          The character literal.
		:raises VHDLWriterError: If the value is not a single graphic character.
		"""
		if len(literal.Value) != 1 or not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("Character literal is not a single graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		self._Write(f"'{literal.Value}'")

	@staticmethod
	def _IsGraphic(text: str) -> bool:
		"""
		Check if all characters are VHDL graphic characters (ISO/IEC 8859-1 without control characters).

		:param text: The text to check.
		:returns:    ``True``, if all characters are graphic characters.
		"""
		return all(32 <= ord(character) <= 126 or 160 <= ord(character) <= 255 for character in text)

	def VisitStringLiteral(self, literal: StringLiteral) -> None:
		"""
		Write a string literal and double each enclosed quotation mark.

		**Format:** ``"say ""hi"" twice"``

		:param literal:          The string literal.
		:raises VHDLWriterError: If the value contains a non-graphic character.
		"""
		if not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("String literal contains a non-graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		value = literal.Value.replace("\"", "\"\"")
		self._Write(f"\"{value}\"")

	def VisitBitStringLiteral(self, literal: BitStringLiteral) -> None:
		"""
		Write a bit string literal.

		**Format:** ``8ux"A0"``

		:param literal:          The bit string literal.
		:raises VHDLWriterError: If the literal's class has no base specifier.
		:raises VHDLWriterError: If a decimal bit string literal is signed or unsigned.
		:raises VHDLWriterError: If the value contains a quotation mark or a non-graphic character.
		"""
		base = self._BASE_SPECIFIERS.get(literal._BASE)
		if base is None:
			ex = VHDLWriterError("Model element is not supported by the VHDL writer.", literal)
			ex.add_note(f"Got type '{getFullyQualifiedName(literal)}'.")
			raise ex

		if literal.IsSigned is None:
			signedness = ""
		elif literal._BASE is BitStringBase.Decimal:
			raise VHDLWriterError("Decimal bit string literal can't be signed or unsigned.", literal)
		elif literal.IsSigned:
			signedness = "s"
		else:
			signedness = "u"

		if "\"" in literal.Value or not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("Bit string literal contains a quotation mark or a non-graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		length = "" if literal.Length is None else str(literal.Length)
		self._Write(f"{length}{signedness}{base}\"{literal.Value}\"")

	def VisitUnaryExpression(self, expression: UnaryExpression) -> None:
		"""
		Write the operator of a unary expression with a reserved word as operator; its operand is a primary.

		**Format:** ``not (a and b)``

		:param expression: The unary expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._Write(self._Keyword(expression._FORMAT[0]))
		self._minimum = OperatorPrecedence.Primary

	def DepartUnaryExpression(self, expression: UnaryExpression) -> None:
		"""
		Leave a unary expression with a reserved word as operator.

		:param expression: The unary expression.
		"""
		self._Leave()

	def VisitNegationExpression(self, expression: NegationExpression) -> None:
		"""
		Write the sign of a negation; its operand is a term.

		**Format:** ``-a``

		:param expression: The negation.
		"""
		self._Enter(expression._PRECEDENCE)
		self._Write(expression._FORMAT[0])
		self._minimum = OperatorPrecedence.Multiplying

	def DepartNegationExpression(self, expression: NegationExpression) -> None:
		"""
		Leave a negation.

		:param expression: The negation.
		"""
		self._Leave()

	def VisitIdentityExpression(self, expression: IdentityExpression) -> None:
		"""
		Write the sign of an identity; its operand is a term.

		**Format:** ``+a``

		:param expression: The identity.
		"""
		self._Enter(expression._PRECEDENCE)
		self._Write(expression._FORMAT[0])
		self._minimum = OperatorPrecedence.Multiplying

	def DepartIdentityExpression(self, expression: IdentityExpression) -> None:
		"""
		Leave an identity.

		:param expression: The identity.
		"""
		self._Leave()

	def DepartTypeConversion(self, conversion: TypeConversion) -> None:
		"""
		Write the right parenthesis closing the operand of a type conversion.

		**Format:** ``integer(r)``

		:param conversion: The type conversion.
		"""
		self._Write(")")

	def VisitSubExpression(self, expression: SubExpression) -> None:
		"""
		Write the left parenthesis of a parenthesized sub-expression from the source.

		**Format:** ``(a + b)``

		:param expression: The sub-expression.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartSubExpression(self, expression: SubExpression) -> None:
		"""
		Write the right parenthesis of a parenthesized sub-expression from the source.

		:param expression: The sub-expression.
		"""
		self._Write(")")

	def VisitLogicalExpression(self, expression: LogicalExpression) -> None:
		"""
		Enter a binary logical expression; its left operand is a relation or a chain of the same associative operator.

		The associative operators are ``and``, ``or``, ``xor`` and ``xnor``.

		**Format:** ``a and b and c`` or ``(a and b) or c``

		:param expression: The logical expression.
		"""
		self._Enter(expression._PRECEDENCE)
		left = expression.LeftOperand
		if any(
			isinstance(expression, operator) and isinstance(left, operator)
			for operator in (AndExpression, OrExpression, XorExpression, XnorExpression)
		):
			self._minimum = OperatorPrecedence.Logical
		else:
			self._minimum = OperatorPrecedence.Relational

	def DepartLogicalExpression(self, expression: LogicalExpression) -> None:
		"""
		Leave a binary logical expression.

		:param expression: The logical expression.
		"""
		self._Leave()

	def VisitRelationalExpression(self, expression: RelationalExpression) -> None:
		"""
		Enter a relational expression; its left operand is a shift expression.

		**Format:** ``a = b``

		:param expression: The relational expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Shift

	def DepartRelationalExpression(self, expression: RelationalExpression) -> None:
		"""
		Leave a relational expression.

		:param expression: The relational expression.
		"""
		self._Leave()

	def VisitShiftExpression(self, expression: ShiftExpression) -> None:
		"""
		Enter a shift or rotate expression; its left operand is a simple expression.

		**Format:** ``a sll 2``

		:param expression: The shift or rotate expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Adding

	def DepartShiftExpression(self, expression: ShiftExpression) -> None:
		"""
		Leave a shift or rotate expression.

		:param expression: The shift or rotate expression.
		"""
		self._Leave()

	def VisitAddingExpression(self, expression: AddingExpression) -> None:
		"""
		Enter an adding expression; it associates to the left.

		**Format:** ``a - b - c`` or ``a - (b - c)``

		:param expression: The adding expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Adding

	def DepartAddingExpression(self, expression: AddingExpression) -> None:
		"""
		Leave an adding expression.

		:param expression: The adding expression.
		"""
		self._Leave()

	def VisitMultiplyingExpression(self, expression: MultiplyingExpression) -> None:
		"""
		Enter a multiplying expression; it associates to the left.

		**Format:** ``(a + b) * c``

		:param expression: The multiplying expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Multiplying

	def DepartMultiplyingExpression(self, expression: MultiplyingExpression) -> None:
		"""
		Leave a multiplying expression.

		:param expression: The multiplying expression.
		"""
		self._Leave()

	def VisitExponentiationExpression(self, expression: ExponentiationExpression) -> None:
		"""
		Enter an exponentiation; both operands are primaries.

		**Format:** ``a ** (b ** c)``

		:param expression: The exponentiation.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Primary

	def DepartExponentiationExpression(self, expression: ExponentiationExpression) -> None:
		"""
		Leave an exponentiation.

		:param expression: The exponentiation.
		"""
		self._Leave()

	def VisitRangeExpression(self, expression: RangeExpression) -> None:
		"""
		Enter a range expression; its bounds are simple expressions.

		**Format:** ``7 downto 0``

		:param expression: The range expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Adding

	def DepartRangeExpression(self, expression: RangeExpression) -> None:
		"""
		Leave a range expression.

		:param expression: The range expression.
		"""
		self._Leave()

	def VisitWhenElseExpression(self, expression: WhenElseExpression) -> None:
		"""
		Enter a conditional expression; its value and condition are logical expressions.

		**Format:** ``a when c else b``

		:param expression: The conditional expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Logical

	def DepartWhenElseExpression(self, expression: WhenElseExpression) -> None:
		"""
		Leave a conditional expression.

		:param expression: The conditional expression.
		"""
		self._Leave()

	def DepartQualifiedExpression(self, expression: QualifiedExpression) -> None:
		"""
		Write the right parenthesis closing the operand of a qualified expression, unless the operand brings its own.

		**Format:** ``byte'(others => '0')``

		:param expression: The qualified expression.
		"""
		if not isinstance(expression.Operand, (Aggregate, SubExpression)):
			self._Write(")")

	def VisitSubtypeAllocation(self, allocation: SubtypeAllocation) -> None:
		"""
		Write the reserved word ``new`` of an allocation of a subtype.

		**Format:** ``new node``

		:param allocation: The allocation.
		"""
		self._Write(f"{self._Keyword('new')} ")

	def VisitQualifiedExpressionAllocation(self, allocation: QualifiedExpressionAllocation) -> None:
		"""
		Write the reserved word ``new`` of an allocation initialized by a qualified expression.

		**Format:** ``new integer'(5)``

		:param allocation: The allocation.
		"""
		self._Write(f"{self._Keyword('new')} ")

	def VisitAggregate(self, aggregate: Aggregate) -> None:
		"""
		Write the left parenthesis of an aggregate.

		**Format:** ``(0 => '1', others => '0')``

		:param aggregate:        The aggregate.
		:raises VHDLWriterError: If the aggregate has no elements.
		:raises VHDLWriterError: If the aggregate has a single positional element (it would read as parentheses). |br|
		                         Use a named element, e.g. ``others => value``.
		"""
		elements = aggregate.Elements
		if len(elements) == 0:
			raise VHDLWriterError("Aggregate has no elements.", aggregate)
		elif len(elements) == 1 and isinstance(elements[0], SimpleAggregateElement):
			ex = VHDLWriterError("Aggregate with a single positional element has no VHDL notation.", aggregate)
			ex.add_note("Use a named element, e.g. 'others => value'.")
			raise ex

		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartAggregate(self, aggregate: Aggregate) -> None:
		"""
		Write the right parenthesis of an aggregate.

		:param aggregate: The aggregate.
		"""
		self._Write(")")

	def VisitIndexedAggregateElement(self, element: IndexedAggregateElement) -> None:
		"""
		Enter an aggregate element chosen by an index; the index is a simple expression.

		**Format:** ``0 => '1'``

		:param element: The aggregate element.
		"""
		self._minimum = OperatorPrecedence.Adding

	def VisitOthersAggregateElement(self, element: OthersAggregateElement) -> None:
		"""
		Write the choice ``others`` of an aggregate element.

		**Format:** ``others => '0'``

		:param element: The aggregate element.
		"""
		self._Write(f"{self._Keyword('others')} => ")
		self._minimum = OperatorPrecedence.Range

	def VisitSimpleRange(self, rng: SimpleRange) -> None:
		"""
		Enter a range given by its bounds; its bounds are simple expressions.

		**Format:** ``0 to 7``

		:param rng: The range.
		"""
		self._Enter(OperatorPrecedence.Range)
		self._minimum = OperatorPrecedence.Adding

	def DepartSimpleRange(self, rng: SimpleRange) -> None:
		"""
		Leave a range given by its bounds.

		:param rng: The range.
		"""
		self._Leave()

	def VisitRangeFromName(self, rng: RangeFromName) -> None:
		"""
		Enter a range denoted by a name.

		**Format:** ``v'range``

		:param rng: The range.
		"""
		self._Enter(OperatorPrecedence.Range)

	def DepartRangeFromName(self, rng: RangeFromName) -> None:
		"""
		Leave a range denoted by a name.

		:param rng: The range.
		"""
		self._Leave()

	def VisitSimpleName(self, name: SimpleName) -> None:
		"""
		Write a simple name.

		**Format:** ``clk``

		:param name: The simple name.
		"""
		self._Write(name.Identifier)

	def DepartSelectedName(self, name: SelectedName) -> None:
		"""
		Write the suffix of a selected name after its prefix.

		**Format:** ``ieee.numeric_std``

		:param name: The selected name.
		"""
		self._Write(f".{name.Identifier}")

	def DepartAllName(self, name: AllName) -> None:
		"""
		Write the suffix ``all`` of a selected name after its prefix.

		**Format:** ``ieee.numeric_std.all``

		:param name: The ``all`` name.
		"""
		self._Write(f".{self._Keyword('all')}")

	def DepartAttributeName(self, name: AttributeName) -> None:
		"""
		Write the attribute designator of an attribute name after its prefix.

		**Format:** ``v'range``

		:param name: The attribute name.
		"""
		self._Write(f"'{name.Identifier}")

	def DepartIndexedName(self, name: IndexedName) -> None:
		"""
		Write the right parenthesis closing the indices of an indexed name.

		**Format:** ``m(i, j)``

		:param name: The indexed name.
		"""
		self._Write(")")

	def DepartParenthesisName(self, name: ParenthesisName) -> None:
		"""
		Write the right parenthesis closing the associations of a parenthesis name (index, slice or function call).

		**Format:** ``resize(a, 8)``

		:param name: The parenthesis name.
		"""
		self._Write(")")

	def VisitSlicedName(self, name: SlicedName) -> None:
		"""
		Reject a sliced name, because it carries no discrete range.

		:param name:             The sliced name.
		:raises VHDLWriterError: Always, because a sliced name carries no discrete range. |br|
		                         Use a :class:`~pyVHDLModel.Name.ParenthesisName` with a range expression as association.
		"""
		ex = VHDLWriterError("Sliced name carries no discrete range.", name)
		ex.add_note("Use a 'ParenthesisName' with a range expression as association.")
		raise ex

	def VisitOpenName(self, name: OpenName) -> None:
		"""
		Write the reserved word ``open``.

		**Format:** ``open``

		:param name: The ``open`` name.
		"""
		self._Write(self._Keyword("open"))

	def VisitAssociationItem(self, item: AssociationItem) -> None:
		"""
		Check an association item before its formal and actual are written.

		**Format:** ``formal => actual`` or ``actual``

		:param item:             The association item.
		:raises VHDLWriterError: If the association item has no actual.
		"""
		if item.Actual is None:
			raise VHDLWriterError("Association item has no actual.", item)

	def VisitSemicolon(self, element: WithGenericsMixin | WithPortsMixin) -> None:
		"""
		Write the semicolon between two items of an interface list; the next item starts on a new line.

		:param element: The element containing the interface list.
		"""
		self._Write(";\n")
		self._WriteIndentation()

	def _WriteIndentation(self) -> None:
		"""
		Write the indentation of the current indentation level.
		"""
		if self._style.IndentStyle is IndentStyle.SmartTabs:
			self._Write("\t" * self._indentation)
		else:
			self._Write(" " * (self._indentation * self._style.IndentSize))

	def VisitVariableAssignment(self, element: WithDefaultExpressionMixin) -> None:
		"""
		Write the variable assignment delimiter (``:=``) before a default expression.

		:param element: The element with the default expression.
		"""
		self._Write(" := ")
		self._minimum = OperatorPrecedence.Range

	def VisitIs(self, element: ModeViewDeclaration | Alias | AttributeSpecification) -> None:
		"""
		Write the reserved word ``is`` ending the header of a declaration; its body is indented.

		In an alias declaration and an attribute specification, the name or the expression follows on the same line.

		:param element: The declaration.
		"""
		if isinstance(element, (Alias, AttributeSpecification)):
			self._Write(f" {self._Keyword('is')} ")
			self._minimum = OperatorPrecedence.Range
		else:
			self._Write(f" {self._Keyword('is')}\n")
			self._indentation += 1

	def VisitRangeConstraint(self, symbol: ConstrainedScalarSubtypeSymbol) -> None:
		"""
		Write the reserved word ``range`` of a range constraint.

		**Format:** ``integer range 0 to 7``

		:param symbol: The constrained subtype symbol.
		"""
		self._Write(f" {self._Keyword('range')} ")
		self._minimum = OperatorPrecedence.Range

	def VisitIndexConstraint(
		self,
		element: ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol | ArrayType
	) -> None:
		"""
		Write the left parenthesis of an index constraint.

		**Format:** ``bit_vector(7 downto 0)``

		:param element: The constrained subtype symbol or the array type.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartIndexConstraint(
		self,
		element: ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol | ArrayType
	) -> None:
		"""
		Write the right parenthesis of an index constraint.

		:param element: The constrained subtype symbol or the array type.
		"""
		self._Write(")")

	def VisitRecordConstraint(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Write the left parenthesis of a record constraint.

		**Format:** ``frame(data(7 downto 0), mask(3 downto 0))``

		:param symbol: The constrained subtype symbol.
		"""
		self._Write("(")

	def DepartRecordConstraint(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Write the right parenthesis of a record constraint.

		:param symbol: The constrained subtype symbol.
		"""
		self._Write(")")

	def VisitGenericClause(self, element: WithGenericsMixin) -> None:
		"""
		Write the reserved word ``generic`` and the left parenthesis of a generic clause; each generic is on its own line.

		**Format:** ``generic (`` ... ``);``

		:param element: The element with generics.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('generic')} (\n")
		self._indentation += 1
		self._WriteIndentation()

	def DepartGenericClause(self, element: WithGenericsMixin) -> None:
		"""
		Write the right parenthesis of a generic clause on its own line.

		:param element: The element with generics.
		"""
		self._WriteClosingParenthesis()

	def _WriteClosingParenthesis(self) -> None:
		"""
		Write the right parenthesis and semicolon closing a generic or port clause on its own line.
		"""
		self._Write("\n")
		self._indentation -= 1
		self._WriteIndentation()
		self._Write(");\n")

	def VisitPortClause(self, element: WithPortsMixin) -> None:
		"""
		Write the reserved word ``port`` and the left parenthesis of a port clause; each port is on its own line.

		**Format:** ``port (`` ... ``);``

		:param element: The element with ports.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('port')} (\n")
		self._indentation += 1
		self._WriteIndentation()

	def DepartPortClause(self, element: WithPortsMixin) -> None:
		"""
		Write the right parenthesis of a port clause on its own line.

		:param element: The element with ports.
		"""
		self._WriteClosingParenthesis()

	def VisitConstant(self, constant: Constant) -> None:
		"""
		Write the reserved word ``constant`` and the identifiers of a constant declaration.

		**Format:** ``constant BITS : positive := 8;``

		:param constant: The constant declaration.
		"""
		self._WriteObjectDeclaration(constant)

	def _WriteObjectDeclaration(self, obj: Obj) -> None:
		"""
		Write the indentation, the object class reserved word and the identifiers of an object declaration.

		:param obj: The object declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(obj._OBJECT_KEYWORD)} {', '.join(obj.Identifiers)} : ")

	def DepartConstant(self, constant: Constant) -> None:
		"""
		Write the semicolon ending a constant declaration.

		:param constant: The constant declaration.
		"""
		self._Write(";\n")

	def VisitDeferredConstant(self, constant: DeferredConstant) -> None:
		"""
		Write the reserved word ``constant`` and the identifiers of a deferred constant declaration.

		**Format:** ``constant BITS : positive;``

		:param constant: The deferred constant declaration.
		"""
		self._WriteObjectDeclaration(constant)

	def DepartDeferredConstant(self, constant: DeferredConstant) -> None:
		"""
		Write the semicolon ending a deferred constant declaration.

		:param constant: The deferred constant declaration.
		"""
		self._Write(";\n")

	def VisitVariable(self, variable: Variable) -> None:
		"""
		Write the reserved word ``variable`` and the identifiers of a variable declaration.

		**Format:** ``variable count : natural := 0;``

		:param variable: The variable declaration.
		"""
		self._WriteObjectDeclaration(variable)

	def DepartVariable(self, variable: Variable) -> None:
		"""
		Write the semicolon ending a variable declaration.

		:param variable: The variable declaration.
		"""
		self._Write(";\n")

	def VisitSharedVariable(self, variable: SharedVariable) -> None:
		"""
		Write the reserved words ``shared variable`` and the identifiers of a shared variable declaration.

		**Format:** ``shared variable counter : counter_t;``

		:param variable: The shared variable declaration.
		"""
		self._WriteObjectDeclaration(variable)

	def DepartSharedVariable(self, variable: SharedVariable) -> None:
		"""
		Write the semicolon ending a shared variable declaration.

		:param variable: The shared variable declaration.
		"""
		self._Write(";\n")

	def VisitSignal(self, signal: Signal) -> None:
		"""
		Write the reserved word ``signal`` and the identifiers of a signal declaration.

		**Format:** ``signal a, b : bit := '0';``

		:param signal: The signal declaration.
		"""
		self._WriteObjectDeclaration(signal)

	def DepartSignal(self, signal: Signal) -> None:
		"""
		Write the semicolon ending a signal declaration.

		:param signal: The signal declaration.
		"""
		self._Write(";\n")

	def VisitFile(self, file: File) -> None:
		"""
		Write the reserved word ``file`` and the identifiers of a file declaration.

		**Format:** ``file input : text;``

		The model carries no file open information, so none is written.

		:param file: The file declaration.
		"""
		self._WriteObjectDeclaration(file)

	def DepartFile(self, file: File) -> None:
		"""
		Write the semicolon ending a file declaration.

		:param file: The file declaration.
		"""
		self._Write(";\n")

	def VisitGenericConstantInterfaceItem(self, item: GenericConstantInterfaceItem) -> None:
		"""
		Write the identifiers and the mode of a generic constant.

		**Format:** ``BITS : positive := 8``

		:param item: The generic constant.
		"""
		self._WriteInterfaceItem(item, "", item.Mode)

	def _WriteInterfaceItem(self, item: Obj, keyword: str, mode: Mode) -> None:
		"""
		Write the object class reserved word (if any), the identifiers and the mode (if any) of an interface item.

		:param item:    The interface item.
		:param keyword: The object class reserved word in lower case, or an empty string.
		:param mode:    The mode; ``Mode.Default`` writes none.
		"""
		if keyword != "":
			self._Write(f"{self._Keyword(keyword)} ")

		self._Write(f"{', '.join(item.Identifiers)} : ")
		if mode is not Mode.Default:
			self._Write(f"{self._Keyword(str(mode))} ")

	def VisitGenericTypeInterfaceItem(self, item: GenericTypeInterfaceItem) -> None:
		"""
		Write a generic type.

		**Format:** ``type T``

		:param item: The generic type.
		"""
		self._Write(f"{self._Keyword('type')} {item.Identifier}")

	def VisitPortSimpleSignalInterfaceItem(self, item: PortSimpleSignalInterfaceItem) -> None:
		"""
		Write the identifiers and the mode of a port.

		**Format:** ``clk : in std_logic``

		:param item: The port.
		"""
		self._WriteInterfaceItem(item, "", item.Mode)

	def VisitPortViewSignalInterfaceItem(self, item: PortViewSignalInterfaceItem) -> None:
		"""
		Write the identifiers and the reserved word ``view`` of a port with a mode view.

		**Format:** ``link : view master``

		:param item: The port.
		"""
		self._WriteInterfaceItem(item, "", Mode.Default)
		self._Write(f"{self._Keyword('view')} ")

	def VisitParameterConstantInterfaceItem(self, item: ParameterConstantInterfaceItem) -> None:
		"""
		Write the reserved word ``constant``, the identifiers and the mode of a constant parameter.

		**Format:** ``constant value : in integer``

		:param item: The constant parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, item.Mode)

	def VisitParameterVariableInterfaceItem(self, item: ParameterVariableInterfaceItem) -> None:
		"""
		Write the reserved word ``variable``, the identifiers and the mode of a variable parameter.

		**Format:** ``variable result : out integer``

		:param item: The variable parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, item.Mode)

	def VisitParameterSimpleSignalInterfaceItem(self, item: ParameterSimpleSignalInterfaceItem) -> None:
		"""
		Write the reserved word ``signal``, the identifiers and the mode of a signal parameter.

		**Format:** ``signal clk : in std_logic``

		:param item: The signal parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, item.Mode)

	def VisitParameterViewSignalInterfaceItem(self, item: ParameterViewSignalInterfaceItem) -> None:
		"""
		Write the reserved word ``signal``, the identifiers and the reserved word ``view`` of a signal parameter.

		**Format:** ``signal link : view master``

		:param item: The signal parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, Mode.Default)
		self._Write(f"{self._Keyword('view')} ")

	def VisitParameterFileInterfaceItem(self, item: ParameterFileInterfaceItem) -> None:
		"""
		Write the reserved word ``file`` and the identifiers of a file parameter.

		**Format:** ``file input : text``

		:param item: The file parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, Mode.Default)

	def VisitModeViewDeclaration(self, declaration: ModeViewDeclaration) -> None:
		"""
		Write the reserved word ``view``, the identifier and the reserved word ``of`` of a mode view declaration.

		**Format:** ``view master of bus_t is`` ... ``end view master;``

		:param declaration: The mode view declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('view')} {declaration.Identifier} {self._Keyword('of')} ")

	def DepartModeViewDeclaration(self, declaration: ModeViewDeclaration) -> None:
		"""
		Write the end of a mode view declaration.

		:param declaration: The mode view declaration.
		"""
		self._WriteEnd("view", declaration.Identifier)

	def _WriteEnd(self, keywords: str, identifier: str) -> None:
		"""
		Leave the indented body and write the reserved word ``end``, the given reserved words and the identifier.

		:param keywords:   The reserved words after ``end`` in lower case.
		:param identifier: The identifier of the declaration.
		"""
		self._indentation -= 1
		self._WriteIndentation()
		self._Write(f"{self._Keyword('end')} {self._Keyword(keywords)} {identifier};\n")

	def VisitSimpleModeViewElement(self, element: SimpleModeViewElement) -> None:
		"""
		Write an element of a mode view with a mode.

		**Format:** ``valid, data : out;``

		:param element:          The mode view element.
		:raises VHDLWriterError: If the mode view element has no mode.
		"""
		if element.Mode is Mode.Default:
			raise VHDLWriterError("Mode view element has no mode.", element)

		self._WriteIndentation()
		self._Write(f"{', '.join(element.Identifiers)} : {self._Keyword(str(element.Mode))};\n")

	def VisitCompositeModeViewElement(self, element: CompositeModeViewElement) -> None:
		"""
		Write the identifiers and the reserved word ``view`` of an element of a mode view with a mode view.

		**Format:** ``request : view master;``

		:param element: The mode view element.
		"""
		self._WriteIndentation()
		self._Write(f"{', '.join(element.Identifiers)} : {self._Keyword('view')} ")

	def DepartCompositeModeViewElement(self, element: CompositeModeViewElement) -> None:
		"""
		Write the semicolon ending an element of a mode view with a mode view.

		:param element: The mode view element.
		"""
		self._Write(";\n")

	def VisitComponent(self, component: Component) -> None:
		"""
		Write the header of a component declaration; its generic and port clauses are indented.

		**Format:** ``component counter is`` ... ``end component counter;``

		:param component: The component declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('component')} {component.Identifier} {self._Keyword('is')}\n")
		self._indentation += 1

	def DepartComponent(self, component: Component) -> None:
		"""
		Write the end of a component declaration.

		:param component: The component declaration.
		"""
		self._WriteEnd("component", component.Identifier)

	def VisitBox(self, arrayType: ArrayType) -> None:
		"""
		Write the reserved word ``range`` and the box (``<>``) of an unbounded index of an array type.

		**Format:** ``natural range <>``

		:param arrayType: The array type.
		"""
		self._Write(f" {self._Keyword('range')} <>")

	def VisitOf(self, arrayType: ArrayType) -> None:
		"""
		Write the reserved word ``of`` before the element subtype of an array type.

		:param arrayType: The array type.
		"""
		self._Write(f" {self._Keyword('of')} ")

	def VisitUnits(self, physicalType: PhysicalType) -> None:
		"""
		Write the reserved word ``units`` and the primary unit of a physical type on their own lines.

		:param physicalType: The physical type.
		"""
		self._Write("\n")
		self._indentation += 1
		self._WriteIndentation()
		self._Write(f"{self._Keyword('units')}\n")
		self._indentation += 1
		self._WriteIndentation()
		self._Write(f"{physicalType.PrimaryUnit};\n")

	def VisitSecondaryUnitDeclaration(self, physicalType: PhysicalType, identifier: str) -> None:
		"""
		Write the identifier of a secondary unit declaration.

		**Format:** ``mm = 1000 um;``

		:param physicalType: The physical type.
		:param identifier:   The identifier of the secondary unit.
		"""
		self._WriteIndentation()
		self._Write(f"{identifier} = ")
		self._minimum = OperatorPrecedence.Range

	def DepartSecondaryUnitDeclaration(self, physicalType: PhysicalType, identifier: str) -> None:
		"""
		Write the semicolon ending a secondary unit declaration.

		:param physicalType: The physical type.
		:param identifier:   The identifier of the secondary unit.
		"""
		self._Write(";\n")

	def VisitEntitySpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the reserved word ``of`` before the names of an attribute specification.

		:param specification: The attribute specification.
		"""
		self._Write(f" {self._Keyword('of')} ")

	def DepartEntitySpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the entity class after the names of an attribute specification.

		:param specification: The attribute specification.
		"""
		self._Write(f" : {self._Keyword(specification.EntityClass.name.lower())}")

	def VisitAnonymousType(self, declaration: AnonymousType) -> None:
		"""
		Write an incomplete type declaration.

		**Format:** ``type node;``

		:param declaration: The incomplete type declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('type')} {declaration.Identifier};\n")

	def VisitSubtype(self, subtype: Subtype) -> None:
		"""
		Write the reserved word ``subtype``, the identifier and the reserved word ``is`` of a subtype declaration.

		**Format:** ``subtype byte is bit_vector(7 downto 0);``

		The model's resolution function of a subtype is not written.

		:param subtype: The subtype declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('subtype')} {subtype.Identifier} {self._Keyword('is')} ")

	def DepartSubtype(self, subtype: Subtype) -> None:
		"""
		Write the semicolon ending a subtype declaration.

		:param subtype: The subtype declaration.
		"""
		self._Write(";\n")

	def VisitEnumeratedType(self, enumeratedType: EnumeratedType) -> None:
		"""
		Write the header and the left parenthesis of an enumerated type declaration.

		**Format:** ``type state is (Idle, Busy, Done);``

		:param enumeratedType: The enumerated type.
		"""
		self._WriteTypeHeader(enumeratedType)
		self._Write("(")

	def _WriteTypeHeader(self, declaration: FullType) -> None:
		"""
		Write the indentation, the reserved word ``type``, the identifier and the reserved word ``is`` of a type.

		:param declaration: The type declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('type')} {declaration.Identifier} {self._Keyword('is')} ")

	def DepartEnumeratedType(self, enumeratedType: EnumeratedType) -> None:
		"""
		Write the right parenthesis ending an enumerated type declaration.

		:param enumeratedType: The enumerated type.
		"""
		self._Write(");\n")

	def VisitIntegerType(self, integerType: IntegerType) -> None:
		"""
		Write the header and the reserved word ``range`` of an integer type declaration.

		**Format:** ``type nibble is range 0 to 15;``

		:param integerType: The integer type.
		"""
		self._WriteTypeHeader(integerType)
		self._Write(f"{self._Keyword('range')} ")
		self._minimum = OperatorPrecedence.Range

	def DepartIntegerType(self, integerType: IntegerType) -> None:
		"""
		Write the semicolon ending an integer type declaration.

		:param integerType: The integer type.
		"""
		self._Write(";\n")

	def VisitRealType(self, realType: RealType) -> None:
		"""
		Write the header and the reserved word ``range`` of a floating-point type declaration.

		**Format:** ``type fraction is range 0.0 to 1.0;``

		:param realType: The floating-point type.
		"""
		self._WriteTypeHeader(realType)
		self._Write(f"{self._Keyword('range')} ")
		self._minimum = OperatorPrecedence.Range

	def DepartRealType(self, realType: RealType) -> None:
		"""
		Write the semicolon ending a floating-point type declaration.

		:param realType: The floating-point type.
		"""
		self._Write(";\n")

	def VisitPhysicalType(self, physicalType: PhysicalType) -> None:
		"""
		Write the header and the reserved word ``range`` of a physical type declaration; its units are indented.

		**Format:** ``type distance is range 0 to 1000000`` ... ``units`` ... ``end units distance;``

		:param physicalType: The physical type.
		"""
		self._WriteTypeHeader(physicalType)
		self._Write(f"{self._Keyword('range')} ")
		self._minimum = OperatorPrecedence.Range

	def DepartPhysicalType(self, physicalType: PhysicalType) -> None:
		"""
		Write the end of the units of a physical type declaration.

		:param physicalType: The physical type.
		"""
		self._WriteEnd("units", physicalType.Identifier)
		self._indentation -= 1

	def VisitArrayType(self, arrayType: ArrayType) -> None:
		"""
		Write the header and the reserved word ``array`` of an array type declaration.

		**Format:** ``type memory is array (0 to 255) of byte;`` or ``type bits is array (natural range <>) of bit;``

		:param arrayType: The array type.
		"""
		self._WriteTypeHeader(arrayType)
		self._Write(f"{self._Keyword('array')} ")

	def DepartArrayType(self, arrayType: ArrayType) -> None:
		"""
		Write the semicolon ending an array type declaration.

		:param arrayType: The array type.
		"""
		self._Write(";\n")

	def VisitRecordType(self, recordType: RecordType) -> None:
		"""
		Write the header of a record type declaration; its element declarations are indented.

		**Format:** ``type frame is record`` ... ``end record frame;``

		:param recordType: The record type.
		"""
		self._WriteTypeHeader(recordType)
		self._Write(f"{self._Keyword('record')}\n")
		self._indentation += 1

	def DepartRecordType(self, recordType: RecordType) -> None:
		"""
		Write the end of a record type declaration.

		:param recordType: The record type.
		"""
		self._WriteEnd("record", recordType.Identifier)

	def VisitRecordTypeElement(self, element: RecordTypeElement) -> None:
		"""
		Write the identifiers of an element declaration of a record type.

		**Format:** ``valid, last : bit;``

		:param element: The record element declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{', '.join(element.Identifiers)} : ")

	def DepartRecordTypeElement(self, element: RecordTypeElement) -> None:
		"""
		Write the semicolon ending an element declaration of a record type.

		:param element: The record element declaration.
		"""
		self._Write(";\n")

	def VisitAccessType(self, accessType: AccessType) -> None:
		"""
		Write the header and the reserved word ``access`` of an access type declaration.

		**Format:** ``type pointer is access node;``

		:param accessType: The access type.
		"""
		self._WriteTypeHeader(accessType)
		self._Write(f"{self._Keyword('access')} ")

	def DepartAccessType(self, accessType: AccessType) -> None:
		"""
		Write the semicolon ending an access type declaration.

		:param accessType: The access type.
		"""
		self._Write(";\n")

	def VisitFileType(self, fileType: FileType) -> None:
		"""
		Write the header and the reserved words ``file of`` of a file type declaration.

		**Format:** ``type text_file is file of string;``

		:param fileType: The file type.
		"""
		self._WriteTypeHeader(fileType)
		self._Write(f"{self._Keyword('file')} {self._Keyword('of')} ")

	def DepartFileType(self, fileType: FileType) -> None:
		"""
		Write the semicolon ending a file type declaration.

		:param fileType: The file type.
		"""
		self._Write(";\n")

	def VisitAlias(self, alias: Alias) -> None:
		"""
		Write the reserved word ``alias`` and the identifier of an alias declaration.

		**Format:** ``alias low : bit_vector(3 downto 0) is data(3 downto 0);`` or ``alias clock is clk;``

		:param alias: The alias declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('alias')} {alias.Identifier}")
		if alias.Subtype is not None:
			self._Write(" : ")

	def DepartAlias(self, alias: Alias) -> None:
		"""
		Write the semicolon ending an alias declaration.

		:param alias: The alias declaration.
		"""
		self._Write(";\n")

	def VisitAttribute(self, attribute: Attribute) -> None:
		"""
		Write the reserved word ``attribute`` and the identifier of an attribute declaration.

		**Format:** ``attribute keep : boolean;``

		:param attribute: The attribute declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword('attribute')} {attribute.Identifier} : ")

	def DepartAttribute(self, attribute: Attribute) -> None:
		"""
		Write the semicolon ending an attribute declaration.

		:param attribute: The attribute declaration.
		"""
		self._Write(";\n")

	def VisitAttributeSpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the reserved word ``attribute`` of an attribute specification.

		**Format:** ``attribute keep of valid, ready : signal is true;``

		:param specification:    The attribute specification.
		:raises VHDLWriterError: If the entity class is ``EntityClass.Others``.
		"""
		if specification.EntityClass is EntityClass.Others:
			raise VHDLWriterError("Entity class 'Others' has no VHDL notation.", specification)

		self._WriteIndentation()
		self._Write(f"{self._Keyword('attribute')} ")

	def DepartAttributeSpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the semicolon ending an attribute specification.

		:param specification: The attribute specification.
		"""
		self._Write(";\n")
