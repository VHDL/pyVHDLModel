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
from pyVHDLModel.Type        import ProtectedType
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
		self.assertEqual((natural, ), signature.ParameterTypes)
		self.assertIsNone(signature.ReturnType)
		self.assertEqual(["natural"], signature.ParameterTypeNames())
		self.assertIsNone(signature.ReturnTypeName())
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

		self.assertEqual((unsigned, positive, positive), signature.ParameterTypes)
		self.assertIs(natural, signature.ReturnType)
		self.assertEqual(["ieee.numeric_std.unsigned", "positive", "positive"], signature.ParameterTypeNames())
		self.assertEqual("natural", signature.ReturnTypeName())
		self.assertEqual("[ieee.numeric_std.unsigned, positive, positive return natural]", str(signature))

	def test_Function_WithoutParameters(self) -> None:
		self.assertEqual("[return integer]", str(Function("random", _returnType()).Signature))

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

