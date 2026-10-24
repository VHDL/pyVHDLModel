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
"""Tests for the walk of subprograms, subprogram instantiations and protected types (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing         import Testcase

from pyVHDLModel.Association   import GenericAssociationItem
from pyVHDLModel.Base          import Mode
from pyVHDLModel.Expression    import IntegerLiteral
from pyVHDLModel.Instantiation import ProcedureInstantiation
from pyVHDLModel.Interface     import GenericTypeInterfaceItem, GenericFunctionInterfaceItem, \
                                      ParameterConstantInterfaceItem
from pyVHDLModel.Name          import SimpleName
from pyVHDLModel.Object        import Variable
from pyVHDLModel.Subprogram    import Procedure, Function
from pyVHDLModel.Symbol        import SimpleSubtypeSymbol, SubprogramReferenceSymbol
from pyVHDLModel.Type          import ProtectedType, ProtectedTypeBody

from tests.unit.Visitor        import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Subprograms(Testcase):
	def test_Procedure(self) -> None:
		"""The parameters are separated by semicolon events; the walk passes ``is`` and ``begin``."""
		first =     ParameterConstantInterfaceItem(["a"], Mode.In, SimpleSubtypeSymbol(SimpleName("integer")))
		second =    ParameterConstantInterfaceItem(["b"], Mode.In, SimpleSubtypeSymbol(SimpleName("integer")))
		variable =  Variable(["v"], SimpleSubtypeSymbol(SimpleName("integer")))
		procedure = Procedure("p", parameterItems=[first, second], declaredItems=[variable])
		recorder =  FullRecorder()

		procedure.Visit(recorder)

		self.assertEqual([
			"VisitProcedure",
			"VisitFormalParameterList",
			"VisitParameterConstantInterfaceItem", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"DepartParameterConstantInterfaceItem",
			"VisitInterfaceListSeparator",
			"VisitParameterConstantInterfaceItem", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"DepartParameterConstantInterfaceItem",
			"DepartFormalParameterList",
			"VisitIs",
			"VisitVariable", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "DepartVariable",
			"VisitBegin",
			"DepartProcedure",
		], [event[0] for event in recorder.Events])

	def test_Procedure_Declaration(self) -> None:
		"""A procedure without parameters walks no parameter list, but ``is`` and ``begin``."""
		procedure = Procedure("reset")
		recorder =  FullRecorder()

		procedure.Visit(recorder)

		self.assertEqual([
			("VisitProcedure",  procedure),
			("VisitIs",         procedure),
			("VisitBegin",      procedure),
			("DepartProcedure", procedure),
		], recorder.Events)

	def test_Function(self) -> None:
		generic =    GenericTypeInterfaceItem("T")
		returnType = SimpleSubtypeSymbol(SimpleName("T"))
		function =   Function("f", returnType, genericItems=[generic])
		recorder =   FullRecorder()

		function.Visit(recorder)

		self.assertEqual([
			("VisitFunction",                  function),
			("VisitGenericClause",             function),
			("VisitGenericTypeInterfaceItem",  generic),
			("DepartGenericTypeInterfaceItem", generic),
			("DepartGenericClause",            function),
			("VisitReturn",                    function),
			("VisitSymbol",                    returnType),
			("VisitSimpleName",                returnType.Name),
			("DepartSimpleName",               returnType.Name),
			("DepartSymbol",                   returnType),
			("VisitIs",                        function),
			("VisitBegin",                     function),
			("DepartFunction",                 function),
		], recorder.Events)

	def test_GenericFunction(self) -> None:
		"""A generic function walks no declarative or statement part."""
		returnType = SimpleSubtypeSymbol(SimpleName("boolean"))
		function =   GenericFunctionInterfaceItem("compare", returnType)
		recorder =   FullRecorder()

		function.Visit(recorder)

		self.assertEqual(
			["VisitGenericFunctionInterfaceItem", "VisitReturn", "VisitSymbol", "VisitSimpleName", "DepartSimpleName",
			 "DepartSymbol", "DepartGenericFunctionInterfaceItem"],
			[event[0] for event in recorder.Events]
		)


class Instantiations(Testcase):
	def test_Procedure(self) -> None:
		reference =     SubprogramReferenceSymbol(SimpleName("log"))
		first =         GenericAssociationItem(SimpleName("N"), IntegerLiteral(8))
		second =        GenericAssociationItem(SimpleName("M"), IntegerLiteral(4))
		instantiation = ProcedureInstantiation("log_byte", reference, [first, second])
		recorder =      FullRecorder()

		instantiation.Visit(recorder)

		self.assertEqual([
			"VisitProcedureInstantiation",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitGenericMapAspect",
			"VisitAssociationItem", "VisitSimpleName", "DepartSimpleName", "VisitArrow", "VisitIntegerLiteral",
			"DepartIntegerLiteral", "DepartAssociationItem",
			"VisitAssociationListSeparator",
			"VisitAssociationItem", "VisitSimpleName", "DepartSimpleName", "VisitArrow", "VisitIntegerLiteral",
			"DepartIntegerLiteral", "DepartAssociationItem",
			"DepartGenericMapAspect",
			"DepartProcedureInstantiation",
		], [event[0] for event in recorder.Events])


class ProtectedTypes(Testcase):
	def test_Declaration(self) -> None:
		method =        Procedure("increment")
		protectedType = ProtectedType("counter", [method])
		recorder =      FullRecorder()

		protectedType.Visit(recorder)

		self.assertEqual([
			("VisitProtectedType",  protectedType),
			("VisitProcedure",      method),
			("VisitIs",             method),
			("VisitBegin",          method),
			("DepartProcedure",     method),
			("DepartProtectedType", protectedType),
		], recorder.Events)

	def test_Body(self) -> None:
		variable = Variable(["count"], SimpleSubtypeSymbol(SimpleName("natural")))
		body =     ProtectedTypeBody("counter", [variable])
		recorder = FullRecorder()

		body.Visit(recorder)

		self.assertEqual(
			["VisitProtectedTypeBody", "VisitVariable", "VisitSymbol", "VisitSimpleName", "DepartSimpleName",
			 "DepartSymbol", "DepartVariable", "DepartProtectedTypeBody"],
			[event[0] for event in recorder.Events]
		)
