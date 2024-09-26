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
# Copyright 2017-2024 Patrick Lehmann - Boetzingen, Germany                                                            #
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

Subprograms are procedures, functions and methods.
"""
from typing                 import List, Optional as Nullable

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Type       import Subtype, ProtectedType
from pyVHDLModel.Sequential import SequentialStatement


@export
class Subprogram(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	_genericItems:   List['GenericInterfaceItem']
	_parameterItems: List['ParameterInterfaceItem']
	_declaredItems:  List
	_statements:     List['SequentialStatement']
	_isPure:         bool

	def __init__(self, identifier: str, isPure: bool, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._genericItems =    []  # TODO: convert to dict
		self._parameterItems =  []  # TODO: convert to dict
		self._declaredItems =   []  # TODO: use mixin class
		self._statements =      []  # TODO: use mixin class
		self._isPure =          isPure

	@readonly
	def GenericItems(self) -> List['GenericInterfaceItem']:
		return self._genericItems

	@readonly
	def ParameterItems(self) -> List['ParameterInterfaceItem']:
		return self._parameterItems

	@readonly
	def DeclaredItems(self) -> List:
		return self._declaredItems

	@readonly
	def Statements(self) -> List['SequentialStatement']:
		return self._statements

	@readonly
	def IsPure(self) -> bool:
		return self._isPure


@export
class Procedure(Subprogram):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, False, documentation, parent)


@export
class Function(Subprogram):
	_returnType: Subtype

	def __init__(self, identifier: str, isPure: bool = True, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, isPure, documentation, parent)

		# FIXME: return type is missing

	@readonly
	def ReturnType(self) -> Subtype:
		return self._returnType


@export
class MethodMixin(metaclass=ExtendedType, mixin=True):
	"""A ``Method`` is a mixin class for all subprograms in a protected type."""

	_protectedType: ProtectedType

	def __init__(self, protectedType: ProtectedType) -> None:
		self._protectedType = protectedType
		protectedType._parent = self

	@readonly
	def ProtectedType(self) -> ProtectedType:
		return self._protectedType


@export
class ProcedureMethod(Procedure, MethodMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, protectedType: Nullable[ProtectedType] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, documentation, parent)
		MethodMixin.__init__(self, protectedType)


@export
class FunctionMethod(Function, MethodMixin):
	def __init__(self, identifier: str, isPure: bool = True, documentation: Nullable[str] = None, protectedType: Nullable[ProtectedType] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, isPure, documentation, parent)
		MethodMixin.__init__(self, protectedType)
