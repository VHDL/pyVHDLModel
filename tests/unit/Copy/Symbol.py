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
Copy tests for symbols (:mod:`pyVHDLModel.Symbol`).

A symbol has no parent (it is no :class:`~pyVHDLModel.Base.ModelEntity`), so only its owned children are checked.
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Symbol as SymbolModule
from pyVHDLModel.Base            import Direction, SimpleRange, RangeFromName
from pyVHDLModel.Expression      import IntegerLiteral, DescendingRangeExpression
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, SelectedName, AllName, AttributeName
from pyVHDLModel.Symbol          import PossibleReference, Symbol, LibraryReferenceSymbol, PackageReferenceSymbol
from pyVHDLModel.Symbol          import ModeViewSymbol, SubprogramReferenceSymbol, ConfigurationSymbol, VariableSymbol
from pyVHDLModel.Symbol          import SignalSymbol, ContextReferenceSymbol, PackageMemberReferenceSymbol
from pyVHDLModel.Symbol          import AllPackageMembersReferenceSymbol, EntityInstantiationSymbol
from pyVHDLModel.Symbol          import ComponentInstantiationSymbol, ConfigurationInstantiationSymbol, EntitySymbol
from pyVHDLModel.Symbol          import ArchitectureSymbol, PackageSymbol, RecordElementSymbol, RangeAttributeSymbol
from pyVHDLModel.Symbol          import SubtypeSymbol, SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Symbol          import ConstrainedArraySubtypeSymbol, ConstrainedRecordSubtypeSymbol
from pyVHDLModel.Symbol          import SimpleObjectOrFunctionCallSymbol, IndexedObjectOrFunctionCallSymbol

from tests.unit                  import _Element, _signal
from tests.unit.Copy             import _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _MirrorSignalSymbol(SignalSymbol):
	"""A signal symbol of another package, constructed from an extra parameter (like a :mod:`pyGHDL.dom` class)."""

	def __init__(self, node: int, name: SimpleName) -> None:
		super().__init__(name)
		self._node = node


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every symbol class has a ``Copy()`` calling its own constructor."""
		classes = _concreteModelClasses(SymbolModule)

		self.assertIn(SimpleSubtypeSymbol, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class Symbols(Testcase):
	def test_Copy(self) -> None:
		original = Symbol(SimpleName("proc"), PossibleReference.Procedure)

		copy = original.Copy()

		self.assertIs(Symbol, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNot(original.Name, copy.Name)
		self.assertEqual("proc", copy.Name.Identifier)
		self.assertIs(PossibleReference.Procedure, copy._possibleReferences)
		self.assertIsNone(copy.Reference)
		self.assertEqual(VHDLWriter().Format(original), VHDLWriter().Format(copy))

	def test_Copy_Resolved(self) -> None:
		"""A copy of a resolved symbol references the same declaration."""
		declaration = _signal("s", "bit")
		original = SignalSymbol(SimpleName("s"))
		original.Signal = declaration

		copy = original.Copy()

		self.assertIsNot(original, copy)
		self.assertIs(declaration, copy.Signal)
		self.assertTrue(copy.IsResolved)

	def test_Copy_Derived(self) -> None:
		"""A copy of a symbol of a class derived outside pyVHDLModel is a symbol of the pyVHDLModel class."""
		original = _MirrorSignalSymbol(42, SimpleName("s"))

		copy = original.Copy()

		self.assertIs(SignalSymbol, type(copy))
		self.assertEqual("s", copy.Name.Identifier)

	def test_Copy_Classes(self) -> None:
		"""Every symbol class constructed from a name alone copies its name and keeps its reference."""
		declaration = _Element()
		for cls in (
			LibraryReferenceSymbol,
			PackageReferenceSymbol,
			ModeViewSymbol,
			SubprogramReferenceSymbol,
			ConfigurationSymbol,
			VariableSymbol,
			SignalSymbol,
			ContextReferenceSymbol,
			PackageMemberReferenceSymbol,
			EntityInstantiationSymbol,
			ComponentInstantiationSymbol,
			ConfigurationInstantiationSymbol,
			EntitySymbol,
			ArchitectureSymbol,
			PackageSymbol,
			RecordElementSymbol,
			SubtypeSymbol,
			SimpleSubtypeSymbol,
			SimpleObjectOrFunctionCallSymbol,
			IndexedObjectOrFunctionCallSymbol
		):
			with self.subTest(cls.__name__):
				original = cls(SelectedName("b", SimpleName("a")))
				original._reference = declaration

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNot(original.Name, copy.Name)
				self.assertIsNot(original.Name.Prefix, copy.Name.Prefix)
				self.assertIs(original._possibleReferences, copy._possibleReferences)
				self.assertIs(declaration, copy.Reference)
				self.assertEqual("a.b", VHDLWriter().Format(copy))

	def test_Copy_AllPackageMembers(self) -> None:
		original = AllPackageMembersReferenceSymbol(AllName(SelectedName("numeric_std", SimpleName("ieee"))))

		copy = original.Copy()

		self.assertIs(AllPackageMembersReferenceSymbol, type(copy))
		self.assertIsNot(original.Name, copy.Name)
		self.assertEqual("ieee.numeric_std.all", VHDLWriter().Format(copy))

	def test_Copy_RangeAttribute(self) -> None:
		original = RangeAttributeSymbol(AttributeName("range", SimpleName("v")))

		copy = original.Copy()

		self.assertIs(RangeAttributeSymbol, type(copy))
		self.assertIsNot(original.Name, copy.Name)
		self.assertIsNot(original.Name.Prefix, copy.Name.Prefix)
		self.assertEqual("v'range", VHDLWriter().Format(copy))


class ConstrainedScalarSubtypeSymbols(Testcase):
	def test_Copy(self) -> None:
		declaration = _Element()
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
		original = ConstrainedScalarSubtypeSymbol(SimpleName("integer"), constraint)
		original.Subtype = declaration

		copy = original.Copy()

		self.assertIs(ConstrainedScalarSubtypeSymbol, type(copy))
		self.assertIsNot(original.Name, copy.Name)
		self.assertEqual("integer", copy.Name.Identifier)
		self.assertIsNot(constraint, copy.Constraint)
		self.assertIsNone(copy.Constraint.Parent)
		self.assertIsNot(constraint.LeftBound, copy.Constraint.LeftBound)
		self.assertEqual(VHDLWriter().Format(constraint), VHDLWriter().Format(copy.Constraint))
		self.assertIs(declaration, copy.Subtype)

	def test_Copy_RangeAttribute(self) -> None:
		constraint = RangeFromName(RangeAttributeSymbol(AttributeName("range", SimpleName("v"))))
		original = ConstrainedScalarSubtypeSymbol(SimpleName("natural"), constraint)

		copy = original.Copy()

		self.assertIsNot(constraint, copy.Constraint)
		self.assertIsNot(constraint.Symbol, copy.Constraint.Symbol)
		self.assertEqual("v'range", VHDLWriter().Format(copy.Constraint))


class ConstrainedArraySubtypeSymbols(Testcase):
	def test_Copy(self) -> None:
		declaration = _Element()
		first = DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		second = SimpleName("index")
		original = ConstrainedArraySubtypeSymbol(SimpleName("matrix"), [first, second])
		original.Subtype = declaration

		copy = original.Copy()

		self.assertIs(ConstrainedArraySubtypeSymbol, type(copy))
		self.assertIsNot(original.Name, copy.Name)
		self.assertIsNot(original.Constraints, copy.Constraints)
		self.assertEqual(2, len(copy.Constraints))
		self.assertIsNot(first, copy.Constraints[0])
		self.assertIsNot(first.LeftOperand, copy.Constraints[0].LeftOperand)
		self.assertEqual("7 downto 0", VHDLWriter().Format(copy.Constraints[0]))
		self.assertIsNot(second, copy.Constraints[1])
		self.assertEqual("index", copy.Constraints[1].Identifier)
		self.assertIs(declaration, copy.Subtype)

	def test_Copy_Modify(self) -> None:
		"""Changing the constraints of the copy leaves the original unchanged."""
		constraint = DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		original = ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [constraint])

		copy = original.Copy()
		copy.Constraints[0] = DescendingRangeExpression(IntegerLiteral(15), IntegerLiteral(0))

		self.assertEqual("7 downto 0", VHDLWriter().Format(original.Constraints[0]))
		self.assertEqual("15 downto 0", VHDLWriter().Format(copy.Constraints[0]))


class ConstrainedRecordSubtypeSymbols(Testcase):
	def test_Copy(self) -> None:
		element = RecordElementSymbol(SimpleName("data"))
		constraint = DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		original = ConstrainedRecordSubtypeSymbol(SimpleName("frame"), {element: constraint})

		copy = original.Copy()

		self.assertIs(ConstrainedRecordSubtypeSymbol, type(copy))
		self.assertIsNot(original.Name, copy.Name)
		self.assertIsNot(original.Constraints, copy.Constraints)
		self.assertNotIn(element, copy.Constraints)
		copyElement, copyConstraint = next(iter(copy.Constraints.items()))
		self.assertIs(RecordElementSymbol, type(copyElement))
		self.assertEqual("data", copyElement.Name.Identifier)
		self.assertIsNot(constraint, copyConstraint)
		self.assertEqual("7 downto 0", VHDLWriter().Format(copyConstraint))

	def test_Copy_WithoutConstraint(self) -> None:
		"""A record element without a translated constraint (``None``) keeps it."""
		original = ConstrainedRecordSubtypeSymbol(SimpleName("frame"), {RecordElementSymbol(SimpleName("data")): None})

		copy = original.Copy()

		self.assertListEqual([None], list(copy.Constraints.values()))
