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
"""Tests for writing type and subtype declarations with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Expression      import IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral, \
                                        EnumerationLiteral, AscendingRangeExpression, DescendingRangeExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, AttributeName
from pyVHDLModel.Symbol          import ConstrainedArraySubtypeSymbol
from pyVHDLModel.Type            import AnonymousType, Subtype, EnumeratedType, IntegerType, RealType, PhysicalType, \
                                        ArrayType, RecordTypeElement, RecordType, AccessType, FileType

from tests.unit                  import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _to(left: int, right: int) -> AscendingRangeExpression:
	"""Ascending range of two integer literals."""
	return AscendingRangeExpression(IntegerLiteral(left), IntegerLiteral(right))


def _distance() -> PhysicalType:
	"""Physical type with two secondary units."""
	return PhysicalType("distance", _to(0, 1000000), "um", [
		("mm", PhysicalIntegerLiteral(1000, "um")),
		("m",  PhysicalIntegerLiteral(1000, "mm"))
	])


class ScalarTypes(Testcase):
	def test_Enumerated(self) -> None:
		enumeratedType = EnumeratedType("state", [EnumerationLiteral("Idle"), EnumerationLiteral("Busy")])

		self.assertEqual("type state is (Idle, Busy);\n", VHDLWriter().Format(enumeratedType))

	def test_Enumerated_Characters(self) -> None:
		"""A character literal of an enumerated type is an enumeration literal carrying its quotes."""
		enumeratedType = EnumeratedType("logic", [EnumerationLiteral("'0'"), EnumerationLiteral("'1'")])

		self.assertEqual("type logic is ('0', '1');\n", VHDLWriter().Format(enumeratedType))

	def test_Integer(self) -> None:
		self.assertEqual("type nibble is range 0 to 15;\n", VHDLWriter().Format(IntegerType("nibble", _to(0, 15))))

	def test_Integer_RangeAttribute(self) -> None:
		integerType = IntegerType("index", AttributeName("range", SimpleName("vector")))

		self.assertEqual("type index is range vector'range;\n", VHDLWriter().Format(integerType))

	def test_Real(self) -> None:
		realType = RealType("fraction", AscendingRangeExpression(FloatingPointLiteral(0.0), FloatingPointLiteral(1.0)))

		self.assertEqual("type fraction is range 0.0 to 1.0;\n", VHDLWriter().Format(realType))

	def test_Physical(self) -> None:
		self.assertEqual(dedent("""\
			type distance is range 0 to 1000000
			  units
			    um;
			    mm = 1000 um;
			    m = 1000 mm;
			  end units distance;
			"""), VHDLWriter().Format(_distance()))

	def test_Physical_SmartTabs(self) -> None:
		self.assertEqual(
			"type distance is range 0 to 1000000\n"
			"\tunits\n"
			"\t\tum;\n"
			"\t\tmm = 1000 um;\n"
			"\t\tm = 1000 mm;\n"
			"\tend units distance;\n",
			VHDLWriter(VHDLStyle(indentStyle=IndentStyle.SmartTabs)).Format(_distance())
		)

	def test_Physical_PrimaryUnitOnly(self) -> None:
		physicalType = PhysicalType("ticks", _to(0, 100), "tick", [])

		self.assertEqual(dedent("""\
			type ticks is range 0 to 100
			  units
			    tick;
			  end units ticks;
			"""), VHDLWriter().Format(physicalType))


class CompositeTypes(Testcase):
	def test_Array_Constrained(self) -> None:
		arrayType = ArrayType("memory", [_to(0, 255)], _subtypeSymbol("byte"))

		self.assertEqual("type memory is array (0 to 255) of byte;\n", VHDLWriter().Format(arrayType))

	def test_Array_Unbounded(self) -> None:
		"""A type mark as index is an unbounded index: ``range <>`` follows."""
		arrayType = ArrayType("matrix", [_subtypeSymbol("natural"), _subtypeSymbol("natural")], _subtypeSymbol("bit"))

		self.assertEqual(
			"type matrix is array (natural range <>, natural range <>) of bit;\n",
			VHDLWriter().Format(arrayType)
		)

	def test_Array_ConstrainedElement(self) -> None:
		element =   ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [
			DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		])
		arrayType = ArrayType("memory", [_to(0, 3)], element)

		self.assertEqual("type memory is array (0 to 3) of bit_vector(7 downto 0);\n", VHDLWriter().Format(arrayType))

	def test_Record(self) -> None:
		recordType = RecordType("frame", [
			RecordTypeElement(["valid", "last"], _subtypeSymbol("bit")),
			RecordTypeElement(["data"], _subtypeSymbol("byte"))
		])

		self.assertEqual(dedent("""\
			type frame is record
			  valid, last : bit;
			  data : byte;
			end record frame;
			"""), VHDLWriter().Format(recordType))

	def test_Record_UpperCase(self) -> None:
		recordType = RecordType("frame", [RecordTypeElement(["valid"], _subtypeSymbol("bit"))])

		self.assertEqual(dedent("""\
			TYPE frame IS RECORD
			  valid : bit;
			END RECORD frame;
			"""), VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(recordType))


class OtherTypes(Testcase):
	def test_Access(self) -> None:
		accessType = AccessType("pointer", _subtypeSymbol("node"))

		self.assertEqual("type pointer is access node;\n", VHDLWriter().Format(accessType))

	def test_File(self) -> None:
		fileType = FileType("text_file", _subtypeSymbol("string"))

		self.assertEqual("type text_file is file of string;\n", VHDLWriter().Format(fileType))

	def test_Incomplete(self) -> None:
		self.assertEqual("type node;\n", VHDLWriter().Format(AnonymousType("node")))

	def test_Subtype(self) -> None:
		subtype = Subtype("byte", ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [
			DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		]))

		self.assertEqual("subtype byte is bit_vector(7 downto 0);\n", VHDLWriter().Format(subtype))

	def test_Subtype_TypeMark(self) -> None:
		self.assertEqual("subtype word is integer;\n", VHDLWriter().Format(Subtype("word", _subtypeSymbol("integer"))))

	def test_UpperCase(self) -> None:
		writer =   VHDLWriter(VHDLStyle(KeywordCase.Upper))
		fileType = FileType("text_file", _subtypeSymbol("string"))

		self.assertEqual("TYPE text_file IS FILE OF string;\n", writer.Format(fileType))
		self.assertEqual("SUBTYPE word IS integer;\n", writer.Format(Subtype("word", _subtypeSymbol("integer"))))
		self.assertEqual(
			"TYPE logic IS ('0', '1');\n",
			writer.Format(EnumeratedType("logic", [EnumerationLiteral("'0'"), EnumerationLiteral("'1'")]))
		)
