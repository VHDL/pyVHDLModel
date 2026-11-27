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
"""Tests for pyVHDLModel.IEEE.NumericBit."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design
from pyVHDLModel.Base        import Mode
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.Expression  import IntegerLiteral, StringLiteral
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Subprogram  import Function, Operator, Procedure
from pyVHDLModel.Symbol      import SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Type        import ArrayType
from pyVHDLModel.IEEE        import Numeric_Bit


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class NumericBits(Testcase):
	"""Package ``ieee.numeric_bit`` (IEEE Std 1076-2008, 16.8)."""

	def test_Declarations(self) -> None:
		"""The constant and types first, then 218 functions, 18 procedures and 34 aliases."""
		numericBit =   Numeric_Bit()
		declarations = numericBit.DeclaredItems

		self.assertIsInstance(declarations[0], Constant)
		self.assertTupleEqual(("copyrightnotice", ), declarations[0].Identifiers)
		self.assertListEqual(["unsigned", "signed"], [declaration.Identifier for declaration in declarations[1:3]])
		self.assertEqual(218, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(18, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))
		self.assertEqual(34, len([declaration for declaration in declarations if isinstance(declaration, Alias)]))
		self.assertEqual(273, len(declarations))
		for declaration in declarations:
			self.assertIs(numericBit, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		numericBit = Numeric_Bit()

		self.assertDictEqual(
			{
				"abs": 1, "-": 11, "+": 10, "*": 6, "/": 6, "rem": 6, "mod": 6, "find_leftmost": 2, "find_rightmost": 2,
				">": 6, "<": 6, "<=": 6, ">=": 6, "=": 6, "/=": 6, "minimum": 6, "maximum": 6,
				"?>": 6, "?<": 6, "?<=": 6, "?>=": 6, "?=": 6, "?/=": 6,
				"shift_left": 2, "shift_right": 2, "rotate_left": 2, "rotate_right": 2,
				"sll": 2, "srl": 2, "rol": 2, "ror": 2, "sla": 2, "sra": 2,
				"resize": 4, "to_integer": 2, "to_unsigned": 2, "to_signed": 2,
				"not": 2, "and": 8, "or": 8, "nand": 8, "nor": 8, "xor": 8, "xnor": 8,
				"to_ostring": 2, "to_hstring": 2
			},
			{identifier: len(overloads) for identifier, overloads in numericBit.Functions.items()}
		)
		self.assertDictEqual(
			{"read": 4, "write": 2, "oread": 4, "hread": 4, "owrite": 2, "hwrite": 2},
			{identifier: len(overloads) for identifier, overloads in numericBit.Procedures.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, the others aren't."""
		numericBit = Numeric_Bit()

		for identifier in ("abs", "+", "?=", "sll", "and", "not"):
			for function in numericBit.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("minimum", "shift_left", "resize", "to_integer", "to_hstring"):
			for function in numericBit.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_Constant(self) -> None:
		"""``constant CopyRightNotice : STRING := "Copyright (c) 2008 IEEE. All rights reserved.";``"""
		notice = Numeric_Bit().Constants["copyrightnotice"]

		self.assertEqual("string", notice.Subtype.Name.Identifier)
		self.assertIsInstance(notice.DefaultExpression, StringLiteral)
		self.assertEqual("Copyright \u00a9 2008 IEEE. All rights reserved.", notice.DefaultExpression.Value)

	def test_Types(self) -> None:
		"""``type UNSIGNED is array (NATURAL range <>) of BIT;``, also ``SIGNED``."""
		numericBit = Numeric_Bit()
		for identifier in ("unsigned", "signed"):
			arrayType = numericBit.Types[identifier]
			self.assertIsInstance(arrayType, ArrayType)
			self.assertEqual("bit", arrayType.ElementType.Name.Identifier)

	def test_Operands(self) -> None:
		"""``"+" (L, R : UNSIGNED)`` has one interface item ``L, R``; ``(L : UNSIGNED; R : BIT)`` has two."""
		sameType, mixed = Numeric_Bit().Functions["+"][0:2]

		self.assertEqual(1, len(sameType.ParameterItems))
		self.assertTupleEqual(("L", "R"), sameType.ParameterItems[0].Identifiers)
		self.assertEqual("unsigned", sameType.ReturnType.Name.Identifier)
		self.assertListEqual(["unsigned", "bit"], [item.Subtype.Name.Identifier for item in mixed.ParameterItems])
		for item in (*sameType.ParameterItems, *mixed.ParameterItems):
			self.assertIsInstance(item, ParameterConstantInterfaceItem)
			self.assertIs(Mode.In, item.Mode)

	def test_ToInteger(self) -> None:
		"""``TO_INTEGER`` of unsigned returns ``NATURAL``, of signed ``INTEGER``."""
		unsignedArgument, signedArgument = Numeric_Bit().Functions["to_integer"]

		self.assertEqual("natural", unsignedArgument.ReturnType.Name.Identifier)
		self.assertEqual("integer", signedArgument.ReturnType.Name.Identifier)

	def test_Read(self) -> None:
		"""``procedure READ (L : inout LINE; VALUE : out UNSIGNED; GOOD : out BOOLEAN);``"""
		read = Numeric_Bit().Procedures["read"][0]
		line, value, good = read.ParameterItems

		for item in read.ParameterItems:
			self.assertIsInstance(item, ParameterVariableInterfaceItem)

		self.assertIs(Mode.InOut, line.Mode)
		self.assertIs(Mode.Out, value.Mode)
		self.assertIs(Mode.Out, good.Mode)
		self.assertListEqual(
			["line", "unsigned", "boolean"],
			[item.Subtype.Name.Identifier for item in read.ParameterItems]
		)

	def test_Write(self) -> None:
		"""``procedure WRITE (...; JUSTIFIED : in SIDE := right; FIELD : in WIDTH := 0);``"""
		write = Numeric_Bit().Procedures["write"][0]
		justified, field = write.ParameterItems[2:]

		self.assertIsInstance(justified.DefaultExpression, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("right", justified.DefaultExpression.Name.Identifier)
		self.assertIsInstance(field.DefaultExpression, IntegerLiteral)
		self.assertEqual(0, field.DefaultExpression.Value)

	def test_Analyze(self) -> None:
		"""Every type mark of the package resolves, e.g. ``BIT`` of ``std.standard`` and ``LINE`` of ``textio``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		numericBit = design.Libraries["ieee"].Packages["numeric_bit"]
		self.assertIsNotNone(numericBit.Functions["+"][1].ParameterItems[1].Subtype.Reference)
		self.assertIsNotNone(numericBit.Procedures["read"][0].ParameterItems[0].Subtype.Reference)

	def test_Aliases(self) -> None:
		"""``alias BREAD is READ [LINE, UNSIGNED, BOOLEAN];``: 34 aliases with a signature."""
		aliases = [declaration for declaration in Numeric_Bit().DeclaredItems if isinstance(declaration, Alias)]

		self.assertListEqual(
			[
				"rising_edge", "falling_edge", *(["to_bstring"] * 2), *(["to_binary_string"] * 2),
				*(["to_octal_string"] * 2), *(["to_hex_string"] * 2), *(["bread"] * 4), *(["binary_read"] * 4),
				*(["octal_read"] * 4), *(["hex_read"] * 4), *(["bwrite"] * 2), *(["binary_write"] * 2), *(["octal_write"] * 2),
				*(["hex_write"] * 2)
			],
			[alias.Identifier for alias in aliases]
		)
		self.assertListEqual(
			[
				"rising_edge", "falling_edge", *(["to_string"] * 4), *(["to_ostring"] * 2), *(["to_hstring"] * 2),
				*(["read"] * 8), *(["oread"] * 4), *(["hread"] * 4), *(["write"] * 4), *(["owrite"] * 2), *(["hwrite"] * 2)
			],
			[alias.Name.Name.Identifier for alias in aliases]
		)
		self.assertListEqual(
			[
				*(["[std.standard.bit return std.standard.boolean]"] * 2),
				*(["[unsigned return string]", "[signed return string]"] * 4),
				*([
					"[line, unsigned, boolean]",
					"[line, signed, boolean]",
					"[line, unsigned]",
					"[line, signed]"
				] * 4),
				*(["[line, unsigned, side, width]", "[line, signed, side, width]"] * 4)
			],
			[str(alias.Signature) for alias in aliases]
		)
		for alias in aliases:
			self.assertIsNone(alias.Subtype)
			self.assertIs(alias, alias.Signature.Parent)
			self.assertTrue(alias.IsOverloadable)

	def test_AnalyzeAliases(self) -> None:
		"""
		The analysis resolves the name of each alias to the subprogram of the signature's type profile, e.g.
		``TO_BSTRING [UNSIGNED return STRING]`` to the implicit ``TO_STRING`` of ``UNSIGNED``, ``RISING_EDGE`` to the
		implicit ``RISING_EDGE`` of ``STD.STANDARD.BIT``.
		"""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		numericBit = design.Libraries["ieee"].Packages["numeric_bit"]
		aliases =    [declaration for declaration in numericBit.DeclaredItems if isinstance(declaration, Alias)]
		self.assertEqual(34, len(aliases))
		for alias in aliases:
			self.assertIsNotNone(alias.Name.Reference)
			self.assertEqual(alias.Name.Name.Identifier, alias.Name.Reference.NormalizedDesignator)
			self.assertTrue(alias.Name.Reference.Signature.HasSameTypeProfile(alias.Signature))

		self.assertIs(design.Libraries["std"].Packages["standard"].Types["bit"], aliases[0].Name.Reference.Parent)
		self.assertIs(numericBit.Types["unsigned"], aliases[2].Name.Reference.Parent)
		self.assertIs(numericBit.Procedures["read"][3], aliases[13].Name.Reference)
