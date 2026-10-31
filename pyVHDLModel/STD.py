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

from pyVHDLModel.Base        import SimpleRange, Direction
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol
from pyVHDLModel.Expression  import EnumerationLiteral, CharacterEnumerationLiteral, IntegerLiteral, \
                                    FloatingPointLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Type        import EnumeratedType, IntegerType, RealType, PhysicalType, ArrayType, AccessType, Subtype
from pyVHDLModel.Predefined  import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody


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
	Predefined package ``std.standard``.

	Predefined types:

	* ``boolean``, ``boolean_vector``
	* ``bit``, ``bit_vector``
	* ``character``, ``string``
	* ``integer``, ``integer_vector``
	* ``natural``, ``positive``
	* ``real``, ``real_vector``
	* ``time``, ``time_vector``
	* ``open_file_kind``, ``open_file_status``

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.Standard_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``standard`` package.
		"""
		super().__init__()

		boolean = EnumeratedType("boolean", (EnumerationLiteral("false"), EnumerationLiteral("true")), None)
		self._types[boolean._normalizedIdentifier] = boolean
		self._declaredItems.append(boolean)

		bit = EnumeratedType("bit", (CharacterEnumerationLiteral("0"), CharacterEnumerationLiteral("1")), None)
		self._types[bit._normalizedIdentifier] = bit
		self._declaredItems.append(bit)

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

		character = EnumeratedType("character", characters, None)
		self._types[character._normalizedIdentifier] = character
		self._declaredItems.append(character)

		levels = "note", "warning", "error", "failure"
		severityLevel = EnumeratedType("severityLevel", [EnumerationLiteral(level) for level in levels], None)
		self._types[severityLevel._normalizedIdentifier] = severityLevel
		self._declaredItems.append(severityLevel)

		integer = IntegerType("integer", SimpleRange(IntegerLiteral(-2**31), IntegerLiteral(2**31 - 1), Direction.To), None)
		self._types[integer._normalizedIdentifier] = integer
		self._declaredItems.append(integer)

		# real
		real = RealType("real", SimpleRange(FloatingPointLiteral(-5.0), FloatingPointLiteral(5.0), Direction.To), None)
		self._types[real._normalizedIdentifier] = real
		self._declaredItems.append(real)

		time = PhysicalType("time", SimpleRange(IntegerLiteral(-2**63), IntegerLiteral(2**63 - 1), Direction.To), primaryUnit="fs", units=(
			("ps", PhysicalIntegerLiteral(1000, "fs")),
			("ns", PhysicalIntegerLiteral(1000, "ps")),
			("us", PhysicalIntegerLiteral(1000, "ns")),
			("ms", PhysicalIntegerLiteral(1000, "us")),
			("sec", PhysicalIntegerLiteral(1000, "ms")),
			("min", PhysicalIntegerLiteral(60, "sec")),
			("hr", PhysicalIntegerLiteral(60, "min")),
		), parent=None)
		self._types[time._normalizedIdentifier] = time
		self._declaredItems.append(time)

		# delay_length

		# now

		natural = Subtype("natural", SimpleSubtypeSymbol(SimpleName("integer")), None)
		natural._baseType = integer
		natural._range = SimpleRange(IntegerLiteral(0), IntegerLiteral(2**31 - 1), Direction.To)
		self._subtypes[natural._normalizedIdentifier] = natural
		self._declaredItems.append(natural)

		positive = Subtype("positive", SimpleSubtypeSymbol(SimpleName("integer")), None)
		positive._baseType = integer
		positive._range = SimpleRange(IntegerLiteral(1), IntegerLiteral(2**31 - 1), Direction.To)
		self._subtypes[positive._normalizedIdentifier] = positive
		self._declaredItems.append(positive)

		string = ArrayType("string", (SimpleSubtypeSymbol(SimpleName("positive")),), SimpleSubtypeSymbol(SimpleName("character")), None)
		self._types[string._normalizedIdentifier] = string
		self._declaredItems.append(string)

		line = AccessType("line", SimpleSubtypeSymbol(SimpleName("character")), None)
		self._types[line._normalizedIdentifier] = line
		self._declaredItems.append(line)

		booleanVector = ArrayType("boolean_vector", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("boolean")), None)
		self._types[booleanVector._normalizedIdentifier] = booleanVector
		self._declaredItems.append(booleanVector)

		bitVector = ArrayType("bit_vector", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("bit")), None)
		self._types[bitVector._normalizedIdentifier] = bitVector
		self._declaredItems.append(bitVector)

		integerVector = ArrayType("integer_vector", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("integer")), None)
		self._types[integerVector._normalizedIdentifier] = integerVector
		self._declaredItems.append(integerVector)

		# real_vector

		timeVector = ArrayType("time_vector", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("time")), None)
		self._types[timeVector._normalizedIdentifier] = timeVector
		self._declaredItems.append(timeVector)

		fileOpenKinds = "read_mode", "write_mode", "append_mode"
		openFileKind = EnumeratedType("open_file_kind", [EnumerationLiteral(kind) for kind in fileOpenKinds], None)
		self._types[openFileKind._normalizedIdentifier] = openFileKind
		self._declaredItems.append(openFileKind)

		fileOpenStati = "open_ok", "status_error", "name_error", "mode_error"
		fileOpenStatus = EnumeratedType("open_file_status", [EnumerationLiteral(status) for status in fileOpenStati], None)
		self._types[fileOpenStatus._normalizedIdentifier] = fileOpenStatus
		self._declaredItems.append(fileOpenStatus)

		# attribute foreign


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
	Predefined package ``std.textio``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.TextIO_Body>` declaration.
	"""


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
