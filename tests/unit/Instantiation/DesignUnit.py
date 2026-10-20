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
Tests for pyVHDLModel.DesignUnit and pyVHDLModel.Regions.

``ConcurrentDeclarationRegionMixin`` (Regions.py) is shared by ``Package``, ``PackageBody``,
``Entity``, ``Architecture`` and (via Common.py/Concurrent.py, tested in their own slice)
``ConcurrentBlockStatement`` and the generate-statement branches. Its actual indexing behaviour is
tested once here via ``Architecture`` as the canonical host; every other consumer below gets only a
one-line smoke test confirming the mixin is wired up.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel            import VHDLModelException
from pyVHDLModel.Exception  import BlackboxWarning
from pyVHDLModel.Base       import ModelEntity
from pyVHDLModel.Name       import SimpleName, SelectedName
from pyVHDLModel.Symbol     import EntitySymbol, PackageSymbol, LibraryReferenceSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Object     import Constant, Signal, Variable, SharedVariable, File, DeferredConstant
from pyVHDLModel.Type       import FullType, Subtype
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.DesignUnit import (
	Reference, LibraryClause, UseClause, ContextReference,
	DesignUnit, PrimaryUnit, SecondaryUnit, Context,
	Package, PackageBody, Entity, Architecture, Component, Configuration,
)

from tests.unit             import _entitySymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class References(Testcase):
	def test_LibraryClause(self) -> None:
		symbol = LibraryReferenceSymbol(SimpleName("ieee"))
		clause = LibraryClause([symbol])

		self.assertEqual(1, len(clause.Symbols))
		self.assertIs(symbol, clause.Symbols[0])

	def test_UseClause(self) -> None:
		"""``UseClause``/``ContextReference`` add no behaviour of their own over the generic
		``Reference`` base - only ``LibraryClause`` overrides ``Symbols``' type hint."""
		clause = UseClause([])

		self.assertIsInstance(clause, Reference)

	def test_ContextReference(self) -> None:
		reference = ContextReference([])

		self.assertIsInstance(reference, Reference)


class _ConcreteDesignUnit(DesignUnit):
	"""``DesignUnit`` is abstract - it requires ``__str__`` - so its own plumbing is exercised through a
	stand-in that adds nothing but the required rendering. Using a real unit like ``Context`` instead
	would drag in that unit's extra state."""

	def __str__(self) -> str:
		return self._identifier


class _ConcretePrimaryUnit(PrimaryUnit):
	def __str__(self) -> str:
		return self._identifier


class _ConcreteSecondaryUnit(SecondaryUnit):
	def __str__(self) -> str:
		return self._identifier


class DesignUnits(Testcase):

	def test_NoContextItems(self) -> None:
		unit = _ConcreteDesignUnit("u")

		self.assertEqual("u", unit.Identifier)
		self.assertEqual(0, len(unit.ContextItems))
		self.assertEqual(0, len(unit.LibraryReferences))
		self.assertEqual(0, len(unit.PackageReferences))
		self.assertEqual(0, len(unit.ContextReferences))
		self.assertIsNone(unit.Document)
		self.assertIsNone(unit.DependencyVertex)
		self.assertIsNone(unit.HierarchyVertex)

	def test_ContextItemsAreSeparatedByKind(self) -> None:
		library = LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])
		use = UseClause([])
		context = ContextReference([])
		unit = _ConcreteDesignUnit("u", [library, use, context])

		self.assertEqual(3, len(unit.ContextItems))
		self.assertEqual([library], unit.LibraryReferences)
		self.assertEqual([use], unit.PackageReferences)
		self.assertEqual([context], unit.ContextReferences)

	def test_DocumentSetter(self) -> None:
		unit = _ConcreteDesignUnit("u")
		document = object()
		unit.Document = document

		self.assertIs(document, unit.Document)

	def test_LibrarySetter(self) -> None:
		"""``Library`` is just a renamed view onto the same ``_parent`` field every ``ModelEntity``
		has."""
		unit = _ConcreteDesignUnit("u")
		library = ModelEntity()
		unit.Library = library

		self.assertIs(library, unit.Library)
		self.assertIs(library, unit.Parent)


class MarkerSubclasses(Testcase):
	def test_PrimaryUnit(self) -> None:
		unit = _ConcretePrimaryUnit("u")

		self.assertEqual("u", unit.Identifier)

	def test_SecondaryUnit(self) -> None:
		unit = _ConcreteSecondaryUnit("u")

		self.assertEqual("u", unit.Identifier)


class Contexts(Testcase):
	def test_NoReferences(self) -> None:
		context = Context("ctx")

		self.assertEqual(0, len(context.LibraryReferences))
		self.assertEqual(0, len(context.PackageReferences))
		self.assertEqual(0, len(context.ContextReferences))

	def test_ReferencesAreSeparatedByKind(self) -> None:
		library = LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))])
		use = UseClause([])
		contextReference = ContextReference([])
		context = Context("ctx", [library, use, contextReference])

		self.assertEqual([library], context.LibraryReferences)
		self.assertEqual([use], context.PackageReferences)
		self.assertEqual([contextReference], context.ContextReferences)
		self.assertIs(context, library.Parent)

	def test_UnknownReferenceKind_Raises(self) -> None:
		"""Regression test: ``VHDLModelException()`` previously carried no message at all (``# FIXME:
		needs exception message`` in the source) - now includes the offending reference. Uses a bare
		``ModelEntity`` (not ``object()``) since the ``.Parent = self`` assignment a few lines above
		the kind-check runs first and needs a real settable ``Parent``."""
		with self.assertRaises(VHDLModelException) as context:
			Context("ctx", [ModelEntity()])

		self.assertIn("neither a library clause, use clause, nor context reference", str(context.exception))


class Packages(Testcase):
	def test_Minimal(self) -> None:
		package = Package("pkg")

		self.assertEqual(0, len(package.DeclaredItems))
		self.assertEqual(0, len(package.DeferredConstants))
		self.assertEqual(0, len(package.Components))
		self.assertIsNone(package.PackageBody)

	def test_IndexDeferredConstant(self) -> None:
		"""``Package`` overrides ``_IndexOtherDeclaredItem`` to additionally index deferred constants
		and components - not covered by the generic ``IndexDeclaredItems`` in Regions.py, so tested
		here specifically."""
		deferredConstant = DeferredConstant(["BITS"], SimpleSubtypeSymbol(SimpleName("positive")))
		package = Package("pkg", declaredItems=[deferredConstant])
		package.IndexDeclaredItems()

		self.assertIs(deferredConstant, package.DeferredConstants["bits"])

	def test_IndexComponent(self) -> None:
		component = Component("comp")
		package = Package("pkg", declaredItems=[component])
		package.IndexDeclaredItems()

		self.assertIs(component, package.Components["comp"])


class PackageBodies(Testcase):
	def test_Minimal(self) -> None:
		packageSymbol = PackageSymbol(SimpleName("pkg"))
		body = PackageBody(packageSymbol)

		self.assertIs(packageSymbol, body.Package)
		self.assertIs(body, packageSymbol.Parent)
		self.assertEqual(0, len(body.DeclaredItems))

	def test_LinkDeclaredItemsToPackage_IsANoOpStub(self) -> None:
		body = PackageBody(PackageSymbol(SimpleName("pkg")))

		self.assertIsNone(body.LinkDeclaredItemsToPackage())


class Entities(Testcase):
	def test_Minimal(self) -> None:
		entity = Entity("ent")

		self.assertEqual(0, len(entity.DeclaredItems))
		self.assertEqual(0, len(entity.Statements))
		self.assertEqual(0, len(entity.Architectures))


class Architectures(Testcase):
	def test_Minimal(self) -> None:
		entitySymbol = _entitySymbol("ent")
		architecture = Architecture("rtl", entitySymbol)

		self.assertIs(entitySymbol, architecture.Entity)
		self.assertIs(architecture, entitySymbol.Parent)
		self.assertEqual(0, len(architecture.DeclaredItems))
		self.assertEqual(0, len(architecture.Statements))

	def test_RegionStartsEmpty(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("ent"))

		self.assertEqual(0, len(architecture.Types))
		self.assertEqual(0, len(architecture.Subtypes))
		self.assertEqual(0, len(architecture.Constants))
		self.assertEqual(0, len(architecture.Signals))
		self.assertEqual(0, len(architecture.SharedVariables))
		self.assertEqual(0, len(architecture.Files))
		self.assertEqual(0, len(architecture.Functions))
		self.assertEqual(0, len(architecture.Procedures))
		self.assertEqual(0, len(architecture.Components))

	def test_IndexDeclaredItems(self) -> None:
		fullType = FullType("my_type")
		subtype = Subtype("my_subtype", SimpleSubtypeSymbol(SimpleName("bit")))
		constant = Constant(["C"], SimpleSubtypeSymbol(SimpleName("natural")))
		signal = Signal(["s"], SimpleSubtypeSymbol(SimpleName("bit")))
		sharedVariable = SharedVariable(["sv"], SimpleSubtypeSymbol(SimpleName("natural")))
		file = File(["f"], SimpleSubtypeSymbol(SimpleName("text")))
		function = Function("f_func", SimpleSubtypeSymbol(SimpleName("integer")))
		procedure = Procedure("p_proc")

		architecture = Architecture(
			"rtl", _entitySymbol("ent"),
			declaredItems=[fullType, subtype, constant, signal, sharedVariable, file, function, procedure],
		)
		architecture.IndexDeclaredItems()

		self.assertIs(fullType, architecture.Types["my_type"])
		self.assertIs(subtype, architecture.Subtypes["my_subtype"])
		self.assertIs(constant, architecture.Constants["c"])
		self.assertIs(signal, architecture.Signals["s"])
		self.assertIs(sharedVariable, architecture.SharedVariables["sv"])
		self.assertIs(file, architecture.Files["f"])
		self.assertEqual(1, len(architecture.Functions["f_func"]))
		self.assertIs(function, architecture.Functions["f_func"][0])
		self.assertEqual(1, len(architecture.Procedures["p_proc"]))
		self.assertIs(procedure, architecture.Procedures["p_proc"][0])

	def test_IndexDeclaredItems_VariablesAreNotYetIndexed(self) -> None:
		"""Still-open gap (documented in Regions.py's own TODO): variables declared directly in a
		concurrent declaration region raise a warning instead of being indexed anywhere - locked in as
		current behaviour, not a regression."""
		variable = Variable(["v"], SimpleSubtypeSymbol(SimpleName("natural")))
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[variable])

		architecture.IndexDeclaredItems()  # must not raise, only warn

	def test_IndexDeclaredItems_Overloads(self) -> None:
		"""Regression test: two overloads sharing a name used to silently collide into one entry (a
		flat ``dict[str, Function]``) - the second always overwrote the first, with no error or
		warning. Fixed by collecting overloads into a list per name instead.

		FIXME: this only *avoids the collision* - it doesn't actually resolve overloads by signature
		(matching call-site argument types against each candidate's parameter/return types). A real
		textual-signature-based attempt was tried and rejected as unreliable (aliased/case-differing
		subtype names would be misjudged as distinct, and symbol resolution happening after indexing
		could change the comparison basis). For now, ``Functions``/``Procedures`` just return every
		overload found under a given name, unresolved."""
		overload1 = Function("f", SimpleSubtypeSymbol(SimpleName("integer")))
		overload2 = Function("f", SimpleSubtypeSymbol(SimpleName("boolean")))
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[overload1, overload2])
		architecture.IndexDeclaredItems()

		self.assertEqual(1, len(architecture.Functions))
		self.assertEqual([overload1, overload2], architecture.Functions["f"])

	def test_IndexDeclaredItems_ProcedureOverloads(self) -> None:
		"""Same as above, but for procedures."""
		overload1 = Procedure("p")
		overload2 = Procedure("p")
		architecture = Architecture("rtl", _entitySymbol("ent"), declaredItems=[overload1, overload2])
		architecture.IndexDeclaredItems()

		self.assertEqual(1, len(architecture.Procedures))
		self.assertEqual([overload1, overload2], architecture.Procedures["p"])


class Components(Testcase):
	def test_Minimal(self) -> None:
		component = Component("comp")

		self.assertEqual("comp", component.Identifier)
		self.assertIsNone(component.IsBlackbox)
		self.assertEqual(0, len(component.GenericItems))
		self.assertEqual(0, len(component.PortItems))
		self.assertIsNone(component.Entity)

	def test_WithGenericAndPortItems(self) -> None:
		"""Uses bare ``ModelEntity`` stand-ins - ``Component``'s own generic-/port-item loops only
		append and set ``.Parent``, they don't care about the item's real type (real
		``GenericInterfaceItemMixin``/``PortInterfaceItemMixin`` classes are covered in their own
		slice)."""
		genericItem = ModelEntity()
		portItem = ModelEntity()
		component = Component("comp", genericItems=[genericItem], portItems=[portItem])

		self.assertEqual(1, len(component.GenericItems))
		self.assertIs(genericItem, component.GenericItems[0])
		self.assertIs(component, genericItem.Parent)
		self.assertEqual(1, len(component.PortItems))
		self.assertIs(portItem, component.PortItems[0])
		self.assertIs(component, portItem.Parent)

	def test_EntitySetter_AlsoClearsBlackboxFlag(self) -> None:
		component = Component("comp")
		entity = Entity("ent")
		component.Entity = entity

		self.assertIs(entity, component.Entity)
		self.assertFalse(component.IsBlackbox)

	def test_BlackboxWarning(self) -> None:
		"""The warning about a component treated as a blackbox carries the component."""
		component = Component("comp")
		warning = BlackboxWarning("Blackbox caused by 'inst: comp'.", component=component)

		self.assertIs(component, warning.Component)
		self.assertIsNone(warning.Instance)


class Configurations(Testcase):
	"""The *design-unit* ``configuration cfg of ent is ... end configuration;`` - not to be confused
	with ``pyVHDLModel.Configuration.ComponentConfiguration``/``BlockConfiguration``, which are tested
	in tests/unit/Configuration.py."""

	def test_Minimal(self) -> None:
		from pyVHDLModel.Configuration import BlockConfiguration
		from pyVHDLModel.Symbol import Symbol, PossibleReference

		entitySymbol = _entitySymbol("ent")
		blockSpec = Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label)
		blockConfiguration = BlockConfiguration(blockSpec)
		configuration = Configuration("cfg", entitySymbol, blockConfiguration)

		self.assertIs(entitySymbol, configuration.Entity)
		self.assertIs(configuration, entitySymbol.Parent)
		self.assertIs(blockConfiguration, configuration.BlockConfiguration)
		self.assertIs(configuration, blockConfiguration.Parent)
