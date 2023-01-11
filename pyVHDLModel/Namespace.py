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


class Namespace(Generic[K, O]):
	_name:            str
	_parentNamespace: 'Namespace'
	_subNamespaces:   Dict[str, 'Namespace']
	_elements:        Dict[K, O]

	def __init__(self, name: str, parentNamespace: 'Namespace' = None):
		self._name = name
		self._parentNamespace = parentNamespace
		self._subNamespaces = {}
		self._elements = {}

	@property
	def Name(self) -> str:
		return self._name

	@property
	def ParentNamespace(self) -> 'Namespace':
		return self._parentNamespace

	@ParentNamespace.setter
	def ParentNamespace(self, value: 'Namespace'):
		self._parentNamespace = value
		value._subNamespaces[self._name] = self

	@property
	def SubNamespaces(self) -> Dict[str, 'Namespace']:
		return self._subNamespaces

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
			parentNamespace = self._parentNamespace
			if parentNamespace is None:
				raise KeyError(f"Component '{componentSymbol.Identifier}' not found in '{self._name}'.")

			return parentNamespace.FindComponent(componentSymbol)
