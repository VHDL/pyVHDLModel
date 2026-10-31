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
#
"""
Split tests for interface items and mode view elements (:mod:`pyVHDLModel.Interface`).

``port (a, b : in bit);`` becomes ``port (a : in bit; b : in bit);``: outside a language construct, in generic clauses,
port clauses and parameter lists with and without a namespace, and in mode view declarations.
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Mode
from pyVHDLModel.DesignUnit      import Component, Entity
from pyVHDLModel.Exception       import NotAChildError
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Interface       import SimpleModeViewElement, CompositeModeViewElement, GenericConstantInterfaceItem, \
                                        PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                        ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                        ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                        ParameterFileInterfaceItem, ModeViewDeclaration, GenericGroup, PortGroup, \
                                        ParameterGroup, GenericTypeInterfaceItem
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Subprogram      import Procedure
from pyVHDLModel.Symbol          import ModeViewSymbol

from tests.unit                  import _subtypeSymbol
from tests.unit.Mutation         import _generic, _parameter, _port, _reindexed
from tests.unit.Split            import _formatted


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _modeView(name: str) -> ModeViewSymbol:
	"""Reference to a mode view."""
	return ModeViewSymbol(SimpleName(name))


class InterfaceItemsWithMode(Testcase):
	def test_Split(self) -> None:
		for cls in (
			GenericConstantInterfaceItem,
			PortSimpleSignalInterfaceItem,
			ParameterConstantInterfaceItem,
			ParameterVariableInterfaceItem,
			ParameterSimpleSignalInterfaceItem
		):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("natural")
				defaultExpression = IntegerLiteral(0)
				original = cls(("a", "B"), Mode.In, subtype, defaultExpression, "Documentation.")

				declarations = original.Split()

				self.assertEqual(2, len(declarations))
				self.assertIs(original, declarations[0])
				self.assertTupleEqual(("a", ), declarations[0].Identifiers)
				self.assertTupleEqual(("B", ), declarations[1].Identifiers)
				self.assertTupleEqual(("b", ), declarations[1].NormalizedIdentifiers)
				self.assertIs(cls, type(declarations[1]))
				self.assertIsNone(declarations[1].Parent)
				self.assertIs(Mode.In, declarations[1].Mode)
				self.assertEqual("Documentation.", declarations[1].Documentation)
				self.assertIs(subtype, original.Subtype)
				self.assertIsNot(subtype, declarations[1].Subtype)
				self.assertIs(declarations[1], declarations[1].Subtype.Parent)
				self.assertIs(defaultExpression, original.DefaultExpression)
				self.assertIsNot(defaultExpression, declarations[1].DefaultExpression)
				self.assertIs(declarations[1], declarations[1].DefaultExpression.Parent)

	def test_Split_OneIdentifier(self) -> None:
		original = _port("a")

		self.assertTupleEqual((original, ), original.Split())
		self.assertTupleEqual(("a", ), original.Identifiers)

	def test_Split_Formatted(self) -> None:
		original = PortSimpleSignalInterfaceItem(("a", "b"), Mode.Out, _subtypeSymbol("bit"), IntegerLiteral(0))

		self.assertListEqual(["a : out bit := 0", "b : out bit := 0"], _formatted(original.Split()))


class InterfaceItemsWithModeView(Testcase):
	def test_Split(self) -> None:
		for cls in (PortViewSignalInterfaceItem, ParameterViewSignalInterfaceItem):
			with self.subTest(cls.__name__):
				modeViewIndication = _modeView("view1")
				original = cls(("a", "b"), modeViewIndication, "Documentation.")

				declarations = original.Split()

				self.assertTupleEqual(("a", ), declarations[0].Identifiers)
				self.assertTupleEqual(("b", ), declarations[1].Identifiers)
				self.assertIs(cls, type(declarations[1]))
				self.assertIsNone(declarations[1].Parent)
				self.assertEqual("Documentation.", declarations[1].Documentation)
				self.assertIs(modeViewIndication, original.ModeViewIndication)
				self.assertIsNot(modeViewIndication, declarations[1].ModeViewIndication)
				self.assertEqual("view1", declarations[1].ModeViewIndication.Name.Identifier)


class FileParameters(Testcase):
	def test_Split(self) -> None:
		subtype = _subtypeSymbol("text")
		original = ParameterFileInterfaceItem(("a", "b"), subtype, "Documentation.")

		declarations = original.Split()

		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(ParameterFileInterfaceItem, type(declarations[1]))
		self.assertIsNone(declarations[1].Parent)
		self.assertEqual("Documentation.", declarations[1].Documentation)
		self.assertIsNot(subtype, declarations[1].Subtype)


class SingleDeclarations(Testcase):
	def test_Split(self) -> None:
		"""Single declarations created before a split are dropped; each declaration has one afterwards."""
		original = _port("a", "b")
		before = original.SingleDeclarations

		declarations = original.Split()

		self.assertEqual(2, len(before))
		self.assertEqual(1, len(original.SingleDeclarations))
		self.assertIsNot(before[0], original.SingleDeclarations[0])
		self.assertEqual("a", original.SingleDeclarations[0].Identifier)
		self.assertEqual(1, len(declarations[1].SingleDeclarations))
		self.assertEqual("b", declarations[1].SingleDeclarations[0].Identifier)
		self.assertIs(declarations[1], declarations[1].SingleDeclarations[0].Declaration)

	def test_IterateSinglePortDeclarations(self) -> None:
		original = _port("a", "b")
		entity = Entity("e", portItems=[original])

		original.Split()

		self.assertListEqual(
			["a", "b"],
			[singleDeclaration.Identifier for singleDeclaration in entity.IterateSinglePortDeclarations()]
		)


class Generics(Testcase):
	def test_Split(self) -> None:
		first = _generic("FIRST")
		original = _generic("A", "B")
		last = _generic("LAST")
		entity = Entity("e", genericItems=[first, original, last])
		entity.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual([first, *declarations, last], entity.GenericItems)
		self.assertIs(entity, declarations[1].Parent)
		self.assertIs(declarations[0], entity._namespace._elements["a"])
		self.assertIs(declarations[1], entity._namespace._elements["b"])
		self.assertDictEqual(*_reindexed(entity))

	def test_Split_Component(self) -> None:
		original = _generic("A", "B")
		component = Component("c", genericItems=[original])

		declarations = original.Split()

		self.assertListEqual(list(declarations), component.GenericItems)
		self.assertIs(component, declarations[1].Parent)

	def test_Split_Group(self) -> None:
		"""The new generics follow the split generic in its generic group."""
		first = _generic("FIRST")
		original = _generic("A", "B")
		last = _generic("LAST")
		group = GenericGroup([first, original])
		other = GenericGroup([last])
		entity = Entity("e", genericItems=[first, original, last], genericGroups=[group, other])

		declarations = original.Split()

		self.assertListEqual([first, *declarations], group.GenericItems)
		self.assertListEqual([last], other.GenericItems)
		self.assertIs(entity, declarations[1].Parent)
		self.assertIs(group, declarations[1].Group)

	def test_Split_NotAChild(self) -> None:
		original = _generic("A", "B")
		entity = Entity("e")
		original.Parent = entity

		with self.assertRaises(NotAChildError) as context:
			original.Split()

		self.assertEqual("GenericConstantInterfaceItem 'A, B' is not a generic of this Entity.", str(context.exception))
		self.assertTupleEqual(("A", "B"), original.Identifiers)


class Ports(Testcase):
	def test_Split(self) -> None:
		first = _port("first")
		original = _port("a", "b", "c")
		entity = Entity("e", portItems=[first, original])
		entity.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual([first, *declarations], entity.PortItems)
		self.assertEqual(4, entity.PortCount)
		self.assertIs(entity, declarations[2].Parent)
		self.assertIs(declarations[0], entity._namespace._elements["a"])
		self.assertIs(declarations[1], entity._namespace._elements["b"])
		self.assertIs(declarations[2], entity._namespace._elements["c"])
		self.assertDictEqual(*_reindexed(entity))

	def test_Split_View(self) -> None:
		original = PortViewSignalInterfaceItem(("a", "b"), _modeView("view1"))
		entity = Entity("e", portItems=[original])
		entity.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual(list(declarations), entity.PortItems)
		self.assertIs(declarations[1], entity._namespace._elements["b"])

	def test_Split_NotIndexed(self) -> None:
		original = _port("a", "b")
		entity = Entity("e", portItems=[original])

		declarations = original.Split()

		self.assertListEqual(list(declarations), entity.PortItems)
		self.assertDictEqual({}, entity._namespace._elements)

	def test_Split_Component(self) -> None:
		original = _port("a", "b")
		component = Component("c", portItems=[original])

		declarations = original.Split()

		self.assertListEqual(list(declarations), component.PortItems)
		self.assertIs(component, declarations[1].Parent)

	def test_Split_Group(self) -> None:
		"""The new ports follow the split port in its port group."""
		first = _port("first")
		original = _port("a", "b")
		last = _port("last")
		group = PortGroup([first, original])
		other = PortGroup([last])
		entity = Entity("e", portItems=[first, original, last], portGroups=[group, other])

		declarations = original.Split()

		self.assertListEqual([first, *declarations], group.PortItems)
		self.assertListEqual([last], other.PortItems)
		self.assertIs(entity, declarations[1].Parent)
		self.assertIs(group, declarations[1].Group)

	def test_Split_NotAChild(self) -> None:
		original = _port("a", "b")
		entity = Entity("e")
		original.Parent = entity

		with self.assertRaises(NotAChildError) as context:
			original.Split()

		self.assertEqual("PortSimpleSignalInterfaceItem 'a, b' is not a port of this Entity.", str(context.exception))
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class Parameters(Testcase):
	def test_Split(self) -> None:
		original = _parameter("a", "b")
		procedure = Procedure("p", parameterItems=[original])
		procedure.IndexDeclaredItems()
		signature = procedure.Signature

		declarations = original.Split()

		self.assertListEqual(list(declarations), procedure.ParameterItems)
		self.assertIs(procedure, declarations[1].Parent)
		self.assertIs(declarations[0], procedure.Namespace._elements["a"])
		self.assertIs(declarations[1], procedure.Namespace._elements["b"])
		self.assertDictEqual(*_reindexed(procedure))
		self.assertIsNot(signature, procedure.Signature)
		self.assertTupleEqual(
			(declarations[0].Subtype, declarations[1].Subtype),
			procedure.Signature.ParameterTypes
		)

	def test_Split_Variable(self) -> None:
		original = ParameterVariableInterfaceItem(("a", "b"), Mode.InOut, _subtypeSymbol("natural"))
		procedure = Procedure("p", parameterItems=[original])
		procedure.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual(list(declarations), procedure.ParameterItems)
		self.assertIs(declarations[1], procedure.Namespace._elements["b"])

	def test_Split_SimpleSignal(self) -> None:
		original = ParameterSimpleSignalInterfaceItem(("a", "b"), Mode.In, _subtypeSymbol("bit"))
		procedure = Procedure("p", parameterItems=[original])
		procedure.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual(list(declarations), procedure.ParameterItems)
		self.assertIs(declarations[1], procedure.Namespace._elements["b"])

	def test_Split_ViewSignal(self) -> None:
		original = ParameterViewSignalInterfaceItem(("a", "b"), _modeView("view1"))
		procedure = Procedure("p", parameterItems=[original])
		procedure.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual(list(declarations), procedure.ParameterItems)
		self.assertIs(declarations[1], procedure.Namespace._elements["b"])

	def test_Split_File(self) -> None:
		original = ParameterFileInterfaceItem(("a", "b"), _subtypeSymbol("text"))
		procedure = Procedure("p", parameterItems=[original])
		procedure.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual(list(declarations), procedure.ParameterItems)
		self.assertIs(declarations[1], procedure.Namespace._elements["b"])

	def test_Split_Group(self) -> None:
		"""The new parameters follow the split parameter in its parameter group."""
		first = _parameter("first")
		original = _parameter("a", "b")
		last = _parameter("last")
		group = ParameterGroup([first, original])
		other = ParameterGroup([last])
		procedure = Procedure("p", parameterItems=[first, original, last], parameterGroups=[group, other])

		declarations = original.Split()

		self.assertListEqual([first, *declarations], group.ParameterItems)
		self.assertListEqual([last], other.ParameterItems)
		self.assertIs(procedure, declarations[1].Parent)
		self.assertIs(group, declarations[1].Group)

	def test_Split_NotAChild(self) -> None:
		original = _parameter("a", "b")
		procedure = Procedure("p")
		original.Parent = procedure

		with self.assertRaises(NotAChildError) as context:
			original.Split()

		self.assertEqual(
			"ParameterConstantInterfaceItem 'a, b' is not a parameter of this Procedure.",
			str(context.exception)
		)
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class ModeViewElements(Testcase):
	def test_Split_Simple(self) -> None:
		original = SimpleModeViewElement(("a", "b"), Mode.Out, "Documentation.")

		declarations = original.Split()

		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(SimpleModeViewElement, type(declarations[1]))
		self.assertIsNone(declarations[1].Parent)
		self.assertIs(Mode.Out, declarations[1].Mode)
		self.assertEqual("Documentation.", declarations[1].Documentation)

	def test_Split_Composite(self) -> None:
		modeViewName = _modeView("inner")
		original = CompositeModeViewElement(("a", "b"), modeViewName)

		declarations = original.Split()

		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(CompositeModeViewElement, type(declarations[1]))
		self.assertIs(modeViewName, original.ModeViewName)
		self.assertIsNot(modeViewName, declarations[1].ModeViewName)
		self.assertIs(declarations[1], declarations[1].ModeViewName.Parent)

	def test_Split_ModeViewDeclaration(self) -> None:
		first = SimpleModeViewElement(("first", ), Mode.In)
		original = SimpleModeViewElement(("a", "b"), Mode.Out)
		modeView = ModeViewDeclaration("view1", _subtypeSymbol("frame"), [first, original])

		declarations = original.Split()

		self.assertListEqual([first, *declarations], modeView.Elements)
		self.assertIs(modeView, declarations[1].Parent)

	def test_Split_NotAChild(self) -> None:
		original = SimpleModeViewElement(("a", "b"), Mode.Out)
		modeView = ModeViewDeclaration("view1", _subtypeSymbol("frame"))
		original.Parent = modeView

		with self.assertRaises(NotAChildError) as context:
			original.Split()

		self.assertEqual(
			"SimpleModeViewElement 'a, b' is not an element of this ModeViewDeclaration.",
			str(context.exception)
		)
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class SplitGenericItem(Testcase):
	def test_Split(self) -> None:
		original = _generic("a", "b")
		container = Entity("e", genericItems=[original])

		declarations = container.SplitGenericItem(original)

		self.assertIs(original, declarations[0])
		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(container, declarations[1].Parent)

	def test_Split_Type(self) -> None:
		"""A generic type declares one identifier and is returned unchanged."""
		original = GenericTypeInterfaceItem("T")
		container = Entity("e", genericItems=[original])

		self.assertTupleEqual((original, ), container.SplitGenericItem(original))

	def test_Split_None(self) -> None:
		container = Entity("e")

		with self.assertRaises(ValueError) as context:
			container.SplitGenericItem(None)

		self.assertEqual("Parameter 'genericItem' is None.", str(context.exception))

	def test_Split_WrongType(self) -> None:
		container = Entity("e")

		with self.assertRaises(TypeError) as context:
			container.SplitGenericItem(_port("p"))

		self.assertEqual("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Split_NotAChild(self) -> None:
		original = _generic("a", "b")
		container = Entity("e")

		with self.assertRaises(NotAChildError) as context:
			container.SplitGenericItem(original)

		self.assertEqual("GenericConstantInterfaceItem 'a, b' is not a generic of this Entity.", str(context.exception))
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class SplitPortItem(Testcase):
	def test_Split(self) -> None:
		original = _port("a", "b")
		container = Entity("e", portItems=[original])

		declarations = container.SplitPortItem(original)

		self.assertIs(original, declarations[0])
		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(container, declarations[1].Parent)

	def test_Split_OneIdentifier(self) -> None:
		"""A port declaring one identifier is returned unchanged."""
		original = _port("a")
		container = Entity("e", portItems=[original])

		self.assertTupleEqual((original, ), container.SplitPortItem(original))

	def test_Split_None(self) -> None:
		container = Entity("e")

		with self.assertRaises(ValueError) as context:
			container.SplitPortItem(None)

		self.assertEqual("Parameter 'portItem' is None.", str(context.exception))

	def test_Split_WrongType(self) -> None:
		container = Entity("e")

		with self.assertRaises(TypeError) as context:
			container.SplitPortItem(_generic("G"))

		self.assertEqual("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Split_NotAChild(self) -> None:
		original = _port("a", "b")
		container = Entity("e")

		with self.assertRaises(NotAChildError) as context:
			container.SplitPortItem(original)

		self.assertEqual("PortSimpleSignalInterfaceItem 'a, b' is not a port of this Entity.", str(context.exception))
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class SplitParameterItem(Testcase):
	def test_Split(self) -> None:
		original = _parameter("a", "b")
		container = Procedure("p", parameterItems=[original])

		declarations = container.SplitParameterItem(original)

		self.assertIs(original, declarations[0])
		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(container, declarations[1].Parent)

	def test_Split_OneIdentifier(self) -> None:
		"""A parameter declaring one identifier is returned unchanged."""
		original = _parameter("a")
		container = Procedure("p", parameterItems=[original])

		self.assertTupleEqual((original, ), container.SplitParameterItem(original))

	def test_Split_None(self) -> None:
		container = Procedure("p")

		with self.assertRaises(ValueError) as context:
			container.SplitParameterItem(None)

		self.assertEqual("Parameter 'parameterItem' is None.", str(context.exception))

	def test_Split_WrongType(self) -> None:
		container = Procedure("p")

		with self.assertRaises(TypeError) as context:
			container.SplitParameterItem(_port("p"))

		self.assertEqual("Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Split_NotAChild(self) -> None:
		original = _parameter("a", "b")
		container = Procedure("p")

		with self.assertRaises(NotAChildError) as context:
			container.SplitParameterItem(original)

		self.assertEqual(
			"ParameterConstantInterfaceItem 'a, b' is not a parameter of this Procedure.",
			str(context.exception)
		)
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class SplitModeViewElement(Testcase):
	def test_Split(self) -> None:
		original = SimpleModeViewElement(("a", "b"), Mode.Out)
		container = ModeViewDeclaration("view1", _subtypeSymbol("frame"), [original])

		declarations = container.SplitElement(original)

		self.assertIs(original, declarations[0])
		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].Identifiers)
		self.assertIs(container, declarations[1].Parent)

	def test_Split_OneIdentifier(self) -> None:
		"""An element declaring one identifier is returned unchanged."""
		original = SimpleModeViewElement(("a", ), Mode.Out)
		container = ModeViewDeclaration("view1", _subtypeSymbol("frame"), [original])

		self.assertTupleEqual((original, ), container.SplitElement(original))

	def test_Split_None(self) -> None:
		container = ModeViewDeclaration("view1", _subtypeSymbol("frame"))

		with self.assertRaises(ValueError) as context:
			container.SplitElement(None)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_Split_WrongType(self) -> None:
		container = ModeViewDeclaration("view1", _subtypeSymbol("frame"))

		with self.assertRaises(TypeError) as context:
			container.SplitElement(_port("p"))

		self.assertEqual("Parameter 'element' is not of type 'ModeViewElement'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Split_NotAChild(self) -> None:
		original = SimpleModeViewElement(("a", "b"), Mode.Out)
		container = ModeViewDeclaration("view1", _subtypeSymbol("frame"))

		with self.assertRaises(NotAChildError) as context:
			container.SplitElement(original)

		self.assertEqual(
			"SimpleModeViewElement 'a, b' is not an element of this ModeViewDeclaration.",
			str(context.exception)
		)
		self.assertTupleEqual(("a", "b"), original.Identifiers)
