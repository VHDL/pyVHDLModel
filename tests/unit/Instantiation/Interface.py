# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |      __| | ___  _ __ ___                                                        #
#  | '_ \| | | \ \ / /| |_| | | | | |     / _` |/ _ \| '_ ` _ \                                                       #
#  | |_) | |_| |\ V / |  _  | |_| | |___ | (_| | (_) | | | | | |                                                       #
#  | .__/ \__, | \_/  |_| |_|____/|_____(_)__,_|\___/|_| |_| |_|                                                       #
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
"""Tests for mode views (VHDL-2019), the Port/Parameter signal interface item split, generic/
parameter interface item kinds, and the With*Mixin/*Group classes."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Concurrent import ConcurrentBlockStatement
from pyVHDLModel.DesignUnit import Component, Entity, Package
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ModeViewSymbol
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.Interface  import ModeViewDeclaration, SimpleModeViewElement, CompositeModeViewElement, \
                                   PortSignalInterfaceItem, PortSimpleSignalInterfaceItem, \
                                   PortViewSignalInterfaceItem, ParameterSignalInterfaceItem, \
                                   ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                   GenericInterfaceItemMixin, GenericSubprogramInterfaceItemMixin, \
                                   GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                   GenericProcedureInterfaceItem, GenericFunctionInterfaceItem, InterfacePackage, \
                                   GenericPackageInterfaceItem, ParameterConstantInterfaceItem, \
                                   ParameterVariableInterfaceItem, ParameterFileInterfaceItem, InterfaceGroup, \
                                   GenericGroup, PortGroup, ParameterGroup
from pyVHDLModel.Regions    import WithGenericsMixin, WithPortsMixin, WithParametersMixin

from tests.unit             import _subtypeSymbol
from tests.unit.Mutation    import _generic, _parameter, _port


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ModeViewSymbols(Testcase):
	def test_Unresolved(self) -> None:
		name = SimpleName("MyView")
		symbol = ModeViewSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.ModeView)

	def test_Resolved(self) -> None:
		symbol = ModeViewSymbol(SimpleName("MyView"))
		subtype = SimpleSubtypeSymbol(SimpleName("RecordType"))
		modeView = ModeViewDeclaration("MyView", subtype)

		symbol.ModeView = modeView

		self.assertTrue(symbol.IsResolved)
		self.assertIs(modeView, symbol.ModeView)
		self.assertIs(modeView, symbol.Reference)


class ModeViewDeclarations(Testcase):
	def test_SimpleElements(self) -> None:
		subtype = SimpleSubtypeSymbol(SimpleName("RecordType"))
		elements = [
			SimpleModeViewElement(["a"], Mode.Out),
			SimpleModeViewElement(["b"], Mode.In),
		]
		modeView = ModeViewDeclaration("MyView", subtype, elements)

		self.assertEqual("MyView", modeView.Identifier)
		self.assertIs(subtype, modeView.Subtype)
		self.assertEqual(2, len(modeView.Elements))

		a, b = modeView.Elements
		self.assertIsInstance(a, SimpleModeViewElement)
		self.assertEqual(("a",), a.Identifiers)
		self.assertEqual(Mode.Out, a.Mode)
		self.assertIsInstance(b, SimpleModeViewElement)
		self.assertEqual(("b",), b.Identifiers)
		self.assertEqual(Mode.In, b.Mode)

	def test_MultipleIdentifiersSharingOneMode(self) -> None:
		"""``a, b : out;`` - one element definition, multiple target field names."""
		element = SimpleModeViewElement(["a", "b"], Mode.Out)

		self.assertEqual(("a", "b"), element.Identifiers)
		self.assertEqual(Mode.Out, element.Mode)

	def test_CompositeElement(self) -> None:
		"""``b : view InnerView;`` - a nested/hierarchical mode view reference."""
		subtype = SimpleSubtypeSymbol(SimpleName("OuterRecord"))
		innerViewSymbol = ModeViewSymbol(SimpleName("InnerView"))
		elements = [
			SimpleModeViewElement(["a"], Mode.Out),
			CompositeModeViewElement(["b"], innerViewSymbol),
		]
		modeView = ModeViewDeclaration("OuterView", subtype, elements)

		b = modeView.Elements[1]
		self.assertIsInstance(b, CompositeModeViewElement)
		self.assertEqual(("b",), b.Identifiers)
		self.assertIs(innerViewSymbol, b.ModeViewName)


	def test_SimpleModeViewElementWithDocumentation(self) -> None:
		"""A mode view element is a declaration, so it carries its own comment."""
		element = SimpleModeViewElement(["a"], Mode.Out, "--! An output element.")

		self.assertEqual("--! An output element.", element.Documentation)

	def test_CompositeModeViewElementWithDocumentation(self) -> None:
		element = CompositeModeViewElement(["b"], ModeViewSymbol(SimpleName("inner")), "--! A composite element.")

		self.assertEqual("--! A composite element.", element.Documentation)

	def test_ModeViewElementWithoutDocumentation(self) -> None:
		element = SimpleModeViewElement(["c"], Mode.In)

		self.assertIsNone(element.Documentation)


class PortSignalInterfaceItems(Testcase):
	def test_SimpleMode(self) -> None:
		port = PortSimpleSignalInterfaceItem(["p"], Mode.In, SimpleSubtypeSymbol(SimpleName("bit")))

		self.assertIsInstance(port, PortSignalInterfaceItem)
		self.assertEqual(Mode.In, port.Mode)
		self.assertIsNotNone(port.Subtype)

	def test_ModeView(self) -> None:
		modeViewIndication = ModeViewSymbol(SimpleName("MyView"))
		port = PortViewSignalInterfaceItem(["p"], modeViewIndication)

		self.assertIsInstance(port, PortSignalInterfaceItem)
		self.assertIs(modeViewIndication, port.ModeViewIndication)
		self.assertIs(modeViewIndication, port.Subtype)


class ParameterSignalInterfaceItems(Testcase):
	def test_SimpleMode(self) -> None:
		parameter = ParameterSimpleSignalInterfaceItem(["s"], Mode.In, SimpleSubtypeSymbol(SimpleName("bit")))

		self.assertIsInstance(parameter, ParameterSignalInterfaceItem)
		self.assertEqual(Mode.In, parameter.Mode)

	def test_ModeView(self) -> None:
		modeViewIndication = ModeViewSymbol(SimpleName("MyView"))
		parameter = ParameterViewSignalInterfaceItem(["s"], modeViewIndication)

		self.assertIsInstance(parameter, ParameterSignalInterfaceItem)
		self.assertIs(modeViewIndication, parameter.ModeViewIndication)
		self.assertIs(modeViewIndication, parameter.Subtype)


class GenericInterfaceItems(Testcase):
	def test_GenericConstantInterfaceItem(self) -> None:
		"""``generic (G : positive := 8);``"""
		default = IntegerLiteral(8)
		item = GenericConstantInterfaceItem(["G"], Mode.In, _subtypeSymbol("positive"), defaultExpression=default)

		self.assertEqual(("G",), item.Identifiers)
		self.assertIs(Mode.In, item.Mode)
		self.assertIs(default, item.DefaultExpression)

	def test_GenericTypeInterfaceItem(self) -> None:
		"""``generic (type T);`` (VHDL-2008)"""
		item = GenericTypeInterfaceItem("T")

		self.assertEqual("T", item.Identifier)

	def test_GenericProcedureInterfaceItem(self) -> None:
		"""``generic (procedure proc);`` (VHDL-2008)"""
		item = GenericProcedureInterfaceItem("proc")

		self.assertEqual("proc", item.Identifier)

	def test_GenericProcedureInterfaceItem_WithDocumentation(self) -> None:
		"""Regression test: the constructor used to forward ``(identifier, documentation, parent)``
		positionally into ``Procedure.__init__``'s real signature
		``(identifier, genericItems, parameterItems, ...)``, so a non-``None`` ``documentation`` landed
		in the ``genericItems`` slot and got iterated as if it were a list of interface items (crashing
		on anything but ``None``/an empty iterable). Fixed by forwarding both as keyword arguments."""
		item = GenericProcedureInterfaceItem("proc", documentation="some documentation")

		self.assertEqual("proc", item.Identifier)
		self.assertEqual("some documentation", item.Documentation)

	def test_GenericProcedureInterfaceItem_Mixin(self) -> None:
		"""A generic procedure is a generic subprogram and a generic interface item."""
		item = GenericProcedureInterfaceItem("proc")

		self.assertIsInstance(item, GenericSubprogramInterfaceItemMixin)
		self.assertIsInstance(item, GenericInterfaceItemMixin)

	def test_GenericFunctionInterfaceItem(self) -> None:
		"""``generic (function func return boolean);`` (VHDL-2008) - regression test (HIGH PRIORITY,
		confirmed live via pyGHDL.dom's actual translation dispatch, not just a landmine):
		``GenericFunctionInterfaceItem`` had no ``returnType`` parameter of its own, so
		``super().__init__(identifier, documentation, parent)`` misaligned against
		``Function.__init__``'s real signature - ``documentation`` landed in the ``returnType`` slot,
		and ``Function.__init__`` unconditionally does ``returnType.Parent = self``, which crashed on
		anything but a real ``Symbol`` (including the plain, no-docs case, since ``None`` has no
		``Parent`` either). Fixed by adding a real ``returnType`` parameter and forwarding
		``documentation``/``parent`` as keyword arguments."""
		returnType = _subtypeSymbol("boolean")
		item = GenericFunctionInterfaceItem("func", returnType)

		self.assertEqual("func", item.Identifier)
		self.assertIs(returnType, item.ReturnType)
		self.assertIs(item, returnType.Parent)

	def test_GenericFunctionInterfaceItem_Mixin(self) -> None:
		"""A generic function is a generic subprogram and a generic interface item."""
		item = GenericFunctionInterfaceItem("func", _subtypeSymbol("boolean"))

		self.assertIsInstance(item, GenericSubprogramInterfaceItemMixin)
		self.assertIsInstance(item, GenericInterfaceItemMixin)

	def test_GenericPackageInterfaceItem(self) -> None:
		"""``generic (package p is new q generic map (<>));`` (VHDL-2008)"""
		item = GenericPackageInterfaceItem("p")

		self.assertIsInstance(item, InterfacePackage)
		self.assertEqual("p", item.Identifier)


class ParameterInterfaceItems(Testcase):
	def test_ParameterConstantInterfaceItem(self) -> None:
		"""``procedure proc(constant c : in natural);``"""
		item = ParameterConstantInterfaceItem(["c"], Mode.In, _subtypeSymbol("natural"))

		self.assertIs(Mode.In, item.Mode)

	def test_ParameterVariableInterfaceItem(self) -> None:
		"""``procedure proc(variable v : inout natural);``"""
		item = ParameterVariableInterfaceItem(["v"], Mode.InOut, _subtypeSymbol("natural"))

		self.assertIs(Mode.InOut, item.Mode)

	def test_ParameterFileInterfaceItem(self) -> None:
		"""``procedure proc(file f : text);``"""
		item = ParameterFileInterfaceItem(["f"], _subtypeSymbol("text"))

		self.assertEqual(("f",), item.Identifiers)

	def test_ParameterConstantInterfaceItem_WithDocumentation(self) -> None:
		"""Regression test: every ``Generic*``/``Parameter*InterfaceItem`` class calls its mixin's own
		``__init__(self)`` (no arguments) *after* the primary base already set ``documentation``
		correctly. Since ``InterfaceItemMixin`` used to inherit ``DocumentedEntityMixin`` itself, that
		trailing, argument-less call silently reset ``_documentation`` back to ``None`` every time - a
		diamond back to the same mixin via two independent paths (the primary base and the interface-
		item mixin), each initialized explicitly rather than cooperatively via ``super()``. Fixed by
		removing ``DocumentedEntityMixin`` from ``InterfaceItemMixin``'s bases instead of removing the
		call: every concrete interface item is already a documentable entity via its primary base
		(constant, signal, variable, file, type, subprogram, or package), so the mixin never needed to
		carry documentation of its own."""
		item = ParameterConstantInterfaceItem(["c"], Mode.In, _subtypeSymbol("natural"), documentation="some documentation")

		self.assertEqual("some documentation", item.Documentation)


class WithGenericsPortsParametersMixins(Testcase):
	"""Tested via a minimal local host combining each mixin with itself (mixins can't be
	instantiated standalone - see the design note in tests/unit/Base.py); real design-unit/
	subprogram hosts already exercise these mixins incidentally in their own slices, but nothing
	elsewhere reads the ``*Count`` properties, so that's the focus here."""

	def test_WithGenericsMixin(self) -> None:
		class _Host(WithGenericsMixin):
			def _AddToNamespace(self, element) -> None:
				pass

			def _RemoveFromNamespace(self, element) -> None:
				pass

			def _ClashingDeclarations(self, item) -> list:
				return []

		item = GenericTypeInterfaceItem("T")
		host = _Host([item])

		self.assertEqual(1, host.GenericCount)
		self.assertIs(item, host.GenericItems[0])

	def test_WithPortsMixin(self) -> None:
		class _Host(WithPortsMixin):
			def _AddToNamespace(self, element) -> None:
				pass

			def _RemoveFromNamespace(self, element) -> None:
				pass

			def _ClashingDeclarations(self, item) -> list:
				return []

		item = PortSimpleSignalInterfaceItem(["p"], Mode.In, _subtypeSymbol("bit"))
		host = _Host([item])

		self.assertEqual(1, host.PortCount)

	def test_WithParametersMixin(self) -> None:
		class _Host(WithParametersMixin):
			def _AddToNamespace(self, element) -> None:
				pass

			def _RemoveFromNamespace(self, element) -> None:
				pass

			def _ClashingDeclarations(self, item) -> list:
				return []

			def _ParameterItemsChanged(self) -> None:
				pass

		item = ParameterFileInterfaceItem(["f"], _subtypeSymbol("text"))
		host = _Host([item])

		self.assertEqual(1, host.ParameterCount)


class InterfaceItemRendering(Testcase):
	"""An interface item renders as an object declaration plus its interface mode - an object's own
	rendering cannot show the mode, since it is not part of an object declaration.

	The trailing ``?`` on each subtype is ``Symbol.__str__``'s unresolved marker: these items are
	built standalone, so their subtype symbols are never linked."""

	def test_PortShowsItsMode(self) -> None:
		port = PortSimpleSignalInterfaceItem(["p1", "p2"], Mode.In, _subtypeSymbol("bit"))

		self.assertEqual("signal p1, p2 : in bit?", str(port))

	def test_GenericShowsItsMode(self) -> None:
		generic = GenericConstantInterfaceItem(["G"], Mode.In, _subtypeSymbol("positive"))

		self.assertEqual("constant G : in positive?", str(generic))

	def test_ParametersShowTheirMode(self) -> None:
		constant = ParameterConstantInterfaceItem(["a"], Mode.In, _subtypeSymbol("integer"))
		variable = ParameterVariableInterfaceItem(["v"], Mode.InOut, _subtypeSymbol("integer"))
		signal = ParameterSimpleSignalInterfaceItem(["s"], Mode.Out, _subtypeSymbol("bit"))

		self.assertEqual("constant a : in integer?", str(constant))
		self.assertEqual("variable v : inout integer?", str(variable))
		self.assertEqual("signal s : out bit?", str(signal))

	def test_DefaultModeIsOmitted(self) -> None:
		"""``Mode.Default`` means the mode is context dependent, so there is nothing to render."""
		generic = GenericConstantInterfaceItem(["G"], Mode.Default, _subtypeSymbol("positive"))

		self.assertEqual("constant G : positive?", str(generic))

	def test_ItemWithoutAModeRendersAsAnObject(self) -> None:
		parameter = ParameterFileInterfaceItem(["f"], _subtypeSymbol("text"))

		self.assertEqual("file f : text?", str(parameter))

	def test_ModeViewIsRenderedAsAView(self) -> None:
		"""VHDL-2019 mode views sit in the subtype position, so they are marked as a view."""
		port = PortViewSignalInterfaceItem(["p"], ModeViewSymbol(SimpleName("myView")))

		self.assertEqual("signal p : view myView?", str(port))


class Groups(Testcase):
	"""Regression test (``__str__``): all three built their string via
	``p._identifier for p in self._xItems``, but interface items come in two incompatible shapes -
	``NamedEntityMixin``-based (singular ``_identifier`` - the four ``Generic*`` subprogram/package/
	type items) vs. ``MultipleNamedEntityMixin``-based (plural ``_identifiers`` - every
	``Constant``/``Signal``/``Variable``/``File``-derived item, i.e. every ``Port*``/``Parameter*``
	item and ``GenericConstantInterfaceItem``, since a single declaration can name several objects at
	once: ``port (p1, p2 : in bit);``). ``PortGroup``/``ParameterGroup.__str__`` crashed for
	essentially any realistic content, and ``GenericGroup.__str__`` crashed the moment a
	``GenericConstantInterfaceItem`` was included or a group mixed both item shapes. Fixed via the
	shared ``_identifiersOf()`` helper, which flattens either shape into a plain tuple of names."""

	def test_GenericGroup(self) -> None:
		item = GenericTypeInterfaceItem("T")
		group = GenericGroup([item], name="generics")

		self.assertEqual(1, len(group))
		self.assertEqual([item], list(group))
		self.assertEqual("GenericGroup: generics (1): T", str(group))

	def test_GenericGroup_MixedItemShapes(self) -> None:
		"""``generic (type T; G : positive := 8);`` - a single generic clause legally mixes a
		``NamedEntityMixin``-based item (``GenericTypeInterfaceItem``) with a
		``MultipleNamedEntityMixin``-based one (``GenericConstantInterfaceItem``)."""
		typeItem = GenericTypeInterfaceItem("T")
		constantItem = GenericConstantInterfaceItem(["G"], Mode.In, _subtypeSymbol("positive"))
		group = GenericGroup([typeItem, constantItem])

		self.assertEqual("GenericGroup: None (2): T, G", str(group))

	def test_PortGroup(self) -> None:
		item = PortSimpleSignalInterfaceItem(["p"], Mode.In, _subtypeSymbol("bit"))
		group = PortGroup([item], name="ports")

		self.assertEqual(1, len(group))
		self.assertEqual([item], list(group))
		self.assertEqual("PortGroup: ports (1): p", str(group))

	def test_PortGroup_MultipleIdentifiersPerItem(self) -> None:
		"""``port (p1, p2 : in bit);`` - one declaration, two port names."""
		item = PortSimpleSignalInterfaceItem(["p1", "p2"], Mode.In, _subtypeSymbol("bit"))
		group = PortGroup([item])

		self.assertEqual("PortGroup: None (1): p1, p2", str(group))

	def test_ParameterGroup(self) -> None:
		item = ParameterFileInterfaceItem(["f"], _subtypeSymbol("text"))
		group = ParameterGroup([item], name="parameters")

		self.assertEqual(1, len(group))
		self.assertEqual([item], list(group))
		self.assertEqual("ParameterGroup: parameters (1): f", str(group))

	def test_InterfaceGroup_NoName(self) -> None:
		group = InterfaceGroup()

		self.assertIsNone(group.Identifier)


class PortGroups(Testcase):
	def test_Constructor(self) -> None:
		"""A port group records its ports, but changes neither their parent nor their group."""
		clock = _port("clock")
		reset = _port("reset")

		group = PortGroup((port for port in (clock, reset)), name="clocking", documentation="Clock and reset.")

		self.assertEqual("clocking", group.Identifier)
		self.assertEqual("Clock and reset.", group.Documentation)
		self.assertListEqual([clock, reset], group.PortItems)
		self.assertIsNone(group.Parent)
		self.assertIsNone(clock.Parent)
		self.assertIsNone(clock.Group)

	def test_Constructor_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			PortGroup(None)

		self.assertEqual("Parameter 'portItems' is None.", str(context.exception))

	def test_Constructor_NotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			PortGroup(_port("clock"))

		self.assertEqual("Parameter 'portItems' is not iterable.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Constructor_WrongElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			PortGroup([_port("clock"), "reset"])

		self.assertEqual(
			"Element of parameter 'portItems' is not of type 'PortSignalInterfaceItem'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Constructor_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			PortGroup([])

		self.assertEqual("Parameter 'portItems' is empty.", str(context.exception))

	def test_Constructor_InGroup(self) -> None:
		"""A port in a port group of a language construct can't be grouped again."""
		clock = _port("clock")
		Entity("e", portItems=[clock])

		with self.assertRaises(ValueError) as context:
			PortGroup([clock])

		self.assertEqual(
			"Element of parameter 'portItems' is in a port group of a language construct.",
			str(context.exception)
		)
		self.assertListEqual(["Got port 'clock' of Entity."], context.exception.__notes__)

	def test_Default(self) -> None:
		"""Without port groups, all ports form one unnamed port group."""
		clock = _port("clock")
		reset = _port("reset")

		entity = Entity("e", portItems=[clock, reset])

		self.assertEqual(1, len(entity.PortGroups))
		group = entity.PortGroups[0]
		self.assertIsNone(group.Identifier)
		self.assertListEqual([clock, reset], group.PortItems)
		self.assertIsNot(entity.PortItems, group.PortItems)
		self.assertIs(entity, group.Parent)
		self.assertIs(entity, clock.Parent)
		self.assertIs(group, clock.Group)
		self.assertIs(group, reset.Group)

	def test_Default_NoPorts(self) -> None:
		entity = Entity("e")

		self.assertListEqual([], entity.PortGroups)

	def test_Partition(self) -> None:
		"""``clock, reset | In_Valid, In_Data, In_Ack | error | Out_Valid, Out_Data, Out_Ack``"""
		names = ("clock", "reset", "In_Valid", "In_Data", "In_Ack", "error", "Out_Valid", "Out_Data", "Out_Ack")
		ports = [_port(name) for name in names]
		groups = [
			PortGroup(ports[0:2]),
			PortGroup(ports[2:5], name="In"),
			PortGroup(ports[5:6]),
			PortGroup(ports[6:9], name="Out")
		]

		entity = Entity("e", portItems=ports, portGroups=groups)

		self.assertListEqual(groups, entity.PortGroups)
		self.assertListEqual([None, "In", None, "Out"], [group.Identifier for group in entity.PortGroups])
		for group in groups:
			self.assertIs(entity, group.Parent)
			for port in group:
				self.assertIs(entity, port.Parent)
				self.assertIs(group, port.Group)

	def test_Partition_Component(self) -> None:
		clock = _port("clock")
		group = PortGroup([clock], name="clocking")

		component = Component("c", portItems=[clock], portGroups=[group])

		self.assertListEqual([group], component.PortGroups)
		self.assertIs(component, group.Parent)
		self.assertIs(group, clock.Group)

	def test_Partition_Block(self) -> None:
		clock = _port("clock")
		group = PortGroup([clock], name="clocking")

		block = ConcurrentBlockStatement("blk", portItems=[clock], portGroups=[group])

		self.assertListEqual([group], block.PortGroups)
		self.assertIs(block, group.Parent)
		self.assertIs(group, clock.Group)

	def test_Partition_NoPorts(self) -> None:
		entity = Entity("e", portGroups=[])

		self.assertListEqual([], entity.PortGroups)

	def test_Partition_WrongOrder(self) -> None:
		clock = _port("clock")
		reset = _port("reset")

		with self.assertRaises(ValueError) as context:
			Entity("e", portItems=[clock, reset], portGroups=[PortGroup([reset]), PortGroup([clock])])

		self.assertEqual("Parameter 'portGroups' doesn't partition parameter 'portItems'.", str(context.exception))
		self.assertListEqual(["Got port groups 'reset | clock' for ports 'clock, reset'."], context.exception.__notes__)

	def test_Partition_MissingPort(self) -> None:
		clock = _port("clock")
		reset = _port("reset")
		error = _port("error")

		with self.assertRaises(ValueError) as context:
			Entity("e", portItems=[clock, reset, error], portGroups=[PortGroup([clock, reset])])

		self.assertEqual("Parameter 'portGroups' doesn't partition parameter 'portItems'.", str(context.exception))
		self.assertListEqual(
			["Got port groups 'clock, reset' for ports 'clock, reset, error'."],
			context.exception.__notes__
		)

	def test_Partition_ForeignPort(self) -> None:
		clock = _port("clock")
		reset = _port("reset")
		foreign = _port("reset")

		with self.assertRaises(ValueError) as context:
			Entity("e", portItems=[clock, reset], portGroups=[PortGroup([clock, foreign])])

		self.assertEqual("Parameter 'portGroups' doesn't partition parameter 'portItems'.", str(context.exception))
		self.assertListEqual(["Got port groups 'clock, reset' for ports 'clock, reset'."], context.exception.__notes__)

	def test_Partition_PortInTwoGroups(self) -> None:
		clock = _port("clock")
		reset = _port("reset")

		with self.assertRaises(ValueError) as context:
			Entity("e", portItems=[clock, reset], portGroups=[PortGroup([clock, reset]), PortGroup([reset])])

		self.assertEqual("Parameter 'portGroups' doesn't partition parameter 'portItems'.", str(context.exception))
		self.assertListEqual(
			["Got port groups 'clock, reset | reset' for ports 'clock, reset'."],
			context.exception.__notes__
		)

	def test_Partition_WrongElementType(self) -> None:
		clock = _port("clock")

		with self.assertRaises(TypeError) as context:
			Entity("e", portItems=[clock], portGroups=[clock])

		self.assertEqual("Element of parameter 'portGroups' is not of type 'PortGroup'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Partition_NotIterable(self) -> None:
		clock = _port("clock")

		with self.assertRaises(TypeError) as context:
			Entity("e", portItems=[clock], portGroups=1)

		self.assertEqual("Parameter 'portGroups' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class GenericGroups(Testcase):
	def test_Constructor(self) -> None:
		"""A generic group records its generics, but changes neither their parent nor their group."""
		width = _generic("WIDTH")
		depth = _generic("DEPTH")

		group = GenericGroup((generic for generic in (width, depth)), name="sizes", documentation="Bus sizes.")

		self.assertEqual("sizes", group.Identifier)
		self.assertEqual("Bus sizes.", group.Documentation)
		self.assertListEqual([width, depth], group.GenericItems)
		self.assertIsNone(group.Parent)
		self.assertIsNone(width.Parent)
		self.assertIsNone(width.Group)

	def test_Constructor_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			GenericGroup(None)

		self.assertEqual("Parameter 'genericItems' is None.", str(context.exception))

	def test_Constructor_NotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			GenericGroup(_generic("WIDTH"))

		self.assertEqual("Parameter 'genericItems' is not iterable.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Constructor_WrongElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			GenericGroup([_generic("WIDTH"), "DEPTH"])

		self.assertEqual(
			"Element of parameter 'genericItems' is not of type 'GenericInterfaceItemMixin'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Constructor_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			GenericGroup([])

		self.assertEqual("Parameter 'genericItems' is empty.", str(context.exception))

	def test_Constructor_InGroup(self) -> None:
		"""A generic in a generic group of a language construct can't be grouped again."""
		width = _generic("WIDTH")
		Entity("e", genericItems=[width])

		with self.assertRaises(ValueError) as context:
			GenericGroup([width])

		self.assertEqual(
			"Element of parameter 'genericItems' is in a generic group of a language construct.",
			str(context.exception)
		)
		self.assertListEqual(["Got generic 'WIDTH' of Entity."], context.exception.__notes__)

	def test_Default(self) -> None:
		"""Without generic groups, all generics form one unnamed generic group."""
		width = _generic("WIDTH")
		depth = _generic("DEPTH")

		entity = Entity("e", genericItems=[width, depth])

		self.assertEqual(1, len(entity.GenericGroups))
		group = entity.GenericGroups[0]
		self.assertIsNone(group.Identifier)
		self.assertListEqual([width, depth], group.GenericItems)
		self.assertIsNot(entity.GenericItems, group.GenericItems)
		self.assertIs(entity, group.Parent)
		self.assertIs(entity, width.Parent)
		self.assertIs(group, width.Group)
		self.assertIs(group, depth.Group)

	def test_Default_NoGenerics(self) -> None:
		entity = Entity("e")

		self.assertListEqual([], entity.GenericGroups)

	def test_Partition(self) -> None:
		"""``WIDTH, DEPTH | IN_WIDTH, IN_DEPTH, IN_LATENCY | DEBUG | OUT_WIDTH, OUT_DEPTH, OUT_LATENCY``"""
		names = ("WIDTH", "DEPTH", "IN_WIDTH", "IN_DEPTH", "IN_LATENCY", "DEBUG", "OUT_WIDTH", "OUT_DEPTH", "OUT_LATENCY")
		generics = [_generic(name) for name in names]
		groups = [
			GenericGroup(generics[0:2]),
			GenericGroup(generics[2:5], name="In"),
			GenericGroup(generics[5:6]),
			GenericGroup(generics[6:9], name="Out")
		]

		entity = Entity("e", genericItems=generics, genericGroups=groups)

		self.assertListEqual(groups, entity.GenericGroups)
		self.assertListEqual([None, "In", None, "Out"], [group.Identifier for group in entity.GenericGroups])
		for group in groups:
			self.assertIs(entity, group.Parent)
			for generic in group:
				self.assertIs(entity, generic.Parent)
				self.assertIs(group, generic.Group)

	def test_Partition_Component(self) -> None:
		width = _generic("WIDTH")
		group = GenericGroup([width], name="sizes")

		component = Component("c", genericItems=[width], genericGroups=[group])

		self.assertListEqual([group], component.GenericGroups)
		self.assertIs(component, group.Parent)
		self.assertIs(group, width.Group)

	def test_Partition_Block(self) -> None:
		width = _generic("WIDTH")
		group = GenericGroup([width], name="sizes")

		block = ConcurrentBlockStatement("blk", genericItems=[width], genericGroups=[group])

		self.assertListEqual([group], block.GenericGroups)
		self.assertIs(block, group.Parent)
		self.assertIs(group, width.Group)

	def test_Partition_NoGenerics(self) -> None:
		entity = Entity("e", genericGroups=[])

		self.assertListEqual([], entity.GenericGroups)

	def test_Partition_Package(self) -> None:
		width = _generic("WIDTH")
		group = GenericGroup([width], name="sizes")

		package = Package("p", genericItems=[width], genericGroups=[group])

		self.assertListEqual([group], package.GenericGroups)
		self.assertIs(package, group.Parent)
		self.assertIs(group, width.Group)

	def test_Partition_Subprogram(self) -> None:
		width = _generic("WIDTH")
		group = GenericGroup([width], name="sizes")

		procedure = Procedure("p", genericItems=[width], genericGroups=[group])

		self.assertListEqual([group], procedure.GenericGroups)
		self.assertIs(procedure, group.Parent)
		self.assertIs(group, width.Group)

	def test_Partition_WrongOrder(self) -> None:
		"""A generic type has one identifier, a generic constant an identifier list: both are named in the note."""
		typeItem = GenericTypeInterfaceItem("T")
		width =    _generic("WIDTH")

		with self.assertRaises(ValueError) as context:
			Entity("e", genericItems=[typeItem, width], genericGroups=[GenericGroup([width]), GenericGroup([typeItem])])

		self.assertEqual(
			"Parameter 'genericGroups' doesn't partition parameter 'genericItems'.",
			str(context.exception)
		)
		self.assertListEqual(["Got generic groups 'WIDTH | T' for generics 'T, WIDTH'."], context.exception.__notes__)

	def test_Partition_MissingGeneric(self) -> None:
		width = _generic("WIDTH")
		depth = _generic("DEPTH")
		debug = _generic("DEBUG")

		with self.assertRaises(ValueError) as context:
			Entity("e", genericItems=[width, depth, debug], genericGroups=[GenericGroup([width, depth])])

		self.assertEqual(
			"Parameter 'genericGroups' doesn't partition parameter 'genericItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got generic groups 'WIDTH, DEPTH' for generics 'WIDTH, DEPTH, DEBUG'."],
			context.exception.__notes__
		)

	def test_Partition_ForeignGeneric(self) -> None:
		width = _generic("WIDTH")
		depth = _generic("DEPTH")
		foreign = _generic("DEPTH")

		with self.assertRaises(ValueError) as context:
			Entity("e", genericItems=[width, depth], genericGroups=[GenericGroup([width, foreign])])

		self.assertEqual(
			"Parameter 'genericGroups' doesn't partition parameter 'genericItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got generic groups 'WIDTH, DEPTH' for generics 'WIDTH, DEPTH'."],
			context.exception.__notes__
		)

	def test_Partition_GenericInTwoGroups(self) -> None:
		width = _generic("WIDTH")
		depth = _generic("DEPTH")

		with self.assertRaises(ValueError) as context:
			Entity("e", genericItems=[width, depth], genericGroups=[GenericGroup([width, depth]), GenericGroup([depth])])

		self.assertEqual(
			"Parameter 'genericGroups' doesn't partition parameter 'genericItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got generic groups 'WIDTH, DEPTH | DEPTH' for generics 'WIDTH, DEPTH'."],
			context.exception.__notes__
		)

	def test_Partition_WrongElementType(self) -> None:
		width = _generic("WIDTH")

		with self.assertRaises(TypeError) as context:
			Entity("e", genericItems=[width], genericGroups=[width])

		self.assertEqual("Element of parameter 'genericGroups' is not of type 'GenericGroup'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Partition_NotIterable(self) -> None:
		width = _generic("WIDTH")

		with self.assertRaises(TypeError) as context:
			Entity("e", genericItems=[width], genericGroups=1)

		self.assertEqual("Parameter 'genericGroups' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class ParameterGroups(Testcase):
	def test_Constructor(self) -> None:
		"""A parameter group records its parameters, but changes neither their parent nor their group."""
		clock = _parameter("clock")
		reset = _parameter("reset")

		group = ParameterGroup((parameter for parameter in (clock, reset)), name="clocking", documentation="Clocking.")

		self.assertEqual("clocking", group.Identifier)
		self.assertEqual("Clocking.", group.Documentation)
		self.assertListEqual([clock, reset], group.ParameterItems)
		self.assertIsNone(group.Parent)
		self.assertIsNone(clock.Parent)
		self.assertIsNone(clock.Group)

	def test_Constructor_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			ParameterGroup(None)

		self.assertEqual("Parameter 'parameterItems' is None.", str(context.exception))

	def test_Constructor_NotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			ParameterGroup(_parameter("clock"))

		self.assertEqual("Parameter 'parameterItems' is not iterable.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.ParameterConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Constructor_WrongElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			ParameterGroup([_parameter("clock"), "reset"])

		self.assertEqual(
			"Element of parameter 'parameterItems' is not of type 'ParameterInterfaceItemMixin'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Constructor_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			ParameterGroup([])

		self.assertEqual("Parameter 'parameterItems' is empty.", str(context.exception))

	def test_Constructor_InGroup(self) -> None:
		"""A parameter in a parameter group of a subprogram can't be grouped again."""
		clock = _parameter("clock")
		Procedure("p", parameterItems=[clock])

		with self.assertRaises(ValueError) as context:
			ParameterGroup([clock])

		self.assertEqual(
			"Element of parameter 'parameterItems' is in a parameter group of a subprogram.",
			str(context.exception)
		)
		self.assertListEqual(["Got parameter 'clock' of Procedure."], context.exception.__notes__)

	def test_Default(self) -> None:
		"""Without parameter groups, all parameters form one unnamed parameter group."""
		clock = _parameter("clock")
		reset = _parameter("reset")

		procedure = Procedure("p", parameterItems=[clock, reset])

		self.assertEqual(1, len(procedure.ParameterGroups))
		group = procedure.ParameterGroups[0]
		self.assertIsNone(group.Identifier)
		self.assertListEqual([clock, reset], group.ParameterItems)
		self.assertIsNot(procedure.ParameterItems, group.ParameterItems)
		self.assertIs(procedure, group.Parent)
		self.assertIs(procedure, clock.Parent)
		self.assertIs(group, clock.Group)
		self.assertIs(group, reset.Group)

	def test_Default_NoParameters(self) -> None:
		procedure = Procedure("p")

		self.assertListEqual([], procedure.ParameterGroups)

	def test_Partition(self) -> None:
		"""``clock, reset | in_valid, in_data, in_ack | error | out_valid, out_data, out_ack``"""
		names = ("clock", "reset", "in_valid", "in_data", "in_ack", "error", "out_valid", "out_data", "out_ack")
		parameters = [_parameter(name) for name in names]
		groups = [
			ParameterGroup(parameters[0:2]),
			ParameterGroup(parameters[2:5], name="In"),
			ParameterGroup(parameters[5:6]),
			ParameterGroup(parameters[6:9], name="Out")
		]

		procedure = Procedure("p", parameterItems=parameters, parameterGroups=groups)

		self.assertListEqual(groups, procedure.ParameterGroups)
		self.assertListEqual([None, "In", None, "Out"], [group.Identifier for group in procedure.ParameterGroups])
		for group in groups:
			self.assertIs(procedure, group.Parent)
			for parameter in group:
				self.assertIs(procedure, parameter.Parent)
				self.assertIs(group, parameter.Group)

	def test_Partition_Function(self) -> None:
		clock = _parameter("clock")
		group = ParameterGroup([clock], name="clocking")

		function = Function("f", _subtypeSymbol("integer"), parameterItems=[clock], parameterGroups=[group])

		self.assertListEqual([group], function.ParameterGroups)
		self.assertIs(function, group.Parent)
		self.assertIs(group, clock.Group)

	def test_Partition_NoParameters(self) -> None:
		procedure = Procedure("p", parameterGroups=[])

		self.assertListEqual([], procedure.ParameterGroups)

	def test_Partition_WrongOrder(self) -> None:
		clock = _parameter("clock")
		reset = _parameter("reset")

		with self.assertRaises(ValueError) as context:
			Procedure("p", parameterItems=[clock, reset], parameterGroups=[ParameterGroup([reset]), ParameterGroup([clock])])

		self.assertEqual(
			"Parameter 'parameterGroups' doesn't partition parameter 'parameterItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got parameter groups 'reset | clock' for parameters 'clock, reset'."],
			context.exception.__notes__
		)

	def test_Partition_MissingParameter(self) -> None:
		clock = _parameter("clock")
		reset = _parameter("reset")
		error = _parameter("error")

		with self.assertRaises(ValueError) as context:
			Procedure("p", parameterItems=[clock, reset, error], parameterGroups=[ParameterGroup([clock, reset])])

		self.assertEqual(
			"Parameter 'parameterGroups' doesn't partition parameter 'parameterItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got parameter groups 'clock, reset' for parameters 'clock, reset, error'."],
			context.exception.__notes__
		)

	def test_Partition_ForeignParameter(self) -> None:
		clock = _parameter("clock")
		reset = _parameter("reset")
		foreign = _parameter("reset")

		with self.assertRaises(ValueError) as context:
			Procedure("p", parameterItems=[clock, reset], parameterGroups=[ParameterGroup([clock, foreign])])

		self.assertEqual(
			"Parameter 'parameterGroups' doesn't partition parameter 'parameterItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got parameter groups 'clock, reset' for parameters 'clock, reset'."],
			context.exception.__notes__
		)

	def test_Partition_ParameterInTwoGroups(self) -> None:
		clock = _parameter("clock")
		reset = _parameter("reset")

		with self.assertRaises(ValueError) as context:
			Procedure(
				"p",
				parameterItems=[clock, reset],
				parameterGroups=[ParameterGroup([clock, reset]), ParameterGroup([reset])]
			)

		self.assertEqual(
			"Parameter 'parameterGroups' doesn't partition parameter 'parameterItems'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got parameter groups 'clock, reset | reset' for parameters 'clock, reset'."],
			context.exception.__notes__
		)

	def test_Partition_WrongElementType(self) -> None:
		clock = _parameter("clock")

		with self.assertRaises(TypeError) as context:
			Procedure("p", parameterItems=[clock], parameterGroups=[clock])

		self.assertEqual("Element of parameter 'parameterGroups' is not of type 'ParameterGroup'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.ParameterConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Partition_NotIterable(self) -> None:
		clock = _parameter("clock")

		with self.assertRaises(TypeError) as context:
			Procedure("p", parameterItems=[clock], parameterGroups=1)

		self.assertEqual("Parameter 'parameterGroups' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
