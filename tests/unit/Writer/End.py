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
"""Tests for the optional reserved words and names after ``end`` with pyVHDLModel.Formatting.VHDL."""
from pathlib                     import Path
from textwrap                    import dedent
from unittest                    import skipIf

from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Document
from pyVHDLModel.Base            import Direction, Mode, SimpleRange
from pyVHDLModel.Concurrent      import ProcessStatement, ConcurrentBlockStatement, ForGenerateStatement
from pyVHDLModel.Configuration   import BlockConfiguration
from pyVHDLModel.DesignUnit      import Context, Package, PackageBody, Entity, Architecture, Configuration, Component
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import OptionalItem, VHDLStyle, VHDLWriter
from pyVHDLModel.Interface       import PortSimpleSignalInterfaceItem
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Object          import Variable
from pyVHDLModel.Sequential      import IfBranch, IfStatement, ForLoopStatement, NullStatement, WaitStatement
from pyVHDLModel.Subprogram      import Procedure, ProcedureMethod
from pyVHDLModel.Symbol          import EntitySymbol, ArchitectureSymbol, PackageSymbol
from pyVHDLModel.Type            import RecordTypeElement, RecordType, ProtectedType, ProtectedTypeBody

from tests.unit                  import _subtypeSymbol
from tests.unit.Writer           import _GHDL, _analyze, _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _style(endKeyword: OptionalItem, endName: OptionalItem) -> VHDLStyle:
	"""Formatting options with the given end keyword and end name actions."""
	return VHDLStyle(endKeyword=endKeyword, endName=endName)


def _process() -> ProcessStatement:
	"""Labeled process with a labeled if statement."""
	return ProcessStatement("p", statements=[IfStatement(IfBranch(_object("a"), [NullStatement()]), label="check")])


class EndKeywordConstants(Testcase):
	def test_Optional(self) -> None:
		"""The reserved words after ``end`` of design units and subprogram bodies are optional."""
		for cls in (Context, Package, PackageBody, Entity, Architecture, Configuration, Procedure, ProcedureMethod):
			with self.subTest(cls=cls.__name__):
				self.assertTrue(cls._END_KEYWORDS_OPTIONAL)

	def test_Required(self) -> None:
		for cls in (Component, RecordType, ProtectedType, ProtectedTypeBody, ProcessStatement, ConcurrentBlockStatement,
		            ForGenerateStatement, IfStatement, ForLoopStatement, BlockConfiguration):
			with self.subTest(cls=cls.__name__):
				self.assertFalse(cls._END_KEYWORDS_OPTIONAL)


class EndKeywords(Testcase):
	def test_Entity(self) -> None:
		writer = VHDLWriter(_style(OptionalItem.Remove, OptionalItem.Add))

		self.assertEqual("entity e is\nend e;\n", writer.Format(Entity("e")))

	def test_Procedure(self) -> None:
		"""A subprogram body has optional reserved words after ``end``, a declaration has no end."""
		body =   Procedure("p", statements=[NullStatement()])
		writer = VHDLWriter(_style(OptionalItem.Remove, OptionalItem.Add))

		self.assertEqual("procedure p is\nbegin\n  null;\nend p;\n", writer.Format(body))
		self.assertEqual("procedure q;\n", writer.Format(Procedure("q")))

	def test_Required(self) -> None:
		"""The reserved words after ``end`` of a component, a process or an if statement are required."""
		component = Component("c", portItems=[PortSimpleSignalInterfaceItem(["a"], Mode.In, _subtypeSymbol("bit"))])
		writer =    VHDLWriter(_style(OptionalItem.Remove, OptionalItem.Add))

		self.assertEqual(dedent("""\
			component c is
			  port (
			    a : in bit
			  );
			end component c;
			"""), writer.Format(component))
		self.assertEqual(dedent("""\
			p : process is
			begin
			  check : if a then
			    null;
			  end if check;
			end process p;
			"""), writer.Format(_process()))


class EndNames(Testcase):
	def test_Entity(self) -> None:
		writer = VHDLWriter(_style(OptionalItem.Add, OptionalItem.Remove))

		self.assertEqual("entity e is\nend entity;\n", writer.Format(Entity("e")))

	def test_Labels(self) -> None:
		self.assertEqual(dedent("""\
			p : process is
			begin
			  check : if a then
			    null;
			  end if;
			end process;
			"""), VHDLWriter(_style(OptionalItem.Add, OptionalItem.Remove)).Format(_process()))

	def test_Neither(self) -> None:
		writer = VHDLWriter(_style(OptionalItem.Remove, OptionalItem.Remove))

		self.assertEqual("entity e is\nend;\n", writer.Format(Entity("e")))

	def test_WithoutLabel(self) -> None:
		"""A statement without label has no name after ``end``."""
		loop = ForLoopStatement("i", SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To), [NullStatement()])

		self.assertEqual("for i in 0 to 3 loop\n  null;\nend loop;\n", VHDLWriter().Format(loop))


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracle(Testcase):
	def test_Ends(self) -> None:
		"""Each combination of end keywords and end names is analyzed by GHDL."""
		def counter() -> ProtectedType:
			"""Nested function returning the protected type ``counter``."""
			return ProtectedType("counter", [ProcedureMethod("increment")])

		designUnits = (
			Context("project"),
			Package("utilities", declaredItems=[
				RecordType("pair", [RecordTypeElement(["a", "b"], _subtypeSymbol("bit"))]),
				counter(),
				Procedure("reset")
			]),
			PackageBody(PackageSymbol(SimpleName("utilities")), declaredItems=[
				ProtectedTypeBody("counter", [
					Variable(["count"], _subtypeSymbol("natural"), IntegerLiteral(0)),
					ProcedureMethod("increment", statements=[NullStatement()])
				]),
				Procedure("reset", statements=[NullStatement()])
			]),
			Entity("top"),
			Architecture("rtl", EntitySymbol(SimpleName("top")), declaredItems=[Component("c")], statements=[
				ProcessStatement("p", statements=[
					IfStatement(IfBranch(_object("true"), [NullStatement()]), label="check"),
					ForLoopStatement(
						"i",
						SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To),
						[NullStatement()],
						"outer"
					),
					WaitStatement()
				]),
				ConcurrentBlockStatement("inner"),
				ForGenerateStatement("gen", "i", SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To))
			]),
			Configuration(
				"top_cfg",
				EntitySymbol(SimpleName("top")),
				BlockConfiguration(ArchitectureSymbol(SimpleName("rtl")))
			)
		)

		for endKeyword in OptionalItem:
			for endName in OptionalItem:
				with self.subTest(endKeyword=endKeyword, endName=endName):
					document = Document(Path("oracle.vhdl"))
					for designUnit in designUnits:
						document._AddDesignUnit(designUnit)

					source = VHDLWriter(_style(endKeyword, endName)).Format(document)

					result = _analyze(source)

					self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)
