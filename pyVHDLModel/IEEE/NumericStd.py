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
"""This module contains the predefined package ``ieee.numeric_std`` of VHDL library ``IEEE``."""

from typing                 import Iterable

from pyTooling.Decorators   import export

from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Expression import CharacterLiteral, StringLiteral
from pyVHDLModel.Type       import ArrayType, Subtype
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Function, Operator, Procedure
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Numeric_Std(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_std`` (IEEE Std 1076-2008, 16.8).

	Its declarations, in the order of the package:

	* the constant ``CopyRightNotice``, the types ``unresolved_unsigned`` and ``unresolved_signed``, the subtypes
	  ``u_unsigned``, ``u_signed``, ``unsigned`` and ``signed``
	* the arithmetic operators and ``find_leftmost``/``find_rightmost``
	* the ordering, equality and matching relational operators, ``minimum`` and ``maximum``
	* the shift and rotate functions and operators, ``resize``, the conversion functions ``to_integer``,
	  ``to_unsigned`` and ``to_signed``
	* the logical and logical reduction operators, ``std_match``, ``to_01``, ``to_x01``, ``to_x01z``, ``to_ux01``,
	  ``is_x``, ``to_ostring`` and ``to_hstring``
	* the procedures ``read``, ``write``, ``oread``, ``hread``, ``owrite`` and ``hwrite``

	The aliases of the package (``to_bstring``, ``bread``, ``hex_write``, ...) aren't declared.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.NumericStd.Numeric_Std_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``numeric_std`` package.
		"""
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

		unsignedType = "unresolved_unsigned"
		signedType =   "unresolved_signed"

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

		def arrayOf(parameterItems: Iterable[ParameterConstantInterfaceItem]) -> SimpleSubtypeSymbol:
			"""
			Nested function creating the type mark of the array type of a signature: ``unresolved_signed``, if a parameter is
			signed, else ``unresolved_unsigned``.

			:param parameterItems: The parameters of the signature.
			:returns:              The type mark.
			"""
			for item in parameterItems:
				if item._subtype._name._normalizedIdentifier == signedType:
					return self._TypeMark(signedType)

			return self._TypeMark(unsignedType)

		def procedure(
			identifier:     str,
			parameterItems: Iterable[ParameterConstantInterfaceItem | ParameterVariableInterfaceItem]
		) -> None:
			"""
			Nested function declaring a procedure of this package.

			:param identifier:     The procedure's identifier.
			:param parameterItems: The parameters, in declaration order.
			"""
			self._DeclareSubprogram(Procedure(identifier, parameterItems=parameterItems), self._procedures)

		# Constant and types
		notice = Constant(
			("copyrightnotice", ),
			self._TypeMark("string"),
			StringLiteral("Copyright \u00a9 2008 IEEE. All rights reserved.")
		)
		self._constants[notice._normalizedIdentifiers[0]] = notice
		self.AddDeclaredItem(notice)

		unresolvedUnsigned = ArrayType(unsignedType, (self._TypeMark("natural"), ), self._TypeMark("std_ulogic"))
		unresolvedSigned =   ArrayType(signedType, (self._TypeMark("natural"), ), self._TypeMark("std_ulogic"))
		self._DeclareItem(unresolvedUnsigned, self._types)
		self._DeclareItem(unresolvedSigned, self._types)
		for identifier, baseType in (
			("u_unsigned", unresolvedUnsigned),
			("u_signed",   unresolvedSigned),
			("unsigned",   unresolvedUnsigned),
			("signed",     unresolvedSigned)
		):
			subtype =           Subtype(identifier, self._TypeMark(baseType._identifier))
			subtype._baseType = baseType
			self._DeclareItem(subtype, self._subtypes)

		# Arithmetic operators
		operator("abs", (self._InParameter(("ARG", ), self._TypeMark(signedType)), ), self._TypeMark(signedType))
		operator("-", (self._InParameter(("ARG", ), self._TypeMark(signedType)), ), self._TypeMark(signedType))
		for operatorSymbol, signatures in (
			("+", (
				(unsignedType, unsignedType), (unsignedType, "std_ulogic"), ("std_ulogic", unsignedType),
				(signedType, signedType), (signedType, "std_ulogic"), ("std_ulogic", signedType),
				(unsignedType, "natural"), ("natural", unsignedType), ("integer", signedType), (signedType, "integer")
			)),
			("-", (
				(unsignedType, unsignedType), (unsignedType, "std_ulogic"), ("std_ulogic", unsignedType),
				(signedType, signedType), (signedType, "std_ulogic"), ("std_ulogic", signedType),
				(unsignedType, "natural"), ("natural", unsignedType), (signedType, "integer"), ("integer", signedType)
			))
		):
			for left, right in signatures:
				parameterItems = operands(self._TypeMark(left), self._TypeMark(right))
				operator(operatorSymbol, parameterItems, arrayOf(parameterItems))

		for operatorSymbol in ("*", "/", "rem", "mod"):
			for left, right in (
				(unsignedType, unsignedType), (signedType, signedType), (unsignedType, "natural"), ("natural", unsignedType),
				(signedType, "integer"), ("integer", signedType)
			):
				parameterItems = operands(self._TypeMark(left), self._TypeMark(right))
				operator(operatorSymbol, parameterItems, arrayOf(parameterItems))

		for identifier in ("find_leftmost", "find_rightmost"):
			for typeName in (unsignedType, signedType):
				function(identifier, (
					self._InParameter(("ARG", ), self._TypeMark(typeName)),
					self._InParameter(("Y", ), self._TypeMark("std_ulogic"))
				), self._TypeMark("integer"))

		# Relational operators, minimum and maximum
		relationalSignatures = (
			(unsignedType, unsignedType), (signedType, signedType), ("natural", unsignedType), ("integer", signedType),
			(unsignedType, "natural"), (signedType, "integer")
		)
		for operatorSymbol in (">", "<", "<=", ">=", "=", "/="):
			for left, right in relationalSignatures:
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark("boolean"))

		for identifier in ("minimum", "maximum"):
			for left, right in relationalSignatures:
				parameterItems = operands(self._TypeMark(left), self._TypeMark(right))
				function(identifier, parameterItems, arrayOf(parameterItems))

		for operatorSymbol in ("?>", "?<", "?<=", "?>=", "?=", "?/="):
			for left, right in relationalSignatures:
				operator(
					operatorSymbol,
					operands(self._TypeMark(left), self._TypeMark(right)),
					self._TypeMark("std_ulogic")
				)

		# Shift and rotate functions and operators, resize, conversion functions
		for leftIdentifier, rightIdentifier in (("shift_left", "shift_right"), ("rotate_left", "rotate_right")):
			for typeName in (unsignedType, signedType):
				for identifier in (leftIdentifier, rightIdentifier):
					function(identifier, (
						self._InParameter(("ARG", ), self._TypeMark(typeName)),
						self._InParameter(("COUNT", ), self._TypeMark("natural"))
					), self._TypeMark(typeName))

		for operatorSymbol in ("sll", "srl", "rol", "ror", "sla", "sra"):
			for typeName in (unsignedType, signedType):
				operator(operatorSymbol, (
					self._InParameter(("ARG", ), self._TypeMark(typeName)),
					self._InParameter(("COUNT", ), self._TypeMark("integer"))
				), self._TypeMark(typeName))

		function("resize", (
			self._InParameter(("ARG", ), self._TypeMark(signedType)),
			self._InParameter(("NEW_SIZE", ), self._TypeMark("natural"))
		), self._TypeMark(signedType))
		function("resize", (
			self._InParameter(("ARG", ), self._TypeMark(unsignedType)),
			self._InParameter(("NEW_SIZE", ), self._TypeMark("natural"))
		), self._TypeMark(unsignedType))
		for typeName in (unsignedType, signedType):
			function(
				"resize",
				(self._InParameter(("ARG", "SIZE_RES"), self._TypeMark(typeName)), ),
				self._TypeMark(typeName)
			)

		function(
			"to_integer",
			(self._InParameter(("ARG", ), self._TypeMark(unsignedType)), ),
			self._TypeMark("natural")
		)
		function("to_integer", (self._InParameter(("ARG", ), self._TypeMark(signedType)), ), self._TypeMark("integer"))
		function(
			"to_unsigned",
			(self._InParameter(("ARG", "SIZE"), self._TypeMark("natural")), ),
			self._TypeMark(unsignedType)
		)
		function("to_signed", (
			self._InParameter(("ARG", ), self._TypeMark("integer")),
			self._InParameter(("SIZE", ), self._TypeMark("natural"))
		), self._TypeMark(signedType))
		function("to_unsigned", (
			self._InParameter(("ARG", ), self._TypeMark("natural")),
			self._InParameter(("SIZE_RES", ), self._TypeMark(unsignedType))
		), self._TypeMark(unsignedType))
		function("to_signed", (
			self._InParameter(("ARG", ), self._TypeMark("integer")),
			self._InParameter(("SIZE_RES", ), self._TypeMark(signedType))
		), self._TypeMark(signedType))

		# Logical and logical reduction operators
		for typeName in (unsignedType, signedType):
			operator("not", (self._InParameter(("L", ), self._TypeMark(typeName)), ), self._TypeMark(typeName))
			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				operator(
					operatorSymbol,
					operands(self._TypeMark(typeName), self._TypeMark(typeName)),
					self._TypeMark(typeName)
				)

		for typeName in (unsignedType, signedType):
			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				operator(
					operatorSymbol,
					operands(self._TypeMark("std_ulogic"), self._TypeMark(typeName)),
					self._TypeMark(typeName)
				)
				operator(
					operatorSymbol,
					operands(self._TypeMark(typeName), self._TypeMark("std_ulogic")),
					self._TypeMark(typeName)
				)

		for typeName in (signedType, unsignedType):
			for operatorSymbol in ("and", "nand", "or", "nor", "xor", "xnor"):
				operator(
					operatorSymbol,
					(self._InParameter(("L", ), self._TypeMark(typeName)), ),
					self._TypeMark("std_ulogic")
				)

		# Matching, strength stripping, string conversions
		for typeName in ("std_ulogic", unsignedType, signedType, "std_ulogic_vector"):
			function("std_match", operands(self._TypeMark(typeName), self._TypeMark(typeName)), self._TypeMark("boolean"))

		for typeName in (unsignedType, signedType):
			function("to_01", (
				self._InParameter(("S", ), self._TypeMark(typeName)),
				self._InParameter(("XMAP", ), self._TypeMark("std_ulogic"), CharacterLiteral("0"))
			), self._TypeMark(typeName))

		for identifier in ("to_x01", "to_x01z", "to_ux01"):
			for typeName in (unsignedType, signedType):
				function(identifier, (self._InParameter(("S", ), self._TypeMark(typeName)), ), self._TypeMark(typeName))

		for typeName in (unsignedType, signedType):
			function("is_x", (self._InParameter(("S", ), self._TypeMark(typeName)), ), self._TypeMark("boolean"))

		for identifier in ("to_ostring", "to_hstring"):
			for typeName in (unsignedType, signedType):
				function(identifier, (self._InParameter(("value", ), self._TypeMark(typeName)), ), self._TypeMark("string"))

		# Textio procedures
		for typeName in (unsignedType, signedType):
			procedure("read", (
				self._LineParameter(),
				self._OutParameter(("VALUE", ), self._TypeMark(typeName)),
				self._OutParameter(("GOOD", ), self._TypeMark("boolean"))
			))
			procedure("read", (self._LineParameter(), self._OutParameter(("VALUE", ), self._TypeMark(typeName))))

		for typeName in (unsignedType, signedType):
			procedure("write", (
				self._LineParameter(),
				self._InParameter(("VALUE", ), self._TypeMark(typeName)),
				*self._JustificationParameters()
			))

		for identifier in ("oread", "hread"):
			for typeName in (unsignedType, signedType):
				procedure(identifier, (
					self._LineParameter(),
					self._OutParameter(("VALUE", ), self._TypeMark(typeName)),
					self._OutParameter(("GOOD", ), self._TypeMark("boolean"))
				))

			for typeName in (unsignedType, signedType):
				procedure(identifier, (self._LineParameter(), self._OutParameter(("VALUE", ), self._TypeMark(typeName))))

		for identifier in ("owrite", "hwrite"):
			for typeName in (unsignedType, signedType):
				procedure(identifier, (
					self._LineParameter(),
					self._InParameter(("VALUE", ), self._TypeMark(typeName)),
					*self._JustificationParameters()
				))


@export
class Numeric_Std_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_std``.
	"""
