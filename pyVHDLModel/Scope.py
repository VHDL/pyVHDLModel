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

A helper class to implement namespaces and scopes.
"""
from typing import TypeVar, Generic, Dict

from pyVHDLModel.Symbol import ComponentInstantiationSymbol

K = TypeVar("K")
O = TypeVar("O")


class Scope(Generic[K, O]):
	_name:        str
	_parentScope: 'Scope'
	_subScopes:   Dict[str, 'Scope']
	_elements:    Dict[K, O]

	def __init__(self, name: str,  parentScope: 'Scope' = None):
		self._name = name
		self._parentScope = parentScope
		self._subScopes = {}
		self._elements = {}

	@property
	def Name(self) -> str:
		return self._name

	@property
	def ParentScope(self) -> 'Scope':
		return self._parentScope

	@ParentScope.setter
	def ParentScope(self, value: 'Scope'):
		self._parentScope = value
		value._subScopes[self._name] = self

	@property
	def SubScopes(self) -> Dict[str, 'Scope']:
		return self._subScopes

	def Elements(self) -> Dict[K, O]:
		return self._elements

	def FindComponent(self, componentSymbol: ComponentInstantiationSymbol):
		from pyVHDLModel.DesignUnit import Component

		try:
			element = self._elements[componentSymbol.NormalizedIdentifier]
			if isinstance(element, Component):
				return element
			else:
				raise TypeError(f"Found element '{componentSymbol.Identifier}', but it is not a component.")
		except KeyError:
			parentScope = self._parentScope
			if parentScope is None:
				raise KeyError(f"Component '{componentSymbol.Identifier}' not found in '{self._name}'.")

			return parentScope.FindComponent(componentSymbol)
