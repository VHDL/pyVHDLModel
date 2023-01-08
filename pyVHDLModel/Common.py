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
from typing import List, Iterable, Optional as Nullable

from pyTooling.Decorators import export

from pyVHDLModel.Base import ModelEntity, LabeledEntityMixin, ExpressionUnion, Direction
from pyVHDLModel.Symbol import NewSymbol
from pyVHDLModel.Association import ParameterAssociationItem


@export
class Range(ModelEntity):
	_leftBound:  ExpressionUnion
	_rightBound: ExpressionUnion
	_direction:  Direction

	def __init__(self, leftBound: ExpressionUnion, rightBound: ExpressionUnion, direction: Direction):
		super().__init__()

		self._leftBound = leftBound
		leftBound._parent = self

		self._rightBound = rightBound
		rightBound._parent = self

		self._direction = direction

	@property
	def LeftBound(self) -> ExpressionUnion:
		return self._leftBound

	@property
	def RightBound(self) -> ExpressionUnion:
		return self._rightBound

	@property
	def Direction(self) -> Direction:
		return self._direction

	def __str__(self) -> str:
		return "{leftBound!s} {direction!s} {rightBound!s}".format(
			leftBound=self._leftBound,
			direction=self._direction,
			rightBound=self._rightBound,
		)


@export
class BaseChoice(ModelEntity):
	"""A ``Choice`` is a base-class for all choices."""


@export
class BaseCase(ModelEntity):
	"""
	A ``Case`` is a base-class for all cases.
	"""


@export
class MixinConditional:
	"""A ``BaseConditional`` is a mixin-class for all statements with a condition."""

	_condition: ExpressionUnion

	def __init__(self, condition: ExpressionUnion = None):
		self._condition = condition
		if condition is not None:
			condition._parent = self

	@property
	def Condition(self) -> ExpressionUnion:
		return self._condition


@export
class MixinBranch:
	"""A ``BaseBranch`` is a mixin-class for all statements with branches."""

	def __init__(self):
		pass


@export
class MixinConditionalBranch(MixinBranch, MixinConditional):
	"""A ``BaseBranch`` is a mixin-class for all branch statements with a condition."""
	def __init__(self, condition: ExpressionUnion):
		super().__init__()
		MixinConditional.__init__(self, condition)


@export
class MixinIfBranch(MixinConditionalBranch):
	"""A ``BaseIfBranch`` is a mixin-class for all if-branches."""


@export
class MixinElsifBranch(MixinConditionalBranch):
	"""A ``BaseElsifBranch`` is a mixin-class for all elsif-branches."""


@export
class MixinElseBranch(MixinBranch):
	"""A ``BaseElseBranch`` is a mixin-class for all else-branches."""


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
	_procedure:         NewSymbol  # TODO: implement a ProcedureSymbol
	_parameterMappings: List[ParameterAssociationItem]

	def __init__(self, procedureName: NewSymbol, parameterMappings: Iterable[ParameterAssociationItem] = None):
		self._procedure = procedureName
		procedureName._parent = self

		# TODO: extract to mixin
		self._parameterMappings = []
		if parameterMappings is not None:
			for parameterMapping in parameterMappings:
				self._parameterMappings.append(parameterMapping)
				parameterMapping._parent = self

	@property
	def Procedure(self) -> NewSymbol:
		return self._procedure

	@property
	def ParameterMappings(self) -> List[ParameterAssociationItem]:
		return self._parameterMappings


@export
class Assignment:
	"""An ``Assignment`` is a base-class for all assignment statements."""

	_target: NewSymbol

	def __init__(self, target: NewSymbol):
		self._target = target
		target._parent = self

	@property
	def Target(self) -> NewSymbol:
		return self._target


@export
class SignalAssignment(Assignment):
	"""An ``SignalAssignment`` is a base-class for all signal assignment statements."""


@export
class VariableAssignment(Assignment):
	"""An ``VariableAssignment`` is a base-class for all variable assignment statements."""
	# FIXME: move to sequential?
	_expression: ExpressionUnion

	def __init__(self, target: NewSymbol, expression: ExpressionUnion):
		super().__init__(target)

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression


@export
class MixinReportStatement:
	"""A ``MixinReportStatement`` is a mixin-class for all report and assert statements."""

	_message:  Nullable[ExpressionUnion]
	_severity: Nullable[ExpressionUnion]

	def __init__(self, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		self._message = message
		if message is not None:
			message._parent = self

		self._severity = severity
		if severity is not None:
			severity._parent = self

	@property
	def Message(self) -> Nullable[ExpressionUnion]:
		return self._message

	@property
	def Severity(self) -> Nullable[ExpressionUnion]:
		return self._severity


@export
class MixinAssertStatement(MixinReportStatement, MixinConditional):
	"""A ``MixinAssertStatement`` is a mixin-class for all assert statements."""

	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		super().__init__(message, severity)
		MixinConditional.__init__(self, condition)


class BlockStatementMixin:
	"""A ``BlockStatement`` is a mixin-class for all block statements."""

	def __init__(self):
		pass


@export
class WaveformElement(ModelEntity):
	_expression: ExpressionUnion
	_after: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, after: ExpressionUnion = None):
		super().__init__()

		self._expression = expression
		expression._parent = self

		self._after = after
		if after is not None:
			after._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	@property
	def After(self) -> Expression:
		return self._after
