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

from typing                import TYPE_CHECKING, TypeVar, Generic, Optional as Nullable

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import readonly
from pyTooling.Warning     import WarningCollector

from pyVHDLModel.Base      import identifiersOf, normalizedIdentifiersOf
from pyVHDLModel.Object    import Obj, Signal, Constant, Variable
from pyVHDLModel.Symbol    import ComponentInstantiationSymbol, Symbol, PossibleReference
from pyVHDLModel.Exception import DuplicateDeclarationWarning, NotInNamespaceError
if TYPE_CHECKING:
	from pyVHDLModel.Type   import BaseType

K = TypeVar("K")
O = TypeVar("O")


class ExtendedKeyError(KeyError):
	"""
	A :exc:`KeyError` reporting which namespaces were searched.

	Raised when a name cannot be resolved. Besides the key (:data:`key`), it carries every namespace
	visited while walking outwards (:data:`searchedNamespaces`).
	"""
	key: str                                   #: The key that was not found.
	searchedNamespaces: tuple[Namespace, ...]  #: The namespaces that were searched for the key.

	def __init__(self, key: str, searchedNamespaces: tuple[Namespace, ...], message: str) -> None:
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
	_name:                   str                  #: The namespace's name.
	_parentNamespace:        Nullable[Namespace]  #: Reference to the enclosing namespace, ``None`` if outermost.
	_subNamespaces:          list[Namespace]      #: List of all nested namespaces, in the order they were linked.
	_elements:               dict[K, O]           #: All elements declared in this namespace, indexed by name.
	_imports:                dict[K, O]           #: All elements imported into this namespace, indexed by name.
	_sharesRegionWithParent: bool                 #: ``True`` if the parent namespace is the same declarative region.

	def __init__(
		self,
		name: str,
		parentNamespace: Nullable[Namespace] = None,
		sharesRegionWithParent: bool = False
	) -> None:
		"""
		Initializes a namespace.

		:param name:                   The namespace's name.
		:param parentNamespace:        Optional, reference to the enclosing namespace, or ``None`` for the outermost one.
		                               Default: ``None``. |br|
		                               This namespace is appended to the parent namespace's sub-namespaces.
		:param sharesRegionWithParent: Optional, ``True`` if the parent namespace is the same declarative region.
		                               Default: ``False``.
		:raises TypeError:             If parameter 'parentNamespace' is not of type :class:`Namespace`.
		"""
		self._name =                   name
		self._parentNamespace =        None
		self._subNamespaces =          []
		self._elements =               {}
		self._imports =                {}
		self._sharesRegionWithParent = sharesRegionWithParent

		if parentNamespace is not None:
			self.ParentNamespace = parentNamespace

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the name (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	@property
	def ParentNamespace(self) -> Nullable[Namespace]:
		"""
		Property to access the parent namespace (:attr:`_parentNamespace`).

		Assigning a namespace links both sides: this namespace leaves the sub-namespaces (:attr:`SubNamespaces`) of its
		previous parent namespace and is appended to the sub-namespaces of the new one. Assigning ``None`` unlinks this
		namespace from its parent namespace. Assigning the current parent namespace changes nothing.

		:returns:          The parent namespace, or ``None`` if this namespace is the outermost one.
		:raises TypeError: If the assigned value is not of type :class:`Namespace`.
		"""
		return self._parentNamespace

	@ParentNamespace.setter
	def ParentNamespace(self, parentNamespace: Nullable[Namespace]) -> None:
		if parentNamespace is not None and not isinstance(parentNamespace, Namespace):
			ex = TypeError("Parameter 'parentNamespace' is not of type 'Namespace'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parentNamespace)}'.")
			raise ex

		if parentNamespace is self._parentNamespace:
			return

		if self._parentNamespace is not None:
			self._parentNamespace._subNamespaces.remove(self)

		self._parentNamespace = parentNamespace
		if parentNamespace is not None:
			parentNamespace._subNamespaces.append(self)

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
	def SubNamespaces(self) -> list[Namespace]:
		"""
		Read-only property to access the sub namespaces (:attr:`_subNamespaces`).

		A sub-namespace is linked by assigning this namespace to its :attr:`ParentNamespace`. Several sub-namespaces may
		share a name, e.g. ``None`` for unlabeled processes.

		:returns: List of sub namespaces, in the order they were linked.
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

		An item imported into a namespace (e.g. by a use clause) is no declaration of that namespace's region: it's kept
		apart (:meth:`AddImport`), so it never clashes with a declaration, and a lookup finds the declaration first.

		:param normalizedIdentifier:           The normalized (lower case) identifier being declared.
		:param element:                        The declared item.
		:param overloadable:                   Optional, ``True`` if this declaration may legally share its name.
		                                       Default: ``False``.
		:raises UnhandledCriticalWarningError: If the identifier is already declared in the declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
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
					f"Identifier '{normalizedIdentifier}' is already used for a declaration in '{namespace._name}'.",
					identifier=self._IdentifierOf(element, normalizedIdentifier),
					namespace=namespace,
					element=element,
					existing=existing
				))
				break

			namespace = namespace._parentNamespace if namespace._sharesRegionWithParent else None

		self._elements[normalizedIdentifier] = element

	def RemoveElement(self, normalizedIdentifier: K, element: O) -> None:
		"""
		Remove a declared item from this namespace.

		:param normalizedIdentifier: The normalized (lower case) identifier of the declared item.
		:param element:              The declared item.
		:raises NotInNamespaceError: If the identifier isn't declared in this namespace.
		:raises NotInNamespaceError: If the identifier refers to another element, e.g. a duplicate declaration.
		"""
		if (existing := self._elements.get(normalizedIdentifier)) is None:
			raise NotInNamespaceError(
				f"Namespace '{self._name}' has no element '{normalizedIdentifier}'.",
				identifier=self._IdentifierOf(element, normalizedIdentifier),
				namespace=self
			)
		elif existing is not element:
			ex = NotInNamespaceError(
				f"Namespace '{self._name}' has another element for '{normalizedIdentifier}'.",
				identifier=self._IdentifierOf(element, normalizedIdentifier),
				namespace=self
			)
			ex.add_note(f"Found element of type '{getFullyQualifiedName(existing)}'.")
			raise ex

		del self._elements[normalizedIdentifier]

	def AddImport(self, normalizedIdentifier: K, element: O) -> None:
		"""
		Add an item imported by a use clause to this namespace.

		An imported item is declared elsewhere, so it's kept apart from the declarations (:meth:`AddElement`): it never
		clashes with a declaration, and a lookup finds a declaration of the same identifier first. Importing another item
		for the same identifier replaces the imported item.

		:param normalizedIdentifier: The normalized (lower case) identifier of the imported item.
		:param element:              The imported item, e.g. a package or a component.
		"""
		self._imports[normalizedIdentifier] = element

	def RemoveImport(self, normalizedIdentifier: K, element: O) -> None:
		"""
		Remove an imported item from this namespace.

		Declarations of the same identifier are kept.

		:param normalizedIdentifier: The normalized (lower case) identifier of the imported item.
		:param element:              The imported item.
		:raises NotInNamespaceError: If the identifier isn't imported into this namespace.
		:raises NotInNamespaceError: If the identifier refers to another imported item.
		"""
		if (existing := self._imports.get(normalizedIdentifier)) is None:
			raise NotInNamespaceError(
				f"Namespace '{self._name}' has no import '{normalizedIdentifier}'.",
				identifier=self._IdentifierOf(element, normalizedIdentifier),
				namespace=self
			)
		elif existing is not element:
			ex = NotInNamespaceError(
				f"Namespace '{self._name}' has another import for '{normalizedIdentifier}'.",
				identifier=self._IdentifierOf(element, normalizedIdentifier),
				namespace=self
			)
			ex.add_note(f"Found element of type '{getFullyQualifiedName(existing)}'.")
			raise ex

		del self._imports[normalizedIdentifier]

	def ClearImports(self) -> None:
		"""
		Remove all imported items from this namespace.

		The declarations (:meth:`Elements`) are kept.
		"""
		self._imports.clear()

	@staticmethod
	def _IdentifierOf(element: O, normalizedIdentifier: K) -> str:
		"""
		Return the identifier of an element as declared, for its normalized identifier.

		:param element:              The named element.
		:param normalizedIdentifier: One of the element's normalized (lower case) identifiers.
		:returns:                    The identifier in its declared spelling.
		"""
		return next(
			identifier
			for identifier, normalized in zip(identifiersOf(element), normalizedIdentifiersOf(element))
			if normalized == normalizedIdentifier
		)

	def Elements(self) -> dict[K, O]:
		"""
		Return the elements declared in this namespace (:attr:`_elements`).

		:returns: Dictionary of declared elements, indexed by normalized identifier.
		"""
		return self._elements

	def Imports(self) -> dict[K, O]:
		"""
		Return the elements imported into this namespace (:attr:`_imports`).

		:returns: Dictionary of imported elements, indexed by normalized identifier.
		"""
		return self._imports

	def _LookupElement(self, normalizedIdentifier: K) -> O:
		"""
		Return the element of an identifier in this namespace: the declared element, else the imported element.

		:param normalizedIdentifier: The normalized (lower case) identifier.
		:returns:                    The declared or imported element.
		:raises KeyError:            If the identifier is neither declared nor imported in this namespace.
		"""
		if (element := self._elements.get(normalizedIdentifier)) is not None:
			return element

		return self._imports[normalizedIdentifier]

	def FindComponent(self, componentSymbol: ComponentInstantiationSymbol) -> Component:
		from pyVHDLModel.DesignUnit import Component

		try:
			element = self._LookupElement(componentSymbol._name._normalizedIdentifier)
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
			element = self._LookupElement(subtypeSymbol._name._normalizedIdentifier)
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
			element = self._LookupElement(objectSymbol._name._normalizedIdentifier)
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
