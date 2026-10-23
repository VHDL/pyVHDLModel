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
"""Tests for the walk of sequential statements (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Common     import ConditionalExpression, SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.Expression import IntegerLiteral, StringLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Sequential import IndexedChoice, SequentialVariableAssignment, \
                                   SequentialConditionalVariableAssignment, SequentialSelectedVariableAssignment, \
                                   SequentialReportStatement, NullStatement, ReturnStatement, WaitStatement
from pyVHDLModel.Symbol     import SignalSymbol, VariableSymbol, SimpleObjectOrFunctionCallSymbol

from tests.unit.Visitor     import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Assignments(Testcase):
	def test_Variable(self) -> None:
		target =     VariableSymbol(SimpleName("v"))
		value =      IntegerLiteral(0)
		assignment = SequentialVariableAssignment(target, value)
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual([
			("VisitSequentialVariableAssignment",  assignment),
			("VisitSymbol",                        target),
			("VisitSimpleName",                    target.Name),
			("DepartSimpleName",                   target.Name),
			("DepartSymbol",                       target),
			("VisitVariableAssignment",            assignment),
			("VisitIntegerLiteral",                value),
			("DepartIntegerLiteral",               value),
			("DepartSequentialVariableAssignment", assignment),
		], recorder.Events)

	def test_ConditionalVariable(self) -> None:
		first =      ConditionalExpression(IntegerLiteral(1), SimpleObjectOrFunctionCallSymbol(SimpleName("c")))
		second =     ConditionalExpression(IntegerLiteral(0))
		assignment = SequentialConditionalVariableAssignment(VariableSymbol(SimpleName("v")), [first, second])
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual(
			[("VisitConditionalExpression", first), ("VisitWhen", first), ("DepartConditionalExpression", first),
			 ("VisitElse", assignment), ("VisitConditionalExpression", second), ("DepartConditionalExpression", second)],
			[event for event in recorder.Events if event[0] in (
				"VisitConditionalExpression", "DepartConditionalExpression", "VisitWhen", "VisitElse"
			)]
		)

	def test_SelectedVariable(self) -> None:
		choice =     IndexedChoice(IntegerLiteral(0))
		selected =   SelectedExpression([choice], IntegerLiteral(1))
		others =     OthersSelectedExpression(IntegerLiteral(0))
		assignment = SequentialSelectedVariableAssignment(
			VariableSymbol(SimpleName("v")),
			SimpleObjectOrFunctionCallSymbol(SimpleName("sel")),
			[selected, others]
		)
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual([
			"VisitSequentialSelectedVariableAssignment",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitSelect",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitVariableAssignment",
			"VisitSelectedExpression", "VisitIntegerLiteral", "DepartIntegerLiteral", "VisitWhen",
			"VisitIndexedChoice", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartIndexedChoice",
			"DepartSelectedExpression",
			"VisitComma",
			"VisitOthersSelectedExpression", "VisitIntegerLiteral", "DepartIntegerLiteral", "VisitWhen",
			"DepartOthersSelectedExpression",
			"DepartSequentialSelectedVariableAssignment",
		], [event[0] for event in recorder.Events])


class Statements(Testcase):
	def test_Report(self) -> None:
		message =   StringLiteral("done")
		statement = SequentialReportStatement(message)
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			("VisitSequentialReportStatement",  statement),
			("VisitReport",                     statement),
			("VisitStringLiteral",              message),
			("DepartStringLiteral",             message),
			("DepartSequentialReportStatement", statement),
		], recorder.Events)

	def test_Return(self) -> None:
		value =     IntegerLiteral(1)
		statement = ReturnStatement(value)
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			("VisitReturnStatement",  statement),
			("VisitIntegerLiteral",   value),
			("DepartIntegerLiteral",  value),
			("DepartReturnStatement", statement),
		], recorder.Events)

	def test_Wait(self) -> None:
		"""The sensitivity list follows ``on``, the condition ``until`` and the timeout ``for``."""
		clock =     SignalSymbol(SimpleName("clk"))
		reset =     SignalSymbol(SimpleName("rst"))
		condition = SimpleObjectOrFunctionCallSymbol(SimpleName("done"))
		timeout =   IntegerLiteral(10)
		statement = WaitStatement([clock, reset], condition, timeout)
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			"VisitWaitStatement",
			"VisitOn",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitComma",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitUntil",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitFor",
			"VisitIntegerLiteral", "DepartIntegerLiteral",
			"DepartWaitStatement",
		], [event[0] for event in recorder.Events])

	def test_Process(self) -> None:
		"""A process walks its statements after ``begin``."""
		statement = NullStatement()
		process =   ProcessStatement(statements=[statement])
		recorder =  FullRecorder()

		process.Visit(recorder)

		self.assertEqual([
			("VisitProcessStatement",  process),
			("VisitIs",                process),
			("VisitBegin",             process),
			("VisitNullStatement",     statement),
			("DepartNullStatement",    statement),
			("DepartProcessStatement", process),
		], recorder.Events)
