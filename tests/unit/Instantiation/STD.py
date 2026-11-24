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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
"""Tests for pyVHDLModel.STD."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import Direction
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Subprogram  import Function
from pyVHDLModel.Type        import EnumeratedType, ArrayType, AccessType
from pyVHDLModel.STD         import Standard, TextIO, Boolean, Bit


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _signatures(fullType, first: int) -> list[tuple[str, tuple[str, ...], str]]:
	"""The implicit operations of a type from index ``first``, as (designator, parameter types, return type) tuples."""
	return [
		(
			operation.Identifier,
			tuple(item.Subtype.Name.Identifier for item in operation.ParameterItems),
			operation.ReturnType.Name.Identifier
		)
		for operation in fullType.ImplicitOperations[first:]
	]


class Standards(Testcase):
	"""Package ``std.standard`` (IEEE Std 1076-2008, 16.3)."""

	def test_Declarations(self) -> None:
		"""The declarations in the order of the standard, each with the package as parent."""
		standard = Standard()

		self.assertListEqual(
			[
				"boolean", "bit", "character", "severity_level", "integer", "real", "time", "delay_length", "now", "natural",
				"positive", "string", "boolean_vector", "bit_vector", "integer_vector", "real_vector", "time_vector",
				"file_open_kind", "file_open_status", "foreign"
			],
			[declaration.Identifier for declaration in standard.DeclaredItems]
		)
		for declaration in standard.DeclaredItems:
			self.assertIs(standard, declaration.Parent)

	def test_Ranges(self) -> None:
		"""The implementation-defined ranges are GHDL's; the subtypes' ranges follow from them."""
		standard = Standard()
		for identifier, left, right in (
			("integer", -2**31, 2**31 - 1),
			("real",    -1.7976931348623157e308, 1.7976931348623157e308)
		):
			rng = standard.Types[identifier].Range
			self.assertEqual(left, rng.LeftBound.Value)
			self.assertEqual(right, rng.RightBound.Value)
			self.assertIs(Direction.To, rng.Direction)

		for identifier, left in (
			("natural",  0),
			("positive", 1)
		):
			subtype = standard.Subtypes[identifier]
			self.assertIs(standard.Types["integer"], subtype.BaseType)
			self.assertEqual(left, subtype.Range.LeftBound.Value)
			self.assertEqual(2**31 - 1, subtype.Range.RightBound.Value)

	def test_DelayLength(self) -> None:
		"""``subtype DELAY_LENGTH is TIME range 0 fs to TIME'HIGH;``"""
		delayLength = Standard().Subtypes["delay_length"]

		self.assertEqual("time", delayLength.BaseType.Identifier)
		self.assertEqual(0, delayLength.Range.LeftBound.Value)
		self.assertEqual(2**63 - 1, delayLength.Range.RightBound.Value)

	def test_Now(self) -> None:
		"""``impure function NOW return DELAY_LENGTH;``"""
		now = Standard().Functions["now"][0]

		self.assertIsInstance(now, Function)
		self.assertFalse(now.IsPure)
		self.assertEqual("delay_length", now.ReturnType.Name.Identifier)
		self.assertListEqual([], now.ParameterItems)

	def test_Vectors(self) -> None:
		"""``STRING`` is indexed by ``POSITIVE``, the vectors by ``NATURAL``."""
		standard = Standard()
		for identifier, index, element in (
			("string",         "positive", "character"),
			("boolean_vector", "natural",  "boolean"),
			("bit_vector",     "natural",  "bit"),
			("integer_vector", "natural",  "integer"),
			("real_vector",    "natural",  "real"),
			("time_vector",    "natural",  "time")
		):
			arrayType = standard.Types[identifier]
			self.assertIsInstance(arrayType, ArrayType)
			self.assertEqual(index, arrayType.Dimensions[0].Name.Identifier)
			self.assertEqual(element, arrayType.ElementType.Name.Identifier)

	def test_Enumerations(self) -> None:
		standard = Standard()
		for identifier, literals in (
			("severity_level",   ["note", "warning", "error", "failure"]),
			("file_open_kind",   ["read_mode", "write_mode", "append_mode"]),
			("file_open_status", ["open_ok", "status_error", "name_error", "mode_error"])
		):
			enumeration = standard.Types[identifier]
			self.assertIsInstance(enumeration, EnumeratedType)
			self.assertListEqual(literals, [literal.NormalizedDesignator for literal in enumeration.Literals])

	def test_Foreign(self) -> None:
		"""``attribute FOREIGN : STRING;``"""
		foreign = Standard().DeclaredItems[-1]

		self.assertIsInstance(foreign, Attribute)
		self.assertEqual("string", foreign.Subtype.Name.Identifier)


class Booleans(Testcase):
	def test_LogicalOperators(self) -> None:
		"""After the operations of an enumerated type: the logical operators."""
		boolean = Boolean()

		self.assertIsInstance(boolean, EnumeratedType)
		self.assertListEqual(
			[
				("and",  ("boolean", "boolean"), "boolean"),
				("or",   ("boolean", "boolean"), "boolean"),
				("nand", ("boolean", "boolean"), "boolean"),
				("nor",  ("boolean", "boolean"), "boolean"),
				("xor",  ("boolean", "boolean"), "boolean"),
				("xnor", ("boolean", "boolean"), "boolean"),
				("not",  ("boolean",),           "boolean")
			],
			_signatures(boolean, 9)
		)


class Bits(Testcase):
	def test_Operators(self) -> None:
		"""After the operations of an enumerated type: the logical, condition and matching relational operators."""
		bit = Bit()

		self.assertIsInstance(bit, EnumeratedType)
		self.assertListEqual(
			[
				("and",  ("bit", "bit"), "bit"),
				("or",   ("bit", "bit"), "bit"),
				("nand", ("bit", "bit"), "bit"),
				("nor",  ("bit", "bit"), "bit"),
				("xor",  ("bit", "bit"), "bit"),
				("xnor", ("bit", "bit"), "bit"),
				("not",  ("bit",),       "bit"),
				("??",   ("bit",),       "boolean"),
				("?=",   ("bit", "bit"), "bit"),
				("?/=",  ("bit", "bit"), "bit"),
				("?<",   ("bit", "bit"), "bit"),
				("?<=",  ("bit", "bit"), "bit"),
				("?>",   ("bit", "bit"), "bit"),
				("?>=",  ("bit", "bit"), "bit")
			],
			_signatures(bit, 9)
		)


class TextIOs(Testcase):
	def test_Line(self) -> None:
		"""``type LINE is access STRING;``"""
		textio = TextIO()
		line =   textio.Types["line"]

		self.assertIsInstance(line, AccessType)
		self.assertEqual("string", line.DesignatedSubtype.Name.Identifier)
		self.assertIs(textio, line.Parent)
