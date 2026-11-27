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
"""Tests for pyVHDLModel.IEEE.StdLogicMisc."""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import Design, IEEEFlavor
from pyVHDLModel.Expression import AscendingRangeExpression, CharacterLiteral
from pyVHDLModel.Subprogram import Function
from pyVHDLModel.Type       import ArrayType, EnumeratedType
from pyVHDLModel.IEEE       import Std_Logic_Misc


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class StdLogicMiscs(Testcase):
	"""Synopsys package ``ieee.std_logic_misc``."""

	def test_Declarations(self) -> None:
		"""The types ``strength`` and ``minomax``, then 29 functions; all with the package as parent."""
		stdLogicMisc = Std_Logic_Misc()
		declarations = stdLogicMisc.DeclaredItems

		self.assertIsInstance(declarations[0], EnumeratedType)
		self.assertIsInstance(declarations[1], ArrayType)
		self.assertEqual(29, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(31, len(declarations))
		for declaration in declarations:
			self.assertIs(stdLogicMisc, declaration.Parent)

	def test_Types(self) -> None:
		"""``type STRENGTH is (strn_X01, ..., strn_WL1);`` and ``type MINOMAX is array (1 to 3) of TIME;``"""
		types = Std_Logic_Misc().Types

		self.assertEqual(10, len(types["strength"].Literals))
		self.assertEqual("strn_x01", types["strength"].Literals[0].Value)
		minomax = types["minomax"]
		self.assertIsInstance(minomax.Dimensions[0], AscendingRangeExpression)
		self.assertEqual(3, minomax.Dimensions[0].RightOperand.Value)
		self.assertEqual("time", minomax.ElementType.Name.Identifier)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{
				"strength_map": 1, "strength_map_z": 1, "drive": 2, "sense": 5, "std_logic_vectortobit_vector": 1,
				"std_ulogic_vectortobit_vector": 1, "std_ulogictobit": 1, "and_reduce": 2, "nand_reduce": 2,
				"or_reduce": 2, "nor_reduce": 2, "xor_reduce": 2, "xnor_reduce": 2, "fun_buf3s": 1, "fun_buf3sl": 1,
				"fun_mux2x1": 1, "fun_maj23": 1, "fun_wiredx": 1
			},
			{identifier: len(overloads) for identifier, overloads in Std_Logic_Misc().Functions.items()}
		)

	def test_Sense(self) -> None:
		"""Five ``Sense`` with ``vZ, vU, vDC : STD_ULOGIC``; two only differ in their return type."""
		sense = Std_Logic_Misc().Functions["sense"]

		self.assertTupleEqual(("vZ", "vU", "vDC"), sense[1].ParameterItems[1].Identifiers)
		self.assertListEqual(
			["std_logic", "std_logic_vector", "std_ulogic_vector", "std_logic_vector", "std_ulogic_vector"],
			[function.ReturnType.Name.Identifier for function in sense]
		)

	def test_ToBit(self) -> None:
		"""``STD_ULOGICtoBIT (V; vX, vZ, vU, vDC: BIT := '0'; Xflag, Zflag, Uflag, DCflag: BOOLEAN := FALSE)``"""
		toBit = Std_Logic_Misc().Functions["std_ulogictobit"][0]

		self.assertTupleEqual(("vX", "vZ", "vU", "vDC"), toBit.ParameterItems[1].Identifiers)
		self.assertIsInstance(toBit.ParameterItems[1].DefaultExpression, CharacterLiteral)
		self.assertEqual("false", toBit.ParameterItems[2].DefaultExpression.Name.Identifier)
		self.assertEqual("bit", toBit.ReturnType.Name.Identifier)

	def test_Reduce(self) -> None:
		"""``AND_REDUCE(ARG: STD_LOGIC_VECTOR) return UX01`` and of ``STD_ULOGIC_VECTOR``."""
		andReduce = Std_Logic_Misc().Functions["and_reduce"]

		self.assertListEqual(
			["std_logic_vector", "std_ulogic_vector"],
			[function.ParameterItems[0].Subtype.Name.Identifier for function in andReduce]
		)
		self.assertEqual("ux01", andReduce[0].ReturnType.Name.Identifier)

	def test_Analyze(self) -> None:
		"""With the Synopsys flavor, every type mark resolves, e.g. ``STRENGTH`` and ``UX01``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.Synopsys)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		stdLogicMisc =   design.Libraries["ieee"].Packages["std_logic_misc"]
		bufferFunction = stdLogicMisc.Functions["fun_buf3s"][0]
		self.assertIs(stdLogicMisc.Types["strength"], bufferFunction.ParameterItems[1].Subtype.Reference)
		self.assertIsNotNone(bufferFunction.ParameterItems[0].Subtype.Reference)
