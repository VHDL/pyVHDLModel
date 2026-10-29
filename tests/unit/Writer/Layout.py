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
"""Tests for the layout of parenthesized lists per construct with pyVHDLModel.Formatting.VHDL."""
from pathlib                     import Path
from textwrap                    import dedent
from unittest                    import skipIf

from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Document
from pyVHDLModel.Association     import GenericAssociationItem, PortAssociationItem, ParameterAssociationItem
from pyVHDLModel.Base            import Mode
from pyVHDLModel.Concurrent      import ComponentInstantiation, ConcurrentProcedureCall
from pyVHDLModel.DesignUnit      import UseClause, Component, Entity, Architecture, Package, PackageBody
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import NewLine, InterfaceListStyle, AssociationListStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                        PortSimpleSignalInterfaceItem, ParameterConstantInterfaceItem, \
                                        ParameterVariableInterfaceItem
from pyVHDLModel.Name            import SimpleName, SelectedName, AllName, ParenthesisName
from pyVHDLModel.Object          import Signal
from pyVHDLModel.Sequential      import NullStatement, ReturnStatement
from pyVHDLModel.Subprogram      import Procedure, Function
from pyVHDLModel.Symbol          import ComponentInstantiationSymbol, IndexedObjectOrFunctionCallSymbol, EntitySymbol, \
                                        PackageSymbol, AllPackageMembersReferenceSymbol

from tests.unit                  import _subtypeSymbol
from tests.unit.Writer           import _GHDL, _analyze, _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


_INTERFACES_ONE_LINE =   InterfaceListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove)    #: On one line.
_ASSOCIATIONS_ONE_LINE = AssociationListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove)  #: On one line.


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


def _parameters() -> list:
	"""A constant and a variable parameter."""
	return [
		ParameterConstantInterfaceItem(["a"], Mode.In, _subtypeSymbol("integer")),
		ParameterVariableInterfaceItem(["b"], Mode.Out, _subtypeSymbol("integer"))
	]


def _instantiation() -> ComponentInstantiation:
	"""Component instantiation with a generic map and a port map."""
	return ComponentInstantiation(
		"u1",
		ComponentInstantiationSymbol(SimpleName("counter")),
		[GenericAssociationItem(SimpleName("BITS"), IntegerLiteral(8))],
		[PortAssociationItem(SimpleName("clk"), _object("clock")), PortAssociationItem(SimpleName("q"), _object("count"))]
	)


def _call(name: str, *actuals: str) -> IndexedObjectOrFunctionCallSymbol:
	"""Function call with positional actuals."""
	return IndexedObjectOrFunctionCallSymbol(ParenthesisName(
		SimpleName(name),
		[ParameterAssociationItem(None, _object(actual)) for actual in actuals]
	))


class InterfaceLists(Testcase):
	def test_PerConstruct(self) -> None:
		"""The generic clause and the port clause of one component have their own layout."""
		style = VHDLStyle(genericClause=_INTERFACES_ONE_LINE)

		self.assertEqual(dedent("""\
			component counter is
			  generic (BITS : positive := 8; type T);
			  port (
			    clk, rst : in bit;
			    q : out T
			  );
			end component counter;
			"""), VHDLWriter(style).Format(_component()))


class AssociationLists(Testcase):
	def test_PerConstruct(self) -> None:
		"""The generic map and the port map of one instantiation have their own layout."""
		style = VHDLStyle(genericMap=_ASSOCIATIONS_ONE_LINE)

		self.assertEqual(dedent("""\
			u1 : component counter
			  generic map (BITS => 8)
			  port map (
			    clk => clock,
			    q => count
			  );
			"""), VHDLWriter(style).Format(_instantiation()))

	def test_LeadingComma(self) -> None:
		style = VHDLStyle(portMap=AssociationListStyle(NewLine.Remove, NewLine.Add))

		self.assertEqual(dedent("""\
			u1 : component counter
			  generic map (
			    BITS => 8
			  )
			  port map (clk => clock
			    , q => count
			  );
			"""), VHDLWriter(style).Format(_instantiation()))

	def test_ProcedureCall(self) -> None:
		call = ConcurrentProcedureCall(None, _object("check"), [
			ParameterAssociationItem(None, _object("clk")),
			ParameterAssociationItem(SimpleName("limit"), IntegerLiteral(4))
		])

		self.assertEqual(dedent("""\
			check(
			  clk,
			  limit => 4
			);
			"""), VHDLWriter(VHDLStyle(procedureCall=AssociationListStyle())).Format(call))


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracle(Testcase):
	def test_Layouts(self) -> None:
		"""Each layout of all lists is analyzed by GHDL."""
		def work(name: str) -> SelectedName:
			"""Nested function returning the name of a design unit in library ``work``."""
			return SelectedName(name, SimpleName("work"))

		def generics() -> list:
			"""Nested function returning the generics of entity and component ``sub``."""
			return [GenericConstantInterfaceItem(["BITS"], Mode.Default, _subtypeSymbol("positive"), IntegerLiteral(8))]

		def ports() -> list:
			"""Nested function returning the ports of entity and component ``sub``."""
			return [
				PortSimpleSignalInterfaceItem(["clock"], Mode.In, _subtypeSymbol("bit")),
				PortSimpleSignalInterfaceItem(["count"], Mode.Out, _subtypeSymbol("integer"))
			]

		def parameters() -> list:
			"""Nested function returning the parameters of function ``f``."""
			return [ParameterConstantInterfaceItem(["a", "b"], Mode.In, _subtypeSymbol("integer"))]

		def maximum() -> Function:
			"""Nested function returning the generic function ``maximum``."""
			return Function(
				"maximum",
				_subtypeSymbol("T"),
				genericItems=[GenericTypeInterfaceItem("T")],
				parameterItems=[ParameterConstantInterfaceItem(["a", "b"], Mode.Default, _subtypeSymbol("T"))],
				statements=[ReturnStatement(_object("a"))]
			)

		designUnits = (
			Package("utilities", declaredItems=[
				Function("f", _subtypeSymbol("integer"), parameterItems=parameters()),
				Procedure("check", parameterItems=[ParameterConstantInterfaceItem(["a"], Mode.In, _subtypeSymbol("integer"))])
			]),
			PackageBody(PackageSymbol(SimpleName("utilities")), declaredItems=[
				Function(
					"f",
					_subtypeSymbol("integer"),
					parameterItems=parameters(),
					statements=[ReturnStatement(_object("a"))]
				),
				Procedure(
					"check",
					parameterItems=[ParameterConstantInterfaceItem(["a"], Mode.In, _subtypeSymbol("integer"))],
					statements=[NullStatement()]
				),
				maximum()
			]),
			Entity("sub", genericItems=generics(), portItems=ports()),
			Architecture("behav", EntitySymbol(SimpleName("sub"))),
			Entity("top"),
			Architecture(
				"rtl",
				EntitySymbol(SimpleName("top")),
				[UseClause([AllPackageMembersReferenceSymbol(AllName(work("utilities")))])],
				[
					Signal(["clock"], _subtypeSymbol("bit")),
					Signal(["count"], _subtypeSymbol("integer")),
					Component("sub", generics(), ports())
				],
				[
					ComponentInstantiation(
						"u1",
						ComponentInstantiationSymbol(SimpleName("sub")),
						[GenericAssociationItem(SimpleName("BITS"), IntegerLiteral(8))],
						[
							PortAssociationItem(SimpleName("clock"), _object("clock")),
							PortAssociationItem(SimpleName("count"), _object("count"))
						]
					),
					ConcurrentProcedureCall(None, _object("check"), [
						ParameterAssociationItem(None, _call("f", "count", "count"))
					])
				]
			)
		)

		leadingInterfaces =   InterfaceListStyle(NewLine.Remove, NewLine.Add)
		leadingAssociations = AssociationListStyle(NewLine.Remove, NewLine.Add)
		for name, interfaces, associations in (
			("one line",          _INTERFACES_ONE_LINE, _ASSOCIATIONS_ONE_LINE),
			("leading separator", leadingInterfaces,    leadingAssociations)
		):
			with self.subTest(layout=name):
				style = VHDLStyle(
					genericClause=interfaces,
					portClause=interfaces,
					subprogramGenericClause=interfaces,
					parameterList=interfaces,
					genericMap=associations,
					portMap=associations,
					procedureCall=associations,
					functionCall=associations
				)
				document = Document(Path("oracle.vhdl"))
				for designUnit in designUnits:
					document._AddDesignUnit(designUnit)

				source = VHDLWriter(style).Format(document)

				result = _analyze(source)

				self.assertEqual(0, result.returncode, msg=source + result.stdout + result.stderr)
