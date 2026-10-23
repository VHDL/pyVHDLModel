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
Copy tests for object declarations (:mod:`pyVHDLModel.Object`).

``a, b : positive := 5`` becomes ``a : natural := 5; b : positive := 3`` by copies: each declaration owns its subtype
indication and default expression.
"""
from pyTooling.Graph             import Vertex
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Object as ObjectModule
from pyVHDLModel.Base            import Direction, SimpleRange
from pyVHDLModel.Expression      import IntegerLiteral, AdditionExpression
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Object          import Constant, DeferredConstant, Variable, SharedVariable, Signal, File
from pyVHDLModel.Symbol          import ConstrainedScalarSubtypeSymbol

from tests.unit                  import _Element, _subtypeSymbol
from tests.unit.Copy             import _object, _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _DerivedSignal(Signal):
	"""A signal of a class derived outside pyVHDLModel, with the constructor of its base-class."""


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every object class has a ``Copy()`` calling its own constructor."""
		classes = _concreteModelClasses(ObjectModule)

		self.assertIn(File, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class ObjectsWithDefaultExpression(Testcase):
	def test_Copy(self) -> None:
		for cls in (Constant, Variable, Signal):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("positive")
				defaultExpression = AdditionExpression(_object("BITS"), IntegerLiteral(1))
				original = cls(("a", "b"), subtype, defaultExpression, "Documentation.", _Element())

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertTupleEqual(("a", "b"), copy.Identifiers)
				self.assertTupleEqual(("a", "b"), copy.NormalizedIdentifiers)
				self.assertEqual("Documentation.", copy.Documentation)
				self.assertIsNot(subtype, copy.Subtype)
				self.assertIsNot(subtype.Name, copy.Subtype.Name)
				self.assertEqual("positive", copy.Subtype.Name.Identifier)
				self.assertIsNot(defaultExpression, copy.DefaultExpression)
				self.assertIs(copy, copy.DefaultExpression.Parent)
				self.assertIsNot(defaultExpression.LeftOperand, copy.DefaultExpression.LeftOperand)
				self.assertIs(copy.DefaultExpression, copy.DefaultExpression.LeftOperand.Parent)
				self.assertEqual("BITS + 1", VHDLWriter().Format(copy.DefaultExpression))
				self.assertEqual(str(original), str(copy))

	def test_Copy_WithoutDefaultExpression(self) -> None:
		for cls in (Variable, Signal):
			with self.subTest(cls.__name__):
				original = cls(("v", ), _subtypeSymbol("bit"))

				copy = original.Copy()

				self.assertIsNone(copy.DefaultExpression)

	def test_Copy_Resolved(self) -> None:
		"""The subtype of a copy references the same subtype declaration."""
		declaration = _Element()
		subtype = _subtypeSymbol("positive")
		subtype.Subtype = declaration
		original = Constant(("a", ), subtype, IntegerLiteral(5))

		copy = original.Copy()

		self.assertIsNot(subtype, copy.Subtype)
		self.assertIs(declaration, copy.Subtype.Subtype)

	def test_Copy_ObjectVertex(self) -> None:
		"""A copy is not in the object graph."""
		original = Signal(("s", ), _subtypeSymbol("bit"))
		original._objectVertex = Vertex(value=original)

		copy = original.Copy()

		self.assertIsNone(copy.ObjectVertex)

	def test_Copy_Constraint(self) -> None:
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
		original = Signal(("a", "b"), ConstrainedScalarSubtypeSymbol(SimpleName("integer"), constraint), IntegerLiteral(5))

		copy = original.Copy()

		self.assertIsNot(constraint, copy.Subtype.Constraint)
		self.assertIsNot(constraint.LeftBound, copy.Subtype.Constraint.LeftBound)
		self.assertEqual("0 to 7", VHDLWriter().Format(copy.Subtype.Constraint))

	def test_Copy_Modify(self) -> None:
		"""A declaration built from a copy with another subtype and default expression leaves the original unchanged."""
		original = Constant(("a", "b"), _subtypeSymbol("positive"), IntegerLiteral(5))

		firstCopy = original.Copy()
		secondCopy = original.Copy()
		first = Constant(("a", ), _subtypeSymbol("natural"), firstCopy.DefaultExpression)
		second = Constant(("b", ), secondCopy.Subtype, IntegerLiteral(3))

		self.assertEqual("positive", original.Subtype.Name.Identifier)
		self.assertEqual(5, original.DefaultExpression.Value)
		self.assertIs(original, original.DefaultExpression.Parent)
		self.assertEqual("natural", first.Subtype.Name.Identifier)
		self.assertEqual(5, first.DefaultExpression.Value)
		self.assertIs(first, first.DefaultExpression.Parent)
		self.assertEqual("positive", second.Subtype.Name.Identifier)
		self.assertEqual(3, second.DefaultExpression.Value)
		self.assertIsNot(original.Subtype, second.Subtype)

	def test_Copy_Derived(self) -> None:
		"""A copy of a signal of a derived class is an instance of that class."""
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
		original = _DerivedSignal(("s", ), ConstrainedScalarSubtypeSymbol(SimpleName("integer"), constraint))

		copy = original.Copy()

		self.assertIs(_DerivedSignal, type(copy))
		self.assertIs(ConstrainedScalarSubtypeSymbol, type(copy.Subtype))


class ObjectsWithoutDefaultExpression(Testcase):
	def test_Copy(self) -> None:
		for cls in (SharedVariable, File):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("text")
				original = cls(("f", "g"), subtype, "Documentation.", _Element())

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertTupleEqual(("f", "g"), copy.Identifiers)
				self.assertEqual("Documentation.", copy.Documentation)
				self.assertIsNot(subtype, copy.Subtype)
				self.assertIsNot(subtype.Name, copy.Subtype.Name)
				self.assertEqual(str(original), str(copy))

	def test_DeferredConstant(self) -> None:
		subtype = _subtypeSymbol("positive")
		original = DeferredConstant(("BITS", ), subtype, "Documentation.", _Element())
		fullConstant = Constant(("BITS", ), _subtypeSymbol("positive"), IntegerLiteral(8))
		original._constantReference = fullConstant

		copy = original.Copy()

		self.assertIs(DeferredConstant, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertTupleEqual(("BITS", ), copy.Identifiers)
		self.assertEqual("Documentation.", copy.Documentation)
		self.assertIsNot(subtype, copy.Subtype)
		self.assertIs(fullConstant, copy.ConstantReference)
