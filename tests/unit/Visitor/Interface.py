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
"""Tests for the walk of interface items, components and mode views (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.DesignUnit import Component
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Interface  import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                   PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                   ParameterFileInterfaceItem, ModeViewDeclaration, SimpleModeViewElement, \
                                   CompositeModeViewElement
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ModeViewSymbol

from tests.unit.Visitor     import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class InterfaceItems(Testcase):
	def test_GenericConstant(self) -> None:
		subtype =  SimpleSubtypeSymbol(SimpleName("positive"))
		default =  IntegerLiteral(8)
		item =     GenericConstantInterfaceItem(["BITS"], Mode.Default, subtype, default)
		recorder = FullRecorder()

		item.Visit(recorder)

		self.assertEqual([
			("VisitGenericConstantInterfaceItem",  item),
			("VisitSymbol",                        subtype),
			("VisitSimpleName",                    subtype.Name),
			("DepartSimpleName",                   subtype.Name),
			("DepartSymbol",                       subtype),
			("VisitVariableAssignment",            item),
			("VisitIntegerLiteral",                default),
			("DepartIntegerLiteral",               default),
			("DepartGenericConstantInterfaceItem", item),
		], recorder.Events)

	def test_GenericType(self) -> None:
		item =     GenericTypeInterfaceItem("T")
		recorder = FullRecorder()

		item.Visit(recorder)

		self.assertEqual([
			("VisitGenericTypeInterfaceItem",  item),
			("DepartGenericTypeInterfaceItem", item),
		], recorder.Events)

	def test_PortView(self) -> None:
		view =     ModeViewSymbol(SimpleName("master"))
		item =     PortViewSignalInterfaceItem(["link"], view)
		recorder = FullRecorder()

		item.Visit(recorder)

		self.assertEqual([
			("VisitPortViewSignalInterfaceItem",  item),
			("VisitSymbol",                       view),
			("VisitSimpleName",                   view.Name),
			("DepartSimpleName",                  view.Name),
			("DepartSymbol",                      view),
			("DepartPortViewSignalInterfaceItem", item),
		], recorder.Events)

	def test_ParameterFile(self) -> None:
		item =     ParameterFileInterfaceItem(["input"], SimpleSubtypeSymbol(SimpleName("text")))
		recorder = FullRecorder()

		item.Visit(recorder)

		self.assertEqual(
			["VisitParameterFileInterfaceItem", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			 "DepartParameterFileInterfaceItem"],
			[event[0] for event in recorder.Events]
		)


class Components(Testcase):
	def test_Component(self) -> None:
		"""The interface items of a clause are separated by semicolon events."""
		generic =   GenericTypeInterfaceItem("T")
		clock =     PortSimpleSignalInterfaceItem(["clk"], Mode.In, SimpleSubtypeSymbol(SimpleName("bit")))
		output =    PortSimpleSignalInterfaceItem(["q"], Mode.Out, SimpleSubtypeSymbol(SimpleName("T")))
		component = Component("counter", [generic], [clock, output])
		recorder =  FullRecorder()

		component.Visit(recorder)

		self.assertEqual([
			("VisitComponent",                      component),
			("VisitGenericClause",                  component),
			("VisitGenericTypeInterfaceItem",       generic),
			("DepartGenericTypeInterfaceItem",      generic),
			("DepartGenericClause",                 component),
			("VisitPortClause",                     component),
			("VisitPortSimpleSignalInterfaceItem",  clock),
			("VisitSymbol",                         clock.Subtype),
			("VisitSimpleName",                     clock.Subtype.Name),
			("DepartSimpleName",                    clock.Subtype.Name),
			("DepartSymbol",                        clock.Subtype),
			("DepartPortSimpleSignalInterfaceItem", clock),
			("VisitSemicolon",                      component),
			("VisitPortSimpleSignalInterfaceItem",  output),
			("VisitSymbol",                         output.Subtype),
			("VisitSimpleName",                     output.Subtype.Name),
			("DepartSimpleName",                    output.Subtype.Name),
			("DepartSymbol",                        output.Subtype),
			("DepartPortSimpleSignalInterfaceItem", output),
			("DepartPortClause",                    component),
			("DepartComponent",                     component),
		], recorder.Events)

	def test_Empty(self) -> None:
		"""Without generics and ports, the walk reports no clause."""
		component = Component("empty")
		recorder =  FullRecorder()

		component.Visit(recorder)

		self.assertEqual([("VisitComponent", component), ("DepartComponent", component)], recorder.Events)


class ModeViews(Testcase):
	def test_ModeView(self) -> None:
		subtype =     SimpleSubtypeSymbol(SimpleName("bus_t"))
		simple =      SimpleModeViewElement(["valid"], Mode.Out)
		view =        ModeViewSymbol(SimpleName("request_master"))
		composite =   CompositeModeViewElement(["request"], view)
		declaration = ModeViewDeclaration("master", subtype, [simple, composite])
		recorder =    FullRecorder()

		declaration.Visit(recorder)

		self.assertEqual([
			("VisitModeViewDeclaration",       declaration),
			("VisitSymbol",                    subtype),
			("VisitSimpleName",                subtype.Name),
			("DepartSimpleName",               subtype.Name),
			("DepartSymbol",                   subtype),
			("VisitIs",                        declaration),
			("VisitSimpleModeViewElement",     simple),
			("DepartSimpleModeViewElement",    simple),
			("VisitCompositeModeViewElement",  composite),
			("VisitSymbol",                    view),
			("VisitSimpleName",                view.Name),
			("DepartSimpleName",               view.Name),
			("DepartSymbol",                   view),
			("DepartCompositeModeViewElement", composite),
			("DepartModeViewDeclaration",      declaration),
		], recorder.Events)
