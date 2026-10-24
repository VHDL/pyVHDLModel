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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
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
This module contains parts of an abstract document language model for VHDL.

All declarations for literals, aggregates, operators forming an expressions.
"""
from __future__            import annotations

from enum                  import Flag, IntEnum, unique
from typing                import TYPE_CHECKING, Iterable, Union, ClassVar, Optional as Nullable, Self

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import abstractclass

from pyVHDLModel.Base      import ModelEntity, Direction, Range, ReservedWord
from pyVHDLModel.Exception import LiteralError
from pyVHDLModel.Symbol    import Symbol, SubtypeSymbol
if TYPE_CHECKING:
	from pyVHDLModel.Visitor import Visitor


ExpressionUnion = Union[
	'BaseExpression',
	'QualifiedExpression',
	'FunctionCall',
	'TypeConversion',
	# ConstantOrSymbol,     TODO: ObjectSymbol
	'Literal',
]


@export
@unique
class OperatorPrecedence(IntEnum):
	"""
	An enumeration of VHDL's operator precedence levels, from loosest to tightest binding.

	The levels follow IEEE Std 1076-2008, clause 9.2. A range and a conditional expression are no operators, but bind
	looser than every operator.
	"""

	Range =         0  #: Range with direction ``to`` or ``downto``.
	Conditional =   1  #: Conditional expression (``when`` ... ``else``).
	Logical =       2  #: Binary logical operators, e.g. ``and``.
	Relational =    3  #: Relational operators, e.g. ``=`` or ``?=``.
	Shift =         4  #: Shift and rotate operators, e.g. ``sll``.
	Adding =        5  #: Adding operators (``+``, ``-``, ``&``) and signs (unary ``+``, ``-``).
	Multiplying =   6  #: Multiplying operators, e.g. ``*`` or ``mod``.
	Miscellaneous = 7  #: Exponentiation (``**``), ``abs``, ``not`` and unary logical operators.
	Primary =       8  #: Primaries, e.g. names, literals, aggregates or parenthesized expressions.


@export
@abstractclass
class BaseExpression(ModelEntity):
	"""
	Represents the base-class of all expressions.

	.. seealso::

	   * :class:`Literal <pyVHDLModel.Expression.Literal>`
	   * :class:`Unary expression <pyVHDLModel.Expression.UnaryExpression>`
	   * :class:`Binary expression <pyVHDLModel.Expression.BinaryExpression>`
	   * :class:`Qualified expression <pyVHDLModel.Expression.QualifiedExpression>`
	   * :class:`Ternary expression <pyVHDLModel.Expression.TernaryExpression>`
	   * :class:`Function call <pyVHDLModel.Expression.FunctionCall>`
	   * :class:`Allocation <pyVHDLModel.Expression.Allocation>`
	   * :class:`Aggregate <pyVHDLModel.Expression.Aggregate>`
	"""


@export
@abstractclass
class Literal(BaseExpression):
	"""
	Represents the base-class of all literals.

	A literal is an expression denoting a value written directly in the source.

	.. seealso::

	   * :class:`Null literal <pyVHDLModel.Expression.NullLiteral>`
	   * :class:`Enumeration literal <pyVHDLModel.Expression.EnumerationLiteral>`
	   * :class:`Numeric literal <pyVHDLModel.Expression.NumericLiteral>`
	   * :class:`Character literal <pyVHDLModel.Expression.CharacterLiteral>`
	   * :class:`String literal <pyVHDLModel.Expression.StringLiteral>`
	   * :class:`Bit string literal <pyVHDLModel.Expression.BitStringLiteral>`
	"""


@export
class NullLiteral(Literal):
	"""
	Represents a ``null`` literal.

	A null literal denotes the null value of an access type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      p := null;
	      --   ^^^^    <- the literal
	"""
	def Copy(self) -> Self:
		"""
		Create a copy of this null literal.

		The copy has no parent.

		:returns: The new null literal.
		"""
		return self.__class__()

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this null literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitNullLiteral(self)
		visitor.DepartNullLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the null literal.

		**Format:** ``null``

		:returns: Formatted null literal.
		"""
		return "null"


@export
class EnumerationLiteral(Literal):
	"""
	Represents an enumeration literal.

	The literal's name is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      st <= Idle;
	      --    ^^^^    <- Value
	"""
	_value: str  #: The enumeration literal's name.

	def __init__(self, value: str, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an enumeration literal.

		:param value:  The enumeration literal's name.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._value = value

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this enumeration literal.

		The copy has no parent.

		:returns: The new enumeration literal.
		"""
		return self.__class__(self._value)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this enumeration literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitEnumerationLiteral(self)
		visitor.DepartEnumerationLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the enumeration literal.

		**Format:** ``idle``

		:returns: Formatted enumeration literal.
		"""
		return self._value


@export
@abstractclass
class NumericLiteral(Literal):
	"""
	Represents the base-class of all numeric literals.

	Integer, floating-point and physical literals are numeric.

	.. seealso::

	   * :class:`Integer literal <pyVHDLModel.Expression.IntegerLiteral>`
	   * :class:`Floating point literal <pyVHDLModel.Expression.FloatingPointLiteral>`
	   * :class:`Physical literal <pyVHDLModel.Expression.PhysicalLiteral>`
	"""


@export
class IntegerLiteral(NumericLiteral):
	"""
	Represents an integer literal.

	The literal's value is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a + 42;
	      --         ^^    <- Value
	"""
	_value: int  #: The literal's integer value.

	def __init__(self, value: int) -> None:
		"""
		Initializes an integer literal.

		:param value: The literal's integer value.
		"""
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> int:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this integer literal.

		The copy has no parent.

		:returns: The new integer literal.
		"""
		return self.__class__(self._value)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this integer literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitIntegerLiteral(self)
		visitor.DepartIntegerLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the integer literal.

		**Format:** ``42``

		:returns: Formatted integer literal.
		"""
		return str(self._value)


@export
class FloatingPointLiteral(NumericLiteral):
	"""
	Represents a floating-point literal.

	The literal's value is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      r <= 3.14;
	      --   ^^^^    <- Value
	"""
	_value: float  #: The literal's floating-point value.

	def __init__(self, value: float) -> None:
		"""
		Initializes a floating-point literal.

		:param value: The literal's floating-point value.
		"""
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> float:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this floating-point literal.

		The copy has no parent.

		:returns: The new floating-point literal.
		"""
		return self.__class__(self._value)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this floating-point literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitFloatingPointLiteral(self)
		visitor.DepartFloatingPointLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the floating-point literal.

		**Format:** ``3.5``

		:returns: Formatted floating-point literal.
		"""
		return str(self._value)


@export
@abstractclass
class PhysicalLiteral(NumericLiteral):
	"""
	Represents the base-class of all physical literals.

	A physical literal combines a numeric value with a unit name (:data:`UnitName`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      t <= 10 ns;
	      --   ^^       <- the value
	      --      ^^    <- UnitName

	.. seealso::

	   * :class:`Physical integer literal <pyVHDLModel.Expression.PhysicalIntegerLiteral>`
	   * :class:`Physical floating literal <pyVHDLModel.Expression.PhysicalFloatingLiteral>`
	"""
	_unitName: str  #: The name of the physical unit the value is given in.

	def __init__(self, unitName: str) -> None:
		"""
		Initializes a physical literal.

		:param unitName: The name of the physical unit the value is given in.
		"""
		super().__init__()
		self._unitName = unitName

	@readonly
	def UnitName(self) -> str:
		"""
		Read-only property to access the unit name (:attr:`_unitName`).

		:returns: The unit name.
		"""
		return self._unitName

	def __str__(self) -> str:
		"""
		Formats the physical literal.

		**Format:** ``10 ns``

		:returns: Formatted physical literal.
		"""
		return f"{self._value} {self._unitName}"


@export
class PhysicalIntegerLiteral(PhysicalLiteral):
	"""
	Represents a physical literal with an integer value.

	Value (:data:`Value`) and unit name (:data:`UnitName`) are available separately.

	.. admonition:: Example

	   .. code-block:: VHDL

	      t <= 10 ns;
	      --   ^^       <- Value
	      --      ^^    <- UnitName
	"""
	_value: int  #: The literal's integer value, in units of :attr:`_unitName`.

	def __init__(self, value: int, unitName: str) -> None:
		"""
		Initializes a physical literal with an integer value.

		:param value:    The literal's integer value, in units of :attr:`_unitName`.
		:param unitName: The name of the physical unit the value is given in.
		"""
		super().__init__(unitName)
		self._value = value

	@readonly
	def Value(self) -> int:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this physical literal.

		The copy has no parent.

		:returns: The new physical literal.
		"""
		return self.__class__(self._value, self._unitName)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this physical literal with an integer value with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitPhysicalIntegerLiteral(self)
		visitor.DepartPhysicalIntegerLiteral(self)


@export
class PhysicalFloatingLiteral(PhysicalLiteral):
	"""
	Represents a physical literal with a floating-point value.

	Value (:data:`Value`) and unit name (:data:`UnitName`) are available separately.

	.. admonition:: Example

	   .. code-block:: VHDL

	      t <= 1.5 ns;
	      --   ^^^       <- Value
	      --       ^^    <- UnitName
	"""
	_value: float  #: The literal's floating-point value, in units of :attr:`_unitName`.

	def __init__(self, value: float, unitName: str) -> None:
		"""
		Initializes a physical literal with a floating-point value.

		:param value:    The literal's floating-point value, in units of :attr:`_unitName`.
		:param unitName: The name of the physical unit the value is given in.
		"""
		super().__init__(unitName)
		self._value = value

	@readonly
	def Value(self) -> float:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this physical literal.

		The copy has no parent.

		:returns: The new physical literal.
		"""
		return self.__class__(self._value, self._unitName)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this physical literal with a floating-point value with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitPhysicalFloatingLiteral(self)
		visitor.DepartPhysicalFloatingLiteral(self)


@export
class CharacterLiteral(Literal):
	"""
	Represents a character literal.

	The literal's character is available as :data:`Value`. It is the bare character without the enclosing apostrophes:
	``a`` for the character literal ``'a'``.

	.. admonition:: Example

	   .. code-block:: VHDL

	      ch <= 'a';
	      --     ^     <- Value
	"""
	_value: str  #: The literal's character value without apostrophes.

	def __init__(self, value: str) -> None:
		"""
		Initializes a character literal.

		:param value:       The literal's character value without apostrophes.
		:raises ValueError: If parameter 'value' is None.
		:raises TypeError:  If parameter 'value' is not of type :class:`str`.
		:raises ValueError: If parameter 'value' is not a single character.
		"""
		super().__init__()

		if value is None:
			raise ValueError("Parameter 'value' is None.")
		elif not isinstance(value, str):
			ex = TypeError("Parameter 'value' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex
		elif len(value) != 1:
			ex = ValueError("Parameter 'value' is not a single character.")
			ex.add_note(f"Got value '{value}'.")
			ex.add_note("Pass the character without apostrophes.")
			raise ex

		self._value = value

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this character literal.

		The copy has no parent.

		:returns: The new character literal.
		"""
		return self.__class__(self._value)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this character literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitCharacterLiteral(self)
		visitor.DepartCharacterLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the character literal.

		**Format:** ``a``

		:returns: Formatted character literal.
		"""
		return str(self._value)


@export
class StringLiteral(Literal):
	"""
	Represents a string literal.

	The literal's text is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      txt <= "text";
	      --     ^^^^^^    <- Value
	"""
	_value: str  #: The literal's string value, without the enclosing double quotes.

	def __init__(self, value: str) -> None:
		"""
		Initializes a string literal.

		:param value: The literal's string value, without the enclosing double quotes.
		"""
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def Copy(self) -> Self:
		"""
		Create a copy of this string literal.

		The copy has no parent.

		:returns: The new string literal.
		"""
		return self.__class__(self._value)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this string literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitStringLiteral(self)
		visitor.DepartStringLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the string literal.

		**Format:** ``"hello"``

		:returns: Formatted string literal.
		"""
		return "\"" + self._value + "\""


@export
class BitStringBase(Flag):
	"""
	Represents the base of a bit string literal: binary, octal, decimal or hexadecimal.
	"""
	NoBase = 0
	Binary = 2
	Octal = 8
	Decimal = 10
	Hexadecimal = 16
	Unsigned = 32
	Signed = 64


@export
@abstractclass
class BitStringLiteral(Literal):
	"""
	Represents the base-class of all bit string literals.

	Besides the literal as written (:data:`Value`), the bits are available in binary form
	(:data:`BinaryValue`, :data:`Bits`), together with the literal's length (:data:`Length`) and
	whether it is signed (:data:`IsSigned`).

	The binary form follows IEEE Std 1076-2008, clause 15.8. It is computed on first access of :data:`BinaryValue` or
	:data:`Bits`, so a literal violating these rules can still be constructed, copied and formatted.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := b"10100000";
	      --     ^^^^^^^^^^^    <- Value

	.. seealso::

	   * :class:`Binary bit string literal <pyVHDLModel.Expression.BinaryBitStringLiteral>`
	   * :class:`Octal bit string literal <pyVHDLModel.Expression.OctalBitStringLiteral>`
	   * :class:`Decimal bit string literal <pyVHDLModel.Expression.DecimalBitStringLiteral>`
	   * :class:`Hexadecimal bit string literal <pyVHDLModel.Expression.HexadecimalBitStringLiteral>`
	"""
	_BASE:        ClassVar[BitStringBase] = BitStringBase.NoBase  #: The base this literal is written in.

	_value:       str             #: The literal as written in the source, without the enclosing double quotes.
	_binaryValue: Nullable[str]   #: The literal's string value, one character per bit, or ``None`` until computed.
	_length:      Nullable[int]   #: The explicitly given length, or ``None`` if the literal has no length specification.
	_isSigned:    Nullable[bool]  #: ``True`` if signed, ``False`` if unsigned, ``None`` if unspecified.

	def __init__(self, value: str, length: Nullable[int] = None, isSigned: Nullable[bool] = None) -> None:
		"""
		Initializes a bit string literal.

		:param value:       The literal as written in the source, without the enclosing double quotes.
		:param length:      The explicitly given length, or ``None`` if the literal has no length specification.
		:param isSigned:    ``True`` if signed, ``False`` if unsigned, ``None`` if unspecified.
		:raises ValueError: If parameter 'value' is None.
		:raises TypeError:  If parameter 'value' is not of type :class:`str`.
		:raises TypeError:  If parameter 'length' is not of type :class:`int`.
		:raises ValueError: If parameter 'length' is negative.
		:raises TypeError:  If parameter 'isSigned' is not of type :class:`bool`.
		"""
		super().__init__()

		if value is None:
			raise ValueError("Parameter 'value' is None.")
		elif not isinstance(value, str):
			ex = TypeError("Parameter 'value' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		if length is not None and not isinstance(length, int):
			ex = TypeError("Parameter 'length' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(length)}'.")
			raise ex
		elif length is not None and length < 0:
			ex = ValueError("Parameter 'length' is negative.")
			ex.add_note(f"Got value '{length}'.")
			raise ex

		if isSigned is not None and not isinstance(isSigned, bool):
			ex = TypeError("Parameter 'isSigned' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(isSigned)}'.")
			raise ex

		self._value =       value
		self._binaryValue = None
		self._length =      length
		self._isSigned =    isSigned

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	@readonly
	def BinaryValue(self) -> str:
		"""
		Read-only property to return the literal's string value, one character per bit (:attr:`_binaryValue`).

		The value follows IEEE Std 1076-2008, clause 15.8. It is computed from :data:`Value`, the base, :data:`Length`
		and :data:`IsSigned` on first access and cached:

		1. Underscores are removed.
		2. Expansion:

		   * Binary, octal and hexadecimal: each digit valid for the base is replaced by its 1, 3 or 4 bits; hexadecimal
		     digits are case-insensitive. Each other graphic character, e.g. ``X``, ``Z`` or ``-``, is repeated 1, 3 or 4
		     times, keeping its case.
		   * Decimal: the digits are converted to binary with the minimal number of bits (none for ``0``).

		3. With a length larger than the expanded value, the value is padded on the left: with ``0`` if unsigned or
		   unspecified, with the leftmost character if signed.
		4. With a length smaller than the expanded value, leftmost characters are deleted: only ``0`` if unsigned or
		   unspecified, only copies of the leftmost remaining character if signed.

		Example: ``12sx"F5"`` |rarr| ``111111110101``.

		:returns:             The literal's string value, one character per bit.
		:raises LiteralError: If the value starts or ends with an underscore or contains two consecutive underscores.
		:raises LiteralError: If a decimal literal is signed or unsigned.
		:raises LiteralError: If a decimal literal contains a character other than a digit or an underscore.
		:raises LiteralError: If a digit is not allowed in the base, e.g. ``2`` in a binary literal.
		:raises LiteralError: If the value contains a non-graphic character.
		:raises LiteralError: If a signed literal with an empty expanded value has a non-zero length.
		:raises LiteralError: If the length of an unsigned or unspecified literal truncates a character other than
		                      ``0``. |br|
		                      Only leading '0' characters can be truncated.
		:raises LiteralError: If the length of a signed literal truncates a character other than the sign. |br|
		                      Only copies of the leftmost remaining character can be truncated.
		"""
		if self._binaryValue is not None:
			return self._binaryValue

		if self._value.startswith("_") or self._value.endswith("_") or "__" in self._value:
			ex = LiteralError("Bit string literal has a leading, trailing or double underscore.", self)
			ex.add_note(f"Got value '{self}'.")
			raise ex

		simplifiedValue = self._value.replace("_", "")
		radix =           self._BASE.value

		if self._BASE is BitStringBase.Decimal:
			if self._isSigned is not None:
				ex = LiteralError("Decimal bit string literal can't be signed or unsigned.", self)
				ex.add_note(f"Got value '{self}'.")
				raise ex

			for character in simplifiedValue:
				if character not in "0123456789":
					ex = LiteralError("Decimal bit string literal contains a character other than a digit.", self)
					ex.add_note(f"Got character '{character}' in value '{self}'.")
					raise ex

			number =        0 if simplifiedValue == "" else int(simplifiedValue)
			expandedValue = "" if number == 0 else f"{number:b}"
		else:
			bitsPerDigit = radix.bit_length() - 1
			bitList =      []
			for character in simplifiedValue:
				if character in "0123456789":
					digit = int(character)
					if digit >= radix:
						ex = LiteralError(f"Bit string literal contains a digit not allowed in base {radix}.", self)
						ex.add_note(f"Got digit '{character}' in value '{self}'.")
						raise ex
				elif radix == 16 and character in "abcdefABCDEF":
					digit = int(character, 16)
				elif 32 <= ord(character) <= 126 or 160 <= ord(character) <= 255:
					bitList.append(character * bitsPerDigit)
					continue
				else:
					ex = LiteralError("Bit string literal contains a non-graphic character.", self)
					ex.add_note(f"Got value {str(self)!r}.")
					raise ex

				bitList.append(f"{digit:0{bitsPerDigit}b}")

			expandedValue = "".join(bitList)

		expandedLength = len(expandedValue)
		if self._length is None or self._length == expandedLength:
			binaryValue = expandedValue
		elif self._length > expandedLength:
			if self._isSigned is not True:
				padding = "0"
			elif expandedLength == 0:
				ex = LiteralError("Signed bit string literal with an empty value can't be extended.", self)
				ex.add_note(f"Got value '{self}'.")
				raise ex
			else:
				padding = expandedValue[0]

			binaryValue = padding * (self._length - expandedLength) + expandedValue
		else:
			deletedCount = expandedLength - self._length
			deletedValue = expandedValue[:deletedCount]
			binaryValue =  expandedValue[deletedCount:]
			if self._isSigned is not True:
				padding = "0"
			elif self._length == 0:
				padding = ""
			else:
				padding = binaryValue[0]

			if deletedValue != padding * deletedCount:
				ex = LiteralError(f"Bit string literal's length {self._length} truncates significant characters.", self)
				ex.add_note(f"Got value '{self}' expanded to '{expandedValue}'.")
				if self._isSigned is True:
					ex.add_note("Only copies of the leftmost remaining character can be truncated.")
				else:
					ex.add_note("Only leading '0' characters can be truncated.")
				raise ex

		self._binaryValue = binaryValue
		return binaryValue

	@readonly
	def Bits(self) -> int:
		"""
		Read-only property to return the number of bits the literal represents.

		This is the length of :data:`BinaryValue`, computed the same way, so the same exceptions apply.

		:returns: The number of bits.
		"""
		return len(self.BinaryValue)

	@readonly
	def Length(self) -> Nullable[int]:
		"""
		Read-only property to access the length (:attr:`_length`).

		:returns: The length, or ``None`` if not set.
		"""
		return self._length

	@readonly
	def IsSigned(self) -> Nullable[bool]:
		"""
		Check if the bit string literal is signed (:attr:`_isSigned`).

		:returns: ``True``, if the literal is signed; ``False``, if unsigned; ``None``, if unspecified.
		"""
		return self._isSigned

	def Copy(self) -> Self:
		"""
		Create a copy of this bit string literal.

		The copy has no parent.

		:returns: The new bit string literal.
		"""
		return self.__class__(self._value, self._length, self._isSigned)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this bit string literal with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitBitStringLiteral(self)
		visitor.DepartBitStringLiteral(self)

	def __str__(self) -> str:
		"""
		Formats the bit string literal.

		**Format:** ``8ub"10100000"``

		The length and the signedness marker (``s``/``u``) are omitted when unspecified.

		:returns: Formatted bit string literal.
		"""
		signed = "" if self._isSigned is None else "s" if self._isSigned is True else "u"
		if self._BASE is BitStringBase.NoBase:
			base = ""
		elif self._BASE is BitStringBase.Binary:
			base = "b"
		elif self._BASE is BitStringBase.Octal:
			base = "o"
		elif self._BASE is BitStringBase.Decimal:
			base = "d"
		elif self._BASE is BitStringBase.Hexadecimal:
			base = "x"
		length = "" if self._length is None else str(self._length)
		return length + signed + base + "\"" + self._value + "\""


@export
class BinaryBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 2.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := b"10100000";
	      --     ^^^^^^^^^^^    <- Value
	"""
	_BASE: ClassVar[BitStringBase] = BitStringBase.Binary  #: The base this literal is written in.


@export
class OctalBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 8.

	Each digit contributes three bits.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := o"240";
	      --     ^^^^^^    <- Value
	"""
	_BASE: ClassVar[BitStringBase] = BitStringBase.Octal  #: The base this literal is written in.


@export
class DecimalBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 10.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := d"160";
	      --     ^^^^^^    <- Value
	"""
	_BASE: ClassVar[BitStringBase] = BitStringBase.Decimal  #: The base this literal is written in.


@export
class HexadecimalBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 16.

	Each digit contributes four bits.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := x"A0";
	      --     ^^^^^    <- Value
	"""
	_BASE: ClassVar[BitStringBase] = BitStringBase.Hexadecimal  #: The base this literal is written in.


@export
class ParenthesisExpression: #(Protocol):
	"""
	Represents the base-class of expressions wrapped in parentheses.

	The operand is available as :data:`Operand`.

	.. seealso::

	   * :class:`Sub expression <pyVHDLModel.Expression.SubExpression>`
	   * :class:`Qualified expression <pyVHDLModel.Expression.QualifiedExpression>`
	"""
	__slots__ = ()  # FIXME: use ExtendedType?

	@readonly
	def Operand(self) -> ExpressionUnion:
		"""
		Read-only property to return the operand. A parenthesis expression has none of its own.

		:returns: The operand.
		"""
		return None


@export
@abstractclass
class UnaryExpression(BaseExpression):
	"""
	Represents the base-class of all unary expressions.

	The operand is available as :data:`Operand`.
	"""

	_PRECEDENCE:    ClassVar[OperatorPrecedence]             #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]                #: The operator's string representation as (prefix, suffix) of the operand.
	_RESERVED_WORD: ClassVar[Nullable[ReservedWord]] = None  #: The operator's reserved word; ``None`` for a symbol (:attr:`_FORMAT`).
	_operand:       ExpressionUnion                          #: The expression the operator is applied to.

	def __init__(self, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a unary expression.

		:param operand: The expression the operator is applied to.
		:param parent:  The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._operand = operand
		operand.Parent = self

	@readonly
	def Operand(self) -> ExpressionUnion:
		"""
		Read-only property to access the operand (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	def Copy(self) -> Self:
		"""
		Create a copy of this unary expression.

		The copy has no parent. Its operand is a copy of this expression's operand.

		:returns: The new unary expression.
		"""
		return self.__class__(self._operand.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this unary expression and its operand with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitUnaryExpression(self)
		self._operand.Visit(visitor)
		visitor.DepartUnaryExpression(self)

	def __str__(self) -> str:
		"""
		Formats the unary expression.

		**Format:** ``not operand``

		:returns: Formatted unary expression.
		"""
		return f"{self._FORMAT[0]}{self._operand!s}{self._FORMAT[1]}"


@export
class NegationExpression(UnaryExpression):
	"""
	Represents a negation (unary minus) expression.

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := - operand;
	      --     ^^^^^^^^^    <- the expression
	      --       ^^^^^^^    <- Operand
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Adding  #: The operator's precedence level.
	_FORMAT:     ClassVar[tuple[str, str]]    = ("-", "")                  #: The operator's string fragments.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this negation and its operand with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitNegationExpression(self)
		self._operand.Visit(visitor)
		visitor.DepartNegationExpression(self)


@export
class IdentityExpression(UnaryExpression):
	"""
	Represents an identity (unary plus) expression.

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := + operand;
	      --     ^^^^^^^^^    <- the expression
	      --       ^^^^^^^    <- Operand
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Adding  #: The operator's precedence level.
	_FORMAT:     ClassVar[tuple[str, str]]    = ("+", "")                  #: The operator's string fragments.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this identity and its operand with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitIdentityExpression(self)
		self._operand.Visit(visitor)
		visitor.DepartIdentityExpression(self)


@export
class InverseExpression(UnaryExpression):
	"""
	Represents a logical inversion expression (``not``).

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := not operand;
	      --     ^^^^^^^^^^^    <- the expression
	      --         ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("not ", "")                      #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Not                  #: The operator's reserved word.


@export
class UnaryAndExpression(UnaryExpression):
	"""
	Represents a ``and`` reduction expression.

	A reduction operator folds all elements of an array into a single value.
	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := and operand;
	      --     ^^^^^^^^^^^    <- the expression
	      --         ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("and ", "")                      #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.And                  #: The operator's reserved word.


@export
class UnaryNandExpression(UnaryExpression):
	"""
	Represents a ``nand`` reduction expression.

	A reduction operator folds all elements of an array into a single value.
	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := nand operand;
	      --     ^^^^^^^^^^^^    <- the expression
	      --          ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("nand ", "")                     #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Nand                 #: The operator's reserved word.


@export
class UnaryOrExpression(UnaryExpression):
	"""
	Represents a ``or`` reduction expression.

	A reduction operator folds all elements of an array into a single value.
	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := or operand;
	      --     ^^^^^^^^^^    <- the expression
	      --        ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("or ", "")                       #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Or                   #: The operator's reserved word.


@export
class UnaryNorExpression(UnaryExpression):
	"""
	Represents a ``nor`` reduction expression.

	A reduction operator folds all elements of an array into a single value.
	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := nor operand;
	      --     ^^^^^^^^^^^    <- the expression
	      --         ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("nor ", "")                      #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Nor                  #: The operator's reserved word.


@export
class UnaryXorExpression(UnaryExpression):
	"""
	Represents a ``xor`` reduction expression.

	A reduction operator folds all elements of an array into a single value.
	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := xor operand;
	      --     ^^^^^^^^^^^    <- the expression
	      --         ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("xor ", "")                      #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Xor                  #: The operator's reserved word.


@export
class UnaryXnorExpression(UnaryExpression):
	"""
	Represents a ``xnor`` reduction expression.

	A reduction operator folds all elements of an array into a single value.
	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := xnor operand;
	      --     ^^^^^^^^^^^^    <- the expression
	      --          ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("xnor ", "")                     #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Xnor                 #: The operator's reserved word.


@export
class AbsoluteExpression(UnaryExpression):
	"""
	Represents an absolute value expression (``abs``).

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := abs operand;
	      --     ^^^^^^^^^^^    <- the expression
	      --         ^^^^^^^    <- Operand
	"""
	_PRECEDENCE:    ClassVar[OperatorPrecedence] = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str]]    = ("abs ", "")                      #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]       = ReservedWord.Abs                  #: The operator's reserved word.


@export
class TypeConversion(UnaryExpression):
	"""
	Represents a type conversion.

	A type conversion converts its operand (:data:`Operand`) to the target subtype
	(:data:`TargetSubtype`). Unlike every other :class:`UnaryExpression`, its "operator" is the target
	type name itself rather than a fixed string, so it carries its own subtype and renders itself.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := integer(val);
	      --     ^^^^^^^         <- TargetSubtype
	      --             ^^^     <- Operand
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Primary  #: The operator's precedence level.

	_targetSubtype: SubtypeSymbol  #: Reference to the subtype the expression is converted to.

	def __init__(self, targetSubtype: SubtypeSymbol, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a type conversion.

		:param targetSubtype: Reference to the subtype the expression is converted to.
		:param operand:       The expression the operator is applied to.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(operand, parent)

		self._targetSubtype = targetSubtype
		targetSubtype.Parent = self

	@readonly
	def TargetSubtype(self) -> SubtypeSymbol:
		"""
		Read-only property to access the target subtype (:attr:`_targetSubtype`).

		:returns: The target subtype.
		"""
		return self._targetSubtype

	def Copy(self) -> Self:
		"""
		Create a copy of this type conversion.

		The copy has no parent. Its target subtype and operand are copies of this conversion's target subtype and operand.

		:returns: The new type conversion.
		"""
		return self.__class__(self._targetSubtype.Copy(), self._operand.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this type conversion, its target subtype and its operand with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitTypeConversion(self)
		self._targetSubtype.Visit(visitor)
		visitor.VisitLeftParenthesis(self)
		self._operand.Visit(visitor)
		visitor.DepartTypeConversion(self)

	def __str__(self) -> str:
		"""
		Formats the type conversion.

		**Format:** ``integer(val)``

		:returns: Formatted type conversion.
		"""
		return f"{self._targetSubtype!s}({self._operand!s})"


@export
class SubExpression(UnaryExpression, ParenthesisExpression):
	"""
	Represents a parenthesized sub-expression.

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := (lhs + rhs);
	      --     ^^^^^^^^^^^    <- the sub-expression
	      --      ^^^^^^^^^     <- Operand
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Primary  #: The operator's precedence level.
	_FORMAT:     ClassVar[tuple[str, str]]    = ("(", ")")                  #: The operator's string fragments.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this sub-expression and its operand with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSubExpression(self)
		self._operand.Visit(visitor)
		visitor.DepartSubExpression(self)


@export
@abstractclass
class BinaryExpression(BaseExpression):
	"""
	Represents the base-class of all binary expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Range expression <pyVHDLModel.Expression.RangeExpression>`
	   * :class:`Adding expression <pyVHDLModel.Expression.AddingExpression>`
	   * :class:`Multiplying expression <pyVHDLModel.Expression.MultiplyingExpression>`
	   * :class:`Logical expression <pyVHDLModel.Expression.LogicalExpression>`
	   * :class:`Relational expression <pyVHDLModel.Expression.RelationalExpression>`
	   * :class:`Shift expression <pyVHDLModel.Expression.ShiftExpression>`
	"""

	_PRECEDENCE:    ClassVar[OperatorPrecedence]             #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str, str]]           #: The operator's string representation as (prefix, infix, suffix).
	_RESERVED_WORD: ClassVar[Nullable[ReservedWord]] = None  #: The operator's reserved word; ``None`` for a symbol (:attr:`_FORMAT`).
	_leftOperand:   ExpressionUnion                          #: The expression left of the operator.
	_rightOperand:  ExpressionUnion                          #: The expression right of the operator.

	def __init__(self, leftOperand: ExpressionUnion, rightOperand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a binary expression.

		:param leftOperand:  The expression left of the operator.
		:param rightOperand: The expression right of the operator.
		:param parent:       The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._leftOperand = leftOperand
		leftOperand.Parent = self

		self._rightOperand = rightOperand
		rightOperand.Parent = self

	@readonly
	def LeftOperand(self) -> ExpressionUnion:
		"""
		Read-only property to access the left operand (:attr:`_leftOperand`).

		:returns: The left operand.
		"""
		return self._leftOperand

	@readonly
	def RightOperand(self) -> ExpressionUnion:
		"""
		Read-only property to access the right operand (:attr:`_rightOperand`).

		:returns: The right operand.
		"""
		return self._rightOperand

	def Copy(self) -> Self:
		"""
		Create a copy of this binary expression.

		The copy has no parent. Its operands are copies of this expression's operands.

		:returns: The new binary expression.
		"""
		return self.__class__(self._leftOperand.Copy(), self._rightOperand.Copy())

	def __str__(self) -> str:
		"""
		Formats the binary expression.

		**Format:** ``lhs + rhs``

		:returns: Formatted binary expression.
		"""
		return "{leftOperator}{leftOperand!s}{middleOperator}{rightOperand!s}{rightOperator}".format(
			leftOperator=self._FORMAT[0],
			leftOperand=self._leftOperand,
			middleOperator=self._FORMAT[1],
			rightOperand=self._rightOperand,
			rightOperator=self._FORMAT[2],
		)


@export
@abstractclass
class RangeExpression(BinaryExpression):
	"""
	Represents the base-class of range expressions.

	A range has a direction (:data:`Direction`) and two bounds. Both operands are available as :data:`LeftOperand` and
	:data:`RightOperand`.

	.. seealso::

	   * :class:`Ascending range expression <pyVHDLModel.Expression.AscendingRangeExpression>`
	   * :class:`Descending range expression <pyVHDLModel.Expression.DescendingRangeExpression>`
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Range  #: The operator's precedence level.
	_DIRECTION:  ClassVar[Direction]                                      #: The range's direction (``to`` or ``downto``).

	@readonly
	def Direction(self) -> Direction:
		"""
		Read-only property to access the direction (:attr:`_DIRECTION`).

		:returns: The direction.
		"""
		return self._DIRECTION

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this range expression and its bounds with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRangeExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitDirection(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartRangeExpression(self)


@export
class AscendingRangeExpression(RangeExpression):
	"""
	Represents an ascending range expression (``to``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := v(0 to 3);
	      --       ^^^^^^     <- the range
	      --       ^          <- LeftOperand
	      --            ^     <- RightOperand
	"""
	_DIRECTION: ClassVar[Direction]            = Direction.To      #: The range's direction.
	_FORMAT:    ClassVar[tuple[str, str, str]] = ("", " to ", "")  #: The operator's string fragments.


@export
class DescendingRangeExpression(RangeExpression):
	"""
	Represents a descending range expression (``downto``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := v(7 downto 4);
	      --       ^^^^^^^^^^     <- the range
	      --       ^              <- LeftOperand
	      --                ^     <- RightOperand
	"""
	_DIRECTION: ClassVar[Direction]            = Direction.DownTo      #: The range's direction.
	_FORMAT:    ClassVar[tuple[str, str, str]] = ("", " downto ", "")  #: The operator's string fragments.


@export
@abstractclass
class AddingExpression(BinaryExpression):
	"""
	Represents the base-class of all adding expressions: ``+``, ``-`` and ``&``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Addition expression <pyVHDLModel.Expression.AdditionExpression>`
	   * :class:`Subtraction expression <pyVHDLModel.Expression.SubtractionExpression>`
	   * :class:`Concatenation expression <pyVHDLModel.Expression.ConcatenationExpression>`
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Adding  #: The operator's precedence level.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this adding expression and its operands with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAddingExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitOperator(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartAddingExpression(self)


@export
class AdditionExpression(AddingExpression):
	"""
	Represents an addition expression (``+``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs + rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " + ", "")  #: The operator's string fragments.


@export
class SubtractionExpression(AddingExpression):
	"""
	Represents a subtraction expression (``-``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs - rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " - ", "")  #: The operator's string fragments.


@export
class ConcatenationExpression(AddingExpression):
	"""
	Represents a concatenation expression (``&``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs & rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " & ", "")  #: The operator's string fragments.


@export
@abstractclass
class MultiplyingExpression(BinaryExpression):
	"""
	Represents the base-class of all multiplying expressions: ``*``, ``/``, ``rem``, ``mod`` and ``**``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Multiply expression <pyVHDLModel.Expression.MultiplyExpression>`
	   * :class:`Division expression <pyVHDLModel.Expression.DivisionExpression>`
	   * :class:`Remainder expression <pyVHDLModel.Expression.RemainderExpression>`
	   * :class:`Modulo expression <pyVHDLModel.Expression.ModuloExpression>`
	   * :class:`Exponentiation expression <pyVHDLModel.Expression.ExponentiationExpression>`
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Multiplying  #: The operator's precedence level.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this multiplying expression and its operands with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitMultiplyingExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitOperator(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartMultiplyingExpression(self)


@export
class MultiplyExpression(MultiplyingExpression):
	"""
	Represents a multiplication expression (``*``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs * rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " * ", "")  #: The operator's string fragments.


@export
class DivisionExpression(MultiplyingExpression):
	"""
	Represents a division expression (``/``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs / rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " / ", "")  #: The operator's string fragments.


@export
class RemainderExpression(MultiplyingExpression):
	"""
	Represents a remainder expression (``rem``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs rem rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " rem ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Rem   #: The operator's reserved word.


@export
class ModuloExpression(MultiplyingExpression):
	"""
	Represents a modulo expression (``mod``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs mod rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " mod ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Mod   #: The operator's reserved word.


@export
class ExponentiationExpression(MultiplyingExpression):
	"""
	Represents an exponentiation expression (``**``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ** rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence]   = OperatorPrecedence.Miscellaneous  #: The operator's precedence level.
	_FORMAT:     ClassVar[tuple[str, str, str]] = ("", "**", "")                    #: The operator's string fragments.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this exponentiation and its operands with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitExponentiationExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitOperator(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartExponentiationExpression(self)


@export
@abstractclass
class LogicalExpression(BinaryExpression):
	"""
	Represents the base-class of all binary logical expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`And expression <pyVHDLModel.Expression.AndExpression>`
	   * :class:`Nand expression <pyVHDLModel.Expression.NandExpression>`
	   * :class:`Or expression <pyVHDLModel.Expression.OrExpression>`
	   * :class:`Nor expression <pyVHDLModel.Expression.NorExpression>`
	   * :class:`Xor expression <pyVHDLModel.Expression.XorExpression>`
	   * :class:`Xnor expression <pyVHDLModel.Expression.XnorExpression>`
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Logical  #: The operator's precedence level.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this logical expression and its operands with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitLogicalExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitOperator(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartLogicalExpression(self)


@export
class AndExpression(LogicalExpression):
	"""
	Represents a logical ``and`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs and rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " and ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.And   #: The operator's reserved word.


@export
class NandExpression(LogicalExpression):
	"""
	Represents a logical ``nand`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs nand rhs;
	      --     ^^^^^^^^^^^^    <- the expression
	      --     ^^^             <- LeftOperand
	      --              ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " nand ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Nand   #: The operator's reserved word.


@export
class OrExpression(LogicalExpression):
	"""
	Represents a logical ``or`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs or rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " or ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Or   #: The operator's reserved word.


@export
class NorExpression(LogicalExpression):
	"""
	Represents a logical ``nor`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs nor rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " nor ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Nor   #: The operator's reserved word.


@export
class XorExpression(LogicalExpression):
	"""
	Represents a logical ``xor`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs xor rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " xor ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Xor   #: The operator's reserved word.


@export
class XnorExpression(LogicalExpression):
	"""
	Represents a logical ``xnor`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs xnor rhs;
	      --     ^^^^^^^^^^^^    <- the expression
	      --     ^^^             <- LeftOperand
	      --              ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " xnor ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Xnor   #: The operator's reserved word.


@export
@abstractclass
class RelationalExpression(BinaryExpression):
	"""
	Represents the base-class of all relational expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Equal expression <pyVHDLModel.Expression.EqualExpression>`
	   * :class:`Unequal expression <pyVHDLModel.Expression.UnequalExpression>`
	   * :class:`Greater than expression <pyVHDLModel.Expression.GreaterThanExpression>`
	   * :class:`Greater equal expression <pyVHDLModel.Expression.GreaterEqualExpression>`
	   * :class:`Less than expression <pyVHDLModel.Expression.LessThanExpression>`
	   * :class:`Less equal expression <pyVHDLModel.Expression.LessEqualExpression>`
	   * :class:`Matching relational expression <pyVHDLModel.Expression.MatchingRelationalExpression>`
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Relational  #: The operator's precedence level.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this relational expression and its operands with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRelationalExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitOperator(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartRelationalExpression(self)


@export
class EqualExpression(RelationalExpression):
	"""
	Represents an equality expression (``=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs = rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " = ", "")  #: The operator's string fragments.


@export
class UnequalExpression(RelationalExpression):
	"""
	Represents an inequality expression (``/=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs /= rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " /= ", "")  #: The operator's string fragments.


@export
class GreaterThanExpression(RelationalExpression):
	"""
	Represents a greater-than expression (``>``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs > rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " > ", "")  #: The operator's string fragments.


@export
class GreaterEqualExpression(RelationalExpression):
	"""
	Represents a greater-or-equal expression (``>=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs >= rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " >= ", "")  #: The operator's string fragments.


@export
class LessThanExpression(RelationalExpression):
	"""
	Represents a less-than expression (``<``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs < rhs;
	      --     ^^^^^^^^^    <- the expression
	      --     ^^^          <- LeftOperand
	      --           ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " < ", "")  #: The operator's string fragments.


@export
class LessEqualExpression(RelationalExpression):
	"""
	Represents a less-or-equal expression (``<=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs <= rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " <= ", "")  #: The operator's string fragments.


@export
@abstractclass
class MatchingRelationalExpression(RelationalExpression):
	"""
	Represents the base-class of all matching relational expressions.

	Matching operators return a ``bit``/``std_ulogic`` rather than a ``boolean``. Both operands are available as
	:data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Matching equal expression <pyVHDLModel.Expression.MatchingEqualExpression>`
	   * :class:`Matching unequal expression <pyVHDLModel.Expression.MatchingUnequalExpression>`
	   * :class:`Matching greater than expression <pyVHDLModel.Expression.MatchingGreaterThanExpression>`
	   * :class:`Matching greater equal expression <pyVHDLModel.Expression.MatchingGreaterEqualExpression>`
	   * :class:`Matching less than expression <pyVHDLModel.Expression.MatchingLessThanExpression>`
	   * :class:`Matching less equal expression <pyVHDLModel.Expression.MatchingLessEqualExpression>`
	"""
	pass


@export
class MatchingEqualExpression(MatchingRelationalExpression):
	"""
	Represents a matching equality expression (``?=``).

	Unlike ``=``, a matching operator returns a ``bit``/``std_ulogic``.
	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ?= rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " ?= ", "")  #: The operator's string fragments.


@export
class MatchingUnequalExpression(MatchingRelationalExpression):
	"""
	Represents a matching inequality expression (``?/=``).

	Unlike ``/=``, a matching operator returns a ``bit``/``std_ulogic``.
	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ?/= rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " ?/= ", "")  #: The operator's string fragments.


@export
class MatchingGreaterThanExpression(MatchingRelationalExpression):
	"""
	Represents a matching greater-than expression (``?>``).

	Unlike ``>``, a matching operator returns a ``bit``/``std_ulogic``.
	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ?> rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " ?> ", "")  #: The operator's string fragments.


@export
class MatchingGreaterEqualExpression(MatchingRelationalExpression):
	"""
	Represents a matching greater-or-equal expression (``?>=``).

	Unlike ``>=``, a matching operator returns a ``bit``/``std_ulogic``.
	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ?>= rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " ?>= ", "")  #: The operator's string fragments.


@export
class MatchingLessThanExpression(MatchingRelationalExpression):
	"""
	Represents a matching less-than expression (``?<``).

	Unlike ``<``, a matching operator returns a ``bit``/``std_ulogic``.
	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ?< rhs;
	      --     ^^^^^^^^^^    <- the expression
	      --     ^^^           <- LeftOperand
	      --            ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " ?< ", "")  #: The operator's string fragments.


@export
class MatchingLessEqualExpression(MatchingRelationalExpression):
	"""
	Represents a matching less-or-equal expression (``?<=``).

	Unlike ``<=``, a matching operator returns a ``bit``/``std_ulogic``.
	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ?<= rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT: ClassVar[tuple[str, str, str]] = ("", " ?<= ", "")  #: The operator's string fragments.


@export
@abstractclass
class ShiftExpression(BinaryExpression):
	"""
	Represents the base-class of all shift and rotate expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Shift logic expression <pyVHDLModel.Expression.ShiftLogicExpression>`
	   * :class:`Shift arithmetic expression <pyVHDLModel.Expression.ShiftArithmeticExpression>`
	   * :class:`Rotate expression <pyVHDLModel.Expression.RotateExpression>`
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence] = OperatorPrecedence.Shift  #: The operator's precedence level.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this shift or rotate expression and its operands with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitShiftExpression(self)
		self._leftOperand.Visit(visitor)
		visitor.VisitOperator(self)
		self._rightOperand.Visit(visitor)
		visitor.DepartShiftExpression(self)


@export
@abstractclass
class ShiftLogicExpression(ShiftExpression):
	"""
	Represents the base-class of the logical shift expressions ``srl`` and ``sll``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Shift right logic expression <pyVHDLModel.Expression.ShiftRightLogicExpression>`
	   * :class:`Shift left logic expression <pyVHDLModel.Expression.ShiftLeftLogicExpression>`
	"""
	pass


@export
@abstractclass
class ShiftArithmeticExpression(ShiftExpression):
	"""
	Represents the base-class of the arithmetic shift expressions ``sra`` and ``sla``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Shift right arithmetic expression <pyVHDLModel.Expression.ShiftRightArithmeticExpression>`
	   * :class:`Shift left arithmetic expression <pyVHDLModel.Expression.ShiftLeftArithmeticExpression>`
	"""
	pass


@export
@abstractclass
class RotateExpression(ShiftExpression):
	"""
	Represents the base-class of the rotate expressions ``ror`` and ``rol``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. seealso::

	   * :class:`Rotate right expression <pyVHDLModel.Expression.RotateRightExpression>`
	   * :class:`Rotate left expression <pyVHDLModel.Expression.RotateLeftExpression>`
	"""
	pass


@export
class ShiftRightLogicExpression(ShiftLogicExpression):
	"""
	Represents a logical right shift expression (``srl``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs srl rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " srl ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Srl   #: The operator's reserved word.


@export
class ShiftLeftLogicExpression(ShiftLogicExpression):
	"""
	Represents a logical left shift expression (``sll``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs sll rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " sll ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Sll   #: The operator's reserved word.


@export
class ShiftRightArithmeticExpression(ShiftArithmeticExpression):
	"""
	Represents an arithmetic right shift expression (``sra``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs sra rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " sra ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Sra   #: The operator's reserved word.


@export
class ShiftLeftArithmeticExpression(ShiftArithmeticExpression):
	"""
	Represents an arithmetic left shift expression (``sla``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs sla rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " sla ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Sla   #: The operator's reserved word.


@export
class RotateRightExpression(RotateExpression):
	"""
	Represents a right rotate expression (``ror``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs ror rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " ror ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Ror   #: The operator's reserved word.


@export
class RotateLeftExpression(RotateExpression):
	"""
	Represents a left rotate expression (``rol``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := lhs rol rhs;
	      --     ^^^^^^^^^^^    <- the expression
	      --     ^^^            <- LeftOperand
	      --             ^^^    <- RightOperand
	"""
	_FORMAT:        ClassVar[tuple[str, str, str]] = ("", " rol ", "")  #: The operator's string fragments.
	_RESERVED_WORD: ClassVar[ReservedWord]         = ReservedWord.Rol   #: The operator's reserved word.


@export
class QualifiedExpression(BaseExpression, ParenthesisExpression):
	"""
	Represents a qualified expression.

	A qualified expression states the subtype (:data:`Subtype`) of its operand (:data:`Operand`),
	resolving which of several overloaded meanings is intended.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := byte'(others => '0');
	      --     ^^^^                    <- Subtype
	      --          ^^^^^^^^^^^^^^^    <- Operand
	"""
	_operand:  ExpressionUnion  #: The expression being qualified.
	_subtype:  Symbol           #: Reference to the subtype qualifying the expression.

	def __init__(self, subtype: Symbol, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a qualified expression.

		:param subtype: Reference to the subtype qualifying the expression.
		:param operand: The expression being qualified.
		:param parent:  The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._operand = operand
		operand.Parent = self

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Operand(self) -> ExpressionUnion:
		"""
		Read-only property to access the operand (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	@readonly
	def Subtype(self) -> Symbol:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	def Copy(self) -> Self:
		"""
		Create a copy of this qualified expression.

		The copy has no parent. Its subtype and operand are copies of this expression's subtype and operand.

		:returns: The new qualified expression.
		"""
		return self.__class__(self._subtype.Copy(), self._operand.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this qualified expression, its subtype and its operand with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitQualifiedExpression(self)
		self._subtype.Visit(visitor)
		visitor.VisitApostrophe(self)
		self._operand.Visit(visitor)
		visitor.DepartQualifiedExpression(self)

	def __str__(self) -> str:
		"""
		Formats the qualified expression.

		**Format:** ``byte'(val)``

		:returns: Formatted qualified expression.
		"""
		return f"{self._subtype}'({self._operand!s})"


@export
@abstractclass
class TernaryExpression(BaseExpression):
	"""
	Represents the base-class of all ternary expressions.

	.. seealso::

	   * :class:`When else expression <pyVHDLModel.Expression.WhenElseExpression>`
	"""

	_PRECEDENCE:    ClassVar[OperatorPrecedence]         #: The operator's precedence level.
	_FORMAT:        ClassVar[tuple[str, str, str, str]]  #: The operator's string representation as four fragments.
	_firstOperand:  ExpressionUnion                      #: The operator's first operand.
	_secondOperand: ExpressionUnion                      #: The operator's second operand.
	_thirdOperand:  ExpressionUnion                      #: The operator's third operand.

	def __init__(
		self,
		firstOperand: ExpressionUnion,
		secondOperand: ExpressionUnion,
		thirdOperand: ExpressionUnion,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a ternary expression.

		:param firstOperand:  The operator's first operand.
		:param secondOperand: The operator's second operand.
		:param thirdOperand:  The operator's third operand.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._firstOperand = firstOperand
		firstOperand.Parent = self

		self._secondOperand = secondOperand
		secondOperand.Parent = self

		self._thirdOperand = thirdOperand
		thirdOperand.Parent = self

	def __str__(self) -> str:
		"""
		Formats the ternary expression.

		**Format:** ``val when cond else other``

		:returns: Formatted ternary expression.
		"""
		return "{beforeFirstOperator}{firstOperand!s}{beforeSecondOperator}{secondOperand!s}{beforeThirdOperator}{thirdOperand!s}{lastOperator}".format(
			beforeFirstOperator=self._FORMAT[0],
			firstOperand=self._firstOperand,
			beforeSecondOperator=self._FORMAT[1],
			secondOperand=self._secondOperand,
			beforeThirdOperator=self._FORMAT[2],
			thirdOperand=self._thirdOperand,
			lastOperator=self._FORMAT[3],
		)


@export
class WhenElseExpression(TernaryExpression):
	"""
	Represents a conditional expression.

	A conditional expression selects between two values (:data:`ThenValue`, :data:`ElseValue`) based on
	a condition (:data:`Condition`). It is usable anywhere an expression is expected - distinct from
	:class:`~pyVHDLModel.Common.ConditionalExpression`, which models the cascading ``when``/``else``
	list of a conditional *assignment*.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a when f else b;
	      --     ^                  <- ThenValue
	      --            ^           <- Condition
	      --                   ^    <- ElseValue
	"""
	_PRECEDENCE: ClassVar[OperatorPrecedence]        = OperatorPrecedence.Conditional  #: The operator's precedence level.
	_FORMAT:     ClassVar[tuple[str, str, str, str]] = ("", " when ", " else ", "")    #: The operator's string fragments.

	def __init__(
		self,
		thenValue: ExpressionUnion,
		condition: ExpressionUnion,
		elseValue: ExpressionUnion,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a conditional expression.

		:param thenValue: The value if the condition holds.
		:param condition: The condition selecting between both values.
		:param elseValue: The value if the condition does not hold.
		:param parent:    The parent model entity of this entity.
		"""
		super().__init__(thenValue, condition, elseValue, parent)

	@readonly
	def ThenValue(self) -> ExpressionUnion:
		"""
		Read-only property to access the then value (:attr:`_firstOperand`).

		:returns: The then value.
		"""
		return self._firstOperand

	@readonly
	def Condition(self) -> ExpressionUnion:
		"""
		Read-only property to access the condition (:attr:`_secondOperand`).

		:returns: The condition.
		"""
		return self._secondOperand

	@readonly
	def ElseValue(self) -> ExpressionUnion:
		"""
		Read-only property to access the else value (:attr:`_thirdOperand`).

		:returns: The else value.
		"""
		return self._thirdOperand

	def Copy(self) -> Self:
		"""
		Create a copy of this conditional expression.

		The copy has no parent. Its values and condition are copies of this expression's values and condition.

		:returns: The new conditional expression.
		"""
		return self.__class__(self._firstOperand.Copy(), self._secondOperand.Copy(), self._thirdOperand.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this conditional expression, its value, condition and alternative value with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitWhenElseExpression(self)
		self._firstOperand.Visit(visitor)
		visitor.VisitWhen(self)
		self._secondOperand.Visit(visitor)
		visitor.VisitElse(self)
		self._thirdOperand.Visit(visitor)
		visitor.DepartWhenElseExpression(self)


@export
class FunctionCall(BaseExpression):
	"""
	Represents a call to a function.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := maximum(a, b);
	      --     ^^^^^^^^^^^^^    <- the call
	"""
	def Copy(self) -> Self:
		"""
		Create a copy of this function call.

		The copy has no parent.

		:returns: The new function call.
		"""
		return self.__class__()


@export
@abstractclass
class Allocation(BaseExpression):
	"""
	Represents the base-class of all allocations via ``new``.

	.. seealso::

	   * :class:`Subtype allocation <pyVHDLModel.Expression.SubtypeAllocation>`
	   * :class:`Qualified expression allocation <pyVHDLModel.Expression.QualifiedExpressionAllocation>`
	"""
	pass


@export
class SubtypeAllocation(Allocation):
	"""
	Represents an allocation of a subtype via ``new``.

	The allocated subtype is available as :data:`Subtype`. The allocated object is default-initialized.

	.. admonition:: Example

	   .. code-block:: VHDL

	      p := new integer;
	      --       ^^^^^^^    <- Subtype
	"""
	_subtype: Symbol  #: Reference to the subtype being allocated.

	def __init__(self, subtype: Symbol, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an allocation of a subtype via ``new``.

		:param subtype: Reference to the subtype being allocated.
		:param parent:  The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Subtype(self) -> Symbol:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	def Copy(self) -> Self:
		"""
		Create a copy of this subtype allocation.

		The copy has no parent. Its subtype is a copy of this allocation's subtype.

		:returns: The new subtype allocation.
		"""
		return self.__class__(self._subtype.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this allocation and its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSubtypeAllocation(self)
		self._subtype.Visit(visitor)
		visitor.DepartSubtypeAllocation(self)

	def __str__(self) -> str:
		"""
		Formats the subtype allocation.

		**Format:** ``new node``

		:returns: Formatted subtype allocation.
		"""
		return f"new {self._subtype!s}"


@export
class QualifiedExpressionAllocation(Allocation):
	"""
	Represents an allocation initialized by a qualified expression.

	The qualified expression providing the initial value is available as :data:`QualifiedExpression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      p := new integer'(5);
	      --       ^^^^^^^^^^^    <- QualifiedExpression
	"""
	_qualifiedExpression: QualifiedExpression  #: The qualified expression the allocated object is initialized with.

	def __init__(self, qualifiedExpression: QualifiedExpression, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an allocation initialized by a qualified expression.

		:param qualifiedExpression: The qualified expression the allocated object is initialized with.
		:param parent:              The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._qualifiedExpression = qualifiedExpression
		qualifiedExpression.Parent = self

	@readonly
	def QualifiedExpression(self) -> QualifiedExpression:
		"""
		Read-only property to access the qualified expression (:attr:`_qualifiedExpression`).

		:returns: The qualified expression.
		"""
		return self._qualifiedExpression

	def Copy(self) -> Self:
		"""
		Create a copy of this qualified expression allocation.

		The copy has no parent. Its qualified expression is a copy of this allocation's qualified expression.

		:returns: The new qualified expression allocation.
		"""
		return self.__class__(self._qualifiedExpression.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this allocation and its qualified expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitQualifiedExpressionAllocation(self)
		self._qualifiedExpression.Visit(visitor)
		visitor.DepartQualifiedExpressionAllocation(self)

	def __str__(self) -> str:
		"""
		Formats the qualified expression allocation.

		**Format:** ``new byte'(val)``

		:returns: Formatted qualified expression allocation.
		"""
		return f"new {self._qualifiedExpression!s}"


@export
@abstractclass
class AggregateElement(ModelEntity):
	"""
	Represents the base-class of all aggregate elements.

	Every element carries the value assigned to it (:data:`Expression`).

	.. seealso::

	   * :class:`Simple aggregate element <pyVHDLModel.Expression.SimpleAggregateElement>`
	   * :class:`Indexed aggregate element <pyVHDLModel.Expression.IndexedAggregateElement>`
	   * :class:`Ranged aggregate element <pyVHDLModel.Expression.RangedAggregateElement>`
	   * :class:`Named aggregate element <pyVHDLModel.Expression.NamedAggregateElement>`
	   * :class:`Others aggregate element <pyVHDLModel.Expression.OthersAggregateElement>`
	"""

	_expression: ExpressionUnion  #: The expression this aggregate element supplies.

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an aggregate element.

		:param expression: The expression this aggregate element supplies.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression

	def Copy(self) -> Self:
		"""
		Create a copy of this aggregate element.

		The copy has no parent. Its expression is a copy of this element's expression.

		:returns: The new aggregate element.
		"""
		return self.__class__(self._expression.Copy())


@export
class SimpleAggregateElement(AggregateElement):
	"""
	Represents an aggregate element given by position.

	A positional element has no choice of its own; only its value (:data:`Expression`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := ('1', '0', '1', '0', '1', '0', '1', '0');
	      --      ^^^                                        <- Expression
	"""
	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this positional aggregate element and its expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSimpleAggregateElement(self)
		self._expression.Visit(visitor)
		visitor.DepartSimpleAggregateElement(self)

	def __str__(self) -> str:
		"""
		Formats the simple aggregate element.

		**Format:** ``val``

		:returns: Formatted simple aggregate element.
		"""
		return str(self._expression)


@export
class IndexedAggregateElement(AggregateElement):
	"""
	Represents an aggregate element chosen by an index.

	The index is available as :data:`Index`, the assigned value as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := (0 => '1', others => '0');
	      --      ^                           <- Index
	      --           ^^^                    <- Expression
	"""
	_index: ExpressionUnion  #: The index expression selecting the element this value is assigned to.

	def __init__(self, index: ExpressionUnion, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an aggregate element chosen by an index.

		:param index:      The index expression selecting the element this value is assigned to.
		:param expression: The expression this aggregate element supplies.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(expression, parent)

		self._index = index

	@readonly
	def Index(self) -> ExpressionUnion:
		"""
		Read-only property to access the index expression (:attr:`_index`).

		:returns: The index expression.
		"""
		return self._index

	def Copy(self) -> Self:
		"""
		Create a copy of this indexed aggregate element.

		The copy has no parent. Its index and expression are copies of this element's index and expression.

		:returns: The new indexed aggregate element.
		"""
		return self.__class__(self._index.Copy(), self._expression.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this aggregate element, its index and its expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitIndexedAggregateElement(self)
		self._index.Visit(visitor)
		visitor.VisitArrow(self)
		self._expression.Visit(visitor)
		visitor.DepartIndexedAggregateElement(self)

	def __str__(self) -> str:
		"""
		Formats the indexed aggregate element.

		**Format:** ``0 => val``

		:returns: Formatted indexed aggregate element.
		"""
		return f"{self._index!s} => {self._expression!s}"


@export
class RangedAggregateElement(AggregateElement):
	"""
	Represents an aggregate element chosen by a range.

	The range is available as :data:`Range`, the assigned value as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := (1 to 3 => '0', others => '1');
	      --      ^^^^^^                           <- Range
	      --                ^^^                    <- Expression
	"""
	_range: Range  #: The range selecting the elements this value is assigned to.

	def __init__(self, rng: Range, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an aggregate element chosen by a range.

		:param rng:        The range selecting the elements this value is assigned to.
		:param expression: The expression this aggregate element supplies.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(expression, parent)

		self._range = rng
		rng.Parent = self

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	def Copy(self) -> Self:
		"""
		Create a copy of this ranged aggregate element.

		The copy has no parent. Its range and expression are copies of this element's range and expression.

		:returns: The new ranged aggregate element.
		"""
		return self.__class__(self._range.Copy(), self._expression.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this aggregate element, its range and its expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRangedAggregateElement(self)
		self._range.Visit(visitor)
		visitor.VisitArrow(self)
		self._expression.Visit(visitor)
		visitor.DepartRangedAggregateElement(self)

	def __str__(self) -> str:
		"""
		Formats the ranged aggregate element.

		**Format:** ``0 to 3 => val``

		:returns: Formatted ranged aggregate element.
		"""
		return f"{self._range!s} => {self._expression!s}"


@export
class NamedAggregateElement(AggregateElement):
	"""
	Represents an aggregate element chosen by a name.

	Used for record aggregates, where the choice names a record element (:data:`Name`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      r := (a => '1', b => '0');
	      --    ^                      <- Name
	      --         ^^^               <- Expression
	"""
	_name: Symbol  #: Reference to the name selecting the element this value is assigned to.

	def __init__(self, name: Symbol, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an aggregate element chosen by a name.

		:param name:       Reference to the name selecting the element this value is assigned to.
		:param expression: The expression this aggregate element supplies.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(expression, parent)

		self._name = name
		name.Parent = self

	@readonly
	def Name(self) -> Symbol:
		"""
		Read-only property to access the name (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	def Copy(self) -> Self:
		"""
		Create a copy of this named aggregate element.

		The copy has no parent. Its name and expression are copies of this element's name and expression.

		:returns: The new named aggregate element.
		"""
		return self.__class__(self._name.Copy(), self._expression.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this aggregate element, its name and its expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitNamedAggregateElement(self)
		self._name.Visit(visitor)
		visitor.VisitArrow(self)
		self._expression.Visit(visitor)
		visitor.DepartNamedAggregateElement(self)

	def __str__(self) -> str:
		"""
		Formats the named aggregate element.

		**Format:** ``elem => val``

		:returns: Formatted named aggregate element.
		"""
		return "{name!s} => {value!s}".format(
			name=self._name,
			value=self._expression,
		)


@export
class OthersAggregateElement(AggregateElement):
	"""
	Represents the ``others`` element of an aggregate.

	It supplies the value (:data:`Expression`) for every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := (0 => '1', others => '0');
	      --                ^^^^^^            <- the choice
	      --                          ^^^     <- Expression
	"""
	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this ``others`` aggregate element and its expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitOthersAggregateElement(self)
		self._expression.Visit(visitor)
		visitor.DepartOthersAggregateElement(self)

	def __str__(self) -> str:
		"""
		Formats the ``others`` aggregate element.

		**Format:** ``others => val``

		:returns: Formatted ``others`` aggregate element.
		"""
		return "others => {value!s}".format(
			value=self._expression,
		)


@export
class Aggregate(BaseExpression):
	"""
	Represents an aggregate.

	An aggregate composes a value from its elements (:data:`Elements`), each of which associates a
	choice with a value.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := (0 => '1', 1 to 3 => '0', others => '1');
	      --     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    <- Elements
	"""
	_elements: list[AggregateElement]  #: List of all elements of this aggregate, in the order they were written.

	def __init__(self, elements: Iterable[AggregateElement], parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an aggregate.

		:param elements: List of all elements of this aggregate, in the order they were written.
		:param parent:   The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._elements = elementList = []
		for element in elements:
			elementList.append(element)
			element.Parent = self

	@readonly
	def Elements(self) -> list[AggregateElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements

	def Copy(self) -> Self:
		"""
		Create a copy of this aggregate.

		The copy has no parent. Its elements are copies of this aggregate's elements.

		:returns: The new aggregate.
		"""
		return self.__class__([element.Copy() for element in self._elements])

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this aggregate and its elements with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAggregate(self)
		for position, element in enumerate(self._elements):
			if position > 0:
				visitor.VisitComma(self)

			element.Visit(visitor)

		visitor.DepartAggregate(self)

	def __str__(self) -> str:
		"""
		Formats the aggregate.

		**Format:** ``(1, others => 0)``

		:returns: Formatted aggregate.
		"""
		choices = [str(element) for element in self._elements]
		return "({choices})".format(
			choices=", ".join(choices)
		)
