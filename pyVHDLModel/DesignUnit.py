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

Design units are contexts, entities, architectures, packages and their bodies as well as configurations.
"""
from __future__                import annotations

from typing                    import TYPE_CHECKING, ClassVar, Union, Iterable, Optional as Nullable

from pyTooling.Common          import getFullyQualifiedName, getTypeName
from pyTooling.Decorators      import export, readonly
from pyTooling.MetaClasses     import ExtendedType, abstractmethod, abstractclass
from pyTooling.Graph           import Vertex

from pyVHDLModel.Common        import AllowBlackboxMixin
from pyVHDLModel.Exception     import VHDLModelException, AlreadyInDesignError, NotAChildError
from pyVHDLModel.Base          import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin, \
                                      normalizedIdentifiersOf, ReservedWord
from pyVHDLModel.Namespace     import Namespace
from pyVHDLModel.Regions       import ConcurrentDeclarationRegionMixin, WithGenericsMixin, WithPortsMixin, \
                                      WithoutStatementsMixin
from pyVHDLModel.Symbol        import Symbol, PackageSymbol, EntitySymbol, LibraryReferenceSymbol
from pyVHDLModel.Interface     import GenericInterfaceItemMixin, PortInterfaceItemMixin, PortGroup
from pyVHDLModel.Object        import DeferredConstant
from pyVHDLModel.Concurrent    import ConcurrentStatement, ConcurrentStatementsMixin
from pyVHDLModel.Configuration import BlockConfiguration

if TYPE_CHECKING:
	from pyVHDLModel.Visitor     import Visitor


@export
@abstractclass
class Reference(ModelEntity):
	"""
	A base-class for all references.

	.. seealso::

	   * :class:`Library clause <pyVHDLModel.DesignUnit.LibraryClause>`
	   * :class:`Use clause <pyVHDLModel.DesignUnit.UseClause>`
	   * :class:`Context reference <pyVHDLModel.DesignUnit.ContextReference>`
	"""

	_symbols:       list[Symbol]  #: List of all symbols referenced by this clause.

	def __init__(self, symbols: Iterable[Symbol], parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a reference by taking a list of symbols and a parent reference.

		:param symbols: A list of symbols this reference references to.
		:param parent:  Reference to the logical parent in the model hierarchy.
		"""
		super().__init__(parent)

		self._symbols = list(symbols)

	@readonly
	def Symbols(self) -> list[Symbol]:
		"""
		Read-only property to access the symbols this reference references to (:attr:`_symbols`).

		:returns: A list of symbols.
		"""
		return self._symbols

	def _VisitSymbols(self, visitor: Visitor) -> None:
		"""
		Walk the referenced symbols, separated by commas, with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		for index, symbol in enumerate(self._symbols):
			if index > 0:
				visitor.VisitNameListSeparator(self)

			symbol.Visit(visitor)


@export
class LibraryClause(Reference):
	"""
	Represents a library clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      library std, ieee;
	"""

	@readonly
	def Symbols(self) -> list[LibraryReferenceSymbol]:
		"""
		Read-only property to access the symbols this library clause references to (:attr:`_symbols`).

		:returns: A list of library reference symbols.
		"""
		return self._symbols

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this library clause and its library names with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitLibraryClause(self)
		self._VisitSymbols(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartLibraryClause(self)


@export
class UseClause(Reference):
	"""
	Represents a use clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use std.text_io.all, ieee.numeric_std.all;
	"""

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this use clause and its selected names with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitUseClause(self)
		self._VisitSymbols(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartUseClause(self)


@export
class ContextReference(Reference):
	"""
	Represents a context reference.

	.. hint:: It's called *context reference* not *context clause* by the LRM.

	.. admonition:: Example

	   .. code-block:: VHDL

	      context ieee.ieee_std_context;
	"""

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this context reference and its context names with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitContextReference(self)
		self._VisitSymbols(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartContextReference(self)


ContextUnion = Union[
	LibraryClause,
	UseClause,
	ContextReference
]


@export
class DesignUnitWithContextMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all design units with a context.

	.. seealso::

	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Package body <pyVHDLModel.DesignUnit.PackageBody>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	   * :class:`Configuration <pyVHDLModel.DesignUnit.Configuration>`
	"""


@export
@abstractclass
class DesignUnit(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	A base-class for all design units.

	When a design unit is formatted, an unknown part - a library that is not set, or an entity with no
	known architecture - is rendered as ``?``.

	.. seealso::

	   * :class:`Primary design units <pyVHDLModel.DesignUnit.PrimaryUnit>`

	     * :class:`Context <pyVHDLModel.DesignUnit.Context>`
	     * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	     * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	     * :class:`Configuration <pyVHDLModel.DesignUnit.Configuration>`

	   * :class:`Secondary design units <pyVHDLModel.DesignUnit.SecondaryUnit>`

	     * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	     * :class:`Package body <pyVHDLModel.DesignUnit.PackageBody>`
	"""

	_CONTINUES_PARENT_REGION: ClassVar[bool] = False       #: ``True`` if it continues its parent's declarative region.

	_document: Document                                    #: The VHDL library, the design unit was analyzed into.

	# Either written as statements before (e.g. entity, architecture, package, ...), or as statements inside (context)
	_contextItems:        list[ContextUnion]               #: List of all context items (library, use and context clauses).
	_libraryReferences:   list[LibraryClause]              #: List of library clauses.
	_packageReferences:   list[UseClause]                  #: List of use clauses.
	_contextReferences:   list[ContextReference]           #: List of context clauses.

	_referencedLibraries: dict[str, Library]               #: Referenced libraries based on explicit library clauses or implicit inheritance
	_referencedPackages:  dict[str, dict[str, Package]]    #: Referenced packages based on explicit use clauses or implicit inheritance
	_referencedContexts:  dict[str, Context]               #: Referenced contexts based on explicit context references or implicit inheritance

	_dependencyVertex:    Vertex  #: Reference to the vertex in the dependency graph representing the design unit. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateDependencyGraph`.
	_hierarchyVertex:     Vertex  #: The vertex in the hierarchy graph

	def __init__(self, identifier: str, contextItems: Nullable[Iterable[ContextUnion]] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a design unit.

		:param identifier:    Identifier (name) of the design unit.
		:param contextItems:  A sequence of library, use or context clauses.
		:param documentation: Associated documentation of the design unit.
		:param parent:        Reference to the logical parent in the model hierarchy.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._document = None

		self._contextItems = contextItemList = []
		self._libraryReferences = libraryReferences = []
		self._packageReferences = packageReferences = []
		self._contextReferences = contextReferences = []

		if contextItems is not None:
			for item in contextItems:
				contextItemList.append(item)
				item.Parent = self
				if isinstance(item, UseClause):
					packageReferences.append(item)
				elif isinstance(item, LibraryClause):
					libraryReferences.append(item)
				elif isinstance(item, ContextReference):
					contextReferences.append(item)

		self._referencedLibraries = {}
		self._referencedPackages = {}
		self._referencedContexts = {}

		self._dependencyVertex = None
		self._hierarchyVertex = None

	@property
	def Document(self) -> Document:
		"""
		Property to access the document (:attr:`_document`).

		:returns: The document.
		"""
		return self._document

	@Document.setter
	def Document(self, document: Document) -> None:
		self._document = document

	@property
	def Library(self) -> Library:
		"""
		Property to access the library (:attr:`_parent`).

		:returns: The library.
		"""
		return self._parent

	@Library.setter
	def Library(self, library: Library) -> None:
		self._parent = library

	@readonly
	def ContextItems(self) -> list[ContextUnion]:
		"""
		Read-only property to access the sequence of all context items comprising library, use and context clauses
		(:attr:`_contextItems`).

		:returns: Sequence of context items.
		"""
		return self._contextItems

	@readonly
	def ContextReferences(self) -> list[ContextReference]:
		"""
		Read-only property to access the sequence of context clauses (:attr:`_contextReferences`).

		:returns: Sequence of context clauses.
		"""
		return self._contextReferences

	@readonly
	def LibraryReferences(self) -> list[LibraryClause]:
		"""
		Read-only property to access the sequence of library clauses (:attr:`_libraryReferences`).

		:returns: Sequence of library clauses.
		"""
		return self._libraryReferences

	def _VisitContextClause(self, visitor: Visitor) -> None:
		"""
		Walk the context clause, i.e. the context items preceding the design unit, with a visitor.

		The context clause is reported, even if it has no context items.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitContextClause(self)
		for item in self._contextItems:
			item.Visit(visitor)

		visitor.DepartContextClause(self)

	@readonly
	def PackageReferences(self) -> list[UseClause]:
		"""
		Read-only property to access the sequence of use clauses (:attr:`_packageReferences`).

		:returns: Sequence of use clauses.
		"""
		return self._packageReferences

	def AddContextItem(self, contextItem: ContextUnion) -> None:
		"""
		Add a context item at the end of the context clause.

		The context item's parent is set to this design unit. A library clause is also added to :data:`LibraryReferences`, a
		use clause to :data:`PackageReferences` and a context reference to :data:`ContextReferences`, in the order of
		:data:`ContextItems`. A context item may repeat an earlier one.

		:param contextItem:           The library clause, use clause or context reference to add.
		:raises ValueError:           If parameter 'contextItem' is ``None``.
		:raises TypeError:            If parameter 'contextItem' is not of type :class:`LibraryClause`, :class:`UseClause`
		                              or :class:`ContextReference`.
		:raises AlreadyInDesignError: If parameter 'contextItem' already has a parent.

		.. attention::

		   The mutator doesn't update what :meth:`~pyVHDLModel.Design.Analyze` derived from the context items: the
		   referenced libraries, packages and contexts (:data:`ReferencedLibraries`, :data:`ReferencedPackages`,
		   :data:`ReferencedContexts`), the namespace entries of a use clause, the edges of the dependency graph, and the
		   references of the symbols. A design changed after its analysis needs a new analysis.

		.. seealso::

		   :meth:`InsertContextItem`
		      |rarr| Insert a context item at a position of the context clause.
		   :meth:`RemoveContextItem`
		      |rarr| Remove a context item from the context clause.
		"""
		self.InsertContextItem(len(self._contextItems), contextItem)

	def InsertContextItem(self, index: int, contextItem: ContextUnion) -> None:
		"""
		Insert a context item at a position of the context clause.

		The context item's parent is set to this design unit. A library clause is also added to :data:`LibraryReferences`, a
		use clause to :data:`PackageReferences` and a context reference to :data:`ContextReferences`, in the order of
		:data:`ContextItems`. A context item may repeat an earlier one.

		:param index:                 Position, from ``0`` (first) to the number of context items (append). A negative index
		                              counts from the end, as for :meth:`list.insert`: ``-1`` inserts before the last
		                              context item.
		:param contextItem:           The library clause, use clause or context reference to insert.
		:raises ValueError:           If parameter 'index' is ``None``.
		:raises TypeError:            If parameter 'index' is not of type :class:`int`.
		:raises ValueError:           If parameter 'index' is out of range.
		:raises ValueError:           If parameter 'contextItem' is ``None``.
		:raises TypeError:            If parameter 'contextItem' is not of type :class:`LibraryClause`, :class:`UseClause`
		                              or :class:`ContextReference`.
		:raises AlreadyInDesignError: If parameter 'contextItem' already has a parent.

		.. attention::

		   The mutator doesn't update what :meth:`~pyVHDLModel.Design.Analyze` derived from the context items: the
		   referenced libraries, packages and contexts (:data:`ReferencedLibraries`, :data:`ReferencedPackages`,
		   :data:`ReferencedContexts`), the namespace entries of a use clause, the edges of the dependency graph, and the
		   references of the symbols. A design changed after its analysis needs a new analysis.

		.. seealso::

		   :meth:`AddContextItem`
		      |rarr| Add a context item at the end of the context clause.
		   :meth:`RemoveContextItem`
		      |rarr| Remove a context item from the context clause.
		"""
		count = len(self._contextItems)
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

		if contextItem is None:
			raise ValueError("Parameter 'contextItem' is None.")
		elif not isinstance(contextItem, (LibraryClause, UseClause, ContextReference)):
			ex = TypeError("Parameter 'contextItem' is not of type 'LibraryClause', 'UseClause' or 'ContextReference'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(contextItem)}'.")
			raise ex
		elif contextItem._parent is not None:
			ex = AlreadyInDesignError(
				f"{getTypeName(contextItem)} already has a parent.",
				element=contextItem,
				parent=contextItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(contextItem._parent)} first.")
			raise ex

		if isinstance(contextItem, LibraryClause):
			references =    self._libraryReferences
			referenceType = LibraryClause
		elif isinstance(contextItem, UseClause):
			references =    self._packageReferences
			referenceType = UseClause
		else:
			references =    self._contextReferences
			referenceType = ContextReference

		position =       index if index >= 0 else count + index
		referenceIndex = sum(1 for item in self._contextItems[:position] if isinstance(item, referenceType))

		self._contextItems.insert(position, contextItem)
		references.insert(referenceIndex, contextItem)
		contextItem.Parent = self

	def RemoveContextItem(self, contextItem: ContextUnion) -> None:
		"""
		Remove a context item from the context clause.

		The context item is detached: its parent is cleared, and it's removed from :data:`ContextItems` and from
		:data:`LibraryReferences`, :data:`PackageReferences` or :data:`ContextReferences`. The context item itself is
		unchanged and can be added to another design unit, or inserted at another position.

		:param contextItem:     The library clause, use clause or context reference to remove.
		:raises ValueError:     If parameter 'contextItem' is ``None``.
		:raises TypeError:      If parameter 'contextItem' is not of type :class:`LibraryClause`, :class:`UseClause` or
		                        :class:`ContextReference`.
		:raises NotAChildError: If parameter 'contextItem' is not a context item of this design unit.

		.. attention::

		   The mutator doesn't update what :meth:`~pyVHDLModel.Design.Analyze` derived from the context items: the
		   referenced libraries, packages and contexts (:data:`ReferencedLibraries`, :data:`ReferencedPackages`,
		   :data:`ReferencedContexts`), the namespace entries of a use clause, the edges of the dependency graph, and the
		   references of the symbols. A design changed after its analysis needs a new analysis.

		.. seealso::

		   :meth:`AddContextItem`
		      |rarr| Add a context item at the end of the context clause.
		   :meth:`InsertContextItem`
		      |rarr| Insert a context item at a position of the context clause.
		"""
		if contextItem is None:
			raise ValueError("Parameter 'contextItem' is None.")
		elif not isinstance(contextItem, (LibraryClause, UseClause, ContextReference)):
			ex = TypeError("Parameter 'contextItem' is not of type 'LibraryClause', 'UseClause' or 'ContextReference'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(contextItem)}'.")
			raise ex

		for index, item in enumerate(self._contextItems):
			if item is contextItem:
				break
		else:
			raise NotAChildError(
				f"{getTypeName(contextItem)} is not a context item of this {getTypeName(self)}.",
				element=contextItem,
				parent=self
			)

		if isinstance(contextItem, LibraryClause):
			references = self._libraryReferences
		elif isinstance(contextItem, UseClause):
			references = self._packageReferences
		else:
			references = self._contextReferences

		del self._contextItems[index]
		references.remove(contextItem)
		contextItem._parent = None

	@readonly
	def ReferencedLibraries(self) -> dict[str, Library]:
		"""
		Read-only property to access the referenced libraries (:attr:`_referencedLibraries`).

		:returns: Dictionary of referenced libraries, indexed by normalized identifier.
		"""
		return self._referencedLibraries

	@readonly
	def ReferencedPackages(self) -> dict[str, Package]:
		"""
		Read-only property to access the referenced packages (:attr:`_referencedPackages`).

		:returns: Dictionary of referenced packages, indexed by normalized identifier.
		"""
		return self._referencedPackages

	@readonly
	def ReferencedContexts(self) -> dict[str, Context]:
		"""
		Read-only property to access the referenced contexts (:attr:`_referencedContexts`).

		:returns: Dictionary of referenced contexts, indexed by normalized identifier.
		"""
		return self._referencedContexts

	@readonly
	def DependencyVertex(self) -> Vertex:
		"""
		Read-only property to access the corresponding dependency vertex (:attr:`_dependencyVertex`).

		The dependency vertex references this design unit by its value field.

		:returns: The corresponding dependency vertex.
		"""
		return self._dependencyVertex

	@readonly
	def HierarchyVertex(self) -> Vertex:
		"""
		Read-only property to access the corresponding hierarchy vertex (:attr:`_hierarchyVertex`).

		The hierarchy vertex references this design unit by its value field.

		:returns: The corresponding hierarchy vertex.
		"""
		return self._hierarchyVertex

	@abstractmethod
	def __str__(self) -> str:
		"""
		Formats the design unit.

		Every concrete design unit renders itself, so this base-class provides no implementation.

		:returns: Formatted design unit.
		"""


@export
@abstractclass
class PrimaryUnit(DesignUnit):
	"""
	A base-class for all primary design units.

	.. seealso::

	   * :class:`Context <pyVHDLModel.DesignUnit.Context>`
	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Configuration <pyVHDLModel.DesignUnit.Configuration>`
	   * :class:`PSL primary unit <pyVHDLModel.PSLModel.PSLPrimaryUnit>` (PSL is not supported)
	"""


@export
@abstractclass
class SecondaryUnit(DesignUnit):
	"""
	A base-class for all secondary design units.

	.. seealso::

	   * :class:`Package body <pyVHDLModel.DesignUnit.PackageBody>`
	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	"""


@export
class Context(PrimaryUnit):
	"""
	Represents a context declaration.

	A context contains a generic list of all its items (library clauses, use clauses and context references) in
	:data:`_contextItems`.

	Furthermore, when a context gets initialized, the item kinds get separated into individual lists:

	* :class:`~pyVHDLModel.DesignUnit.LibraryClause` |rarr| :data:`_libraryReferences`
	* :class:`~pyVHDLModel.DesignUnit.UseClause` |rarr| :data:`_packageReferences`
	* :class:`~pyVHDLModel.DesignUnit.ContextReference` |rarr| :data:`_contextReferences`

	When :meth:`pyVHDLModel.Design.LinkContexts` got called, these lists were processed and the fields:

	* :data:`_referencedLibraries` (:pycode:`dict[libName, Library]`)
	* :data:`_referencedPackages` (:pycode:`dict[libName, [pkgName, Package]]`)
	* :data:`_referencedContexts` (:pycode:`dict[libName, [ctxName, Context]]`)

	are populated.

	.. admonition:: Example

	   .. code-block:: VHDL

	      context ctx is
	        -- ...
	      end context;

	.. seealso::

	   * :class:`Library clause <pyVHDLModel.DesignUnit.LibraryClause>`
	   * :class:`Use clause <pyVHDLModel.DesignUnit.UseClause>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Context,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                     #: The reserved words after ``end`` are optional.

	def __init__(self, identifier: str, references: Nullable[Iterable[ContextUnion]] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a context declaration.

		:param identifier:           The identifier of a model entity.
		:param references:           All context items, in declaration order.
		:param documentation:        The documentation comment associated with this declaration.
		:param parent:               The parent model entity of this entity.
		:raises VHDLModelException: If a context item is neither a library clause, use clause, nor context reference.
		"""
		super().__init__(identifier, None, documentation, parent)

		if references is not None:
			for reference in references:
				self._contextItems.append(reference)
				reference.Parent = self

				if isinstance(reference, LibraryClause):
					self._libraryReferences.append(reference)
				elif isinstance(reference, UseClause):
					self._packageReferences.append(reference)
				elif isinstance(reference, ContextReference):
					self._contextReferences.append(reference)
				else:
					raise VHDLModelException(f"Reference '{reference!r}' is neither a library clause, use clause, nor context reference.")

	@readonly
	def LibraryReferences(self) -> list[LibraryClause]:
		"""
		Read-only property to access the library references (:attr:`_libraryReferences`).

		:returns: List of library references.
		"""
		return self._libraryReferences

	@readonly
	def PackageReferences(self) -> list[UseClause]:
		"""
		Read-only property to access the package references (:attr:`_packageReferences`).

		:returns: List of package references.
		"""
		return self._packageReferences

	@readonly
	def ContextReferences(self) -> list[ContextReference]:
		"""
		Read-only property to access the context references (:attr:`_contextReferences`).

		:returns: List of context references.
		"""
		return self._contextReferences

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this context declaration and its context items with a visitor.

		A context declaration has no context clause: its context items are walked inside the declaration.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitContext(self)
		for item in self._contextItems:
			item.Visit(visitor)

		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartContext(self)

	def __str__(self) -> str:
		"""
		Formats the context declaration.

		**Format:** ``Context: mylib.myContext``

		:returns: Formatted context declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"Context: {lib}.{self._identifier}"


@export
class Package(
	PrimaryUnit,
	DesignUnitWithContextMixin,
	WithGenericsMixin,
	ConcurrentDeclarationRegionMixin,
	WithoutStatementsMixin,
	AllowBlackboxMixin
):
	"""
	Represents a package declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      package pkg is
	        -- ...
	      end package;

	.. seealso::

	   * :class:`Package instantiation <pyVHDLModel.Instantiation.PackageInstantiation>`
	   * :class:`Predefined package <pyVHDLModel.Predefined.PredefinedPackage>`
	   * :class:`Package body implementing it <pyVHDLModel.DesignUnit.PackageBody>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Package,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                     #: The reserved words after ``end`` are optional.

	_packageBody:       Nullable[PackageBody]        #: The corresponding package body, or ``None`` if none was analyzed.

	_deferredConstants: dict[str, DeferredConstant]  #: Deferred constants, indexed by name.

	def __init__(
		self,
		identifier:    str,
		contextItems:  Nullable[Iterable[ContextUnion]] = None,
		genericItems:  Nullable[Iterable[GenericInterfaceItemMixin]] = None,
		declaredItems: Nullable[Iterable] = None,
		documentation: Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initialize a package.

		:param identifier:    Name of the VHDL package.
		:param contextItems:
		:param genericItems:
		:param declaredItems:
		:param documentation:
		:param allowBlackbox: Specify if blackboxes are allowed in this design.
		:param parent:        The parent model entity (library) of this VHDL package.
		"""
		super().__init__(identifier, contextItems, documentation, parent)
		DesignUnitWithContextMixin.__init__(self)
		ConcurrentDeclarationRegionMixin.__init__(
			self, self._normalizedIdentifier, declaredItems, self._CONTINUES_PARENT_REGION
		)
		WithGenericsMixin.__init__(self, genericItems)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		self._packageBody = None

		self._deferredConstants = {}
		self._components = {}

	@readonly
	def PackageBody(self) -> Nullable[PackageBody]:
		"""
		Read-only property to access the package body (:attr:`_packageBody`).

		:returns: The package body, or ``None`` if not set.
		"""
		return self._packageBody

	@readonly
	def DeclaredItems(self) -> list:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	@readonly
	def DeferredConstants(self) -> dict[str, DeferredConstant]:
		"""
		Read-only property to access the deferred constants (:attr:`_deferredConstants`).

		:returns: Dictionary of deferred constants, indexed by normalized identifier.
		"""
		return self._deferredConstants

	@readonly
	def Components(self) -> dict[str, Component]:
		"""
		Read-only property to access the components (:attr:`_components`).

		:returns: Dictionary of components, indexed by normalized identifier.
		"""
		return self._components

	def _IndexOtherDeclaredItem(self, item) -> None:
		if isinstance(item, DeferredConstant):
			for normalizedIdentifier in item.NormalizedIdentifiers:
				self._deferredConstants[normalizedIdentifier] = item
		elif isinstance(item, Component):
			self._components[item._normalizedIdentifier] = item
		else:
			super()._IndexOtherDeclaredItem(item)

	def _UnindexOtherDeclaredItem(self, item: ModelEntity) -> None:
		"""
		Remove a declared item, which a concurrent declaration region doesn't handle itself.

		A deferred constant is removed from :attr:`_deferredConstants`. An entry referring to another deferred constant of
		the same identifier (a duplicate declaration) is kept: :meth:`RemoveDeclaredItem` indexes the region again.

		:param item: The declared item.
		"""
		if isinstance(item, DeferredConstant):
			for normalizedIdentifier in item._normalizedIdentifiers:
				if self._deferredConstants.get(normalizedIdentifier) is item:
					del self._deferredConstants[normalizedIdentifier]
		else:
			super()._UnindexOtherDeclaredItem(item)

	def _SharedRegions(self) -> tuple[ConcurrentDeclarationRegionMixin, ...]:
		"""
		Return the other language constructs forming one declarative region with this package.

		:returns: Tuple of the package body, if linked (:attr:`_packageBody`).
		"""
		return () if self._packageBody is None else (self._packageBody, )

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this package declaration, its context clause, its generic clause and its declared items with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		self._VisitContextClause(visitor)
		visitor.VisitPackage(self)
		self._VisitGenericClause(visitor)
		self._VisitDeclaredItems(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartPackage(self)

	def __str__(self) -> str:
		"""
		Formats the package declaration.

		**Format:** ``Package: 'mylib.myPackage'``

		:returns: Formatted package declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"Package: '{lib}.{self._identifier}'"

	def __repr__(self) -> str:
		"""
		Formats a representation of the package declaration.

		**Format:** ``mylib.myPackage``

		:returns: String representation of the package declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"{lib}.{self._identifier}"


	def IndexDeclaredItems(self) -> None:
		"""
		A generic package's generics share the declarative region of its declarative part.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self._deferredConstants.clear()
		self._IndexGenericItems()

		super().IndexDeclaredItems()

	def _Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Return all declarations of this package: its generics share the declarative region.

		:returns: Tuple of declarations: the generics, then the declared items.
		"""
		return (*self._genericItems, *super()._Declarations())


@export
class PackageBody(SecondaryUnit, DesignUnitWithContextMixin, ConcurrentDeclarationRegionMixin, WithoutStatementsMixin):
	"""
	Represents a package body declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      package body pkg is
	        -- ...
	      end package body;

	.. seealso::

	   * :class:`Predefined package body <pyVHDLModel.Predefined.PredefinedPackageBody>`
	   * :class:`Package it implements <pyVHDLModel.DesignUnit.Package>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Package, ReservedWord.Body)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                                       #: The reserved words after ``end`` are optional.

	_CONTINUES_PARENT_REGION: ClassVar[bool] = True  #: A package body continues its package's declarative region.

	_package:               PackageSymbol           #: Reference to the package this body implements.

	def __init__(
		self,
		packageSymbol: PackageSymbol,
		contextItems: Nullable[Iterable[ContextUnion]] = None,
		declaredItems: Nullable[Iterable] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a package body declaration.

		:param packageSymbol: Reference to the package this body implements.
		:param contextItems:  List of all context items (library, use and context clauses).
		:param declaredItems: List of all declared items in this concurrent declaration region.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(packageSymbol.Name.Identifier, contextItems, documentation, parent)
		DesignUnitWithContextMixin.__init__(self)
		ConcurrentDeclarationRegionMixin.__init__(
			self, self._normalizedIdentifier, declaredItems, self._CONTINUES_PARENT_REGION
		)

		self._package = packageSymbol
		packageSymbol.Parent = self

	@readonly
	def Package(self) -> PackageSymbol:
		"""
		Read-only property to access the package (:attr:`_package`).

		:returns: The package.
		"""
		return self._package

	@readonly
	def DeclaredItems(self) -> list:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	def LinkDeclaredItemsToPackage(self) -> None:
		pass

	def _SharedRegions(self) -> tuple[ConcurrentDeclarationRegionMixin, ...]:
		"""
		Return the other language constructs forming one declarative region with this package body.

		:returns: Tuple of the package, if linked.
		"""
		package = self._package.Package
		return () if package is None else (package, )

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this package body, its context clause and its declared items with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		self._VisitContextClause(visitor)
		visitor.VisitPackageBody(self)
		self._VisitDeclaredItems(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartPackageBody(self)

	def __str__(self) -> str:
		"""
		Formats the package body declaration.

		**Format:** ``Package Body: mylib.myPackage(body)``

		:returns: Formatted package body declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"Package Body: {lib}.{self._identifier}(body)"

	def __repr__(self) -> str:
		"""
		Formats a representation of the package body declaration.

		**Format:** ``mylib.myPackage(body)``

		:returns: String representation of the package body declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"{lib}.{self._identifier}(body)"


@export
class Entity(PrimaryUnit, DesignUnitWithContextMixin, WithGenericsMixin, WithPortsMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin):
	"""
	Represents an entity declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      entity ent is
	        -- ...
	      end entity;

	.. seealso::

	   * :class:`Architecture implementing it <pyVHDLModel.DesignUnit.Architecture>`
	   * :class:`Component declaring the same interface <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Configuration binding it <pyVHDLModel.DesignUnit.Configuration>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Entity,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                    #: The reserved words after ``end`` are optional.

	_architectures: dict[str, Architecture]  #: Dictionary of all architectures of this entity, indexed by name.

	def __init__(
		self,
		identifier:    str,
		contextItems:  Nullable[Iterable[ContextUnion]] = None,
		genericItems:  Nullable[Iterable[GenericInterfaceItemMixin]] = None,
		portItems:     Nullable[Iterable[PortInterfaceItemMixin]] = None,
		declaredItems: Nullable[Iterable] = None,
		statements:    Nullable[Iterable[ConcurrentStatement]] = None,
		documentation: Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None,
		portGroups:    Nullable[Iterable[PortGroup]] = None
	) -> None:
		"""
		Initializes an entity declaration.

		:param identifier:    The identifier of a model entity.
		:param contextItems:  List of all context items (library, use and context clauses).
		:param genericItems:  List of all generics, in declaration order.
		:param portItems:     List of all ports, in declaration order.
		:param declaredItems: List of all declared items in this concurrent declaration region.
		:param statements:    List of all concurrent statements in this construct.
		:param documentation: The documentation comment associated with this declaration.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		:param portGroups:    Optional, list of port groups partitioning the ports, in declaration order. Default:
		                      ``None``, one unnamed port group.
		"""
		super().__init__(identifier, contextItems, documentation, parent)
		DesignUnitWithContextMixin.__init__(self)
		ConcurrentDeclarationRegionMixin.__init__(
			self, self._normalizedIdentifier, declaredItems, self._CONTINUES_PARENT_REGION
		)
		WithGenericsMixin.__init__(self, genericItems)
		WithPortsMixin.__init__(self, portItems, portGroups)
		ConcurrentStatementsMixin.__init__(self, statements)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		self._architectures = {}

	@readonly
	def Architectures(self) -> dict[str, Architecture]:
		"""
		Read-only property to access the architectures (:attr:`_architectures`).

		:returns: Dictionary of architectures, indexed by normalized identifier.
		"""
		return self._architectures

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this entity, its context clause, its interface, its declared items and its statements with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		self._VisitContextClause(visitor)
		visitor.VisitEntity(self)
		self._VisitGenericClause(visitor)
		self._VisitPortClause(visitor)
		self._VisitDeclaredItems(visitor)
		visitor.VisitBegin(self)
		self._VisitStatements(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartEntity(self)

	def __str__(self) -> str:
		"""
		Formats the entity declaration.

		**Format:** ``Entity: 'mylib.myEntity(rtl, sim)'``

		The parenthesis lists the known architectures, or ``?`` if there are none.

		:returns: Formatted entity declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"
		archs = ', '.join(self._architectures.keys()) if self._architectures else "?"

		return f"Entity: '{lib}.{self._identifier}({archs})'"

	def __repr__(self) -> str:
		"""
		Formats a representation of the entity declaration.

		**Format:** ``mylib.myEntity(rtl, sim)``

		:returns: String representation of the entity declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"
		archs = ', '.join(self._architectures.keys()) if self._architectures else "?"

		return f"{lib}.{self._identifier}({archs})"


	def IndexDeclaredItems(self) -> None:
		"""
		An entity's generics and ports share the declarative region of its declarative part.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self._IndexGenericItems()
		self._IndexPortItems()

		super().IndexDeclaredItems()

	def _Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Return all declarations of this entity: its generics and ports share the declarative region.

		:returns: Tuple of declarations: the generics, the ports, then the declared items.
		"""
		return (*self._genericItems, *self._portItems, *super()._Declarations())

	def _SharedRegions(self) -> tuple[ConcurrentDeclarationRegionMixin, ...]:
		"""
		Return the other language constructs forming one declarative region with this entity.

		:returns: Tuple of the linked architectures (:attr:`_architectures`).
		"""
		return tuple(self._architectures.values())


@export
class Architecture(SecondaryUnit, DesignUnitWithContextMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin):
	"""
	Represents an architecture declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      architecture rtl of ent is
	        -- ...
	      begin
	        -- ...
	      end architecture;

	.. seealso::

	   * :class:`Entity it implements <pyVHDLModel.DesignUnit.Entity>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Architecture,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                          #: The reserved words after ``end`` are optional.

	_CONTINUES_PARENT_REGION: ClassVar[bool] = True  #: An architecture continues its entity's declarative region.

	_entity:                EntitySymbol           #: Reference to the entity this architecture implements.

	def __init__(
		self,
		identifier:    str,
		entity:        EntitySymbol,
		contextItems:  Nullable[Iterable[Context]] = None,
		declaredItems: Nullable[Iterable] = None,
		statements:    Iterable[ConcurrentStatement] = None,
		documentation: Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an architecture declaration.

		:param identifier:    The identifier of a model entity.
		:param entity:        Reference to the entity this architecture implements.
		:param contextItems:  List of all context items (library, use and context clauses).
		:param declaredItems: List of all declared items in this concurrent declaration region.
		:param statements:    List of all concurrent statements in this construct.
		:param documentation: The documentation comment associated with this declaration.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, contextItems, documentation, parent)
		DesignUnitWithContextMixin.__init__(self)
		ConcurrentDeclarationRegionMixin.__init__(
			self, self._normalizedIdentifier, declaredItems, self._CONTINUES_PARENT_REGION
		)
		ConcurrentStatementsMixin.__init__(self, statements)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		self._entity = entity
		entity.Parent = self

	@readonly
	def Entity(self) -> EntitySymbol:  # FIXME: change to entitySymbol, offer entity directly, but raise exception if not resolved.
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this architecture, its context clause, its entity, its declared items and its statements with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		self._VisitContextClause(visitor)
		visitor.VisitArchitecture(self)
		self._entity.Visit(visitor)
		visitor.VisitIs(self)
		self._VisitDeclaredItems(visitor)
		visitor.VisitBegin(self)
		self._VisitStatements(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartArchitecture(self)

	def __str__(self) -> str:
		"""
		Formats the architecture declaration.

		**Format:** ``Architecture: mylib.myEntity(rtl)``

		:returns: Formatted architecture declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"
		ent = self._entity._name._identifier if self._entity is not None else "?"

		return f"Architecture: {lib}.{ent}({self._identifier})"

	def __repr__(self) -> str:
		"""
		Formats a representation of the architecture declaration.

		**Format:** ``mylib.myEntity(rtl)``

		:returns: String representation of the architecture declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"
		ent = self._entity._name._identifier if self._entity is not None else "?"

		return f"{lib}.{ent}({self._identifier})"

	def _SharedRegions(self) -> tuple[ConcurrentDeclarationRegionMixin, ...]:
		"""
		Return the other language constructs forming one declarative region with this architecture.

		:returns: Tuple of the entity, if linked.
		"""
		entity = self._entity.Entity
		return () if entity is None else (entity, )


@export
class Component(
	ModelEntity,
	NamedEntityMixin,
	DocumentedEntityMixin,
	WithGenericsMixin,
	WithPortsMixin,
	AllowBlackboxMixin
):
	"""
	Represents a component declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      component ent is
	        -- ...
	      end component;

	.. seealso::

	   * :class:`Entity it may be bound to <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Component configuration <pyVHDLModel.Configuration.ComponentConfiguration>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Component,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     False                      #: The reserved words after ``end`` are optional.

	_isBlackbox: Nullable[bool]    #: Component is a blackbox.
	_entity:     Nullable[Entity]  #: Linked entity, or ``None`` if unresolved.

	def __init__(
		self,
		identifier:    str,
		genericItems:  Nullable[Iterable[GenericInterfaceItemMixin]] = None,
		portItems:     Nullable[Iterable[PortInterfaceItemMixin]] = None,
		documentation: Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None,
		portGroups:    Nullable[Iterable[PortGroup]] = None
	) -> None:
		"""
		Initializes a component declaration.

		:param identifier:    The identifier of a model entity.
		:param genericItems:  List of all generics of this component, in declaration order.
		:param portItems:     List of all ports of this component, in declaration order.
		:param documentation: The documentation comment associated with this declaration.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		:param portGroups:    Optional, list of port groups partitioning the ports, in declaration order. Default:
		                      ``None``, one unnamed port group.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)
		WithGenericsMixin.__init__(self, genericItems)
		WithPortsMixin.__init__(self, portItems, portGroups)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		self._isBlackbox = None
		self._entity =     None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this component declaration, its generic clause and its port clause with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitComponent(self)
		self._VisitGenericClause(visitor)
		self._VisitPortClause(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartComponent(self)

	def _AddToNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Add nothing, because a component has no namespace.

		:param element: The named element, e.g. an interface item.
		"""

	def _RemoveFromNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Remove nothing, because a component has no namespace.

		:param element: The named element, e.g. an interface item.
		"""

	def _ClashingDeclarations(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> tuple[ModelEntity, ...]:
		"""
		Return the generics and ports of this component sharing an identifier with the given item.

		:param item: The new generic or port.
		:returns:    Tuple of clashing generics and ports.
		"""
		identifiers = set(normalizedIdentifiersOf(item))
		return tuple(
			declaration for declaration in (*self._genericItems, *self._portItems)
			if not identifiers.isdisjoint(normalizedIdentifiersOf(declaration))
		)

	@readonly
	def IsBlackbox(self) -> Nullable[bool]:
		"""
		Check if the component is a blackbox (:attr:`_isBlackbox`).

		If components were not linked to matching entities, this property returns ``None``.

		:returns: ``True``, if the component is a blackbox; ``False``, if it is not; ``None``, if components
		          were not linked to entities yet.
		"""
		return self._isBlackbox

	@property
	def Entity(self) -> Nullable[Entity]:
		"""
		Property to access the entity (:attr:`_entity`).

		:returns: The entity, or ``None`` if not set.
		"""
		return self._entity

	@Entity.setter
	def Entity(self, value: Entity) -> None:
		self._entity = value
		self._isBlackbox = False

	def __str__(self) -> str:
		"""
		Formats the component declaration.

		**Format:** ``Component: myComponent``

		:returns: Formatted component declaration.
		"""
		return f"Component: {self._identifier}"

	def __repr__(self) -> str:
		"""
		Formats a representation of the component declaration.

		**Format:** ``mylib.myPackage:myComponent``

		:returns: String representation of the component declaration.
		"""
		return f"{self._parent!r}:{self._identifier}"


@export
class Configuration(PrimaryUnit, DesignUnitWithContextMixin):
	"""
	Represents a configuration declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      configuration cfg of ent is
	        for rtl
	          -- ...
	        end for;
	      end configuration;

	.. seealso::

	   * :class:`Entity it configures <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Block configuration <pyVHDLModel.Configuration.BlockConfiguration>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Configuration,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                           #: The reserved words after ``end`` are optional.

	_entity:             EntitySymbol        #: Reference to the entity this configuration configures.
	_blockConfiguration: BlockConfiguration  #: The configuration of the entity's architecture.
	_namespace:          Namespace           #: The namespace of this configuration's declarative region.

	def __init__(
		self,
		identifier: str,
		entity: EntitySymbol,
		blockConfiguration: BlockConfiguration,
		contextItems: Nullable[Iterable[Context]] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a configuration declaration.

		:param identifier:         The identifier of a model entity.
		:param entity:             Reference to the entity this configuration configures.
		:param blockConfiguration: The configuration of the entity's architecture.
		:param contextItems:       List of all context items (library, use and context clauses).
		:param documentation:      The documentation comment associated with this declaration.
		:param parent:             The parent model entity of this entity.
		"""
		super().__init__(identifier, contextItems, documentation, parent)
		DesignUnitWithContextMixin.__init__(self)

		self._namespace = Namespace(self._normalizedIdentifier)

		self._entity = entity
		entity.Parent = self

		self._blockConfiguration = blockConfiguration
		blockConfiguration.Parent = self

	@readonly
	def Entity(self) -> EntitySymbol:
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	@readonly
	def BlockConfiguration(self) -> BlockConfiguration:
		"""
		Read-only property to access the block configuration (:attr:`_blockConfiguration`).

		:returns: The block configuration.
		"""
		return self._blockConfiguration

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this configuration, its context clause, its entity and its block configuration with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		self._VisitContextClause(visitor)
		visitor.VisitConfiguration(self)
		self._entity.Visit(visitor)
		visitor.VisitIs(self)
		self._blockConfiguration.Visit(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartConfiguration(self)

	def __str__(self) -> str:
		"""
		Formats the configuration declaration.

		**Format:** ``Configuration: mylib.myConfiguration``

		:returns: Formatted configuration declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"Configuration: {lib}.{self._identifier}"

	def __repr__(self) -> str:
		"""
		Formats a representation of the configuration declaration.

		**Format:** ``mylib.myConfiguration``

		:returns: String representation of the configuration declaration.
		"""
		lib = self._parent._identifier if self._parent is not None else "?"

		return f"{lib}.{self._identifier}"
