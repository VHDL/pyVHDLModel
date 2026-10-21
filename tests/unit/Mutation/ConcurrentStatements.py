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
Mutation tests for the statements of language constructs with concurrent statements
(:class:`~pyVHDLModel.Concurrent.ConcurrentStatementsMixin`).

A statement label is declared in the enclosing declarative region, so the label checks cover other labels, declared
items, and the region an entity shares with its architecture.
"""
from pathlib                import Path

from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document, Library
from pyVHDLModel.Concurrent import ComponentInstantiation, ConcurrentAssertStatement, ConcurrentBlockStatement
from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.DesignUnit import Architecture, Entity
from pyVHDLModel.Exception  import AlreadyInDesignError, DuplicateLabelError, DuplicateSignalError
from pyVHDLModel.Exception  import DuplicateVariableError, NotAChildError
from pyVHDLModel.Expression import EnumerationLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Sequential import IfBranch, IfStatement, NullStatement
from pyVHDLModel.Symbol     import ComponentInstantiationSymbol

from tests.unit             import _entitySymbol
from tests.unit.Mutation    import _port, _signal, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _architecture(*statements) -> Architecture:
	return Architecture("rtl", _entitySymbol("ent"), statements=statements)


def _instance(label: str) -> ComponentInstantiation:
	return ComponentInstantiation(label, ComponentInstantiationSymbol(SimpleName("comp")))


def _assert() -> ConcurrentAssertStatement:
	return ConcurrentAssertStatement(EnumerationLiteral("true"))


def _link(entity: Entity, architecture: Architecture) -> None:
	"""Link an architecture to its entity, so both share one declarative region."""
	design = Design()
	library = Library("work")
	design.AddLibrary(library)
	document = Document(Path("virtual.vhdl"))
	document._AddDesignUnit(entity)
	document._AddDesignUnit(architecture)
	design.AddDocument(document, library)
	design.CreateDependencyGraph()
	design.LinkArchitectures()


class Add(Testcase):
	def test_Add(self) -> None:
		architecture = _architecture()
		process = ProcessStatement("p")
		instance = _instance("u")

		architecture.AddStatement(process)
		architecture.AddStatement(instance)

		self.assertListEqual([process, instance], architecture.Statements)
		self.assertIs(architecture, process.Parent)
		self.assertIs(architecture, instance.Parent)

	def test_Add_ConnectsNamespace(self) -> None:
		"""A process' namespace is connected to the namespace of the construct it's added to."""
		architecture = _architecture()
		process = ProcessStatement("p")

		architecture.AddStatement(process)

		self.assertIs(architecture._namespace, process._namespace.ParentNamespace)

	def test_Add_Unlabeled(self) -> None:
		"""Unlabeled statements declare nothing, so they never clash."""
		architecture = _architecture()
		first = _assert()
		second = _assert()

		architecture.AddStatement(first)
		architecture.AddStatement(second)

		self.assertListEqual([first, second], architecture.Statements)

	def test_Add_NestedLabel(self) -> None:
		"""A label inside a block is declared in the block's region, so the architecture may repeat it."""
		inner = ProcessStatement("p")
		architecture = _architecture(ConcurrentBlockStatement("b", statements=[inner]))
		outer = ProcessStatement("p")

		architecture.AddStatement(outer)

		self.assertIs(architecture, outer.Parent)
		self.assertIs(architecture.Statements[0], inner.Parent)


class Insert(Testcase):
	def test_Insert(self) -> None:
		first = ProcessStatement("p1")
		third = ProcessStatement("p3")
		architecture = _architecture(first, third)
		second = ProcessStatement("p2")

		architecture.InsertStatement(1, second)

		self.assertListEqual([first, second, third], architecture.Statements)

	def test_Insert_Negative(self) -> None:
		first = ProcessStatement("p1")
		last = ProcessStatement("p3")
		architecture = _architecture(first, last)
		statement = ProcessStatement("p2")

		architecture.InsertStatement(-1, statement)

		self.assertListEqual([first, statement, last], architecture.Statements)

	def test_InsertBefore(self) -> None:
		first = ProcessStatement("p1")
		last = ProcessStatement("p3")
		architecture = _architecture(first, last)
		statement = ProcessStatement("p2")

		architecture.InsertStatementBefore(statement, last)

		self.assertListEqual([first, statement, last], architecture.Statements)

	def test_InsertAfter(self) -> None:
		first = ProcessStatement("p1")
		last = ProcessStatement("p3")
		architecture = _architecture(first, last)
		statement = ProcessStatement("p2")

		architecture.InsertStatementAfter(statement, first)

		self.assertListEqual([first, statement, last], architecture.Statements)

	def test_InsertBefore_NotAChild(self) -> None:
		architecture = _architecture()
		before = ProcessStatement("q")

		with self.assertRaises(NotAChildError) as context:
			architecture.InsertStatementBefore(ProcessStatement("p"), before)

		self.assertEqual("ProcessStatement 'q' is not a statement of this Architecture.", str(context.exception))
		self.assertIs(before, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)

	def test_InsertAfter_NotAChild(self) -> None:
		architecture = _architecture()
		after = _assert()

		with self.assertRaises(NotAChildError) as context:
			architecture.InsertStatementAfter(ProcessStatement("p"), after)

		self.assertEqual("ConcurrentAssertStatement is not a statement of this Architecture.", str(context.exception))
		self.assertIs(after, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)


class Checks(Testcase):
	def test_Index_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_architecture().InsertStatement(None, ProcessStatement("p"))

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Index_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_architecture().InsertStatement("0", ProcessStatement("p"))

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Index_Range(self) -> None:
		with self.assertRaises(ValueError) as context:
			_architecture(ProcessStatement("p")).InsertStatement(2, ProcessStatement("q"))

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))

	def test_Statement_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_architecture().AddStatement(None)

		self.assertEqual("Parameter 'statement' is None.", str(context.exception))

	def test_Statement_Type(self) -> None:
		"""A sequential statement isn't a concurrent statement."""
		with self.assertRaises(TypeError) as context:
			_architecture().AddStatement(NullStatement())

		self.assertEqual("Parameter 'statement' is not of type 'ConcurrentStatement'.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Sequential.NullStatement'."], context.exception.__notes__)

	def test_Statement_HasParent(self) -> None:
		process = ProcessStatement("p")
		first = _architecture(process)

		with self.assertRaises(AlreadyInDesignError) as context:
			_architecture().AddStatement(process)

		self.assertEqual("ProcessStatement 'p' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Architecture first."], context.exception.__notes__)
		self.assertIs(process, context.exception.Element)
		self.assertIs(first, context.exception.Parent)


class Labels(Testcase):
	def test_DuplicateLabel(self) -> None:
		process = ProcessStatement("p")
		architecture = _architecture(process)
		statement = _instance("P")

		with self.assertRaises(DuplicateLabelError) as context:
			architecture.AddStatement(statement)

		self.assertEqual("Architecture already declares 'P'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Concurrent.ProcessStatement'."],
			context.exception.__notes__
		)
		self.assertEqual("P", context.exception.Identifier)
		self.assertEqual("p", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertIs(statement, context.exception.Element)
		self.assertIs(process, context.exception.Existing)
		self.assertEqual(1, len(architecture.Statements))
		self.assertIsNone(statement.Parent)

	def test_LabelVsDeclaredItem(self) -> None:
		"""A label may not repeat a signal's identifier."""
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[_signal("s")])

		with self.assertRaises(DuplicateLabelError) as context:
			architecture.AddStatement(ProcessStatement("s"))

		self.assertEqual("Architecture already declares 's'.", str(context.exception))
		self.assertListEqual(["Existing declaration is of type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)

	def test_LabelVsEntityPort(self) -> None:
		"""An entity and its architecture share the declarative region: a label may not repeat a port."""
		entity = Entity("ent", portItems=[_port("x")])
		architecture = _architecture()
		_link(entity, architecture)

		with self.assertRaises(DuplicateLabelError) as context:
			architecture.AddStatement(ProcessStatement("x"))

		self.assertEqual("Entity already declares 'x'.", str(context.exception))

	def test_DeclaredItemVsLabel(self) -> None:
		"""A signal may not repeat a statement's label."""
		architecture = _architecture(ProcessStatement("p"))
		signal = _signal("p")

		with self.assertRaises(DuplicateSignalError) as context:
			architecture.AddDeclaredItem(signal)

		self.assertEqual("Architecture already declares 'p'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Concurrent.ProcessStatement'."],
			context.exception.__notes__
		)
		self.assertIsNone(signal.Parent)

	def test_VariableVsNestedSequentialLabel(self) -> None:
		"""A label inside an if branch of a process is declared in the process' region."""
		statement = NullStatement(label="l1")
		process = ProcessStatement("p", statements=[IfStatement(IfBranch(EnumerationLiteral("true"), [statement]))])

		with self.assertRaises(DuplicateVariableError) as context:
			process.AddDeclaredItem(_variable("l1"))

		self.assertEqual("ProcessStatement already declares 'l1'.", str(context.exception))


class Remove(Testcase):
	def test_Remove(self) -> None:
		first = ProcessStatement("p1")
		second = ProcessStatement("p2")
		architecture = _architecture(first, second)

		architecture.RemoveStatement(first)

		self.assertListEqual([second], architecture.Statements)
		self.assertIsNone(first._parent)

	def test_Remove_Readd(self) -> None:
		"""A removed statement can be added to another construct, and its label is free again."""
		process = ProcessStatement("p")
		source = _architecture(process)
		target = _architecture()

		source.RemoveStatement(process)
		target.AddStatement(process)
		source.AddStatement(ProcessStatement("p"))

		self.assertIs(target, process.Parent)

	def test_Remove_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_architecture().RemoveStatement(None)

		self.assertEqual("Parameter 'statement' is None.", str(context.exception))

	def test_Remove_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_architecture().RemoveStatement("p")

		self.assertEqual("Parameter 'statement' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Remove_NotAChild(self) -> None:
		architecture = _architecture()
		process = ProcessStatement("p")

		with self.assertRaises(NotAChildError) as context:
			architecture.RemoveStatement(process)

		self.assertEqual("ProcessStatement 'p' is not a statement of this Architecture.", str(context.exception))
		self.assertIs(process, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)


class Index(Testcase):
	def test_IndexStatements_Again(self) -> None:
		"""Indexing again yields the same lookup tables."""
		instance = _instance("u")
		block = ConcurrentBlockStatement("b")
		architecture = _architecture(instance, block)

		architecture.IndexStatements()
		architecture.IndexStatements()

		self.assertDictEqual({"u": instance}, architecture._instantiations)
		self.assertDictEqual({"b": block}, architecture._hierarchy)

	def test_Insert_Indexed(self) -> None:
		architecture = _architecture()
		architecture.IndexStatements()
		instance = _instance("u")
		nested = _instance("v")
		block = ConcurrentBlockStatement("b", statements=[nested])

		architecture.AddStatement(instance)
		architecture.AddStatement(block)

		self.assertDictEqual({"u": instance}, architecture._instantiations)
		self.assertDictEqual({"b": block}, architecture._hierarchy)
		self.assertDictEqual({"v": nested}, block._instantiations)
		self.assertListEqual([instance, nested], list(architecture.IterateInstantiations()))

	def test_Insert_NotIndexed(self) -> None:
		"""Not indexed yet, the lookup tables stay empty until :meth:`IndexStatements`."""
		architecture = _architecture()

		architecture.AddStatement(_instance("u"))

		self.assertDictEqual({}, architecture._instantiations)

	def test_Remove_Indexed(self) -> None:
		instance = _instance("u")
		block = ConcurrentBlockStatement("b")
		architecture = _architecture(instance, block)
		architecture.IndexStatements()

		architecture.RemoveStatement(instance)
		architecture.RemoveStatement(block)

		self.assertDictEqual({}, architecture._instantiations)
		self.assertDictEqual({}, architecture._hierarchy)
