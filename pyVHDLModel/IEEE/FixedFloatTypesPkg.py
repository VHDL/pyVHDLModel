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
"""This module contains the predefined package ``ieee.fixed_float_types`` of VHDL library ``IEEE``."""

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Expression import EnumerationLiteral
from pyVHDLModel.Type       import EnumeratedType
from pyVHDLModel.Predefined import PredefinedPackage


@export
class Fixed_Float_Types(PredefinedPackage):
	"""
	Predefined package ``ieee.fixed_float_types`` (IEEE Std 1076-2008, 16.10 and 16.11).

	It declares the types of the generics of ``fixed_generic_pkg`` and ``float_generic_pkg``, in the order of the
	package:

	* ``fixed_round_style_type`` with the literals ``fixed_round`` and ``fixed_truncate``
	* ``fixed_overflow_style_type`` with the literals ``fixed_saturate`` and ``fixed_wrap``
	* ``round_type`` with the literals ``round_nearest``, ``round_inf``, ``round_neginf`` and ``round_zero``
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``fixed_float_types`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		for identifier, literals in (
			("fixed_round_style_type",    ("fixed_round", "fixed_truncate")),
			("fixed_overflow_style_type", ("fixed_saturate", "fixed_wrap")),
			("round_type",                ("round_nearest", "round_inf", "round_neginf", "round_zero"))
		):
			self._DeclareItem(
				EnumeratedType(identifier, [EnumerationLiteral(literal) for literal in literals]),
				self._types
			)
