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
"""This module contains the predefined package ``ieee.float_generic_pkg`` of VHDL library ``IEEE``."""

from typing                  import Iterable

from pyTooling.Decorators    import export

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Base        import Direction, Mode, SimpleRange
from pyVHDLModel.Name        import AllName, SelectedName, SimpleName
from pyVHDLModel.Symbol      import PossibleReference, Symbol, SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol, \
                                    ConstrainedArraySubtypeSymbol, PackageReferenceSymbol, \
                                    AllPackageMembersReferenceSymbol
from pyVHDLModel.Expression  import CharacterLiteral, EnumerationLiteral, IntegerLiteral, NegationExpression, \
                                    StringLiteral
from pyVHDLModel.Type        import ArrayType, EnumeratedType, Subtype
from pyVHDLModel.Object      import Constant, DeferredConstant
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.DesignUnit  import UseClause
from pyVHDLModel.Interface   import GenericConstantInterfaceItem, GenericPackageInterfaceItem, \
                                    ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram  import Function, Operator, Procedure
from pyVHDLModel.Predefined  import PredefinedPackage, PredefinedPackageBody


@export
class Float_Generic_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.float_generic_pkg`` (IEEE Std 1076-2008, 16.11).

	A generic package; ``ieee.float_pkg`` instantiates it. Its declarations, in the order of the package:

	* the generics ``float_exponent_width``, ``float_fraction_width``, ``float_round_style``, ``float_denormalize``,
	  ``float_check_error``, ``float_guard_bits``, ``no_warning`` and the package generic ``fixed_pkg``
	* the constant ``CopyRightNotice``, the use clause ``use fixed_pkg.all;``, the type ``unresolved_float``, the subtypes
	  ``float``, ``unresolved_float32`` ... ``float128`` with their aliases ``u_float`` ..., the type ``valid_fpstate``,
	  the deferred constant ``fphdlsynth_or_real``
	* ``classfp``, the arithmetic operators and functions (``add``, ``divide``, ``mac``, ``sqrt``, ...), ``is_negative``,
	  the comparison functions (``eq``, ...), the relational and matching operators, ``std_match``, ``find_rightmost``,
	  ``find_leftmost``, ``maximum``, ``minimum``
	* ``resize``, the conversion functions (``to_float32`` ..., ``to_slv``, ``to_sulv``, ``to_float``, ``to_unsigned``,
	  ``to_ufixed``, ``to_real``, ``to_integer``, ``realtobits``, ``bitstoreal``), ``to_01``, ``is_x``, ``to_x01``,
	  ``to_x01z``, ``to_ux01``, ``break_number`` and ``normalize``
	* the arithmetic, relational and matching operators, ``maximum`` and ``minimum`` with ``real`` or ``integer``, the
	  logical and logical reduction operators
	* ``copysign``, ``scalb``, ``logb``, ``nextafter``, ``unordered``, ``finite``, ``isnan``, the functions returning
	  special values (``zerofp``, ``nanfp``, ...), the procedures ``write``, ``read``, ``owrite``, ``oread``, ``hwrite``,
	  ``hread``, ``to_string``, ``to_hstring``, ``to_ostring``, ``from_string``, ``from_ostring`` and ``from_hstring``

	The conversion functions ``to_slv`` and ``to_sulv``, the procedures ``read``/``write`` and the string conversions are
	each followed by their aliases (``to_stdlogicvector``, ``bread``, ``to_bstring``, ``from_hex_string``, ...); each
	alias of a subprogram selects an overload by a signature, e.g. ``alias BREAD is READ [LINE, UNRESOLVED_float];``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.FloatGenericPkg.Float_Generic_Pkg_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``float_generic_pkg`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))

		floatType =  "unresolved_float"
		ufixedType = "unresolved_ufixed"
		sfixedType = "unresolved_sfixed"

		def name(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating a name in an expression.

			It names an enumeration literal or a generic, e.g. ``round_nearest`` or ``float_guard_bits``.

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
			Nested function creating the style parameters, whose default values are the package's generics.

			An example is ``round_style`` (default ``float_round_style``) or ``check_error`` (default ``float_check_error``).

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

		def argument(typeName: str = floatType) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating the parameter ``arg``.

			:param typeName: Optional, the name of the parameter's type. Default: ``unresolved_float``.
			:returns:        The parameter.
			"""
			return self._InParameter(("arg", ), self._TypeMark(typeName))

		styleParameters = {
			"round_style":    ("round_type", "float_round_style"),
			"guard":          ("natural",    "float_guard_bits"),
			"nguard":         ("natural",    "float_guard_bits"),
			"check_error":    ("boolean",    "float_check_error"),
			"denormalize":    ("boolean",    "float_denormalize"),
			"denormalize_in": ("boolean",    "float_denormalize"),
			"exponent_width": ("natural",    "float_exponent_width"),
			"fraction_width": ("natural",    "float_fraction_width")
		}
		arithmeticStyles = ("round_style", "guard", "check_error", "denormalize")
		conversionStyles = ("round_style", "check_error", "denormalize_in", "denormalize")

		# Generics
		for identifier, typeName, defaultExpression in (
			("float_exponent_width", "natural",    IntegerLiteral(8)),
			("float_fraction_width", "natural",    IntegerLiteral(23)),
			("float_round_style",    "round_type", name("round_nearest")),
			("float_denormalize",    "boolean",    name("true")),
			("float_check_error",    "boolean",    name("true")),
			("float_guard_bits",     "natural",    IntegerLiteral(3)),
			("no_warning",           "boolean",    name("false"))
		):
			self.AddGenericItem(GenericConstantInterfaceItem(
				(identifier, ),
				Mode.In,
				self._TypeMark(typeName),
				defaultExpression
			))

		self.AddGenericItem(GenericPackageInterfaceItem(
			"fixed_pkg",
			genericPackage=PackageReferenceSymbol(SelectedName("fixed_generic_pkg", SimpleName("IEEE")))
		))

		# Constant, use clause, types, subtypes and aliases, deferred constant
		notice = Constant(
			("copyrightnotice", ),
			self._TypeMark("string"),
			StringLiteral("Copyright \u00a9 2008 IEEE. All rights reserved.")
		)
		self._constants[notice._normalizedIdentifiers[0]] = notice
		self.AddDeclaredItem(notice)

		self.AddDeclaredItem(UseClause([AllPackageMembersReferenceSymbol(AllName(SimpleName("fixed_pkg")))]))

		unresolvedFloat = ArrayType(floatType, (self._TypeMark("integer"), ), self._TypeMark("std_ulogic"))

		def alias(identifier: str, typeName: str) -> None:
			"""
			Nested function declaring an alias of a type or subtype of this package.

			:param identifier: The alias' identifier.
			:param typeName:   The name of the aliased type or subtype.
			"""
			self.AddDeclaredItem(Alias(
				identifier,
				Symbol(SimpleName(typeName), PossibleReference.PackageMember | PossibleReference.EnumLiteral)
			))

		def subtype(identifier: str, typeMark: SimpleSubtypeSymbol | ConstrainedArraySubtypeSymbol) -> None:
			"""
			Nested function declaring a subtype of ``unresolved_float``.

			:param identifier: The subtype's identifier.
			:param typeMark:   The subtype indication.
			"""
			floatSubtype =           Subtype(identifier, typeMark)
			floatSubtype._baseType = unresolvedFloat
			self._DeclareItem(floatSubtype, self._subtypes)

		def constrained(typeName: str, exponentWidth: int, fractionWidth: int) -> ConstrainedArraySubtypeSymbol:
			"""
			Nested function creating the subtype indication ``<typeName> (<exponentWidth> downto -<fractionWidth>)``.

			:param typeName:      The name of the constrained type or subtype.
			:param exponentWidth: The left bound, the width of the exponent.
			:param fractionWidth: The negated right bound, the width of the fraction.
			:returns:             The subtype indication.
			"""
			return ConstrainedArraySubtypeSymbol(SimpleName(typeName), (SimpleRange(
				IntegerLiteral(exponentWidth),
				NegationExpression(IntegerLiteral(fractionWidth)),
				Direction.DownTo
			), ))

		self._DeclareItem(unresolvedFloat, self._types)
		alias("u_float", floatType)
		subtype("float", self._TypeMark(floatType))
		for width, exponentWidth, fractionWidth in ((32, 8, 23), (64, 11, 52), (128, 15, 112)):
			subtype(f"unresolved_float{width}", constrained(floatType, exponentWidth, fractionWidth))
			alias(f"u_float{width}", f"unresolved_float{width}")
			subtype(f"float{width}", constrained("float", exponentWidth, fractionWidth))

		self._DeclareItem(EnumeratedType("valid_fpstate", [EnumerationLiteral(literal) for literal in (
			"nan", "quiet_nan", "neg_inf", "neg_normal", "neg_denormal", "neg_zero", "pos_zero", "pos_denormal",
			"pos_normal", "pos_inf", "isx"
		)]), self._types)

		synthesisFlag = DeferredConstant(("fphdlsynth_or_real", ), self._TypeMark("boolean"))
		self._deferredConstants[synthesisFlag._normalizedIdentifiers[0]] = synthesisFlag
		self.AddDeclaredItem(synthesisFlag)

		# classfp, arithmetic operators and functions
		function(
			"classfp",
			(self._InParameter(("x", ), self._TypeMark(floatType)), *styles("check_error")),
			self._TypeMark("valid_fpstate")
		)
		operator("abs", (argument(), ), self._TypeMark(floatType))
		operator("-", (argument(), ), self._TypeMark(floatType))
		for operatorSymbol in ("+", "-", "*", "/", "rem", "mod"):
			operator(
				operatorSymbol,
				operands(self._TypeMark(floatType), self._TypeMark(floatType)),
				self._TypeMark(floatType)
			)

		for identifier, operandIdentifiers in (
			("add",        ("l", "r")),
			("subtract",   ("l", "r")),
			("multiply",   ("l", "r")),
			("divide",     ("l", "r")),
			("remainder",  ("l", "r")),
			("modulo",     ("l", "r")),
			("reciprocal", ("arg", )),
			("dividebyp2", ("l", "r")),
			("mac",        ("l", "r", "c")),
			("sqrt",       ("arg", ))
		):
			function(identifier, (
				self._InParameter(operandIdentifiers, self._TypeMark(floatType)),
				*styles(*arithmeticStyles)
			), self._TypeMark(floatType))

		function("is_negative", (argument(), ), self._TypeMark("boolean"))

		# Comparison functions, relational operators, std_match, find_rightmost, find_leftmost, maximum, minimum
		for identifier in ("eq", "ne", "lt", "gt", "le", "ge"):
			function(identifier, (
				self._InParameter(("l", "r"), self._TypeMark(floatType)),
				*styles("check_error", "denormalize")
			), self._TypeMark("boolean"))

		for operatorSymbol in ("=", "/=", ">=", "<=", ">", "<"):
			operator(
				operatorSymbol,
				operands(self._TypeMark(floatType), self._TypeMark(floatType)),
				self._TypeMark("boolean")
			)

		for operatorSymbol in ("?=", "?/=", "?>", "?>=", "?<", "?<="):
			operator(
				operatorSymbol,
				operands(self._TypeMark(floatType), self._TypeMark(floatType)),
				self._TypeMark("std_ulogic")
			)

		function("std_match", operands(self._TypeMark(floatType), self._TypeMark(floatType)), self._TypeMark("boolean"))
		for identifier in ("find_rightmost", "find_leftmost"):
			function(
				identifier,
				(argument(), self._InParameter(("y", ), self._TypeMark("std_ulogic"))),
				self._TypeMark("integer")
			)

		for identifier in ("maximum", "minimum"):
			function(identifier, operands(self._TypeMark(floatType), self._TypeMark(floatType)), self._TypeMark(floatType))

		# resize and conversion functions
		function(
			"resize",
			(argument(), *styles("exponent_width", "fraction_width", *conversionStyles)),
			self._TypeMark(floatType)
		)
		function(
			"resize",
			(argument(), self._InParameter(("size_res", ), self._TypeMark(floatType)), *styles(*conversionStyles)),
			self._TypeMark(floatType)
		)
		for width in (32, 64, 128):
			function(f"to_float{width}", (argument(), *styles(*conversionStyles)), self._TypeMark(f"unresolved_float{width}"))

		for identifier, vectorType, aliasIdentifiers in (
			("to_slv",  "std_logic_vector",  ("to_stdlogicvector", "to_std_logic_vector")),
			("to_sulv", "std_ulogic_vector", ("to_stdulogicvector", "to_std_ulogic_vector"))
		):
			function(identifier, (argument(), ), self._TypeMark(vectorType))
			for aliasIdentifier in aliasIdentifiers:
				self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark(floatType), ), self._TypeMark(vectorType))

		for sourceType, styleIdentifiers in (
			("std_ulogic_vector",   ()),
			("integer",             ("round_style", )),
			("real",                ("round_style", "denormalize")),
			("unresolved_unsigned", ("round_style", )),
			("unresolved_signed",   ("round_style", )),
			(ufixedType,            ("round_style", "denormalize")),
			(sfixedType,            ("round_style", "denormalize"))
		):
			function(
				"to_float",
				(argument(sourceType), *styles("exponent_width", "fraction_width", *styleIdentifiers)),
				self._TypeMark(floatType)
			)

		for sourceType, styleIdentifiers in (
			("integer",             ("round_style", )),
			("real",                ("round_style", "denormalize")),
			("unresolved_unsigned", ("round_style", )),
			("unresolved_signed",   ("round_style", )),
			("std_ulogic_vector",   ()),
			(ufixedType,            ("round_style", "denormalize")),
			(sfixedType,            ("round_style", "denormalize"))
		):
			function("to_float", (
				argument(sourceType),
				self._InParameter(("size_res", ), self._TypeMark(floatType)),
				*styles(*styleIdentifiers)
			), self._TypeMark(floatType))

		def fixedStyles() -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the parameters ``overflow_style`` and ``round_style`` of the conversions to fixed-point
			values, whose default values are the generics of ``fixed_pkg``, and ``check_error`` and ``denormalize``.

			:returns: The parameters.
			"""
			return (
				self._InParameter(
					("overflow_style", ),
					self._TypeMark("fixed_overflow_style_type"),
					name("fixed_overflow_style")
				),
				self._InParameter(("round_style", ), self._TypeMark("fixed_round_style_type"), name("fixed_round_style")),
				*styles("check_error", "denormalize")
			)

		for identifier, vectorType in (("to_unsigned", "unresolved_unsigned"), ("to_signed", "unresolved_signed")):
			function(
				identifier,
				(argument(), self._InParameter(("size", ), self._TypeMark("natural")), *styles("round_style", "check_error")),
				self._TypeMark(vectorType)
			)

		for identifier, fixedType in (("to_ufixed", ufixedType), ("to_sfixed", sfixedType)):
			function(identifier, (
				argument(),
				self._InParameter(("left_index", ), self._TypeMark("integer")),
				self._InParameter(("right_index", ), self._TypeMark("integer")),
				*fixedStyles()
			), self._TypeMark(fixedType))

		for identifier, vectorType in (("to_unsigned", "unresolved_unsigned"), ("to_signed", "unresolved_signed")):
			function(identifier, (
				argument(),
				self._InParameter(("size_res", ), self._TypeMark(vectorType)),
				*styles("round_style", "check_error")
			), self._TypeMark(vectorType))

		for identifier, fixedType in (("to_ufixed", ufixedType), ("to_sfixed", sfixedType)):
			function(
				identifier,
				(argument(), self._InParameter(("size_res", ), self._TypeMark(fixedType)), *fixedStyles()),
				self._TypeMark(fixedType)
			)

		function("to_real", (argument(), *styles("check_error", "denormalize")), self._TypeMark("real"))
		function("to_integer", (argument(), *styles("round_style", "check_error")), self._TypeMark("integer"))
		function("realtobits", (argument("real"), ), self._TypeMark("std_ulogic_vector"))
		function("bitstoreal", (argument("std_ulogic_vector"), ), self._TypeMark("real"))

		# to_01, is_x, to_x01, to_x01z, to_ux01, break_number, normalize
		function(
			"to_01",
			(argument(), self._InParameter(("XMAP", ), self._TypeMark("std_logic"), CharacterLiteral("0"))),
			self._TypeMark(floatType)
		)
		function("is_x", (argument(), ), self._TypeMark("boolean"))
		for identifier in ("to_x01", "to_x01z", "to_ux01"):
			function(identifier, (argument(), ), self._TypeMark(floatType))

		for fractionType in ("unresolved_unsigned", ufixedType):
			procedure("break_number", (
				argument(),
				*styles("denormalize", "check_error"),
				self._OutParameter(("fract", ), self._TypeMark(fractionType)),
				self._OutParameter(("expon", ), self._TypeMark("unresolved_signed")),
				self._OutParameter(("sign", ), self._TypeMark("std_ulogic"))
			))

		def normalizeParameters(fractionType: str) -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the parameters ``fract``, ``expon``, ``sign`` and ``sticky`` of ``normalize``.

			:param fractionType: The name of the type of ``fract``.
			:returns:            The parameters.
			"""
			return (
				self._InParameter(("fract", ), self._TypeMark(fractionType)),
				self._InParameter(("expon", ), self._TypeMark("unresolved_signed")),
				self._InParameter(("sign", ), self._TypeMark("std_ulogic")),
				self._InParameter(("sticky", ), self._TypeMark("std_ulogic"), CharacterLiteral("0"))
			)

		for fractionType in ("unresolved_unsigned", ufixedType):
			function("normalize", (
				*normalizeParameters(fractionType),
				*styles("exponent_width", "fraction_width", "round_style", "denormalize", "nguard")
			), self._TypeMark(floatType))

		for fractionType in ("unresolved_unsigned", ufixedType):
			function("normalize", (
				*normalizeParameters(fractionType),
				self._InParameter(("size_res", ), self._TypeMark(floatType)),
				*styles("round_style", "denormalize", "nguard")
			), self._TypeMark(floatType))

		# Arithmetic, relational and matching operators, maximum and minimum with real and integer
		mixedOperands = ((floatType, "real"), ("real", floatType), (floatType, "integer"), ("integer", floatType))
		for operatorSymbol in ("+", "-", "*", "/", "rem", "mod"):
			for left, right in mixedOperands:
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(floatType))

		for left, right in mixedOperands:
			for operatorSymbol in ("=", "/=", ">=", "<=", ">", "<"):
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark("boolean"))

		for left, right in mixedOperands:
			for operatorSymbol in ("?=", "?/=", "?>", "?>=", "?<", "?<="):
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark("std_ulogic"))

		for left, right in mixedOperands:
			for identifier in ("maximum", "minimum"):
				function(identifier, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(floatType))

		# Logical operators and logical reduction operators
		operator("not", (self._InParameter(("l", ), self._TypeMark(floatType)), ), self._TypeMark(floatType))
		for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
			operator(
				operatorSymbol,
				operands(self._TypeMark(floatType), self._TypeMark(floatType)),
				self._TypeMark(floatType)
			)

		for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
			for left, right in (("std_ulogic", floatType), (floatType, "std_ulogic")):
				operator(operatorSymbol, operands(self._TypeMark(left), self._TypeMark(right)), self._TypeMark(floatType))

		for operatorSymbol in ("and", "nand", "or", "nor", "xor", "xnor"):
			operator(
				operatorSymbol,
				(self._InParameter(("l", ), self._TypeMark(floatType)), ),
				self._TypeMark("std_ulogic")
			)

		# copysign, scalb, logb, nextafter, unordered, finite, isnan
		function("copysign", (self._InParameter(("x", "y"), self._TypeMark(floatType)), ), self._TypeMark(floatType))
		for countType in ("integer", "unresolved_signed"):
			function("scalb", (
				self._InParameter(("y", ), self._TypeMark(floatType)),
				self._InParameter(("N", ), self._TypeMark(countType)),
				*styles("round_style", "check_error", "denormalize")
			), self._TypeMark(floatType))

		for returnType in ("integer", "unresolved_signed"):
			function("logb", (self._InParameter(("x", ), self._TypeMark(floatType)), ), self._TypeMark(returnType))

		function("nextafter", (
			self._InParameter(("x", "y"), self._TypeMark(floatType)),
			*styles("check_error", "denormalize")
		), self._TypeMark(floatType))
		function("unordered", (self._InParameter(("x", "y"), self._TypeMark(floatType)), ), self._TypeMark("boolean"))
		for identifier in ("finite", "isnan"):
			function(identifier, (self._InParameter(("x", ), self._TypeMark(floatType)), ), self._TypeMark("boolean"))

		# Special values
		specialValues = ("zerofp", "nanfp", "qnanfp", "pos_inffp", "neg_inffp", "neg_zerofp")
		for identifier in specialValues:
			function(identifier, styles("exponent_width", "fraction_width"), self._TypeMark(floatType))

		for identifier in specialValues:
			function(
				identifier,
				(self._InParameter(("size_res", ), self._TypeMark(floatType)), ),
				self._TypeMark(floatType)
			)

		# Procedures read and write, to_string, from_string, and their aliases
		for writeIdentifier, readIdentifier, aliasIdentifiers in (
			("write",  "read",  (("bread", "bwrite"), ("binary_read", "binary_write"))),
			("owrite", "oread", (("octal_read", "octal_write"), )),
			("hwrite", "hread", (("hex_read", "hex_write"), ))
		):
			procedure(writeIdentifier, (
				self._LineParameter(),
				self._InParameter(("VALUE", ), self._TypeMark(floatType)),
				*self._JustificationParameters()
			))
			procedure(readIdentifier, (self._LineParameter(), self._OutParameter(("VALUE", ), self._TypeMark(floatType))))
			procedure(readIdentifier, (
				self._LineParameter(),
				self._OutParameter(("VALUE", ), self._TypeMark(floatType)),
				self._OutParameter(("GOOD", ), self._TypeMark("boolean"))
			))
			for readAlias, writeAlias in aliasIdentifiers:
				self._DeclareAlias(
					readAlias,
					readIdentifier,
					(self._TypeMark("line"), self._TypeMark(floatType), self._TypeMark("boolean"))
				)
				self._DeclareAlias(readAlias, readIdentifier, (self._TypeMark("line"), self._TypeMark(floatType)))
				self._DeclareAlias(
					writeAlias,
					writeIdentifier,
					(self._TypeMark("line"), self._TypeMark(floatType), self._TypeMark("side"), self._TypeMark("width"))
				)

		for identifier, aliasIdentifiers in (
			("to_string",  ("to_bstring", "to_binary_string")),
			("to_hstring", ("to_hex_string", )),
			("to_ostring", ("to_octal_string", ))
		):
			function(identifier, (self._InParameter(("value", ), self._TypeMark(floatType)), ), self._TypeMark("string"))
			for aliasIdentifier in aliasIdentifiers:
				self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark(floatType), ), self._TypeMark("string"))

		stringConversions = (
			("from_string",  "bstring", ("from_bstring", "from_binary_string")),
			("from_ostring", "ostring", ("from_octal_string", )),
			("from_hstring", "hstring", ("from_hex_string", ))
		)
		for identifier, stringParameter, aliasIdentifiers in stringConversions:
			function(identifier, (
				self._InParameter((stringParameter, ), self._TypeMark("string")),
				*styles("exponent_width", "fraction_width")
			), self._TypeMark(floatType))
			for aliasIdentifier in aliasIdentifiers:
				self._DeclareAlias(
					aliasIdentifier,
					identifier,
					(self._TypeMark("string"), self._TypeMark("natural"), self._TypeMark("natural")),
					self._TypeMark(floatType)
				)

		for identifier, stringParameter, aliasIdentifiers in stringConversions:
			function(identifier, (
				self._InParameter((stringParameter, ), self._TypeMark("string")),
				self._InParameter(("size_res", ), self._TypeMark(floatType))
			), self._TypeMark(floatType))
			for aliasIdentifier in aliasIdentifiers:
				self._DeclareAlias(
					aliasIdentifier,
					identifier,
					(self._TypeMark("string"), self._TypeMark(floatType)),
					self._TypeMark(floatType)
				)


@export
class Float_Generic_Pkg_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.float_generic_pkg``.
	"""
