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
"""Tests for pyVHDLModel.IEEE.VITALTimingPkg."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design, IEEEFlavor
from pyVHDLModel.Base        import Direction, Mode
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Expression  import Aggregate, CharacterLiteral, OthersAggregateElement, PhysicalIntegerLiteral, \
                                    StringLiteral
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterSimpleSignalInterfaceItem, \
                                    ParameterVariableInterfaceItem
from pyVHDLModel.Name        import AttributeName
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Subprogram  import Function, Procedure
from pyVHDLModel.Symbol      import ConstrainedArraySubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                                    IndexedObjectOrFunctionCallSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Type        import AccessType, ArrayType, EnumeratedType, RecordType, Subtype
from pyVHDLModel.IEEE        import VITAL_Timing


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VITALTimings(Testcase):
	"""Package ``ieee.VITAL_Timing`` (IEEE Std 1076.4-2000)."""

	def test_Declarations(self) -> None:
		"""67 declarations of 9 kinds, all with the package as parent."""
		vitalTiming =  VITAL_Timing()
		declarations = vitalTiming.DeclaredItems

		self.assertEqual(67, len(declarations))
		for declaration in declarations:
			self.assertIs(vitalTiming, declaration.Parent)

		self.assertEqual(4, len([declaration for declaration in declarations if isinstance(declaration, EnumeratedType)]))
		self.assertEqual(7, len([declaration for declaration in declarations if isinstance(declaration, RecordType)]))
		self.assertEqual(3, len([declaration for declaration in declarations if isinstance(declaration, AccessType)]))
		self.assertEqual(16, len([declaration for declaration in declarations if isinstance(declaration, ArrayType)]))
		self.assertEqual(6, len([declaration for declaration in declarations if isinstance(declaration, Subtype)]))
		self.assertEqual(9, len([declaration for declaration in declarations if isinstance(declaration, Constant)]))
		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, Attribute)]))
		self.assertEqual(7, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(13, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))

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

	def test_CalcDelay(self) -> None:
		"""``FUNCTION VitalCalcDelay ( CONSTANT NewVal : IN std_ulogic := 'X'; ... ) RETURN TIME;`` of each delay type."""
		overloads = VITAL_Timing().Functions["vitalcalcdelay"]

		self.assertEqual(3, len(overloads))
		self.assertEqual("VitalDelayType01Z", overloads[2].ParameterItems[2].Subtype.Name.Identifier)
		self.assertEqual("TIME", overloads[2].ReturnType.Name.Identifier)
		newValue = overloads[0].ParameterItems[0]
		self.assertIsInstance(newValue.DefaultExpression, CharacterLiteral)
		self.assertEqual("X", newValue.DefaultExpression.Value)

	def test_PathDelay(self) -> None:
		"""``PROCEDURE VitalPathDelay01Z ( SIGNAL OutSignal : OUT std_logic; VARIABLE GlitchData : INOUT ...; ... );``"""
		vitalTiming =  VITAL_Timing()
		pathDelay =    vitalTiming.Procedures["vitalpathdelay"][0]
		pathDelay01Z = vitalTiming.Procedures["vitalpathdelay01z"][0]

		self.assertEqual(12, len(pathDelay.ParameterItems))
		self.assertEqual(14, len(pathDelay01Z.ParameterItems))
		outSignal = pathDelay01Z.ParameterItems[0]
		self.assertIsInstance(outSignal, ParameterSimpleSignalInterfaceItem)
		self.assertIs(Mode.Out, outSignal.Mode)
		glitchData = pathDelay01Z.ParameterItems[1]
		self.assertIsInstance(glitchData, ParameterVariableInterfaceItem)
		self.assertIs(Mode.InOut, glitchData.Mode)
		self.assertTupleEqual(("OutputMap", ), pathDelay01Z.ParameterItems[10].Identifiers)
		self.assertEqual("VitalDefaultOutputMap", pathDelay01Z.ParameterItems[10].DefaultExpression.Name.Identifier)
		self.assertTupleEqual(("RejectFastPath", ), pathDelay01Z.ParameterItems[13].Identifiers)

	def test_WireDelay(self) -> None:
		"""``PROCEDURE VitalWireDelay ( SIGNAL OutSig : OUT std_ulogic; SIGNAL InSig : IN std_ulogic; ... );``"""
		vitalTiming = VITAL_Timing()
		overloads =   vitalTiming.Procedures["vitalwiredelay"]

		self.assertEqual(3, len(overloads))
		for parameter in overloads[1].ParameterItems[:2]:
			self.assertIsInstance(parameter, ParameterSimpleSignalInterfaceItem)

		for parameter in overloads[1].ParameterItems[2:]:
			self.assertIsInstance(parameter, ParameterConstantInterfaceItem)

		self.assertEqual("TIME", vitalTiming.Procedures["vitalsignaldelay"][0].ParameterItems[2].Subtype.Name.Identifier)

	def test_SetupHoldCheck(self) -> None:
		"""``PROCEDURE VitalSetupHoldCheck ( VARIABLE Violation : OUT X01; ... HeaderMsg : IN STRING := " "; ...``"""
		overloads = VITAL_Timing().Procedures["vitalsetupholdcheck"]

		self.assertEqual(2, len(overloads))
		self.assertEqual(22, len(overloads[1].ParameterItems))
		self.assertEqual("std_logic_vector", overloads[1].ParameterItems[2].Subtype.Name.Identifier)
		self.assertTupleEqual(("TestDelay", ), overloads[1].ParameterItems[4].Identifiers)
		self.assertEqual("0 ns", str(overloads[1].ParameterItems[4].DefaultExpression))
		headerMessage = overloads[1].ParameterItems[14]
		self.assertTupleEqual(("HeaderMsg", ), headerMessage.Identifiers)
		self.assertIsInstance(headerMessage.DefaultExpression, StringLiteral)
		self.assertEqual(" ", headerMessage.DefaultExpression.Value)
		severity = overloads[1].ParameterItems[17].DefaultExpression
		self.assertIsInstance(severity, SimpleObjectOrFunctionCallSymbol)
		self.assertEqual("WARNING", severity.Name.Identifier)

	def test_SkewChecks(self) -> None:
		"""``CONSTANT SkewS1S2RiseRise : IN TIME := TIME'HIGH;`` ... ``SIGNAL Trigger : INOUT std_ulogic``."""
		vitalTiming = VITAL_Timing()

		for identifier in ("vitalinphaseskewcheck", "vitaloutphaseskewcheck"):
			parameters = vitalTiming.Procedures[identifier][0].ParameterItems
			self.assertEqual(18, len(parameters))
			for parameter in parameters[8:12]:
				self.assertIsInstance(parameter.DefaultExpression, IndexedObjectOrFunctionCallSymbol)
				self.assertIsInstance(parameter.DefaultExpression.Name, AttributeName)
				self.assertEqual("HIGH", parameter.DefaultExpression.Name.Identifier)
				self.assertEqual("TIME", parameter.DefaultExpression.Name.Prefix.Identifier)

			self.assertIsInstance(parameters[17], ParameterSimpleSignalInterfaceItem)
			self.assertIs(Mode.InOut, parameters[17].Mode)

		parameters = vitalTiming.Procedures["vitaloutphaseskewcheck"][0].ParameterItems
		self.assertTupleEqual(("SkewS2S1FallRise", ), parameters[11].Identifiers)

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
		self.assertIs(
			design.Libraries["ieee"].Packages["std_logic_1164"].Subtypes["x01"],
			vitalTiming.Procedures["vitalsetupholdcheck"][0].ParameterItems[0].Subtype.Reference
		)
