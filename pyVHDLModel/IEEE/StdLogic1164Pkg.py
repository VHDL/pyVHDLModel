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
"""This module contains the predefined package ``ieee.std_logic_1164`` of VHDL library ``IEEE``."""

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import SimpleRange, Direction, Mode
from pyVHDLModel.Expression import CharacterEnumerationLiteral, CharacterLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, ResolutionFunctionSymbol
from pyVHDLModel.Type       import EnumeratedType, ArrayType, Subtype, MatchingOperatorsMixin
from pyVHDLModel.Interface  import ParameterSimpleSignalInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function, Operator, PredefinedOperation


@export
class StdULogic(EnumeratedType, MatchingOperatorsMixin):
	"""
	Represents the type ``std_ulogic`` of package ``ieee.std_logic_1164``.

	Its enumeration literals are ``'U'``, ``'X'``, ``'0'``, ``'1'``, ``'Z'``, ``'W'``, ``'L'``, ``'H'`` and ``'-'``.
	Besides the operations of an enumerated type, it declares the matching relational operators (IEEE Std 1076-2008,
	9.2.3). Its logical operators are explicit declarations of the package.
	"""

	def __init__(self) -> None:
		"""
		Initializes the type ``std_ulogic``.
		"""
		super().__init__("std_ulogic", [CharacterEnumerationLiteral(value) for value in "UX01ZWLH-"])

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this type declares implicitly: those of an enumerated type, then the matching relational
		operators ``"?="``, ``"?/="``, ``"?<"``, ``"?<="``, ``"?>"`` and ``"?>="``.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		operations.extend(self._CreateMatchingOperators())

		return operations


@export
class Std_Logic_1164(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_1164`` (IEEE Std 1076-2008, 16.7).

	Its declarations, in the order of the standard:

	* types ``std_ulogic`` and ``std_ulogic_vector``, the resolution function ``resolved``, subtypes ``std_logic``,
	  ``std_logic_vector``, ``x01``, ``x01z``, ``ux01`` and ``ux01z``
	* the logical operators of ``std_ulogic`` and ``std_ulogic_vector``, the shift operators of ``std_ulogic_vector``
	* the conversion functions ``to_bit``, ``to_bitvector``, ``to_stdulogic``, ``to_stdlogicvector`` and
	  ``to_stdulogicvector``, the aliases ``to_bit_vector``, ``to_bv``, ``to_std_logic_vector``, ``to_slv``,
	  ``to_std_ulogic_vector`` and ``to_sulv``, the functions ``to_01``, ``to_x01``, ``to_x01z`` and ``to_ux01``
	* the condition operator ``"??"``, ``rising_edge``, ``falling_edge`` and ``is_x``
	* the string conversions ``to_ostring``, ``to_hstring`` and their aliases (``to_bstring``, ``to_binary_string``,
	  ``to_octal_string``, ``to_hex_string``)
	* the procedures ``read``, ``write``, ``oread``, ``hread``, ``owrite`` and ``hwrite`` and their aliases (``bread``,
	  ``binary_read``, ``octal_read``, ``hex_read``, ``bwrite``, ``binary_write``, ``octal_write``, ``hex_write``)

	Each alias selects an overload by a signature, e.g. ``alias To_SLV is To_StdLogicVector [BIT_VECTOR return
	STD_LOGIC_VECTOR];``. ``to_bstring`` and ``to_binary_string`` alias the implicit ``to_string`` of
	``std_ulogic_vector``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_1164`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("STD.TEXTIO.all", ))

		stdULogic = StdULogic()
		self._DeclareItem(stdULogic, self._types)

		stdULogicVector = ArrayType("std_ulogic_vector", (self._TypeMark("natural"),), self._TypeMark("std_ulogic"))
		self._DeclareItem(stdULogicVector, self._types)

		self._DeclareSubprogram(
			Function("resolved", self._TypeMark("std_ulogic"), parameterItems=(
				self._InParameter(("s",), self._TypeMark("std_ulogic_vector")),
			)),
			self._functions
		)

		def resolved() -> ResolutionFunctionSymbol:
			"""
			Nested function creating the resolution function name ``resolved`` of a subtype indication.

			:returns: The resolution function name.
			"""
			return ResolutionFunctionSymbol(SimpleName("resolved"))

		stdLogic =           Subtype("std_logic", SimpleSubtypeSymbol(SimpleName("std_ulogic"), resolution=resolved()))
		stdLogic._baseType = stdULogic
		self._DeclareItem(stdLogic, self._subtypes)

		stdLogicVector =           Subtype("std_logic_vector", self._ElementResolvedTypeMark("std_ulogic_vector"))
		stdLogicVector._baseType = stdULogicVector
		self._DeclareItem(stdLogicVector, self._subtypes)

		for identifier, low, high in (
			("x01",   "X", "1"),
			("x01z",  "X", "Z"),
			("ux01",  "U", "1"),
			("ux01z", "U", "Z")
		):
			subtypeRange =      SimpleRange(CharacterLiteral(low), CharacterLiteral(high), Direction.To)
			typeMark =          ConstrainedScalarSubtypeSymbol(SimpleName("std_ulogic"), subtypeRange, resolution=resolved())
			subtype =           Subtype(identifier, typeMark)
			subtype._baseType = stdULogic
			self._DeclareItem(subtype, self._subtypes)

		logicalOperators = ("and", "nand", "or", "nor", "xor", "xnor")
		for operatorSymbol in logicalOperators:
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("ux01"), parameterItems=(
					self._InParameter(("l",), self._TypeMark("std_ulogic")),
					self._InParameter(("r",), self._TypeMark("std_ulogic"))
				)),
				self._functions
			)

		self._DeclareSubprogram(
			Operator("not", self._TypeMark("ux01"), parameterItems=(
				self._InParameter(("l",), self._TypeMark("std_ulogic")),
			)),
			self._functions
		)

		for operatorSymbol in logicalOperators:
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("std_ulogic_vector"), parameterItems=(
					self._InParameter(("l", "r"), self._TypeMark("std_ulogic_vector")),
				)),
				self._functions
			)

		self._DeclareSubprogram(
			Operator("not", self._TypeMark("std_ulogic_vector"), parameterItems=(
				self._InParameter(("l",), self._TypeMark("std_ulogic_vector")),
			)),
			self._functions
		)

		for operatorSymbol in logicalOperators:
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("std_ulogic_vector"), parameterItems=(
					self._InParameter(("l",), self._TypeMark("std_ulogic_vector")),
					self._InParameter(("r",), self._TypeMark("std_ulogic"))
				)),
				self._functions
			)
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("std_ulogic_vector"), parameterItems=(
					self._InParameter(("l",), self._TypeMark("std_ulogic")),
					self._InParameter(("r",), self._TypeMark("std_ulogic_vector"))
				)),
				self._functions
			)

		for operatorSymbol in logicalOperators:
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("std_ulogic"), parameterItems=(
					self._InParameter(("l",), self._TypeMark("std_ulogic_vector")),
				)),
				self._functions
			)

		for operatorSymbol in ("sll", "srl", "rol", "ror"):
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("std_ulogic_vector"), parameterItems=(
					self._InParameter(("l",), self._TypeMark("std_ulogic_vector")),
					self._InParameter(("r",), self._TypeMark("integer"))
				)),
				self._functions
			)

		for identifier, subtype, returnType in (
			("to_bit",       "std_ulogic",        "bit"),
			("to_bitvector", "std_ulogic_vector", "bit_vector")
		):
			self._DeclareSubprogram(
				Function(identifier, self._TypeMark(returnType), parameterItems=(
					self._InParameter(("s",), self._TypeMark(subtype)),
					self._InParameter(("xmap",), self._TypeMark("bit"), CharacterLiteral("0"))
				)),
				self._functions
			)

		for identifier, parameter, subtype, returnType in (
			("to_stdulogic",       "b", "bit",               "std_ulogic"),
			("to_stdlogicvector",  "b", "bit_vector",        "std_logic_vector"),
			("to_stdlogicvector",  "s", "std_ulogic_vector", "std_logic_vector"),
			("to_stdulogicvector", "b", "bit_vector",        "std_ulogic_vector"),
			("to_stdulogicvector", "s", "std_logic_vector",  "std_ulogic_vector")
		):
			self._DeclareSubprogram(
				Function(identifier, self._TypeMark(returnType), parameterItems=(
					self._InParameter((parameter,), self._TypeMark(subtype)),
				)),
				self._functions
			)

		for identifier in ("to_bit_vector", "to_bv"):
			self._DeclareAlias(
				identifier,
				"to_bitvector",
				(self._TypeMark("std_ulogic_vector"), self._TypeMark("bit")),
				self._TypeMark("bit_vector")
			)

		for identifier, name, subtype, returnType in (
			("to_std_logic_vector",  "to_stdlogicvector",  "bit_vector",        "std_logic_vector"),
			("to_slv",               "to_stdlogicvector",  "bit_vector",        "std_logic_vector"),
			("to_std_logic_vector",  "to_stdlogicvector",  "std_ulogic_vector", "std_logic_vector"),
			("to_slv",               "to_stdlogicvector",  "std_ulogic_vector", "std_logic_vector"),
			("to_std_ulogic_vector", "to_stdulogicvector", "bit_vector",        "std_ulogic_vector"),
			("to_sulv",              "to_stdulogicvector", "bit_vector",        "std_ulogic_vector"),
			("to_std_ulogic_vector", "to_stdulogicvector", "std_logic_vector",  "std_ulogic_vector"),
			("to_sulv",              "to_stdulogicvector", "std_logic_vector",  "std_ulogic_vector")
		):
			self._DeclareAlias(identifier, name, (self._TypeMark(subtype), ), self._TypeMark(returnType))

		for subtype, returnType in (
			("std_ulogic_vector", "std_ulogic_vector"),
			("std_ulogic",        "std_ulogic"),
			("bit_vector",        "std_ulogic_vector"),
			("bit",               "std_ulogic")
		):
			self._DeclareSubprogram(
				Function("to_01", self._TypeMark(returnType), parameterItems=(
					self._InParameter(("s",), self._TypeMark(subtype)),
					self._InParameter(("xmap",), self._TypeMark("std_ulogic"), CharacterLiteral("0"))
				)),
				self._functions
			)

		for identifier, scalarReturnType in (
			("to_x01",  "x01"),
			("to_x01z", "x01z"),
			("to_ux01", "ux01")
		):
			for parameter, subtype, returnType in (
				("s", "std_ulogic_vector", "std_ulogic_vector"),
				("s", "std_ulogic",        scalarReturnType),
				("b", "bit_vector",        "std_ulogic_vector"),
				("b", "bit",               scalarReturnType)
			):
				self._DeclareSubprogram(
					Function(identifier, self._TypeMark(returnType), parameterItems=(
						self._InParameter((parameter,), self._TypeMark(subtype)),
					)),
					self._functions
				)

		self._DeclareSubprogram(
			Operator("??", self._TypeMark("boolean"), parameterItems=(
				self._InParameter(("l",), self._TypeMark("std_ulogic")),
			)),
			self._functions
		)

		for identifier in ("rising_edge", "falling_edge"):
			self._DeclareSubprogram(
				Function(identifier, self._TypeMark("boolean"), parameterItems=(
					ParameterSimpleSignalInterfaceItem(("s",), Mode.In, self._TypeMark("std_ulogic")),
				)),
				self._functions
			)

		for subtype in ("std_ulogic_vector", "std_ulogic"):
			self._DeclareSubprogram(
				Function("is_x", self._TypeMark("boolean"), parameterItems=(
					self._InParameter(("s",), self._TypeMark(subtype)),
				)),
				self._functions
			)

		for identifier in ("to_bstring", "to_binary_string"):
			self._DeclareAlias(identifier, "to_string", (self._TypeMark("std_ulogic_vector"), ), self._TypeMark("string"))

		for identifier, aliasIdentifier in (
			("to_ostring", "to_octal_string"),
			("to_hstring", "to_hex_string")
		):
			self._DeclareSubprogram(
				Function(identifier, self._TypeMark("string"), parameterItems=(
					self._InParameter(("VALUE",), self._TypeMark("std_ulogic_vector")),
				)),
				self._functions
			)
			self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark("std_ulogic_vector"), ), self._TypeMark("string"))

		for subtype in ("std_ulogic", "std_ulogic_vector"):
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark(subtype)),
					self._OutParameter(("GOOD",), self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark(subtype))
				)),
				self._procedures
			)

		for subtype in ("std_ulogic", "std_ulogic_vector"):
			self._DeclareSubprogram(
				Procedure("write", parameterItems=(
					self._LineParameter(),
					self._InParameter(("VALUE",), self._TypeMark(subtype)),
					*self._JustificationParameters()
				)),
				self._procedures
			)

		for identifier in ("bread", "binary_read"):
			self._DeclareAlias(
				identifier,
				"read",
				(self._TypeMark("line"), self._TypeMark("std_ulogic_vector"), self._TypeMark("boolean"))
			)
			self._DeclareAlias(identifier, "read", (self._TypeMark("line"), self._TypeMark("std_ulogic_vector")))

		for identifier, aliasIdentifier in (
			("oread", "octal_read"),
			("hread", "hex_read")
		):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark("std_ulogic_vector")),
					self._OutParameter(("GOOD",), self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark("std_ulogic_vector"))
				)),
				self._procedures
			)
			self._DeclareAlias(
				aliasIdentifier,
				identifier,
				(self._TypeMark("line"), self._TypeMark("std_ulogic_vector"), self._TypeMark("boolean"))
			)
			self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark("line"), self._TypeMark("std_ulogic_vector")))

		for identifier in ("bwrite", "binary_write"):
			self._DeclareAlias(
				identifier,
				"write",
				(
					self._TypeMark("line"),
					self._TypeMark("std_ulogic_vector"),
					self._TypeMark("side"),
					self._TypeMark("width")
				)
			)

		for identifier, aliasIdentifier in (
			("owrite", "octal_write"),
			("hwrite", "hex_write")
		):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._InParameter(("VALUE",), self._TypeMark("std_ulogic_vector")),
					*self._JustificationParameters()
				)),
				self._procedures
			)
			self._DeclareAlias(
				aliasIdentifier,
				identifier,
				(
					self._TypeMark("line"),
					self._TypeMark("std_ulogic_vector"),
					self._TypeMark("side"),
					self._TypeMark("width")
				)
			)

@export
class Std_Logic_1164_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.std_logic_1164``.
	"""
