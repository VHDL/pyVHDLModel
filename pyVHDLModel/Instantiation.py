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
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
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
"""
This module contains parts of an abstract document language model for VHDL.

Instantiations of packages, procedures, functions and protected types.
"""
from typing import List

from pyTooling.Decorators import export

from pyVHDLModel.Base import ModelEntity
from pyVHDLModel.DesignUnit import PrimaryUnit
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Symbol import PackageReferenceSymbol


@export
class GenericEntityInstantiation:
	def __init__(self):
		pass


@export
class SubprogramInstantiation(ModelEntity, GenericEntityInstantiation):
	def __init__(self):
		super().__init__()
		GenericEntityInstantiation.__init__(self)
		self._subprogramReference = None


@export
class ProcedureInstantiation(Procedure, SubprogramInstantiation):
	pass


@export
class FunctionInstantiation(Function, SubprogramInstantiation):
	pass


@export
class PackageInstantiation(PrimaryUnit, GenericEntityInstantiation):
	_packageReference: PackageReferenceSymbol
	_genericAssociations: List[GenericAssociationItem]

	def __init__(self, identifier: str, uninstantiatedPackage: PackageReferenceSymbol, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericEntityInstantiation.__init__(self)

		self._packageReference = uninstantiatedPackage
		# uninstantiatedPackage._parent = self    # FIXME: uninstantiatedPackage is provided as int

		# TODO: extract to mixin
		self._genericAssociations = []

	@property
	def PackageReference(self) -> PackageReferenceSymbol:
		return self._packageReference

	@property
	def GenericAssociations(self) -> List[GenericAssociationItem]:
		return self._genericAssociations
