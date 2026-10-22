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
#
"""
Tests for pyVHDLModel.Association.

An association item is the parent of its formal and its actual, if they are model entities.
"""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Association import GenericAssociationItem, PortAssociationItem, ParameterAssociationItem
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Name        import SimpleName, ParenthesisName

from tests.unit              import _signalSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class AssociationItems(Testcase):
	def test_Formal(self) -> None:
		formal = SimpleName("G")
		association = GenericAssociationItem(formal, IntegerLiteral(1))

		self.assertIs(association, formal.Parent)

	def test_Formal_Partial(self) -> None:
		formal = ParenthesisName(SimpleName("a"), [IntegerLiteral(0)])
		association = PortAssociationItem(formal, SimpleName("s"))

		self.assertIs(association, formal.Parent)

	def test_Formal_Symbol(self) -> None:
		"""A symbol has no parent: the association leaves it alone."""
		formal = _signalSymbol("a")

		PortAssociationItem(formal, SimpleName("s"))

		self.assertNotIn("Parent", vars(formal))

	def test_Actual(self) -> None:
		actual = IntegerLiteral(1)
		association = GenericAssociationItem(SimpleName("G"), actual)

		self.assertIs(association, actual.Parent)

	def test_Actual_Name(self) -> None:
		actual = SimpleName("s")
		association = PortAssociationItem(None, actual)

		self.assertIs(association, actual.Parent)

	def test_Actual_Symbol(self) -> None:
		actual = _signalSymbol("s")

		PortAssociationItem(SimpleName("p"), actual)

		self.assertNotIn("Parent", vars(actual))

	def test_Actual_None(self) -> None:
		association = ParameterAssociationItem(SimpleName("x"), None)

		self.assertIsNone(association.Actual)
