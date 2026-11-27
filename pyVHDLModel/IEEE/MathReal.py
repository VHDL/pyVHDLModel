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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
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
"""This module contains the predefined package ``ieee.math_real`` of VHDL library ``IEEE``."""

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import Mode
from pyVHDLModel.Expression import FloatingPointLiteral, StringLiteral
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function, Operator
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Math_Real(PredefinedPackage):
	"""
	Predefined package ``ieee.math_real`` (IEEE Std 1076-2008, 16.8.2).

	Its declarations, in the order of the standard:

	* the constant ``copyrightnotice`` and the mathematical constants, e.g. ``math_e`` and ``math_pi``
	* the functions ``sign``, ``ceil``, ``floor``, ``round``, ``trunc``, the operator ``"mod"``, the functions ``realmax``
	  and ``realmin``, and the procedure ``uniform``
	* the functions ``sqrt``, ``cbrt``, the operators ``"**"``, and the exponential and logarithm functions
	* the trigonometric and hyperbolic functions and their inverses
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``math_real`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		def real(*identifiers: str) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a constant parameter of mode ``in`` and type ``real``.

			:param identifiers: The identifiers of the parameter declaration, e.g. ``X, Y``.
			:returns:           The parameter.
			"""
			return ParameterConstantInterfaceItem(identifiers, Mode.In, self._TypeMark("real"))

		def function(identifier: str, *parameterItems: ParameterConstantInterfaceItem) -> None:
			"""
			Nested function declaring a function returning ``real`` in this package.

			:param identifier:     The function's identifier.
			:param parameterItems: The function's parameters, in declaration order.
			"""
			declaration = Function(identifier, self._TypeMark("real"), parameterItems=parameterItems)
			self._DeclareSubprogram(declaration, self._functions)

		copyrightNotice = Constant(
			("copyrightnotice",),
			self._TypeMark("string"),
			StringLiteral("Copyright \u00a9 2008 IEEE. All rights reserved.")
		)
		self._constants["copyrightnotice"] = copyrightNotice
		self.AddDeclaredItem(copyrightNotice)

		for identifier, value in (
			("math_e",             2.71828_18284_59045_23536),
			("math_1_over_e",      0.36787_94411_71442_32160),
			("math_pi",            3.14159_26535_89793_23846),
			("math_2_pi",          6.28318_53071_79586_47693),
			("math_1_over_pi",     0.31830_98861_83790_67154),
			("math_pi_over_2",     1.57079_63267_94896_61923),
			("math_pi_over_3",     1.04719_75511_96597_74615),
			("math_pi_over_4",     0.78539_81633_97448_30962),
			("math_3_pi_over_2",   4.71238_89803_84689_85769),
			("math_log_of_2",      0.69314_71805_59945_30942),
			("math_log_of_10",     2.30258_50929_94045_68402),
			("math_log2_of_e",     1.44269_50408_88963_4074),
			("math_log10_of_e",    0.43429_44819_03251_82765),
			("math_sqrt_2",        1.41421_35623_73095_04880),
			("math_1_over_sqrt_2", 0.70710_67811_86547_52440),
			("math_sqrt_pi",       1.77245_38509_05516_02730),
			("math_deg_to_rad",    0.01745_32925_19943_29577),
			("math_rad_to_deg",    57.29577_95130_82320_87680)
		):
			constant =                    Constant((identifier,), self._TypeMark("real"), FloatingPointLiteral(value))
			self._constants[identifier] = constant
			self.AddDeclaredItem(constant)

		for identifier in ("sign", "ceil", "floor", "round", "trunc"):
			function(identifier, real("X"))

		self._DeclareSubprogram(Operator("mod", self._TypeMark("real"), parameterItems=(real("X", "Y"),)), self._functions)
		for identifier in ("realmax", "realmin"):
			function(identifier, real("X", "Y"))

		self._DeclareSubprogram(
			Procedure("uniform", parameterItems=(
				ParameterVariableInterfaceItem(("SEED1", "SEED2"), Mode.InOut, self._TypeMark("positive")),
				ParameterVariableInterfaceItem(("X",), Mode.Out, self._TypeMark("real"))
			)),
			self._procedures
		)

		for identifier in ("sqrt", "cbrt"):
			function(identifier, real("X"))

		self._DeclareSubprogram(
			Operator("**", self._TypeMark("real"), parameterItems=(
				ParameterConstantInterfaceItem(("X",), Mode.In, self._TypeMark("integer")),
				real("Y")
			)),
			self._functions
		)
		self._DeclareSubprogram(
			Operator("**", self._TypeMark("real"), parameterItems=(real("X"), real("Y"))),
			self._functions
		)

		for identifier in ("exp", "log", "log2", "log10"):
			function(identifier, real("X"))

		function("log", real("X"), real("BASE"))

		for identifier in ("sin", "cos", "tan", "arcsin", "arccos"):
			function(identifier, real("X"))

		function("arctan", real("Y"))
		function("arctan", real("Y"), real("X"))

		for identifier in ("sinh", "cosh", "tanh", "arcsinh", "arccosh", "arctanh"):
			function(identifier, real("X"))


@export
class Math_Real_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.math_real``.
	"""
