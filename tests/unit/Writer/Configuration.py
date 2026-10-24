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
"""Tests for writing configurations with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Configuration   import EntityAspectEntity, EntityAspectConfiguration, EntityAspectOpen, \
                                        BindingIndication, AllInstantiationList, OthersInstantiationList, \
                                        ComponentConfiguration, BlockConfiguration
from pyVHDLModel.DesignUnit      import Configuration
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, SelectedName, OpenName
from pyVHDLModel.Symbol          import ArchitectureSymbol, ComponentInstantiationSymbol, ConfigurationSymbol

from tests.unit                  import _entitySymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _component(name: str) -> ComponentInstantiationSymbol:
	"""Reference to a component by name."""
	return ComponentInstantiationSymbol(SimpleName(name))


def _work(name: str) -> SelectedName:
	"""Name of a design unit in library ``work``."""
	return SelectedName(name, SimpleName("work"))


class BindingIndications(Testcase):
	def test_EntityAspectEntity(self) -> None:
		aspect = EntityAspectEntity(_entitySymbol("counter"))

		self.assertEqual("entity counter", VHDLWriter().Format(aspect))

	def test_EntityAspectEntity_Architecture(self) -> None:
		aspect = EntityAspectEntity(_entitySymbol("counter"), ArchitectureSymbol(SimpleName("rtl")))

		self.assertEqual("entity counter(rtl)", VHDLWriter().Format(aspect))

	def test_EntityAspectConfiguration(self) -> None:
		aspect = EntityAspectConfiguration(ConfigurationSymbol(_work("counter_cfg")))

		self.assertEqual("configuration work.counter_cfg", VHDLWriter().Format(aspect))

	def test_EntityAspectOpen(self) -> None:
		self.assertEqual("open", VHDLWriter().Format(EntityAspectOpen()))

	def test_ComponentConfiguration(self) -> None:
		configuration = ComponentConfiguration(
			[SimpleName("u1"), SimpleName("u2")],
			_component("counter"),
			BindingIndication(
				EntityAspectEntity(_entitySymbol("counter"), ArchitectureSymbol(SimpleName("rtl"))),
				[GenericAssociationItem(SimpleName("BITS"), IntegerLiteral(4))],
				[
					PortAssociationItem(SimpleName("clk"), _object("clock")),
					PortAssociationItem(SimpleName("q"), OpenName())
				]
			)
		)

		self.assertEqual(dedent("""\
			for u1, u2 : counter
			  use entity counter(rtl)
			    generic map (
			      BITS => 4
			    )
			    port map (
			      clk => clock,
			      q => open
			    );
			end for;
			"""), VHDLWriter().Format(configuration))

	def test_ComponentConfiguration_WithoutBinding(self) -> None:
		configuration = ComponentConfiguration(OthersInstantiationList(), _component("counter"))

		self.assertEqual("for others : counter\nend for;\n", VHDLWriter().Format(configuration))


class Configurations(Testcase):
	def test_Configuration(self) -> None:
		configuration = Configuration(
			"top_cfg",
			_entitySymbol("top"),
			BlockConfiguration(ArchitectureSymbol(SimpleName("rtl")), [
				ComponentConfiguration(
					AllInstantiationList(),
					_component("counter"),
					BindingIndication(EntityAspectConfiguration(ConfigurationSymbol(_work("counter_cfg"))))
				),
				BlockConfiguration(ArchitectureSymbol(SimpleName("gen")))
			])
		)

		self.assertEqual(dedent("""\
			configuration top_cfg of top is
			  for rtl
			    for all : counter
			      use configuration work.counter_cfg;
			    end for;
			    for gen
			    end for;
			  end for;
			end configuration top_cfg;
			"""), VHDLWriter().Format(configuration))

	def test_UpperCase(self) -> None:
		configuration = Configuration(
			"top_cfg",
			_entitySymbol("top"),
			BlockConfiguration(ArchitectureSymbol(SimpleName("rtl")))
		)

		self.assertEqual(dedent("""\
			CONFIGURATION top_cfg OF top IS
			  FOR rtl
			  END FOR;
			END CONFIGURATION top_cfg;
			"""), VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(configuration))
