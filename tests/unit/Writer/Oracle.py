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
GHDL as oracle for pyVHDLModel.Formatting.VHDL: written expressions must pass ``ghdl -a --std=08``.

Each expression becomes the value of a constant declaration in a package. Skipped if GHDL is not on PATH.
"""
from textwrap                    import dedent
from typing                      import Iterable, Tuple
from unittest                    import skipIf

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import ParameterAssociationItem
from pyVHDLModel.Expression      import (
	IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral, PhysicalFloatingLiteral, CharacterLiteral,
	StringLiteral, BinaryBitStringLiteral, DecimalBitStringLiteral, HexadecimalBitStringLiteral
)
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName, AttributeName
from pyVHDLModel.Symbol          import IndexedObjectOrFunctionCallSymbol

from tests.unit.Writer           import _GHDL, _analyze, _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


_DECLARATIONS = dedent("""\
	library ieee;
	use     ieee.std_logic_1164.all;
	use     ieee.numeric_std.all;

	package oracle is
		constant a : integer                := 3;
		constant b : integer                := 5;
		constant c : integer                := 2;
		constant p : boolean                := true;
		constant q : boolean                := false;
		constant r : boolean                := true;
		constant v : bit_vector(7 downto 0) := x"A5";
		constant u : unsigned(7 downto 0)   := x"5A";
		constant s : std_ulogic             := '1';

		type record_t is record
			valid : bit;
			data  : integer;
		end record;
	""")  #: Declarations the written expressions refer to.


def _package(constants: Iterable[Tuple[str, str]]) -> str:
	"""Source text of a package declaring one constant per (subtype, value) pair."""
	declarations = "".join(
		f"\tconstant c{index} : {subtype} := {value};\n" for index, (subtype, value) in enumerate(constants)
	)
	return f"{_DECLARATIONS}{declarations}end package;\n"


@skipIf(_GHDL is None, "GHDL is not on PATH.")
class GHDLOracle(Testcase):
	def test_Name(self) -> None:
		writer = VHDLWriter()
		constants = [
			("integer", writer.Format(IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("maximum"), [
				ParameterAssociationItem(None, _object("a")),
				ParameterAssociationItem(None, _object("b"))
			])))),
			("integer", writer.Format(IndexedObjectOrFunctionCallSymbol(AttributeName("high", SimpleName("integer"))))),
			("unsigned(7 downto 0)", writer.Format(IndexedObjectOrFunctionCallSymbol(ParenthesisName(
				SimpleName("to_unsigned"),
				[ParameterAssociationItem(None, _object("a")), ParameterAssociationItem(SimpleName("size"), IntegerLiteral(8))]
			)))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)

	def test_Literal(self) -> None:
		writer = VHDLWriter()
		constants = [
			("real", writer.Format(FloatingPointLiteral(1e-9))),
			("real", writer.Format(FloatingPointLiteral(-2.5))),
			("time", writer.Format(PhysicalIntegerLiteral(10, "ns"))),
			("time", writer.Format(PhysicalFloatingLiteral(1.5, "ns"))),
			("character", writer.Format(CharacterLiteral("'"))),
			("string", writer.Format(StringLiteral("say \"hi\""))),
			("bit_vector", writer.Format(BinaryBitStringLiteral("1010"))),
			("bit_vector", writer.Format(HexadecimalBitStringLiteral("A5", 8, False))),
			("bit_vector", writer.Format(HexadecimalBitStringLiteral("F", 12, True))),
			("bit_vector", writer.Format(DecimalBitStringLiteral("160", 8))),
		]

		result = _analyze(_package(constants))

		self.assertEqual(0, result.returncode, msg=result.stdout + result.stderr)
