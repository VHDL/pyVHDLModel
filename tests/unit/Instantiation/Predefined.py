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
"""Tests for pyVHDLModel.IEEE.NumericBitUnsigned."""
from pyTooling.Testing       import Testcase
"""Tests for pyVHDLModel.Predefined."""
from pyTooling.Testing       import Testcase

from pyVHDLModel             import Design, VHDLVersion, IEEEFlavor
from pyVHDLModel.STD         import Std, Standard_Body
from pyVHDLModel.IEEE        import Ieee, Numeric_Std, Std_Logic_Arith_Synopsys


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VHDLVersions(Testcase):
	"""The VHDL version of the predefined libraries, packages and package bodies."""

	def test_Default(self) -> None:
		"""Without a parameter, a library, its packages and package bodies are VHDL-2008."""
		ieee = Ieee()

		self.assertIs(VHDLVersion.VHDL2008, ieee.VHDLVersion)
		for package in ieee.Packages.values():
			self.assertIs(VHDLVersion.VHDL2008, package.VHDLVersion)

		for packageBody in ieee.PackageBodies.values():
			self.assertIs(VHDLVersion.VHDL2008, packageBody.VHDLVersion)

	def test_Std(self) -> None:
		"""``Std(VHDLVersion.VHDL2008)`` passes the version on to its packages."""
		std = Std(VHDLVersion.VHDL2008)

		self.assertIs(VHDLVersion.VHDL2008, std.VHDLVersion)
		for package in std.Packages.values():
			self.assertIs(VHDLVersion.VHDL2008, package.VHDLVersion)

	def test_Package(self) -> None:
		"""A package, a vendor package with its own identifier and a package body take the version."""
		self.assertIs(VHDLVersion.VHDL2008, Numeric_Std(VHDLVersion.VHDL2008).VHDLVersion)
		self.assertIs(VHDLVersion.VHDL2008, Std_Logic_Arith_Synopsys(VHDLVersion.VHDL2008).VHDLVersion)
		self.assertEqual("Std_Logic_Arith", Std_Logic_Arith_Synopsys(VHDLVersion.VHDL2008).Identifier)
		self.assertIs(VHDLVersion.VHDL2008, Standard_Body(VHDLVersion.VHDL2008).VHDLVersion)

	def test_Design(self) -> None:
		"""``LoadStdLibrary``/``LoadIEEELibrary`` create the libraries and their documents with the version."""
		design = Design("design")
		std =    design.LoadStdLibrary(VHDLVersion.VHDL2008)
		ieee =   design.LoadIEEELibrary(VHDLVersion.VHDL2008, IEEEFlavor.Synopsys)

		self.assertIs(VHDLVersion.VHDL2008, std.VHDLVersion)
		self.assertIs(VHDLVersion.VHDL2008, ieee.VHDLVersion)
		self.assertIn("std_logic_arith", ieee.Packages)
		for document in design.Documents:
			self.assertIs(VHDLVersion.VHDL2008, document.VHDLVersion)

	def test_None(self) -> None:
		"""``None`` is rejected by a library and a package."""
		with self.assertRaises(ValueError) as context:
			Std(None)

		self.assertEqual("Parameter 'vhdlVersion' is None.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			Numeric_Std(None)

		self.assertEqual("Parameter 'vhdlVersion' is None.", str(context.exception))

	def test_Type(self) -> None:
		"""A flavor given in the place of the version (``Ieee(IEEEFlavor.Synopsys)``) is a :exc:`TypeError`."""
		with self.assertRaises(TypeError) as context:
			Ieee(IEEEFlavor.Synopsys)

		self.assertEqual("Parameter 'vhdlVersion' is not of type 'VHDLVersion'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.IEEEFlavor'."], context.exception.__notes__)

		with self.assertRaises(TypeError) as context:
			Standard_Body("VHDL2008")

		self.assertEqual("Parameter 'vhdlVersion' is not of type 'VHDLVersion'.", str(context.exception))

	def test_Unsupported(self) -> None:
		"""VHDL-2019 isn't supported yet: the libraries, packages and the design loaders raise a :exc:`ValueError`."""
		with self.assertRaises(ValueError) as context:
			Ieee(VHDLVersion.VHDL2019)

		self.assertEqual("Parameter 'vhdlVersion' is not a supported VHDL version.", str(context.exception))
		self.assertEqual(
			[f"Got value '{VHDLVersion.VHDL2019}'.", "Supported VHDL versions: VHDL2008"],
			context.exception.__notes__
		)

		with self.assertRaises(ValueError):
			Numeric_Std(VHDLVersion.VHDL93)

		design = Design("design")
		with self.assertRaises(ValueError):
			design.LoadStdLibrary(VHDLVersion.VHDL2019)

		self.assertEqual(0, len(design.Libraries))
		self.assertEqual(0, len(design.Documents))
