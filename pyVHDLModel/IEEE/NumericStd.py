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
"""This module contains the predefined package ``ieee.numeric_std`` of VHDL library ``IEEE``."""

from pyTooling.Decorators   import export

from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Type       import ArrayType, Subtype


@export
class Numeric_Std(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_std``.

	Predefined types:

	* ``unresolved_unsigned``, ``unsigned``
	* ``unresolved_signed``, ``signed``
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``numeric_std`` package.
		"""
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

		unresolvedUnsigned = ArrayType("unresolved_unsigned", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		self._types[unresolvedUnsigned._normalizedIdentifier] = unresolvedUnsigned
		self._declaredItems.append(unresolvedUnsigned)

		unsigned = Subtype("unsigned", SimpleSubtypeSymbol(SimpleName("unresolved_unsigned")), None)
		unsigned._baseType = unresolvedUnsigned
		self._subtypes[unsigned._normalizedIdentifier] = unsigned
		self._declaredItems.append(unsigned)

		unresolvedSigned = ArrayType("unresolved_signed", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		self._types[unresolvedSigned._normalizedIdentifier] = unresolvedSigned
		self._declaredItems.append(unresolvedSigned)

		signed = Subtype("signed", SimpleSubtypeSymbol(SimpleName("unresolved_signed")), None)
		signed._baseType = unresolvedSigned
		self._subtypes[signed._normalizedIdentifier] = signed
		self._declaredItems.append(signed)


@export
class Numeric_Std_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_std``.
	"""
