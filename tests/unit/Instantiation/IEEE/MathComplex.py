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
"""Tests for pyVHDLModel.IEEE.MathComplexPkg."""
from pyTooling.Testing               import Testcase

from pyVHDLModel.Base                import Direction, Mode
from pyVHDLModel.Expression          import FloatingPointLiteral, StringLiteral, NegationExpression, \
                                            QualifiedExpression, Aggregate, SimpleAggregateElement
from pyVHDLModel.Symbol              import ConstrainedScalarSubtypeSymbol, SimpleObjectOrFunctionCallSymbol, \
                                            IndexedObjectOrFunctionCallSymbol
from pyVHDLModel.Interface           import ParameterConstantInterfaceItem
from pyVHDLModel.Subprogram          import Function, Operator
from pyVHDLModel.Type                import RecordType
from pyVHDLModel.IEEE.MathComplexPkg import Math_Complex


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class MathComplexs(Testcase):
	"""Package ``ieee.math_complex`` (IEEE Std 1076-2008, 16.8.3)."""

	def setUp(self) -> None:
		self._package = Math_Complex()

	def test_Declarations(self) -> None:
		"""The types, subtypes and constants in the order of the standard, then the 58 subprograms."""
		declarations = self._package.DeclaredItems

		self.assertIs(self._package.Constants["copyrightnotice"], declarations[0])
		self.assertIs(self._package.Types["complex"],             declarations[1])
		self.assertIs(self._package.Subtypes["positive_real"],    declarations[2])
		self.assertIs(self._package.Subtypes["principal_value"],  declarations[3])
		self.assertIs(self._package.Types["complex_polar"],       declarations[4])
		self.assertIs(self._package.Constants["math_cbase_1"],    declarations[5])
		self.assertIs(self._package.Constants["math_cbase_j"],    declarations[6])
		self.assertIs(self._package.Constants["math_czero"],      declarations[7])
		self.assertEqual(66, len(declarations))
		for declaration in declarations[8:]:
			self.assertIsInstance(declaration, Function)

	def test_Parent(self) -> None:
		for declaration in self._package.DeclaredItems:
			self.assertIs(self._package, declaration.Parent)

	def test_Complex(self) -> None:
		"""``type COMPLEX is record RE : REAL; IM : REAL; end record;``"""
		complexType = self._package.Types["complex"]

		self.assertIsInstance(complexType, RecordType)
		self.assertListEqual([("re",), ("im",)], [element.Identifiers for element in complexType.Elements])
		for element in complexType.Elements:
			self.assertEqual("real", element.Subtype.Name.Identifier)

	def test_ComplexPolar(self) -> None:
		"""``type COMPLEX_POLAR is record MAG : POSITIVE_REAL; ARG : PRINCIPAL_VALUE; end record;``"""
		complexPolar = self._package.Types["complex_polar"]

		self.assertIsInstance(complexPolar, RecordType)
		self.assertListEqual([("mag",), ("arg",)], [element.Identifiers for element in complexPolar.Elements])
		self.assertListEqual(
			["positive_real", "principal_value"],
			[element.Subtype.Name.Identifier for element in complexPolar.Elements]
		)

	def test_PositiveReal(self) -> None:
		"""``subtype POSITIVE_REAL is REAL range 0.0 to REAL'HIGH;``"""
		positiveReal = self._package.Subtypes["positive_real"]
		rng =          positiveReal.Range

		self.assertIsInstance(positiveReal.Type, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("real", positiveReal.Type.Name.Identifier)
		self.assertIsInstance(rng.LeftBound, FloatingPointLiteral)
		self.assertEqual(0.0, rng.LeftBound.Value)
		self.assertIsInstance(rng.RightBound, IndexedObjectOrFunctionCallSymbol)
		self.assertEqual("high", rng.RightBound.Name.Identifier)
		self.assertEqual("real", rng.RightBound.Name.Prefix.Identifier)
		self.assertIs(Direction.To, rng.Direction)

	def test_PrincipalValue(self) -> None:
		"""``subtype PRINCIPAL_VALUE is REAL range -MATH_PI to MATH_PI;``"""
		principalValue = self._package.Subtypes["principal_value"]
		rng =            principalValue.Range

		self.assertIsInstance(principalValue.Type, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("real", principalValue.Type.Name.Identifier)
		self.assertIsInstance(rng.LeftBound, NegationExpression)
		self.assertIsInstance(rng.LeftBound.Operand, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("math_pi", rng.LeftBound.Operand.Name.Identifier)
		self.assertIsInstance(rng.RightBound, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("math_pi", rng.RightBound.Name.Identifier)
		self.assertIs(Direction.To, rng.Direction)

	def test_CopyRightNotice(self) -> None:
		constant = self._package.Constants["copyrightnotice"]

		self.assertEqual("string", constant.Subtype.Name.Identifier)
		self.assertIsInstance(constant.DefaultExpression, StringLiteral)
		self.assertEqual("Copyright \u00a9 2008 IEEE. All rights reserved.", constant.DefaultExpression.Value)

	def test_Constants(self) -> None:
		"""``constant MATH_CBASE_1 : COMPLEX := COMPLEX'(1.0, 0.0);``, ``MATH_CBASE_J`` and ``MATH_CZERO``."""
		for identifier, re, im in (
			("math_cbase_1", 1.0, 0.0),
			("math_cbase_j", 0.0, 1.0),
			("math_czero",   0.0, 0.0)
		):
			constant = self._package.Constants[identifier]
			value =    constant.DefaultExpression
			self.assertEqual("complex", constant.Subtype.Name.Identifier)
			self.assertIsInstance(value, QualifiedExpression)
			self.assertEqual("complex", value.Subtype.Name.Identifier)
			self.assertIsInstance(value.Operand, Aggregate)
			for element in value.Operand.Elements:
				self.assertIsInstance(element, SimpleAggregateElement)

			self.assertListEqual([re, im], [element.Expression.Value for element in value.Operand.Elements])

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{
				"=": 1, "/=": 1, "cmplx": 1, "get_principal_value": 1, "complex_to_polar": 1, "polar_to_complex": 1,
				"abs": 2, "arg": 2, "-": 8, "conj": 2, "sqrt": 2, "exp": 2, "log": 4, "log2": 2, "log10": 2, "sin": 2,
				"cos": 2, "sinh": 2, "cosh": 2, "+": 6, "*": 6, "/": 6
			},
			{designator: len(overloads) for designator, overloads in self._package.Functions.items()}
		)

	def test_Operators(self) -> None:
		"""A designator written as operator symbol is an :class:`Operator`, the others are functions."""
		for designator in ("=", "/=", "abs", "-", "+", "*", "/"):
			for function in self._package.Functions[designator]:
				self.assertIsInstance(function, Operator)

		for designator in ("cmplx", "arg", "conj", "sqrt", "log", "cosh"):
			for function in self._package.Functions[designator]:
				self.assertNotIsInstance(function, Operator)

	def test_Parameters(self) -> None:
		"""Every parameter is a constant of mode ``in``."""
		for overloads in self._package.Functions.values():
			for function in overloads:
				for item in function.ParameterItems:
					self.assertIsInstance(item, ParameterConstantInterfaceItem)
					self.assertIs(Mode.In, item.Mode)

	def test_Cmplx(self) -> None:
		"""``function CMPLX (X : in REAL; Y : in REAL := 0.0) return COMPLEX;``"""
		cmplx, = self._package.Functions["cmplx"]
		x, y =   cmplx.ParameterItems

		self.assertEqual("complex", cmplx.ReturnType.Name.Identifier)
		self.assertEqual(("X",), x.Identifiers)
		self.assertIsNone(x.DefaultExpression)
		self.assertEqual(("Y",), y.Identifiers)
		self.assertIsInstance(y.DefaultExpression, FloatingPointLiteral)
		self.assertEqual(0.0, y.DefaultExpression.Value)

	def test_Log(self) -> None:
		"""``LOG`` of a complex number, of a polar one, and each with a ``BASE``."""
		self.assertListEqual(
			[["complex"], ["complex_polar"], ["complex", "real"], ["complex_polar", "real"]],
			[[item.Subtype.Name.Identifier for item in log.ParameterItems] for log in self._package.Functions["log"]]
		)

	def test_Plus(self) -> None:
		"""``"+"`` of two complex numbers and of a complex number and a ``real``, for both representations."""
		pluses = self._package.Functions["+"]

		self.assertListEqual(
			[
				["complex", "complex"], ["real", "complex"], ["complex", "real"],
				["complex_polar", "complex_polar"], ["real", "complex_polar"], ["complex_polar", "real"]
			],
			[[item.Subtype.Name.Identifier for item in plus.ParameterItems] for plus in pluses]
		)
		self.assertListEqual(
			["complex"] * 3 + ["complex_polar"] * 3,
			[plus.ReturnType.Name.Identifier for plus in pluses]
		)

	def test_Minus(self) -> None:
		"""The unary ``"-"`` of both representations precedes the binary ones."""
		minuses = self._package.Functions["-"]

		self.assertListEqual([1, 1, 2, 2, 2, 2, 2, 2], [len(minus.ParameterItems) for minus in minuses])
