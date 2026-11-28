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
"""Tests for pyVHDLModel.IEEE.FloatGenericPkg."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design
from pyVHDLModel.Base        import Direction, Mode
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.DesignUnit  import UseClause
from pyVHDLModel.Expression  import CharacterLiteral, NegationExpression
from pyVHDLModel.Interface   import GenericConstantInterfaceItem, GenericPackageInterfaceItem
from pyVHDLModel.Object      import Constant, DeferredConstant
from pyVHDLModel.Subprogram  import Function, Operator, Procedure
from pyVHDLModel.Symbol      import ConstrainedArraySubtypeSymbol
from pyVHDLModel.Type        import ArrayType, EnumeratedType, Subtype
from pyVHDLModel.IEEE        import Float_Generic_Pkg


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class FloatGenericPkgs(Testcase):
	"""Package ``ieee.float_generic_pkg`` (IEEE Std 1076-2008, 16.11)."""

	def test_Generics(self) -> None:
		"""Seven generic constants with their defaults, then ``package fixed_pkg is new IEEE.fixed_generic_pkg``."""
		generics = Float_Generic_Pkg().GenericItems

		self.assertListEqual(
			[
				"float_exponent_width", "float_fraction_width", "float_round_style", "float_denormalize",
				"float_check_error", "float_guard_bits", "no_warning"
			],
			[generic.Identifiers[0] for generic in generics[:7]]
		)
		for generic in generics[:7]:
			self.assertIsInstance(generic, GenericConstantInterfaceItem)
			self.assertIs(Mode.In, generic.Mode)

		self.assertEqual(8, generics[0].DefaultExpression.Value)
		self.assertEqual(23, generics[1].DefaultExpression.Value)
		self.assertEqual("round_nearest", generics[2].DefaultExpression.Name.Identifier)
		self.assertIsInstance(generics[7], GenericPackageInterfaceItem)
		self.assertEqual("fixed_pkg", generics[7].Identifier)
		self.assertEqual("IEEE.fixed_generic_pkg", str(generics[7].PackageReference.Name))

	def test_Declarations(self) -> None:
		"""The constant, use clause, types, subtypes, aliases, deferred constant, then 231 subprograms and 28 aliases."""
		floatGenericPkg = Float_Generic_Pkg()
		declarations =    floatGenericPkg.DeclaredItems

		self.assertIsInstance(declarations[0], Constant)
		self.assertIsInstance(declarations[1], UseClause)
		self.assertEqual("fixed_pkg.all", str(declarations[1].Symbols[0].Name))
		self.assertIsInstance(declarations[2], ArrayType)
		self.assertListEqual(
			[
				"u_float", "float", "unresolved_float32", "u_float32", "float32", "unresolved_float64", "u_float64",
				"float64", "unresolved_float128", "u_float128", "float128"
			],
			[declaration.Identifier for declaration in declarations[3:14]]
		)
		self.assertIsInstance(declarations[14], EnumeratedType)
		self.assertIsInstance(declarations[15], DeferredConstant)
		self.assertEqual(220, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(11, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))
		self.assertEqual(32, len([declaration for declaration in declarations if isinstance(declaration, Alias)]))
		self.assertEqual(275, len(declarations))
		for declaration in declarations:
			self.assertIs(floatGenericPkg, declaration.Parent)

	def test_Subtypes(self) -> None:
		"""``subtype UNRESOLVED_float32 is UNRESOLVED_float (8 downto -23);`` and ``float32`` of ``float``."""
		subtypes = Float_Generic_Pkg().Subtypes

		self.assertListEqual(
			["float", "unresolved_float32", "float32", "unresolved_float64", "float64", "unresolved_float128", "float128"],
			list(subtypes)
		)
		float32 = subtypes["unresolved_float32"].Type
		self.assertIsInstance(float32, ConstrainedArraySubtypeSymbol)
		self.assertEqual("unresolved_float", float32.Name.Identifier)
		self.assertEqual(8, float32.Constraints[0].LeftBound.Value)
		self.assertIsInstance(float32.Constraints[0].RightBound, NegationExpression)
		self.assertEqual(23, float32.Constraints[0].RightBound.Operand.Value)
		self.assertIs(Direction.DownTo, float32.Constraints[0].Direction)
		self.assertEqual("float", subtypes["float128"].Type.Name.Identifier)
		self.assertEqual(15, subtypes["float128"].Type.Constraints[0].LeftBound.Value)

	def test_Aliases(self) -> None:
		"""``alias U_float32 is UNRESOLVED_float32;``"""
		declarations = Float_Generic_Pkg().DeclaredItems
		aliases =      [item for item in declarations if isinstance(item, Alias) and item.Signature is None]

		self.assertListEqual(["u_float", "u_float32", "u_float64", "u_float128"], [alias.Identifier for alias in aliases])
		self.assertEqual("unresolved_float32", aliases[1].Name.Name.Identifier)

	def test_SubprogramAliases(self) -> None:
		"""``alias BREAD is READ [LINE, UNRESOLVED_float];``: 28 aliases with a signature, after their subprograms."""
		declarations = Float_Generic_Pkg().DeclaredItems
		aliases =      [item for item in declarations if isinstance(item, Alias) and item.Signature is not None]

		self.assertListEqual(
			[
				"to_stdlogicvector", "to_std_logic_vector", "to_stdulogicvector", "to_std_ulogic_vector", "bread", "bread",
				"bwrite", "binary_read", "binary_read", "binary_write", "octal_read", "octal_read", "octal_write", "hex_read",
				"hex_read", "hex_write", "to_bstring", "to_binary_string", "to_hex_string", "to_octal_string",
				"from_bstring", "from_binary_string", "from_octal_string", "from_hex_string", "from_bstring",
				"from_binary_string", "from_octal_string", "from_hex_string"
			],
			[alias.Identifier for alias in aliases]
		)
		self.assertListEqual(
			[
				"to_slv", "to_slv", "to_sulv", "to_sulv", *(["read", "read", "write"] * 2), "oread", "oread", "owrite",
				"hread", "hread", "hwrite", "to_string", "to_string", "to_hstring", "to_ostring",
				*(["from_string", "from_string", "from_ostring", "from_hstring"] * 2)
			],
			[alias.Name.Name.Identifier for alias in aliases]
		)
		self.assertListEqual(
			[
				"[unresolved_float return std_logic_vector]",
				"[unresolved_float return std_logic_vector]",
				"[unresolved_float return std_ulogic_vector]",
				"[unresolved_float return std_ulogic_vector]",
				*([
					"[line, unresolved_float, boolean]",
					"[line, unresolved_float]",
					"[line, unresolved_float, side, width]"
				] * 4),
				*(["[unresolved_float return string]"] * 4),
				*(["[string, natural, natural return unresolved_float]"] * 4),
				*(["[string, unresolved_float return unresolved_float]"] * 4)
			],
			[str(alias.Signature) for alias in aliases]
		)
		for alias in aliases:
			self.assertIsNone(alias.Subtype)
			self.assertIs(alias, alias.Signature.Parent)
			self.assertTrue(alias.IsOverloadable)

	def test_ValidFpstate(self) -> None:
		"""``type valid_fpstate is (nan, quiet_nan, ..., isx);``, the return type of ``classfp``."""
		floatGenericPkg = Float_Generic_Pkg()
		validFpstate =    floatGenericPkg.Types["valid_fpstate"]

		self.assertEqual(11, len(validFpstate.Literals))
		self.assertEqual("nan", validFpstate.Literals[0].Value)
		self.assertEqual("isx", validFpstate.Literals[10].Value)
		self.assertEqual("valid_fpstate", floatGenericPkg.Functions["classfp"][0].ReturnType.Name.Identifier)

	def test_DeferredConstant(self) -> None:
		"""``constant fphdlsynth_or_real : BOOLEAN;``, completed by the package body."""
		floatGenericPkg = Float_Generic_Pkg()
		constant =        floatGenericPkg.DeferredConstants["fphdlsynth_or_real"]

		self.assertEqual("boolean", constant.Subtype.Name.Identifier)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		floatGenericPkg = Float_Generic_Pkg()

		self.assertDictEqual(
			{
				"classfp": 1, "abs": 1, "-": 6, "+": 5, "*": 5, "/": 5, "rem": 5, "mod": 5, "add": 1, "subtract": 1,
				"multiply": 1, "divide": 1, "remainder": 1, "modulo": 1, "reciprocal": 1, "dividebyp2": 1, "mac": 1,
				"sqrt": 1, "is_negative": 1, "eq": 1, "ne": 1, "lt": 1, "gt": 1, "le": 1, "ge": 1,
				"=": 5, "/=": 5, ">=": 5, "<=": 5, ">": 5, "<": 5, "?=": 5, "?/=": 5, "?>": 5, "?>=": 5, "?<": 5, "?<=": 5,
				"std_match": 1, "find_rightmost": 1, "find_leftmost": 1, "maximum": 5, "minimum": 5, "resize": 2,
				"to_float32": 1, "to_float64": 1, "to_float128": 1, "to_slv": 1, "to_sulv": 1, "to_float": 14,
				"to_unsigned": 2, "to_signed": 2, "to_ufixed": 2, "to_sfixed": 2, "to_real": 1, "to_integer": 1,
				"realtobits": 1, "bitstoreal": 1, "to_01": 1, "is_x": 1, "to_x01": 1, "to_x01z": 1, "to_ux01": 1,
				"normalize": 4, "not": 1, "and": 4, "or": 4, "nand": 4, "nor": 4, "xor": 4, "xnor": 4, "copysign": 1,
				"scalb": 2, "logb": 2, "nextafter": 1, "unordered": 1, "finite": 1, "isnan": 1, "zerofp": 2, "nanfp": 2,
				"qnanfp": 2, "pos_inffp": 2, "neg_inffp": 2, "neg_zerofp": 2, "to_string": 1, "to_hstring": 1,
				"to_ostring": 1, "from_string": 2, "from_ostring": 2, "from_hstring": 2
			},
			{identifier: len(overloads) for identifier, overloads in floatGenericPkg.Functions.items()}
		)
		self.assertDictEqual(
			{"break_number": 2, "write": 1, "read": 2, "owrite": 1, "oread": 2, "hwrite": 1, "hread": 2},
			{identifier: len(overloads) for identifier, overloads in floatGenericPkg.Procedures.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, the others aren't."""
		floatGenericPkg = Float_Generic_Pkg()

		for identifier in ("abs", "+", "mod", "=", "?<="):
			for function in floatGenericPkg.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("add", "mac", "eq", "resize", "to_float", "normalize"):
			for function in floatGenericPkg.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_ArithmeticStyles(self) -> None:
		"""``mac (l, r, c : UNRESOLVED_float; round_style, guard, check_error, denormalize)``, defaults the generics."""
		mac = Float_Generic_Pkg().Functions["mac"][0]

		self.assertListEqual(
			[("l", "r", "c"), ("round_style", ), ("guard", ), ("check_error", ), ("denormalize", )],
			[item.Identifiers for item in mac.ParameterItems]
		)
		self.assertListEqual(
			["float_round_style", "float_guard_bits", "float_check_error", "float_denormalize"],
			[item.DefaultExpression.Name.Identifier for item in mac.ParameterItems[1:]]
		)

	def test_ToFloat(self) -> None:
		"""``to_float`` from ``STD_ULOGIC_VECTOR`` first, from ``UNRESOLVED_ufixed`` with ``denormalize``; ``size_res``."""
		conversions = Float_Generic_Pkg().Functions["to_float"]

		self.assertListEqual(
			[
				"std_ulogic_vector", "integer", "real", "unresolved_unsigned", "unresolved_signed", "unresolved_ufixed",
				"unresolved_sfixed", "integer", "real", "unresolved_unsigned", "unresolved_signed", "std_ulogic_vector",
				"unresolved_ufixed", "unresolved_sfixed"
			],
			[function.ParameterItems[0].Subtype.Name.Identifier for function in conversions]
		)
		self.assertListEqual(
			[("arg", ), ("exponent_width", ), ("fraction_width", ), ("round_style", ), ("denormalize", )],
			[item.Identifiers for item in conversions[5].ParameterItems]
		)
		self.assertEqual("size_res", conversions[7].ParameterItems[1].Identifiers[0])

	def test_ToUfixed(self) -> None:
		"""``to_ufixed``'s ``overflow_style`` and ``round_style`` are of the types of ``fixed_float_types``."""
		toUfixed = Float_Generic_Pkg().Functions["to_ufixed"][0]

		self.assertListEqual(
			["unresolved_float", "integer", "integer", "fixed_overflow_style_type", "fixed_round_style_type", "boolean",
			 "boolean"],
			[item.Subtype.Name.Identifier for item in toUfixed.ParameterItems]
		)
		self.assertEqual("fixed_round_style", toUfixed.ParameterItems[4].DefaultExpression.Name.Identifier)
		self.assertEqual("unresolved_ufixed", toUfixed.ReturnType.Name.Identifier)

	def test_Normalize(self) -> None:
		"""``normalize (fract; expon; sign; sticky : STD_ULOGIC := '0'; ...)`` and ``break_number``'s modes."""
		floatGenericPkg = Float_Generic_Pkg()
		normalize =       floatGenericPkg.Functions["normalize"][1]
		breakNumber =     floatGenericPkg.Procedures["break_number"][0]

		self.assertEqual("unresolved_ufixed", normalize.ParameterItems[0].Subtype.Name.Identifier)
		self.assertIsInstance(normalize.ParameterItems[3].DefaultExpression, CharacterLiteral)
		self.assertEqual("nguard", normalize.ParameterItems[8].Identifiers[0])
		self.assertListEqual(
			[Mode.In, Mode.In, Mode.In, Mode.Out, Mode.Out, Mode.Out],
			[item.Mode for item in breakNumber.ParameterItems]
		)

	def test_MixedOperands(self) -> None:
		"""``"+"`` with ``REAL``/``INTEGER`` on either side; ``"?="`` returns ``STD_ULOGIC``; ``maximum`` pairs."""
		floatGenericPkg = Float_Generic_Pkg()

		additions = floatGenericPkg.Functions["+"]
		self.assertListEqual(
			[
				["unresolved_float"], ["unresolved_float", "real"], ["real", "unresolved_float"],
				["unresolved_float", "integer"], ["integer", "unresolved_float"]
			],
			[[item.Subtype.Name.Identifier for item in function.ParameterItems] for function in additions]
		)
		for function in floatGenericPkg.Functions["?="][1:]:
			self.assertEqual("std_ulogic", function.ReturnType.Name.Identifier)

		declarations = floatGenericPkg.DeclaredItems
		maximum =      floatGenericPkg.Functions["maximum"][1]
		self.assertIs(floatGenericPkg.Functions["minimum"][1], declarations[declarations.index(maximum) + 1])

	def test_Logical(self) -> None:
		"""``"and"`` of two values, with a ``STD_ULOGIC`` operand on either side, and as reduction to ``STD_ULOGIC``."""
		operators = Float_Generic_Pkg().Functions["and"]

		self.assertTupleEqual(("l", "r"), operators[0].ParameterItems[0].Identifiers)
		self.assertEqual("std_ulogic", operators[1].ParameterItems[0].Subtype.Name.Identifier)
		self.assertEqual("std_ulogic", operators[2].ParameterItems[1].Subtype.Name.Identifier)
		self.assertEqual(1, len(operators[3].ParameterItems))
		self.assertEqual("std_ulogic", operators[3].ReturnType.Name.Identifier)

	def test_SpecialValues(self) -> None:
		"""``zerofp (exponent_width, fraction_width)`` with the generics as defaults, and ``zerofp (size_res)``."""
		zerofp = Float_Generic_Pkg().Functions["zerofp"]

		self.assertListEqual(
			["float_exponent_width", "float_fraction_width"],
			[item.DefaultExpression.Name.Identifier for item in zerofp[0].ParameterItems]
		)
		self.assertEqual("size_res", zerofp[1].ParameterItems[0].Identifiers[0])

	def test_ReadWrite(self) -> None:
		"""``WRITE (L; VALUE; JUSTIFIED; FIELD)``, ``READ (L; VALUE)`` and with ``GOOD``; ``hread`` too."""
		floatGenericPkg = Float_Generic_Pkg()
		write =           floatGenericPkg.Procedures["write"][0]
		read =            floatGenericPkg.Procedures["hread"][1]

		self.assertListEqual(
			[("L", ), ("VALUE", ), ("JUSTIFIED", ), ("FIELD", )],
			[item.Identifiers for item in write.ParameterItems]
		)
		self.assertListEqual([Mode.InOut, Mode.Out, Mode.Out], [item.Mode for item in read.ParameterItems])

	def test_FromString(self) -> None:
		"""``from_string (bstring : STRING; exponent_width; fraction_width)`` and with ``size_res``."""
		fromString = Float_Generic_Pkg().Functions["from_string"]

		self.assertListEqual(
			[("bstring", ), ("exponent_width", ), ("fraction_width", )],
			[item.Identifiers for item in fromString[0].ParameterItems]
		)
		self.assertEqual("size_res", fromString[1].ParameterItems[1].Identifiers[0])

	def test_Analyze(self) -> None:
		"""``fixed_pkg`` is linked; ``use fixed_pkg.all;`` resolves ``UNRESOLVED_ufixed`` of ``fixed_generic_pkg``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		ieee =            design.Libraries["ieee"]
		floatGenericPkg = ieee.Packages["float_generic_pkg"]
		fixedGenericPkg = ieee.Packages["fixed_generic_pkg"]
		toFloat =         floatGenericPkg.Functions["to_float"][5]
		self.assertIs(fixedGenericPkg, floatGenericPkg.GenericItems[7].PackageReference.Reference)
		self.assertIs(fixedGenericPkg.Types["unresolved_ufixed"], toFloat.ParameterItems[0].Subtype.Reference)
		self.assertIs(floatGenericPkg.Types["valid_fpstate"], floatGenericPkg.Functions["classfp"][0].ReturnType.Reference)

	def test_AnalyzeAliases(self) -> None:
		"""
		The analysis resolves the name of each alias with a signature to the subprogram of the signature's type profile,
		e.g. ``TO_BSTRING [UNRESOLVED_float return STRING]`` to the package's ``to_string``.
		"""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		package = design.Libraries["ieee"].Packages["float_generic_pkg"]
		aliases = [item for item in package.DeclaredItems if isinstance(item, Alias) and item.Signature is not None]
		self.assertEqual(28, len(aliases))
		for alias in aliases:
			self.assertIsNotNone(alias.Name.Reference)
			self.assertEqual(alias.Name.Name.Identifier, alias.Name.Reference.NormalizedDesignator)
			self.assertTrue(alias.Name.Reference.Signature.HasSameTypeProfile(alias.Signature))

		self.assertIs(package.Functions["to_string"][0], aliases[16].Name.Reference)
		self.assertIs(package.Procedures["read"][1], aliases[4].Name.Reference)
