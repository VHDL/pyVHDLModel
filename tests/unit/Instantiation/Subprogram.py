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

from pyVHDLModel.Base        import Direction, Mode, SimpleRange
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, GenericTypeInterfaceItem
from pyVHDLModel.Name        import SelectedName, SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol
from pyVHDLModel.Sequential  import NullStatement
from pyVHDLModel.Type        import IntegerType, ProtectedType, RecordType, Subtype
from pyVHDLModel.Subprogram  import Procedure, Function, Operator, PredefinedOperator, PredefinedFunction, \
                                    PredefinedSubprogramMixin, ProcedureMethod, FunctionMethod, SubprogramSignature


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _returnType(name: str = "integer") -> SimpleSubtypeSymbol:
	return SimpleSubtypeSymbol(SimpleName(name))


class Procedures(Testcase):
	"""
	Procedures, also testing the shared subprogram behaviour.

	``Subprogram`` itself is not meant to be instantiated directly (there's no VHDL construct that
	is "just" a subprogram, only procedures and functions) - its shared declared-items/statements/
	generic-items/parameter-items wiring is tested once here via ``Procedure``, the simpler of its two
	concrete subclasses, rather than on the base class itself.
	"""

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
		"""A generic and a parameter are checked by their group, so they are real interface items."""
		genericItem = GenericTypeInterfaceItem("T")
		parameterItem = _parameter(("a", ), _returnType())
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

	def test_NormalizedDesignator(self) -> None:
		"""The key a namespace indexes the function by: its normalized identifier."""
		self.assertEqual("func", Function("Func", _returnType()).NormalizedDesignator)


class Operators(Testcase):
	def test_Construction(self) -> None:
		"""An operator: the operator symbol without quotation marks."""
		returnType = _returnType("bit")
		operator =   Operator("and", returnType, parameterItems=[_parameter(("L", "R"), _returnType("bit"))])

		self.assertEqual("and", operator.Identifier)
		self.assertIs(returnType, operator.ReturnType)
		self.assertIsInstance(operator, Function)

	def test_UpperCase(self) -> None:
		"""A word operator is normalized like an identifier."""
		operator = Operator("AND", _returnType("bit"))

		self.assertEqual("AND", operator.Identifier)
		self.assertEqual("and", operator.NormalizedIdentifier)
		self.assertEqual("and", operator.NormalizedDesignator)

	def test_NoOperatorSymbol(self) -> None:
		with self.assertRaises(ValueError) as context:
			Operator("func", _returnType())

		self.assertEqual("Parameter 'operatorSymbol' isn't an operator symbol.", str(context.exception))
		self.assertEqual("Got value 'func'.", context.exception.__notes__[0])


class PredefinedOperators(Testcase):
	def test_Construction(self) -> None:
		"""A predefined operator of a type: parameters, no body."""
		recordType = RecordType("rec", None)
		returnType = _returnType("boolean")
		left =       _parameter(("L",), SimpleSubtypeSymbol(SimpleName("rec")))
		right =      _parameter(("R",), SimpleSubtypeSymbol(SimpleName("rec")))
		operator =   PredefinedOperator("=", returnType, [left, right], parent=recordType)

		self.assertEqual("=", operator.Identifier)
		self.assertIs(returnType, operator.ReturnType)
		self.assertListEqual([left, right], operator.ParameterItems)
		self.assertIs(recordType, operator.Parent)
		self.assertIs(operator, left.Parent)
		self.assertTrue(operator.IsPure)
		self.assertListEqual([], operator.DeclaredItems)
		self.assertListEqual([], operator.Statements)
		self.assertIsInstance(operator, Operator)
		self.assertIsInstance(operator, PredefinedSubprogramMixin)

	def test_NoOperatorSymbol(self) -> None:
		with self.assertRaises(ValueError) as context:
			PredefinedOperator("minimum", _returnType(), [], parent=RecordType("rec", None))

		self.assertEqual("Parameter 'operatorSymbol' isn't an operator symbol.", str(context.exception))


class PredefinedFunctions(Testcase):
	def test_Construction(self) -> None:
		"""A predefined function of a type: an identifier, parameters, no body."""
		recordType = RecordType("rec", None)
		returnType = _returnType("rec")
		left =       _parameter(("L",), SimpleSubtypeSymbol(SimpleName("rec")))
		right =      _parameter(("R",), SimpleSubtypeSymbol(SimpleName("rec")))
		function =   PredefinedFunction("minimum", returnType, [left, right], parent=recordType)

		self.assertEqual("minimum", function.Identifier)
		self.assertIs(returnType, function.ReturnType)
		self.assertListEqual([left, right], function.ParameterItems)
		self.assertIs(recordType, function.Parent)
		self.assertIs(function, left.Parent)
		self.assertTrue(function.IsPure)
		self.assertListEqual([], function.DeclaredItems)
		self.assertListEqual([], function.Statements)
		self.assertNotIsInstance(function, Operator)
		self.assertIsInstance(function, PredefinedSubprogramMixin)


class MethodMixinHosts(Testcase):
	"""
	Procedure and function methods with and without a protected type.

	Regression test: ``MethodMixin.__init__`` set :pycode:`protectedType.Parent = self` unconditionally,
	but ``protectedType`` genuinely defaults to ``None`` at both call sites (a subprogram declared
	directly in a protected type body still goes through the same constructor) - so the common,
	no-argument case crashed immediately with ``AttributeError: 'NoneType' object has no attribute
	'Parent'``. Fixed to null-check like every other optional-reference mixin in this codebase.
	"""

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

		self.assertEqual("Parameter 'parent' is not of type 'Subprogram' or 'Alias'.", str(context.exception))

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


class TypeProfiles(Testcase):
	"""Two signatures have the same parameter and result type profile, if their base types match (4.5.1)."""

	def setUp(self) -> None:
		self._bit =     IntegerType("bit_like", SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To))
		self._integer = IntegerType("int_like", SimpleRange(IntegerLiteral(0), IntegerLiteral(9), Direction.To))

	def _typeMark(self, fullType: IntegerType) -> SimpleSubtypeSymbol:
		typeMark =         _returnType(fullType.Identifier)
		typeMark.Subtype = fullType

		return typeMark

	def test_Same(self) -> None:
		"""Type marks written differently, referencing the same types, have the same profile."""
		selected =         SimpleSubtypeSymbol(SelectedName("bit_like", SimpleName("p")))
		selected.Subtype = self._bit
		first =            SubprogramSignature([self._typeMark(self._bit)], self._typeMark(self._integer))
		second =           SubprogramSignature([selected], self._typeMark(self._integer))

		self.assertNotEqual(first, second)
		self.assertTrue(first.HasSameTypeProfile(second))

	def test_Same_Procedure(self) -> None:
		first =  SubprogramSignature([self._typeMark(self._bit), self._typeMark(self._integer)])
		second = SubprogramSignature([self._typeMark(self._bit), self._typeMark(self._integer)])

		self.assertTrue(first.HasSameTypeProfile(second))

	def test_Different_ParameterType(self) -> None:
		first =  SubprogramSignature([self._typeMark(self._bit)], self._typeMark(self._integer))
		second = SubprogramSignature([self._typeMark(self._integer)], self._typeMark(self._integer))

		self.assertFalse(first.HasSameTypeProfile(second))

	def test_Different_ReturnType(self) -> None:
		first =  SubprogramSignature([self._typeMark(self._bit)], self._typeMark(self._integer))
		second = SubprogramSignature([self._typeMark(self._bit)], self._typeMark(self._bit))

		self.assertFalse(first.HasSameTypeProfile(second))

	def test_Different_ParameterCount(self) -> None:
		first =  SubprogramSignature([self._typeMark(self._bit)], self._typeMark(self._integer))
		second = SubprogramSignature([self._typeMark(self._bit), self._typeMark(self._bit)], self._typeMark(self._integer))

		self.assertFalse(first.HasSameTypeProfile(second))

	def test_Different_ProcedureFunction(self) -> None:
		procedure = SubprogramSignature([self._typeMark(self._bit)])
		function =  SubprogramSignature([self._typeMark(self._bit)], self._typeMark(self._bit))

		self.assertFalse(procedure.HasSameTypeProfile(function))
		self.assertFalse(function.HasSameTypeProfile(procedure))

	def test_Unresolved(self) -> None:
		"""A signature with an unresolved type mark has no profile to compare."""
		resolved =   SubprogramSignature([self._typeMark(self._bit)])
		unresolved = SubprogramSignature([_returnType("bit_like")])

		self.assertFalse(resolved.HasSameTypeProfile(unresolved))
		self.assertFalse(unresolved.HasSameTypeProfile(resolved))

	def test_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			SubprogramSignature([]).HasSameTypeProfile(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_OtherType(self) -> None:
		with self.assertRaises(TypeError) as context:
			SubprogramSignature([]).HasSameTypeProfile("[]")

		self.assertEqual("Parameter 'other' is not of type 'SubprogramSignature'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
