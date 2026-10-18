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

The mutators are tested on an entity (a declarative region with a namespace), a component (no namespace) and a port
group.
"""
from pyTooling.MetaClasses  import UnfulfilledExpectationError
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode, ModelEntity
from pyVHDLModel.DesignUnit import Component, Entity
from pyVHDLModel.Exception  import AlreadyInDesignError, NotAChildError, DuplicatePortError
from pyVHDLModel.Interface  import PortGroup
from pyVHDLModel.Regions    import WithPortsMixin

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

	def test_Add_Group(self) -> None:
		group = PortGroup([])
		clock = _port("Clock")

		group.AddPortItem(clock)

		self.assertListEqual([clock], group.PortItems)
		self.assertIs(group, clock.Parent)

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
		Component("c", portItems=[clock])
		entity = Entity("e")

		with self.assertRaises(AlreadyInDesignError) as context:
			entity.AddPortItem(clock)

		self.assertEqual("PortSimpleSignalInterfaceItem 'Clock' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Component first."], context.exception.__notes__)
		self.assertEqual(0, entity.PortCount)

	def test_Add_Duplicate(self) -> None:
		entity = Entity("e", portItems=[_port("Clock")])
		duplicate = _port("CLOCK")

		with self.assertRaises(DuplicatePortError) as context:
			entity.AddPortItem(duplicate)

		self.assertEqual("Entity already has a port 'CLOCK'.", str(context.exception))
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
		clock = _port("Clock")

		entity.AddPortItem(clock)

		self.assertIs(clock, entity._namespace._elements["clock"])

		entity.RemovePortItem(clock)

		self.assertNotIn("clock", entity._namespace._elements)

	def test_Contract(self) -> None:
		"""A host class without the namespace methods expected by the mixin can't be instantiated."""
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
			],
			context.exception.__notes__
		)
