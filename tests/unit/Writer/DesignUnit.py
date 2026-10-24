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
"""Tests for writing context items, design units and documents with pyVHDLModel.Formatting.VHDL."""
from pathlib                     import Path
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Document
from pyVHDLModel.Association     import GenericAssociationItem
from pyVHDLModel.Base            import Mode
from pyVHDLModel.Concurrent      import ConcurrentBlockStatement
from pyVHDLModel.DesignUnit      import LibraryClause, UseClause, ContextReference, Context, Package, PackageBody, \
                                        Entity, Architecture
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Instantiation   import PackageInstantiation
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, PortSimpleSignalInterfaceItem
from pyVHDLModel.Name            import SimpleName, SelectedName, AllName
from pyVHDLModel.Object          import Constant, Signal
from pyVHDLModel.Subprogram      import Function, Procedure
from pyVHDLModel.Symbol          import LibraryReferenceSymbol, AllPackageMembersReferenceSymbol, \
                                        ContextReferenceSymbol, PackageMemberReferenceSymbol, PackageSymbol, \
                                        PackageReferenceSymbol

from tests.unit                  import _entitySymbol, _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _library(name: str) -> LibraryClause:
	"""Library clause of one library."""
	return LibraryClause([LibraryReferenceSymbol(SimpleName(name))])


def _useAll(library: str, package: str) -> UseClause:
	"""Use clause of all members of one package."""
	return UseClause([AllPackageMembersReferenceSymbol(AllName(SelectedName(package, SimpleName(library))))])


def _counter() -> Entity:
	"""Entity with a context clause, a generic and two ports."""
	return Entity(
		"counter",
		[_library("ieee"), _useAll("ieee", "std_logic_1164")],
		[GenericConstantInterfaceItem(["BITS"], Mode.Default, _subtypeSymbol("positive"), IntegerLiteral(8))],
		[
			PortSimpleSignalInterfaceItem(["clk"], Mode.In, _subtypeSymbol("std_logic")),
			PortSimpleSignalInterfaceItem(["count"], Mode.Out, _subtypeSymbol("natural"))
		]
	)


class ContextItems(Testcase):
	def test_Library(self) -> None:
		clause = LibraryClause([LibraryReferenceSymbol(SimpleName("ieee")), LibraryReferenceSymbol(SimpleName("std"))])

		self.assertEqual("library ieee, std;\n", VHDLWriter().Format(clause))

	def test_Use(self) -> None:
		clause = UseClause([
			AllPackageMembersReferenceSymbol(AllName(SelectedName("std_logic_1164", SimpleName("ieee")))),
			PackageMemberReferenceSymbol(SelectedName("to_unsigned", SelectedName("numeric_std", SimpleName("ieee"))))
		])

		self.assertEqual("use ieee.std_logic_1164.all, ieee.numeric_std.to_unsigned;\n", VHDLWriter().Format(clause))

	def test_ContextReference(self) -> None:
		reference = ContextReference([ContextReferenceSymbol(SelectedName("ieee_std_context", SimpleName("ieee")))])

		self.assertEqual("context ieee.ieee_std_context;\n", VHDLWriter().Format(reference))

	def test_UpperCase(self) -> None:
		self.assertEqual("LIBRARY ieee;\n", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(_library("ieee")))


class DesignUnits(Testcase):
	def test_Entity(self) -> None:
		"""Context items precede the design unit, separated by a blank line."""
		self.assertEqual(dedent("""\
			library ieee;
			use ieee.std_logic_1164.all;

			entity counter is
			  generic (
			    BITS : positive := 8
			  );
			  port (
			    clk : in std_logic;
			    count : out natural
			  );
			end entity counter;
			"""), VHDLWriter().Format(_counter()))

	def test_Entity_Empty(self) -> None:
		self.assertEqual("entity top is\nend entity top;\n", VHDLWriter().Format(Entity("top")))

	def test_Entity_Declarations(self) -> None:
		entity = Entity("e", declaredItems=[Constant(["DEPTH"], _subtypeSymbol("natural"), IntegerLiteral(4))])

		self.assertEqual(dedent("""\
			entity e is
			  constant DEPTH : natural := 4;
			end entity e;
			"""), VHDLWriter().Format(entity))

	def test_Entity_Statements(self) -> None:
		"""An entity with statements has a statement part after ``begin``."""
		entity = Entity("e", statements=[ConcurrentBlockStatement("b")])

		self.assertEqual(dedent("""\
			entity e is
			begin
			  b : block
			  begin
			  end block b;
			end entity e;
			"""), VHDLWriter().Format(entity))

	def test_Architecture(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("counter"), declaredItems=[
			Signal(["value"], _subtypeSymbol("natural"), IntegerLiteral(0))
		])

		self.assertEqual(dedent("""\
			architecture rtl of counter is
			  signal value : natural := 0;
			begin
			end architecture rtl;
			"""), VHDLWriter().Format(architecture))

	def test_Architecture_Empty(self) -> None:
		architecture = Architecture("empty", _entitySymbol("e"))

		self.assertEqual("architecture empty of e is\nbegin\nend architecture empty;\n", VHDLWriter().Format(architecture))

	def test_Package(self) -> None:
		package = Package(
			"utilities",
			genericItems=[GenericConstantInterfaceItem(["WIDTH"], Mode.Default, _subtypeSymbol("positive"))],
			declaredItems=[Function("parity", _subtypeSymbol("bit"))]
		)

		self.assertEqual(dedent("""\
			package utilities is
			  generic (
			    WIDTH : positive
			  );
			  function parity return bit;
			end package utilities;
			"""), VHDLWriter().Format(package))

	def test_PackageBody(self) -> None:
		body = PackageBody(PackageSymbol(SimpleName("utilities")), [_library("ieee")], [
			Constant(["ZERO"], _subtypeSymbol("natural"), IntegerLiteral(0))
		])

		self.assertEqual(dedent("""\
			library ieee;

			package body utilities is
			  constant ZERO : natural := 0;
			end package body utilities;
			"""), VHDLWriter().Format(body))

	def test_Subprograms(self) -> None:
		"""An empty subprogram is a subprogram declaration in a package, but an empty subprogram body in a package body."""
		package = Package("p", declaredItems=[Procedure("stub")])
		body =    PackageBody(PackageSymbol(SimpleName("p")), declaredItems=[Procedure("stub")])

		self.assertEqual("package p is\n  procedure stub;\nend package p;\n", VHDLWriter().Format(package))
		self.assertEqual(dedent("""\
			package body p is
			  procedure stub is
			  begin
			  end procedure stub;
			end package body p;
			"""), VHDLWriter().Format(body))

	def test_PackageInstantiation(self) -> None:
		instantiation = PackageInstantiation(
			"fifo_byte",
			PackageReferenceSymbol(SelectedName("fifo", SimpleName("work"))),
			genericAssociationItems=[GenericAssociationItem(SimpleName("WIDTH"), IntegerLiteral(8))]
		)

		self.assertEqual(dedent("""\
			package fifo_byte is new work.fifo
			  generic map (
			    WIDTH => 8
			  );
			"""), VHDLWriter().Format(instantiation))

	def test_Context(self) -> None:
		context = Context("project", [_library("ieee"), _useAll("ieee", "numeric_std")])

		self.assertEqual(dedent("""\
			context project is
			  library ieee;
			  use ieee.numeric_std.all;
			end context project;
			"""), VHDLWriter().Format(context))

	def test_SmartTabs(self) -> None:
		package = Package("p", declaredItems=[Constant(["C"], _subtypeSymbol("natural"), IntegerLiteral(1))])

		self.assertEqual(
			"package p is\n\tconstant C : natural := 1;\nend package p;\n",
			VHDLWriter(VHDLStyle(indentStyle=IndentStyle.SmartTabs)).Format(package)
		)

	def test_UpperCase(self) -> None:
		body = PackageBody(PackageSymbol(SimpleName("p")))

		self.assertEqual("PACKAGE BODY p IS\nEND PACKAGE BODY p;\n", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(body))


class Documents(Testcase):
	def test_Document(self) -> None:
		"""Design units are separated by a blank line."""
		document = Document(Path("counter.vhdl"))
		document._AddDesignUnit(_counter())
		document._AddDesignUnit(Architecture("rtl", _entitySymbol("counter")))

		self.assertEqual(dedent("""\
			library ieee;
			use ieee.std_logic_1164.all;

			entity counter is
			  generic (
			    BITS : positive := 8
			  );
			  port (
			    clk : in std_logic;
			    count : out natural
			  );
			end entity counter;

			architecture rtl of counter is
			begin
			end architecture rtl;
			"""), VHDLWriter().Format(document))

	def test_Empty(self) -> None:
		self.assertEqual("", VHDLWriter().Format(Document(Path("empty.vhdl"))))
