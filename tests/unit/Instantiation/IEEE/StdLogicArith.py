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
"""Tests for pyVHDLModel.IEEE.StdLogicArithPkg."""
from pyTooling.Testing      import Testcase
from pyTooling.Warning      import WarningCollector

from pyVHDLModel            import Design, IEEEFlavor
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.Symbol     import ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Type       import ArrayType, Subtype
from pyVHDLModel.DesignUnit import UseClause
from pyVHDLModel.IEEE       import Std_Logic_Arith_MentorGraphics, Std_Logic_Arith_Synopsys


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class StdLogicArithSynopsys(Testcase):
	"""Synopsys package ``ieee.std_logic_arith``."""

	def test_Declarations(self) -> None:
		"""The types ``unsigned`` and ``signed``, the subtype ``small_int``, 134 functions; the package is the parent."""
		stdLogicArith = Std_Logic_Arith_Synopsys()
		declarations =  stdLogicArith.DeclaredItems

		self.assertEqual("std_logic_arith", stdLogicArith.NormalizedIdentifier)
		self.assertIsInstance(declarations[0], ArrayType)
		self.assertIsInstance(declarations[1], ArrayType)
		self.assertIsInstance(declarations[2], Subtype)
		self.assertEqual(134, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(137, len(declarations))
		for declaration in declarations:
			self.assertIs(stdLogicArith, declaration.Parent)

	def test_Types(self) -> None:
		"""``type UNSIGNED is array (NATURAL range <>) of STD_LOGIC;`` and ``subtype SMALL_INT is INTEGER range 0 to 1;``"""
		stdLogicArith = Std_Logic_Arith_Synopsys()
		unsigned =      stdLogicArith.Types["unsigned"]
		smallInt =      stdLogicArith.Subtypes["small_int"]

		self.assertEqual("natural", unsigned.Dimensions[0].Name.Identifier)
		self.assertEqual("std_logic", unsigned.ElementType.Name.Identifier)
		self.assertIsInstance(smallInt.Type, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("integer", smallInt.Type.Name.Identifier)
		self.assertEqual(1, smallInt.Type.Constraint.RightBound.Value)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{
				"+": 28, "-": 26, "abs": 2, "*": 8, "<": 8, "<=": 8, ">": 8, ">=": 8, "=": 8, "/=": 8, "shl": 2, "shr": 2,
				"conv_integer": 4, "conv_unsigned": 4, "conv_signed": 4, "conv_std_logic_vector": 4, "ext": 1, "sxt": 1
			},
			{identifier: len(overloads) for identifier, overloads in Std_Logic_Arith_Synopsys().Functions.items()}
		)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, ``shl`` ... ``sxt`` aren't."""
		stdLogicArith = Std_Logic_Arith_Synopsys()

		for identifier in ("+", "abs", "*", "/="):
			for function in stdLogicArith.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("shl", "conv_integer", "conv_std_logic_vector", "ext"):
			for function in stdLogicArith.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_ResultTypes(self) -> None:
		"""``"+"(L: UNSIGNED; R: UNSIGNED)`` returns ``UNSIGNED``, the 13th overload ``STD_LOGIC_VECTOR``."""
		additions = Std_Logic_Arith_Synopsys().Functions["+"]

		self.assertListEqual(
			[["unsigned", "unsigned"], ["unsigned", "unsigned"]],
			[[item.Subtype.Name.Identifier for item in additions[index].ParameterItems] for index in (0, 12)]
		)
		self.assertEqual("unsigned", additions[0].ReturnType.Name.Identifier)
		self.assertEqual("std_logic_vector", additions[12].ReturnType.Name.Identifier)
		self.assertEqual("std_logic_vector", additions[27].ReturnType.Name.Identifier)

	def test_Unary(self) -> None:
		"""The unary ``"+"``, ``"-"``, ``"ABS"`` return ``UNSIGNED``/``SIGNED``, then ``STD_LOGIC_VECTOR``."""
		absolute = Std_Logic_Arith_Synopsys().Functions["abs"]

		self.assertListEqual(["signed", "std_logic_vector"], [function.ReturnType.Name.Identifier for function in absolute])
		self.assertEqual(1, len(absolute[0].ParameterItems))

	def test_Conversions(self) -> None:
		"""``CONV_INTEGER(ARG: STD_ULOGIC) return SMALL_INT``, ``CONV_UNSIGNED(ARG: INTEGER; SIZE: INTEGER)``."""
		stdLogicArith = Std_Logic_Arith_Synopsys()

		self.assertEqual("small_int", stdLogicArith.Functions["conv_integer"][3].ReturnType.Name.Identifier)
		self.assertListEqual(
			[("ARG", ), ("SIZE", )],
			[item.Identifiers for item in stdLogicArith.Functions["conv_unsigned"][0].ParameterItems]
		)

	def test_Analyze(self) -> None:
		"""With the Synopsys flavor, every type mark resolves, e.g. ``SMALL_INT``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.Synopsys)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		stdLogicArith = design.Libraries["ieee"].Packages["std_logic_arith"]
		self.assertIsInstance(stdLogicArith, Std_Logic_Arith_Synopsys)
		self.assertIs(stdLogicArith.Subtypes["small_int"], stdLogicArith.Functions["conv_integer"][3].ReturnType.Reference)


class StdLogicArithMentorGraphics(Testcase):
	"""Mentor Graphics package ``ieee.std_logic_arith``."""

	def test_Declarations(self) -> None:
		"""The use clause, the types ``signed`` and ``unsigned``, then 139 functions; the package is the parent."""
		stdLogicArith = Std_Logic_Arith_MentorGraphics()
		declarations =  stdLogicArith.DeclaredItems

		self.assertEqual("std_logic_arith", stdLogicArith.NormalizedIdentifier)
		self.assertIsInstance(declarations[0], UseClause)
		self.assertEqual("ieee.std_logic_1164.all", str(declarations[0].Symbols[0].Name))
		self.assertListEqual(["signed", "unsigned"], [declaration.Identifier for declaration in declarations[1:3]])
		self.assertEqual(139, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(142, len(declarations))
		for declaration in declarations:
			self.assertIs(stdLogicArith, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		self.assertDictEqual(
			{
				"std_ulogic_wired_or": 1, "std_ulogic_wired_and": 1, "to_integer": 5, "conv_integer": 5, "to_stdlogic": 1,
				"to_stdlogicvector": 1, "to_stdulogicvector": 1, "to_unsigned": 1, "conv_unsigned": 1, "to_signed": 1,
				"conv_signed": 1, "zero_extend": 4, "sign_extend": 1, "+": 9, "-": 6, "*": 4, "abs": 1, "/": 4, "mod": 3,
				"rem": 3, "**": 3, "sla": 4, "sra": 4, "sll": 4, "srl": 4, "rol": 4, "ror": 4, "eq": 5, "=": 2, "ne": 5,
				"/=": 2, "lt": 5, "<": 2, "gt": 5, ">": 2, "le": 5, "<=": 2, "ge": 5, ">=": 2, "and": 2, "nand": 2,
				"or": 2, "nor": 2, "xor": 2, "not": 2, "xnor": 4
			},
			{identifier: len(overloads) for identifier, overloads in Std_Logic_Arith_MentorGraphics().Functions.items()}
		)

	def test_ToInteger(self) -> None:
		"""``to_integer ( arg1 : STD_LOGIC; x : INTEGER := 0 ) RETURN NATURAL``"""
		toInteger = Std_Logic_Arith_MentorGraphics().Functions["to_integer"][2]

		self.assertListEqual([("arg1", ), ("x", )], [item.Identifiers for item in toInteger.ParameterItems])
		self.assertEqual(0, toInteger.ParameterItems[1].DefaultExpression.Value)
		self.assertEqual("natural", toInteger.ReturnType.Name.Identifier)

	def test_Arithmetic(self) -> None:
		"""``"+" ( arg1, arg2 : STD_LOGIC )`` - one interface item - and the unary ``"+"``; ``"/" ( l, r : SIGNED )``."""
		stdLogicArith = Std_Logic_Arith_MentorGraphics()
		additions =     stdLogicArith.Functions["+"]

		self.assertTupleEqual(("arg1", "arg2"), additions[0].ParameterItems[0].Identifiers)
		self.assertEqual("std_logic", additions[0].ReturnType.Name.Identifier)
		self.assertEqual(1, len(additions[5].ParameterItems))
		self.assertTupleEqual(("l", "r"), stdLogicArith.Functions["/"][3].ParameterItems[0].Identifiers)

	def test_Comparisons(self) -> None:
		"""``eq ( l, r : STD_LOGIC ) RETURN BOOLEAN`` of five types, then ``"="`` of ``UNSIGNED`` and ``SIGNED``."""
		stdLogicArith = Std_Logic_Arith_MentorGraphics()

		self.assertListEqual(
			["std_logic", "std_ulogic_vector", "std_logic_vector", "unsigned", "signed"],
			[function.ParameterItems[0].Subtype.Name.Identifier for function in stdLogicArith.Functions["eq"]]
		)
		self.assertNotIsInstance(stdLogicArith.Functions["eq"][0], Operator)
		self.assertIsInstance(stdLogicArith.Functions["="][0], Operator)

	def test_Analyze(self) -> None:
		"""With the Mentor Graphics flavor, the use clause in the package makes ``std_logic`` visible."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.MentorGraphics)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		stdLogicArith = design.Libraries["ieee"].Packages["std_logic_arith"]
		stdLogic1164 =  design.Libraries["ieee"].Packages["std_logic_1164"]
		self.assertIsInstance(stdLogicArith, Std_Logic_Arith_MentorGraphics)
		self.assertIs(stdLogic1164.Subtypes["std_logic"], stdLogicArith.Functions["+"][0].ReturnType.Reference)

