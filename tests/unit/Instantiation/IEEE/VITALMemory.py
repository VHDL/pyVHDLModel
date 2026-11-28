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
"""Tests for pyVHDLModel.IEEE.VITALMemoryPkg."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design, IEEEFlavor
from pyVHDLModel.Base        import Mode
from pyVHDLModel.Expression  import Aggregate, CharacterEnumerationLiteral, IntegerLiteral, NamedAggregateElement, \
                                    NegationExpression
from pyVHDLModel.Interface   import ParameterSimpleSignalInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Object      import Constant
from pyVHDLModel.Subprogram  import Function, Procedure
from pyVHDLModel.Symbol      import RecordElementSymbol
from pyVHDLModel.Type        import AccessType, ArrayType, EnumeratedType, RecordType, Subtype
from pyVHDLModel.IEEE        import VITAL_Memory


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VITALMemory(Testcase):
	"""Package ``ieee.VITAL_Memory`` (IEEE Std 1076.4-2000)."""

	def test_Declarations(self) -> None:
		"""78 declarations of 8 kinds, all with the package as parent."""
		vitalMemory =  VITAL_Memory()
		declarations = vitalMemory.DeclaredItems

		self.assertEqual(78, len(declarations))
		for declaration in declarations:
			self.assertIs(vitalMemory, declaration.Parent)

		self.assertEqual(8, len([declaration for declaration in declarations if isinstance(declaration, EnumeratedType)]))
		self.assertEqual(4, len([declaration for declaration in declarations if isinstance(declaration, RecordType)]))
		self.assertEqual(5, len([declaration for declaration in declarations if isinstance(declaration, AccessType)]))
		self.assertEqual(11, len([declaration for declaration in declarations if isinstance(declaration, ArrayType)]))
		self.assertEqual(1, len([declaration for declaration in declarations if isinstance(declaration, Subtype)]))
		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, Constant)]))
		self.assertEqual(3, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(44, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))

	def test_Constants(self) -> None:
		"""``DefaultNumBitsPerSubword := -1`` and ``VitalDefaultPortFlag := ( MemoryCurrent => READ, ... )``."""
		constants = VITAL_Memory().Constants

		negation = constants["defaultnumbitspersubword"].DefaultExpression
		self.assertIsInstance(negation, NegationExpression)
		self.assertIsInstance(negation.Operand, IntegerLiteral)
		self.assertEqual(1, negation.Operand.Value)
		portFlag = constants["vitaldefaultportflag"].DefaultExpression
		self.assertIsInstance(portFlag, Aggregate)
		self.assertEqual(5, len(portFlag.Elements))
		for element in portFlag.Elements:
			self.assertIsInstance(element, NamedAggregateElement)
			self.assertIsInstance(element.Name, RecordElementSymbol)

		self.assertEqual("MemoryCurrent", portFlag.Elements[0].Name.Name.Identifier)
		self.assertEqual("READ", portFlag.Elements[0].Expression.Name.Identifier)

	def test_Records(self) -> None:
		"""``TYPE VitalMemoryTimingDataType IS RECORD ... RefLastA : X01ArrayPT; ... END RECORD;``"""
		timingData = VITAL_Memory().Types["vitalmemorytimingdatatype"]

		self.assertEqual(13, len(timingData.Elements))
		self.assertTupleEqual(("RefLastA", ), timingData.Elements[9].Identifiers)
		self.assertEqual("X01ArrayPT", timingData.Elements[9].Subtype.Name.Identifier)

	def test_Symbols(self) -> None:
		"""``VitalMemorySymbolType`` has 40 character literals; ``VitalMemoryTableType`` has two dimensions."""
		types =    VITAL_Memory().Types
		literals = types["vitalmemorysymboltype"].Literals

		self.assertEqual(40, len(literals))
		for literal in literals:
			self.assertIsInstance(literal, CharacterEnumerationLiteral)

		self.assertListEqual(["/", "\\", "P"], [literal.Value for literal in literals[:3]])
		self.assertEqual("t", literals[39].Value)
		violationLiterals = types["vitalmemoryviolationsymboltype"].Literals
		self.assertListEqual(["X", "0", "-"], [literal.Value for literal in violationLiterals])
		self.assertEqual(2, len(types["vitalmemorytabletype"].Dimensions))

	def test_AddPathDelay(self) -> None:
		"""24 overloads of ``VitalMemoryAddPathDelay``: 6 of each delay type."""
		overloads = VITAL_Memory().Procedures["vitalmemoryaddpathdelay"]

		self.assertEqual(24, len(overloads))
		self.assertEqual(7, len(overloads[0].ParameterItems))
		self.assertTupleEqual(("PathDelay", ), overloads[0].ParameterItems[4].Identifiers)
		self.assertEqual("VitalDelayType", overloads[0].ParameterItems[4].Subtype.Name.Identifier)
		last = overloads[23].ParameterItems
		self.assertEqual(9, len(last))
		self.assertIsInstance(last[0], ParameterVariableInterfaceItem)
		self.assertTupleEqual(("ScheduleDataArray", ), last[0].Identifiers)
		self.assertIsInstance(last[1], ParameterSimpleSignalInterfaceItem)
		self.assertEqual("STD_LOGIC_VECTOR", last[1].Subtype.Name.Identifier)
		self.assertTupleEqual(("InputChangeTimeArray", ), last[3].Identifiers)
		self.assertIs(Mode.InOut, last[3].Mode)
		self.assertEqual("VitalDelayArrayType01ZX", last[4].Subtype.Name.Identifier)
		self.assertTupleEqual(("PathConditionArray", ), last[6].Identifiers)
		self.assertIsNone(last[6].DefaultExpression)
		self.assertEqual("BitCorrupt", last[8].DefaultExpression.Name.Identifier)

	def test_SetupHoldCheck(self) -> None:
		"""Seven overloads; the last has ``ArcType`` and ``NumBitsPerSubWord`` after ``MsgSeverity``."""
		overloads = VITAL_Memory().Procedures["vitalmemorysetupholdcheck"]

		self.assertEqual(7, len(overloads))
		self.assertEqual(22, len(overloads[0].ParameterItems))
		self.assertEqual("TIME", overloads[0].ParameterItems[4].Subtype.Name.Identifier)
		self.assertEqual("VitalBoolArrayT", overloads[0].ParameterItems[12].Subtype.Name.Identifier)
		last = overloads[6].ParameterItems
		self.assertEqual(25, len(last))
		self.assertEqual("X01", last[0].Subtype.Name.Identifier)
		self.assertTupleEqual(("MsgSeverity", ), last[17].Identifiers)
		self.assertTupleEqual(("ArcType", ), last[18].Identifiers)
		self.assertEqual("CrossArc", last[18].DefaultExpression.Name.Identifier)
		self.assertTupleEqual(("MsgFormat", ), last[20].Identifiers)

	def test_DeclareMemory(self) -> None:
		"""``IMPURE FUNCTION VitalDeclareMemory ( ... ) RETURN VitalMemoryDataType;`` with and without sub-words."""
		overloads = VITAL_Memory().Functions["vitaldeclarememory"]

		self.assertEqual(2, len(overloads))
		for overload in overloads:
			self.assertFalse(overload.IsPure)
			self.assertEqual("VitalMemoryDataType", overload.ReturnType.Name.Identifier)

		self.assertEqual(5, len(overloads[0].ParameterItems))
		self.assertEqual(4, len(overloads[1].ParameterItems))

	def test_MemoryTable(self) -> None:
		"""``VitalMemoryTable`` with and without an enable bus; ``PortType : IN VitalPortType := UNDEF``."""
		overloads = VITAL_Memory().Procedures["vitalmemorytable"]

		self.assertEqual(16, len(overloads[0].ParameterItems))
		self.assertEqual(18, len(overloads[1].ParameterItems))
		self.assertTupleEqual(("PrevEnableBus", ), overloads[1].ParameterItems[3].Identifiers)
		self.assertTupleEqual(("PortFlagArray", ), overloads[1].ParameterItems[6].Identifiers)
		self.assertTupleEqual(("EnableBus", ), overloads[1].ParameterItems[8].Identifiers)
		self.assertEqual("UNDEF", overloads[1].ParameterItems[13].DefaultExpression.Name.Identifier)

	def test_Analyze(self) -> None:
		"""With the VITAL packages, every type mark resolves, e.g. ``VitalDelayArrayType01ZX`` of ``VITAL_Timing``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.IEEE | IEEEFlavor.WithVITAL)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		ieee =        design.Libraries["ieee"]
		vitalTiming = ieee.Packages["vital_timing"]
		vitalMemory = ieee.Packages["vital_memory"]
		self.assertIs(
			vitalTiming.Types["vitaldelayarraytype01zx"],
			vitalMemory.Procedures["vitalmemoryaddpathdelay"][23].ParameterItems[4].Subtype.Reference
		)
		self.assertIs(
			vitalMemory.Types["x01arraypt"],
			vitalMemory.Types["vitalmemorytimingdatatype"].Elements[9].Subtype.Reference
		)
