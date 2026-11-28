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
"""This module contains the predefined package ``ieee.float_pkg`` of VHDL library ``IEEE``."""

from pyTooling.Decorators    import export

from pyVHDLModel             import VHDLVersion
from pyVHDLModel.Name        import SimpleName, SelectedName
from pyVHDLModel.Symbol      import PackageReferenceSymbol, SimpleObjectOrFunctionCallSymbol, \
                                    IndexedObjectOrFunctionCallSymbol
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Predefined  import PredefinedPackageInstantiation


@export
class Float_Pkg(PredefinedPackageInstantiation):
	"""
	Predefined package ``ieee.float_pkg`` (IEEE Std 1076-2008, 16.11).

	It instantiates ``ieee.float_generic_pkg``:

	.. code-block:: VHDL

	   package float_pkg is new IEEE.float_generic_pkg
	     generic map (
	       float_exponent_width => 8,
	       float_fraction_width => 23,
	       float_round_style    => IEEE.fixed_float_types.round_nearest,
	       float_denormalize    => true,
	       float_check_error    => true,
	       float_guard_bits     => 3,
	       no_warning           => false,
	       fixed_pkg            => IEEE.fixed_pkg
	     );
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``float_pkg`` package instantiation.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		def name(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating a simple name in an expression.

			It names an enumeration literal, e.g. ``true``.

			:param identifier: The identifier.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		super().__init__(
			vhdlVersion,
			PackageReferenceSymbol(SelectedName("float_generic_pkg", SimpleName("IEEE"))),
			(
				GenericAssociationItem(SimpleName("float_exponent_width"), IntegerLiteral(8)),
				GenericAssociationItem(SimpleName("float_fraction_width"), IntegerLiteral(23)),
				GenericAssociationItem(SimpleName("float_round_style"),    IndexedObjectOrFunctionCallSymbol(
					SelectedName("round_nearest", SelectedName("fixed_float_types", SimpleName("IEEE")))
				)),
				GenericAssociationItem(SimpleName("float_denormalize"),    name("true")),
				GenericAssociationItem(SimpleName("float_check_error"),    name("true")),
				GenericAssociationItem(SimpleName("float_guard_bits"),     IntegerLiteral(3)),
				GenericAssociationItem(SimpleName("no_warning"),           name("false")),
				GenericAssociationItem(SimpleName("fixed_pkg"),            IndexedObjectOrFunctionCallSymbol(
					SelectedName("fixed_pkg", SimpleName("IEEE"))
				))
			)
		)

		self._AddLibraryClause(("ieee", ))
