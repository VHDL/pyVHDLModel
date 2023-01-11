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

Design units are contexts, entities, architectures, packages and their bodies as well as configurations.
"""
from typing import List, Dict, Union, Iterable, Optional as Nullable

from pyTooling.Decorators import export
from pyTooling.Graph import Vertex

from pyVHDLModel.Exception  import VHDLModelException
from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Namespace  import Namespace
from pyVHDLModel.Symbol     import Symbol, PackageSymbol, EntitySymbol
from pyVHDLModel.Interface  import GenericInterfaceItem, PortInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Object     import Constant, Variable, Signal
from pyVHDLModel.Type       import Type, Subtype
from pyVHDLModel.Concurrent import ConcurrentStatement, ConcurrentStatements, ConcurrentDeclarations


ContextUnion = Union[
	'LibraryClause',
	'UseClause',
	'ContextReference'
]


@export
class Reference(ModelEntity):
	_symbols:       List[Symbol]

	def __init__(self, symbols: Iterable[Symbol]):
		super().__init__()

		self._symbols = [s for s in symbols]

	@property
	def Symbols(self) -> List[Symbol]:
		return self._symbols


@export
class LibraryClause(Reference):
	pass


@export
class UseClause(Reference):
	pass


@export
class ContextReference(Reference):
	# TODO: rename to ContextClause?
	pass


@export
class DesignUnitWithContextMixin:  # (metaclass=ExtendedType, useSlots=True):
	pass


@export
class DesignUnit(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""A ``DesignUnit`` is a base-class for all design units."""

	_library:             'Library'                        #: The VHDL library, the design unit was analyzed into.

	# Either written as statements before (e.g. entity, architecture, package, ...), or as statements inside (context)
	_contextItems:        List['ContextUnion']             #: List of all context items (library, use and context clauses).
	_libraryReferences:   List['LibraryClause']            #: List of library clauses.
	_packageReferences:   List['UseClause']                #: List of use clauses.
	_contextReferences:   List['ContextReference']         #: List of context clauses.

	_referencedLibraries: Dict[str, 'Library']             #: Referenced libraries based on explicit library clauses or implicit inheritance
	_referencedPackages:  Dict[str, Dict[str, 'Package']]  #: Referenced packages based on explicit use clauses or implicit inheritance
	_referencedContexts:  Dict[str, 'Context']             #: Referenced contexts based on explicit context references or implicit inheritance

	_dependencyVertex:    Vertex[str, 'DesignUnit', None, None]  #: The vertex in the dependency graph
	_hierarchyVertex:     Vertex[str, 'DesignUnit', None, None]  #: The vertex in the hierarchy graph

	_namespace:           'Namespace'

	def __init__(self, identifier: str, contextItems: Iterable['ContextUnion'] = None, documentation: str = None):
		"""
		Initializes a design unit.

		:param identifier:    Identifier (name) of the design unit.
		:param contextItems:  A sequence of library, use or context clauses.
		:param documentation: Associated documentation of the design unit.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._library = None

		self._contextItems = []
		self._libraryReferences = []
		self._packageReferences = []
		self._contextReferences = []

		if contextItems is not None:
			for item in contextItems:
				self._contextItems.append(item)
				if isinstance(item, UseClause):
					self._packageReferences.append(item)
				elif isinstance(item, LibraryClause):
					self._libraryReferences.append(item)
				elif isinstance(item, ContextReference):
					self._contextReferences.append(item)

		self._referencedLibraries = {}
		self._referencedPackages = {}
		self._referencedContexts = {}

		self._dependencyVertex = None
		self._hierarchyVertex = None

		self._namespace = Namespace(self._normalizedIdentifier)

	@property
	def Document(self) -> 'Document':
		return self._parent

	@Document.setter
	def Document(self, document: 'Document') -> None:
		self._parent = document

	@property
	def Library(self) -> 'Library':
		return self._library

	@Library.setter
	def Library(self, library: 'Library') -> None:
		self._library = library

	@property
	def ContextItems(self) -> List['ContextUnion']:
		"""
		Read-only property to access the sequence of all context items comprising library, use and context clauses
		(:py:attr:`_contextItems`).

		:returns: Sequence of context items.
		"""
		return self._contextItems

	@property
	def ContextReferences(self) -> List['ContextReference']:
		"""
		Read-only property to access the sequence of context clauses (:py:attr:`_contextReferences`).

		:returns: Sequence of context clauses.
		"""
		return self._contextReferences

	@property
	def LibraryReferences(self) -> List['LibraryClause']:
		"""
		Read-only property to access the sequence of library clauses (:py:attr:`_libraryReferences`).

		:returns: Sequence of library clauses.
		"""
		return self._libraryReferences

	@property
	def PackageReferences(self) -> List['UseClause']:
		"""
		Read-only property to access the sequence of use clauses (:py:attr:`_packageReferences`).

		:returns: Sequence of use clauses.
		"""
		return self._packageReferences

	@property
	def ReferencedLibraries(self) -> Dict[str, 'Library']:
		return self._referencedLibraries

	@property
	def ReferencedPackages(self) -> Dict[str, 'Package']:
		return self._referencedPackages

	@property
	def ReferencedContexts(self) -> Dict[str, 'Context']:
		return self._referencedContexts

	@property
	def DependencyVertex(self) -> Vertex:
		return self._dependencyVertex

	@property
	def HierarchyVertex(self) -> Vertex:
		return self._hierarchyVertex


@export
class PrimaryUnit(DesignUnit):
	"""A ``PrimaryUnit`` is a base-class for all primary units."""


@export
class SecondaryUnit(DesignUnit):
	"""A ``SecondaryUnit`` is a base-class for all secondary units."""


@export
class Context(PrimaryUnit):
	_references:        List[ContextUnion]
	_libraryReferences: List[LibraryClause]
	_packageReferences: List[UseClause]
	_contextReferences: List[ContextReference]

	def __init__(self, identifier: str, references: Iterable[ContextUnion] = None, documentation: str = None):
		super().__init__(identifier, documentation)

		self._references = []
		self._libraryReferences = []
		self._packageReferences = []
		self._contextReferences = []

		if references is not None:
			for reference in references:
				self._references.append(reference)
				reference._parent = self

				if isinstance(reference, LibraryClause):
					self._libraryReferences.append(reference)
				elif isinstance(reference, UseClause):
					self._packageReferences.append(reference)
				elif isinstance(reference, ContextReference):
					self._contextReferences.append(reference)
				else:
					raise VHDLModelException()

	@property
	def LibraryReferences(self) -> List[LibraryClause]:
		return self._libraryReferences

	@property
	def PackageReferences(self) -> List[UseClause]:
		return self._packageReferences

	@property
	def ContextReferences(self) -> List[ContextReference]:
		return self._contextReferences

	def __str__(self):
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"Context: {lib}.{self.Identifier}"


@export
class Package(PrimaryUnit, DesignUnitWithContextMixin):
	_genericItems:      List[GenericInterfaceItem]
	_declaredItems:     List

	_types:      Dict[str, Union[Type, Subtype]]
	_objects:    Dict[str, Union[Constant, Variable, Signal]]
	_constants:  Dict[str, Constant]
	_functions:  Dict[str, Dict[str, Function]]
	_procedures: Dict[str, Dict[str, Procedure]]
	_components: Dict[str, 'Component']

	def __init__(self, identifier: str, contextItems: Iterable['Context'] = None, genericItems: Iterable[GenericInterfaceItem] = None, declaredItems: Iterable = None, documentation: str = None):
		super().__init__(identifier, contextItems, documentation)
		DesignUnitWithContextMixin.__init__(self)

		# TODO: extract to mixin
		self._genericItems = []  # TODO: convert to dict
		if genericItems is not None:
			for generic in genericItems:
				self._genericItems.append(generic)
				generic._parent = self

		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

		self._types = {}
		self._objects = {}
		self._constants = {}
		self._functions = {}
		self._procedures = {}
		self._components = {}

	@property
	def GenericItems(self) -> List[GenericInterfaceItem]:
		return self._genericItems

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems

	# TODO: move into __init__ ?
	# TODO: share with architecture and block statement?
	def IndexPackage(self):
		for item in self._declaredItems:
			if isinstance(item, Type):
				print(item)
			elif isinstance(item, Subtype):
				print(item)
			elif isinstance(item, Function):
				print(item)
			elif isinstance(item, Procedure):
				print(item)
			elif isinstance(item, Constant):
				for identifier in item.Identifiers:
					normalizedIdentifier = identifier.lower()
					self._constants[normalizedIdentifier] = item
					self._objects[normalizedIdentifier] = item
			elif isinstance(item, Variable):
				for identifier in item.Identifiers:
					self._objects[identifier.lower()] = item
			elif isinstance(item, Signal):
				for identifier in item.Identifiers:
					self._objects[identifier.lower()] = item
			elif isinstance(item, Component):
				self._components[item.NormalizedIdentifier] = item
			else:
				print(item)

	def __str__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"Package: {lib}.{self.Identifier}"

	def __repr__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"{lib}.{self.Identifier}"


@export
class PackageBody(SecondaryUnit, DesignUnitWithContextMixin):
	_package: PackageSymbol
	_declaredItems:     List

	def __init__(self, packageSymbol: PackageSymbol, contextItems: Iterable['Context'] = None, declaredItems: Iterable = None, documentation: str = None):
		super().__init__(packageSymbol.Identifier, contextItems, documentation)
		DesignUnitWithContextMixin.__init__(self)

		self._package = packageSymbol
		packageSymbol._parent = self

		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def Package(self) -> PackageSymbol:
		return self._package

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems

	def IndexPackageBody(self):
		pass

	def LinkDeclaredItemsToPackage(self):
		pass

	def __str__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"Package Body: {lib}.{self.Identifier}(body)"

	def __repr__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"{lib}.{self.Identifier}(body)"


@export
class Entity(PrimaryUnit, DesignUnitWithContextMixin, ConcurrentDeclarations, ConcurrentStatements):
	_genericItems:  List[GenericInterfaceItem]
	_portItems:     List[PortInterfaceItem]

	_architectures: Dict[str, 'Architecture']

	def __init__(
		self,
		identifier: str,
		contextItems: Iterable[ContextUnion] = None,
		genericItems: Iterable[GenericInterfaceItem] = None,
		portItems: Iterable[PortInterfaceItem] = None,
		declaredItems: Iterable = None,
		statements: Iterable[ConcurrentStatement] = None,
		documentation: str = None
	):
		super().__init__(identifier, contextItems, documentation)
		DesignUnitWithContextMixin.__init__(self)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)

		# TODO: extract to mixin
		self._genericItems = []
		if genericItems is not None:
			for item in genericItems:
				self._genericItems.append(item)
				item._parent = self

		# TODO: extract to mixin
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item._parent = self

		self._architectures = {}

	@property
	def GenericItems(self) -> List[GenericInterfaceItem]:
		return self._genericItems

	@property
	def PortItems(self) -> List[PortInterfaceItem]:
		return self._portItems

	@property
	def Architectures(self) -> Dict[str, 'Architecture']:
		return self._architectures

	def __str__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"Entity: {lib}.{self.Identifier}({', '.join(self._architectures.keys())})"

	def __repr__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"{lib}.{self.Identifier}({', '.join(self._architectures.keys())})"


@export
class Architecture(SecondaryUnit, DesignUnitWithContextMixin, ConcurrentDeclarations, ConcurrentStatements):
	_library:       'Library' = None
	_entity: EntitySymbol

	def __init__(self, identifier: str, entity: EntitySymbol, contextItems: Iterable[Context] = None, declaredItems: Iterable = None, statements: Iterable['ConcurrentStatement'] = None, documentation: str = None):
		super().__init__(identifier, contextItems, documentation)
		DesignUnitWithContextMixin.__init__(self)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)

		self._entity = entity
		entity._parent = self

	@property
	def Entity(self) -> EntitySymbol:
		return self._entity

	# TODO: move to Design Unit
	@property
	def Library(self) -> 'Library':
		return self._library

	@Library.setter
	def Library(self, library: 'Library') -> None:
		self._library = library

	def __str__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""
		ent = self._entity.Identifier + "?" if self._entity is not None else ""

		return f"Architecture: {lib}.{ent}({self.Identifier})"

	def __repr__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""
		ent = self._entity.Identifier + "?" if self._entity is not None else ""

		return f"{lib}.{ent}({self.Identifier})"


@export
class Component(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	_genericItems:      List[GenericInterfaceItem]
	_portItems:         List[PortInterfaceItem]

	_entity:            Nullable[Entity]

	def __init__(self, identifier: str, genericItems: Iterable[GenericInterfaceItem] = None, portItems: Iterable[PortInterfaceItem] = None, documentation: str = None):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		# TODO: extract to mixin
		self._genericItems = []
		if genericItems is not None:
			for item in genericItems:
				self._genericItems.append(item)
				item._parent = self

		# TODO: extract to mixin
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item._parent = self

	@property
	def GenericItems(self) -> List[GenericInterfaceItem]:
		return self._genericItems

	@property
	def PortItems(self) -> List[PortInterfaceItem]:
		return self._portItems

	@property
	def Entity(self) -> Nullable[Entity]:
		return self._entity

	@Entity.setter
	def Entity(self, value: Entity) -> None:
		self._entity = value


@export
class Configuration(PrimaryUnit, DesignUnitWithContextMixin):
	def __init__(self, identifier: str, contextItems: Iterable[Context] = None, documentation: str = None):
		super().__init__(identifier, contextItems, documentation)
		DesignUnitWithContextMixin.__init__(self)

	def __str__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"Configuration: {lib}.{self.Identifier}"

	def __repr__(self) -> str:
		lib = self._library.Identifier + "?" if self._library is not None else ""

		return f"{lib}.{self.Identifier}"
