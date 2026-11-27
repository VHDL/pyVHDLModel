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
"""This module contains library and package declarations for VHDL library ``STD``."""

from typing                  import Iterable, Optional as Nullable

from pyTooling.Decorators    import export

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Base        import SimpleRange, Direction, Mode
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                                    SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression  import EnumerationLiteral, CharacterEnumerationLiteral, IntegerLiteral, \
                                    FloatingPointLiteral, PhysicalIntegerLiteral, StringLiteral, ConcatenationExpression
from pyVHDLModel.Type        import EnumeratedType, IntegerType, RealType, PhysicalType, PhysicalUnit, ArrayType, \
                                    AccessType, FileType, Subtype, RecordType, RecordTypeElement, \
                                    LogicalOperatorsMixin, MatchingOperatorsMixin
from pyVHDLModel.Object      import File, DeferredConstant
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                    ParameterFileInterfaceItem
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Subprogram  import Procedure, Function, Operator, PredefinedOperation
from pyVHDLModel.Predefined  import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody


@export
class Boolean(EnumeratedType, LogicalOperatorsMixin):
	"""
	Represents the predefined type ``boolean`` of package ``std.standard``: ``(false, true)``.

	Besides the operations of an enumerated type, it declares the logical operators (IEEE Std 1076-2008, 9.2.2).
	"""

	def __init__(self) -> None:
		"""
		Initializes the type ``boolean``.
		"""
		super().__init__("boolean", (EnumerationLiteral("false"), EnumerationLiteral("true")))

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, then the logical operators.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateLogicalOperators())

		return operations


@export
class Bit(EnumeratedType, LogicalOperatorsMixin, MatchingOperatorsMixin):
	"""
	Represents the predefined type ``bit`` of package ``std.standard``: ``('0', '1')``.

	Besides the operations of an enumerated type, it declares the logical operators (IEEE Std 1076-2008, 9.2.2), the
	condition operator ``"??"`` (9.2.9) and the matching relational operators (9.2.3).
	"""

	def __init__(self) -> None:
		"""
		Initializes the type ``bit``.
		"""
		super().__init__("bit", (CharacterEnumerationLiteral("0"), CharacterEnumerationLiteral("1")))

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, the logical operators, the
		condition operator ``"??"`` and the matching relational operators ``"?="``, ``"?/="``, ``"?<"``, ``"?<="``,
		``"?>"`` and ``"?>="``.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateLogicalOperators())
		operations.append(self._UnaryOperator("??", SimpleSubtypeSymbol(SimpleName("boolean"))))
		operations.extend(self._CreateMatchingOperators())

		return operations


@export
class Std(PredefinedLibrary):
	"""
	Predefined VHDL library ``std``.

	The following predefined packages are in this library:

	* :class:`~pyVHDLModel.STD.Standard`
	* :class:`~pyVHDLModel.STD.Env`
	* :class:`~pyVHDLModel.STD.TextIO`

	.. seealso::

	   Other predefined libraries:
	     * Library :class:`~pyVHDLModel.IEEE.Ieee`
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std`` library.

		:param vhdlVersion: Optional, the VHDL version of the library's packages. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(PACKAGES, vhdlVersion)


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

	   Matching :class:`Package Body <pyVHDLModel.STD.Standard_Body>` declaration.
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

	   Matching :class:`Package <pyVHDLModel.STD.Standard>` declaration.
	"""


@export
class TextIO(PredefinedPackage):
	"""
	Predefined package ``std.textio`` (IEEE Std 1076-2008, 16.4).

	Its declarations, in the order of the standard:

	* types ``line``, ``text`` and ``side``, subtype ``width`` and function ``justify``
	* files ``input`` and ``output``
	* the input procedures ``readline``, ``read``, ``sread``, ``oread`` and ``hread``
	* the output procedures ``writeline``, ``tee``, ``write``, ``owrite`` and ``hwrite``

	The aliases of the standard (``string_read``, ``bread``, ``swrite``, ``hex_write``, ...) aren't declared.

	With :data:`VHDLVersion.VHDL2019 <pyVHDLModel.VHDLVersion.VHDL2019>`, it declares the addition of IEEE Std
	1076-2019, 16.4: the type ``line_vector`` after ``line``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.TextIO_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``textio`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._DeclareItem(AccessType("line", self._TypeMark("string")), self._types)
		if vhdlVersion is VHDLVersion.VHDL2019:
			lineVector = ArrayType("line_vector", (self._TypeMark("natural"),), self._TypeMark("line"))
			self._DeclareItem(lineVector, self._types)

		self._DeclareItem(FileType("text", self._TypeMark("string")), self._types)
		self._DeclareItem(EnumeratedType("side", (EnumerationLiteral("right"), EnumerationLiteral("left"))), self._types)
		self._DeclareItem(Subtype("width", self._TypeMark("natural")), self._subtypes)
		self._DeclareSubprogram(
			Function("justify", self._TypeMark("string"), parameterItems=(
				self._InParameter(("VALUE",), self._TypeMark("string")),
				*self._JustificationParameters()
			)),
			self._functions
		)

		for identifier in ("input", "output"):
			file =                    File((identifier,), self._TypeMark("text"))
			self._files[identifier] = file
			self.AddDeclaredItem(file)

		self._DeclareSubprogram(
			Procedure("readline", parameterItems=(
				ParameterFileInterfaceItem(("F",), self._TypeMark("text")),
				self._LineParameter()
			)),
			self._procedures
		)
		for subtype in ("bit", "bit_vector", "boolean", "character", "integer", "real", "string", "time"):
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark(subtype)),
					self._OutParameter(("GOOD",), self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark(subtype))
				)),
				self._procedures
			)

		self._DeclareSubprogram(
			Procedure("sread", parameterItems=(
				self._LineParameter(),
				self._OutParameter(("VALUE",), self._TypeMark("string")),
				self._OutParameter(("STRLEN",), self._TypeMark("natural"))
			)),
			self._procedures
		)
		for identifier in ("oread", "hread"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark("bit_vector")),
					self._OutParameter(("GOOD",), self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark("bit_vector"))
				)),
				self._procedures
			)

		for identifier in ("writeline", "tee"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					ParameterFileInterfaceItem(("F",), self._TypeMark("text")),
					self._LineParameter()
				)),
				self._procedures
			)

		for subtype in ("bit", "bit_vector", "boolean", "character", "integer"):
			self._DeclareSubprogram(
				Procedure("write", parameterItems=(
					self._LineParameter(),
					self._InParameter(("VALUE",), self._TypeMark(subtype)),
					*self._JustificationParameters()
				)),
				self._procedures
			)

		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("real")),
				*self._JustificationParameters(),
				self._InParameter(("DIGITS",), self._TypeMark("natural"), IntegerLiteral(0))
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("real")),
				self._InParameter(("FORMAT",), self._TypeMark("string"))
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("string")),
				*self._JustificationParameters()
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("time")),
				*self._JustificationParameters(),
				self._InParameter(("UNIT",), self._TypeMark("time"), SimpleObjectOrFunctionCallSymbol(SimpleName("ns")))
			)),
			self._procedures
		)
		for identifier in ("owrite", "hwrite"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._InParameter(("VALUE",), self._TypeMark("bit_vector")),
					*self._JustificationParameters()
				)),
				self._procedures
			)


@export
class TextIO_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``std.textio``.

	.. seealso::

	   Matching :class:`Package <pyVHDLModel.STD.TextIO>` declaration.
	"""


@export
class Env(PredefinedPackage):
	"""
	Predefined package ``std.env`` (IEEE Std 1076-2008, 16.5).

	Its declarations, in the order of the standard: the procedures ``stop`` and ``finish``, each with and without a
	``STATUS`` parameter, and the function ``resolution_limit``.

	With :data:`VHDLVersion.VHDL2019 <pyVHDLModel.VHDLVersion.VHDL2019>`, it declares the additions of IEEE Std
	1076-2019, 16.5 after them, in the order of the standard:

	* date and time: type ``dayofweek``, record type ``time_record``, functions like ``localtime`` and ``epoch``,
	  the operators ``"+"`` and ``"-"`` of ``time_record`` and ``to_string``
	* environment and tool: function ``getenv``, functions like ``vhdl_version`` and ``tool_name``
	* directories and files: types ``directory_items`` and ``directory``, the status types like ``dir_open_status``,
	  subprograms like ``dir_open`` and ``dir_createdir``, the deferred constant ``dir_separator``
	* call path: types ``call_path_element``, ``call_path_vector`` and ``call_path_vector_ptr``, functions
	  ``to_string``, ``get_call_path``, ``file_name``, ``file_path`` and ``file_line``
	* assertions and PSL: subprograms like ``isvhdlassertfailed``, ``setvhdlassertenable`` and ``clearpslstate``

	The declarations follow the package ``std/env.vhdl`` of the IEEE Std 1076-2019 packages, also where the
	standard is known to be wrong, e.g. the constant parameter ``Dir`` of ``dir_close`` of a type containing an
	access type.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.Env_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``env`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("work.textio.all",))

		for identifier in ("stop", "finish"):
			status = self._InParameter(("STATUS",), self._TypeMark("integer"))
			self._DeclareSubprogram(Procedure(identifier, parameterItems=(status,)), self._procedures)
			self._DeclareSubprogram(Procedure(identifier), self._procedures)

		self._DeclareSubprogram(Function("resolution_limit", self._TypeMark("delay_length")), self._functions)

		if vhdlVersion is VHDLVersion.VHDL2019:
			self._DeclareVHDL2019Additions()

	def _DeclareVHDL2019Additions(self) -> None:
		"""
		Declare the additions of IEEE Std 1076-2019, 16.5, in the order of the standard.
		"""
		def function(
			identifier:     str,
			returnType:     SimpleSubtypeSymbol,
			parameterItems: Nullable[Iterable[ParameterConstantInterfaceItem | ParameterVariableInterfaceItem]] = None,
			isPure:         bool = True
		) -> None:
			"""
			Nested function declaring a function of this package.

			:param identifier:     The function's identifier.
			:param returnType:     The type mark of the return type.
			:param parameterItems: Optional, the parameters, in declaration order. Default: ``None``, no parameters.
			:param isPure:         Optional, ``False`` for an impure function. Default: ``True``, a pure function.
			"""
			self._DeclareSubprogram(Function(identifier, returnType, isPure, parameterItems=parameterItems), self._functions)

		def procedure(
			identifier:     str,
			parameterItems: Nullable[Iterable[ParameterConstantInterfaceItem | ParameterVariableInterfaceItem]] = None
		) -> None:
			"""
			Nested function declaring a procedure of this package.

			:param identifier:     The procedure's identifier.
			:param parameterItems: Optional, the parameters, in declaration order. Default: ``None``, no parameters.
			"""
			self._DeclareSubprogram(Procedure(identifier, parameterItems=parameterItems), self._procedures)

		def enumeration(identifier: str, literals: Iterable[str]) -> None:
			"""
			Nested function declaring an enumerated type of this package.

			:param identifier: The type's identifier.
			:param literals:   The identifiers of the enumeration literals, in declaration order.
			"""
			self._DeclareItem(EnumeratedType(identifier, [EnumerationLiteral(literal) for literal in literals]), self._types)

		def integerRange(low: int, high: int) -> ConstrainedScalarSubtypeSymbol:
			"""
			Nested function creating the subtype indication ``INTEGER range low to high``.

			:param low:  The lower bound.
			:param high: The upper bound.
			:returns:    The subtype indication.
			"""
			return ConstrainedScalarSubtypeSymbol(
				SimpleName("integer"),
				SimpleRange(IntegerLiteral(low), IntegerLiteral(high), Direction.To)
			)

		def literal(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating the name of an enumeration literal or a constant used as default value.

			:param identifier: The literal's identifier, e.g. ``true``.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		# Date and time
		enumeration("dayofweek", ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"))
		self._DeclareItem(
			RecordType("time_record", (
				RecordTypeElement(("microsecond", ), integerRange(0, 999_999)),
				RecordTypeElement(("second", ),      integerRange(0, 61)),
				RecordTypeElement(("minute", ),      integerRange(0, 59)),
				RecordTypeElement(("hour", ),        integerRange(0, 23)),
				RecordTypeElement(("day", ),         integerRange(1, 31)),
				RecordTypeElement(("month", ),       integerRange(0, 11)),
				RecordTypeElement(("year", ),        integerRange(1, 4095)),
				RecordTypeElement(("weekday", ),     self._TypeMark("dayofweek")),
				RecordTypeElement(("dayofyear", ),   integerRange(0, 365))
			)),
			self._types
		)

		function("localtime", self._TypeMark("time_record"), isPure=False)
		function("gmtime", self._TypeMark("time_record"), isPure=False)
		function("epoch", self._TypeMark("real"), isPure=False)
		for identifier in ("localtime", "gmtime"):
			function(identifier, self._TypeMark("time_record"), (self._InParameter(("TIMER", ), self._TypeMark("real")), ))

		function("epoch", self._TypeMark("real"), (self._InParameter(("TREC", ), self._TypeMark("time_record")), ))
		for identifier in ("localtime", "gmtime"):
			function(identifier, self._TypeMark("time_record"), (
				self._InParameter(("TREC", ), self._TypeMark("time_record")),
			))

		for operatorSymbol in ("+", "-"):
			for left, leftType, right, rightType in (
				("TREC",  "time_record", "DELTA", "real"),
				("DELTA", "real",        "TREC",  "time_record")
			):
				operator = Operator(operatorSymbol, self._TypeMark("time_record"), parameterItems=(
					self._InParameter((left, ), self._TypeMark(leftType)),
					self._InParameter((right, ), self._TypeMark(rightType))
				))
				self._DeclareSubprogram(operator, self._functions)

		difference = Operator("-", self._TypeMark("real"), parameterItems=(
			self._InParameter(("TR1", "TR2"), self._TypeMark("time_record")),
		))
		self._DeclareSubprogram(difference, self._functions)

		function("time_to_seconds", self._TypeMark("real"), (self._InParameter(("TIME_VAL", ), self._TypeMark("time")), ))
		function("seconds_to_time", self._TypeMark("time"), (self._InParameter(("REAL_VAL", ), self._TypeMark("real")), ))
		function("to_string", self._TypeMark("string"), (
			self._InParameter(("TREC", ), self._TypeMark("time_record")),
			ParameterConstantInterfaceItem(("FRAC_DIGITS", ), Mode.In, integerRange(0, 6), IntegerLiteral(0))
		))

		# Environment and tool
		for returnType in ("string", "line"):
			function("getenv", self._TypeMark(returnType), (
				self._InParameter(("Name", ), self._TypeMark("string")),
			), isPure=False)

		function("vhdl_version", self._TypeMark("string"), isPure=False)
		for identifier in ("tool_type", "tool_vendor", "tool_name", "tool_edition", "tool_version"):
			function(identifier, self._TypeMark("string"))

		# Directories and files
		self._DeclareItem(AccessType("directory_items", self._TypeMark("line_vector")), self._types)
		self._DeclareItem(
			RecordType("directory", (
				RecordTypeElement(("Name", ),  self._TypeMark("line")),
				RecordTypeElement(("Items", ), self._TypeMark("directory_items"))
			)),
			self._types
		)
		for identifier, literals in (
			("dir_open_status",    ("status_ok", "status_not_found", "status_no_directory", "status_access_denied",
			                        "status_error")),
			("dir_create_status",  ("status_ok", "status_item_exists", "status_access_denied", "status_error")),
			("dir_delete_status",  ("status_ok", "status_no_directory", "status_not_empty", "status_access_denied",
			                        "status_error")),
			("file_delete_status", ("status_ok", "status_no_file", "status_access_denied", "status_error"))
		):
			enumeration(identifier, literals)

		procedure("dir_open", (
			self._OutParameter(("Dir", ), self._TypeMark("directory")),
			self._InParameter(("Path", ), self._TypeMark("string")),
			self._OutParameter(("Status", ), self._TypeMark("dir_open_status"))
		))
		function("dir_open", self._TypeMark("dir_open_status"), (
			self._OutParameter(("Dir", ), self._TypeMark("directory")),
			self._InParameter(("Path", ), self._TypeMark("string"))
		), isPure=False)
		procedure("dir_close", (self._InParameter(("Dir", ), self._TypeMark("directory")), ))
		for identifier in ("dir_itemexists", "dir_itemisdir", "dir_itemisfile"):
			function(identifier, self._TypeMark("boolean"), (
				self._InParameter(("Path", ), self._TypeMark("string")),
			), isPure=False)

		procedure("dir_workingdir", (
			self._InParameter(("Path", ), self._TypeMark("string")),
			self._OutParameter(("Status", ), self._TypeMark("dir_open_status"))
		))
		function("dir_workingdir", self._TypeMark("dir_open_status"), (
			self._InParameter(("Path", ), self._TypeMark("string")),
		), isPure=False)
		function("dir_workingdir", self._TypeMark("string"), isPure=False)

		for identifier, option, status in (
			("dir_createdir", "Parents",   "dir_create_status"),
			("dir_deletedir", "Recursive", "dir_delete_status")
		):
			procedure(identifier, (
				self._InParameter(("Path", ), self._TypeMark("string")),
				self._OutParameter(("Status", ), self._TypeMark(status))
			))
			procedure(identifier, (
				self._InParameter(("Path", ), self._TypeMark("string")),
				self._InParameter((option, ), self._TypeMark("boolean")),
				self._OutParameter(("Status", ), self._TypeMark(status))
			))
			function(identifier, self._TypeMark(status), (
				self._InParameter(("Path", ), self._TypeMark("string")),
				self._InParameter((option, ), self._TypeMark("boolean"), literal("false"))
			), isPure=False)

		procedure("dir_deletefile", (
			self._InParameter(("Path", ), self._TypeMark("string")),
			self._OutParameter(("Status", ), self._TypeMark("file_delete_status"))
		))
		function("dir_deletefile", self._TypeMark("file_delete_status"), (
			self._InParameter(("Path", ), self._TypeMark("string")),
		), isPure=False)

		dirSeparator = DeferredConstant(("dir_separator", ), self._TypeMark("string"))
		self._deferredConstants[dirSeparator._normalizedIdentifiers[0]] = dirSeparator
		self.AddDeclaredItem(dirSeparator)

		# Call path
		self._DeclareItem(
			RecordType("call_path_element", (
				RecordTypeElement(("name", ),      self._TypeMark("line")),
				RecordTypeElement(("file_name", ), self._TypeMark("line")),
				RecordTypeElement(("file_path", ), self._TypeMark("line")),
				RecordTypeElement(("file_line", ), self._TypeMark("positive"))
			)),
			self._types
		)
		function("to_string", self._TypeMark("string"), (
			self._InParameter(("call_path", ), self._TypeMark("call_path_element")),
		), isPure=False)
		for typeDefinition in (
			ArrayType("call_path_vector", (self._TypeMark("natural"), ), self._TypeMark("call_path_element")),
			AccessType("call_path_vector_ptr", self._TypeMark("call_path_vector"))
		):
			self._DeclareItem(typeDefinition, self._types)
			separator = ConcatenationExpression(StringLiteral(""), literal("lf"))
			function("to_string", self._TypeMark("string"), (
				self._InParameter(("call_path", ), self._TypeMark(typeDefinition._identifier)),
				self._InParameter(("Separator", ), self._TypeMark("string"), separator)
			), isPure=False)

		function("get_call_path", self._TypeMark("call_path_vector_ptr"), isPure=False)
		for identifier, returnTypes in (
			("file_name", ("line", "string")),
			("file_path", ("line", "string")),
			("file_line", ("positive", "string"))
		):
			for returnType in returnTypes:
				function(identifier, self._TypeMark(returnType), isPure=False)

		# Assertions and PSL
		for identifier, returnType in (("isvhdlassertfailed", "boolean"), ("getvhdlassertcount", "natural")):
			function(identifier, self._TypeMark(returnType), isPure=False)
			function(identifier, self._TypeMark(returnType), (
				self._InParameter(("Level", ), self._TypeMark("severity_level")),
			), isPure=False)

		procedure("clearvhdlassert")
		procedure("setvhdlassertenable", (self._InParameter(("Enable", ), self._TypeMark("boolean"), literal("true")), ))
		procedure("setvhdlassertenable", (
			self._InParameter(("Level", ), self._TypeMark("severity_level"), literal("note")),
			self._InParameter(("Enable", ), self._TypeMark("boolean"), literal("true"))
		))
		function("getvhdlassertenable", self._TypeMark("boolean"), (
			self._InParameter(("Level", ), self._TypeMark("severity_level"), literal("note")),
		), isPure=False)
		procedure("setvhdlassertformat", (
			self._InParameter(("Level", ), self._TypeMark("severity_level")),
			self._InParameter(("Format", ), self._TypeMark("string"))
		))
		procedure("setvhdlassertformat", (
			self._InParameter(("Level", ), self._TypeMark("severity_level")),
			self._InParameter(("Format", ), self._TypeMark("string")),
			self._OutParameter(("Valid", ), self._TypeMark("boolean"))
		))
		function("getvhdlassertformat", self._TypeMark("string"), (
			self._InParameter(("Level", ), self._TypeMark("severity_level")),
		), isPure=False)
		procedure("setvhdlreadseverity", (
			self._InParameter(("Level", ), self._TypeMark("severity_level"), literal("failure")),
		))
		function("getvhdlreadseverity", self._TypeMark("severity_level"), isPure=False)

		function("pslassertfailed", self._TypeMark("boolean"), isPure=False)
		function("psliscovered", self._TypeMark("boolean"), isPure=False)
		procedure("setpslcoverassert", (self._InParameter(("Enable", ), self._TypeMark("boolean"), literal("true")), ))
		function("getpslcoverassert", self._TypeMark("boolean"), isPure=False)
		function("pslisassertcovered", self._TypeMark("boolean"), isPure=False)
		procedure("clearpslstate")


@export
class Env_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``std.env``.

	.. seealso::

	   Matching :class:`Package <pyVHDLModel.STD.Env>` declaration.
	"""


PACKAGES = (
	(Standard, Standard_Body),
	(TextIO, TextIO_Body),
	(Env, Env_Body),
)
