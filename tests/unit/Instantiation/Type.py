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
"""Tests for pyVHDLModel.Type."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, RangeFromName, SimpleRange
from pyVHDLModel.Name       import SimpleName, AttributeName
from pyVHDLModel.Symbol     import RangeAttributeSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Expression import IntegerLiteral, CharacterEnumerationLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Object     import Variable
from pyVHDLModel.Subprogram import Procedure
from pyVHDLModel.Type       import Subtype, RangedScalarType, EnumeratedType, IntegerType, RealType, PhysicalType, \
                                   ArrayType, RecordTypeElement, RecordType, ProtectedType, ProtectedTypeBody, \
                                   AccessType, FileType

from tests.unit             import _Element, _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _range(left: int = 0, right: int = 15, direction: Direction = Direction.To) -> SimpleRange:
	return SimpleRange(IntegerLiteral(left), IntegerLiteral(right), direction)


class ParentAndDocumentationWiringAcrossAllLeafTypes(Testcase):
	"""``BaseType`` provides identifier/documentation/parent handling and the (private,
	regression-tested-here) ``_objectVertex`` slot to every type class - but ``Type``, ``AnonymousType``,
	``FullType``, ``ScalarType``, ``CompositeType`` and ``RangedScalarType`` are pure taxonomy markers
	with no VHDL construct of their own (never directly instantiated anywhere in pyGHDL.dom, confirmed
	by grep) and either add no ``__init__`` override at all, or (``RangedScalarType``) are only ever
	reached through a further concrete subclass - so they are deliberately not instantiated directly
	here. Instead, every *concrete* leaf type below is checked directly, one by one, rather than
	assuming "tested once via the base class" is enough.

	That assumption is exactly what let a real bug through: unlike a true mixin (one shared
	implementation), each concrete leaf class below defines its *own* ``__init__`` that independently
	forwards to ``BaseType.__init__``, so each one carries its own, separate risk of getting that
	forwarding call wrong. Confirmed and fixed here: every single one of them called
	``super().__init__(identifier, parent)`` positionally, which ``BaseType``'s
	``(identifier, documentation=None, parent=None)`` signature silently misinterprets - ``parent``
	landed in the ``documentation`` slot, and the real ``Parent`` chain was never set (e.g.
	``ProtectedType("pt", parent=parent)`` previously left ``.Parent`` as ``None`` and
	``.Documentation`` holding the parent object itself).

	None of these classes exposed their own ``documentation`` parameter at all (only ``BaseType``
	did) - fixed alongside the ``Parent`` bug, since it's the same forwarding call: every constructor
	below now accepts ``documentation`` in the same position as ``BaseType`` itself, so each
	``super().__init__(identifier, documentation, parent)`` call is a plain, correctly-ordered
	positional forward - no ``parent=`` keyword workaround needed anymore."""

	def test_AllLeafTypes(self) -> None:
		parent = _Element()
		builders = (
			("Subtype", lambda: Subtype("t", _subtypeSymbol("natural"), "doc", parent)),
			("EnumeratedType", lambda: EnumeratedType("t", [], "doc", parent)),
			("IntegerType", lambda: IntegerType("t", _range(), "doc", parent)),
			("RealType", lambda: RealType("t", _range(), "doc", parent)),
			("PhysicalType", lambda: PhysicalType("t", _range(), "ps", [], "doc", parent)),
			("ArrayType", lambda: ArrayType("t", [], _subtypeSymbol("natural"), "doc", parent)),
			("RecordType", lambda: RecordType("t", None, "doc", parent)),
			("ProtectedType", lambda: ProtectedType("t", None, "doc", parent)),
			("ProtectedTypeBody", lambda: ProtectedTypeBody("t", None, "doc", parent)),
			("AccessType", lambda: AccessType("t", _subtypeSymbol("natural"), "doc", parent)),
			("FileType", lambda: FileType("t", _subtypeSymbol("natural"), "doc", parent)),
		)
		for name, build in builders:
			with self.subTest(type=name):
				instance = build()

				self.assertIs(parent, instance.Parent)
				self.assertEqual("doc", instance.Documentation)

	def test_ObjectVertexRegression(self) -> None:
		"""Regression test, checked once via ``EnumeratedType`` as a representative leaf class (the
		bug was in ``BaseType.__init__`` itself, shared unchanged by every leaf type): the constructor
		previously assigned a bare local variable (``_objectVertex = None``) instead of
		``self._objectVertex = None``, so the declared slot was never actually initialized by the
		constructor - only ever set from the outside, later, by the object-graph builder in
		pyVHDLModel/__init__.py. There's no public property for it (unlike
		``Object.Obj.ObjectVertex``), so this is checked via the private attribute directly."""
		enumType = EnumeratedType("t", [])

		self.assertIsNone(enumType._objectVertex)


class Subtypes(Testcase):
	def test_Construction(self) -> None:
		symbol = _subtypeSymbol("std_logic")
		subtype = Subtype("my_std_logic", symbol)

		self.assertEqual("my_std_logic", subtype.Identifier)
		self.assertIs(symbol, subtype.Type)
		self.assertIsNone(subtype.BaseType)
		self.assertIsNone(subtype.Range)
		self.assertIsNone(subtype.ResolutionFunction)
		self.assertEqual("subtype my_std_logic is None", str(subtype))


class EnumeratedTypes(Testcase):
	def test_Construction(self) -> None:
		literal0 = CharacterEnumerationLiteral("0")
		literal1 = CharacterEnumerationLiteral("1")
		enumType = EnumeratedType("my_bit", [literal0, literal1])

		self.assertEqual(2, len(enumType.Literals))
		self.assertIs(enumType, literal0.Parent)
		self.assertIs(enumType, literal1.Parent)
		self.assertEqual("my_bit is ('0', '1')", str(enumType))

	def test_NoLiterals(self) -> None:
		"""``literals`` has no default value in the signature, but the body still guards for ``None``
		explicitly - accepted here even though nothing currently calls it that way."""
		enumType = EnumeratedType("empty", None)

		self.assertEqual(0, len(enumType.Literals))


class IntegerTypes(Testcase):
	"""Also covers ``RangedScalarType.Range`` (shared, unmodified, by ``IntegerType``/``RealType``/
	``PhysicalType``): it accepts any ``Range``, so either a ``SimpleRange`` or a ``RangeFromName`` for an
	attribute-based range like ``type t is range r'range;`` - checked once here since this behaviour
	genuinely is a single, shared implementation, unlike the constructor-forwarding concern above."""

	def test_WithLiteralRange(self) -> None:
		rng = _range(0, 15)
		integerType = IntegerType("nibble", rng)

		self.assertIs(rng, integerType.Range)
		self.assertEqual("nibble is range 0 to 15", str(integerType))

	def test_WithAttributeRange(self) -> None:
		rng = RangeFromName(RangeAttributeSymbol(AttributeName("range", SimpleName("r"))))
		integerType = IntegerType("t", rng)

		self.assertIs(rng, integerType.Range)


class RealTypes(Testcase):
	def test_Construction(self) -> None:
		rng = _range(0, 1)
		realType = RealType("fraction", rng)

		self.assertIs(rng, realType.Range)
		self.assertEqual("fraction is range 0 to 1", str(realType))


class PhysicalTypes(Testcase):
	def test_Construction(self) -> None:
		rng = _range(0, 1000)
		femtoSeconds = PhysicalIntegerLiteral(1000, "fs")
		physicalType = PhysicalType("my_time", rng, "ps", [("fs", femtoSeconds)])

		self.assertIs(rng, physicalType.Range)
		self.assertEqual("ps", physicalType.PrimaryUnit)
		self.assertEqual(1, len(physicalType.SecondaryUnits))
		self.assertEqual("fs", physicalType.SecondaryUnits[0][0])
		self.assertIs(femtoSeconds, physicalType.SecondaryUnits[0][1])
		self.assertIs(physicalType, femtoSeconds.Parent)
		self.assertEqual("my_time is range 0 to 1000 units ps; fs = 1000 fs;", str(physicalType))

	def test_NoSecondaryUnits(self) -> None:
		physicalType = PhysicalType("my_time", _range(0, 1000), "ps", [])

		self.assertEqual(0, len(physicalType.SecondaryUnits))


class ArrayTypes(Testcase):
	"""Regression-tracking test, not a regression fix: still-open gap, already confirmed and
	documented in the gap analysis - ``ArrayType.__init__`` deliberately (if unfortunately) never
	wires up ``Parent`` for its indices or element subtype (both ``.Parent = self`` lines are
	commented out with a FIXME). This locks in the *current* behaviour so a future fix shows up as an
	intentional test change, not a silent regression."""

	def test_Construction(self) -> None:
		index = _range(0, 7)
		elementSubtype = _subtypeSymbol("std_logic")
		arrayType = ArrayType("my_vector", [index], elementSubtype)

		self.assertEqual(1, len(arrayType.Dimensions))
		self.assertIs(index, arrayType.Dimensions[0])
		self.assertIs(elementSubtype, arrayType.ElementType)
		self.assertEqual("my_vector is array(0 to 7) of std_logic?", str(arrayType))

	def test_ParentIsNotWiredYet(self) -> None:
		"""``index.Parent`` is genuinely ``None`` (``Range`` is a ``ModelEntity`` with a declared
		``Parent`` property), but ``elementSubtype.Parent`` doesn't even exist as an attribute -
		``Symbol`` isn't a ``ModelEntity`` (see the design note in tests/unit/Symbol.py) and nothing
		ever assigns it here, so there's no ad-hoc attribute to find either."""
		index = _range(0, 7)
		elementSubtype = _subtypeSymbol("std_logic")
		arrayType = ArrayType("my_vector", [index], elementSubtype)

		self.assertIsNone(index.Parent)
		self.assertFalse(hasattr(elementSubtype, "Parent"))


class RecordTypeElements(Testcase):
	def test_Construction(self) -> None:
		subtype = _subtypeSymbol("natural")
		element = RecordTypeElement(["a", "b"], subtype)

		self.assertEqual(("a", "b"), element.Identifiers)
		self.assertIs(subtype, element.Subtype)
		self.assertIs(element, subtype.Parent)
		self.assertEqual("a, b : natural?", str(element))
		self.assertIsNone(element.Documentation)

	def test_WithDocumentation(self) -> None:
		"""A record element may carry a doc comment, like every other declaration."""
		element = RecordTypeElement(["a"], _subtypeSymbol("natural"), "--! The first field.")

		self.assertEqual("--! The first field.", element.Documentation)


class RecordTypes(Testcase):
	def test_WithElements(self) -> None:
		element = RecordTypeElement(["a"], _subtypeSymbol("natural"))
		recordType = RecordType("my_record", [element])

		self.assertEqual(1, len(recordType.Elements))
		self.assertIs(element, recordType.Elements[0])
		self.assertIs(recordType, element.Parent)
		self.assertEqual("my_record is record a : natural?;", str(recordType))

	def test_NoElements(self) -> None:
		recordType = RecordType("my_record")

		self.assertEqual(0, len(recordType.Elements))


class ProtectedTypes(Testcase):
	"""A protected type declaration admits subprogram declarations only, so ``DeclaredItems`` and
	``Methods`` hold the same items. Real ``Procedure`` instances are needed because ``Methods`` is
	defined by type, not by position."""

	def test_WithMethods(self) -> None:
		method = Procedure("increment")
		protectedType = ProtectedType("my_protected", [method])

		self.assertEqual(1, len(protectedType.DeclaredItems))
		self.assertEqual(1, len(protectedType.Methods))
		self.assertIs(method, protectedType.Methods[0])
		self.assertIs(protectedType, method.Parent)

	def test_NoMethods(self) -> None:
		protectedType = ProtectedType("my_protected")

		self.assertEqual(0, len(protectedType.DeclaredItems))
		self.assertEqual(0, len(protectedType.Methods))

	def test_IndexDeclaredItems(self) -> None:
		method = Procedure("increment")
		protectedType = ProtectedType("my_protected", [method])
		protectedType.IndexDeclaredItems()

		self.assertIn("increment", protectedType.Procedures)
		self.assertIn("increment", protectedType._namespace._elements)


class ProtectedTypeBodies(Testcase):
	"""A protected type body's declarative part matches a subprogram's, so it may declare more than
	methods. ``Methods`` is the subprogram subset of ``DeclaredItems``, not all of them."""

	def test_WithDeclaredItems(self) -> None:
		variable = Variable(["count"], _subtypeSymbol("natural"))
		method = Procedure("increment")
		body = ProtectedTypeBody("my_protected", [variable, method])

		self.assertEqual(2, len(body.DeclaredItems))
		self.assertEqual(1, len(body.Methods))
		self.assertIs(method, body.Methods[0])
		self.assertIs(body, variable.Parent)
		self.assertIs(body, method.Parent)

	def test_NoDeclaredItems(self) -> None:
		body = ProtectedTypeBody("my_protected")

		self.assertEqual(0, len(body.DeclaredItems))
		self.assertEqual(0, len(body.Methods))

	def test_IndexDeclaredItems(self) -> None:
		variable = Variable(["count"], _subtypeSymbol("natural"))
		method = Procedure("increment")
		body = ProtectedTypeBody("my_protected", [variable, method])
		body.IndexDeclaredItems()

		self.assertIn("count", body.Variables)
		self.assertIn("increment", body.Procedures)
		self.assertIn("count", body._namespace._elements)
		self.assertIn("increment", body._namespace._elements)


class AccessTypes(Testcase):
	def test_Construction(self) -> None:
		designated = _subtypeSymbol("natural")
		accessType = AccessType("my_pointer", designated)

		self.assertIs(designated, accessType.DesignatedSubtype)
		self.assertIs(accessType, designated.Parent)
		self.assertEqual("my_pointer is access natural?", str(accessType))


class FileTypes(Testcase):
	"""Regression test: ``__str__`` previously read ``"...is access ..."`` - copy-pasted from
	``AccessType`` - instead of the correct ``"...is file of ..."``."""

	def test_Construction(self) -> None:
		designated = _subtypeSymbol("character")
		fileType = FileType("text", designated)

		self.assertIs(designated, fileType.DesignatedSubtype)
		self.assertIs(fileType, designated.Parent)
		self.assertEqual("text is file of character?", str(fileType))
