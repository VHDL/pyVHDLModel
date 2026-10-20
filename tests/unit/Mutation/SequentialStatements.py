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
Mutation tests for the statements of language constructs with sequential statements
(:class:`~pyVHDLModel.Sequential.SequentialStatementsMixin`).

Every label of a process or subprogram body is declared in the process' or subprogram's declarative region, also a
label nested in an if branch, a case alternative or a loop.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.Exception  import AlreadyInDesignError, DuplicateLabelError, NotAChildError
from pyVHDLModel.Expression import EnumerationLiteral
from pyVHDLModel.Sequential import Case, CaseStatement, EndlessLoopStatement, IfBranch, IfStatement, IndexedChoice
from pyVHDLModel.Sequential import NullStatement
from pyVHDLModel.Subprogram import Procedure

from tests.unit.Mutation    import _parameter, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _null(label: str = None) -> NullStatement:
	return NullStatement(label=label)


def _if(*statements) -> IfStatement:
	return IfStatement(IfBranch(EnumerationLiteral("true"), statements))


def _case(*statements) -> Case:
	return Case([IndexedChoice(EnumerationLiteral("a"))], statements)


class Add(Testcase):
	def test_Add(self) -> None:
		process = ProcessStatement("p")
		first = _null("l1")
		second = _null()

		process.AddStatement(first)
		process.AddStatement(second)

		self.assertListEqual([first, second], process.Statements)
		self.assertIs(process, first.Parent)
		self.assertIs(process, second.Parent)

	def test_Add_Unlabeled(self) -> None:
		"""Unlabeled statements declare nothing, so they never clash."""
		process = ProcessStatement("p", statements=[_null()])

		process.AddStatement(_null())

		self.assertEqual(2, len(process.Statements))

	def test_Add_Branch(self) -> None:
		ifStatement = _if()
		ProcessStatement("p", statements=[ifStatement])
		statement = _null("l1")

		ifStatement.IfBranch.AddStatement(statement)

		self.assertIs(ifStatement.IfBranch, statement.Parent)


class Insert(Testcase):
	def test_Insert(self) -> None:
		first = _null("l1")
		third = _null("l3")
		process = ProcessStatement("p", statements=[first, third])
		second = _null("l2")

		process.InsertStatement(1, second)

		self.assertListEqual([first, second, third], process.Statements)

	def test_Insert_Negative(self) -> None:
		first = _null("l1")
		last = _null("l3")
		process = ProcessStatement("p", statements=[first, last])
		statement = _null("l2")

		process.InsertStatement(-1, statement)

		self.assertListEqual([first, statement, last], process.Statements)

	def test_InsertBefore(self) -> None:
		first = _null("l1")
		last = _null("l3")
		process = ProcessStatement("p", statements=[first, last])
		statement = _null("l2")

		process.InsertStatementBefore(statement, last)

		self.assertListEqual([first, statement, last], process.Statements)

	def test_InsertAfter(self) -> None:
		first = _null("l1")
		last = _null("l3")
		process = ProcessStatement("p", statements=[first, last])
		statement = _null("l2")

		process.InsertStatementAfter(statement, first)

		self.assertListEqual([first, statement, last], process.Statements)

	def test_InsertBefore_NotAChild(self) -> None:
		with self.assertRaises(NotAChildError) as context:
			ProcessStatement("p").InsertStatementBefore(_null(), _null("l9"))

		self.assertEqual("NullStatement 'l9' is not a statement of this ProcessStatement.", str(context.exception))

	def test_InsertAfter_NotAChild(self) -> None:
		with self.assertRaises(NotAChildError) as context:
			ProcessStatement("p").InsertStatementAfter(_null(), _null())

		self.assertEqual("NullStatement is not a statement of this ProcessStatement.", str(context.exception))


class Checks(Testcase):
	def test_Index_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			ProcessStatement("p").InsertStatement(None, _null())

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Index_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			ProcessStatement("p").InsertStatement(1.0, _null())

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'float'."], context.exception.__notes__)

	def test_Index_Range(self) -> None:
		with self.assertRaises(ValueError) as context:
			ProcessStatement("p").InsertStatement(-1, _null())

		self.assertEqual("Parameter 'index' is out of range 0..0.", str(context.exception))

	def test_Statement_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			ProcessStatement("p").AddStatement(None)

		self.assertEqual("Parameter 'statement' is None.", str(context.exception))

	def test_Statement_Type(self) -> None:
		"""A concurrent statement isn't a sequential statement."""
		with self.assertRaises(TypeError) as context:
			ProcessStatement("p").AddStatement(ProcessStatement("q"))

		self.assertEqual("Parameter 'statement' is not of type 'SequentialStatement'.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Concurrent.ProcessStatement'."], context.exception.__notes__)

	def test_Statement_HasParent(self) -> None:
		statement = _null("l1")
		ProcessStatement("p", statements=[statement])

		with self.assertRaises(AlreadyInDesignError) as context:
			ProcessStatement("q").AddStatement(statement)

		self.assertEqual("NullStatement 'l1' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its ProcessStatement first."], context.exception.__notes__)


class Labels(Testcase):
	def test_DuplicateLabel(self) -> None:
		process = ProcessStatement("p", statements=[_null("l1")])
		statement = _null("L1")

		with self.assertRaises(DuplicateLabelError) as context:
			process.AddStatement(statement)

		self.assertEqual("ProcessStatement already declares 'L1'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Sequential.NullStatement'."],
			context.exception.__notes__
		)
		self.assertIsNone(statement.Parent)

	def test_LabelInBranchVsBody(self) -> None:
		"""A label in an if branch is declared in the process' region."""
		process = ProcessStatement("p", statements=[_if(_null("l1"))])

		with self.assertRaises(DuplicateLabelError) as context:
			process.AddStatement(_null("l1"))

		self.assertEqual("ProcessStatement already declares 'l1'.", str(context.exception))

	def test_BodyLabelVsNewBranchStatement(self) -> None:
		"""A statement added to a branch may not repeat a label of the process body."""
		ifStatement = _if()
		ProcessStatement("p", statements=[ifStatement, _null("l1")])

		with self.assertRaises(DuplicateLabelError) as context:
			ifStatement.IfBranch.AddStatement(_null("l1"))

		self.assertEqual("ProcessStatement already declares 'l1'.", str(context.exception))

	def test_CaseAlternatives(self) -> None:
		"""Two case alternatives may not use the same label."""
		first = _case(_null("l1"))
		second = _case()
		ProcessStatement("p", statements=[CaseStatement(EnumerationLiteral("a"), [first, second])])

		with self.assertRaises(DuplicateLabelError) as context:
			second.AddStatement(_null("l1"))

		self.assertEqual("ProcessStatement already declares 'l1'.", str(context.exception))

	def test_LoopBody(self) -> None:
		"""A label in a loop body is declared in the process' region."""
		loop = EndlessLoopStatement(label="lp")
		ProcessStatement("p", statements=[loop, _null("l1")])

		with self.assertRaises(DuplicateLabelError) as context:
			loop.AddStatement(_null("l1"))

		self.assertEqual("ProcessStatement already declares 'l1'.", str(context.exception))

	def test_NestedLabelOfCompoundStatement(self) -> None:
		"""An inserted if statement brings the labels of its branches into the process' region."""
		process = ProcessStatement("p", statements=[_null("l1")])

		with self.assertRaises(DuplicateLabelError) as context:
			process.AddStatement(_if(_null("l1")))

		self.assertEqual("ProcessStatement already declares 'l1'.", str(context.exception))

	def test_LabelVsVariable(self) -> None:
		process = ProcessStatement("p", declaredItems=[_variable("v")])

		with self.assertRaises(DuplicateLabelError) as context:
			process.AddStatement(_null("v"))

		self.assertEqual("ProcessStatement already declares 'v'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Object.Variable'."],
			context.exception.__notes__
		)

	def test_LabelVsParameter(self) -> None:
		"""A subprogram's parameters share its declarative region with the labels of its body."""
		procedure = Procedure("proc", parameterItems=[_parameter("x")])

		with self.assertRaises(DuplicateLabelError) as context:
			procedure.AddStatement(_null("x"))

		self.assertEqual("Procedure already declares 'x'.", str(context.exception))

	def test_DetachedBranch(self) -> None:
		"""A branch not in a process checks the labels of its own statements."""
		branch = IfBranch(EnumerationLiteral("true"), [_null("l1")])

		with self.assertRaises(DuplicateLabelError) as context:
			branch.AddStatement(_null("l1"))

		self.assertEqual("IfBranch already declares 'l1'.", str(context.exception))


class Remove(Testcase):
	def test_Remove(self) -> None:
		first = _null("l1")
		second = _null("l2")
		process = ProcessStatement("p", statements=[first, second])

		process.RemoveStatement(first)

		self.assertListEqual([second], process.Statements)
		self.assertIsNone(first._parent)

	def test_Remove_FreesLabel(self) -> None:
		statement = _null("l1")
		process = ProcessStatement("p", statements=[statement])

		process.RemoveStatement(statement)
		process.AddStatement(_null("l1"))

		self.assertEqual(1, len(process.Statements))

	def test_Remove_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			ProcessStatement("p").RemoveStatement(None)

		self.assertEqual("Parameter 'statement' is None.", str(context.exception))

	def test_Remove_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			ProcessStatement("p").RemoveStatement(42)

		self.assertEqual("Parameter 'statement' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Remove_NotAChild(self) -> None:
		with self.assertRaises(NotAChildError) as context:
			ProcessStatement("p").RemoveStatement(_null("l1"))

		self.assertEqual("NullStatement 'l1' is not a statement of this ProcessStatement.", str(context.exception))
