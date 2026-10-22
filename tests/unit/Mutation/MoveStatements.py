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
Mutation tests: moving a concurrent or sequential statement to another position of its construct.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Concurrent import ComponentInstantiation, ConcurrentAssertStatement, ProcessStatement
from pyVHDLModel.DesignUnit import Architecture
from pyVHDLModel.Exception  import NotAChildError
from pyVHDLModel.Expression import EnumerationLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Sequential import NullStatement
from pyVHDLModel.Symbol     import ComponentInstantiationSymbol

from tests.unit             import _entitySymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _instance(label: str) -> ComponentInstantiation:
	return ComponentInstantiation(label, ComponentInstantiationSymbol(SimpleName("comp")))


class ConcurrentStatements(Testcase):
	def test_Move(self) -> None:
		process = ProcessStatement("p")
		instance = _instance("u")
		assertion = ConcurrentAssertStatement(EnumerationLiteral("true"))
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[process, instance, assertion])

		architecture.MoveStatement(process, -1)

		self.assertListEqual([instance, assertion, process], architecture.Statements)
		self.assertIs(architecture, process.Parent)
		self.assertIs(architecture._namespace, process._namespace.ParentNamespace)

	def test_Move_Indexed(self) -> None:
		instance1 = _instance("u1")
		instance2 = _instance("u2")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[instance1, instance2])
		architecture.IndexStatements()

		architecture.MoveStatement(instance2, 0)

		self.assertListEqual([instance2, instance1], architecture.Statements)
		self.assertDictEqual({"u1": instance1, "u2": instance2}, architecture._instantiations)

	def test_Before(self) -> None:
		instance1 = _instance("u1")
		instance2 = _instance("u2")
		instance3 = _instance("u3")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[instance1, instance2, instance3])

		architecture.MoveStatementBefore(instance1, instance3)

		self.assertListEqual([instance2, instance1, instance3], architecture.Statements)

	def test_After(self) -> None:
		instance1 = _instance("u1")
		instance2 = _instance("u2")
		instance3 = _instance("u3")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[instance1, instance2, instance3])

		architecture.MoveStatementAfter(instance3, instance1)

		self.assertListEqual([instance1, instance3, instance2], architecture.Statements)

	def test_After_Itself(self) -> None:
		instance1 = _instance("u1")
		instance2 = _instance("u2")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[instance1, instance2])

		architecture.MoveStatementAfter(instance1, instance1)

		self.assertListEqual([instance1, instance2], architecture.Statements)

	def test_Move_NotAChild(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[_instance("u1")])
		process = ProcessStatement("q")

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveStatement(process, 0)

		self.assertEqual("ProcessStatement 'q' is not a statement of this Architecture.", str(context.exception))
		self.assertIs(process, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)

	def test_Move_IndexOutOfRange(self) -> None:
		instance = _instance("u1")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[instance])

		with self.assertRaises(ValueError) as context:
			architecture.MoveStatement(instance, 1)

		self.assertEqual("Parameter 'index' is out of range -1..0.", str(context.exception))
		self.assertListEqual(["Got value '1'."], context.exception.__notes__)

	def test_Before_NotAChild(self) -> None:
		instance = _instance("u1")
		architecture = Architecture("rtl", _entitySymbol("e"), statements=[instance])
		assertion = ConcurrentAssertStatement(EnumerationLiteral("true"))

		with self.assertRaises(NotAChildError) as context:
			architecture.MoveStatementBefore(instance, assertion)

		self.assertEqual("ConcurrentAssertStatement is not a statement of this Architecture.", str(context.exception))
		self.assertIs(assertion, context.exception.Element)


class SequentialStatements(Testcase):
	def test_Move(self) -> None:
		null1 = NullStatement(label="l1")
		null2 = NullStatement()
		null3 = NullStatement(label="l3")
		process = ProcessStatement("p", statements=[null1, null2, null3])

		process.MoveStatement(null3, 1)

		self.assertListEqual([null1, null3, null2], process.Statements)
		self.assertIs(process, null3.Parent)

	def test_Before(self) -> None:
		null1 = NullStatement(label="l1")
		null2 = NullStatement(label="l2")
		process = ProcessStatement("p", statements=[null1, null2])

		process.MoveStatementBefore(null2, null1)

		self.assertListEqual([null2, null1], process.Statements)

	def test_Before_Itself(self) -> None:
		null1 = NullStatement(label="l1")
		null2 = NullStatement(label="l2")
		process = ProcessStatement("p", statements=[null1, null2])

		process.MoveStatementBefore(null1, null1)

		self.assertListEqual([null1, null2], process.Statements)

	def test_After(self) -> None:
		null1 = NullStatement(label="l1")
		null2 = NullStatement(label="l2")
		null3 = NullStatement(label="l3")
		process = ProcessStatement("p", statements=[null1, null2, null3])

		process.MoveStatementAfter(null1, null3)

		self.assertListEqual([null2, null3, null1], process.Statements)

	def test_Move_None(self) -> None:
		process = ProcessStatement("p", statements=[NullStatement()])

		with self.assertRaises(ValueError) as context:
			process.MoveStatement(None, 0)

		self.assertEqual("Parameter 'statement' is None.", str(context.exception))

	def test_Move_WrongType(self) -> None:
		process = ProcessStatement("p", statements=[NullStatement()])

		with self.assertRaises(TypeError) as context:
			process.MoveStatement("null", 0)

		self.assertEqual("Parameter 'statement' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Move_NotAChild(self) -> None:
		process = ProcessStatement("p", statements=[NullStatement()])
		null = NullStatement(label="l9")

		with self.assertRaises(NotAChildError) as context:
			process.MoveStatement(null, 0)

		self.assertEqual("NullStatement 'l9' is not a statement of this ProcessStatement.", str(context.exception))
		self.assertIs(null, context.exception.Element)
		self.assertIs(process, context.exception.Parent)

	def test_Move_IndexOutOfRange(self) -> None:
		null = NullStatement()
		process = ProcessStatement("p", statements=[null, NullStatement()])

		with self.assertRaises(ValueError) as context:
			process.MoveStatement(null, -3)

		self.assertEqual("Parameter 'index' is out of range -2..1.", str(context.exception))
		self.assertListEqual(["Got value '-3'."], context.exception.__notes__)

	def test_After_NotAChild(self) -> None:
		null = NullStatement()
		process = ProcessStatement("p", statements=[null])
		other = NullStatement()

		with self.assertRaises(NotAChildError) as context:
			process.MoveStatementAfter(null, other)

		self.assertEqual("NullStatement is not a statement of this ProcessStatement.", str(context.exception))
		self.assertIs(other, context.exception.Element)
