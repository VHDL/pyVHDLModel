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
Mutation tests for identifier clashes within a declarative region.

An identifier is declared once per declarative region: interface items and declared items count, and an entity and its
architecture form one region, as do a package and its body. A mutator checks all clashes before it writes anything, so
after the error the lists, the parent, the lookup tables and the namespace are unchanged.
"""
from pathlib                import Path
from typing                 import Any, Dict

from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document, Library
from pyVHDLModel.DesignUnit import Architecture, Component, Entity, Package, PackageBody
from pyVHDLModel.Exception  import DuplicateConstantError, DuplicateSignalError, DuplicateVariableError
from pyVHDLModel.Exception  import DuplicateGenericError, DuplicatePortError, DuplicateParameterError
from pyVHDLModel.Interface  import GenericFunctionInterfaceItem
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Object     import DeferredConstant
from pyVHDLModel.Symbol     import PackageSymbol
from pyVHDLModel.Type       import ProtectedType, ProtectedTypeBody

from tests.unit             import _entitySymbol, _subtypeSymbol
from tests.unit.Mutation    import _constant, _function, _generic, _parameter, _port, _reindexed, _signal, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


_FIELDS = (
	"_declaredItems", "_genericItems", "_portItems", "_parameterItems", "_types", "_subtypes", "_constants", "_signals",
	"_variables", "_sharedVariables", "_files", "_functions", "_procedures", "_components", "_deferredConstants"
)


def _snapshot(region) -> Dict[str, Any]:
	"""Copy the lists, lookup tables and namespace of a declarative region."""
	snapshot = {"namespace": dict(region._namespace._elements)}
	for field in _FIELDS:
		value = getattr(region, field, None)
		if isinstance(value, list):
			snapshot[field] = list(value)
		elif isinstance(value, dict):
			snapshot[field] = {key: list(entry) if isinstance(entry, list) else entry for key, entry in value.items()}

	return snapshot


def _link(entity: Entity, architecture: Architecture, package: Package, packageBody: PackageBody) -> None:
	"""Link an architecture to its entity and a package body to its package, then index all four."""
	design = Design()
	library = Library("work")
	design.AddLibrary(library)
	document = Document(Path("virtual.vhdl"))
	document._AddDesignUnit(entity)
	document._AddDesignUnit(architecture)
	document._AddDesignUnit(package)
	document._AddDesignUnit(packageBody)
	design.AddDocument(document, library)
	design.CreateDependencyGraph()
	design.LinkArchitectures()
	design.LinkPackageBodies()

	entity.IndexDeclaredItems()
	architecture.IndexDeclaredItems()
	package.IndexDeclaredItems()
	packageBody.IndexDeclaredItems()


def _architecture(*declaredItems) -> Architecture:
	return Architecture("rtl", _entitySymbol("ent"), declaredItems=declaredItems)


def _packageBody(*declaredItems) -> PackageBody:
	return PackageBody(PackageSymbol(SimpleName("pkg")), declaredItems=declaredItems)


class DeclaredItemVsInterfaceItems(Testcase):
	def test_Port(self) -> None:
		entity = Entity("ent", portItems=[_port("x")])
		entity.IndexDeclaredItems()
		before = _snapshot(entity)
		signal = _signal("X")

		with self.assertRaises(DuplicateSignalError) as context:
			entity.AddDeclaredItem(signal)

		self.assertEqual("Entity already declares 'X'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertDictEqual(before, _snapshot(entity))
		self.assertIsNone(signal.Parent)

	def test_Generic(self) -> None:
		package = Package("pkg", genericItems=[_generic("BITS")])
		package.IndexDeclaredItems()
		before = _snapshot(package)
		constant = _constant("bits")

		with self.assertRaises(DuplicateConstantError) as context:
			package.AddDeclaredItem(constant)

		self.assertEqual("Package already declares 'bits'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(package))
		self.assertIsNone(constant.Parent)

	def test_Parameter(self) -> None:
		function = _function("f")
		function.AddParameterItem(_parameter("a"))
		function.IndexDeclaredItems()
		before = _snapshot(function)
		variable = _variable("A")

		with self.assertRaises(DuplicateVariableError) as context:
			function.AddDeclaredItem(variable)

		self.assertEqual("Function already declares 'A'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(function))
		self.assertIsNone(variable.Parent)

	def test_GenericFunction(self) -> None:
		"""A declared function overloads a generic function."""
		genericFunction = GenericFunctionInterfaceItem("f", _subtypeSymbol("integer"))
		entity = Entity("ent", genericItems=[genericFunction])
		entity.IndexDeclaredItems()
		function = _function("f")

		entity.AddDeclaredItem(function)

		self.assertDictEqual({"f": [function]}, entity.Functions)
		self.assertIs(function, entity._namespace._elements["f"])


class DeclaredItemVsSharedRegion(Testcase):
	def test_Architecture_EntityPort(self) -> None:
		entity = Entity("ent", portItems=[_port("p")])
		architecture = _architecture()
		_link(entity, architecture, Package("pkg"), _packageBody())
		before = _snapshot(architecture)
		signal = _signal("p")

		with self.assertRaises(DuplicateSignalError) as context:
			architecture.AddDeclaredItem(signal)

		self.assertEqual("Entity already declares 'p'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(architecture))
		self.assertIsNone(signal.Parent)

	def test_Architecture_EntityDeclaration(self) -> None:
		entity = Entity("ent", declaredItems=[_signal("x")])
		architecture = _architecture()
		_link(entity, architecture, Package("pkg"), _packageBody())
		before = _snapshot(architecture)

		with self.assertRaises(DuplicateConstantError) as context:
			architecture.AddDeclaredItem(_constant("x"))

		self.assertEqual("Entity already declares 'x'.", str(context.exception))
		self.assertListEqual(["Existing declaration is of type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)
		self.assertDictEqual(before, _snapshot(architecture))

	def test_Entity_ArchitectureDeclaration(self) -> None:
		entity = Entity("ent")
		architecture = _architecture(_signal("x"))
		_link(entity, architecture, Package("pkg"), _packageBody())
		before = _snapshot(entity)

		with self.assertRaises(DuplicateSignalError) as context:
			entity.AddDeclaredItem(_signal("x"))

		self.assertEqual("Architecture already declares 'x'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(entity))

	def test_PackageBody_PackageDeclaration(self) -> None:
		package = Package("pkg", declaredItems=[_constant("c")])
		packageBody = _packageBody()
		_link(Entity("ent"), _architecture(), package, packageBody)
		before = _snapshot(packageBody)

		with self.assertRaises(DuplicateConstantError) as context:
			packageBody.AddDeclaredItem(_constant("C"))

		self.assertEqual("Package already declares 'C'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(packageBody))

	def test_Package_PackageBodyDeclaration(self) -> None:
		package = Package("pkg")
		packageBody = _packageBody(_constant("c"))
		_link(Entity("ent"), _architecture(), package, packageBody)
		before = _snapshot(package)

		with self.assertRaises(DuplicateConstantError) as context:
			package.AddDeclaredItem(_constant("c"))

		self.assertEqual("PackageBody already declares 'c'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(package))

	def test_PackageBody_DeferredConstant(self) -> None:
		"""A constant in the package body completes the deferred constant of its package."""
		package = Package("pkg", declaredItems=[DeferredConstant(["c"], _subtypeSymbol("natural"))])
		packageBody = _packageBody()
		_link(Entity("ent"), _architecture(), package, packageBody)
		constant = _constant("c")

		packageBody.AddDeclaredItem(constant)

		self.assertDictEqual({"c": constant}, packageBody.Constants)
		self.assertIs(constant, packageBody._namespace._elements["c"])

	def test_PackageBody_ProtectedTypeBody(self) -> None:
		protectedType = ProtectedType("counter")
		package = Package("pkg", declaredItems=[protectedType])
		packageBody = _packageBody()
		_link(Entity("ent"), _architecture(), package, packageBody)
		protectedTypeBody = ProtectedTypeBody("counter")

		packageBody.AddDeclaredItem(protectedTypeBody)

		self.assertListEqual([protectedTypeBody], packageBody.DeclaredItems)
		self.assertDictEqual({"counter": protectedType}, package.Types)

	def test_Architecture_Overload(self) -> None:
		"""A function in the architecture overloads a function of its entity."""
		entity = Entity("ent", declaredItems=[_function("f")])
		architecture = _architecture()
		_link(entity, architecture, Package("pkg"), _packageBody())
		function = _function("f")

		architecture.AddDeclaredItem(function)

		self.assertDictEqual({"f": [function]}, architecture.Functions)

	def test_Architecture_NotLinked(self) -> None:
		"""An architecture not linked to its entity doesn't know the entity's declarations."""
		Entity("ent", portItems=[_port("p")])
		architecture = _architecture()
		signal = _signal("p")

		architecture.AddDeclaredItem(signal)

		self.assertListEqual([signal], architecture.DeclaredItems)


class InterfaceItemVsDeclarations(Testcase):
	def test_Generic_DeclaredItem(self) -> None:
		entity = Entity("ent", declaredItems=[_signal("G")])
		entity.IndexDeclaredItems()
		before = _snapshot(entity)
		generic = _generic("g")

		with self.assertRaises(DuplicateGenericError) as context:
			entity.AddGenericItem(generic)

		self.assertEqual("Entity already declares 'g'.", str(context.exception))
		self.assertListEqual(["Existing declaration is of type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)
		self.assertDictEqual(before, _snapshot(entity))
		self.assertIsNone(generic.Parent)

	def test_Port_Generic(self) -> None:
		entity = Entity("ent", genericItems=[_generic("x")])
		entity.IndexDeclaredItems()
		before = _snapshot(entity)
		port = _port("x")

		with self.assertRaises(DuplicatePortError) as context:
			entity.AddPortItem(port)

		self.assertEqual("Entity already declares 'x'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertDictEqual(before, _snapshot(entity))
		self.assertIsNone(port.Parent)

	def test_Port_ArchitectureDeclaration(self) -> None:
		entity = Entity("ent")
		architecture = _architecture(_signal("x"))
		_link(entity, architecture, Package("pkg"), _packageBody())
		before = _snapshot(entity)

		with self.assertRaises(DuplicatePortError) as context:
			entity.AddPortItem(_port("x"))

		self.assertEqual("Architecture already declares 'x'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(entity))

	def test_Generic_PackageBodyDeclaration(self) -> None:
		package = Package("pkg")
		packageBody = _packageBody(_constant("BITS"))
		_link(Entity("ent"), _architecture(), package, packageBody)
		before = _snapshot(package)

		with self.assertRaises(DuplicateGenericError) as context:
			package.AddGenericItem(_generic("bits"))

		self.assertEqual("PackageBody already declares 'bits'.", str(context.exception))
		self.assertDictEqual(before, _snapshot(package))

	def test_Parameter_DeclaredItem(self) -> None:
		function = _function("f")
		function.AddDeclaredItem(_variable("a"))
		before = _snapshot(function)
		parameter = _parameter("A")

		with self.assertRaises(DuplicateParameterError) as context:
			function.AddParameterItem(parameter)

		self.assertEqual("Function already declares 'A'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Object.Variable'."],
			context.exception.__notes__
		)
		self.assertDictEqual(before, _snapshot(function))
		self.assertIsNone(parameter.Parent)

	def test_Component_PortVsGeneric(self) -> None:
		"""A component's generics and ports share one declarative region."""
		component = Component("comp", genericItems=[_generic("x")])
		port = _port("X")

		with self.assertRaises(DuplicatePortError) as context:
			component.AddPortItem(port)

		self.assertEqual("Component already declares 'X'.", str(context.exception))
		self.assertListEqual([], component.PortItems)
		self.assertIsNone(port.Parent)

	def test_GenericFunction_DeclaredFunction(self) -> None:
		"""A generic function overloads a declared function; the namespace refers to the declared one, as after indexing."""
		function = _function("f")
		entity = Entity("ent", declaredItems=[function])
		entity.IndexDeclaredItems()
		genericFunction = GenericFunctionInterfaceItem("f", _subtypeSymbol("integer"))

		entity.AddGenericItem(genericFunction)

		self.assertListEqual([genericFunction], entity.GenericItems)
		self.assertIs(function, entity._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(entity))

	def test_GenericFunction_Remove(self) -> None:
		"""Removing a generic function overloaded by a declared function leaves the namespace entry of the declared one."""
		genericFunction = GenericFunctionInterfaceItem("f", _subtypeSymbol("integer"))
		function = _function("f")
		entity = Entity("ent", genericItems=[genericFunction], declaredItems=[function])
		entity.IndexDeclaredItems()

		entity.RemoveGenericItem(genericFunction)

		self.assertIs(function, entity._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(entity))

	def test_DeclaredFunction_Remove(self) -> None:
		"""Removing a declared function overloading a generic function re-points the namespace entry to the generic one."""
		genericFunction = GenericFunctionInterfaceItem("f", _subtypeSymbol("integer"))
		function = _function("f")
		entity = Entity("ent", genericItems=[genericFunction], declaredItems=[function])
		entity.IndexDeclaredItems()

		entity.RemoveDeclaredItem(function)

		self.assertIs(genericFunction, entity._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(entity))


class ImportedItems(Testcase):
	"""An item imported into the namespace (e.g. by a use clause) is hidden by a declaration."""

	def test_DeclaredItem(self) -> None:
		imported = _constant("BITS")
		Package("other", declaredItems=[imported])
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		architecture._namespace._elements["bits"] = imported
		constant = _constant("BITS")

		architecture.AddDeclaredItem(constant)

		self.assertIs(constant, architecture._namespace._elements["bits"])

	def test_DeclaredItem_SharedRegion(self) -> None:
		"""An item imported into the entity's namespace is hidden by a declaration in the architecture."""
		imported = _constant("BITS")
		Package("other", declaredItems=[imported])
		entity = Entity("ent")
		architecture = _architecture()
		_link(entity, architecture, Package("pkg"), _packageBody())
		entity._namespace._elements["bits"] = imported
		constant = _constant("BITS")

		architecture.AddDeclaredItem(constant)

		self.assertIs(constant, architecture._namespace._elements["bits"])

	def test_Port(self) -> None:
		imported = _signal("clock")
		Package("other", declaredItems=[imported])
		entity = Entity("ent")
		entity.IndexDeclaredItems()
		entity._namespace._elements["clock"] = imported
		port = _port("Clock")

		entity.AddPortItem(port)

		self.assertIs(port, entity._namespace._elements["clock"])
