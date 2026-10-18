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
Tests for pyVHDLModel.Concurrent - the concurrent statement kinds not already covered by
tests/unit/Assignment.py (conditional/selected signal assignments) or tests/unit/Base.py
(ConcurrentBlockStatement's BlockStatementMixin/LabeledEntityMixin wiring).
"""
from pyTooling.Testing       import Testcase

from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import Direction, Mode, SimpleRange
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import (
	ComponentInstantiationSymbol, EntityInstantiationSymbol, ArchitectureSymbol,
	ConfigurationInstantiationSymbol, SignalSymbol, Symbol, PossibleReference, EntitySymbol,
)
from pyVHDLModel.Expression  import IntegerLiteral, CharacterLiteral
from pyVHDLModel.Association import GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Base        import WaveformElement
from pyVHDLModel.DesignUnit  import Architecture
from pyVHDLModel.Interface   import GenericConstantInterfaceItem, PortSimpleSignalInterfaceItem
from pyVHDLModel.Concurrent  import (
	ComponentInstantiation, EntityInstantiation, ConfigurationInstantiation,
	ProcessStatement, ConcurrentProcedureCall, ConcurrentBlockStatement,
	IfGenerateBranch, ElsifGenerateBranch, ElseGenerateBranch,
	GenerateStatement, IfGenerateStatement,
	IndexedGenerateChoice, RangedGenerateChoice, GenerateCase, OthersGenerateCase, CaseGenerateStatement,
	ForGenerateStatement, ConcurrentSimpleSignalAssignment, ConcurrentAssertStatement,
)

from tests.unit              import _entitySymbol, _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Instantiations(Testcase):
	def test_ComponentInstantiation(self) -> None:
		componentSymbol = ComponentInstantiationSymbol(SimpleName("comp"))
		generic = GenericAssociationItem(SimpleName("G"), IntegerLiteral(1))
		port = PortAssociationItem(SimpleName("p"), SimpleName("s"))
		instance = ComponentInstantiation("inst", componentSymbol, [generic], [port])

		self.assertIs(componentSymbol, instance.Component)
		self.assertIs(instance, componentSymbol.Parent)
		self.assertEqual(1, len(instance.GenericAssociationItems))
		self.assertIs(instance, generic.Parent)
		self.assertEqual(1, len(instance.PortAssociationItems))
		self.assertIs(instance, port.Parent)

	def test_EntityInstantiation_WithArchitecture(self) -> None:
		entitySymbol = EntityInstantiationSymbol(SimpleName("ent"))
		architectureSymbol = ArchitectureSymbol(SimpleName("rtl"))
		instance = EntityInstantiation("inst", entitySymbol, architectureSymbol)

		self.assertIs(entitySymbol, instance.Entity)
		self.assertIs(architectureSymbol, instance.Architecture)
		self.assertIs(instance, architectureSymbol.Parent)

	def test_EntityInstantiation_WithoutArchitecture(self) -> None:
		instance = EntityInstantiation("inst", EntityInstantiationSymbol(SimpleName("ent")))

		self.assertIsNone(instance.Architecture)

	def test_ConfigurationInstantiation(self) -> None:
		configurationSymbol = ConfigurationInstantiationSymbol(SimpleName("cfg"))
		instance = ConfigurationInstantiation("inst", configurationSymbol)

		self.assertIs(configurationSymbol, instance.Configuration)
		self.assertIs(instance, configurationSymbol.Parent)


class ProcessStatements(Testcase):
	def test_Empty(self) -> None:
		"""``proc: process begin end process;``"""
		process = ProcessStatement("proc")

		self.assertEqual("proc", process.Label)
		self.assertIsNone(process.SensitivityList)
		self.assertEqual(0, len(process.DeclaredItems))
		self.assertEqual(0, len(process.Statements))

	def test_WithSensitivityList(self) -> None:
		"""``proc: process(clk) begin end process;``"""
		clk = SimpleName("clk")
		process = ProcessStatement("proc", sensitivityList=[clk])

		self.assertEqual(1, len(process.SensitivityList))
		self.assertIs(clk, process.SensitivityList[0])


class ConcurrentProcedureCalls(Testcase):
	def test_Construction(self) -> None:
		procedureName = Symbol(SimpleName("proc"), PossibleReference.Procedure)
		call = ConcurrentProcedureCall("lbl", procedureName)

		self.assertIs(procedureName, call.Procedure)
		self.assertEqual("lbl", call.Label)

	def test_Construction_WithoutLabel(self) -> None:
		"""``proc(clock, open);``"""
		procedureName = Symbol(SimpleName("proc"), PossibleReference.Procedure)
		call = ConcurrentProcedureCall(None, procedureName)

		self.assertIs(procedureName, call.Procedure)
		self.assertIsNone(call.Label)


class ConcurrentBlockStatements(Testcase):
	"""``BlockStatementMixin``/``LabeledEntityMixin`` wiring is already covered in tests/unit/Base.py;
	this covers the block-specific state: the block header (generic and port clauses with their map
	aspects) and the declared items/statements via
	``ConcurrentDeclarationRegionMixin``/``ConcurrentStatementsMixin``."""

	def test_WithPortItems(self) -> None:
		portItem = PortSimpleSignalInterfaceItem(["p"], Mode.In, _subtypeSymbol("bit"))
		block = ConcurrentBlockStatement("blk", portItems=[portItem])

		self.assertEqual(1, len(block.PortItems))
		self.assertIs(portItem, block.PortItems[0])
		self.assertIs(block, portItem.Parent)

	def test_WithGenericItems(self) -> None:
		genericItem = GenericConstantInterfaceItem(["G"], Mode.In, _subtypeSymbol("positive"))
		block = ConcurrentBlockStatement("blk", genericItems=[genericItem])

		self.assertEqual(1, len(block.GenericItems))
		self.assertIs(genericItem, block.GenericItems[0])
		self.assertIs(block, genericItem.Parent)

	def test_WithGenericMapAspect(self) -> None:
		association = GenericAssociationItem(SimpleName("G"), IntegerLiteral(2))
		block = ConcurrentBlockStatement("blk", genericAssociationItems=[association])

		self.assertEqual(1, len(block.GenericAssociationItems))
		self.assertIs(association, block.GenericAssociationItems[0])
		self.assertIs(block, association.Parent)

	def test_WithPortMapAspect(self) -> None:
		association = PortAssociationItem(SimpleName("p"), SimpleName("s"))
		block = ConcurrentBlockStatement("blk", portAssociationItems=[association])

		self.assertEqual(1, len(block.PortAssociationItems))
		self.assertIs(association, block.PortAssociationItems[0])
		self.assertIs(block, association.Parent)

	def test_WithoutBlockHeader(self) -> None:
		"""A block header is optional; all four lists stay empty."""
		block = ConcurrentBlockStatement("blk")

		self.assertEqual(0, len(block.GenericItems))
		self.assertEqual(0, len(block.GenericAssociationItems))
		self.assertEqual(0, len(block.PortItems))
		self.assertEqual(0, len(block.PortAssociationItems))


class GenerateBranches(Testcase):
	def test_IfGenerateBranch(self) -> None:
		condition = IntegerLiteral(1)
		branch = IfGenerateBranch(condition, alternativeLabel="LBL")

		self.assertIs(condition, branch.Condition)
		self.assertEqual("LBL", branch.AlternativeLabel)
		self.assertEqual("lbl", branch.NormalizedAlternativeLabel)

	def test_IfGenerateBranch_NoLabel(self) -> None:
		branch = IfGenerateBranch(IntegerLiteral(1))

		self.assertIsNone(branch.AlternativeLabel)
		self.assertIsNone(branch.NormalizedAlternativeLabel)

	def test_ElsifGenerateBranch(self) -> None:
		condition = IntegerLiteral(1)
		branch = ElsifGenerateBranch(condition)

		self.assertIs(condition, branch.Condition)

	def test_ElseGenerateBranch(self) -> None:
		branch = ElseGenerateBranch()

		self.assertEqual(0, len(branch.Statements))


class GenerateStatements(Testcase):
	def test_AbstractMethodsRaise(self) -> None:
		"""``GenerateStatement`` itself is meant to always be used through a concrete subclass -
		``IterateInstantiations``/``IndexStatement`` are placeholders raising ``NotImplementedError``
		if a subclass doesn't override them (none of the three real subclasses omit them, so this only
		matters if constructed directly, as done here)."""
		statement = GenerateStatement("gen")

		with self.assertRaises(NotImplementedError):
			next(statement.IterateInstantiations())

		with self.assertRaises(NotImplementedError):
			statement.IndexStatement()


class IfGenerateStatements(Testcase):
	def test_IfOnly(self) -> None:
		ifBranch = IfGenerateBranch(IntegerLiteral(1))
		statement = IfGenerateStatement("gen", ifBranch)

		self.assertIs(ifBranch, statement.IfBranch)
		self.assertIs(statement, ifBranch.Parent)
		self.assertEqual(0, len(statement.ElsifBranches))
		self.assertIsNone(statement.ElseBranch)

	def test_IterateInstantiations_And_IndexStatement(self) -> None:
		componentSymbol = ComponentInstantiationSymbol(SimpleName("comp"))
		instance = ComponentInstantiation("inst", componentSymbol)
		ifBranch = IfGenerateBranch(IntegerLiteral(1), statements=[instance])
		statement = IfGenerateStatement("gen", ifBranch)

		statement.IndexStatement()
		instantiations = list(statement.IterateInstantiations())

		self.assertEqual(1, len(instantiations))
		self.assertIs(instance, instantiations[0])


class IfGenerateStatementInstantiations(Testcase):
	def test_IterateInstantiations_AllBranches(self) -> None:
		"""Each branch yields its own instantiations, in branch order."""
		ifInstance =    ComponentInstantiation("ifInst", ComponentInstantiationSymbol(SimpleName("comp")))
		elsifInstance = ComponentInstantiation("elsifInst", ComponentInstantiationSymbol(SimpleName("comp")))
		elseInstance =  ComponentInstantiation("elseInst", ComponentInstantiationSymbol(SimpleName("comp")))
		ifBranch =      IfGenerateBranch(IntegerLiteral(1), statements=[ifInstance])
		elsifBranch =   ElsifGenerateBranch(IntegerLiteral(2), statements=[elsifInstance])
		elseBranch =    ElseGenerateBranch(statements=[elseInstance])
		statement =     IfGenerateStatement("gen", ifBranch, [elsifBranch], elseBranch)

		statement.IndexStatement()
		instantiations = list(statement.IterateInstantiations())

		self.assertEqual(3, len(instantiations))
		self.assertIs(ifInstance, instantiations[0])
		self.assertIs(elsifInstance, instantiations[1])
		self.assertIs(elseInstance, instantiations[2])


class GenerateChoices(Testcase):
	def test_IndexedGenerateChoice(self) -> None:
		expression = IntegerLiteral(0)
		choice = IndexedGenerateChoice(expression)

		self.assertIs(expression, choice.Expression)
		self.assertIs(choice, expression.Parent)
		self.assertEqual("0", str(choice))

	def test_RangedGenerateChoice(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		choice = RangedGenerateChoice(rng)

		self.assertIs(rng, choice.Range)
		self.assertEqual("0 to 3", str(choice))


class GenerateCases(Testcase):
	def test_GenerateCase(self) -> None:
		choice = IndexedGenerateChoice(IntegerLiteral(0))
		case = GenerateCase([choice])

		self.assertEqual(1, len(case.Choices))
		self.assertEqual("when 0 =>", str(case))

	def test_OthersGenerateCase(self) -> None:
		case = OthersGenerateCase()

		self.assertEqual("when others =>", str(case))


class CaseGenerateStatements(Testcase):
	def test_Construction(self) -> None:
		expression = IntegerLiteral(0)
		case = GenerateCase([IndexedGenerateChoice(IntegerLiteral(0))])
		statement = CaseGenerateStatement("gen", expression, [case])

		self.assertIs(expression, statement.SelectExpression)
		self.assertIs(statement, expression.Parent)
		self.assertEqual(1, len(statement.Cases))
		self.assertIs(case, statement.Cases[0])
		self.assertIs(statement, case.Parent)

	def test_IterateInstantiations_And_IndexStatement(self) -> None:
		componentSymbol = ComponentInstantiationSymbol(SimpleName("comp"))
		instance = ComponentInstantiation("inst", componentSymbol)
		case = GenerateCase([IndexedGenerateChoice(IntegerLiteral(0))], statements=[instance])
		statement = CaseGenerateStatement("gen", IntegerLiteral(0), [case])

		statement.IndexStatement()
		instantiations = list(statement.IterateInstantiations())

		self.assertEqual(1, len(instantiations))
		self.assertIs(instance, instantiations[0])


class ForGenerateStatements(Testcase):
	def test_Construction(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		statement = ForGenerateStatement("gen", "i", rng)

		self.assertEqual("i", statement.LoopIndex)
		self.assertIs(rng, statement.Range)
		self.assertIs(statement, rng.Parent)

	def test_IterateInstantiations_And_IndexStatement(self) -> None:
		componentSymbol = ComponentInstantiationSymbol(SimpleName("comp"))
		instance = ComponentInstantiation("inst", componentSymbol)
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		statement = ForGenerateStatement("gen", "i", rng, statements=[instance])

		statement.IndexStatement()
		instantiations = list(statement.IterateInstantiations())

		self.assertEqual(1, len(instantiations))
		self.assertIs(instance, instantiations[0])


class ConcurrentSimpleSignalAssignments(Testcase):
	def test_Construction(self) -> None:
		"""``s <= '1';``"""
		target = SignalSymbol(SimpleName("s"))
		waveformElement = WaveformElement(CharacterLiteral("1"))
		assignment = ConcurrentSimpleSignalAssignment("lbl", target, [waveformElement])

		self.assertIs(target, assignment.Target)
		self.assertEqual(1, len(assignment.Waveform))
		self.assertIs(waveformElement, assignment.Waveform[0])

	def test_Construction_WithoutLabel(self) -> None:
		target = SignalSymbol(SimpleName("s"))
		assignment = ConcurrentSimpleSignalAssignment(None, target, [WaveformElement(CharacterLiteral("1"))])

		self.assertIs(target, assignment.Target)
		self.assertIsNone(assignment.Label)


class ConcurrentAssertStatements(Testcase):
	def test_Full(self) -> None:
		condition = IntegerLiteral(1)
		message = CharacterLiteral("a")
		severity = IntegerLiteral(2)
		statement = ConcurrentAssertStatement(condition, message, severity, label="lbl")

		self.assertIs(condition, statement.Condition)
		self.assertIs(message, statement.Message)
		self.assertIs(severity, statement.Severity)
		self.assertEqual("lbl", statement.Label)

	def test_NoSeverityNoLabel(self) -> None:
		statement = ConcurrentAssertStatement(IntegerLiteral(1), CharacterLiteral("a"))

		self.assertIsNone(statement.Severity)
		self.assertIsNone(statement.Label)

	def test_ConditionOnly(self) -> None:
		"""``assert sel = '0';``"""
		condition = IntegerLiteral(1)
		statement = ConcurrentAssertStatement(condition)

		self.assertIs(condition, statement.Condition)
		self.assertIsNone(statement.Message)
		self.assertIsNone(statement.Severity)
		self.assertIsNone(statement.Label)


class ConcurrentStatementsMixinIndexing(Testcase):
	"""Tested via ``Architecture`` (the canonical ``ConcurrentDeclarationRegionMixin``/
	``ConcurrentStatementsMixin`` host - see tests/unit/DesignUnit.py)."""

	def test_IndexStatements_BucketsByKind(self) -> None:
		"""Blocks and generates both land in the single, unified ``_hierarchy`` dict (in source/
		declaration order), not separate per-kind dicts."""
		entitySymbol = _entitySymbol("e")
		instance = ComponentInstantiation("inst", ComponentInstantiationSymbol(SimpleName("comp")))
		block = ConcurrentBlockStatement("blk")
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		generate = ForGenerateStatement("gen", "i", rng)

		architecture = Architecture("rtl", entitySymbol, statements=[instance, block, generate])
		architecture.IndexStatements()

		self.assertIs(instance, architecture._instantiations["inst"])
		self.assertIs(block, architecture._hierarchy["blk"])
		self.assertIs(generate, architecture._hierarchy["gen"])
		self.assertEqual(["blk", "gen"], list(architecture._hierarchy.keys()))

	def test_IterateInstantiations_RecursesIntoBlocksAndGenerates(self) -> None:
		entitySymbol = _entitySymbol("e")
		nestedInstance = ComponentInstantiation("nested_inst", ComponentInstantiationSymbol(SimpleName("comp")))
		block = ConcurrentBlockStatement("blk", statements=[nestedInstance])

		architecture = Architecture("rtl", entitySymbol, statements=[block])
		architecture.IndexStatements()
		instantiations = list(architecture.IterateInstantiations())

		self.assertEqual(1, len(instantiations))
		self.assertIs(nestedInstance, instantiations[0])
