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
**An abstract VHDL language model.**

This package provides a unified abstract language model for VHDL. Projects reading from source files can derive own
classes and implement additional logic to create a concrete language model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can build higher level features and services
on such a model, while supporting multiple frontends.

.. admonition:: Copyright Information

   :copyright: Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany
   :copyright: Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
   :license: Apache License, Version 2.0
"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2016-2023, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.22.1"


from enum                      import unique, Enum, Flag, auto
from pathlib                   import Path

from typing                    import Union, Dict, cast, List, Generator

from pyTooling.Decorators      import export
from pyTooling.Graph           import Graph, Vertex, Edge

from pyVHDLModel.Exception     import VHDLModelException
from pyVHDLModel.Exception     import LibraryExistsInDesignError, LibraryRegisteredToForeignDesignError, LibraryNotRegisteredError, EntityExistsInLibraryError
from pyVHDLModel.Exception     import ArchitectureExistsInLibraryError, PackageExistsInLibraryError, PackageBodyExistsError, ConfigurationExistsInLibraryError
from pyVHDLModel.Exception     import ContextExistsInLibraryError, ReferencedLibraryNotExistingError
from pyVHDLModel.Base          import ModelEntity, NamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Symbol        import AllPackageMembersReferenceSymbol, PackageMembersReferenceSymbol
from pyVHDLModel.Concurrent    import EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation
from pyVHDLModel.DesignUnit    import DesignUnit, PrimaryUnit, Architecture, PackageBody, Context, Entity, Configuration, Package
from pyVHDLModel.PSLModel      import VerificationUnit, VerificationProperty, VerificationMode
from pyVHDLModel.Instantiation import PackageInstantiation


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
#	AMS93 =              93  #:
	AMS99 =              99  #: VHDL-AMS-1999
	VHDL2000 =         2000  #: VHDL-2000
	VHDL2002 =         2002  #: VHDL-2002
	VHDL2008 =         2008  #: VHDL-2008
	AMS2017 =          2017  #: VHDL-AMS-2017
	VHDL2019 =         2019  #: VHDL-2019
	Latest =          10000  #: Latest VHDL (2019)

	__VERSION_MAPPINGS__: Dict[Union[int, str], Enum] = {
		87:     VHDL87,
		93:     VHDL93,
		99:     AMS99,
		0:      VHDL2000,
		2:      VHDL2002,
		8:      VHDL2008,
		17:     AMS2017,
		19:     VHDL2019,
		1987:   VHDL87,
		1993:   VHDL93,
		1999:   AMS99,
		2000:   VHDL2000,
		2002:   VHDL2002,
		2008:   VHDL2008,
		2017:   AMS2017,
		2019:   VHDL2019,
		"Any":  Any,
		"Latest": Latest,
		"87":   VHDL87,
		"93":   VHDL93,
		"99":   AMS99,
		"00":   VHDL2000,
		"02":   VHDL2002,
		"08":   VHDL2008,
		"17":   AMS2017,
		"19":   VHDL2019,
		"1987": VHDL87,
		"1993": VHDL93,
		"1999": AMS99,
		"2000": VHDL2000,
		"2002": VHDL2002,
		"2008": VHDL2008,
		"2017": AMS2017,
		"2019": VHDL2019
	}  #: Dictionary of VHDL and VHDL-AMS year codes variants as integer and strings for mapping to unique enum values.

	def __init__(self, *_) -> None:
		"""Patch the embedded MAP dictionary"""
		for k, v in self.__class__.__VERSION_MAPPINGS__.items():
			if ((not isinstance(v, self.__class__)) and (v == self.value)):
				self.__class__.__VERSION_MAPPINGS__[k] = self

	@classmethod
	def Parse(cls, value: Union[int, str]) -> 'Enum':
		"""
		Parses a VHDL or VHDL-AMS year code as integer or string to an enum value.

		:param value:       VHDL/VHDL-AMS year code.
		:returns:           Enumeration value.
		:raises ValueError: If the year code is not recognized.
		"""
		try:
			return cls.__VERSION_MAPPINGS__[value]
		except KeyError:
			ValueError(f"Value '{value!s}' cannot be parsed to member of {cls.__name__}.")

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
			if ((self is self.__class__.Any) or (other is self.__class__.Any)):
				return True
			else:
				return (self.value == other.value)
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	@property
	def IsVHDL(self) -> bool:
		"""
		Checks if the version is a VHDL (not VHDL-AMS) version.

		:returns:          True if version is a VHDL version.
		"""
		return self in (self.VHDL87, self.VHDL93, self.VHDL2002, self.VHDL2008, self.VHDL2019)

	@property
	def IsAMS(self) -> bool:
		"""
		Checks if the version is a VHDL-AMS (not VHDL) version.

		:returns:          True if version is a VHDL-AMS version.
		"""
		return self in (self.AMS99, self.AMS2017)

	def __str__(self) -> str:
		"""
		Formats the VHDL version to pattern ``VHDL'xx`` or in case of VHDL-AMS to ``VHDL-AMS'xx``.

		:return: Formatted VHDL/VHDL-AMS version.
		"""
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
		return str(self.value)


@export
@unique
class ObjectClass(Enum):
	"""
	An ``ObjectClass`` is an enumeration. It represents an object's class (``constant``, ``signal``, ...).

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

	def __str__(self):
		"""
		Formats the object class.

		:return: Formatted object class.
		"""
		return ("", "constant", "variable", "signal", "file", "type", "procedure", "function")[cast(int, self.value)]       # TODO: check performance


@export
@unique
class DesignUnitKind(Flag):
	Context = auto()
	Package = auto()
	PackageBody = auto()
	Entity = auto()
	Architecture = auto()
	Configuration = auto()

	Primary = Context | Configuration | Entity | Package
	Secondary = Architecture | PackageBody
	WithContext = Configuration | Entity | Package | Architecture | PackageBody

	All = Primary | Secondary


@export
@unique
class DependencyGraphVertexKind(Flag):
	Document = auto()
	Library = auto()

	Context = auto()
	Package = auto()
	PackageBody = auto()
	Entity = auto()
	Architecture = auto()
	Component = auto()
	Configuration = auto()


@export
@unique
class DependencyGraphEdgeKind(Flag):
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
class Design(ModelEntity):
	"""
	A ``Design`` represents all loaded and analysed files (see :class:`~pyVHDLModel.Document`). It's the root of this
	document-object-model (DOM). It contains at least one VHDL library (see :class:`~pyVHDLModel.Library`).
	"""
	_libraries:  Dict[str, 'Library']  #: List of all libraries defined for a design.
	_documents:  List['Document']      #: List of all documents loaded for a design.

	_compileOrderGraph: Graph[None, None, None, None, None, 'Document', None, None, None, None, None, None, None]
	_dependencyGraph:   Graph[None, None, None, None, str, DesignUnit, None, None, None, None, None, None, None]
	_hierarchyGraph:    Graph[None, None, None, None, str, DesignUnit, None, None, None, None, None, None, None]
	_toplevel:          Union[Entity, Configuration]

	def __init__(self):
		super().__init__()

		self._libraries = {}
		self._documents = []

		self._compileOrderGraph = Graph()
		self._dependencyGraph = Graph()
		self._hierarchyGraph = Graph()
		self._toplevel = None

	@property
	def Libraries(self) -> Dict[str, 'Library']:
		"""Returns a list of all libraries specified for this design."""
		return self._libraries

	@property
	def Documents(self) -> List['Document']:
		"""Returns a list of all documents (files) loaded for this design."""
		return self._documents

	@property
	def CompileOrderGraph(self) -> Graph:
		return self._compileOrderGraph

	@property
	def DependencyGraph(self) -> Graph:
		return self._dependencyGraph

	@property
	def HierarchyGraph(self) -> Graph:
		return self._hierarchyGraph

	@property
	def TopLevel(self) -> 'Entity':
		# Check for cached result
		if self._toplevel is not None:
			return self._toplevel

		if self._hierarchyGraph.EdgeCount == 0:
			raise VHDLModelException(f"Hierarchy is not yet computed from dependency graph.")

		roots = tuple(self._hierarchyGraph.IterateRoots())
		if len(roots) == 1:
			self._toplevel = roots[0]
			return roots[0]
		else:
			raise VHDLModelException(f"Found more than one toplevel: {', '.join(roots)}")

	def _LoadLibrary(self, library: 'Library') -> None:
		libraryIdentifier = library.NormalizedIdentifier
		if libraryIdentifier in self._libraries:
			raise LibraryExistsInDesignError(library)

		self._libraries[libraryIdentifier] = library
		library._parent = self

	def LoadStdLibrary(self) -> 'Library':
		from pyVHDLModel.STD import Std

		doc = Document(Path("std.vhdl"))

		library = Std()
		for designUnit in library.IterateDesignUnits():
			doc._AddDesignUnit(designUnit)

		self._LoadLibrary(library)

		return library

	def LoadIEEELibrary(self) -> 'Library':
		from pyVHDLModel.IEEE import Ieee

		doc = Document(Path("ieee.vhdl"))

		library = Ieee()
		for designUnit in library.IterateDesignUnits():
			doc._AddDesignUnit(designUnit)

		self._LoadLibrary(library)

		return library

	def AddLibrary(self, library: 'Library') -> None:
		if library.NormalizedIdentifier in self._libraries:
			raise LibraryExistsInDesignError(library)

		if library._parent is not None:
			raise LibraryRegisteredToForeignDesignError(library)

		self._libraries[library.NormalizedIdentifier] = library
		library._parent = self

	def GetLibrary(self, libraryName: str) -> 'Library':
		libraryIdentifier = libraryName.lower()
		try:
			return self._libraries[libraryIdentifier]
		except KeyError:
			lib = Library(libraryName)
			self._libraries[libraryIdentifier] = lib
			lib._parent = self
			return lib

	# TODO: allow overloaded parameter library to be str?
	def AddDocument(self, document: 'Document', library: 'Library') -> None:
		if library.NormalizedIdentifier not in self._libraries:
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
		for library in self._libraries.values():
			yield from library.IterateDesignUnits(filter)

	def Analyze(self) -> None:
		self.AnalyzeDependencies()

	def AnalyzeDependencies(self) -> None:
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

	def CreateDependencyGraph(self) -> None:
		predefinedLibraries = ("std", "ieee")

		for libraryIdentifier, library in self._libraries.items():
			dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}", value=library, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Library
			dependencyVertex["predefined"] = libraryIdentifier in predefinedLibraries
			library._dependencyVertex = dependencyVertex

			for contextIdentifier, context in library._contexts.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{contextIdentifier}", value=context, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Context
				dependencyVertex["predefined"] = context._library._normalizedIdentifier in predefinedLibraries
				context._dependencyVertex = dependencyVertex

			for packageIdentifier, package in library._packages.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageIdentifier}", value=package, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Package
				dependencyVertex["predefined"] = package._library._normalizedIdentifier in predefinedLibraries
				package._dependencyVertex = dependencyVertex

			for packageBodyIdentifier, packageBody in library._packageBodies.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageBodyIdentifier}(body)", value=packageBody, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.PackageBody
				dependencyVertex["predefined"] = packageBody._library._normalizedIdentifier in predefinedLibraries
				packageBody._dependencyVertex = dependencyVertex

			for entityIdentifier, entity in library._entities.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}", value=entity, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Entity
				dependencyVertex["predefined"] = entity._library._normalizedIdentifier in predefinedLibraries
				entity._dependencyVertex = dependencyVertex

			for entityIdentifier, architectures in library._architectures.items():
				for architectureIdentifier, architecture in architectures.items():
					dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}({architectureIdentifier})", value=architecture, graph=self._dependencyGraph)
					dependencyVertex["kind"] = DependencyGraphVertexKind.Architecture
					dependencyVertex["predefined"] = architecture._library._normalizedIdentifier in predefinedLibraries
					architecture._dependencyVertex = dependencyVertex

			for configurationIdentifier, configuration in library._configurations.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{configurationIdentifier}", value=configuration, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Configuration
				dependencyVertex["predefined"] = configuration._library._normalizedIdentifier in predefinedLibraries
				configuration._dependencyVertex = dependencyVertex

	def CreateCompileOrderGraph(self) -> None:
		for document in self._documents:
			dependencyVertex = Vertex(vertexID=document.Path.name, value=document, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Document
			document._dependencyVertex = dependencyVertex

			compilerOrderVertex = dependencyVertex.Copy(self._compileOrderGraph, linkingKeyToOriginalVertex="dependencyVertex", linkingKeyFromOriginalVertex="compileOrderVertex")
			document._compileOrderVertex = compilerOrderVertex

			for designUnit in document._designUnits:
				edge = dependencyVertex.LinkFromVertex(designUnit._dependencyVertex)
				edge["kind"] = DependencyGraphEdgeKind.SourceFile

	def LinkContexts(self) -> None:
		for context in self.IterateDesignUnits(DesignUnitKind.Context):
			# Create entries in _referenced*** for the current working library under its real name.
			workingLibrary: Library = context.Library
			libraryIdentifier = workingLibrary.NormalizedIdentifier

			context._referencedLibraries[libraryIdentifier] = self._libraries[libraryIdentifier]
			context._referencedPackages[libraryIdentifier] = {}
			context._referencedContexts[libraryIdentifier] = {}

			# Process all library clauses
			for libraryReference in context._libraryReferences:
				# A library clause can have multiple comma-separated references
				for librarySymbol in libraryReference.Symbols:
					libraryIdentifier = librarySymbol.NormalizedIdentifier
					try:
						library = self._libraries[libraryIdentifier]
					except KeyError:
						raise ReferencedLibraryNotExistingError(context, librarySymbol)
						# TODO: add position to these messages

					librarySymbol.Library = library

					context._referencedLibraries[libraryIdentifier] = library
					context._referencedPackages[libraryIdentifier] = {}
					context._referencedContexts[libraryIdentifier] = {}
					# TODO: warn duplicate library reference

					dependency = context._dependencyVertex.LinkToVertex(library._dependencyVertex, edgeValue=libraryReference)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

			# Process all use clauses
			for packageReference in context.PackageReferences:
				# A use clause can have multiple comma-separated references
				for symbol in packageReference.Symbols:
					packageSymbol = symbol.Prefix
					librarySymbol = packageSymbol.Prefix

					libraryIdentifier = librarySymbol.NormalizedIdentifier
					packageIdentifier = packageSymbol.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						library: Library = context.Library
						libraryIdentifier = library.NormalizedIdentifier
					elif libraryIdentifier not in context._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Use clause references library '{librarySymbol.Identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryIdentifier]

					try:
						package = library._packages[packageIdentifier]
					except KeyError:
						raise VHDLModelException(f"Package '{packageSymbol.Identifier}' not found in {'working ' if librarySymbol.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")

					librarySymbol.Library = library
					packageSymbol.Package = package

					# TODO: warn duplicate package reference
					context._referencedPackages[libraryIdentifier][packageIdentifier] = package

					dependency = context._dependencyVertex.LinkToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(symbol, AllPackageMembersReferenceSymbol):
						pass

					elif isinstance(symbol, PackageMembersReferenceSymbol):
						raise NotImplementedError()
					else:
						raise VHDLModelException()

	def LinkArchitectures(self) -> None:
		for library in self._libraries.values():
			library.LinkArchitectures()

	def LinkPackageBodies(self) -> None:
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

					dependency = designUnit._dependencyVertex.LinkToVertex(referencedLibrary._dependencyVertex)
					dependency["kind"] = DependencyGraphEdgeKind.LibraryClause

				workingLibrary: Library = designUnit.Library
				libraryIdentifier = workingLibrary.NormalizedIdentifier
				referencedLibrary = self._libraries[libraryIdentifier]


				designUnit._referencedLibraries[libraryIdentifier] = referencedLibrary
				designUnit._referencedPackages[libraryIdentifier] = {}
				designUnit._referencedContexts[libraryIdentifier] = {}

				dependency = designUnit._dependencyVertex.LinkToVertex(referencedLibrary._dependencyVertex)
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
					libraryIdentifier = librarySymbol.NormalizedIdentifier
					try:
						library = self._libraries[libraryIdentifier]
					except KeyError:
						raise VHDLModelException(f"Library '{librarySymbol.Identifier}' referenced by library clause of design unit '{designUnit.Identifier}' doesn't exist in design.")

					librarySymbol.Library = library
					designUnit._referencedLibraries[libraryIdentifier] = library
					designUnit._referencedPackages[libraryIdentifier] = {}
					designUnit._referencedContexts[libraryIdentifier] = {}
					# TODO: warn duplicate library reference

					dependency = designUnit._dependencyVertex.LinkToVertex(library._dependencyVertex, edgeValue=libraryReference)
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

							dependency = designUnit._dependencyVertex.LinkToVertex(referencedPackage._dependencyVertex)
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
				for symbol in packageReference.Symbols:
					packageSymbol = symbol.Prefix
					librarySymbol = packageSymbol.Prefix

					libraryIdentifier = librarySymbol.NormalizedIdentifier
					packageIdentifier = packageSymbol.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						library: Library = designUnit.Library
						libraryIdentifier = library.NormalizedIdentifier
					elif libraryIdentifier not in designUnit._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Use clause references library '{librarySymbol.Identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryIdentifier]

					try:
						package = library._packages[packageIdentifier]
					except KeyError:
						raise VHDLModelException(f"Package '{packageSymbol.Identifier}' not found in {'working ' if librarySymbol.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")

					librarySymbol.Library = library
					packageSymbol.Package = package

					# TODO: warn duplicate package reference
					designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

					dependency = designUnit._dependencyVertex.LinkToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(symbol, AllPackageMembersReferenceSymbol):
						for componentIdentifier, component in package._components.items():
							designUnit._namespace._elements[componentIdentifier] = component

					elif isinstance(symbol, PackageMembersReferenceSymbol):
						raise NotImplementedError()
					else:
						raise VHDLModelException()

	def LinkContextReferences(self) -> None:
		for designUnit in self.IterateDesignUnits():
			for contextReference in designUnit._contextReferences:
				# A context reference can have multiple comma-separated references
				for contextSymbol in contextReference.Symbols:
					librarySymbol = contextSymbol.Prefix

					libraryIdentifier = librarySymbol.NormalizedIdentifier
					contextIdentifier = contextSymbol.NormalizedIdentifier

					# In case work is used, resolve to the real library name.
					if libraryIdentifier == "work":
						referencedLibrary = designUnit.Library
						libraryIdentifier = referencedLibrary.NormalizedIdentifier
					elif libraryIdentifier not in designUnit._referencedLibraries:
						# TODO: This check doesn't trigger if it's the working library.
						raise VHDLModelException(f"Context reference references library '{librarySymbol.Identifier}', which was not referenced by a library clause.")
					else:
						referencedLibrary = self._libraries[libraryIdentifier]

					try:
						referencedContext = referencedLibrary._contexts[contextIdentifier]
					except KeyError:
						raise VHDLModelException(f"Context '{contextSymbol.Identifier}' not found in {'working ' if librarySymbol.NormalizedIdentifier == 'work' else ''}library '{referencedLibrary.Identifier}'.")

					librarySymbol.Library = referencedLibrary
					contextSymbol.Package = referencedContext

					# TODO: warn duplicate referencedContext reference
					designUnit._referencedContexts[libraryIdentifier][contextIdentifier] = referencedContext

					dependency = designUnit._dependencyVertex.LinkToVertex(referencedContext._dependencyVertex, edgeValue=contextReference)
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
		for package in self.IterateDesignUnits(DesignUnitKind.Package):
			library = package._library
			for component in package._components.values():
				try:
					entity = library._entities[component.NormalizedIdentifier]
				except KeyError:
					print(f"Entity '{component.Identifier}' not found for component '{component.Identifier}' in library '{library.Identifier}'.")

				component.Entity = entity

				# QUESTION: Add link in dependency graph as dashed line from component to entity?
				#           Currently, component has no _dependencyVertex field

	def LinkInstantiations(self) -> None:
		for architecture in self.IterateDesignUnits(DesignUnitKind.Architecture):
			for instance in architecture.IterateInstantiations():
				if isinstance(instance, EntityInstantiation):
					libraryIdentifier = instance.Entity.Prefix.Identifier
					normalizedLibraryIdentifier = instance.Entity.Prefix.NormalizedIdentifier
					if normalizedLibraryIdentifier == "work":
						libraryIdentifier = architecture.Library.Identifier
						normalizedLibraryIdentifier = architecture.Library.NormalizedIdentifier
					elif normalizedLibraryIdentifier not in architecture._referencedLibraries:
						ex =Exception(f"Referenced library '{libraryIdentifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Prefix.Identifier}.{instance.Entity.Identifier}' not found in architecture '{architecture!r}'.")
						ex.add_note(f"Add a library reference to the architecture or entity using a library clause like: 'library {libraryIdentifier};'.")
						raise ex

					try:
						library = self._libraries[normalizedLibraryIdentifier]
					except KeyError:
						ex = Exception(f"Referenced library '{libraryIdentifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Prefix.Identifier}.{instance.Entity.Identifier}' not found in design.")
						ex.add_note(f"No design units were parsed into library '{libraryIdentifier}'. Thus it doesn't exist in design.")
						raise ex

					try:
						entity = library._entities[instance.Entity.NormalizedIdentifier]
					except KeyError:
						ex = Exception(f"Referenced entity '{instance.Entity.Identifier}' in direct entity instantiation '{instance.Label}: entity {instance.Entity.Prefix.Identifier}.{instance.Entity.Identifier}' not found in {'working ' if instance.Entity.Prefix.NormalizedIdentifier == 'work' else ''}library '{libraryIdentifier}'.")
						libs = [library.Identifier for library in self._libraries.values() for entityIdentifier in library._entities.keys() if entityIdentifier == instance.Entity.NormalizedIdentifier]
						if libs:
							ex.add_note(f"Found entity '{instance.Entity.Identifier}' in other libraries: {', '.join(libs)}")
						raise ex

					instance.Entity.Prefix.Library = library
					instance.Entity.Entity = entity

					dependency = architecture._dependencyVertex.LinkToVertex(entity._dependencyVertex, edgeValue=instance)
					dependency["kind"] = DependencyGraphEdgeKind.EntityInstantiation

				elif isinstance(instance, ComponentInstantiation):
					component = architecture._namespace.FindComponent(instance.Component)

					instance.Component.Component = component

					dependency = architecture._dependencyVertex.LinkToVertex(component.Entity._dependencyVertex, edgeValue=instance)
					dependency["kind"] = DependencyGraphEdgeKind.ComponentInstantiation

				elif isinstance(instance, ConfigurationInstantiation):
					# pass
					print(instance.Label, instance.Configuration)

	def IndexPackages(self) -> None:
		for library in self._libraries.values():
			library.IndexPackages()

	def IndexArchitectures(self) -> None:
		for library in self._libraries.values():
			library.IndexArchitectures()

	def CreateHierarchyGraph(self) -> None:
		# Copy all entity and architecture vertices from dependency graph to hierarchy graph and double-link them
		entityArchitectureFilter = lambda v: v["kind"] in DependencyGraphVertexKind.Entity | DependencyGraphVertexKind.Architecture
		for vertex in self._dependencyGraph.IterateVertices(predicate=entityArchitectureFilter):
			newVertex = vertex.Copy(self._hierarchyGraph, linkingKeyToOriginalVertex="dependencyVertex", linkingKeyFromOriginalVertex="hierarchyVertex")

		# Copy implementation edges from
		for hierarchyArchitectureVertex in self._hierarchyGraph.IterateVertices(predicate=lambda v: v["kind"] is DependencyGraphVertexKind.Architecture):
			for dependencyEdge in hierarchyArchitectureVertex["dependencyVertex"].IterateOutboundEdges():
				kind: DependencyGraphEdgeKind = dependencyEdge["kind"]
				if DependencyGraphEdgeKind.Implementation in kind:
					hierarchyDestinationVertex = dependencyEdge.Destination["hierarchyVertex"]
					newEdge = hierarchyArchitectureVertex.LinkFromVertex(hierarchyDestinationVertex)
				elif DependencyGraphEdgeKind.Instantiation in kind:
					hierarchyDestinationVertex = dependencyEdge.Destination["hierarchyVertex"]
					newEdge = hierarchyArchitectureVertex.LinkToVertex(hierarchyDestinationVertex)
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
			elif sourceVertex.HasLinkToDestination(destinationVertex):
				continue

			e = sourceVertex.LinkToVertex(destinationVertex)
			e["kind"] = DependencyGraphEdgeKind.CompileOrder

			e = sourceVertex["dependencyVertex"].LinkToVertex(destinationVertex["dependencyVertex"])
			e["kind"] = DependencyGraphEdgeKind.CompileOrder

	def IterateDocumentsInCompileOrder(self) -> Generator['Document', None, None]:
		if self._compileOrderGraph.EdgeCount == 0:
			raise VHDLModelException(f"Compile order is not yet computed from dependency graph.")

		return self._compileOrderGraph.IterateTopologically()

	def GetUnusedDesignUnits(self) -> List[DesignUnit]:
		raise NotImplementedError()


@export
class Library(ModelEntity, NamedEntityMixin):
	"""A ``Library`` represents a VHDL library. It contains all *primary* and *secondary* design units."""

	_contexts:       Dict[str, Context]                  #: Dictionary of all contexts defined in a library.
	_configurations: Dict[str, Configuration]            #: Dictionary of all configurations defined in a library.
	_entities:       Dict[str, Entity]                   #: Dictionary of all entities defined in a library.
	_architectures:  Dict[str, Dict[str, Architecture]]  #: Dictionary of all architectures defined in a library.
	_packages:       Dict[str, Package]                  #: Dictionary of all packages defined in a library.
	_packageBodies:  Dict[str, PackageBody]              #: Dictionary of all package bodies defined in a library.

	_dependencyVertex: Vertex[str, Union['Library', DesignUnit], None, None]

	def __init__(self, identifier: str):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)

		self._contexts =        {}
		self._configurations =  {}
		self._entities =        {}
		self._architectures =   {}
		self._packages =        {}
		self._packageBodies =   {}

		self._dependencyVertex = None

	@property
	def Contexts(self) -> Dict[str, Context]:
		"""Returns a list of all context declarations declared in this library."""
		return self._contexts

	@property
	def Configurations(self) -> Dict[str, Configuration]:
		"""Returns a list of all configuration declarations declared in this library."""
		return self._configurations

	@property
	def Entities(self) -> Dict[str, Entity]:
		"""Returns a list of all entity declarations declared in this library."""
		return self._entities

	@property
	def Architectures(self) -> Dict[str, Dict[str, Architecture]]:
		"""Returns a list of all architectures declarations declared in this library."""
		return self._architectures

	@property
	def Packages(self) -> Dict[str, Package]:
		"""Returns a list of all package declarations declared in this library."""
		return self._packages

	@property
	def PackageBodies(self) -> Dict[str, PackageBody]:
		"""Returns a list of all package body declarations declared in this library."""
		return self._packageBodies

	@property
	def DependencyVertex(self) -> Vertex:
		return self._dependencyVertex

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
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

	def LinkArchitectures(self):
		for entityName, architecturesPerEntity in self._architectures.items():
			if entityName not in self._entities:
				architectureNames = "', '".join(architecturesPerEntity.keys())
				raise VHDLModelException(f"Entity '{entityName}' referenced by architecture(s) '{architectureNames}' doesn't exist in library '{self.Identifier}'.")
				# TODO: search in other libraries to find that entity.
				# TODO: add code position

			for architecture in architecturesPerEntity.values():
				entity = self._entities[entityName]

				if architecture.NormalizedIdentifier in entity._architectures:
					raise VHDLModelException(f"Architecture '{architecture.Identifier}' already exists for entity '{entity.Identifier}'.")
					# TODO: add code position of existing and current

				entity._architectures[architecture.NormalizedIdentifier] = architecture
				architecture._entity.Entity = entity
				architecture._namespace.ParentNamespace = entity._namespace

				# add "architecture -> entity" relation in dependency graph
				dependency = architecture._dependencyVertex.LinkToVertex(entity._dependencyVertex)
				dependency["kind"] = DependencyGraphEdgeKind.EntityImplementation

	def LinkPackageBodies(self):
		for packageBodyName, packageBody in self._packageBodies.items():
			if packageBodyName not in self._packages:
				raise VHDLModelException(f"Package '{packageBodyName}' referenced by package body '{packageBodyName}' doesn't exist in library '{self.Identifier}'.")

			package = self._packages[packageBodyName]
			packageBody._package.Package = package
			packageBody._namespace.ParentNamespace = package._namespace

			# add "package body -> package" relation in dependency graph
			dependency = packageBody._dependencyVertex.LinkToVertex(package._dependencyVertex)
			dependency["kind"] = DependencyGraphEdgeKind.PackageImplementation

	def IndexPackages(self):
		for package in self._packages.values():
			package.IndexPackage()

	def IndexArchitectures(self):
		for architectures in self._architectures.values():
			for architecture in architectures.values():
				architecture.Index()

	def __str__(self):
		return f"Library: '{self.Identifier}'"


@export
class Document(ModelEntity, DocumentedEntityMixin):
	"""A ``Document`` represents a sourcefile. It contains *primary* and *secondary* design units."""

	_path:                   Path                                  #: path to the document. ``None`` if virtual document.
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

	_dependencyVertex:       Vertex[None, 'Document', None, None]
	_compileOrderVertex:     Vertex[None, 'Document', None, None]

	def __init__(self, path: Path, documentation: str = None):
		super().__init__()
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

		self._dependencyVertex = None
		self._compileOrderVertex = None

	def _AddEntity(self, item: Entity) -> None:
		if not isinstance(item, Entity):
			raise TypeError(f"Parameter 'item' is not of type 'Entity'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._entities:
			raise ValueError(f"An entity '{item.Identifier}' already exists in this document.")

		self._entities[identifier] = item
		self._designUnits.append(item)
		item._parent = self


	def _AddArchitecture(self, item: Architecture) -> None:
		if not isinstance(item, Architecture):
			raise TypeError(f"Parameter 'item' is not of type 'Architecture'.")

		entity = item.Entity
		entityIdentifier = entity.NormalizedIdentifier
		try:
			architectures = self._architectures[entityIdentifier]
			if item.Identifier in architectures:
				raise ValueError(f"An architecture '{item.Identifier}' for entity '{entity.Identifier}' already exists in this document.")

			architectures[item.Identifier] = item
		except KeyError:
			self._architectures[entityIdentifier] = {item.Identifier: item}

		self._designUnits.append(item)
		item._parent = self

	def _AddPackage(self, item: Package) -> None:
		if not isinstance(item, (Package, PackageInstantiation)):
			raise TypeError(f"Parameter 'item' is not of type 'Package' or 'PackageInstantiation'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._packages:
			raise ValueError(f"A package '{item.Identifier}' already exists in this document.")

		self._packages[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddPackageBody(self, item: PackageBody) -> None:
		if not isinstance(item, PackageBody):
			raise TypeError(f"Parameter 'item' is not of type 'PackageBody'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._packageBodies:
			raise ValueError(f"A package body '{item.Identifier}' already exists in this document.")

		self._packageBodies[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddContext(self, item: Context) -> None:
		if not isinstance(item, Context):
			raise TypeError(f"Parameter 'item' is not of type 'Context'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._contexts:
			raise ValueError(f"A context '{item.Identifier}' already exists in this document.")

		self._contexts[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddConfiguration(self, item: Configuration) -> None:
		if not isinstance(item, Configuration):
			raise TypeError(f"Parameter 'item' is not of type 'Configuration'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._configurations:
			raise ValueError(f"A configuration '{item.Identifier}' already exists in this document.")

		self._configurations[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddVerificationUnit(self, item: VerificationUnit) -> None:
		if not isinstance(item, VerificationUnit):
			raise TypeError(f"Parameter 'item' is not of type 'VerificationUnit'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationUnits:
			raise ValueError(f"A verification unit '{item.Identifier}' already exists in this document.")

		self._verificationUnits[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddVerificationProperty(self, item: VerificationProperty) -> None:
		if not isinstance(item, VerificationProperty):
			raise TypeError(f"Parameter 'item' is not of type 'VerificationProperty'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationProperties:
			raise ValueError(f"A verification property '{item.Identifier}' already exists in this document.")

		self._verificationProperties[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddVerificationMode(self, item: VerificationMode) -> None:
		if not isinstance(item, VerificationMode):
			raise TypeError(f"Parameter 'item' is not of type 'VerificationMode'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._verificationModes:
			raise ValueError(f"A verification mode '{item.Identifier}' already exists in this document.")

		self._verificationModes[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddDesignUnit(self, item: DesignUnit) -> None:
		identifier = item.NormalizedIdentifier
		if isinstance(item, Entity):
			self._entities[identifier] = item
		elif isinstance(item, Architecture):
			entityIdentifier = item.Entity.NormalizedIdentifier
			try:
				architectures = self._architectures[entityIdentifier]
				if identifier in architectures:
					raise ValueError(f"An architecture '{item.Identifier}' for entity '{item.Entity.Identifier}' already exists in this document.")

				architectures[identifier] = item
			except KeyError:
				self._architectures[entityIdentifier] = {identifier: item}
		elif isinstance(item, Package):
			self._packages[identifier] = item
		elif isinstance(item, PackageBody):
			self._packageBodies[identifier] = item
		elif isinstance(item, Context):
			self._contexts[identifier] = item
		elif isinstance(item, Configuration):
			self._configurations[identifier] = item
		elif isinstance(item, VerificationUnit):
			self._verificationUnits[identifier] = item
		elif isinstance(item, VerificationProperty):
			self._verificationProperties[identifier] = item
		elif isinstance(item, VerificationMode):
			self._verificationModes[identifier] = item
		elif isinstance(item, DesignUnit):
			raise TypeError(f"Parameter 'item' is an unknown 'DesignUnit'.")
		else:
			raise TypeError(f"Parameter 'item' is not of type 'DesignUnit'.")

		self._designUnits.append(item)
		item._parent = self

	@property
	def Path(self) -> Path:
		return self._path

	@property
	def DesignUnits(self) -> List[DesignUnit]:
		"""Returns a list of all design units declarations found in this document."""
		return self._designUnits

	@property
	def Contexts(self) -> Dict[str, Context]:
		"""Returns a list of all context declarations found in this document."""
		return self._contexts

	@property
	def Configurations(self) -> Dict[str, Configuration]:
		"""Returns a list of all configuration declarations found in this document."""
		return self._configurations

	@property
	def Entities(self) -> Dict[str, Entity]:
		"""Returns a list of all entity declarations found in this document."""
		return self._entities

	@property
	def Architectures(self) -> Dict[str, Dict[str, Architecture]]:
		"""Returns a list of all architecture declarations found in this document."""
		return self._architectures

	@property
	def Packages(self) -> Dict[str, Package]:
		"""Returns a list of all package declarations found in this document."""
		return self._packages

	@property
	def PackageBodies(self) -> Dict[str, PackageBody]:
		"""Returns a list of all package body declarations found in this document."""
		return self._packageBodies

	@property
	def VerificationUnits(self) -> Dict[str, VerificationUnit]:
		"""Returns a list of all verification unit declarations found in this document."""
		return self._verificationUnits

	@property
	def VerificationProperties(self) -> Dict[str, VerificationProperty]:
		"""Returns a list of all verification property declarations found in this document."""
		return self._verificationProperties

	@property
	def VerificationModes(self) -> Dict[str, VerificationMode]:
		"""Returns a list of all verification mode declarations found in this document."""
		return self._verificationModes

	@property
	def CompileOrderVertex(self) -> Vertex[None, 'Document', None, None]:
		return self._compileOrderVertex

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
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
