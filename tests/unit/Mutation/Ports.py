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
Mutation tests for port clauses (:class:`~pyVHDLModel.Regions.WithPortsMixin`).

The mutators are tested on an entity (a declarative region with a namespace) and a component (no namespace). The port
groups of the language construct stay a partition of its port clause.
"""
from pyTooling.MetaClasses  import UnfulfilledExpectationError
from pyTooling.Warning      import WarningCollector
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode, ModelEntity
from pyVHDLModel.DesignUnit import Component, Entity
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicatePortError, NotInNamespaceError
from pyVHDLModel.Interface  import PortGroup
from pyVHDLModel.Object     import Signal
from pyVHDLModel.Regions    import WithPortsMixin

from tests.unit             import _subtypeSymbol
from tests.unit.Mutation    import _generic, _port


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Ports(Testcase):
	def test_Add(self) -> None:
		entity = Entity("e")
		clock = _port("Clock")
		reset = _port("Reset")

		entity.AddPortItem(clock)
		entity.AddPortItem(reset)

		self.assertListEqual([clock, reset], entity.PortItems)
		self.assertEqual(2, entity.PortCount)
		self.assertIs(entity, clock.Parent)
		self.assertIs(entity, reset.Parent)

	def test_Add_Component(self) -> None:
		component = Component("c")
		clock = _port("Clock")

		component.AddPortItem(clock)

		self.assertListEqual([clock], component.PortItems)
		self.assertIs(component, clock.Parent)

	def test_Add_None(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.AddPortItem(None)

		self.assertEqual("Parameter 'portItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.AddPortItem(_generic("BITS"))

		self.assertEqual("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.GenericConstantInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Add_AlreadyInDesign(self) -> None:
		clock = _port("Clock")
		component = Component("c", portItems=[clock])
		entity = Entity("e")

		with self.assertRaises(AlreadyInDesignError) as context:
			entity.AddPortItem(clock)

		self.assertEqual("PortSimpleSignalInterfaceItem 'Clock' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Component first."], context.exception.__notes__)
		self.assertIs(clock, context.exception.Element)
		self.assertIs(component, context.exception.Parent)
		self.assertEqual(0, entity.PortCount)

	def test_Add_Duplicate(self) -> None:
		clock = _port("Clock")
		entity = Entity("e", portItems=[clock])
		duplicate = _port("CLOCK")

		with self.assertRaises(DuplicatePortError) as context:
			entity.AddPortItem(duplicate)

		self.assertEqual("Entity already declares 'CLOCK'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)
		self.assertEqual("CLOCK", context.exception.Identifier)
		self.assertEqual("clock", context.exception.NormalizedIdentifier)
		self.assertIs(entity, context.exception.Parent)
		self.assertIs(duplicate, context.exception.Element)
		self.assertIs(clock, context.exception.Existing)
		self.assertEqual(1, entity.PortCount)
		self.assertIsNone(duplicate.Parent)

	def test_Insert_Start(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		entity = Entity("e", portItems=[clock, reset])
		enable = _port("Enable")

		entity.InsertPortItem(0, enable)

		self.assertListEqual([enable, clock, reset], entity.PortItems)
		self.assertIs(entity, enable.Parent)

	def test_Insert_Middle(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		entity = Entity("e", portItems=[clock, reset])
		enable = _port("Enable")

		entity.InsertPortItem(1, enable)

		self.assertListEqual([clock, enable, reset], entity.PortItems)

	def test_Insert_End(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		entity = Entity("e", portItems=[clock, reset])
		enable = _port("Enable")

		entity.InsertPortItem(2, enable)

		self.assertListEqual([clock, reset, enable], entity.PortItems)

	def test_Insert_OutOfRange(self) -> None:
		entity = Entity("e")
		enable = _port("Enable")

		with self.assertRaises(ValueError) as context:
			entity.InsertPortItem(1, enable)

		self.assertEqual("Parameter 'index' is out of range 0..0.", str(context.exception))
		self.assertListEqual(["Got value '1'."], context.exception.__notes__)
		self.assertIsNone(enable.Parent)

	def test_Insert_Negative(self) -> None:
		clock = _port("Clock")
		enable = _port("Enable")
		entity = Entity("e", portItems=[clock, enable])
		reset = _port("Reset")

		entity.InsertPortItem(-1, reset)

		self.assertListEqual([clock, reset, enable], entity.PortItems)
		self.assertIs(entity, reset.Parent)

	def test_Insert_Negative_OutOfRange(self) -> None:
		entity = Entity("e", portItems=[_port("Clock")])
		enable = _port("Enable")

		with self.assertRaises(ValueError) as context:
			entity.InsertPortItem(-2, enable)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertIsNone(enable.Parent)

	def test_Remove(self) -> None:
		clock = _port("Clock")
		reset = _port("Reset")
		entity = Entity("e", portItems=[clock, reset])

		entity.RemovePortItem(clock)

		self.assertListEqual([reset], entity.PortItems)
		self.assertIsNone(clock.Parent)
		self.assertTupleEqual(("Clock", ), clock.Identifiers)
		self.assertIs(Mode.In, clock.Mode)

	def test_Remove_AddElsewhere(self) -> None:
		clock = _port("Clock")
		entity = Entity("e", portItems=[clock])
		component = Component("c")

		entity.RemovePortItem(clock)
		component.AddPortItem(clock)

		self.assertEqual(0, entity.PortCount)
		self.assertListEqual([clock], component.PortItems)
		self.assertIs(component, clock.Parent)

	def test_Remove_None(self) -> None:
		entity = Entity("e")

		with self.assertRaises(ValueError) as context:
			entity.RemovePortItem(None)

		self.assertEqual("Parameter 'portItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		entity = Entity("e")

		with self.assertRaises(TypeError) as context:
			entity.RemovePortItem(_generic("BITS"))

		self.assertEqual("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.", str(context.exception))

	def test_Remove_NotAChild(self) -> None:
		entity = Entity("e")
		clock = _port("Clock")

		with self.assertRaises(NotAChildError) as context:
			entity.RemovePortItem(clock)

		self.assertEqual("PortSimpleSignalInterfaceItem 'Clock' is not a port of this Entity.", str(context.exception))
		self.assertIs(clock, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)

	def test_Move(self) -> None:
		"""A move within one port clause is a remove followed by an insert."""
		clock = _port("Clock")
		reset = _port("Reset")
		enable = _port("Enable")
		entity = Entity("e", portItems=[clock, reset, enable])

		entity.RemovePortItem(clock)
		entity.InsertPortItem(2, clock)

		self.assertListEqual([reset, enable, clock], entity.PortItems)
		self.assertIs(entity, clock.Parent)

	def test_Namespace(self) -> None:
		entity = Entity("e")
		entity.IndexDeclaredItems()
		clock = _port("Clock")

		entity.AddPortItem(clock)

		self.assertIs(clock, entity._namespace._elements["clock"])

		entity.RemovePortItem(clock)

		self.assertNotIn("clock", entity._namespace._elements)

	def test_Namespace_AddNotIndexed(self) -> None:
		"""A port added to a region, which wasn't indexed yet, enters the namespace when the region is indexed."""
		entity = Entity("e")
		clock = _port("Clock")

		entity.AddPortItem(clock)

		self.assertDictEqual({}, entity._namespace._elements)

		entity.IndexDeclaredItems()

		self.assertDictEqual({"clock": clock}, entity._namespace._elements)

	def test_Namespace_OtherElement(self) -> None:
		"""Removing a port, whose identifier refers to a duplicate declaration in the namespace, is rejected."""
		clock = _port("Clock")
		signal = Signal(["clock"], _subtypeSymbol("std_logic"))
		entity = Entity("e", portItems=[clock], declaredItems=[signal])
		with WarningCollector():
			entity.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			entity.RemovePortItem(clock)

		self.assertEqual("Namespace 'e' has another element for 'clock'.", str(context.exception))
		self.assertListEqual(["Found element of type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)
		self.assertEqual("Clock", context.exception.Identifier)
		self.assertEqual("clock", context.exception.NormalizedIdentifier)
		self.assertIs(entity._namespace, context.exception.Namespace)
		self.assertListEqual([clock], entity.PortItems)
		self.assertIs(entity, clock.Parent)
		self.assertIs(signal, entity._namespace._elements["clock"])

	def test_Namespace_NotIndexed(self) -> None:
		"""Removing a port of a region, which wasn't indexed yet, leaves the namespace as is."""
		clock = _port("Clock")
		entity = Entity("e", portItems=[clock])

		entity.RemovePortItem(clock)

		self.assertEqual(0, entity.PortCount)
		self.assertIsNone(clock.Parent)
		self.assertDictEqual({}, entity._namespace._elements)

	def test_Contract(self) -> None:
		"""A host class without the methods expected by the mixin can't be instantiated."""
		class Host(ModelEntity, WithPortsMixin):
			def __init__(self) -> None:
				super().__init__()
				WithPortsMixin.__init__(self)

		with self.assertRaises(UnfulfilledExpectationError) as context:
			Host()

		self.assertEqual("Class 'Host' doesn't provide every expected member.", str(context.exception))
		self.assertListEqual(
			[
				"Missing '_AddToNamespace', expected by 'WithPortsMixin'.",
				"Missing '_RemoveFromNamespace', expected by 'WithPortsMixin'.",
				"Missing '_ClashingDeclarations', expected by 'WithPortsMixin'.",
			],
			context.exception.__notes__
		)


class PortGroups(Testcase):
	def _Entity(self) -> tuple[Entity, PortGroup, PortGroup, PortGroup]:
		"""Return an entity with the port groups ``clock, reset | In_Valid, In_Data | error``."""
		clocking = PortGroup([_port("clock"), _port("reset")])
		inbound =  PortGroup([_port("In_Valid"), _port("In_Data")], name="In")
		errors =   PortGroup([_port("error")])
		entity =   Entity("e", portItems=[*clocking, *inbound, *errors], portGroups=[clocking, inbound, errors])

		return entity, clocking, inbound, errors

	def assertPartition(self, entity: Entity) -> None:
		"""Assert the port groups list every port exactly once, in declaration order, and each port refers to its group."""
		self.assertListEqual(entity.PortItems, [port for group in entity.PortGroups for port in group])
		for group in entity.PortGroups:
			self.assertIs(entity, group.Parent)
			self.assertGreater(len(group), 0)
			for port in group:
				self.assertIs(group, port.Group)

	def test_Add(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		warning = _port("warning")

		entity.AddPortItem(warning)

		self.assertIs(errors, warning.Group)
		self.assertListEqual([clocking, inbound, errors], entity.PortGroups)
		self.assertPartition(entity)

	def test_Add_NoPorts(self) -> None:
		entity = Entity("e")
		clock = _port("clock")

		entity.AddPortItem(clock)

		self.assertEqual(1, len(entity.PortGroups))
		self.assertIsNone(entity.PortGroups[0].Identifier)
		self.assertListEqual([clock], entity.PortGroups[0].PortItems)
		self.assertPartition(entity)

	def test_Add_Group(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inAck = _port("In_Ack")

		entity.AddPortItem(inAck, inbound)

		self.assertIs(inbound, inAck.Group)
		self.assertIs(inAck, inbound.PortItems[-1])
		self.assertIs(inAck, entity.PortItems[4])
		self.assertPartition(entity)

	def test_Add_Group_Foreign(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		other, _, otherInbound, _ = self._Entity()
		inAck = _port("In_Ack")

		with self.assertRaises(NotAChildError) as context:
			entity.AddPortItem(inAck, otherInbound)

		self.assertEqual("PortGroup 'In' is not a port group of this Entity.", str(context.exception))
		self.assertIs(otherInbound, context.exception.Element)
		self.assertIs(entity, context.exception.Parent)
		self.assertIsNone(inAck.Parent)
		self.assertIsNone(inAck.Group)

	def test_Insert_Middle(self) -> None:
		"""Without a port group, the port joins the port group of the port before it."""
		entity, clocking, inbound, errors = self._Entity()
		enable = _port("enable")

		entity.InsertPortItem(2, enable)

		self.assertIs(clocking, enable.Group)
		self.assertListEqual(["clock", "reset", "enable"], [port.Identifiers[0] for port in clocking])
		self.assertPartition(entity)

	def test_Insert_Start(self) -> None:
		"""At index 0, the port joins the port group of the first port."""
		entity, clocking, inbound, errors = self._Entity()
		enable = _port("enable")

		entity.InsertPortItem(0, enable)

		self.assertIs(clocking, enable.Group)
		self.assertIs(enable, clocking.PortItems[0])
		self.assertPartition(entity)

	def test_Insert_Negative(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		enable = _port("enable")

		entity.InsertPortItem(-1, enable)

		self.assertIs(inbound, enable.Group)
		self.assertIs(enable, entity.PortItems[4])
		self.assertPartition(entity)

	def test_Insert_Group(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inAck = _port("In_Ack")

		entity.InsertPortItem(3, inAck, inbound)

		self.assertIs(inbound, inAck.Group)
		self.assertListEqual(["In_Valid", "In_Ack", "In_Data"], [port.Identifiers[0] for port in inbound])
		self.assertPartition(entity)

	def test_Insert_Group_Start(self) -> None:
		"""A port group given takes a port at its start, although the port before belongs to another port group."""
		entity, clocking, inbound, errors = self._Entity()
		inAck = _port("In_Ack")

		entity.InsertPortItem(2, inAck, inbound)

		self.assertIs(inbound, inAck.Group)
		self.assertIs(inAck, inbound.PortItems[0])
		self.assertPartition(entity)

	def test_Insert_Group_End(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inAck = _port("In_Ack")

		entity.InsertPortItem(4, inAck, inbound)

		self.assertIs(inbound, inAck.Group)
		self.assertIs(inAck, inbound.PortItems[-1])
		self.assertPartition(entity)

	def test_Insert_Group_Outside(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inAck = _port("In_Ack")

		with self.assertRaises(ValueError) as context:
			entity.InsertPortItem(5, inAck, inbound)

		self.assertEqual("Parameter 'index' is outside of parameter 'group' at 2..4.", str(context.exception))
		self.assertListEqual(["Got value '5'."], context.exception.__notes__)
		self.assertIsNone(inAck.Parent)
		self.assertIsNone(inAck.Group)
		self.assertEqual(5, entity.PortCount)

	def test_Insert_Group_Foreign(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		group = PortGroup([_port("x")])
		inAck = _port("In_Ack")

		with self.assertRaises(NotAChildError) as context:
			entity.InsertPortItem(0, inAck, group)

		self.assertEqual("PortGroup is not a port group of this Entity.", str(context.exception))
		self.assertIs(group, context.exception.Element)
		self.assertIsNone(inAck.Parent)

	def test_Insert_Group_WrongType(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inAck = _port("In_Ack")

		with self.assertRaises(TypeError) as context:
			entity.InsertPortItem(0, inAck, "In")

		self.assertEqual("Parameter 'group' is not of type 'PortGroup'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertIsNone(inAck.Parent)

	def test_Remove(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inData = inbound.PortItems[1]

		entity.RemovePortItem(inData)

		self.assertIsNone(inData.Group)
		self.assertListEqual(["In_Valid"], [port.Identifiers[0] for port in inbound])
		self.assertListEqual([clocking, inbound, errors], entity.PortGroups)
		self.assertPartition(entity)

	def test_Remove_LastPortOfGroup(self) -> None:
		"""A port group, which becomes empty, is removed from the language construct."""
		entity, clocking, inbound, errors = self._Entity()
		error = errors.PortItems[0]

		entity.RemovePortItem(error)

		self.assertIsNone(error.Group)
		self.assertIsNone(errors.Parent)
		self.assertListEqual([clocking, inbound], entity.PortGroups)
		self.assertPartition(entity)

	def test_Remove_AddElsewhere(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		error = errors.PortItems[0]
		component = Component("c")

		entity.RemovePortItem(error)
		component.AddPortItem(error)

		self.assertIs(component.PortGroups[0], error.Group)
		self.assertPartition(component)

	def test_Move(self) -> None:
		"""A moved port leaves its port group and joins the port group of the port before its new position."""
		entity, clocking, inbound, errors = self._Entity()
		reset = clocking.PortItems[1]

		entity.MovePortItem(reset, 2)

		self.assertIs(inbound, reset.Group)
		self.assertListEqual(["clock"], [port.Identifiers[0] for port in clocking])
		self.assertListEqual(["In_Valid", "reset", "In_Data"], [port.Identifiers[0] for port in inbound])
		self.assertPartition(entity)

	def test_Move_Start(self) -> None:
		entity, clocking, inbound, errors = self._Entity()
		inData = inbound.PortItems[1]

		entity.MovePortItem(inData, 0)

		self.assertIs(clocking, inData.Group)
		self.assertIs(inData, clocking.PortItems[0])
		self.assertPartition(entity)

	def test_Move_LastPortOfGroup(self) -> None:
		"""Moving the only port of a port group removes the port group."""
		entity, clocking, inbound, errors = self._Entity()
		error = errors.PortItems[0]

		entity.MovePortItem(error, 0)

		self.assertIs(clocking, error.Group)
		self.assertIsNone(errors.Parent)
		self.assertListEqual([clocking, inbound], entity.PortGroups)
		self.assertPartition(entity)

	def test_Move_SamePosition(self) -> None:
		"""A move to the port's current position keeps its port group."""
		entity, clocking, inbound, errors = self._Entity()
		inValid = inbound.PortItems[0]

		entity.MovePortItem(inValid, 2)

		self.assertIs(inbound, inValid.Group)
		self.assertPartition(entity)
