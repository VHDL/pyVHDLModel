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

from typing                  import TYPE_CHECKING, List, Dict, Iterable, Optional as Nullable, Any

from pyTooling.Common        import getFullyQualifiedName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType
from pyTooling.Warning       import WarningCollector

from pyVHDLModel.Base        import NamedEntityMixin, MultipleNamedEntityMixin, identifiersOf, normalizedIdentifiersOf
from pyVHDLModel.Exception   import NotImplementedWarning, AlreadyInDesignError, NotAChildError
from pyVHDLModel.Exception   import DuplicateGenericError, DuplicatePortError, DuplicateParameterError
from pyVHDLModel.Namespace   import Namespace
from pyVHDLModel.Object      import Constant, SharedVariable, File, Variable, Signal
if TYPE_CHECKING:
	from pyVHDLModel.Interface import GenericInterfaceItemMixin, PortInterfaceItemMixin, ParameterInterfaceItemMixin
	from pyVHDLModel.Interface import PortSignalInterfaceItem
	from pyVHDLModel.Type      import Subtype, FullType

# `pyVHDLModel.Subprogram` imports this module (Subprogram is a sequential declaration region), so
# `Function`/`Procedure` are quoted in annotations and imported lazily where they're needed at runtime.
# The same holds for the interface item classes of `pyVHDLModel.Interface`.



@export
class WithGenericsMixin(metaclass=ExtendedType, mixin=True, expects=("_AddToNamespace", "_RemoveFromNamespace")):
	"""
	A mixin-class for language constructs with a generic clause.

	The host class provides ``_AddToNamespace(element)`` and ``_RemoveFromNamespace(element)``, called when a generic is
	inserted or removed: :class:`~pyVHDLModel.Regions.DeclarationRegionMixin` updates its namespace, a language construct
	without a namespace implements both as no-operations.

	.. seealso::

	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Component <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Generic group <pyVHDLModel.Interface.GenericGroup>`
	"""
	_genericItems: List[GenericInterfaceItemMixin]  #: List of all generics, in declaration order.

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
	def GenericItems(self) -> List[GenericInterfaceItemMixin]:
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
		:raises DuplicateGenericError: If the generic clause already has a generic of the same identifier.

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
		:param genericItem:            The generic to insert.
		:raises ValueError:            If parameter 'index' is ``None``.
		:raises TypeError:             If parameter 'index' is not of type :class:`int`.
		:raises ValueError:            If parameter 'index' is out of range.
		:raises ValueError:            If parameter 'genericItem' is ``None``.
		:raises TypeError:             If parameter 'genericItem' is not of type
		                               :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`.
		:raises AlreadyInDesignError:  If parameter 'genericItem' already has a parent.
		:raises DuplicateGenericError: If the generic clause already has a generic of the same identifier.

		.. seealso::

		   :meth:`AddGenericItem`
		      |rarr| Add a generic at the end of the generic clause.
		   :meth:`RemoveGenericItem`
		      |rarr| Remove a generic from the generic clause.
		"""
		from pyVHDLModel.Interface import GenericInterfaceItemMixin

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif index < 0 or index > len(self._genericItems):
			ex = ValueError(f"Parameter 'index' is out of range 0..{len(self._genericItems)}.")
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
			ex = AlreadyInDesignError(f"{genericItem.__class__.__name__} '{identifiers}' already has a parent.")
			ex.add_note(f"Remove it from its {genericItem._parent.__class__.__name__} first.")
			raise ex

		existingIdentifiers = {name for item in self._genericItems for name in normalizedIdentifiersOf(item)}
		newIdentifiers = zip(identifiersOf(genericItem), normalizedIdentifiersOf(genericItem))
		for identifier, normalizedIdentifier in newIdentifiers:
			if normalizedIdentifier in existingIdentifiers:
				raise DuplicateGenericError(f"{self.__class__.__name__} already has a generic '{identifier}'.")

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
				f"{genericItem.__class__.__name__} '{identifiers}' is not a generic of this {self.__class__.__name__}."
			)

		self._RemoveFromNamespace(genericItem)
		del self._genericItems[index]
		genericItem._parent = None


@export
class WithPortsMixin(metaclass=ExtendedType, mixin=True, expects=("_AddToNamespace", "_RemoveFromNamespace")):
	"""
	A mixin-class for language constructs with a port clause.

	The host class provides ``_AddToNamespace(element)`` and ``_RemoveFromNamespace(element)``, called when a port is
	inserted or removed: :class:`~pyVHDLModel.Regions.DeclarationRegionMixin` updates its namespace, a language construct
	without a namespace implements both as no-operations.

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Component <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Port group <pyVHDLModel.Interface.PortGroup>`
	"""
	_portItems: List[PortInterfaceItemMixin]  #: List of all ports, in declaration order.

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
	def PortItems(self) -> List[PortInterfaceItemMixin]:
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
		:raises DuplicatePortError:   If the port clause already has a port of the same identifier.

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
		:param portItem:              The port to insert.
		:raises ValueError:           If parameter 'index' is ``None``.
		:raises TypeError:            If parameter 'index' is not of type :class:`int`.
		:raises ValueError:           If parameter 'index' is out of range.
		:raises ValueError:           If parameter 'portItem' is ``None``.
		:raises TypeError:            If parameter 'portItem' is not of type
		                              :class:`~pyVHDLModel.Interface.PortSignalInterfaceItem`.
		:raises AlreadyInDesignError: If parameter 'portItem' already has a parent.
		:raises DuplicatePortError:   If the port clause already has a port of the same identifier.

		.. seealso::

		   :meth:`AddPortItem`
		      |rarr| Add a port at the end of the port clause.
		   :meth:`RemovePortItem`
		      |rarr| Remove a port from the port clause.
		"""
		from pyVHDLModel.Interface import PortSignalInterfaceItem

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif index < 0 or index > len(self._portItems):
			ex = ValueError(f"Parameter 'index' is out of range 0..{len(self._portItems)}.")
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
			ex = AlreadyInDesignError(f"{portItem.__class__.__name__} '{identifiers}' already has a parent.")
			ex.add_note(f"Remove it from its {portItem._parent.__class__.__name__} first.")
			raise ex

		existingIdentifiers = {name for item in self._portItems for name in normalizedIdentifiersOf(item)}
		newIdentifiers = zip(identifiersOf(portItem), normalizedIdentifiersOf(portItem))
		for identifier, normalizedIdentifier in newIdentifiers:
			if normalizedIdentifier in existingIdentifiers:
				raise DuplicatePortError(f"{self.__class__.__name__} already has a port '{identifier}'.")

		self._portItems.insert(index, portItem)
		portItem.Parent = self
		self._AddToNamespace(portItem)

	def RemovePortItem(self, portItem: PortSignalInterfaceItem) -> None:
		"""
		Remove a port from the port clause.

		The port is detached: its parent is cleared and its identifiers are removed from the language construct's
		namespace, if it has one. The port itself is unchanged and can be added to another language construct, or
		inserted at another position.

		:param portItem:        The port to remove.
		:raises ValueError:     If parameter 'portItem' is ``None``.
		:raises TypeError:      If parameter 'portItem' is not of type
		                        :class:`~pyVHDLModel.Interface.PortSignalInterfaceItem`.
		:raises NotAChildError: If parameter 'portItem' is not a port of this language construct.

		.. seealso::

		   :meth:`AddPortItem`
		      |rarr| Add a port at the end of the port clause.
		   :meth:`InsertPortItem`
		      |rarr| Insert a port at a position of the port clause.
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
				f"{portItem.__class__.__name__} '{identifiers}' is not a port of this {self.__class__.__name__}."
			)

		del self._portItems[index]
		portItem._parent = None
		self._RemoveFromNamespace(portItem)


@export
class WithParametersMixin(metaclass=ExtendedType, mixin=True, expects=("_AddToNamespace", "_RemoveFromNamespace")):
	"""
	A mixin-class for language constructs with a parameter list.

	The host class provides ``_AddToNamespace(element)`` and ``_RemoveFromNamespace(element)``, called when a parameter is
	inserted or removed: :class:`~pyVHDLModel.Regions.DeclarationRegionMixin` updates its namespace, a language construct
	without a namespace implements both as no-operations.

	.. seealso::

	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Parameter group <pyVHDLModel.Interface.ParameterGroup>`
	"""
	_parameterItems: List[ParameterInterfaceItemMixin]  #: List of all parameters, in declaration order.

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
	def ParameterItems(self) -> List[ParameterInterfaceItemMixin]:
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
		:raises DuplicateParameterError: If the parameter list already has a parameter of the same identifier.

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
		:param parameterItem:            The parameter to insert.
		:raises ValueError:              If parameter 'index' is ``None``.
		:raises TypeError:               If parameter 'index' is not of type :class:`int`.
		:raises ValueError:              If parameter 'index' is out of range.
		:raises ValueError:              If parameter 'parameterItem' is ``None``.
		:raises TypeError:               If parameter 'parameterItem' is not of type
		                                 :class:`~pyVHDLModel.Interface.ParameterInterfaceItemMixin`.
		:raises AlreadyInDesignError:    If parameter 'parameterItem' already has a parent.
		:raises DuplicateParameterError: If the parameter list already has a parameter of the same identifier.

		.. seealso::

		   :meth:`AddParameterItem`
		      |rarr| Add a parameter at the end of the parameter list.
		   :meth:`RemoveParameterItem`
		      |rarr| Remove a parameter from the parameter list.
		"""
		from pyVHDLModel.Interface import ParameterInterfaceItemMixin

		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif index < 0 or index > len(self._parameterItems):
			ex = ValueError(f"Parameter 'index' is out of range 0..{len(self._parameterItems)}.")
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
			ex = AlreadyInDesignError(f"{parameterItem.__class__.__name__} '{identifiers}' already has a parent.")
			ex.add_note(f"Remove it from its {parameterItem._parent.__class__.__name__} first.")
			raise ex

		existingIdentifiers = {name for item in self._parameterItems for name in normalizedIdentifiersOf(item)}
		newIdentifiers = zip(identifiersOf(parameterItem), normalizedIdentifiersOf(parameterItem))
		for identifier, normalizedIdentifier in newIdentifiers:
			if normalizedIdentifier in existingIdentifiers:
				raise DuplicateParameterError(f"{self.__class__.__name__} already has a parameter '{identifier}'.")

		self._parameterItems.insert(index, parameterItem)
		parameterItem.Parent = self
		self._AddToNamespace(parameterItem)

	def RemoveParameterItem(self, parameterItem: ParameterInterfaceItemMixin) -> None:
		"""
		Remove a parameter from the parameter list.

		The parameter is detached: its parent is cleared and its identifiers are removed from the language construct's
		namespace, if it has one. The parameter itself is unchanged and can be added to another language construct, or
		inserted at another position.

		:param parameterItem:   The parameter to remove.
		:raises ValueError:     If parameter 'parameterItem' is ``None``.
		:raises TypeError:      If parameter 'parameterItem' is not of type
		                        :class:`~pyVHDLModel.Interface.ParameterInterfaceItemMixin`.
		:raises NotAChildError: If parameter 'parameterItem' is not a parameter of this language construct.

		.. seealso::

		   :meth:`AddParameterItem`
		      |rarr| Add a parameter at the end of the parameter list.
		   :meth:`InsertParameterItem`
		      |rarr| Insert a parameter at a position of the parameter list.
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
				f"{parameterItem.__class__.__name__} '{identifiers}' is not a parameter of this {self.__class__.__name__}."
			)

		del self._parameterItems[index]
		parameterItem._parent = None
		self._RemoveFromNamespace(parameterItem)


@export
class DeclarationRegionMixin(metaclass=ExtendedType, mixin=True):
	"""
	A base-class for the concurrent and sequential declaration region mixins.

	It carries what both regions share: adding interface items to the region's namespace, and the hook for
	declared items neither region handles itself.

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
	"""
	_isIndexed: bool  #: ``True`` if :meth:`IndexDeclaredItems` filled the region's namespace.

	def __init__(self) -> None:
		"""
		Initializes a declaration region, which isn't indexed yet.
		"""
		self._isIndexed = False

	def _IndexGenericItems(self) -> None:
		"""Add this region's generics to its namespace."""
		for item in self._genericItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _IndexPortItems(self) -> None:
		"""Add this region's ports to its namespace."""
		for item in self._portItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _IndexParameterItems(self) -> None:
		"""Add this region's parameters to its namespace."""
		for item in self._parameterItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _AddToNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Add an element's identifiers to this region's namespace.

		Nothing is added to a region not indexed yet: :meth:`IndexDeclaredItems` adds the element later.

		:param element: The named element to add, e.g. an interface item.
		"""
		if not self._isIndexed:
			return

		for normalizedIdentifier in normalizedIdentifiersOf(element):
			self._namespace.AddElement(normalizedIdentifier, element)

	def _RemoveFromNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Remove an element's identifiers from this region's namespace.

		Nothing is removed from a region not indexed yet, as its namespace doesn't contain the element.

		:param element:              The named element to remove, e.g. an interface item.
		:raises NotInNamespaceError: If the region is indexed, and an identifier of the element isn't declared in the
		                             namespace.
		:raises NotInNamespaceError: If the region is indexed, and an identifier of the element refers to another element,
		                             e.g. a duplicate declaration.
		"""
		if not self._isIndexed:
			return

		for normalizedIdentifier in normalizedIdentifiersOf(element):
			self._namespace.RemoveElement(normalizedIdentifier, element)

	def _IndexOtherDeclaredItem(self, item) -> None:
		"""Hook for declared items the region doesn't handle itself. Derived classes may override it."""
		pass


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
	_declaredItems:   List                        #: List of all declared items in this concurrent declaration region.

	# _attributes:     Dict[str, Attribute]
	# _aliases:        Dict[str, Alias]
	_types:           Dict[str, FullType]         #: Dictionary of all types declared in this concurrent declaration region.
	_subtypes:        Dict[str, Subtype]          #: Dictionary of all subtypes declared in this concurrent declaration region.
	# _objects:        Dict[str, Union[Constant, Variable, Signal]]
	_constants:       Dict[str, Constant]         #: Dictionary of all constants declared in this concurrent declaration region.
	_signals:         Dict[str, Signal]           #: Dictionary of all signals declared in this concurrent declaration region.
	_sharedVariables: Dict[str, SharedVariable]   #: Dictionary of all shared variables declared in this concurrent declaration region.
	_files:           Dict[str, File]             #: Dictionary of all files declared in this concurrent declaration region.
	# _subprograms:     Dict[str, List[Subprogram]]  #: Dictionary of all subprograms declared in this concurrent declaration region.
	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:       Dict[str, List[Function]]   #: Dictionary of all functions declared in this concurrent declaration region, indexed by name; each entry is a list of overloads.
	_procedures:      Dict[str, List[Procedure]]  #: Dictionary of all procedures declared in this concurrent declaration region, indexed by name; each entry is a list of overloads.
	_components:      Dict[str, Any]              #: Dictionary of all components declared in this concurrent declaration region.

	def __init__(self, declaredItems: Nullable[Iterable] = None) -> None:
		# TODO: extract to mixin
		"""
		Initializes a concurrent declaration region.

		:param declaredItems: List of all declared items in this concurrent declaration region.
		"""
		DeclarationRegionMixin.__init__(self)

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
	def DeclaredItems(self) -> List:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	@readonly
	def Types(self) -> Dict[str, FullType]:
		"""
		Read-only property to access the types (:attr:`_types`).

		:returns: Dictionary of types, indexed by normalized identifier.
		"""
		return self._types

	@readonly
	def Subtypes(self) -> Dict[str, Subtype]:
		"""
		Read-only property to access the subtypes (:attr:`_subtypes`).

		:returns: Dictionary of subtypes, indexed by normalized identifier.
		"""
		return self._subtypes

	# @readonly
	# def Objects(self) -> Dict[str, Union[Constant, SharedVariable, Signal, File]]:
	# 	return self._objects

	@readonly
	def Constants(self) -> Dict[str, Constant]:
		"""
		Read-only property to access the constants (:attr:`_constants`).

		:returns: Dictionary of constants, indexed by normalized identifier.
		"""
		return self._constants

	@readonly
	def Signals(self) -> Dict[str, Signal]:
		"""
		Read-only property to access the signals (:attr:`_signals`).

		:returns: Dictionary of signals, indexed by normalized identifier.
		"""
		return self._signals

	@readonly
	def SharedVariables(self) -> Dict[str, SharedVariable]:
		"""
		Read-only property to access the shared variables (:attr:`_sharedVariables`).

		:returns: Dictionary of shared variables, indexed by normalized identifier.
		"""
		return self._sharedVariables

	@readonly
	def Files(self) -> Dict[str, File]:
		"""
		Read-only property to access the files (:attr:`_files`).

		:returns: Dictionary of files, indexed by normalized identifier.
		"""
		return self._files

	# @readonly
	# def Subprograms(self) -> Dict[str, Subprogram]:
	# 	return self._subprograms

	@readonly
	def Functions(self) -> Dict[str, List[Function]]:
		"""
		Read-only property to access the functions (:attr:`_functions`).

		:returns: Dictionary of functions, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> Dict[str, List[Procedure]]:
		"""
		Read-only property to access the procedures (:attr:`_procedures`).

		:returns: Dictionary of procedures, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._procedures

	@readonly
	def Components(self) -> Dict[str, Any]:
		"""
		Read-only property to access the components (:attr:`_components`).

		:returns: Dictionary of components, indexed by normalized identifier.
		"""
		return self._components

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the concurrent declaration region.

		.. rubric:: Algorithm

		1. Iterate all declared items:

		   * Every declared item is added to :attr:`_namespace`.
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

		.. seealso::

		   :meth:`pyVHDLModel.Design.IndexPackages`
		     Iterate all packages in the design and index declared items.
		   :meth:`pyVHDLModel.Library.IndexPackages`
		     Iterate all packages in the library and index declared items.
		   :meth:`pyVHDLModel.Library._IndexOtherDeclaredItem`
		     Iterate all packages in the library and index declared items.
		"""
		from pyVHDLModel.DesignUnit import Component
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType

		for item in self._declaredItems:
			if isinstance(item, FullType):
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
				WarningCollector.Raise(NotImplementedWarning(f"IndexDeclaredItems: variable(s) {identifiers} are not yet indexed."))
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

		self._isIndexed = True


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

	_declaredItems: List                        #: List of all declared items in this sequential declaration region.
	_namespace:     Namespace                   #: The namespace of this sequential declaration region.

	_types:         Dict[str, FullType]         #: Dictionary of all types declared in this sequential declaration region.
	_subtypes:      Dict[str, Subtype]          #: Dictionary of all subtypes declared in this sequential declaration region.
	_constants:     Dict[str, Constant]         #: Dictionary of all constants declared in this sequential declaration region.
	_variables:     Dict[str, Variable]         #: Dictionary of all variables declared in this sequential declaration region.
	_files:         Dict[str, File]             #: Dictionary of all files declared in this sequential declaration region.
	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:     Dict[str, List[Function]]   #: Dictionary of all functions declared in this sequential declaration region, indexed by name; each entry is a list of overloads.
	_procedures:    Dict[str, List[Procedure]]  #: Dictionary of all procedures declared in this sequential declaration region, indexed by name; each entry is a list of overloads.

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
	def DeclaredItems(self) -> List:
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
	def Types(self) -> Dict[str, FullType]:
		"""
		Read-only property to access the declared types (:attr:`_types`).

		:returns: Dictionary of types, indexed by normalized identifier.
		"""
		return self._types

	@readonly
	def Subtypes(self) -> Dict[str, Subtype]:
		"""
		Read-only property to access the declared subtypes (:attr:`_subtypes`).

		:returns: Dictionary of subtypes, indexed by normalized identifier.
		"""
		return self._subtypes

	@readonly
	def Constants(self) -> Dict[str, Constant]:
		"""
		Read-only property to access the declared constants (:attr:`_constants`).

		:returns: Dictionary of constants, indexed by normalized identifier.
		"""
		return self._constants

	@readonly
	def Variables(self) -> Dict[str, Variable]:
		"""
		Read-only property to access the declared variables (:attr:`_variables`).

		:returns: Dictionary of variables, indexed by normalized identifier.
		"""
		return self._variables

	@readonly
	def Files(self) -> Dict[str, File]:
		"""
		Read-only property to access the declared files (:attr:`_files`).

		:returns: Dictionary of files, indexed by normalized identifier.
		"""
		return self._files

	@readonly
	def Functions(self) -> Dict[str, List[Function]]:
		"""
		Read-only property to access the declared functions (:attr:`_functions`).

		:returns: Dictionary of functions, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> Dict[str, List[Procedure]]:
		"""
		Read-only property to access the declared procedures (:attr:`_procedures`).

		:returns: Dictionary of procedures, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._procedures

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the sequential declaration region.

		Every declared item is added to :attr:`_namespace`, and additionally to the lookup table matching its
		kind. Items of an unhandled kind are passed to :meth:`_IndexOtherDeclaredItem`.

		.. seealso::

		   :meth:`ConcurrentDeclarationRegionMixin.IndexDeclaredItems`
		     The same algorithm for a concurrent declaration region.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType

		for item in self._declaredItems:
			if isinstance(item, FullType):
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

		self._isIndexed = True


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

	_declaredItems: List                        #: List of all declared items in this protected type declaration.
	_namespace:     Namespace                   #: The namespace of this protected type declaration.

	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:     Dict[str, List[Function]]   #: All declared functions, indexed by name; each is a list of overloads.
	_procedures:    Dict[str, List[Procedure]]  #: All declared procedures by name; each is a list of overloads.

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
	def DeclaredItems(self) -> List:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of all declared items.
		"""
		return self._declaredItems

	@readonly
	def Functions(self) -> Dict[str, List[Function]]:
		"""
		Read-only property to access the declared functions (:attr:`_functions`).

		:returns: Dictionary of all functions, indexed by name; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> Dict[str, List[Procedure]]:
		"""
		Read-only property to access the declared procedures (:attr:`_procedures`).

		:returns: Dictionary of all procedures, indexed by name; each entry is a list of overloads.
		"""
		return self._procedures

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the protected type declaration.

		Only subprogram declarations are legal here, so anything else is passed to
		:meth:`_IndexOtherDeclaredItem`.

		.. seealso::

		   :meth:`SequentialDeclarationRegionMixin.IndexDeclaredItems`
		     The same algorithm for the protected type's body.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType

		for item in self._declaredItems:
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

		self._isIndexed = True
