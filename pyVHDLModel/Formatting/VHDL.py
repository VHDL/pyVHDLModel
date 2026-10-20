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
from math                    import isfinite
from typing                  import ClassVar, Optional as Nullable

from pyTooling.Common        import getFullyQualifiedName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Association import AssociationItem
from pyVHDLModel.Base        import ModelElementUnion, ModelEntity
from pyVHDLModel.Exception   import VHDLWriterError
from pyVHDLModel.Expression  import (
	NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral,
	PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BitStringBase, BitStringLiteral
)
from pyVHDLModel.Name        import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, AttributeName
from pyVHDLModel.Name        import AllName, OpenName
from pyVHDLModel.Symbol      import Symbol
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
class VHDLStyle(metaclass=ExtendedType, slots=True):
	"""
	Represents the formatting options of the :class:`VHDL writer <VHDLWriter>`.
	"""

	_keywordCase: KeywordCase  #: Letter case of reserved words.

	def __init__(self, keywordCase: KeywordCase = KeywordCase.Lower) -> None:
		"""
		Initializes the formatting options.

		:param keywordCase: Optional, letter case of reserved words. Default: ``KeywordCase.Lower``.
		:raises ValueError: If parameter 'keywordCase' is None.
		:raises TypeError:  If parameter 'keywordCase' is not of type :class:`KeywordCase`.
		"""
		if keywordCase is None:
			raise ValueError("Parameter 'keywordCase' is None.")
		elif not isinstance(keywordCase, KeywordCase):
			ex = TypeError("Parameter 'keywordCase' is not of type 'KeywordCase'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(keywordCase)}'.")
			raise ex

		self._keywordCase = keywordCase

	@readonly
	def KeywordCase(self) -> KeywordCase:
		"""
		Read-only property to access the letter case of reserved words (:attr:`_keywordCase`).

		:returns: The letter case of reserved words.
		"""
		return self._keywordCase




@export
class VHDLWriter(Visitor):
	"""
	A writer formatting VHDL language model elements as VHDL source text.

	The writer handles the :mod:`visitor events <pyVHDLModel.Visitor>` of each supported model class. An element of a
	class without a walk of its own raises :exc:`~pyVHDLModel.Exception.VHDLWriterError`; nothing is skipped.

	Symbols are written from their :attr:`~pyVHDLModel.Symbol.Symbol.Name`, whether resolved or not.
	"""

	_BASE_SPECIFIERS: ClassVar[dict[BitStringBase, str]] = {
		BitStringBase.Binary:      "b",
		BitStringBase.Octal:       "o",
		BitStringBase.Decimal:     "d",
		BitStringBase.Hexadecimal: "x",
	}  #: Dictionary of base specifiers, indexed by bit string base.

	_style:  VHDLStyle  #: Formatting options.
	_buffer: list[str]  #: Fragments of the VHDL source text written by the running :meth:`Format` call.

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

		self._style =  style
		self._buffer = []

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

		Each call starts with an empty buffer.

		:param element:          The model element to format.
		:returns:                The VHDL source text.
		:raises ValueError:      If parameter 'element' is None.
		:raises TypeError:       If parameter 'element' is not of type :class:`~pyVHDLModel.Base.ModelEntity` or
		                         :class:`~pyVHDLModel.Symbol.Symbol`.
		:raises VHDLWriterError: If the element or one of its children is not supported by the writer.
		:raises VHDLWriterError: If the element or one of its children has no VHDL notation.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, (ModelEntity, Symbol)):
			ex = TypeError("Parameter 'element' is not of type 'ModelEntity' or 'Symbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		self._buffer = []
		element.Visit(self)
		return "".join(self._buffer)

	def VisitUnknown(self, element: ModelElementUnion) -> None:
		"""
		Reject a model element of a class without a walk of its own.

		:param element:          The model element.
		:raises VHDLWriterError: Always, because the writer doesn't support the element's class.
		"""
		ex = VHDLWriterError("Model element is not supported by the VHDL writer.", element)
		ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
		raise ex

	def VisitLeftParenthesis(self, element: IndexedName | ParenthesisName) -> None:
		"""
		Write the left parenthesis opening a parenthesized list.

		:param element: The element enclosing the list.
		"""
		self._Write("(")

	def _Write(self, text: str) -> None:
		"""
		Append VHDL source text to the buffer.

		:param text: The VHDL source text.
		"""
		self._buffer.append(text)

	def VisitComma(self, element: IndexedName | ParenthesisName) -> None:
		"""
		Write the comma between two items of a list.

		:param element: The element containing the list.
		"""
		self._Write(", ")

	def VisitArrow(self, element: AssociationItem) -> None:
		"""
		Write the arrow (``=>``) between a choice or formal and its value.

		:param element: The element containing the arrow.
		"""
		self._Write(" => ")

	def VisitNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Write a null literal.

		**Format:** ``null``

		:param literal: The null literal.
		"""
		self._Write(self._Keyword("null"))

	def _Keyword(self, word: str) -> str:
		"""
		Apply the keyword case of the formatting options to a reserved word.

		:param word: The reserved word in lower case.
		:returns:    The reserved word in the configured letter case.
		"""
		if self._style.KeywordCase is KeywordCase.Upper:
			return word.upper()

		return word

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

		:param literal: The integer literal.
		"""
		self._Write(str(literal.Value))

	def VisitFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Write a floating-point literal.

		**Format:** ``3.5``

		:param literal: The floating-point literal.
		"""
		self._Write(self._FormatReal(literal, literal.Value))

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
		self._Write(f"{literal.Value} {literal.UnitName}")

	def VisitPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Write a physical literal with a floating-point value.

		**Format:** ``1.5 ns``

		:param literal: The physical literal.
		"""
		self._Write(f"{self._FormatReal(literal, literal.Value)} {literal.UnitName}")

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
		base = self._BASE_SPECIFIERS.get(literal._base)
		if base is None:
			ex = VHDLWriterError("Model element is not supported by the VHDL writer.", literal)
			ex.add_note(f"Got type '{getFullyQualifiedName(literal)}'.")
			raise ex

		if literal.IsSigned is None:
			signedness = ""
		elif literal._base is BitStringBase.Decimal:
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
