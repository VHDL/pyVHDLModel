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

A helper class to implement namespaces and scopes.
"""
from __future__            import annotations

from typing                import TYPE_CHECKING, TypeVar, Generic, Dict, Optional as Nullable, Any, Tuple

from pyVHDLModel.Object    import Obj, Signal, Constant, Variable
from pyVHDLModel.Symbol    import ComponentInstantiationSymbol, Symbol, PossibleReference
from pyVHDLModel.Exception import DuplicateDeclarationWarning

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import readonly
from pyTooling.Warning     import WarningCollector
if TYPE_CHECKING:
	from pyVHDLModel.Type   import Subtype, FullType, BaseType

K = TypeVar("K")
O = TypeVar("O")


class ExtendedKeyError(KeyError):
	"""
	A :exc:`KeyError` reporting which namespaces were searched.

	Raised when a name cannot be resolved. Besides the key (:data:`key`), it carries every namespace
	visited while walking outwards (:data:`searchedNamespaces`).
	"""
	key: str                                   #: The key that was not found.
	searchedNamespaces: Tuple[Namespace, ...]  #: The namespaces that were searched for the key.

	def __init__(self, key: str, searchedNamespaces: Tuple[Namespace, ...], message: str) -> None:
		"""
		Initializes an extended key error.

		:param key:                The key that was not found.
		:param searchedNamespaces: The namespaces that were searched for the key.
		:param message:            The error message.
		"""
		super().__init__(message)

		self.key = key
		self.searchedNamespaces = searchedNamespaces


class Namespace(Generic[K, O]):
	"""
	Represents a namespace: the declared items visible in one declarative region.

	Namespaces nest, so a lookup that misses locally continues in the parent namespace
	(:data:`ParentNamespace`). That is what makes an entity's ports visible inside its architecture,
	and lets a process variable hide an outer signal.

	.. seealso::

	   * :class:`Concurrent declaration region <pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin>`
	   * :class:`Sequential declaration region <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	"""
	_name:                   str                   #: The namespace's name.
	_parentNamespace:        Namespace             #: Reference to the enclosing namespace, ``None`` if outermost.
	_subNamespaces:          Dict[str, Namespace]  #: Dictionary of all nested namespaces, indexed by name.
	_elements:               Dict[K, O]            #: All elements declared in this namespace, indexed by name.
	_sharesRegionWithParent: bool                  #: ``True`` if the parent namespace is the same declarative region.

	def __init__(
		self,
		name: str,
		parentNamespace: Nullable[Namespace] = None,
		sharesRegionWithParent: bool = False
	) -> None:
		"""
		Initializes a namespace.

		:param name:            The namespace's name.
		:param parentNamespace: Reference to the enclosing namespace, or ``None`` for the outermost one.
		"""
		self._name = name
		self._parentNamespace = parentNamespace
		self._subNamespaces = {}
		self._elements = {}
		self._sharesRegionWithParent = sharesRegionWithParent

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the name (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	@property
	def ParentNamespace(self) -> Namespace:
		"""
		Property to access the parent namespace (:attr:`_parentNamespace`).

		:returns: The parent namespace.
		"""
		return self._parentNamespace

	@ParentNamespace.setter
	def ParentNamespace(self, value: Namespace) -> None:
		self._parentNamespace = value
		value._subNamespaces[self._name] = self

	@readonly
	def SharesRegionWithParent(self) -> bool:
		"""
		Read-only property to access whether this namespace continues its parent's declarative region
		(:attr:`_sharesRegionWithParent`).

		.. hint::

		   An entity and its architecture form one VHDL declarative region, as do a package and its body,
		   even though each owns a namespace. A duplicate declaration is reported across such a link, while
		   a genuinely nested region - a process, a block - hides instead.

		:returns: ``True`` if the parent namespace is the same declarative region.
		"""
		return self._sharesRegionWithParent

	@readonly
	def SubNamespaces(self) -> Dict[str, Namespace]:
		"""
		Read-only property to access the sub namespaces (:attr:`_subNamespaces`).

		:returns: Dictionary of sub namespaces.
		"""
		return self._subNamespaces

	def AddElement(self, normalizedIdentifier: K, element: O, overloadable: bool = False) -> None:
		"""
		Add a declared item to this namespace, reporting a duplicate declaration.

		VHDL rejects two declarations sharing an identifier in one declarative region. A region can span
		more than one namespace - an entity and its architecture form one, as do a package and its body -
		so enclosing namespaces are searched too, but only while they share this one's region.

		Overloadable declarations are exempt: several subprograms may share a name as long as their
		signatures differ. Signatures are not compared yet, so two subprograms sharing a name are always
		accepted (see the overload-resolution finding).

		:param normalizedIdentifier: The normalized (lower case) identifier being declared.
		:param element:              The declared item.
		:param overloadable:         ``True`` if this declaration may legally share its name.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		namespace = self
		while namespace is not None:
			existing = namespace._elements.get(normalizedIdentifier)
			# `existing is element` means the region is being re-indexed, not that the name is declared twice.
			isReindex = existing is element
			isOverload = overloadable and isinstance(existing, (Function, Procedure))
			if existing is not None and not isReindex and not isOverload:
				WarningCollector.Raise(DuplicateDeclarationWarning(
					f"Identifier '{normalizedIdentifier}' is already used for a declaration in '{namespace._name}'."
				))
				break

			namespace = namespace._parentNamespace if namespace._sharesRegionWithParent else None

		self._elements[normalizedIdentifier] = element

	def Elements(self) -> Dict[K, O]:
		return self._elements

	def FindComponent(self, componentSymbol: ComponentInstantiationSymbol) -> Component:
		from pyVHDLModel.DesignUnit import Component

		try:
			element = self._elements[componentSymbol._name._normalizedIdentifier]
			if isinstance(element, Component):
				return element
			else:
				ex = TypeError(f"Found element '{componentSymbol._name._identifier}', but it is not a component.")
				ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
				raise ex
		except KeyError:
			key = componentSymbol._name._identifier

			if (parentNamespace := self._parentNamespace) is None:
				raise ExtendedKeyError(key, (self, ), f"Component '{key}' not found in '{self._name}'.")

			try:
				return parentNamespace.FindComponent(componentSymbol)
			except ExtendedKeyError as ex:
				searchedNamespaces = (self, *ex.searchedNamespaces)
				raise ExtendedKeyError(key, searchedNamespaces, f"Component '{key}' not found in: {', '.join(ns._name for ns in searchedNamespaces)}.") from ex

	def FindSubtype(self, subtypeSymbol: Symbol) -> BaseType:
		from pyVHDLModel.Type import Subtype, FullType

		try:
			element = self._elements[subtypeSymbol._name._normalizedIdentifier]
			if isinstance(element, Subtype):
				if PossibleReference.Subtype in subtypeSymbol._possibleReferences:
					return element
				else:
					ex = TypeError(f"Found subtype '{subtypeSymbol._name._identifier}', but it was not expected.")
					ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
					ex.add_note(f"Expected one of: {subtypeSymbol._possibleReferences}.")
					raise ex
			elif isinstance(element, FullType):
				if PossibleReference.Type in subtypeSymbol._possibleReferences:
					return element
				else:
					ex = TypeError(f"Found type '{subtypeSymbol._name._identifier}', but it was not expected.")
					ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
					ex.add_note(f"Expected one of: {subtypeSymbol._possibleReferences}.")
					raise ex
			else:
				ex = TypeError(f"Found element '{subtypeSymbol._name._identifier}', but it is not a type or subtype.")
				ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
				raise ex
		except KeyError:
			key = subtypeSymbol._name._identifier

			if (parentNamespace := self._parentNamespace) is None:
				raise ExtendedKeyError(key, (self, ), f"Subtype '{key}' not found in '{self._name}'.")

			try:
				return parentNamespace.FindSubtype(subtypeSymbol)
			except ExtendedKeyError as ex:
				searchedNamespaces = (self, *ex.searchedNamespaces)
				raise ExtendedKeyError(key, searchedNamespaces, f"Subtype '{key}' not found in: {', '.join(ns._name for ns in searchedNamespaces)}.") from ex

	def FindObject(self, objectSymbol: Symbol) -> Obj:
		try:
			element = self._elements[objectSymbol._name._normalizedIdentifier]
			if isinstance(element, Signal):
				if PossibleReference.Signal in objectSymbol._possibleReferences:
					return element
				elif PossibleReference.SignalAttribute in objectSymbol._possibleReferences:
					return element
				else:
					ex = TypeError(f"Found signal '{objectSymbol._name._identifier}', but it was not expected.")
					ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
					ex.add_note(f"Expected one of: {objectSymbol._possibleReferences}.")
					raise ex
			elif isinstance(element, Constant):
				if PossibleReference.Constant in objectSymbol._possibleReferences:
					return element
				else:
					ex = TypeError(f"Found constant '{objectSymbol._name._identifier}', but it was not expected.")
					ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
					ex.add_note(f"Expected one of: {objectSymbol._possibleReferences}.")
					raise ex
			elif isinstance(element, Variable):
				if PossibleReference.Variable in objectSymbol._possibleReferences:
					return element
				else:
					ex = TypeError(f"Found variable '{objectSymbol._name._identifier}', but it was not expected.")
					ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
					ex.add_note(f"Expected one of: {objectSymbol._possibleReferences}.")
					raise ex
			else:
				ex = TypeError(f"Found element '{objectSymbol._name._identifier}', but it is not an object.")
				ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
				raise ex
		except KeyError:
			key = objectSymbol._name._identifier

			if (parentNamespace := self._parentNamespace) is None:
				raise ExtendedKeyError(key, (self, ), f"Object '{key}' not found in '{self._name}'.")

			try:
				return parentNamespace.FindObject(objectSymbol)
			except ExtendedKeyError as ex:
				searchedNamespaces = (self, *ex.searchedNamespaces)
				raise ExtendedKeyError(key, searchedNamespaces, f"Object '{key}' not found in: {', '.join(ns._name for ns in searchedNamespaces)}.") from ex
