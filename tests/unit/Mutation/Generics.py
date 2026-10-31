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
Mutation tests for generic clauses (:class:`~pyVHDLModel.Regions.WithGenericsMixin`).

The mutators are tested on an entity and a subprogram (declarative regions with a namespace) and a component (no
namespace). The generic groups of the language construct stay a partition of its generic clause.
"""
from pyTooling.MetaClasses  import UnfulfilledExpectationError
from pyTooling.Warning      import WarningCollector
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import ModelEntity
from pyVHDLModel.DesignUnit import Component, Entity
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicateGenericError, NotInNamespaceError
from pyVHDLModel.Interface  import GenericTypeInterfaceItem, GenericFunctionInterfaceItem, GenericGroup
from pyVHDLModel.Regions    import WithGenericsMixin
from pyVHDLModel.Subprogram import Procedure

from tests.unit             import _subtypeSymbol
from tests.unit.Mutation    import _generic, _port, _reindexed


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Generics(Testcase):
	def test_Add(self) -> None:
		entity = Entity("e")
		bits = _generic("BITS")
		depth = _generic("DEPTH")

		entity.AddGenericItem(bits)
		entity.AddGenericItem(depth)

		self.assertListEqual([bits, depth], entity.GenericItems)
		self.assertEqual(2, entity.GenericCount)
		self.assertIs(entity, bits.Parent)
		self.assertIs(entity, depth.Parent)

	def test_Add_Constructed(self) -> None:
		"""A generic added after construction goes behind the generics given to the constructor."""
		bits = _generic("BITS")
		entity = Entity("e", genericItems=[bits])
		depth = _generic("DEPTH")

		entity.AddGenericItem(depth)

		self.assertListEqual([bits, depth], entity.GenericItems)

	def test_Add_Component(self) -> None:
		component = Component("c")
		bits = _generic("BITS")

		component.AddGenericItem(bits)

		self.assertListEqual([bits], component.GenericItems)
		self.assertIs(component, bits.Parent)

	def test_Add_Subprogram(self) -> None:
		procedure = Procedure("p")
		procedure.IndexDeclaredItems()
		bits = _generic("BITS")

		procedure.AddGenericItem(bits)

		self.assertListEqual([bits], procedure.GenericItems)
		self.assertEqual(1, procedure.GenericCount)
		self.assertIs(procedure, bits.Parent)
		self.assertIs(bits, procedure._namespace._elements["bits"])

	def test_Add_Type(self) -> None:
		entity = Entity("e")
		typeItem = GenericTypeInterfaceItem("T")

		entity.AddGenericItem(typeItem)

		self.assertListEqual([typeItem], entity.GenericItems)
		self.assertIs(entity, typeItem.Parent)

	def test_Add_None(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.AddGenericItem(None)

		self.assertEqual("Parameter 'genericItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.AddGenericItem(_port("Clock"))

		self.assertEqual("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertEqual(0, entity.GenericCount)

	def test_Add_AlreadyInDesign(self) -> None:
		bits = _generic("BITS")
		first = Entity("e1", genericItems=[bits])
		entity = Entity("e2")

		with self.assertRaises(AlreadyInDesignError) as context:
			entity.AddGenericItem(bits)

		self.assertEqual("GenericConstantInterfaceItem 'BITS' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Entity first."], context.exception.__notes__)
		self.assertIs(bits, context.exception.Element)
		self.assertIs(first, context.exception.Parent)
		self.assertEqual(0, entity.GenericCount)

	def test_Add_Twice(self) -> None:
		entity = Entity("e")
		bits = _generic("BITS")
		entity.AddGenericItem(bits)

		with self.assertRaises(AlreadyInDesignError):
			entity.AddGenericItem(bits)

		self.assertListEqual([bits], entity.GenericItems)

	def test_Add_Duplicate(self) -> None:
		bits = _generic("BITS")
		entity = Entity("e", genericItems=[bits])
		duplicate = _generic("Depth", "bits")

		with self.assertRaises(DuplicateGenericError) as context:
			entity.AddGenericItem(duplicate)

		self.assertEqual("Entity already declares 'bits'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertEqual("bits", context.exception.Identifier)
		self.assertEqual("bits", context.exception.NormalizedIdentifier)
		self.assertIs(entity, context.exception.Parent)
		self.assertIs(duplicate, context.exception.Element)
		self.assertIs(bits, context.exception.Existing)
		self.assertEqual(1, entity.GenericCount)
		self.assertIsNone(duplicate.Parent)
		self.assertNotIn("depth", entity._namespace._elements)

	def test_Insert_Start(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])
		width = _generic("WIDTH")

		entity.InsertGenericItem(0, width)

		self.assertListEqual([width, bits, depth], entity.GenericItems)
		self.assertIs(entity, width.Parent)

	def test_Insert_Middle(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])
		width = _generic("WIDTH")

		entity.InsertGenericItem(1, width)

		self.assertListEqual([bits, width, depth], entity.GenericItems)

	def test_Insert_End(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])
		width = _generic("WIDTH")

		entity.InsertGenericItem(2, width)

		self.assertListEqual([bits, depth, width], entity.GenericItems)

	def test_Insert_OutOfRange(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])
		width = _generic("WIDTH")

		with self.assertRaises(ValueError) as context:
			entity.InsertGenericItem(2, width)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)
		self.assertEqual(1, entity.GenericCount)
		self.assertIsNone(width.Parent)

	def test_Insert_Negative(self) -> None:
		bits =  _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])
		width = _generic("WIDTH")

		entity.InsertGenericItem(-1, width)

		self.assertListEqual([bits, width, depth], entity.GenericItems)
		self.assertIs(entity, width.Parent)

	def test_Insert_Negative_Start(self) -> None:
		bits =  _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])
		width = _generic("WIDTH")

		entity.InsertGenericItem(-2, width)

		self.assertListEqual([width, bits, depth], entity.GenericItems)

	def test_Insert_Negative_OutOfRange(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])
		width = _generic("WIDTH")

		with self.assertRaises(ValueError) as context:
			entity.InsertGenericItem(-2, width)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertEqual(1, entity.GenericCount)
		self.assertIsNone(width.Parent)

	def test_Insert_IndexNone(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.InsertGenericItem(None, _generic("WIDTH"))

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Insert_IndexWrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.InsertGenericItem("0", _generic("WIDTH"))

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Remove(self) -> None:
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits, depth])

		entity.RemoveGenericItem(bits)

		self.assertListEqual([depth], entity.GenericItems)
		self.assertIsNone(bits.Parent)
		self.assertTupleEqual(("BITS", ), bits.Identifiers)
		self.assertEqual("positive", bits.Subtype.Name.Identifier)

	def test_Remove_AddElsewhere(self) -> None:
		bits = _generic("BITS")
		entity = Entity("e1", genericItems=[bits])
		other = Entity("e2")

		entity.RemoveGenericItem(bits)
		other.AddGenericItem(bits)

		self.assertEqual(0, entity.GenericCount)
		self.assertListEqual([bits], other.GenericItems)
		self.assertIs(other, bits.Parent)

	def test_Remove_None(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.RemoveGenericItem(None)

		self.assertEqual("Parameter 'genericItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.RemoveGenericItem(_port("Clock"))

		self.assertEqual("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Remove_NotAChild(self) -> None:
		bits = _generic("BITS")
		Entity("e1", genericItems=[bits])
		entity = Entity("e2", genericItems=[_generic("BITS")])

		with self.assertRaises(NotAChildError) as context:
			entity.RemoveGenericItem(bits)

		self.assertEqual("GenericConstantInterfaceItem 'BITS' is not a generic of this Entity.", str(context.exception))
		self.assertIs(bits, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)
		self.assertEqual(1, entity.GenericCount)
		self.assertIsNotNone(bits.Parent)

	def test_Remove_Twice(self) -> None:
		bits = _generic("BITS")
		entity = Entity("e", genericItems=[bits])
		entity.RemoveGenericItem(bits)

		with self.assertRaises(NotAChildError):
			entity.RemoveGenericItem(bits)

	def test_Move(self) -> None:
		"""A move within one generic clause is a remove followed by an insert."""
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		width = _generic("WIDTH")
		entity = Entity("e", genericItems=[bits, depth, width])
		entity.IndexDeclaredItems()

		entity.RemoveGenericItem(width)
		entity.InsertGenericItem(0, width)

		self.assertListEqual([width, bits, depth], entity.GenericItems)
		self.assertIs(entity, width.Parent)
		self.assertIs(width, entity._namespace._elements["width"])

	def test_Move_Elsewhere(self) -> None:
		bits = _generic("BITS")
		entity = Entity("e")
		entity.AddGenericItem(bits)
		component = Component("c", genericItems=[_generic("DEPTH")])

		entity.RemoveGenericItem(bits)
		component.InsertGenericItem(0, bits)

		self.assertEqual(0, entity.GenericCount)
		self.assertNotIn("bits", entity._namespace._elements)
		self.assertIs(bits, component.GenericItems[0])
		self.assertIs(component, bits.Parent)

	def test_Namespace(self) -> None:
		entity = Entity("e")
		entity.IndexDeclaredItems()
		item = _generic("BITS", "Depth")

		entity.AddGenericItem(item)

		self.assertIs(item, entity._namespace._elements["bits"])
		self.assertIs(item, entity._namespace._elements["depth"])

		entity.RemoveGenericItem(item)

		self.assertNotIn("bits", entity._namespace._elements)
		self.assertNotIn("depth", entity._namespace._elements)

	def test_Namespace_Indexed(self) -> None:
		"""Re-indexing after a mutation neither duplicates nor revives entries."""
		bits = _generic("BITS")
		depth = _generic("DEPTH")
		entity = Entity("e", genericItems=[bits])
		entity.IndexDeclaredItems()

		entity.AddGenericItem(depth)
		entity.RemoveGenericItem(bits)
		entity.IndexDeclaredItems()

		self.assertDictEqual({"depth": depth}, entity._namespace._elements)

	def test_Namespace_AddNotIndexed(self) -> None:
		"""A generic added to a region, which wasn't indexed yet, enters the namespace when the region is indexed."""
		entity = Entity("e")
		bits = _generic("BITS")

		entity.AddGenericItem(bits)

		self.assertDictEqual({}, entity._namespace._elements)

		entity.IndexDeclaredItems()

		self.assertDictEqual({"bits": bits}, entity._namespace._elements)

	def test_Namespace_OtherElement(self) -> None:
		"""Removing a generic, whose identifier refers to a duplicate declaration in the namespace, is rejected."""
		bits = _generic("BITS")
		port = _port("bits")
		entity = Entity("e", genericItems=[bits], portItems=[port])
		with WarningCollector():
			entity.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			entity.RemoveGenericItem(bits)

		self.assertEqual("Namespace 'e' has another element for 'bits'.", str(context.exception))
		self.assertListEqual(
			["Found element of type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertEqual("BITS", context.exception.Identifier)
		self.assertEqual("bits", context.exception.NormalizedIdentifier)
		self.assertIs(entity._namespace, context.exception.Namespace)
		self.assertListEqual([bits], entity.GenericItems)
		self.assertIs(entity, bits.Parent)
		self.assertIs(port, entity._namespace._elements["bits"])

	def test_Namespace_NotIndexed(self) -> None:
		"""Removing a generic of a region, which wasn't indexed yet, leaves the namespace as is."""
		bits = _generic("BITS")
		entity = Entity("e", genericItems=[bits])

		entity.RemoveGenericItem(bits)

		self.assertEqual(0, entity.GenericCount)
		self.assertIsNone(bits.Parent)
		self.assertDictEqual({}, entity._namespace._elements)

	def test_Contract(self) -> None:
		"""A host class without the methods expected by the mixin can't be instantiated."""
		class Host(ModelEntity, WithGenericsMixin):
			def __init__(self) -> None:
				super().__init__()
				WithGenericsMixin.__init__(self)

		with self.assertRaises(UnfulfilledExpectationError) as context:
			Host()

		self.assertEqual("Class 'Host' doesn't provide every expected member.", str(context.exception))
		self.assertListEqual(
			[
				"Missing '_AddToNamespace', expected by 'WithGenericsMixin'.",
				"Missing '_RemoveFromNamespace', expected by 'WithGenericsMixin'.",
				"Missing '_ClashingDeclarations', expected by 'WithGenericsMixin'.",
			],
			context.exception.__notes__
		)


class GenericGroups(Testcase):
	def _Entity(self) -> tuple[Entity, GenericGroup, GenericGroup, GenericGroup]:
		"""Return an entity with the generic groups ``WIDTH, DEPTH | IN_WIDTH, IN_DEPTH | DEBUG``."""
		sizes = GenericGroup([_generic("WIDTH"), _generic("DEPTH")])
		inbound =  GenericGroup([_generic("IN_WIDTH"), _generic("IN_DEPTH")], name="In")
		debugging =   GenericGroup([_generic("DEBUG")])
		entity =   Entity("e", genericItems=[*sizes, *inbound, *debugging], genericGroups=[sizes, inbound, debugging])

		return entity, sizes, inbound, debugging

	def assertPartition(self, entity: Entity) -> None:
		"""Assert the generic groups list every generic once, in declaration order, and each generic refers to its group."""
		self.assertListEqual(entity.GenericItems, [generic for group in entity.GenericGroups for generic in group])
		for group in entity.GenericGroups:
			self.assertIs(entity, group.Parent)
			self.assertGreater(len(group), 0)
			for generic in group:
				self.assertIs(group, generic.Group)

	def test_Add(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		trace = _generic("TRACE")

		entity.AddGenericItem(trace)

		self.assertIs(debugging, trace.Group)
		self.assertListEqual([sizes, inbound, debugging], entity.GenericGroups)
		self.assertPartition(entity)

	def test_Add_NoGenerics(self) -> None:
		entity = Entity("e")
		width = _generic("WIDTH")

		entity.AddGenericItem(width)

		self.assertEqual(1, len(entity.GenericGroups))
		self.assertIsNone(entity.GenericGroups[0].Identifier)
		self.assertListEqual([width], entity.GenericGroups[0].GenericItems)
		self.assertPartition(entity)

	def test_Add_Group(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inLatency = _generic("IN_LATENCY")

		entity.AddGenericItem(inLatency, inbound)

		self.assertIs(inbound, inLatency.Group)
		self.assertIs(inLatency, inbound.GenericItems[-1])
		self.assertIs(inLatency, entity.GenericItems[4])
		self.assertPartition(entity)

	def test_Add_Group_Foreign(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		other, _, otherInbound, _ = self._Entity()
		inLatency = _generic("IN_LATENCY")

		with self.assertRaises(NotAChildError) as context:
			entity.AddGenericItem(inLatency, otherInbound)

		self.assertEqual("GenericGroup 'In' is not a generic group of this Entity.", str(context.exception))
		self.assertIs(otherInbound, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)
		self.assertIsNone(inLatency.Parent)
		self.assertIsNone(inLatency.Group)

	def test_Insert_Middle(self) -> None:
		"""Without a generic group, the generic joins the generic group of the generic before it."""
		entity, sizes, inbound, debugging = self._Entity()
		size = _generic("SIZE")

		entity.InsertGenericItem(2, size)

		self.assertIs(sizes, size.Group)
		self.assertListEqual(["WIDTH", "DEPTH", "SIZE"], [generic.Identifiers[0] for generic in sizes])
		self.assertPartition(entity)

	def test_Insert_Start(self) -> None:
		"""At index 0, the generic joins the generic group of the first generic."""
		entity, sizes, inbound, debugging = self._Entity()
		size = _generic("SIZE")

		entity.InsertGenericItem(0, size)

		self.assertIs(sizes, size.Group)
		self.assertIs(size, sizes.GenericItems[0])
		self.assertPartition(entity)

	def test_Insert_Negative(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		size = _generic("SIZE")

		entity.InsertGenericItem(-1, size)

		self.assertIs(inbound, size.Group)
		self.assertIs(size, entity.GenericItems[4])
		self.assertPartition(entity)

	def test_Insert_Group(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inLatency = _generic("IN_LATENCY")

		entity.InsertGenericItem(3, inLatency, inbound)

		self.assertIs(inbound, inLatency.Group)
		self.assertListEqual(["IN_WIDTH", "IN_LATENCY", "IN_DEPTH"], [generic.Identifiers[0] for generic in inbound])
		self.assertPartition(entity)

	def test_Insert_Group_Start(self) -> None:
		"""A generic group given takes a generic at its start, although the generic before is in another generic group."""
		entity, sizes, inbound, debugging = self._Entity()
		inLatency = _generic("IN_LATENCY")

		entity.InsertGenericItem(2, inLatency, inbound)

		self.assertIs(inbound, inLatency.Group)
		self.assertIs(inLatency, inbound.GenericItems[0])
		self.assertPartition(entity)

	def test_Insert_Group_End(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inLatency = _generic("IN_LATENCY")

		entity.InsertGenericItem(4, inLatency, inbound)

		self.assertIs(inbound, inLatency.Group)
		self.assertIs(inLatency, inbound.GenericItems[-1])
		self.assertPartition(entity)

	def test_Insert_Group_Outside(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inLatency = _generic("IN_LATENCY")

		with self.assertRaises(ValueError) as context:
			entity.InsertGenericItem(5, inLatency, inbound)

		self.assertEqual("Parameter 'index' is outside of parameter 'group' at 2..4.", str(context.exception))
		self.assertListEqual(["Got value '5'."], context.exception.__notes__)
		self.assertIsNone(inLatency.Parent)
		self.assertIsNone(inLatency.Group)
		self.assertEqual(5, entity.GenericCount)

	def test_Insert_Group_Foreign(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		group = GenericGroup([_generic("X")])
		inLatency = _generic("IN_LATENCY")

		with self.assertRaises(NotAChildError) as context:
			entity.InsertGenericItem(0, inLatency, group)

		self.assertEqual("GenericGroup is not a generic group of this Entity.", str(context.exception))
		self.assertIs(group, context.exception.Element)
		self.assertIsNone(inLatency.Parent)

	def test_Insert_Group_WrongType(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inLatency = _generic("IN_LATENCY")

		with self.assertRaises(TypeError) as context:
			entity.InsertGenericItem(0, inLatency, "In")

		self.assertEqual("Parameter 'group' is not of type 'GenericGroup'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertIsNone(inLatency.Parent)

	def test_Remove(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inDepth = inbound.GenericItems[1]

		entity.RemoveGenericItem(inDepth)

		self.assertIsNone(inDepth.Group)
		self.assertListEqual(["IN_WIDTH"], [generic.Identifiers[0] for generic in inbound])
		self.assertListEqual([sizes, inbound, debugging], entity.GenericGroups)
		self.assertPartition(entity)

	def test_Remove_LastGenericOfGroup(self) -> None:
		"""A generic group, which becomes empty, is removed from the language construct."""
		entity, sizes, inbound, debugging = self._Entity()
		debug = debugging.GenericItems[0]

		entity.RemoveGenericItem(debug)

		self.assertIsNone(debug.Group)
		self.assertIsNone(debugging.Parent)
		self.assertListEqual([sizes, inbound], entity.GenericGroups)
		self.assertPartition(entity)

	def test_Remove_AddElsewhere(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		debug = debugging.GenericItems[0]
		component = Component("c")

		entity.RemoveGenericItem(debug)
		component.AddGenericItem(debug)

		self.assertIs(component.GenericGroups[0], debug.Group)
		self.assertPartition(component)

	def test_Move(self) -> None:
		"""A moved generic leaves its generic group and joins the generic group of the generic before its new position."""
		entity, sizes, inbound, debugging = self._Entity()
		depth = sizes.GenericItems[1]

		entity.MoveGenericItem(depth, 2)

		self.assertIs(inbound, depth.Group)
		self.assertListEqual(["WIDTH"], [generic.Identifiers[0] for generic in sizes])
		self.assertListEqual(["IN_WIDTH", "DEPTH", "IN_DEPTH"], [generic.Identifiers[0] for generic in inbound])
		self.assertPartition(entity)

	def test_Move_Start(self) -> None:
		entity, sizes, inbound, debugging = self._Entity()
		inDepth = inbound.GenericItems[1]

		entity.MoveGenericItem(inDepth, 0)

		self.assertIs(sizes, inDepth.Group)
		self.assertIs(inDepth, sizes.GenericItems[0])
		self.assertPartition(entity)

	def test_Move_LastGenericOfGroup(self) -> None:
		"""Moving the only generic of a generic group removes the generic group."""
		entity, sizes, inbound, debugging = self._Entity()
		debug = debugging.GenericItems[0]

		entity.MoveGenericItem(debug, 0)

		self.assertIs(sizes, debug.Group)
		self.assertIsNone(debugging.Parent)
		self.assertListEqual([sizes, inbound], entity.GenericGroups)
		self.assertPartition(entity)

	def test_Move_SamePosition(self) -> None:
		"""A move to the generic's current position keeps its generic group."""
		entity, sizes, inbound, debugging = self._Entity()
		inWidth = inbound.GenericItems[0]

		entity.MoveGenericItem(inWidth, 2)

		self.assertIs(inbound, inWidth.Group)
		self.assertPartition(entity)

	def test_Move_Overload(self) -> None:
		"""A moved generic subprogram changes its generic group; the namespace refers to the overload declared last."""
		overload1 = GenericFunctionInterfaceItem("f", _subtypeSymbol("integer"))
		overload2 = GenericFunctionInterfaceItem("f", _subtypeSymbol("integer"))
		first =     GenericGroup([overload1])
		second =    GenericGroup([overload2])
		entity =    Entity("e", genericItems=[overload1, overload2], genericGroups=[first, second])
		entity.IndexDeclaredItems()

		entity.MoveGenericItem(overload2, 0)

		self.assertListEqual([overload2, overload1], entity.GenericItems)
		self.assertIs(first, overload2.Group)
		self.assertListEqual([first], entity.GenericGroups)
		self.assertIsNone(second.Parent)
		self.assertIs(overload1, entity._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(entity))
		self.assertPartition(entity)
