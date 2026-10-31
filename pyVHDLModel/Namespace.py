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
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Warning     import WarningCollector

from pyVHDLModel.Base      import ModelEntity, identifiersOf, normalizedIdentifiersOf
from pyVHDLModel.Object    import Obj, Signal, Constant, Variable
from pyVHDLModel.Symbol    import ComponentInstantiationSymbol, Symbol, PossibleReference
from pyVHDLModel.Exception import DuplicateDeclarationWarning, NotInNamespaceError
if TYPE_CHECKING:
	from pyVHDLModel.DesignUnit import Component, UseClause as _UseClause
	from pyVHDLModel.Type       import BaseType

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


@export
class Import(metaclass=ExtendedType, slots=True):
	"""
	Represents a declaration imported into a namespace by a use clause.

	Besides the imported declaration (:data:`Element`), it records its origin (:data:`UseClause`), so a conflict between
	two use clauses can be reported with both use clauses.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std.all;
	      --  ^^^^^^^^^^^^^^^^^^^^^    <- UseClause, importing e.g. 'unsigned' as Element
	"""
	_element:   ModelEntity           #: The imported declaration.
	_useClause: Nullable[_UseClause]  #: The use clause importing the declaration, ``None`` for the implicit use clause.

	def __init__(self, element: ModelEntity, useClause: Nullable[_UseClause]) -> None:
		"""
		Initializes an imported declaration.

		:param element:   The imported declaration.
		:param useClause: The use clause importing the declaration, or ``None`` for the implicit ``use std.standard.all;``
		                  preceding every design unit.
		"""
		self._element =   element
		self._useClause = useClause

	@readonly
	def Element(self) -> ModelEntity:
		"""
		Read-only property to access the imported declaration (:attr:`_element`).

		:returns: The imported declaration.
		"""
		return self._element

	@readonly
	def UseClause(self) -> Nullable[_UseClause]:
		"""
		Read-only property to access the use clause importing the declaration (:attr:`_useClause`).

		:returns: The use clause, or ``None`` for the implicit ``use std.standard.all;``.
		"""
		return self._useClause

	def __repr__(self) -> str:
		"""
		Formats a representation of the imported declaration.

		**Format:** ``Import: <declaration> by <use clause>``, or ``... by implicit use clause``

		:returns: String representation of the imported declaration.
		"""
		origin = "implicit use clause" if self._useClause is None else str(self._useClause)
		return f"Import: {self._element!s} by {origin}"


@export
class LookupResult(metaclass=ExtendedType, slots=True):
	"""
	Represents the result of looking up an identifier at a place (:meth:`Namespace.Lookup`).

	The directly visible declarations (:data:`Declarations`) are either one declaration, which isn't overloadable, or one
	or more overloadable declarations (subprograms and enumeration literals). Use clauses importing conflicting
	declarations make none of them directly visible: they are listed as conflicts (:data:`Conflicts`) instead.
	"""
	_normalizedIdentifier: str                      #: The normalized (lower case) identifier looked up.
	_declarations:         tuple[ModelEntity, ...]  #: The directly visible declarations.
	_imports:              tuple[Import, ...]       #: The imported declarations among the directly visible ones.
	_conflicts:            tuple[Import, ...]       #: The imported declarations conflicting with each other.
	_searchedNamespaces:   tuple[Namespace, ...]    #: The namespaces searched, innermost first.

	def __init__(
		self,
		normalizedIdentifier: str,
		declarations:         tuple[ModelEntity, ...],
		imports:              tuple[Import, ...],
		conflicts:            tuple[Import, ...],
		searchedNamespaces:   tuple[Namespace, ...]
	) -> None:
		"""
		Initializes a lookup result.

		:param normalizedIdentifier: The normalized (lower case) identifier looked up.
		:param declarations:         The directly visible declarations, innermost first.
		:param imports:              The imported declarations among the directly visible ones.
		:param conflicts:            The imported declarations conflicting with each other.
		:param searchedNamespaces:   The namespaces searched, innermost first.
		"""
		self._normalizedIdentifier = normalizedIdentifier
		self._declarations =         declarations
		self._imports =              imports
		self._conflicts =            conflicts
		self._searchedNamespaces =   searchedNamespaces

	@readonly
	def NormalizedIdentifier(self) -> str:
		"""
		Read-only property to access the normalized (lower case) identifier looked up (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier.
		"""
		return self._normalizedIdentifier

	@readonly
	def Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Read-only property to access the directly visible declarations (:attr:`_declarations`).

		Declarations of the innermost declarative region come first, then those of enclosing regions, then imported
		declarations.

		:returns: Tuple of directly visible declarations.
		"""
		return self._declarations

	@readonly
	def Imports(self) -> tuple[Import, ...]:
		"""
		Read-only property to access the imported declarations among the directly visible ones (:attr:`_imports`).

		:returns: Tuple of imported declarations with their use clauses.
		"""
		return self._imports

	@readonly
	def Conflicts(self) -> tuple[Import, ...]:
		"""
		Read-only property to access the imported declarations conflicting with each other (:attr:`_conflicts`).

		:returns: Tuple of imported declarations with their use clauses, empty if there is no conflict.
		"""
		return self._conflicts

	@readonly
	def SearchedNamespaces(self) -> tuple[Namespace, ...]:
		"""
		Read-only property to access the namespaces searched (:attr:`_searchedNamespaces`).

		:returns: Tuple of namespaces, innermost first.
		"""
		return self._searchedNamespaces

	@readonly
	def IsVisible(self) -> bool:
		"""
		Check if at least one declaration is directly visible (:attr:`_declarations`).

		:returns: ``True``, if at least one declaration is directly visible.
		"""
		return len(self._declarations) > 0

	@readonly
	def HasConflicts(self) -> bool:
		"""
		Check if use clauses imported conflicting declarations (:attr:`_conflicts`).

		:returns: ``True``, if conflicting declarations made none of them directly visible.
		"""
		return len(self._conflicts) > 0

	def __repr__(self) -> str:
		"""
		Formats a representation of the lookup result.

		**Format:** ``LookupResult: 'x' -> 1 declaration(s), 0 conflict(s)``

		:returns: String representation of the lookup result.
		"""
		return (
			f"LookupResult: '{self._normalizedIdentifier}' -> {len(self._declarations)} declaration(s), "
			f"{len(self._conflicts)} conflict(s)"
		)


@export
class Namespace(Generic[K, O]):
	"""
	Represents a namespace: the declared items visible in one declarative region.

	Namespaces nest, so a lookup that misses locally continues in the parent namespace
	(:data:`ParentNamespace`). That is what makes an entity's ports visible inside its architecture,
	and lets a process variable hide an outer signal.

	A namespace keeps three kinds of entries per normalized identifier:

	* the declarations of its region (:data:`Elements`), one entry per identifier,
	* the enumeration literals and physical units declared by the types among them (:data:`ImplicitDeclarations`), and
	* the declarations imported by use clauses (:data:`Imports`), each with its use clause.

	:meth:`Lookup` applies VHDL's visibility rules (IEEE Std 1076-2008, clause 12) to these entries.

	.. seealso::

	   * :class:`Concurrent declaration region <pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin>`
	   * :class:`Sequential declaration region <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	"""
	_name:                   str                    #: The namespace's name.
	_parentNamespace:        Nullable[Namespace]    #: Reference to the enclosing namespace, ``None`` if outermost.
	_subNamespaces:          list[Namespace]        #: List of all nested namespaces, in the order they were linked.
	_elements:               dict[K, O]             #: All elements declared in this namespace, indexed by name.
	_implicitDeclarations:   dict[K, list[O]]       #: Enumeration literals and physical units of the declared types.
	_imports:                dict[K, list[Import]]  #: All elements imported into this namespace, indexed by name.
	_sharesRegionWithParent: bool                   #: ``True`` if the parent namespace is the same declarative region.

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
		self._implicitDeclarations =   {}
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

		Overloadable declarations (:meth:`IsOverloadable`) are exempt: several subprograms may share a name as long as their
		signatures differ. Signatures are not compared yet, so two subprograms sharing a name are always
		accepted (see the overload-resolution finding).

		An item imported into a namespace (e.g. by a use clause) is no declaration of that namespace's region: it's kept
		apart (:meth:`AddImport`), so it never clashes with a declaration, and a lookup finds the declaration first.

		The enumeration literals of an enumerated type and the units of a physical type are added as implicit declarations
		(:data:`ImplicitDeclarations`).

		:param normalizedIdentifier:           The normalized (lower case) identifier being declared.
		:param element:                        The declared item.
		:param overloadable:                   Optional, ``True`` if this declaration may legally share its name.
		                                       Default: ``False``.
		:raises UnhandledCriticalWarningError: If the identifier is already declared in the declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		namespace = self
		while namespace is not None:
			existing = namespace._elements.get(normalizedIdentifier)
			# `existing is element` means the region is being re-indexed, not that the name is declared twice.
			isReindex = existing is element
			isOverload = overloadable and self.IsOverloadable(existing)
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

		for implicitIdentifier, declaration in self._GetImplicitDeclarationsOf(element):
			declarations = self._implicitDeclarations.setdefault(implicitIdentifier, [])
			if not any(existing is declaration for existing in declarations):
				declarations.append(declaration)

	def RemoveElement(self, normalizedIdentifier: K, element: O) -> None:
		"""
		Remove a declared item from this namespace.

		The enumeration literals and physical units declared by the item are removed too.

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

		for implicitIdentifier, declaration in self._GetImplicitDeclarationsOf(element):
			declarations = self._implicitDeclarations[implicitIdentifier]
			declarations.remove(declaration)
			if len(declarations) == 0:
				del self._implicitDeclarations[implicitIdentifier]

	@staticmethod
	def _GetImplicitDeclarationsOf(element: O) -> tuple[tuple[str, ModelEntity], ...]:
		"""
		Return the declarations a type declaration implies: an enumerated type's literals, a physical type's units.

		:param element: A declared element.
		:returns:       Tuple of (normalized designator, declaration) pairs, empty if the element is no such type.
		"""
		from pyVHDLModel.Type import EnumeratedType, PhysicalType

		if isinstance(element, EnumeratedType):
			return tuple((Namespace.GetNormalizedDesignatorOf(literal), literal) for literal in element._literals)
		elif isinstance(element, PhysicalType):
			units = (element._primaryUnit, *element._secondaryUnits)
			return tuple((unit._normalizedIdentifier, unit) for unit in units)

		return ()

	@staticmethod
	def IsOverloadable(element: Nullable[ModelEntity]) -> bool:
		"""
		Check if a declaration is overloadable: it may share its designator with other overloadable declarations.

		Subprograms and enumeration literals are overloadable, as is an alias without a subtype indication, whose name may
		denote a subprogram or an enumeration literal (:attr:`~pyVHDLModel.Symbol.Symbol.Reference`, else the symbol's
		possible references), e.g. ``alias To_SLV is To_StdLogicVector [std_ulogic_vector return std_logic_vector];``.

		:param element: A declaration, or ``None``.
		:returns:       ``True``, if the declaration is overloadable.
		"""
		from pyVHDLModel.Declaration import Alias
		from pyVHDLModel.Expression  import EnumerationLiteral
		from pyVHDLModel.Subprogram  import Function, Procedure

		if isinstance(element, (Function, Procedure, EnumerationLiteral)):
			return True
		elif isinstance(element, Alias) and element._subtype is None:
			if (reference := element._name._reference) is not None:
				return isinstance(reference, (Function, Procedure, EnumerationLiteral))

			overloadables = PossibleReference.SubProgram | PossibleReference.EnumLiteral
			return (element._name._possibleReferences & overloadables) != PossibleReference.Unknown

		return False

	@staticmethod
	def GetNormalizedDesignatorOf(element: ModelEntity) -> str:
		"""
		Return the normalized designator of a declaration, the key it's indexed by in a namespace.

		An identifier is normalized to lower case. A character literal keeps its case and is enclosed in apostrophes, so
		the enumeration literal ``'a'`` doesn't clash with an identifier ``a``.

		:param element:    A named entity or an enumeration literal.
		:returns:          The normalized designator.
		:raises TypeError: If parameter 'element' has no designator.
		"""
		from pyVHDLModel.Expression import EnumerationLiteral, CharacterEnumerationLiteral

		if isinstance(element, CharacterEnumerationLiteral):
			return f"'{element._value}'"
		elif isinstance(element, EnumerationLiteral):
			return element._value.lower()

		return normalizedIdentifiersOf(element)[0]

	def AddImport(self, normalizedIdentifier: K, element: O, useClause: Nullable[_UseClause]) -> None:
		"""
		Add an item imported by a use clause to this namespace.

		An imported item is declared elsewhere, so it's kept apart from the declarations (:meth:`AddElement`): it never
		clashes with a declaration, and a declaration of the same identifier hides it (:meth:`Lookup`). Several items can
		be imported for the same identifier, e.g. overloaded subprograms, or conflicting declarations of two packages. The
		same item imported by several use clauses is kept once per use clause, because their positions differ; importing
		it again by the same use clause changes nothing.

		Imports are computed by the analysis (:meth:`~pyVHDLModel.Design.Analyze`): adding, removing or moving a declaration
		of a package or a use clause doesn't update them, a later analysis does. Until then, :meth:`Lookup` ignores an
		import by a removed use clause; a declaration removed from its package stays imported.

		:param normalizedIdentifier: The normalized (lower case) identifier of the imported item.
		:param element:              The imported item, e.g. a package, a type or a subprogram.
		:param useClause:            The use clause importing the item, or ``None`` for the implicit
		                             ``use std.standard.all;``.
		"""
		imports = self._imports.setdefault(normalizedIdentifier, [])
		if not any(existing._element is element and existing._useClause is useClause for existing in imports):
			imports.append(Import(element, useClause))

	def RemoveImport(self, normalizedIdentifier: K, element: O) -> None:
		"""
		Remove an imported item from this namespace.

		Declarations of the same identifier and other items imported for it are kept.

		:param normalizedIdentifier: The normalized (lower case) identifier of the imported item.
		:param element:              The imported item.
		:raises NotInNamespaceError: If the identifier isn't imported into this namespace.
		:raises NotInNamespaceError: If the identifier refers to other imported items only.
		"""
		if (imports := self._imports.get(normalizedIdentifier)) is None:
			raise NotInNamespaceError(
				f"Namespace '{self._name}' has no import '{normalizedIdentifier}'.",
				identifier=self._IdentifierOf(element, normalizedIdentifier),
				namespace=self
			)

		for index, existing in enumerate(imports):
			if existing._element is element:
				break
		else:
			ex = NotInNamespaceError(
				f"Namespace '{self._name}' has another import for '{normalizedIdentifier}'.",
				identifier=self._IdentifierOf(element, normalizedIdentifier),
				namespace=self
			)
			for existing in imports:
				ex.add_note(f"Found element of type '{getFullyQualifiedName(existing._element)}'.")
			raise ex

		del imports[index]
		if len(imports) == 0:
			del self._imports[normalizedIdentifier]

	def ClearImports(self) -> None:
		"""
		Remove all imported items from this namespace.

		The declarations (:data:`Elements`) are kept.
		"""
		self._imports.clear()

	@staticmethod
	def _IdentifierOf(element: O, normalizedIdentifier: K) -> str:
		"""
		Return the identifier of an element as declared, for its normalized identifier.

		An enumeration literal's identifier is its value.

		:param element:              The named element.
		:param normalizedIdentifier: One of the element's normalized (lower case) identifiers.
		:returns:                    The identifier in its declared spelling.
		"""
		from pyVHDLModel.Expression import EnumerationLiteral

		if isinstance(element, EnumerationLiteral):
			return element._value

		return next(
			identifier
			for identifier, normalized in zip(identifiersOf(element), normalizedIdentifiersOf(element))
			if normalized == normalizedIdentifier
		)

	@readonly
	def Elements(self) -> dict[K, O]:
		"""
		Read-only property to access the elements declared in this namespace (:attr:`_elements`).

		:returns: Dictionary of declared elements, indexed by normalized identifier.
		"""
		return self._elements

	@readonly
	def ImplicitDeclarations(self) -> dict[K, list[O]]:
		"""
		Read-only property to access the enumeration literals and physical units declared by the types of this namespace
		(:attr:`_implicitDeclarations`).

		:returns: Dictionary of lists of enumeration literals and physical units, indexed by normalized designator
		          (:meth:`GetNormalizedDesignatorOf`).
		"""
		return self._implicitDeclarations

	@readonly
	def Imports(self) -> dict[K, list[Import]]:
		"""
		Read-only property to access the elements imported into this namespace (:attr:`_imports`).

		:returns: Dictionary of lists of imported elements with their use clauses, indexed by normalized identifier.
		"""
		return self._imports

	def FindDeclarations(self, normalizedIdentifier: K) -> tuple[ModelEntity, ...]:
		"""
		Return the declarations of an identifier in this namespace's own declarative region.

		Neither imported items nor enclosing namespaces are searched; this is the lookup of the suffix of an expanded name
		like ``pkg.T``. All overloads of a subprogram are returned, as are enumeration literals and physical units.

		:param normalizedIdentifier: The normalized (lower case) identifier or designator
		                             (:meth:`GetNormalizedDesignatorOf`).
		:returns:                    Tuple of declarations in declaration order, enumeration literals and physical units
		                             last.
		"""
		return tuple(declaration for declaration, _ in self._GetDeclarationsOf(normalizedIdentifier))

	def _GetDeclarationsOf(self, normalizedIdentifier: K) -> list[tuple[ModelEntity, ModelEntity]]:
		"""
		Return the declarations of an identifier in this namespace, each with the item deciding its declaration order.

		An overloadable declaration (:meth:`IsOverloadable`) is expanded to all overloads of its declarative region. An
		enumeration literal or a physical unit is ordered by its type.

		:param normalizedIdentifier: The normalized (lower case) identifier or designator.
		:returns:                    List of (declaration, item in declaration order) pairs.
		"""
		from pyVHDLModel.Regions import DeclarationRegionMixin

		declarations = []
		if (element := self._elements.get(normalizedIdentifier)) is not None:
			region = element._parent
			if self.IsOverloadable(element) and isinstance(region, DeclarationRegionMixin):
				for declaration in region._Declarations():
					if (
						self.IsOverloadable(declaration)
						and normalizedIdentifier in normalizedIdentifiersOf(declaration)
					):
						declarations.append((declaration, declaration))
			else:
				declarations.append((element, element))

		for declaration in self._implicitDeclarations.get(normalizedIdentifier, ()):
			declarations.append((declaration, declaration._parent))

		return declarations

	def _GetAnchorOf(self, place: Nullable[ModelEntity]) -> Nullable[ModelEntity]:
		"""
		Return the item of this namespace's declarative region containing a place.

		:param place: The model entity, at which an identifier is looked up, or ``None``.
		:returns:     The place itself or its ancestor, whose parent is the declarative region of this namespace, or
		              ``None``, if the place isn't inside the region, e.g. inside an architecture of an entity.
		"""
		from pyVHDLModel.Regions import DeclarationRegionMixin

		item = place
		while item is not None:
			parent = item._parent
			if isinstance(parent, DeclarationRegionMixin) and parent._namespace is self:
				return item

			item = parent

		return None

	@staticmethod
	def _Precedes(item: Nullable[ModelEntity], anchor: ModelEntity, inclusive: bool) -> bool:
		"""
		Check if an item precedes an anchor in the anchor's declarative region.

		An item, which isn't a declaration of the region (e.g. a use clause of the context clause), precedes every anchor.

		:param item:      The item in declaration order, or ``None`` for the implicit use clause.
		:param anchor:    The item of the region containing the place of a lookup.
		:param inclusive: ``True``, if the anchor precedes itself, i.e. the place is nested inside the anchor.
		:returns:         ``True``, if the item is visible at the anchor.
		"""
		itemIndex =   None
		anchorIndex = None
		for index, declaration in enumerate(anchor._parent._Declarations()):
			if declaration is item:
				itemIndex = index

			if declaration is anchor:
				anchorIndex = index

		if itemIndex is None or anchorIndex is None:
			return True

		return itemIndex < anchorIndex or (inclusive and itemIndex == anchorIndex)

	def Lookup(self, normalizedIdentifier: K, place: Nullable[ModelEntity] = None) -> LookupResult:
		"""
		Look up the declarations of an identifier directly visible at a place inside this namespace's region.

		.. rubric:: Rules (IEEE Std 1076-2008, clause 12)

		* Namespaces are searched from this one outwards (:attr:`ParentNamespace`).
		* Declaration order: a declaration or a use clause is visible after its own place in its declarative region. The
		  place is the model entity at which the identifier is used, e.g. the declaration containing a type mark; with
		  ``None``, every declaration is visible, as from the statements of a region. A full type is visible from its
		  incomplete type declaration on.
		* A declaration hides the declarations of the same identifier in enclosing regions. Overloadable declarations
		  (:meth:`IsOverloadable`: subprograms, enumeration literals, subprogram aliases) of all regions coexist, until a
		  region declares the identifier as something not overloadable.
		* A declaration of the identifier in the region or in an enclosing region hides every imported declaration of the
		  same identifier, unless both are overloadable.
		* Imported declarations of all use clauses visible at the place are potentially visible: overloadable ones coexist;
		  if one of two different ones isn't overloadable, neither is directly visible, and both are reported as conflicts.
		  The same declaration imported twice is no conflict, nor is an alias and the declaration its resolved name denotes.
		* Imports are those of the last analysis; an import by a removed use clause is ignored.

		Overloadable declarations aren't compared by their parameter and result type profiles, so a homograph doesn't hide
		an overloadable declaration.

		:param normalizedIdentifier: The normalized (lower case) identifier or designator
		                             (:meth:`GetNormalizedDesignatorOf`).
		:param place:                Optional, the model entity at which the identifier is used. Default: ``None``.
		:returns:                    The directly visible declarations, or the conflicts, and the searched namespaces.
		"""
		from pyVHDLModel.Declaration import Alias
		from pyVHDLModel.Type        import FullType, AnonymousType

		declarations = []
		imports = []
		searchedNamespaces = []
		isHidden = False

		namespace = self
		while namespace is not None:
			searchedNamespaces.append(namespace)
			anchor = namespace._GetAnchorOf(place)
			inclusive = anchor is not place

			for declaration, item in namespace._GetDeclarationsOf(normalizedIdentifier):
				if anchor is not None and not self._Precedes(item, anchor, inclusive):
					# A full type is visible from its incomplete type declaration on.
					if not isinstance(declaration, FullType) or not any(
						isinstance(incompleteType, AnonymousType)
						and incompleteType._normalizedIdentifier == normalizedIdentifier
						and self._Precedes(incompleteType, anchor, inclusive)
						for incompleteType in anchor._parent._Declarations()
					):
						continue

				if self.IsOverloadable(declaration):
					declarations.append(declaration)
				else:
					# Not overloadable: it hides every declaration further out and every import, unless an inner overloadable
					# declaration hides it.
					if len(declarations) == 0:
						declarations.append(declaration)

					isHidden = True
					break

			if isHidden:
				break

			for imported in namespace._imports.get(normalizedIdentifier, ()):
				# An import by a removed use clause waits for the next analysis to vanish.
				useClause = imported._useClause
				if useClause is not None and useClause._parent is None:
					continue
				elif anchor is None or self._Precedes(useClause, anchor, inclusive):
					imports.append(imported)

			namespace = namespace._parentNamespace

		if isHidden or len(imports) == 0:
			return LookupResult(normalizedIdentifier, tuple(declarations), (), (), tuple(searchedNamespaces))

		# An alias, whose name is resolved, denotes the same named entity as the aliased declaration.
		distinctImports = []
		denotedElements = []
		for imported in imports:
			element = imported._element
			if isinstance(element, Alias) and element._name._reference is not None:
				element = element._name._reference

			if not any(denotedElement is element for denotedElement in denotedElements):
				denotedElements.append(element)
				distinctImports.append(imported)

		if len(declarations) > 0:
			# Declared overloadable declarations hide imported declarations, which aren't overloadable.
			visibleImports = tuple(imported for imported in distinctImports if self.IsOverloadable(imported._element))
		elif len(distinctImports) == 1 or all(self.IsOverloadable(imported._element) for imported in distinctImports):
			visibleImports = tuple(distinctImports)
		else:
			return LookupResult(normalizedIdentifier, (), (), tuple(distinctImports), tuple(searchedNamespaces))

		return LookupResult(
			normalizedIdentifier,
			(*declarations, *(imported._element for imported in visibleImports)),
			visibleImports,
			(),
			tuple(searchedNamespaces)
		)

	def _LookupElement(self, normalizedIdentifier: K) -> O:
		"""
		Return the element of an identifier in this namespace: the declared element, else the first imported element.

		:param normalizedIdentifier: The normalized (lower case) identifier.
		:returns:                    The declared or imported element.
		:raises KeyError:            If the identifier is neither declared nor imported in this namespace.
		"""
		if (element := self._elements.get(normalizedIdentifier)) is not None:
			return element

		return self._imports[normalizedIdentifier][0]._element

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
