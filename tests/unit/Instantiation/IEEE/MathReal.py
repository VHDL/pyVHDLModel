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
"""Tests for pyVHDLModel.IEEE.MathRealPkg."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Expression import FloatingPointLiteral, StringLiteral
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function, Operator
from pyVHDLModel.IEEE       import Math_Real


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class MathReals(Testcase):
	"""Package ``ieee.math_real`` (IEEE Std 1076-2008, 16.8.2)."""

	def test_Constants(self) -> None:
		"""The constants in the order of the standard, each with the package as parent."""
		mathReal =  Math_Real()
		constants = [item for item in mathReal.DeclaredItems if isinstance(item, Constant)]

		self.assertListEqual(
			[
				"copyrightnotice", "math_e", "math_1_over_e", "math_pi", "math_2_pi", "math_1_over_pi", "math_pi_over_2",
				"math_pi_over_3", "math_pi_over_4", "math_3_pi_over_2", "math_log_of_2", "math_log_of_10", "math_log2_of_e",
				"math_log10_of_e", "math_sqrt_2", "math_1_over_sqrt_2", "math_sqrt_pi", "math_deg_to_rad", "math_rad_to_deg"
			],
			[constant.Identifiers[0] for constant in constants]
		)
		for constant in constants:
			self.assertIs(mathReal, constant.Parent)
			self.assertIs(constant, mathReal.Constants[constant.Identifiers[0]])

	def test_ConstantValues(self) -> None:
		"""The mathematical constants are ``real`` literals; ``copyrightnotice`` is a ``string``."""
		constants = Math_Real().Constants

		self.assertEqual("string", constants["copyrightnotice"].Subtype.Name.Identifier)
		self.assertIsInstance(constants["copyrightnotice"].DefaultExpression, StringLiteral)
		self.assertEqual(
			"Copyright \u00a9 2008 IEEE. All rights reserved.",
			constants["copyrightnotice"].DefaultExpression.Value
		)
		for identifier, value in (
			("math_e",          2.718281828459045),
			("math_pi",         3.141592653589793),
			("math_rad_to_deg", 57.29577951308232)
		):
			constant = constants[identifier]
			self.assertEqual("real", constant.Subtype.Name.Identifier)
			self.assertIsInstance(constant.DefaultExpression, FloatingPointLiteral)
			self.assertEqual(value, constant.DefaultExpression.Value)

	def test_Subprograms(self) -> None:
		"""The subprograms in the order of the standard, each with the package as parent."""
		mathReal =    Math_Real()
		subprograms = [item for item in mathReal.DeclaredItems if not isinstance(item, Constant)]

		self.assertListEqual(
			[
				"sign", "ceil", "floor", "round", "trunc", "mod", "realmax", "realmin", "uniform", "sqrt", "cbrt", "**", "**",
				"exp", "log", "log2", "log10", "log", "sin", "cos", "tan", "arcsin", "arccos", "arctan", "arctan", "sinh",
				"cosh", "tanh", "arcsinh", "arccosh", "arctanh"
			],
			[subprogram.Identifier for subprogram in subprograms]
		)
		for subprogram in subprograms:
			self.assertIs(mathReal, subprogram.Parent)

	def test_Overloads(self) -> None:
		"""30 functions, 27 designators (``"**"``, ``log``, ``arctan`` are overloaded); one procedure, ``uniform``."""
		mathReal = Math_Real()

		self.assertEqual(27, len(mathReal.Functions))
		for identifier in ("**", "log", "arctan"):
			self.assertEqual(2, len(mathReal.Functions[identifier]))

		self.assertListEqual(["uniform"], list(mathReal.Procedures))

	def test_Functions(self) -> None:
		"""``function SQRT (X : in REAL) return REAL;``"""
		sqrt, = Math_Real().Functions["sqrt"]

		self.assertIsInstance(sqrt, Function)
		self.assertNotIsInstance(sqrt, Operator)
		self.assertEqual("real", sqrt.ReturnType.Name.Identifier)
		item, = sqrt.ParameterItems
		self.assertIsInstance(item, ParameterConstantInterfaceItem)
		self.assertIs(Mode.In, item.Mode)
		self.assertTupleEqual(("X",), item.Identifiers)
		self.assertEqual("real", item.Subtype.Name.Identifier)

	def test_Mod(self) -> None:
		"""``function "MOD" (X, Y : in REAL) return REAL;``: an operator with one parameter declaration of two."""
		mod, = Math_Real().Functions["mod"]

		self.assertIsInstance(mod, Operator)
		item, = mod.ParameterItems
		self.assertTupleEqual(("X", "Y"), item.Identifiers)

	def test_Exponentiation(self) -> None:
		"""``"**"`` with an ``integer`` and with a ``real`` base."""
		integerBase, realBase = Math_Real().Functions["**"]

		self.assertIsInstance(integerBase, Operator)
		self.assertIsInstance(realBase, Operator)
		self.assertListEqual(["integer", "real"], [item.Subtype.Name.Identifier for item in integerBase.ParameterItems])
		self.assertListEqual(["real", "real"], [item.Subtype.Name.Identifier for item in realBase.ParameterItems])

	def test_Uniform(self) -> None:
		"""``procedure UNIFORM (variable SEED1, SEED2 : inout POSITIVE; variable X : out REAL);``"""
		uniform, = Math_Real().Procedures["uniform"]
		seeds, x = uniform.ParameterItems

		self.assertIsInstance(uniform, Procedure)
		self.assertIsInstance(seeds, ParameterVariableInterfaceItem)
		self.assertIs(Mode.InOut, seeds.Mode)
		self.assertTupleEqual(("SEED1", "SEED2"), seeds.Identifiers)
		self.assertEqual("positive", seeds.Subtype.Name.Identifier)
		self.assertIsInstance(x, ParameterVariableInterfaceItem)
		self.assertIs(Mode.Out, x.Mode)
		self.assertEqual("real", x.Subtype.Name.Identifier)
