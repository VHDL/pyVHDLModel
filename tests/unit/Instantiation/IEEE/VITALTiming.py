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
"""Tests for pyVHDLModel.IEEE.VITALTiming."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design, IEEEFlavor
from pyVHDLModel.Base        import Direction
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Expression  import Aggregate, OthersAggregateElement, PhysicalIntegerLiteral, StringLiteral
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Subprogram  import Function
from pyVHDLModel.Symbol      import ConstrainedArraySubtypeSymbol, ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Type        import AccessType, ArrayType, EnumeratedType, RecordType, Subtype
from pyVHDLModel.IEEE        import VITAL_Timing


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VITALTimings(Testcase):
	"""Package ``ieee.VITAL_Timing`` (IEEE Std 1076.4-2000)."""

	def test_Declarations(self) -> None:
		"""48 declarations of 8 kinds, all with the package as parent."""
		vitalTiming =  VITAL_Timing()
		declarations = vitalTiming.DeclaredItems

		self.assertEqual(48, len(declarations))
		for declaration in declarations:
			self.assertIs(vitalTiming, declaration.Parent)

		self.assertEqual(4, len([declaration for declaration in declarations if isinstance(declaration, EnumeratedType)]))
		self.assertEqual(7, len([declaration for declaration in declarations if isinstance(declaration, RecordType)]))
		self.assertEqual(3, len([declaration for declaration in declarations if isinstance(declaration, AccessType)]))
		self.assertEqual(16, len([declaration for declaration in declarations if isinstance(declaration, ArrayType)]))
		self.assertEqual(6, len([declaration for declaration in declarations if isinstance(declaration, Subtype)]))
		self.assertEqual(9, len([declaration for declaration in declarations if isinstance(declaration, Constant)]))
		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, Attribute)]))
		self.assertEqual(1, len([declaration for declaration in declarations if isinstance(declaration, Function)]))

	def test_DelayTypes(self) -> None:
		"""``TYPE VitalDelayType01 IS ARRAY (VitalTransitionType RANGE tr01 to tr10) OF TIME;``"""
		delayType = VITAL_Timing().Types["vitaldelaytype01"]
		index =     delayType.Dimensions[0]

		self.assertIsInstance(index, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("VitalTransitionType", index.Name.Identifier)
		self.assertEqual("tr10", index.Constraint.RightBound.Name.Identifier)
		self.assertIs(Direction.To, index.Constraint.Direction)
		self.assertEqual("TIME", delayType.ElementType.Name.Identifier)

	def test_ZeroDelays(self) -> None:
		"""``VitalZeroDelay := 0 ns``, ``VitalZeroDelay01 := ( 0 ns, 0 ns )``, ``... := ( OTHERS => 0 ns )``"""
		constants = VITAL_Timing().Constants

		self.assertIsInstance(constants["vitalzerodelay"].DefaultExpression, PhysicalIntegerLiteral)
		self.assertEqual("ns", constants["vitalzerodelay"].DefaultExpression.UnitName)
		self.assertEqual(2, len(constants["vitalzerodelay01"].DefaultExpression.Elements))
		others = constants["vitalzerodelay01z"].DefaultExpression
		self.assertIsInstance(others, Aggregate)
		self.assertIsInstance(others.Elements[0], OthersAggregateElement)

	def test_StdLogicVectors(self) -> None:
		"""``SUBTYPE std_logic_vector8 IS std_logic_vector(7 DOWNTO 0);``"""
		subtype = VITAL_Timing().Subtypes["std_logic_vector8"].Type

		self.assertIsInstance(subtype, ConstrainedArraySubtypeSymbol)
		self.assertEqual(7, subtype.Constraints[0].LeftBound.Value)
		self.assertIs(Direction.DownTo, subtype.Constraints[0].Direction)

	def test_Maps(self) -> None:
		"""``TYPE VitalOutputMapType IS ARRAY ( std_ulogic ) OF std_ulogic;`` and its default ``"UX01ZWLH-"``."""
		vitalTiming = VITAL_Timing()

		self.assertEqual("std_ulogic", vitalTiming.Types["vitaloutputmaptype"].Dimensions[0].Identifier)
		self.assertIsInstance(vitalTiming.Constants["vitaldefaultoutputmap"].DefaultExpression, StringLiteral)
		self.assertEqual(5, len(vitalTiming.Constants["vitaldefaultresultzmap"].DefaultExpression.Elements))

	def test_Records(self) -> None:
		"""``TYPE VitalTimingDataType IS RECORD NotFirstFlag : BOOLEAN; ... SetupEnA : VitalBoolArrayPT; END RECORD;``"""
		timingData = VITAL_Timing().Types["vitaltimingdatatype"]

		self.assertEqual(11, len(timingData.Elements))
		self.assertTupleEqual(("SetupEnA", ), timingData.Elements[10].Identifiers)
		self.assertEqual("VitalBoolArrayPT", timingData.Elements[10].Subtype.Name.Identifier)

	def test_Symbols(self) -> None:
		"""``VitalTableSymbolType`` has 23 character literals; ``VitalEdgeSymbolType`` is ``RANGE '/' TO '*'``."""
		vitalTiming = VITAL_Timing()
		literals =    [literal.Value for literal in vitalTiming.Types["vitaltablesymboltype"].Literals]

		self.assertEqual(23, len(literals))
		self.assertListEqual(["/", "\\", "P"], literals[:3])
		edge = vitalTiming.Subtypes["vitaledgesymboltype"].Type
		self.assertEqual("*", edge.Constraint.RightBound.Value)

	def test_Analyze(self) -> None:
		"""With the VITAL packages, every type mark resolves, e.g. ``X01`` of a record element."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.IEEE | IEEEFlavor.WithVITAL)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		vitalTiming = design.Libraries["ieee"].Packages["vital_timing"]
		self.assertIs(
			vitalTiming.Types["vitaltransitiontype"],
			vitalTiming.Types["vitaldelaytype01"].Dimensions[0].Reference
		)
		self.assertIsNotNone(vitalTiming.Types["vitaltimingdatatype"].Elements[1].Subtype.Reference)
