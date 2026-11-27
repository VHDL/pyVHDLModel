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
"""This module contains the predefined package ``ieee.fixed_pkg`` of VHDL library ``IEEE``."""

from pyTooling.Decorators    import export

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Name        import SimpleName, SelectedName
from pyVHDLModel.Symbol      import PackageReferenceSymbol, SimpleObjectOrFunctionCallSymbol, \
                                    IndexedObjectOrFunctionCallSymbol
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Predefined  import PredefinedPackageInstantiation


@export
class Fixed_Pkg(PredefinedPackageInstantiation):
	"""
	Predefined package ``ieee.fixed_pkg`` (IEEE Std 1076-2008, 16.10).

	It instantiates ``ieee.fixed_generic_pkg``:

	.. code-block:: VHDL

	   package fixed_pkg is new IEEE.fixed_generic_pkg
	     generic map (
	       fixed_round_style    => IEEE.fixed_float_types.fixed_round,
	       fixed_overflow_style => IEEE.fixed_float_types.fixed_saturate,
	       fixed_guard_bits     => 3,
	       no_warning           => false
	     );
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``fixed_pkg`` package instantiation.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		def fixedFloatTypes(identifier: str) -> IndexedObjectOrFunctionCallSymbol:
			"""
			Nested function creating the name of an enumeration literal of ``ieee.fixed_float_types``.

			:param identifier: The literal's identifier.
			:returns:          The name ``IEEE.fixed_float_types.<identifier>``.
			"""
			return IndexedObjectOrFunctionCallSymbol(
				SelectedName(identifier, SelectedName("fixed_float_types", SimpleName("IEEE")))
			)

		super().__init__(
			vhdlVersion,
			PackageReferenceSymbol(SelectedName("fixed_generic_pkg", SimpleName("IEEE"))),
			(
				GenericAssociationItem(SimpleName("fixed_round_style"),    fixedFloatTypes("fixed_round")),
				GenericAssociationItem(SimpleName("fixed_overflow_style"), fixedFloatTypes("fixed_saturate")),
				GenericAssociationItem(SimpleName("fixed_guard_bits"),     IntegerLiteral(3)),
				GenericAssociationItem(
					SimpleName("no_warning"),
					SimpleObjectOrFunctionCallSymbol(SimpleName("false"))
				)
			)
		)

		self._AddLibraryClause(("IEEE", ))
