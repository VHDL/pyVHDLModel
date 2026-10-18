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
"""Tests for pyVHDLModel.Configuration."""
from unittest import TestCase

from pyVHDLModel.Name          import SimpleName, SelectedName
from pyVHDLModel.Symbol        import EntitySymbol, ArchitectureSymbol, ConfigurationSymbol
from pyVHDLModel.Symbol        import ComponentInstantiationSymbol, Symbol, PossibleReference
from pyVHDLModel.Association   import GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Expression    import IntegerLiteral
from pyVHDLModel.Configuration import (
	EntityAspect, EntityAspectEntity, EntityAspectConfiguration, EntityAspectOpen,
	BindingIndication, AllInstantiationList, OthersInstantiationList, ComponentConfiguration,
	BlockConfiguration,
)


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class EntityAspects(TestCase):
	def test_Entity(self) -> None:
		"""``use entity work.sub(behav);``"""
		entity = EntitySymbol(SelectedName("sub", SimpleName("work")))
		architecture = ArchitectureSymbol(SimpleName("behav"))
		aspect = EntityAspectEntity(entity, architecture)

		self.assertIsInstance(aspect, EntityAspect)
		self.assertIs(entity, aspect.Entity)
		self.assertIs(architecture, aspect.Architecture)

	def test_EntityWithoutArchitecture(self) -> None:
		"""``use entity work.sub;``"""
		entity = EntitySymbol(SelectedName("sub", SimpleName("work")))
		aspect = EntityAspectEntity(entity)

		self.assertIs(entity, aspect.Entity)
		self.assertIsNone(aspect.Architecture)

	def test_Configuration(self) -> None:
		"""``use configuration work.cfg;``"""
		configuration = ConfigurationSymbol(SelectedName("cfg", SimpleName("work")))
		aspect = EntityAspectConfiguration(configuration)

		self.assertIsInstance(aspect, EntityAspect)
		self.assertIs(configuration, aspect.Configuration)

	def test_Open(self) -> None:
		"""``use open;``"""
		aspect = EntityAspectOpen()

		self.assertIsInstance(aspect, EntityAspect)


class BindingIndications(TestCase):
	def test_Full(self) -> None:
		"""``use entity work.sub(behav) generic map (G => 1) port map (p => s);``"""
		entity = EntitySymbol(SelectedName("sub", SimpleName("work")))
		aspect = EntityAspectEntity(entity, ArchitectureSymbol(SimpleName("behav")))
		generics = [GenericAssociationItem(SimpleName("G"), IntegerLiteral(1))]
		ports = [PortAssociationItem(SimpleName("p"), SimpleName("s"))]

		binding = BindingIndication(aspect, generics, ports)

		self.assertIs(aspect, binding.EntityAspect)
		self.assertEqual(1, len(binding.GenericAssociationItems))
		self.assertEqual(1, len(binding.PortAssociationItems))

	def test_Empty(self) -> None:
		binding = BindingIndication()

		self.assertIsNone(binding.EntityAspect)
		self.assertEqual(0, len(binding.GenericAssociationItems))
		self.assertEqual(0, len(binding.PortAssociationItems))


class ComponentConfigurations(TestCase):
	"""Also covers configuration specifications, which are structurally identical."""

	def test_LabeledInstantiationList(self) -> None:
		"""``for U1 : comp use entity work.sub(behav);``"""
		componentName = ComponentInstantiationSymbol(SimpleName("comp"))
		binding = BindingIndication(EntityAspectEntity(EntitySymbol(SimpleName("sub"))))

		config = ComponentConfiguration([SimpleName("U1")], componentName, binding)

		self.assertEqual(1, len(config.InstantiationList))
		self.assertIs(componentName, config.ComponentName)
		self.assertIs(binding, config.BindingIndication)

	def test_All(self) -> None:
		"""``for all : comp use entity work.sub(behav);``"""
		allMarker = AllInstantiationList()
		config = ComponentConfiguration(allMarker, ComponentInstantiationSymbol(SimpleName("comp")))

		self.assertIs(allMarker, config.InstantiationList)

	def test_Others(self) -> None:
		"""``for others : comp use entity work.sub(behav);``"""
		othersMarker = OthersInstantiationList()
		config = ComponentConfiguration(othersMarker, ComponentInstantiationSymbol(SimpleName("comp")))

		self.assertIs(othersMarker, config.InstantiationList)

	def test_WithoutBindingIndication(self) -> None:
		config = ComponentConfiguration([SimpleName("U1")], ComponentInstantiationSymbol(SimpleName("comp")))

		self.assertIsNone(config.BindingIndication)


class BlockConfigurations(TestCase):
	def test_Empty(self) -> None:
		"""``for rtl end for;``"""
		blockSpec = Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label)
		block = BlockConfiguration(blockSpec)

		self.assertIs(blockSpec, block.BlockSpecification)
		self.assertEqual(0, len(block.Items))

	def test_WithComponentConfiguration(self) -> None:
		"""``for rtl for U1 : comp use entity work.sub(behav); end for; end for;``"""
		blockSpec = Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label)
		componentConfig = ComponentConfiguration(
			[SimpleName("U1")], ComponentInstantiationSymbol(SimpleName("comp"))
		)
		block = BlockConfiguration(blockSpec, [componentConfig])

		self.assertEqual(1, len(block.Items))
		self.assertIs(componentConfig, block.Items[0])

	def test_NestedBlockConfiguration(self) -> None:
		"""
		A block configuration may itself contain nested block configurations.

		A generate statement's alternative is configured by such a nested block configuration.
		"""
		outerSpec = Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label)
		innerSpec = Symbol(SimpleName("gen_label"), PossibleReference.Architecture | PossibleReference.Label)
		innerBlock = BlockConfiguration(innerSpec)
		outerBlock = BlockConfiguration(outerSpec, [innerBlock])

		self.assertEqual(1, len(outerBlock.Items))
		self.assertIs(innerBlock, outerBlock.Items[0])
