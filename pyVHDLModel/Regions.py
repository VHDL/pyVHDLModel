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

tbd.
"""
from typing                 import List, Dict, Iterable

from pyTooling.Decorators   import export
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Object     import Constant, SharedVariable, File, Variable, Signal
from pyVHDLModel.Subprogram import Subprogram, Function, Procedure
from pyVHDLModel.Type       import Subtype, FullType


@export
class ConcurrentDeclarationRegionMixin(metaclass=ExtendedType, mixin=True):
	_declaredItems:   List  # FIXME: define list prefix type e.g. via Union

	# _attributes:     Dict[str, Attribute]
	# _aliases:        Dict[str, Alias]
	_types:           Dict[str, FullType]
	_subtypes:        Dict[str, Subtype]
	# _objects:        Dict[str, Union[Constant, Variable, Signal]]
	_constants:       Dict[str, Constant]
	_signals:         Dict[str, Signal]
	_sharedVariables: Dict[str, SharedVariable]
	_files:           Dict[str, File]
	_subprograms:     Dict[str, Dict[str, Subprogram]]
	_functions:       Dict[str, Dict[str, Function]]
	_procedures:      Dict[str, Dict[str, Procedure]]

	def __init__(self, declaredItems: Iterable = None):
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

		self._types =       {}
		self._subtypes =    {}
		# self._objects =     {}
		self._constants =   {}
		self._signals =     {}
		self._sharedVariables = {}
		self._files =       {}
		self._subprograms = {}
		self._functions =   {}
		self._procedures =  {}

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems

	@property
	def Types(self) -> Dict[str, FullType]:
		return self._types

	@property
	def Subtypes(self) -> Dict[str, Subtype]:
		return self._subtypes

	# @property
	# def Objects(self) -> Dict[str, Union[Constant, SharedVariable, Signal, File]]:
	# 	return self._objects

	@property
	def Constants(self) -> Dict[str, Constant]:
		return self._constants

	@property
	def Signals(self) -> Dict[str, Signal]:
		return self._signals

	@property
	def SharedVariables(self) -> Dict[str, SharedVariable]:
		return self._sharedVariables

	@property
	def Files(self) -> Dict[str, File]:
		return self._files

	@property
	def Subprograms(self) -> Dict[str, Subprogram]:
		return self._subprograms

	@property
	def Functions(self) -> Dict[str, Dict[str, Function]]:
		return self._functions

	@property
	def Procedures(self) -> Dict[str, Dict[str, Procedure]]:
		return self._procedures

	def IndexDeclaredItems(self):
		for item in self._declaredItems:
			if isinstance(item, FullType):
				self._types[item._normalizedIdentifier] = item
				self._namespace._elements[item._normalizedIdentifier] = item
			elif isinstance(item, Subtype):
				self._subtypes[item._normalizedIdentifier] = item
				self._namespace._elements[item._normalizedIdentifier] = item
			elif isinstance(item, Function):
				self._functions[item._normalizedIdentifier] = item
				self._namespace._elements[item._normalizedIdentifier] = item
			elif isinstance(item, Procedure):
				self._procedures[item._normalizedIdentifier] = item
				self._namespace._elements[item._normalizedIdentifier] = item
			elif isinstance(item, Constant):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._constants[normalizedIdentifier] = item
					self._namespace._elements[normalizedIdentifier] = item
					# self._objects[normalizedIdentifier] = item
			elif isinstance(item, Signal):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._signals[normalizedIdentifier] = item
					self._namespace._elements[normalizedIdentifier] = item
			elif isinstance(item, Variable):
				print(f"IndexDeclaredItems - {item._identifiers}")
			elif isinstance(item, SharedVariable):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._sharedVariables[normalizedIdentifier] = item
					self._namespace._elements[normalizedIdentifier] = item
			elif isinstance(item, File):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._files[normalizedIdentifier] = item
					self._namespace._elements[normalizedIdentifier] = item
			else:
				self._IndexOtherDeclaredItem(item)

	def _IndexOtherDeclaredItem(self, item):
		print(f"_IndexOtherDeclaredItem - {item}\n  ({' -> '.join(t.__name__ for t in type(item).mro())})")
