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
GHDL as oracle for pyVHDLModel.Formatting.VHDL: written expressions must pass ``ghdl -a --std=08``.

Each expression becomes the value of a constant declaration in a package. Skipped if GHDL is not on PATH.
"""
from textwrap                    import dedent
from typing                      import Iterable
from unittest                    import skipIf

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import ParameterAssociationItem
from pyVHDLModel.Base            import Direction, Mode, SimpleRange
from pyVHDLModel.DesignUnit      import Component
from pyVHDLModel.Expression      import (
	IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral,
	StringLiteral, BinaryBitStringLiteral, DecimalBitStringLiteral, HexadecimalBitStringLiteral,
	NegationExpression, InverseExpression, AbsoluteExpression, UnaryXorExpression, TypeConversion, SubExpression,
	DescendingRangeExpression, AdditionExpression, SubtractionExpression, ConcatenationExpression, MultiplyExpression,
	DivisionExpression, ModuloExpression, RemainderExpression, ExponentiationExpression, AndExpression, NandExpression,
	OrExpression, EqualExpression, UnequalExpression, LessThanExpression, MatchingEqualExpression,
	ShiftLeftLogicExpression, ShiftRightLogicExpression, RotateLeftExpression, QualifiedExpression,
	SimpleAggregateElement, IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement,
	OthersAggregateElement, Aggregate
)
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Interface       import (
	GenericConstantInterfaceItem, GenericTypeInterfaceItem, PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem,
	ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, ParameterSimpleSignalInterfaceItem,
	ParameterViewSignalInterfaceItem, ParameterFileInterfaceItem, ModeViewDeclaration, SimpleModeViewElement,
	CompositeModeViewElement
)
from pyVHDLModel.Name            import SimpleName, ParenthesisName, AttributeName
from pyVHDLModel.Object          import Constant, DeferredConstant, Variable, SharedVariable, Signal, File
from pyVHDLModel.Symbol          import RecordElementSymbol, SimpleSubtypeSymbol, IndexedObjectOrFunctionCallSymbol
from pyVHDLModel.Symbol          import ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol
from pyVHDLModel.Symbol          import ConstrainedRecordSubtypeSymbol, ModeViewSymbol

from tests.unit.Writer           import _GHDL, _analyze, _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


_DECLARATIONS = dedent("""\
	library ieee;
	use     ieee.std_logic_1164.all;
	use     ieee.numeric_std.all;

	package oracle is
		constant a : integer                := 3;
		constant b : integer                := 5;
		constant c : integer                := 2;
		constant p : boolean                := true;
		constant q : boolean                := false;
		constant r : boolean                := true;
		constant v : bit_vector(7 downto 0) := x"A5";
		constant u : unsigned(7 downto 0)   := x"5A";
		constant s : std_ulogic             := '1';

		type record_t is record
			valid : bit;
			data  : integer;
		end record;
	""")  #: Declarations the written expressions refer to.


def _package(constants: Iterable[tuple[str, str]]) -> str:
	"""Source text of a package declaring one constant per (subtype, value) pair."""
	declarations = "".join(
		f"\tconstant c{index} : {subtype} := {value};\n" for index, (subtype, value) in enumerate(constants)
	)
	return f"{_DECLARATIONS}{declarations}end package;\n"


def _integer(name: str) -> SimpleSubtypeSymbol:
	"""Reference to a subtype, as type mark of a qualified expression or type conversion."""
	return SimpleSubtypeSymbol(SimpleName(name))


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracle(Testcase):
	def test_Integer(self) -> None:
		writer = VHDLWriter()
		expressions = [
			MultiplyExpression(AdditionExpression(_object("a"), _object("b")), _object("c")),
			AdditionExpression(_object("a"), MultiplyExpression(_object("b"), _object("c"))),
			SubtractionExpression(_object("a"), SubtractionExpression(_object("b"), _object("c"))),
			SubtractionExpression(SubtractionExpression(_object("a"), _object("b")), _object("c")),
			DivisionExpression(_object("a"), MultiplyExpression(_object("b"), _object("c"))),
			ExponentiationExpression(_object("c"), ExponentiationExpression(_object("c"), _object("c"))),
			ExponentiationExpression(ExponentiationExpression(_object("c"), _object("c")), _object("c")),
			NegationExpression(NegationExpression(_object("a"))),
			NegationExpression(MultiplyExpression(_object("a"), _object("b"))),
			NegationExpression(AdditionExpression(_object("a"), _object("b"))),
			MultiplyExpression(NegationExpression(_object("a")), _object("b")),
			AdditionExpression(NegationExpression(_object("a")), _object("b")),
			AdditionExpression(_object("a"), NegationExpression(_object("b"))),
			SubtractionExpression(_object("a"), IntegerLiteral(-1)),
			AdditionExpression(IntegerLiteral(-1), _object("a")),
			AbsoluteExpression(NegationExpression(_object("a"))),
			ModuloExpression(_object("a"), RemainderExpression(_object("b"), _object("c"))),
			QualifiedExpression(_integer("integer"), SubExpression(AdditionExpression(_object("a"), _object("b")))),
			TypeConversion(_integer("integer"), FloatingPointLiteral(2.5)),
		]

		result = _analyze(_package(("integer", writer.Format(expression)) for expression in expressions))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_Boolean(self) -> None:
		writer = VHDLWriter()
		expressions = [
			OrExpression(AndExpression(_object("p"), _object("q")), _object("r")),
			AndExpression(AndExpression(_object("p"), _object("q")), _object("r")),
			AndExpression(_object("p"), AndExpression(_object("q"), _object("r"))),
			NandExpression(NandExpression(_object("p"), _object("q")), _object("r")),
			InverseExpression(AndExpression(_object("p"), _object("q"))),
			InverseExpression(InverseExpression(_object("p"))),
			EqualExpression(EqualExpression(_object("a"), _object("b")), _object("p")),
			AndExpression(EqualExpression(_object("a"), _object("b")), UnequalExpression(_object("a"), _object("c"))),
			LessThanExpression(
				AdditionExpression(_object("a"), _object("b")),
				MultiplyExpression(_object("b"), _object("c"))
			),
		]

		result = _analyze(_package(("boolean", writer.Format(expression)) for expression in expressions))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_Vector(self) -> None:
		writer = VHDLWriter()
		constants = [
			("bit_vector", writer.Format(ShiftLeftLogicExpression(_object("v"), IntegerLiteral(2)))),
			("bit_vector", writer.Format(ShiftRightLogicExpression(
				ShiftLeftLogicExpression(_object("v"), IntegerLiteral(1)),
				IntegerLiteral(1)
			))),
			("bit_vector", writer.Format(RotateLeftExpression(
				_object("v"),
				AdditionExpression(_object("c"), IntegerLiteral(1))
			))),
			("bit_vector", writer.Format(ConcatenationExpression(_object("v"), _object("v")))),
			("bit", writer.Format(UnaryXorExpression(_object("v")))),
			("unsigned", writer.Format(AdditionExpression(_object("u"), IntegerLiteral(1)))),
			("std_ulogic", writer.Format(MatchingEqualExpression(_object("s"), CharacterLiteral("1")))),
			("bit_vector", writer.Format(IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("v"), [
				DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))
			])))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_Name(self) -> None:
		writer = VHDLWriter()
		constants = [
			("integer", writer.Format(IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("maximum"), [
				ParameterAssociationItem(None, _object("a")),
				ParameterAssociationItem(None, _object("b"))
			])))),
			("integer", writer.Format(IndexedObjectOrFunctionCallSymbol(AttributeName("high", SimpleName("integer"))))),
			("unsigned(7 downto 0)", writer.Format(IndexedObjectOrFunctionCallSymbol(ParenthesisName(
				SimpleName("to_unsigned"),
				[ParameterAssociationItem(None, _object("a")), ParameterAssociationItem(SimpleName("size"), IntegerLiteral(8))]
			)))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_Literal(self) -> None:
		writer = VHDLWriter()
		constants = [
			("real", writer.Format(FloatingPointLiteral(1e-9))),
			("real", writer.Format(FloatingPointLiteral(-2.5))),
			("time", writer.Format(PhysicalIntegerLiteral(10, "ns"))),
			("time", writer.Format(PhysicalFloatingLiteral(1.5, "ns"))),
			("character", writer.Format(CharacterLiteral("'"))),
			("string", writer.Format(StringLiteral("say \"hi\""))),
			("bit_vector", writer.Format(BinaryBitStringLiteral("1010"))),
			("bit_vector", writer.Format(HexadecimalBitStringLiteral("A5", 8, False))),
			("bit_vector", writer.Format(HexadecimalBitStringLiteral("F", 12, True))),
			("bit_vector", writer.Format(DecimalBitStringLiteral("160", 8))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_Aggregate(self) -> None:
		writer = VHDLWriter()
		constants = [
			("bit_vector(3 downto 0)", writer.Format(Aggregate([
				SimpleAggregateElement(CharacterLiteral("1")),
				SimpleAggregateElement(CharacterLiteral("0")),
				SimpleAggregateElement(CharacterLiteral("1")),
				SimpleAggregateElement(CharacterLiteral("0"))
			]))),
			("bit_vector(3 downto 0)", writer.Format(Aggregate([
				IndexedAggregateElement(AdditionExpression(_object("c"), IntegerLiteral(1)), CharacterLiteral("1")),
				OthersAggregateElement(CharacterLiteral("0"))
			]))),
			("bit_vector(3 downto 0)", writer.Format(Aggregate([
				RangedAggregateElement(SimpleRange(IntegerLiteral(1), IntegerLiteral(2), Direction.To), CharacterLiteral("1")),
				OthersAggregateElement(CharacterLiteral("0"))
			]))),
			("record_t", writer.Format(Aggregate([
				NamedAggregateElement(RecordElementSymbol(SimpleName("valid")), CharacterLiteral("1")),
				NamedAggregateElement(RecordElementSymbol(SimpleName("data")), _object("a"))
			]))),
			("bit_vector", writer.Format(QualifiedExpression(
				_integer("bit_vector"),
				Aggregate([IndexedAggregateElement(IntegerLiteral(0), CharacterLiteral("1"))])
			))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_UpperCase(self) -> None:
		writer = VHDLWriter(VHDLStyle(KeywordCase.Upper))
		constants = [
			("integer", writer.Format(ModuloExpression(AbsoluteExpression(NegationExpression(_object("a"))), _object("b")))),
			("boolean", writer.Format(InverseExpression(OrExpression(_object("p"), _object("q"))))),
			("bit_vector(3 downto 0)", writer.Format(Aggregate([OthersAggregateElement(CharacterLiteral("0"))]))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_IllegalWithoutParentheses(self) -> None:
		"""
		The oracle rejects what the writer parenthesizes.

		GHDL accepts ``a ** b ** c``, which the grammar (``factor ::= primary [ ** primary ]``) rejects.
		"""
		for value in ("a + -b", "a * -b", "- -a", "abs -a"):
			with self.subTest(value=value):
				self.assertNotEqual(0, _analyze(_package([("integer", value)])).returncode)

		for value in ("not not p", "p and q or r", "p nand q nand r", "a = b = p"):
			with self.subTest(value=value):
				self.assertNotEqual(0, _analyze(_package([("boolean", value)])).returncode)


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracleDeclarations(Testcase):
	def test_Objects(self) -> None:
		writer =   VHDLWriter()
		byte =     ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [
			DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		])
		count =    ConstrainedScalarSubtypeSymbol(
			SimpleName("integer"),
			SimpleRange(IntegerLiteral(0), IntegerLiteral(15), Direction.To)
		)
		frame =    ConstrainedRecordSubtypeSymbol(SimpleName("frame_t"), {
			RecordElementSymbol(SimpleName("data")): DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		})
		package =  "".join(writer.Format(declaration) for declaration in (
			Constant(["A", "B"], _integer("natural"), IntegerLiteral(1)),
			DeferredConstant(["C"], _integer("natural")),
			Signal(["s1", "s2"], byte, _object("v")),
			Signal(["s3"], count),
			Signal(["s4"], frame),
			SharedVariable(["counter"], _integer("counter_t")),
			File(["log"], _integer("text_file")),
		))
		variables = "".join(writer.Format(declaration) for declaration in (
			Variable(["v1"], count, IntegerLiteral(3)),
			Variable(["v2"], byte),
		))
		source =   dedent("""\
			package objects is
				constant v : bit_vector(7 downto 0) := x"A5";
				type frame_t is record
					data : bit_vector;
				end record;
				type text_file is file of string;
				type counter_t is protected
				end protected;
			{package}end package;

			package body objects is
				constant C : natural := 2;
				type counter_t is protected body
				end protected body;
			end package body;

			entity tb is
			end entity;

			architecture sim of tb is
			begin
				process
			{variables}	begin
					wait;
				end process;
			end architecture;
			""").format(package=package, variables=variables)

		result = _analyze(source)

		self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_Component(self) -> None:
		component = Component(
			"counter",
			[
				GenericConstantInterfaceItem(["BITS"], Mode.Default, _integer("positive"), IntegerLiteral(8)),
				GenericConstantInterfaceItem(["INIT"], Mode.In, _integer("natural")),
				GenericTypeInterfaceItem("element_t")
			],
			[
				PortSimpleSignalInterfaceItem(["clk", "rst"], Mode.In, _integer("bit")),
				PortSimpleSignalInterfaceItem(["enable"], Mode.Default, _integer("bit"), CharacterLiteral("1")),
				PortSimpleSignalInterfaceItem(["value"], Mode.Out, _integer("element_t")),
				PortSimpleSignalInterfaceItem(["data"], Mode.InOut, _integer("bit")),
				PortSimpleSignalInterfaceItem(["last"], Mode.Buffer, _integer("bit"))
			]
		)

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				source = f"package components is\n{VHDLWriter(style).Format(component)}end package;\n"

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_Parameters(self) -> None:
		writer =     VHDLWriter()
		parameters = "; ".join(writer.Format(item) for item in (
			ParameterConstantInterfaceItem(["a"], Mode.In, _integer("integer"), IntegerLiteral(0)),
			ParameterVariableInterfaceItem(["b"], Mode.InOut, _integer("integer")),
			ParameterSimpleSignalInterfaceItem(["c"], Mode.Out, _integer("bit")),
			ParameterSimpleSignalInterfaceItem(["d"], Mode.Default, _integer("bit")),
			ParameterFileInterfaceItem(["e"], _integer("text_file"))
		))
		source =     dedent("""\
			package parameters is
				type text_file is file of string;
				procedure p({parameters});
			end package;
			""").format(parameters=parameters)

		result = _analyze(source)

		self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_ModeView(self) -> None:
		"""Mode views are VHDL-2019."""
		writer =      VHDLWriter()
		declaration = ModeViewDeclaration("master", _integer("bus_t"), [
			SimpleModeViewElement(["valid", "data"], Mode.Out),
			SimpleModeViewElement(["ready"], Mode.In),
			CompositeModeViewElement(["request"], ModeViewSymbol(SimpleName("request_master")))
		])
		port =        writer.Format(PortViewSignalInterfaceItem(["link"], ModeViewSymbol(SimpleName("master"))))
		parameter =   writer.Format(ParameterViewSignalInterfaceItem(["link"], ModeViewSymbol(SimpleName("master"))))
		source =      dedent("""\
			package views is
				type request_t is record
					address : bit_vector(7 downto 0);
				end record;
				view request_master of request_t is
					address : out;
				end view;
				type bus_t is record
					valid, data, ready : bit;
					request : request_t;
				end record;
			{declaration}	procedure p({parameter});
			end package;

			use work.views.all;

			entity e is
				port ({port});
			end entity;
			""").format(declaration=writer.Format(declaration), parameter=parameter, port=port)

		result = _analyze(source, std="19")

		self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)
