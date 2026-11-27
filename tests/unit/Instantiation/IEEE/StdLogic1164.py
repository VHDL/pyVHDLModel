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
"""Tests for pyVHDLModel.IEEE.StdLogic1164."""
from pyTooling.Testing              import Testcase

from pyVHDLModel.Base               import Direction, Mode
from pyVHDLModel.DesignUnit         import Entity, LibraryClause
from pyVHDLModel.Expression         import CharacterLiteral
from pyVHDLModel.Interface          import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                           ParameterSimpleSignalInterfaceItem
from pyVHDLModel.Name               import SimpleName
from pyVHDLModel.Subprogram         import Procedure, Function, Operator
from pyVHDLModel.Symbol             import ConstrainedScalarSubtypeSymbol, LibraryReferenceSymbol
from pyVHDLModel.Type               import ArrayType, Subtype
from pyVHDLModel.IEEE.StdLogic1164  import Std_Logic_1164, StdULogic

from tests.unit.Visibility          import _design, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class StdLogic1164s(Testcase):
	"""Package ``ieee.std_logic_1164`` (IEEE Std 1076-2008, 16.7)."""

	def test_Declarations(self) -> None:
		"""The types and subtypes in the order of the standard, each declaration with the package as parent."""
		package = Std_Logic_1164()

		self.assertListEqual(
			["std_ulogic", "std_ulogic_vector", "resolved", "std_logic", "std_logic_vector", "x01", "x01z", "ux01", "ux01z"],
			[declaration.Identifier for declaration in package.DeclaredItems[:9]]
		)
		for declaration in package.DeclaredItems:
			self.assertIs(package, declaration.Parent)

	def test_Overloads(self) -> None:
		"""The number of overloads per designator."""
		package = Std_Logic_1164()

		self.assertDictEqual(
			{
				"resolved": 1, "and": 5, "nand": 5, "or": 5, "nor": 5, "xor": 5, "xnor": 5, "not": 2,
				"sll": 1, "srl": 1, "rol": 1, "ror": 1,
				"to_bit": 1, "to_bitvector": 1, "to_stdulogic": 1, "to_stdlogicvector": 2, "to_stdulogicvector": 2,
				"to_01": 4, "to_x01": 4, "to_x01z": 4, "to_ux01": 4, "??": 1, "rising_edge": 1, "falling_edge": 1,
				"is_x": 2, "to_ostring": 1, "to_hstring": 1
			},
			{identifier: len(overloads) for identifier, overloads in package.Functions.items()}
		)
		self.assertDictEqual(
			{"read": 4, "write": 2, "oread": 2, "hread": 2, "owrite": 1, "hwrite": 1},
			{identifier: len(overloads) for identifier, overloads in package.Procedures.items()}
		)

	def test_StdULogic(self) -> None:
		"""``type STD_ULOGIC is ('U', 'X', '0', '1', 'Z', 'W', 'L', 'H', '-');``"""
		stdULogic = Std_Logic_1164().Types["std_ulogic"]

		self.assertIsInstance(stdULogic, StdULogic)
		self.assertListEqual(list("UX01ZWLH-"), [literal.Value for literal in stdULogic.Literals])

	def test_StdULogicVector(self) -> None:
		"""``type STD_ULOGIC_VECTOR is array (NATURAL range <>) of STD_ULOGIC;``"""
		vector = Std_Logic_1164().Types["std_ulogic_vector"]

		self.assertIsInstance(vector, ArrayType)
		self.assertEqual("std_ulogic", vector.ElementType.Name.Identifier)

	def test_Subtypes(self) -> None:
		"""``std_logic`` and ``std_logic_vector`` have the base types ``std_ulogic`` and ``std_ulogic_vector``."""
		package = Std_Logic_1164()

		self.assertIs(package.Types["std_ulogic"], package.Subtypes["std_logic"].BaseType)
		self.assertIs(package.Types["std_ulogic_vector"], package.Subtypes["std_logic_vector"].BaseType)

	def test_RangeSubtypes(self) -> None:
		"""``subtype X01 is resolved STD_ULOGIC range 'X' to '1';`` and its relatives."""
		package = Std_Logic_1164()
		for identifier, low, high in (
			("x01",   "X", "1"),
			("x01z",  "X", "Z"),
			("ux01",  "U", "1"),
			("ux01z", "U", "Z")
		):
			subtype = package.Subtypes[identifier]
			self.assertIsInstance(subtype, Subtype)
			self.assertIsInstance(subtype.Type, ConstrainedScalarSubtypeSymbol)
			self.assertIs(package.Types["std_ulogic"], subtype.BaseType)
			self.assertEqual(low, subtype.Range.LeftBound.Value)
			self.assertEqual(high, subtype.Range.RightBound.Value)
			self.assertIs(Direction.To, subtype.Range.Direction)

	def test_LogicalOperators_StdULogic(self) -> None:
		"""``function "and" (l : STD_ULOGIC; r : STD_ULOGIC) return UX01;`` - the first overload of each operator."""
		package = Std_Logic_1164()
		for operatorSymbol in ("and", "nand", "or", "nor", "xor", "xnor"):
			operator = package.Functions[operatorSymbol][0]
			self.assertIsInstance(operator, Operator)
			self.assertEqual("ux01", operator.ReturnType.Name.Identifier)
			self.assertListEqual(
				["std_ulogic", "std_ulogic"],
				[item.Subtype.Name.Identifier for item in operator.ParameterItems]
			)

	def test_LogicalOperators_Vector(self) -> None:
		"""``function "and" (l, r : STD_ULOGIC_VECTOR) return STD_ULOGIC_VECTOR;``: one parameter item, two identifiers."""
		operator = Std_Logic_1164().Functions["and"][1]
		item, =    operator.ParameterItems

		self.assertTupleEqual(("l", "r"), item.Identifiers)
		self.assertEqual("std_ulogic_vector", item.Subtype.Name.Identifier)
		self.assertEqual("std_ulogic_vector", operator.ReturnType.Name.Identifier)

	def test_Reduction(self) -> None:
		"""``function "and" (l : STD_ULOGIC_VECTOR) return STD_ULOGIC;``"""
		operator = Std_Logic_1164().Functions["and"][4]

		self.assertEqual("std_ulogic", operator.ReturnType.Name.Identifier)
		self.assertListEqual(["std_ulogic_vector"], [item.Subtype.Name.Identifier for item in operator.ParameterItems])

	def test_ToBit(self) -> None:
		"""``function To_bit (s : STD_ULOGIC; xmap : BIT := '0') return BIT;``"""
		toBit =   Std_Logic_1164().Functions["to_bit"][0]
		s, xmap = toBit.ParameterItems

		self.assertIsInstance(toBit, Function)
		self.assertNotIsInstance(toBit, Operator)
		self.assertEqual("bit", toBit.ReturnType.Name.Identifier)
		self.assertIsNone(s.DefaultExpression)
		self.assertIsInstance(xmap, ParameterConstantInterfaceItem)
		self.assertIs(Mode.In, xmap.Mode)
		self.assertIsInstance(xmap.DefaultExpression, CharacterLiteral)
		self.assertEqual("0", xmap.DefaultExpression.Value)

	def test_ToX01(self) -> None:
		"""``To_X01``: vector, scalar (returning ``X01``), bit vector, bit."""
		toX01 = Std_Logic_1164().Functions["to_x01"]

		self.assertListEqual(
			["std_ulogic_vector", "std_ulogic", "bit_vector", "bit"],
			[function.ParameterItems[0].Subtype.Name.Identifier for function in toX01]
		)
		self.assertListEqual(
			["std_ulogic_vector", "x01", "std_ulogic_vector", "x01"],
			[function.ReturnType.Name.Identifier for function in toX01]
		)

	def test_RisingEdge(self) -> None:
		"""``function rising_edge (signal s : STD_ULOGIC) return BOOLEAN;`` - also ``falling_edge``."""
		package = Std_Logic_1164()
		for identifier in ("rising_edge", "falling_edge"):
			s, = package.Functions[identifier][0].ParameterItems
			self.assertIsInstance(s, ParameterSimpleSignalInterfaceItem)
			self.assertIs(Mode.In, s.Mode)
			self.assertEqual("std_ulogic", s.Subtype.Name.Identifier)

	def test_Read(self) -> None:
		"""``READ`` of ``STD_ULOGIC`` and ``STD_ULOGIC_VECTOR``, with and without ``GOOD``."""
		reads = Std_Logic_1164().Procedures["read"]

		self.assertListEqual([3, 2, 3, 2], [len(read.ParameterItems) for read in reads])
		for read in reads:
			self.assertIsInstance(read, Procedure)
			self.assertIs(Mode.InOut, read.ParameterItems[0].Mode)
			for item in read.ParameterItems:
				self.assertIsInstance(item, ParameterVariableInterfaceItem)

	def test_Write(self) -> None:
		"""``WRITE``, ``OWRITE``, ``HWRITE``: ``L``, ``VALUE``, ``JUSTIFIED``, ``FIELD``."""
		package = Std_Logic_1164()
		for identifier in ("write", "owrite", "hwrite"):
			for write in package.Procedures[identifier]:
				self.assertListEqual(
					["L", "VALUE", "JUSTIFIED", "FIELD"],
					[item.Identifiers[0] for item in write.ParameterItems]
				)


class StdULogics(Testcase):
	def test_MatchingOperators(self) -> None:
		"""``std_ulogic`` declares the matching relational operators (IEEE Std 1076-2008, 9.2.3) after those of an
		enumerated type."""
		stdULogic = StdULogic()

		self.assertListEqual(
			["?=", "?/=", "?<", "?<=", "?>", "?>="],
			[operation.Identifier for operation in stdULogic.ImplicitOperations[-6:]]
		)

	def test_VectorMatchingOperators(self) -> None:
		"""After the analysis, ``std_ulogic_vector`` declares ``"?="`` and ``"?/="`` returning ``std_ulogic``."""
		entity = Entity("e", [LibraryClause([LibraryReferenceSymbol(SimpleName("ieee"))]), _use("ieee.std_logic_1164.all")])
		design = _design(entity)
		vector = design.GetPackage("ieee", "std_logic_1164").Types["std_ulogic_vector"]

		for operatorSymbol in ("?=", "?/="):
			operations = [operation for operation in vector.ImplicitOperations if operation.Identifier == operatorSymbol]
			self.assertEqual(1, len(operations))
			self.assertEqual("std_ulogic", operations[0].ReturnType.Name.Identifier)
			self.assertIn(operations[0], entity._namespace.Lookup(operatorSymbol).Declarations)
