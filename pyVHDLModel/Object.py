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

Objects are constants, variables, signals and files.
"""
from typing import Iterable, Optional as Nullable

from pyTooling.Decorators import export

from pyVHDLModel.Symbol import Symbol
from pyVHDLModel.Base import ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin, ExpressionUnion


@export
class Obj(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	_subtype: Symbol

	def __init__(self, identifiers: Iterable[str], subtype: Symbol, documentation: str = None):
		super().__init__()
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> Symbol:
		return self._subtype


@export
class BaseConstant(Obj):
	pass


@export
class WithDefaultExpressionMixin:
	"""A ``WithDefaultExpression`` is a mixin class for all objects declarations accepting default expressions."""

	_defaultExpression: Nullable[ExpressionUnion]

	def __init__(self, defaultExpression: ExpressionUnion = None):
		self._defaultExpression = defaultExpression
		if defaultExpression is not None:
			defaultExpression._parent = self

	@property
	def DefaultExpression(self) -> Nullable[ExpressionUnion]:
		return self._defaultExpression


@export
class Constant(BaseConstant, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class DeferredConstant(BaseConstant):
	_constantReference: Constant

	def __init__(self, identifiers: Iterable[str], subtype: Symbol, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)

	@property
	def ConstantReference(self) -> Constant:
		return self._constantReference


@export
class Variable(Obj, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class SharedVariable(Obj):
	pass


@export
class Signal(Obj, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class File(Obj):
	pass
