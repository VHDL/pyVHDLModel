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

from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Common     import ConditionalExpression, SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.Expression import IntegerLiteral, StringLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Sequential import IndexedChoice, SequentialVariableAssignment, \
                                   SequentialConditionalVariableAssignment, SequentialSelectedVariableAssignment, \
                                   SequentialReportStatement, NullStatement, ReturnStatement, WaitStatement, IfBranch, \
                                   ElsifBranch, ElseBranch, IfStatement, Case, OthersCase, CaseStatement, \
                                   EndlessLoopStatement, ForLoopStatement, WhileLoopStatement, NextStatement, \
                                   ExitStatement
from pyVHDLModel.Symbol     import SignalSymbol, VariableSymbol, SimpleObjectOrFunctionCallSymbol, AggregateSymbol

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
			("VisitTerminator",                    assignment),
			("DepartSequentialVariableAssignment", assignment),
		], recorder.Events)

	def test_Variable_AggregateTarget(self) -> None:
		carry =      VariableSymbol(SimpleName("carry"))
		sum =        VariableSymbol(SimpleName("sum"))
		target =     AggregateSymbol([carry, sum])
		value =      IntegerLiteral(0)
		assignment = SequentialVariableAssignment(target, value)
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual([
			("VisitSequentialVariableAssignment",  assignment),
			("VisitAggregateSymbol",               target),
			("VisitSymbol",                        carry),
			("VisitSimpleName",                    carry.Name),
			("DepartSimpleName",                   carry.Name),
			("DepartSymbol",                       carry),
			("VisitElementSeparator",              target),
			("VisitSymbol",                        sum),
			("VisitSimpleName",                    sum.Name),
			("DepartSimpleName",                   sum.Name),
			("DepartSymbol",                       sum),
			("DepartAggregateSymbol",              target),
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
			"VisitSelectedAlternativeSeparator",
			"VisitOthersSelectedExpression", "VisitIntegerLiteral", "DepartIntegerLiteral", "VisitWhen",
			"DepartOthersSelectedExpression",
			"VisitTerminator", "DepartSequentialSelectedVariableAssignment",
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
			("VisitTerminator",                 statement),
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
			("VisitTerminator",       statement),
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
			"VisitNameListSeparator",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitUntil",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitFor",
			"VisitIntegerLiteral", "DepartIntegerLiteral",
			"VisitTerminator", "DepartWaitStatement",
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
			("VisitTerminator",        statement),
			("DepartNullStatement",    statement),
			("DepartProcessStatement", process),
		], recorder.Events)


class CompoundStatements(Testcase):
	def test_If(self) -> None:
		"""Each condition is followed by the ``then`` event, then the branch's statements."""
		condition1 =  SimpleObjectOrFunctionCallSymbol(SimpleName("a"))
		statement1 =  NullStatement()
		ifBranch =    IfBranch(condition1, [statement1])
		condition2 =  SimpleObjectOrFunctionCallSymbol(SimpleName("b"))
		elsifBranch = ElsifBranch(condition2)
		elseBranch =  ElseBranch()
		statement =   IfStatement(ifBranch, [elsifBranch], elseBranch)
		recorder =    FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			("VisitIfStatement",    statement),
			("VisitIfBranch",       ifBranch),
			("VisitSymbol",         condition1),
			("VisitSimpleName",     condition1.Name),
			("DepartSimpleName",    condition1.Name),
			("DepartSymbol",        condition1),
			("VisitThen",           ifBranch),
			("VisitNullStatement",  statement1),
			("VisitTerminator",     statement1),
			("DepartNullStatement", statement1),
			("DepartIfBranch",      ifBranch),
			("VisitElsifBranch",    elsifBranch),
			("VisitSymbol",         condition2),
			("VisitSimpleName",     condition2.Name),
			("DepartSimpleName",    condition2.Name),
			("DepartSymbol",        condition2),
			("VisitThen",           elsifBranch),
			("DepartElsifBranch",   elsifBranch),
			("VisitElseBranch",     elseBranch),
			("DepartElseBranch",    elseBranch),
			("DepartIfStatement",   statement),
		], recorder.Events)

	def test_Case(self) -> None:
		selector =  SimpleObjectOrFunctionCallSymbol(SimpleName("v"))
		first =     IndexedChoice(IntegerLiteral(0))
		second =    IndexedChoice(IntegerLiteral(1))
		case =      Case([first, second])
		others =    OthersCase()
		statement = CaseStatement(selector, [case, others])
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			"VisitCaseStatement",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitIs",
			"VisitCase",
			"VisitIndexedChoice", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartIndexedChoice",
			"VisitBar",
			"VisitIndexedChoice", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartIndexedChoice",
			"VisitArrow",
			"DepartCase",
			"VisitOthersCase",
			"VisitArrow",
			"DepartOthersCase",
			"DepartCaseStatement",
		], [event[0] for event in recorder.Events])

	def test_Loops(self) -> None:
		"""Each loop reports the ``loop`` event before its statements."""
		endless =   EndlessLoopStatement([ExitStatement()])
		forLoop =   ForLoopStatement("i", SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To))
		whileLoop = WhileLoopStatement(SimpleObjectOrFunctionCallSymbol(SimpleName("c")), [NextStatement()])
		recorder =  FullRecorder()

		endless.Visit(recorder)
		forLoop.Visit(recorder)
		whileLoop.Visit(recorder)

		self.assertEqual([
			"VisitEndlessLoopStatement", "VisitLoop", "VisitExitStatement", "VisitTerminator", "DepartExitStatement",
			"DepartEndlessLoopStatement",
			"VisitForLoopStatement", "VisitSimpleRange", "VisitIntegerLiteral", "DepartIntegerLiteral", "VisitDirection",
			"VisitIntegerLiteral", "DepartIntegerLiteral", "DepartSimpleRange", "VisitLoop", "DepartForLoopStatement",
			"VisitWhileLoopStatement", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "VisitLoop",
			"VisitNextStatement", "VisitTerminator", "DepartNextStatement", "DepartWhileLoopStatement",
		], [event[0] for event in recorder.Events])

	def test_Exit_Condition(self) -> None:
		condition = SimpleObjectOrFunctionCallSymbol(SimpleName("done"))
		statement = ExitStatement(condition)
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual(
			["VisitExitStatement", "VisitWhen", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			 "VisitTerminator", "DepartExitStatement"],
			[event[0] for event in recorder.Events]
		)
