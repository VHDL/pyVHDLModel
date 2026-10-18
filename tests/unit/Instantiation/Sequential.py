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
"""
Tests for pyVHDLModel.Sequential - the sequential statement kinds not already covered by
tests/unit/Assignment.py (conditional/selected/force/release assignments) or
tests/unit/Base.py (branches, report/assert statements, choices).
"""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import ModelEntity, Direction, SimpleRange
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SignalSymbol, VariableSymbol, Symbol, PossibleReference
from pyVHDLModel.Expression  import IntegerLiteral, CharacterLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Association import ParameterAssociationItem
from pyVHDLModel.Sequential  import (
	SequentialProcedureCall, SequentialSignalAssignment, SequentialSimpleSignalAssignment,
	CompoundStatement, IfBranch, ElseBranch, IfStatement,
	IndexedChoice, RangedChoice, Case, OthersCase, CaseStatement,
	LoopStatement, EndlessLoopStatement, ForLoopStatement, WhileLoopStatement,
	NextStatement, ExitStatement, NullStatement, ReturnStatement, WaitStatement,
)
from pyVHDLModel.Base        import WaveformElement

from tests.unit              import _signalSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SequentialProcedureCalls(Testcase):
	"""``ProcedureCallMixin`` is shared with ``ConcurrentProcedureCall`` (tests/unit/Concurrent.py);
	tested once here since the mixin's own logic doesn't differ between the two."""

	def test_WithParameters(self) -> None:
		procedureName = Symbol(SimpleName("proc"), PossibleReference.Procedure)
		parameter = ParameterAssociationItem(None, IntegerLiteral(1))
		call = SequentialProcedureCall(procedureName, [parameter], label="lbl")

		self.assertIs(procedureName, call.Procedure)
		self.assertIs(call, procedureName.Parent)
		self.assertEqual(1, len(call.ParameterAssociationItems))
		self.assertIs(call, parameter.Parent)
		self.assertEqual("lbl", call.Label)

	def test_NoParameters(self) -> None:
		call = SequentialProcedureCall(Symbol(SimpleName("proc"), PossibleReference.Procedure))

		self.assertEqual(0, len(call.ParameterAssociationItems))
		self.assertIsNone(call.Label)


class SequentialSignalAssignments(Testcase):
	def test_Construction(self) -> None:
		target = _signalSymbol("s")
		assignment = SequentialSignalAssignment(target, label="lbl")

		self.assertIs(target, assignment.Target)
		self.assertIs(assignment, target.Parent)
		self.assertEqual("lbl", assignment.Label)


class SequentialSimpleSignalAssignments(Testcase):
	def test_Construction(self) -> None:
		"""``s <= '1';``"""
		target = _signalSymbol("s")
		waveformElement = WaveformElement(CharacterLiteral("'1'"))
		assignment = SequentialSimpleSignalAssignment(target, [waveformElement])

		self.assertIs(target, assignment.Target)
		self.assertEqual(1, len(assignment.Waveform))
		self.assertIs(waveformElement, assignment.Waveform[0])
		self.assertIs(assignment, waveformElement.Parent)


class IfStatements(Testcase):
	def test_IfOnly(self) -> None:
		ifBranch = IfBranch(IntegerLiteral(1))
		statement = IfStatement(ifBranch)

		self.assertIs(ifBranch, statement.IfBranch)
		self.assertIs(statement, ifBranch.Parent)
		self.assertEqual(0, len(statement.ElsIfBranches))
		self.assertIsNone(statement.ElseBranch)

	def test_IfElsifElse(self) -> None:
		from pyVHDLModel.Sequential import ElsifBranch

		ifBranch = IfBranch(IntegerLiteral(1))
		elsifBranch = ElsifBranch(IntegerLiteral(2))
		elseBranch = ElseBranch()
		statement = IfStatement(ifBranch, [elsifBranch], elseBranch)

		self.assertEqual(1, len(statement.ElsIfBranches))
		self.assertIs(elsifBranch, statement.ElsIfBranches[0])
		self.assertIs(statement, elsifBranch.Parent)
		self.assertIs(elseBranch, statement.ElseBranch)
		self.assertIs(statement, elseBranch.Parent)


class Choices(Testcase):
	"""Regression test: ``IndexedChoice``'s ``expression.Parent = self`` was previously commented out
	(``# FIXME: received None``) - confirmed stale in the gap analysis (every real construction site
	always provides a real expression) and now re-enabled."""

	def test_IndexedChoice(self) -> None:
		expression = IntegerLiteral(0)
		choice = IndexedChoice(expression)

		self.assertIs(expression, choice.Expression)
		self.assertIs(choice, expression.Parent)
		self.assertEqual("0", str(choice))

	def test_RangedChoice(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		choice = RangedChoice(rng)

		self.assertIs(rng, choice.Range)
		self.assertIs(choice, rng.Parent)
		self.assertEqual("0 to 3", str(choice))


class Cases(Testcase):
	def test_Case(self) -> None:
		choice = IndexedChoice(IntegerLiteral(0))
		case = Case([choice])

		self.assertEqual(1, len(case.Choices))
		self.assertEqual("when 0 =>", str(case))

	def test_Case_MultipleChoices(self) -> None:
		"""``when 0 | 1 =>``"""
		case = Case([IndexedChoice(IntegerLiteral(0)), IndexedChoice(IntegerLiteral(1))])

		self.assertEqual("when 0 | 1 =>", str(case))

	def test_OthersCase(self) -> None:
		case = OthersCase()

		self.assertEqual(0, len(case.Choices))
		self.assertEqual("when others =>", str(case))


class CaseStatements(Testcase):
	def test_Construction(self) -> None:
		expression = IntegerLiteral(0)
		case = Case([IndexedChoice(IntegerLiteral(0))])
		statement = CaseStatement(expression, [case])

		self.assertIs(expression, statement.SelectExpression)
		self.assertIs(statement, expression.Parent)
		self.assertEqual(1, len(statement.Cases))
		self.assertIs(case, statement.Cases[0])
		self.assertIs(statement, case.Parent)


class LoopStatements(Testcase):
	def test_EndlessLoopStatement(self) -> None:
		statement = EndlessLoopStatement(label="lbl")

		self.assertEqual("lbl", statement.Label)
		self.assertEqual(0, len(statement.Statements))

	def test_ForLoopStatement(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		statement = ForLoopStatement("i", rng)

		self.assertEqual("i", statement.LoopIndex)
		self.assertIs(rng, statement.Range)
		self.assertIs(statement, rng.Parent)

	def test_WhileLoopStatement(self) -> None:
		condition = IntegerLiteral(1)
		statement = WhileLoopStatement(condition)

		self.assertIs(condition, statement.Condition)


class LoopControlStatements(Testcase):
	"""Regression test: ``_loopReference`` was declared but never initialized in
	``LoopControlStatement.__init__`` - the same crash-on-first-property-access shape as the fixed
	``DeferredConstant`` bug. ``NextStatement``/``ExitStatement`` add no state of their own, so the
	fix is tested via both, once each."""

	def test_NextStatement(self) -> None:
		condition = IntegerLiteral(1)
		statement = NextStatement(condition)

		self.assertIs(condition, statement.Condition)
		self.assertIsNone(statement.LoopReference)

	def test_ExitStatement(self) -> None:
		statement = ExitStatement()

		self.assertIsNone(statement.Condition)
		self.assertIsNone(statement.LoopReference)


class NullStatements(Testcase):
	def test_Construction(self) -> None:
		statement = NullStatement(label="lbl")

		self.assertEqual("lbl", statement.Label)


class ReturnStatements(Testcase):
	def test_WithValue(self) -> None:
		value = IntegerLiteral(1)
		statement = ReturnStatement(value)

		self.assertIs(value, statement.ReturnValue)
		self.assertIs(statement, value.Parent)

	def test_WithoutValue(self) -> None:
		"""``return;`` (procedures) vs. ``return expr;`` (functions)."""
		statement = ReturnStatement()

		self.assertIsNone(statement.ReturnValue)


class WaitStatements(Testcase):
	def test_Empty(self) -> None:
		"""``wait;``"""
		statement = WaitStatement()

		self.assertIsNone(statement.SensitivityList)
		self.assertIsNone(statement.Condition)
		self.assertIsNone(statement.Timeout)

	def test_Full(self) -> None:
		"""``wait on clock until condition for 10 ns;``"""
		sensitivitySignal = _signalSymbol("clock")
		condition = IntegerLiteral(1)
		timeout = PhysicalIntegerLiteral(10, "ns")
		statement = WaitStatement([sensitivitySignal], condition, timeout)

		self.assertEqual(1, len(statement.SensitivityList))
		self.assertIs(sensitivitySignal, statement.SensitivityList[0])
		self.assertIs(statement, sensitivitySignal.Parent)
		self.assertIs(condition, statement.Condition)
		self.assertIs(statement, condition.Parent)
		self.assertIs(timeout, statement.Timeout)
		self.assertIs(statement, timeout.Parent)
