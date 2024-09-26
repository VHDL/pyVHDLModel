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

A helper class to implement namespaces and scopes.
"""
from typing               import TypeVar, Generic, Dict, Optional as Nullable

from pyTooling.Decorators import readonly

from pyVHDLModel.Object   import Obj, Signal, Constant, Variable
from pyVHDLModel.Symbol   import ComponentInstantiationSymbol, Symbol, PossibleReference
from pyVHDLModel.Type     import Subtype, FullType, BaseType

K = TypeVar("K")
O = TypeVar("O")


class Namespace(Generic[K, O]):
	_name:            str
	_parentNamespace: 'Namespace'
	_subNamespaces:   Dict[str, 'Namespace']
	_elements:        Dict[K, O]

	def __init__(self, name: str, parentNamespace: Nullable["Namespace"] = None) -> None:
		self._name = name
		self._parentNamespace = parentNamespace
		self._subNamespaces = {}
		self._elements = {}

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def ParentNamespace(self) -> 'Namespace':
		return self._parentNamespace

	@ParentNamespace.setter
	def ParentNamespace(self, value: 'Namespace'):
		self._parentNamespace = value
		value._subNamespaces[self._name] = self

	@readonly
	def SubNamespaces(self) -> Dict[str, 'Namespace']:
		return self._subNamespaces

	def Elements(self) -> Dict[K, O]:
		return self._elements

	def FindComponent(self, componentSymbol: ComponentInstantiationSymbol) -> 'Component':
		from pyVHDLModel.DesignUnit import Component

		try:
			element = self._elements[componentSymbol._name._normalizedIdentifier]
			if isinstance(element, Component):
				return element
			else:
				raise TypeError(f"Found element '{componentSymbol._name._identifier}', but it is not a component.")
		except KeyError:
			parentNamespace = self._parentNamespace
			if parentNamespace is None:
				raise KeyError(f"Component '{componentSymbol._name._identifier}' not found in '{self._name}'.")

			return parentNamespace.FindComponent(componentSymbol)

	def FindSubtype(self, subtypeSymbol: Symbol) -> BaseType:
		try:
			element = self._elements[subtypeSymbol._name._normalizedIdentifier]
			if isinstance(element, Subtype):
				if PossibleReference.Subtype in subtypeSymbol._possibleReferences:
					return element
				else:
					raise TypeError(f"Found subtype '{subtypeSymbol._name._identifier}', but it was not expected.")
			elif isinstance(element, FullType):
				if PossibleReference.Type in subtypeSymbol._possibleReferences:
					return element
				else:
					raise TypeError(f"Found type '{subtypeSymbol._name._identifier}', but it was not expected.")
			else:
				raise TypeError(f"Found element '{subtypeSymbol._name._identifier}', but it is not a type or subtype.")
		except KeyError:
			parentNamespace = self._parentNamespace
			if parentNamespace is None:
				raise KeyError(f"Subtype '{subtypeSymbol._name._identifier}' not found in '{self._name}'.")

			return parentNamespace.FindSubtype(subtypeSymbol)

	def FindObject(self, objectSymbol: Symbol) -> Obj:
		try:
			element = self._elements[objectSymbol._name._normalizedIdentifier]
			if isinstance(element, Signal):
				if PossibleReference.Signal in objectSymbol._possibleReferences:
					return element
				elif PossibleReference.SignalAttribute in objectSymbol._possibleReferences:
					return element
				else:
					raise TypeError(f"Found signal '{objectSymbol._name._identifier}', but it was not expected.")
			elif isinstance(element, Constant):
				if PossibleReference.Constant in objectSymbol._possibleReferences:
					return element
				else:
					raise TypeError(f"Found constant '{objectSymbol._name._identifier}', but it was not expected.")
			elif isinstance(element, Variable):
				if PossibleReference.Variable in objectSymbol._possibleReferences:
					return element
				else:
					raise TypeError(f"Found variable '{objectSymbol._name._identifier}', but it was not expected.")
			else:
				raise TypeError(f"Found element '{objectSymbol._name._identifier}', but it is not a type or subtype.")
		except KeyError:
			parentNamespace = self._parentNamespace
			if parentNamespace is None:
				raise KeyError(f"Subtype '{objectSymbol._name._identifier}' not found in '{self._name}'.")

			return parentNamespace.FindObject(objectSymbol)
