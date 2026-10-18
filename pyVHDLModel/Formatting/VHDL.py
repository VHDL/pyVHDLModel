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

The writer is a visitor over the pyVHDLModel base classes: it dispatches on the class hierarchy of each model element,
so a parser's subclass of a model class (e.g. from ``pyGHDL.dom``) is written like that model class. Writing is a
re-format: comments, blank lines and the letter case of reserved words in a parsed source are not preserved.
"""
from __future__              import annotations

from enum                    import Enum, unique
from math                    import isfinite
from typing                  import Any, ClassVar, Dict, Union, Optional as Nullable

from pyTooling.Common        import getFullyQualifiedName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Association import GenericAssociationItem, PortAssociationItem, ParameterAssociationItem
from pyVHDLModel.Exception   import VHDLWriterError
from pyVHDLModel.Expression  import (
	NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral,
	PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BitStringLiteral, BinaryBitStringLiteral,
	OctalBitStringLiteral, DecimalBitStringLiteral, HexadecimalBitStringLiteral
)
from pyVHDLModel.Name        import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, AttributeName
from pyVHDLModel.Name        import AllName, OpenName
from pyVHDLModel.Symbol      import (
	Symbol, LibraryReferenceSymbol, PackageReferenceSymbol, ModeViewSymbol, SubprogramReferenceSymbol,
	ConfigurationSymbol, VariableSymbol, SignalSymbol, ContextReferenceSymbol, PackageMemberReferenceSymbol,
	AllPackageMembersReferenceSymbol, EntityInstantiationSymbol, ComponentInstantiationSymbol,
	ConfigurationInstantiationSymbol, EntitySymbol, ArchitectureSymbol, PackageSymbol, RecordElementSymbol,
	RangeAttributeSymbol, SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol, IndexedObjectOrFunctionCallSymbol
)


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
class VHDLWriter(metaclass=ExtendedType, slots=True):
	"""
	A writer formatting VHDL language model elements as VHDL source text.

	:meth:`Format` looks up a formatter method in :attr:`_FORMATTERS` along the class hierarchy (MRO) of the element. An
	element without a formatter raises :exc:`~pyVHDLModel.Exception.VHDLWriterError`; nothing is skipped.

	Symbols are written from their :attr:`~pyVHDLModel.Symbol.Symbol.Name`, whether resolved or not.
	"""

	_FORMATTERS: ClassVar[Dict[type, str]] = {
		NullLiteral:                       "_FormatNullLiteral",
		EnumerationLiteral:                "_FormatEnumerationLiteral",
		IntegerLiteral:                    "_FormatIntegerLiteral",
		FloatingPointLiteral:              "_FormatFloatingPointLiteral",
		PhysicalIntegerLiteral:            "_FormatPhysicalLiteral",
		PhysicalFloatingLiteral:           "_FormatPhysicalLiteral",
		CharacterLiteral:                  "_FormatCharacterLiteral",
		StringLiteral:                     "_FormatStringLiteral",
		BitStringLiteral:                  "_FormatBitStringLiteral",
		SimpleName:                        "_FormatSimpleName",
		SelectedName:                      "_FormatSelectedName",
		AllName:                           "_FormatAllName",
		AttributeName:                     "_FormatAttributeName",
		IndexedName:                       "_FormatIndexedName",
		ParenthesisName:                   "_FormatParenthesisName",
		SlicedName:                        "_FormatSlicedName",
		OpenName:                          "_FormatOpenName",
		LibraryReferenceSymbol:            "_FormatSymbol",
		PackageReferenceSymbol:            "_FormatSymbol",
		ModeViewSymbol:                    "_FormatSymbol",
		SubprogramReferenceSymbol:         "_FormatSymbol",
		ConfigurationSymbol:               "_FormatSymbol",
		VariableSymbol:                    "_FormatSymbol",
		SignalSymbol:                      "_FormatSymbol",
		ContextReferenceSymbol:            "_FormatSymbol",
		PackageMemberReferenceSymbol:      "_FormatSymbol",
		AllPackageMembersReferenceSymbol:  "_FormatSymbol",
		EntityInstantiationSymbol:         "_FormatSymbol",
		ComponentInstantiationSymbol:      "_FormatSymbol",
		ConfigurationInstantiationSymbol:  "_FormatSymbol",
		EntitySymbol:                      "_FormatSymbol",
		ArchitectureSymbol:                "_FormatSymbol",
		PackageSymbol:                     "_FormatSymbol",
		RecordElementSymbol:               "_FormatSymbol",
		RangeAttributeSymbol:              "_FormatSymbol",
		SimpleSubtypeSymbol:               "_FormatSymbol",
		SimpleObjectOrFunctionCallSymbol:  "_FormatSymbol",
		IndexedObjectOrFunctionCallSymbol: "_FormatSymbol",
		GenericAssociationItem:            "_FormatAssociationItem",
		PortAssociationItem:               "_FormatAssociationItem",
		ParameterAssociationItem:          "_FormatAssociationItem",
	}  #: Dictionary of formatter method names, indexed by model class.

	_BIT_STRING_BASES: ClassVar[Dict[type, str]] = {
		BinaryBitStringLiteral:      "b",
		OctalBitStringLiteral:       "o",
		DecimalBitStringLiteral:     "d",
		HexadecimalBitStringLiteral: "x",
	}  #: Dictionary of base specifiers, indexed by bit string literal class.

	_style: VHDLStyle  #: Formatting options.

	def __init__(self, style: Nullable[VHDLStyle] = None) -> None:
		"""
		Initializes a VHDL writer.

		:param style:      Optional, formatting options. Default: ``VHDLStyle()``.
		:raises TypeError: If parameter 'style' is not of type :class:`VHDLStyle`.
		"""
		if style is None:
			style = VHDLStyle()
		elif not isinstance(style, VHDLStyle):
			ex = TypeError("Parameter 'style' is not of type 'VHDLStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(style)}'.")
			raise ex

		self._style = style

	@readonly
	def Style(self) -> VHDLStyle:
		"""
		Read-only property to access the formatting options (:attr:`_style`).

		:returns: The formatting options.
		"""
		return self._style

	def Format(self, element: Any) -> str:
		"""
		Format a model element as VHDL source text.

		:param element:          The model element to format.
		:returns:                The VHDL source text.
		:raises ValueError:      If parameter 'element' is None.
		:raises VHDLWriterError: If the class of the element or of one of its children has no formatter.
		:raises VHDLWriterError: If the element or one of its children has no VHDL notation.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")

		return self._Format(element)

	def _Format(self, element: Any) -> str:
		"""
		Format a model element by the formatter of the closest class in its class hierarchy.

		:param element:          The model element to format.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If no class in the element's class hierarchy has a formatter.
		"""
		for cls in type(element).__mro__:
			methodName = self._FORMATTERS.get(cls)
			if methodName is not None:
				return getattr(self, methodName)(element)

		ex = VHDLWriterError("Model element is not supported by the VHDL writer.", element)
		ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
		raise ex

	def _Lookup(self, table: Dict[type, Any], element: Any) -> Any:
		"""
		Look up the entry of the closest class in an element's class hierarchy.

		:param table:            Dictionary of entries, indexed by model class.
		:param element:          The model element.
		:returns:                The entry.
		:raises VHDLWriterError: If no class in the element's class hierarchy has an entry.
		"""
		for cls in type(element).__mro__:
			if cls in table:
				return table[cls]

		ex = VHDLWriterError("Model element is not supported by the VHDL writer.", element)
		ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
		raise ex

	def _Keyword(self, word: str) -> str:
		"""
		Apply the keyword case of the formatting options to a reserved word.

		:param word: The reserved word in lower case.
		:returns:    The reserved word in the configured letter case.
		"""
		if self._style.KeywordCase is KeywordCase.Upper:
			return word.upper()

		return word

	def _FormatReal(self, element: Any, value: float) -> str:
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

	@staticmethod
	def _IsGraphic(text: str) -> bool:
		"""
		Check if all characters are VHDL graphic characters (ISO/IEC 8859-1 without control characters).

		:param text: The text to check.
		:returns:    ``True``, if all characters are graphic characters.
		"""
		return all(32 <= ord(character) <= 126 or 160 <= ord(character) <= 255 for character in text)

	def _FormatNullLiteral(self, literal: NullLiteral) -> str:
		"""
		Format a null literal.

		**Format:** ``null``

		:param literal: The null literal.
		:returns:       The VHDL source text.
		"""
		return self._Keyword("null")

	def _FormatEnumerationLiteral(self, literal: EnumerationLiteral) -> str:
		"""
		Format an enumeration literal.

		**Format:** ``Idle``

		:param literal: The enumeration literal.
		:returns:       The VHDL source text.
		"""
		return literal.Value

	def _FormatIntegerLiteral(self, literal: IntegerLiteral) -> str:
		"""
		Format an integer literal.

		**Format:** ``42``

		:param literal: The integer literal.
		:returns:       The VHDL source text.
		"""
		return str(literal.Value)

	def _FormatFloatingPointLiteral(self, literal: FloatingPointLiteral) -> str:
		"""
		Format a floating-point literal.

		**Format:** ``3.5``

		:param literal: The floating-point literal.
		:returns:       The VHDL source text.
		"""
		return self._FormatReal(literal, literal.Value)

	def _FormatPhysicalLiteral(self, literal: Union[PhysicalIntegerLiteral, PhysicalFloatingLiteral]) -> str:
		"""
		Format a physical literal.

		**Format:** ``10 ns``

		:param literal: The physical literal.
		:returns:       The VHDL source text.
		"""
		if isinstance(literal.Value, float):
			return f"{self._FormatReal(literal, literal.Value)} {literal.UnitName}"

		return f"{literal.Value} {literal.UnitName}"

	def _FormatCharacterLiteral(self, literal: CharacterLiteral) -> str:
		"""
		Format a character literal.

		**Format:** ``'a'``

		:param literal:          The character literal.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If the value is not a single graphic character.
		"""
		if len(literal.Value) != 1 or not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("Character literal is not a single graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		return f"'{literal.Value}'"

	def _FormatStringLiteral(self, literal: StringLiteral) -> str:
		"""
		Format a string literal and double each enclosed quotation mark.

		**Format:** ``"say ""hi"" twice"``

		:param literal:          The string literal.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If the value contains a non-graphic character.
		"""
		if not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("String literal contains a non-graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		value = literal.Value.replace("\"", "\"\"")
		return f"\"{value}\""

	def _FormatBitStringLiteral(self, literal: BitStringLiteral) -> str:
		"""
		Format a bit string literal.

		**Format:** ``8ux"A0"``

		:param literal:          The bit string literal.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If the literal's class has no base specifier.
		:raises VHDLWriterError: If a decimal bit string literal is signed or unsigned.
		:raises VHDLWriterError: If the value contains a quotation mark or a non-graphic character.
		"""
		base = self._Lookup(self._BIT_STRING_BASES, literal)
		if literal.IsSigned is None:
			signedness = ""
		elif isinstance(literal, DecimalBitStringLiteral):
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
		return f"{length}{signedness}{base}\"{literal.Value}\""

	def _FormatSimpleName(self, name: SimpleName) -> str:
		"""
		Format a simple name.

		**Format:** ``clk``

		:param name: The simple name.
		:returns:    The VHDL source text.
		"""
		return name.Identifier

	def _FormatSelectedName(self, name: SelectedName) -> str:
		"""
		Format a selected name.

		**Format:** ``ieee.numeric_std``

		:param name: The selected name.
		:returns:    The VHDL source text.
		"""
		return f"{self._Format(name.Prefix)}.{name.Identifier}"

	def _FormatAllName(self, name: AllName) -> str:
		"""
		Format a selected name with suffix ``all``.

		**Format:** ``ieee.numeric_std.all``

		:param name: The ``all`` name.
		:returns:    The VHDL source text.
		"""
		return f"{self._Format(name.Prefix)}.{self._Keyword('all')}"

	def _FormatAttributeName(self, name: AttributeName) -> str:
		"""
		Format an attribute name.

		**Format:** ``v'range``

		:param name: The attribute name.
		:returns:    The VHDL source text.
		"""
		return f"{self._Format(name.Prefix)}'{name.Identifier}"

	def _FormatIndexedName(self, name: IndexedName) -> str:
		"""
		Format an indexed name.

		**Format:** ``m(i, j)``

		:param name: The indexed name.
		:returns:    The VHDL source text.
		"""
		return f"{self._Format(name.Prefix)}({', '.join(self._Format(index) for index in name.Indices)})"

	def _FormatParenthesisName(self, name: ParenthesisName) -> str:
		"""
		Format a name followed by a parenthesized association list (index, slice or function call).

		**Format:** ``resize(a, 8)``

		:param name: The parenthesis name.
		:returns:    The VHDL source text.
		"""
		associations = ", ".join(self._Format(association) for association in name.Associations)
		return f"{self._Format(name.Prefix)}({associations})"

	def _FormatSlicedName(self, name: SlicedName) -> str:
		"""
		Reject a sliced name, because it carries no discrete range.

		:param name:             The sliced name.
		:raises VHDLWriterError: Always, because a sliced name carries no discrete range. |br|
		                         Use a :class:`~pyVHDLModel.Name.ParenthesisName` with a range expression as association.
		"""
		ex = VHDLWriterError("Sliced name carries no discrete range.", name)
		ex.add_note("Use a 'ParenthesisName' with a range expression as association.")
		raise ex

	def _FormatOpenName(self, name: OpenName) -> str:
		"""
		Format the reserved word ``open``.

		**Format:** ``open``

		:param name: The ``open`` name.
		:returns:    The VHDL source text.
		"""
		return self._Keyword("open")

	def _FormatSymbol(self, symbol: Symbol) -> str:
		"""
		Format a symbol by its name.

		**Format:** ``ieee.std_logic_1164.all``

		:param symbol: The symbol.
		:returns:      The VHDL source text.
		"""
		return self._Format(symbol.Name)

	def _FormatAssociationItem(
		self,
		item: Union[GenericAssociationItem, PortAssociationItem, ParameterAssociationItem]
	) -> str:
		"""
		Format an association item, named or positional.

		**Format:** ``formal => actual`` or ``actual``

		:param item:             The association item.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If the association item has no actual.
		"""
		if item.Actual is None:
			raise VHDLWriterError("Association item has no actual.", item)
		elif item.Formal is None:
			return self._Format(item.Actual)

		return f"{self._Format(item.Formal)} => {self._Format(item.Actual)}"
