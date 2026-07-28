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
from unittest import TestCase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ModeViewSymbol
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Interface  import ModeViewDeclaration, SimpleModeViewElement, CompositeModeViewElement
from pyVHDLModel.Interface  import PortSignalInterfaceItem, PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem
from pyVHDLModel.Interface  import ParameterSignalInterfaceItem, ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem
from pyVHDLModel.Interface  import (
	GenericConstantInterfaceItem, GenericTypeInterfaceItem,
	GenericProcedureInterfaceItem, GenericFunctionInterfaceItem,
	InterfacePackage, GenericPackageInterfaceItem,
	ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, ParameterFileInterfaceItem,
	WithGenericsMixin, WithPortsMixin, WithParametersMixin,
	InterfaceGroup, GenericGroup, PortGroup, ParameterGroup,
)


def _subtype(name: str = "bit") -> SimpleSubtypeSymbol:
	return SimpleSubtypeSymbol(SimpleName(name))


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ModeViewSymbols(TestCase):
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


class ModeViewDeclarations(TestCase):
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


class PortSignalInterfaceItems(TestCase):
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


class ParameterSignalInterfaceItems(TestCase):
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


class GenericInterfaceItems(TestCase):
	def test_GenericConstantInterfaceItem(self) -> None:
		"""``generic (G : positive := 8);``"""
		default = IntegerLiteral(8)
		item = GenericConstantInterfaceItem(["G"], Mode.In, _subtype("positive"), defaultExpression=default)

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
		returnType = _subtype("boolean")
		item = GenericFunctionInterfaceItem("func", returnType)

		self.assertEqual("func", item.Identifier)
		self.assertIs(returnType, item.ReturnType)
		self.assertIs(item, returnType.Parent)

	def test_GenericPackageInterfaceItem(self) -> None:
		"""``generic (package p is new q generic map (<>));`` (VHDL-2008)"""
		item = GenericPackageInterfaceItem("p")

		self.assertIsInstance(item, InterfacePackage)
		self.assertEqual("p", item.Identifier)


class ParameterInterfaceItems(TestCase):
	def test_ParameterConstantInterfaceItem(self) -> None:
		"""``procedure proc(constant c : in natural);``"""
		item = ParameterConstantInterfaceItem(["c"], Mode.In, _subtype("natural"))

		self.assertIs(Mode.In, item.Mode)

	def test_ParameterVariableInterfaceItem(self) -> None:
		"""``procedure proc(variable v : inout natural);``"""
		item = ParameterVariableInterfaceItem(["v"], Mode.InOut, _subtype("natural"))

		self.assertIs(Mode.InOut, item.Mode)

	def test_ParameterFileInterfaceItem(self) -> None:
		"""``procedure proc(file f : text);``"""
		item = ParameterFileInterfaceItem(["f"], _subtype("text"))

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
		item = ParameterConstantInterfaceItem(["c"], Mode.In, _subtype("natural"), documentation="some documentation")

		self.assertEqual("some documentation", item.Documentation)


class WithGenericsPortsParametersMixins(TestCase):
	"""Tested via a minimal local host combining each mixin with itself (mixins can't be
	instantiated standalone - see the design note in tests/unit/Base.py); real design-unit/
	subprogram hosts already exercise these mixins incidentally in their own slices, but nothing
	elsewhere reads the ``*Count`` properties, so that's the focus here."""

	def test_WithGenericsMixin(self) -> None:
		class _Host(WithGenericsMixin):
			pass

		item = GenericTypeInterfaceItem("T")
		host = _Host([item])

		self.assertEqual(1, host.GenericCount)
		self.assertIs(item, host.GenericItems[0])

	def test_WithPortsMixin(self) -> None:
		class _Host(WithPortsMixin):
			pass

		item = PortSimpleSignalInterfaceItem(["p"], Mode.In, _subtype())
		host = _Host([item])

		self.assertEqual(1, host.PortCount)

	def test_WithParametersMixin(self) -> None:
		class _Host(WithParametersMixin):
			pass

		item = ParameterFileInterfaceItem(["f"], _subtype("text"))
		host = _Host([item])

		self.assertEqual(1, host.ParameterCount)


class Groups(TestCase):
	"""Regression test (missing base class): ``GenericGroup``/``ParameterGroup`` didn't list
	``WithGenericsMixin``/``WithParametersMixin`` as base classes at all (unlike ``PortGroup``, which
	correctly lists ``WithPortsMixin``), so the slots-based metaclass never allocated storage for
	``_genericItems``/``_parameterItems`` - construction crashed immediately with
	``AttributeError: ... no __dict__ for setting new attributes``, even for the simplest, empty-list
	case. Fixed by adding the missing base class to both, mirroring ``PortGroup``.

	Regression test (``__str__``): all three built their string via
	``p._identifier for p in self._xItems``, but interface items come in two incompatible shapes -
	``NamedEntityMixin``-based (singular ``_identifier`` - the four ``Generic*`` subprogram/package/
	type items) vs. ``MultipleNamedEntityMixin``-based (plural ``_identifiers`` - every
	``Constant``/``Signal``/``Variable``/``File``-derived item, i.e. every ``Port*``/``Parameter*``
	item and ``GenericConstantInterfaceItem``, since a single declaration can name several objects at
	once: ``port (p1, p2 : in bit);``). ``PortGroup``/``ParameterGroup.__str__`` crashed for
	essentially any realistic content, and ``GenericGroup.__str__`` crashed the moment a
	``GenericConstantInterfaceItem`` was included or a group mixed both item shapes. Fixed via the
	shared ``identifiersOf()`` helper, which flattens either shape into a plain tuple of names.
	Since then both naming mixins render themselves, so the groups simply join ``str(item)``."""

	def test_GenericGroup(self) -> None:
		item = GenericTypeInterfaceItem("T")
		group = GenericGroup([item], name="generics")

		self.assertEqual(1, len(group))
		self.assertEqual([item], list(group))
		self.assertEqual("GenericGroup: generics (1): T", str(group))

	def test_GenericGroup_Empty(self) -> None:
		group = GenericGroup([])

		self.assertEqual(0, len(group))
		self.assertEqual("GenericGroup: None (0): ", str(group))

	def test_GenericGroup_MixedItemShapes(self) -> None:
		"""``generic (type T; G : positive := 8);`` - a single generic clause legally mixes a
		``NamedEntityMixin``-based item (``GenericTypeInterfaceItem``) with a
		``MultipleNamedEntityMixin``-based one (``GenericConstantInterfaceItem``)."""
		typeItem = GenericTypeInterfaceItem("T")
		constantItem = GenericConstantInterfaceItem(["G"], Mode.In, _subtype("positive"))
		group = GenericGroup([typeItem, constantItem])

		self.assertEqual("GenericGroup: None (2): T, G", str(group))

	def test_PortGroup(self) -> None:
		item = PortSimpleSignalInterfaceItem(["p"], Mode.In, _subtype())
		group = PortGroup([item], name="ports")

		self.assertEqual(1, len(group))
		self.assertEqual([item], list(group))
		self.assertEqual("PortGroup: ports (1): p", str(group))

	def test_PortGroup_MultipleIdentifiersPerItem(self) -> None:
		"""``port (p1, p2 : in bit);`` - one declaration, two port names."""
		item = PortSimpleSignalInterfaceItem(["p1", "p2"], Mode.In, _subtype())
		group = PortGroup([item])

		self.assertEqual("PortGroup: None (1): p1, p2", str(group))

	def test_ParameterGroup(self) -> None:
		item = ParameterFileInterfaceItem(["f"], _subtype("text"))
		group = ParameterGroup([item], name="parameters")

		self.assertEqual(1, len(group))
		self.assertEqual([item], list(group))
		self.assertEqual("ParameterGroup: parameters (1): f", str(group))

	def test_ParameterGroup_Empty(self) -> None:
		group = ParameterGroup([])

		self.assertEqual(0, len(group))

	def test_InterfaceGroup_NoName(self) -> None:
		group = InterfaceGroup()

		self.assertIsNone(group.Identifier)
