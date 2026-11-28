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
"""This module contains the predefined package ``ieee.numeric_bit`` of VHDL library ``IEEE``."""

from typing                  import Iterable

from pyTooling.Decorators    import export

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Name        import SelectedName, SimpleName
from pyVHDLModel.Symbol      import PossibleReference, Symbol, SimpleSubtypeSymbol
from pyVHDLModel.Expression  import StringLiteral
from pyVHDLModel.Type        import ArrayType
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.Subprogram  import Function, Operator, Procedure, SubprogramSignature
from pyVHDLModel.Predefined  import PredefinedPackage, PredefinedPackageBody


@export
class Numeric_Bit(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_bit`` (IEEE Std 1076-2008, 16.8).

	Its declarations, in the order of the package:

	* the constant ``CopyRightNotice``, the types ``unsigned`` and ``signed``, arrays of ``bit``
	* the arithmetic operators and ``find_leftmost``/``find_rightmost``
	* the ordering, equality and matching relational operators, ``minimum`` and ``maximum``
	* the shift and rotate functions and operators, ``resize``, the conversion functions ``to_integer``,
	  ``to_unsigned`` and ``to_signed``
	* the logical and logical reduction operators, the aliases ``rising_edge`` and ``falling_edge`` of the functions of
	  ``std.standard.bit``
	* the string conversions ``to_ostring`` and ``to_hstring`` and their aliases (``to_bstring``, ``to_binary_string``,
	  ``to_octal_string``, ``to_hex_string``)
	* the procedures ``read``, ``write``, ``oread``, ``hread``, ``owrite`` and ``hwrite`` and their aliases (``bread``,
	  ``binary_read``, ``octal_read``, ``hex_read``, ``bwrite``, ``binary_write``, ``octal_write``, ``hex_write``)

	Each alias selects an overload by a signature, e.g. ``alias BREAD is READ [LINE, UNSIGNED];``. ``to_bstring`` and
	``to_binary_string`` alias the implicit ``to_string`` of ``unsigned`` and ``signed``; ``rising_edge`` aliases
	``STD.STANDARD.RISING_EDGE [STD.STANDARD.BIT return STD.STANDARD.BOOLEAN]``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.NumericBit.Numeric_Bit_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``numeric_bit`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("STD.TEXTIO.all", ))

		unsignedType = "unsigned"
		signedType =   "signed"

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
			Nested function creating the type mark of the array type of a signature: ``signed``, if a parameter is signed,
			else ``unsigned``.

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

		def standard(identifier: str) -> SelectedName:
			"""
			Nested function creating the expanded name ``std.standard.<identifier>``.

			:param identifier: The identifier of the declaration of package ``std.standard``.
			:returns:          The expanded name.
			"""
			return SelectedName(identifier, SelectedName("standard", SimpleName("std")))

		# Constant and types
		notice = Constant(
			("copyrightnotice", ),
			self._TypeMark("string"),
			StringLiteral("Copyright \u00a9 2008 IEEE. All rights reserved.")
		)
		self._constants[notice._normalizedIdentifiers[0]] = notice
		self.AddDeclaredItem(notice)

		unsigned = ArrayType(unsignedType, (self._TypeMark("natural"), ), self._TypeMark("bit"))
		signed =   ArrayType(signedType, (self._TypeMark("natural"), ), self._TypeMark("bit"))
		self._DeclareItem(unsigned, self._types)
		self._DeclareItem(signed, self._types)

		# Arithmetic operators
		operator("abs", (self._InParameter(("ARG", ), self._TypeMark(signedType)), ), self._TypeMark(signedType))
		operator("-", (self._InParameter(("ARG", ), self._TypeMark(signedType)), ), self._TypeMark(signedType))
		for operatorSymbol, signatures in (
			("+", (
				(unsignedType, unsignedType), (unsignedType, "bit"), ("bit", unsignedType),
				(signedType, signedType), (signedType, "bit"), ("bit", signedType),
				(unsignedType, "natural"), ("natural", unsignedType), ("integer", signedType), (signedType, "integer")
			)),
			("-", (
				(unsignedType, unsignedType), (unsignedType, "bit"), ("bit", unsignedType),
				(signedType, signedType), (signedType, "bit"), ("bit", signedType),
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
					self._InParameter(("Y", ), self._TypeMark("bit"))
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
					self._TypeMark("bit")
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
					operands(self._TypeMark("bit"), self._TypeMark(typeName)),
					self._TypeMark(typeName)
				)
				operator(
					operatorSymbol,
					operands(self._TypeMark(typeName), self._TypeMark("bit")),
					self._TypeMark(typeName)
				)

		for typeName in (signedType, unsignedType):
			for operatorSymbol in ("and", "nand", "or", "nor", "xor", "xnor"):
				operator(
					operatorSymbol,
					(self._InParameter(("L", ), self._TypeMark(typeName)), ),
					self._TypeMark("bit")
				)

		for identifier in ("rising_edge", "falling_edge"):
			self.AddDeclaredItem(Alias(
				identifier,
				Symbol(standard(identifier), PossibleReference.PackageMember | PossibleReference.EnumLiteral),
				signature=SubprogramSignature(
					(SimpleSubtypeSymbol(standard("bit")), ),
					SimpleSubtypeSymbol(standard("boolean"))
				)
			))

		# String conversions
		for identifier in ("to_bstring", "to_binary_string"):
			for typeName in (unsignedType, signedType):
				self._DeclareAlias(identifier, "to_string", (self._TypeMark(typeName), ), self._TypeMark("string"))

		for identifier, aliasIdentifier in (
			("to_ostring", "to_octal_string"),
			("to_hstring", "to_hex_string")
		):
			for typeName in (unsignedType, signedType):
				function(identifier, (self._InParameter(("value", ), self._TypeMark(typeName)), ), self._TypeMark("string"))

			for typeName in (unsignedType, signedType):
				self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark(typeName), ), self._TypeMark("string"))

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

		for identifier in ("bread", "binary_read"):
			for typeName in (unsignedType, signedType):
				self._DeclareAlias(
					identifier,
					"read",
					(self._TypeMark("line"), self._TypeMark(typeName), self._TypeMark("boolean"))
				)

			for typeName in (unsignedType, signedType):
				self._DeclareAlias(identifier, "read", (self._TypeMark("line"), self._TypeMark(typeName)))

		for identifier, aliasIdentifier in (
			("oread", "octal_read"),
			("hread", "hex_read")
		):
			for typeName in (unsignedType, signedType):
				procedure(identifier, (
					self._LineParameter(),
					self._OutParameter(("VALUE", ), self._TypeMark(typeName)),
					self._OutParameter(("GOOD", ), self._TypeMark("boolean"))
				))

			for typeName in (unsignedType, signedType):
				procedure(identifier, (self._LineParameter(), self._OutParameter(("VALUE", ), self._TypeMark(typeName))))

			for typeName in (unsignedType, signedType):
				self._DeclareAlias(
					aliasIdentifier,
					identifier,
					(self._TypeMark("line"), self._TypeMark(typeName), self._TypeMark("boolean"))
				)

			for typeName in (unsignedType, signedType):
				self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark("line"), self._TypeMark(typeName)))

		for identifier in ("bwrite", "binary_write"):
			for typeName in (unsignedType, signedType):
				self._DeclareAlias(
					identifier,
					"write",
					(self._TypeMark("line"), self._TypeMark(typeName), self._TypeMark("side"), self._TypeMark("width"))
				)

		for identifier, aliasIdentifier in (
			("owrite", "octal_write"),
			("hwrite", "hex_write")
		):
			for typeName in (unsignedType, signedType):
				procedure(identifier, (
					self._LineParameter(),
					self._InParameter(("VALUE", ), self._TypeMark(typeName)),
					*self._JustificationParameters()
				))

			for typeName in (unsignedType, signedType):
				self._DeclareAlias(
					aliasIdentifier,
					identifier,
					(self._TypeMark("line"), self._TypeMark(typeName), self._TypeMark("side"), self._TypeMark("width"))
				)


@export
class Numeric_Bit_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_bit``.
	"""
