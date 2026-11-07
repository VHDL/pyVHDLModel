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
Type attributes (IEEE Std 1076-2008, 16.2): ``x'subtype``, ``A'element`` and ``T'base`` as type marks.
"""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import Mode
from pyVHDLModel.Concurrent  import ProcessStatement
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.DesignUnit  import Architecture, Entity, Package
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Interface   import GenericConstantInterfaceItem, PortSimpleSignalInterfaceItem
from pyVHDLModel.Name        import AttributeName, ParenthesisName, SelectedName, SimpleName, AllName, IndexedName
from pyVHDLModel.Object      import File, SharedVariable, Signal, Variable
from pyVHDLModel.Symbol      import PossibleReference, SimpleObjectOrFunctionCallSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Type        import AccessType, ArrayType, RecordType, RecordTypeElement, Subtype

from tests.unit              import _entitySymbol, _signal, _subtypeSymbol
from tests.unit.Resolution   import _resolve
from tests.unit.Visibility   import _constant, _design, _enumeration, _function, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _attribute(prefix: str, *attributes: str) -> SimpleSubtypeSymbol:
	"""A type mark by an attribute name, e.g. ``s'subtype'element``."""
	name = SimpleName(prefix)
	for attribute in attributes:
		name = AttributeName(attribute, name)

	return SimpleSubtypeSymbol(name)


class TypeAttributes(Testcase):
	"""Attribute names denoting a type."""

	def setUp(self) -> None:
		self._type =  _enumeration("T", "a", "b")
		self._array = ArrayType("AT", [_subtypeSymbol("natural")], _subtypeSymbol("T"))

	def _resolve(self, *declaredItems) -> tuple[Architecture, list]:
		"""An architecture with ``T``, ``AT`` and the declared items; the design is analyzed and resolved."""
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[self._type, self._array, *declaredItems])
		return architecture, _resolve(_design(Entity("e"), architecture, analyze=False))

	def test_Subtype_Object(self) -> None:
		"""``signal s2 : s'subtype;``."""
		signal = _signal("s", "AT")
		other =  Signal(("s2", ), _attribute("s", "subtype"))
		_, warnings = self._resolve(signal, other)

		self.assertListEqual([], warnings)
		self.assertIs(self._array, other.Subtype.Reference)

	def test_Subtype_Type(self) -> None:
		"""``T'subtype`` is illegal: the prefix is a type."""
		other = Signal(("s2", ), _attribute("T", "subtype"))
		_, warnings = self._resolve(other)

		self.assertEqual(1, len(warnings))
		self.assertEqual("Prefix 'T' of type mark 'T'subtype' isn't an object.", str(warnings[0]))
		self.assertIsNone(other.Subtype.Reference)

	def test_Subtype_NotFound(self) -> None:
		"""``x'subtype`` with an unknown ``x``."""
		other = Signal(("s2", ), _attribute("x", "subtype"))
		_, warnings = self._resolve(other)

		self.assertEqual(1, len(warnings))
		self.assertEqual("Prefix 'x' of type mark 'x'subtype' not found in: rtl, e.", str(warnings[0]))

	def test_Element_Type(self) -> None:
		"""``subtype ET is AT'element;``."""
		subtype = Subtype("ET", _attribute("AT", "element"))
		_, warnings = self._resolve(subtype)

		self.assertListEqual([], warnings)
		self.assertIs(self._type, subtype.Type.Reference)
		self.assertIs(self._type, subtype.BaseType)

	def test_Element_Object(self) -> None:
		"""``signal e : s'element;``."""
		signal =  _signal("s", "AT")
		element = Signal(("e", ), _attribute("s", "element"))
		_, warnings = self._resolve(signal, element)

		self.assertListEqual([], warnings)
		self.assertIs(self._type, element.Subtype.Reference)

	def test_Element_OfSubtype(self) -> None:
		"""``v'subtype'element``."""
		signal =  _signal("s", "AT")
		element = Signal(("e", ), _attribute("s", "subtype", "element"))
		_, warnings = self._resolve(signal, element)

		self.assertListEqual([], warnings)
		self.assertIs(self._type, element.Subtype.Reference)

	def test_Element_NotAnArray(self) -> None:
		"""``i'element`` of an integer or a record."""
		integer =      _signal("i", "integer")
		record =       RecordType("R", [RecordTypeElement(("x", ), _subtypeSymbol("bit"))])
		recordSignal = _signal("rv", "R")
		first =        Signal(("e1", ), _attribute("i", "element"))
		second =       Signal(("e2", ), _attribute("rv", "element"))
		_, warnings = self._resolve(integer, record, recordSignal, first, second)

		self.assertEqual(2, len(warnings))
		self.assertEqual("Prefix 'i' of type mark 'i'element' isn't an array.", str(warnings[0]))
		self.assertEqual("Prefix 'rv' of type mark 'rv'element' isn't an array.", str(warnings[1]))

	def test_Base_AsTypeMark(self) -> None:
		"""``signal v : ST'base;`` is illegal."""
		subtype = Subtype("ST", _subtypeSymbol("integer"))
		signal =  Signal(("v", ), _attribute("ST", "base"))
		_, warnings = self._resolve(subtype, signal)

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Attribute name 'ST'base' isn't allowed as type mark: 'base is only a prefix of an attribute.",
			str(warnings[0])
		)

	def test_Base_AsPrefix(self) -> None:
		"""``subtype S is AT'base'element;``: ``'base`` as the prefix of another attribute."""
		subtype = Subtype("ST", _subtypeSymbol("AT"))
		element = Subtype("S", _attribute("ST", "base", "element"))
		_, warnings = self._resolve(subtype, element)

		self.assertListEqual([], warnings)
		self.assertIs(self._type, element.Type.Reference)

	def test_OtherAttribute(self) -> None:
		"""``s'range`` doesn't denote a type."""
		signal = _signal("s", "AT")
		other =  Signal(("s2", ), _attribute("s", "range"))
		_, warnings = self._resolve(signal, other)

		self.assertEqual(1, len(warnings))
		self.assertEqual("Attribute name 's'range' doesn't denote a type.", str(warnings[0]))


class InterfaceLists(Testcase):
	"""A port can't be used in its own interface list, a generic can."""

	def test_Port(self) -> None:
		first =    PortSimpleSignalInterfaceItem(("i", ), Mode.In, _subtypeSymbol("bit"))
		second =   PortSimpleSignalInterfaceItem(("o", ), Mode.Out, _attribute("i", "subtype"))
		warnings = _resolve(_design(Entity("e", portItems=[first, second]), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Prefix 'i' of type mark 'i'subtype' isn't usable in its own interface list.",
			str(warnings[0])
		)

	def test_Generic(self) -> None:
		first =  GenericConstantInterfaceItem(("G", ), Mode.Default, _subtypeSymbol("natural"))
		second = GenericConstantInterfaceItem(("H", ), Mode.Default, _attribute("G", "subtype"))
		design = _design(Entity("e", genericItems=[first, second]), analyze=False)

		self.assertListEqual([], _resolve(design))
		self.assertIs(design.GetPackage("std", "standard").Subtypes["natural"], second.Subtype.Reference)


class Prefixes(Testcase):
	"""Object aliases and record elements as prefixes (GHDL accepts)."""

	def setUp(self) -> None:
		self._type =  _enumeration("T", "a", "b")
		self._array = ArrayType("AT", [_subtypeSymbol("natural")], _subtypeSymbol("T"))

	def _resolve(self, *declaredItems) -> list:
		"""Resolve an architecture with ``T``, ``AT`` and the declared items."""
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[self._type, self._array, *declaredItems])
		return _resolve(_design(Entity("e"), architecture, analyze=False))

	def test_ObjectAlias(self) -> None:
		"""``alias al : AT is s; signal sig1 : al'subtype; signal sig2 : al'element;``."""
		signal = _signal("s", "AT")
		alias =  Alias("al", SimpleObjectOrFunctionCallSymbol(SimpleName("s")), _subtypeSymbol("AT"))
		first =  Signal(("sig1", ), _attribute("al", "subtype"))
		second = Signal(("sig2", ), _attribute("al", "element"))

		self.assertListEqual([], self._resolve(signal, alias, first, second))
		self.assertIs(self._array, first.Subtype.Reference)
		self.assertIs(self._type, second.Subtype.Reference)

	def test_RecordElement(self) -> None:
		"""``signal sig1 : rec.f'subtype;``."""
		record = RecordType("R", [RecordTypeElement(("f", ), _subtypeSymbol("AT"))])
		signal = _signal("rec", "R")
		other =  Signal(("sig1", ), SimpleSubtypeSymbol(AttributeName("subtype", SelectedName("f", SimpleName("rec")))))

		self.assertListEqual([], self._resolve(record, signal, other))
		self.assertIs(self._array, other.Subtype.Reference)



class LibrariesAndPackages(Testcase):
	"""Prefixes naming a library, a package and its declarations."""

	def setUp(self) -> None:
		self._type =     _enumeration("T", "a", "b")
		self._array =    ArrayType("AT", [_subtypeSymbol("natural")], _subtypeSymbol("T"))
		self._constant = _constant("c", "AT")
		self._package =  Package("p", declaredItems=[self._type, self._array, self._constant])

	def _resolve(self, *declaredItems, contextItems=()) -> list:
		"""Resolve the package ``p`` and an architecture with the declared items."""
		architecture = Architecture("rtl", _entitySymbol("e"), contextItems, declaredItems)
		return _resolve(_design(self._package, Entity("e"), architecture, analyze=False))

	def test_Library(self) -> None:
		"""``signal s : work.p.c'subtype;``."""
		name =   AttributeName("subtype", SelectedName("c", SelectedName("p", SimpleName("work"))))
		signal = Signal(("s", ), SimpleSubtypeSymbol(name))

		self.assertListEqual([], self._resolve(signal))
		self.assertIs(self._array, signal.Subtype.Reference)

	def test_Library_NoPackage(self) -> None:
		"""``work.q.c'subtype``: the library has no package ``q``."""
		name =     AttributeName("subtype", SelectedName("c", SelectedName("q", SimpleName("work"))))
		signal =   Signal(("s", ), SimpleSubtypeSymbol(name))
		warnings = self._resolve(signal)

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Prefix 'work.q' of type mark 'work.q.c'subtype' isn't a package of library 'lib'.",
			str(warnings[0])
		)

	def test_Package(self) -> None:
		"""``use work.p; signal s : p.c'subtype; signal e : p.AT'element;``."""
		first =  Signal(("s", ), SimpleSubtypeSymbol(AttributeName("subtype", SelectedName("c", SimpleName("p")))))
		second = Signal(("e", ), SimpleSubtypeSymbol(AttributeName("element", SelectedName("AT", SimpleName("p")))))

		self.assertListEqual([], self._resolve(first, second, contextItems=[_use("work.p")]))
		self.assertIs(self._array, first.Subtype.Reference)
		self.assertIs(self._type, second.Subtype.Reference)

	def test_Package_NotFound(self) -> None:
		"""``p.x'subtype``: ``p`` declares no ``x``."""
		signal =   Signal(("s", ), SimpleSubtypeSymbol(AttributeName("subtype", SelectedName("x", SimpleName("p")))))
		warnings = self._resolve(signal, contextItems=[_use("work.p")])

		self.assertEqual(1, len(warnings))
		self.assertEqual("Prefix 'p.x' of type mark 'p.x'subtype' not found in: p.", str(warnings[0]))


class OtherPrefixes(Testcase):
	"""Subprograms, unresolved aliases and names without a declaration (unsupported) as prefixes."""

	def setUp(self) -> None:
		self._type =  _enumeration("T", "a", "b")
		self._array = ArrayType("AT", [_subtypeSymbol("natural")], _subtypeSymbol("T"))

	def _resolve(self, *declaredItems, statements=()) -> list:
		"""Resolve an architecture with ``T``, ``AT``, the declared items and the statements."""
		architecture = Architecture(
			"rtl", _entitySymbol("e"), declaredItems=[self._type, self._array, *declaredItems], statements=statements
		)
		return _resolve(_design(Entity("e"), architecture, analyze=False))

	def test_AllName(self) -> None:
		"""``ptr.all'subtype`` isn't supported: ``ptr.all`` denotes an object without a declaration."""
		access =   AccessType("A", _subtypeSymbol("AT"))
		pointer =  Variable(("ptr", ), _subtypeSymbol("A"))
		variable = Variable(("v", ), SimpleSubtypeSymbol(AttributeName("subtype", AllName(SimpleName("ptr")))))
		process =  ProcessStatement("proc", declaredItems=[pointer, variable])
		warnings = self._resolve(access, statements=[process])

		self.assertEqual(1, len(warnings))
		self.assertEqual("Prefix 'ptr.all' of type mark 'ptr.all'subtype' isn't supported: AllName.", str(warnings[0]))

	def test_ParenthesisName(self) -> None:
		"""``m(0)'subtype`` isn't supported: ``m(0)`` denotes an object without a declaration."""
		signal =   _signal("m", "AT")
		indexed =  ParenthesisName(SimpleName("m"), [IntegerLiteral(0)])
		other =    Signal(("s2", ), SimpleSubtypeSymbol(AttributeName("subtype", indexed)))
		warnings = self._resolve(signal, other)

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Prefix 'm(0)' of type mark 'm(0)'subtype' isn't supported: ParenthesisName.",
			str(warnings[0])
		)

	def test_Function(self) -> None:
		"""``f'subtype`` with a function ``f``."""
		function = _function("f", "integer")
		other =    Signal(("s2", ), _attribute("f", "subtype"))
		warnings = self._resolve(function, other)

		self.assertEqual(1, len(warnings))
		self.assertEqual(
			"Prefix 'f' of type mark 'f'subtype' is neither an object, a type nor a package: Function.",
			str(warnings[0])
		)

	def test_IndexedName(self) -> None:
		"""``m(0)'subtype`` with an indexed name isn't supported."""
		signal =   _signal("m", "AT")
		indexed =  IndexedName(SimpleName("m"), [IntegerLiteral(0)])
		other =    Signal(("s2", ), SimpleSubtypeSymbol(AttributeName("subtype", indexed)))
		warnings = self._resolve(signal, other)

		self.assertEqual(1, len(warnings))
		self.assertEqual("Prefix 'm(0)' of type mark 'm(0)'subtype' isn't supported: IndexedName.", str(warnings[0]))

	def test_Alias_Unresolved(self) -> None:
		"""``alias al is x; signal s2 : al'subtype;``: the alias' name isn't resolved."""
		alias =    Alias("al", SimpleObjectOrFunctionCallSymbol(SimpleName("x")))
		other =    Signal(("s2", ), _attribute("al", "subtype"))
		warnings = self._resolve(alias, other)

		self.assertEqual(2, len(warnings))
		self.assertEqual("Name of prefix 'al' of type mark 'al'subtype' isn't resolved.", str(warnings[1]))


class ReferenceKinds(Testcase):
	"""The kind of reference to a declaration, as a symbol's possible references name it."""

	def test_Objects(self) -> None:
		self.assertIs(PossibleReference.Constant, _constant("c", "bit").ReferenceKind)
		self.assertIs(PossibleReference.Variable, Variable(("v", ), _subtypeSymbol("bit")).ReferenceKind)
		self.assertIs(PossibleReference.Variable, SharedVariable(("v", ), _subtypeSymbol("P")).ReferenceKind)
		self.assertIs(PossibleReference.Signal, _signal("s", "bit").ReferenceKind)
		self.assertIs(PossibleReference.File, File(("f", ), _subtypeSymbol("text")).ReferenceKind)

	def test_RecordElement(self) -> None:
		self.assertIs(PossibleReference.RecordElement, RecordTypeElement(("f", ), _subtypeSymbol("bit")).ReferenceKind)

	def test_Types(self) -> None:
		self.assertIs(PossibleReference.Type, _enumeration("T", "a").ReferenceKind)
		self.assertIs(PossibleReference.Subtype, Subtype("ST", _subtypeSymbol("T")).ReferenceKind)

	def test_Package(self) -> None:
		self.assertIs(PossibleReference.Package, Package("p").ReferenceKind)

	def test_Library(self) -> None:
		design = _design(analyze=False)

		self.assertIs(PossibleReference.Library, design.GetLibrary("lib").ReferenceKind)

	def test_Alias(self) -> None:
		"""An alias with a subtype indication is an object alias; without one, its kind is unknown."""
		objectAlias = Alias("al", SimpleObjectOrFunctionCallSymbol(SimpleName("s")), _subtypeSymbol("bit"))
		otherAlias =  Alias("al", SimpleObjectOrFunctionCallSymbol(SimpleName("s")))

		self.assertIs(PossibleReference.Object, objectAlias.ReferenceKind)
		self.assertIs(PossibleReference.Unknown, otherAlias.ReferenceKind)

	def test_Other(self) -> None:
		self.assertIs(PossibleReference.Unknown, _function("f", "integer").ReferenceKind)

