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
Copy tests for ranges (:mod:`pyVHDLModel.Base`).
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Direction, SimpleRange, RangeFromName
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, AttributeName
from pyVHDLModel.Symbol          import RangeAttributeSymbol

from tests.unit                  import _Element
from tests.unit.Copy             import _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _DerivedSimpleRange(SimpleRange):
	"""A range of a class derived outside pyVHDLModel, with the constructor of its base-class."""


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every range class has a ``Copy()`` calling its own constructor."""
		self.assertListEqual([], _copyAboveConstructor((SimpleRange, RangeFromName)))


class SimpleRanges(Testcase):
	def test_Copy(self) -> None:
		left = IntegerLiteral(7)
		right = IntegerLiteral(0)
		original = SimpleRange(left, right, Direction.DownTo, _Element())

		copy = original.Copy()

		self.assertIs(SimpleRange, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertIs(Direction.DownTo, copy.Direction)
		self.assertIsNot(left, copy.LeftBound)
		self.assertIs(copy, copy.LeftBound.Parent)
		self.assertIsNot(right, copy.RightBound)
		self.assertIs(copy, copy.RightBound.Parent)
		self.assertEqual("7 downto 0", VHDLWriter().Format(copy))

	def test_Copy_Derived(self) -> None:
		"""A copy of a range of a derived class is an instance of that class."""
		original = _DerivedSimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)

		copy = original.Copy()

		self.assertIs(_DerivedSimpleRange, type(copy))
		self.assertEqual("0 to 7", VHDLWriter().Format(copy))


class RangesFromName(Testcase):
	def test_Copy(self) -> None:
		symbol = RangeAttributeSymbol(AttributeName("range", SimpleName("v")))
		original = RangeFromName(symbol, _Element())

		copy = original.Copy()

		self.assertIs(RangeFromName, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(symbol, copy.Symbol)
		self.assertIsNot(symbol.Name, copy.Symbol.Name)
		self.assertEqual("v'range", VHDLWriter().Format(copy))
