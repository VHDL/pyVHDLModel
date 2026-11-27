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
# Derived from the package declaration of STD_LOGIC_ARITH by Synopsys, Inc.:                                           #
#                                                                                                                      #
#   Copyright (c) 1990,1991,1992 by Synopsys, Inc.  All rights reserved.                                               #
#                                                                                                                      #
#   This source file may be used and distributed without restriction                                                   #
#   provided that this copyright statement is not removed from the file                                                #
#   and that any derivative work contains this copyright notice.                                                       #
# ==================================================================================================================== #
#
"""
This module contains the Mentor Graphics and Synopsys variants of the package ``ieee.std_logic_arith`` of VHDL
library ``IEEE``.
"""

from typing                 import Iterable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Type       import ArrayType, Subtype
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Std_Logic_Arith_MentorGraphics(PredefinedPackage):
	"""
	Predefined Mentor Graphics package ``ieee.std_logic_arith``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_arith`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion, "Std_Logic_Arith")

		self._AddLibraryClause(("IEEE", ))


@export
class Std_Logic_Arith_Body_MentorGraphics(PredefinedPackageBody):
	"""
	Predefined package body of Mentor Graphics package ``ieee.std_logic_arith``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_arith`` package body.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion, "Std_Logic_Arith")


@export
class Std_Logic_Arith_Synopsys(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_arith``.

	It declares arithmetic, conversion and comparison functions for its types ``signed`` and ``unsigned``. Its
	declarations, in the order of the package:

	* the types ``unsigned`` and ``signed`` (arrays of ``std_logic``), the subtype ``small_int``
	* the operators ``"+"``, ``"-"``, ``"*"`` (also with ``integer`` or ``std_ulogic``), the unary ``"+"``, ``"-"``,
	  ``"abs"``, each returning ``unsigned``/``signed`` and, as a second overload, ``std_logic_vector``
	* the relational operators ``"<"`` ... ``"/="``
	* ``shl``, ``shr``, ``conv_integer``, ``conv_unsigned``, ``conv_signed``, ``conv_std_logic_vector``, ``ext`` and
	  ``sxt``
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_arith`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion, "Std_Logic_Arith")

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

		unsignedType = "unsigned"
		signedType =   "signed"
		vectorType =   "std_logic_vector"

		def operands(*typeNames: str) -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the parameters ``L`` and, of a binary operator, ``R``, each an interface item.

			:param typeNames: The names of the parameters' types, in declaration order.
			:returns:         The parameters.
			"""
			return tuple(
				self._InParameter((identifier, ), self._TypeMark(typeName))
				for identifier, typeName in zip(("L", "R"), typeNames)
			)

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

		def operatorsTwice(signatures: tuple[tuple[str, tuple[str, ...], str], ...]) -> None:
			"""
			Nested function declaring a group of operators twice: first returning their result types, then
			``std_logic_vector``.

			:param signatures: The operator symbols, the names of the parameters' types and of the result types.
			"""
			for operatorSymbol, typeNames, resultType in signatures:
				operator(operatorSymbol, operands(*typeNames), self._TypeMark(resultType))

			for operatorSymbol, typeNames, _ in signatures:
				operator(operatorSymbol, operands(*typeNames), self._TypeMark(vectorType))

		# Types and subtype
		self._DeclareItem(ArrayType(unsignedType, (self._TypeMark("natural"), ), self._TypeMark("std_logic")), self._types)
		self._DeclareItem(ArrayType(signedType, (self._TypeMark("natural"), ), self._TypeMark("std_logic")), self._types)
		smallInt = Subtype("small_int", ConstrainedScalarSubtypeSymbol(
			SimpleName("integer"),
			SimpleRange(IntegerLiteral(0), IntegerLiteral(1), Direction.To)
		))
		self._DeclareItem(smallInt, self._subtypes)

		# Arithmetic operators
		for operatorSymbol in ("+", "-"):
			operatorsTwice(tuple((operatorSymbol, typeNames, resultType) for typeNames, resultType in (
				((unsignedType, unsignedType), unsignedType), ((signedType,   signedType),   signedType),
				((unsignedType, signedType),   signedType),   ((signedType,   unsignedType), signedType),
				((unsignedType, "integer"),    unsignedType), (("integer",    unsignedType), unsignedType),
				((signedType,   "integer"),    signedType),   (("integer",    signedType),   signedType),
				((unsignedType, "std_ulogic"), unsignedType), (("std_ulogic", unsignedType), unsignedType),
				((signedType,   "std_ulogic"), signedType),   (("std_ulogic", signedType),   signedType)
			)))

		operatorsTwice((
			("+",   (unsignedType, ), unsignedType),
			("+",   (signedType, ),   signedType),
			("-",   (signedType, ),   signedType),
			("abs", (signedType, ),   signedType)
		))
		operatorsTwice((
			("*", (unsignedType, unsignedType), unsignedType),
			("*", (signedType,   signedType),   signedType),
			("*", (signedType,   unsignedType), signedType),
			("*", (unsignedType, signedType),   signedType)
		))

		# Relational operators
		for operatorSymbol in ("<", "<=", ">", ">=", "=", "/="):
			for typeNames in (
				(unsignedType, unsignedType), (signedType, signedType), (unsignedType, signedType), (signedType, unsignedType),
				(unsignedType, "integer"), ("integer", unsignedType), (signedType, "integer"), ("integer", signedType)
			):
				operator(operatorSymbol, operands(*typeNames), self._TypeMark("boolean"))

		# Shift and conversion functions
		for identifier in ("shl", "shr"):
			for argumentType in (unsignedType, signedType):
				function(identifier, (
					self._InParameter(("ARG", ), self._TypeMark(argumentType)),
					self._InParameter(("COUNT", ), self._TypeMark(unsignedType))
				), self._TypeMark(argumentType))

		for argumentType, resultType in (
			("integer", "integer"), (unsignedType, "integer"), (signedType, "integer"), ("std_ulogic", "small_int")
		):
			function(
				"conv_integer",
				(self._InParameter(("ARG", ), self._TypeMark(argumentType)), ),
				self._TypeMark(resultType)
			)

		for identifier, resultType in (
			("conv_unsigned",         unsignedType),
			("conv_signed",           signedType),
			("conv_std_logic_vector", vectorType)
		):
			for argumentType in ("integer", unsignedType, signedType, "std_ulogic"):
				function(identifier, (
					self._InParameter(("ARG", ), self._TypeMark(argumentType)),
					self._InParameter(("SIZE", ), self._TypeMark("integer"))
				), self._TypeMark(resultType))

		for identifier in ("ext", "sxt"):
			function(identifier, (
				self._InParameter(("ARG", ), self._TypeMark(vectorType)),
				self._InParameter(("SIZE", ), self._TypeMark("integer"))
			), self._TypeMark(vectorType))
