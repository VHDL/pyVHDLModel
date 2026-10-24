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
"""Tests for writing interface items, components and mode views with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Mode
from pyVHDLModel.DesignUnit      import Component
from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import IntegerLiteral, CharacterLiteral
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, NewLine, ListStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                        PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                        ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                        ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                        ParameterFileInterfaceItem, ModeViewDeclaration, SimpleModeViewElement, \
                                        CompositeModeViewElement
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Symbol          import ModeViewSymbol

from tests.unit                  import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _view(name: str) -> ModeViewSymbol:
	"""Reference to a mode view."""
	return ModeViewSymbol(SimpleName(name))


def _component() -> Component:
	"""Component with a generic constant, a generic type and two ports."""
	return Component(
		"counter",
		[
			GenericConstantInterfaceItem(["BITS"], Mode.Default, _subtypeSymbol("positive"), IntegerLiteral(8)),
			GenericTypeInterfaceItem("T")
		],
		[
			PortSimpleSignalInterfaceItem(["clk", "rst"], Mode.In, _subtypeSymbol("bit")),
			PortSimpleSignalInterfaceItem(["q"], Mode.Out, _subtypeSymbol("T"))
		]
	)


class GenericItems(Testcase):
	def test_Constant(self) -> None:
		item = GenericConstantInterfaceItem(["BITS"], Mode.Default, _subtypeSymbol("positive"))

		self.assertEqual("BITS : positive", VHDLWriter().Format(item))

	def test_Constant_Mode(self) -> None:
		item = GenericConstantInterfaceItem(["BITS"], Mode.In, _subtypeSymbol("positive"), IntegerLiteral(8))

		self.assertEqual("BITS : in positive := 8", VHDLWriter().Format(item))

	def test_Type(self) -> None:
		self.assertEqual("type T", VHDLWriter().Format(GenericTypeInterfaceItem("T")))


class PortItems(Testcase):
	def test_Simple(self) -> None:
		item = PortSimpleSignalInterfaceItem(["clk", "rst"], Mode.In, _subtypeSymbol("bit"))

		self.assertEqual("clk, rst : in bit", VHDLWriter().Format(item))

	def test_Simple_Modes(self) -> None:
		writer =  VHDLWriter()
		out =     PortSimpleSignalInterfaceItem(["p"], Mode.Out, _subtypeSymbol("bit"))
		inout =   PortSimpleSignalInterfaceItem(["p"], Mode.InOut, _subtypeSymbol("bit"))
		buffer =  PortSimpleSignalInterfaceItem(["p"], Mode.Buffer, _subtypeSymbol("bit"))
		linkage = PortSimpleSignalInterfaceItem(["p"], Mode.Linkage, _subtypeSymbol("bit"))

		self.assertEqual("p : out bit", writer.Format(out))
		self.assertEqual("p : inout bit", writer.Format(inout))
		self.assertEqual("p : buffer bit", writer.Format(buffer))
		self.assertEqual("p : linkage bit", writer.Format(linkage))

	def test_Simple_DefaultMode(self) -> None:
		"""A port without a mode is written without one, which means ``in``."""
		item = PortSimpleSignalInterfaceItem(["d"], Mode.Default, _subtypeSymbol("bit"))

		self.assertEqual("d : bit", VHDLWriter().Format(item))

	def test_Simple_DefaultExpression(self) -> None:
		item = PortSimpleSignalInterfaceItem(["d"], Mode.In, _subtypeSymbol("bit"), CharacterLiteral("0"))

		self.assertEqual("d : in bit := '0'", VHDLWriter().Format(item))

	def test_View(self) -> None:
		item = PortViewSignalInterfaceItem(["link"], _view("master"))

		self.assertEqual("link : view master", VHDLWriter().Format(item))


class ParameterItems(Testcase):
	def test_Constant(self) -> None:
		item = ParameterConstantInterfaceItem(["value"], Mode.In, _subtypeSymbol("integer"), IntegerLiteral(0))

		self.assertEqual("constant value : in integer := 0", VHDLWriter().Format(item))

	def test_Variable(self) -> None:
		item = ParameterVariableInterfaceItem(["result"], Mode.Out, _subtypeSymbol("integer"))

		self.assertEqual("variable result : out integer", VHDLWriter().Format(item))

	def test_Signal(self) -> None:
		item = ParameterSimpleSignalInterfaceItem(["clk"], Mode.Default, _subtypeSymbol("bit"))

		self.assertEqual("signal clk : bit", VHDLWriter().Format(item))

	def test_View(self) -> None:
		item = ParameterViewSignalInterfaceItem(["link"], _view("master"))

		self.assertEqual("signal link : view master", VHDLWriter().Format(item))

	def test_File(self) -> None:
		item = ParameterFileInterfaceItem(["input"], _subtypeSymbol("text"))

		self.assertEqual("file input : text", VHDLWriter().Format(item))

	def test_UpperCase(self) -> None:
		item = ParameterSimpleSignalInterfaceItem(["clk"], Mode.In, _subtypeSymbol("bit"))

		self.assertEqual("SIGNAL clk : IN bit", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(item))


class Components(Testcase):
	def test_Component(self) -> None:
		self.assertEqual(dedent("""\
			component counter is
			  generic (
			    BITS : positive := 8;
			    type T
			  );
			  port (
			    clk, rst : in bit;
			    q : out T
			  );
			end component counter;
			"""), VHDLWriter().Format(_component()))

	def test_Empty(self) -> None:
		"""A component without generics and ports has neither clause."""
		self.assertEqual("component empty is\nend component empty;\n", VHDLWriter().Format(Component("empty")))

	def test_Ports(self) -> None:
		component = Component("inverter", portItems=[
			PortSimpleSignalInterfaceItem(["a"], Mode.In, _subtypeSymbol("bit")),
			PortSimpleSignalInterfaceItem(["y"], Mode.Out, _subtypeSymbol("bit"))
		])

		self.assertEqual(dedent("""\
			component inverter is
			  port (
			    a : in bit;
			    y : out bit
			  );
			end component inverter;
			"""), VHDLWriter().Format(component))

	def test_SmartTabs(self) -> None:
		style = VHDLStyle(indentStyle=IndentStyle.SmartTabs)

		self.assertEqual(
			"component counter is\n"
			"\tgeneric (\n"
			"\t\tBITS : positive := 8;\n"
			"\t\ttype T\n"
			"\t);\n"
			"\tport (\n"
			"\t\tclk, rst : in bit;\n"
			"\t\tq : out T\n"
			"\t);\n"
			"end component counter;\n",
			VHDLWriter(style).Format(_component())
		)

	def test_IndentSize(self) -> None:
		component = Component("buffer_t", portItems=[PortSimpleSignalInterfaceItem(["a"], Mode.In, _subtypeSymbol("bit"))])

		self.assertEqual(dedent("""\
			component buffer_t is
			    port (
			        a : in bit
			    );
			end component buffer_t;
			"""), VHDLWriter(VHDLStyle(indentSize=4)).Format(component))

	def test_UpperCase(self) -> None:
		component = Component("inverter", portItems=[PortSimpleSignalInterfaceItem(["a"], Mode.In, _subtypeSymbol("bit"))])

		self.assertEqual(dedent("""\
			COMPONENT inverter IS
			  PORT (
			    a : IN bit
			  );
			END COMPONENT inverter;
			"""), VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(component))

	def test_InterfaceElement_Remove(self) -> None:
		"""Interface elements and the right parenthesis continue the line: one line per clause."""
		listStyle = ListStyle(NewLine.Remove, lastCloseParen=NewLine.Remove)
		style =     VHDLStyle(genericClause=listStyle, portClause=listStyle)

		self.assertEqual(dedent("""\
			component counter is
			  generic (BITS : positive := 8; type T);
			  port (clk, rst : in bit; q : out T);
			end component counter;
			"""), VHDLWriter(style).Format(_component()))

	def test_InterfaceListSemicolon_Add(self) -> None:
		"""The semicolon starts the line of the next interface element."""
		listStyle = ListStyle(NewLine.Remove, NewLine.Add)
		style =     VHDLStyle(genericClause=listStyle, portClause=listStyle)

		self.assertEqual(dedent("""\
			component counter is
			  generic (BITS : positive := 8
			    ; type T
			  );
			  port (clk, rst : in bit
			    ; q : out T
			  );
			end component counter;
			"""), VHDLWriter(style).Format(_component()))

	def test_InterfaceListSemicolon_Add_InterfaceElement_Add(self) -> None:
		"""The semicolon and the next interface element each start a new line."""
		listStyle = ListStyle(separator=NewLine.Add)
		style =     VHDLStyle(genericClause=listStyle, portClause=listStyle)

		self.assertEqual(dedent("""\
			component counter is
			  generic (
			    BITS : positive := 8
			    ;
			    type T
			  );
			  port (
			    clk, rst : in bit
			    ;
			    q : out T
			  );
			end component counter;
			"""), VHDLWriter(style).Format(_component()))


class ModeViews(Testcase):
	def test_ModeView(self) -> None:
		declaration = ModeViewDeclaration("master", _subtypeSymbol("bus_t"), [
			SimpleModeViewElement(["valid", "data"], Mode.Out),
			SimpleModeViewElement(["ready"], Mode.In),
			CompositeModeViewElement(["request"], _view("request_master"))
		])

		self.assertEqual(dedent("""\
			view master of bus_t is
			  valid, data : out;
			  ready : in;
			  request : view request_master;
			end view master;
			"""), VHDLWriter().Format(declaration))

	def test_Element_WithoutMode(self) -> None:
		element =     SimpleModeViewElement(["valid"], Mode.Default)
		declaration = ModeViewDeclaration("master", _subtypeSymbol("bus_t"), [element])

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(declaration)

		self.assertEqual("Mode view element has no mode.", str(context.exception))
		self.assertIs(element, context.exception.Element)
