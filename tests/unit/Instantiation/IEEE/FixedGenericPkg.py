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
from pyVHDLModel.Expression  import IntegerLiteral
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
		"""The constant, types, aliases and subtypes first, then 77 subprograms; all with the package as parent."""
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
		self.assertEqual(75, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))
		self.assertEqual(84, len(declarations))
		for declaration in declarations:
			self.assertIs(fixedGenericPkg, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		fixedGenericPkg = Fixed_Generic_Pkg()

		self.assertDictEqual(
			{
				"abs": 1, "-": 11, "+": 10, "*": 10, "/": 10, "rem": 10, "mod": 10, "divide": 2, "reciprocal": 2,
				"remainder": 2, "modulo": 2, "scalb": 4, "is_negative": 1
			},
			{identifier: len(overloads) for identifier, overloads in fixedGenericPkg.Functions.items()}
		)
		self.assertDictEqual(
			{"add_carry": 2},
			{identifier: len(overloads) for identifier, overloads in fixedGenericPkg.Procedures.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, the others aren't."""
		fixedGenericPkg = Fixed_Generic_Pkg()

		for identifier in ("abs", "+", "rem", "mod"):
			for function in fixedGenericPkg.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("divide", "reciprocal", "modulo", "scalb", "is_negative"):
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
