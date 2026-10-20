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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
from typing               import TYPE_CHECKING, Iterable, Optional as Nullable, Union

from pyTooling.Decorators import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractclass

from pyVHDLModel.Base       import ModelEntity
from pyVHDLModel.Symbol     import Symbol
from pyVHDLModel.Expression import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
if TYPE_CHECKING:
	from pyVHDLModel.Visitor  import Visitor


ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
@abstractclass
class AssociationItem(ModelEntity):
	"""
	A base-class for all association items.

	.. seealso::

	   * :class:`Generic association item <pyVHDLModel.Association.GenericAssociationItem>`
	   * :class:`Port association item <pyVHDLModel.Association.PortAssociationItem>`
	   * :class:`Parameter association item <pyVHDLModel.Association.ParameterAssociationItem>`
	"""

	_formal: Nullable[Symbol]  #: Reference to the formal part, or ``None`` for a positional association.
	_actual: ExpressionUnion   #: The actual part of this association.

	def __init__(self, formal: Nullable[Symbol], actual: ExpressionUnion) -> None:
		"""
		Initializes an association item.

		:param formal: Reference to the formal part, or ``None`` for a positional association.
		:param actual: The actual part of this association.
		"""
		super().__init__()

		self._formal = formal
		if formal is not None:
			formal.Parent = self

		self._actual = actual
		# actual._parent = self  # FIXME: actual is provided as None

	@readonly
	def Formal(self) -> Nullable[Symbol]:  # TODO: can also be a conversion function !!
		"""
		Read-only property to access the formal (:attr:`_formal`).

		:returns: The formal, or ``None`` if not set.
		"""
		return self._formal

	@readonly
	def Actual(self) -> ExpressionUnion:
		"""
		Read-only property to access the actual (:attr:`_actual`).

		:returns: The actual.
		"""
		return self._actual

	def Visit(self, visitor: "Visitor") -> None:
		"""
		Walk this association item, its formal and its actual with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAssociationItem(self)
		if self._formal is not None:
			self._formal.Visit(visitor)
			visitor.VisitArrow(self)

		if self._actual is not None:
			self._actual.Visit(visitor)

		visitor.DepartAssociationItem(self)

	def __str__(self) -> str:
		"""
		Formats the association item.

		**Format:** ``formal => actual``, or ``actual`` alone when positional

		:returns: Formatted association item.
		"""
		if self._formal is None:
			return str(self._actual)
		else:
			return f"{self._formal!s} => {self._actual!s}"


@export
class GenericAssociationItem(AssociationItem):
	"""
	A base-class for all generic association items used in generic map aspects.
	"""


@export
class PortAssociationItem(AssociationItem):
	"""
	A base-class for all port association items used in port map aspects.
	"""


@export
class ParameterAssociationItem(AssociationItem):
	"""
	A base-class for all parameter association items used in parameter map aspects.
	"""


@export
class GenericMapAspectMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for language constructs with a generic map aspect.

	.. seealso::

	   * :class:`Instantiation <pyVHDLModel.Concurrent.Instantiation>`
	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Binding indication <pyVHDLModel.Configuration.BindingIndication>`
	   * :class:`Port map aspect <pyVHDLModel.Association.PortMapAspectMixin>`
	"""

	_genericAssociationItems: list[GenericAssociationItem]  #: List of all generic associations.

	def __init__(self, genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None) -> None:
		"""
		Initializes a generic map aspect.

		:param genericAssociationItems: List of all generic associations.
		"""
		self._genericAssociationItems = []
		if genericAssociationItems is not None:
			for association in genericAssociationItems:
				self._genericAssociationItems.append(association)
				association.Parent = self

	@readonly
	def GenericAssociationItems(self) -> list[GenericAssociationItem]:
		"""
		Read-only property to access the generic associations (:attr:`_genericAssociationItems`).

		:returns: List of generic association items.
		"""
		return self._genericAssociationItems


@export
class PortMapAspectMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for language constructs with a port map aspect.

	.. seealso::

	   * :class:`Instantiation <pyVHDLModel.Concurrent.Instantiation>`
	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Binding indication <pyVHDLModel.Configuration.BindingIndication>`
	   * :class:`Generic map aspect <pyVHDLModel.Association.GenericMapAspectMixin>`
	"""

	_portAssociationItems: list[PortAssociationItem]  #: List of all port associations.

	def __init__(self, portAssociationItems: Nullable[Iterable[PortAssociationItem]] = None) -> None:
		"""
		Initializes a port map aspect.

		:param portAssociationItems: List of all port associations.
		"""
		self._portAssociationItems = []
		if portAssociationItems is not None:
			for association in portAssociationItems:
				self._portAssociationItems.append(association)
				association.Parent = self

	@readonly
	def PortAssociationItems(self) -> list[PortAssociationItem]:
		"""
		Read-only property to access the port associations (:attr:`_portAssociationItems`).

		:returns: List of port association items.
		"""
		return self._portAssociationItems
