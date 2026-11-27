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
"""Tests for pyVHDLModel.IEEE.NumericStdUnsigned."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design
from pyVHDLModel.Base        import Mode
from pyVHDLModel.Expression  import StringLiteral
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Subprogram  import Function, Operator
from pyVHDLModel.IEEE        import Numeric_Std_Unsigned


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class NumericStdUnsigneds(Testcase):
	"""Package ``ieee.numeric_std_unsigned`` (IEEE Std 1076-2008, 16.8)."""

	def test_Declarations(self) -> None:
		"""The constant first, then 79 functions; all with the package as parent."""
		numericStdUnsigned = Numeric_Std_Unsigned()
		declarations =       numericStdUnsigned.DeclaredItems

		self.assertIsInstance(declarations[0], Constant)
		self.assertTupleEqual(("copyrightnotice", ), declarations[0].Identifiers)
		self.assertEqual(79, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(80, len(declarations))
		for declaration in declarations:
			self.assertIs(numericStdUnsigned, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		numericStdUnsigned = Numeric_Std_Unsigned()

		self.assertDictEqual(
			{
				"+": 5, "-": 5, "*": 3, "/": 3, "rem": 3, "mod": 3, "find_leftmost": 1, "find_rightmost": 1,
				">": 3, "<": 3, "<=": 3, ">=": 3, "=": 3, "/=": 3, "minimum": 3, "maximum": 3,
				"?>": 3, "?<": 3, "?<=": 3, "?>=": 3, "?=": 3, "?/=": 3,
				"shift_left": 1, "shift_right": 1, "rotate_left": 1, "rotate_right": 1, "sla": 1, "sra": 1,
				"resize": 2, "to_integer": 1, "to_stdlogicvector": 2, "to_stdulogicvector": 2
			},
			{identifier: len(overloads) for identifier, overloads in numericStdUnsigned.Functions.items()}
		)
		self.assertDictEqual({}, numericStdUnsigned.Procedures)

	def test_Operators(self) -> None:
		"""A function with an operator symbol is an :class:`Operator`, the others aren't."""
		numericStdUnsigned = Numeric_Std_Unsigned()

		for identifier in ("+", "mod", ">", "?=", "sla"):
			for function in numericStdUnsigned.Functions[identifier]:
				self.assertIsInstance(function, Operator)

		for identifier in ("find_leftmost", "minimum", "shift_left", "resize", "to_integer", "to_stdlogicvector"):
			for function in numericStdUnsigned.Functions[identifier]:
				self.assertNotIsInstance(function, Operator)

	def test_Constant(self) -> None:
		"""``constant CopyRightNotice : STRING := "Copyright (c) 2008 IEEE. All rights reserved.";``"""
		notice = Numeric_Std_Unsigned().Constants["copyrightnotice"]

		self.assertEqual("string", notice.Subtype.Name.Identifier)
		self.assertIsInstance(notice.DefaultExpression, StringLiteral)
		self.assertEqual("Copyright \u00a9 2008 IEEE. All rights reserved.", notice.DefaultExpression.Value)

	def test_Operands(self) -> None:
		"""``"+" (L, R : STD_ULOGIC_VECTOR)`` has one interface item ``L, R``; ``(L : ...; R : STD_ULOGIC)`` has two."""
		sameType, mixed = Numeric_Std_Unsigned().Functions["+"][0:2]

		self.assertEqual(1, len(sameType.ParameterItems))
		self.assertTupleEqual(("L", "R"), sameType.ParameterItems[0].Identifiers)
		self.assertEqual("std_ulogic_vector", sameType.ReturnType.Name.Identifier)
		self.assertListEqual(
			["std_ulogic_vector", "std_ulogic"],
			[item.Subtype.Name.Identifier for item in mixed.ParameterItems]
		)
		for item in (*sameType.ParameterItems, *mixed.ParameterItems):
			self.assertIsInstance(item, ParameterConstantInterfaceItem)
			self.assertIs(Mode.In, item.Mode)

	def test_Relational(self) -> None:
		"""``">"`` returns ``BOOLEAN``, the matching ``"?>"`` returns ``STD_ULOGIC``."""
		numericStdUnsigned = Numeric_Std_Unsigned()

		for function in numericStdUnsigned.Functions[">"]:
			self.assertEqual("boolean", function.ReturnType.Name.Identifier)

		for function in numericStdUnsigned.Functions["?>"]:
			self.assertEqual("std_ulogic", function.ReturnType.Name.Identifier)

	def test_ToStdLogicVector(self) -> None:
		"""``function To_StdLogicVector (ARG, SIZE : NATURAL) return STD_LOGIC_VECTOR;`` and the ``SIZE_RES`` form."""
		withSize, withSizeRes = Numeric_Std_Unsigned().Functions["to_stdlogicvector"]

		self.assertTupleEqual(("ARG", "SIZE"), withSize.ParameterItems[0].Identifiers)
		self.assertEqual("natural", withSize.ParameterItems[0].Subtype.Name.Identifier)
		self.assertEqual("std_logic_vector", withSize.ReturnType.Name.Identifier)
		self.assertListEqual(
			["natural", "std_ulogic_vector"],
			[item.Subtype.Name.Identifier for item in withSizeRes.ParameterItems]
		)

	def test_Analyze(self) -> None:
		"""Every type mark of the package resolves, e.g. ``STD_ULOGIC_VECTOR`` of ``std_logic_1164``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary()
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		numericStdUnsigned = design.Libraries["ieee"].Packages["numeric_std_unsigned"]
		self.assertIsNotNone(numericStdUnsigned.Functions["+"][1].ParameterItems[1].Subtype.Reference)
		self.assertIsNotNone(numericStdUnsigned.Functions["to_stdlogicvector"][0].ReturnType.Reference)
