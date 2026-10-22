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
Copy tests for ranges and the class of a copy (:mod:`pyVHDLModel.Base`).
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Direction, SimpleRange, RangeFromName, modelClassOf
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


class _MirrorSimpleRange(SimpleRange):
	"""A range of another package, constructed from an extra parameter (like a :mod:`pyGHDL.dom` class)."""

	_node: int  #: The extra constructor parameter.

	def __init__(self, node: int, leftBound: IntegerLiteral, rightBound: IntegerLiteral, direction: Direction) -> None:
		super().__init__(leftBound, rightBound, direction)
		self._node = node


class _DerivedMirrorSimpleRange(_MirrorSimpleRange):
	"""A class derived from a class derived outside pyVHDLModel."""


class ModelClasses(Testcase):
	def test_ModelClass(self) -> None:
		self.assertIs(SimpleName, modelClassOf(SimpleName("a")))

	def test_Derived(self) -> None:
		"""A class derived outside pyVHDLModel is replaced by its nearest base-class from pyVHDLModel."""
		element = _MirrorSimpleRange(42, IntegerLiteral(0), IntegerLiteral(7), Direction.To)

		self.assertIs(SimpleRange, modelClassOf(element))

	def test_Derived_Twice(self) -> None:
		element = _DerivedMirrorSimpleRange(42, IntegerLiteral(0), IntegerLiteral(7), Direction.To)

		self.assertIs(SimpleRange, modelClassOf(element))


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
		"""A copy of a range of a class derived outside pyVHDLModel is a range of the pyVHDLModel class."""
		original = _MirrorSimpleRange(42, IntegerLiteral(0), IntegerLiteral(7), Direction.To)

		copy = original.Copy()

		self.assertIs(SimpleRange, type(copy))
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
