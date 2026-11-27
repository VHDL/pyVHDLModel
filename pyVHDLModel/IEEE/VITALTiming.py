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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
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
"""This module contains the predefined package ``ieee.VITAL_Timing`` of VHDL library ``IEEE``."""

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleObjectOrFunctionCallSymbol, ConstrainedScalarSubtypeSymbol, \
                                   ConstrainedArraySubtypeSymbol
from pyVHDLModel.Expression import Aggregate, CharacterEnumerationLiteral, CharacterLiteral, EnumerationLiteral, \
                                   IntegerLiteral, OthersAggregateElement, PhysicalIntegerLiteral, \
                                   SimpleAggregateElement, StringLiteral, ExpressionUnion
from pyVHDLModel.Type       import AccessType, ArrayType, EnumeratedType, RecordType, RecordTypeElement, Subtype
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Declaration import Attribute
from pyVHDLModel.Subprogram import Function
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class VITAL_Timing(PredefinedPackage):
	"""
	Predefined package ``ieee.VITAL_Timing`` (IEEE Std 1076.4-2000).

	It defines the types, attributes, constants, functions and procedures for timing in ASIC models. Its declarations,
	in the order of the package:

	* the transition and delay types (``VitalTransitionType``, ``VitalDelayType``, ``VitalDelayType01`` ...) with their
	  array types and the zero delay constants (``VitalZeroDelay`` ...)
	* the attributes ``VITAL_Level0`` and ``VITAL_Level1``, the subtypes ``std_logic_vector2`` ... ``std_logic_vector8``
	* the output and result map types with their default constants, the time, boolean and logic array and access types
	* the records of the timing, period, glitch, path and skew data with their initial values, the glitch kinds, the table
	  symbols and the edge symbols
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``VITAL_Timing`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))

		def name(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating a name in an expression.

			It names an enumeration literal, e.g. ``tr01`` or ``FALSE``.

			:param identifier: The identifier.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		def nanoseconds(value: int) -> PhysicalIntegerLiteral:
			"""
			Nested function creating a physical literal of unit ``ns``.

			:param value: The value.
			:returns:     The literal.
			"""
			return PhysicalIntegerLiteral(value, "ns")

		def aggregate(*expressions: ExpressionUnion) -> Aggregate:
			"""
			Nested function creating a positional aggregate.

			:param expressions: The expressions, in order.
			:returns:           The aggregate.
			"""
			return Aggregate([SimpleAggregateElement(expression) for expression in expressions])

		def constant(identifier: str, typeName: str, defaultExpression: ExpressionUnion) -> None:
			"""
			Nested function declaring a constant of this package.

			:param identifier:        The constant's identifier.
			:param typeName:          The name of the constant's type.
			:param defaultExpression: The constant's value.
			"""
			declaration = Constant((identifier, ), self._TypeMark(typeName), defaultExpression)
			self._constants[declaration._normalizedIdentifiers[0]] = declaration
			self.AddDeclaredItem(declaration)

		def record(identifier: str, *elements: tuple[str, str]) -> None:
			"""
			Nested function declaring a record type of this package.

			:param identifier: The record type's identifier.
			:param elements:   The identifier and the type name of each element, in declaration order.
			"""
			self._DeclareItem(RecordType(identifier, [
				RecordTypeElement((elementIdentifier, ), self._TypeMark(typeName)) for elementIdentifier, typeName in elements
			]), self._types)

		def arrayType(identifier: str, indexType: str, elementType: str) -> None:
			"""
			Nested function declaring an unconstrained array type ``array (<indexType> range <>) of <elementType>``.

			:param identifier:  The array type's identifier.
			:param indexType:   The name of the index type.
			:param elementType: The name of the element type.
			"""
			self._DeclareItem(
				ArrayType(identifier, (self._TypeMark(indexType), ), self._TypeMark(elementType)),
				self._types
			)

		# Transition and delay types, zero delays
		self._DeclareItem(EnumeratedType("VitalTransitionType", [EnumerationLiteral(literal) for literal in (
			"tr01", "tr10", "tr0z", "trz1", "tr1z", "trz0", "tr0X", "trx1", "tr1x", "trx0", "trxz", "trzx"
		)]), self._types)
		self._DeclareItem(Subtype("VitalDelayType", self._TypeMark("TIME")), self._subtypes)
		for identifier, highLiteral in (
			("VitalDelayType01",   "tr10"),
			("VitalDelayType01Z",  "trz0"),
			("VitalDelayType01ZX", "trzx")
		):
			self._DeclareItem(ArrayType(
				identifier,
				(ConstrainedScalarSubtypeSymbol(
					SimpleName("VitalTransitionType"),
					SimpleRange(name("tr01"), name(highLiteral), Direction.To)
				), ),
				self._TypeMark("TIME")
			), self._types)

		for suffix in ("", "01", "01Z", "01ZX"):
			arrayType(f"VitalDelayArrayType{suffix}", "NATURAL", f"VitalDelayType{suffix}")

		constant("VitalZeroDelay", "VitalDelayType", nanoseconds(0))
		constant("VitalZeroDelay01", "VitalDelayType01", aggregate(nanoseconds(0), nanoseconds(0)))
		for suffix in ("01Z", "01ZX"):
			constant(
				f"VitalZeroDelay{suffix}",
				f"VitalDelayType{suffix}",
				Aggregate([OthersAggregateElement(nanoseconds(0))])
			)

		# Attributes, subtypes of std_logic_vector
		for identifier in ("VITAL_Level0", "VITAL_Level1"):
			self.AddDeclaredItem(Attribute(identifier, self._TypeMark("BOOLEAN")))

		for width in (2, 3, 4, 8):
			self._DeclareItem(Subtype(f"std_logic_vector{width}", ConstrainedArraySubtypeSymbol(
				SimpleName("std_logic_vector"),
				(SimpleRange(IntegerLiteral(width - 1), IntegerLiteral(0), Direction.DownTo), )
			)), self._subtypes)

		# Output and result maps
		for identifier, indexType in (
			("VitalOutputMapType",  "std_ulogic"),
			("VitalResultMapType",  "UX01"),
			("VitalResultZMapType", "UX01Z")
		):
			self._DeclareItem(
				ArrayType(identifier, (SimpleName(indexType), ), self._TypeMark("std_ulogic")),
				self._types
			)

		constant("VitalDefaultOutputMap", "VitalOutputMapType", StringLiteral("UX01ZWLH-"))
		for identifier, typeName, values in (
			("VitalDefaultResultMap",  "VitalResultMapType",  "UX01"),
			("VitalDefaultResultZMap", "VitalResultZMapType", "UX01Z")
		):
			constant(identifier, typeName, aggregate(*(CharacterLiteral(value) for value in values)))

		# Arrays and access types
		arrayType("VitalTimeArrayT", "INTEGER", "TIME")
		self._DeclareItem(AccessType("VitalTimeArrayPT", self._TypeMark("VitalTimeArrayT")), self._types)
		arrayType("VitalBoolArrayT", "INTEGER", "BOOLEAN")
		self._DeclareItem(AccessType("VitalBoolArrayPT", self._TypeMark("VitalBoolArrayT")), self._types)
		self._DeclareItem(AccessType("VitalLogicArrayPT", self._TypeMark("std_logic_vector")), self._types)

		# Timing and period data
		record(
			"VitalTimingDataType",
			("NotFirstFlag", "BOOLEAN"), ("RefLast", "X01"), ("RefTime", "TIME"), ("HoldEn", "BOOLEAN"),
			("TestLast", "std_ulogic"), ("TestTime", "TIME"), ("SetupEn", "BOOLEAN"), ("TestLastA", "VitalLogicArrayPT"),
			("TestTimeA", "VitalTimeArrayPT"), ("HoldEnA", "VitalBoolArrayPT"), ("SetupEnA", "VitalBoolArrayPT")
		)
		self._DeclareSubprogram(
			Function("VitalTimingDataInit", self._TypeMark("VitalTimingDataType")),
			self._functions
		)
		record("VitalPeriodDataType", ("Last", "X01"), ("Rise", "TIME"), ("Fall", "TIME"), ("NotFirstFlag", "BOOLEAN"))
		constant(
			"VitalPeriodDataInit",
			"VitalPeriodDataType",
			aggregate(CharacterLiteral("X"), nanoseconds(0), nanoseconds(0), name("FALSE"))
		)

		# Glitch and path data
		self._DeclareItem(EnumeratedType("VitalGlitchKindType", [EnumerationLiteral(literal) for literal in (
			"OnEvent", "OnDetect", "VitalInertial", "VitalTransport"
		)]), self._types)
		record(
			"VitalGlitchDataType",
			("SchedTime", "TIME"), ("GlitchTime", "TIME"), ("SchedValue", "std_ulogic"), ("LastValue", "std_ulogic")
		)
		arrayType("VitalGlitchDataArrayType", "NATURAL", "VitalGlitchDataType")
		for suffix in ("", "01", "01Z"):
			record(
				f"VitalPath{suffix}Type",
				("InputChangeTime", "TIME"), ("PathDelay", f"VitalDelayType{suffix}"), ("PathCondition", "BOOLEAN")
			)

		for suffix in ("", "01", "01Z"):
			arrayType(f"VitalPathArray{suffix}Type", "NATURAL", f"VitalPath{suffix}Type")

		# Table and edge symbols, skew data
		self._DeclareItem(EnumeratedType("VitalTableSymbolType", [
			CharacterEnumerationLiteral(literal) for literal in "/\\PNrfpnRF^vEAD*X01-BZS"
		]), self._types)
		self._DeclareItem(Subtype("VitalEdgeSymbolType", ConstrainedScalarSubtypeSymbol(
			SimpleName("VitalTableSymbolType"),
			SimpleRange(CharacterLiteral("/"), CharacterLiteral("*"), Direction.To)
		)), self._subtypes)
		self._DeclareItem(EnumeratedType("VitalSkewExpectedType", [EnumerationLiteral(literal) for literal in (
			"none", "s1r", "s1f", "s2r", "s2f"
		)]), self._types)
		record(
			"VitalSkewDataType",
			("ExpectedType", "VitalSkewExpectedType"), ("Signal1Old1", "TIME"), ("Signal2Old1", "TIME"),
			("Signal1Old2", "TIME"), ("Signal2Old2", "TIME")
		)
		constant(
			"VitalSkewDataInit",
			"VitalSkewDataType",
			aggregate(name("none"), nanoseconds(0), nanoseconds(0), nanoseconds(0), nanoseconds(0))
		)


@export
class VITAL_Timing_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.VITAL_Timing``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``VITAL_Timing`` package body.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))
