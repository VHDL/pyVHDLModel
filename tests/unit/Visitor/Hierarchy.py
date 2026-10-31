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
"""Tests for the walk of instantiations, block statements and generate statements (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Association import PortAssociationItem
from pyVHDLModel.Base        import Direction, SimpleRange
from pyVHDLModel.Concurrent  import EntityInstantiation, ConcurrentBlockStatement, IfGenerateBranch, \
                                    ElseGenerateBranch, IfGenerateStatement, IndexedGenerateChoice, GenerateCase, \
                                    OthersGenerateCase, CaseGenerateStatement, ForGenerateStatement
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Object      import Signal
from pyVHDLModel.Symbol      import EntityInstantiationSymbol, ArchitectureSymbol, SimpleObjectOrFunctionCallSymbol, \
                                    SimpleSubtypeSymbol

from tests.unit.Visitor      import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Instantiations(Testcase):
	def test_Entity(self) -> None:
		"""The architecture name is enclosed by parenthesis events; the map aspects follow."""
		entity =        EntityInstantiationSymbol(SimpleName("counter"))
		architecture =  ArchitectureSymbol(SimpleName("rtl"))
		association =   PortAssociationItem(None, SimpleName("clk"))
		instantiation = EntityInstantiation("u1", entity, architecture, portAssociationItems=[association])
		recorder =      FullRecorder()

		instantiation.Visit(recorder)

		self.assertEqual([
			"VisitEntityInstantiation",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitLeftParenthesis",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitRightParenthesis",
			"VisitPortMapAspect",
			"VisitAssociationItem", "VisitSimpleName", "DepartSimpleName", "DepartAssociationItem",
			"DepartPortMapAspect",
			"VisitTerminator", "DepartEntityInstantiation",
		], [event[0] for event in recorder.Events])


class Blocks(Testcase):
	def test_Block(self) -> None:
		signal =   Signal(["t"], SimpleSubtypeSymbol(SimpleName("bit")))
		block =    ConcurrentBlockStatement("b", declaredItems=[signal])
		recorder = FullRecorder()

		block.Visit(recorder)

		self.assertEqual(
			["VisitConcurrentBlockStatement", "VisitSignal", "VisitSymbol", "VisitSimpleName", "DepartSimpleName",
			 "DepartSymbol", "VisitTerminator", "DepartSignal", "VisitBegin", "DepartConcurrentBlockStatement"],
			[event[0] for event in recorder.Events]
		)


class Generates(Testcase):
	def test_If(self) -> None:
		condition =  SimpleObjectOrFunctionCallSymbol(SimpleName("ENABLE"))
		ifBranch =   IfGenerateBranch(condition)
		elseBranch = ElseGenerateBranch()
		statement =  IfGenerateStatement("gen", ifBranch, elseBranch=elseBranch)
		recorder =   FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			("VisitIfGenerateStatement",  statement),
			("VisitIfGenerateBranch",     ifBranch),
			("VisitSymbol",               condition),
			("VisitSimpleName",           condition.Name),
			("DepartSimpleName",          condition.Name),
			("DepartSymbol",              condition),
			("VisitGenerate",             ifBranch),
			("VisitBegin",                ifBranch),
			("DepartIfGenerateBranch",    ifBranch),
			("VisitElseGenerateBranch",   elseBranch),
			("VisitGenerate",             elseBranch),
			("VisitBegin",                elseBranch),
			("DepartElseGenerateBranch",  elseBranch),
			("DepartIfGenerateStatement", statement),
		], recorder.Events)

	def test_Case(self) -> None:
		selector =  SimpleObjectOrFunctionCallSymbol(SimpleName("MODE"))
		value =     IntegerLiteral(0)
		choice =    IndexedGenerateChoice(value)
		case =      GenerateCase([choice])
		others =    OthersGenerateCase()
		statement = CaseGenerateStatement("gen", selector, [case, others])
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual([
			("VisitCaseGenerateStatement",  statement),
			("VisitSymbol",                 selector),
			("VisitSimpleName",             selector.Name),
			("DepartSimpleName",            selector.Name),
			("DepartSymbol",                selector),
			("VisitGenerate",               statement),
			("VisitGenerateCase",           case),
			("VisitIndexedGenerateChoice",  choice),
			("VisitIntegerLiteral",         value),
			("DepartIntegerLiteral",        value),
			("DepartIndexedGenerateChoice", choice),
			("VisitArrow",                  case),
			("VisitBegin",                  case),
			("DepartGenerateCase",          case),
			("VisitOthersGenerateCase",     others),
			("VisitArrow",                  others),
			("VisitBegin",                  others),
			("DepartOthersGenerateCase",    others),
			("DepartCaseGenerateStatement", statement),
		], recorder.Events)

	def test_For(self) -> None:
		rng =       SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		statement = ForGenerateStatement("gen", "i", rng)
		recorder =  FullRecorder()

		statement.Visit(recorder)

		self.assertEqual(
			["VisitForGenerateStatement", "VisitSimpleRange", "VisitIntegerLiteral", "DepartIntegerLiteral",
			 "VisitDirection", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartSimpleRange", "VisitGenerate",
			 "VisitBegin", "DepartForGenerateStatement"],
			[event[0] for event in recorder.Events]
		)
