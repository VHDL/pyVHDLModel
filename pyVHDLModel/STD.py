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

from typing                  import Optional as Nullable

from pyTooling.Decorators    import export
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import SimpleRange, Direction, Mode
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                                    SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression  import EnumerationLiteral, CharacterEnumerationLiteral, IntegerLiteral, \
                                    FloatingPointLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Type        import EnumeratedType, IntegerType, RealType, PhysicalType, PhysicalUnit, ArrayType, \
                                    AccessType, FileType, Subtype
from pyVHDLModel.Object      import File
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                    ParameterFileInterfaceItem
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Subprogram  import Procedure, Function, PredefinedOperator, PredefinedOperation
from pyVHDLModel.Predefined  import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody


@export
class LogicalOperatorsMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_TypeMark", "_BinaryOperator", "_UnaryOperator")
):
	"""
	A mixin-class for the types ``boolean`` and ``bit``, which declare the logical operators (IEEE Std 1076-2008, 9.2.2).

	.. seealso::

	   * :class:`Boolean <pyVHDLModel.STD.Boolean>`
	   * :class:`Bit <pyVHDLModel.STD.Bit>`
	"""

	def _CreateLogicalOperators(self) -> list[PredefinedOperator]:
		"""
		Create the logical operators of this type: ``"and"``, ``"or"``, ``"nand"``, ``"nor"``, ``"xor"`` and ``"xnor"``,
		then ``"not"``.

		:returns: List of predefined operators.
		"""
		operations = []
		for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

		operations.append(self._UnaryOperator("not", self._TypeMark()))

		return operations


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
class Bit(EnumeratedType, LogicalOperatorsMixin):
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
		for operatorSymbol in ("?=", "?/=", "?<", "?<=", "?>", "?>="):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

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

	def __init__(self) -> None:
		"""
		Initializes the ``std`` library.
		"""
		super().__init__(PACKAGES)


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

	The types declare their predefined operations (:attr:`~pyVHDLModel.Type.FullType.ImplicitOperations`). The
	implementation-defined ranges are GHDL's: ``integer`` has 32 bits, ``real`` is an IEEE 754 double, ``time`` counts
	femtoseconds in 64 bits.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.Standard_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``standard`` package.
		"""
		super().__init__()

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

		kinds = "read_mode", "write_mode", "append_mode"
		self._DeclareItem(EnumeratedType("file_open_kind", [EnumerationLiteral(kind) for kind in kinds]), self._types)

		statuses =       "open_ok", "status_error", "name_error", "mode_error"
		fileOpenStatus = EnumeratedType("file_open_status", [EnumerationLiteral(status) for status in statuses])
		self._DeclareItem(fileOpenStatus, self._types)

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

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.TextIO_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``textio`` package.
		"""
		super().__init__()

		def line() -> ParameterVariableInterfaceItem:
			"""
			Nested function creating the parameter ``L : inout LINE``.

			:returns: The parameter.
			"""
			return ParameterVariableInterfaceItem(("L",), Mode.InOut, self._TypeMark("line"))

		def variable(identifier: str, subtype: SimpleSubtypeSymbol) -> ParameterVariableInterfaceItem:
			"""
			Nested function creating a variable parameter of mode ``out``.

			:param identifier: The parameter's identifier.
			:param subtype:    The parameter's type mark.
			:returns:          The parameter.
			"""
			return ParameterVariableInterfaceItem((identifier,), Mode.Out, subtype)

		def constant(
			identifier:        str,
			subtype:           SimpleSubtypeSymbol,
			defaultExpression: Nullable[IntegerLiteral | SimpleObjectOrFunctionCallSymbol] = None
		) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a constant parameter of mode ``in``.

			:param identifier:        The parameter's identifier.
			:param subtype:           The parameter's type mark.
			:param defaultExpression: Optional, the default value. Default: ``None``, no default value.
			:returns:                 The parameter.
			"""
			return ParameterConstantInterfaceItem((identifier,), Mode.In, subtype, defaultExpression)

		def justification() -> tuple[ParameterConstantInterfaceItem, ParameterConstantInterfaceItem]:
			"""
			Nested function creating the parameters ``JUSTIFIED : SIDE := RIGHT`` and ``FIELD : WIDTH := 0``.

			:returns: The two parameters.
			"""
			return (
				constant("JUSTIFIED", self._TypeMark("side"), SimpleObjectOrFunctionCallSymbol(SimpleName("right"))),
				constant("FIELD", self._TypeMark("width"), IntegerLiteral(0))
			)

		self._DeclareItem(AccessType("line", self._TypeMark("string")), self._types)
		self._DeclareItem(FileType("text", self._TypeMark("string")), self._types)
		self._DeclareItem(EnumeratedType("side", (EnumerationLiteral("right"), EnumerationLiteral("left"))), self._types)
		self._DeclareItem(Subtype("width", self._TypeMark("natural")), self._subtypes)
		self._DeclareSubprogram(
			Function("justify", self._TypeMark("string"), parameterItems=(
				constant("VALUE", self._TypeMark("string")),
				*justification()
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
				line()
			)),
			self._procedures
		)
		for subtype in ("bit", "bit_vector", "boolean", "character", "integer", "real", "string", "time"):
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					line(),
					variable("VALUE", self._TypeMark(subtype)),
					variable("GOOD", self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(line(), variable("VALUE", self._TypeMark(subtype)))),
				self._procedures
			)

		self._DeclareSubprogram(
			Procedure("sread", parameterItems=(
				line(),
				variable("VALUE", self._TypeMark("string")),
				variable("STRLEN", self._TypeMark("natural"))
			)),
			self._procedures
		)
		for identifier in ("oread", "hread"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					line(),
					variable("VALUE", self._TypeMark("bit_vector")),
					variable("GOOD", self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					line(),
					variable("VALUE", self._TypeMark("bit_vector"))
				)),
				self._procedures
			)

		for identifier in ("writeline", "tee"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					ParameterFileInterfaceItem(("F",), self._TypeMark("text")),
					line()
				)),
				self._procedures
			)

		for subtype in ("bit", "bit_vector", "boolean", "character", "integer"):
			self._DeclareSubprogram(
				Procedure("write", parameterItems=(
					line(),
					constant("VALUE", self._TypeMark(subtype)),
					*justification()
				)),
				self._procedures
			)

		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				line(),
				constant("VALUE", self._TypeMark("real")),
				*justification(),
				constant("DIGITS", self._TypeMark("natural"), IntegerLiteral(0))
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				line(),
				constant("VALUE", self._TypeMark("real")),
				constant("FORMAT", self._TypeMark("string"))
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				line(),
				constant("VALUE", self._TypeMark("string")),
				*justification()
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				line(),
				constant("VALUE", self._TypeMark("time")),
				*justification(),
				constant("UNIT", self._TypeMark("time"), SimpleObjectOrFunctionCallSymbol(SimpleName("ns")))
			)),
			self._procedures
		)
		for identifier in ("owrite", "hwrite"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					line(),
					constant("VALUE", self._TypeMark("bit_vector")),
					*justification()
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
	Predefined package ``std.env``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.Env_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``env`` package.
		"""
		super().__init__()

		self._AddPackageClause(("work.textio.all",))


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
