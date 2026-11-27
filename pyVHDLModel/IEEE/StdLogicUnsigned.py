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
# Derived from the package declaration of STD_LOGIC_UNSIGNED by Synopsys, Inc.:                                        #
#                                                                                                                      #
#   Copyright (c) 1990, 1991, 1992 by Synopsys, Inc.                                                                   #
#                                               All rights reserved.                                                   #
#                                                                                                                      #
#   This source file may be used and distributed without restriction                                                   #
#   provided that this copyright statement is not removed from the file                                                #
#   and that any derivative work contains this copyright notice.                                                       #
# ==================================================================================================================== #
#
"""This module contains the predefined Synopsys package ``ieee.std_logic_unsigned`` of VHDL library ``IEEE``."""

from typing                 import Iterable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.Predefined import PredefinedPackage


@export
class Std_Logic_Unsigned(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_unsigned``.

	It declares arithmetic and relational operators treating ``std_logic_vector`` as unsigned number. Its declarations, in
	the order of the package:

	* the operators ``"+"``, ``"-"`` (with a vector, ``integer`` or ``std_logic`` operand), the unary ``"+"`` and ``"*"``
	* the relational operators ``"<"`` ... ``"/="`` (with a vector or ``integer`` operand)
	* the functions ``shl``, ``shr`` and ``conv_integer``
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_unsigned`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))
		self._AddPackageClause(("IEEE.std_logic_arith.all", ))

		vectorType = "std_logic_vector"

		def operands(left: str, right: str) -> tuple[ParameterConstantInterfaceItem, ParameterConstantInterfaceItem]:
			"""
			Nested function creating the parameters ``L`` and ``R``, each an interface item of its own.

			:param left:  The name of the type of parameter ``L``.
			:param right: The name of the type of parameter ``R``.
			:returns:     The parameters.
			"""
			return self._InParameter(("L", ), self._TypeMark(left)), self._InParameter(("R", ), self._TypeMark(right))

		def operator(
			operatorSymbol: str,
			parameterItems: Iterable[ParameterConstantInterfaceItem],
			returnType:     SimpleSubtypeSymbol
		) -> None:
			"""
			Nested function declaring an operator of this package.

			:param operatorSymbol: The operator symbol without quotation marks.
			:param parameterItems: The parameters, in declaration order.
			:param returnType:     The type mark of the return value.
			"""
			self._DeclareSubprogram(Operator(operatorSymbol, returnType, parameterItems=parameterItems), self._functions)

		def function(
			identifier:     str,
			parameterItems: Iterable[ParameterConstantInterfaceItem],
			returnType:     SimpleSubtypeSymbol
		) -> None:
			"""
			Nested function declaring a function of this package.

			:param identifier:     The function's identifier.
			:param parameterItems: The parameters, in declaration order.
			:param returnType:     The type mark of the return value.
			"""
			self._DeclareSubprogram(Function(identifier, returnType, parameterItems=parameterItems), self._functions)

		# Arithmetic operators
		for operatorSymbol in ("+", "-"):
			for left, right in (
				(vectorType, vectorType), (vectorType, "integer"), ("integer", vectorType), (vectorType, "std_logic"),
				("std_logic", vectorType)
			):
				operator(operatorSymbol, operands(left, right), self._TypeMark(vectorType))

		operator("+", (self._InParameter(("L", ), self._TypeMark(vectorType)), ), self._TypeMark(vectorType))
		operator("*", operands(vectorType, vectorType), self._TypeMark(vectorType))

		# Relational operators
		for operatorSymbol in ("<", "<=", ">", ">=", "=", "/="):
			for left, right in ((vectorType, vectorType), (vectorType, "integer"), ("integer", vectorType)):
				operator(operatorSymbol, operands(left, right), self._TypeMark("boolean"))

		# shl, shr, conv_integer
		for identifier in ("shl", "shr"):
			function(identifier, (
				self._InParameter(("ARG", ), self._TypeMark(vectorType)),
				self._InParameter(("COUNT", ), self._TypeMark(vectorType))
			), self._TypeMark(vectorType))

		function("conv_integer", (self._InParameter(("ARG", ), self._TypeMark(vectorType)), ), self._TypeMark("integer"))
