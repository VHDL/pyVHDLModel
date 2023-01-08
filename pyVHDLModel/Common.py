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

Common definitions and MixIns are used by many classes in the model as base-classes.
"""
from typing                  import List, Iterable

from pyTooling.Decorators    import export

from pyVHDLModel.Base        import ModelEntity, LabeledEntityMixin, ExpressionUnion
from pyVHDLModel.Symbol      import Symbol
from pyVHDLModel.Association import ParameterAssociationItem


@export
class Statement(ModelEntity, LabeledEntityMixin):
	"""
	A ``Statement`` is a base-class for all statements.
	"""
	def __init__(self, label: str = None):
		super().__init__()
		LabeledEntityMixin.__init__(self, label)


@export
class ProcedureCall:
	_procedure:         Symbol  # TODO: implement a ProcedureSymbol
	_parameterMappings: List[ParameterAssociationItem]

	def __init__(self, procedureName: Symbol, parameterMappings: Iterable[ParameterAssociationItem] = None):
		self._procedure = procedureName
		procedureName._parent = self

		# TODO: extract to mixin
		self._parameterMappings = []
		if parameterMappings is not None:
			for parameterMapping in parameterMappings:
				self._parameterMappings.append(parameterMapping)
				parameterMapping._parent = self

	@property
	def Procedure(self) -> Symbol:
		return self._procedure

	@property
	def ParameterMappings(self) -> List[ParameterAssociationItem]:
		return self._parameterMappings


@export
class Assignment:
	"""An ``Assignment`` is a base-class for all assignment statements."""

	_target: Symbol

	def __init__(self, target: Symbol):
		self._target = target
		target._parent = self

	@property
	def Target(self) -> Symbol:
		return self._target


@export
class SignalAssignment(Assignment):
	"""An ``SignalAssignment`` is a base-class for all signal assignment statements."""


@export
class VariableAssignment(Assignment):
	"""An ``VariableAssignment`` is a base-class for all variable assignment statements."""
	# FIXME: move to sequential?
	_expression: ExpressionUnion

	def __init__(self, target: Symbol, expression: ExpressionUnion):
		super().__init__(target)

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression
