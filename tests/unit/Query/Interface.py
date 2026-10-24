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
"""Tests for single declarations: one view per identifier declared by a generic, port or parameter."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.DesignUnit import Entity
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Interface  import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                   PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                   ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                   ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                   ParameterFileInterfaceItem, ParameterGroup, SingleGenericConstantDeclaration, \
                                   SinglePortSimpleSignalDeclaration, SinglePortViewSignalDeclaration, \
                                   SingleParameterConstantDeclaration, SingleParameterVariableDeclaration, \
                                   SingleParameterSimpleSignalDeclaration, SingleParameterViewSignalDeclaration, \
                                   SingleParameterFileDeclaration
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import ModeViewSymbol

from tests.unit             import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SingleGenerics(Testcase):
	def test_Constant(self) -> None:
		"""``generic (WIDTH, DEPTH : positive := 8)`` yields one single declaration per identifier."""
		subtype = _subtypeSymbol("positive")
		default = IntegerLiteral(8)
		generic = GenericConstantInterfaceItem(("WIDTH", "DEPTH"), Mode.In, subtype, default, documentation="Sizes.")
		entity =  Entity("ent", genericItems=[generic])

		singleGenerics = list(entity.IterateSingleGenericDeclarations())

		self.assertEqual(2, len(singleGenerics))
		for position, singleGeneric in enumerate(singleGenerics):
			self.assertIsInstance(singleGeneric, SingleGenericConstantDeclaration)
			self.assertIs(generic, singleGeneric.Parent)
			self.assertIs(generic, singleGeneric.Declaration)
			self.assertEqual(position, singleGeneric.Position)
			self.assertIs(Mode.In, singleGeneric.Mode)
			self.assertIs(subtype, singleGeneric.Subtype)
			self.assertIs(default, singleGeneric.DefaultExpression)
			self.assertEqual("Sizes.", singleGeneric.Documentation)

		self.assertEqual("WIDTH", singleGenerics[0].Identifier)
		self.assertEqual("width", singleGenerics[0].NormalizedIdentifier)
		self.assertEqual("DEPTH", str(singleGenerics[1]))

	def test_Type(self) -> None:
		"""A generic type declares exactly one identifier and is yielded itself."""
		generic = GenericTypeInterfaceItem("T")
		entity =  Entity("ent", genericItems=[generic])

		self.assertListEqual([generic], list(entity.IterateSingleGenericDeclarations()))

	def test_DeclarationOrder(self) -> None:
		generics = [
			GenericConstantInterfaceItem(("A", "B"), Mode.In, _subtypeSymbol("positive")),
			GenericTypeInterfaceItem("T"),
			GenericConstantInterfaceItem(("C", ), Mode.In, _subtypeSymbol("natural")),
		]
		entity = Entity("ent", genericItems=generics)

		identifiers = [generic.Identifier for generic in entity.IterateSingleGenericDeclarations()]

		self.assertListEqual(["A", "B", "T", "C"], identifiers)

	def test_Predicate(self) -> None:
		typeGeneric = GenericTypeInterfaceItem("T")
		generics = [
			GenericConstantInterfaceItem(("A", "B"), Mode.In, _subtypeSymbol("positive")),
			typeGeneric,
		]
		entity = Entity("ent", genericItems=generics)

		def isSecondOrNoConstant(generic: SingleGenericConstantDeclaration | GenericTypeInterfaceItem) -> bool:
			return not isinstance(generic, SingleGenericConstantDeclaration) or generic.Position == 1

		singleGenerics = list(entity.IterateSingleGenericDeclarations(isSecondOrNoConstant))

		self.assertEqual(2, len(singleGenerics))
		self.assertEqual("B", singleGenerics[0].Identifier)
		self.assertIs(typeGeneric, singleGenerics[1])

	def test_NoGenerics(self) -> None:
		self.assertListEqual([], list(Entity("ent").IterateSingleGenericDeclarations()))

	def test_NotInModel(self) -> None:
		"""A single declaration isn't added to its declaration nor to the entity."""
		generic = GenericConstantInterfaceItem(("A", "B"), Mode.In, _subtypeSymbol("positive"))
		entity =  Entity("ent", genericItems=[generic])

		_ = list(entity.IterateSingleGenericDeclarations())

		self.assertListEqual([generic], entity.GenericItems)
		self.assertIs(entity, generic.Parent)
		self.assertTupleEqual(("A", "B"), generic.Identifiers)


class SinglePorts(Testcase):
	def test_SimpleSignal(self) -> None:
		"""``port (a, b : out bit := '0')`` yields one single declaration per identifier."""
		subtype = _subtypeSymbol("bit")
		default = IntegerLiteral(0)
		port =    PortSimpleSignalInterfaceItem(("a", "b"), Mode.Out, subtype, default)
		entity =  Entity("ent", portItems=[port])

		singlePorts = list(entity.IterateSinglePortDeclarations())

		self.assertEqual(2, len(singlePorts))
		for position, singlePort in enumerate(singlePorts):
			self.assertIsInstance(singlePort, SinglePortSimpleSignalDeclaration)
			self.assertIs(port, singlePort.Declaration)
			self.assertEqual(position, singlePort.Position)
			self.assertIs(Mode.Out, singlePort.Mode)
			self.assertIs(subtype, singlePort.Subtype)
			self.assertIs(default, singlePort.DefaultExpression)

		self.assertListEqual(["a", "b"], [singlePort.Identifier for singlePort in singlePorts])

	def test_ViewSignal(self) -> None:
		modeView = ModeViewSymbol(SimpleName("MyView"))
		port =     PortViewSignalInterfaceItem(("p", "q"), modeView)
		entity =   Entity("ent", portItems=[port])

		singlePorts = list(entity.IterateSinglePortDeclarations())

		self.assertEqual(2, len(singlePorts))
		for singlePort in singlePorts:
			self.assertIsInstance(singlePort, SinglePortViewSignalDeclaration)
			self.assertIs(modeView, singlePort.ModeViewIndication)
			self.assertIs(modeView, singlePort.Subtype)
			self.assertFalse(hasattr(singlePort, "Mode"))

	def test_Predicate(self) -> None:
		port =   PortSimpleSignalInterfaceItem(("a", "b", "c"), Mode.In, _subtypeSymbol("bit"))
		entity = Entity("ent", portItems=[port])

		def isNotB(singlePort: SinglePortSimpleSignalDeclaration) -> bool:
			return singlePort.NormalizedIdentifier != "b"

		singlePorts = list(entity.IterateSinglePortDeclarations(isNotB))

		self.assertListEqual(["a", "c"], [singlePort.Identifier for singlePort in singlePorts])

	def test_NoPorts(self) -> None:
		self.assertListEqual([], list(Entity("ent").IterateSinglePortDeclarations()))


class SingleParameters(Testcase):
	def test_Constant(self) -> None:
		subtype =   _subtypeSymbol("integer")
		parameter = ParameterConstantInterfaceItem(("a", "b"), Mode.In, subtype)
		group =     ParameterGroup([parameter])

		singleParameters = list(group.IterateSingleParameterDeclarations())

		self.assertEqual(2, len(singleParameters))
		for singleParameter in singleParameters:
			self.assertIsInstance(singleParameter, SingleParameterConstantDeclaration)
			self.assertIs(parameter, singleParameter.Declaration)
			self.assertIs(Mode.In, singleParameter.Mode)
			self.assertIs(subtype, singleParameter.Subtype)
			self.assertIsNone(singleParameter.DefaultExpression)

	def test_Variable(self) -> None:
		group = ParameterGroup([ParameterVariableInterfaceItem(("v", ), Mode.InOut, _subtypeSymbol("integer"))])

		singleParameters = list(group.IterateSingleParameterDeclarations())

		self.assertEqual(1, len(singleParameters))
		self.assertIsInstance(singleParameters[0], SingleParameterVariableDeclaration)
		self.assertIs(Mode.InOut, singleParameters[0].Mode)

	def test_SimpleSignal(self) -> None:
		group = ParameterGroup([ParameterSimpleSignalInterfaceItem(("s", ), Mode.In, _subtypeSymbol("bit"))])

		singleParameters = list(group.IterateSingleParameterDeclarations())

		self.assertEqual(1, len(singleParameters))
		self.assertIsInstance(singleParameters[0], SingleParameterSimpleSignalDeclaration)
		self.assertIs(Mode.In, singleParameters[0].Mode)

	def test_ViewSignal(self) -> None:
		modeView = ModeViewSymbol(SimpleName("MyView"))
		group =    ParameterGroup([ParameterViewSignalInterfaceItem(("s", ), modeView)])

		singleParameters = list(group.IterateSingleParameterDeclarations())

		self.assertEqual(1, len(singleParameters))
		self.assertIsInstance(singleParameters[0], SingleParameterViewSignalDeclaration)
		self.assertIs(modeView, singleParameters[0].ModeViewIndication)

	def test_File(self) -> None:
		subtype = _subtypeSymbol("text")
		group =   ParameterGroup([ParameterFileInterfaceItem(("f", "g"), subtype)])

		singleParameters = list(group.IterateSingleParameterDeclarations())

		self.assertEqual(2, len(singleParameters))
		for singleParameter in singleParameters:
			self.assertIsInstance(singleParameter, SingleParameterFileDeclaration)
			self.assertIs(subtype, singleParameter.Subtype)
			self.assertFalse(hasattr(singleParameter, "Mode"))
			self.assertFalse(hasattr(singleParameter, "DefaultExpression"))

	def test_Predicate(self) -> None:
		parameters = [
			ParameterConstantInterfaceItem(("a", "b"), Mode.In, _subtypeSymbol("integer")),
			ParameterFileInterfaceItem(("f", ), _subtypeSymbol("text")),
		]
		group = ParameterGroup(parameters)

		def isFile(singleParameter: SingleParameterConstantDeclaration | SingleParameterFileDeclaration) -> bool:
			return isinstance(singleParameter, SingleParameterFileDeclaration)

		singleParameters = list(group.IterateSingleParameterDeclarations(isFile))

		self.assertListEqual(["f"], [singleParameter.Identifier for singleParameter in singleParameters])


class Cache(Testcase):
	def test_SingleDeclarations(self) -> None:
		"""The single declarations are created on first access, one per identifier in list order, and kept."""
		port = PortSimpleSignalInterfaceItem(("Clock", "Reset"), Mode.In, _subtypeSymbol("bit"))

		singleDeclarations = port.SingleDeclarations

		self.assertEqual(2, len(singleDeclarations))
		self.assertIs(singleDeclarations, port.SingleDeclarations)
		for position, singleDeclaration in enumerate(singleDeclarations):
			self.assertIsInstance(singleDeclaration, SinglePortSimpleSignalDeclaration)
			self.assertIs(port, singleDeclaration.Parent)
			self.assertEqual(position, singleDeclaration.Position)

		self.assertEqual("Reset", singleDeclarations[1].Identifier)
		self.assertEqual("reset", singleDeclarations[1].NormalizedIdentifier)

	def test_IterateTwice(self) -> None:
		"""Iterating twice yields the same single declarations."""
		port =   PortSimpleSignalInterfaceItem(("a", "b"), Mode.In, _subtypeSymbol("bit"))
		entity = Entity("ent", portItems=[port])

		first =  list(entity.IterateSinglePortDeclarations())
		second = list(entity.IterateSinglePortDeclarations())

		self.assertEqual(2, len(second))
		for singlePort, again in zip(first, second):
			self.assertIs(singlePort, again)


class Construction(Testcase):
	def test_Fields(self) -> None:
		port = PortSimpleSignalInterfaceItem(("Clock", "Reset"), Mode.In, _subtypeSymbol("bit"))

		singlePort = SinglePortSimpleSignalDeclaration("Reset", "reset", 1, parent=port)

		self.assertEqual("Reset", singlePort.Identifier)
		self.assertEqual("reset", singlePort.NormalizedIdentifier)
		self.assertEqual(1, singlePort.Position)
		self.assertIs(port, singlePort.Declaration)

	def test_Parent_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = SinglePortSimpleSignalDeclaration("a", "a", 0, parent=None)

		self.assertEqual("Parameter 'parent' is None.", str(context.exception))

	def test_Parent_Type(self) -> None:
		"""A single declaration accepts only the declaration class it represents."""
		generic = GenericConstantInterfaceItem(("a", ), Mode.In, _subtypeSymbol("bit"))

		with self.assertRaises(TypeError) as context:
			_ = SinglePortSimpleSignalDeclaration("a", "a", 0, parent=generic)

		self.assertEqual("Parameter 'parent' is not of type 'PortSimpleSignalInterfaceItem'.", str(context.exception))
		notes = ["Got type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."]
		self.assertListEqual(notes, context.exception.__notes__)
