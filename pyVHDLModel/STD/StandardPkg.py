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
"""This module contains the predefined package ``std.standard`` of VHDL library ``STD``."""

from pyTooling.Decorators    import export
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Base        import SimpleRange, Direction, Mode
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Expression  import EnumerationLiteral, CharacterEnumerationLiteral, IntegerLiteral, \
                                    FloatingPointLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Type        import EnumeratedType, IntegerType, RealType, PhysicalType, PhysicalUnit, ArrayType, \
                                    Subtype, LogicalOperatorsMixin, MatchingOperatorsMixin
from pyVHDLModel.Interface   import ParameterSimpleSignalInterfaceItem
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Subprogram  import Function, PredefinedFunction, PredefinedOperation
from pyVHDLModel.Predefined  import PredefinedPackage, PredefinedPackageBody


@export
class EdgeFunctionsMixin(metaclass=ExtendedType, mixin=True, expects=("_TypeMark", "_Function")):
	"""
	A mixin-class for the enumerated types declaring the functions ``rising_edge`` and ``falling_edge`` (IEEE Std
	1076-2008, 16.3): ``boolean`` and ``bit`` of package ``std.standard``.

	.. seealso::

	   * :class:`Boolean <pyVHDLModel.STD.StandardPkg.Boolean>`
	   * :class:`Bit <pyVHDLModel.STD.StandardPkg.Bit>`
	"""

	def _CreateEdgeFunctions(self) -> list[PredefinedFunction]:
		"""
		Create the functions ``rising_edge`` and ``falling_edge`` of this type: ``(signal S : <type>) return BOOLEAN``.

		:returns: List of predefined functions.
		"""
		functions = []
		for identifier in ("rising_edge", "falling_edge"):
			functions.append(self._Function(
				identifier,
				SimpleSubtypeSymbol(SimpleName("boolean")),
				(ParameterSimpleSignalInterfaceItem(("S", ), Mode.In, self._TypeMark()), )
			))

		return functions


@export
class Boolean(EnumeratedType, LogicalOperatorsMixin, EdgeFunctionsMixin):
	"""
	Represents the predefined type ``boolean`` of package ``std.standard``: ``(false, true)``.

	Besides the operations of an enumerated type, it declares the logical operators (IEEE Std 1076-2008, 9.2.2) and the
	functions ``rising_edge`` and ``falling_edge`` (16.3).
	"""

	def __init__(self) -> None:
		"""
		Initializes the type ``boolean``.
		"""
		super().__init__("boolean", (EnumerationLiteral("false"), EnumerationLiteral("true")))

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, the logical operators, then
		``rising_edge`` and ``falling_edge``.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateLogicalOperators())
		operations.extend(self._CreateEdgeFunctions())

		return operations


@export
class Bit(EnumeratedType, LogicalOperatorsMixin, MatchingOperatorsMixin, EdgeFunctionsMixin):
	"""
	Represents the predefined type ``bit`` of package ``std.standard``: ``('0', '1')``.

	Besides the operations of an enumerated type, it declares the logical operators (IEEE Std 1076-2008, 9.2.2), the
	condition operator ``"??"`` (9.2.9), the matching relational operators (9.2.3) and the functions ``rising_edge`` and
	``falling_edge`` (16.3).
	"""

	def __init__(self) -> None:
		"""
		Initializes the type ``bit``.
		"""
		super().__init__("bit", (CharacterEnumerationLiteral("0"), CharacterEnumerationLiteral("1")))

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, the logical operators, the
		condition operator ``"??"``, the matching relational operators ``"?="``, ``"?/="``, ``"?<"``, ``"?<="``,
		``"?>"`` and ``"?>="``, then ``rising_edge`` and ``falling_edge``.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateLogicalOperators())
		operations.append(self._UnaryOperator("??", SimpleSubtypeSymbol(SimpleName("boolean"))))
		operations.extend(self._CreateMatchingOperators())
		operations.extend(self._CreateEdgeFunctions())

		return operations


@export
class Standard(PredefinedPackage):
	"""
	Predefined package ``std.standard`` (IEEE Std 1076-2008, 16.3).

	Its declarations, in the order of the standard:

	* types ``boolean``, ``bit``, ``character``, ``severity_level``, ``integer``, ``real`` and ``time``
	* subtype ``delay_length`` and function ``now``
	* subtypes ``natural`` and ``positive``
	* types ``string``, ``boolean_vector``, ``bit_vector``, ``integer_vector``, ``real_vector`` and ``time_vector``
	* types ``file_open_kind`` and ``file_open_status``
	* attribute ``foreign``

	With :data:`VHDLVersion.VHDL2019 <pyVHDLModel.VHDLVersion.VHDL2019>`, it declares the additions of IEEE Std
	1076-2019, 16.3: the type ``range_direction`` before ``boolean``, the literal ``read_write_mode`` of
	``file_open_kind`` and the types ``file_open_state`` and ``file_origin_kind`` after ``file_open_status``. The
	implicitly defined range record types (``boolean_range_record``, ...) aren't declared.

	The types declare their predefined operations (:attr:`~pyVHDLModel.Type.FullType.ImplicitOperations`). The
	implementation-defined ranges are GHDL's: ``integer`` has 32 bits, ``real`` is an IEEE 754 double, ``time`` counts
	femtoseconds in 64 bits.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.StandardPkg.Standard_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``standard`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		if vhdlVersion is VHDLVersion.VHDL2019:
			directions =     "ascending", "descending"
			rangeDirection = EnumeratedType("range_direction", [EnumerationLiteral(direction) for direction in directions])
			self._DeclareItem(rangeDirection, self._types)

		self._DeclareItem(Boolean(), self._types)
		self._DeclareItem(Bit(), self._types)

		controlCharacters = \
			"nul", "soh", "stx", "etx", "eot", "enq", "ack", "bel", "bs",  "ht",  "lf",  "vt",  "ff",  "cr",  "so",  "si", \
			"dle", "dc1", "dc2", "dc3", "dc4", "nak", "syn", "etb", "can", "em",  "sub", "esc", "fsp", "gsp", "rsp", "usp"
		characters = []
		for position in range(256):
			if position < 32:
				characters.append(EnumerationLiteral(controlCharacters[position]))
			elif position == 127:
				characters.append(EnumerationLiteral("del"))
			elif 128 <= position < 160:
				characters.append(EnumerationLiteral(f"c{position}"))
			else:
				characters.append(CharacterEnumerationLiteral(chr(position)))

		self._DeclareItem(EnumeratedType("character", characters), self._types)

		levels = "note", "warning", "error", "failure"
		self._DeclareItem(EnumeratedType("severity_level", [EnumerationLiteral(level) for level in levels]), self._types)

		integer = IntegerType("integer", SimpleRange(IntegerLiteral(-2**31), IntegerLiteral(2**31 - 1), Direction.To))
		self._DeclareItem(integer, self._types)

		realRange = SimpleRange(
			FloatingPointLiteral(-1.7976931348623157e308),
			FloatingPointLiteral(1.7976931348623157e308),
			Direction.To
		)
		self._DeclareItem(RealType("real", realRange), self._types)

		time = PhysicalType(
			"time",
			SimpleRange(IntegerLiteral(-2**63), IntegerLiteral(2**63 - 1), Direction.To),
			primaryUnit=PhysicalUnit("fs"),
			secondaryUnits=(
				PhysicalUnit("ps",  PhysicalIntegerLiteral(1000, "fs")),
				PhysicalUnit("ns",  PhysicalIntegerLiteral(1000, "ps")),
				PhysicalUnit("us",  PhysicalIntegerLiteral(1000, "ns")),
				PhysicalUnit("ms",  PhysicalIntegerLiteral(1000, "us")),
				PhysicalUnit("sec", PhysicalIntegerLiteral(1000, "ms")),
				PhysicalUnit("min", PhysicalIntegerLiteral(60, "sec")),
				PhysicalUnit("hr",  PhysicalIntegerLiteral(60, "min")),
			)
		)
		self._DeclareItem(time, self._types)

		delayLengthRange =      SimpleRange(
			PhysicalIntegerLiteral(0, "fs"),
			PhysicalIntegerLiteral(2**63 - 1, "fs"),
			Direction.To
		)
		delayLengthSymbol =     ConstrainedScalarSubtypeSymbol(SimpleName("time"), delayLengthRange)
		delayLength =           Subtype("delay_length", delayLengthSymbol)
		delayLength._baseType = time
		self._DeclareItem(delayLength, self._subtypes)

		now =                    Function("now", self._TypeMark("delay_length"), isPure=False)
		self._DeclareSubprogram(now, self._functions)

		for identifier, low in (
			("natural",  0),
			("positive", 1)
		):
			subtypeRange =      SimpleRange(IntegerLiteral(low), IntegerLiteral(2**31 - 1), Direction.To)
			subtype =           Subtype(identifier, ConstrainedScalarSubtypeSymbol(SimpleName("integer"), subtypeRange))
			subtype._baseType = integer
			self._DeclareItem(subtype, self._subtypes)

		self._DeclareItem(ArrayType("string", (self._TypeMark("positive"),), self._TypeMark("character")), self._types)
		for identifier, element in (
			("boolean_vector", "boolean"),
			("bit_vector",     "bit"),
			("integer_vector", "integer"),
			("real_vector",    "real"),
			("time_vector",    "time")
		):
			self._DeclareItem(ArrayType(identifier, (self._TypeMark("natural"),), self._TypeMark(element)), self._types)

		if vhdlVersion is VHDLVersion.VHDL2019:
			kinds = "read_mode", "read_write_mode", "write_mode", "append_mode"
		else:
			kinds = "read_mode", "write_mode", "append_mode"
		self._DeclareItem(EnumeratedType("file_open_kind", [EnumerationLiteral(kind) for kind in kinds]), self._types)

		statuses =       "open_ok", "status_error", "name_error", "mode_error"
		fileOpenStatus = EnumeratedType("file_open_status", [EnumerationLiteral(status) for status in statuses])
		self._DeclareItem(fileOpenStatus, self._types)

		if vhdlVersion is VHDLVersion.VHDL2019:
			for identifier, literals in (
				("file_open_state",  ("state_open", "state_closed")),
				("file_origin_kind", ("file_origin_begin", "file_origin_current", "file_origin_end"))
			):
				enumeration = EnumeratedType(identifier, [EnumerationLiteral(literal) for literal in literals])
				self._DeclareItem(enumeration, self._types)

		self.AddDeclaredItem(Attribute("foreign", self._TypeMark("string")))


@export
class Standard_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``std.standard``.

	.. seealso::

	   Matching :class:`Package <pyVHDLModel.STD.StandardPkg.Standard>` declaration.
	"""
