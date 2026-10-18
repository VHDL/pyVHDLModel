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
Interface items - generics, ports and parameters - resolved through their region's namespace.

An interface item shares the declarative region of the declarative part beside it. Verified against the
GHDL analyzer: ``port (g : in bit)`` beside ``generic (g : integer)``, ``signal x`` beside
``port (x : in bit)``, and a subprogram variable named like a parameter are each rejected with
"identifier already used for a declaration". So they go into the *same* namespace as the declared items,
not a separate one.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Concurrent import ConcurrentBlockStatement, ProcessStatement
from pyVHDLModel.DesignUnit import Architecture, Entity, Package
from pyVHDLModel.Interface  import (
	GenericConstantInterfaceItem,
	GenericTypeInterfaceItem,
	ParameterVariableInterfaceItem,
	PortSimpleSignalInterfaceItem,
)
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Object     import Signal
from pyVHDLModel.Subprogram import Procedure
from pyVHDLModel.Symbol     import EntitySymbol, SignalSymbol, SimpleSubtypeSymbol, VariableSymbol

from tests.unit             import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _port(*identifiers: str) -> PortSimpleSignalInterfaceItem:
	return PortSimpleSignalInterfaceItem(identifiers, Mode.In, _subtypeSymbol("natural"))


def _generic(*identifiers: str) -> GenericConstantInterfaceItem:
	return GenericConstantInterfaceItem(identifiers, Mode.In, _subtypeSymbol("natural"))


class EntityInterfaceItems(Testcase):
	def test_PortIsIndexedIntoTheEntityNamespace(self) -> None:
		port = _port("clk")
		entity = Entity("ent", portItems=[port])
		entity.IndexDeclaredItems()

		self.assertIs(port, entity._namespace.Elements()["clk"])

	def test_PortIsResolvable(self) -> None:
		"""A port signal interface item *is* a `Signal`, so `FindObject` resolves it."""
		port = _port("clk")
		entity = Entity("ent", portItems=[port])
		entity.IndexDeclaredItems()

		found = entity._namespace.FindObject(SignalSymbol(SimpleName("clk")))

		self.assertIs(port, found)
		self.assertIsInstance(found, Signal)

	def test_EveryIdentifierOfAMultiIdentifierPortIsIndexed(self) -> None:
		"""``port (clk, rst : in bit)`` is one item with two identifiers."""
		port = _port("clk", "rst")
		entity = Entity("ent", portItems=[port])
		entity.IndexDeclaredItems()

		self.assertIs(port, entity._namespace.Elements()["clk"])
		self.assertIs(port, entity._namespace.Elements()["rst"])

	def test_GenericIsIndexed(self) -> None:
		generic = _generic("width")
		entity = Entity("ent", genericItems=[generic])
		entity.IndexDeclaredItems()

		self.assertIs(generic, entity._namespace.Elements()["width"])

	def test_SingularGenericTypeIsIndexed(self) -> None:
		"""``generic (type T)`` is singularly named, unlike every other interface item."""
		genericType = GenericTypeInterfaceItem("T")
		entity = Entity("ent", genericItems=[genericType])
		entity.IndexDeclaredItems()

		self.assertIs(genericType, entity._namespace.Elements()["t"])

	def test_GenericsPortsAndDeclarationsShareOneNamespace(self) -> None:
		generic = _generic("width")
		port = _port("clk")
		signal = Signal(("internal", ), _subtypeSymbol("natural"))
		entity = Entity("ent", genericItems=[generic], portItems=[port], declaredItems=[signal])
		entity.IndexDeclaredItems()

		self.assertEqual({"width", "clk", "internal"}, set(entity._namespace.Elements().keys()))

	def test_PortIsVisibleInTheArchitecture(self) -> None:
		"""The whole point: a port name resolves from inside the architecture."""
		port = _port("clk")
		entity = Entity("ent", portItems=[port])
		entity.IndexDeclaredItems()

		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")))
		architecture._namespace.ParentNamespace = entity._namespace
		architecture.IndexDeclaredItems()

		self.assertIs(port, architecture._namespace.FindObject(SignalSymbol(SimpleName("clk"))))

	def test_PortIsVisibleInsideAProcess(self) -> None:
		port = _port("clk")
		entity = Entity("ent", portItems=[port])
		entity.IndexDeclaredItems()

		architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")))
		architecture._namespace.ParentNamespace = entity._namespace
		architecture.IndexDeclaredItems()

		process = ProcessStatement("proc")
		process.Parent = architecture

		self.assertIs(port, process.Namespace.FindObject(SignalSymbol(SimpleName("clk"))))


class PackageGenerics(Testcase):
	def test_GenericIsIndexed(self) -> None:
		"""A generic package (VHDL-2008) has generics but no ports."""
		generic = _generic("width")
		package = Package("gp", genericItems=[generic])
		package.IndexDeclaredItems()

		self.assertIs(generic, package._namespace.Elements()["width"])


class BlockPorts(Testcase):
	def test_PortIsIndexed(self) -> None:
		"""``ConcurrentBlockStatement`` hand-rolls its port list rather than using ``WithPortsMixin``."""
		port = _port("bp")
		block = ConcurrentBlockStatement("blk", portItems=[port])
		block.IndexDeclaredItems()

		self.assertIs(port, block._namespace.Elements()["bp"])


class SubprogramInterfaceItems(Testcase):
	"""
	``Subprogram`` can't inherit ``WithGenericsMixin``/``WithParametersMixin``:
	:mod:`pyVHDLModel.Interface` needs ``Procedure``/``Function`` as real base classes for its generic
	subprogram interface items, so :mod:`pyVHDLModel.Subprogram` may never import it. Indexing therefore
	reads the canonical field names, which covers hand-rolled and mixin-provided lists alike.
	"""

	def test_ParameterIsIndexed(self) -> None:
		parameter = ParameterVariableInterfaceItem(("p", ), Mode.In, _subtypeSymbol("natural"))
		procedure = Procedure("helper", parameterItems=[parameter])
		procedure.IndexDeclaredItems()

		self.assertIs(parameter, procedure.Namespace.Elements()["p"])
		self.assertIs(parameter, procedure.Namespace.FindObject(VariableSymbol(SimpleName("p"))))

	def test_EveryIdentifierOfAMultiIdentifierParameterIsIndexed(self) -> None:
		parameter = ParameterVariableInterfaceItem(("p", "q"), Mode.In, _subtypeSymbol("natural"))
		procedure = Procedure("helper", parameterItems=[parameter])
		procedure.IndexDeclaredItems()

		self.assertIs(parameter, procedure.Namespace.Elements()["p"])
		self.assertIs(parameter, procedure.Namespace.Elements()["q"])

	def test_GenericAndParameterShareTheNamespace(self) -> None:
		generic = _generic("g")
		parameter = ParameterVariableInterfaceItem(("p", ), Mode.In, _subtypeSymbol("natural"))
		procedure = Procedure("helper", genericItems=[generic], parameterItems=[parameter])
		procedure.IndexDeclaredItems()

		self.assertEqual({"g", "p"}, set(procedure.Namespace.Elements().keys()))
