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

from pyVHDLModel.Expression import CharacterEnumerationLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Type       import EnumeratedType, ArrayType, Subtype


@export
class Std_Logic_1164(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_1164``.

	Predefined types:

	* ``std_ulogic``, ``std_ulogic_vector``
	* ``std_logic``, ``std_logic_vector``
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_1164`` package.
		"""
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))

		stdULogic = EnumeratedType("std_ulogic", (
			CharacterEnumerationLiteral("U"),
			CharacterEnumerationLiteral("X"),
			CharacterEnumerationLiteral("0"),
			CharacterEnumerationLiteral("1"),
			CharacterEnumerationLiteral("Z"),
			CharacterEnumerationLiteral("W"),
			CharacterEnumerationLiteral("L"),
			CharacterEnumerationLiteral("H"),
			CharacterEnumerationLiteral("-"),
		), None)
		self._types[stdULogic._normalizedIdentifier] = stdULogic
		self._declaredItems.append(stdULogic)

		stdULogicVector = ArrayType("std_ulogic_vector", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		self._types[stdULogicVector._normalizedIdentifier] = stdULogicVector
		self._declaredItems.append(stdULogicVector)

		stdLogic = Subtype("std_logic", SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		stdLogic._baseType = stdULogic
		self._subtypes[stdLogic._normalizedIdentifier] = stdLogic
		self._declaredItems.append(stdLogic)

		stdLogicVector = Subtype("std_logic_vector", SimpleSubtypeSymbol(SimpleName("std_ulogic_vector")), None)
		stdLogicVector._baseType = stdULogicVector
		self._subtypes[stdLogicVector._normalizedIdentifier] = stdLogicVector
		self._declaredItems.append(stdLogicVector)


@export
class Std_Logic_1164_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.std_logic_1164``.
	"""
