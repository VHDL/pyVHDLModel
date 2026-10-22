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

tbd.
"""
from __future__              import annotations

from typing                  import TYPE_CHECKING, Any, ClassVar, Iterable, Optional as Nullable

from pyTooling.Common        import getFullyQualifiedName, getTypeName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType, expects
from pyTooling.Warning       import WarningCollector

from pyVHDLModel.Base        import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, identifiersOf
from pyVHDLModel.Base        import normalizedIdentifiersOf, normalizedDeclaredNamesOf
from pyVHDLModel.Exception   import NotImplementedWarning, AlreadyInDesignError, NotAChildError
from pyVHDLModel.Exception   import DuplicateGenericError, DuplicatePortError, DuplicateParameterError
from pyVHDLModel.Exception   import DuplicateDeclarationError, DuplicateTypeError, DuplicateSubtypeError
from pyVHDLModel.Exception   import DuplicateConstantError, DuplicateSignalError, DuplicateVariableError
from pyVHDLModel.Exception   import DuplicateFileError, DuplicateComponentError, DuplicateSubprogramError
from pyVHDLModel.Namespace   import Namespace
from pyVHDLModel.Object      import BaseConstant, Constant, DeferredConstant, SharedVariable, File, Variable, Signal
if TYPE_CHECKING:
	from pyVHDLModel.Interface import GenericInterfaceItemMixin, PortInterfaceItemMixin, ParameterInterfaceItemMixin
	from pyVHDLModel.Interface import PortSignalInterfaceItem
	from pyVHDLModel.Type      import Subtype, FullType
	from pyVHDLModel.Visitor   import Visitor

# `pyVHDLModel.Subprogram` imports this module (Subprogram is a sequential declaration region), so
# `Function`/`Procedure` are quoted in annotations and imported lazily where they're needed at runtime.
# The same holds for the interface item classes of `pyVHDLModel.Interface`.


@export
class WithGenericsMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_AddToNamespace", "_RemoveFromNamespace", "_ClashingDeclarations")
):
	"""
	A mixin-class for language constructs with a generic clause.

	The host class provides ``_AddToNamespace(element)`` and ``_RemoveFromNamespace(element)``, called when a generic is
	inserted or removed: :class:`~pyVHDLModel.Regions.DeclarationRegionMixin` updates its namespace, a language construct
	without a namespace implements both as no-operations.

	The host class also provides ``_ClashingDeclarations(item)``, called before a generic is inserted: it returns the
	declarations sharing an identifier with the new item.

	Indexing the generics (``_IndexGenericItems()``) needs the host's namespace ``_namespace``; a host without one, e.g.
	a component, can't index them.

	.. seealso::

	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Component <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Generic group <pyVHDLModel.Interface.GenericGroup>`
	"""
	_genericItems: list[GenericInterfaceItemMixin]  #: List of all generics, in declaration order.

	def __init__(
		self,
		genericItems: Nullable[Iterable[GenericInterfaceItemMixin]] = None,
 	) -> None:
		"""
		Initializes a language construct with a generic clause.

		:param genericItems: List of all generics, in declaration order.
		"""
		self._genericItems = []
		if genericItems is not None:
			for item in genericItems:
				self._genericItems.append(item)
				item.Parent = self

	@readonly
	def GenericItems(self) -> list[GenericInterfaceItemMixin]:
		"""
		Read-only property to access the generic items (:attr:`_genericItems`).

		:returns: List of generic items.
		"""
		return self._genericItems

	@readonly
	def GenericCount(self) -> int:
		"""
		Read-only property to return the number of generics in :attr:`_genericItems`.

		:returns: The generic count.
		"""
		return len(self._genericItems)

	def AddGenericItem(self, genericItem: GenericInterfaceItemMixin) -> None:
		"""
		Add a generic at the end of the generic clause.

		The generic's parent is set to this language construct, and its identifiers are added to the language construct's
		namespace, if it has one.

		:param genericItem:            The generic to add.
		:raises ValueError:            If parameter 'genericItem' is ``None``.
		:raises TypeError:             If parameter 'genericItem' is not of type
		                               :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`.
		:raises AlreadyInDesignError:  If parameter 'genericItem' already has a parent.
		:raises DuplicateGenericError: If an existing declaration of the language construct shares an identifier
		                               with the generic.

		.. seealso::

		   :meth:`InsertGenericItem`
		      |rarr| Insert a generic at a position of the generic clause.
		   :meth:`RemoveGenericItem`
		      |rarr| Remove a generic from the generic clause.
		"""
		self.InsertGenericItem(len(self._genericItems), genericItem)

	def InsertGenericItem(self, index: int, genericItem: GenericInterfaceItemMixin) -> None:
		"""
		Insert a generic at a position of the generic clause.

		The generic's parent is set to this language construct, and its identifiers are added to the language construct's
		namespace, if it has one.

		:param index:                  Position, from ``0`` (first) to :data:`GenericCount` (append).
		                               A negative index counts from the end, as for :meth:`list.insert`: ``-1`` inserts
		                               before the last generic.
		:param genericItem:            The generic to insert.
		:raises ValueError:            If parameter 'index' is ``None``.
		:raises TypeError:             If parameter 'index' is not of type :class:`int`.
		:raises ValueError:            If parameter 'index' is out of range.
		:raises ValueError:            If parameter 'genericItem' is ``None``.
		:raises TypeError:             If parameter 'genericItem' is not of type
		                               :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`.
		:raises AlreadyInDesignError:  If parameter 'genericItem' already has a parent.
		:raises DuplicateGenericError: If an existing declaration of the language construct shares an identifier
		                               with the generic.

		.. seealso::

		   :meth:`AddGenericItem`
		      |rarr| Add a generic at the end of the generic clause.
		   :meth:`RemoveGenericItem`
		      |rarr| Remove a generic from the generic clause.
		   :meth:`MoveGenericItem`
		      |rarr| Move a generic to a position of the generic clause.
		"""
		from pyVHDLModel.Interface import GenericInterfaceItemMixin

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._genericItems) <= index <= len(self._genericItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._genericItems)}..{len(self._genericItems)}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if genericItem is None:
			raise ValueError("Parameter 'genericItem' is None.")
		elif not isinstance(genericItem, GenericInterfaceItemMixin):
			ex = TypeError("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericItem)}'.")
			raise ex
		elif genericItem._parent is not None:
			identifiers = ", ".join(identifiersOf(genericItem))
			ex = AlreadyInDesignError(
				f"{getTypeName(genericItem)} '{identifiers}' already has a parent.",
				element=genericItem,
				parent=genericItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(genericItem._parent)} first.")
			raise ex

		if len(clashes := self._ClashingDeclarations(genericItem)) > 0:
			existingIdentifiers = normalizedIdentifiersOf(clashes[0])
			newIdentifiers = zip(identifiersOf(genericItem), normalizedIdentifiersOf(genericItem))
			identifier = next(name for name, normalizedName in newIdentifiers if normalizedName in existingIdentifiers)
			ex = DuplicateGenericError(
				f"{getTypeName(clashes[0]._parent)} already declares '{identifier}'.",
				identifier=identifier,
				parent=self,
				element=genericItem,
				existing=clashes[0]
			)
			ex.add_note(f"Existing declaration is of type '{getFullyQualifiedName(clashes[0])}'.")
			raise ex

		self._genericItems.insert(index, genericItem)
		genericItem.Parent = self
		self._AddToNamespace(genericItem)

	def RemoveGenericItem(self, genericItem: GenericInterfaceItemMixin) -> None:
		"""
		Remove a generic from the generic clause.

		The generic is detached: its parent is cleared and its identifiers are removed from the language construct's
		namespace, if it has one. The generic itself is unchanged and can be added to another language construct, or
		inserted at another position.

		:param genericItem:          The generic to remove.
		:raises ValueError:          If parameter 'genericItem' is ``None``.
		:raises TypeError:           If parameter 'genericItem' is not of type
		                             :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`.
		:raises NotAChildError:      If parameter 'genericItem' is not a generic of this language construct.
		:raises NotInNamespaceError: If the namespace is indexed, and an identifier of the generic isn't declared in it.
		:raises NotInNamespaceError: If the namespace is indexed, and an identifier of the generic refers to another
		                             element, e.g. a duplicate declaration.

		.. seealso::

		   :meth:`AddGenericItem`
		      |rarr| Add a generic at the end of the generic clause.
		   :meth:`InsertGenericItem`
		      |rarr| Insert a generic at a position of the generic clause.
		   :meth:`MoveGenericItem`
		      |rarr| Move a generic to a position of the generic clause.
		"""
		from pyVHDLModel.Interface import GenericInterfaceItemMixin

		if genericItem is None:
			raise ValueError("Parameter 'genericItem' is None.")
		elif not isinstance(genericItem, GenericInterfaceItemMixin):
			ex = TypeError("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericItem)}'.")
			raise ex

		for index, item in enumerate(self._genericItems):
			if item is genericItem:
				break
		else:
			identifiers = ", ".join(identifiersOf(genericItem))
			raise NotAChildError(
				f"{getTypeName(genericItem)} '{identifiers}' is not a generic of this {getTypeName(self)}.",
				element=genericItem,
				parent=self
			)

		self._RemoveFromNamespace(genericItem)
		del self._genericItems[index]
		genericItem._parent = None

	def MoveGenericItem(self, genericItem: GenericInterfaceItemMixin, index: int) -> None:
		"""
		Move a generic to a position of the generic clause.

		The generic stays a generic of this language construct: only the order of the generic clause changes. A generic
		subprogram is an overload: if the language construct's namespace is indexed, it refers to the overload declared
		last afterwards.

		:param genericItem:          The generic to move.
		:param index:                Position of the generic after the move, from ``0`` (first) to :data:`GenericCount`
		                             minus one (last). A negative index counts from the end, as for a :class:`list`
		                             index: ``-1`` moves the generic to the end.
		:raises ValueError:          If parameter 'genericItem' is ``None``.
		:raises TypeError:           If parameter 'genericItem' is not of type
		                             :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`.
		:raises NotAChildError:      If parameter 'genericItem' is not a generic of this language construct.
		:raises ValueError:          If parameter 'index' is ``None``.
		:raises TypeError:           If parameter 'index' is not of type :class:`int`.
		:raises ValueError:          If parameter 'index' is out of range.
		:raises NotInNamespaceError: If the namespace is indexed, and the identifier of a generic subprogram refers to an
		                             element, which is no overload, e.g. a duplicate declaration.

		.. seealso::

		   :meth:`InsertGenericItem`
		      |rarr| Insert a generic at a position of the generic clause.
		   :meth:`RemoveGenericItem`
		      |rarr| Remove a generic from the generic clause.
		"""
		from pyVHDLModel.Interface  import GenericInterfaceItemMixin
		from pyVHDLModel.Subprogram import Function, Procedure

		if genericItem is None:
			raise ValueError("Parameter 'genericItem' is None.")
		elif not isinstance(genericItem, GenericInterfaceItemMixin):
			ex = TypeError("Parameter 'genericItem' is not of type 'GenericInterfaceItemMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericItem)}'.")
			raise ex

		for currentIndex, item in enumerate(self._genericItems):
			if item is genericItem:
				break
		else:
			identifiers = ", ".join(identifiersOf(genericItem))
			raise NotAChildError(
				f"{getTypeName(genericItem)} '{identifiers}' is not a generic of this {getTypeName(self)}.",
				element=genericItem,
				parent=self
			)

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._genericItems) <= index < len(self._genericItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._genericItems)}..{len(self._genericItems) - 1}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		newIndex = index if index >= 0 else len(self._genericItems) + index
		if newIndex == currentIndex:
			return

		isOverload = isinstance(genericItem, (Function, Procedure))
		if isOverload:
			self._RemoveFromNamespace(genericItem)

		del self._genericItems[currentIndex]
		self._genericItems.insert(newIndex, genericItem)

		if isOverload:
			self._AddToNamespace(genericItem)

	@expects("_namespace")
	def _IndexGenericItems(self) -> None:
		"""Add the generics to the host's namespace; a generic subprogram is an overload."""
		from pyVHDLModel.Subprogram import Function, Procedure

		for item in self._genericItems:
			overloadable = isinstance(item, (Function, Procedure))
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item, overloadable=overloadable)

	def _VisitGenericClause(self, visitor: Visitor) -> None:
		"""
		Walk the generic clause, if there are generics, with a visitor.

		The generics are separated by semicolons.

		:param visitor: The visitor receiving the events.
		"""
		if len(self._genericItems) == 0:
			return

		visitor.VisitGenericClause(self)
		for index, item in enumerate(self._genericItems):
			if index > 0:
				visitor.VisitSemicolon(self)

			item.Visit(visitor)

		visitor.DepartGenericClause(self)


@export
class WithPortsMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_AddToNamespace", "_RemoveFromNamespace", "_ClashingDeclarations")
):
	"""
	A mixin-class for language constructs with a port clause.

	The host class provides ``_AddToNamespace(element)`` and ``_RemoveFromNamespace(element)``, called when a port is
	inserted or removed: :class:`~pyVHDLModel.Regions.DeclarationRegionMixin` updates its namespace, a language construct
	without a namespace implements both as no-operations.

	The host class also provides ``_ClashingDeclarations(item)``, called before a port is inserted: it returns the
	declarations sharing an identifier with the new item.

	Indexing the ports (``_IndexPortItems()``) needs the host's namespace ``_namespace``; a host without one, e.g.
	a component, can't index them.

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Component <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Port group <pyVHDLModel.Interface.PortGroup>`
	"""
	_portItems: list[PortInterfaceItemMixin]  #: List of all ports, in declaration order.

	def __init__(
		self,
		portItems: Nullable[Iterable[PortInterfaceItemMixin]] = None,
	) -> None:
		"""
		Initializes a language construct with a port clause.

		:param portItems: List of all ports, in declaration order.
		"""
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item.Parent = self

	@readonly
	def PortItems(self) -> list[PortInterfaceItemMixin]:
		"""
		Read-only property to access the port items (:attr:`_portItems`).

		:returns: List of port items.
		"""
		return self._portItems

	@readonly
	def PortCount(self) -> int:
		"""
		Read-only property to return the number of ports in :attr:`_portItems`.

		:returns: The port count.
		"""
		return len(self._portItems)

	def AddPortItem(self, portItem: PortSignalInterfaceItem) -> None:
		"""
		Add a port at the end of the port clause.

		The port's parent is set to this language construct, and its identifiers are added to the language construct's
		namespace, if it has one.

		:param portItem:              The port to add.
		:raises ValueError:           If parameter 'portItem' is ``None``.
		:raises TypeError:            If parameter 'portItem' is not of type
		                              :class:`~pyVHDLModel.Interface.PortSignalInterfaceItem`.
		:raises AlreadyInDesignError: If parameter 'portItem' already has a parent.
		:raises DuplicatePortError:   If an existing declaration of the language construct shares an identifier
		                              with the port.

		.. seealso::

		   :meth:`InsertPortItem`
		      |rarr| Insert a port at a position of the port clause.
		   :meth:`RemovePortItem`
		      |rarr| Remove a port from the port clause.
		"""
		self.InsertPortItem(len(self._portItems), portItem)

	def InsertPortItem(self, index: int, portItem: PortSignalInterfaceItem) -> None:
		"""
		Insert a port at a position of the port clause.

		The port's parent is set to this language construct, and its identifiers are added to the language construct's
		namespace, if it has one.

		:param index:                 Position, from ``0`` (first) to :data:`PortCount` (append).
		                              A negative index counts from the end, as for :meth:`list.insert`: ``-1`` inserts
		                              before the last port.
		:param portItem:              The port to insert.
		:raises ValueError:           If parameter 'index' is ``None``.
		:raises TypeError:            If parameter 'index' is not of type :class:`int`.
		:raises ValueError:           If parameter 'index' is out of range.
		:raises ValueError:           If parameter 'portItem' is ``None``.
		:raises TypeError:            If parameter 'portItem' is not of type
		                              :class:`~pyVHDLModel.Interface.PortSignalInterfaceItem`.
		:raises AlreadyInDesignError: If parameter 'portItem' already has a parent.
		:raises DuplicatePortError:   If an existing declaration of the language construct shares an identifier
		                              with the port.

		.. seealso::

		   :meth:`AddPortItem`
		      |rarr| Add a port at the end of the port clause.
		   :meth:`RemovePortItem`
		      |rarr| Remove a port from the port clause.
		   :meth:`MovePortItem`
		      |rarr| Move a port to a position of the port clause.
		"""
		from pyVHDLModel.Interface import PortSignalInterfaceItem

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._portItems) <= index <= len(self._portItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._portItems)}..{len(self._portItems)}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if portItem is None:
			raise ValueError("Parameter 'portItem' is None.")
		elif not isinstance(portItem, PortSignalInterfaceItem):
			ex = TypeError("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portItem)}'.")
			raise ex
		elif portItem._parent is not None:
			identifiers = ", ".join(identifiersOf(portItem))
			ex = AlreadyInDesignError(
				f"{getTypeName(portItem)} '{identifiers}' already has a parent.",
				element=portItem,
				parent=portItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(portItem._parent)} first.")
			raise ex

		if len(clashes := self._ClashingDeclarations(portItem)) > 0:
			existingIdentifiers = normalizedIdentifiersOf(clashes[0])
			newIdentifiers = zip(identifiersOf(portItem), normalizedIdentifiersOf(portItem))
			identifier = next(name for name, normalizedName in newIdentifiers if normalizedName in existingIdentifiers)
			ex = DuplicatePortError(
				f"{getTypeName(clashes[0]._parent)} already declares '{identifier}'.",
				identifier=identifier,
				parent=self,
				element=portItem,
				existing=clashes[0]
			)
			ex.add_note(f"Existing declaration is of type '{getFullyQualifiedName(clashes[0])}'.")
			raise ex

		self._portItems.insert(index, portItem)
		portItem.Parent = self
		self._AddToNamespace(portItem)

	def RemovePortItem(self, portItem: PortSignalInterfaceItem) -> None:
		"""
		Remove a port from the port clause.

		The port is detached: its parent is cleared and its identifiers are removed from the language construct's
		namespace, if it has one. The port itself is unchanged and can be added to another language construct, or
		inserted at another position.

		:param portItem:             The port to remove.
		:raises ValueError:          If parameter 'portItem' is ``None``.
		:raises TypeError:           If parameter 'portItem' is not of type
		                             :class:`~pyVHDLModel.Interface.PortSignalInterfaceItem`.
		:raises NotAChildError:      If parameter 'portItem' is not a port of this language construct.
		:raises NotInNamespaceError: If the namespace is indexed, and an identifier of the port isn't declared in it.
		:raises NotInNamespaceError: If the namespace is indexed, and an identifier of the port refers to another
		                             element, e.g. a duplicate declaration.

		.. seealso::

		   :meth:`AddPortItem`
		      |rarr| Add a port at the end of the port clause.
		   :meth:`InsertPortItem`
		      |rarr| Insert a port at a position of the port clause.
		   :meth:`MovePortItem`
		      |rarr| Move a port to a position of the port clause.
		"""
		from pyVHDLModel.Interface import PortSignalInterfaceItem

		if portItem is None:
			raise ValueError("Parameter 'portItem' is None.")
		elif not isinstance(portItem, PortSignalInterfaceItem):
			ex = TypeError("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portItem)}'.")
			raise ex

		for index, item in enumerate(self._portItems):
			if item is portItem:
				break
		else:
			identifiers = ", ".join(identifiersOf(portItem))
			raise NotAChildError(
				f"{getTypeName(portItem)} '{identifiers}' is not a port of this {getTypeName(self)}.",
				element=portItem,
				parent=self
			)

		self._RemoveFromNamespace(portItem)
		del self._portItems[index]
		portItem._parent = None

	def MovePortItem(self, portItem: PortSignalInterfaceItem, index: int) -> None:
		"""
		Move a port to a position of the port clause.

		The port stays a port of this language construct: only the order of the port clause changes.

		:param portItem:        The port to move.
		:param index:           Position of the port after the move, from ``0`` (first) to :data:`PortCount` minus one
		                        (last). A negative index counts from the end, as for a :class:`list` index: ``-1`` moves the
		                        port to the end.
		:raises ValueError:     If parameter 'portItem' is ``None``.
		:raises TypeError:      If parameter 'portItem' is not of type
		                        :class:`~pyVHDLModel.Interface.PortSignalInterfaceItem`.
		:raises NotAChildError: If parameter 'portItem' is not a port of this language construct.
		:raises ValueError:     If parameter 'index' is ``None``.
		:raises TypeError:      If parameter 'index' is not of type :class:`int`.
		:raises ValueError:     If parameter 'index' is out of range.

		.. seealso::

		   :meth:`InsertPortItem`
		      |rarr| Insert a port at a position of the port clause.
		   :meth:`RemovePortItem`
		      |rarr| Remove a port from the port clause.
		"""
		from pyVHDLModel.Interface import PortSignalInterfaceItem

		if portItem is None:
			raise ValueError("Parameter 'portItem' is None.")
		elif not isinstance(portItem, PortSignalInterfaceItem):
			ex = TypeError("Parameter 'portItem' is not of type 'PortSignalInterfaceItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portItem)}'.")
			raise ex

		for currentIndex, item in enumerate(self._portItems):
			if item is portItem:
				break
		else:
			identifiers = ", ".join(identifiersOf(portItem))
			raise NotAChildError(
				f"{getTypeName(portItem)} '{identifiers}' is not a port of this {getTypeName(self)}.",
				element=portItem,
				parent=self
			)

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._portItems) <= index < len(self._portItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._portItems)}..{len(self._portItems) - 1}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		newIndex = index if index >= 0 else len(self._portItems) + index
		del self._portItems[currentIndex]
		self._portItems.insert(newIndex, portItem)

	@expects("_namespace")
	def _IndexPortItems(self) -> None:
		"""Add the ports to the host's namespace."""
		for item in self._portItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _VisitPortClause(self, visitor: Visitor) -> None:
		"""
		Walk the port clause, if there are ports, with a visitor.

		The ports are separated by semicolons.

		:param visitor: The visitor receiving the events.
		"""
		if len(self._portItems) == 0:
			return

		visitor.VisitPortClause(self)
		for index, item in enumerate(self._portItems):
			if index > 0:
				visitor.VisitSemicolon(self)

			item.Visit(visitor)

		visitor.DepartPortClause(self)


@export
class WithParametersMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_AddToNamespace", "_RemoveFromNamespace", "_ClashingDeclarations", "_ParameterItemsChanged")
):
	"""
	A mixin-class for language constructs with a parameter list.

	The host class provides ``_AddToNamespace(element)`` and ``_RemoveFromNamespace(element)``, called when a parameter is
	inserted or removed: :class:`~pyVHDLModel.Regions.DeclarationRegionMixin` updates its namespace, a language construct
	without a namespace implements both as no-operations.

	The host class also provides ``_ClashingDeclarations(item)``, called before a parameter is inserted: it returns the
	declarations sharing an identifier with the new item.

	The host class provides ``_ParameterItemsChanged()`` too, called after a parameter is inserted, removed or moved:
	:class:`~pyVHDLModel.Subprogram.Subprogram` clears its signature, a parameter group does nothing.

	Indexing the parameters (``_IndexParameterItems()``) needs the host's namespace ``_namespace``; a host without one,
	e.g. a parameter group, can't index them.

	.. seealso::

	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Parameter group <pyVHDLModel.Interface.ParameterGroup>`
	"""
	_parameterItems: list[ParameterInterfaceItemMixin]  #: List of all parameters, in declaration order.

	def __init__(
		self,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
	) -> None:
		"""
		Initializes a language construct with a parameter list.

		:param parameterItems: List of all parameters, in declaration order.
		"""
		self._parameterItems = []
		if parameterItems is not None:
			for item in parameterItems:
				self._parameterItems.append(item)
				item.Parent = self

	@readonly
	def ParameterItems(self) -> list[ParameterInterfaceItemMixin]:
		"""
		Read-only property to access the parameter items (:attr:`_parameterItems`).

		:returns: List of parameter items.
		"""
		return self._parameterItems

	@readonly
	def ParameterCount(self) -> int:
		"""
		Read-only property to return the number of parameters in :attr:`_parameterItems`.

		:returns: The parameter count.
		"""
		return len(self._parameterItems)

	def AddParameterItem(self, parameterItem: ParameterInterfaceItemMixin) -> None:
		"""
		Add a parameter at the end of the parameter list.

		The parameter's parent is set to this language construct, and its identifiers are added to the language construct's
		namespace, if it has one.

		:param parameterItem:            The parameter to add.
		:raises ValueError:              If parameter 'parameterItem' is ``None``.
		:raises TypeError:               If parameter 'parameterItem' is not of type
		                                 :class:`~pyVHDLModel.Interface.ParameterInterfaceItemMixin`.
		:raises AlreadyInDesignError:    If parameter 'parameterItem' already has a parent.
		:raises DuplicateParameterError: If an existing declaration of the language construct shares an identifier
		                                 with the parameter.

		.. seealso::

		   :meth:`InsertParameterItem`
		      |rarr| Insert a parameter at a position of the parameter list.
		   :meth:`RemoveParameterItem`
		      |rarr| Remove a parameter from the parameter list.
		"""
		self.InsertParameterItem(len(self._parameterItems), parameterItem)

	def InsertParameterItem(self, index: int, parameterItem: ParameterInterfaceItemMixin) -> None:
		"""
		Insert a parameter at a position of the parameter list.

		The parameter's parent is set to this language construct, and its identifiers are added to the language construct's
		namespace, if it has one.

		:param index:                    Position, from ``0`` (first) to :data:`ParameterCount` (append).
		                                 A negative index counts from the end, as for :meth:`list.insert`: ``-1`` inserts
		                                 before the last parameter.
		:param parameterItem:            The parameter to insert.
		:raises ValueError:              If parameter 'index' is ``None``.
		:raises TypeError:               If parameter 'index' is not of type :class:`int`.
		:raises ValueError:              If parameter 'index' is out of range.
		:raises ValueError:              If parameter 'parameterItem' is ``None``.
		:raises TypeError:               If parameter 'parameterItem' is not of type
		                                 :class:`~pyVHDLModel.Interface.ParameterInterfaceItemMixin`.
		:raises AlreadyInDesignError:    If parameter 'parameterItem' already has a parent.
		:raises DuplicateParameterError: If an existing declaration of the language construct shares an identifier
		                                 with the parameter.

		.. seealso::

		   :meth:`AddParameterItem`
		      |rarr| Add a parameter at the end of the parameter list.
		   :meth:`RemoveParameterItem`
		      |rarr| Remove a parameter from the parameter list.
		   :meth:`MoveParameterItem`
		      |rarr| Move a parameter to a position of the parameter list.
		"""
		from pyVHDLModel.Interface import ParameterInterfaceItemMixin

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._parameterItems) <= index <= len(self._parameterItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._parameterItems)}..{len(self._parameterItems)}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if parameterItem is None:
			raise ValueError("Parameter 'parameterItem' is None.")
		elif not isinstance(parameterItem, ParameterInterfaceItemMixin):
			ex = TypeError("Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterItem)}'.")
			raise ex
		elif parameterItem._parent is not None:
			identifiers = ", ".join(identifiersOf(parameterItem))
			ex = AlreadyInDesignError(
				f"{getTypeName(parameterItem)} '{identifiers}' already has a parent.",
				element=parameterItem,
				parent=parameterItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(parameterItem._parent)} first.")
			raise ex

		if len(clashes := self._ClashingDeclarations(parameterItem)) > 0:
			existingIdentifiers = normalizedIdentifiersOf(clashes[0])
			newIdentifiers = zip(identifiersOf(parameterItem), normalizedIdentifiersOf(parameterItem))
			identifier = next(name for name, normalizedName in newIdentifiers if normalizedName in existingIdentifiers)
			ex = DuplicateParameterError(
				f"{getTypeName(clashes[0]._parent)} already declares '{identifier}'.",
				identifier=identifier,
				parent=self,
				element=parameterItem,
				existing=clashes[0]
			)
			ex.add_note(f"Existing declaration is of type '{getFullyQualifiedName(clashes[0])}'.")
			raise ex

		self._parameterItems.insert(index, parameterItem)
		parameterItem.Parent = self
		self._AddToNamespace(parameterItem)
		self._ParameterItemsChanged()

	def RemoveParameterItem(self, parameterItem: ParameterInterfaceItemMixin) -> None:
		"""
		Remove a parameter from the parameter list.

		The parameter is detached: its parent is cleared and its identifiers are removed from the language construct's
		namespace, if it has one. The parameter itself is unchanged and can be added to another language construct, or
		inserted at another position.

		:param parameterItem:        The parameter to remove.
		:raises ValueError:          If parameter 'parameterItem' is ``None``.
		:raises TypeError:           If parameter 'parameterItem' is not of type
		                             :class:`~pyVHDLModel.Interface.ParameterInterfaceItemMixin`.
		:raises NotAChildError:      If parameter 'parameterItem' is not a parameter of this language construct.
		:raises NotInNamespaceError: If the namespace is indexed, and an identifier of the parameter isn't declared in it.
		:raises NotInNamespaceError: If the namespace is indexed, and an identifier of the parameter refers to another
		                             element, e.g. a duplicate declaration.

		.. seealso::

		   :meth:`AddParameterItem`
		      |rarr| Add a parameter at the end of the parameter list.
		   :meth:`InsertParameterItem`
		      |rarr| Insert a parameter at a position of the parameter list.
		   :meth:`MoveParameterItem`
		      |rarr| Move a parameter to a position of the parameter list.
		"""
		from pyVHDLModel.Interface import ParameterInterfaceItemMixin

		if parameterItem is None:
			raise ValueError("Parameter 'parameterItem' is None.")
		elif not isinstance(parameterItem, ParameterInterfaceItemMixin):
			ex = TypeError("Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterItem)}'.")
			raise ex

		for index, item in enumerate(self._parameterItems):
			if item is parameterItem:
				break
		else:
			identifiers = ", ".join(identifiersOf(parameterItem))
			raise NotAChildError(
				f"{getTypeName(parameterItem)} '{identifiers}' is not a parameter of this {getTypeName(self)}.",
				element=parameterItem,
				parent=self
			)

		self._RemoveFromNamespace(parameterItem)
		del self._parameterItems[index]
		parameterItem._parent = None
		self._ParameterItemsChanged()

	def MoveParameterItem(self, parameterItem: ParameterInterfaceItemMixin, index: int) -> None:
		"""
		Move a parameter to a position of the parameter list.

		The parameter stays a parameter of this language construct: only the order of the parameter list changes.

		:param parameterItem:   The parameter to move.
		:param index:           Position of the parameter after the move, from ``0`` (first) to :data:`ParameterCount`
		                        minus one (last). A negative index counts from the end, as for a :class:`list` index:
		                        ``-1`` moves the parameter to the end.
		:raises ValueError:     If parameter 'parameterItem' is ``None``.
		:raises TypeError:      If parameter 'parameterItem' is not of type
		                        :class:`~pyVHDLModel.Interface.ParameterInterfaceItemMixin`.
		:raises NotAChildError: If parameter 'parameterItem' is not a parameter of this language construct.
		:raises ValueError:     If parameter 'index' is ``None``.
		:raises TypeError:      If parameter 'index' is not of type :class:`int`.
		:raises ValueError:     If parameter 'index' is out of range.

		.. seealso::

		   :meth:`InsertParameterItem`
		      |rarr| Insert a parameter at a position of the parameter list.
		   :meth:`RemoveParameterItem`
		      |rarr| Remove a parameter from the parameter list.
		"""
		from pyVHDLModel.Interface import ParameterInterfaceItemMixin

		if parameterItem is None:
			raise ValueError("Parameter 'parameterItem' is None.")
		elif not isinstance(parameterItem, ParameterInterfaceItemMixin):
			ex = TypeError("Parameter 'parameterItem' is not of type 'ParameterInterfaceItemMixin'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterItem)}'.")
			raise ex

		for currentIndex, item in enumerate(self._parameterItems):
			if item is parameterItem:
				break
		else:
			identifiers = ", ".join(identifiersOf(parameterItem))
			raise NotAChildError(
				f"{getTypeName(parameterItem)} '{identifiers}' is not a parameter of this {getTypeName(self)}.",
				element=parameterItem,
				parent=self
			)

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._parameterItems) <= index < len(self._parameterItems)):
			ex = ValueError(
				f"Parameter 'index' is out of range {-len(self._parameterItems)}..{len(self._parameterItems) - 1}."
			)
			ex.add_note(f"Got value '{index}'.")
			raise ex

		newIndex = index if index >= 0 else len(self._parameterItems) + index
		del self._parameterItems[currentIndex]
		self._parameterItems.insert(newIndex, parameterItem)
		self._ParameterItemsChanged()

	@expects("_namespace")
	def _IndexParameterItems(self) -> None:
		"""Add the parameters to the host's namespace."""
		for item in self._parameterItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)


@export
class DeclarationRegionMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=(
		"_namespace",
		"_functions",
		"_procedures",
		"_declaredItems",
		"_Declarations",
		"_IndexDeclaredItem",
		"_UnindexDeclaredItem",
		"IndexDeclaredItems",
		"_Labels"
	)
):
	"""
	A base-class for the concurrent, sequential and protected type declaration region mixins.

	It carries what all regions share: adding interface items to the region's namespace, the mutators for declared items
	(e.g. :meth:`AddDeclaredItem`), and the hooks for declared items no region handles itself.

	The derived region mixin-class provides the namespace ``_namespace``, the declared items ``_declaredItems`` and the
	lookup tables ``_functions`` and ``_procedures``; it or the host class provides the methods ``_Declarations()``,
	``_IndexDeclaredItem(item)``, ``_UnindexDeclaredItem(item)`` and ``IndexDeclaredItems()``.

	An interface item shares the declarative region of the declarative part beside it - VHDL rejects
	``port (g : in bit)`` beside ``generic (g : integer)``, ``signal x`` beside ``port (x : in bit)``, and a
	subprogram variable named like one of its parameters, all as "identifier already used for a
	declaration". So they belong in the region's *own* namespace, not a separate one.

	Which of the three a region has is known statically by the class that declares them, so each derived
	class calls the ones it needs from its own :meth:`IndexDeclaredItems` before delegating upwards.
	Interface items are added to the namespace only - ``GenericItems``/``PortItems``/``ParameterItems``
	already expose them as ordered lists, so no extra lookup table is needed.

	.. seealso::

	   * :class:`Concurrent declaration region mixin <pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin>`
	   * :class:`Sequential declaration region mixin <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	   * :class:`Protected type declaration region mixin <pyVHDLModel.Regions.ProtectedTypeDeclarationRegionMixin>`

	A statement label is declared implicitly in the declarative region enclosing the statement, so the host provides the
	labeled statements of the region by ``_Labels()``: a host with statements gets it from its statements mixin
	(e.g. :class:`~pyVHDLModel.Concurrent.ConcurrentStatementsMixin`), a host without statements from
	:class:`WithoutStatementsMixin`.
	"""
	_DECLARED_ITEM_TYPES:     ClassVar[tuple[type, ...]]  #: Accepted classes of declared items (:mod:`pyVHDLModel`).
	_areDeclaredItemsIndexed: bool                        #: ``True`` if :meth:`IndexDeclaredItems` filled the namespace.

	def __init__(self) -> None:
		"""
		Initializes a declaration region, which isn't indexed yet.
		"""
		self._areDeclaredItemsIndexed = False

	def _AddToNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Add an element's identifiers to this region's namespace.

		Nothing is added to a region not indexed yet: :meth:`IndexDeclaredItems` adds the element later. A generic
		subprogram is an overload (:meth:`_AddOverloadToNamespace`).

		:param element: The named element to add, e.g. an interface item.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		if not self._areDeclaredItemsIndexed:
			return
		elif isinstance(element, (Function, Procedure)):
			self._AddOverloadToNamespace(element)
			return

		for normalizedIdentifier in normalizedIdentifiersOf(element):
			self._namespace.AddElement(normalizedIdentifier, element)

	def _RemoveFromNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Remove an element's identifiers from this region's namespace.

		Nothing is removed from a region not indexed yet, as its namespace doesn't contain the element. A generic
		subprogram is an overload (:meth:`_RemoveOverloadFromNamespace`).

		:param element:              The named element to remove, e.g. an interface item.
		:raises NotInNamespaceError: If the region is indexed, and an identifier of the element isn't declared in the
		                             namespace.
		:raises NotInNamespaceError: If the region is indexed, and an identifier of the element refers to another element,
		                             e.g. a duplicate declaration.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		if not self._areDeclaredItemsIndexed:
			return
		elif isinstance(element, (Function, Procedure)):
			self._RemoveOverloadFromNamespace(element)
			return

		for normalizedIdentifier in normalizedIdentifiersOf(element):
			self._namespace.RemoveElement(normalizedIdentifier, element)

	def _IndexOtherDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Hook for declared items the region doesn't handle itself. Derived classes may override it.

		:param item: The declared item.
		"""

	def _UnindexOtherDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Hook to remove declared items the region doesn't handle itself. Derived classes may override it.

		:param item: The declared item.
		"""

	def _RemoveDeclaredItemsFromNamespace(self) -> None:
		"""
		Remove all declared items of this region from its namespace.

		Interface items of this region and items imported from elsewhere (e.g. by a use clause) are kept.
		"""
		from pyVHDLModel.Interface import InterfaceItemMixin

		for normalizedIdentifier, element in list(self._namespace.Elements().items()):
			if not isinstance(element, InterfaceItemMixin) and element._parent is self:
				self._namespace.RemoveElement(normalizedIdentifier, element)

	def _RemoveDeclaredItemEntries(
		self,
		lookupTable: dict[str, Any],
		item:        NamedEntityMixin | MultipleNamedEntityMixin
	) -> None:
		"""
		Remove a declared item's entries from a lookup table and from the namespace.

		Every identifier is checked before anything is removed.

		:param lookupTable:          The lookup table matching the declared item's kind.
		:param item:                 The declared item.
		:raises NotInNamespaceError: If an identifier of the declared item isn't declared in the namespace.
		:raises NotInNamespaceError: If an identifier of the declared item refers to another element, e.g. a duplicate
		                             declaration.
		"""
		normalizedIdentifiers = normalizedIdentifiersOf(item)
		elements = self._namespace.Elements()
		for normalizedIdentifier in normalizedIdentifiers:
			if elements.get(normalizedIdentifier) is not item:
				# raises NotInNamespaceError, naming the reason
				self._namespace.RemoveElement(normalizedIdentifier, item)

		for normalizedIdentifier in normalizedIdentifiers:
			del lookupTable[normalizedIdentifier]
			self._namespace.RemoveElement(normalizedIdentifier, item)

	def _IndexOverload(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Add an inserted function or procedure to its lookup table and to the namespace.

		The list of overloads follows the declaration order. The namespace is updated by :meth:`_AddOverloadToNamespace`.

		:param item: The inserted function or procedure.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		kind = Function if isinstance(item, Function) else Procedure
		lookupTable = self._functions if kind is Function else self._procedures
		normalizedIdentifier = item._normalizedIdentifier
		lookupTable[normalizedIdentifier] = [
			declaration for declaration in self._declaredItems
			if isinstance(declaration, kind) and declaration._normalizedIdentifier == normalizedIdentifier
		]

		self._AddOverloadToNamespace(item)

	def _UnindexOverload(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Remove a function or procedure from its lookup table and from the namespace.

		The namespace is updated first, by :meth:`_RemoveOverloadFromNamespace`.

		:param item:                 The function or procedure to remove, still a declared item of this region.
		:raises NotInNamespaceError: If the identifier isn't declared in the namespace.
		:raises NotInNamespaceError: If the identifier refers to an element, which is no overload, e.g. a duplicate
		                             declaration.
		"""
		from pyVHDLModel.Subprogram import Function

		self._RemoveOverloadFromNamespace(item)

		normalizedIdentifier = item._normalizedIdentifier
		lookupTable = self._functions if isinstance(item, Function) else self._procedures
		overloads = lookupTable[normalizedIdentifier]
		overloads.remove(item)
		if len(overloads) == 0:
			del lookupTable[normalizedIdentifier]

	def _AddOverloadToNamespace(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Add a function or procedure to the namespace, if it's the overload declared last.

		The namespace keeps one entry per identifier: the overload declared last, as after :meth:`IndexDeclaredItems`, which
		adds interface items first, then declared items (:meth:`_Declarations`).

		:param item: The function or procedure, already an interface item or declared item of this region.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		normalizedIdentifier = item._normalizedIdentifier
		overloads = [
			declaration for declaration in self._Declarations()
			if isinstance(declaration, (Function, Procedure)) and declaration._normalizedIdentifier == normalizedIdentifier
		]
		if overloads[-1] is item:
			self._namespace.AddElement(normalizedIdentifier, item, overloadable=True)

	def _RemoveOverloadFromNamespace(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Remove a function or procedure from the namespace.

		Removing the overload the namespace refers to, the namespace refers to the remaining overload declared last
		(:meth:`_Declarations`), or the identifier is removed, if no overload remains. Removing another overload leaves the
		namespace unchanged. The namespace is checked before it's changed.

		:param item:                 The function or procedure, still an interface item or declared item of this region.
		:raises NotInNamespaceError: If the identifier isn't declared in the namespace.
		:raises NotInNamespaceError: If the identifier refers to an element, which is no overload, e.g. a duplicate
		                             declaration.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		normalizedIdentifier = item._normalizedIdentifier
		entry = self._namespace.Elements().get(normalizedIdentifier)
		if entry is item:
			remaining = [
				declaration for declaration in self._Declarations()
				if declaration is not item
				and isinstance(declaration, (Function, Procedure))
				and declaration._normalizedIdentifier == normalizedIdentifier
			]
			if len(remaining) == 0:
				self._namespace.RemoveElement(normalizedIdentifier, item)
			else:
				self._namespace.AddElement(normalizedIdentifier, remaining[-1], overloadable=True)
		elif not isinstance(entry, (Function, Procedure)):
			# raises NotInNamespaceError, naming the reason
			self._namespace.RemoveElement(normalizedIdentifier, item)

	def _SharedRegions(self) -> tuple[DeclarationRegionMixin, ...]:
		"""
		Return the other language constructs forming one declarative region with this one.

		An entity and each of its architectures form one declarative region, as do a package and its body. Derived classes
		override it.

		:returns: Tuple of declarative regions.
		"""
		return ()

	def _MayShareIdentifier(self, item: ModelEntity, existing: ModelEntity) -> bool:
		"""
		Check if two declarations may share an identifier in one declarative region.

		Subprograms are overloadable. A protected type body completes its protected type, a full type completes its
		incomplete type, and a constant completes its deferred constant.

		:param item:     The new declaration.
		:param existing: The existing declaration.
		:returns:        ``True``, if both declarations may share an identifier.
		"""
		from pyVHDLModel.Interface  import InterfaceItemMixin
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import FullType, AnonymousType, ProtectedType, ProtectedTypeBody

		return (
			(isinstance(item, (Function, Procedure)) and isinstance(existing, (Function, Procedure)))
			or (isinstance(item, ProtectedTypeBody) and isinstance(existing, ProtectedType))
			or (isinstance(item, ProtectedType) and isinstance(existing, ProtectedTypeBody))
			or (isinstance(item, FullType) and isinstance(existing, AnonymousType))
			or (isinstance(item, AnonymousType) and isinstance(existing, FullType))
			or (
				isinstance(item, Constant) and not isinstance(item, InterfaceItemMixin)
				and isinstance(existing, DeferredConstant)
			)
			or (
				isinstance(item, DeferredConstant)
				and isinstance(existing, Constant) and not isinstance(existing, InterfaceItemMixin)
			)
		)

	def _ClashingDeclarations(self, item: ModelEntity) -> tuple[ModelEntity, ...]:
		"""
		Return the declarations sharing an identifier with the given item, which may not share it.

		The declarations (:meth:`_Declarations`) and the labeled statements (``_Labels()``) of this declarative region and
		of the language constructs sharing it (:meth:`_SharedRegions`) are searched: a statement label is declared
		implicitly. Items imported into the namespace (e.g. by a use clause) are no declarations.

		:param item: The new declaration, or the new labeled statement.
		:returns:    Tuple of clashing declarations, interface items first, then declared items in declaration order, then
		             labeled statements.
		"""
		if len(names := set(normalizedDeclaredNamesOf(item))) == 0:
			return ()

		return tuple(
			declaration
			for region in (self, *self._SharedRegions())
			for declaration in (*region._Declarations(), *region._Labels())
			if (
				declaration is not item
				and not names.isdisjoint(normalizedDeclaredNamesOf(declaration))
				and not self._MayShareIdentifier(item, declaration)
			)
		)

	def _DeclaredItemsSharingIdentifiers(self, declaredItem: ModelEntity) -> list[ModelEntity]:
		"""
		Return the other declared items of this region sharing an identifier with the given declared item.

		:param declaredItem: The declared item.
		:returns:            List of declared items, in declaration order.
		"""
		if not isinstance(declaredItem, (NamedEntityMixin, MultipleNamedEntityMixin)):
			return []

		identifiers = set(normalizedIdentifiersOf(declaredItem))
		return [
			item for item in self._declaredItems
			if item is not declaredItem
			and isinstance(item, (NamedEntityMixin, MultipleNamedEntityMixin))
			and not identifiers.isdisjoint(normalizedIdentifiersOf(item))
		]

	def AddDeclaredItem(self, declaredItem: ModelEntity) -> None:
		"""
		Add a declared item at the end of the declarative region.

		The declared item's parent is set to this declarative region. If the region is indexed, its identifiers are added
		to the region's namespace and to the lookup table matching its kind.

		:param declaredItem:               The declared item to add.
		:raises ValueError:                If parameter 'declaredItem' is ``None``.
		:raises TypeError:                 If parameter 'declaredItem' is not a declaration allowed in this declarative
		                                   region.
		:raises AlreadyInDesignError:      If parameter 'declaredItem' already has a parent.
		:raises DuplicateDeclarationError: If an existing declaration of the declarative region shares an
		                                   identifier with the declared item.

		.. seealso::

		   :meth:`InsertDeclaredItem`
		      |rarr| Insert a declared item at a position of the declarative region.
		   :meth:`RemoveDeclaredItem`
		      |rarr| Remove a declared item from the declarative region.
		"""
		self.InsertDeclaredItem(len(self._declaredItems), declaredItem)

	def InsertDeclaredItem(self, index: int, declaredItem: ModelEntity) -> None:
		"""
		Insert a declared item at a position of the declarative region.

		The declared item's parent is set to this declarative region. If the region is indexed, its identifiers are added
		to the region's namespace and to the lookup table matching its kind.

		An identifier is declared once per declarative region: interface items and declared items count, including those of
		the language construct sharing the declarative region (an entity and its architecture, a package and its body).
		Subprograms are overloadable: a subprogram may share its identifier with other subprograms. A protected type body
		may share its identifier with its protected type, a full type with its incomplete type declaration, and a constant
		with its deferred constant. Items imported into the namespace (e.g. by a use clause) are hidden.

		:param index:                      Position, from ``0`` (first) to the number of declared items (append).
		                                   A negative index counts from the end, as for :meth:`list.insert`: ``-1``
		                                   inserts before the last declared item.
		:param declaredItem:               The declared item to insert.
		:raises ValueError:                If parameter 'index' is ``None``.
		:raises TypeError:                 If parameter 'index' is not of type :class:`int`.
		:raises ValueError:                If parameter 'index' is out of range.
		:raises ValueError:                If parameter 'declaredItem' is ``None``.
		:raises TypeError:                 If parameter 'declaredItem' is not a declaration allowed in this declarative
		                                   region.
		:raises AlreadyInDesignError:      If parameter 'declaredItem' already has a parent.
		:raises DuplicateDeclarationError: If an existing declaration of the declarative region shares an
		                                   identifier with the declared item.

		.. seealso::

		   :meth:`AddDeclaredItem`
		      |rarr| Add a declared item at the end of the declarative region.
		   :meth:`InsertDeclaredItemBefore`
		      |rarr| Insert a declared item before another declared item.
		   :meth:`InsertDeclaredItemAfter`
		      |rarr| Insert a declared item after another declared item.
		   :meth:`RemoveDeclaredItem`
		      |rarr| Remove a declared item from the declarative region.
		   :meth:`MoveDeclaredItem`
		      |rarr| Move a declared item to a position of the declarative region.
		"""
		from pyVHDLModel.DesignUnit import Component
		from pyVHDLModel.Interface  import InterfaceItemMixin
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import BaseType, Subtype

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._declaredItems) <= index <= len(self._declaredItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._declaredItems)}..{len(self._declaredItems)}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if declaredItem is None:
			raise ValueError("Parameter 'declaredItem' is None.")
		elif not isinstance(declaredItem, self._DECLARED_ITEM_TYPES) or isinstance(declaredItem, InterfaceItemMixin):
			ex = TypeError(f"Parameter 'declaredItem' is not a declaration allowed in {getTypeName(self)}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(declaredItem)}'.")
			raise ex
		elif declaredItem._parent is not None:
			identifiers = ""
			if isinstance(declaredItem, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(declaredItem))}'"
			ex = AlreadyInDesignError(
				f"{getTypeName(declaredItem)}{identifiers} already has a parent.",
				element=declaredItem,
				parent=declaredItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(declaredItem._parent)} first.")
			raise ex

		if len(clashes := self._ClashingDeclarations(declaredItem)) > 0:
			existingIdentifiers = normalizedDeclaredNamesOf(clashes[0])
			newIdentifiers = zip(identifiersOf(declaredItem), normalizedIdentifiersOf(declaredItem))
			identifier = next(name for name, normalizedName in newIdentifiers if normalizedName in existingIdentifiers)

			if isinstance(declaredItem, Subtype):
				errorClass = DuplicateSubtypeError
			elif isinstance(declaredItem, BaseType):
				errorClass = DuplicateTypeError
			elif isinstance(declaredItem, (Function, Procedure)):
				errorClass = DuplicateSubprogramError
			elif isinstance(declaredItem, BaseConstant):
				errorClass = DuplicateConstantError
			elif isinstance(declaredItem, Signal):
				errorClass = DuplicateSignalError
			elif isinstance(declaredItem, (Variable, SharedVariable)):
				errorClass = DuplicateVariableError
			elif isinstance(declaredItem, File):
				errorClass = DuplicateFileError
			elif isinstance(declaredItem, Component):
				errorClass = DuplicateComponentError
			else:
				errorClass = DuplicateDeclarationError
			region = clashes[0]._parent
			while not isinstance(region, DeclarationRegionMixin):
				region = region._parent
			ex = errorClass(
				f"{getTypeName(region)} already declares '{identifier}'.",
				identifier=identifier,
				namespace=self._namespace,
				element=declaredItem,
				existing=clashes[0]
			)
			ex.add_note(f"Existing declaration is of type '{getFullyQualifiedName(clashes[0])}'.")
			raise ex

		sharingItems = self._DeclaredItemsSharingIdentifiers(declaredItem)

		self._declaredItems.insert(index, declaredItem)
		declaredItem.Parent = self
		if self._areDeclaredItemsIndexed:
			if isinstance(declaredItem, (Function, Procedure)):
				self._IndexOverload(declaredItem)
			else:
				self._IndexDeclaredItem(declaredItem)

	def InsertDeclaredItemBefore(self, declaredItem: ModelEntity, before: ModelEntity) -> None:
		"""
		Insert a declared item before another declared item.

		The declared item's parent is set to this declarative region. If the region is indexed, its identifiers are added
		to the region's namespace and to the lookup table matching its kind.

		:param declaredItem:               The declared item to insert.
		:param before:                     The declared item of this declarative region to insert before.
		:raises ValueError:                If parameter 'before' is ``None``.
		:raises TypeError:                 If parameter 'before' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError:            If parameter 'before' is not a declared item of this declarative region.
		:raises ValueError:                If parameter 'declaredItem' is ``None``.
		:raises TypeError:                 If parameter 'declaredItem' is not a declaration allowed in this declarative
		                                   region.
		:raises AlreadyInDesignError:      If parameter 'declaredItem' already has a parent.
		:raises DuplicateDeclarationError: If an existing declaration of the declarative region shares an
		                                   identifier with the declared item.

		.. seealso::

		   :meth:`InsertDeclaredItem`
		      |rarr| Insert a declared item at a position of the declarative region.
		   :meth:`InsertDeclaredItemAfter`
		      |rarr| Insert a declared item after another declared item.
		"""
		if before is None:
			raise ValueError("Parameter 'before' is None.")
		elif not isinstance(before, ModelEntity):
			ex = TypeError("Parameter 'before' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(before)}'.")
			raise ex

		for index, item in enumerate(self._declaredItems):
			if item is before:
				break
		else:
			identifiers = ""
			if isinstance(before, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(before))}'"
			raise NotAChildError(
				f"{getTypeName(before)}{identifiers} is not a declared item of this {getTypeName(self)}.",
				element=before,
				parent=self
			)

		self.InsertDeclaredItem(index, declaredItem)

	def InsertDeclaredItemAfter(self, declaredItem: ModelEntity, after: ModelEntity) -> None:
		"""
		Insert a declared item after another declared item.

		The declared item's parent is set to this declarative region. If the region is indexed, its identifiers are added
		to the region's namespace and to the lookup table matching its kind.

		:param declaredItem:               The declared item to insert.
		:param after:                      The declared item of this declarative region to insert after.
		:raises ValueError:                If parameter 'after' is ``None``.
		:raises TypeError:                 If parameter 'after' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError:            If parameter 'after' is not a declared item of this declarative region.
		:raises ValueError:                If parameter 'declaredItem' is ``None``.
		:raises TypeError:                 If parameter 'declaredItem' is not a declaration allowed in this declarative
		                                   region.
		:raises AlreadyInDesignError:      If parameter 'declaredItem' already has a parent.
		:raises DuplicateDeclarationError: If an existing declaration of the declarative region shares an
		                                   identifier with the declared item.

		.. seealso::

		   :meth:`InsertDeclaredItem`
		      |rarr| Insert a declared item at a position of the declarative region.
		   :meth:`InsertDeclaredItemBefore`
		      |rarr| Insert a declared item before another declared item.
		"""
		if after is None:
			raise ValueError("Parameter 'after' is None.")
		elif not isinstance(after, ModelEntity):
			ex = TypeError("Parameter 'after' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(after)}'.")
			raise ex

		for index, item in enumerate(self._declaredItems):
			if item is after:
				break
		else:
			identifiers = ""
			if isinstance(after, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(after))}'"
			raise NotAChildError(
				f"{getTypeName(after)}{identifiers} is not a declared item of this {getTypeName(self)}.",
				element=after,
				parent=self
			)

		self.InsertDeclaredItem(index + 1, declaredItem)

	def RemoveDeclaredItem(self, declaredItem: ModelEntity) -> None:
		"""
		Remove a declared item from the declarative region.

		The declared item is detached: its parent is cleared. If the region is indexed, the declared item's identifiers are
		removed from the region's namespace and from the lookup table matching its kind first; they are checked before
		anything is changed. The declared item itself is unchanged and can be added to another declarative region, or
		inserted at another position.

		The namespace refers to the overload declared last: removing it, the namespace refers to the remaining overload
		declared last. If another declaration shares an identifier with the declared item (e.g. a duplicate declaration
		read by a parser), the region is indexed again (:meth:`IndexDeclaredItems`) after the removal.

		:param declaredItem:         The declared item to remove.
		:raises ValueError:          If parameter 'declaredItem' is ``None``.
		:raises TypeError:           If parameter 'declaredItem' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError:      If parameter 'declaredItem' is not a declared item of this declarative region.
		:raises NotInNamespaceError: If the region is indexed, and an identifier of the declared item isn't declared in
		                             its namespace.
		:raises NotInNamespaceError: If the region is indexed, and an identifier of the declared item refers to another
		                             declaration, e.g. a duplicate declaration.

		.. seealso::

		   :meth:`AddDeclaredItem`
		      |rarr| Add a declared item at the end of the declarative region.
		   :meth:`InsertDeclaredItem`
		      |rarr| Insert a declared item at a position of the declarative region.
		   :meth:`MoveDeclaredItem`
		      |rarr| Move a declared item to a position of the declarative region.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		if declaredItem is None:
			raise ValueError("Parameter 'declaredItem' is None.")
		elif not isinstance(declaredItem, ModelEntity):
			ex = TypeError("Parameter 'declaredItem' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(declaredItem)}'.")
			raise ex

		for index, item in enumerate(self._declaredItems):
			if item is declaredItem:
				break
		else:
			identifiers = ""
			if isinstance(declaredItem, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(declaredItem))}'"
			raise NotAChildError(
				f"{getTypeName(declaredItem)}{identifiers} is not a declared item of this {getTypeName(self)}.",
				element=declaredItem,
				parent=self
			)

		reindex = False
		if self._areDeclaredItemsIndexed:
			isOverload = isinstance(declaredItem, (Function, Procedure))
			reindex = any(
				not (isOverload and isinstance(item, (Function, Procedure)))
				for item in self._DeclaredItemsSharingIdentifiers(declaredItem)
			)
			self._UnindexDeclaredItem(declaredItem)

		del self._declaredItems[index]
		declaredItem._parent = None

		if reindex:
			self.IndexDeclaredItems()

	def MoveDeclaredItem(self, declaredItem: ModelEntity, index: int) -> None:
		"""
		Move a declared item to a position of the declarative region.

		The declared item stays a declared item of this declarative region: only the order of the declared items changes.

		If the region is indexed, the lookup tables and the namespace follow the new order: a list of overloads (e.g. in
		``Functions``) follows the declaration order, and the namespace refers to the overload declared last. If
		another declaration shares an identifier with the declared item (e.g. a duplicate declaration read by a parser),
		the region is indexed again (:meth:`IndexDeclaredItems`) after the move.

		:param declaredItem:    The declared item to move.
		:param index:           Position of the declared item after the move, from ``0`` (first) to the number of
		                        declared items minus one (last). A negative index counts from the end, as for a
		                        :class:`list` index: ``-1`` moves the declared item to the end.
		:raises ValueError:     If parameter 'declaredItem' is ``None``.
		:raises TypeError:      If parameter 'declaredItem' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError: If parameter 'declaredItem' is not a declared item of this declarative region.
		:raises ValueError:     If parameter 'index' is ``None``.
		:raises TypeError:      If parameter 'index' is not of type :class:`int`.
		:raises ValueError:     If parameter 'index' is out of range.

		.. seealso::

		   :meth:`MoveDeclaredItemBefore`
		      |rarr| Move a declared item before another declared item.
		   :meth:`MoveDeclaredItemAfter`
		      |rarr| Move a declared item after another declared item.
		   :meth:`InsertDeclaredItem`
		      |rarr| Insert a declared item at a position of the declarative region.
		   :meth:`RemoveDeclaredItem`
		      |rarr| Remove a declared item from the declarative region.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		if declaredItem is None:
			raise ValueError("Parameter 'declaredItem' is None.")
		elif not isinstance(declaredItem, ModelEntity):
			ex = TypeError("Parameter 'declaredItem' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(declaredItem)}'.")
			raise ex

		for currentIndex, item in enumerate(self._declaredItems):
			if item is declaredItem:
				break
		else:
			identifiers = ""
			if isinstance(declaredItem, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(declaredItem))}'"
			raise NotAChildError(
				f"{getTypeName(declaredItem)}{identifiers} is not a declared item of this {getTypeName(self)}.",
				element=declaredItem,
				parent=self
			)

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._declaredItems) <= index < len(self._declaredItems)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._declaredItems)}..{len(self._declaredItems) - 1}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		newIndex = index if index >= 0 else len(self._declaredItems) + index
		if newIndex == currentIndex:
			return

		reindex =   False
		overloads = False
		if self._areDeclaredItemsIndexed and len(sharingItems := self._DeclaredItemsSharingIdentifiers(declaredItem)) > 0:
			isOverload = isinstance(declaredItem, (Function, Procedure))
			reindex =    any(not (isOverload and isinstance(item, (Function, Procedure))) for item in sharingItems)
			overloads =  not reindex

		if overloads:
			self._RemoveOverloadFromNamespace(declaredItem)

		del self._declaredItems[currentIndex]
		self._declaredItems.insert(newIndex, declaredItem)

		if reindex:
			self.IndexDeclaredItems()
		elif overloads:
			self._IndexOverload(declaredItem)

	def MoveDeclaredItemBefore(self, declaredItem: ModelEntity, before: ModelEntity) -> None:
		"""
		Move a declared item before another declared item.

		The declared item stays a declared item of this declarative region: only the order of the declared items changes,
		as for :meth:`MoveDeclaredItem`. Moving a declared item before itself keeps it in place.

		:param declaredItem:    The declared item to move.
		:param before:          The declared item of this declarative region to move before.
		:raises ValueError:     If parameter 'before' is ``None``.
		:raises TypeError:      If parameter 'before' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError: If parameter 'before' is not a declared item of this declarative region.
		:raises ValueError:     If parameter 'declaredItem' is ``None``.
		:raises TypeError:      If parameter 'declaredItem' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError: If parameter 'declaredItem' is not a declared item of this declarative region.

		.. seealso::

		   :meth:`MoveDeclaredItem`
		      |rarr| Move a declared item to a position of the declarative region.
		   :meth:`MoveDeclaredItemAfter`
		      |rarr| Move a declared item after another declared item.
		"""
		if before is None:
			raise ValueError("Parameter 'before' is None.")
		elif not isinstance(before, ModelEntity):
			ex = TypeError("Parameter 'before' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(before)}'.")
			raise ex

		for index, item in enumerate(self._declaredItems):
			if item is before:
				break
		else:
			identifiers = ""
			if isinstance(before, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(before))}'"
			raise NotAChildError(
				f"{getTypeName(before)}{identifiers} is not a declared item of this {getTypeName(self)}.",
				element=before,
				parent=self
			)

		precedes = any(item is declaredItem for item in self._declaredItems[:index])
		self.MoveDeclaredItem(declaredItem, index - 1 if precedes else index)

	def MoveDeclaredItemAfter(self, declaredItem: ModelEntity, after: ModelEntity) -> None:
		"""
		Move a declared item after another declared item.

		The declared item stays a declared item of this declarative region: only the order of the declared items changes,
		as for :meth:`MoveDeclaredItem`. Moving a declared item after itself keeps it in place.

		:param declaredItem:    The declared item to move.
		:param after:           The declared item of this declarative region to move after.
		:raises ValueError:     If parameter 'after' is ``None``.
		:raises TypeError:      If parameter 'after' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError: If parameter 'after' is not a declared item of this declarative region.
		:raises ValueError:     If parameter 'declaredItem' is ``None``.
		:raises TypeError:      If parameter 'declaredItem' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError: If parameter 'declaredItem' is not a declared item of this declarative region.

		.. seealso::

		   :meth:`MoveDeclaredItem`
		      |rarr| Move a declared item to a position of the declarative region.
		   :meth:`MoveDeclaredItemBefore`
		      |rarr| Move a declared item before another declared item.
		"""
		if after is None:
			raise ValueError("Parameter 'after' is None.")
		elif not isinstance(after, ModelEntity):
			ex = TypeError("Parameter 'after' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(after)}'.")
			raise ex

		for index, item in enumerate(self._declaredItems):
			if item is after:
				break
		else:
			identifiers = ""
			if isinstance(after, (NamedEntityMixin, MultipleNamedEntityMixin)):
				identifiers = f" '{', '.join(identifiersOf(after))}'"
			raise NotAChildError(
				f"{getTypeName(after)}{identifiers} is not a declared item of this {getTypeName(self)}.",
				element=after,
				parent=self
			)

		precedes = any(item is declaredItem for item in self._declaredItems[:index + 1])
		self.MoveDeclaredItem(declaredItem, index if precedes else index + 1)


@export
class WithoutStatementsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for language constructs with a declarative region, but without statements.

	It provides the labeled statements ``_Labels()`` the declaration region expects from its host class: none.

	.. seealso::

	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Package body <pyVHDLModel.DesignUnit.PackageBody>`
	   * :class:`Protected type <pyVHDLModel.Type.ProtectedType>`
	   * :class:`Protected type body <pyVHDLModel.Type.ProtectedTypeBody>`
	"""

	def _Labels(self) -> tuple[ModelEntity, ...]:
		"""
		Return the labeled statements, whose labels are declared in this declarative region.

		:returns: An empty tuple.
		"""
		return ()


@export
class ConcurrentDeclarationRegionMixin(DeclarationRegionMixin, mixin=True):
	# FIXME: define list prefix type e.g. via Union
	"""
	A mixin-class for concurrent declaration regions.

	Entities, architectures, packages, blocks and generate bodies declare items concurrently. Beside
	the namespace, the region keeps a lookup table per kind of declared item (:data:`Types`,
	:data:`Signals`, :data:`Constants`, ...).

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`For generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Package body <pyVHDLModel.DesignUnit.PackageBody>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	   * :class:`Sequential declaration region <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	   * :class:`Namespace <pyVHDLModel.Namespace.Namespace>`
	"""
	_declaredItems:   list                        #: List of all declared items in this concurrent declaration region.
	_namespace:       Namespace                   #: The namespace of this concurrent declaration region.

	# _attributes:     dict[str, Attribute]
	# _aliases:        dict[str, Alias]
	_types:           dict[str, FullType]         #: Dictionary of all types declared in this concurrent declaration region.
	_subtypes:        dict[str, Subtype]          #: Dictionary of all subtypes declared in this concurrent declaration region.
	# _objects:        dict[str, Union[Constant, Variable, Signal]]
	_constants:       dict[str, Constant]         #: Dictionary of all constants declared in this concurrent declaration region.
	_signals:         dict[str, Signal]           #: Dictionary of all signals declared in this concurrent declaration region.
	_sharedVariables: dict[str, SharedVariable]   #: Dictionary of all shared variables declared in this concurrent declaration region.
	_files:           dict[str, File]             #: Dictionary of all files declared in this concurrent declaration region.
	# _subprograms:     dict[str, list[Subprogram]]  #: Dictionary of all subprograms declared in this concurrent declaration region.
	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:       dict[str, list[Function]]   #: Dictionary of all functions declared in this concurrent declaration region, indexed by name; each entry is a list of overloads.
	_procedures:      dict[str, list[Procedure]]  #: Dictionary of all procedures declared in this concurrent declaration region, indexed by name; each entry is a list of overloads.
	_components:      dict[str, Any]              #: Dictionary of all components declared in this concurrent declaration region.

	def __init__(
		self,
		namespaceName:          Nullable[str] = None,
		declaredItems:          Nullable[Iterable] = None,
		sharesRegionWithParent: bool = False
	) -> None:
		# TODO: extract to mixin
		"""
		Initializes a concurrent declaration region.

		:param namespaceName:          Name of this region's namespace, usually the host's label or identifier.
		:param declaredItems:          List of all declared items in this concurrent declaration region.
		:param sharesRegionWithParent: Optional, ``True`` if this region continues its parent's declarative region (an
		                               architecture its entity's, a package body its package's). Default: ``False``.
		"""
		DeclarationRegionMixin.__init__(self)

		self._namespace = Namespace(namespaceName, sharesRegionWithParent=sharesRegionWithParent)

		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item.Parent = self

		self._types =       {}
		self._subtypes =    {}
		# self._objects =     {}
		self._constants =   {}
		self._signals =     {}
		self._sharedVariables = {}
		self._files =       {}
		# self._subprograms = {}
		self._functions =   {}
		self._procedures =  {}
		self._components =  {}

	@readonly
	def DeclaredItems(self) -> list:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	@readonly
	def Types(self) -> dict[str, FullType]:
		"""
		Read-only property to access the types (:attr:`_types`).

		:returns: Dictionary of types, indexed by normalized identifier.
		"""
		return self._types

	@readonly
	def Subtypes(self) -> dict[str, Subtype]:
		"""
		Read-only property to access the subtypes (:attr:`_subtypes`).

		:returns: Dictionary of subtypes, indexed by normalized identifier.
		"""
		return self._subtypes

	# @readonly
	# def Objects(self) -> dict[str, Union[Constant, SharedVariable, Signal, File]]:
	# 	return self._objects

	@readonly
	def Constants(self) -> dict[str, Constant]:
		"""
		Read-only property to access the constants (:attr:`_constants`).

		:returns: Dictionary of constants, indexed by normalized identifier.
		"""
		return self._constants

	@readonly
	def Signals(self) -> dict[str, Signal]:
		"""
		Read-only property to access the signals (:attr:`_signals`).

		:returns: Dictionary of signals, indexed by normalized identifier.
		"""
		return self._signals

	@readonly
	def SharedVariables(self) -> dict[str, SharedVariable]:
		"""
		Read-only property to access the shared variables (:attr:`_sharedVariables`).

		:returns: Dictionary of shared variables, indexed by normalized identifier.
		"""
		return self._sharedVariables

	@readonly
	def Files(self) -> dict[str, File]:
		"""
		Read-only property to access the files (:attr:`_files`).

		:returns: Dictionary of files, indexed by normalized identifier.
		"""
		return self._files

	# @readonly
	# def Subprograms(self) -> dict[str, Subprogram]:
	# 	return self._subprograms

	@readonly
	def Functions(self) -> dict[str, list[Function]]:
		"""
		Read-only property to access the functions (:attr:`_functions`).

		:returns: Dictionary of functions, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> dict[str, list[Procedure]]:
		"""
		Read-only property to access the procedures (:attr:`_procedures`).

		:returns: Dictionary of procedures, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._procedures

	@readonly
	def Components(self) -> dict[str, Any]:
		"""
		Read-only property to access the components (:attr:`_components`).

		:returns: Dictionary of components, indexed by normalized identifier.
		"""
		return self._components

	def _Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Return all declarations of this declarative region.

		A host class with interface items extends the list by its interface items, listed first.

		:returns: Tuple of declarations: the declared items, in declaration order.
		"""
		return tuple(self._declaredItems)

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the concurrent declaration region.

		.. rubric:: Algorithm

		1. Clear all lookup tables and remove all declared items from :attr:`_namespace`. Interface items and imported
		   items stay in the namespace.
		2. Iterate all declared items:

		   * Every declared item is added to :attr:`_namespace`, except a protected type body.
		   * If the declared item is a :class:`~pyVHDLModel.Type.ProtectedTypeBody`, skip it: it completes its protected
		     type.
		   * If the declared item is a :class:`~pyVHDLModel.Type.FullType`, then add an entry to :attr:`_types`.
		   * If the declared item is a :class:`~pyVHDLModel.Type.Subtype`, then add an entry to :attr:`_subtypes`.
		   * If the declared item is a :class:`~pyVHDLModel.Subprogram.Function`, then add an entry to :attr:`_functions`.
		   * If the declared item is a :class:`~pyVHDLModel.Subprogram.Procedure`, then add an entry to :attr:`_procedures`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.Constant`, then add an entry to :attr:`_constants`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.Signal`, then add an entry to :attr:`_signals`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.Variable`, TODO.
		   * If the declared item is a :class:`~pyVHDLModel.Object.SharedVariable`, then add an entry to :attr:`_sharedVariables`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.File`, then add an entry to :attr:`_files`.
		   * If the declared item is neither of these types, call :meth:`_IndexOtherDeclaredItem`. |br|
		     Derived classes may override this virtual function.

		Indexing again yields the same lookup tables and namespace.

		.. seealso::

		   :meth:`pyVHDLModel.Design.IndexPackages`
		     Iterate all packages in the design and index declared items.
		   :meth:`pyVHDLModel.Library.IndexPackages`
		     Iterate all packages in the library and index declared items.
		   :meth:`pyVHDLModel.Library._IndexOtherDeclaredItem`
		     Iterate all packages in the library and index declared items.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self._types.clear()
		self._subtypes.clear()
		self._constants.clear()
		self._signals.clear()
		self._sharedVariables.clear()
		self._files.clear()
		self._functions.clear()
		self._procedures.clear()
		self._components.clear()
		self._RemoveDeclaredItemsFromNamespace()

		for item in self._declaredItems:
			self._IndexDeclaredItem(item)

		self._areDeclaredItemsIndexed = True

	def _IndexDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Add a declared item to the namespace and to the lookup table matching its kind.

		:param item: The declared item.
		"""
		from pyVHDLModel.DesignUnit import Component
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType, ProtectedTypeBody

		if isinstance(item, ProtectedTypeBody):
			# A protected type body completes its protected type.
			pass
		elif isinstance(item, FullType):
			self._types[item._normalizedIdentifier] = item
			self._namespace.AddElement(item._normalizedIdentifier, item)
		elif isinstance(item, Subtype):
			self._subtypes[item._normalizedIdentifier] = item
			self._namespace.AddElement(item._normalizedIdentifier, item)
		elif isinstance(item, Function):
			# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
			#        real overload resolution yet).
			self._functions.setdefault(item._normalizedIdentifier, []).append(item)
			self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
		elif isinstance(item, Procedure):
			# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
			#        real overload resolution yet).
			self._procedures.setdefault(item._normalizedIdentifier, []).append(item)
			self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
		elif isinstance(item, Constant):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._constants[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
				# self._objects[normalizedIdentifier] = item
		elif isinstance(item, Signal):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._signals[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
		elif isinstance(item, Variable):
			# TODO: variables declared in a concurrent declaration region (e.g. shared variables outside a
			#       protected type) are not yet indexed into a dedicated namespace/lookup table.
			identifiers = ", ".join(f"'{i}'" for i in item._identifiers)
			WarningCollector.Raise(
				NotImplementedWarning(f"IndexDeclaredItems: variable(s) {identifiers} are not yet indexed.", item=item)
			)
		elif isinstance(item, SharedVariable):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._sharedVariables[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
		elif isinstance(item, File):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._files[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
		elif isinstance(item, Component):
			self._components[item._normalizedIdentifier] = item
			self._namespace.AddElement(item._normalizedIdentifier, item)
		else:
			self._IndexOtherDeclaredItem(item)

	def _UnindexDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Remove a declared item from the namespace and from the lookup table matching its kind.

		:param item: The declared item.
		"""
		from pyVHDLModel.DesignUnit import Component
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType, ProtectedTypeBody

		if isinstance(item, ProtectedTypeBody):
			pass
		elif isinstance(item, FullType):
			self._RemoveDeclaredItemEntries(self._types, item)
		elif isinstance(item, Subtype):
			self._RemoveDeclaredItemEntries(self._subtypes, item)
		elif isinstance(item, (Function, Procedure)):
			self._UnindexOverload(item)
		elif isinstance(item, Constant):
			self._RemoveDeclaredItemEntries(self._constants, item)
		elif isinstance(item, Signal):
			self._RemoveDeclaredItemEntries(self._signals, item)
		elif isinstance(item, Variable):
			pass
		elif isinstance(item, SharedVariable):
			self._RemoveDeclaredItemEntries(self._sharedVariables, item)
		elif isinstance(item, File):
			self._RemoveDeclaredItemEntries(self._files, item)
		elif isinstance(item, Component):
			self._RemoveDeclaredItemEntries(self._components, item)
		else:
			self._UnindexOtherDeclaredItem(item)


@export
class SequentialDeclarationRegionMixin(DeclarationRegionMixin, mixin=True):
	"""
	A mixin-class for sequential declaration regions: process statements and subprogram bodies.

	.. note::

	   VHDL's ``process_declarative_item`` and ``subprogram_declarative_item`` rules are identical, so both
	   regions share this implementation. Compared to a concurrent region
	   (:class:`ConcurrentDeclarationRegionMixin`, ``block_declarative_item``), a sequential region can
	   declare a **variable**, but no signal, shared variable, component or mode view, and none of the
	   specifications.

	.. seealso::

	   * :class:`Process statement <pyVHDLModel.Concurrent.ProcessStatement>`
	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Concurrent declaration region <pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin>`
	   * :class:`Namespace <pyVHDLModel.Namespace.Namespace>`
	"""

	_declaredItems: list                        #: List of all declared items in this sequential declaration region.
	_namespace:     Namespace                   #: The namespace of this sequential declaration region.

	_types:         dict[str, FullType]         #: Dictionary of all types declared in this sequential declaration region.
	_subtypes:      dict[str, Subtype]          #: Dictionary of all subtypes declared in this sequential declaration region.
	_constants:     dict[str, Constant]         #: Dictionary of all constants declared in this sequential declaration region.
	_variables:     dict[str, Variable]         #: Dictionary of all variables declared in this sequential declaration region.
	_files:         dict[str, File]             #: Dictionary of all files declared in this sequential declaration region.
	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:     dict[str, list[Function]]   #: Dictionary of all functions declared in this sequential declaration region, indexed by name; each entry is a list of overloads.
	_procedures:    dict[str, list[Procedure]]  #: Dictionary of all procedures declared in this sequential declaration region, indexed by name; each entry is a list of overloads.

	def __init__(self, namespaceName: Nullable[str] = None, declaredItems: Nullable[Iterable] = None) -> None:
		"""
		Initialize a sequential declaration region.

		:param namespaceName:  Name of this region's namespace, usually the host's label or identifier.
		:param declaredItems:  The items declared in this region.
		"""
		DeclarationRegionMixin.__init__(self)

		self._namespace = Namespace(namespaceName)

		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item.Parent = self

		self._types =      {}
		self._subtypes =   {}
		self._constants =  {}
		self._variables =  {}
		self._files =      {}
		self._functions =  {}
		self._procedures = {}

	@readonly
	def DeclaredItems(self) -> list:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	@readonly
	def Namespace(self) -> Namespace:
		"""
		Read-only property to access this region's namespace (:attr:`_namespace`).

		:returns: The namespace.
		"""
		return self._namespace

	@readonly
	def Types(self) -> dict[str, FullType]:
		"""
		Read-only property to access the declared types (:attr:`_types`).

		:returns: Dictionary of types, indexed by normalized identifier.
		"""
		return self._types

	@readonly
	def Subtypes(self) -> dict[str, Subtype]:
		"""
		Read-only property to access the declared subtypes (:attr:`_subtypes`).

		:returns: Dictionary of subtypes, indexed by normalized identifier.
		"""
		return self._subtypes

	@readonly
	def Constants(self) -> dict[str, Constant]:
		"""
		Read-only property to access the declared constants (:attr:`_constants`).

		:returns: Dictionary of constants, indexed by normalized identifier.
		"""
		return self._constants

	@readonly
	def Variables(self) -> dict[str, Variable]:
		"""
		Read-only property to access the declared variables (:attr:`_variables`).

		:returns: Dictionary of variables, indexed by normalized identifier.
		"""
		return self._variables

	@readonly
	def Files(self) -> dict[str, File]:
		"""
		Read-only property to access the declared files (:attr:`_files`).

		:returns: Dictionary of files, indexed by normalized identifier.
		"""
		return self._files

	@readonly
	def Functions(self) -> dict[str, list[Function]]:
		"""
		Read-only property to access the declared functions (:attr:`_functions`).

		:returns: Dictionary of functions, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> dict[str, list[Procedure]]:
		"""
		Read-only property to access the declared procedures (:attr:`_procedures`).

		:returns: Dictionary of procedures, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._procedures

	def _Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Return all declarations of this declarative region.

		A host class with interface items extends the list by its interface items, listed first.

		:returns: Tuple of declarations: the declared items, in declaration order.
		"""
		return tuple(self._declaredItems)

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the sequential declaration region.

		All lookup tables are cleared and all declared items are removed from :attr:`_namespace` first. Then every declared
		item is added to :attr:`_namespace`, and additionally to the lookup table matching its kind. Items of an unhandled
		kind are passed to :meth:`_IndexOtherDeclaredItem`. A protected type body completes its protected type, so it's
		skipped. Indexing again yields the same lookup tables and namespace.

		.. seealso::

		   :meth:`ConcurrentDeclarationRegionMixin.IndexDeclaredItems`
		     The same algorithm for a concurrent declaration region.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self._types.clear()
		self._subtypes.clear()
		self._constants.clear()
		self._variables.clear()
		self._files.clear()
		self._functions.clear()
		self._procedures.clear()
		self._RemoveDeclaredItemsFromNamespace()

		for item in self._declaredItems:
			self._IndexDeclaredItem(item)

		self._areDeclaredItemsIndexed = True

	def _IndexDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Add a declared item to the namespace and to the lookup table matching its kind.

		:param item: The declared item.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType, ProtectedTypeBody

		if isinstance(item, ProtectedTypeBody):
			# A protected type body completes its protected type.
			pass
		elif isinstance(item, FullType):
			self._types[item._normalizedIdentifier] = item
			self._namespace.AddElement(item._normalizedIdentifier, item)
		elif isinstance(item, Subtype):
			self._subtypes[item._normalizedIdentifier] = item
			self._namespace.AddElement(item._normalizedIdentifier, item)
		elif isinstance(item, Function):
			# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
			#        real overload resolution yet).
			self._functions.setdefault(item._normalizedIdentifier, []).append(item)
			self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
		elif isinstance(item, Procedure):
			# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
			#        real overload resolution yet).
			self._procedures.setdefault(item._normalizedIdentifier, []).append(item)
			self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
		elif isinstance(item, Constant):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._constants[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
		elif isinstance(item, Variable):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._variables[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
		elif isinstance(item, File):
			for normalizedIdentifier in item._normalizedIdentifiers:
				self._files[normalizedIdentifier] = item
				self._namespace.AddElement(normalizedIdentifier, item)
		else:
			self._IndexOtherDeclaredItem(item)

	def _UnindexDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Remove a declared item from the namespace and from the lookup table matching its kind.

		:param item: The declared item.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType, ProtectedTypeBody

		if isinstance(item, ProtectedTypeBody):
			pass
		elif isinstance(item, FullType):
			self._RemoveDeclaredItemEntries(self._types, item)
		elif isinstance(item, Subtype):
			self._RemoveDeclaredItemEntries(self._subtypes, item)
		elif isinstance(item, (Function, Procedure)):
			self._UnindexOverload(item)
		elif isinstance(item, Constant):
			self._RemoveDeclaredItemEntries(self._constants, item)
		elif isinstance(item, Variable):
			self._RemoveDeclaredItemEntries(self._variables, item)
		elif isinstance(item, File):
			self._RemoveDeclaredItemEntries(self._files, item)
		else:
			self._UnindexOtherDeclaredItem(item)


@export
class ProtectedTypeDeclarationRegionMixin(DeclarationRegionMixin, mixin=True):
	"""
	A mixin-class for the declarative region of a protected type declaration.

	VHDL's ``protected_type_declarative_item`` rule admits subprogram declarations only, making this the
	narrowest declarative region in the language. A protected type *body* differs: its declarative part
	matches a subprogram's, so it uses :class:`SequentialDeclarationRegionMixin`.

	.. seealso::

	   * :class:`Protected type <pyVHDLModel.Type.ProtectedType>`
	   * :class:`Protected type body <pyVHDLModel.Type.ProtectedTypeBody>`
	   * :class:`Sequential declaration region <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	   * :class:`Namespace <pyVHDLModel.Namespace.Namespace>`
	"""

	_declaredItems: list                        #: List of all declared items in this protected type declaration.
	_namespace:     Namespace                   #: The namespace of this protected type declaration.

	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:     dict[str, list[Function]]   #: All declared functions, indexed by name; each is a list of overloads.
	_procedures:    dict[str, list[Procedure]]  #: All declared procedures by name; each is a list of overloads.

	def __init__(self, namespaceName: Nullable[str] = None, declaredItems: Nullable[Iterable] = None) -> None:
		"""
		Initialize a protected type declaration region.

		:param namespaceName: Name of this region's namespace, usually the protected type's identifier.
		:param declaredItems: The items declared in this region.
		"""
		DeclarationRegionMixin.__init__(self)

		self._namespace = Namespace(namespaceName)

		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item.Parent = self

		self._functions =  {}
		self._procedures = {}

	@readonly
	def DeclaredItems(self) -> list:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of all declared items.
		"""
		return self._declaredItems

	@readonly
	def Functions(self) -> dict[str, list[Function]]:
		"""
		Read-only property to access the declared functions (:attr:`_functions`).

		:returns: Dictionary of all functions, indexed by name; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> dict[str, list[Procedure]]:
		"""
		Read-only property to access the declared procedures (:attr:`_procedures`).

		:returns: Dictionary of all procedures, indexed by name; each entry is a list of overloads.
		"""
		return self._procedures

	def _Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Return all declarations of this declarative region.

		A host class with interface items extends the list by its interface items, listed first.

		:returns: Tuple of declarations: the declared items, in declaration order.
		"""
		return tuple(self._declaredItems)

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the protected type declaration.

		Both lookup tables are cleared and all declared items are removed from :attr:`_namespace` first. Only subprogram
		declarations are legal here, so anything else is passed to :meth:`_IndexOtherDeclaredItem`. Indexing again yields
		the same lookup tables and namespace.

		.. seealso::

		   :meth:`SequentialDeclarationRegionMixin.IndexDeclaredItems`
		     The same algorithm for the protected type's body.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self._functions.clear()
		self._procedures.clear()
		self._RemoveDeclaredItemsFromNamespace()

		for item in self._declaredItems:
			self._IndexDeclaredItem(item)

		self._areDeclaredItemsIndexed = True

	def _IndexDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Add a declared item to the namespace and to the lookup table matching its kind.

		:param item: The declared item.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		if isinstance(item, Function):
			# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
			#        real overload resolution yet).
			self._functions.setdefault(item._normalizedIdentifier, []).append(item)
			self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
		elif isinstance(item, Procedure):
			# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
			#        real overload resolution yet).
			self._procedures.setdefault(item._normalizedIdentifier, []).append(item)
			self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
		else:
			self._IndexOtherDeclaredItem(item)

	def _UnindexDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Remove a declared item from the namespace and from the lookup table matching its kind.

		:param item: The declared item.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		if isinstance(item, (Function, Procedure)):
			self._UnindexOverload(item)
		else:
			self._UnindexOtherDeclaredItem(item)
