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
"""Tests for pyVHDLModel.IEEE.VITALPrimitivesPkg."""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel             import Design, IEEEFlavor
from pyVHDLModel.Base        import Direction, Mode
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, ParameterSimpleSignalInterfaceItem, \
                                    ParameterVariableInterfaceItem
from pyVHDLModel.Object      import DeferredConstant
from pyVHDLModel.Subprogram  import Function, Procedure
from pyVHDLModel.Symbol      import ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Type        import ArrayType, Subtype
from pyVHDLModel.IEEE        import VITAL_Primitives


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class VITALPrimitives(Testcase):
	"""Package ``ieee.VITAL_Primitives`` (IEEE Std 1076.4-2000)."""

	def test_Declarations(self) -> None:
		"""93 declarations of 5 kinds, all with the package as parent."""
		vitalPrimitives = VITAL_Primitives()
		declarations =    vitalPrimitives.DeclaredItems

		self.assertEqual(93, len(declarations))
		for declaration in declarations:
			self.assertIs(vitalPrimitives, declaration.Parent)

		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, Subtype)]))
		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, ArrayType)]))
		self.assertEqual(2, len([declaration for declaration in declarations if isinstance(declaration, DeferredConstant)]))
		self.assertEqual(41, len([declaration for declaration in declarations if isinstance(declaration, Function)]))
		self.assertEqual(46, len([declaration for declaration in declarations if isinstance(declaration, Procedure)]))

	def test_Tables(self) -> None:
		"""``SUBTYPE VitalTruthSymbolType IS VitalTableSymbolType RANGE 'X' TO 'Z';`` and its table type."""
		vitalPrimitives = VITAL_Primitives()
		symbols =         vitalPrimitives.Subtypes["vitaltruthsymboltype"].Type

		self.assertIsInstance(symbols, ConstrainedScalarSubtypeSymbol)
		self.assertEqual("VitalTableSymbolType", symbols.Name.Identifier)
		self.assertEqual("X", symbols.Constraint.LeftBound.Value)
		self.assertEqual("Z", symbols.Constraint.RightBound.Value)
		self.assertIs(Direction.To, symbols.Constraint.Direction)
		table = vitalPrimitives.Types["vitaltruthtabletype"]
		self.assertEqual(2, len(table.Dimensions))
		self.assertEqual("VitalTruthSymbolType", table.ElementType.Name.Identifier)

	def test_DefaultDelays(self) -> None:
		"""``CONSTANT VitalDefDelay01 : VitalDelayType01;`` and ``VitalDefDelay01Z``: deferred constants."""
		deferredConstants = VITAL_Primitives().DeferredConstants

		self.assertIsInstance(deferredConstants["vitaldefdelay01"], DeferredConstant)
		self.assertEqual("VitalDelayType01Z", deferredConstants["vitaldefdelay01z"].Subtype.Name.Identifier)

	def test_Gates(self) -> None:
		"""``PROCEDURE VitalAND3 ( SIGNAL q : OUT std_ulogic; SIGNAL a, b, c : IN std_ulogic; ... );`` and its function."""
		vitalPrimitives = VITAL_Primitives()
		function =        vitalPrimitives.Functions["vitaland3"][0]
		procedure =       vitalPrimitives.Procedures["vitaland3"][0]

		self.assertTupleEqual(("a", "b", "c"), function.ParameterItems[0].Identifiers)
		self.assertEqual("VitalDefaultResultMap", function.ParameterItems[1].DefaultExpression.Name.Identifier)
		self.assertEqual("std_ulogic", function.ReturnType.Name.Identifier)
		self.assertEqual(6, len(procedure.ParameterItems))
		for parameter in procedure.ParameterItems[:2]:
			self.assertIsInstance(parameter, ParameterSimpleSignalInterfaceItem)

		for parameter in procedure.ParameterItems[2:]:
			self.assertIsInstance(parameter, ParameterConstantInterfaceItem)

		self.assertIs(Mode.Out, procedure.ParameterItems[0].Mode)
		self.assertTupleEqual(("a", "b", "c"), procedure.ParameterItems[1].Identifiers)
		self.assertTupleEqual(("tpd_c_q", ), procedure.ParameterItems[4].Identifiers)
		self.assertEqual("VitalDefDelay01", procedure.ParameterItems[4].DefaultExpression.Name.Identifier)

	def test_Buffers(self) -> None:
		"""``PROCEDURE VitalBUFIF0 ( ...; CONSTANT tpd_enable_q : IN VitalDelayType01Z := VitalDefDelay01Z; ... );``"""
		procedure = VITAL_Primitives().Procedures["vitalbufif0"][0]

		self.assertEqual(6, len(procedure.ParameterItems))
		enableDelay = procedure.ParameterItems[4]
		self.assertEqual("VitalDelayType01Z", enableDelay.Subtype.Name.Identifier)
		self.assertEqual("VitalDefDelay01Z", enableDelay.DefaultExpression.Name.Identifier)
		self.assertEqual("VitalResultZMapType", procedure.ParameterItems[5].Subtype.Name.Identifier)

	def test_Multiplexers(self) -> None:
		"""``FUNCTION VitalMUX8 ( CONSTANT Data : IN std_logic_vector8; CONSTANT dSelect : IN std_logic_vector3; ... )``"""
		vitalPrimitives = VITAL_Primitives()
		function =        vitalPrimitives.Functions["vitalmux8"][0]

		self.assertEqual("std_logic_vector8", function.ParameterItems[0].Subtype.Name.Identifier)
		self.assertEqual("std_logic_vector3", function.ParameterItems[1].Subtype.Name.Identifier)
		self.assertTupleEqual(("d1", "d0"), vitalPrimitives.Procedures["vitalmux2"][0].ParameterItems[1].Identifiers)

	def test_Decoders(self) -> None:
		"""``VitalDECODER2`` has a scalar data delay with a default, ``VitalDECODER4`` an array of delays without one."""
		vitalPrimitives = VITAL_Primitives()
		decoder2 =        vitalPrimitives.Procedures["vitaldecoder2"][0]
		decoder4 =        vitalPrimitives.Procedures["vitaldecoder4"][0]

		self.assertEqual("std_logic_vector2", decoder2.ParameterItems[0].Subtype.Name.Identifier)
		self.assertEqual("VitalDelayType01", decoder2.ParameterItems[3].Subtype.Name.Identifier)
		self.assertIsNotNone(decoder2.ParameterItems[3].DefaultExpression)
		self.assertEqual("VitalDelayArrayType01", decoder4.ParameterItems[3].Subtype.Name.Identifier)
		self.assertIsNone(decoder4.ParameterItems[3].DefaultExpression)
		self.assertEqual("std_logic_vector8", vitalPrimitives.Functions["vitaldecoder8"][0].ReturnType.Name.Identifier)

	def test_StateTable(self) -> None:
		"""Four overloads: variables or signals of mode ``inout`` as result, ``NumStates`` for a vector result."""
		overloads = VITAL_Primitives().Procedures["vitalstatetable"]

		self.assertEqual(4, len(overloads))
		self.assertEqual(5, len(overloads[0].ParameterItems))
		for parameter in overloads[0].ParameterItems[:2]:
			self.assertIsInstance(parameter, ParameterVariableInterfaceItem)
			self.assertIs(Mode.InOut, parameter.Mode)

		self.assertEqual(3, len(overloads[3].ParameterItems))
		self.assertIsInstance(overloads[3].ParameterItems[0], ParameterSimpleSignalInterfaceItem)
		self.assertIs(Mode.InOut, overloads[3].ParameterItems[0].Mode)
		self.assertEqual("std_logic", overloads[3].ParameterItems[0].Subtype.Name.Identifier)

	def test_Analyze(self) -> None:
		"""With the VITAL packages, every type mark resolves, e.g. ``std_logic_vector4`` of package ``VITAL_Timing``."""
		design = Design("design")
		design.LoadStdLibrary()
		design.LoadIEEELibrary(flavor=IEEEFlavor.IEEE | IEEEFlavor.WithVITAL)
		with WarningCollector() as collector:
			design.Analyze()

		self.assertListEqual([], list(collector.Warnings))
		ieee =            design.Libraries["ieee"]
		vitalTiming =     ieee.Packages["vital_timing"]
		vitalPrimitives = ieee.Packages["vital_primitives"]
		self.assertIs(
			vitalTiming.Subtypes["std_logic_vector4"],
			vitalPrimitives.Functions["vitalmux4"][0].ParameterItems[0].Subtype.Reference
		)
		self.assertIs(
			vitalTiming.Types["vitaltablesymboltype"],
			vitalPrimitives.Subtypes["vitaltruthsymboltype"].Type.Reference
		)
