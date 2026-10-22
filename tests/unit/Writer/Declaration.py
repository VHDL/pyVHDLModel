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
"""Tests for writing alias and attribute declarations with pyVHDLModel.Formatting.VHDL."""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Declaration     import EntityClass, Alias, Attribute, AttributeSpecification
from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import IntegerLiteral, EnumerationLiteral, DescendingRangeExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName
from pyVHDLModel.Symbol          import ConstrainedArraySubtypeSymbol, IndexedObjectOrFunctionCallSymbol

from tests.unit                  import _subtypeSymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _low() -> DescendingRangeExpression:
	"""Range ``3 downto 0``."""
	return DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))


class Aliases(Testcase):
	def test_Alias(self) -> None:
		self.assertEqual("alias clock is clk;\n", VHDLWriter().Format(Alias("clock", _object("clk"))))

	def test_Alias_Subtype(self) -> None:
		alias = Alias(
			"low",
			IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("data"), [_low()])),
			ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [_low()])
		)

		self.assertEqual("alias low : bit_vector(3 downto 0) is data(3 downto 0);\n", VHDLWriter().Format(alias))

	def test_UpperCase(self) -> None:
		alias = Alias("clock", _object("clk"))

		self.assertEqual("ALIAS clock IS clk;\n", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(alias))


class Attributes(Testcase):
	def test_Attribute(self) -> None:
		self.assertEqual("attribute keep : boolean;\n", VHDLWriter().Format(Attribute("keep", _subtypeSymbol("boolean"))))

	def test_Specification(self) -> None:
		specification = AttributeSpecification(
			[SimpleName("valid"), SimpleName("ready")],
			SimpleName("keep"),
			EntityClass.Signal,
			EnumerationLiteral("true")
		)

		self.assertEqual("attribute keep of valid, ready : signal is true;\n", VHDLWriter().Format(specification))

	def test_Specification_EntityClass(self) -> None:
		specification = AttributeSpecification(
			[SimpleName("byte")],
			SimpleName("bits"),
			EntityClass.Subtype,
			IntegerLiteral(8)
		)

		self.assertEqual("attribute bits of byte : subtype is 8;\n", VHDLWriter().Format(specification))

	def test_Specification_UpperCase(self) -> None:
		specification = AttributeSpecification(
			[SimpleName("u")],
			SimpleName("keep"),
			EntityClass.Label,
			EnumerationLiteral("true")
		)
		writer =        VHDLWriter(VHDLStyle(KeywordCase.Upper))

		self.assertEqual("ATTRIBUTE keep OF u : LABEL IS true;\n", writer.Format(specification))

	def test_Specification_Others(self) -> None:
		specification = AttributeSpecification(
			[SimpleName("x")],
			SimpleName("keep"),
			EntityClass.Others,
			EnumerationLiteral("true")
		)

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(specification)

		self.assertEqual("Entity class 'Others' has no VHDL notation.", str(context.exception))
		self.assertIs(specification, context.exception.Element)
