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
"""This module contains the predefined package ``ieee.VITAL_Memory`` of VHDL library ``IEEE``."""

from typing                 import Iterable, Optional as Nullable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import Mode, ExpressionUnion
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleObjectOrFunctionCallSymbol, RecordElementSymbol
from pyVHDLModel.Expression import Aggregate, CharacterEnumerationLiteral, EnumerationLiteral, IntegerLiteral, \
                                   Literal, NamedAggregateElement, NegationExpression, PhysicalIntegerLiteral, \
                                   StringLiteral
from pyVHDLModel.Type       import AccessType, ArrayType, EnumeratedType, RecordType, RecordTypeElement, Subtype
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterSimpleSignalInterfaceItem, \
                                   ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class VITAL_Memory(PredefinedPackage):
	"""
	Predefined package ``ieee.VITAL_Memory`` (IEEE Std 1076.4-2000).

	It defines the types, constants, functions and procedures of memory models. Its declarations, in the order of the
	package:

	* the arc, output retain and message format kinds, the ``X01`` array and access types, the constant
	  ``DefaultNumBitsPerSubword``, the records of the schedule and timing data with their array types, the port states
	  and the port flag record with its default ``VitalDefaultPortFlag``
	* the path delay procedures ``VitalMemoryInitPathDelay``, ``VitalMemoryAddPathDelay`` (of each delay type, of a
	  ``STD_ULOGIC`` and a ``STD_LOGIC_VECTOR`` input signal) and ``VitalMemorySchedulePathDelay``
	* the function ``VitalMemoryTimingDataInit``, the timing check procedures ``VitalMemorySetupHoldCheck`` and
	  ``VitalMemoryPeriodPulseCheck``
	* the memory word and array types with their access types, ``VitalMemoryArrayRecType``, the memory, violation and
	  port types, ``VitalAddressValueType``
	* the impure function ``VitalDeclareMemory``, the procedures ``VitalMemoryTable``, ``VitalMemoryCrossPorts`` and
	  ``VitalMemoryViolation``

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.VITALMemoryPkg.VITAL_Memory_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``VITAL_Memory`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.VITAL_Timing.all", ))
		self._AddPackageClause(("IEEE.VITAL_Primitives.all", ))

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))

		def name(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating a name in an expression.

			It names an enumeration literal or a constant, e.g. ``CrossArc`` or ``VitalDefaultOutputMap``.

			:param identifier: The identifier.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		def enumeration(identifier: str, *literals: str) -> None:
			"""
			Nested function declaring an enumerated type of this package.

			:param identifier: The enumerated type's identifier.
			:param literals:   The enumeration literals, in declaration order.
			"""
			self._DeclareItem(EnumeratedType(identifier, [EnumerationLiteral(literal) for literal in literals]), self._types)

		def arrayType(identifier: str, elementType: str, dimensions: int = 1) -> None:
			"""
			Nested function declaring an unconstrained array type ``array (NATURAL range <>, ...) of <elementType>``.

			:param identifier:  The array type's identifier.
			:param elementType: The name of the element type.
			:param dimensions:  Optional, the number of dimensions. Default: ``1``.
			"""
			self._DeclareItem(ArrayType(
				identifier,
				tuple(self._TypeMark("NATURAL") for _ in range(dimensions)),
				self._TypeMark(elementType)
			), self._types)

		def accessType(identifier: str, designatedType: str) -> None:
			"""
			Nested function declaring an access type of this package.

			:param identifier:     The access type's identifier.
			:param designatedType: The name of the designated type.
			"""
			self._DeclareItem(AccessType(identifier, self._TypeMark(designatedType)), self._types)

		def record(identifier: str, *elements: tuple[str, str]) -> None:
			"""
			Nested function declaring a record type of this package.

			:param identifier: The record type's identifier.
			:param elements:   The identifier and the type name of each element, in declaration order.
			"""
			self._DeclareItem(RecordType(identifier, [
				RecordTypeElement((elementIdentifier, ), self._TypeMark(typeName)) for elementIdentifier, typeName in elements
			]), self._types)

		def constant(identifier: str, typeName: str, defaultExpression: Literal | NegationExpression | Aggregate) -> None:
			"""
			Nested function declaring a constant of this package.

			:param identifier:        The constant's identifier.
			:param typeName:          The name of the constant's type.
			:param defaultExpression: The constant's value.
			"""
			declaration = Constant((identifier, ), self._TypeMark(typeName), defaultExpression)
			self._constants[declaration._normalizedIdentifiers[0]] = declaration
			self.AddDeclaredItem(declaration)

		def parameter(
			identifier:        str,
			typeName:          str,
			defaultExpression: Nullable[ExpressionUnion] = None
		) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a constant parameter of mode ``in``.

			:param identifier:        The parameter's identifier.
			:param typeName:          The name of the parameter's type.
			:param defaultExpression: Optional, the default value. Default: ``None``, no default value.
			:returns:                 The parameter.
			"""
			return self._InParameter((identifier, ), self._TypeMark(typeName), defaultExpression)

		def signal(identifier: str, mode: Mode, typeName: str) -> ParameterSimpleSignalInterfaceItem:
			"""
			Nested function creating a signal parameter.

			:param identifier: The parameter's identifier.
			:param mode:       The parameter's mode.
			:param typeName:   The name of the parameter's type.
			:returns:          The parameter.
			"""
			return ParameterSimpleSignalInterfaceItem((identifier, ), mode, self._TypeMark(typeName))

		def variable(identifier: str, mode: Mode, typeName: str) -> ParameterVariableInterfaceItem:
			"""
			Nested function creating a variable parameter.

			:param identifier: The parameter's identifier.
			:param mode:       The parameter's mode.
			:param typeName:   The name of the parameter's type.
			:returns:          The parameter.
			"""
			return ParameterVariableInterfaceItem((identifier, ), mode, self._TypeMark(typeName))

		def text(identifier: str, value: str = "") -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a constant parameter of type ``STRING`` with a default value.

			:param identifier: The parameter's identifier.
			:param value:      Optional, the default value. Default: ``""``.
			:returns:          The parameter.
			"""
			return parameter(identifier, "STRING", StringLiteral(value))

		def flags(value: str, *identifiers: str) -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating constant parameters of type ``BOOLEAN`` with the same default value.

			:param value:       The default value, ``TRUE`` or ``FALSE``.
			:param identifiers: The identifiers of the parameters, in declaration order.
			:returns:           The parameters.
			"""
			return tuple(parameter(identifier, "BOOLEAN", name(value)) for identifier in identifiers)

		def severity() -> ParameterConstantInterfaceItem:
			"""
			Nested function creating the parameter ``MsgSeverity`` of type ``SEVERITY_LEVEL`` with the default ``WARNING``.

			:returns: The parameter.
			"""
			return parameter("MsgSeverity", "SEVERITY_LEVEL", name("WARNING"))

		def messages() -> tuple[ParameterConstantInterfaceItem, ...]:
			"""
			Nested function creating the parameters ``HeaderMsg`` (default ``" "``), ``XOn`` and ``MsgOn`` (default ``TRUE``)
			and ``MsgSeverity`` (default ``WARNING``) of a timing check.

			:returns: The parameters.
			"""
			return text("HeaderMsg", " "), *flags("TRUE", "XOn", "MsgOn"), severity()

		def scheduleData(isVector: bool) -> ParameterVariableInterfaceItem:
			"""
			Nested function creating the variable parameter ``ScheduleDataArray`` or ``ScheduleData`` of mode ``inout``.

			:param isVector: ``True`` for ``ScheduleDataArray`` of type ``VitalMemoryScheduleDataVectorType``, ``False``
			                 for ``ScheduleData`` of type ``VitalMemoryScheduleDataType``.
			:returns:        The parameter.
			"""
			if isVector:
				return variable("ScheduleDataArray", Mode.InOut, "VitalMemoryScheduleDataVectorType")

			return variable("ScheduleData", Mode.InOut, "VitalMemoryScheduleDataType")

		def checkedSignal(
			identifier:      str,
			delayIdentifier: str,
			isVector:        bool
		) -> tuple[ParameterSimpleSignalInterfaceItem, ParameterConstantInterfaceItem, ParameterConstantInterfaceItem]:
			"""
			Nested function creating the parameters of a checked signal: the signal of mode ``in``, its name (default ``""``)
			and its delay.

			:param identifier:      The identifier of the signal, e.g. ``TestSignal``.
			:param delayIdentifier: The identifier of the delay, e.g. ``TestDelay``.
			:param isVector:        ``True`` for a ``std_logic_vector`` signal with delays of type ``VitalDelayArrayType``,
			                        ``False`` for a ``std_ulogic`` signal with a delay of type ``TIME`` (default ``0 ns``).
			:returns:               The parameters.
			"""
			if isVector:
				return (
					signal(identifier, Mode.In, "std_logic_vector"),
					text(f"{identifier}Name"),
					parameter(delayIdentifier, "VitalDelayArrayType")
				)

			return (
				signal(identifier, Mode.In, "std_ulogic"),
				text(f"{identifier}Name"),
				parameter(delayIdentifier, "TIME", PhysicalIntegerLiteral(0, "ns"))
			)

		def arc() -> tuple[ParameterConstantInterfaceItem, ParameterConstantInterfaceItem]:
			"""
			Nested function creating the parameters ``ArcType`` (default ``CrossArc``) and ``NumBitsPerSubWord`` (default
			``1``) of a timing check.

			:returns: The parameters.
			"""
			return (
				parameter("ArcType", "VitalMemoryArcType", name("CrossArc")),
				parameter("NumBitsPerSubWord", "INTEGER", IntegerLiteral(1))
			)

		def procedure(
			identifier:     str,
			parameterItems: Iterable[
				ParameterConstantInterfaceItem | ParameterSimpleSignalInterfaceItem | ParameterVariableInterfaceItem
			]
		) -> None:
			"""
			Nested function declaring a procedure of this package.

			:param identifier:     The procedure's identifier.
			:param parameterItems: The parameters, in declaration order.
			"""
			self._DeclareSubprogram(Procedure(identifier, parameterItems=parameterItems), self._procedures)

		# Kinds, X01 arrays, schedule and timing data, port flags
		enumeration("VitalMemoryArcType", "ParallelArc", "CrossArc", "SubwordArc")
		enumeration("OutputRetainBehaviorType", "BitCorrupt", "WordCorrupt")
		enumeration("VitalMemoryMsgFormatType", "Vector", "Scalar", "VectorEnum")
		arrayType("X01ArrayT", "X01")
		accessType("X01ArrayPT", "X01ArrayT")
		accessType("VitalMemoryViolationType", "X01ArrayT")
		constant("DefaultNumBitsPerSubword", "INTEGER", NegationExpression(IntegerLiteral(1)))
		record(
			"VitalMemoryScheduleDataType",
			("OutputData", "std_ulogic"), ("NumBitsPerSubWord", "INTEGER"), ("ScheduleTime", "TIME"),
			("ScheduleValue", "std_ulogic"), ("LastOutputValue", "std_ulogic"), ("PropDelay", "TIME"),
			("OutputRetainDelay", "TIME"), ("InputAge", "TIME")
		)
		record(
			"VitalMemoryTimingDataType",
			("NotFirstFlag", "BOOLEAN"), ("RefLast", "X01"), ("RefTime", "TIME"), ("HoldEn", "BOOLEAN"),
			("TestLast", "std_ulogic"), ("TestTime", "TIME"), ("SetupEn", "BOOLEAN"), ("TestLastA", "VitalLogicArrayPT"),
			("TestTimeA", "VitalTimeArrayPT"), ("RefLastA", "X01ArrayPT"), ("RefTimeA", "VitalTimeArrayPT"),
			("HoldEnA", "VitalBoolArrayPT"), ("SetupEnA", "VitalBoolArrayPT")
		)
		arrayType("VitalPeriodDataArrayType", "VitalPeriodDataType")
		arrayType("VitalMemoryScheduleDataVectorType", "VitalMemoryScheduleDataType")
		enumeration("VitalPortStateType", "UNDEF", "READ", "WRITE", "CORRUPT", "HIGHZ")
		record(
			"VitalPortFlagType",
			("MemoryCurrent", "VitalPortStateType"), ("MemoryPrevious", "VitalPortStateType"),
			("DataCurrent", "VitalPortStateType"), ("DataPrevious", "VitalPortStateType"), ("OutputDisable", "BOOLEAN")
		)
		constant("VitalDefaultPortFlag", "VitalPortFlagType", Aggregate([
			NamedAggregateElement(RecordElementSymbol(SimpleName(element)), name(value)) for element, value in (
				("MemoryCurrent",  "READ"),
				("MemoryPrevious", "UNDEF"),
				("DataCurrent",    "READ"),
				("DataPrevious",   "UNDEF"),
				("OutputDisable",  "FALSE")
			)
		]))
		arrayType("VitalPortFlagVectorType", "VitalPortFlagType")

		# Path delays
		procedure("VitalMemoryInitPathDelay", (
			scheduleData(True),
			variable("OutputDataArray", Mode.In, "STD_LOGIC_VECTOR"),
			parameter("NumBitsPerSubWord", "INTEGER", name("DefaultNumBitsPerSubword"))
		))
		procedure("VitalMemoryInitPathDelay", (scheduleData(False), variable("OutputData", Mode.In, "STD_ULOGIC")))
		for suffix in ("", "01", "01Z", "01ZX"):
			hasRetain = suffix in ("01Z", "01ZX")
			for isScheduleVector, isInputVector, isConditionArray in (
				(False, False, False),
				(True,  False, False),
				(True,  False, True),
				(False, True,  False),
				(True,  True,  False),
				(True,  True,  True)
			):
				if isInputVector:
					inputSignal =     signal("InputSignal", Mode.In, "STD_LOGIC_VECTOR")
					inputChangeTime = variable("InputChangeTimeArray", Mode.InOut, "VitalTimeArrayT")
				else:
					inputSignal =     signal("InputSignal", Mode.In, "STD_ULOGIC")
					inputChangeTime = variable("InputChangeTime", Mode.InOut, "Time")

				if isScheduleVector or isInputVector:
					pathDelay = parameter("PathDelayArray", f"VitalDelayArrayType{suffix}")
				else:
					pathDelay = parameter("PathDelay", f"VitalDelayType{suffix}")

				if isConditionArray:
					pathCondition = parameter("PathConditionArray", "VitalBoolArrayT")
				else:
					pathCondition = parameter("PathCondition", "BOOLEAN", name("TRUE"))

				procedure("VitalMemoryAddPathDelay", (
					scheduleData(isScheduleVector),
					inputSignal,
					text("OutputSignalName"),
					inputChangeTime,
					pathDelay,
					parameter("ArcType", "VitalMemoryArcType", name("CrossArc")),
					pathCondition,
					*(flags("FALSE", "OutputRetainFlag") if hasRetain else ()),
					*(
						(parameter("OutputRetainBehavior", "OutputRetainBehaviorType", name("BitCorrupt")), )
						if hasRetain and isInputVector else ()
					)
				))

		for outputType, portFlag, isScheduleVector in (
			("std_logic_vector", parameter("PortFlag", "VitalPortFlagType", name("VitalDefaultPortFlag")), True),
			("std_logic_vector", parameter("PortFlag", "VitalPortFlagVectorType"),                         True),
			("std_ulogic",       parameter("PortFlag", "VitalPortFlagType", name("VitalDefaultPortFlag")), False)
		):
			procedure("VitalMemorySchedulePathDelay", (
				signal("OutSignal", Mode.Out, outputType),
				text("OutputSignalName"),
				portFlag,
				parameter("OutputMap", "VitalOutputMapType", name("VitalDefaultOutputMap")),
				scheduleData(isScheduleVector)
			))

		# Timing checks
		self._DeclareSubprogram(
			Function("VitalMemoryTimingDataInit", self._TypeMark("VitalMemoryTimingDataType")),
			self._functions
		)

		setupHold = ("SetupHigh", "SetupLow", "HoldHigh", "HoldLow")
		enables =   ("EnableSetupOnTest", "EnableSetupOnRef", "EnableHoldOnRef", "EnableHoldOnTest")
		procedure("VitalMemorySetupHoldCheck", (
			variable("Violation", Mode.Out, "X01ArrayT"),
			variable("TimingData", Mode.InOut, "VitalMemoryTimingDataType"),
			*checkedSignal("TestSignal", "TestDelay", False),
			*checkedSignal("RefSignal", "RefDelay", False),
			*(parameter(identifier, "VitalDelayType") for identifier in setupHold),
			parameter("CheckEnabled", "VitalBoolArrayT"),
			parameter("RefTransition", "VitalEdgeSymbolType"),
			*messages(),
			*flags("TRUE", *enables)
		))
		for violationType, isReferenceVector, isCheckArray, hasArc in (
			("X01ArrayT", False, False, False),
			("X01ArrayT", False, True,  True),
			("X01ArrayT", True,  False, True),
			("X01ArrayT", True,  True,  True),
			("X01",       False, False, False)
		):
			if isCheckArray:
				checkEnabled = parameter("CheckEnabled", "VitalBoolArrayT")
			else:
				checkEnabled = parameter("CheckEnabled", "BOOLEAN", name("TRUE"))

			procedure("VitalMemorySetupHoldCheck", (
				variable("Violation", Mode.Out, violationType),
				variable("TimingData", Mode.InOut, "VitalMemoryTimingDataType"),
				*checkedSignal("TestSignal", "TestDelay", True),
				*checkedSignal("RefSignal", "RefDelay", isReferenceVector),
				*(parameter(identifier, "VitalDelayArrayType") for identifier in setupHold),
				checkEnabled,
				parameter("RefTransition", "VitalEdgeSymbolType"),
				*(arc() if hasArc else ()),
				*messages(),
				parameter("MsgFormat", "VitalMemoryMsgFormatType"),
				*flags("TRUE", *enables)
			))

		procedure("VitalMemorySetupHoldCheck", (
			variable("Violation", Mode.Out, "X01"),
			variable("TimingData", Mode.InOut, "VitalMemoryTimingDataType"),
			*checkedSignal("TestSignal", "TestDelay", True),
			*checkedSignal("RefSignal", "RefDelay", True),
			*(parameter(identifier, "VitalDelayArrayType") for identifier in setupHold),
			*flags("TRUE", "CheckEnabled"),
			parameter("RefTransition", "VitalEdgeSymbolType"),
			*messages(),
			*arc(),
			parameter("MsgFormat", "VitalMemoryMsgFormatType"),
			*flags("TRUE", *enables)
		))
		for violationType in ("X01ArrayT", "X01"):
			procedure("VitalMemoryPeriodPulseCheck", (
				variable("Violation", Mode.Out, violationType),
				variable("PeriodData", Mode.InOut, "VitalPeriodDataArrayType"),
				*checkedSignal("TestSignal", "TestDelay", True),
				*(parameter(identifier, "VitalDelayArrayType") for identifier in ("Period", "PulseWidthHigh", "PulseWidthLow")),
				*flags("TRUE", "CheckEnabled"),
				*messages(),
				parameter("MsgFormat", "VitalMemoryMsgFormatType")
			))

		# Memory, violation and port types
		arrayType("MemoryWordType", "UX01")
		accessType("MemoryWordPtr", "MemoryWordType")
		arrayType("MemoryArrayType", "MemoryWordPtr")
		accessType("MemoryArrayPtrType", "MemoryArrayType")
		record(
			"VitalMemoryArrayRecType",
			("NoOfWords", "POSITIVE"), ("NoOfBitsPerWord", "POSITIVE"), ("NoOfBitsPerSubWord", "POSITIVE"),
			("NoOfBitsPerEnable", "POSITIVE"), ("MemoryArrayPtr", "MemoryArrayPtrType")
		)
		accessType("VitalMemoryDataType", "VitalMemoryArrayRecType")
		arrayType("VitalTimingDataVectorType", "VitalTimingDataType")
		arrayType("VitalMemoryViolFlagSizeType", "INTEGER")
		self._DeclareItem(EnumeratedType("VitalMemorySymbolType", [
			CharacterEnumerationLiteral(literal) for literal in "/\\PNrfpnRF^vEAD*X01-BZSguiGUIwscldeCLMmt"
		]), self._types)
		arrayType("VitalMemoryTableType", "VitalMemorySymbolType", 2)
		self._DeclareItem(EnumeratedType("VitalMemoryViolationSymbolType", [
			CharacterEnumerationLiteral(literal) for literal in "X0-"
		]), self._types)
		arrayType("VitalMemoryViolationTableType", "VitalMemoryViolationSymbolType", 2)
		enumeration("VitalPortType", "UNDEF", "READ", "WRITE", "RDNWR")
		enumeration(
			"VitalCrossPortModeType",
			"CpRead", "WriteContention", "ReadWriteContention", "CpReadAndWriteContention", "CpReadAndReadContention"
		)
		self._DeclareItem(Subtype("VitalAddressValueType", self._TypeMark("INTEGER")), self._subtypes)
		arrayType("VitalAddressValueVectorType", "VitalAddressValueType")

		# Memory declaration, table, cross ports, violation
		for sizes in (("NoOfWords", "NoOfBitsPerWord", "NoOfBitsPerSubWord"), ("NoOfWords", "NoOfBitsPerWord")):
			self._DeclareSubprogram(Function(
				"VitalDeclareMemory",
				self._TypeMark("VitalMemoryDataType"),
				isPure=False,
				parameterItems=(
					*(parameter(identifier, "POSITIVE") for identifier in sizes),
					parameter("MemoryLoadFile", "string", StringLiteral("")),
					*flags("FALSE", "BinaryLoadFile")
				)
			), self._functions)

		for portFlag, buses in (
			("PortFlag",      ("Controls", "DataInBus", "AddressBus")),
			("PortFlagArray", ("Controls", "EnableBus", "DataInBus", "AddressBus"))
		):
			procedure("VitalMemoryTable", (
				variable("DataOutBus", Mode.InOut, "std_logic_vector"),
				variable("MemoryData", Mode.InOut, "VitalMemoryDataType"),
				*(variable(f"Prev{bus}", Mode.InOut, "std_logic_vector") for bus in buses),
				variable(portFlag, Mode.InOut, "VitalPortFlagVectorType"),
				*(parameter(bus, "std_logic_vector") for bus in buses),
				variable("AddressValue", Mode.InOut, "VitalAddressValueType"),
				parameter("MemoryTable", "VitalMemoryTableType"),
				parameter("PortType", "VitalPortType", name("UNDEF")),
				text("PortName"),
				text("HeaderMsg"),
				*flags("TRUE", "MsgOn"),
				severity()
			))

		procedure("VitalMemoryCrossPorts", (
			variable("DataOutBus", Mode.InOut, "std_logic_vector"),
			variable("MemoryData", Mode.InOut, "VitalMemoryDataType"),
			variable("SamePortFlag", Mode.InOut, "VitalPortFlagVectorType"),
			parameter("SamePortAddressValue", "VitalAddressValueType"),
			parameter("CrossPortFlagArray", "VitalPortFlagVectorType"),
			parameter("CrossPortAddressArray", "VitalAddressValueVectorType"),
			parameter("CrossPortMode", "VitalCrossPortModeType", name("CpReadAndWriteContention")),
			text("PortName"),
			text("HeaderMsg"),
			*flags("TRUE", "MsgOn")
		))
		procedure("VitalMemoryCrossPorts", (
			variable("MemoryData", Mode.InOut, "VitalMemoryDataType"),
			parameter("CrossPortFlagArray", "VitalPortFlagVectorType"),
			parameter("CrossPortAddressArray", "VitalAddressValueVectorType"),
			text("HeaderMsg"),
			*flags("TRUE", "MsgOn")
		))
		for violationArrays in (
			(("ViolationFlagsArray", "X01ArrayT"), ("ViolationSizesArray", "VitalMemoryViolFlagSizeType")),
			()
		):
			procedure("VitalMemoryViolation", (
				variable("DataOutBus", Mode.InOut, "std_logic_vector"),
				variable("MemoryData", Mode.InOut, "VitalMemoryDataType"),
				variable("PortFlag", Mode.InOut, "VitalPortFlagVectorType"),
				parameter("DataInBus", "std_logic_vector"),
				parameter("AddressValue", "VitalAddressValueType"),
				parameter("ViolationFlags", "std_logic_vector"),
				*(parameter(identifier, typeName) for identifier, typeName in violationArrays),
				parameter("ViolationTable", "VitalMemoryTableType"),
				parameter("PortType", "VitalPortType"),
				text("PortName"),
				text("HeaderMsg"),
				*flags("TRUE", "MsgOn"),
				severity()
			))


@export
class VITAL_Memory_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.VITAL_Memory``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``VITAL_Memory`` package body.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.VITAL_Timing.all", ))
		self._AddPackageClause(("IEEE.VITAL_Primitives.all", ))

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))
