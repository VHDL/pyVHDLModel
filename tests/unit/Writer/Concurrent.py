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
"""Tests for writing concurrent statements with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import ParameterAssociationItem
from pyVHDLModel.Base            import Direction, SimpleRange, WaveformElement
from pyVHDLModel.Common          import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Concurrent      import ProcessStatement, ConcurrentProcedureCall, ConcurrentSimpleSignalAssignment, \
                                        ConcurrentSelectedSignalAssignment, ConcurrentConditionalSignalAssignment, \
                                        ConcurrentAssertStatement
from pyVHDLModel.Expression      import IntegerLiteral, CharacterLiteral, StringLiteral, EnumerationLiteral, \
                                        PhysicalIntegerLiteral, EqualExpression, GreaterThanExpression, OrExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, AllName
from pyVHDLModel.Object          import Variable
from pyVHDLModel.Sequential      import IndexedChoice, RangedChoice, NullStatement

from tests.unit                  import _signalSymbol, _subtypeSymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SignalAssignments(Testcase):
	def test_Simple(self) -> None:
		assignment = ConcurrentSimpleSignalAssignment(None, _signalSymbol("q"), [WaveformElement(_object("d"))])

		self.assertEqual("q <= d;\n", VHDLWriter().Format(assignment))

	def test_Simple_Waveform(self) -> None:
		assignment = ConcurrentSimpleSignalAssignment("drive", _signalSymbol("q"), [
			WaveformElement(CharacterLiteral("1"), PhysicalIntegerLiteral(5, "ns")),
			WaveformElement(CharacterLiteral("0"), PhysicalIntegerLiteral(10, "ns"))
		])

		self.assertEqual("drive : q <= '1' after 5 ns, '0' after 10 ns;\n", VHDLWriter().Format(assignment))

	def test_Conditional(self) -> None:
		assignment = ConcurrentConditionalSignalAssignment(None, _signalSymbol("q"), [
			ConditionalWaveform([WaveformElement(_object("a"))], EqualExpression(_object("sel"), CharacterLiteral("0"))),
			ConditionalWaveform([WaveformElement(_object("b"))], EqualExpression(_object("sel"), CharacterLiteral("1"))),
			ConditionalWaveform([WaveformElement(CharacterLiteral("X"))])
		])

		self.assertEqual(
			"q <= a when sel = '0' else b when sel = '1' else 'X';\n",
			VHDLWriter().Format(assignment)
		)

	def test_Conditional_Condition(self) -> None:
		"""A condition binds looser than the reserved words around it, so it needs no parentheses."""
		assignment = ConcurrentConditionalSignalAssignment(None, _signalSymbol("q"), [
			ConditionalWaveform([WaveformElement(_object("a"))], OrExpression(_object("x"), _object("y"))),
			ConditionalWaveform([WaveformElement(_object("b"))])
		])

		self.assertEqual("q <= a when x or y else b;\n", VHDLWriter().Format(assignment))

	def test_Selected(self) -> None:
		assignment = ConcurrentSelectedSignalAssignment("mux", _signalSymbol("q"), _object("sel"), [
			SelectedWaveform([IndexedChoice(IntegerLiteral(0))], [WaveformElement(_object("a"))]),
			SelectedWaveform(
				[
					IndexedChoice(IntegerLiteral(1)),
					RangedChoice(SimpleRange(IntegerLiteral(2), IntegerLiteral(3), Direction.To))
				],
				[WaveformElement(_object("b"))]
			),
			OthersSelectedWaveform([WaveformElement(_object("c"))])
		])

		self.assertEqual(
			"mux : with sel select q <= a when 0, b when 1 | 2 to 3, c when others;\n",
			VHDLWriter().Format(assignment)
		)

	def test_UpperCase(self) -> None:
		assignment = ConcurrentSelectedSignalAssignment(None, _signalSymbol("q"), _object("sel"), [
			SelectedWaveform(
				[IndexedChoice(IntegerLiteral(0))],
				[WaveformElement(_object("a"), PhysicalIntegerLiteral(1, "ns"))]
			),
			OthersSelectedWaveform([WaveformElement(_object("c"))])
		])

		self.assertEqual(
			"WITH sel SELECT q <= a AFTER 1 ns WHEN 0, c WHEN OTHERS;\n",
			VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(assignment)
		)


class Statements(Testcase):
	def test_ProcedureCall(self) -> None:
		call = ConcurrentProcedureCall(None, _object("check"), [
			ParameterAssociationItem(None, _object("clk")),
			ParameterAssociationItem(SimpleName("limit"), IntegerLiteral(4))
		])

		self.assertEqual("check(clk, limit => 4);\n", VHDLWriter().Format(call))

	def test_ProcedureCall_WithoutParameters(self) -> None:
		self.assertEqual("tick : tock;\n", VHDLWriter().Format(ConcurrentProcedureCall("tick", _object("tock"))))

	def test_Assert(self) -> None:
		assertion = ConcurrentAssertStatement(GreaterThanExpression(_object("BITS"), IntegerLiteral(0)))

		self.assertEqual("assert BITS > 0;\n", VHDLWriter().Format(assertion))

	def test_Assert_ReportSeverity(self) -> None:
		assertion = ConcurrentAssertStatement(
			GreaterThanExpression(_object("BITS"), IntegerLiteral(0)),
			StringLiteral("no bits"),
			EnumerationLiteral("failure"),
			"check"
		)

		self.assertEqual(
			"check : assert BITS > 0 report \"no bits\" severity failure;\n",
			VHDLWriter().Format(assertion)
		)

	def test_Assert_UpperCase(self) -> None:
		assertion = ConcurrentAssertStatement(_object("ok"), severity=EnumerationLiteral("note"))

		self.assertEqual("ASSERT ok SEVERITY note;\n", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(assertion))


class Processes(Testcase):
	def test_Process(self) -> None:
		process = ProcessStatement(
			"count",
			[Variable(["value"], _subtypeSymbol("natural"), IntegerLiteral(0))],
			sensitivityList=[SimpleName("clk"), SimpleName("rst")]
		)

		self.assertEqual(dedent("""\
			count : process (clk, rst) is
			  variable value : natural := 0;
			begin
			end process count;
			"""), VHDLWriter().Format(process))

	def test_Process_All(self) -> None:
		"""An ``all`` name without prefix is the sensitivity list ``all``."""
		process = ProcessStatement(sensitivityList=[AllName(None)])

		self.assertEqual("process (all) is\nbegin\nend process;\n", VHDLWriter().Format(process))

	def test_Process_WithoutSensitivityList(self) -> None:
		self.assertEqual("process is\nbegin\nend process;\n", VHDLWriter().Format(ProcessStatement()))

	def test_Process_Statements(self) -> None:
		"""Sequential statements have no walk yet: a process with statements raises, nothing is skipped."""
		process = ProcessStatement(statements=[NullStatement()])

		with self.assertRaises(NotImplementedError):
			VHDLWriter().Format(process)
