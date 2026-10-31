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
"""Tests for writing sequential statements with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import ParameterAssociationItem
from pyVHDLModel.Base            import WaveformElement, Direction, SimpleRange
from pyVHDLModel.Common          import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform, \
                                        ConditionalExpression, SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Concurrent      import ProcessStatement
from pyVHDLModel.Expression      import IntegerLiteral, CharacterLiteral, StringLiteral, PhysicalIntegerLiteral, \
                                        AdditionExpression, EqualExpression, LessThanExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Sequential      import IndexedChoice, SequentialProcedureCall, SequentialSimpleSignalAssignment, \
                                        SequentialVariableAssignment, SequentialConditionalVariableAssignment, \
                                        SequentialConditionalSignalAssignment, SequentialSelectedVariableAssignment, \
                                        SequentialSelectedSignalAssignment, SignalForceAssignment, \
                                        SignalReleaseAssignment, SequentialReportStatement, SequentialAssertStatement, \
                                        NullStatement, ReturnStatement, WaitStatement, RangedChoice, IfBranch, \
                                        ElsifBranch, ElseBranch, IfStatement, Case, OthersCase, CaseStatement, \
                                        EndlessLoopStatement, ForLoopStatement, WhileLoopStatement, NextStatement, \
                                        ExitStatement
from pyVHDLModel.Subprogram      import Function
from pyVHDLModel.Symbol          import AggregateSymbol

from tests.unit                  import _signalSymbol, _subtypeSymbol, _variableSymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SignalAssignments(Testcase):
	def test_Simple(self) -> None:
		assignment = SequentialSimpleSignalAssignment(_signalSymbol("q"), [
			WaveformElement(_object("d"), PhysicalIntegerLiteral(1, "ns"))
		])

		self.assertEqual("q <= d after 1 ns;\n", VHDLWriter().Format(assignment))

	def test_Conditional(self) -> None:
		assignment = SequentialConditionalSignalAssignment(_signalSymbol("q"), [
			ConditionalWaveform([WaveformElement(_object("a"))], EqualExpression(_object("sel"), CharacterLiteral("0"))),
			ConditionalWaveform([WaveformElement(_object("b"))])
		])

		self.assertEqual("q <= a when sel = '0' else b;\n", VHDLWriter().Format(assignment))

	def test_Selected(self) -> None:
		assignment = SequentialSelectedSignalAssignment(_signalSymbol("q"), _object("sel"), [
			SelectedWaveform([IndexedChoice(IntegerLiteral(0))], [WaveformElement(_object("a"))]),
			OthersSelectedWaveform([WaveformElement(_object("b"))])
		], "mux")

		self.assertEqual("mux : with sel select q <= a when 0, b when others;\n", VHDLWriter().Format(assignment))

	def test_Force(self) -> None:
		assignment = SignalForceAssignment(_signalSymbol("q"), CharacterLiteral("1"))

		self.assertEqual("q <= force '1';\n", VHDLWriter().Format(assignment))

	def test_Release(self) -> None:
		self.assertEqual("q <= release;\n", VHDLWriter().Format(SignalReleaseAssignment(_signalSymbol("q"))))


class VariableAssignments(Testcase):
	def test_Simple(self) -> None:
		assignment = SequentialVariableAssignment(
			_variableSymbol("count"),
			AdditionExpression(_object("count"), IntegerLiteral(1)),
			"increment"
		)

		self.assertEqual("increment : count := count + 1;\n", VHDLWriter().Format(assignment))

	def test_AggregateTarget(self) -> None:
		"""``(carry, sum) := ...`` - a group of targets on the left-hand side."""
		target =     AggregateSymbol([_variableSymbol("carry"), _variableSymbol("sum")])
		assignment = SequentialVariableAssignment(target, _object("result"))

		self.assertEqual("(carry, sum) := result;\n", VHDLWriter().Format(assignment))

	def test_Conditional(self) -> None:
		assignment = SequentialConditionalVariableAssignment(_variableSymbol("v"), [
			ConditionalExpression(_object("a"), _object("enable")),
			ConditionalExpression(_object("b"))
		])

		self.assertEqual("v := a when enable else b;\n", VHDLWriter().Format(assignment))

	def test_Selected(self) -> None:
		assignment = SequentialSelectedVariableAssignment(_variableSymbol("v"), _object("sel"), [
			SelectedExpression([IndexedChoice(IntegerLiteral(0)), IndexedChoice(IntegerLiteral(1))], _object("a")),
			OthersSelectedExpression(_object("b"))
		])

		self.assertEqual("with sel select v := a when 0 | 1, b when others;\n", VHDLWriter().Format(assignment))


class Statements(Testcase):
	def test_ProcedureCall(self) -> None:
		call = SequentialProcedureCall(_object("check"), [
			ParameterAssociationItem(None, _object("value")),
			ParameterAssociationItem(SimpleName("limit"), IntegerLiteral(4))
		])

		self.assertEqual("check(value, limit => 4);\n", VHDLWriter().Format(call))

	def test_Report(self) -> None:
		statement = SequentialReportStatement(StringLiteral("done"), _object("note"), "finish")

		self.assertEqual("finish : report \"done\" severity note;\n", VHDLWriter().Format(statement))

	def test_Assert(self) -> None:
		assertion = SequentialAssertStatement(_object("ok"), StringLiteral("failed"))

		self.assertEqual("assert ok report \"failed\";\n", VHDLWriter().Format(assertion))

	def test_Null(self) -> None:
		self.assertEqual("null;\n", VHDLWriter().Format(NullStatement()))

	def test_Return(self) -> None:
		statement = ReturnStatement(AdditionExpression(_object("count"), IntegerLiteral(1)))

		self.assertEqual("return count + 1;\n", VHDLWriter().Format(statement))

	def test_Return_WithoutValue(self) -> None:
		self.assertEqual("return;\n", VHDLWriter().Format(ReturnStatement()))

	def test_Wait(self) -> None:
		statement = WaitStatement(
			[_signalSymbol("clk"), _signalSymbol("rst")],
			EqualExpression(_object("clk"), CharacterLiteral("1")),
			PhysicalIntegerLiteral(10, "ns")
		)

		self.assertEqual("wait on clk, rst until clk = '1' for 10 ns;\n", VHDLWriter().Format(statement))

	def test_Wait_Forever(self) -> None:
		self.assertEqual("wait;\n", VHDLWriter().Format(WaitStatement()))

	def test_UpperCase(self) -> None:
		writer = VHDLWriter(VHDLStyle(KeywordCase.Upper))

		self.assertEqual("WAIT FOR 1 ns;\n", writer.Format(WaitStatement(timeout=PhysicalIntegerLiteral(1, "ns"))))
		self.assertEqual("q <= RELEASE;\n", writer.Format(SignalReleaseAssignment(_signalSymbol("q"))))
		self.assertEqual("NULL;\n", writer.Format(NullStatement()))


class StatementParts(Testcase):
	def test_Process(self) -> None:
		process = ProcessStatement("p", statements=[
			SequentialVariableAssignment(_variableSymbol("v"), IntegerLiteral(0)),
			WaitStatement()
		])

		self.assertEqual(dedent("""\
			p : process is
			begin
			  v := 0;
			  wait;
			end process p;
			"""), VHDLWriter().Format(process))

	def test_Function(self) -> None:
		function = Function("one", _subtypeSymbol("integer"), statements=[ReturnStatement(IntegerLiteral(1))])

		self.assertEqual(dedent("""\
			function one return integer is
			begin
			  return 1;
			end function one;
			"""), VHDLWriter().Format(function))


def _increment() -> SequentialVariableAssignment:
	"""Variable assignment incrementing ``v``."""
	return SequentialVariableAssignment(_variableSymbol("v"), AdditionExpression(_object("v"), IntegerLiteral(1)))


class CompoundStatements(Testcase):
	def test_If(self) -> None:
		statement = IfStatement(
			IfBranch(_object("a"), [_increment()]),
			[ElsifBranch(_object("b"), [NullStatement()])],
			ElseBranch([_increment(), _increment()]),
			"check"
		)

		self.assertEqual(dedent("""\
			check : if a then
			  v := v + 1;
			elsif b then
			  null;
			else
			  v := v + 1;
			  v := v + 1;
			end if check;
			"""), VHDLWriter().Format(statement))

	def test_If_Only(self) -> None:
		statement = IfStatement(IfBranch(EqualExpression(_object("v"), IntegerLiteral(0)), [NullStatement()]))

		self.assertEqual("if v = 0 then\n  null;\nend if;\n", VHDLWriter().Format(statement))

	def test_Case(self) -> None:
		statement = CaseStatement(_object("v"), [
			Case(
				[
					IndexedChoice(IntegerLiteral(0)),
					RangedChoice(SimpleRange(IntegerLiteral(1), IntegerLiteral(2), Direction.To))
				],
				[_increment()]
			),
			OthersCase([NullStatement()])
		])

		self.assertEqual(dedent("""\
			case v is
			  when 0 | 1 to 2 =>
			    v := v + 1;
			  when others =>
			    null;
			end case;
			"""), VHDLWriter().Format(statement))

	def test_ForLoop(self) -> None:
		statement = ForLoopStatement(
			"i",
			SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To),
			[NextStatement(_object("skip")), _increment()],
			"outer"
		)

		self.assertEqual(dedent("""\
			outer : for i in 0 to 3 loop
			  next when skip;
			  v := v + 1;
			end loop outer;
			"""), VHDLWriter().Format(statement))

	def test_WhileLoop(self) -> None:
		statement = WhileLoopStatement(LessThanExpression(_object("v"), IntegerLiteral(8)), [_increment()])

		self.assertEqual("while v < 8 loop\n  v := v + 1;\nend loop;\n", VHDLWriter().Format(statement))

	def test_EndlessLoop(self) -> None:
		statement = EndlessLoopStatement([ExitStatement(_object("done")), ExitStatement()], "forever")

		self.assertEqual(dedent("""\
			forever : loop
			  exit when done;
			  exit;
			end loop forever;
			"""), VHDLWriter().Format(statement))

	def test_Nested(self) -> None:
		statement = ForLoopStatement("i", SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To), [
			IfStatement(IfBranch(_object("a"), [ExitStatement()]))
		])

		self.assertEqual(dedent("""\
			for i in 0 to 1 loop
			  if a then
			    exit;
			  end if;
			end loop;
			"""), VHDLWriter().Format(statement))

	def test_UpperCase(self) -> None:
		statement = IfStatement(IfBranch(_object("a"), [NullStatement()]), elseBranch=ElseBranch([NullStatement()]))

		self.assertEqual(
			"IF a THEN\n  NULL;\nELSE\n  NULL;\nEND IF;\n",
			VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(statement)
		)
