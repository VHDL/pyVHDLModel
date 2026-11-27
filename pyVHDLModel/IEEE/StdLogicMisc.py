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
# Derived from the package declaration of std_logic_misc by Synopsys, Inc.:                                            #
#                                                                                                                      #
#   Copyright (c) 1990, 1991, 1992 by Synopsys, Inc.  All rights reserved.                                             #
#                                                                                                                      #
#   This source file may be used and distributed without restriction                                                   #
#   provided that this copyright statement is not removed from the file                                                #
#   and that any derivative work contains this copyright notice.                                                       #
# ==================================================================================================================== #
#
"""This module contains the predefined Synopsys package ``ieee.std_logic_misc`` of VHDL library ``IEEE``."""

from typing                 import Iterable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression import AscendingRangeExpression, CharacterLiteral, EnumerationLiteral, IntegerLiteral
from pyVHDLModel.Type       import ArrayType, EnumeratedType
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Subprogram import Function
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Std_Logic_Misc(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_misc``.

	It defines supplemental types and functions for ``ieee.std_logic_1164``. Its declarations, in the order of the
	package:

	* the types ``strength`` and ``minomax``
	* the functions ``strength_map``, ``strength_map_z``, ``drive``, ``sense``, the conversions to ``bit`` and
	  ``bit_vector`` (``std_logic_vectortobit_vector``, ...)
	* the reduction functions ``and_reduce`` ... ``xnor_reduce`` and the functions ``fun_buf3s`` ... ``fun_wiredx``
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_misc`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

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

		def parameter(identifiers: Iterable[str], typeName: str) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a parameter without default value.

			:param identifiers: The parameter's identifiers.
			:param typeName:    The name of the parameter's type.
			:returns:           The parameter.
			"""
			return self._InParameter(identifiers, self._TypeMark(typeName))

		# Types
		self._DeclareItem(EnumeratedType("strength", [EnumerationLiteral(literal) for literal in (
			"strn_x01", "strn_x0h", "strn_xl1", "strn_x0z", "strn_xz1", "strn_wlh", "strn_wlz", "strn_wzh", "strn_w0h",
			"strn_wl1"
		)]), self._types)
		self._DeclareItem(ArrayType(
			"minomax",
			(AscendingRangeExpression(IntegerLiteral(1), IntegerLiteral(3)), ),
			self._TypeMark("time")
		), self._types)

		# strength_map, drive, sense
		for identifier in ("strength_map", "strength_map_z"):
			function(
				identifier,
				(parameter(("input", ), "std_ulogic"), parameter(("strn", ), "strength")),
				self._TypeMark("std_logic")
			)

		for parameterType, returnType in (
			("std_ulogic_vector", "std_logic_vector"),
			("std_logic_vector",  "std_ulogic_vector")
		):
			function("drive", (parameter(("V", ), parameterType), ), self._TypeMark(returnType))

		for parameterType, returnType in (
			("std_ulogic",        "std_logic"),
			("std_ulogic_vector", "std_logic_vector"),
			("std_ulogic_vector", "std_ulogic_vector"),
			("std_logic_vector",  "std_logic_vector"),
			("std_logic_vector",  "std_ulogic_vector")
		):
			function(
				"sense",
				(parameter(("V", ), parameterType), parameter(("vZ", "vU", "vDC"), "std_ulogic")),
				self._TypeMark(returnType)
			)

		# Conversions to bit and bit_vector
		for identifier, parameterType, returnType in (
			("std_logic_vectortobit_vector",  "std_logic_vector",  "bit_vector"),
			("std_ulogic_vectortobit_vector", "std_ulogic_vector", "bit_vector"),
			("std_ulogictobit",               "std_ulogic",        "bit")
		):
			function(identifier, (
				parameter(("V", ), parameterType),
				self._InParameter(("vX", "vZ", "vU", "vDC"), self._TypeMark("bit"), CharacterLiteral("0")),
				self._InParameter(
					("Xflag", "Zflag", "Uflag", "DCflag"),
					self._TypeMark("boolean"),
					SimpleObjectOrFunctionCallSymbol(SimpleName("false"))
				)
			), self._TypeMark(returnType))

		# Reduction functions
		for vectorType in ("std_logic_vector", "std_ulogic_vector"):
			for identifier in ("and_reduce", "nand_reduce", "or_reduce", "nor_reduce", "xor_reduce", "xnor_reduce"):
				function(identifier, (parameter(("ARG", ), vectorType), ), self._TypeMark("ux01"))

		# Functions of the cells
		for identifier in ("fun_buf3s", "fun_buf3sl"):
			function(
				identifier,
				(parameter(("Input", "Enable"), "ux01"), parameter(("Strn", ), "strength")),
				self._TypeMark("std_logic")
			)

		function("fun_mux2x1", (parameter(("Input0", "Input1", "Sel"), "ux01"), ), self._TypeMark("ux01"))
		function("fun_maj23", (parameter(("Input0", "Input1", "Input2"), "ux01"), ), self._TypeMark("ux01"))
		function("fun_wiredx", (parameter(("Input0", "Input1"), "std_ulogic"), ), self._TypeMark("std_logic"))


@export
class Std_Logic_Misc_Body(PredefinedPackageBody):
	"""
	Predefined package body of Synopsys package ``ieee.std_logic_misc``.
	"""
