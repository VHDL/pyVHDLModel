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
"""
Tests for pyVHDLModel.Symbol.

Most ``Symbol`` subclasses share an identical shape: constructed from just a ``Name``, fixed to one
``PossibleReference`` flag, with a single settable property used to store the resolved reference.
That shared shape is tested once, table-driven, in ``SimpleReferenceSymbols`` instead of one
hand-written test per class. Classes with distinct behaviour (constraints, the ``Symbol`` base
itself, the object/function-call symbols with no dedicated property) get their own test class.
"""
from unittest import TestCase

from pyVHDLModel.Base   import Direction, SimpleRange, RangeFromName
from pyVHDLModel.Name   import SimpleName, AllName, AttributeName
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Symbol import (
	PossibleReference, Symbol,
	LibraryReferenceSymbol, PackageReferenceSymbol, ModeViewSymbol, SubprogramReferenceSymbol,
	ConfigurationSymbol, VariableSymbol, SignalSymbol, ContextReferenceSymbol,
	PackageMemberReferenceSymbol, AllPackageMembersReferenceSymbol,
	EntityInstantiationSymbol, ComponentInstantiationSymbol, ConfigurationInstantiationSymbol,
	EntitySymbol, ArchitectureSymbol, PackageSymbol,
	RangeAttributeSymbol, RecordElementSymbol, SubtypeSymbol, SimpleSubtypeSymbol,
	ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, ConstrainedRecordSubtypeSymbol,
	SimpleObjectOrFunctionCallSymbol, IndexedObjectOrFunctionCallSymbol,
)


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SymbolBase(TestCase):
	"""
	``Symbol`` itself.

	It is used directly e.g. for ``Alias.Name``, which has no single fixed ``PossibleReference`` - see the design note
	in tests/unit/Declaration.py.
	"""

	def test_Unresolved(self) -> None:
		name = SimpleName("s")
		symbol = Symbol(name, PossibleReference.Signal | PossibleReference.Variable)

		self.assertIs(name, symbol.Name)
		self.assertIsNone(symbol.Reference)
		self.assertFalse(symbol.IsResolved)
		self.assertFalse(bool(symbol))
		self.assertEqual("s?", str(symbol))
		self.assertEqual("Symbol: 's' -> unresolved", repr(symbol))

	def test_Resolved(self) -> None:
		"""Resolution is exposed through each subclass's own named property (see
		``SimpleReferenceSymbols`` below); the base class only exposes the generic, readonly
		``Reference``/``IsResolved``/``__bool__``/``__str__`` machinery every subclass inherits."""
		symbol = LibraryReferenceSymbol(SimpleName("ieee"))
		library = object()
		symbol.Library = library

		self.assertIs(library, symbol.Reference)
		self.assertTrue(symbol.IsResolved)
		self.assertTrue(bool(symbol))
		self.assertEqual(str(library), str(symbol))
		self.assertIn("->", repr(symbol))


# (SymbolClass, property name, expected PossibleReference)
_SIMPLE_REFERENCE_SYMBOLS = (
	(LibraryReferenceSymbol,              "Library",       PossibleReference.Library),
	(PackageReferenceSymbol,              "Package",       PossibleReference.Package),
	(ModeViewSymbol,                      "ModeView",      PossibleReference.View),
	(SubprogramReferenceSymbol,           "Subprogram",    PossibleReference.SubProgram),
	(ConfigurationSymbol,                 "Configuration", PossibleReference.Configuration),
	(VariableSymbol,                      "Variable",      PossibleReference.Variable),
	(SignalSymbol,                        "Signal",        PossibleReference.Signal),
	(ContextReferenceSymbol,              "Context",       PossibleReference.Context),
	(PackageMemberReferenceSymbol,        "Member",        PossibleReference.PackageMember),
	(EntityInstantiationSymbol,           "Entity",        PossibleReference.Entity),
	(ComponentInstantiationSymbol,        "Component",     PossibleReference.Component),
	(ConfigurationInstantiationSymbol,    "Configuration", PossibleReference.Configuration),
	(EntitySymbol,                        "Entity",        PossibleReference.Entity),
	(ArchitectureSymbol,                  "Architecture",  PossibleReference.Architecture),
	(PackageSymbol,                       "Package",       PossibleReference.Package),
)


class SimpleReferenceSymbols(TestCase):
	def test_AllVariants(self) -> None:
		for symbolClass, propertyName, possibleReference in _SIMPLE_REFERENCE_SYMBOLS:
			with self.subTest(symbol=symbolClass.__name__):
				name = SimpleName("target")
				symbol = symbolClass(name)

				self.assertIs(name, symbol.Name)
				self.assertIs(possibleReference, symbol._possibleReferences)
				self.assertIsNone(getattr(symbol, propertyName))
				self.assertFalse(symbol.IsResolved)

				target = object()
				setattr(symbol, propertyName, target)

				self.assertIs(target, getattr(symbol, propertyName))
				self.assertIs(target, symbol.Reference)
				self.assertTrue(symbol.IsResolved)

	def test_AllPackageMembersReferenceSymbol(self) -> None:
		"""Same shape as the table above, but the name must be an ``AllName``
		(``use pkg.all;``), not a plain ``Name``, and the property is plural (``Members``)."""
		name = AllName(SimpleName("pkg"))
		symbol = AllPackageMembersReferenceSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertIs(PossibleReference.PackageMember, symbol._possibleReferences)
		self.assertIsNone(symbol.Members)

		target = object()
		symbol.Members = target

		self.assertIs(target, symbol.Members)


class NoPropertyReferenceSymbols(TestCase):
	"""``RecordElementSymbol``, ``SimpleObjectOrFunctionCallSymbol`` and
	``IndexedObjectOrFunctionCallSymbol`` fix a ``PossibleReference`` like the table above, but expose
	no dedicated named property - only the base ``Symbol.Reference``."""

	def test_RecordElementSymbol(self) -> None:
		symbol = RecordElementSymbol(SimpleName("field"))

		self.assertIs(PossibleReference.RecordElement, symbol._possibleReferences)
		self.assertIsNone(symbol.Reference)

	def test_SimpleObjectOrFunctionCallSymbol(self) -> None:
		symbol = SimpleObjectOrFunctionCallSymbol(SimpleName("x"))

		self.assertIs(PossibleReference.SimpleNameInExpression, symbol._possibleReferences)

	def test_IndexedObjectOrFunctionCallSymbol(self) -> None:
		"""``arr(0)``, ``f(0)`` and ``integer(0)`` are written identically, so all three possibilities
		are carried until the name resolves."""
		symbol = IndexedObjectOrFunctionCallSymbol(SimpleName("x"))

		expected = (
			PossibleReference.Object | PossibleReference.Function |
			PossibleReference.Type | PossibleReference.Subtype
		)
		self.assertIs(expected, symbol._possibleReferences)


class SubtypeSymbols(TestCase):
	def test_SubtypeSymbol(self) -> None:
		name = SimpleName("std_logic")
		symbol = SubtypeSymbol(name)

		self.assertIs(PossibleReference.Type | PossibleReference.Subtype, symbol._possibleReferences)
		self.assertIsNone(symbol.Subtype)

		target = object()
		symbol.Subtype = target

		self.assertIs(target, symbol.Subtype)

	def test_SimpleSubtypeSymbol(self) -> None:
		"""``SimpleSubtypeSymbol`` adds no behaviour of its own over ``SubtypeSymbol``."""
		symbol = SimpleSubtypeSymbol(SimpleName("bit"))

		self.assertIsNone(symbol.Subtype)


class ConstrainedSubtypeSymbols(TestCase):
	"""``signal s : integer range 0 to 15;`` / ``std_logic_vector(7 downto 0)`` / record constraints."""

	def test_ScalarConstraint_WithRange(self) -> None:
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(15), Direction.To)
		symbol = ConstrainedScalarSubtypeSymbol(SimpleName("integer"), constraint)

		self.assertIs(constraint, symbol.Constraint)

	def test_ScalarConstraint_RangeIsMandatory(self) -> None:
		"""``integer range`` isn't a VHDL construct - a type mark without a range constraint is a
		``SimpleSubtypeSymbol``, so the range can't be omitted here."""
		with self.assertRaises(TypeError):
			ConstrainedScalarSubtypeSymbol(SimpleName("integer"))

	def test_ScalarConstraint_WithRangeAttribute(self) -> None:
		"""``subtype index is natural range vector'range;`` - the range constraint is a range attribute,
		which is a range denoted by a name."""
		constraint = RangeFromName(RangeAttributeSymbol(AttributeName("range", SimpleName("vector"))))
		symbol = ConstrainedScalarSubtypeSymbol(SimpleName("natural"), constraint)

		self.assertIs(constraint, symbol.Constraint)

	def test_ArrayConstraint(self) -> None:
		constraint = SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		symbol = ConstrainedArraySubtypeSymbol(SimpleName("std_logic_vector"), [constraint])

		self.assertEqual(1, len(symbol.Constraints))
		self.assertIs(constraint, symbol.Constraints[0])

	def test_RecordConstraint(self) -> None:
		element = RecordElementSymbol(SimpleName("field"))
		constraint = SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		symbol = ConstrainedRecordSubtypeSymbol(SimpleName("rec_t"), {element: constraint})

		self.assertEqual(1, len(symbol.Constraints))
		self.assertIs(constraint, symbol.Constraints[element])
