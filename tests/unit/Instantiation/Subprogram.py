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
"""Tests for pyVHDLModel.Subprogram."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import Mode
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem
from pyVHDLModel.Name        import SelectedName, SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol
from pyVHDLModel.Sequential  import NullStatement
from pyVHDLModel.Type        import ProtectedType, Subtype
from pyVHDLModel.Subprogram  import Procedure, Function, ProcedureMethod, FunctionMethod, SubprogramSignature


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _returnType(name: str = "integer") -> SimpleSubtypeSymbol:
	return SimpleSubtypeSymbol(SimpleName(name))


class Procedures(Testcase):
	"""``Subprogram`` itself is not meant to be instantiated directly (there's no VHDL construct that
	is "just" a subprogram, only procedures and functions) - its shared declared-items/statements/
	generic-items/parameter-items wiring is tested once here via ``Procedure``, the simpler of its two
	concrete subclasses, rather than on the base class itself."""

	def test_Minimal(self) -> None:
		procedure = Procedure("proc")

		self.assertEqual("proc", procedure.Identifier)
		self.assertFalse(procedure.IsPure)
		self.assertEqual(0, len(procedure.GenericItems))
		self.assertEqual(0, len(procedure.ParameterItems))
		self.assertEqual(0, len(procedure.DeclaredItems))
		self.assertEqual(0, len(procedure.Statements))

	def test_WithDeclaredItemsAndStatements(self) -> None:
		declaredItem = Procedure("nested")
		statement = NullStatement()
		procedure = Procedure("proc", declaredItems=[declaredItem], statements=[statement])

		self.assertEqual(1, len(procedure.DeclaredItems))
		self.assertIs(procedure, declaredItem.Parent)
		self.assertEqual(1, len(procedure.Statements))
		self.assertIs(procedure, statement.Parent)

	def test_WithGenericAndParameterItems(self) -> None:
		"""Uses bare ``Procedure`` stand-ins for the generic/parameter items - only ``.Parent``-wiring
		is exercised here, and real ``GenericInterfaceItemMixin``/``ParameterInterfaceItemMixin``
		classes are covered in tests/unit/Interface.py."""
		genericItem = Procedure("generic_item")
		parameterItem = Procedure("parameter_item")
		procedure = Procedure("proc", genericItems=[genericItem], parameterItems=[parameterItem])

		self.assertEqual(1, len(procedure.GenericItems))
		self.assertIs(procedure, genericItem.Parent)
		self.assertEqual(1, len(procedure.ParameterItems))
		self.assertIs(procedure, parameterItem.Parent)


class Functions(Testcase):
	def test_Minimal(self) -> None:
		returnType = _returnType()
		function = Function("func", returnType)

		self.assertIs(returnType, function.ReturnType)
		self.assertIs(function, returnType.Parent)
		self.assertTrue(function.IsPure)

	def test_Impure(self) -> None:
		function = Function("func", _returnType(), isPure=False)

		self.assertFalse(function.IsPure)


class MethodMixinHosts(Testcase):
	"""Regression test: ``MethodMixin.__init__`` set ``protectedType.Parent = self`` unconditionally,
	but ``protectedType`` genuinely defaults to ``None`` at both call sites (a subprogram declared
	directly in a protected type body still goes through the same constructor) - so the common,
	no-argument case crashed immediately with ``AttributeError: 'NoneType' object has no attribute
	'Parent'``. Fixed to null-check like every other optional-reference mixin in this codebase."""

	def test_ProcedureMethod_WithoutProtectedType(self) -> None:
		method = ProcedureMethod("proc")

		self.assertIsNone(method.ProtectedType)

	def test_ProcedureMethod_WithProtectedType(self) -> None:
		protectedType = ProtectedType("pt")
		method = ProcedureMethod("proc", protectedType=protectedType)

		self.assertIs(protectedType, method.ProtectedType)
		self.assertIs(method, protectedType.Parent)

	def test_FunctionMethod_WithoutProtectedType(self) -> None:
		method = FunctionMethod("func", _returnType())

		self.assertIsNone(method.ProtectedType)

	def test_FunctionMethod_WithProtectedType(self) -> None:
		protectedType = ProtectedType("pt")
		method = FunctionMethod("func", _returnType(), protectedType=protectedType)

		self.assertIs(protectedType, method.ProtectedType)
		self.assertIs(method, protectedType.Parent)


def _parameter(identifiers: tuple[str, ...], typeMark: SimpleSubtypeSymbol) -> ParameterConstantInterfaceItem:
	return ParameterConstantInterfaceItem(identifiers, Mode.In, typeMark)


class Signatures(Testcase):
	def test_Procedure(self) -> None:
		natural = _returnType("natural")
		procedure = Procedure("reset", parameterItems=[_parameter(("value", ), natural)])

		signature = procedure.Signature

		self.assertIsInstance(signature, SubprogramSignature)
		self.assertIs(procedure, signature.Parent)
		self.assertEqual((natural, ), signature.ParameterTypes)
		self.assertIsNone(signature.ReturnType)
		self.assertEqual(("natural", ), signature.ParameterTypeNames)
		self.assertIsNone(signature.ReturnTypeName)
		self.assertEqual("[natural]", str(signature))

	def test_Procedure_WithoutParameters(self) -> None:
		self.assertEqual("[]", str(Procedure("reset").Signature))

	def test_Function(self) -> None:
		"""A parameter with an identifier list contributes its type mark per identifier."""
		unsigned = SimpleSubtypeSymbol(SelectedName("unsigned", SelectedName("numeric_std", SimpleName("ieee"))))
		positive = _returnType("positive")
		natural =  _returnType("natural")
		function = Function("to_index", natural, parameterItems=[
			_parameter(("value", ), unsigned),
			_parameter(("low", "high"), positive),
		])

		signature = function.Signature

		self.assertIs(function, signature.Parent)
		self.assertEqual((unsigned, positive, positive), signature.ParameterTypes)
		self.assertIs(natural, signature.ReturnType)
		self.assertEqual(("ieee.numeric_std.unsigned", "positive", "positive"), signature.ParameterTypeNames)
		self.assertEqual("natural", signature.ReturnTypeName)
		self.assertEqual("[ieee.numeric_std.unsigned, positive, positive return natural]", str(signature))

	def test_Function_WithoutParameters(self) -> None:
		self.assertEqual("[return integer]", str(Function("random", _returnType()).Signature))

	def test_Kept(self) -> None:
		value =    _parameter(("value", ), _returnType("unsigned"))
		function = Function("to_index", _returnType("natural"), parameterItems=[value])

		self.assertIs(function.Signature, function.Signature)

	def test_ParameterItemsChanged(self) -> None:
		"""Adding, inserting, moving and removing a parameter clears the kept signature."""
		value = _parameter(("value", ), _returnType("unsigned"))
		low =   _parameter(("low", ), _returnType("positive"))
		high =  _parameter(("high", ), _returnType("natural"))
		function = Function("to_index", _returnType("natural"), parameterItems=[value])

		signature = function.Signature
		function.AddParameterItem(low)
		self.assertIsNot(signature, function.Signature)
		self.assertEqual("[unsigned, positive return natural]", str(function.Signature))

		signature = function.Signature
		function.InsertParameterItem(0, high)
		self.assertIsNot(signature, function.Signature)
		self.assertEqual("[natural, unsigned, positive return natural]", str(function.Signature))

		signature = function.Signature
		function.MoveParameterItem(high, -1)
		self.assertIsNot(signature, function.Signature)
		self.assertEqual("[unsigned, positive, natural return natural]", str(function.Signature))

		signature = function.Signature
		function.RemoveParameterItem(value)
		self.assertIsNot(signature, function.Signature)
		self.assertEqual("[positive, natural return natural]", str(function.Signature))

	def test_Parent(self) -> None:
		with self.assertRaises(TypeError) as context:
			SubprogramSignature([], parent=ProtectedType("pt"))

		self.assertEqual("Parameter 'parent' is not of type 'Subprogram'.", str(context.exception))

	def test_Checks(self) -> None:
		for parameterTypes, returnType, exception in (
			(None,          None,      ValueError),
			(1,             None,      TypeError),
			(["natural"],   None,      TypeError),
			([],            "natural", TypeError),
		):
			with self.subTest(parameterTypes=parameterTypes, returnType=returnType):
				with self.assertRaises(exception):
					SubprogramSignature(parameterTypes, returnType)



class SignatureComparisons(Testcase):
	def test_Equal(self) -> None:
		"""Two overloads' signatures compare by their profile, not by their parent."""
		first =  Function("f", _returnType("natural"), parameterItems=[_parameter(("a", "b"), _returnType("bit"))])
		second = Function("g", _returnType("natural"), parameterItems=[
			_parameter(("x", ), _returnType("bit")),
			_parameter(("y", ), _returnType("bit"))
		])

		self.assertIsNot(first.Signature.Parent, second.Signature.Parent)
		self.assertEqual(first.Signature, second.Signature)
		self.assertFalse(first.Signature != second.Signature)
		self.assertEqual(hash(first.Signature), hash(second.Signature))

	def test_Equal_Normalized(self) -> None:
		"""Type mark names compare normalized (lower case)."""
		upperName = SelectedName("UNSIGNED", SimpleName("Numeric_Std"))
		lowerName = SelectedName("unsigned", SimpleName("numeric_std"))
		upper =     SubprogramSignature([SimpleSubtypeSymbol(upperName)], _returnType("Natural"))
		lower =     SubprogramSignature([SimpleSubtypeSymbol(lowerName)], _returnType("natural"))

		self.assertEqual(("numeric_std.unsigned", ), upper.NormalizedParameterTypeNames)
		self.assertEqual("natural", upper.NormalizedReturnTypeName)
		self.assertEqual(upper, lower)
		self.assertEqual(hash(upper), hash(lower))

	def test_Equal_Procedure(self) -> None:
		first =  Procedure("p", parameterItems=[_parameter(("a", ), _returnType("bit"))])
		second = Procedure("q", parameterItems=[_parameter(("b", ), _returnType("bit"))])

		self.assertIsNone(first.Signature.NormalizedReturnTypeName)
		self.assertEqual(first.Signature, second.Signature)
		self.assertEqual(hash(first.Signature), hash(second.Signature))

	def test_Unequal_ParameterType(self) -> None:
		first =  SubprogramSignature([_returnType("bit"), _returnType("natural")], _returnType("boolean"))
		second = SubprogramSignature([_returnType("bit"), _returnType("integer")], _returnType("boolean"))

		self.assertNotEqual(first, second)
		self.assertFalse(first == second)

	def test_Unequal_ParameterOrder(self) -> None:
		first =  SubprogramSignature([_returnType("bit"), _returnType("natural")])
		second = SubprogramSignature([_returnType("natural"), _returnType("bit")])

		self.assertNotEqual(first, second)

	def test_Unequal_ParameterCount(self) -> None:
		first =  SubprogramSignature([_returnType("bit")], _returnType("boolean"))
		second = SubprogramSignature([_returnType("bit"), _returnType("bit")], _returnType("boolean"))

		self.assertNotEqual(first, second)

	def test_Unequal_ReturnType(self) -> None:
		first =  SubprogramSignature([_returnType("bit")], _returnType("boolean"))
		second = SubprogramSignature([_returnType("bit")], _returnType("bit"))

		self.assertNotEqual(first, second)

	def test_Unequal_ProcedureFunction(self) -> None:
		"""A procedure's signature has no return type mark, so it differs from a function's with the same parameters."""
		procedure = SubprogramSignature([_returnType("bit")])
		function =  SubprogramSignature([_returnType("bit")], _returnType("bit"))

		self.assertNotEqual(procedure, function)

	def test_Unequal_AsWritten(self) -> None:
		"""Type marks aren't resolved: a simple name and a selected name of the same type differ."""
		simple =   SubprogramSignature([_returnType("natural")])
		name =     SelectedName("natural", SelectedName("standard", SimpleName("std")))
		selected = SubprogramSignature([SimpleSubtypeSymbol(name)])

		self.assertEqual(("std.standard.natural", ), selected.NormalizedParameterTypeNames)
		self.assertNotEqual(simple, selected)

	def test_Hash_Kept(self) -> None:
		"""Resolving a type mark doesn't change the hash."""
		natural =   _returnType("natural")
		signature = SubprogramSignature([natural])
		before =    hash(signature)

		natural.Subtype = Subtype("natural", _returnType("integer"))

		self.assertEqual(before, hash(signature))

	def test_Hash_ParameterItemsChanged(self) -> None:
		"""A changed parameter list gives a new signature; the previous one keeps its profile and hash."""
		function =  Function("f", _returnType("natural"), parameterItems=[_parameter(("a", ), _returnType("bit"))])
		signature = function.Signature
		before =    hash(signature)

		function.AddParameterItem(_parameter(("b", ), _returnType("bit")))

		self.assertEqual(before, hash(signature))
		self.assertEqual(("bit", ), signature.NormalizedParameterTypeNames)
		self.assertNotEqual(signature, function.Signature)

	def test_DictionaryKey(self) -> None:
		first =  Function("f", _returnType("natural"), parameterItems=[_parameter(("a", ), _returnType("bit"))])
		second = Function("f", _returnType("natural"), parameterItems=[_parameter(("b", ), _returnType("BIT"))])
		third =  Function("f", _returnType("natural"), parameterItems=[_parameter(("a", ), _returnType("bit_vector"))])

		overloads = {first.Signature: first}

		self.assertIn(second.Signature, overloads)
		self.assertIs(first, overloads[second.Signature])
		self.assertNotIn(third.Signature, overloads)

	def test_SetMember(self) -> None:
		signatures = {
			SubprogramSignature([_returnType("bit")]),
			SubprogramSignature([_returnType("Bit")]),
			SubprogramSignature([_returnType("bit")], _returnType("bit")),
			SubprogramSignature([])
		}

		self.assertEqual(3, len(signatures))
		self.assertIn(SubprogramSignature([]), signatures)

	def test_OtherType(self) -> None:
		signature = SubprogramSignature([])

		with self.assertRaises(TypeError) as context:
			_ = signature == "[]"

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = signature != "[]"

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
