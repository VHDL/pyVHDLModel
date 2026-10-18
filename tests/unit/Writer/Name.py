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
"""Tests for writing names with pyVHDLModel.Formatting.VHDL."""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import ParameterAssociationItem
from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import DescendingRangeExpression, IntegerLiteral
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName
from pyVHDLModel.Name            import AttributeName, AllName, OpenName

from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Names(Testcase):
	def test_SimpleName(self) -> None:
		self.assertEqual("Clock", VHDLWriter().Format(SimpleName("Clock")))

	def test_SelectedName(self) -> None:
		name = SelectedName("numeric_std", SimpleName("ieee"))

		self.assertEqual("ieee.numeric_std", VHDLWriter().Format(name))

	def test_AllName(self) -> None:
		name = AllName(SelectedName("numeric_std", SimpleName("ieee")))

		self.assertEqual("ieee.numeric_std.all", VHDLWriter().Format(name))

	def test_AllName_UpperCase(self) -> None:
		name = AllName(SelectedName("numeric_std", SimpleName("ieee")))

		self.assertEqual("ieee.numeric_std.ALL", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(name))

	def test_AttributeName(self) -> None:
		name = AttributeName("range", SimpleName("v"))

		self.assertEqual("v'range", VHDLWriter().Format(name))

	def test_AttributeName_Selected(self) -> None:
		name = AttributeName("length", SelectedName("data", SimpleName("r")))

		self.assertEqual("r.data'length", VHDLWriter().Format(name))

	def test_IndexedName(self) -> None:
		name = IndexedName(SimpleName("m"), [_object("i"), IntegerLiteral(1)])

		self.assertEqual("m(i, 1)", VHDLWriter().Format(name))

	def test_OpenName(self) -> None:
		self.assertEqual("open", VHDLWriter().Format(OpenName()))

	def test_SlicedName(self) -> None:
		name = SlicedName("v")

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(name)

		self.assertEqual("Sliced name carries no discrete range.", str(context.exception))
		self.assertEqual(
			["Use a 'ParenthesisName' with a range expression as association."],
			context.exception.__notes__
		)


class ParenthesisNames(Testcase):
	def test_AssociationItems(self) -> None:
		name = ParenthesisName(SimpleName("resize"), [
			ParameterAssociationItem(None, _object("a")),
			ParameterAssociationItem(SimpleName("new_size"), IntegerLiteral(8))
		])

		self.assertEqual("resize(a, new_size => 8)", VHDLWriter().Format(name))

	def test_Expressions(self) -> None:
		"""pyGHDL passes the actuals as plain expressions."""
		name = ParenthesisName(SimpleName("maximum"), [_object("a"), _object("b")])

		self.assertEqual("maximum(a, b)", VHDLWriter().Format(name))

	def test_Slice(self) -> None:
		name = ParenthesisName(SimpleName("v"), [DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))])

		self.assertEqual("v(3 downto 0)", VHDLWriter().Format(name))

	def test_Selected(self) -> None:
		name = ParenthesisName(SelectedName("to_unsigned", SimpleName("numeric_std")), [_object("n"), IntegerLiteral(8)])

		self.assertEqual("numeric_std.to_unsigned(n, 8)", VHDLWriter().Format(name))
