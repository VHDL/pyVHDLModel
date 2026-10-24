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
from pathlib                     import Path
from textwrap                    import dedent
from typing                      import Iterable
from unittest                    import skipIf

from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Document
from pyVHDLModel.Association     import ParameterAssociationItem, GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Base            import Direction, Mode, SimpleRange, WaveformElement
from pyVHDLModel.Common          import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform, \
                                        ConditionalExpression, SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Concurrent      import ProcessStatement, ConcurrentProcedureCall, ConcurrentSimpleSignalAssignment, \
                                        ConcurrentSelectedSignalAssignment, ConcurrentConditionalSignalAssignment, \
                                        ConcurrentAssertStatement, ComponentInstantiation, EntityInstantiation, \
                                        ConfigurationInstantiation, ConcurrentBlockStatement, IfGenerateBranch, \
                                        ElsifGenerateBranch, ElseGenerateBranch, IfGenerateStatement, \
                                        IndexedGenerateChoice, RangedGenerateChoice, GenerateCase, OthersGenerateCase, \
                                        CaseGenerateStatement, ForGenerateStatement
from pyVHDLModel.Declaration     import EntityClass, Alias, Attribute, AttributeSpecification
from pyVHDLModel.Configuration   import EntityAspectEntity, EntityAspectOpen, BindingIndication, AllInstantiationList, \
                                        OthersInstantiationList, ComponentConfiguration, BlockConfiguration
from pyVHDLModel.DesignUnit      import LibraryClause, UseClause, ContextReference, Context, Package, PackageBody, \
                                        Entity, Architecture, Configuration, Component
from pyVHDLModel.Expression      import EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, \
                                        PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral, \
                                        StringLiteral, BinaryBitStringLiteral, DecimalBitStringLiteral, \
                                        HexadecimalBitStringLiteral, NegationExpression, InverseExpression, \
                                        AbsoluteExpression, UnaryXorExpression, TypeConversion, SubExpression, \
                                        AscendingRangeExpression, DescendingRangeExpression, AdditionExpression, \
                                        SubtractionExpression, ConcatenationExpression, MultiplyExpression, \
                                        DivisionExpression, ModuloExpression, RemainderExpression, \
                                        ExponentiationExpression, AndExpression, NandExpression, OrExpression, \
                                        EqualExpression, UnequalExpression, LessThanExpression, \
                                        MatchingEqualExpression, ShiftLeftLogicExpression, ShiftRightLogicExpression, \
                                        RotateLeftExpression, QualifiedExpression, SimpleAggregateElement, \
                                        IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement, \
                                        OthersAggregateElement, Aggregate, GreaterThanExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Instantiation   import ProcedureInstantiation, FunctionInstantiation, PackageInstantiation
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                        PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                        ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                        ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                        ParameterFileInterfaceItem, ModeViewDeclaration, SimpleModeViewElement, \
                                        CompositeModeViewElement, GenericProcedureInterfaceItem, \
                                        GenericFunctionInterfaceItem
from pyVHDLModel.Name            import SimpleName, ParenthesisName, AttributeName, SelectedName, AllName, OpenName
from pyVHDLModel.Object          import Constant, DeferredConstant, Variable, SharedVariable, Signal, File
from pyVHDLModel.Sequential      import IndexedChoice, RangedChoice, SequentialProcedureCall, \
                                        SequentialSimpleSignalAssignment, SequentialVariableAssignment, \
                                        SequentialConditionalVariableAssignment, \
                                        SequentialConditionalSignalAssignment, SequentialSelectedVariableAssignment, \
                                        SequentialSelectedSignalAssignment, SignalForceAssignment, \
                                        SignalReleaseAssignment, SequentialReportStatement, SequentialAssertStatement, \
                                        NullStatement, ReturnStatement, WaitStatement, IfBranch, ElsifBranch, \
                                        ElseBranch, IfStatement, Case, OthersCase, CaseStatement, \
                                        EndlessLoopStatement, ForLoopStatement, WhileLoopStatement, NextStatement, \
                                        ExitStatement
from pyVHDLModel.Subprogram      import Procedure, Function, ProcedureMethod, FunctionMethod
from pyVHDLModel.Symbol          import RecordElementSymbol, SimpleSubtypeSymbol, IndexedObjectOrFunctionCallSymbol, \
                                        ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, \
                                        ConstrainedRecordSubtypeSymbol, ModeViewSymbol, SubprogramReferenceSymbol, \
                                        LibraryReferenceSymbol, AllPackageMembersReferenceSymbol, \
                                        ContextReferenceSymbol, EntitySymbol, ArchitectureSymbol, PackageSymbol, \
                                        PackageReferenceSymbol, ComponentInstantiationSymbol, SignalSymbol, \
                                        EntityInstantiationSymbol, ConfigurationInstantiationSymbol, \
                                        ConfigurationSymbol, VariableSymbol
from pyVHDLModel.Type            import AnonymousType, Subtype, EnumeratedType, IntegerType, RealType, PhysicalType, \
                                        ArrayType, RecordTypeElement, RecordType, AccessType, FileType, ProtectedType, \
                                        ProtectedTypeBody

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

	def test_Types(self) -> None:
		def to(left: int, right: int) -> AscendingRangeExpression:
			"""Nested function returning an ascending range of two integer literals."""
			return AscendingRangeExpression(IntegerLiteral(left), IntegerLiteral(right))

		byte =         ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [
			DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		])
		declarations = (
			EnumeratedType("state", [EnumerationLiteral("Idle"), EnumerationLiteral("Busy")]),
			EnumeratedType("logic", [EnumerationLiteral("'0'"), EnumerationLiteral("'1'"), EnumerationLiteral("'Z'")]),
			IntegerType("nibble", to(0, 15)),
			RealType("fraction", AscendingRangeExpression(FloatingPointLiteral(0.0), FloatingPointLiteral(1.0))),
			PhysicalType("distance", to(0, 1000000), "um", [
				("mm", PhysicalIntegerLiteral(1000, "um")),
				("m",  PhysicalIntegerLiteral(1000, "mm"))
			]),
			Subtype("byte", byte),
			Subtype("word", _integer("integer")),
			ArrayType("memory", [to(0, 255)], _integer("byte")),
			ArrayType("matrix", [_integer("natural"), _integer("natural")], _integer("bit")),
			AnonymousType("node"),
			AccessType("pointer", _integer("node")),
			RecordType("node", [
				RecordTypeElement(["value", "count"], _integer("integer")),
				RecordTypeElement(["successor"], _integer("pointer"))
			]),
			FileType("text_file", _integer("string")),
		)

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				writer = VHDLWriter(style)
				source = f"package types is\n{''.join(writer.Format(d) for d in declarations)}end package;\n"

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_AliasesAndAttributes(self) -> None:
		writer =       VHDLWriter()
		low =          DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))
		declarations = (
			Alias("clock", _object("clk")),
			Alias(
				"low",
				IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("data"), [low])),
				ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [
					DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))
				])
			),
			Attribute("keep", _integer("boolean")),
			Attribute("bits", _integer("natural")),
			AttributeSpecification(
				[SimpleName("clk"), SimpleName("data")],
				SimpleName("keep"),
				EntityClass.Signal,
				EnumerationLiteral("true")
			),
			AttributeSpecification([SimpleName("byte")], SimpleName("bits"), EntityClass.Subtype, IntegerLiteral(8)),
		)
		source =       dedent("""\
			package declarations is
				signal clk : bit;
				signal data : bit_vector(7 downto 0);
				subtype byte is bit_vector(7 downto 0);
			{declarations}end package;
			""").format(declarations="".join(writer.Format(declaration) for declaration in declarations))

		result = _analyze(source)

		self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_Subprograms(self) -> None:
		def parameters() -> list:
			"""Nested function returning a constant and a variable parameter."""
			return [
				ParameterConstantInterfaceItem(["a"], Mode.In, _integer("integer")),
				ParameterVariableInterfaceItem(["b"], Mode.Out, _integer("integer"))
			]

		def body() -> list:
			"""Nested function returning the declared items of a subprogram body."""
			return [Constant(["ONE"], _integer("integer"), IntegerLiteral(1))]

		def genericProcedure() -> Procedure:
			"""Nested function returning a generic procedure."""
			return Procedure(
				"tick",
				genericItems=[GenericConstantInterfaceItem(["N"], Mode.Default, _integer("natural"))],
				parameterItems=[ParameterConstantInterfaceItem(["x"], Mode.Default, _integer("integer"))]
			)

		def genericFunction() -> Function:
			"""Nested function returning a generic function with a generic type and a generic function."""
			greater = GenericFunctionInterfaceItem("greater", _integer("boolean"))
			greater.AddParameterItem(ParameterConstantInterfaceItem(["l", "r"], Mode.Default, _integer("T")))
			return Function(
				"largest",
				_integer("T"),
				genericItems=[GenericTypeInterfaceItem("T"), greater],
				parameterItems=[ParameterConstantInterfaceItem(["l", "r"], Mode.Default, _integer("T"))]
			)

		def withBody(subprogram: Procedure | Function) -> Procedure | Function:
			"""Nested function adding the declared items of a body to a subprogram."""
			for item in body():
				subprogram.AddDeclaredItem(item)

			return subprogram

		def reporter() -> Procedure:
			"""Nested function returning a procedure with a generic procedure."""
			logger = GenericProcedureInterfaceItem("log")
			logger.AddParameterItem(ParameterConstantInterfaceItem(["message"], Mode.In, _integer("string")))
			return Procedure("report_all", genericItems=[logger])

		declarations = (
			Procedure("reset"),
			Procedure("p", parameterItems=parameters()),
			Function("parity", _integer("bit"), parameterItems=[
				ParameterSimpleSignalInterfaceItem(["data"], Mode.In, _integer("bit_vector"))
			]),
			Function("value", _integer("natural"), False),
			genericProcedure(),
			genericFunction(),
			reporter(),
			ProtectedType("counter", [ProcedureMethod("increment"), FunctionMethod("count", _integer("natural"), False)]),
		)
		bodies = (
			Procedure("reset", declaredItems=body()),
			Procedure("p", parameterItems=parameters(), declaredItems=[
				Procedure("inner", declaredItems=[Variable(["v"], _integer("bit"))])
			]),
			Function("parity", _integer("bit"), declaredItems=body(), parameterItems=[
				ParameterSimpleSignalInterfaceItem(["data"], Mode.In, _integer("bit_vector"))
			]),
			Function("value", _integer("natural"), False, declaredItems=body()),
			withBody(genericProcedure()),
			withBody(genericFunction()),
			withBody(reporter()),
			ProcedureInstantiation("tick_8", SubprogramReferenceSymbol(SimpleName("tick")), [
				GenericAssociationItem(SimpleName("N"), IntegerLiteral(8))
			]),
			FunctionInstantiation("largest_int", SubprogramReferenceSymbol(SimpleName("largest")), genericAssociationItems=[
				GenericAssociationItem(SimpleName("T"), _integer("integer")),
				GenericAssociationItem(SimpleName("greater"), _object('">"'))
			]),
			ProtectedTypeBody("counter", [
				Variable(["counter"], _integer("natural"), IntegerLiteral(0)),
				ProcedureMethod("increment", declaredItems=body()),
				FunctionMethod("count", _integer("natural"), False, declaredItems=body())
			]),
		)

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				writer = VHDLWriter(style)
				source = (
					f"package subprograms is\n{''.join(writer.Format(d) for d in declarations)}end package;\n\n"
					f"package body subprograms is\n{''.join(writer.Format(b) for b in bodies)}end package body;\n"
				)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracleDesignUnits(Testcase):
	def test_Document(self) -> None:
		def useAll(library: str, package: str) -> UseClause:
			"""Nested function returning a use clause of all members of a package."""
			return UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName(package, SimpleName(library))))])

		def ieee() -> LibraryClause:
			"""Nested function returning a library clause of library ``ieee``."""
			return LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])

		def work(name: str) -> SelectedName:
			"""Nested function returning the name of a design unit in library ``work``."""
			return SelectedName(name, SimpleName("work"))

		ports = [
			PortSimpleSignalInterfaceItem(["clk"], Mode.In, _integer("std_logic")),
			PortSimpleSignalInterfaceItem(["count"], Mode.Out, _integer("natural"))
		]
		designUnits = (
			Context("project", [ieee(), useAll("ieee", "std_logic_1164")]),
			Package(
				"generic_fifo",
				genericItems=[GenericConstantInterfaceItem(["DEPTH"], Mode.Default, _integer("positive"))],
				declaredItems=[Constant(["SIZE"], _integer("positive"), _object("DEPTH"))]
			),
			PackageInstantiation(
				"fifo_4",
				PackageReferenceSymbol(work("generic_fifo")),
				genericAssociationItems=[GenericAssociationItem(SimpleName("DEPTH"), IntegerLiteral(4))]
			),
			Package("utilities", [ieee(), useAll("ieee", "numeric_std")], declaredItems=[
				Function("ones", _integer("natural")),
				Component("sub", portItems=[PortSimpleSignalInterfaceItem(["a"], Mode.In, _integer("bit"))])
			]),
			PackageBody(PackageSymbol(SimpleName("utilities")), declaredItems=[
				Function("ones", _integer("natural"), declaredItems=[Constant(["ONE"], _integer("natural"), IntegerLiteral(1))])
			]),
			Entity(
				"counter",
				[ContextReference([ContextReferenceSymbol(work("project"))])],
				[GenericConstantInterfaceItem(["BITS"], Mode.Default, _integer("positive"), IntegerLiteral(8))],
				ports,
				[Constant(["MAXIMUM"], _integer("natural"), IntegerLiteral(255))]
			),
			Architecture("rtl", EntitySymbol(SimpleName("counter")), [useAll("work", "utilities")], [
				Signal(["value"], _integer("natural"), IntegerLiteral(0)),
				Component("sub", portItems=[PortSimpleSignalInterfaceItem(["a"], Mode.In, _integer("bit"))])
			]),
			Entity("sub", portItems=[PortSimpleSignalInterfaceItem(["a"], Mode.In, _integer("bit"))]),
			Architecture("behav", EntitySymbol(SimpleName("sub"))),
			Configuration("counter_cfg", EntitySymbol(SimpleName("counter")), BlockConfiguration(
				ArchitectureSymbol(SimpleName("rtl")),
				[
					ComponentConfiguration(
						AllInstantiationList(),
						ComponentInstantiationSymbol(SimpleName("sub")),
						BindingIndication(
							EntityAspectEntity(EntitySymbol(work("sub")), ArchitectureSymbol(SimpleName("behav"))),
							portAssociationItems=[PortAssociationItem(SimpleName("a"), OpenName())]
						)
					),
					ComponentConfiguration(
						OthersInstantiationList(),
						ComponentInstantiationSymbol(SimpleName("sub")),
						BindingIndication(EntityAspectOpen())
					),
				]
			)),
		)

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				document = Document(Path("oracle.vhdl"))
				for designUnit in designUnits:
					document._AddDesignUnit(designUnit)

				source = VHDLWriter(style).Format(document)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracleConcurrentStatements(Testcase):
	def test_Statements(self) -> None:
		def target(name: str) -> SignalSymbol:
			"""Nested function returning a reference to a signal as assignment target."""
			return SignalSymbol(SimpleName(name))

		def waveform(name: str) -> list:
			"""Nested function returning a waveform of one object."""
			return [WaveformElement(_object(name))]

		statements = (
			ConcurrentSimpleSignalAssignment(None, target("q1"), [
				WaveformElement(_object("a"), PhysicalIntegerLiteral(1, "ns")),
				WaveformElement(CharacterLiteral("0"), PhysicalIntegerLiteral(2, "ns"))
			]),
			ConcurrentConditionalSignalAssignment("cond", target("q2"), [
				ConditionalWaveform(waveform("a"), EqualExpression(_object("sel"), IntegerLiteral(0))),
				ConditionalWaveform(waveform("b"), AndExpression(_object("en"), _object("en"))),
				ConditionalWaveform([WaveformElement(CharacterLiteral("0"))])
			]),
			ConcurrentSelectedSignalAssignment("mux", target("q3"), _object("sel"), [
				SelectedWaveform([IndexedChoice(IntegerLiteral(0))], waveform("a")),
				SelectedWaveform(
					[
					IndexedChoice(IntegerLiteral(1)),
					RangedChoice(SimpleRange(IntegerLiteral(2), IntegerLiteral(3), Direction.To))
				],
					waveform("b")
				),
				OthersSelectedWaveform([WaveformElement(CharacterLiteral("1"))])
			]),
			ConcurrentProcedureCall(None, _object("check"), [ParameterAssociationItem(None, _object("a"))]),
			ConcurrentProcedureCall("tick", _object("tock")),
			ConcurrentAssertStatement(_object("en"), StringLiteral("disabled"), _object("note"), "check_en"),
			ProcessStatement("p", [Variable(["v"], _integer("bit"))], sensitivityList=[SimpleName("a"), SimpleName("b")]),
			ProcessStatement(sensitivityList=[AllName(None)]),
		)
		architecture = Architecture("rtl", EntitySymbol(SimpleName("e")), declaredItems=[
			Signal(["a", "b", "q1", "q2", "q3"], _integer("bit")),
			Signal(["en"], _integer("boolean"), EnumerationLiteral("true")),
			Signal(["sel"], _integer("natural"), IntegerLiteral(0)),
		], statements=statements)
		header = dedent("""\
			entity e is
			end entity;

			package checks is
				procedure check(signal s : in bit);
				procedure tock;
			end package;

			package body checks is
				procedure check(signal s : in bit) is
				begin
				end procedure;
				procedure tock is
				begin
				end procedure;
			end package body;

			use work.checks.all;

			""")

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				source = header + VHDLWriter(style).Format(architecture)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_Hierarchy(self) -> None:
		def assign(target: str, source: str) -> ConcurrentSimpleSignalAssignment:
			"""Nested function returning a concurrent signal assignment of one object to a signal."""
			waveform = [WaveformElement(_object(source))]
			return ConcurrentSimpleSignalAssignment(None, SignalSymbol(SimpleName(target)), waveform)

		def work(name: str) -> SelectedName:
			"""Nested function returning the name of a design unit in library ``work``."""
			return SelectedName(name, SimpleName("work"))

		def bit(name: str) -> Signal:
			"""Nested function returning a signal declaration of type ``bit``."""
			return Signal([name], _integer("bit"))

		ports = [GenericAssociationItem(SimpleName("BITS"), IntegerLiteral(4))]
		statements = (
			EntityInstantiation("u1", EntityInstantiationSymbol(work("sub")), ArchitectureSymbol(SimpleName("rtl")), ports, [
				PortAssociationItem(SimpleName("a"), _object("x")),
				PortAssociationItem(SimpleName("y"), _object("q1"))
			]),
			ComponentInstantiation("u2", ComponentInstantiationSymbol(SimpleName("sub")), portAssociationItems=[
				PortAssociationItem(None, _object("x")),
				PortAssociationItem(None, OpenName())
			]),
			ConfigurationInstantiation("u3", ConfigurationInstantiationSymbol(work("sub_cfg")), portAssociationItems=[
				PortAssociationItem(SimpleName("a"), _object("x")),
				PortAssociationItem(SimpleName("y"), _object("q2"))
			]),
			ConcurrentBlockStatement(
				"blk",
				[GenericConstantInterfaceItem(["G"], Mode.Default, _integer("positive"))],
				[GenericAssociationItem(SimpleName("G"), IntegerLiteral(2))],
				[PortSimpleSignalInterfaceItem(["bp"], Mode.In, _integer("bit"))],
				[PortAssociationItem(SimpleName("bp"), _object("x"))],
				[bit("inner")],
				[assign("inner", "bp")]
			),
			IfGenerateStatement(
				"gen_if",
				IfGenerateBranch(GreaterThanExpression(_object("W"), IntegerLiteral(8)), statements=[assign("q3", "x")]),
				[ElsifGenerateBranch(
					GreaterThanExpression(_object("W"), IntegerLiteral(4)),
					[bit("t")],
					[assign("t", "x"), assign("q3", "t")],
					alternativeLabel="middle"
				)],
				ElseGenerateBranch(statements=[assign("q3", "x")], alternativeLabel="small")
			),
			CaseGenerateStatement("gen_case", _object("W"), [
				GenerateCase(
					[
						IndexedGenerateChoice(IntegerLiteral(0)),
						RangedGenerateChoice(SimpleRange(IntegerLiteral(1), IntegerLiteral(2), Direction.To))
					],
					statements=[assign("q4", "x")]
				),
				GenerateCase(
					[IndexedGenerateChoice(IntegerLiteral(3))],
					statements=[assign("q4", "x")],
					alternativeLabel="three"
				),
				OthersGenerateCase(declaredItems=[bit("t")], statements=[assign("t", "x"), assign("q4", "t")])
			]),
			ForGenerateStatement(
				"gen_for",
				"i",
				SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To),
				[bit("t")],
				[assign("t", "x")]
			),
		)
		architecture = Architecture("rtl", EntitySymbol(SimpleName("e")), declaredItems=[
			Constant(["W"], _integer("natural"), IntegerLiteral(6)),
			*(bit(name) for name in ("x", "q1", "q2", "q3", "q4")),
			Component("sub", portItems=[
				PortSimpleSignalInterfaceItem(["a"], Mode.In, _integer("bit")),
				PortSimpleSignalInterfaceItem(["y"], Mode.Out, _integer("bit"))
			]),
		], statements=statements)
		header = dedent("""\
			entity sub is
				generic (BITS : natural := 1);
				port (a : in bit; y : out bit);
			end entity;

			architecture rtl of sub is
			begin
				y <= a;
			end architecture;

			configuration sub_cfg of sub is
				for rtl
				end for;
			end configuration;

			entity e is
			end entity;

			""")

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				source = header + VHDLWriter(style).Format(architecture)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracleSequentialStatements(Testcase):
	def test_Statements(self) -> None:
		def signal(name: str) -> SignalSymbol:
			"""Nested function returning a reference to a signal."""
			return SignalSymbol(SimpleName(name))

		def variable(name: str) -> VariableSymbol:
			"""Nested function returning a reference to a variable."""
			return VariableSymbol(SimpleName(name))

		statements = [
			SequentialSimpleSignalAssignment(signal("q"), [WaveformElement(_object("d"), PhysicalIntegerLiteral(1, "ns"))]),
			SequentialVariableAssignment(variable("v"), AdditionExpression(_object("v"), IntegerLiteral(1)), "increment"),
			SequentialConditionalVariableAssignment(variable("v"), [
				ConditionalExpression(IntegerLiteral(1), _object("en")),
				ConditionalExpression(IntegerLiteral(0))
			]),
			SequentialConditionalSignalAssignment(signal("q"), [
				ConditionalWaveform([WaveformElement(_object("d"))], _object("en")),
				ConditionalWaveform([WaveformElement(CharacterLiteral("0"))])
			]),
			SequentialSelectedVariableAssignment(variable("v"), _object("v"), [
				SelectedExpression([IndexedChoice(IntegerLiteral(0)), IndexedChoice(IntegerLiteral(1))], IntegerLiteral(2)),
				OthersSelectedExpression(IntegerLiteral(0))
			]),
			SequentialSelectedSignalAssignment(signal("q"), _object("v"), [
				SelectedWaveform([IndexedChoice(IntegerLiteral(0))], [WaveformElement(CharacterLiteral("1"))]),
				OthersSelectedWaveform([WaveformElement(CharacterLiteral("0"))])
			]),
			SignalForceAssignment(signal("q"), CharacterLiteral("1")),
			SignalReleaseAssignment(signal("q")),
			SequentialProcedureCall(_object("check"), [ParameterAssociationItem(None, _object("v"))]),
			SequentialReportStatement(StringLiteral("tick"), _object("note")),
			SequentialAssertStatement(_object("en"), StringLiteral("disabled"), _object("warning")),
			NullStatement("nothing"),
			WaitStatement(
				[signal("d")],
				EqualExpression(_object("d"), CharacterLiteral("1")),
				PhysicalIntegerLiteral(10, "ns")
			),
			WaitStatement(),
		]
		process = ProcessStatement("p", [Variable(["v"], _integer("natural"), IntegerLiteral(0))], statements)
		check =   Procedure(
			"check",
			parameterItems=[ParameterConstantInterfaceItem(["x"], Mode.In, _integer("natural"))],
			statements=[ReturnStatement()]
		)
		twice =   Function(
			"twice",
			_integer("natural"),
			parameterItems=[ParameterConstantInterfaceItem(["x"], Mode.Default, _integer("natural"))],
			statements=[ReturnStatement(MultiplyExpression(_object("x"), IntegerLiteral(2)))]
		)
		architecture = Architecture("sim", EntitySymbol(SimpleName("tb")), declaredItems=[
			Signal(["d", "q"], _integer("bit")),
			Signal(["en"], _integer("boolean"), EnumerationLiteral("true")),
			check,
			twice,
		], statements=[process])

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				source = "entity tb is\nend entity;\n\n" + VHDLWriter(style).Format(architecture)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)

	def test_CompoundStatements(self) -> None:
		def increment() -> SequentialVariableAssignment:
			"""Nested function returning a variable assignment incrementing ``v``."""
			value = AdditionExpression(_object("v"), IntegerLiteral(1))
			return SequentialVariableAssignment(VariableSymbol(SimpleName("v")), value)

		statements = [
			IfStatement(
				IfBranch(EqualExpression(_object("v"), IntegerLiteral(0)), [increment()]),
				[ElsifBranch(_object("en"), [NullStatement()])],
				ElseBranch([increment(), increment()]),
				"check"
			),
			CaseStatement(_object("v"), [
				Case(
					[
						IndexedChoice(IntegerLiteral(0)),
						RangedChoice(SimpleRange(IntegerLiteral(1), IntegerLiteral(2), Direction.To))
					],
					[increment()]
				),
				OthersCase([NullStatement()])
			]),
			ForLoopStatement("i", SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To), [
				NextStatement(_object("en")),
				increment()
			], "outer"),
			WhileLoopStatement(LessThanExpression(_object("v"), IntegerLiteral(8)), [increment()]),
			EndlessLoopStatement([ExitStatement(_object("en")), ExitStatement()]),
			WaitStatement(),
		]
		process = ProcessStatement("p", [Variable(["v"], _integer("natural"), IntegerLiteral(0))], statements)
		architecture = Architecture("sim", EntitySymbol(SimpleName("tb")), declaredItems=[
			Signal(["en"], _integer("boolean"), EnumerationLiteral("true")),
		], statements=[process])

		for style in (VHDLStyle(), VHDLStyle(KeywordCase.Upper, IndentStyle.SmartTabs)):
			with self.subTest(style=style.KeywordCase):
				source = "entity tb is\nend entity;\n\n" + VHDLWriter(style).Format(architecture)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)
