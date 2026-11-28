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
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base   import ModelEntity, Direction, SimpleRange, RangeFromName
from pyVHDLModel.Name   import SimpleName, SelectedName, AllName, AttributeName
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Symbol import PossibleReference, Symbol, LibraryReferenceSymbol, PackageReferenceSymbol, \
                               ModeViewSymbol, SubprogramReferenceSymbol, ConfigurationSymbol, VariableSymbol, \
                               SignalSymbol, ContextReferenceSymbol, PackageMemberReferenceSymbol, \
                               AllPackageMembersReferenceSymbol, EntityInstantiationSymbol, \
                               ComponentInstantiationSymbol, ConfigurationInstantiationSymbol, EntitySymbol, \
                               ArchitectureSymbol, PackageSymbol, RangeAttributeSymbol, RecordElementSymbol, \
                               SubtypeSymbol, SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                               ConstrainedArraySubtypeSymbol, ConstrainedRecordSubtypeSymbol, \
                               ArrayElementConstraint, RecordElementConstraint, SimpleObjectOrFunctionCallSymbol, \
                               IndexedObjectOrFunctionCallSymbol, AggregateSymbol, LoopSymbol, \
                               ResolutionIndicationMixin, ResolutionFunctionSymbol, ArrayElementResolution, \
                               RecordResolution, RecordElementResolution

from tests.unit         import _Element


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SymbolBase(Testcase):
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

	def test_ModelEntity(self) -> None:
		"""A symbol is a model entity without a parent; it is the parent of its name."""
		name =   SimpleName("s")
		symbol = Symbol(name, PossibleReference.Signal)

		self.assertIsInstance(symbol, ModelEntity)
		self.assertIsNone(symbol.Parent)
		self.assertIs(symbol, name.Parent)

	def test_Parent(self) -> None:
		parent = _Element()
		symbol = Symbol(SimpleName("s"), PossibleReference.Signal, parent=parent)

		self.assertIs(parent, symbol.Parent)

	def test_Parent_Assigned(self) -> None:
		"""The model entity using a symbol sets its parent."""
		parent =        _Element()
		symbol =        Symbol(SimpleName("s"), PossibleReference.Signal)
		symbol.Parent = parent

		self.assertIs(parent, symbol.Parent)

	def test_Slots(self) -> None:
		"""A symbol has no instance dictionary: an undeclared attribute can't be set."""
		symbol = Symbol(SimpleName("s"), PossibleReference.Signal)

		with self.assertRaises(AttributeError):
			symbol.Undeclared = 1

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
	(LoopSymbol,                          "Loop",          PossibleReference.Label),
)


class SimpleReferenceSymbols(Testcase):
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

	def test_AllVariants_Parent(self) -> None:
		for symbolClass, _, _ in _SIMPLE_REFERENCE_SYMBOLS:
			with self.subTest(symbol=symbolClass.__name__):
				parent = _Element()
				name =   SimpleName("target")
				symbol = symbolClass(name, parent=parent)

				self.assertIs(parent, symbol.Parent)
				self.assertIs(symbol, name.Parent)

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

	def test_AllPackageMembersReferenceSymbol_Parent(self) -> None:
		parent = _Element()
		name =   AllName(SimpleName("pkg"))
		symbol = AllPackageMembersReferenceSymbol(name, parent=parent)

		self.assertIs(parent, symbol.Parent)
		self.assertIs(symbol, name.Parent)


class NoPropertyReferenceSymbols(Testcase):
	"""
	Symbols without a dedicated reference property.

	``RecordElementSymbol``, ``SimpleObjectOrFunctionCallSymbol`` and
	``IndexedObjectOrFunctionCallSymbol`` fix a ``PossibleReference`` like the table above, but expose
	no dedicated named property - only the base ``Symbol.Reference``.
	"""

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

	def test_Parent(self) -> None:
		for symbolClass in (RecordElementSymbol, SimpleObjectOrFunctionCallSymbol, IndexedObjectOrFunctionCallSymbol):
			with self.subTest(symbol=symbolClass.__name__):
				parent = _Element()
				name =   SimpleName("x")
				symbol = symbolClass(name, parent=parent)

				self.assertIs(parent, symbol.Parent)
				self.assertIs(symbol, name.Parent)


class SubtypeSymbols(Testcase):
	def test_SubtypeSymbol(self) -> None:
		name = SimpleName("std_logic")
		symbol = SubtypeSymbol(name)

		self.assertIs(PossibleReference.Type | PossibleReference.Subtype, symbol._possibleReferences)
		self.assertIsNone(symbol.Subtype)

		target = object()
		symbol.Subtype = target

		self.assertIs(target, symbol.Subtype)

	def test_TypeMark_SimpleName(self) -> None:
		symbol = SimpleSubtypeSymbol(SimpleName("Natural"))

		self.assertEqual("Natural", symbol.TypeMark)

	def test_TypeMark_SelectedName(self) -> None:
		symbol = SimpleSubtypeSymbol(SelectedName("unsigned", SelectedName("numeric_std", SimpleName("ieee"))))

		self.assertEqual("ieee.numeric_std.unsigned", symbol.TypeMark)

	def test_SimpleSubtypeSymbol(self) -> None:
		"""``SimpleSubtypeSymbol`` adds no behaviour of its own over ``SubtypeSymbol``."""
		symbol = SimpleSubtypeSymbol(SimpleName("bit"))

		self.assertIsNone(symbol.Subtype)

	def test_Parent(self) -> None:
		for symbolClass in (SubtypeSymbol, SimpleSubtypeSymbol):
			with self.subTest(symbol=symbolClass.__name__):
				parent = _Element()
				name =   SimpleName("bit")
				symbol = symbolClass(name, parent=parent)

				self.assertIs(parent, symbol.Parent)
				self.assertIs(symbol, name.Parent)


class ConstrainedSubtypeSymbols(Testcase):
	"""``signal s : integer range 0 to 15;`` / ``std_logic_vector(7 downto 0)`` / record constraints."""

	def test_ScalarConstraint_WithRange(self) -> None:
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(15), Direction.To)
		symbol = ConstrainedScalarSubtypeSymbol(SimpleName("integer"), constraint)

		self.assertIs(constraint, symbol.Constraint)
		self.assertIs(symbol, constraint.Parent)

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
		self.assertIs(symbol, constraint.Parent)

	def test_ArrayConstraint(self) -> None:
		constraint = SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		symbol = ConstrainedArraySubtypeSymbol(SimpleName("std_logic_vector"), [constraint])

		self.assertEqual(1, len(symbol.Constraints))
		self.assertIs(constraint, symbol.Constraints[0])
		self.assertIs(symbol, constraint.Parent)

	def test_RecordConstraint(self) -> None:
		element =    RecordElementSymbol(SimpleName("field"))
		constraint = ArrayElementConstraint([SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)])
		symbol =     ConstrainedRecordSubtypeSymbol(SimpleName("rec_t"), {element: constraint})

		self.assertEqual(1, len(symbol.Constraints))
		self.assertIs(constraint, symbol.Constraints[element])
		self.assertIs(symbol, element.Parent)
		self.assertIs(symbol, constraint.Parent)

	def test_ScalarConstraint_Parent(self) -> None:
		parent =     _Element()
		name =       SimpleName("integer")
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(15), Direction.To)
		symbol =     ConstrainedScalarSubtypeSymbol(name, constraint, parent=parent)

		self.assertIs(parent, symbol.Parent)
		self.assertIs(symbol, name.Parent)

	def test_ArrayConstraint_Parent(self) -> None:
		parent =     _Element()
		name =       SimpleName("std_logic_vector")
		constraint = SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		symbol =     ConstrainedArraySubtypeSymbol(name, [constraint], parent=parent)

		self.assertIs(parent, symbol.Parent)
		self.assertIs(symbol, name.Parent)

	def test_RecordConstraint_Parent(self) -> None:
		parent =     _Element()
		name =       SimpleName("rec_t")
		element =    RecordElementSymbol(SimpleName("field"))
		constraint = ArrayElementConstraint([SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)])
		symbol =     ConstrainedRecordSubtypeSymbol(name, {element: constraint}, parent=parent)

		self.assertIs(parent, symbol.Parent)
		self.assertIs(symbol, name.Parent)


class ElementConstraints(Testcase):
	"""``signal s : rec_t(data(7 downto 0), m(0 to 1, 0 to 7), inner(field(3 downto 0)));``"""

	def test_ArrayElementConstraint(self) -> None:
		rng =        SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		constraint = ArrayElementConstraint([rng])

		self.assertIsNone(constraint.Parent)
		self.assertListEqual([rng], constraint.Constraints)
		self.assertIs(constraint, rng.Parent)
		self.assertEqual("(7 downto 0)", str(constraint))

	def test_ArrayElementConstraint_Dimensions(self) -> None:
		rows =       SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To)
		columns =    SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
		constraint = ArrayElementConstraint([rows, columns])

		self.assertListEqual([rows, columns], constraint.Constraints)
		self.assertIs(constraint, rows.Parent)
		self.assertIs(constraint, columns.Parent)
		self.assertEqual("(0 to 1, 0 to 7)", str(constraint))

	def test_ArrayElementConstraint_Parent(self) -> None:
		parent =     _Element()
		constraint = ArrayElementConstraint(
			[SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)],
			parent=parent
		)

		self.assertIs(parent, constraint.Parent)

	def test_RecordElementConstraint(self) -> None:
		element =    RecordElementSymbol(SimpleName("field"))
		inner =      ArrayElementConstraint([SimpleRange(IntegerLiteral(3), IntegerLiteral(0), Direction.DownTo)])
		constraint = RecordElementConstraint({element: inner})

		self.assertIsNone(constraint.Parent)
		self.assertDictEqual({element: inner}, constraint.Constraints)
		self.assertIs(constraint, element.Parent)
		self.assertIs(constraint, inner.Parent)
		self.assertEqual("(field(3 downto 0))", str(constraint))

	def test_RecordElementConstraint_Parent(self) -> None:
		parent =     _Element()
		inner =      ArrayElementConstraint([SimpleRange(IntegerLiteral(3), IntegerLiteral(0), Direction.DownTo)])
		constraint = RecordElementConstraint({RecordElementSymbol(SimpleName("field")): inner}, parent=parent)

		self.assertIs(parent, constraint.Parent)

	def test_RecordConstraint_Nested(self) -> None:
		"""A record element constraint is the parent of its elements and element constraints, at every level."""
		data =        RecordElementSymbol(SimpleName("data"))
		dataRange =   ArrayElementConstraint([SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)])
		field =       RecordElementSymbol(SimpleName("field"))
		fieldRange =  ArrayElementConstraint([SimpleRange(IntegerLiteral(3), IntegerLiteral(0), Direction.DownTo)])
		inner =       RecordElementSymbol(SimpleName("inner"))
		innerRecord = RecordElementConstraint({field: fieldRange})
		symbol =      ConstrainedRecordSubtypeSymbol(SimpleName("rec_t"), {data: dataRange, inner: innerRecord})

		self.assertListEqual([data, inner], list(symbol.Constraints))
		self.assertIs(dataRange, symbol.Constraints[data])
		self.assertIs(innerRecord, symbol.Constraints[inner])
		self.assertIs(symbol, data.Parent)
		self.assertIs(symbol, dataRange.Parent)
		self.assertIs(symbol, inner.Parent)
		self.assertIs(symbol, innerRecord.Parent)
		self.assertIs(innerRecord, field.Parent)
		self.assertIs(innerRecord, fieldRange.Parent)


class AggregateSymbols(Testcase):
	def test_Construction(self) -> None:
		carry =  VariableSymbol(SimpleName("carry"))
		sum =    VariableSymbol(SimpleName("sum"))
		symbol = AggregateSymbol([carry, sum])

		self.assertListEqual([carry, sum], symbol.Targets)
		self.assertIsNone(symbol.Name)
		self.assertIs(PossibleReference.Variable, symbol._possibleReferences)
		self.assertFalse(symbol.IsResolved)
		self.assertEqual("(carry?, sum?)", str(symbol))
		self.assertEqual(
			"AggregateSymbol: (VariableSymbol: 'carry' -> unresolved, VariableSymbol: 'sum' -> unresolved)",
			repr(symbol)
		)

	def test_Parent(self) -> None:
		"""The group is the parent of its targets."""
		parent = _Element()
		carry =  VariableSymbol(SimpleName("carry"))
		sum =    VariableSymbol(SimpleName("sum"))
		symbol = AggregateSymbol([carry, sum], parent=parent)

		self.assertIs(parent, symbol.Parent)
		self.assertIs(symbol, carry.Parent)
		self.assertIs(symbol, sum.Parent)

	def test_PossibleReferences(self) -> None:
		"""The group can reference what any of its targets can reference."""
		symbol = AggregateSymbol([VariableSymbol(SimpleName("v")), SignalSymbol(SimpleName("s"))])

		self.assertIs(PossibleReference.Variable | PossibleReference.Signal, symbol._possibleReferences)

	def test_Nested(self) -> None:
		inner =  AggregateSymbol([VariableSymbol(SimpleName("b")), VariableSymbol(SimpleName("c"))])
		symbol = AggregateSymbol([VariableSymbol(SimpleName("a")), inner])

		self.assertEqual("(a?, (b?, c?))", str(symbol))

	def test_IsResolved(self) -> None:
		"""Resolved once every target is resolved."""
		carry =  VariableSymbol(SimpleName("carry"))
		sum =    VariableSymbol(SimpleName("sum"))
		symbol = AggregateSymbol([carry, sum])

		carry._reference = object()
		self.assertFalse(symbol.IsResolved)

		sum._reference = object()
		self.assertTrue(symbol.IsResolved)
		self.assertTrue(bool(symbol))

	def test_Targets_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			AggregateSymbol(None)

		self.assertEqual("Parameter 'targets' is None.", str(context.exception))

	def test_Targets_NotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			AggregateSymbol(5)

		self.assertEqual("Parameter 'targets' is not iterable.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Targets_NoSymbol(self) -> None:
		with self.assertRaises(TypeError) as context:
			AggregateSymbol([VariableSymbol(SimpleName("a")), 5])

		self.assertEqual("Target in parameter 'targets' is not of type 'Symbol'.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Targets_Single(self) -> None:
		with self.assertRaises(ValueError) as context:
			AggregateSymbol([VariableSymbol(SimpleName("a"))])

		self.assertEqual("Parameter 'targets' has fewer than two targets.", str(context.exception))
		self.assertEqual(
			["Got 1 target(s).", "A single target in parentheses is no aggregate; use the target's symbol."],
			context.exception.__notes__
		)


class ResolutionFunctionSymbols(Testcase):
	"""``subtype std_logic is resolved std_ulogic;``"""

	def test_Construction(self) -> None:
		name =   SimpleName("resolved")
		symbol = ResolutionFunctionSymbol(name)

		self.assertIsInstance(symbol, Symbol)
		self.assertIsInstance(symbol, ResolutionIndicationMixin)
		self.assertIs(PossibleReference.Function, symbol._possibleReferences)
		self.assertIs(name, symbol.Name)
		self.assertIs(symbol, name.Parent)
		self.assertIsNone(symbol.Function)
		self.assertEqual("resolved?", str(symbol))

	def test_Function(self) -> None:
		symbol = ResolutionFunctionSymbol(SimpleName("resolved"))
		target = object()

		symbol.Function = target

		self.assertIs(target, symbol.Function)
		self.assertIs(target, symbol.Reference)
		self.assertEqual("resolved", str(symbol))

	def test_Parent(self) -> None:
		parent = _Element()
		symbol = ResolutionFunctionSymbol(SimpleName("resolved"), parent=parent)

		self.assertIs(parent, symbol.Parent)


class ArrayElementResolutions(Testcase):
	"""``subtype std_logic_vector is (resolved) std_ulogic_vector;``"""

	def test_Construction(self) -> None:
		function =   ResolutionFunctionSymbol(SimpleName("resolved"))
		resolution = ArrayElementResolution(function)

		self.assertIsInstance(resolution, ResolutionIndicationMixin)
		self.assertIsNone(resolution.Parent)
		self.assertIs(function, resolution.Resolution)
		self.assertIs(resolution, function.Parent)
		self.assertEqual("(resolved?)", str(resolution))

	def test_Nested(self) -> None:
		"""``((resolved))``: the elements of a multi-level array."""
		inner =      ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
		resolution = ArrayElementResolution(inner)

		self.assertIs(inner, resolution.Resolution)
		self.assertIs(resolution, inner.Parent)
		self.assertEqual("((resolved?))", str(resolution))

	def test_Parent(self) -> None:
		parent =     _Element()
		resolution = ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")), parent=parent)

		self.assertIs(parent, resolution.Parent)

	def test_Resolution_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			ArrayElementResolution(None)

		self.assertEqual("Parameter 'resolution' is None.", str(context.exception))

	def test_Resolution_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			ArrayElementResolution(SimpleName("resolved"))

		self.assertEqual("Parameter 'resolution' is not of type 'ResolutionIndicationMixin'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)


class RecordResolutions(Testcase):
	"""``subtype pair is (a resolved, b (resolved)) pair_t;``"""

	def test_Construction(self) -> None:
		a =          RecordElementResolution(
			RecordElementSymbol(SimpleName("a")),
			ResolutionFunctionSymbol(SimpleName("resolved"))
		)
		b =          RecordElementResolution(
			RecordElementSymbol(SimpleName("b")),
			ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
		)
		resolution = RecordResolution([a, b])

		self.assertIsInstance(resolution, ResolutionIndicationMixin)
		self.assertIsNone(resolution.Parent)
		self.assertListEqual([a, b], resolution.Elements)
		self.assertIs(resolution, a.Parent)
		self.assertIs(resolution, b.Parent)
		self.assertEqual("(a resolved?, b (resolved?))", str(resolution))

	def test_Parent(self) -> None:
		parent =     _Element()
		element =    RecordElementResolution(
			RecordElementSymbol(SimpleName("a")),
			ResolutionFunctionSymbol(SimpleName("resolved"))
		)
		resolution = RecordResolution([element], parent=parent)

		self.assertIs(parent, resolution.Parent)

	def test_Elements_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			RecordResolution(None)

		self.assertEqual("Parameter 'elements' is None.", str(context.exception))

	def test_Elements_NotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			RecordResolution(5)

		self.assertEqual("Parameter 'elements' is not iterable.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Elements_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			RecordResolution([ResolutionFunctionSymbol(SimpleName("resolved"))])

		self.assertEqual(
			"Element of parameter 'elements' is not of type 'RecordElementResolution'.",
			str(context.exception)
		)
		self.assertEqual(["Got type 'pyVHDLModel.Symbol.ResolutionFunctionSymbol'."], context.exception.__notes__)

	def test_Elements_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			RecordResolution([])

		self.assertEqual("Parameter 'elements' is empty.", str(context.exception))


class RecordElementResolutions(Testcase):
	"""``b (resolved)`` in ``(a resolved, b (resolved))``"""

	def test_Construction(self) -> None:
		element =    RecordElementSymbol(SimpleName("b"))
		inner =      ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
		resolution = RecordElementResolution(element, inner)

		self.assertIsNone(resolution.Parent)
		self.assertIs(element, resolution.Element)
		self.assertIs(inner, resolution.Resolution)
		self.assertIs(resolution, element.Parent)
		self.assertIs(resolution, inner.Parent)
		self.assertEqual("b (resolved?)", str(resolution))

	def test_Parent(self) -> None:
		parent =     _Element()
		resolution = RecordElementResolution(
			RecordElementSymbol(SimpleName("a")),
			ResolutionFunctionSymbol(SimpleName("resolved")),
			parent=parent
		)

		self.assertIs(parent, resolution.Parent)

	def test_Element_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			RecordElementResolution(None, ResolutionFunctionSymbol(SimpleName("resolved")))

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_Element_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			RecordElementResolution(SimpleName("a"), ResolutionFunctionSymbol(SimpleName("resolved")))

		self.assertEqual("Parameter 'element' is not of type 'RecordElementSymbol'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)

	def test_Resolution_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			RecordElementResolution(RecordElementSymbol(SimpleName("a")), None)

		self.assertEqual("Parameter 'resolution' is None.", str(context.exception))

	def test_Resolution_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			RecordElementResolution(RecordElementSymbol(SimpleName("a")), SimpleName("resolved"))

		self.assertEqual("Parameter 'resolution' is not of type 'ResolutionIndicationMixin'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)


class SubtypeSymbolResolutions(Testcase):
	"""``signal s : resolved std_ulogic;``: the resolution indication of a subtype indication."""

	def test_None(self) -> None:
		symbol = SimpleSubtypeSymbol(SimpleName("std_ulogic"))

		self.assertIsNone(symbol.Resolution)
		self.assertEqual("std_ulogic?", str(symbol))

	def test_SimpleSubtypeSymbol(self) -> None:
		resolution = ResolutionFunctionSymbol(SimpleName("resolved"))
		symbol =     SimpleSubtypeSymbol(SimpleName("std_ulogic"), resolution=resolution)

		self.assertIs(resolution, symbol.Resolution)
		self.assertIs(symbol, resolution.Parent)
		self.assertEqual("resolved? std_ulogic?", str(symbol))

	def test_ConstrainedScalarSubtypeSymbol(self) -> None:
		"""``subtype x01 is resolved std_ulogic range 'X' to '1';``"""
		resolution = ResolutionFunctionSymbol(SimpleName("resolved"))
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To)
		symbol =     ConstrainedScalarSubtypeSymbol(SimpleName("std_ulogic"), constraint, resolution=resolution)

		self.assertIs(resolution, symbol.Resolution)
		self.assertIs(symbol, resolution.Parent)
		self.assertIs(constraint, symbol.Constraint)

	def test_ConstrainedArraySubtypeSymbol(self) -> None:
		"""``signal v : (resolved) std_ulogic_vector(7 downto 0);``"""
		resolution = ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
		constraint = SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		symbol =     ConstrainedArraySubtypeSymbol(SimpleName("std_ulogic_vector"), [constraint], resolution=resolution)

		self.assertIs(resolution, symbol.Resolution)
		self.assertIs(symbol, resolution.Parent)
		self.assertListEqual([constraint], symbol.Constraints)

	def test_ConstrainedRecordSubtypeSymbol(self) -> None:
		"""``signal p : (a resolved) pair_t(b(3 downto 0));``"""
		resolution = RecordResolution([
			RecordElementResolution(RecordElementSymbol(SimpleName("a")), ResolutionFunctionSymbol(SimpleName("resolved")))
		])
		element =    RecordElementSymbol(SimpleName("b"))
		constraint = ArrayElementConstraint([SimpleRange(IntegerLiteral(3), IntegerLiteral(0), Direction.DownTo)])
		symbol =     ConstrainedRecordSubtypeSymbol(SimpleName("pair_t"), {element: constraint}, resolution=resolution)

		self.assertIs(resolution, symbol.Resolution)
		self.assertIs(symbol, resolution.Parent)
		self.assertIs(constraint, symbol.Constraints[element])

	def test_SimpleSubtypeSymbol_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			SimpleSubtypeSymbol(SimpleName("std_ulogic"), resolution=SimpleName("resolved"))

		self.assertEqual("Parameter 'resolution' is not of type 'ResolutionIndicationMixin'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)

	def test_ConstrainedScalarSubtypeSymbol_Type(self) -> None:
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To)

		with self.assertRaises(TypeError) as context:
			ConstrainedScalarSubtypeSymbol(SimpleName("std_ulogic"), constraint, resolution=SimpleName("resolved"))

		self.assertEqual("Parameter 'resolution' is not of type 'ResolutionIndicationMixin'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)

	def test_ConstrainedArraySubtypeSymbol_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			ConstrainedArraySubtypeSymbol(SimpleName("std_ulogic_vector"), [], resolution=SimpleName("resolved"))

		self.assertEqual("Parameter 'resolution' is not of type 'ResolutionIndicationMixin'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)

	def test_ConstrainedRecordSubtypeSymbol_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			ConstrainedRecordSubtypeSymbol(SimpleName("pair_t"), {}, resolution=SimpleName("resolved"))

		self.assertEqual("Parameter 'resolution' is not of type 'ResolutionIndicationMixin'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Name.SimpleName'."], context.exception.__notes__)
