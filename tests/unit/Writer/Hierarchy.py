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
"""Tests for writing instantiations, block statements and generate statements with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Base            import Direction, Mode, SimpleRange, WaveformElement
from pyVHDLModel.Concurrent      import ComponentInstantiation, EntityInstantiation, ConfigurationInstantiation, \
                                        ConcurrentBlockStatement, IfGenerateBranch, ElsifGenerateBranch, \
                                        ElseGenerateBranch, IfGenerateStatement, IndexedGenerateChoice, \
                                        RangedGenerateChoice, GenerateCase, OthersGenerateCase, CaseGenerateStatement, \
                                        ForGenerateStatement, ConcurrentSimpleSignalAssignment
from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import IntegerLiteral, GreaterThanExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, PortSimpleSignalInterfaceItem
from pyVHDLModel.Name            import SimpleName, SelectedName, OpenName
from pyVHDLModel.Object          import Signal
from pyVHDLModel.Symbol          import ComponentInstantiationSymbol, EntityInstantiationSymbol, ArchitectureSymbol, \
                                        ConfigurationInstantiationSymbol

from tests.unit                  import _signalSymbol, _subtypeSymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _assign(target: str, source: str) -> ConcurrentSimpleSignalAssignment:
	"""Concurrent signal assignment of one object to a signal."""
	return ConcurrentSimpleSignalAssignment(None, _signalSymbol(target), [WaveformElement(_object(source))])


def _work(name: str) -> SelectedName:
	"""Name of a design unit in library ``work``."""
	return SelectedName(name, SimpleName("work"))


class Instantiations(Testcase):
	def test_Entity(self) -> None:
		instantiation = EntityInstantiation(
			"u1",
			EntityInstantiationSymbol(_work("counter")),
			ArchitectureSymbol(SimpleName("rtl")),
			[GenericAssociationItem(SimpleName("BITS"), IntegerLiteral(8))],
			[PortAssociationItem(SimpleName("clk"), _object("clock")), PortAssociationItem(SimpleName("q"), OpenName())]
		)

		self.assertEqual(dedent("""\
			u1 : entity work.counter(rtl)
			  generic map (
			    BITS => 8
			  )
			  port map (
			    clk => clock,
			    q => open
			  );
			"""), VHDLWriter().Format(instantiation))

	def test_Entity_WithoutArchitecture(self) -> None:
		instantiation = EntityInstantiation("u1", EntityInstantiationSymbol(_work("top")))

		self.assertEqual("u1 : entity work.top;\n", VHDLWriter().Format(instantiation))

	def test_Component(self) -> None:
		instantiation = ComponentInstantiation(
			"u2",
			ComponentInstantiationSymbol(SimpleName("counter")),
			portAssociationItems=[PortAssociationItem(None, _object("clock"))]
		)

		self.assertEqual(dedent("""\
			u2 : component counter
			  port map (
			    clock
			  );
			"""), VHDLWriter().Format(instantiation))

	def test_Configuration(self) -> None:
		instantiation = ConfigurationInstantiation("u3", ConfigurationInstantiationSymbol(_work("counter_cfg")))

		self.assertEqual("u3 : configuration work.counter_cfg;\n", VHDLWriter().Format(instantiation))

	def test_WithoutLabel(self) -> None:
		instantiation = ComponentInstantiation(None, ComponentInstantiationSymbol(SimpleName("counter")))

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(instantiation)

		self.assertEqual("Component instantiation has no label.", str(context.exception))
		self.assertIs(instantiation, context.exception.Element)

	def test_UpperCase(self) -> None:
		instantiation = EntityInstantiation(
			"u1",
			EntityInstantiationSymbol(_work("top")),
			portAssociationItems=[PortAssociationItem(SimpleName("a"), _object("b"))]
		)

		self.assertEqual(dedent("""\
			u1 : ENTITY work.top
			  PORT MAP (
			    a => b
			  );
			"""), VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(instantiation))


class Blocks(Testcase):
	def test_Block(self) -> None:
		block = ConcurrentBlockStatement(
			"inner",
			[GenericConstantInterfaceItem(["G"], Mode.Default, _subtypeSymbol("positive"))],
			[GenericAssociationItem(SimpleName("G"), IntegerLiteral(2))],
			[PortSimpleSignalInterfaceItem(["bp"], Mode.In, _subtypeSymbol("bit"))],
			[PortAssociationItem(SimpleName("bp"), _object("clock"))],
			[Signal(["local"], _subtypeSymbol("bit"))],
			[_assign("local", "bp")]
		)

		self.assertEqual(dedent("""\
			inner : block
			  generic (
			    G : positive
			  );
			  generic map (
			    G => 2
			  );
			  port (
			    bp : in bit
			  );
			  port map (
			    bp => clock
			  );
			  signal local : bit;
			begin
			  local <= bp;
			end block inner;
			"""), VHDLWriter().Format(block))

	def test_Block_Empty(self) -> None:
		self.assertEqual("empty : block\nbegin\nend block empty;\n", VHDLWriter().Format(ConcurrentBlockStatement("empty")))

	def test_Block_SmartTabs(self) -> None:
		block = ConcurrentBlockStatement("inner", statements=[_assign("q", "d")])

		self.assertEqual(
			"inner : block\nbegin\n\tq <= d;\nend block inner;\n",
			VHDLWriter(VHDLStyle(indentStyle=IndentStyle.SmartTabs)).Format(block)
		)


class Generates(Testcase):
	def test_If(self) -> None:
		statement = IfGenerateStatement(
			"gen",
			IfGenerateBranch(GreaterThanExpression(_object("BITS"), IntegerLiteral(8)), statements=[_assign("q", "a")]),
			[ElsifGenerateBranch(
				GreaterThanExpression(_object("BITS"), IntegerLiteral(4)),
				[Signal(["t"], _subtypeSymbol("bit"))],
				[_assign("q", "t")],
				alternativeLabel="middle"
			)],
			ElseGenerateBranch(statements=[_assign("q", "b")])
		)

		self.assertEqual(dedent("""\
			gen : if BITS > 8 generate
			  q <= a;
			elsif middle : BITS > 4 generate
			  signal t : bit;
			begin
			  q <= t;
			else generate
			  q <= b;
			end generate gen;
			"""), VHDLWriter().Format(statement))

	def test_If_AlternativeLabels(self) -> None:
		statement = IfGenerateStatement(
			"gen",
			IfGenerateBranch(_object("ENABLE"), statements=[_assign("q", "a")], alternativeLabel="on"),
			elseBranch=ElseGenerateBranch(statements=[_assign("q", "b")], alternativeLabel="off")
		)

		self.assertEqual(dedent("""\
			gen : if on : ENABLE generate
			  q <= a;
			else off : generate
			  q <= b;
			end generate gen;
			"""), VHDLWriter().Format(statement))

	def test_Case(self) -> None:
		statement = CaseGenerateStatement("gen", _object("MODE"), [
			GenerateCase(
				[
					IndexedGenerateChoice(IntegerLiteral(0)),
					RangedGenerateChoice(SimpleRange(IntegerLiteral(1), IntegerLiteral(2), Direction.To))
				],
				statements=[_assign("q", "a")]
			),
			GenerateCase(
				[IndexedGenerateChoice(IntegerLiteral(3))],
				statements=[_assign("q", "c")],
				alternativeLabel="three"
			),
			OthersGenerateCase(declaredItems=[Signal(["t"], _subtypeSymbol("bit"))], statements=[_assign("q", "t")])
		])

		self.assertEqual(dedent("""\
			gen : case MODE generate
			  when 0 | 1 to 2 =>
			    q <= a;
			  when three : 3 =>
			    q <= c;
			  when others =>
			    signal t : bit;
			  begin
			    q <= t;
			end generate gen;
			"""), VHDLWriter().Format(statement))

	def test_For(self) -> None:
		statement = ForGenerateStatement(
			"gen",
			"i",
			SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To),
			[Signal(["t"], _subtypeSymbol("bit"))],
			[_assign("t", "a")]
		)

		self.assertEqual(dedent("""\
			gen : for i in 0 to 3 generate
			  signal t : bit;
			begin
			  t <= a;
			end generate gen;
			"""), VHDLWriter().Format(statement))

	def test_WithoutLabel(self) -> None:
		statement = ForGenerateStatement(None, "i", SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To))

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(statement)

		self.assertEqual("For-generate statement has no label.", str(context.exception))

	def test_UpperCase(self) -> None:
		statement = ForGenerateStatement(
			"gen",
			"i",
			SimpleRange(IntegerLiteral(3), IntegerLiteral(0), Direction.DownTo),
			statements=[_assign("q", "a")]
		)

		self.assertEqual(dedent("""\
			gen : FOR i IN 3 DOWNTO 0 GENERATE
			  q <= a;
			END GENERATE gen;
			"""), VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(statement))
