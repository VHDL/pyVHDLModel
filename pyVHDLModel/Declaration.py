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


"""
from enum import unique, Enum
from typing import List, Iterable

from pyTooling.Decorators import export

from pyVHDLModel.Base import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, ExpressionUnion
from pyVHDLModel.Symbol import Symbol


@export
@unique
class EntityClass(Enum):
	"""An ``EntityClass`` is an enumeration. It represents a VHDL language entity class (``entity``, ``label``, ...)."""

	Entity =        0   #: Entity
	Architecture =  1   #: Architecture
	Configuration = 2   #: Configuration
	Procedure =     3   #: Procedure
	Function =      4   #: Function
	Package =       5   #: Package
	Type =          6   #: Type
	Subtype =       7   #: Subtype
	Constant =      8   #: Constant
	Signal =        9   #: Signal
	Variable =      10  #: Variable
	Component =     11  #: Component
	Label =         12  #: Label
	Literal =       13  #: Literal
	Units =         14  #: Units
	Group =         15  #: Group
	File =          16  #: File
	Property =      17  #: Property
	Sequence =      18  #: Sequence
	View =          19  #: View
	Others =        20  #: Others


@export
class Attribute(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	_subtype: Symbol

	def __init__(self, identifier: str, subtype: Symbol, documentation: str = None):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self):
		return self._subtype


@export
class AttributeSpecification(ModelEntity, DocumentedEntityMixin):
	_identifiers: List['Name']
	_attribute: 'Name'
	_entityClass: EntityClass
	_expression: ExpressionUnion

	def __init__(self, identifiers: Iterable['Name'], attribute: 'Name', entityClass: EntityClass, expression: ExpressionUnion, documentation: str = None):
		super().__init__()
		DocumentedEntityMixin.__init__(self, documentation)

		self._identifiers = []  # TODO: convert to dict
		for identifier in identifiers:
			self._identifiers.append(identifier)
			identifier._parent = self

		self._attribute = attribute
		attribute._parent = self

		self._entityClass = entityClass

		self._expression = expression
		expression._parent = self

	@property
	def Identifiers(self) -> List['Name']:
		return self._identifiers

	@property
	def Attribute(self) -> 'Name':
		return self._attribute

	@property
	def EntityClass(self) -> EntityClass:
		return self._entityClass

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression


@export
class Alias(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	def __init__(self, identifier: str, documentation: str = None):
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)
