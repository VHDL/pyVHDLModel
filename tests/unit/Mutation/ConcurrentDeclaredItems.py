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
"""
Mutation tests for the declared items of concurrent declaration regions
(:class:`~pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin`).

The mutators are tested on an architecture and a package (deferred constants).
"""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel.Declaration import Alias
from pyVHDLModel.DesignUnit  import Architecture, Component, Package, UseClause
from pyVHDLModel.Exception   import AlreadyInDesignError, NotAChildError, DuplicateDeclarationError, \
                                    DuplicateTypeError, DuplicateSubtypeError, DuplicateConstantError, \
                                    DuplicateSignalError, DuplicateVariableError, DuplicateFileError, \
                                    DuplicateComponentError, DuplicateSubprogramError
from pyVHDLModel.Object      import DeferredConstant, File, SharedVariable
from pyVHDLModel.Type        import AnonymousType, FullType, ProtectedType, ProtectedTypeBody, Subtype

from tests.unit              import _entitySymbol, _signalSymbol, _subtypeSymbol
from tests.unit.Mutation     import _constant, _function, _port, _procedure, _reindexed, _signal, _variable


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _architecture(*declaredItems) -> Architecture:
	return Architecture("rtl", _entitySymbol("e"), declaredItems=declaredItems)


class Add(Testcase):
	def test_Add(self) -> None:
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		signal = _signal("a", "b")
		constant = _constant("C")

		architecture.AddDeclaredItem(signal)
		architecture.AddDeclaredItem(constant)

		self.assertListEqual([signal, constant], architecture.DeclaredItems)
		self.assertIs(architecture, signal.Parent)
		self.assertIs(architecture, constant.Parent)
		self.assertDictEqual({"a": signal, "b": signal}, architecture.Signals)
		self.assertDictEqual({"c": constant}, architecture.Constants)
		self.assertDictEqual({"a": signal, "b": signal, "c": constant}, architecture._namespace._elements)

	def test_Add_Types(self) -> None:
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		fullType = FullType("T")
		subtype = Subtype("S", _subtypeSymbol("bit"))

		architecture.AddDeclaredItem(fullType)
		architecture.AddDeclaredItem(subtype)

		self.assertDictEqual({"t": fullType}, architecture.Types)
		self.assertDictEqual({"s": subtype}, architecture.Subtypes)
		self.assertDictEqual({"t": fullType, "s": subtype}, architecture._namespace._elements)

	def test_Add_Objects(self) -> None:
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		sharedVariable = SharedVariable(["sv"], _subtypeSymbol("natural"))
		file = File(["f"], _subtypeSymbol("text"))

		architecture.AddDeclaredItem(sharedVariable)
		architecture.AddDeclaredItem(file)

		self.assertDictEqual({"sv": sharedVariable}, architecture.SharedVariables)
		self.assertDictEqual({"f": file}, architecture.Files)

	def test_Add_Subprograms(self) -> None:
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		function = _function("f")
		procedure = _procedure("p")

		architecture.AddDeclaredItem(function)
		architecture.AddDeclaredItem(procedure)

		self.assertDictEqual({"f": [function]}, architecture.Functions)
		self.assertDictEqual({"p": [procedure]}, architecture.Procedures)
		self.assertIs(architecture._namespace, function._namespace.ParentNamespace)

	def test_Add_Component(self) -> None:
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		component = Component("c")

		architecture.AddDeclaredItem(component)

		self.assertDictEqual({"c": component}, architecture.Components)
		self.assertIs(component, architecture._namespace._elements["c"])

	def test_Add_NotIndexedKind(self) -> None:
		"""A declared item without a lookup table is added to the list only, as by ``IndexDeclaredItems``."""
		architecture = _architecture()
		alias = Alias("a", _signalSymbol("s"))
		useClause = UseClause([])

		architecture.AddDeclaredItem(alias)
		architecture.AddDeclaredItem(useClause)

		self.assertListEqual([alias, useClause], architecture.DeclaredItems)
		self.assertIs(architecture, useClause.Parent)
		self.assertDictEqual({}, architecture._namespace._elements)

	def test_Add_DeferredConstant(self) -> None:
		package = Package("pkg")
		package.IndexDeclaredItems()
		deferredConstant = DeferredConstant(["BITS"], _subtypeSymbol("positive"))

		package.AddDeclaredItem(deferredConstant)

		self.assertDictEqual({"bits": deferredConstant}, package.DeferredConstants)
		self.assertIs(package, deferredConstant.Parent)

	def test_Add_Overloads(self) -> None:
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		overload1 = _function("f")
		overload2 = _function("F")
		procedure = _procedure("f")

		architecture.AddDeclaredItem(overload1)
		architecture.AddDeclaredItem(overload2)
		architecture.AddDeclaredItem(procedure)

		self.assertDictEqual({"f": [overload1, overload2]}, architecture.Functions)
		self.assertDictEqual({"f": [procedure]}, architecture.Procedures)
		self.assertIs(procedure, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Add_IncompleteType(self) -> None:
		"""A full type completes an incomplete type declaration of the same identifier."""
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		incompleteType = AnonymousType("node")
		fullType = FullType("node")

		architecture.AddDeclaredItem(incompleteType)
		architecture.AddDeclaredItem(fullType)

		self.assertListEqual([incompleteType, fullType], architecture.DeclaredItems)
		self.assertDictEqual({"node": fullType}, architecture.Types)

	def test_Add_ProtectedTypeBody(self) -> None:
		"""A protected type body shares the identifier of its protected type."""
		architecture = _architecture()
		architecture.IndexDeclaredItems()
		protectedType = ProtectedType("counter")
		protectedTypeBody = ProtectedTypeBody("counter")

		architecture.AddDeclaredItem(protectedType)
		architecture.AddDeclaredItem(protectedTypeBody)

		self.assertListEqual([protectedType, protectedTypeBody], architecture.DeclaredItems)
		self.assertIs(architecture, protectedTypeBody.Parent)
		self.assertDictEqual({"counter": protectedType}, architecture.Types)
		self.assertDictEqual({"counter": protectedType}, architecture._namespace._elements)

	def test_Add_None(self) -> None:
		architecture = _architecture()

		with self.assertRaises(ValueError) as context:
			architecture.AddDeclaredItem(None)

		self.assertEqual("Parameter 'declaredItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.AddDeclaredItem(_variable("v"))

		self.assertEqual("Parameter 'declaredItem' is not a declaration allowed in Architecture.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Object.Variable'."], context.exception.__notes__)
		self.assertListEqual([], architecture.DeclaredItems)

	def test_DeclaredItemTypes(self) -> None:
		"""The accepted classes are class variables: a package accepts deferred constants, an architecture doesn't."""
		self.assertIn(DeferredConstant, Package._DECLARED_ITEM_TYPES)
		self.assertNotIn(DeferredConstant, Architecture._DECLARED_ITEM_TYPES)

	def test_Add_WrongType_DeferredConstant(self) -> None:
		"""Only a package declares deferred constants."""
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.AddDeclaredItem(DeferredConstant(["BITS"], _subtypeSymbol("positive")))

		self.assertEqual("Parameter 'declaredItem' is not a declaration allowed in Architecture.", str(context.exception))

	def test_Add_WrongType_InterfaceItem(self) -> None:
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.AddDeclaredItem(_port("Clock"))

		self.assertEqual("Parameter 'declaredItem' is not a declaration allowed in Architecture.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyVHDLModel.Interface.PortSimpleSignalInterfaceItem'."],
			context.exception.__notes__
		)

	def test_Add_AlreadyInDesign(self) -> None:
		signal = _signal("a", "b")
		other = _architecture(signal)
		architecture = _architecture()

		with self.assertRaises(AlreadyInDesignError) as context:
			architecture.AddDeclaredItem(signal)

		self.assertEqual("Signal 'a, b' already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Architecture first."], context.exception.__notes__)
		self.assertIs(signal, context.exception.Element)
		self.assertIs(other, context.exception.Parent)
		self.assertListEqual([], architecture.DeclaredItems)

	def test_Add_AlreadyInDesign_Unnamed(self) -> None:
		useClause = UseClause([])
		package = Package("pkg", declaredItems=[useClause])
		architecture = _architecture()

		with self.assertRaises(AlreadyInDesignError) as context:
			architecture.AddDeclaredItem(useClause)

		self.assertEqual("UseClause already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its Package first."], context.exception.__notes__)
		self.assertIs(useClause, context.exception.Element)
		self.assertIs(package, context.exception.Parent)

	def test_Add_Duplicate(self) -> None:
		signal = _signal("a", "b")
		architecture = _architecture(signal)
		architecture.IndexDeclaredItems()
		duplicate = _constant("C", "B")


		with self.assertRaises(DuplicateConstantError) as context:
			architecture.AddDeclaredItem(duplicate)

		self.assertEqual("Architecture already declares 'B'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Object.Signal'."],
			context.exception.__notes__
		)
		self.assertEqual("B", context.exception.Identifier)
		self.assertEqual("b", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertIs(duplicate, context.exception.Element)
		self.assertIs(signal, context.exception.Existing)
		self.assertListEqual([signal], architecture.DeclaredItems)
		self.assertDictEqual({}, architecture.Constants)
		self.assertIsNone(duplicate.Parent)

	def test_Add_Duplicate_Kinds(self) -> None:
		"""The error names the kind of the declared item to add."""
		architecture = _architecture(_signal("x"))

		with self.assertRaises(DuplicateTypeError):
			architecture.AddDeclaredItem(FullType("x"))

		with self.assertRaises(DuplicateSubtypeError):
			architecture.AddDeclaredItem(Subtype("x", _subtypeSymbol("bit")))

		with self.assertRaises(DuplicateConstantError):
			architecture.AddDeclaredItem(_constant("x"))

		with self.assertRaises(DuplicateSignalError):
			architecture.AddDeclaredItem(_signal("x"))

		with self.assertRaises(DuplicateVariableError):
			architecture.AddDeclaredItem(SharedVariable(["x"], _subtypeSymbol("natural")))

		with self.assertRaises(DuplicateFileError):
			architecture.AddDeclaredItem(File(["x"], _subtypeSymbol("text")))

		with self.assertRaises(DuplicateComponentError):
			architecture.AddDeclaredItem(Component("x"))

		with self.assertRaises(DuplicateSubprogramError):
			architecture.AddDeclaredItem(_function("x"))

		self.assertEqual(1, len(architecture.DeclaredItems))

	def test_Add_Duplicate_OtherKind(self) -> None:
		function = _function("x")
		architecture = _architecture(function)
		alias = Alias("X", _signalSymbol("s"))


		with self.assertRaises(DuplicateDeclarationError) as context:
			architecture.AddDeclaredItem(alias)

		self.assertIs(DuplicateDeclarationError, type(context.exception))
		self.assertEqual("Architecture already declares 'X'.", str(context.exception))
		self.assertListEqual(
			["Existing declaration is of type 'pyVHDLModel.Subprogram.Function'."],
			context.exception.__notes__
		)
		self.assertEqual("X", context.exception.Identifier)
		self.assertEqual("x", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertIs(alias, context.exception.Element)
		self.assertIs(function, context.exception.Existing)

	def test_Add_Duplicate_ProtectedTypeBody(self) -> None:
		architecture = _architecture(ProtectedType("counter"), ProtectedTypeBody("counter"))


		with self.assertRaises(DuplicateTypeError):
			architecture.AddDeclaredItem(ProtectedTypeBody("counter"))



class Insert(Testcase):
	def test_Insert_Start(self) -> None:
		clock = _signal("Clock")
		reset = _signal("Reset")
		architecture = _architecture(clock, reset)
		architecture.IndexDeclaredItems()
		enable = _signal("Enable")

		architecture.InsertDeclaredItem(0, enable)

		self.assertListEqual([enable, clock, reset], architecture.DeclaredItems)
		self.assertIs(architecture, enable.Parent)
		self.assertIs(enable, architecture.Signals["enable"])

	def test_Insert_Middle(self) -> None:
		clock = _signal("Clock")
		reset = _signal("Reset")
		architecture = _architecture(clock, reset)
		enable = _signal("Enable")

		architecture.InsertDeclaredItem(1, enable)

		self.assertListEqual([clock, enable, reset], architecture.DeclaredItems)

	def test_Insert_End(self) -> None:
		clock = _signal("Clock")
		architecture = _architecture(clock)
		enable = _signal("Enable")

		architecture.InsertDeclaredItem(1, enable)

		self.assertListEqual([clock, enable], architecture.DeclaredItems)

	def test_Insert_IndexNone(self) -> None:
		architecture = _architecture()

		with self.assertRaises(ValueError) as context:
			architecture.InsertDeclaredItem(None, _signal("Clock"))

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Insert_IndexWrongType(self) -> None:
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.InsertDeclaredItem("0", _signal("Clock"))

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Insert_IndexOutOfRange(self) -> None:
		architecture = _architecture(_signal("Clock"))

		with self.assertRaises(ValueError) as context:
			architecture.InsertDeclaredItem(2, _signal("Reset"))

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '2'."], context.exception.__notes__)

	def test_Insert_IndexNegative(self) -> None:
		clock = _signal("Clock")
		enable = _signal("Enable")
		architecture = _architecture(clock, enable)
		reset = _signal("Reset")

		architecture.InsertDeclaredItem(-1, reset)

		self.assertListEqual([clock, reset, enable], architecture.DeclaredItems)
		self.assertIs(architecture, reset.Parent)

	def test_Insert_IndexNegative_OutOfRange(self) -> None:
		architecture = _architecture(_signal("Clock"))
		reset = _signal("Reset")

		with self.assertRaises(ValueError) as context:
			architecture.InsertDeclaredItem(-2, reset)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertIsNone(reset.Parent)


class InsertBeforeAfter(Testcase):
	def test_InsertBefore(self) -> None:
		clock = _signal("Clock")
		reset = _signal("Reset")
		architecture = _architecture(clock, reset)
		architecture.IndexDeclaredItems()
		enable = _signal("Enable")

		architecture.InsertDeclaredItemBefore(enable, reset)

		self.assertListEqual([clock, enable, reset], architecture.DeclaredItems)
		self.assertIs(architecture, enable.Parent)
		self.assertIs(enable, architecture.Signals["enable"])

	def test_InsertBefore_First(self) -> None:
		clock = _signal("Clock")
		architecture = _architecture(clock)
		enable = _signal("Enable")

		architecture.InsertDeclaredItemBefore(enable, clock)

		self.assertListEqual([enable, clock], architecture.DeclaredItems)

	def test_InsertBefore_None(self) -> None:
		architecture = _architecture()

		with self.assertRaises(ValueError) as context:
			architecture.InsertDeclaredItemBefore(_signal("Enable"), None)

		self.assertEqual("Parameter 'before' is None.", str(context.exception))

	def test_InsertBefore_WrongType(self) -> None:
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.InsertDeclaredItemBefore(_signal("Enable"), "Clock")

		self.assertEqual("Parameter 'before' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_InsertBefore_NotAChild(self) -> None:
		clock = _signal("Clock")
		_architecture(clock)
		architecture = _architecture()

		with self.assertRaises(NotAChildError) as context:
			architecture.InsertDeclaredItemBefore(_signal("Enable"), clock)

		self.assertEqual("Signal 'Clock' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(clock, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)

	def test_InsertAfter(self) -> None:
		clock = _signal("Clock")
		reset = _signal("Reset")
		architecture = _architecture(clock, reset)
		enable = _signal("Enable")

		architecture.InsertDeclaredItemAfter(enable, clock)

		self.assertListEqual([clock, enable, reset], architecture.DeclaredItems)
		self.assertIs(architecture, enable.Parent)

	def test_InsertAfter_Last(self) -> None:
		clock = _signal("Clock")
		architecture = _architecture(clock)
		enable = _signal("Enable")

		architecture.InsertDeclaredItemAfter(enable, clock)

		self.assertListEqual([clock, enable], architecture.DeclaredItems)

	def test_InsertAfter_None(self) -> None:
		architecture = _architecture()

		with self.assertRaises(ValueError) as context:
			architecture.InsertDeclaredItemAfter(_signal("Enable"), None)

		self.assertEqual("Parameter 'after' is None.", str(context.exception))

	def test_InsertAfter_WrongType(self) -> None:
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.InsertDeclaredItemAfter(_signal("Enable"), 1)

		self.assertEqual("Parameter 'after' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_InsertAfter_NotAChild(self) -> None:
		useClause = UseClause([])
		architecture = _architecture()

		with self.assertRaises(NotAChildError) as context:
			architecture.InsertDeclaredItemAfter(_signal("Enable"), useClause)

		self.assertEqual("UseClause is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(useClause, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)

	def test_InsertAfter_Duplicate(self) -> None:
		clock = _signal("Clock")
		architecture = _architecture(clock)
		duplicate = _signal("clock")


		with self.assertRaises(DuplicateSignalError) as context:
			architecture.InsertDeclaredItemAfter(duplicate, clock)

		self.assertEqual("Architecture already declares 'clock'.", str(context.exception))
		self.assertEqual("clock", context.exception.Identifier)
		self.assertEqual("clock", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertIs(duplicate, context.exception.Element)
		self.assertIs(clock, context.exception.Existing)


class Remove(Testcase):
	def test_Remove(self) -> None:
		signal = _signal("a", "b")
		constant = _constant("C")
		architecture = _architecture(signal, constant)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(signal)

		self.assertListEqual([constant], architecture.DeclaredItems)
		self.assertIsNone(signal.Parent)
		self.assertDictEqual({}, architecture.Signals)
		self.assertDictEqual({"c": constant}, architecture._namespace._elements)

	def test_Remove_Kinds(self) -> None:
		fullType = FullType("t")
		component = Component("c")
		function = _function("f")
		architecture = _architecture(fullType, component, function)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(fullType)
		architecture.RemoveDeclaredItem(component)
		architecture.RemoveDeclaredItem(function)

		self.assertDictEqual({}, architecture.Types)
		self.assertDictEqual({}, architecture.Components)
		self.assertDictEqual({}, architecture.Functions)
		self.assertDictEqual({}, architecture._namespace._elements)

	def test_Remove_DeferredConstant(self) -> None:
		deferredConstant = DeferredConstant(["BITS"], _subtypeSymbol("positive"))
		package = Package("pkg", declaredItems=[deferredConstant])
		package.IndexDeclaredItems()

		package.RemoveDeclaredItem(deferredConstant)

		self.assertDictEqual({}, package.DeferredConstants)
		self.assertIsNone(deferredConstant.Parent)

	def test_Remove_ProtectedType(self) -> None:
		"""Removing a protected type leaves its body out of the lookup tables and the namespace."""
		protectedType = ProtectedType("counter")
		architecture = _architecture(protectedType, ProtectedTypeBody("counter"))
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(protectedType)

		self.assertDictEqual({}, architecture.Types)
		self.assertDictEqual({}, architecture._namespace._elements)

	def test_Remove_ParsedDuplicate(self) -> None:
		"""Removing one of two declarations parsed with the same identifier leaves the other one indexed."""
		signal1 = _signal("s")
		signal2 = _signal("s")
		architecture = _architecture(signal1, signal2)
		with WarningCollector():
			architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(signal2)

		self.assertDictEqual({"s": signal1}, architecture.Signals)
		self.assertDictEqual({"s": signal1}, architecture._namespace._elements)

	def test_Remove_ReAdd(self) -> None:
		"""A removed declared item can be added to another declarative region."""
		signal = _signal("s")
		architecture1 = _architecture(signal)
		architecture2 = _architecture()

		architecture1.RemoveDeclaredItem(signal)
		architecture2.AddDeclaredItem(signal)

		self.assertListEqual([], architecture1.DeclaredItems)
		self.assertListEqual([signal], architecture2.DeclaredItems)
		self.assertIs(architecture2, signal.Parent)

	def test_Remove_Move(self) -> None:
		"""Remove and insert move a declared item to another position."""
		clock = _signal("Clock")
		reset = _signal("Reset")
		enable = _signal("Enable")
		architecture = _architecture(clock, reset, enable)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(enable)
		architecture.InsertDeclaredItemBefore(enable, clock)

		self.assertListEqual([enable, clock, reset], architecture.DeclaredItems)
		self.assertIs(enable, architecture.Signals["enable"])

	def test_Remove_None(self) -> None:
		architecture = _architecture()

		with self.assertRaises(ValueError) as context:
			architecture.RemoveDeclaredItem(None)

		self.assertEqual("Parameter 'declaredItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		architecture = _architecture()

		with self.assertRaises(TypeError) as context:
			architecture.RemoveDeclaredItem("s")

		self.assertEqual("Parameter 'declaredItem' is not of type 'ModelEntity'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Remove_NotAChild(self) -> None:
		signal = _signal("a", "b")
		other = _architecture(signal)
		architecture = _architecture()

		with self.assertRaises(NotAChildError) as context:
			architecture.RemoveDeclaredItem(signal)

		self.assertEqual("Signal 'a, b' is not a declared item of this Architecture.", str(context.exception))
		self.assertIs(signal, context.exception.Element)
		self.assertIs(architecture, context.exception.Parent)
		self.assertIs(other, signal.Parent)


class Consistency(Testcase):
	def test_IndexDeclaredItems(self) -> None:
		"""After a sequence of mutations, indexing again changes neither the lookup tables nor the namespace."""
		signal = _signal("a", "b")
		constant = _constant("C")
		overload1 = _function("f")
		overload2 = _function("f")
		architecture = _architecture(signal, overload1)
		architecture.IndexDeclaredItems()

		architecture.InsertDeclaredItem(0, overload2)
		architecture.InsertDeclaredItemAfter(constant, signal)
		architecture.AddDeclaredItem(FullType("t"))
		architecture.RemoveDeclaredItem(signal)
		architecture.AddDeclaredItem(Component("comp"))

		signals = dict(architecture.Signals)
		constants = dict(architecture.Constants)
		types = dict(architecture.Types)
		components = dict(architecture.Components)
		functions = {name: list(overloads) for name, overloads in architecture.Functions.items()}
		elements = dict(architecture._namespace._elements)
		architecture.IndexDeclaredItems()

		self.assertDictEqual(signals, architecture.Signals)
		self.assertDictEqual(constants, architecture.Constants)
		self.assertDictEqual(types, architecture.Types)
		self.assertDictEqual(components, architecture.Components)
		self.assertDictEqual(functions, architecture.Functions)
		self.assertDictEqual(elements, architecture._namespace._elements)
