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

from pyTooling.Decorators    import export
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity, SimpleRange, Direction
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol
from pyVHDLModel.Expression  import EnumerationLiteral, CharacterEnumerationLiteral, IntegerLiteral, \
                                    FloatingPointLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Type        import EnumeratedType, IntegerType, RealType, PhysicalType, PhysicalUnit, ArrayType, \
                                    AccessType, Subtype
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Subprogram  import Function, PredefinedFunction
from pyVHDLModel.Predefined  import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody


@export
class LogicalOperationsMixin(metaclass=ExtendedType, mixin=True, expects=("_Operation",)):
	"""
	A mixin-class for the types ``boolean`` and ``bit``, which declare the logical operators (IEEE Std 1076-2008, 9.2.2).

	.. seealso::

	   * :class:`Boolean <pyVHDLModel.STD.Boolean>`
	   * :class:`Bit <pyVHDLModel.STD.Bit>`
	"""

	def _CreateLogicalOperations(self) -> list[PredefinedFunction]:
		"""
		Create the logical operators of this type: ``"and"``, ``"or"``, ``"nand"``, ``"nor"``, ``"xor"`` and ``"xnor"``,
		then ``"not"``.

		:returns: List of predefined functions.
		"""
		operations = []
		for designator in ("and", "or", "nand", "nor", "xor", "xnor"):
			operations.append(self._Operation(designator, self, ("L", self), ("R", self)))

		operations.append(self._Operation("not", self, ("R", self)))

		return operations


@export
class Boolean(EnumeratedType, LogicalOperationsMixin):
	"""
	Represents the predefined type ``boolean`` of package ``std.standard``: ``(false, true)``.

	Besides the operations of an enumerated type, it declares the logical operators (IEEE Std 1076-2008, 9.2.2).
	"""

	def __init__(self) -> None:
		"""
		Initializes the type ``boolean``.
		"""
		super().__init__("boolean", (EnumerationLiteral("false"), EnumerationLiteral("true")))

	def _CreateImplicitOperations(self) -> list[PredefinedFunction]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, then the logical operators.

		:returns: List of predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateLogicalOperations())

		return operations


@export
class Bit(EnumeratedType, LogicalOperationsMixin):
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

	def _CreateImplicitOperations(self) -> list[PredefinedFunction]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, the logical operators, the
		condition operator ``"??"`` and the matching relational operators ``"?="``, ``"?/="``, ``"?<"``, ``"?<="``,
		``"?>"`` and ``"?>="``.

		:returns: List of predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateLogicalOperations())
		operations.append(self._Operation("??", "boolean", ("R", self)))
		for designator in ("?=", "?/=", "?<", "?<=", "?>", "?>="):
			operations.append(self._Operation(designator, self, ("L", self), ("R", self)))

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

		def declare(declaration: ModelEntity, table: dict[str, ModelEntity]) -> None:
			"""
			Nested function adding a declaration to this package and to the package's lookup table of its kind.

			:param declaration: The declaration.
			:param table:       The lookup table of the declaration's kind, e.g. :attr:`_types`.
			"""
			table[declaration._normalizedIdentifier] = declaration
			self.AddDeclaredItem(declaration)

		def typeMark(identifier: str) -> SimpleSubtypeSymbol:
			"""
			Nested function creating a type mark naming a declaration of this package.

			:param identifier: The identifier of the declaration.
			:returns:          The type mark.
			"""
			return SimpleSubtypeSymbol(SimpleName(identifier))

		declare(Boolean(), self._types)
		declare(Bit(), self._types)

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

		declare(EnumeratedType("character", characters), self._types)

		levels = "note", "warning", "error", "failure"
		declare(EnumeratedType("severity_level", [EnumerationLiteral(level) for level in levels]), self._types)

		integer = IntegerType("integer", SimpleRange(IntegerLiteral(-2**31), IntegerLiteral(2**31 - 1), Direction.To))
		declare(integer, self._types)

		realRange = SimpleRange(
			FloatingPointLiteral(-1.7976931348623157e308),
			FloatingPointLiteral(1.7976931348623157e308),
			Direction.To
		)
		declare(RealType("real", realRange), self._types)

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
		declare(time, self._types)

		delayLength =           Subtype("delay_length", typeMark("time"))
		delayLength._baseType = time
		delayLength._range =     SimpleRange(
			PhysicalIntegerLiteral(0, "fs"),
			PhysicalIntegerLiteral(2**63 - 1, "fs"),
			Direction.To
		)
		declare(delayLength, self._subtypes)

		now =                    Function("now", typeMark("delay_length"), isPure=False)
		self._functions["now"] = [now]
		self.AddDeclaredItem(now)

		for identifier, low in (
			("natural",  0),
			("positive", 1)
		):
			subtype =           Subtype(identifier, typeMark("integer"))
			subtype._baseType = integer
			subtype._range =    SimpleRange(IntegerLiteral(low), IntegerLiteral(2**31 - 1), Direction.To)
			declare(subtype, self._subtypes)

		declare(ArrayType("string", (typeMark("positive"),), typeMark("character")), self._types)
		for identifier, element in (
			("boolean_vector", "boolean"),
			("bit_vector",     "bit"),
			("integer_vector", "integer"),
			("real_vector",    "real"),
			("time_vector",    "time")
		):
			declare(ArrayType(identifier, (typeMark("natural"),), typeMark(element)), self._types)

		kinds = "read_mode", "write_mode", "append_mode"
		declare(EnumeratedType("file_open_kind", [EnumerationLiteral(kind) for kind in kinds]), self._types)

		statuses = "open_ok", "status_error", "name_error", "mode_error"
		declare(EnumeratedType("file_open_status", [EnumerationLiteral(status) for status in statuses]), self._types)

		self.AddDeclaredItem(Attribute("foreign", typeMark("string")))


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

	Its declarations: type ``line``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.TextIO_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``textio`` package.
		"""
		super().__init__()

		line =                                    AccessType("line", SimpleSubtypeSymbol(SimpleName("string")))
		self._types[line._normalizedIdentifier] = line
		self.AddDeclaredItem(line)


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
