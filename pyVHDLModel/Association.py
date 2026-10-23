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
from __future__              import annotations

from typing                  import TYPE_CHECKING, Iterable, Optional as Nullable, Union, Self

from pyTooling.Common        import getFullyQualifiedName, getTypeName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType, abstractclass

from pyVHDLModel.Base        import ModelEntity
from pyVHDLModel.Exception   import AlreadyInDesignError, NotAChildError, AssociationOrderError
from pyVHDLModel.Exception   import DuplicateGenericAssociationError, DuplicatePortAssociationError
from pyVHDLModel.Name        import Name, SimpleName
from pyVHDLModel.Symbol      import Symbol
from pyVHDLModel.Expression  import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
if TYPE_CHECKING:
	from pyVHDLModel.Visitor   import Visitor


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

	The association item is the parent of its formal and its actual, if they are model entities: a
	:class:`~pyVHDLModel.Symbol.Symbol` has no parent.

	.. seealso::

	   * :class:`Generic association item <pyVHDLModel.Association.GenericAssociationItem>`
	   * :class:`Port association item <pyVHDLModel.Association.PortAssociationItem>`
	   * :class:`Parameter association item <pyVHDLModel.Association.ParameterAssociationItem>`
	"""

	_formal: Nullable[Name | Symbol]  #: Reference to the formal part, or ``None`` for a positional association.
	_actual: ExpressionUnion          #: The actual part of this association.

	def __init__(self, formal: Nullable[Name | Symbol], actual: ExpressionUnion) -> None:
		"""
		Initializes an association item.

		:param formal: Reference to the formal part, or ``None`` for a positional association.
		:param actual: The actual part of this association.
		"""
		super().__init__()

		self._formal = formal
		if isinstance(formal, ModelEntity):
			formal.Parent = self

		self._actual = actual
		if isinstance(actual, ModelEntity):
			actual.Parent = self

	@readonly
	def Formal(self) -> Nullable[Name | Symbol]:  # TODO: can also be a conversion function !!
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

	def Copy(self) -> Self:
		"""
		Create a copy of this association item.

		The copy has no parent. Its formal and actual are copies of this item's formal and actual.

		:returns: The new association item.
		"""
		formal = None if self._formal is None else self._formal.Copy()
		actual = None if self._actual is None else self._actual.Copy()
		return self.__class__(formal, actual)

	def Visit(self, visitor: Visitor) -> None:
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

	An association declares nothing: the mutators update neither a namespace nor a lookup table of the host class, so the
	mixin expects nothing from its host.

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

	def _VisitGenericMapAspect(self, visitor: Visitor) -> None:
		"""
		Walk the generic map aspect, if there are generic associations, with a visitor.

		The associations are separated by commas.

		:param visitor: The visitor receiving the events.
		"""
		if len(self._genericAssociationItems) == 0:
			return

		visitor.VisitGenericMapAspect(self)
		for index, item in enumerate(self._genericAssociationItems):
			if index > 0:
				visitor.VisitComma(self)

			item.Visit(visitor)

		visitor.DepartGenericMapAspect(self)

	def AddGenericAssociationItem(self, genericAssociationItem: GenericAssociationItem) -> None:
		"""
		Add a generic association at the end of the generic map aspect.

		The association's parent is set to this language construct.

		:param genericAssociationItem:            The generic association to add.
		:raises ValueError:                       If parameter 'genericAssociationItem' is ``None``.
		:raises TypeError:                        If parameter 'genericAssociationItem' is not of type
		                                          :class:`~pyVHDLModel.Association.GenericAssociationItem`.
		:raises AlreadyInDesignError:             If parameter 'genericAssociationItem' already has a parent.
		:raises DuplicateGenericAssociationError: If the association is named, and another named association of the generic
		                                          map aspect has the same formal.
		:raises AssociationOrderError:            If the association is positional, and the generic map aspect has a named
		                                          association.

		.. seealso::

		   :meth:`InsertGenericAssociationItem`
		      |rarr| Insert a generic association at a position of the generic map aspect.
		   :meth:`RemoveGenericAssociationItem`
		      |rarr| Remove a generic association from the generic map aspect.
		"""
		self.InsertGenericAssociationItem(len(self._genericAssociationItems), genericAssociationItem)

	def InsertGenericAssociationItem(self, index: int, genericAssociationItem: GenericAssociationItem) -> None:
		"""
		Insert a generic association at a position of the generic map aspect.

		The association's parent is set to this language construct.

		A named association (``formal => actual``) can't repeat the formal of another named association of the generic map
		aspect. Only formals given as a simple name are compared: a partial association (``a(0) => x``) or a conversion
		function (``to_integer(a) => x``) is accepted. All positional associations precede the named associations.

		:param index:                             Position, from ``0`` (first) to the number of generic associations
		                                          (append). A negative index counts from the end, as for
		                                          :meth:`list.insert`: ``-1`` inserts before the last generic association.
		:param genericAssociationItem:            The generic association to insert.
		:raises ValueError:                       If parameter 'index' is ``None``.
		:raises TypeError:                        If parameter 'index' is not of type :class:`int`.
		:raises ValueError:                       If parameter 'index' is out of range.
		:raises ValueError:                       If parameter 'genericAssociationItem' is ``None``.
		:raises TypeError:                        If parameter 'genericAssociationItem' is not of type
		                                          :class:`~pyVHDLModel.Association.GenericAssociationItem`.
		:raises AlreadyInDesignError:             If parameter 'genericAssociationItem' already has a parent.
		:raises DuplicateGenericAssociationError: If the association is named, and another named association of the generic
		                                          map aspect has the same formal.
		:raises AssociationOrderError:            If the association is positional, and a named association precedes the
		                                          position.
		:raises AssociationOrderError:            If the association is named, and a positional association follows the
		                                          position.

		.. seealso::

		   :meth:`AddGenericAssociationItem`
		      |rarr| Add a generic association at the end of the generic map aspect.
		   :meth:`RemoveGenericAssociationItem`
		      |rarr| Remove a generic association from the generic map aspect.
		"""
		count = len(self._genericAssociationItems)
		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-count <= index <= count):
			ex = ValueError(f"Parameter 'index' is out of range {-count}..{count}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if genericAssociationItem is None:
			raise ValueError("Parameter 'genericAssociationItem' is None.")
		elif not isinstance(genericAssociationItem, GenericAssociationItem):
			ex = TypeError("Parameter 'genericAssociationItem' is not of type 'GenericAssociationItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericAssociationItem)}'.")
			raise ex
		elif genericAssociationItem._parent is not None:
			ex = AlreadyInDesignError(
				f"{getTypeName(genericAssociationItem)} already has a parent.",
				element=genericAssociationItem,
				parent=genericAssociationItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(genericAssociationItem._parent)} first.")
			raise ex

		formal = genericAssociationItem._formal
		if isinstance(formal, SimpleName):
			normalizedFormal = formal._normalizedIdentifier
			for existing in self._genericAssociationItems:
				if isinstance(existing._formal, SimpleName) and existing._formal._normalizedIdentifier == normalizedFormal:
					ex = DuplicateGenericAssociationError(
						f"{getTypeName(self)} already associates generic '{formal._identifier}'.",
						identifier=formal._identifier,
						parent=self,
						element=genericAssociationItem,
						existing=existing
					)
					ex.add_note(f"Existing association is '{existing!s}'.")
					raise ex

		position = index if index >= 0 else count + index
		if formal is None:
			for existing in self._genericAssociationItems[:position]:
				if existing._formal is not None:
					ex = AssociationOrderError(
						f"Positional generic association can't follow named association '{existing!s}'.",
						parent=self,
						element=genericAssociationItem,
						existing=existing
					)
					ex.add_note("Insert it before the first named association, or name its formal.")
					raise ex
		else:
			for existing in self._genericAssociationItems[position:]:
				if existing._formal is None:
					ex = AssociationOrderError(
						f"Named generic association can't precede positional association '{existing!s}'.",
						parent=self,
						element=genericAssociationItem,
						existing=existing
					)
					ex.add_note("Insert it after the last positional association.")
					raise ex

		self._genericAssociationItems.insert(index, genericAssociationItem)
		genericAssociationItem.Parent = self

	def RemoveGenericAssociationItem(self, genericAssociationItem: GenericAssociationItem) -> None:
		"""
		Remove a generic association from the generic map aspect.

		The association is detached: its parent is cleared. The association itself is unchanged and can be added to another
		language construct, or inserted at another position.

		:param genericAssociationItem: The generic association to remove.
		:raises ValueError:            If parameter 'genericAssociationItem' is ``None``.
		:raises TypeError:             If parameter 'genericAssociationItem' is not of type
		                               :class:`~pyVHDLModel.Association.GenericAssociationItem`.
		:raises NotAChildError:        If parameter 'genericAssociationItem' is not a generic association of this language
		                               construct.

		.. seealso::

		   :meth:`AddGenericAssociationItem`
		      |rarr| Add a generic association at the end of the generic map aspect.
		   :meth:`InsertGenericAssociationItem`
		      |rarr| Insert a generic association at a position of the generic map aspect.
		"""
		if genericAssociationItem is None:
			raise ValueError("Parameter 'genericAssociationItem' is None.")
		elif not isinstance(genericAssociationItem, GenericAssociationItem):
			ex = TypeError("Parameter 'genericAssociationItem' is not of type 'GenericAssociationItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericAssociationItem)}'.")
			raise ex

		for index, item in enumerate(self._genericAssociationItems):
			if item is genericAssociationItem:
				break
		else:
			raise NotAChildError(
				f"{getTypeName(genericAssociationItem)} is not a generic association of this {getTypeName(self)}.",
				element=genericAssociationItem,
				parent=self
			)

		del self._genericAssociationItems[index]
		genericAssociationItem._parent = None


@export
class PortMapAspectMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for language constructs with a port map aspect.

	An association declares nothing: the mutators update neither a namespace nor a lookup table of the host class, so the
	mixin expects nothing from its host.

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

	def AddPortAssociationItem(self, portAssociationItem: PortAssociationItem) -> None:
		"""
		Add a port association at the end of the port map aspect.

		The association's parent is set to this language construct.

		:param portAssociationItem:            The port association to add.
		:raises ValueError:                    If parameter 'portAssociationItem' is ``None``.
		:raises TypeError:                     If parameter 'portAssociationItem' is not of type
		                                       :class:`~pyVHDLModel.Association.PortAssociationItem`.
		:raises AlreadyInDesignError:          If parameter 'portAssociationItem' already has a parent.
		:raises DuplicatePortAssociationError: If the association is named, and another named association of the port map
		                                       aspect has the same formal.
		:raises AssociationOrderError:         If the association is positional, and the port map aspect has a named
		                                       association.

		.. seealso::

		   :meth:`InsertPortAssociationItem`
		      |rarr| Insert a port association at a position of the port map aspect.
		   :meth:`RemovePortAssociationItem`
		      |rarr| Remove a port association from the port map aspect.
		"""
		self.InsertPortAssociationItem(len(self._portAssociationItems), portAssociationItem)

	def InsertPortAssociationItem(self, index: int, portAssociationItem: PortAssociationItem) -> None:
		"""
		Insert a port association at a position of the port map aspect.

		The association's parent is set to this language construct.

		A named association (``formal => actual``) can't repeat the formal of another named association of the port map
		aspect. Only formals given as a simple name are compared: a partial association (``a(0) => x``) or a conversion
		function (``to_integer(a) => x``) is accepted. All positional associations precede the named associations.

		:param index:                          Position, from ``0`` (first) to the number of port associations (append). A
		                                       negative index counts from the end, as for :meth:`list.insert`: ``-1``
		                                       inserts before the last port association.
		:param portAssociationItem:            The port association to insert.
		:raises ValueError:                    If parameter 'index' is ``None``.
		:raises TypeError:                     If parameter 'index' is not of type :class:`int`.
		:raises ValueError:                    If parameter 'index' is out of range.
		:raises ValueError:                    If parameter 'portAssociationItem' is ``None``.
		:raises TypeError:                     If parameter 'portAssociationItem' is not of type
		                                       :class:`~pyVHDLModel.Association.PortAssociationItem`.
		:raises AlreadyInDesignError:          If parameter 'portAssociationItem' already has a parent.
		:raises DuplicatePortAssociationError: If the association is named, and another named association of the port map
		                                       aspect has the same formal.
		:raises AssociationOrderError:         If the association is positional, and a named association precedes the
		                                       position.
		:raises AssociationOrderError:         If the association is named, and a positional association follows the
		                                       position.

		.. seealso::

		   :meth:`AddPortAssociationItem`
		      |rarr| Add a port association at the end of the port map aspect.
		   :meth:`RemovePortAssociationItem`
		      |rarr| Remove a port association from the port map aspect.
		"""
		count = len(self._portAssociationItems)
		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-count <= index <= count):
			ex = ValueError(f"Parameter 'index' is out of range {-count}..{count}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if portAssociationItem is None:
			raise ValueError("Parameter 'portAssociationItem' is None.")
		elif not isinstance(portAssociationItem, PortAssociationItem):
			ex = TypeError("Parameter 'portAssociationItem' is not of type 'PortAssociationItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portAssociationItem)}'.")
			raise ex
		elif portAssociationItem._parent is not None:
			ex = AlreadyInDesignError(
				f"{getTypeName(portAssociationItem)} already has a parent.",
				element=portAssociationItem,
				parent=portAssociationItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(portAssociationItem._parent)} first.")
			raise ex

		formal = portAssociationItem._formal
		if isinstance(formal, SimpleName):
			normalizedFormal = formal._normalizedIdentifier
			for existing in self._portAssociationItems:
				if isinstance(existing._formal, SimpleName) and existing._formal._normalizedIdentifier == normalizedFormal:
					ex = DuplicatePortAssociationError(
						f"{getTypeName(self)} already associates port '{formal._identifier}'.",
						identifier=formal._identifier,
						parent=self,
						element=portAssociationItem,
						existing=existing
					)
					ex.add_note(f"Existing association is '{existing!s}'.")
					raise ex

		position = index if index >= 0 else count + index
		if formal is None:
			for existing in self._portAssociationItems[:position]:
				if existing._formal is not None:
					ex = AssociationOrderError(
						f"Positional port association can't follow named association '{existing!s}'.",
						parent=self,
						element=portAssociationItem,
						existing=existing
					)
					ex.add_note("Insert it before the first named association, or name its formal.")
					raise ex
		else:
			for existing in self._portAssociationItems[position:]:
				if existing._formal is None:
					ex = AssociationOrderError(
						f"Named port association can't precede positional association '{existing!s}'.",
						parent=self,
						element=portAssociationItem,
						existing=existing
					)
					ex.add_note("Insert it after the last positional association.")
					raise ex

		self._portAssociationItems.insert(index, portAssociationItem)
		portAssociationItem.Parent = self

	def RemovePortAssociationItem(self, portAssociationItem: PortAssociationItem) -> None:
		"""
		Remove a port association from the port map aspect.

		The association is detached: its parent is cleared. The association itself is unchanged and can be added to another
		language construct, or inserted at another position.

		:param portAssociationItem: The port association to remove.
		:raises ValueError:         If parameter 'portAssociationItem' is ``None``.
		:raises TypeError:          If parameter 'portAssociationItem' is not of type
		                            :class:`~pyVHDLModel.Association.PortAssociationItem`.
		:raises NotAChildError:     If parameter 'portAssociationItem' is not a port association of this language construct.

		.. seealso::

		   :meth:`AddPortAssociationItem`
		      |rarr| Add a port association at the end of the port map aspect.
		   :meth:`InsertPortAssociationItem`
		      |rarr| Insert a port association at a position of the port map aspect.
		"""
		if portAssociationItem is None:
			raise ValueError("Parameter 'portAssociationItem' is None.")
		elif not isinstance(portAssociationItem, PortAssociationItem):
			ex = TypeError("Parameter 'portAssociationItem' is not of type 'PortAssociationItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portAssociationItem)}'.")
			raise ex

		for index, item in enumerate(self._portAssociationItems):
			if item is portAssociationItem:
				break
		else:
			raise NotAChildError(
				f"{getTypeName(portAssociationItem)} is not a port association of this {getTypeName(self)}.",
				element=portAssociationItem,
				parent=self
			)

		del self._portAssociationItems[index]
		portAssociationItem._parent = None
