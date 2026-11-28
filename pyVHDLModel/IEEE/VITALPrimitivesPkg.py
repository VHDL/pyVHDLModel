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
"""This module contains the predefined package ``ieee.VITAL_Primitives`` of VHDL library ``IEEE``."""

from typing                 import Iterable, Optional as Nullable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import Direction, Mode, SimpleRange, ExpressionUnion
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleObjectOrFunctionCallSymbol, ConstrainedScalarSubtypeSymbol
from pyVHDLModel.Expression import CharacterLiteral
from pyVHDLModel.Type       import ArrayType, Subtype
from pyVHDLModel.Object     import DeferredConstant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterSimpleSignalInterfaceItem, \
                                   ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Function, Procedure
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class VITAL_Primitives(PredefinedPackage):
	"""
	Predefined package ``ieee.VITAL_Primitives`` (IEEE Std 1076.4-2000).

	It defines the logic primitives of ASIC models, each as a function (the value) and as a procedure (a signal assignment
	with the propagation delays). Its declarations, in the order of the package:

	* the subtypes ``VitalTruthSymbolType`` and ``VitalStateSymbolType``, the two-dimensional table types
	  ``VitalTruthTableType`` and ``VitalStateTableType``, the deferred constants ``VitalDefDelay01`` and
	  ``VitalDefDelay01Z``
	* the gates ``VitalAND``, ``VitalOR``, ``VitalXOR``, ``VitalNAND``, ``VitalNOR``, ``VitalXNOR`` of a vector and of 2,
	  3 and 4 inputs (``VitalAND2`` ...)
	* the buffers ``VitalBUF``, ``VitalBUFIF0``, ``VitalBUFIF1``, ``VitalIDENT`` and the inverters ``VitalINV``,
	  ``VitalINVIF0``, ``VitalINVIF1``
	* the multiplexers ``VitalMUX``, ``VitalMUX2``, ``VitalMUX4``, ``VitalMUX8`` and the decoders ``VitalDECODER``,
	  ``VitalDECODER2``, ``VitalDECODER4``, ``VitalDECODER8``
	* ``VitalTruthTable``, ``VitalStateTable`` and the procedure ``VitalResolve``

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.VITALPrimitivesPkg.VITAL_Primitives_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``VITAL_Primitives`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.VITAL_Timing.all", ))

		def name(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating a name in an expression.

			It names a constant, e.g. ``VitalDefDelay01`` or ``VitalDefaultResultMap``.

			:param identifier: The identifier.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		def parameter(
			identifiers:       Iterable[str],
			typeName:          str,
			defaultExpression: Nullable[ExpressionUnion] = None
		) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a constant parameter of mode ``in``.

			:param identifiers:       The parameter's identifiers.
			:param typeName:          The name of the parameter's type.
			:param defaultExpression: Optional, the default value. Default: ``None``, no default value.
			:returns:                 The parameter.
			"""
			return self._InParameter(identifiers, self._TypeMark(typeName), defaultExpression)

		def signal(identifiers: Iterable[str], mode: Mode, typeName: str) -> ParameterSimpleSignalInterfaceItem:
			"""
			Nested function creating a signal parameter.

			:param identifiers: The parameter's identifiers.
			:param mode:        The parameter's mode.
			:param typeName:    The name of the parameter's type.
			:returns:           The parameter.
			"""
			return ParameterSimpleSignalInterfaceItem(identifiers, mode, self._TypeMark(typeName))

		def variable(identifiers: Iterable[str], typeName: str) -> ParameterVariableInterfaceItem:
			"""
			Nested function creating a variable parameter of mode ``inout``.

			:param identifiers: The parameter's identifiers.
			:param typeName:    The name of the parameter's type.
			:returns:           The parameter.
			"""
			return ParameterVariableInterfaceItem(identifiers, Mode.InOut, self._TypeMark(typeName))

		def delay(identifier: str, suffix: str) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a propagation delay parameter of type ``VitalDelayType<suffix>`` with the default value
			``VitalDefDelay<suffix>``.

			:param identifier: The parameter's identifier, e.g. ``tpd_a_q``.
			:param suffix:     The suffix of the delay type, ``01`` or ``01Z``.
			:returns:          The parameter.
			"""
			return parameter((identifier, ), f"VitalDelayType{suffix}", name(f"VitalDefDelay{suffix}"))

		def resultMap(suffix: str) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating the parameter ``ResultMap`` of type ``VitalResult<suffix>MapType`` with the default value
			``VitalDefaultResult<suffix>Map``.

			:param suffix: The suffix of the result map type, ``""`` or ``Z``.
			:returns:      The parameter.
			"""
			return parameter(("ResultMap", ), f"VitalResult{suffix}MapType", name(f"VitalDefaultResult{suffix}Map"))

		def output(typeName: str = "std_ulogic") -> ParameterSimpleSignalInterfaceItem:
			"""
			Nested function creating the output signal parameter ``q`` of a procedure.

			:param typeName: Optional, the name of the output's type. Default: ``std_ulogic``.
			:returns:        The parameter.
			"""
			return signal(("q", ), Mode.Out, typeName)

		def function(
			identifier:     str,
			parameterItems: Iterable[ParameterConstantInterfaceItem],
			returnType:     str = "std_ulogic"
		) -> None:
			"""
			Nested function declaring a function of this package.

			:param identifier:     The function's identifier.
			:param parameterItems: The parameters, in declaration order.
			:param returnType:     Optional, the name of the return type. Default: ``std_ulogic``.
			"""
			self._DeclareSubprogram(
				Function(identifier, self._TypeMark(returnType), parameterItems=parameterItems),
				self._functions
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

		# Symbols, tables, default delays
		for identifier, low, high in (("VitalTruthSymbolType", "X", "Z"), ("VitalStateSymbolType", "/", "S")):
			self._DeclareItem(Subtype(identifier, ConstrainedScalarSubtypeSymbol(
				SimpleName("VitalTableSymbolType"),
				SimpleRange(CharacterLiteral(low), CharacterLiteral(high), Direction.To)
			)), self._subtypes)

		for identifier, elementType in (
			("VitalTruthTableType", "VitalTruthSymbolType"),
			("VitalStateTableType", "VitalStateSymbolType")
		):
			self._DeclareItem(ArrayType(
				identifier,
				(self._TypeMark("NATURAL"), self._TypeMark("NATURAL")),
				self._TypeMark(elementType)
			), self._types)

		for suffix in ("01", "01Z"):
			defaultDelay = DeferredConstant((f"VitalDefDelay{suffix}", ), self._TypeMark(f"VitalDelayType{suffix}"))
			self._deferredConstants[defaultDelay._normalizedIdentifiers[0]] = defaultDelay
			self.AddDeclaredItem(defaultDelay)

		# Gates of a vector and of 2, 3 and 4 inputs
		gates = ("AND", "OR", "XOR", "NAND", "NOR", "XNOR")
		for gate in gates:
			function(f"Vital{gate}", (parameter(("Data", ), "std_logic_vector"), resultMap("")))

		for gate in gates:
			procedure(f"Vital{gate}", (
				output(),
				signal(("Data", ), Mode.In, "std_logic_vector"),
				parameter(("tpd_data_q", ), "VitalDelayArrayType01"),
				resultMap("")
			))

		inputs = ("a", "b", "c", "d")
		for count in (2, 3, 4):
			for gate in gates:
				function(f"Vital{gate}{count}", (parameter(inputs[:count], "std_ulogic"), resultMap("")))

		for count in (2, 3, 4):
			for gate in gates:
				procedure(f"Vital{gate}{count}", (
					output(),
					signal(inputs[:count], Mode.In, "std_ulogic"),
					*(delay(f"tpd_{input}_q", "01") for input in inputs[:count]),
					resultMap("")
				))

		# Buffers and inverters
		for kind, hasIdentity in (("BUF", True), ("INV", False)):
			function(f"Vital{kind}", (parameter(("Data", ), "std_ulogic"), resultMap("")))
			for enable in ("0", "1"):
				function(f"Vital{kind}IF{enable}", (parameter(("Data", "Enable"), "std_ulogic"), resultMap("Z")))

			if hasIdentity:
				function("VitalIDENT", (parameter(("Data", ), "std_ulogic"), resultMap("Z")))

			procedure(f"Vital{kind}", (
				output(),
				signal(("a", ), Mode.In, "std_ulogic"),
				delay("tpd_a_q", "01"),
				resultMap("")
			))
			for enable in ("0", "1"):
				procedure(f"Vital{kind}IF{enable}", (
					output(),
					signal(("Data", ), Mode.In, "std_ulogic"),
					signal(("Enable", ), Mode.In, "std_ulogic"),
					delay("tpd_data_q", "01"),
					delay("tpd_enable_q", "01Z"),
					resultMap("Z")
				))

			if hasIdentity:
				procedure("VitalIDENT", (
					output(),
					signal(("a", ), Mode.In, "std_ulogic"),
					delay("tpd_a_q", "01Z"),
					resultMap("Z")
				))

		# Multiplexers
		multiplexers = (("4", "std_logic_vector4", "std_logic_vector2"), ("8", "std_logic_vector8", "std_logic_vector3"))
		function("VitalMUX", (
			parameter(("Data", ), "std_logic_vector"),
			parameter(("dSelect", ), "std_logic_vector"),
			resultMap("")
		))
		function("VitalMUX2", (
			parameter(("Data1", "Data0"), "std_ulogic"),
			parameter(("dSelect", ), "std_ulogic"),
			resultMap("")
		))
		for count, dataType, selectType in multiplexers:
			function(f"VitalMUX{count}", (
				parameter(("Data", ), dataType),
				parameter(("dSelect", ), selectType),
				resultMap("")
			))

		procedure("VitalMUX", (
			output(),
			signal(("Data", ), Mode.In, "std_logic_vector"),
			signal(("dSel", ), Mode.In, "std_logic_vector"),
			parameter(("tpd_data_q", ), "VitalDelayArrayType01"),
			parameter(("tpd_dsel_q", ), "VitalDelayArrayType01"),
			resultMap("")
		))
		procedure("VitalMUX2", (
			output(),
			signal(("d1", "d0"), Mode.In, "std_ulogic"),
			signal(("dSel", ), Mode.In, "std_ulogic"),
			delay("tpd_d1_q", "01"),
			delay("tpd_d0_q", "01"),
			delay("tpd_dsel_q", "01"),
			resultMap("")
		))
		for count, dataType, selectType in multiplexers:
			procedure(f"VitalMUX{count}", (
				output(),
				signal(("Data", ), Mode.In, dataType),
				signal(("dSel", ), Mode.In, selectType),
				parameter(("tpd_data_q", ), "VitalDelayArrayType01"),
				parameter(("tpd_dsel_q", ), "VitalDelayArrayType01"),
				resultMap("")
			))

		# Decoders
		decoders = (
			("",  "std_logic_vector",  "std_logic_vector"),
			("2", "std_ulogic",        "std_logic_vector2"),
			("4", "std_logic_vector2", "std_logic_vector4"),
			("8", "std_logic_vector3", "std_logic_vector8")
		)
		for suffix, dataType, resultType in decoders:
			function(f"VitalDECODER{suffix}", (
				parameter(("Data", ), dataType),
				parameter(("Enable", ), "std_ulogic"),
				resultMap("")
			), resultType)

		for suffix, dataType, resultType in decoders:
			procedure(f"VitalDECODER{suffix}", (
				output(resultType),
				signal(("Data", ), Mode.In, dataType),
				signal(("Enable", ), Mode.In, "std_ulogic"),
				delay("tpd_data_q", "01") if dataType == "std_ulogic" else parameter(("tpd_data_q", ), "VitalDelayArrayType01"),
				delay("tpd_enable_q", "01"),
				resultMap("")
			))

		# Truth and state tables, resolution
		for resultType in ("std_logic_vector", "std_logic"):
			function("VitalTruthTable", (
				parameter(("TruthTable", ), "VitalTruthTableType"),
				parameter(("DataIn", ), "std_logic_vector")
			), resultType)

		for resultType in ("std_logic_vector", "std_logic"):
			procedure("VitalTruthTable", (
				signal(("Result", ), Mode.Out, resultType),
				parameter(("TruthTable", ), "VitalTruthTableType"),
				signal(("DataIn", ), Mode.In, "std_logic_vector")
			))

		for resultType in ("std_logic_vector", "std_logic"):
			procedure("VitalStateTable", (
				variable(("Result", ), resultType),
				variable(("PreviousDataIn", ), "std_logic_vector"),
				parameter(("StateTable", ), "VitalStateTableType"),
				parameter(("DataIn", ), "std_logic_vector"),
				*((parameter(("NumStates", ), "NATURAL"), ) if resultType == "std_logic_vector" else ())
			))

		for resultType in ("std_logic_vector", "std_logic"):
			procedure("VitalStateTable", (
				signal(("Result", ), Mode.InOut, resultType),
				parameter(("StateTable", ), "VitalStateTableType"),
				signal(("DataIn", ), Mode.In, "std_logic_vector"),
				*((parameter(("NumStates", ), "NATURAL"), ) if resultType == "std_logic_vector" else ())
			))

		procedure("VitalResolve", (output(), signal(("Data", ), Mode.In, "std_logic_vector")))


@export
class VITAL_Primitives_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.VITAL_Primitives``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``VITAL_Primitives`` package body.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))
