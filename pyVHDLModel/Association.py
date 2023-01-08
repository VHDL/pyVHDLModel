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

Associations are used in generic maps, port maps and parameter maps.
"""
from typing import Optional as Nullable

from pyTooling.Decorators import export

from pyVHDLModel.Base import ModelEntity, ExpressionUnion
from pyVHDLModel.Symbol import Symbol


@export
class AssociationItem(ModelEntity):
	_formal: Nullable[Symbol]
	_actual: ExpressionUnion

	def __init__(self, actual: ExpressionUnion, formal: Symbol = None):
		super().__init__()

		self._formal = formal
		if formal is not None:
			formal._parent = self

		self._actual = actual
		# actual._parent = self  # FIXME: actual is provided as None

	@property
	def Formal(self) -> Nullable[Symbol]:  # TODO: can also be a conversion function !!
		return self._formal

	@property
	def Actual(self) -> ExpressionUnion:
		return self._actual

	def __str__(self):
		if self._formal is None:
			return str(self._actual)
		else:
			return "{formal!s} => {actual!s}".format(formal=self._formal, actual=self._actual)


@export
class GenericAssociationItem(AssociationItem):
	pass


@export
class PortAssociationItem(AssociationItem):
	pass


@export
class ParameterAssociationItem(AssociationItem):
	pass
