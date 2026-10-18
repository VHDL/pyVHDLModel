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
"""
Indexing tests for declared items (``IndexDeclaredItems``).

Indexing clears what it fills, so indexing again yields the same lookup tables and namespace.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.DesignUnit import Architecture, Entity, Package
from pyVHDLModel.Interface  import PortSimpleSignalInterfaceItem
from pyVHDLModel.Object     import Constant, DeferredConstant, Variable
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.Type       import ProtectedType

from tests.unit             import _entitySymbol, _signal, _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ConcurrentDeclaredItems(Testcase):
	def test_Reindex_Overloads(self) -> None:
		"""Indexing twice keeps one entry per overload (regression)."""
		overload1 = Function("f", _subtypeSymbol("integer"))
		overload2 = Function("f", _subtypeSymbol("boolean"))
		procedure = Procedure("p")
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[overload1, overload2, procedure])

		architecture.IndexDeclaredItems()
		architecture.IndexDeclaredItems()

		self.assertDictEqual({"f": [overload1, overload2]}, architecture.Functions)
		self.assertDictEqual({"p": [procedure]}, architecture.Procedures)

	def test_Reindex_StaleEntries(self) -> None:
		"""Indexing again drops entries of items no longer declared in the region."""
		signal = _signal("s", "bit")
		constant = Constant(["C"], _subtypeSymbol("natural"))
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[signal, constant])
		architecture.IndexDeclaredItems()

		architecture.DeclaredItems.remove(signal)
		architecture.IndexDeclaredItems()

		self.assertDictEqual({}, architecture.Signals)
		self.assertDictEqual({"c": constant}, architecture.Constants)
		self.assertDictEqual({"c": constant}, architecture._namespace._elements)

	def test_Reindex_InterfaceItems(self) -> None:
		"""Indexing again keeps the region's interface items in the namespace."""
		port = PortSimpleSignalInterfaceItem(["Clock"], Mode.In, _subtypeSymbol("std_logic"))
		signal = _signal("s", "bit")
		entity = Entity("e", portItems=[port], declaredItems=[signal])

		entity.IndexDeclaredItems()
		entity.IndexDeclaredItems()

		self.assertDictEqual({"clock": port, "s": signal}, entity._namespace._elements)

	def test_Reindex_ImportedItems(self) -> None:
		"""Indexing again keeps items imported into the namespace from elsewhere."""
		otherPackage = Package("other", declaredItems=[Constant(["BITS"], _subtypeSymbol("positive"))])
		imported = otherPackage.DeclaredItems[0]
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[_signal("s", "bit")])
		architecture._namespace._elements["bits"] = imported

		architecture.IndexDeclaredItems()

		self.assertIs(imported, architecture._namespace._elements["bits"])

	def test_Reindex_DeferredConstants(self) -> None:
		deferredConstant = DeferredConstant(["BITS"], _subtypeSymbol("positive"))
		package = Package("pkg", declaredItems=[deferredConstant])
		package.IndexDeclaredItems()

		package.DeclaredItems.remove(deferredConstant)
		package.IndexDeclaredItems()

		self.assertDictEqual({}, package.DeferredConstants)


class SequentialDeclaredItems(Testcase):
	def test_Reindex(self) -> None:
		variable = Variable(["v"], _subtypeSymbol("natural"))
		overload1 = Procedure("p")
		overload2 = Procedure("p")
		process = ProcessStatement("proc", declaredItems=[variable, overload1, overload2])
		process.IndexDeclaredItems()

		process.DeclaredItems.remove(variable)
		process.IndexDeclaredItems()

		self.assertDictEqual({}, process.Variables)
		self.assertDictEqual({"p": [overload1, overload2]}, process.Procedures)
		self.assertDictEqual({"p": overload2}, process._namespace._elements)


class ProtectedTypeDeclaredItems(Testcase):
	def test_Reindex(self) -> None:
		function = Function("get", _subtypeSymbol("integer"))
		procedure = Procedure("increment")
		protectedType = ProtectedType("counter", [function, procedure])
		protectedType.IndexDeclaredItems()

		protectedType.DeclaredItems.remove(procedure)
		protectedType.IndexDeclaredItems()

		self.assertDictEqual({"get": [function]}, protectedType.Functions)
		self.assertDictEqual({}, protectedType.Procedures)
		self.assertDictEqual({"get": function}, protectedType._namespace._elements)
