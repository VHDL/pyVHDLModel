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
# Derived from the package declaration of STD_LOGIC_TEXTIO by Synopsys, Inc.:                                          #
#                                                                                                                      #
#   Copyright (c) 1990, 1991, 1992 by Synopsys, Inc.  All rights reserved.                                             #
#                                                                                                                      #
#   This source file may be used and distributed without restriction                                                   #
#   provided that this copyright statement is not removed from the file                                                #
#   and that any derivative work contains this copyright notice.                                                       #
# ==================================================================================================================== #
#
"""
This module contains the predefined package ``ieee.std_logic_textio`` and its Synopsys variant of VHDL library
``IEEE``.
"""

from typing                 import Iterable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Procedure
from pyVHDLModel.Predefined import PredefinedPackage


@export
class Std_Logic_TextIO(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_textio``.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_textio`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_Logic_TextIO_Synopsys(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_textio``.

	It overloads the procedures ``read`` and ``write`` of ``std.textio`` for ``std_ulogic``, ``std_ulogic_vector`` and
	``std_logic_vector``, and declares ``hread``, ``hwrite``, ``oread`` and ``owrite`` for the vectors: 21 procedures.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``std_logic_textio`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(vhdlVersion, "Std_Logic_TextIO")

		self._AddPackageClause(("STD.textio.all", ))

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

		def procedure(
			identifier:     str,
			parameterItems: Iterable[ParameterConstantInterfaceItem | ParameterVariableInterfaceItem]
		) -> None:
			"""
			Nested function declaring a procedure of this package.

			:param identifier:     The procedure's identifier.
			:param parameterItems: The parameters, in declaration order.
			"""
			self._DeclareSubprogram(Procedure(identifier, parameterItems=parameterItems), self._procedures)

		def reads(identifier: str, typeName: str) -> None:
			"""
			Nested function declaring a read procedure without and with parameter ``GOOD``.

			:param identifier: The procedure's identifier, e.g. ``read`` or ``hread``.
			:param typeName:   The name of the type of parameter ``VALUE``.
			"""
			procedure(identifier, (self._LineParameter(), self._OutParameter(("VALUE", ), self._TypeMark(typeName))))
			procedure(identifier, (
				self._LineParameter(),
				self._OutParameter(("VALUE", ), self._TypeMark(typeName)),
				self._OutParameter(("GOOD", ), self._TypeMark("boolean"))
			))

		def write(identifier: str, typeName: str) -> None:
			"""
			Nested function declaring a write procedure.

			:param identifier: The procedure's identifier, e.g. ``write`` or ``hwrite``.
			:param typeName:   The name of the type of parameter ``VALUE``.
			"""
			procedure(identifier, (
				self._LineParameter(),
				self._InParameter(("VALUE", ), self._TypeMark(typeName)),
				*self._JustificationParameters()
			))

		reads("read", "std_ulogic")
		reads("read", "std_ulogic_vector")
		write("write", "std_ulogic")
		write("write", "std_ulogic_vector")
		reads("read", "std_logic_vector")
		write("write", "std_logic_vector")
		for readIdentifier, writeIdentifier in (("hread", "hwrite"), ("oread", "owrite")):
			for vectorType in ("std_ulogic_vector", "std_logic_vector"):
				reads(readIdentifier, vectorType)
				write(writeIdentifier, vectorType)
