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
# Copyright 2017-2024 Patrick Lehmann - Boetzingen, Germany                                                            #
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
**An abstract VHDL language model.**

This package provides a unified abstract language model for VHDL. Projects reading from source files can derive own
classes and implement additional logic to create a concrete language model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can build higher level features and services
on such a model, while supporting multiple frontends.

.. admonition:: Copyright Information

   :copyright: Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany
   :copyright: Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
   :license: Apache License, Version 2.0
"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2016-2024, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.29.2"


from enum                      import unique, Enum, Flag, auto
from pathlib                   import Path
from sys                       import version_info

from typing                    import Union, Dict, cast, List, Generator, Optional as Nullable

from pyTooling.Common          import getFullyQualifiedName
from pyTooling.Decorators      import export, readonly
from pyTooling.Graph           import Graph, Vertex, Edge

from pyVHDLModel.Exception     import VHDLModelException
from pyVHDLModel.Exception     import LibraryExistsInDesignError, LibraryRegisteredToForeignDesignError, LibraryNotRegisteredError, EntityExistsInLibraryError
from pyVHDLModel.Exception     import ArchitectureExistsInLibraryError, PackageExistsInLibraryError, PackageBodyExistsError, ConfigurationExistsInLibraryError
from pyVHDLModel.Exception     import ContextExistsInLibraryError, ReferencedLibraryNotExistingError
from pyVHDLModel.Base          import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Expression    import UnaryExpression, BinaryExpression, TernaryExpression
from pyVHDLModel.Namespace     import Namespace
from pyVHDLModel.Object        import Obj, Signal, Constant, DeferredConstant
from pyVHDLModel.Symbol        import PackageReferenceSymbol, AllPackageMembersReferenceSymbol, PackageMemberReferenceSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Concurrent    import EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation
from pyVHDLModel.DesignUnit    import DesignUnit, PrimaryUnit, Architecture, PackageBody, Context, Entity, Configuration, Package
from pyVHDLModel.PSLModel      import VerificationUnit, VerificationProperty, VerificationMode
from pyVHDLModel.Instantiation import PackageInstantiation
from pyVHDLModel.Type          import IntegerType, PhysicalType, ArrayType, RecordType


@export
@unique
class VHDLVersion(Enum):
	"""
	An enumeration for all possible version numbers for VHDL and VHDL-AMS.

	A version can be given as integer or string and is represented as a unified
	enumeration value.

	This enumeration supports compare operators.
	"""

	Any =                -1  #: Any
	VHDL87 =             87  #: VHDL-1987
	VHDL93 =             93  #: VHDL-1993
	AMS93 =            1993  #: VHDL-AMS-1993
	AMS99 =            1999  #: VHDL-AMS-1999
	VHDL2000 =         2000  #: VHDL-2000
	VHDL2002 =         2002  #: VHDL-2002
	VHDL2008 =         2008  #: VHDL-2008
	AMS2017 =          2017  #: VHDL-AMS-2017
	VHDL2019 =         2019  #: VHDL-2019
	Latest =          10000  #: Latest VHDL (2019)

	__VERSION_MAPPINGS__: Dict[Union[int, str], Enum] = {
		-1:       Any,
		87:       VHDL87,
		93:       VHDL93,
		# 93:       AMS93,
		99:       AMS99,
		0:        VHDL2000,
		2:        VHDL2002,
		8:        VHDL2008,
		17:       AMS2017,
		19:       VHDL2019,
		1987:     VHDL87,
		# 1993:     VHDL93,
		1993:     AMS93,
		1999:     AMS99,
		2000:     VHDL2000,
		2002:     VHDL2002,
		2008:     VHDL2008,
		2017:     AMS2017,
		2019:     VHDL2019,
		10000:    Latest,
		"Any":    Any,
		"87":     VHDL87,
		"93":     VHDL93,
		# "93":     AMS93,
		"99":     AMS99,
		"00":     VHDL2000,
		"02":     VHDL2002,
		"08":     VHDL2008,
		"17":     AMS2017,
		"19":     VHDL2019,
		"1987":   VHDL87,
		# "1993":   VHDL93,
		"1993":   AMS93,
		"1999":   AMS99,
		"2000":   VHDL2000,
		"2002":   VHDL2002,
		"2008":   VHDL2008,
		"2017":   AMS2017,
		"2019":   VHDL2019,
		"Latest": Latest,
	}  #: Dictionary of VHDL and VHDL-AMS year codes variants as integer and strings for mapping to unique enum values.

	def __init__(self, *_) -> None:
		"""Patch the embedded MAP dictionary"""
		for k, v in self.__class__.__VERSION_MAPPINGS__.items():
			if (not isinstance(v, self.__class__)) and (v == self.value):
				self.__class__.__VERSION_MAPPINGS__[k] = self

	@classmethod
	def Parse(cls, value: Union[int, str]) -> "VHDLVersion":
		"""
		Parses a VHDL or VHDL-AMS year code as integer or string to an enum value.

		:param value:       VHDL/VHDL-AMS year code.
		:returns:           Enumeration value.
		:raises ValueError: If the year code is not recognized.
		"""
		try:
			return cls.__VERSION_MAPPINGS__[value]
		except KeyError:
			raise ValueError(f"Value '{value!s}' cannot be parsed to member of {cls.__name__}.")

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is less than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is less than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value < other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __le__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is less or equal than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is less or equal than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value <= other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is greater than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is greater than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value > other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is greater or equal than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is greater or equal than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value >= other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is unequal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is unequal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value != other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is equal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is equal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			if (self is self.__class__.Any) or (other is self.__class__.Any):
				return True
			else:
				return self.value == other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	@readonly
	def IsVHDL(self) -> bool:
		"""
		Checks if the version is a VHDL (not VHDL-AMS) version.

		:returns:          True if version is a VHDL version.
		"""
		return self in (self.VHDL87, self.VHDL93, self.VHDL2002, self.VHDL2008, self.VHDL2019)

	@readonly
	def IsAMS(self) -> bool:
		"""
		Checks if the version is a VHDL-AMS (not VHDL) version.

		:returns:          True if version is a VHDL-AMS version.
		"""
		return self in (self.AMS93, self.AMS99, self.AMS2017)

	def __str__(self) -> str:
		"""
		Formats the VHDL version to pattern ``VHDL'xx`` or in case of VHDL-AMS to ``VHDL-AMS'xx``.

		:return: Formatted VHDL/VHDL-AMS version.
		"""
		if self.value == self.Any.value:
			return "VHDL'Any"
		elif self.value == self.Latest.value:
			return "VHDL'Latest"

		year = str(self.value)[-2:]
		if self.IsVHDL:
			return f"VHDL'{year}"
		else:
			return f"VHDL-AMS'{year}"

	def __repr__(self) -> str:
		"""
		Formats the VHDL/VHDL-AMS version to pattern ``xxxx``.

		:return: Formatted VHDL/VHDL-AMS version.
		"""
		if self.value == self.Any.value:
			return "Any"
		elif self.value == self.Latest.value:
			return "Latest"
		else:
			return str(self.value)


@export
@unique
class ObjectClass(Enum):
	"""
	An ``ObjectClass`` is an enumeration and represents an object's class (``constant``, ``signal``, ...).

	In case no *object class* is defined, ``Default`` is used, so the *object class* is inferred from context.
	"""

	Default =    0  #: Object class not defined, thus it's context dependent.
	Constant =   1  #: Constant
	Variable =   2  #: Variable
	Signal =     3  #: Signal
	File =       4  #: File
	Type =       5  #: Type
	# FIXME: Package?
	Procedure =  6  #: Procedure
	Function =   7  #: Function

	def __str__(self) -> str:
		"""
		Formats the object class.

		:return: Formatted object class.
		"""
		return ("", "constant", "variable", "signal", "file", "type", "procedure", "function")[cast(int, self.value)]       # TODO: check performance


@export
@unique
class DesignUnitKind(Flag):
	"""
	A ``DesignUnitKind`` is an enumeration and represents the kind of design unit (``Entity``, ``Architecture``, ...).

	"""
	Context = auto()                                                             #: Context
	Package = auto()                                                             #: Package
	PackageBody = auto()                                                         #: Package Body
	Entity = auto()                                                              #: Entity
	Architecture = auto()                                                        #: Architecture
	Configuration = auto()                                                       #: Configuration

	Primary = Context | Configuration | Entity | Package                         #: List of primary design units.
	Secondary = PackageBody | Architecture                                       #: List of secondary design units.
	WithContext = Configuration | Package | Entity | PackageBody | Architecture  #: List of design units with a context.
	WithDeclaredItems = Package | Entity | PackageBody | Architecture            #: List of design units having a declaration region.

	All = Primary | Secondary                                                    #: List of all design units.


@export
@unique
class DependencyGraphVertexKind(Flag):
	"""
	A ``DependencyGraphVertexKind`` is an enumeration and represents the kind of vertex in the dependency graph.
	"""
	Document = auto()       #: A document (VHDL source file).
	Library = auto()        #: A VHDL library.

	Context = auto()        #: A context design unit.
	Package = auto()        #: A package design unit.
	PackageBody = auto()    #: A package body design unit.
	Entity = auto()         #: A entity design unit.
	Architecture = auto()   #: A architecture design unit.
	Component = auto()      #: A VHDL component.
	Configuration = auto()  #: A configuration design unit.


@export
@unique
class DependencyGraphEdgeKind(Flag):
	"""
	A ``DependencyGraphEdgeKind`` is an enumeration and represents the kind of edge in the dependency graph.
	"""
	Document =       auto()
	Library =        auto()
	Context =        auto()
	Package =        auto()
	Entity =         auto()
	# Architecture = auto()
	Configuration =  auto()
	Component =      auto()

	DeclaredIn =     auto()
	Order =          auto()
	Reference =      auto()
	Implementation = auto()
	Instantiation =  auto()

	SourceFile =                 Document | DeclaredIn
	CompileOrder =               Document | Order

	LibraryClause =              Library | Reference
	UseClause =                  Package | Reference
	ContextReference =           Context | Reference

	EntityImplementation =       Entity | Implementation
	PackageImplementation =      Package | Implementation

	EntityInstantiation =        Entity | Instantiation
	ComponentInstantiation =     Component | Instantiation
	ConfigurationInstantiation = Configuration | Instantiation


@export
@unique
class ObjectGraphVertexKind(Flag):
	"""
	A ``ObjectGraphVertexKind`` is an enumeration and represents the kind of vertex in the object graph.
	"""
	Type = auto()
	Subtype = auto()

	Constant = auto()
	DeferredConstant = auto()
	Variable = auto()
	Signal = auto()
	File = auto()

	Alias = auto()


@export
@unique
class ObjectGraphEdgeKind(Flag):
	"""
	A ``ObjectGraphEdgeKind`` is an enumeration and represents the kind of edge in the object graph.
	"""
	BaseType = auto()
	Subtype = auto()

	ReferenceInExpression = auto()


@export
class Design(ModelEntity):
	"""
	A ``Design`` represents set of VHDL libraries as well as all loaded and analysed source files (see :class:`~pyVHDLModel.Document`).

	It's the root of this code document-object-model (CodeDOM). It contains at least one VHDL library (see :class:`~pyVHDLModel.Library`). When the design is
	analysed (see :meth:`Analyze`), multiple graph data structures will be created and populated with vertices and edges. As a first result, the design's compile
	order and hierarchy can be iterated. As a second result, the design's *top-level* is identified and referenced from the design (see :attr:`TopLevel`).

	The *design* contains references to the following graphs:

	* :attr:`DependencyGraph`
	* :attr:`CompileOrderGraph`
	* :attr:`HierarchyGraph`
	* :attr:`ObjectGraph`
	"""
	_name:              Nullable[str]         #: Name of the design
	_libraries:         Dict[str, 'Library']  #: List of all libraries defined for a design.
	_documents:         List['Document']      #: List of all documents loaded for a design.
	_dependencyGraph:   Graph[None, None, None, None, None, None, None, None, str, DesignUnit, None, None, None, None, None, None, None, None, None, None, None, None, None]   #: The graph of all dependencies in the designs.
	_compileOrderGraph: Graph[None, None, None, None, None, None, None, None, None, 'Document', None, None, None, None, None, None, None, None, None, None, None, None, None]  #: A graph derived from dependency graph containing the order of documents for compilation.
	_hierarchyGraph:    Graph[None, None, None, None, None, None, None, None, str, DesignUnit, None, None, None, None, None, None, None, None, None, None, None, None, None]   #: A graph derived from dependency graph containing the design hierarchy.
	_objectGraph:       Graph[None, None, None, None, None, None, None, None, str, Obj, None, None, None, None, None, None, None, None, None, None, None, None, None]          #: The graph of all types and objects in the design.
	_toplevel:          Union[Entity, Configuration]  #: When computed, the toplevel design unit is cached in this field.

	def __init__(self, name: Nullable[str] = None) -> None:
		"""
		Initializes a VHDL design.

		:param name: Name of the design.
		"""
		super().__init__()

		self._name =      name
		self._libraries = {}
		self._documents = []

		self._compileOrderGraph = Graph()
		self._dependencyGraph = Graph()
		self._hierarchyGraph = Graph()
		self._objectGraph = Graph()
		self._toplevel = None

	@readonly
	def Libraries(self) -> Dict[str, 'Library']:
		"""
		Read-only property to access the dictionary of library names and VHDL libraries (:attr:`_libraries`).

		:returns: A dictionary of library names and VHDL libraries.
		"""
		return self._libraries

	@readonly
	def Documents(self) -> List['Document']:
		"""
		Read-only property to access the list of all documents (VHDL source files) loaded for this design (:attr:`_documents`).

		:returns: A list of all documents.
		"""
		return self._documents

	@readonly
	def CompileOrderGraph(self) -> Graph:
		"""
		Read-only property to access the compile-order graph (:attr:`_compileOrderGraph`).

		:returns: Reference to the compile-order graph.
		"""
		return self._compileOrderGraph

	@readonly
	def DependencyGraph(self) -> Graph:
		"""
		Read-only property to access the dependency graph (:attr:`_dependencyGraph`).

		:returns: Reference to the dependency graph.
		"""
		return self._dependencyGraph

	@readonly
	def HierarchyGraph(self) -> Graph:
		"""
		Read-only property to access the hierarchy graph (:attr:`_hierarchyGraph`).

		:returns: Reference to the hierarchy graph.
		"""
		return self._hierarchyGraph

	@readonly
	def ObjectGraph(self) -> Graph:
		"""
		Read-only property to access the object graph (:attr:`_objectGraph`).

		:returns: Reference to the object graph.
		"""
		return self._objectGraph

	@readonly
	def TopLevel(self) -> Union[Entity, Configuration]:
		"""
		Read-only property to access the design's *top-level* (:attr:`_toplevel`).

		When called the first time, the hierarchy graph is checked for its root elements. When there is only one root element in the graph, a new field ``toplevel``
		is added to :attr:`_hierarchyGraph` referencing that single element. In addition, the result is cached in :attr:`_toplevel`.

		:returns:                   Reference to the design's *top-level*.
		:raises VHDLModelException: If the hierarchy graph is not yet computed from dependency graph.
		:raises VHDLModelException: If there is more than one *top-level*.
		"""
		# Check for cached result
		if self._toplevel is not None:
			return self._toplevel

		if self._hierarchyGraph.EdgeCount == 0:
			raise VHDLModelException(f"Hierarchy is not yet computed from dependency graph.")

		roots = tuple(self._hierarchyGraph.IterateRoots())
		if len(roots) == 1:
			toplevel = roots[0]
			self._hierarchyGraph["toplevel"] = toplevel
			self._toplevel = toplevel.Value

			return toplevel.Value
		else:
			raise VHDLModelException(f"Found more than one toplevel: {', '.join(roots)}")

	def LoadStdLibrary(self) -> 'Library':
		"""
		Load the predefined VHDL library ``std`` into the design.

		This will create a virtual source code file ``std.vhdl`` and register VHDL design units of library ``std`` to that file.

		:returns: The library object of library ``std``.
		"""
		from pyVHDLModel.STD import Std

		doc = Document(Path("std.vhdl"), parent=self)

		library = Std()
		for designUnit in library.IterateDesignUnits():
			doc._AddDesignUnit(designUnit)

		self.AddLibrary(library)

		return library

	def LoadIEEELibrary(self) -> 'Library':
		"""
		Load the predefined VHDL library ``ieee`` into the design.

		This will create a virtual source code file ``ieee.vhdl`` and register VHDL design units of library ``ieee`` to that file.

		:returns: The library object of library ``ieee``.
		"""
		from pyVHDLModel.IEEE import Ieee

		doc = Document(Path("ieee.vhdl"), parent=self)

		library = Ieee()
		for designUnit in library.IterateDesignUnits():
			doc._AddDesignUnit(designUnit)

		self.AddLibrary(library)

		return library

	def AddLibrary(self, library: 'Library') -> None:
		"""
		Add a VHDL library to the design.

		Ensure the libraries name doesn't collide with existing libraries in the design. |br|
		If ok, set the libraries parent reference to the design.

		:param library:                                Library object to loaded.
		:raises LibraryExistsInDesignError:            If the library already exists in the design.
		:raises LibraryRegisteredToForeignDesignError: If library is already used by a different design.
		"""
		libraryIdentifier = library.NormalizedIdentifier
		if libraryIdentifier in self._libraries:
			raise LibraryExistsInDesignError(library)

		if library._parent is not None:
			raise LibraryRegisteredToForeignDesignError(library)

		self._libraries[libraryIdentifier] = library
		library._parent = self

	def GetLibrary(self, libraryName: str) -> 'Library':
		"""
		Return an (existing) VHDL library object of name ``libraryName``.

		If the requested VHDL library doesn't exist, a new VHDL library with that name will be created.

		:param libraryName: Name of the requested VHDL library.
		:returns:           The VHDL library object.
		"""
		libraryIdentifier = libraryName.lower()
		try:
			return self._libraries[libraryIdentifier]
		except KeyError:
			lib = Library(libraryName, parent=self)
			self._libraries[libraryIdentifier] = lib
			lib._parent = self
			return lib

	# TODO: allow overloaded parameter library to be str?
	def AddDocument(self, document: 'Document', library: 'Library') -> None:
		"""
		Add a document (VHDL source file) to the design and register all embedded design units to the given VHDL library.

		.. rubric:: Algorithm

		1. Iterate all entities in the document

		   1. Check if entity name might exist in target library.
		   2. Add entity to library and update library membership.

		2. Iterate all architectures in the document

		   1. Check if architecture name might exist in target library.
		   2. Add architecture to library and update library membership.

		3. Iterate all packages in the document

		   1. Check if package name might exist in target library.
		   2. Add package to library and update library membership.

		4. Iterate all package bodies in the document

		   1. Check if package body name might exist in target library.
		   2. Add package body to library and update library membership.

		5. Iterate all configurations in the document

		   1. Check if configuration name might exist in target library.
		   2. Add configuration to library and update library membership.

		6. Iterate all contexts in the document

		   1. Check if context name might exist in target library.
		   2. Add context to library and update library membership.

		:param document:                           The VHDL source code file.
		:param library:                            The VHDL library used to register the embedded design units to.
		:raises LibraryNotRegisteredError:         If the given VHDL library is not a library in the design.
		:raises EntityExistsInLibraryError:        If the processed entity's name is already existing in the VHDL library.
		:raises ArchitectureExistsInLibraryError:  If the processed architecture's name is already existing in the VHDL library.
		:raises PackageExistsInLibraryError:       If the processed package's name is already existing in the VHDL library.
		:raises PackageBodyExistsError:            If the processed package body's name is already existing in the VHDL library.
		:raises ConfigurationExistsInLibraryError: If the processed configuration's name is already existing in the VHDL library.
		:raises ContextExistsInLibraryError:       If the processed context's name is already existing in the VHDL library.
		"""
		# FIXME: this checks for the library name, but not the object
		# should the libraries parent be checked too?
		if library._normalizedIdentifier not in self._libraries:
			raise LibraryNotRegisteredError(library)

		self._documents.append(document)
		document._parent = self

		for entityIdentifier, entity in document._entities.items():
			if entityIdentifier in library._entities:
				raise EntityExistsInLibraryError(entity, library)

			library._entities[entityIdentifier] = entity
			entity.Library = library

		for entityIdentifier, architectures in document._architectures.items():
			try:
				architecturesPerEntity = library._architectures[entityIdentifier]
				for architectureIdentifier, architecture in architectures.items():
					if architectureIdentifier in architecturesPerEntity:
						raise ArchitectureExistsInLibraryError(architecture, library._entities[entityIdentifier], library)

					architecturesPerEntity[architectureIdentifier] = architecture
					architecture.Library = library
			except KeyError:
				architecturesPerEntity = document._architectures[entityIdentifier].copy()
				library._architectures[entityIdentifier] = architecturesPerEntity

				for architecture in architecturesPerEntity.values():
					architecture.Library = library

		for packageIdentifier, package in document._packages.items():
			if packageIdentifier in library._packages:
				raise PackageExistsInLibraryError(package, library)

			library._packages[packageIdentifier] = package
			package.Library = library

		for packageBodyIdentifier, packageBody in document._packageBodies.items():
			if packageBodyIdentifier in library._packageBodies:
				raise PackageBodyExistsError(packageBody, library)

			library._packageBodies[packageBodyIdentifier] = packageBody
			packageBody.Library = library

		for configurationIdentifier, configuration in document._configurations.items():
			if configurationIdentifier in library._configurations:
				raise ConfigurationExistsInLibraryError(configuration, library)

			library._configurations[configurationIdentifier] = configuration
			configuration.Library = library

		for contextIdentifier, context in document._contexts.items():
			if contextIdentifier in library._contexts:
				raise ContextExistsInLibraryError(context, library)

			library._contexts[contextIdentifier] = context
			context.Library = library

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		"""
		Iterate all design units in the design.

		A union of :class:`DesignUnitKind` values can be given to filter the returned result for suitable design units.

		.. rubric:: Algorithm

		1. Iterate all VHDL libraries.

		   1. Iterate all contexts in that library.
		   2. Iterate all packages in that library.
		   3. Iterate all package bodies in that library.
		   4. Iterate all entites in that library.
		   5. Iterate all architectures in that library.
		   6. Iterate all configurations in that library.

		:param filter: An enumeration with possibly multiple flags to filter the returned design units.
		:returns:      A generator to iterate all matched design units in the design.

		.. seealso::

		   :meth:`pyVHDLModel.Library.IterateDesignUnits`
		     Iterate all design units in the library.
		   :meth:`pyVHDLModel.Document.IterateDesignUnits`
		     Iterate all design units in the document.
		"""
		for library in self._libraries.values():
			yield from library.IterateDesignUnits(filter)

	def Analyze(self) -> None:
		"""
		Analyze the whole design.

		.. rubric:: Algorithm

		1. Analyze dependencies of design units. |br|
		   This will also yield the design hierarchy and the compiler order.
		2. Analyze dependencies of types and objects.

		.. seealso::

		   :meth:`AnalyzeDependencies`
		     Analyze the dependencies of design units.

		   :meth:`AnalyzeObjects`
		     Analyze the dependencies of types and objects.
		"""
		self.AnalyzeDependencies()
		self.AnalyzeObjects()

	def AnalyzeDependencies(self) -> None:
		"""
		Analyze the dependencies of design units.

		.. rubric:: Algorithm

		1. Create all vertices of the dependency graph by iterating all design units in all libraries. |br|
		   |rarr| :meth:`CreateDependencyGraph`
		2. Create the compile order graph. |br|
		   |rarr| :meth:`CreateCompileOrderGraph`
		3. Index all packages. |br|
		   |rarr| :meth:`IndexPackages`
		4. Index all architectures. |br|
		   |rarr| :meth:`IndexArchitectures`
		5. Link all contexts |br|
		   |rarr| :meth:`LinkContexts`
		6. Link all architectures. |br|
		   |rarr| :meth:`LinkArchitectures`
		7. Link all package bodies. |br|
		   |rarr| :meth:`LinkPackageBodies`
		8. Link all library references. |br|
		   |rarr| :meth:`LinkLibraryReferences`
		9. Link all package references. |br|
		   |rarr| :meth:`LinkPackageReferences`
		10. Link all context references. |br|
		    |rarr| :meth:`LinkContextReferences`
		11. Link all components. |br|
		    |rarr| :meth:`LinkComponents`
		12. Link all instantiations. |br|
		    |rarr| :meth:`LinkInstantiations`
		13. Create the hierarchy graph. |br|
		    |rarr| :meth:`CreateHierarchyGraph`
		14. Compute the compile order. |br|
		    |rarr| :meth:`ComputeCompileOrder`
		"""
		self.CreateDependencyGraph()
		self.CreateCompileOrderGraph()

		self.IndexPackages()
		self.IndexArchitectures()

		self.LinkContexts()
		self.LinkArchitectures()
		self.LinkPackageBodies()
		self.LinkLibraryReferences()
		self.LinkPackageReferences()
		self.LinkContextReferences()

		self.LinkComponents()
		self.LinkInstantiations()
		self.CreateHierarchyGraph()
		self.ComputeCompileOrder()

	def AnalyzeObjects(self) -> None:
		"""
		Analyze the dependencies of types and objects.

		.. rubric:: Algorithm

		1. Index all entities. |br|
		   |rarr| :meth:`IndexEntities`
		2. Index all package bodies. |br|
		   |rarr| :meth:`IndexPackageBodies`
		3. Import objects. |br|
		   |rarr| :meth:`ImportObjects`
		4. Create the type and object graph. |br|
		   |rarr| :meth:`CreateTypeAndObjectGraph`
		"""
		self.IndexEntities()
		self.IndexPackageBodies()

		self.ImportObjects()
		self.CreateTypeAndObjectGraph()

	def CreateDependencyGraph(self) -> None:
		"""
		Create all vertices of the dependency graph by iterating all design units in all libraries.

		This method will purely create a sea of vertices without any linking between vertices. The edges will be created later by other methods. |br|
		See :meth:`AnalyzeDependencies` for these methods and their algorithmic order.

		Each vertex has the following properties:

		* The vertex' ID is the design unit's identifier.
		* The vertex' value references the design unit.
		* A key-value-pair called ``kind`` denotes the vertex's kind as an enumeration value of type :class:`DependencyGraphVertexKind`.
		* A key-value-pair called ``predefined`` denotes if the referenced design unit is a predefined language entity.

		.. rubric:: Algorithm

		1. Iterate all libraries in the design.

		   * Create a vertex for that library and reference the library by the vertex' value field. |br|
		     In return, set the library's :attr:`~pyVHDLModel.Library._dependencyVertex` field to reference the created vertex.

		   1. Iterate all contexts in that library.

		      * Create a vertex for that context and reference the context by the vertex' value field. |br|
		        In return, set the context's :attr:`~pyVHDLModel.DesignUnit.Context._dependencyVertex` field to reference the created vertex.

		   2. Iterate all packages in that library.

		      * Create a vertex for that package and reference the package by the vertex' value field. |br|
		        In return, set the package's :attr:`~pyVHDLModel.DesignUnit.Package._dependencyVertex` field to reference the created vertex.

		   3. Iterate all package bodies in that library.

		      * Create a vertex for that package body and reference the package body by the vertex' value field. |br|
		        In return, set the package body's :attr:`~pyVHDLModel.DesignUnit.PackageBody._dependencyVertex` field to reference the created vertex.

		   4. Iterate all entities in that library.

		      * Create a vertex for that entity and reference the entity by the vertex' value field. |br|
		        In return, set the entity's :attr:`~pyVHDLModel.DesignUnit.Entity._dependencyVertex` field to reference the created vertex.

		   5. Iterate all architectures in that library.

		      * Create a vertex for that architecture and reference the architecture by the vertex' value field. |br|
		        In return, set the architecture's :attr:`~pyVHDLModel.DesignUnit.Architecture._dependencyVertex` field to reference the created vertex.

		   6. Iterate all configurations in that library.

		      * Create a vertex for that configuration and reference the configuration by the vertex' value field. |br|
		        In return, set the configuration's :attr:`~pyVHDLModel.DesignUnit.Configuration._dependencyVertex` field to reference the created vertex.
		"""
		predefinedLibraries = ("std", "ieee")

		for libraryIdentifier, library in self._libraries.items():
			dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}", value=library, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Library
			dependencyVertex["predefined"] = libraryIdentifier in predefinedLibraries
			library._dependencyVertex = dependencyVertex

			for contextIdentifier, context in library._contexts.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{contextIdentifier}", value=context, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Context
				dependencyVertex["predefined"] = context._parent._normalizedIdentifier in predefinedLibraries
				context._dependencyVertex = dependencyVertex

			for packageIdentifier, package in library._packages.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageIdentifier}", value=package, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Package
				dependencyVertex["predefined"] = package._parent._normalizedIdentifier in predefinedLibraries
				package._dependencyVertex = dependencyVertex

			for packageBodyIdentifier, packageBody in library._packageBodies.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageBodyIdentifier}(body)", value=packageBody, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.PackageBody
				dependencyVertex["predefined"] = packageBody._parent._normalizedIdentifier in predefinedLibraries
				packageBody._dependencyVertex = dependencyVertex

			for entityIdentifier, entity in library._entities.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}", value=entity, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Entity
				dependencyVertex["predefined"] = entity._parent._normalizedIdentifier in predefinedLibraries
				entity._dependencyVertex = dependencyVertex

			for entityIdentifier, architectures in library._architectures.items():
				for architectureIdentifier, architecture in architectures.items():
					dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}({architectureIdentifier})", value=architecture, graph=self._dependencyGraph)
					dependencyVertex["kind"] = DependencyGraphVertexKind.Architecture
					dependencyVertex["predefined"] = architecture._parent._normalizedIdentifier in predefinedLibraries
					architecture._dependencyVertex = dependencyVertex

			for configurationIdentifier, configuration in library._configurations.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{configurationIdentifier}", value=configuration, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Configuration
				dependencyVertex["predefined"] = configuration._parent._normalizedIdentifier in predefinedLibraries
				configuration._dependencyVertex = dependencyVertex

	def CreateCompileOrderGraph(self) -> None:
		"""
		Create a compile-order graph with bidirectional references to the dependency graph.

		Add vertices representing a document (VHDL source file) to the dependency graph. Each "document" vertex in dependency graph is copied into the compile-order
		graph and bidirectionally referenced.

		In addition, each vertex of a corresponding design unit in a document is linked to the vertex representing that document to express the design unit in
		document relationship.

		Each added vertex has the following properties:

		* The vertex' ID is the document's filename.
		* The vertex' value references the document.
		* A key-value-pair called ``kind`` denotes the vertex's kind as an enumeration value of type :class:`DependencyGraphVertexKind`.
		* A key-value-pair called ``predefined`` does not exist.

		.. rubric:: Algorithm

		1. Iterate all documents in the design.

		   * Create a vertex for that document and reference the document by the vertex' value field. |br|
		     In return, set the documents's :attr:`~pyVHDLModel.Document._dependencyVertex` field to reference the created vertex.
		   * Copy the vertex from dependency graph to compile-order graph and link both vertices bidirectionally. |br|
		     In addition, set the documents's :attr:`~pyVHDLModel.Document._dependencyVertex` field to reference the copied vertex.

		     * Add a key-value-pair called ``compileOrderVertex`` to the dependency graph's vertex.
		     * Add a key-value-pair called ``dependencyVertex`` to the compiler-order graph's vertex.

		   1. Iterate the documents design units and create an edge from the design unit's corresponding dependency vertex to the documents corresponding
		      dependency vertex. This expresses a "design unit is located in document" relation.

		      * Add a key-value-pair called `kind`` denoting the edge's kind as an enumeration value of type :class:`DependencyGraphEdgeKind`.
		"""
		for document in self._documents:
			dependencyVertex = Vertex(vertexID=document.Path.name, value=document, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Document
			document._dependencyVertex = dependencyVertex

			compilerOrderVertex = dependencyVertex.Copy(
				self._compileOrderGraph,
				copyDict=True,
				linkingKeyToOriginalVertex="dependencyVertex",
				linkingKeyFromOriginalVertex="compileOrderVertex"
			)
			document._compileOrderVertex = compilerOrderVertex

			for designUnit in document._designUnits:
				edge = dependencyVertex.EdgeFromVertex(designUnit._dependencyVertex)
				edge["kind"] = DependencyGraphEdgeKind.SourceFile

	def ImportObjects(self) -> None:
		def _ImportObjects(package: Package) -> None:
			for referencedLibrary in package._referencedPackages.values():
				for referencedPackage in referencedLibrary.values():
					for declaredItem in referencedPackage._declaredItems:
						if isinstance(declaredItem, MultipleNamedEntityMixin):
							for normalizedIdentifier in declaredItem._normalizedIdentifiers:
								package._namespace._elements[normalizedIdentifier] = declaredItem
						elif isinstance(declaredItem, NamedEntityMixin):
							package._namespace._elements[declaredItem._normalizedIdentifier] = declaredItem
						else:
							raise VHDLModelException(f"Unexpected declared item.")

		for libraryName in ("std", "ieee"):
			for package in self.GetLibrary(libraryName).IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_ImportObjects(package)

		for document in self.IterateDocumentsInCompileOrder():
			for package in document.IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_ImportObjects(package)

	def CreateTypeAndObjectGraph(self) -> None:
		def _HandlePackage(package) -> None:
			packagePrefix = f"{package.Library.NormalizedIdentifier}.{package.NormalizedIdentifier}"

			for deferredConstant in package._deferredConstants.values():
				print(f"Deferred Constant: {deferredConstant}")
				deferredConstantVertex = Vertex(
					vertexID=f"{packagePrefix}.{deferredConstant.NormalizedIdentifiers[0]}",
					value=deferredConstant,
					graph=self._objectGraph
				)
				deferredConstantVertex["kind"] = ObjectGraphVertexKind.DeferredConstant
				deferredConstant._objectVertex = deferredConstantVertex

			for constant in package._constants.values():
				print(f"Constant: {constant}")
				constantVertex = Vertex(
					vertexID=f"{packagePrefix}.{constant.NormalizedIdentifiers[0]}",
					value=constant,
					graph=self._objectGraph
				)
				constantVertex["kind"] = ObjectGraphVertexKind.Constant
				constant._objectVertex = constantVertex

			for type in package._types.values():
				print(f"Type: {type}")
				typeVertex = Vertex(
					vertexID=f"{packagePrefix}.{type.NormalizedIdentifier}",
					value=type,
					graph=self._objectGraph
				)
				typeVertex["kind"] = ObjectGraphVertexKind.Type
				type._objectVertex = typeVertex

			for subtype in package._subtypes.values():
				print(f"Subtype: {subtype}")
				subtypeVertex = Vertex(
					vertexID=f"{packagePrefix}.{subtype.NormalizedIdentifier}",
					value=subtype,
					graph=self._objectGraph
				)
				subtypeVertex["kind"] = ObjectGraphVertexKind.Subtype
				subtype._objectVertex = subtypeVertex

			for function in package._functions.values():
				print(f"Function: {function}")
				functionVertex = Vertex(
					vertexID=f"{packagePrefix}.{function.NormalizedIdentifier}",
					value=function,
					graph=self._objectGraph
				)
				functionVertex["kind"] = ObjectGraphVertexKind.Function
				function._objectVertex = functionVertex

			for procedure in package._procedures.values():
				print(f"Procedure: {procedure}")
				procedureVertex = Vertex(
					vertexID=f"{packagePrefix}.{procedure.NormalizedIdentifier}",
					value=procedure,
					graph=self._objectGraph
				)
				procedureVertex["kind"] = ObjectGraphVertexKind.Function
				procedure._objectVertex = procedureVertex

			for signal in package._signals.values():
				print(f"Signal: {signal}")
				signalVertex = Vertex(
					vertexID=f"{packagePrefix}.{signal.NormalizedIdentifiers[0]}",
					value=signal,
					graph=self._objectGraph
				)
				signalVertex["kind"] = ObjectGraphVertexKind.Signal
				signal._objectVertex = signalVertex

		def _LinkSymbolsInExpression(expression, namespace: Namespace, typeVertex: Vertex):
			if isinstance(expression, UnaryExpression):
				_LinkSymbolsInExpression(expression.Operand, namespace, typeVertex)
			elif isinstance(expression, BinaryExpression):
				_LinkSymbolsInExpression(expression.LeftOperand, namespace, typeVertex)
				_LinkSymbolsInExpression(expression.RightOperand, namespace, typeVertex)
			elif isinstance(expression, TernaryExpression):
				pass
			elif isinstance(expression, SimpleObjectOrFunctionCallSymbol):
				obj = namespace.FindObject(expression)
				expression._reference = obj

				edge = obj._objectVertex.EdgeToVertex(typeVertex)
				edge["kind"] = ObjectGraphEdgeKind.ReferenceInExpression
			else:
				pass

		def _LinkItems(package: Package):
			for item in package._declaredItems:
				if isinstance(item, Constant):
					print(f"constant: {item}")
				elif isinstance(item, DeferredConstant):
					print(f"deferred constant: {item}")
				elif isinstance(item, Signal):
					print(f"signal: {item}")
				elif isinstance(item, IntegerType):
					typeNode = item._objectVertex

					_LinkSymbolsInExpression(item.Range.LeftBound, package._namespace, typeNode)
					_LinkSymbolsInExpression(item.Range.RightBound, package._namespace, typeNode)
				# elif isinstance(item, FloatingType):
				# 	print(f"signal: {item}")
				elif isinstance(item, PhysicalType):
					typeNode = item._objectVertex

					_LinkSymbolsInExpression(item.Range.LeftBound, package._namespace, typeNode)
					_LinkSymbolsInExpression(item.Range.RightBound, package._namespace, typeNode)
				elif isinstance(item, ArrayType):
					# Resolve dimensions
					for dimension in item._dimensions:
						subtype = package._namespace.FindSubtype(dimension)
						dimension._reference = subtype

						edge = item._objectVertex.EdgeToVertex(subtype._objectVertex)
						edge["kind"] = ObjectGraphEdgeKind.Subtype

					# Resolve element subtype
					subtype = package._namespace.FindSubtype(item._elementType)
					item._elementType._reference = subtype

					edge = item._objectVertex.EdgeToVertex(subtype._objectVertex)
					edge["kind"] = ObjectGraphEdgeKind.Subtype
				elif isinstance(item, RecordType):
					# Resolve each elements subtype
					for element in item._elements:
						subtype = package._namespace.FindSubtype(element._subtype)
						element._subtype._reference = subtype

						edge = item._objectVertex.EdgeToVertex(subtype._objectVertex)
						edge["kind"] = ObjectGraphEdgeKind.Subtype
				else:
					print(f"not handled: {item}")

		for libraryName in ("std", "ieee"):
			for package in self.GetLibrary(libraryName).IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_HandlePackage(package)
				_LinkItems(package)

		for document in self.IterateDocumentsInCompileOrder():
			for package in document.IterateDesignUnits(filter=DesignUnitKind.Package):  # type: Package
				_HandlePackage(package)
				_LinkItems(package)

	def LinkContexts(self) -> None:
		"""
		Resolves and links all items (library clauses, use clauses and nested context references) in contexts.

		It iterates all contexts in the design. Therefore, the library of the context is used as the working library. By
		default, the working library is implicitly referenced in :data:`_referencedLibraries`. In addition, a new empty
		dictionary is created in :data:`_referencedPackages` and :data:`_referencedContexts` for that working library.

		At first, all library clauses are resolved (a library clause my have multiple library reference symbols). For each
		referenced library an entry in :data:`_referencedLibraries` is generated and new empty dictionaries in
		:data:`_referencedPackages` and :data:`_referencedContexts` for that working library. In addition, a vertex in the
		dependency graph is added for that relationship.

		At second, all use clauses are resolved (a use clause my have multiple package member reference symbols). For each
		referenced package,
		"""
		for context in self.IterateDesignUnits(DesignUnitKind.Context):  # type: Context
			# Create entries in _referenced*** for the current working library under its real name.
			workingLibrary: Library = context.Library
			libraryNormalizedIdentifier = workingLibrary._normalizedIdentifier

			context._referencedLibraries[libraryNormalizedIdentifier] = self._libraries[libraryNormalizedIdentifier]
			context._referencedPackages[libraryNormalizedIdentifier] = {}
			context._referencedContexts[libraryNormalizedIdentifier] = {}

			# Process all library clauses
			for libraryReference in context._libraryReferences:
				# A library clause can have multiple comma-separated references
				for libraryName in libraryReference.Symbols:
					libraryNormalizedIdentifier = libraryName.Name._normalizedIdentifier
					try:
						library = self._libraries[libraryNormalizedIdentifier]
					except KeyError:
						raise ReferencedLibraryNotExistingError(context, libraryName)
						# TODO: add position to these messages

					libraryName.Library = library

					context._referencedLibraries[libraryNormalizedIdentifier] = library
					context._referencedPackages[libraryNormalizedIdentifier] = {}
					context._referencedContexts[libraryNormalizedIdentifier] = {}
					# TODO: warn duplicate library reference

					dependency = context._dependencyVertex.EdgeToVertex(library._dependencyVertex, edgeValue=libraryReference)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

			# Process all use clauses
			for packageReference in context.PackageReferences:
				# A use clause can have multiple comma-separated references
				for symbol in packageReference.Symbols:  # type: PackageReferenceSymbol
					packageName = symbol.Name.Prefix
					libraryName = packageName.Prefix

					libraryNormalizedIdentifier = libraryName._normalizedIdentifier
					packageNormalizedIdentifier = packageName._normalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryNormalizedIdentifier == "work":
						library: Library = context._parent
						libraryNormalizedIdentifier = library._normalizedIdentifier
					elif libraryNormalizedIdentifier not in context._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Use clause references library '{libraryName._identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryNormalizedIdentifier]

					try:
						package = library._packages[packageNormalizedIdentifier]
					except KeyError:
						raise VHDLModelException(f"Package '{packageName._identifier}' not found in {'working ' if libraryName._normalizedIdentifier == 'work' else ''}library '{library._identifier}'.")

					symbol.Package = package

					# TODO: warn duplicate package reference
					context._referencedPackages[libraryNormalizedIdentifier][packageNormalizedIdentifier] = package

					dependency = context._dependencyVertex.EdgeToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(symbol, AllPackageMembersReferenceSymbol):
						pass

					elif isinstance(symbol, PackageMemberReferenceSymbol):
						raise NotImplementedError()
					else:
						raise VHDLModelException()

	def LinkArchitectures(self) -> None:
		"""
		Link all architectures to corresponding entities in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all architecture groups (grouped per entity symbol's name).
		      |rarr| :meth:`pyVHDLModel.Library.LinkArchitectures`

		      * Check if entity symbol's name exists as an entity in this library.

		      1. For each architecture in the same architecture group:

		         * Add architecture to entities architecture dictionary :attr:`pyVHDLModel.DesignUnit.Entity._architectures`.
		         * Assign found entity to architecture's entity symbol :attr:`pyVHDLModel.DesignUnit.Architecture._entity`
		         * Set parent namespace of architecture's namespace to the entitie's namespace.
		         * Add an edge in the dependency graph from the architecture's corresponding dependency vertex to the entity's corresponding dependency vertex.

		.. seealso::

		   :meth:`LinkPackageBodies`
		     Link all package bodies to corresponding packages in all libraries.
		"""
		for library in self._libraries.values():
			library.LinkArchitectures()

	def LinkPackageBodies(self) -> None:
		"""
		Link all package bodies to corresponding packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all package bodies.
		      |rarr| :meth:`pyVHDLModel.Library.LinkPackageBodies`

		      * Check if package body symbol's name exists as a package in this library.
		      * Add package body to package :attr:`pyVHDLModel.DesignUnit.Package._packageBody`.
		      * Assign found package to package body's package symbol :attr:`pyVHDLModel.DesignUnit.PackageBody._package`
		      * Set parent namespace of package body's namespace to the package's namespace.
		      * Add an edge in the dependency graph from the package body's corresponding dependency vertex to the package's corresponding dependency vertex.

		.. seealso::

		   :meth:`LinkArchitectures`
		     Link all architectures to corresponding entities in all libraries.
		"""
		for library in self._libraries.values():
			library.LinkPackageBodies()

	def LinkLibraryReferences(self) -> None:
		DEFAULT_LIBRARIES = ("std",)

		for designUnit in self.IterateDesignUnits(DesignUnitKind.WithContext):
			# All primary units supporting a context, have at least one library implicitly referenced
			if isinstance(designUnit, PrimaryUnit):
				for libraryIdentifier in DEFAULT_LIBRARIES:
					referencedLibrary = self._libraries[libraryIdentifier]
					designUnit._referencedLibraries[libraryIdentifier] = referencedLibrary
					designUnit._referencedPackages[libraryIdentifier] = {}
					designUnit._referencedContexts[libraryIdentifier] = {}
					# TODO: catch KeyError on self._libraries[libName]
					# TODO: warn duplicate library reference

					dependency = designUnit._dependencyVertex.EdgeToVertex(referencedLibrary._dependencyVertex)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

				workingLibrary: Library = designUnit.Library
				libraryIdentifier = workingLibrary.NormalizedIdentifier
				referencedLibrary = self._libraries[libraryIdentifier]


				designUnit._referencedLibraries[libraryIdentifier] = referencedLibrary
				designUnit._referencedPackages[libraryIdentifier] = {}
				designUnit._referencedContexts[libraryIdentifier] = {}

				dependency = designUnit._dependencyVertex.EdgeToVertex(referencedLibrary._dependencyVertex)
				dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

			# All secondary units inherit referenced libraries from their primary units.
			else:
				if isinstance(designUnit, Architecture):
					referencedLibraries = designUnit.Entity.Entity._referencedLibraries
				elif isinstance(designUnit, PackageBody):
					referencedLibraries = designUnit.Package.Package._referencedLibraries
				else:
					raise VHDLModelException()

				for libraryIdentifier, library in referencedLibraries.items():
					designUnit._referencedLibraries[libraryIdentifier] = library

			for libraryReference in designUnit._libraryReferences:
				# A library clause can have multiple comma-separated references
				for librarySymbol in libraryReference.Symbols:
					libraryIdentifier = librarySymbol.Name.NormalizedIdentifier
					try:
						library = self._libraries[libraryIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Library '{librarySymbol.Name.Identifier}' referenced by library clause of design unit '{designUnit.Identifier}' doesn't exist in design.")
						ex.add_note(f"""Known libraries: '{"', '".join(library for library in self._libraries)}'""")
						raise ex

					librarySymbol.Library = library
					designUnit._referencedLibraries[libraryIdentifier] = library
					designUnit._referencedPackages[libraryIdentifier] = {}
					designUnit._referencedContexts[libraryIdentifier] = {}
					# TODO: warn duplicate library reference

					dependency = designUnit._dependencyVertex.EdgeToVertex(library._dependencyVertex, edgeValue=libraryReference)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

	def LinkPackageReferences(self) -> None:
		DEFAULT_PACKAGES = (
			("std", ("standard",)),
		)

		for designUnit in self.IterateDesignUnits(DesignUnitKind.WithContext):
			# All primary units supporting a context, have at least one package implicitly referenced
			if isinstance(designUnit, PrimaryUnit):
				if designUnit.Library.NormalizedIdentifier != "std" and \
					designUnit.NormalizedIdentifier != "standard":
					for lib in DEFAULT_PACKAGES:
						if lib[0] not in designUnit._referencedLibraries:
							raise VHDLModelException()
						for pack in lib[1]:
							referencedPackage = self._libraries[lib[0]]._packages[pack]
							designUnit._referencedPackages[lib[0]][pack] = referencedPackage
							# TODO: catch KeyError on self._libraries[lib[0]]._packages[pack]
							# TODO: warn duplicate package reference

							dependency = designUnit._dependencyVertex.EdgeToVertex(referencedPackage._dependencyVertex)
							dependency["kind"] = DependencyGraphEdgeKind.UseClause

			# All secondary units inherit referenced packages from their primary units.
			else:
				if isinstance(designUnit, Architecture):
					referencedPackages = designUnit.Entity.Entity._referencedPackages
				elif isinstance(designUnit, PackageBody):
					referencedPackages = designUnit.Package.Package._referencedPackages
				else:
					raise VHDLModelException()

				for packageIdentifier, package in referencedPackages.items():
					designUnit._referencedPackages[packageIdentifier] = package

			for packageReference in designUnit.PackageReferences:
				# A use clause can have multiple comma-separated references
				for packageMemberSymbol in packageReference.Symbols:
					packageName = packageMemberSymbol.Name.Prefix
					libraryName = packageName.Prefix

					libraryIdentifier = libraryName.NormalizedIdentifier
					packageIdentifier = packageName.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						library: Library = designUnit.Library
						libraryIdentifier = library.NormalizedIdentifier
					elif libraryIdentifier not in designUnit._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Use clause references library '{libraryName.Identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryIdentifier]

					try:
						package = library._packages[packageIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Package '{packageName.Identifier}' not found in {'working ' if libraryName.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")
						ex.add_note(f"Caused in design unit '{designUnit}' in file '{designUnit.Document}'.")
						raise ex

					packageMemberSymbol.Package = package

					# TODO: warn duplicate package reference
					designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

					dependency = designUnit._dependencyVertex.EdgeToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(packageMemberSymbol, AllPackageMembersReferenceSymbol):
						for componentIdentifier, component in package._components.items():
							designUnit._namespace._elements[componentIdentifier] = component

					elif isinstance(packageMemberSymbol, PackageMemberReferenceSymbol):
						raise NotImplementedError()
					else:
						raise VHDLModelException()

	def LinkContextReferences(self) -> None:
		for designUnit in self.IterateDesignUnits():
			for contextReference in designUnit._contextReferences:
				# A context reference can have multiple comma-separated references
				for contextSymbol in contextReference.Symbols:
					libraryName = contextSymbol.Name.Prefix

					libraryIdentifier = libraryName.NormalizedIdentifier
					contextIdentifier = contextSymbol.Name.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						referencedLibrary = designUnit.Library
						libraryIdentifier = referencedLibrary.NormalizedIdentifier
					elif libraryIdentifier not in designUnit._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Context reference references library '{libraryName.Identifier}', which was not referenced by a library clause.")
					else:
						referencedLibrary = self._libraries[libraryIdentifier]

					try:
						referencedContext = referencedLibrary._contexts[contextIdentifier]
					except KeyError:
						raise VHDLModelException(f"Context '{contextSymbol.Name.Identifier}' not found in {'working ' if libraryName.NormalizedIdentifier == 'work' else ''}library '{referencedLibrary.Identifier}'.")

					contextSymbol.Package = referencedContext

					# TODO: warn duplicate referencedContext reference
					designUnit._referencedContexts[libraryIdentifier][contextIdentifier] = referencedContext

					dependency = designUnit._dependencyVertex.EdgeToVertex(referencedContext._dependencyVertex, edgeValue=contextReference)
					dependency["kind"] = DependencyGraphEdgeKind.ContextReference

		for vertex in self._dependencyGraph.IterateTopologically():
			if vertex["kind"] is DependencyGraphVertexKind.Context:
				context: Context = vertex.Value
				for designUnitVertex in vertex.IteratePredecessorVertices():
					designUnit: DesignUnit = designUnitVertex.Value
					for libraryIdentifier, library in context._referencedLibraries.items():
						# if libraryIdentifier in designUnit._referencedLibraries:
						# 	raise VHDLModelException(f"Referenced library '{library.Identifier}' already exists in references for design unit '{designUnit.Identifier}'.")

						designUnit._referencedLibraries[libraryIdentifier] = library
						designUnit._referencedPackages[libraryIdentifier] = {}

					for libraryIdentifier, packages in context._referencedPackages.items():
						for packageIdentifier, package in packages.items():
							if packageIdentifier in designUnit._referencedPackages:
								raise VHDLModelException(f"Referenced package '{package.Identifier}' already exists in references for design unit '{designUnit.Identifier}'.")

							designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

	def LinkComponents(self) -> None:
		for package in self.IterateDesignUnits(DesignUnitKind.Package):  # type: Package
			library = package._parent
			for component in package._components.values():
				try:
					entity = library._entities[component.NormalizedIdentifier]
				except KeyError:
					print(f"Entity '{component.Identifier}' not found for component '{component.Identifier}' in library '{library.Identifier}'.")

				component.Entity = entity

				# QUESTION: Add link in dependency graph as dashed line from component to entity?
				#           Currently, component has no _dependencyVertex field

	def LinkInstantiations(self) -> None:
		for architecture in self.IterateDesignUnits(DesignUnitKind.Architecture):  # type: Architecture
			for instance in architecture.IterateInstantiations():
				if isinstance(instance, EntityInstantiation):
					libraryName = instance.Entity.Name.Prefix
					libraryIdentifier = libraryName.Identifier
					normalizedLibraryIdentifier = libraryName.NormalizedIdentifier
					if normalizedLibraryIdentifier == "work":
						libraryIdentifier = architecture.Library.Identifier
						normalizedLibraryIdentifier = architecture.Library.NormalizedIdentifier
					elif normalizedLibraryIdentifier not in architecture._referencedLibraries:
						ex = VHDLModelException(f"Referenced library '{libraryIdentifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Prefix.Identifier}.{instance.Entity.Identifier}' not found in architecture '{architecture!r}'.")
						ex.add_note(f"Add a library reference to the architecture or entity using a library clause like: 'library {libraryIdentifier};'.")
						raise ex

					try:
						library = self._libraries[normalizedLibraryIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Referenced library '{libraryIdentifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Prefix.Identifier}.{instance.Entity.Identifier}' not found in design.")
						ex.add_note(f"No design units were parsed into library '{libraryIdentifier}'. Thus it doesn't exist in design.")
						raise ex

					try:
						entity = library._entities[instance.Entity.Name.NormalizedIdentifier]
					except KeyError:
						ex = VHDLModelException(f"Referenced entity '{instance.Entity.Name.Identifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Name.Prefix.Identifier}.{instance.Entity.Name.Identifier}' not found in {'working ' if instance.Entity.Name.Prefix.NormalizedIdentifier == 'work' else ''}library '{libraryIdentifier}'.")
						libs = [library.Identifier for library in self._libraries.values() for entityIdentifier in library._entities.keys() if entityIdentifier == instance.Entity.Name.NormalizedIdentifier]
						if libs:
							ex.add_note(f"Found entity '{instance.Entity!s}' in other libraries: {', '.join(libs)}")
						raise ex

					instance.Entity.Entity = entity

					dependency = architecture._dependencyVertex.EdgeToVertex(entity._dependencyVertex, edgeValue=instance)
					dependency["kind"] = DependencyGraphEdgeKind.EntityInstantiation

				elif isinstance(instance, ComponentInstantiation):
					component = architecture._namespace.FindComponent(instance.Component)

					instance.Component.Component = component

					dependency = architecture._dependencyVertex.EdgeToVertex(component.Entity._dependencyVertex, edgeValue=instance)
					dependency["kind"] = DependencyGraphEdgeKind.ComponentInstantiation

				elif isinstance(instance, ConfigurationInstantiation):
					# pass
					print(instance.Label, instance.Configuration)

	def IndexPackages(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexPackages`

		      * Index all declared items in that package. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.Package.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackageBodies`
		     Index all declared items in all package bodies in all libraries.
		   :meth:`IndexEntities`
		     Index all declared items in all entities in all libraries.
		   :meth:`IndexArchitectures`
		     Index all declared items in all architectures in all libraries.
		"""
		for library in self._libraries.values():
			library.IndexPackages()

	def IndexPackageBodies(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexPackageBodies`

		      * Index all declared items in that package body. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.PackageBody.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in all packages in all libraries.
		   :meth:`IndexEntities`
		     Index all declared items in all entities in all libraries.
		   :meth:`IndexArchitectures`
		     Index all declared items in all architectures in all libraries.
		"""
		for library in self._libraries.values():
			library.IndexPackageBodies()

	def IndexEntities(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexEntities`

		      * Index all declared items in that entity. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.Entity.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in all packages in all libraries.
		   :meth:`IndexPackageBodies`
		     Index all declared items in all package bodies in all libraries.
		   :meth:`IndexArchitectures`
		     Index all declared items in all architectures in all libraries.
		"""
		for library in self._libraries.values():
			library.IndexEntities()

	def IndexArchitectures(self) -> None:
		"""
		Index all declared items in all packages in all libraries.

		.. rubric:: Algorithm

		1. Iterate all libraries:

		   1. Iterate all packages |br|
		      |rarr| :meth:`pyVHDLModel.Library.IndexArchitectures`

		      * Index all declared items in that architecture. |br|
		        |rarr| :meth:`pyVHDLModel.DesignUnit.Architecture.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in all packages in all libraries.
		   :meth:`IndexPackageBodies`
		     Index all declared items in all package bodies in all libraries.
		   :meth:`IndexEntities`
		     Index all declared items in all entities in all libraries.
		"""
		for library in self._libraries.values():
			library.IndexArchitectures()

	def CreateHierarchyGraph(self) -> None:
		"""
		Create the hierarchy graph from dependency graph.

		.. rubric:: Algorithm

		1. Iterate all vertices corresponding to entities and architectures in the dependency graph:

		   * Copy these vertices to the hierarchy graph and create a bidirectional linking. |br|
		     In addition, set the referenced design unit's :attr:`~pyVHDLModel.Document._hierarchyVertex` field to reference the copied vertex.

		     * Add a key-value-pair called ``hierarchyVertex`` to the dependency graph's vertex.
		     * Add a key-value-pair called ``dependencyVertex`` to the hierarchy graph's vertex.

		2. Iterate all architectures ...

		   .. todo:: Design::CreateHierarchyGraph describe algorithm

		   1. Iterate all outbound edges

		      .. todo:: Design::CreateHierarchyGraph describe algorithm
		"""
		# Copy all entity and architecture vertices from dependency graph to hierarchy graph and double-link them
		entityArchitectureFilter = lambda v: v["kind"] in DependencyGraphVertexKind.Entity | DependencyGraphVertexKind.Architecture
		for vertex in self._dependencyGraph.IterateVertices(predicate=entityArchitectureFilter):
			hierarchyVertex = vertex.Copy(self._hierarchyGraph, copyDict=True, linkingKeyToOriginalVertex="dependencyVertex", linkingKeyFromOriginalVertex="hierarchyVertex")
			vertex.Value._hierarchyVertex = hierarchyVertex

		# Copy implementation edges from
		for hierarchyArchitectureVertex in self._hierarchyGraph.IterateVertices(predicate=lambda v: v["kind"] is DependencyGraphVertexKind.Architecture):
			for dependencyEdge in hierarchyArchitectureVertex["dependencyVertex"].IterateOutboundEdges():
				kind: DependencyGraphEdgeKind = dependencyEdge["kind"]
				if DependencyGraphEdgeKind.Implementation in kind:
					hierarchyDestinationVertex = dependencyEdge.Destination["hierarchyVertex"]
					newEdge = hierarchyArchitectureVertex.EdgeFromVertex(hierarchyDestinationVertex)
				elif DependencyGraphEdgeKind.Instantiation in kind:
					hierarchyDestinationVertex = dependencyEdge.Destination["hierarchyVertex"]

					# FIXME: avoid parallel edges, to graph can be converted to a tree until "real" hierarchy is computed (unrole generics and blocks)
					if hierarchyArchitectureVertex.HasEdgeToDestination(hierarchyDestinationVertex):
						continue

					newEdge = hierarchyArchitectureVertex.EdgeToVertex(hierarchyDestinationVertex)
				else:
					continue

				newEdge["kind"] = kind

	def ComputeCompileOrder(self) -> None:
		def predicate(edge: Edge) -> bool:
			return (
				DependencyGraphEdgeKind.Implementation in edge["kind"] or
				DependencyGraphEdgeKind.Instantiation in edge["kind"] or
				DependencyGraphEdgeKind.UseClause in edge["kind"] or
				DependencyGraphEdgeKind.ContextReference in edge["kind"]
			) and edge.Destination["predefined"] is False

		for edge in self._dependencyGraph.IterateEdges(predicate=predicate):
			sourceDocument:      Document = edge.Source.Value.Document
			destinationDocument: Document = edge.Destination.Value.Document

			sourceVertex =      sourceDocument._compileOrderVertex
			destinationVertex = destinationDocument._compileOrderVertex

			# Don't add self-edges
			if sourceVertex is destinationVertex:
				continue
			# Don't add parallel edges
			elif sourceVertex.HasEdgeToDestination(destinationVertex):
				continue

			e = sourceVertex.EdgeToVertex(destinationVertex)
			e["kind"] = DependencyGraphEdgeKind.CompileOrder

			e = sourceVertex["dependencyVertex"].EdgeToVertex(destinationVertex["dependencyVertex"])
			e["kind"] = DependencyGraphEdgeKind.CompileOrder

	def IterateDocumentsInCompileOrder(self) -> Generator['Document', None, None]:
		"""
		Iterate all document in compile-order.

		.. rubric:: Algorithm

		* Check if compile-order graph was populated with vertices and its vertices are linked by edges.

		1. Iterate compile-order graph in topological order. |br|
		   :meth:`pyTooling.Graph.Graph.IterateTopologically`

		   * yield the compiler-order vertex' referenced document.

		:returns:                   A generator to iterate all documents in compile-order in the design.
		:raises VHDLModelException: If compile-order was not computed.

		.. seealso::

		   .. todo:: missing text

		      :meth:`pyVHDLModel.Design.ComputeCompileOrder`

		"""
		if self._compileOrderGraph.EdgeCount < self._compileOrderGraph.VertexCount - 1:
			raise VHDLModelException(f"Compile order is not yet computed from dependency graph.")

		for compileOrderNode in self._compileOrderGraph.IterateTopologically():
			yield compileOrderNode.Value

	def GetUnusedDesignUnits(self) -> List[DesignUnit]:
		raise NotImplementedError()

	def __repr__(self) -> str:
		"""
		Formats a representation of the design.

		**Format:** ``Document: 'my_design'``

		:returns: String representation of the design.
		"""
		return f"Design: {self._name}"

	__str__ = __repr__


@export
class Library(ModelEntity, NamedEntityMixin):
	"""A ``Library`` represents a VHDL library. It contains all *primary* and *secondary* design units."""

	_contexts:       Dict[str, Context]                  #: Dictionary of all contexts defined in a library.
	_configurations: Dict[str, Configuration]            #: Dictionary of all configurations defined in a library.
	_entities:       Dict[str, Entity]                   #: Dictionary of all entities defined in a library.
	_architectures:  Dict[str, Dict[str, Architecture]]  #: Dictionary of all architectures defined in a library.
	_packages:       Dict[str, Package]                  #: Dictionary of all packages defined in a library.
	_packageBodies:  Dict[str, PackageBody]              #: Dictionary of all package bodies defined in a library.

	_dependencyVertex: Vertex[None, None, str, Union['Library', DesignUnit], None, None, None, None, None, None, None, None, None, None, None, None, None]  #: Reference to the vertex in the dependency graph representing the library. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateDependencyGraph`.

	def __init__(self, identifier: str, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)

		self._contexts =        {}
		self._configurations =  {}
		self._entities =        {}
		self._architectures =   {}
		self._packages =        {}
		self._packageBodies =   {}

		self._dependencyVertex = None

	@readonly
	def Contexts(self) -> Dict[str, Context]:
		"""Returns a list of all context declarations declared in this library."""
		return self._contexts

	@readonly
	def Configurations(self) -> Dict[str, Configuration]:
		"""Returns a list of all configuration declarations declared in this library."""
		return self._configurations

	@readonly
	def Entities(self) -> Dict[str, Entity]:
		"""Returns a list of all entity declarations declared in this library."""
		return self._entities

	@readonly
	def Architectures(self) -> Dict[str, Dict[str, Architecture]]:
		"""Returns a list of all architectures declarations declared in this library."""
		return self._architectures

	@readonly
	def Packages(self) -> Dict[str, Package]:
		"""Returns a list of all package declarations declared in this library."""
		return self._packages

	@readonly
	def PackageBodies(self) -> Dict[str, PackageBody]:
		"""Returns a list of all package body declarations declared in this library."""
		return self._packageBodies

	@readonly
	def DependencyVertex(self) -> Vertex:
		"""
		Read-only property to access the corresponding dependency vertex (:attr:`_dependencyVertex`).

		The dependency vertex references this library by its value field.

		:returns: The corresponding dependency vertex.
		"""
		return self._dependencyVertex

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		"""
		Iterate all design units in the library.

		A union of :class:`DesignUnitKind` values can be given to filter the returned result for suitable design units.

		.. rubric:: Algorithm

		1. Iterate all contexts in that library.
		2. Iterate all packages in that library.
		3. Iterate all package bodies in that library.
		4. Iterate all entites in that library.
		5. Iterate all architectures in that library.
		6. Iterate all configurations in that library.

		:param filter: An enumeration with possibly multiple flags to filter the returned design units.
		:returns:      A generator to iterate all matched design units in the library.

		.. seealso::

		   :meth:`pyVHDLModel.Design.IterateDesignUnits`
		     Iterate all design units in the design.
		   :meth:`pyVHDLModel.Document.IterateDesignUnits`
		     Iterate all design units in the document.
		"""
		if DesignUnitKind.Context in filter:
			for context in self._contexts.values():
				yield context

		if DesignUnitKind.Package in filter:
			for package in self._packages.values():
				yield package

		if DesignUnitKind.PackageBody in filter:
			for packageBody in self._packageBodies.values():
				yield packageBody

		if DesignUnitKind.Entity in filter:
			for entity in self._entities.values():
				yield entity

		if DesignUnitKind.Architecture in filter:
			for architectures in self._architectures.values():
				for architecture in architectures.values():
					yield architecture

		if DesignUnitKind.Configuration in filter:
			for configuration in self._configurations.values():
				yield configuration

		# for verificationProperty in self._verificationUnits.values():
		# 	yield verificationProperty
		# for verificationUnit in self._verificationProperties.values():
		# 	yield entity
		# for verificationMode in self._verificationModes.values():
		# 	yield verificationMode

	def LinkArchitectures(self) -> None:
		"""
		Link all architectures to corresponding entities.

		.. rubric:: Algorithm

		1. Iterate all architecture groups (grouped per entity symbol's name).

		   * Check if entity symbol's name exists as an entity in this library.

		   1. For each architecture in the same architecture group:

		      * Add architecture to entities architecture dictionary :attr:`pyVHDLModel.DesignUnit.Entity._architectures`.
		      * Assign found entity to architecture's entity symbol :attr:`pyVHDLModel.DesignUnit.Architecture._entity`
		      * Set parent namespace of architecture's namespace to the entitie's namespace.
		      * Add an edge in the dependency graph from the architecture's corresponding dependency vertex to the entity's corresponding dependency vertex.

		:raises VHDLModelException: If entity name doesn't exist.
		:raises VHDLModelException: If architecture name already exists for entity.

		.. seealso::

		   :meth:`LinkPackageBodies`
		     Link all package bodies to corresponding packages.
		"""
		for entityName, architecturesPerEntity in self._architectures.items():
			if entityName not in self._entities:
				architectureNames = "', '".join(architecturesPerEntity.keys())
				raise VHDLModelException(f"Entity '{entityName}' referenced by architecture(s) '{architectureNames}' doesn't exist in library '{self._identifier}'.")
			# TODO: search in other libraries to find that entity.
			# TODO: add code position

			entity = self._entities[entityName]
			for architecture in architecturesPerEntity.values():
				if architecture._normalizedIdentifier in entity._architectures:
					raise VHDLModelException(f"Architecture '{architecture._identifier}' already exists for entity '{entity._identifier}'.")
				# TODO: add code position of existing and current

				entity._architectures[architecture._normalizedIdentifier] = architecture
				architecture._entity.Entity = entity
				architecture._namespace._parentNamespace = entity._namespace

				# add "architecture -> entity" relation in dependency graph
				dependency = architecture._dependencyVertex.EdgeToVertex(entity._dependencyVertex)
				dependency["kind"] = DependencyGraphEdgeKind.EntityImplementation

	def LinkPackageBodies(self) -> None:
		"""
		Link all package bodies to corresponding packages.

		.. rubric:: Algorithm

		1. Iterate all package bodies.

		   * Check if package body symbol's name exists as a package in this library.
		   * Add package body to package :attr:`pyVHDLModel.DesignUnit.Package._packageBody`.
		   * Assign found package to package body's package symbol :attr:`pyVHDLModel.DesignUnit.PackageBody._package`
		   * Set parent namespace of package body's namespace to the package's namespace.
		   * Add an edge in the dependency graph from the package body's corresponding dependency vertex to the package's corresponding dependency vertex.

		:raises VHDLModelException: If package name doesn't exist.

		.. seealso::

		   :meth:`LinkArchitectures`
		     Link all architectures to corresponding entities.
		"""
		for packageBodyName, packageBody in self._packageBodies.items():
			if packageBodyName not in self._packages:
				raise VHDLModelException(f"Package '{packageBodyName}' referenced by package body '{packageBodyName}' doesn't exist in library '{self._identifier}'.")

			package = self._packages[packageBodyName]
			package._packageBody = packageBody    # TODO: add warning if package had already a body, which is now replaced
			packageBody._package.Package = package
			packageBody._namespace._parentNamespace = package._namespace

			# add "package body -> package" relation in dependency graph
			dependency = packageBody._dependencyVertex.EdgeToVertex(package._dependencyVertex)
			dependency["kind"] = DependencyGraphEdgeKind.PackageImplementation

	def IndexPackages(self) -> None:
		"""
		Index declared items in all packages.

		.. rubric:: Algorithm

		1. Iterate all packages:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.Package.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackageBodies`
		     Index all declared items in a package body.
		   :meth:`IndexEntities`
		     Index all declared items in an entity.
		   :meth:`IndexArchitectures`
		     Index all declared items in an architecture.
		"""
		for package in self._packages.values():
			if isinstance(package, Package):
				package.IndexDeclaredItems()

	def IndexPackageBodies(self) -> None:
		"""
		Index declared items in all package bodies.

		.. rubric:: Algorithm

		1. Iterate all package bodies:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.PackageBody.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in a package.
		   :meth:`IndexEntities`
		     Index all declared items in an entity.
		   :meth:`IndexArchitectures`
		     Index all declared items in an architecture.
		"""
		for packageBody in self._packageBodies.values():
			packageBody.IndexDeclaredItems()

	def IndexEntities(self) -> None:
		"""
		Index declared items in all entities.

		.. rubric:: Algorithm

		1. Iterate all entities:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.Entity.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in a package.
		   :meth:`IndexPackageBodies`
		     Index all declared items in a package body.
		   :meth:`IndexArchitectures`
		     Index all declared items in an architecture.
		"""
		for entity in self._entities.values():
			entity.IndexDeclaredItems()

	def IndexArchitectures(self) -> None:
		"""
		Index declared items in all architectures.

		.. rubric:: Algorithm

		1. Iterate all architectures:

		   * Index all declared items. |br|
		     |rarr| :meth:`pyVHDLModel.DesignUnit.Architecture.IndexDeclaredItems`

		.. seealso::

		   :meth:`IndexPackages`
		     Index all declared items in a package.
		   :meth:`IndexPackageBodies`
		     Index all declared items in a package body.
		   :meth:`IndexEntities`
		     Index all declared items in an entity.
		"""
		for architectures in self._architectures.values():
			for architecture in architectures.values():
				architecture.IndexDeclaredItems()
				architecture.IndexStatements()

	def __repr__(self) -> str:
		"""
		Formats a representation of the library.

		**Format:** ``Library: 'my_library'``

		:returns: String representation of the library.
		"""
		return f"Library: '{self._identifier}'"

	__str__ = __repr__


@export
class Document(ModelEntity, DocumentedEntityMixin):
	"""A ``Document`` represents a sourcefile. It contains *primary* and *secondary* design units."""

	_path:                   Path                                #: path to the document. ``None`` if virtual document.
	_designUnits:            List[DesignUnit]                    #: List of all design units defined in a document.
	_contexts:               Dict[str, Context]                  #: Dictionary of all contexts defined in a document.
	_configurations:         Dict[str, Configuration]            #: Dictionary of all configurations defined in a document.
	_entities:               Dict[str, Entity]                   #: Dictionary of all entities defined in a document.
	_architectures:          Dict[str, Dict[str, Architecture]]  #: Dictionary of all architectures defined in a document.
	_packages:               Dict[str, Package]                  #: Dictionary of all packages defined in a document.
	_packageBodies:          Dict[str, PackageBody]              #: Dictionary of all package bodies defined in a document.
	_verificationUnits:      Dict[str, VerificationUnit]         #: Dictionary of all PSL verification units defined in a document.
	_verificationProperties: Dict[str, VerificationProperty]     #: Dictionary of all PSL verification properties defined in a document.
	_verificationModes:      Dict[str, VerificationMode]         #: Dictionary of all PSL verification modes defined in a document.

	_dependencyVertex:       Vertex[None, None, None, 'Document', None, None, None, None, None, None, None, None, None, None, None, None, None]  #: Reference to the vertex in the dependency graph representing the document. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateCompileOrderGraph`.
	_compileOrderVertex:     Vertex[None, None, None, 'Document', None, None, None, None, None, None, None, None, None, None, None, None, None]  #: Reference to the vertex in the compile-order graph representing the document. |br| This reference is set by :meth:`~pyVHDLModel.Design.CreateCompileOrderGraph`.

	def __init__(self, path: Path, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		DocumentedEntityMixin.__init__(self, documentation)

		self._path =                   path
		self._designUnits =            []
		self._contexts =               {}
		self._configurations =         {}
		self._entities =               {}
		self._architectures =          {}
		self._packages =               {}
		self._packageBodies =          {}
		self._verificationUnits =      {}
		self._verificationProperties = {}
		self._verificationModes =      {}

		self._dependencyVertex =   None
		self._compileOrderVertex = None

	def _AddEntity(self, item: Entity) -> None:
		"""
		Add an entity to the document's lists of design units.

		:param item:                Entity object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.Entity`.
		:raises VHDLModelException: If entity name already exists in document.
		"""
		if not isinstance(item, Entity):
			ex = TypeError(f"Parameter 'item' is not of type 'Entity'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._entities:
			# TODO: use a more specific exception
			raise VHDLModelException(f"An entity '{item._identifier}' already exists in this document.")

		self._entities[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddArchitecture(self, item: Architecture) -> None:
		"""
		Add an architecture to the document's lists of design units.

		:param item:                Architecture object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.Architecture`.
		:raises VHDLModelException: If architecture name already exists for the referenced entity name in document.
		"""
		if not isinstance(item, Architecture):
			ex = TypeError(f"Parameter 'item' is not of type 'Architecture'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		entity = item._entity.Name
		entityIdentifier = entity._normalizedIdentifier
		try:
			architectures = self._architectures[entityIdentifier]
			if item._normalizedIdentifier in architectures:
				# TODO: use a more specific exception
				# FIXME: this is allowed and should be a warning or a strict mode.
				raise VHDLModelException(f"An architecture '{item._identifier}' for entity '{entity._identifier}' already exists in this document.")

			architectures[item.Identifier] = item
		except KeyError:
			self._architectures[entityIdentifier] = {item._identifier: item}

		self._designUnits.append(item)
		item._document = self

	def _AddPackage(self, item: Package) -> None:
		"""
		Add a package to the document's lists of design units.

		:param item:                Package object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.Package`.
		:raises VHDLModelException: If package name already exists in document.
		"""
		if not isinstance(item, (Package, PackageInstantiation)):
			ex = TypeError(f"Parameter 'item' is not of type 'Package' or 'PackageInstantiation'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._packages:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A package '{item._identifier}' already exists in this document.")

		self._packages[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddPackageBody(self, item: PackageBody) -> None:
		"""
		Add a package body to the document's lists of design units.

		:param item:                Package body object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.PackageBody`.
		:raises VHDLModelException: If package body name already exists in document.
		"""
		if not isinstance(item, PackageBody):
			ex = TypeError(f"Parameter 'item' is not of type 'PackageBody'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._packageBodies:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A package body '{item._identifier}' already exists in this document.")

		self._packageBodies[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddContext(self, item: Context) -> None:
		"""
		Add a context to the document's lists of design units.

		:param item:                Context object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.Context`.
		:raises VHDLModelException: If context name already exists in document.
		"""
		if not isinstance(item, Context):
			ex = TypeError(f"Parameter 'item' is not of type 'Context'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._contexts:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A context '{item._identifier}' already exists in this document.")

		self._contexts[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddConfiguration(self, item: Configuration) -> None:
		"""
		Add a configuration to the document's lists of design units.

		:param item:                Configuration object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.Configuration`.
		:raises VHDLModelException: If configuration name already exists in document.
		"""
		if not isinstance(item, Configuration):
			ex = TypeError(f"Parameter 'item' is not of type 'Configuration'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._configurations:
			# TODO: use a more specific exception
			raise VHDLModelException(f"A configuration '{item._identifier}' already exists in this document.")

		self._configurations[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddVerificationUnit(self, item: VerificationUnit) -> None:
		if not isinstance(item, VerificationUnit):
			ex = TypeError(f"Parameter 'item' is not of type 'VerificationUnit'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item._normalizedIdentifier
		if identifier in self._verificationUnits:
			raise ValueError(f"A verification unit '{item._identifier}' already exists in this document.")

		self._verificationUnits[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddVerificationProperty(self, item: VerificationProperty) -> None:
		if not isinstance(item, VerificationProperty):
			ex = TypeError(f"Parameter 'item' is not of type 'VerificationProperty'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationProperties:
			raise ValueError(f"A verification property '{item.Identifier}' already exists in this document.")

		self._verificationProperties[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddVerificationMode(self, item: VerificationMode) -> None:
		if not isinstance(item, VerificationMode):
			ex = TypeError(f"Parameter 'item' is not of type 'VerificationMode'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationModes:
			raise ValueError(f"A verification mode '{item.Identifier}' already exists in this document.")

		self._verificationModes[identifier] = item
		self._designUnits.append(item)
		item._document = self

	def _AddDesignUnit(self, item: DesignUnit) -> None:
		"""
		Add a design unit to the document's lists of design units.

		:param item:                Configuration object to be added to the document.
		:raises TypeError:          If parameter 'item' is not of type :class:`~pyVHDLModel.DesignUnits.DesignUnit`.
		:raises ValueError:         If parameter 'item' is an unknown :class:`~pyVHDLModel.DesignUnits.DesignUnit`.
		:raises VHDLModelException: If configuration name already exists in document.
		"""
		if not isinstance(item, DesignUnit):
			ex = TypeError(f"Parameter 'item' is not of type 'DesignUnit'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

		if isinstance(item, Entity):
			self._AddEntity(item)
		elif isinstance(item, Architecture):
			self._AddArchitecture(item)
		elif isinstance(item, Package):
			self._AddPackage(item)
		elif isinstance(item, PackageBody):
			self._AddPackageBody(item)
		elif isinstance(item, Context):
			self._AddContext(item)
		elif isinstance(item, Configuration):
			self._AddConfiguration(item)
		elif isinstance(item, VerificationUnit):
			self._AddVerificationUnit(item)
		elif isinstance(item, VerificationProperty):
			self._AddVerificationProperty(item)
		elif isinstance(item, VerificationMode):
			self._AddVerificationMode(item)
		else:
			ex = ValueError(f"Parameter 'item' is an unknown 'DesignUnit'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
			raise ex

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the document's path (:attr:`_path`).

		:returns: The path of this document.
		"""
		return self._path

	@readonly
	def DesignUnits(self) -> List[DesignUnit]:
		"""
		Read-only property to access a list of all design units declarations found in this document (:attr:`_designUnits`).

		:returns: List of all design units.
		"""
		return self._designUnits

	@readonly
	def Contexts(self) -> Dict[str, Context]:
		"""
		Read-only property to access a list of all context declarations found in this document (:attr:`_contexts`).

		:returns: List of all contexts.
		"""
		return self._contexts

	@readonly
	def Configurations(self) -> Dict[str, Configuration]:
		"""
		Read-only property to access a list of all configuration declarations found in this document (:attr:`_configurations`).

		:returns: List of all configurations.
		"""
		return self._configurations

	@readonly
	def Entities(self) -> Dict[str, Entity]:
		"""
		Read-only property to access a list of all entity declarations found in this document (:attr:`_entities`).

		:returns: List of all entities.
		"""
		return self._entities

	@readonly
	def Architectures(self) -> Dict[str, Dict[str, Architecture]]:
		"""
		Read-only property to access a list of all architecture declarations found in this document (:attr:`_architectures`).

		:returns: List of all architectures.
		"""
		return self._architectures

	@readonly
	def Packages(self) -> Dict[str, Package]:
		"""
		Read-only property to access a list of all package declarations found in this document (:attr:`_packages`).

		:returns: List of all packages.
		"""
		return self._packages

	@readonly
	def PackageBodies(self) -> Dict[str, PackageBody]:
		"""
		Read-only property to access a list of all package body declarations found in this document (:attr:`_packageBodies`).

		:returns: List of all package bodies.
		"""
		return self._packageBodies

	@readonly
	def VerificationUnits(self) -> Dict[str, VerificationUnit]:
		"""
		Read-only property to access a list of all verification unit declarations found in this document (:attr:`_verificationUnits`).

		:returns: List of all verification units.
		"""
		return self._verificationUnits

	@readonly
	def VerificationProperties(self) -> Dict[str, VerificationProperty]:
		"""
		Read-only property to access a list of all verification properties declarations found in this document (:attr:`_verificationProperties`).

		:returns: List of all verification properties.
		"""
		return self._verificationProperties

	@readonly
	def VerificationModes(self) -> Dict[str, VerificationMode]:
		"""
		Read-only property to access a list of all verification modes declarations found in this document (:attr:`_verificationModes`).

		:returns: List of all verification modes.
		"""
		return self._verificationModes

	@readonly
	def CompileOrderVertex(self) -> Vertex[None, None, None, 'Document', None, None, None, None, None, None, None, None, None, None, None, None, None]:
		"""
		Read-only property to access the corresponding compile-order vertex (:attr:`_compileOrderVertex`).

		The compile-order vertex references this document by its value field.

		:returns: The corresponding compile-order vertex.
		"""
		return self._compileOrderVertex

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		"""
		Iterate all design units in the document.

		A union of :class:`DesignUnitKind` values can be given to filter the returned result for suitable design units.

		.. rubric:: Algorithm

		* If contexts are selected in the filter:

		  1. Iterate all contexts in that library.

		* If packages are selected in the filter:

		  1. Iterate all packages in that library.

		* If package bodies are selected in the filter:

		  1. Iterate all package bodies in that library.

		* If entites are selected in the filter:

		  1. Iterate all entites in that library.

		* If architectures are selected in the filter:

		  1. Iterate all architectures in that library.

		* If configurations are selected in the filter:

		  1. Iterate all configurations in that library.

		:param filter: An enumeration with possibly multiple flags to filter the returned design units.
		:returns:      A generator to iterate all matched design units in the document.

		.. seealso::

		   :meth:`pyVHDLModel.Design.IterateDesignUnits`
		     Iterate all design units in the design.
		   :meth:`pyVHDLModel.Library.IterateDesignUnits`
		     Iterate all design units in the library.
		"""
		if DesignUnitKind.Context in filter:
			for context in self._contexts.values():
				yield context

		if DesignUnitKind.Package in filter:
			for package in self._packages.values():
				yield package

		if DesignUnitKind.PackageBody in filter:
			for packageBody in self._packageBodies.values():
				yield packageBody

		if DesignUnitKind.Entity in filter:
			for entity in self._entities.values():
				yield entity

		if DesignUnitKind.Architecture in filter:
			for architectures in self._architectures.values():
				for architecture in architectures.values():
					yield architecture

		if DesignUnitKind.Configuration in filter:
			for configuration in self._configurations.values():
				yield configuration

		# for verificationProperty in self._verificationUnits.values():
		# 	yield verificationProperty
		# for verificationUnit in self._verificationProperties.values():
		# 	yield entity
		# for verificationMode in self._verificationModes.values():
		# 	yield verificationMode

	def __repr__(self) -> str:
		"""
		Formats a representation of the document.

		**Format:** ``Document: 'path/to/file.vhdl'``

		:returns: String representation of the document.
		"""
		return f"Document: '{self._path}'"

	__str__ = __repr__
