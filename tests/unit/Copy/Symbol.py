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

A copy of a symbol has no parent; it is the parent of its copied name.
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Symbol as SymbolModule
from pyVHDLModel.Base            import Direction, SimpleRange, RangeFromName
from pyVHDLModel.Expression      import IntegerLiteral, DescendingRangeExpression
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, SelectedName, AllName, AttributeName
from pyVHDLModel.Symbol          import PossibleReference, Symbol, LibraryReferenceSymbol, PackageReferenceSymbol, \
                                        ModeViewSymbol, SubprogramReferenceSymbol, ConfigurationSymbol, \
                                        VariableSymbol, SignalSymbol, ContextReferenceSymbol, \
                                        PackageMemberReferenceSymbol, AllPackageMembersReferenceSymbol, \
                                        EntityInstantiationSymbol, ComponentInstantiationSymbol, \
                                        ConfigurationInstantiationSymbol, EntitySymbol, ArchitectureSymbol, \
                                        PackageSymbol, RecordElementSymbol, RangeAttributeSymbol, SubtypeSymbol, \
                                        SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                                        ConstrainedArraySubtypeSymbol, ConstrainedRecordSubtypeSymbol, \
                                        ArrayElementConstraint, RecordElementConstraint, \
                                        SimpleObjectOrFunctionCallSymbol, IndexedObjectOrFunctionCallSymbol, \
                                        AggregateSymbol, LoopSymbol

from tests.unit                  import _Element, _signal
from tests.unit.Copy             import _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _DerivedSignalSymbol(SignalSymbol):
	"""A symbol of a class derived outside pyVHDLModel, with the constructor of its base-class."""


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every symbol class has a ``Copy()`` calling its own constructor."""
		classes = _concreteModelClasses(SymbolModule)

		self.assertIn(SimpleSubtypeSymbol, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class Symbols(Testcase):
	def test_Copy(self) -> None:
		original = Symbol(SimpleName("proc"), PossibleReference.Procedure, parent=_Element())

		copy = original.Copy()

		self.assertIs(Symbol, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Name, copy.Name)
		self.assertIs(copy, copy.Name.Parent)
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
		"""A copy of a symbol of a derived class is an instance of that class."""
		original = _DerivedSignalSymbol(SimpleName("s"))

		copy = original.Copy()

		self.assertIs(_DerivedSignalSymbol, type(copy))
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
			LoopSymbol,
			RecordElementSymbol,
			SubtypeSymbol,
			SimpleSubtypeSymbol,
			SimpleObjectOrFunctionCallSymbol,
			IndexedObjectOrFunctionCallSymbol
		):
			with self.subTest(cls.__name__):
				original =            cls(SelectedName("b", SimpleName("a")), parent=_Element())
				original._reference = declaration

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertIsNot(original.Name, copy.Name)
				self.assertIs(copy, copy.Name.Parent)
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
		self.assertIs(original, constraint.Parent)
		self.assertIs(copy, copy.Constraint.Parent)
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
		declaration =      _Element()
		element =          RecordElementSymbol(SimpleName("data"))
		rng =              DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		constraint =       ArrayElementConstraint([rng])
		original =         ConstrainedRecordSubtypeSymbol(SimpleName("frame"), {element: constraint})
		original.Subtype = declaration

		copy = original.Copy()

		self.assertIs(ConstrainedRecordSubtypeSymbol, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Name, copy.Name)
		self.assertIsNot(original.Constraints, copy.Constraints)
		self.assertNotIn(element, copy.Constraints)
		copyElement, copyConstraint = next(iter(copy.Constraints.items()))
		self.assertIs(RecordElementSymbol, type(copyElement))
		self.assertEqual("data", copyElement.Name.Identifier)
		self.assertIs(copy, copyElement.Parent)
		self.assertIs(ArrayElementConstraint, type(copyConstraint))
		self.assertIsNot(constraint, copyConstraint)
		self.assertIs(copy, copyConstraint.Parent)
		self.assertIsNot(rng, copyConstraint.Constraints[0])
		self.assertEqual("frame(data(7 downto 0))", VHDLWriter().Format(copy))
		self.assertIs(declaration, copy.Subtype)

	def test_Copy_Nested(self) -> None:
		"""A nested record element constraint is copied with its elements and element constraints."""
		field =    RecordElementSymbol(SimpleName("field"))
		inner =    RecordElementConstraint({
			field: ArrayElementConstraint([DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))])
		})
		original = ConstrainedRecordSubtypeSymbol(SimpleName("rec_t"), {RecordElementSymbol(SimpleName("inner")): inner})

		copy = original.Copy()

		copyInner = next(iter(copy.Constraints.values()))
		self.assertIs(RecordElementConstraint, type(copyInner))
		self.assertIsNot(inner, copyInner)
		self.assertIs(copy, copyInner.Parent)
		self.assertNotIn(field, copyInner.Constraints)
		self.assertEqual("rec_t(inner(field(3 downto 0)))", VHDLWriter().Format(copy))


class ArrayElementConstraints(Testcase):
	def test_Copy(self) -> None:
		rows =     DescendingRangeExpression(IntegerLiteral(1), IntegerLiteral(0))
		columns =  DescendingRangeExpression(IntegerLiteral(7), IntegerLiteral(0))
		original = ArrayElementConstraint([rows, columns], parent=_Element())

		copy = original.Copy()

		self.assertIs(ArrayElementConstraint, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Constraints, copy.Constraints)
		self.assertEqual(2, len(copy.Constraints))
		self.assertIsNot(rows, copy.Constraints[0])
		self.assertIsNot(columns, copy.Constraints[1])
		self.assertIs(copy, copy.Constraints[0].Parent)
		self.assertIs(copy, copy.Constraints[1].Parent)
		self.assertEqual("(1 downto 0, 7 downto 0)", VHDLWriter().Format(copy))


class RecordElementConstraints(Testcase):
	def test_Copy(self) -> None:
		element =    RecordElementSymbol(SimpleName("field"))
		constraint = ArrayElementConstraint([DescendingRangeExpression(IntegerLiteral(3), IntegerLiteral(0))])
		original =   RecordElementConstraint({element: constraint}, parent=_Element())

		copy = original.Copy()

		self.assertIs(RecordElementConstraint, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertIsNot(original.Constraints, copy.Constraints)
		copyElement, copyConstraint = next(iter(copy.Constraints.items()))
		self.assertIsNot(element, copyElement)
		self.assertEqual("field", copyElement.Name.Identifier)
		self.assertIs(copy, copyElement.Parent)
		self.assertIsNot(constraint, copyConstraint)
		self.assertIs(copy, copyConstraint.Parent)
		self.assertEqual("(field(3 downto 0))", VHDLWriter().Format(copy))

	def test_Copy_AggregateSymbol(self) -> None:
		original = AggregateSymbol([VariableSymbol(SimpleName("carry")), VariableSymbol(SimpleName("sum"))])

		copy = original.Copy()

		self.assertIs(AggregateSymbol, type(copy))
		self.assertEqual("(carry?, sum?)", str(copy))
		for originalElement, copiedElement in zip(original.Targets, copy.Targets):
			self.assertIsNot(originalElement, copiedElement)
			self.assertIs(copy, copiedElement.Parent)
