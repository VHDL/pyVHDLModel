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
"""Tests for pyVHDLModel.IEEE.StdLogicTextIOPkg."""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import Design, IEEEFlavor
from pyVHDLModel.Base       import Mode
from pyVHDLModel.Subprogram import Procedure
from pyVHDLModel.IEEE       import Std_Logic_TextIO, Std_Logic_TextIO_Synopsys


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class StdLogicTextIOs(Testcase):
	"""Package ``ieee.std_logic_textio`` of VHDL-2008: its procedures are part of ``ieee.std_logic_1164``."""

	def test_Empty(self) -> None:
		"""The VHDL-2008 package declares nothing."""
		self.assertListEqual([], Std_Logic_TextIO().DeclaredItems)


class StdLogicTextIOSynopsys(Testcase):
	"""Synopsys package ``ieee.std_logic_textio``."""

	def test_Declarations(self) -> None:
		"""21 procedures with the package as parent; the VHDL name is ``std_logic_textio``."""
		textIO =       Std_Logic_TextIO_Synopsys()
		declarations = textIO.DeclaredItems

		self.assertEqual("std_logic_textio", textIO.NormalizedIdentifier)
		self.assertEqual(21, len(declarations))
		for declaration in declarations:
			self.assertIsInstance(declaration, Procedure)
			self.assertIs(textIO, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{"read": 6, "write": 3, "hread": 4, "hwrite": 2, "oread": 4, "owrite": 2},
			{identifier: len(overloads) for identifier, overloads in Std_Logic_TextIO_Synopsys().Procedures.items()}
		)
		self.assertDictEqual({}, Std_Logic_TextIO_Synopsys().Functions)

	def test_Read(self) -> None:
		"""``READ(L:inout LINE; VALUE:out STD_ULOGIC; GOOD: out BOOLEAN)``"""
		read = Std_Logic_TextIO_Synopsys().Procedures["read"][1]

		self.assertListEqual([("L", ), ("VALUE", ), ("GOOD", )], [item.Identifiers for item in read.ParameterItems])
		self.assertListEqual([Mode.InOut, Mode.Out, Mode.Out], [item.Mode for item in read.ParameterItems])
		self.assertEqual("std_ulogic", read.ParameterItems[1].Subtype.Name.Identifier)

	def test_Write(self) -> None:
		"""``HWRITE(L:inout LINE; VALUE:in STD_LOGIC_VECTOR; JUSTIFIED:in SIDE := RIGHT; FIELD:in WIDTH := 0)``"""
		hwrite = Std_Logic_TextIO_Synopsys().Procedures["hwrite"][1]

		self.assertListEqual(
			["line", "std_logic_vector", "side", "width"],
			[item.Subtype.Name.Identifier for item in hwrite.ParameterItems]
		)
		self.assertEqual("right", hwrite.ParameterItems[2].DefaultExpression.Name.Identifier)
		self.assertEqual(0, hwrite.ParameterItems[3].DefaultExpression.Value)

	def test_Analyze(self) -> None:
		"""With the Synopsys flavor, every type mark resolves, e.g. ``LINE`` of ``std.textio``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.Synopsys)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		textIO = design.Libraries["ieee"].Packages["std_logic_textio"]
		line =   design.Libraries["std"].Packages["textio"].Types["line"]
		self.assertIsInstance(textIO, Std_Logic_TextIO_Synopsys)
		self.assertIs(line, textIO.Procedures["read"][0].ParameterItems[0].Subtype.Reference)
