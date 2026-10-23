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
Namespaces of *sequential* declaration regions: process statements and subprogram bodies.

VHDL's ``process_declarative_item`` and ``subprogram_declarative_item`` rules are identical, so both use
``SequentialDeclarationRegionMixin``. Unlike a concurrent region it can declare a **variable**, which is
the usual thing to hide an outer signal with.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Concurrent import ConcurrentBlockStatement, ProcessStatement
from pyVHDLModel.DesignUnit import Architecture
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Namespace  import ExtendedKeyError
from pyVHDLModel.Object     import Constant, Signal, Variable
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.Symbol     import EntitySymbol, PossibleReference, SignalSymbol, SimpleSubtypeSymbol, Symbol, \
                                   VariableSymbol
from pyVHDLModel.Type       import IntegerType

from tests.unit             import _signal, _subtypeSymbol, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _architecture(*declaredItems) -> Architecture:
	architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=list(declaredItems))
	architecture.IndexDeclaredItems()

	return architecture


class ProcessNamespaces(Testcase):
	def test_NamespaceIsNamedAfterTheLabel(self) -> None:
		process = ProcessStatement("proc")

		self.assertEqual("proc", process.Namespace.Name)

	def test_UnlabelledProcessHasAnUnnamedNamespace(self) -> None:
		process = ProcessStatement()

		self.assertIsNone(process.Namespace.Name)

	def test_IndexDeclaredItemsPopulatesVariables(self) -> None:
		"""A variable is exactly what a concurrent region can *not* declare."""
		variable = _variable("counter", "natural")
		process = ProcessStatement("proc", declaredItems=[variable])
		process.IndexDeclaredItems()

		self.assertIs(variable, process.Variables["counter"])
		self.assertIs(variable, process.Namespace.Elements()["counter"])

	def test_IndexDeclaredItemsPopulatesEveryKind(self) -> None:
		integerType = IntegerType("nibble", None)
		constant = Constant(("width", ), _subtypeSymbol("natural"))
		variable = _variable("index", "natural")
		nestedProcedure = Procedure("helper")

		process = ProcessStatement("proc", declaredItems=[integerType, constant, variable, nestedProcedure])
		process.IndexDeclaredItems()

		self.assertIs(integerType, process.Types["nibble"])
		self.assertIs(constant, process.Constants["width"])
		self.assertIs(variable, process.Variables["index"])
		self.assertIs(nestedProcedure, process.Procedures["helper"][0])
		self.assertEqual(4, len(process.Namespace.Elements()))

	def test_NamespaceNestsInsideTheArchitecture(self) -> None:
		architecture = _architecture()
		process = ProcessStatement("proc")
		process.Parent = architecture

		self.assertIs(architecture._namespace, process.Namespace.ParentNamespace)

	def test_ProcessVariableHidesArchitectureSignal(self) -> None:
		architectureSignal = _signal("x", "natural")
		architecture = _architecture(architectureSignal)

		processVariable = _variable("x", "natural")
		process = ProcessStatement("proc", declaredItems=[processVariable])
		process.Parent = architecture
		process.IndexDeclaredItems()

		self.assertIs(processVariable, process.Namespace.FindObject(VariableSymbol(SimpleName("x"))))
		# Hiding is one-directional.
		self.assertIs(architectureSignal, architecture._namespace.FindObject(SignalSymbol(SimpleName("x"))))

	def test_ProcessInheritsArchitectureDeclaration(self) -> None:
		architectureSignal = _signal("clk", "natural")
		architecture = _architecture(architectureSignal)

		process = ProcessStatement("proc")
		process.Parent = architecture

		self.assertIs(architectureSignal, process.Namespace.FindObject(SignalSymbol(SimpleName("clk"))))

	def test_ProcessInsideABlockNestsInsideTheBlock(self) -> None:
		architecture = _architecture()
		block = ConcurrentBlockStatement("blk")
		block.Parent = architecture
		block.IndexDeclaredItems()

		process = ProcessStatement("proc")
		process.Parent = block

		self.assertIs(block._namespace, process.Namespace.ParentNamespace)


class SubprogramNamespaces(Testcase):
	def test_NamespaceIsNamedAfterTheIdentifier(self) -> None:
		procedure = Procedure("DoIt")

		self.assertEqual("doit", procedure.Namespace.Name)

	def test_IndexDeclaredItemsPopulatesVariables(self) -> None:
		variable = _variable("temp", "natural")
		function = Function("compute", _subtypeSymbol("natural"), declaredItems=[variable])
		function.IndexDeclaredItems()

		self.assertIs(variable, function.Variables["temp"])
		self.assertIs(variable, function.Namespace.Elements()["temp"])

	def test_NamespaceNestsInsideTheArchitecture(self) -> None:
		architecture = _architecture()
		procedure = Procedure("helper")
		procedure.Parent = architecture

		self.assertIs(architecture._namespace, procedure.Namespace.ParentNamespace)

	def test_SubprogramVariableHidesArchitectureSignal(self) -> None:
		architectureSignal = _signal("x", "natural")
		architecture = _architecture(architectureSignal)

		subprogramVariable = _variable("x", "natural")
		procedure = Procedure("helper", declaredItems=[subprogramVariable])
		procedure.Parent = architecture
		procedure.IndexDeclaredItems()

		self.assertIs(subprogramVariable, procedure.Namespace.FindObject(VariableSymbol(SimpleName("x"))))
		self.assertIs(architectureSignal, architecture._namespace.FindObject(SignalSymbol(SimpleName("x"))))

	def test_SubprogramInheritsArchitectureDeclaration(self) -> None:
		constant = Constant(("width", ), _subtypeSymbol("natural"))
		architecture = _architecture(constant)

		procedure = Procedure("helper")
		procedure.Parent = architecture

		symbol = Symbol(SimpleName("width"), PossibleReference.Constant)

		self.assertIs(constant, procedure.Namespace.FindObject(symbol))

	def test_NestedSubprogramNestsInsideTheOuterSubprogram(self) -> None:
		"""A subprogram is itself a sequential declaration region, so subprograms nest."""
		outerVariable = _variable("outer", "natural")
		inner = Procedure("inner")
		outer = Procedure("outer", declaredItems=[outerVariable, inner])
		outer.IndexDeclaredItems()

		self.assertIs(outer._namespace, inner.Namespace.ParentNamespace)
		self.assertIs(outerVariable, inner.Namespace.FindObject(VariableSymbol(SimpleName("outer"))))

	def test_NestedSubprogramVariableHidesTheOuterOne(self) -> None:
		outerVariable = _variable("x", "natural")
		innerVariable = _variable("x", "natural")
		inner = Procedure("inner", declaredItems=[innerVariable])
		outer = Procedure("outer", declaredItems=[outerVariable, inner])
		outer.IndexDeclaredItems()
		inner.IndexDeclaredItems()

		self.assertIs(innerVariable, inner.Namespace.FindObject(VariableSymbol(SimpleName("x"))))
		self.assertIs(outerVariable, outer.Namespace.FindObject(VariableSymbol(SimpleName("x"))))

	def test_UnresolvedNameReportsTheWholeChain(self) -> None:
		architecture = _architecture()
		procedure = Procedure("helper")
		procedure.Parent = architecture
		process = ProcessStatement("proc")
		process.Parent = architecture

		with self.assertRaises(ExtendedKeyError) as context:
			procedure.Namespace.FindObject(VariableSymbol(SimpleName("missing")))

		# The subprogram's namespace and the architecture's are both reported as searched.
		self.assertEqual(2, len(context.exception.searchedNamespaces))
		self.assertIn("helper, rtl", str(context.exception))
