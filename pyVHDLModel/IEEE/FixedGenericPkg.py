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
"""This module contains the predefined package ``ieee.fixed_generic_pkg`` of VHDL library ``IEEE``."""

from typing                  import Iterable

from pyTooling.Decorators    import export

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Base        import Mode
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import PossibleReference, Symbol, SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression  import IntegerLiteral, StringLiteral
from pyVHDLModel.Type        import ArrayType, Subtype
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.Interface   import GenericConstantInterfaceItem, ParameterConstantInterfaceItem, \
                                    ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram  import Function, Operator, Procedure
from pyVHDLModel.Predefined  import PredefinedPackage, PredefinedPackageBody


@export
class Fixed_Generic_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.fixed_generic_pkg`` (IEEE Std 1076-2008, 16.10).

	A generic package; ``ieee.fixed_pkg`` instantiates it. Its declarations, in the order of the package:

	* the generics ``fixed_round_style``, ``fixed_overflow_style``, ``fixed_guard_bits`` and ``no_warning``
	* the constant ``CopyRightNotice``, the types ``unresolved_ufixed`` and ``unresolved_sfixed``, the aliases
	  ``u_ufixed`` and ``u_sfixed``, the subtypes ``ufixed`` and ``sfixed``
	* the arithmetic operators, ``divide``, ``reciprocal``, ``remainder``, ``modulo``, ``add_carry``, ``scalb`` and
	  ``is_negative``
	* the ordering, equality and matching relational operators, ``std_match``, ``maximum`` and ``minimum``, of two
	  fixed-point values and of a fixed-point value with ``natural`` or ``real`` (``ufixed``), ``integer`` or ``real``
	  (``sfixed``)
	* the shift and rotate operators, ``shift_left`` and ``shift_right``, the logical operators and the logical reduction
	  operators

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.FixedGenericPkg.Fixed_Generic_Pkg_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``fixed_generic_pkg`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))

		ufixedType = "unresolved_ufixed"
		sfixedType = "unresolved_sfixed"

		def name(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating a name in an expression.

			It names an enumeration literal or a generic, e.g. ``fixed_round`` or ``fixed_guard_bits``.

			:param identifier: The identifier.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		def operands(left: SimpleSubtypeSymbol, right: SimpleSubtypeSymbol) -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the parameters ``l`` and ``r``: one interface item ``l, r`` with the type mark ``left``,
			if both type marks name the same type.

			:param left:  The type mark of parameter ``l``.
			:param right: The type mark of parameter ``r``.
			:returns:     The parameters.
			"""
			if left._name._normalizedIdentifier == right._name._normalizedIdentifier:
				return (self._InParameter(("l", "r"), left), )

			return self._InParameter(("l", ), left), self._InParameter(("r", ), right)

		def styles(*identifiers: str) -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the style parameters, whose default values are the package's generics: ``overflow_style``
			(default ``fixed_overflow_style``), ``round_style`` (default ``fixed_round_style``) and ``guard_bits`` (default
			``fixed_guard_bits``).

			:param identifiers: The identifiers of the style parameters, in declaration order.
			:returns:           The parameters.
			"""
			parameters = []
			for identifier in identifiers:
				typeName, generic = styleParameters[identifier]
				parameters.append(self._InParameter((identifier, ), self._TypeMark(typeName), name(generic)))

			return tuple(parameters)

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

		styleParameters = {
			"overflow_style": ("fixed_overflow_style_type", "fixed_overflow_style"),
			"round_style":    ("fixed_round_style_type",    "fixed_round_style"),
			"guard_bits":     ("natural",                   "fixed_guard_bits")
		}

		# Generics
		for identifier, typeName, defaultExpression in (
			("fixed_round_style",    "fixed_round_style_type",    name("fixed_round")),
			("fixed_overflow_style", "fixed_overflow_style_type", name("fixed_saturate")),
			("fixed_guard_bits",     "natural",                   IntegerLiteral(3)),
			("no_warning",           "boolean",                   name("false"))
		):
			self.AddGenericItem(GenericConstantInterfaceItem(
				(identifier, ),
				Mode.In,
				self._TypeMark(typeName),
				defaultExpression
			))

		# Constant, types, aliases and subtypes
		notice = Constant(
			("copyrightnotice", ),
			self._TypeMark("string"),
			StringLiteral("Copyright © 2008 IEEE. All rights reserved.")
		)
		self._constants[notice._normalizedIdentifiers[0]] = notice
		self.AddDeclaredItem(notice)

		unresolvedUfixed = ArrayType(ufixedType, (self._TypeMark("integer"), ), self._TypeMark("std_ulogic"))
		unresolvedSfixed = ArrayType(sfixedType, (self._TypeMark("integer"), ), self._TypeMark("std_ulogic"))
		self._DeclareItem(unresolvedUfixed, self._types)
		self._DeclareItem(unresolvedSfixed, self._types)
		for identifier, typeName in (("u_ufixed", ufixedType), ("u_sfixed", sfixedType)):
			self.AddDeclaredItem(Alias(
				identifier,
				Symbol(SimpleName(typeName), PossibleReference.PackageMember | PossibleReference.EnumLiteral)
			))

		for identifier, baseType in (("ufixed", unresolvedUfixed), ("sfixed", unresolvedSfixed)):
			subtype =           Subtype(identifier, self._TypeMark(baseType._identifier))
			subtype._baseType = baseType
			self._DeclareItem(subtype, self._subtypes)

		# Arithmetic operators
		operator("abs", (self._InParameter(("arg", ), self._TypeMark(sfixedType)), ), self._TypeMark(sfixedType))
		operator("-", (self._InParameter(("arg", ), self._TypeMark(sfixedType)), ), self._TypeMark(sfixedType))
		for operatorSymbol in ("+", "-", "*", "/", "rem", "mod"):
			for fixedType in (ufixedType, sfixedType):
				operator(
					operatorSymbol,
					operands(self._TypeMark(fixedType), self._TypeMark(fixedType)),
					self._TypeMark(fixedType)
				)

		for fixedType, integerType in ((ufixedType, "natural"), (sfixedType, "integer")):
			for operatorSymbol in ("+", "-", "*", "/", "rem", "mod"):
				for left, right in (
					(fixedType, "real"), ("real", fixedType), (fixedType, integerType), (integerType, fixedType)
				):
					operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(fixedType))

		# divide, reciprocal, remainder, modulo, add_carry, scalb, is_negative
		for identifier, fixedType, operandIdentifiers, styleIdentifiers in (
			("divide",     ufixedType, ("l", "r"), ("round_style", "guard_bits")),
			("divide",     sfixedType, ("l", "r"), ("round_style", "guard_bits")),
			("reciprocal", ufixedType, ("arg", ),  ("round_style", "guard_bits")),
			("reciprocal", sfixedType, ("arg", ),  ("round_style", "guard_bits")),
			("remainder",  ufixedType, ("l", "r"), ("round_style", "guard_bits")),
			("remainder",  sfixedType, ("l", "r"), ("round_style", "guard_bits")),
			("modulo",     ufixedType, ("l", "r"), ("round_style", "guard_bits")),
			("modulo",     sfixedType, ("l", "r"), ("overflow_style", "round_style", "guard_bits"))
		):
			function(identifier, (
				self._InParameter(operandIdentifiers, self._TypeMark(fixedType)),
				*styles(*styleIdentifiers)
			), self._TypeMark(fixedType))

		for fixedType in (ufixedType, sfixedType):
			procedure("add_carry", (
				self._InParameter(("L", "R"), self._TypeMark(fixedType)),
				self._InParameter(("c_in", ), self._TypeMark("std_ulogic")),
				self._OutParameter(("result", ), self._TypeMark(fixedType)),
				self._OutParameter(("c_out", ), self._TypeMark("std_ulogic"))
			))

		for fixedType in (ufixedType, sfixedType):
			for countType in ("integer", "unresolved_signed"):
				function("scalb", (
					self._InParameter(("y", ), self._TypeMark(fixedType)),
					self._InParameter(("N", ), self._TypeMark(countType))
				), self._TypeMark(fixedType))

		function("is_negative", (self._InParameter(("arg", ), self._TypeMark(sfixedType)), ), self._TypeMark("boolean"))

		# Relational operators, std_match, maximum and minimum
		for operatorSymbol in (">", "<", "<=", ">=", "=", "/="):
			for fixedType in (ufixedType, sfixedType):
				operator(
					operatorSymbol,
					operands(self._TypeMark(fixedType), self._TypeMark(fixedType)),
					self._TypeMark("boolean")
				)

		for fixedType in (ufixedType, sfixedType):
			for operatorSymbol in ("?=", "?/=", "?>", "?>=", "?<", "?<="):
				operator(
					operatorSymbol,
					operands(self._TypeMark(fixedType), self._TypeMark(fixedType)),
					self._TypeMark("std_ulogic")
				)

		for fixedType in (ufixedType, sfixedType):
			function("std_match", operands(self._TypeMark(fixedType), self._TypeMark(fixedType)), self._TypeMark("boolean"))

		for fixedType in (ufixedType, sfixedType):
			for identifier in ("maximum", "minimum"):
				function(identifier, operands(self._TypeMark(fixedType), self._TypeMark(fixedType)), self._TypeMark(fixedType))

		sideBySide = (("maximum", 0), ("minimum", 0), ("maximum", 1), ("minimum", 1))
		nameByName = (("maximum", 0), ("maximum", 1), ("minimum", 0), ("minimum", 1))
		for fixedType, otherType, minimumMaximum in (
			(ufixedType, "natural", sideBySide),
			(ufixedType, "real",    nameByName),
			(sfixedType, "integer", nameByName),
			(sfixedType, "real",    nameByName)
		):
			sides = ((fixedType, otherType), (otherType, fixedType))
			for left, right in sides:
				for operatorSymbol in ("=", "/=", ">=", "<=", ">", "<"):
					operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark("boolean"))

			for left, right in sides:
				for operatorSymbol in ("?=", "?/=", "?>=", "?<=", "?>", "?<"):
					operator(
						operatorSymbol,
						operands(self._TypeMark(left), self._TypeMark(right)),
						self._TypeMark("std_ulogic")
					)

			for identifier, side in minimumMaximum:
				left, right = sides[side]
				function(identifier, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(fixedType))

		# Shift and rotate operators, shift_left, shift_right
		for fixedType in (ufixedType, sfixedType):
			for operatorSymbol in ("sll", "srl", "rol", "ror", "sla", "sra"):
				operator(operatorSymbol, (
					self._InParameter(("ARG", ), self._TypeMark(fixedType)),
					self._InParameter(("COUNT", ), self._TypeMark("integer"))
				), self._TypeMark(fixedType))

		for fixedType in (ufixedType, sfixedType):
			for identifier in ("shift_left", "shift_right"):
				function(identifier, (
					self._InParameter(("ARG", ), self._TypeMark(fixedType)),
					self._InParameter(("COUNT", ), self._TypeMark("natural"))
				), self._TypeMark(fixedType))

		# Logical operators and logical reduction operators
		for fixedType in (ufixedType, sfixedType):
			operator("not", (self._InParameter(("l", ), self._TypeMark(fixedType)), ), self._TypeMark(fixedType))
			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				operator(
					operatorSymbol,
					operands(self._TypeMark(fixedType), self._TypeMark(fixedType)),
					self._TypeMark(fixedType)
				)

		for fixedType in (ufixedType, sfixedType):
			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				for left, right in (("std_ulogic", fixedType), (fixedType, "std_ulogic")):
					operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(fixedType))

		for fixedType in (ufixedType, sfixedType):
			for operatorSymbol in ("and", "nand", "or", "nor", "xor", "xnor"):
				operator(
					operatorSymbol,
					(self._InParameter(("l", ), self._TypeMark(fixedType)), ),
					self._TypeMark("std_ulogic")
				)


@export
class Fixed_Generic_Pkg_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.fixed_generic_pkg``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``fixed_generic_pkg`` package body.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.MATH_REAL.all", ))
