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
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design, VHDLVersion
from pyVHDLModel.Base        import Direction, Mode
from pyVHDLModel.Expression  import IntegerLiteral, StringLiteral, ConcatenationExpression
from pyVHDLModel.Symbol      import ConstrainedScalarSubtypeSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Object      import File, DeferredConstant
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                    ParameterFileInterfaceItem, ParameterSimpleSignalInterfaceItem
from pyVHDLModel.Declaration import Alias, Attribute
from pyVHDLModel.Subprogram  import Procedure, Function, Operator
from pyVHDLModel.Type        import EnumeratedType, ArrayType, AccessType, FileType, Subtype, RecordType
from pyVHDLModel.STD         import Standard, TextIO, Env, Boolean, Bit


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
			self.assertIsInstance(subtype.Type, ConstrainedScalarSubtypeSymbol)
			self.assertEqual("integer", subtype.Type.Name.Identifier)
			self.assertEqual(left, subtype.Range.LeftBound.Value)
			self.assertEqual(2**31 - 1, subtype.Range.RightBound.Value)

	def test_DelayLength(self) -> None:
		"""``subtype DELAY_LENGTH is TIME range 0 fs to TIME'HIGH;``"""
		delayLength = Standard().Subtypes["delay_length"]

		self.assertEqual("time", delayLength.BaseType.Identifier)
		self.assertIsInstance(delayLength.Type, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("time", delayLength.Type.Name.Identifier)
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

	def test_Declarations_VHDL2019(self) -> None:
		"""VHDL-2019 adds ``range_direction`` before ``boolean``, ``file_open_state`` and ``file_origin_kind``."""
		standard = Standard(VHDLVersion.VHDL2019)

		self.assertListEqual(
			[
				"range_direction", "boolean", "bit", "character", "severity_level", "integer", "real", "time", "delay_length",
				"now", "natural", "positive", "string", "boolean_vector", "bit_vector", "integer_vector", "real_vector",
				"time_vector", "file_open_kind", "file_open_status", "file_open_state", "file_origin_kind", "foreign"
			],
			[declaration.Identifier for declaration in standard.DeclaredItems]
		)
		for declaration in standard.DeclaredItems:
			self.assertIs(standard, declaration.Parent)

	def test_Enumerations_VHDL2019(self) -> None:
		"""The new enumerations of VHDL-2019 and the literal ``read_write_mode`` of ``file_open_kind``."""
		standard = Standard(VHDLVersion.VHDL2019)
		for identifier, literals in (
			("range_direction",  ["ascending", "descending"]),
			("file_open_kind",   ["read_mode", "read_write_mode", "write_mode", "append_mode"]),
			("file_open_state",  ["state_open", "state_closed"]),
			("file_origin_kind", ["file_origin_begin", "file_origin_current", "file_origin_end"])
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
		"""After the operations of an enumerated type: the logical operators, ``rising_edge`` and ``falling_edge``."""
		boolean = Boolean()

		self.assertIsInstance(boolean, EnumeratedType)
		self.assertListEqual(
			[
				("and",          ("boolean", "boolean"), "boolean"),
				("or",           ("boolean", "boolean"), "boolean"),
				("nand",         ("boolean", "boolean"), "boolean"),
				("nor",          ("boolean", "boolean"), "boolean"),
				("xor",          ("boolean", "boolean"), "boolean"),
				("xnor",         ("boolean", "boolean"), "boolean"),
				("not",          ("boolean",),           "boolean"),
				("rising_edge",  ("boolean",),           "boolean"),
				("falling_edge", ("boolean",),           "boolean")
			],
			_signatures(boolean, 9)
		)


class Bits(Testcase):
	def test_Operators(self) -> None:
		"""
		After the operations of an enumerated type: the logical, condition and matching relational operators,
		``rising_edge`` and ``falling_edge``.
		"""
		bit = Bit()

		self.assertIsInstance(bit, EnumeratedType)
		self.assertListEqual(
			[
				("and",          ("bit", "bit"), "bit"),
				("or",           ("bit", "bit"), "bit"),
				("nand",         ("bit", "bit"), "bit"),
				("nor",          ("bit", "bit"), "bit"),
				("xor",          ("bit", "bit"), "bit"),
				("xnor",         ("bit", "bit"), "bit"),
				("not",          ("bit",),       "bit"),
				("??",           ("bit",),       "boolean"),
				("?=",           ("bit", "bit"), "bit"),
				("?/=",          ("bit", "bit"), "bit"),
				("?<",           ("bit", "bit"), "bit"),
				("?<=",          ("bit", "bit"), "bit"),
				("?>",           ("bit", "bit"), "bit"),
				("?>=",          ("bit", "bit"), "bit"),
				("rising_edge",  ("bit",),       "boolean"),
				("falling_edge", ("bit",),       "boolean")
			],
			_signatures(bit, 9)
		)

	def test_EdgeFunctions(self) -> None:
		"""``function RISING_EDGE (signal S : BIT) return BOOLEAN;`` - also ``FALLING_EDGE``, also of ``BOOLEAN``."""
		for enumeration in (Bit(), Boolean()):
			for function in enumeration.ImplicitOperations[-2:]:
				self.assertIs(enumeration, function.Parent)
				s, = function.ParameterItems
				self.assertIsInstance(s, ParameterSimpleSignalInterfaceItem)
				self.assertIs(Mode.In, s.Mode)
				self.assertIs(enumeration, s.Subtype.Reference)


class TextIOs(Testcase):
	"""Package ``std.textio`` (IEEE Std 1076-2008, 16.4)."""

	def test_Declarations(self) -> None:
		"""The declarations in the order of the standard, each with the package as parent."""
		textio = TextIO()

		self.assertListEqual(
			[
				"line", "text", "side", "width", "justify", "input", "output", "readline", *(["read"] * 16), "sread",
				"string_read", "bread", "bread", "binary_read", "binary_read", "oread", "oread", "octal_read", "octal_read",
				"hread", "hread", "hex_read", "hex_read", "writeline", "tee", *(["write"] * 9), "swrite", "string_write",
				"bwrite", "binary_write", "owrite", "octal_write", "hwrite", "hex_write"
			],
			[
				declaration.Identifiers[0] if isinstance(declaration, File) else declaration.Identifier
				for declaration in textio.DeclaredItems
			]
		)
		for declaration in textio.DeclaredItems:
			self.assertIs(textio, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator; ``justify`` is the only function."""
		textio = TextIO()

		self.assertDictEqual(
			{
				"readline": 1, "read": 16, "sread": 1, "oread": 2, "hread": 2, "writeline": 1, "tee": 1, "write": 9,
				"owrite": 1, "hwrite": 1
			},
			{identifier: len(overloads) for identifier, overloads in textio.Procedures.items()}
		)
		self.assertListEqual(["justify"], list(textio.Functions))

	def test_Line(self) -> None:
		"""``type LINE is access STRING;``"""
		textio = TextIO()
		line =   textio.Types["line"]

		self.assertIsInstance(line, AccessType)
		self.assertEqual("string", line.DesignatedSubtype.Name.Identifier)
		self.assertIs(textio, line.Parent)
		self.assertNotIn("line_vector", textio.Types)

	def test_LineVector_VHDL2019(self) -> None:
		"""VHDL-2019: ``type LINE_VECTOR is array (NATURAL range <>) of LINE;`` after ``LINE``."""
		textio =     TextIO(VHDLVersion.VHDL2019)
		lineVector = textio.Types["line_vector"]

		self.assertIsInstance(lineVector, ArrayType)
		self.assertEqual("natural", lineVector.Dimensions[0].Name.Identifier)
		self.assertEqual("line", lineVector.ElementType.Name.Identifier)
		self.assertIs(textio, lineVector.Parent)
		self.assertListEqual(
			["line", "line_vector", "text", "side", "width", "justify"],
			[declaration.Identifier for declaration in textio.DeclaredItems[:6]]
		)

	def test_Text(self) -> None:
		"""``type TEXT is file of STRING;``"""
		text = TextIO().Types["text"]

		self.assertIsInstance(text, FileType)
		self.assertEqual("string", text.DesignatedSubtype.Name.Identifier)

	def test_Side(self) -> None:
		"""``type SIDE is (RIGHT, LEFT);``"""
		side = TextIO().Types["side"]

		self.assertIsInstance(side, EnumeratedType)
		self.assertListEqual(["right", "left"], [literal.NormalizedDesignator for literal in side.Literals])

	def test_Width(self) -> None:
		"""``subtype WIDTH is NATURAL;``"""
		width = TextIO().Subtypes["width"]

		self.assertIsInstance(width, Subtype)
		self.assertEqual("natural", width.Type.Name.Identifier)

	def test_Files(self) -> None:
		"""``file INPUT : TEXT ...;``, ``file OUTPUT : TEXT ...;``"""
		textio = TextIO()
		for identifier in ("input", "output"):
			file = textio.Files[identifier]
			self.assertIsInstance(file, File)
			self.assertEqual("text", file.Subtype.Name.Identifier)

	def test_Justify(self) -> None:
		"""``function JUSTIFY (VALUE: STRING; JUSTIFIED: SIDE := RIGHT; FIELD: WIDTH := 0) return STRING;``"""
		justify = TextIO().Functions["justify"][0]

		self.assertEqual("string", justify.ReturnType.Name.Identifier)
		self.assertListEqual(["VALUE", "JUSTIFIED", "FIELD"], [item.Identifiers[0] for item in justify.ParameterItems])
		for item in justify.ParameterItems:
			self.assertIsInstance(item, ParameterConstantInterfaceItem)
			self.assertIs(Mode.In, item.Mode)

		self.assertIsNone(justify.ParameterItems[0].DefaultExpression)
		self.assertIsInstance(justify.ParameterItems[1].DefaultExpression, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("right", justify.ParameterItems[1].DefaultExpression.Name.Identifier)
		self.assertIsInstance(justify.ParameterItems[2].DefaultExpression, IntegerLiteral)
		self.assertEqual(0, justify.ParameterItems[2].DefaultExpression.Value)

	def test_ReadLine(self) -> None:
		"""``procedure READLINE (file F: TEXT; L: inout LINE);`` - also ``WRITELINE`` and ``TEE``."""
		textio = TextIO()
		for identifier in ("readline", "writeline", "tee"):
			file, line = textio.Procedures[identifier][0].ParameterItems
			self.assertIsInstance(file, ParameterFileInterfaceItem)
			self.assertEqual("text", file.Subtype.Name.Identifier)
			self.assertIsInstance(line, ParameterVariableInterfaceItem)
			self.assertIs(Mode.InOut, line.Mode)
			self.assertEqual("line", line.Subtype.Name.Identifier)

	def test_Read(self) -> None:
		"""``READ`` with and without ``GOOD``, for each of the eight types; ``L`` is ``inout``, the others ``out``."""
		reads = TextIO().Procedures["read"]

		self.assertListEqual(
			[
				subtype
				for subtype in ("bit", "bit_vector", "boolean", "character", "integer", "real", "string", "time")
				for _ in range(2)
			],
			[read.ParameterItems[1].Subtype.Name.Identifier for read in reads]
		)
		self.assertListEqual([3, 2] * 8, [len(read.ParameterItems) for read in reads])
		for read in reads:
			self.assertIsInstance(read, Procedure)
			self.assertIs(Mode.InOut, read.ParameterItems[0].Mode)
			for item in read.ParameterItems:
				self.assertIsInstance(item, ParameterVariableInterfaceItem)

			for item in read.ParameterItems[1:]:
				self.assertIs(Mode.Out, item.Mode)

	def test_SRead(self) -> None:
		"""``procedure SREAD (L: inout LINE; VALUE: out STRING; STRLEN: out NATURAL);``"""
		sread = TextIO().Procedures["sread"][0]

		self.assertListEqual(["L", "VALUE", "STRLEN"], [item.Identifiers[0] for item in sread.ParameterItems])
		self.assertListEqual(["line", "string", "natural"], [item.Subtype.Name.Identifier for item in sread.ParameterItems])

	def test_OctalHexRead(self) -> None:
		"""``OREAD`` and ``HREAD`` read a ``BIT_VECTOR``, with and without ``GOOD``."""
		textio = TextIO()
		for identifier in ("oread", "hread"):
			withGood, withoutGood = textio.Procedures[identifier]
			self.assertListEqual(
				["line", "bit_vector", "boolean"],
				[item.Subtype.Name.Identifier for item in withGood.ParameterItems]
			)
			self.assertListEqual(
				["line", "bit_vector"],
				[item.Subtype.Name.Identifier for item in withoutGood.ParameterItems]
			)

	def test_Write(self) -> None:
		"""``WRITE``: ``L`` is a variable of mode ``inout``, the others are constants of mode ``in``."""
		writes = TextIO().Procedures["write"]

		self.assertListEqual(
			[
				["L", "VALUE", "JUSTIFIED", "FIELD"],
				["L", "VALUE", "JUSTIFIED", "FIELD"],
				["L", "VALUE", "JUSTIFIED", "FIELD"],
				["L", "VALUE", "JUSTIFIED", "FIELD"],
				["L", "VALUE", "JUSTIFIED", "FIELD"],
				["L", "VALUE", "JUSTIFIED", "FIELD", "DIGITS"],
				["L", "VALUE", "FORMAT"],
				["L", "VALUE", "JUSTIFIED", "FIELD"],
				["L", "VALUE", "JUSTIFIED", "FIELD", "UNIT"]
			],
			[[item.Identifiers[0] for item in write.ParameterItems] for write in writes]
		)
		self.assertListEqual(
			["bit", "bit_vector", "boolean", "character", "integer", "real", "real", "string", "time"],
			[write.ParameterItems[1].Subtype.Name.Identifier for write in writes]
		)
		for write in writes:
			self.assertIsInstance(write.ParameterItems[0], ParameterVariableInterfaceItem)
			self.assertIs(Mode.InOut, write.ParameterItems[0].Mode)
			for item in write.ParameterItems[1:]:
				self.assertIsInstance(item, ParameterConstantInterfaceItem)
				self.assertIs(Mode.In, item.Mode)

	def test_WriteDefaults(self) -> None:
		"""``DIGITS: NATURAL := 0`` of ``REAL``, ``UNIT: TIME := NS`` of ``TIME``."""
		writes = TextIO().Procedures["write"]
		digits = writes[5].ParameterItems[4]
		unit =   writes[8].ParameterItems[4]

		self.assertEqual("natural", digits.Subtype.Name.Identifier)
		self.assertEqual(0, digits.DefaultExpression.Value)
		self.assertEqual("time", unit.Subtype.Name.Identifier)
		self.assertEqual("ns", unit.DefaultExpression.Name.Identifier)
		self.assertIsNone(writes[6].ParameterItems[2].DefaultExpression)

	def test_OctalHexWrite(self) -> None:
		"""``OWRITE`` and ``HWRITE`` write a ``BIT_VECTOR``."""
		textio = TextIO()
		for identifier in ("owrite", "hwrite"):
			write = textio.Procedures[identifier][0]
			self.assertListEqual(
				["line", "bit_vector", "side", "width"],
				[item.Subtype.Name.Identifier for item in write.ParameterItems]
			)

	def test_Aliases(self) -> None:
		"""``alias STRING_READ is SREAD [LINE, STRING, NATURAL];``: 15 aliases of procedures, each with a signature."""
		aliases = [declaration for declaration in TextIO().DeclaredItems if isinstance(declaration, Alias)]

		self.assertListEqual(
			[
				"string_read", "bread", "bread", "binary_read", "binary_read", "octal_read", "octal_read", "hex_read",
				"hex_read", "swrite", "string_write", "bwrite", "binary_write", "octal_write", "hex_write"
			],
			[alias.Identifier for alias in aliases]
		)
		self.assertListEqual(
			[
				"sread", "read", "read", "read", "read", "oread", "oread", "hread", "hread", "write", "write", "write",
				"write", "owrite", "hwrite"
			],
			[alias.Name.Name.Identifier for alias in aliases]
		)
		self.assertListEqual(
			[
				"[line, string, natural]",
				*(["[line, bit_vector, boolean]", "[line, bit_vector]"] * 4),
				"[line, string, side, width]",
				"[line, string, side, width]",
				*(["[line, bit_vector, side, width]"] * 4)
			],
			[str(alias.Signature) for alias in aliases]
		)
		for alias in aliases:
			self.assertIsNone(alias.Subtype)
			self.assertIsNone(alias.Signature.ReturnType)
			self.assertIs(alias, alias.Signature.Parent)
			self.assertTrue(alias.IsOverloadable)

	def test_AnalyzeAliases(self) -> None:
		"""
		The analysis resolves the name of each alias to the procedure of the signature's type profile, e.g.
		``BINARY_READ [LINE, BIT_VECTOR]`` to ``READ`` of ``BIT_VECTOR`` without ``GOOD``.
		"""
		design = Design("design")
		design.LoadStdLibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		textio =  design.Libraries["std"].Packages["textio"]
		aliases = [declaration for declaration in textio.DeclaredItems if isinstance(declaration, Alias)]
		self.assertEqual(15, len(aliases))
		for alias in aliases:
			self.assertIsNotNone(alias.Name.Reference)
			self.assertEqual(alias.Name.Name.Identifier, alias.Name.Reference.NormalizedDesignator)
			self.assertTrue(alias.Name.Reference.Signature.HasSameTypeProfile(alias.Signature))

		self.assertIs(textio.Procedures["read"][3], aliases[4].Name.Reference)


class Envs(Testcase):
	"""Package ``std.env`` (IEEE Std 1076-2008, 16.5)."""

	def test_Declarations(self) -> None:
		"""The declarations in the order of the standard, each with the package as parent."""
		env = Env()

		self.assertListEqual(
			["stop", "stop", "finish", "finish", "resolution_limit"],
			[declaration.Identifier for declaration in env.DeclaredItems]
		)
		for declaration in env.DeclaredItems:
			self.assertIs(env, declaration.Parent)

	def test_StopFinish(self) -> None:
		"""``procedure STOP (STATUS: INTEGER);`` and ``procedure STOP;`` - also ``FINISH``."""
		env = Env()
		for identifier in ("stop", "finish"):
			withStatus, withoutStatus = env.Procedures[identifier]
			status, = withStatus.ParameterItems
			self.assertIsInstance(status, ParameterConstantInterfaceItem)
			self.assertIs(Mode.In, status.Mode)
			self.assertTupleEqual(("STATUS",), status.Identifiers)
			self.assertEqual("integer", status.Subtype.Name.Identifier)
			self.assertListEqual([], withoutStatus.ParameterItems)

	def test_ResolutionLimit(self) -> None:
		"""``function RESOLUTION_LIMIT return DELAY_LENGTH;``"""
		resolutionLimit, = Env().Functions["resolution_limit"]

		self.assertIsInstance(resolutionLimit, Function)
		self.assertTrue(resolutionLimit.IsPure)
		self.assertEqual("delay_length", resolutionLimit.ReturnType.Name.Identifier)
		self.assertListEqual([], resolutionLimit.ParameterItems)

	def test_Declarations_VHDL2019(self) -> None:
		"""VHDL-2019 adds 82 declarations after ``resolution_limit``, each with the package as parent."""
		env = Env(VHDLVersion.VHDL2019)

		self.assertListEqual(
			[
				"stop", "stop", "finish", "finish", "resolution_limit",
				"dayofweek", "time_record", "localtime", "gmtime", "epoch", "localtime", "gmtime", "epoch", "localtime",
				"gmtime", "+", "+", "-", "-", "-", "time_to_seconds", "seconds_to_time", "to_string",
				"getenv", "getenv", "vhdl_version", "tool_type", "tool_vendor", "tool_name", "tool_edition", "tool_version",
				"directory_items", "directory", "dir_open_status", "dir_create_status", "dir_delete_status",
				"file_delete_status", "dir_open", "dir_open", "dir_close", "dir_itemexists", "dir_itemisdir", "dir_itemisfile",
				"dir_workingdir", "dir_workingdir", "dir_workingdir", "dir_createdir", "dir_createdir", "dir_createdir",
				"dir_deletedir", "dir_deletedir", "dir_deletedir", "dir_deletefile", "dir_deletefile", "dir_separator",
				"call_path_element", "to_string", "call_path_vector", "to_string", "call_path_vector_ptr", "to_string",
				"get_call_path", "file_name", "file_name", "file_path", "file_path", "file_line", "file_line",
				"isvhdlassertfailed", "isvhdlassertfailed", "getvhdlassertcount", "getvhdlassertcount", "clearvhdlassert",
				"setvhdlassertenable", "setvhdlassertenable", "getvhdlassertenable", "setvhdlassertformat",
				"setvhdlassertformat", "getvhdlassertformat", "setvhdlreadseverity", "getvhdlreadseverity",
				"pslassertfailed", "psliscovered", "setpslcoverassert", "getpslcoverassert", "pslisassertcovered",
				"clearpslstate"
			],
			[
				declaration.Identifiers[0] if isinstance(declaration, DeferredConstant) else declaration.Identifier
				for declaration in env.DeclaredItems
			]
		)
		for declaration in env.DeclaredItems:
			self.assertIs(env, declaration.Parent)

	def test_TimeRecord_VHDL2019(self) -> None:
		"""``type TIME_RECORD is record ... end record;`` with ranges of ``INTEGER`` and ``WEEKDAY : DAYOFWEEK``."""
		env =        Env(VHDLVersion.VHDL2019)
		timeRecord = env.Types["time_record"]

		self.assertIsInstance(timeRecord, RecordType)
		self.assertListEqual(
			["microsecond", "second", "minute", "hour", "day", "month", "year", "weekday", "dayofyear"],
			[element.Identifiers[0] for element in timeRecord.Elements]
		)
		integerElements = [element for element in timeRecord.Elements if element.Identifiers[0] != "weekday"]
		self.assertListEqual(
			[(0, 999_999), (0, 61), (0, 59), (0, 23), (1, 31), (0, 11), (1, 4095), (0, 365)],
			[
				(element.Subtype.Constraint.LeftBound.Value, element.Subtype.Constraint.RightBound.Value)
				for element in integerElements
			]
		)
		for element in integerElements:
			self.assertIsInstance(element.Subtype, ConstrainedScalarSubtypeSymbol)
			self.assertEqual("integer", element.Subtype.Name.Identifier)

		self.assertEqual("dayofweek", timeRecord.Elements[7].Subtype.Name.Identifier)

		self.assertListEqual(
			["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
			[literal.NormalizedDesignator for literal in env.Types["dayofweek"].Literals]
		)

	def test_TimeFunctions_VHDL2019(self) -> None:
		"""``LOCALTIME``, ``GMTIME`` and ``EPOCH`` without parameters are impure; the operators of ``TIME_RECORD``."""
		env = Env(VHDLVersion.VHDL2019)
		for identifier in ("localtime", "gmtime", "epoch"):
			overloads = env.Functions[identifier]
			self.assertListEqual([False] + [True] * (len(overloads) - 1), [function.IsPure for function in overloads])
			self.assertListEqual([], overloads[0].ParameterItems)

		self.assertListEqual(
			[("TREC", "DELTA"), ("DELTA", "TREC")],
			[tuple(item.Identifiers[0] for item in plus.ParameterItems) for plus in env.Functions["+"]]
		)
		for operator in (*env.Functions["+"], *env.Functions["-"]):
			self.assertIsInstance(operator, Operator)

		difference = env.Functions["-"][2]
		self.assertTupleEqual(("TR1", "TR2"), difference.ParameterItems[0].Identifiers)
		self.assertEqual("real", difference.ReturnType.Name.Identifier)

	def test_ToString_VHDL2019(self) -> None:
		"""``FRAC_DIGITS: INTEGER range 0 to 6 := 0``; ``Separator : STRING := "" & LF`` of the call path functions."""
		toStrings = Env(VHDLVersion.VHDL2019).Functions["to_string"]

		self.assertListEqual(
			["time_record", "call_path_element", "call_path_vector", "call_path_vector_ptr"],
			[function.ParameterItems[0].Subtype.Name.Identifier for function in toStrings]
		)
		self.assertListEqual([True, False, False, False], [function.IsPure for function in toStrings])

		fracDigits = toStrings[0].ParameterItems[1]
		self.assertIsInstance(fracDigits.Subtype, ConstrainedScalarSubtypeSymbol)
		self.assertEqual(6, fracDigits.Subtype.Constraint.RightBound.Value)
		self.assertEqual(0, fracDigits.DefaultExpression.Value)

		for function in toStrings[2:]:
			separator = function.ParameterItems[1].DefaultExpression
			self.assertIsInstance(separator, ConcatenationExpression)
			self.assertIsInstance(separator.LeftOperand, StringLiteral)
			self.assertEqual("", separator.LeftOperand.Value)
			self.assertEqual("lf", separator.RightOperand.Name.Identifier)

	def test_Directories_VHDL2019(self) -> None:
		"""``DIRECTORY_ITEMS`` is an access to ``LINE_VECTOR``; ``DIR_OPEN`` returns ``Dir`` as ``out`` parameter."""
		env = Env(VHDLVersion.VHDL2019)

		directoryItems = env.Types["directory_items"]
		self.assertIsInstance(directoryItems, AccessType)
		self.assertEqual("line_vector", directoryItems.DesignatedSubtype.Name.Identifier)
		self.assertListEqual(
			[("Name", "line"), ("Items", "directory_items")],
			[(element.Identifiers[0], element.Subtype.Name.Identifier) for element in env.Types["directory"].Elements]
		)

		for dirOpen in (env.Procedures["dir_open"][0], env.Functions["dir_open"][0]):
			directory = dirOpen.ParameterItems[0]
			self.assertIsInstance(directory, ParameterVariableInterfaceItem)
			self.assertIs(Mode.Out, directory.Mode)
			self.assertEqual("directory", directory.Subtype.Name.Identifier)

		self.assertFalse(env.Functions["dir_open"][0].IsPure)
		self.assertEqual("false", env.Functions["dir_createdir"][0].ParameterItems[1].DefaultExpression.Name.Identifier)
		self.assertIsInstance(env.DeferredConstants["dir_separator"], DeferredConstant)

	def test_StatusTypes_VHDL2019(self) -> None:
		"""The four status types share literals like ``STATUS_OK``."""
		env = Env(VHDLVersion.VHDL2019)
		for identifier, literals in (
			("dir_open_status",    [
				"status_ok", "status_not_found", "status_no_directory", "status_access_denied", "status_error"
			]),
			("dir_create_status",  ["status_ok", "status_item_exists", "status_access_denied", "status_error"]),
			("dir_delete_status",  [
				"status_ok", "status_no_directory", "status_not_empty", "status_access_denied", "status_error"
			]),
			("file_delete_status", ["status_ok", "status_no_file", "status_access_denied", "status_error"])
		):
			enumeration = env.Types[identifier]
			self.assertIsInstance(enumeration, EnumeratedType)
			self.assertListEqual(literals, [literal.NormalizedDesignator for literal in enumeration.Literals])

	def test_Overloads_VHDL2019(self) -> None:
		"""The number of overloads per designator."""
		env = Env(VHDLVersion.VHDL2019)

		self.assertDictEqual(
			{
				"stop": 2, "finish": 2, "dir_open": 1, "dir_close": 1, "dir_workingdir": 1, "dir_createdir": 2,
				"dir_deletedir": 2, "dir_deletefile": 1, "clearvhdlassert": 1, "setvhdlassertenable": 2,
				"setvhdlassertformat": 2, "setvhdlreadseverity": 1, "setpslcoverassert": 1, "clearpslstate": 1
			},
			{identifier: len(overloads) for identifier, overloads in env.Procedures.items()}
		)
		self.assertDictEqual(
			{
				"resolution_limit": 1, "localtime": 3, "gmtime": 3, "epoch": 2, "+": 2, "-": 3, "time_to_seconds": 1,
				"seconds_to_time": 1, "to_string": 4, "getenv": 2, "vhdl_version": 1, "tool_type": 1, "tool_vendor": 1,
				"tool_name": 1, "tool_edition": 1, "tool_version": 1, "dir_open": 1, "dir_itemexists": 1, "dir_itemisdir": 1,
				"dir_itemisfile": 1, "dir_workingdir": 2, "dir_createdir": 1, "dir_deletedir": 1, "dir_deletefile": 1,
				"get_call_path": 1, "file_name": 2, "file_path": 2, "file_line": 2, "isvhdlassertfailed": 2,
				"getvhdlassertcount": 2, "getvhdlassertenable": 1, "getvhdlassertformat": 1, "getvhdlreadseverity": 1,
				"pslassertfailed": 1, "psliscovered": 1, "getpslcoverassert": 1, "pslisassertcovered": 1
			},
			{identifier: len(overloads) for identifier, overloads in env.Functions.items()}
		)

	def test_AssertDefaults_VHDL2019(self) -> None:
		"""``Enable : boolean := TRUE``, ``Level : SEVERITY_LEVEL := NOTE`` and ``:= FAILURE`` of the read severity."""
		env = Env(VHDLVersion.VHDL2019)
		enable, levelEnable = env.Procedures["setvhdlassertenable"]

		self.assertEqual("true", enable.ParameterItems[0].DefaultExpression.Name.Identifier)
		self.assertListEqual(
			["note", "true"],
			[item.DefaultExpression.Name.Identifier for item in levelEnable.ParameterItems]
		)
		self.assertEqual(
			"failure",
			env.Procedures["setvhdlreadseverity"][0].ParameterItems[0].DefaultExpression.Name.Identifier
		)
		valid = env.Procedures["setvhdlassertformat"][1].ParameterItems[2]
		self.assertIsInstance(valid, ParameterVariableInterfaceItem)
		self.assertIs(Mode.Out, valid.Mode)
