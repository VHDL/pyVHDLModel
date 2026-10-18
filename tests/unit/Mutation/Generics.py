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

The mutators are tested on an entity and a subprogram (declarative regions with a namespace), a component (no
namespace) and a generic group.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.DesignUnit import Component, Entity
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicateGenericError
from pyVHDLModel.Interface  import GenericTypeInterfaceItem, GenericGroup
from pyVHDLModel.Subprogram import Procedure

from tests.unit.Mutation    import _generic, _port


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

	def test_Add_Group(self) -> None:
		group = GenericGroup([])
		bits = _generic("BITS")

		group.AddGenericItem(bits)

		self.assertListEqual([bits], group.GenericItems)
		self.assertIs(group, bits.Parent)

	def test_Add_Subprogram(self) -> None:
		procedure = Procedure("p")
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
		Entity("e1", genericItems=[bits])
		entity = Entity("e2")

		with self.assertRaises(AlreadyInDesignError) as context:
			entity.AddGenericItem(bits)

		self.assertEqual("GenericConstantInterfaceItem 'BITS' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Entity first."], context.exception.__notes__)
		self.assertEqual(0, entity.GenericCount)

	def test_Add_Twice(self) -> None:
		entity = Entity("e")
		bits = _generic("BITS")
		entity.AddGenericItem(bits)

		with self.assertRaises(AlreadyInDesignError):
			entity.AddGenericItem(bits)

		self.assertListEqual([bits], entity.GenericItems)

	def test_Add_Duplicate(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])
		duplicate = _generic("Depth", "bits")

		with self.assertRaises(DuplicateGenericError) as context:
			entity.AddGenericItem(duplicate)

		self.assertEqual("Entity already has a generic 'bits'.", str(context.exception))
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

		self.assertEqual("Parameter 'index' is out of range 0..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)
		self.assertEqual(1, entity.GenericCount)
		self.assertIsNone(width.Parent)

	def test_Insert_Negative(self) -> None:
		entity = Entity("e", genericItems=[_generic("BITS")])

		with self.assertRaises(ValueError) as context:
			entity.InsertGenericItem(-1, _generic("WIDTH"))

		self.assertEqual("Parameter 'index' is out of range 0..1.", str(context.exception))
		self.assertEqual(1, entity.GenericCount)

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

	def test_Namespace_OtherElement(self) -> None:
		"""Removing a generic leaves a namespace entry of another element with the same identifier."""
		entity = Entity("e")
		bits = _generic("BITS")
		entity.AddGenericItem(bits)
		port = _port("bits")
		entity._namespace._elements["bits"] = port

		entity.RemoveGenericItem(bits)

		self.assertIs(port, entity._namespace._elements["bits"])
