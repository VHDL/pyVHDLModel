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
Visibility rules (IEEE Std 1076-2008, 12.3 and 12.4): hiding, conflicting imports and declaration order.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Concurrent import ProcessStatement
from pyVHDLModel.DesignUnit import Architecture, Entity, Package
from pyVHDLModel.Interface  import PortSimpleSignalInterfaceItem
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Namespace  import Namespace
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Type       import AccessType, AnonymousType, RecordType, RecordTypeElement

from tests.unit             import _entitySymbol, _signal, _subtypeSymbol, _variable
from tests.unit.Visibility  import _constant, _design, _enumeration, _function, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Hiding(Testcase):
	"""A declaration hides imported homographs and homographs of enclosing regions (A042-A045, A058, A068, A082)."""

	def setUp(self) -> None:
		self._imported = _constant("K", "integer")
		self._f =        _function("f", "integer")
		self._package =  Package("p", declaredItems=[self._imported, self._f])

	def test_LocalDeclaration(self) -> None:
		"""``use work.p.all; signal K : bit;``: ``K`` is the signal (A042)."""
		signal = _signal("K", "bit")
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p.all")], declaredItems=[signal])
		_design(self._package, Entity("e"), architecture)

		result = architecture._namespace.Lookup("k")

		self.assertTupleEqual((signal, ), result.Declarations)
		self.assertTupleEqual((), result.Imports)

	def test_EnclosingDeclaration_HidesInnerUseClause(self) -> None:
		"""A process' ``use work.p.all;`` doesn't make ``K`` visible over the architecture's signal ``K`` (A043)."""
		signal = _signal("K", "bit")
		process = ProcessStatement("proc", declaredItems=[_use("work.p.all")])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[signal], statements=[process])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((signal, ), process._namespace.Lookup("k").Declarations)

	def test_LocalAndImportedOverloads(self) -> None:
		"""Overloaded subprograms of the region and of a use clause coexist (A058)."""
		local = _function("f", "bit")
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p.all")], declaredItems=[local])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((local, self._f), architecture._namespace.Lookup("f").Declarations)

	def test_EnclosingOverloads(self) -> None:
		"""Overloaded subprograms of nested regions coexist."""
		outer = _function("f", "bit")
		inner = _function("f", "integer")
		process = ProcessStatement("proc", declaredItems=[inner])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[outer], statements=[process])
		_design(Entity("e"), architecture)
		process.IndexDeclaredItems()

		self.assertTupleEqual((inner, outer), process._namespace.Lookup("f").Declarations)

	def test_InnerObject_HidesOuterOverloads(self) -> None:
		"""A declaration, which isn't overloadable, hides all overloads further out."""
		outer = _function("f", "bit")
		variable = _variable("f", "integer")
		process = ProcessStatement("proc", declaredItems=[variable])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[outer], statements=[process])
		_design(Entity("e"), architecture)
		process.IndexDeclaredItems()

		self.assertTupleEqual((variable, ), process._namespace.Lookup("f").Declarations)

	def test_LocalType_HidesStdStandard(self) -> None:
		"""A local type ``natural`` hides ``std.standard.natural``, its literals are visible (A068)."""
		natural = _enumeration("natural", "one", "two")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[natural])
		_design(Entity("e"), architecture)

		self.assertTupleEqual((natural, ), architecture._namespace.Lookup("natural").Declarations)
		self.assertTupleEqual((natural.Literals[0], ), architecture._namespace.Lookup("one").Declarations)

	def test_LocalObject_HidesEnumerationLiteral(self) -> None:
		"""``constant red`` in the architecture hides the imported literal ``red`` (A056)."""
		package = Package("q", declaredItems=[_enumeration("T", "red", "green")])
		constant = _constant("red", "integer")
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.q.all")], declaredItems=[constant])
		_design(package, Entity("e"), architecture)

		self.assertTupleEqual((constant, ), architecture._namespace.Lookup("red").Declarations)


class Conflicts(Testcase):
	"""Potentially visible declarations of two use clauses (A046-A055, A069)."""

	def setUp(self) -> None:
		self._k1 = _constant("K", "integer")
		self._k2 = _constant("K", "integer")
		self._p1 = Package("p1", declaredItems=[self._k1, _function("f", "integer"), _enumeration("T1", "a", "b")])
		self._p2 = Package("p2", declaredItems=[self._k2, _function("f", "bit"), _enumeration("T2", "b", "c")])

	def test_Constants(self) -> None:
		"""``K`` of ``p1`` and of ``p2``: neither is directly visible (A047)."""
		useClause = _use("work.p1.all", "work.p2.all")
		entity = Entity("e", [useClause])
		_design(self._p1, self._p2, entity)

		result = entity._namespace.Lookup("k")

		self.assertFalse(result.IsVisible)
		self.assertTrue(result.HasConflicts)
		self.assertTupleEqual((self._k1, self._k2), tuple(imported.Element for imported in result.Conflicts))
		self.assertIs(useClause, result.Conflicts[0].UseClause)
		self.assertEqual("LookupResult: 'k' -> 0 declaration(s), 2 conflict(s)", repr(result))

	def test_InnerAndOuterUseClauses(self) -> None:
		"""A use clause of the process and one of the architecture conflict (GHDL: "due to conflicts")."""
		process = ProcessStatement("proc", declaredItems=[_use("work.p2.all")])
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p1.all")], statements=[process])
		_design(self._p1, self._p2, Entity("e"), architecture)

		result = process._namespace.Lookup("k")

		self.assertFalse(result.IsVisible)
		self.assertTupleEqual((self._k2, self._k1), tuple(imported.Element for imported in result.Conflicts))

	def test_SameDeclarationTwice(self) -> None:
		"""The same declaration imported by two use clauses is no conflict (A050, A092)."""
		entity = Entity("e", [_use("work.p1.all"), _use("work.p1.k")])
		_design(self._p1, entity)

		self.assertTupleEqual((self._k1, ), entity._namespace.Lookup("k").Declarations)

	def test_Overloadables(self) -> None:
		"""Subprograms and enumeration literals of two packages coexist (A051, A053)."""
		entity = Entity("e", [_use("work.p1.all", "work.p2.all")])
		_design(self._p1, self._p2, entity)

		self.assertEqual(2, len(entity._namespace.Lookup("f").Declarations))
		self.assertEqual(2, len(entity._namespace.Lookup("b").Declarations))

	def test_LiteralAndObject(self) -> None:
		"""An imported literal ``red`` and an imported constant ``red`` conflict (A055)."""
		literals = Package("p3", declaredItems=[_enumeration("T", "red", "green")])
		objects = Package("p4", declaredItems=[_constant("red", "integer")])
		entity = Entity("e", [_use("work.p3.all", "work.p4.all")])
		_design(literals, objects, entity)

		result = entity._namespace.Lookup("red")

		self.assertFalse(result.IsVisible)
		self.assertEqual(2, len(result.Conflicts))

	def test_StdStandard(self) -> None:
		"""A package's type ``bit`` conflicts with ``std.standard.bit`` (A069)."""
		bit = _enumeration("bit", "lo", "hi")
		entity = Entity("e", [_use("work.p3.all")])
		_design(Package("p3", declaredItems=[bit]), entity)

		result = entity._namespace.Lookup("bit")

		self.assertFalse(result.IsVisible)
		self.assertIsNone(result.Conflicts[0].UseClause)
		self.assertIs(bit, result.Conflicts[1].Element)


class DeclarationOrder(Testcase):
	"""A declaration and a use clause are visible after their place in the region (A026, A040, A071-A073)."""

	def setUp(self) -> None:
		self._imported = _constant("K", "integer")
		self._package =  Package("p", declaredItems=[self._imported])

	def test_UseClauseAfterDeclaration(self) -> None:
		"""``constant c1 : integer := K; use work.p.all; constant c2 : integer := K;`` (A026)."""
		c1 = _constant("c1", "integer")
		c2 = _constant("c2", "integer")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[c1, _use("work.p.all"), c2])
		_design(self._package, Entity("e"), architecture)

		self.assertFalse(architecture._namespace.Lookup("k", c1).IsVisible)
		self.assertTupleEqual((self._imported, ), architecture._namespace.Lookup("k", c2).Declarations)
		self.assertTupleEqual((self._imported, ), architecture._namespace.Lookup("k").Declarations)

	def test_PortBeforeUseClause(self) -> None:
		"""A use clause in the entity's declarative part isn't seen by the ports (A040)."""
		port = PortSimpleSignalInterfaceItem(("x", ), Mode.In, _subtypeSymbol("K"))
		entity = Entity("e", portItems=[port], declaredItems=[_use("work.p.all")])
		_design(self._package, entity)

		self.assertFalse(entity._namespace.Lookup("k", port).IsVisible)

	def test_Object(self) -> None:
		"""``constant c1 : integer := c2; constant c2 ...``: ``c2`` isn't visible in ``c1`` (A071)."""
		c1 = _constant("c1", "integer")
		c2 = _constant("c2", "integer")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[c1, c2])
		_design(Entity("e"), architecture)

		self.assertFalse(architecture._namespace.Lookup("c2", c1).IsVisible)
		self.assertFalse(architecture._namespace.Lookup("c1", c1).IsVisible)
		self.assertTupleEqual((c1, ), architecture._namespace.Lookup("c1", c2).Declarations)

	def test_UseClauseBeforeLocalHomograph(self) -> None:
		"""``use work.p.all; constant k1 := K; signal K : bit; constant k2 := K;`` (A072)."""
		k1 = _constant("k1", "integer")
		signal = _signal("K", "bit")
		k2 = _constant("k2", "integer")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[_use("work.p.all"), k1, signal, k2])
		_design(self._package, Entity("e"), architecture)

		self.assertTupleEqual((self._imported, ), architecture._namespace.Lookup("k", k1).Declarations)
		self.assertTupleEqual((signal, ), architecture._namespace.Lookup("k", k2).Declarations)

	def test_SubprogramVisibleInItself(self) -> None:
		"""A subprogram is visible in its own body (recursion), an outer declaration after it isn't."""
		function = _function("f", "integer")
		later = _constant("later", "integer")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[function, later])
		_design(Entity("e"), architecture)
		function.IndexDeclaredItems()

		self.assertTupleEqual((function, ), function._namespace.Lookup("f", function.ParameterItems[0]).Declarations)
		self.assertFalse(function._namespace.Lookup("later", function.ParameterItems[0]).IsVisible)

	def test_IncompleteType(self) -> None:
		"""``type node; type ptr is access node; type node is record ... end record;``: ``node`` in ``ptr``."""
		incomplete = AnonymousType("node")
		pointer = AccessType("ptr", SimpleSubtypeSymbol(SimpleName("node")))
		node = RecordType("node", [RecordTypeElement(("next", ), SimpleSubtypeSymbol(SimpleName("ptr")))])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[incomplete, pointer, node])
		_design(Entity("e"), architecture)

		self.assertTupleEqual((node, ), architecture._namespace.Lookup("node", pointer).Declarations)

	def test_IncompleteType_After(self) -> None:
		"""Without an incomplete type declaration, a full type isn't visible before its declaration."""
		pointer = AccessType("ptr", SimpleSubtypeSymbol(SimpleName("node")))
		node = RecordType("node", [RecordTypeElement(("next", ), SimpleSubtypeSymbol(SimpleName("ptr")))])
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[pointer, node])
		_design(Entity("e"), architecture)

		self.assertFalse(architecture._namespace.Lookup("node", pointer).IsVisible)


class Designators(Testcase):
	"""Keys of enumeration literals and units in a namespace (:meth:`~pyVHDLModel.Namespace.Namespace.Lookup`)."""

	def test_CharacterLiteral(self) -> None:
		literal = _enumeration("T", "'a'").Literals[0]

		self.assertEqual("'a'", Namespace.NormalizedDesignatorOf(literal))

	def test_EnumerationLiteral(self) -> None:
		literal = _enumeration("T", "Idle").Literals[0]

		self.assertEqual("idle", Namespace.NormalizedDesignatorOf(literal))

	def test_ImplicitDeclarations(self) -> None:
		"""An enumerated type in a region declares its literals; removing the type removes them."""
		enumeration = _enumeration("T", "Idle", "'a'")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[enumeration])
		architecture.IndexDeclaredItems()

		self.assertDictEqual(
			{"idle": [enumeration.Literals[0]], "'a'": [enumeration.Literals[1]]},
			architecture._namespace.ImplicitDeclarations()
		)

		architecture.RemoveDeclaredItem(enumeration)

		self.assertDictEqual({}, architecture._namespace.ImplicitDeclarations())
