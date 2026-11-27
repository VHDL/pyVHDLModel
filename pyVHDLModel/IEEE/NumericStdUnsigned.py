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
"""This module contains the predefined package ``ieee.numeric_std_unsigned`` of VHDL library ``IEEE``."""

from typing                 import Iterable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Expression import StringLiteral
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Numeric_Std_Unsigned(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_std_unsigned`` (IEEE Std 1076-2008, 16.8).

	It declares the operations of ``numeric_std`` for ``unsigned`` on ``std_ulogic_vector``. Its declarations, in the
	order of the package:

	* the constant ``CopyRightNotice``
	* the arithmetic operators and ``find_leftmost``/``find_rightmost``
	* the ordering, equality and matching relational operators, ``minimum`` and ``maximum``
	* the shift and rotate functions and operators, ``resize`` and the conversion functions ``to_integer``,
	  ``to_stdlogicvector`` and ``to_stdulogicvector``

	The aliases of the package (``to_slv``, ``to_sulv``, ...) aren't declared.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.NumericStdUnsigned.Numeric_Std_Unsigned_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``numeric_std_unsigned`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

		vectorType = "std_ulogic_vector"

		def operands(left: SimpleSubtypeSymbol, right: SimpleSubtypeSymbol) -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the parameters ``L`` and ``R``: one interface item ``L, R`` with the type mark ``left``,
			if both type marks name the same type.

			:param left:  The type mark of parameter ``L``.
			:param right: The type mark of parameter ``R``.
			:returns:     The parameters.
			"""
			if left._name._normalizedIdentifier == right._name._normalizedIdentifier:
				return (self._InParameter(("L", "R"), left), )

			return self._InParameter(("L", ), left), self._InParameter(("R", ), right)

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

		# Constant
		notice = Constant(
			("copyrightnotice", ),
			self._TypeMark("string"),
			StringLiteral("Copyright \u00a9 2008 IEEE. All rights reserved.")
		)
		self._constants[notice._normalizedIdentifiers[0]] = notice
		self.AddDeclaredItem(notice)

		# Arithmetic operators
		for operatorSymbol in ("+", "-"):
			for left, right in (
				(vectorType, vectorType), (vectorType, "std_ulogic"), ("std_ulogic", vectorType), (vectorType, "natural"),
				("natural", vectorType)
			):
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(vectorType))

		for operatorSymbol in ("*", "/", "rem", "mod"):
			for left, right in ((vectorType, vectorType), (vectorType, "natural"), ("natural", vectorType)):
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(vectorType))

		for identifier in ("find_leftmost", "find_rightmost"):
			function(identifier, (
				self._InParameter(("ARG", ), self._TypeMark(vectorType)),
				self._InParameter(("Y", ), self._TypeMark("std_ulogic"))
			), self._TypeMark("integer"))

		# Relational operators, minimum and maximum
		relationalSignatures = ((vectorType, vectorType), ("natural", vectorType), (vectorType, "natural"))
		for operatorSymbol in (">", "<", "<=", ">=", "=", "/="):
			for left, right in relationalSignatures:
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark("boolean"))

		for identifier in ("minimum", "maximum"):
			for left, right in relationalSignatures:
				function(identifier, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(vectorType))

		for operatorSymbol in ("?>", "?<", "?<=", "?>=", "?=", "?/="):
			for left, right in relationalSignatures:
				operator(
					operatorSymbol,
					operands(self._TypeMark(left), self._TypeMark(right)),
					self._TypeMark("std_ulogic")
				)

		# Shift and rotate functions and operators, resize, conversion functions
		for identifier in ("shift_left", "shift_right", "rotate_left", "rotate_right"):
			function(identifier, (
				self._InParameter(("ARG", ), self._TypeMark(vectorType)),
				self._InParameter(("COUNT", ), self._TypeMark("natural"))
			), self._TypeMark(vectorType))

		for operatorSymbol in ("sla", "sra"):
			operator(operatorSymbol, (
				self._InParameter(("ARG", ), self._TypeMark(vectorType)),
				self._InParameter(("COUNT", ), self._TypeMark("integer"))
			), self._TypeMark(vectorType))

		function("resize", (
			self._InParameter(("ARG", ), self._TypeMark(vectorType)),
			self._InParameter(("NEW_SIZE", ), self._TypeMark("natural"))
		), self._TypeMark(vectorType))
		function(
			"resize",
			(self._InParameter(("ARG", "SIZE_RES"), self._TypeMark(vectorType)), ),
			self._TypeMark(vectorType)
		)

		function("to_integer", (self._InParameter(("ARG", ), self._TypeMark(vectorType)), ), self._TypeMark("natural"))
		for identifier, typeName in (
			("to_stdlogicvector",  "std_logic_vector"),
			("to_stdulogicvector", vectorType)
		):
			function(
				identifier,
				(self._InParameter(("ARG", "SIZE"), self._TypeMark("natural")), ),
				self._TypeMark(typeName)
			)
			function(identifier, (
				self._InParameter(("ARG", ), self._TypeMark("natural")),
				self._InParameter(("SIZE_RES", ), self._TypeMark(vectorType))
			), self._TypeMark(typeName))


@export
class Numeric_Std_Unsigned_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_std_unsigned``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``numeric_std_unsigned`` package body.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_std.all", ))
