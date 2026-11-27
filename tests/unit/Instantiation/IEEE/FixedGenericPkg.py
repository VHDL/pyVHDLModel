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
"""Tests for pyVHDLModel.IEEE.NumericBitUnsigned."""
from pyTooling.Testing       import Testcase
"""Tests for pyVHDLModel.IEEE.FixedGenericPkg."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design
from pyVHDLModel.Base        import Mode
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.Expression  import CharacterLiteral, IntegerLiteral
from pyVHDLModel.Interface   import GenericConstantInterfaceItem
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Subprogram  import Function, Operator, Procedure
from pyVHDLModel.Type        import ArrayType, Subtype
from pyVHDLModel.IEEE        import Fixed_Generic_Pkg


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class FixedGenericPkgs(Testcase):
	"""Package ``ieee.fixed_generic_pkg`` (IEEE Std 1076-2008, 16.10)."""

	def test_Generics(self) -> None:
		"""``fixed_round_style``, ``fixed_overflow_style``, ``fixed_guard_bits`` and ``no_warning`` with their defaults."""
		generics = Fixed_Generic_Pkg().GenericItems

		self.assertListEqual(
			["fixed_round_style", "fixed_overflow_style", "fixed_guard_bits", "no_warning"],
			[generic.Identifiers[0] for generic in generics]
		)
		self.assertListEqual(
			["fixed_round_style_type", "fixed_overflow_style_type", "natural", "boolean"],
			[generic.Subtype.Name.Identifier for generic in generics]
		)
		for generic in generics:
			self.assertIsInstance(generic, GenericConstantInterfaceItem)
			self.assertIs(Mode.In, generic.Mode)

		self.assertEqual("fixed_round", generics[0].DefaultExpression.Name.Identifier)
		self.assertEqual("fixed_saturate", generics[1].DefaultExpression.Name.Identifier)
		self.assertIsInstance(generics[2].DefaultExpression, IntegerLiteral)
		self.assertEqual(3, generics[2].DefaultExpression.Value)
		self.assertEqual("false", generics[3].DefaultExpression.Name.Identifier)

	def test_Declarations(self) -> None:
		"""The constant, types, aliases and subtypes first, then 394 subprograms; all with the package as parent."""
		fixedGenericPkg = Fixed_Generic_Pkg()
		declarations =    fixedGenericPkg.DeclaredItems

		self.assertIsInstance(declarations[0], Constant)
		for declaration in declarations[1:3]:
			self.assertIsInstance(declaration, ArrayType)

		for declaration in declarations[3:5]:
			self.assertIsInstance(declaration, Alias)

		for declaration in declarations[5:7]:
			self.assertIsInstance(declaration, Subtype)

		self.assertListEqual(
			["unresolved_ufixed", "unresolved_sfixed", "u_ufixed", "u_sfixed", "ufixed", "sfixed"],
			[declaration.Identifier for declaration in declarations[1:7]]
		)
		self.assertEqual(374, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(20, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))
		self.assertEqual(401, len(declarations))
		for declaration in declarations:
			self.assertIs(fixedGenericPkg, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		fixedGenericPkg = Fixed_Generic_Pkg()

		self.assertDictEqual(
			{
				"abs": 1, "-": 11, "+": 10, "*": 10, "/": 10, "rem": 10, "mod": 10, "divide": 2, "reciprocal": 2,
				"remainder": 2, "modulo": 2, "scalb": 4, "is_negative": 1,
				">": 10, "<": 10, "<=": 10, ">=": 10, "=": 10, "/=": 10,
				"?=": 10, "?/=": 10, "?>": 10, "?>=": 10, "?<": 10, "?<=": 10, "std_match": 2, "maximum": 10, "minimum": 10,
				"sll": 2, "srl": 2, "rol": 2, "ror": 2, "sla": 2, "sra": 2, "shift_left": 2, "shift_right": 2,
				"not": 2, "and": 8, "or": 8, "nand": 8, "nor": 8, "xor": 8, "xnor": 8,
				"find_leftmost": 2, "find_rightmost": 2, "resize": 4, "to_ufixed": 9, "to_unsigned": 2, "to_real": 2,
				"to_integer": 2, "to_sfixed": 10, "to_signed": 2, "ufixed_high": 2, "ufixed_low": 2, "sfixed_high": 2,
				"sfixed_low": 2, "saturate": 4, "to_01": 2, "is_x": 2, "to_x01": 2, "to_x01z": 2, "to_ux01": 2, "to_slv": 2,
				"to_sulv": 2, "to_ufix": 1, "to_sfix": 1, "ufix_high": 1, "ufix_low": 1, "sfix_high": 1, "sfix_low": 1,
				"to_string": 2, "to_ostring": 2, "to_hstring": 2, "from_string": 6, "from_ostring": 6, "from_hstring": 6
			},
			{identifier: len(overloads) for identifier, overloads in fixedGenericPkg.Functions.items()}
		)
		self.assertDictEqual(
			{"add_carry": 2, "write": 2, "read": 4, "owrite": 2, "oread": 4, "hwrite": 2, "hread": 4},
			{identifier: len(overloads) for identifier, overloads in fixedGenericPkg.Procedures.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, the others aren't."""
		fixedGenericPkg = Fixed_Generic_Pkg()

		for identifier in ("abs", "+", "rem", "mod", ">", "?=", "sll", "not", "xnor"):
			for function in fixedGenericPkg.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("divide", "reciprocal", "modulo", "scalb", "is_negative", "std_match", "maximum", "shift_left"):
			for function in fixedGenericPkg.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_Subtypes(self) -> None:
		"""``subtype ufixed is (resolved) UNRESOLVED_ufixed;`` and ``sfixed``: their base types are the array types."""
		fixedGenericPkg = Fixed_Generic_Pkg()

		self.assertIs(fixedGenericPkg.Types["unresolved_ufixed"], fixedGenericPkg.Subtypes["ufixed"].BaseType)
		self.assertIs(fixedGenericPkg.Types["unresolved_sfixed"], fixedGenericPkg.Subtypes["sfixed"].BaseType)
		self.assertEqual("integer", fixedGenericPkg.Types["unresolved_ufixed"].Dimensions[0].Name.Identifier)
		self.assertEqual("std_ulogic", fixedGenericPkg.Types["unresolved_ufixed"].ElementType.Name.Identifier)

	def test_MixedOperands(self) -> None:
		"""``"+" (l : UNRESOLVED_ufixed; r : NATURAL)`` and ``"+" (l : INTEGER; r : UNRESOLVED_sfixed)``."""
		additions = Fixed_Generic_Pkg().Functions["+"]

		self.assertListEqual(
			["unresolved_ufixed", "natural"],
			[item.Subtype.Name.Identifier for item in additions[4].ParameterItems]
		)
		self.assertListEqual(
			["integer", "unresolved_sfixed"],
			[item.Subtype.Name.Identifier for item in additions[9].ParameterItems]
		)

	def test_StyleParameters(self) -> None:
		"""``divide`` has ``round_style`` and ``guard_bits``; ``modulo`` of ``sfixed`` also ``overflow_style``."""
		fixedGenericPkg = Fixed_Generic_Pkg()
		divide =          fixedGenericPkg.Functions["divide"][0]
		modulo =          fixedGenericPkg.Functions["modulo"][1]

		self.assertListEqual(
			[("l", "r"), ("round_style", ), ("guard_bits", )],
			[item.Identifiers for item in divide.ParameterItems]
		)
		self.assertListEqual(
			["fixed_round_style", "fixed_guard_bits"],
			[item.DefaultExpression.Name.Identifier for item in divide.ParameterItems[1:]]
		)
		self.assertListEqual(
			["overflow_style", "round_style", "guard_bits"],
			[item.Identifiers[0] for item in modulo.ParameterItems[1:]]
		)
		self.assertEqual("unresolved_sfixed", modulo.ReturnType.Name.Identifier)

	def test_AddCarry(self) -> None:
		"""``procedure add_carry (L, R : in UNRESOLVED_ufixed; c_in : in STD_ULOGIC; result, c_out : out ...)``."""
		addCarry = Fixed_Generic_Pkg().Procedures["add_carry"][0]

		self.assertListEqual(
			[("L", "R"), ("c_in", ), ("result", ), ("c_out", )],
			[item.Identifiers for item in addCarry.ParameterItems]
		)
		self.assertListEqual(
			[Mode.In, Mode.In, Mode.Out, Mode.Out],
			[item.Mode for item in addCarry.ParameterItems]
		)

	def test_Relational(self) -> None:
		"""``">"`` returns ``BOOLEAN``, ``"?>"`` returns ``STD_ULOGIC``; both also with ``NATURAL`` or ``REAL``."""
		fixedGenericPkg = Fixed_Generic_Pkg()

		for function in fixedGenericPkg.Functions[">"]:
			self.assertEqual("boolean", function.ReturnType.Name.Identifier)

		for function in fixedGenericPkg.Functions["?>"]:
			self.assertEqual("std_ulogic", function.ReturnType.Name.Identifier)

		equalities = fixedGenericPkg.Functions["="]
		self.assertListEqual(
			[
				["unresolved_ufixed"], ["unresolved_sfixed"],
				["unresolved_ufixed", "natural"], ["natural", "unresolved_ufixed"],
				["unresolved_ufixed", "real"], ["real", "unresolved_ufixed"],
				["unresolved_sfixed", "integer"], ["integer", "unresolved_sfixed"],
				["unresolved_sfixed", "real"], ["real", "unresolved_sfixed"]
			],
			[[item.Subtype.Name.Identifier for item in function.ParameterItems] for function in equalities]
		)

	def test_MaximumMinimum(self) -> None:
		"""With ``NATURAL``, ``maximum`` and ``minimum`` alternate; with ``REAL``, the two ``maximum`` come first."""
		declarations = Fixed_Generic_Pkg().DeclaredItems
		functions =    [(index, item) for index, item in enumerate(declarations) if isinstance(item, Function)]
		maximum =      [index for index, function in functions if function.Identifier == "maximum"]
		minimum =      [index for index, function in functions if function.Identifier == "minimum"]

		self.assertEqual(minimum[2] - 1, maximum[2])
		self.assertEqual(maximum[3] - 1, minimum[2])
		self.assertEqual(maximum[5] - 1, maximum[4])
		self.assertEqual(
			["real", "unresolved_ufixed"],
			[item.Subtype.Name.Identifier for item in declarations[maximum[5]].ParameterItems]
		)

	def test_Shift(self) -> None:
		"""``"sll" (ARG : UNRESOLVED_ufixed; COUNT : INTEGER)``; ``shift_left`` with ``COUNT : NATURAL``."""
		fixedGenericPkg = Fixed_Generic_Pkg()
		operator =        fixedGenericPkg.Functions["sll"][1]
		function =        fixedGenericPkg.Functions["shift_left"][0]

		self.assertListEqual(["ARG", "COUNT"], [item.Identifiers[0] for item in operator.ParameterItems])
		self.assertListEqual(
			["unresolved_sfixed", "integer"],
			[item.Subtype.Name.Identifier for item in operator.ParameterItems]
		)
		self.assertEqual("natural", function.ParameterItems[1].Subtype.Name.Identifier)

	def test_Logical(self) -> None:
		"""``"and"`` of two values, with a ``STD_ULOGIC`` operand on either side, and as reduction to ``STD_ULOGIC``."""
		operators = Fixed_Generic_Pkg().Functions["and"]

		self.assertTupleEqual(("l", "r"), operators[0].ParameterItems[0].Identifiers)
		self.assertListEqual(
			["std_ulogic", "unresolved_ufixed"],
			[item.Subtype.Name.Identifier for item in operators[2].ParameterItems]
		)
		self.assertListEqual(
			["unresolved_ufixed", "std_ulogic"],
			[item.Subtype.Name.Identifier for item in operators[3].ParameterItems]
		)
		self.assertEqual(1, len(operators[6].ParameterItems))
		self.assertEqual("std_ulogic", operators[6].ReturnType.Name.Identifier)

	def test_Conversions(self) -> None:
		"""``to_ufixed`` from ``NATURAL``: ``right_index : INTEGER := 0``; from ``REAL``: no default, ``guard_bits``."""
		conversions = Fixed_Generic_Pkg().Functions["to_ufixed"]

		self.assertListEqual(
			[("arg", ), ("left_index", ), ("right_index", ), ("overflow_style", ), ("round_style", )],
			[item.Identifiers for item in conversions[0].ParameterItems]
		)
		self.assertIsInstance(conversions[0].ParameterItems[2].DefaultExpression, IntegerLiteral)
		self.assertEqual(0, conversions[0].ParameterItems[2].DefaultExpression.Value)
		self.assertEqual("real", conversions[2].ParameterItems[0].Subtype.Name.Identifier)
		self.assertIsNone(conversions[2].ParameterItems[2].DefaultExpression)
		self.assertEqual("guard_bits", conversions[2].ParameterItems[5].Identifiers[0])
		self.assertEqual("unresolved_unsigned", conversions[6].ParameterItems[0].Subtype.Name.Identifier)
		self.assertEqual(1, len(conversions[6].ParameterItems))

	def test_IndexRange(self) -> None:
		"""``ufixed_high (left_index, right_index : INTEGER; operation : CHARACTER := 'X'; left_index2, ...)``."""
		high = Fixed_Generic_Pkg().Functions["ufixed_high"][0]

		self.assertListEqual(
			[("left_index", "right_index"), ("operation", ), ("left_index2", "right_index2")],
			[item.Identifiers for item in high.ParameterItems]
		)
		self.assertIsInstance(high.ParameterItems[1].DefaultExpression, CharacterLiteral)
		self.assertEqual("X", high.ParameterItems[1].DefaultExpression.Value)
		self.assertEqual(0, high.ParameterItems[2].DefaultExpression.Value)

	def test_ReadWrite(self) -> None:
		"""``WRITE (L : inout LINE; VALUE : in ...; JUSTIFIED : in SIDE := right; FIELD : in WIDTH := 0)``, ``READ``."""
		fixedGenericPkg = Fixed_Generic_Pkg()
		write =           fixedGenericPkg.Procedures["write"][0]
		read =            fixedGenericPkg.Procedures["read"][1]

		self.assertListEqual(
			[("L", ), ("VALUE", ), ("JUSTIFIED", ), ("FIELD", )],
			[item.Identifiers for item in write.ParameterItems]
		)
		self.assertListEqual([Mode.InOut, Mode.In, Mode.In, Mode.In], [item.Mode for item in write.ParameterItems])
		self.assertListEqual([Mode.InOut, Mode.Out, Mode.Out], [item.Mode for item in read.ParameterItems])
		self.assertEqual("boolean", read.ParameterItems[2].Subtype.Name.Identifier)

	def test_FromString(self) -> None:
		"""``from_string (bstring : STRING; left_index, right_index)``, with ``size_res`` and alone; ``from_hstring``."""
		fixedGenericPkg = Fixed_Generic_Pkg()
		fromString =      fixedGenericPkg.Functions["from_string"]

		self.assertListEqual([3, 3, 2, 2, 1, 1], [len(function.ParameterItems) for function in fromString])
		self.assertEqual("bstring", fromString[0].ParameterItems[0].Identifiers[0])
		self.assertEqual("hstring", fixedGenericPkg.Functions["from_hstring"][0].ParameterItems[0].Identifiers[0])
		self.assertEqual("unresolved_sfixed", fromString[5].ReturnType.Name.Identifier)

	def test_Analyze(self) -> None:
		"""Every type mark resolves, e.g. ``UNRESOLVED_SIGNED`` of ``numeric_std``; ``u_ufixed`` names its type."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		fixedGenericPkg = design.Libraries["ieee"].Packages["fixed_generic_pkg"]
		numericStd =      design.Libraries["ieee"].Packages["numeric_std"]
		scalb =           fixedGenericPkg.Functions["scalb"][1]
		self.assertIs(numericStd.Types["unresolved_signed"], scalb.ParameterItems[1].Subtype.Reference)
		self.assertIs(fixedGenericPkg.Types["unresolved_ufixed"], fixedGenericPkg.DeclaredItems[3].Name.Reference)
		self.assertIsNotNone(fixedGenericPkg.GenericItems[0].Subtype.Reference)
