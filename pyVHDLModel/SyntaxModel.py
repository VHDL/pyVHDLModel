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
# Copyright 2017-2022 Patrick Lehmann - Boetzingen, Germany                                                            #
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
This module contains an abstract document language model for VHDL.

:copyright: Copyright 2007-2022 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from pathlib               import Path

from pyTooling.Graph       import Graph, Vertex
from pyTooling.MetaClasses import ExtendedType
from typing                import List, Tuple, Union, Dict, Iterator, Optional as Nullable, Iterable, Generator, cast

from pyTooling.Decorators  import export

from pyVHDLModel import EntityClass, Direction, Mode, DesignUnitKind, DependencyGraphVertexKind, DependencyGraphEdgeKind
from pyVHDLModel           import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, LabeledEntityMixin, DocumentedEntityMixin, PossibleReference
from pyVHDLModel           import Name, Symbol, NewSymbol, LibraryClause, UseClause, ContextReference, DesignUnit
from pyVHDLModel           import PrimaryUnit, SecondaryUnit
from pyVHDLModel           import ExpressionUnion, ConstraintUnion, ContextUnion, SubtypeOrSymbol, DesignUnitWithContextMixin
from pyVHDLModel.PSLModel  import VerificationUnit, VerificationProperty, VerificationMode

try:
	from typing import Protocol
except ImportError:  # pragma: no cover
	class Protocol:
		pass


@export
class SimpleName(Name):
	def __str__(self):
		return self._identifier


@export
class ParenthesisName(Name):
	_associations: List

	def __init__(self, prefix: Name, associations: Iterable):
		super().__init__("", prefix)

		self._associations = []
		for association in associations:
			self._associations.append(association)
			association._parent = self

	@property
	def Associations(self) -> List:
		return self._associations

	def __str__(self):
		return str(self._prefix) + "(" + ", ".join([str(a) for a in self._associations]) + ")"


@export
class IndexedName(Name):
	_indices: List[ExpressionUnion]

	def __init__(self, prefix: Name, indices: Iterable[ExpressionUnion]):
		super().__init__("", prefix)

		self._indices = []
		for index in indices:
			self._indices.append(index)
			index._parent = self

	@property
	def Indices(self) -> List[ExpressionUnion]:
		return self._indices


@export
class SlicedName(Name):
	pass


@export
class SelectedName(Name):
	def __init__(self, identifier: str, prefix: Name):
		super().__init__(identifier, prefix)

	def __str__(self):
		return str(self._prefix) + "." + self._identifier


@export
class AttributeName(Name):
	def __init__(self, identifier: str, prefix: Name):
		super().__init__(identifier, prefix)

	def __str__(self):
		return str(self._prefix) + "'" + self._identifier


@export
class AllName(Name):
	def __init__(self, prefix: Name):
		super().__init__("all", prefix)

	def __str__(self):
		return str(self._prefix) + "." + "all"


@export
class OpenName(Name):
	def __init__(self):
		super().__init__("open")

	def __str__(self):
		return "open"


@export
class LibraryReferenceSymbol(SimpleName, NewSymbol):
	"""A library reference in a library clause."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		NewSymbol.__init__(self, PossibleReference.Library)

	@property
	def Library(self) -> 'Library':
		return self._reference

	@Library.setter
	def Library(self, value: 'Library') -> None:
		self._reference = value


@export
class PackageReferenceSymbol(SelectedName, NewSymbol):
	"""A package reference in a use clause."""

	def __init__(self, identifier: str, prefix: LibraryReferenceSymbol):
		super().__init__(identifier, prefix)
		NewSymbol.__init__(self, PossibleReference.Package)

	@property
	def Prefix(self) -> LibraryReferenceSymbol:
		return cast(LibraryReferenceSymbol, self._prefix)

	@property
	def Package(self) -> 'Package':
		return self._reference

	@Package.setter
	def Package(self, value: 'Package') -> None:
		self._reference = value


@export
class PackageMembersReferenceSymbol(SelectedName, NewSymbol):
	"""A package member reference in a use clause."""

	def __init__(self, identifier: str, prefix: PackageReferenceSymbol):
		super().__init__(identifier, prefix)
		NewSymbol.__init__(self, PossibleReference.PackageMember)

	@property
	def Prefix(self) -> PackageReferenceSymbol:
		return cast(PackageReferenceSymbol, self._prefix)

	@property
	def Member(self) -> 'Package':
		return self._reference

	@Member.setter
	def Member(self, value: 'Package') -> None:
		self._reference = value


@export
class AllPackageMembersReferenceSymbol(AllName, NewSymbol):
	"""A package reference in a use clause."""

	def __init__(self, prefix: PackageReferenceSymbol):
		super().__init__(prefix)
		NewSymbol.__init__(self, PossibleReference.PackageMember)

	@property
	def Prefix(self) -> PackageReferenceSymbol:
		return cast(PackageReferenceSymbol, self._prefix)

	@property
	def Members(self) -> 'Package':
		return self._reference

	@Members.setter
	def Members(self, value: 'Package') -> None:
		self._reference = value


@export
class ContextReferenceSymbol(SelectedName, NewSymbol):
	"""A context reference in a context clause."""

	def __init__(self, identifier: str, prefix: LibraryReferenceSymbol):
		super().__init__(identifier, prefix)
		NewSymbol.__init__(self, PossibleReference.Context)

	@property
	def Prefix(self) -> LibraryReferenceSymbol:
		return cast(LibraryReferenceSymbol, self._prefix)

	@property
	def Context(self) -> 'Context':
		return self._reference

	@Context.setter
	def Context(self, value: 'Context') -> None:
		self._reference = value


@export
class EntitySymbol(SimpleName, NewSymbol):
	"""An entity reference in an architecture declaration."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		NewSymbol.__init__(self, PossibleReference.Entity)

	@property
	def Entity(self) -> 'Entity':
		return self._reference

	@Entity.setter
	def Entity(self, value: 'Entity') -> None:
		self._reference = value


@export
class ArchitectureSymbol(Name, NewSymbol):
	"""An entity reference in an entity instantiation with architecture name."""

	def __init__(self, identifier: str, prefix: EntitySymbol):
		super().__init__(identifier, prefix)
		NewSymbol.__init__(self, PossibleReference.Architecture)

	@property
	def Prefix(self) -> EntitySymbol:
		return cast(EntitySymbol, self._prefix)

	@property
	def Architecture(self) -> 'Architecture':
		return self._reference

	@Architecture.setter
	def Architecture(self, value: 'Architecture') -> None:
		self._reference = value


@export
class PackageSymbol(SimpleName, NewSymbol):
	"""A package reference in a package body declaration."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		NewSymbol.__init__(self, PossibleReference.Package)

	@property
	def Package(self) -> 'Package':
		return self._reference

	@Package.setter
	def Package(self, value: 'Package') -> None:
		self._reference = value


@export
class EntityInstantiationSymbol(SelectedName, NewSymbol):
	"""An entity reference in a direct entity instantiation."""

	def __init__(self, identifier: str, prefix: LibraryReferenceSymbol):
		super().__init__(identifier, prefix)
		NewSymbol.__init__(self, PossibleReference.Entity)

	@property
	def Prefix(self) -> LibraryReferenceSymbol:
		return cast(LibraryReferenceSymbol, self._prefix)

	@property
	def Entity(self) -> 'Entity':
		return self._reference

	@Entity.setter
	def Entity(self, value: 'Entity') -> None:
		self._reference = value


@export
class ComponentInstantiationSymbol(SimpleName, NewSymbol):
	"""A component reference in a component instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		NewSymbol.__init__(self, PossibleReference.Component)

	@property
	def Component(self) -> 'Component':
		return self._reference

	@Component.setter
	def Component(self, value: 'Component') -> None:
		self._reference = value


@export
class ConfigurationInstantiationSymbol(SimpleName, NewSymbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		NewSymbol.__init__(self, PossibleReference.Configuration)

	@property
	def Configuration(self) -> 'Configuration':
		return self._reference

	@Configuration.setter
	def Configuration(self, value: 'Configuration') -> None:
		self._reference = value


@export
class SubtypeSymbol(Symbol):
	def __init__(self, symbolName: Name, possibleReferences: PossibleReference):
		super().__init__(symbolName, PossibleReference.Subtype | PossibleReference.TypeAttribute | possibleReferences)

	@property
	def Subtype(self) -> 'Subtype':
		return self._reference

	@Subtype.setter
	def Subtype(self, value: 'Subtype') -> None:
		self._reference = value


@export
class SimpleSubtypeSymbol(SubtypeSymbol):
	def __init__(self, subtypeName: Name):
		super().__init__(subtypeName, PossibleReference.ScalarType)


@export
class ConstrainedScalarSubtypeSymbol(SubtypeSymbol):
	_range: 'Range'

	def __init__(self, subtypeName: Name, rng: 'Range' = None):
		super().__init__(subtypeName, PossibleReference.ArrayType)
		self._range = rng

	@property
	def Range(self) -> 'Range':
		return self._range


@export
class ConstrainedCompositeSubtypeSymbol(SubtypeSymbol):
	_constraints: List[ConstraintUnion]

	def __init__(self, subtypeName: Name, constraints: Iterable[ConstraintUnion] = None):
		super().__init__(subtypeName, PossibleReference.Unknown)
		self._subtype = None
		self._constraints = [c for c in constraints]

	@property
	def Constraints(self) -> List[ConstraintUnion]:
		return self._constraints


@export
class ObjectSymbol(Symbol):
	pass


@export
class SimpleObjectOrFunctionCallSymbol(ObjectSymbol):
	def __init__(self, objectName: Name):
		super().__init__(objectName, PossibleReference.Constant | PossibleReference.Variable | PossibleReference.Signal | PossibleReference.ScalarType | PossibleReference.Function | PossibleReference.EnumLiteral)

	@property
	def ObjectOrFunction(self) -> Union['Constant', 'Signal', 'Variable', 'Function', 'EnumerationLiteral']:
		return self._reference

	@ObjectOrFunction.setter
	def ObjectOrFunction(self, value: Union['Constant', 'Signal', 'Variable', 'Function', 'EnumerationLiteral']):
		self._reference = value


@export
class IndexedObjectOrFunctionCallSymbol(ObjectSymbol):
	def __init__(self, objectName: Name):
		super().__init__(objectName, PossibleReference.Constant | PossibleReference.Variable | PossibleReference.Signal | PossibleReference.ArrayType | PossibleReference.Function)

	@property
	def ObjectOrFunction(self) -> Union['Constant', 'Signal', 'Variable', 'Function']:
		return self._reference

	@ObjectOrFunction.setter
	def ObjectOrFunction(self, value: Union['Constant', 'Signal', 'Variable', 'Function']):
		self._reference = value


@export
class ConstantSymbol(ObjectSymbol):
	def __init__(self, symbolName: Name):
		super().__init__(symbolName, PossibleReference.Constant)

	@property
	def Constant(self) -> 'Constant':
		return self._reference

	@Constant.setter
	def Constant(self, value: 'Constant') -> None:
		self._reference = value


@export
class VariableSymbol(ObjectSymbol):
	def __init__(self, symbolName: Name):
		super().__init__(symbolName, PossibleReference.Constant)

	@property
	def Variable(self) -> 'Variable':
		return self._reference

	@Variable.setter
	def Variable(self, value: 'Variable') -> None:
		self._reference = value


@export
class SignalSymbol(ObjectSymbol):
	def __init__(self, symbolName: Name):
		super().__init__(symbolName, PossibleReference.Signal)

	@property
	def Signal(self) -> 'Signal':
		return self._reference

	@Signal.setter
	def Signal(self, value: 'Signal') -> None:
		self._reference = value


@export
class Design(ModelEntity):
	"""
	A ``Design`` represents all loaded files (see :class:`~pyVHDLModel.SyntaxModel.Document`)
	and analysed. It's the root of this document-object-model (DOM). It contains
	at least on VHDL library (see :class:`~pyVHDLModel.SyntaxModel.Library`).
	"""
	_libraries:  Dict[str, 'Library']  #: List of all libraries defined for a design.
	_documents:  List['Document']      #: List of all documents loaded for a design.

	_compileOrderGraph: Graph[None, None, None, None, None, 'Document', None, None, None, None, None, None, None]
	_dependencyGraph:   Graph[None, None, None, None, str, 'DesignUnit', None, None, None, None, None, None, None]
	_hierarchyGraph:    Graph[None, None, None, None, str, 'DesignUnit', None, None, None, None, None, None, None]

	def __init__(self):
		super().__init__()

		self._libraries = {}
		self._documents = []

		self._compileOrderGraph = Graph()
		self._dependencyGraph = Graph()
		self._hierarchyGraph = Graph()

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

	def _LoadLibrary(self, library) -> None:
		libraryIdentifier = library.NormalizedIdentifier
		if libraryIdentifier in self._libraries:
			raise Exception(f"Library '{library.Identifier}' already exists in design.")
		self._libraries[libraryIdentifier] = library
		library._parent = self

	def LoadStdLibrary(self) -> 'Library':
		from pyVHDLModel.std import Std

		library = Std()
		self._LoadLibrary(library)

		return library

	def LoadIEEELibrary(self) -> 'Library':
		from pyVHDLModel.ieee import Ieee

		library = Ieee()
		self._LoadLibrary(library)

		return library

	def AddLibrary(self, library: 'Library') -> None:
		if library.NormalizedIdentifier in self._libraries:
			raise Exception(f"Library '{library.Identifier}' already exists in design.")

		if library._parent is not None:
			raise Exception(f"Library '{library.Identifier}' already registered in design '{library.Parent}'.")

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
			raise Exception(f"Library '{library.Identifier}' is not registered in the design.")

		self._documents.append(document)
		document._parent = self

		for entityIdentifier, entity in document._entities.items():
			if entityIdentifier in library._entities:
				raise ValueError(f"Entity '{entity.Identifier}' already exists in library '{library.Identifier}'.")

			library._entities[entityIdentifier] = entity
			entity.Library = library

		for entityIdentifier, architectures in document._architectures.items():
			try:
				architecturesPerEntity = library._architectures[entityIdentifier]
				for architectureIdentifier, architecture in architectures.items():
					if architectureIdentifier in architecturesPerEntity:
						raise ValueError(f"Architecture '{architecture.Identifier}' for entity '{entityIdentifier}' already exists in library '{library.Identifier}'.")

					architecturesPerEntity[architectureIdentifier] = architecture
					architecture.Library = library
			except KeyError:
				architecturesPerEntity = document._architectures[entityIdentifier].copy()
				library._architectures[entityIdentifier] = architecturesPerEntity

				for architecture in architecturesPerEntity.values():
					architecture.Library = library

		for packageIdentifier, package in document._packages.items():
			if packageIdentifier in library._packages:
				raise ValueError(f"Package '{packageIdentifier}' already exists in library '{library.Identifier}'.")

			library._packages[packageIdentifier] = package
			package.Library = library

		for packageBodyIdentifier, packageBody in document._packageBodies.items():
			if packageBodyIdentifier in library._packageBodies:
				raise ValueError(f"Package body '{packageBodyIdentifier}' already exists in library '{library.Identifier}'.")

			library._packageBodies[packageBodyIdentifier] = packageBody
			packageBody.Library = library

		for configurationIdentifier, configuration in document._configurations.items():
			if configurationIdentifier in library._configurations:
				raise ValueError(f"Configuration '{configurationIdentifier}' already exists in library '{library.Identifier}'.")

			library._configurations[configurationIdentifier] = configuration
			configuration.Library = library

		for contextIdentifier, context in document._contexts.items():
			if contextIdentifier in library._contexts:
				raise ValueError(f"Context '{contextIdentifier}' already exists in library '{library.Identifier}'.")

			library._contexts[contextIdentifier] = context
			context.Library = library

	def IterateDesignUnits(self, filter: DesignUnitKind = DesignUnitKind.All) -> Generator[DesignUnit, None, None]:
		for library in self._libraries.values():
			yield from library.IterateDesignUnits(filter)

	def Analyze(self) -> None:
		self.AnalyzeDependencies()

	def AnalyzeDependencies(self) -> None:
		self.CreateCompilerOrderGraph()
		self.CreateDependencyGraph()

		self.LinkContexts()
		self.LinkArchitectures()
		self.LinkPackageBodies()
		self.LinkLibraryReferences()
		self.LinkPackageReferences()
		self.LinkContextReferences()

		self.IndexPackages()
		self.IndexArchitectures()

		self.LinkInstantiations()
		self.CreateHierarchyGraph()

	def CreateCompilerOrderGraph(self) -> None:
		for document in self._documents:
			compilerOrderVertex = Vertex(value=document, graph=self._compileOrderGraph)
			document._compileOrderVertex = compilerOrderVertex

	def CreateDependencyGraph(self) -> None:
		for libraryIdentifier, library in self._libraries.items():
			dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}", value=library, graph=self._dependencyGraph)
			dependencyVertex["kind"] = DependencyGraphVertexKind.Library
			library._dependencyVertex = dependencyVertex

			for contextIdentifier, context in library._contexts.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{contextIdentifier}", value=context, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Context
				context._dependencyVertex = dependencyVertex

			for packageIdentifier, package in library._packages.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageIdentifier}", value=package, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Package
				package._dependencyVertex = dependencyVertex

			for packageBodyIdentifier, packageBody in library._packageBodies.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{packageBodyIdentifier}(body)", value=packageBody, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.PackageBody
				packageBody._dependencyVertex = dependencyVertex

			for entityIdentifier, entity in library._entities.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}", value=entity, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Entity
				entity._dependencyVertex = dependencyVertex

			for entityIdentifier, architectures in library._architectures.items():
				for architectureIdentifier, architecture in architectures.items():
					dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{entityIdentifier}({architectureIdentifier})", value=architecture, graph=self._dependencyGraph)
					dependencyVertex["kind"] = DependencyGraphVertexKind.Architecture
					architecture._dependencyVertex = dependencyVertex

			for configurationIdentifier, configuration in library._configurations.items():
				dependencyVertex = Vertex(vertexID=f"{libraryIdentifier}.{configurationIdentifier}", value=configuration, graph=self._dependencyGraph)
				dependencyVertex["kind"] = DependencyGraphVertexKind.Configuration
				configuration._dependencyVertex = dependencyVertex

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
						raise Exception(f"Library '{librarySymbol.Identifier}' referenced by library clause of context '{context.Identifier}' doesn't exist in design.")
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
						raise Exception(f"Use clause references library '{librarySymbol.Identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryIdentifier]

					try:
						package = library._packages[packageIdentifier]
					except KeyError:
						raise Exception(f"Package '{packageSymbol.Identifier}' not found in {'working ' if librarySymbol.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")

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
						raise Exception()

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
					raise Exception()

				for libraryIdentifier, library in referencedLibraries.items():
					designUnit._referencedLibraries[libraryIdentifier] = library

			for libraryReference in designUnit._libraryReferences:
				# A library clause can have multiple comma-separated references
				for librarySymbol in libraryReference.Symbols:
					libraryIdentifier = librarySymbol.NormalizedIdentifier
					try:
						library = self._libraries[libraryIdentifier]
					except KeyError:
						raise Exception(f"Library '{librarySymbol.Identifier}' referenced by library clause of design unit '{designUnit.Identifier}' doesn't exist in design.")

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
							raise Exception()
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
					raise Exception()

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
						raise Exception(f"Use clause references library '{librarySymbol.Identifier}', which was not referenced by a library clause.")
					else:
						library = self._libraries[libraryIdentifier]

					try:
						package = library._packages[packageIdentifier]
					except KeyError:
						raise Exception(f"Package '{packageSymbol.Identifier}' not found in {'working ' if librarySymbol.NormalizedIdentifier == 'work' else ''}library '{library.Identifier}'.")

					librarySymbol.Library = library
					packageSymbol.Package = package

					# TODO: warn duplicate package reference
					designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

					dependency = designUnit._dependencyVertex.LinkToVertex(package._dependencyVertex, edgeValue=packageReference)
					dependency["kind"] = DependencyGraphEdgeKind.UseClause

					# TODO: update the namespace with visible members
					if isinstance(symbol, AllPackageMembersReferenceSymbol):
						pass

					elif isinstance(symbol, PackageMembersReferenceSymbol):
						raise NotImplementedError()
					else:
						raise Exception()

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
						raise Exception(f"Context reference references library '{librarySymbol.Identifier}', which was not referenced by a library clause.")
					else:
						referencedLibrary = self._libraries[libraryIdentifier]

					try:
						referencedContext = referencedLibrary._contexts[contextIdentifier]
					except KeyError:
						raise Exception(f"Context '{contextSymbol.Identifier}' not found in {'working ' if librarySymbol.NormalizedIdentifier == 'work' else ''}library '{referencedLibrary.Identifier}'.")

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
						# 	raise Exception(f"Referenced library '{library.Identifier}' already exists in references for design unit '{designUnit.Identifier}'.")

						designUnit._referencedLibraries[libraryIdentifier] = library
						designUnit._referencedPackages[libraryIdentifier] = {}

					for libraryIdentifier, packages in context._referencedPackages.items():
						for packageIdentifier, package in packages.items():
							if packageIdentifier in designUnit._referencedPackages:
								raise Exception(f"Referenced package '{package.Identifier}' already exists in references for design unit '{designUnit.Identifier}'.")

							designUnit._referencedPackages[libraryIdentifier][packageIdentifier] = package

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
					# pass
					print(instance.Label, instance.Component)
				elif isinstance(instance, ConfigurationInstantiation):
					# pass
					print(instance.Label, instance.Configuration)

	def CreateHierarchyGraph(self) -> None:
		pass

	def IndexPackages(self) -> None:
		for library in self._libraries.values():
			library.IndexPackages()

	def IndexArchitectures(self) -> None:
		for library in self._libraries.values():
			library.IndexArchitectures()

	def ComputeHierarchy(self) -> None:
		raise NotImplementedError()

	def GetCompileOrder(self) -> Generator['Document', None, None]:
		raise NotImplementedError()

	def GetTopLevel(self) -> 'Entity':
		raise NotImplementedError()

	def GetUnusedDesignUnits(self) -> List[DesignUnit]:
		raise NotImplementedError()


@export
class Library(ModelEntity, NamedEntityMixin):
	"""A ``Library`` represents a VHDL library. It contains all *primary* design units."""

	_contexts:       Dict[str, 'Context']                  #: Dictionary of all contexts defined in a library.
	_configurations: Dict[str, 'Configuration']            #: Dictionary of all configurations defined in a library.
	_entities:       Dict[str, 'Entity']                   #: Dictionary of all entities defined in a library.
	_architectures:  Dict[str, Dict[str, 'Architecture']]  #: Dictionary of all architectures defined in a library.
	_packages:       Dict[str, 'Package']                  #: Dictionary of all packages defined in a library.
	_packageBodies:  Dict[str, 'PackageBody']              #: Dictionary of all package bodies defined in a library.

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
	def Contexts(self) -> Dict[str, 'Context']:
		"""Returns a list of all context declarations declared in this library."""
		return self._contexts

	@property
	def Configurations(self) -> Dict[str, 'Configuration']:
		"""Returns a list of all configuration declarations declared in this library."""
		return self._configurations

	@property
	def Entities(self) -> Dict[str, 'Entity']:
		"""Returns a list of all entity declarations declared in this library."""
		return self._entities

	@property
	def Architectures(self) -> Dict[str, Dict[str, 'Architecture']]:
		"""Returns a list of all architectures declarations declared in this library."""
		return self._architectures

	@property
	def Packages(self) -> Dict[str, 'Package']:
		"""Returns a list of all package declarations declared in this library."""
		return self._packages

	@property
	def PackageBodies(self) -> Dict[str, 'PackageBody']:
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
				raise Exception(f"Entity '{entityName}' referenced by architecture(s) '{architectureNames}' doesn't exist in library '{self.Identifier}'.")
				# TODO: search in other libraries to find that entity.
				# TODO: add code position

			for architecture in architecturesPerEntity.values():
				entity = self._entities[entityName]

				if architecture.NormalizedIdentifier in entity._architectures:
					raise Exception(f"Architecture '{architecture.Identifier}' already exists for entity '{entity.Identifier}'.")
					# TODO: add code position of existing and current

				entity._architectures[architecture.NormalizedIdentifier] = architecture
				architecture._entity.Entity = entity

				# add "architecture -> entity" relation in dependency graph
				dependency = architecture._dependencyVertex.LinkToVertex(entity._dependencyVertex)
				dependency["kind"] = DependencyGraphEdgeKind.EntityImplementation

	def LinkPackageBodies(self):
		for packageBodyName, packageBody in self._packageBodies.items():
			if packageBodyName not in self._packages:
				raise Exception(f"Package '{packageBodyName}' referenced by package body '{packageBodyName}' doesn't exist in library '{self.Identifier}'.")

			package = self._packages[packageBodyName]
			packageBody._package.Package = package

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
	"""A ``Document`` represents a sourcefile. It contains primary and secondary design units."""

	_path:                   Path                                  #: path to the document. ``None`` if virtual document.
	_designUnits:            List['DesignUnit']                    #: List of all design units defined in a document.
	_contexts:               Dict[str, 'Context']                  #: Dictionary of all contexts defined in a document.
	_configurations:         Dict[str, 'Configuration']            #: Dictionary of all configurations defined in a document.
	_entities:               Dict[str, 'Entity']                   #: Dictionary of all entities defined in a document.
	_architectures:          Dict[str, Dict[str, 'Architecture']]  #: Dictionary of all architectures defined in a document.
	_packages:               Dict[str, 'Package']                  #: Dictionary of all packages defined in a document.
	_packageBodies:          Dict[str, 'PackageBody']              #: Dictionary of all package bodies defined in a document.
	_verificationUnits:      Dict[str, 'VerificationUnit']         #: Dictionary of all PSL verification units defined in a document.
	_verificationProperties: Dict[str, 'VerificationProperty']     #: Dictionary of all PSL verification properties defined in a document.
	_verificationModes:      Dict[str, 'VerificationMode']         #: Dictionary of all PSL verification modes defined in a document.

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

		self._compileOrderVertex = None

	def _AddEntity(self, item: 'Entity') -> None:
		if not isinstance(item, Entity):
			raise TypeError(f"Parameter 'item' is not of type 'Entity'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._entities:
			raise ValueError(f"An entity '{item.Identifier}' already exists in this document.")

		self._entities[identifier] = item
		self._designUnits.append(item)
		item._parent = self


	def _AddArchitecture(self, item: 'Architecture') -> None:
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

	def _AddPackage(self, item: 'Package') -> None:
		if not isinstance(item, (Package, PackageInstantiation)):
			raise TypeError(f"Parameter 'item' is not of type 'Package' or 'PackageInstantiation'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._packages:
			raise ValueError(f"A package '{item.Identifier}' already exists in this document.")

		self._packages[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddPackageBody(self, item: 'PackageBody') -> None:
		if not isinstance(item, PackageBody):
			raise TypeError(f"Parameter 'item' is not of type 'PackageBody'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._packageBodies:
			raise ValueError(f"A package body '{item.Identifier}' already exists in this document.")

		self._packageBodies[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddContext(self, item: 'Context') -> None:
		if not isinstance(item, Context):
			raise TypeError(f"Parameter 'item' is not of type 'Context'.")

		identifier = item.NormalizedIdentifier
		if identifier in self._contexts:
			raise ValueError(f"A context '{item.Identifier}' already exists in this document.")

		self._contexts[identifier] = item
		self._designUnits.append(item)
		item._parent = self

	def _AddConfiguration(self, item: 'Configuration') -> None:
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
	def DesignUnits(self) -> List['DesignUnit']:
		"""Returns a list of all design units declarations found in this document."""
		return self._designUnits

	@property
	def Contexts(self) -> Dict[str, 'Context']:
		"""Returns a list of all context declarations found in this document."""
		return self._contexts

	@property
	def Configurations(self) -> Dict[str, 'Configuration']:
		"""Returns a list of all configuration declarations found in this document."""
		return self._configurations

	@property
	def Entities(self) -> Dict[str, 'Entity']:
		"""Returns a list of all entity declarations found in this document."""
		return self._entities

	@property
	def Architectures(self) -> Dict[str, Dict[str, 'Architecture']]:
		"""Returns a list of all architecture declarations found in this document."""
		return self._architectures

	@property
	def Packages(self) -> Dict[str, 'Package']:
		"""Returns a list of all package declarations found in this document."""
		return self._packages

	@property
	def PackageBodies(self) -> Dict[str, 'PackageBody']:
		"""Returns a list of all package body declarations found in this document."""
		return self._packageBodies

	@property
	def VerificationUnits(self) -> Dict[str, 'VerificationUnit']:
		"""Returns a list of all verification unit declarations found in this document."""
		return self._verificationUnits

	@property
	def VerificationProperties(self) -> Dict[str, 'VerificationProperty']:
		"""Returns a list of all verification property declarations found in this document."""
		return self._verificationProperties

	@property
	def VerificationModes(self) -> Dict[str, 'VerificationMode']:
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

@export
class Alias(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	def __init__(self, identifier: str, documentation: str = None):
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class BaseType(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""``BaseType`` is the base-class of all type entities in this model."""

	def __init__(self, identifier: str, documentation: str = None):
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class Type(BaseType):
	pass


@export
class FullType(BaseType):
	pass


@export
class Subtype(BaseType):
	_type:               'Subtype'
	_baseType:           BaseType
	_range:              'Range'
	_resolutionFunction: 'Function'

	def __init__(self, identifier: str):
		super().__init__(identifier)

	@property
	def Type(self) -> 'Subtype':
		return self._type

	@property
	def BaseType(self) -> BaseType:
		return self._baseType

	@property
	def Range(self) -> 'Range':
		return self._range

	@property
	def ResolutionFunction(self) -> 'Function':
		return self._resolutionFunction


@export
class AnonymousType(Type):
	pass


@export
class ScalarType(FullType):
	"""A ``ScalarType`` is a base-class for all scalar types."""


@export
class RangedScalarType(ScalarType):
	"""A ``RangedScalarType`` is a base-class for all scalar types with a range."""

	_range:      Union['Range', Name]
	_leftBound:  ExpressionUnion
	_rightBound: ExpressionUnion

	def __init__(self, identifier: str, rng: Union['Range', Name]):
		super().__init__(identifier)
		self._range = rng

	@property
	def Range(self) -> Union['Range', Name]:
		return self._range


@export
class NumericType:
	"""A ``NumericType`` is a mixin class for all numeric types."""

	def __init__(self):
		pass


@export
class DiscreteType:
	"""A ``DiscreteType`` is a mixin class for all discrete types."""

	def __init__(self):
		pass


@export
class CompositeType(FullType):
	"""A ``CompositeType`` is a base-class for all composite types."""


@export
class ProtectedType(FullType):
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, methods: Union[List, Iterator] = None):
		super().__init__(identifier)

		self._methods = []
		if methods is not None:
			for method in methods:
				self._methods.append(method)
				method._parent = self

	@property
	def Methods(self) -> List[Union['Procedure', 'Function']]:
		return self._methods


@export
class ProtectedTypeBody(FullType):
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, declaredItems: Union[List, Iterator] = None):
		super().__init__(identifier)

		self._methods = []
		if declaredItems is not None:
			for method in declaredItems:
				self._methods.append(method)
				method._parent = self

	# FIXME: needs to be declared items or so
	@property
	def Methods(self) -> List[Union['Procedure', 'Function']]:
		return self._methods


@export
class AccessType(FullType):
	_designatedSubtype: SubtypeOrSymbol

	def __init__(self, identifier: str, designatedSubtype: SubtypeOrSymbol):
		super().__init__(identifier)

		self._designatedSubtype = designatedSubtype
		designatedSubtype._parent = self

	@property
	def DesignatedSubtype(self):
		return self._designatedSubtype


@export
class FileType(FullType):
	_designatedSubtype: SubtypeOrSymbol

	def __init__(self, identifier: str, designatedSubtype: SubtypeOrSymbol):
		super().__init__(identifier)

		self._designatedSubtype = designatedSubtype
		designatedSubtype._parent = self

	@property
	def DesignatedSubtype(self):
		return self._designatedSubtype


@export
class EnumeratedType(ScalarType, DiscreteType):
	_literals: List['EnumerationLiteral']

	def __init__(self, identifier: str, literals: Iterable['EnumerationLiteral']):
		super().__init__(identifier)

		self._literals = []
		if literals is not None:
			for literal in literals:
				self._literals.append(literal)
				literal._parent = self

	@property
	def Literals(self) -> List['EnumerationLiteral']:
		return self._literals


@export
class IntegerType(RangedScalarType, NumericType, DiscreteType):
	def __init__(self, identifier: str, rng: Union['Range', Name]):
		super().__init__(identifier, rng)


@export
class RealType(RangedScalarType, NumericType):
	def __init__(self, identifier: str, rng: Union['Range', Name]):
		super().__init__(identifier, rng)


@export
class PhysicalType(RangedScalarType, NumericType):
	_primaryUnit:    str
	_secondaryUnits: List[Tuple[str, 'PhysicalIntegerLiteral']]

	def __init__(self, identifier: str, rng: Union['Range', Name], primaryUnit: str, units: Iterable[Tuple[str, 'PhysicalIntegerLiteral']]):
		super().__init__(identifier, rng)

		self._primaryUnit = primaryUnit

		self._secondaryUnits = []  # TODO: convert to dict
		for unit in units:
			self._secondaryUnits.append(unit)
			unit[1]._parent = self

	@property
	def PrimaryUnit(self) -> str:
		return self._primaryUnit

	@property
	def SecondaryUnits(self) -> List[Tuple[str, 'PhysicalIntegerLiteral']]:
		return self._secondaryUnits


@export
class ArrayType(CompositeType):
	_dimensions:  List['Range']
	_elementType: Subtype

	def __init__(self, identifier: str, indices: List, elementSubtype: SubtypeOrSymbol):
		super().__init__(identifier)

		self._dimensions = []

		self._elementType = elementSubtype
		# elementSubtype._parent = self   # FIXME: subtype is provided as None

	@property
	def Dimensions(self) -> List['Range']:
		return self._dimensions

	@property
	def ElementType(self) -> Subtype:
		return self._elementType


@export
class RecordTypeElement(ModelEntity, MultipleNamedEntityMixin):
	_subtype: SubtypeOrSymbol

	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol):
		super().__init__()
		MultipleNamedEntityMixin.__init__(self, identifiers)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> SubtypeOrSymbol:
		return self._subtype


@export
class RecordType(CompositeType):
	_elements: List[RecordTypeElement]

	def __init__(self, identifier: str, elements: Iterable[RecordTypeElement] = None):
		super().__init__(identifier)

		self._elements = []  # TODO: convert to dict
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element._parent = self

	@property
	def Elements(self) -> List[RecordTypeElement]:
		return self._elements


@export
class BaseExpression(ModelEntity):
	"""A ``BaseExpression`` is a base-class for all expressions."""


@export
class Literal(BaseExpression):
	"""A ``Literal`` is a base-class for all literals."""
# TODO: add a reference to a basetype ?


@export
class NullLiteral(Literal):
	def __str__(self) -> str:
		return "null"


@export
class EnumerationLiteral(Literal):
	_value: str

	def __init__(self, value: str):
		super().__init__()

		self._value = value

	@property
	def Value(self) -> str:
		return self._value

	def __str__(self) -> str:
		return self._value


@export
class NumericLiteral(Literal):
	"""A ``NumericLiteral`` is a base-class for all numeric literals."""


@export
class IntegerLiteral(NumericLiteral):
	_value: int

	def __init__(self, value: int):
		super().__init__()
		self._value = value

	@property
	def Value(self) -> int:
		return self._value

	def __str__(self) -> str:
		return str(self._value)


@export
class FloatingPointLiteral(NumericLiteral):
	_value: float

	def __init__(self, value: float):
		super().__init__()
		self._value = value

	@property
	def Value(self) -> float:
		return self._value

	def __str__(self) -> str:
		return str(self._value)


@export
class PhysicalLiteral(NumericLiteral):
	_unitName: str

	def __init__(self, unitName: str):
		super().__init__()
		self._unitName = unitName

	@property
	def UnitName(self) -> str:
		return self._unitName

	def __str__(self) -> str:
		return f"{self._value} {self._unitName}"


@export
class PhysicalIntegerLiteral(PhysicalLiteral):
	_value: int

	def __init__(self, value: int, unitName: str):
		super().__init__(unitName)
		self._value = value

	@property
	def Value(self) -> int:
		return self._value


@export
class PhysicalFloatingLiteral(PhysicalLiteral):
	_value: float

	def __init__(self, value: float, unitName: str):
		super().__init__(unitName)
		self._value = value

	@property
	def Value(self) -> float:
		return self._value


@export
class CharacterLiteral(Literal):
	_value: str

	def __init__(self, value: str):
		super().__init__()
		self._value = value

	@property
	def Value(self) -> str:
		return self._value

	def __str__(self) -> str:
		return str(self._value)


@export
class StringLiteral(Literal):
	_value: str

	def __init__(self, value: str):
		super().__init__()
		self._value = value

	@property
	def Value(self) -> str:
		return self._value

	def __str__(self) -> str:
		return "\"" + self._value + "\""


@export
class BitStringLiteral(Literal):
	_value: str

	def __init__(self, value: str):
		super().__init__()
		self._value = value

	@property
	def Value(self) -> str:
		return self._value

	def __str__(self) -> str:
		return "\"" + self._value + "\""


@export
class ParenthesisExpression(Protocol):
	@property
	def Operand(self) -> ExpressionUnion:
		return None


@export
class UnaryExpression(BaseExpression):
	"""A ``UnaryExpression`` is a base-class for all unary expressions."""

	_FORMAT:  Tuple[str, str]
	_operand: ExpressionUnion

	def __init__(self, operand: ExpressionUnion):
		super().__init__()

		self._operand = operand
		# operand._parent = self  # FIXME: operand is provided as None

	@property
	def Operand(self):
		return self._operand

	def __str__(self) -> str:
		return f"{self._FORMAT[0]}{self._operand!s}{self._FORMAT[1]}"


@export
class NegationExpression(UnaryExpression):
	_FORMAT = ("-", "")


@export
class IdentityExpression(UnaryExpression):
	_FORMAT = ("+", "")


@export
class InverseExpression(UnaryExpression):
	_FORMAT = ("not ", "")


@export
class AbsoluteExpression(UnaryExpression):
	_FORMAT = ("abs ", "")


@export
class TypeConversion(UnaryExpression):
	pass


@export
class SubExpression(UnaryExpression, ParenthesisExpression):
	_FORMAT = ("(", ")")


@export
class BinaryExpression(BaseExpression):
	"""A ``BinaryExpression`` is a base-class for all binary expressions."""

	_FORMAT: Tuple[str, str, str]
	_leftOperand:  ExpressionUnion
	_rightOperand: ExpressionUnion

	def __init__(self, leftOperand: ExpressionUnion, rightOperand: ExpressionUnion):
		super().__init__()

		self._leftOperand = leftOperand
		leftOperand._parent = self

		self._rightOperand = rightOperand
		rightOperand._parent = self

	@property
	def LeftOperand(self):
		return self._leftOperand

	@property
	def RightOperand(self):
		return self._rightOperand

	def __str__(self) -> str:
		return "{leftOperator}{leftOperand!s}{middleOperator}{rightOperand!s}{rightOperator}".format(
			leftOperator=self._FORMAT[0],
			leftOperand=self._leftOperand,
			middleOperator=self._FORMAT[1],
			rightOperand=self._rightOperand,
			rightOperator=self._FORMAT[2],
		)


@export
class RangeExpression(BinaryExpression):
	_direction: Direction

	@property
	def Direction(self) -> Direction:
		return self._direction


@export
class AscendingRangeExpression(RangeExpression):
	_direction = Direction.To
	_FORMAT = ("", " to ", "")


@export
class DescendingRangeExpression(RangeExpression):
	_direction = Direction.DownTo
	_FORMAT = ("", " downto ", "")


@export
class AddingExpression(BinaryExpression):
	"""A ``AddingExpression`` is a base-class for all adding expressions."""


@export
class AdditionExpression(AddingExpression):
	_FORMAT = ("", " + ", "")


@export
class SubtractionExpression(AddingExpression):
	_FORMAT = ("", " - ", "")


@export
class ConcatenationExpression(AddingExpression):
	_FORMAT = ("", " & ", "")


@export
class MultiplyingExpression(BinaryExpression):
	"""A ``MultiplyingExpression`` is a base-class for all multiplying expressions."""


@export
class MultiplyExpression(MultiplyingExpression):
	_FORMAT = ("", " * ", "")


@export
class DivisionExpression(MultiplyingExpression):
	_FORMAT = ("", " / ", "")


@export
class RemainderExpression(MultiplyingExpression):
	_FORMAT = ("", " rem ", "")


@export
class ModuloExpression(MultiplyingExpression):
	_FORMAT = ("", " mod ", "")


@export
class ExponentiationExpression(MultiplyingExpression):
	_FORMAT = ("", "**", "")


@export
class LogicalExpression(BinaryExpression):
	"""A ``LogicalExpression`` is a base-class for all logical expressions."""


@export
class AndExpression(LogicalExpression):
	_FORMAT = ("", " and ", "")


@export
class NandExpression(LogicalExpression):
	_FORMAT = ("", " nand ", "")


@export
class OrExpression(LogicalExpression):
	_FORMAT = ("", " or ", "")


@export
class NorExpression(LogicalExpression):
	_FORMAT = ("", " nor ", "")


@export
class XorExpression(LogicalExpression):
	_FORMAT = ("", " xor ", "")


@export
class XnorExpression(LogicalExpression):
	_FORMAT = ("", " xnor ", "")


@export
class RelationalExpression(BinaryExpression):
	"""A ``RelationalExpression`` is a base-class for all shifting expressions."""


@export
class EqualExpression(RelationalExpression):
	_FORMAT = ("", " = ", "")


@export
class UnequalExpression(RelationalExpression):
	_FORMAT = ("", " /= ", "")


@export
class GreaterThanExpression(RelationalExpression):
	_FORMAT = ("", " > ", "")


@export
class GreaterEqualExpression(RelationalExpression):
	_FORMAT = ("", " >= ", "")


@export
class LessThanExpression(RelationalExpression):
	_FORMAT = ("", " < ", "")


@export
class LessEqualExpression(RelationalExpression):
	_FORMAT = ("", " <= ", "")


@export
class MatchingRelationalExpression(RelationalExpression):
	pass


@export
class MatchingEqualExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?= ", "")


@export
class MatchingUnequalExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?/= ", "")


@export
class MatchingGreaterThanExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?> ", "")


@export
class MatchingGreaterEqualExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?>= ", "")


@export
class MatchingLessThanExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?< ", "")


@export
class MatchingLessEqualExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?<= ", "")


@export
class ShiftExpression(BinaryExpression):
	"""A ``ShiftExpression`` is a base-class for all shifting expressions."""


@export
class ShiftLogicExpression(ShiftExpression):
	pass


@export
class ShiftArithmeticExpression(ShiftExpression):
	pass


@export
class RotateExpression(ShiftExpression):
	pass


@export
class ShiftRightLogicExpression(ShiftLogicExpression):
	_FORMAT = ("", " srl ", "")


@export
class ShiftLeftLogicExpression(ShiftLogicExpression):
	_FORMAT = ("", " sll ", "")


@export
class ShiftRightArithmeticExpression(ShiftArithmeticExpression):
	_FORMAT = ("", " sra ", "")


@export
class ShiftLeftArithmeticExpression(ShiftArithmeticExpression):
	_FORMAT = ("", " sla ", "")


@export
class RotateRightExpression(RotateExpression):
	_FORMAT = ("", " ror ", "")


@export
class RotateLeftExpression(RotateExpression):
	_FORMAT = ("", " rol ", "")


@export
class QualifiedExpression(BaseExpression, ParenthesisExpression):
	_operand:  ExpressionUnion
	_subtype:  SubtypeOrSymbol

	def __init__(self, subtype: SubtypeOrSymbol, operand: ExpressionUnion):
		super().__init__()

		self._operand = operand
		operand._parent = self

		self._subtype = subtype
		subtype._parent = self

	@property
	def Operand(self):
		return self._operand

	@property
	def Subtyped(self):
		return self._subtype

	def __str__(self) -> str:
		return f"{self._subtype}'({self._operand!s})"


@export
class TernaryExpression(BaseExpression):
	"""A ``TernaryExpression`` is a base-class for all ternary expressions."""

	_FORMAT: Tuple[str, str, str, str]
	_firstOperand:  ExpressionUnion
	_secondOperand: ExpressionUnion
	_thirdOperand:  ExpressionUnion

	def __init__(self):
		super().__init__()

		# FIXME: parameters and initializers are missing !!

	@property
	def FirstOperand(self):
		return self._firstOperand

	@property
	def SecondOperand(self):
		return self._secondOperand

	@property
	def ThirdOperand(self):
		return self._thirdOperand

	def __str__(self) -> str:
		return "{beforeFirstOperator}{firstOperand!s}{beforeSecondOperator}{secondOperand!s}{beforeThirdOperator}{thirdOperand!s}{lastOperator}".format(
			beforeFirstOperator=self._FORMAT[0],
			firstOperand=self._firstOperand,
			beforeSecondOperator=self._FORMAT[1],
			secondOperand=self._secondOperand,
			beforeThirdOperator=self._FORMAT[2],
			thirdOperand=self._thirdOperand,
			lastOperator=self._FORMAT[4],
		)


@export
class WhenElseExpression(TernaryExpression):
	_FORMAT = ("", " when ", " else ", "")


@export
class FunctionCall(BaseExpression):
	pass


@export
class Allocation(BaseExpression):
	pass


@export
class SubtypeAllocation(Allocation):
	_subtype: Symbol

	def __init__(self, subtype: Symbol):
		super().__init__()

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> Symbol:
		return self._subtype

	def __str__(self) -> str:
		return "new {subtype!s}".format(subtype=self._subtype)


@export
class QualifiedExpressionAllocation(Allocation):
	_qualifiedExpression: QualifiedExpression

	def __init__(self, qualifiedExpression: QualifiedExpression):
		super().__init__()

		self._qualifiedExpression = qualifiedExpression
		qualifiedExpression._parent = self

	@property
	def QualifiedExpression(self) -> QualifiedExpression:
		return self._qualifiedExpression

	def __str__(self) -> str:
		return "new {expr!s}".format(expr=self._qualifiedExpression)


@export
class AggregateElement(ModelEntity):
	"""A ``AggregateElement`` is a base-class for all aggregate elements."""

	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion):
		super().__init__()

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self):
		return self._expression


@export
class SimpleAggregateElement(AggregateElement):
	def __str__(self) -> str:
		return str(self._expression)


@export
class IndexedAggregateElement(AggregateElement):
	_index: int

	def __init__(self, index: ExpressionUnion, expression: ExpressionUnion):
		super().__init__(expression)

		self._index = index

	@property
	def Index(self) -> int:
		return self._index

	def __str__(self) -> str:
		return "{index!s} => {value!s}".format(
			index=self._index,
			value=self._expression,
		)


@export
class RangedAggregateElement(AggregateElement):
	_range: 'Range'

	def __init__(self, rng: 'Range', expression: ExpressionUnion):
		super().__init__(expression)

		self._range = rng
		rng._parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return "{range!s} => {value!s}".format(
			range=self._range,
			value=self._expression,
		)


@export
class NamedAggregateElement(AggregateElement):
	_name: Symbol

	def __init__(self, name: Symbol, expression: ExpressionUnion):
		super().__init__(expression)

		self._name = name
		name._parent = self

	@property
	def Name(self) -> Symbol:
		return self._name

	def __str__(self) -> str:
		return "{name!s} => {value!s}".format(
			name=self._name,
			value=self._expression,
		)


@export
class OthersAggregateElement(AggregateElement):
	def __str__(self) -> str:
		return "others => {value!s}".format(
			value=self._expression,
		)


@export
class Aggregate(BaseExpression):
	_elements: List[AggregateElement]

	def __init__(self, elements: Iterable[AggregateElement]):
		super().__init__()

		self._elements = []
		for element in elements:
			self._elements.append(element)
			element._parent = self

	@property
	def Elements(self) -> List[AggregateElement]:
		return self._elements

	def __str__(self) -> str:
		choices = [str(element) for element in self._elements]
		return "({choices})".format(
			choices=", ".join(choices)
		)


@export
class Range(ModelEntity):
	_leftBound:  ExpressionUnion
	_rightBound: ExpressionUnion
	_direction:  Direction

	def __init__(self, leftBound: ExpressionUnion, rightBound: ExpressionUnion, direction: Direction):
		super().__init__()

		self._leftBound = leftBound
		leftBound._parent = self

		self._rightBound = rightBound
		rightBound._parent = self

		self._direction = direction

	@property
	def LeftBound(self) -> ExpressionUnion:
		return self._leftBound

	@property
	def RightBound(self) -> ExpressionUnion:
		return self._rightBound

	@property
	def Direction(self) -> Direction:
		return self._direction

	def __str__(self) -> str:
		return "{leftBound!s} {direction!s} {rightBound!s}".format(
			leftBound=self._leftBound,
			direction=self._direction,
			rightBound=self._rightBound,
		)


@export
class BaseConstraint(ModelEntity):
	pass


# FIXME: Is this used?
@export
class RangeAttribute(BaseConstraint):
	pass


# FIXME: Is this used?
@export
class RangeSubtype(BaseConstraint):
	pass


@export
class Obj(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	_subtype: SubtypeOrSymbol

	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__()
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> SubtypeOrSymbol:
		return self._subtype


@export
class WithDefaultExpressionMixin:
	"""A ``WithDefaultExpression`` is a mixin class for all objects declarations accepting default expressions."""

	_defaultExpression: Nullable[ExpressionUnion]

	def __init__(self, defaultExpression: ExpressionUnion = None):
		self._defaultExpression = defaultExpression
		if defaultExpression is not None:
			defaultExpression._parent = self

	@property
	def DefaultExpression(self) -> Nullable[ExpressionUnion]:
		return self._defaultExpression


@export
class BaseConstant(Obj):
	pass


@export
class Constant(BaseConstant, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class DeferredConstant(BaseConstant):
	_constantReference: Constant

	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)

	@property
	def ConstantReference(self) -> Constant:
		return self._constantReference


@export
class Variable(Obj, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class SharedVariable(Obj):
	pass


@export
class Signal(Obj, WithDefaultExpressionMixin):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class File(Obj):
	pass


@export
class SubProgramm(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	_genericItems:   List['GenericInterfaceItem']
	_parameterItems: List['ParameterInterfaceItem']
	_declaredItems:  List
	_statements:     List['SequentialStatement']
	_isPure:         bool

	def __init__(self, identifier: str, documentation: str = None):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._genericItems =    []  # TODO: convert to dict
		self._parameterItems =  []  # TODO: convert to dict
		self._declaredItems =   []  # TODO: use mixin class
		self._statements =      []  # TODO: use mixin class

	@property
	def GenericItems(self) -> List['GenericInterfaceItem']:
		return self._genericItems

	@property
	def ParameterItems(self) -> List['ParameterInterfaceItem']:
		return self._parameterItems

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems

	@property
	def Statements(self) -> List['SequentialStatement']:
		return self._statements

	@property
	def IsPure(self) -> bool:
		return self._isPure


@export
class Procedure(SubProgramm):
	_isPure: bool = False


@export
class Function(SubProgramm):
	_returnType: Subtype

	def __init__(self, identifier: str, isPure: bool = True, documentation: str = None):
		super().__init__(identifier, documentation)

		self._isPure = isPure
		# FIXME: return type is missing

	@property
	def ReturnType(self) -> Subtype:
		return self._returnType


@export
class Method:
	"""A ``Method`` is a mixin class for all subprograms in a protected type."""

	_protectedType: ProtectedType

	def __init__(self, protectedType: ProtectedType):
		self._protectedType = protectedType
		protectedType._parent = self

	@property
	def ProtectedType(self) -> ProtectedType:
		return self._protectedType


@export
class ProcedureMethod(Procedure, Method):
	def __init__(self, identifier: str, protectedType: ProtectedType):
		super().__init__(identifier)
		Method.__init__(self, protectedType)


@export
class FunctionMethod(Function, Method):
	def __init__(self, identifier: str, protectedType: ProtectedType):
		super().__init__(identifier)
		Method.__init__(self, protectedType)


@export
class Attribute(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	_subtype: SubtypeOrSymbol

	def __init__(self, identifier: str, subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self):
		return self._subtype


@export
class AttributeSpecification(ModelEntity, DocumentedEntityMixin):
	_identifiers: List[Name]
	_attribute: Name
	_entityClass: EntityClass
	_expression: ExpressionUnion

	def __init__(self, identifiers: Iterable[Name], attribute: Name, entityClass: EntityClass, expression: ExpressionUnion, documentation: str = None):
		super().__init__()
		DocumentedEntityMixin.__init__(self, documentation)

		self._identifiers = []  # TODO: convert to dict
		for identifier in identifiers:
			self._identifiers.append(identifier)
			identifier._parent = self

		self._attribute = attribute
		attribute._parent = self

		self._entityClass = entityClass

		self._expression = expression
		expression._parent = self

	@property
	def Identifiers(self) -> List[Name]:
		return self._identifiers

	@property
	def Attribute(self) -> Name:
		return self._attribute

	@property
	def EntityClass(self) -> EntityClass:
		return self._entityClass

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression


@export
class InterfaceItem(DocumentedEntityMixin):
	"""An ``InterfaceItem`` is a base-class for all mixin-classes for all interface items."""

	def __init__(self, documentation: str = None):
		super().__init__(documentation)


@export
class InterfaceItemWithMode:
	"""An ``InterfaceItemWithMode`` is a mixin-class to provide a ``Mode`` to interface items."""

	_mode: Mode

	def __init__(self, mode: Mode):
		self._mode = mode

	@property
	def Mode(self) -> Mode:
		return self._mode


@export
class GenericInterfaceItem(InterfaceItem):
	"""A ``GenericInterfaceItem`` is a mixin class for all generic interface items."""


@export
class PortInterfaceItem(InterfaceItem, InterfaceItemWithMode):
	"""A ``PortInterfaceItem`` is a mixin class for all port interface items."""

	def __init__(self, mode: Mode):
		super().__init__()
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterInterfaceItem(InterfaceItem):
	"""A ``ParameterInterfaceItem`` is a mixin class for all parameter interface items."""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		GenericInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class GenericTypeInterfaceItem(Type, GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class GenericSubprogramInterfaceItem(GenericInterfaceItem):
	pass


@export
class GenericProcedureInterfaceItem(Procedure, GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class GenericFunctionInterfaceItem(Function, GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class GenericPackageInterfaceItem(GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		#	super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class PortSignalInterfaceItem(Signal, PortInterfaceItem):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		PortInterfaceItem.__init__(self, mode)


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		ParameterInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		ParameterInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: SubtypeOrSymbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		ParameterInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItem):
	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		ParameterInterfaceItem.__init__(self)


@export
class AssociationItem(ModelEntity):
	_formal: Name
	_actual: ExpressionUnion

	def __init__(self, actual: ExpressionUnion, formal: Name = None):
		super().__init__()

		self._formal = formal
		if formal is not None:
			formal._parent = self

		self._actual = actual
		# actual._parent = self  # FIXME: actual is provided as None

	@property
	def Formal(self) -> Name:  # TODO: can also be a conversion function !!
		return self._formal

	@property
	def Actual(self) -> ExpressionUnion:
		return self._actual

	def __str__(self):
		if self._formal is None:
			return str(self._actual)
		else:
			return "{formal!s} => {actual!s}".format(formal=self._formal, actual=self._actual)


@export
class GenericAssociationItem(AssociationItem):
	pass


@export
class PortAssociationItem(AssociationItem):
	pass


@export
class ParameterAssociationItem(AssociationItem):
	pass


@export
class GenericEntityInstantiation:
	def __init__(self):
		pass


@export
class SubprogramInstantiation(ModelEntity, GenericEntityInstantiation):
	def __init__(self):
		super().__init__()
		GenericEntityInstantiation.__init__(self)
		self._subprogramReference = None


@export
class ProcedureInstantiation(Procedure, SubprogramInstantiation):
	pass


@export
class FunctionInstantiation(Function, SubprogramInstantiation):
	pass


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
	_package:           PackageSymbol
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
class PackageInstantiation(PrimaryUnit, GenericEntityInstantiation):
	_packageReference:    PackageReferenceSymbol
	_genericAssociations: List[GenericAssociationItem]

	def __init__(self, identifier: str, uninstantiatedPackage: PackageReferenceSymbol, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericEntityInstantiation.__init__(self)

		self._packageReference = uninstantiatedPackage
		# uninstantiatedPackage._parent = self    # FIXME: uninstantiatedPackage is provided as int

		# TODO: extract to mixin
		self._genericAssociations = []

	@property
	def PackageReference(self) -> PackageReferenceSymbol:
		return self._packageReference

	@property
	def GenericAssociations(self) -> List[GenericAssociationItem]:
		return self._genericAssociations


@export
class Statement(ModelEntity, LabeledEntityMixin):
	def __init__(self, label: str = None):
		super().__init__()
		LabeledEntityMixin.__init__(self, label)


@export
class ConcurrentStatement(Statement):
	"""A ``ConcurrentStatement`` is a base-class for all concurrent statements."""


@export
class SequentialStatement(Statement):
	"""A ``SequentialStatement`` is a base-class for all sequential statements."""


# FIXME: Why not used in package, package body
@export
class ConcurrentDeclarations:
	_declaredItems: List  # FIXME: define list prefix type e.g. via Union

	def __init__(self, declaredItems: Iterable = None):
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class ConcurrentStatements:
	_statements:     List[ConcurrentStatement]

	_instantiations: Dict[str, 'Instantiation']  # TODO: add another instantiation class level for entity/configuration/component inst.
	_blocks:         Dict[str, 'ConcurrentBlockStatement']
	_generates:      Dict[str, 'GenerateStatement']
	_hierarchy:      Dict[str, Union['ConcurrentBlockStatement', 'GenerateStatement']]

	def __init__(self, statements: Iterable[ConcurrentStatement] = None):
		self._statements = []

		self._instantiations = {}
		self._blocks = {}
		self._generates = {}
		self._hierarchy = {}

		if statements is not None:
			for statement in statements:
				self._statements.append(statement)
				statement._parent = self

	@property
	def Statements(self) -> List[ConcurrentStatement]:
		return self._statements

	def IterateInstantiations(self) -> Generator['Instantiation', None, None]:
		for instance in self._instantiations.values():
			yield instance

		for block in self._blocks.values():
			yield from block.IterateInstantiations()

		for generate in self._generates.values():
			yield from generate.IterateInstantiations()

	# TODO: move into _init__
	def Index(self):
		for statement in self._statements:
			if isinstance(statement, EntityInstantiation):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, ComponentInstantiation):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, ConfigurationInstantiation):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, ForGenerateStatement):
				self._generates[statement.NormalizedLabel] = statement
				statement.Index()
			elif isinstance(statement, IfGenerateStatement):
				self._generates[statement.NormalizedLabel] = statement
				statement.Index()
			elif isinstance(statement, CaseGenerateStatement):
				self._generates[statement.NormalizedLabel] = statement
				statement.Index()
			elif isinstance(statement, ConcurrentBlockStatement):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.Index()


@export
class SequentialDeclarations:
	_declaredItems: List

	def __init__(self, declaredItems: Iterable):
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class SequentialStatements:
	_statements: List[SequentialStatement]

	def __init__(self, statements: Iterable[SequentialStatement] = None):
		# TODO: extract to mixin
		self._statements = []
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item._parent = self

	@property
	def Statements(self) -> List[SequentialStatement]:
		return self._statements


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
					raise Exception()

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
	_library:       Library = None
	_entity:        EntitySymbol

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


@export
class Instantiation(ConcurrentStatement):
	_genericAssociations: List[AssociationItem]
	_portAssociations: List[AssociationItem]

	def __init__(self, label: str, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label)

		# TODO: extract to mixin
		self._genericAssociations = []
		if genericAssociations is not None:
			for association in genericAssociations:
				self._genericAssociations.append(association)
				association._parent = self

		# TODO: extract to mixin
		self._portAssociations = []
		if portAssociations is not None:
			for association in portAssociations:
				self._portAssociations.append(association)
				association._parent = self

	@property
	def GenericAssociations(self) -> List[AssociationItem]:
		return self._genericAssociations

	@property
	def PortAssociations(self) -> List[AssociationItem]:
		return self._portAssociations


@export
class ComponentInstantiation(Instantiation):
	_component: ComponentInstantiationSymbol

	def __init__(self, label: str, componentSymbol: ComponentInstantiationSymbol, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label, genericAssociations, portAssociations)

		self._component = componentSymbol
		componentSymbol._parent = self

	@property
	def Component(self) -> ComponentInstantiationSymbol:
		return self._component


@export
class EntityInstantiation(Instantiation):
	_entity:       EntityInstantiationSymbol
	_architecture: ArchitectureSymbol

	def __init__(self, label: str, entitySymbol: EntityInstantiationSymbol, architectureSymbol: ArchitectureSymbol = None, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label, genericAssociations, portAssociations)

		self._entity = entitySymbol
		entitySymbol._parent = self

		self._architecture = architectureSymbol
		if architectureSymbol is not None:
			architectureSymbol._parent = self

	@property
	def Entity(self) -> EntityInstantiationSymbol:
		return self._entity

	@property
	def Architecture(self) -> ArchitectureSymbol:
		return self._architecture


@export
class ConfigurationInstantiation(Instantiation):
	_configuration: ConfigurationInstantiationSymbol

	def __init__(self, label: str, configurationSymbol: ConfigurationInstantiationSymbol, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label, genericAssociations, portAssociations)

		self._configuration = configurationSymbol
		configurationSymbol._parent = self

	@property
	def Configuration(self) -> ConfigurationInstantiationSymbol:
		return self._configuration


@export
class ProcessStatement(ConcurrentStatement, SequentialDeclarations, SequentialStatements, DocumentedEntityMixin):
	_sensitivityList: List[Name]  # TODO: implement a SignalSymbol

	def __init__(
		self,
		label: str = None,
		declaredItems: Iterable = None,
		statements: Iterable[SequentialStatement] = None,
		sensitivityList: Iterable[Name] = None,
		documentation: str = None
	):
		super().__init__(label)
		SequentialDeclarations.__init__(self, declaredItems)
		SequentialStatements.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				# signalSymbol._parent = self  # FIXME: currently str are provided

	@property
	def SensitivityList(self) -> List[Name]:
		return self._sensitivityList


@export
class ProcedureCall:
	_procedure: Name  # TODO: implement a ProcedureSymbol
	_parameterMappings: List[ParameterAssociationItem]

	def __init__(self, procedureName: Name, parameterMappings: Iterable[ParameterAssociationItem] = None):
		self._procedure = procedureName
		procedureName._parent = self

		# TODO: extract to mixin
		self._parameterMappings = []
		if parameterMappings is not None:
			for parameterMapping in parameterMappings:
				self._parameterMappings.append(parameterMapping)
				parameterMapping._parent = self

	@property
	def Procedure(self) -> Name:
		return self._procedure

	@property
	def ParameterMappings(self) -> List[ParameterAssociationItem]:
		return self._parameterMappings


@export
class ConcurrentProcedureCall(ConcurrentStatement, ProcedureCall):
	def __init__(self, label: str, procedureName: Name, parameterMappings: Iterable[ParameterAssociationItem] = None):
		super().__init__(label)
		ProcedureCall.__init__(self, procedureName, parameterMappings)


@export
class SequentialProcedureCall(SequentialStatement, ProcedureCall):
	def __init__(self, procedureName: Name, parameterMappings: Iterable[ParameterAssociationItem] = None, label: str = None):
		super().__init__(label)
		ProcedureCall.__init__(self, procedureName, parameterMappings)


# TODO: could be unified with ProcessStatement if 'List[ConcurrentStatement]' becomes parametric to T
class BlockStatement:
	"""A ``BlockStatement`` is a mixin-class for all block statements."""

	def __init__(self):
		pass


@export
class ConcurrentBlockStatement(ConcurrentStatement, BlockStatement, LabeledEntityMixin, ConcurrentDeclarations, ConcurrentStatements, DocumentedEntityMixin):
	_portItems:     List[PortInterfaceItem]

	def __init__(
		self,
		label: str,
		portItems: Iterable[PortInterfaceItem] = None,
		declaredItems: Iterable = None,
		statements: Iterable['ConcurrentStatement'] = None,
		documentation: str = None
	):
		super().__init__(label)
		BlockStatement.__init__(self)
		LabeledEntityMixin.__init__(self, label)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		# TODO: extract to mixin
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item._parent = self

	@property
	def PortItems(self) -> List[PortInterfaceItem]:
		return self._portItems


@export
class MixinConditional:
	"""A ``BaseConditional`` is a mixin-class for all statements with a condition."""

	_condition: ExpressionUnion

	def __init__(self, condition: ExpressionUnion = None):
		self._condition = condition
		if condition is not None:
			condition._parent = self

	@property
	def Condition(self) -> ExpressionUnion:
		return self._condition


@export
class MixinBranch:
	"""A ``BaseBranch`` is a mixin-class for all statements with branches."""

	def __init__(self):
		pass


@export
class MixinConditionalBranch(MixinBranch, MixinConditional):
	"""A ``BaseBranch`` is a mixin-class for all branch statements with a condition."""
	def __init__(self, condition: ExpressionUnion):
		super().__init__()
		MixinConditional.__init__(self, condition)


@export
class MixinIfBranch(MixinConditionalBranch):
	"""A ``BaseIfBranch`` is a mixin-class for all if-branches."""


@export
class MixinElsifBranch(MixinConditionalBranch):
	"""A ``BaseElsifBranch`` is a mixin-class for all elsif-branches."""


@export
class MixinElseBranch(MixinBranch):
	"""A ``BaseElseBranch`` is a mixin-class for all else-branches."""


@export
class GenerateBranch(ModelEntity, ConcurrentDeclarations, ConcurrentStatements):
	"""A ``GenerateBranch`` is a base-class for all branches in a generate statements."""

	_alternativeLabel:           Nullable[str]
	_normalizedAlternativeLabel: Nullable[str]

	def __init__(self, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__()
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)

		self._alternativeLabel = alternativeLabel
		self._normalizedAlternativeLabel = alternativeLabel.lower() if alternativeLabel is not None else None

	@property
	def AlternativeLabel(self) -> Nullable[str]:
		return self._alternativeLabel

	@property
	def NormalizedAlternativeLabel(self) -> Nullable[str]:
		return self._normalizedAlternativeLabel


@export
class IfGenerateBranch(GenerateBranch, MixinIfBranch):
	def __init__(self, condition: ExpressionUnion, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)
		MixinIfBranch.__init__(self, condition)


@export
class ElsifGenerateBranch(GenerateBranch, MixinElsifBranch):
	def __init__(self, condition: ExpressionUnion, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)
		MixinElsifBranch.__init__(self, condition)


@export
class ElseGenerateBranch(GenerateBranch, MixinElseBranch):
	def __init__(self, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)
		MixinElseBranch.__init__(self)


@export
class GenerateStatement(ConcurrentStatement):
	"""A ``GenerateStatement`` is a base-class for all generate statements."""

	def __init__(self, label: str = None):
		super().__init__(label)

	# @mustoverride
	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		raise NotImplementedError()

	# @mustoverride
	def Index(self) -> None:
		raise NotImplementedError()


@export
class IfGenerateStatement(GenerateStatement):
	_ifBranch:      IfGenerateBranch
	_elsifBranches: List[ElsifGenerateBranch]
	_elseBranch:    Nullable[ElseGenerateBranch]

	def __init__(self, label: str, ifBranch: IfGenerateBranch, elsifBranches: Iterable[ElsifGenerateBranch] = None, elseBranch: ElseGenerateBranch = None):
		super().__init__(label)

		self._ifBranch = ifBranch
		ifBranch._parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch._parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch._parent = self
		else:
			self._elseBranch = None

	@property
	def IfBranch(self) -> IfGenerateBranch:
		return self._ifBranch

	@property
	def ElsifBranches(self) -> List[ElsifGenerateBranch]:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> Nullable[ElseGenerateBranch]:
		return self._elseBranch

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		yield from self._ifBranch.IterateInstantiations()
		for branch in self._elsifBranches:
			yield from branch.IterateInstantiations()
		if self._elseBranch is not None:
			yield from self._ifBranch.IterateInstantiations()

	def Index(self) -> None:
		self._ifBranch.Index()
		for branch in self._elsifBranches:
			branch.Index()
		if self._elseBranch is not None:
			self._elseBranch.Index()


@export
class Choice(ModelEntity):
	"""A ``Choice`` is a base-class for all choices."""


@export
class ConcurrentChoice(Choice):
	"""A ``ConcurrentChoice`` is a base-class for all concurrent choices (in case...generate statements)."""


@export
class SequentialChoice(Choice):
	"""A ``SequentialChoice`` is a base-class for all sequential choices (in case statements)."""


@export
class BaseCase(ModelEntity):
	"""
	A ``Case`` is a base-class for all cases.
	"""


@export
class ConcurrentCase(BaseCase, LabeledEntityMixin, ConcurrentDeclarations, ConcurrentStatements):
	def __init__(self, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__()
		LabeledEntityMixin.__init__(self, alternativeLabel)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)


@export
class SequentialCase(BaseCase, SequentialStatements):
	_choices: List

	def __init__(self, statements: Iterable[SequentialStatement] = None):
		super().__init__()
		SequentialStatements.__init__(self, statements)

		# TODO: what about choices?

	@property
	def Choices(self) -> List[Choice]:
		return self._choices


@export
class GenerateCase(ConcurrentCase):
	_choices: List[ConcurrentChoice]

	def __init__(self, choices: Iterable[ConcurrentChoice], declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)

		# TODO: move to parent or grandparent
		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice._parent = self

	# TODO: move to parent or grandparent
	@property
	def Choices(self) -> List[ConcurrentChoice]:
		return self._choices

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join([str(c) for c in self._choices]))


@export
class OthersGenerateCase(ConcurrentCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class IndexedGenerateChoice(ConcurrentChoice):
	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion):
		super().__init__()

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	def __str__(self) -> str:
		return "{expression!s}".format(expression=self._expression)


@export
class RangedGenerateChoice(ConcurrentChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range'):
		super().__init__()

		self._range = rng
		rng._parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return "{range!s}".format(range=self._range)


@export
class CaseGenerateStatement(GenerateStatement):
	_expression: ExpressionUnion
	_cases:      List[GenerateCase]

	def __init__(self, label: str, expression: ExpressionUnion, cases: Iterable[ConcurrentCase]):
		super().__init__(label)

		self._expression = expression
		expression._parent = self

		# TODO: create a mixin for things with cases
		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case._parent = self

	@property
	def SelectExpression(self) -> ExpressionUnion:
		return self._expression

	@property
	def Cases(self) -> List[GenerateCase]:
		return self._cases

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		for case in self._cases:
			yield from case.IterateInstantiations()

	def Index(self):
		for case in self._cases:
			case.Index()


@export
class ForGenerateStatement(GenerateStatement, ConcurrentDeclarations, ConcurrentStatements):
	_loopIndex: str
	_range:     Range

	def __init__(self, label: str, loopIndex: str, rng: Range, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None):
		super().__init__(label)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)

		self._loopIndex = loopIndex

		self._range = rng
		rng._parent = self

	@property
	def LoopIndex(self) -> str:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range

	IterateInstantiations = ConcurrentStatements.IterateInstantiations

	Index = ConcurrentStatements.Index

	# def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
	# 	return ConcurrentStatements.IterateInstantiations(self)
	#
	# def Index(self) -> None:
	# 	return ConcurrentStatements.Index(self)


@export
class Assignment:
	"""An ``Assignment`` is a base-class for all assignment statements."""

	_target:     Name

	def __init__(self, target: Name):
		self._target = target
		target._parent = self

	@property
	def Target(self) -> Name:
		return self._target


@export
class SignalAssignment(Assignment):
	"""An ``SignalAssignment`` is a base-class for all signal assignment statements."""


@export
class VariableAssignment(Assignment):
	"""An ``VariableAssignment`` is a base-class for all variable assignment statements."""

	_expression: ExpressionUnion

	def __init__(self, target: Name, expression: ExpressionUnion):
		super().__init__(target)

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression


@export
class WaveformElement(ModelEntity):
	_expression: ExpressionUnion
	_after: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, after: ExpressionUnion = None):
		super().__init__()

		self._expression = expression
		expression._parent = self

		self._after = after
		if after is not None:
			after._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	@property
	def After(self) -> Expression:
		return self._after


@export
class ConcurrentSignalAssignment(ConcurrentStatement, SignalAssignment):
	def __init__(self, label: str, target: Name):
		super().__init__(label)
		SignalAssignment.__init__(self, target)


@export
class ConcurrentSimpleSignalAssignment(ConcurrentSignalAssignment):
	_waveform: List[WaveformElement]

	def __init__(self, label: str, target: Name, waveform: Iterable[WaveformElement]):
		super().__init__(label, target)

		# TODO: extract to mixin
		self._waveform = []
		if waveform is not None:
			for waveformElement in waveform:
				self._waveform.append(waveformElement)
				waveformElement._parent = self

	@property
	def Waveform(self) -> List[WaveformElement]:
		return self._waveform


@export
class ConcurrentSelectedSignalAssignment(ConcurrentSignalAssignment):
	def __init__(self, label: str, target: Name, expression: ExpressionUnion):
		super().__init__(label, target)


@export
class ConcurrentConditionalSignalAssignment(ConcurrentSignalAssignment):
	def __init__(self, label: str, target: Name, expression: ExpressionUnion):
		super().__init__(label, target)



@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignment):
	def __init__(self, target: Name, label: str = None):
		super().__init__(label)
		SignalAssignment.__init__(self, target)


@export
class SequentialSimpleSignalAssignment(SequentialSignalAssignment):
	_waveform: List[WaveformElement]

	def __init__(self, target: Name, waveform: Iterable[WaveformElement], label: str = None):
		super().__init__(target, label)

		# TODO: extract to mixin
		self._waveform = []
		if waveform is not None:
			for waveformElement in waveform:
				self._waveform.append(waveformElement)
				waveformElement._parent = self

	@property
	def Waveform(self) -> List[WaveformElement]:
		return self._waveform


@export
class SequentialVariableAssignment(SequentialStatement, VariableAssignment):
	def __init__(self, target: Name, expression: ExpressionUnion, label: str = None):
		super().__init__(label)
		VariableAssignment.__init__(self, target, expression)


@export
class MixinReportStatement:
	"""A ``MixinReportStatement`` is a mixin-class for all report and assert statements."""

	_message:  Nullable[ExpressionUnion]
	_severity: Nullable[ExpressionUnion]

	def __init__(self, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		self._message = message
		if message is not None:
			message._parent = self

		self._severity = severity
		if severity is not None:
			severity._parent = self

	@property
	def Message(self) -> Nullable[ExpressionUnion]:
		return self._message

	@property
	def Severity(self) -> Nullable[ExpressionUnion]:
		return self._severity


@export
class MixinAssertStatement(MixinReportStatement):
	"""A ``MixinAssertStatement`` is a mixin-class for all assert statements."""

	_condition: ExpressionUnion

	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		super().__init__(message, severity)

		self._condition = condition
		if condition is not None:
			condition._parent = self

	@property
	def Condition(self) -> ExpressionUnion:
		return self._condition


@export
class ConcurrentAssertStatement(ConcurrentStatement, MixinAssertStatement):
	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinAssertStatement.__init__(self, condition, message, severity)


@export
class SequentialReportStatement(SequentialStatement, MixinReportStatement):
	def __init__(self, message: ExpressionUnion, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinReportStatement.__init__(self, message, severity)


@export
class SequentialAssertStatement(SequentialStatement, MixinAssertStatement):
	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinAssertStatement.__init__(self, condition, message, severity)


@export
class Branch(ModelEntity, SequentialStatements):
	"""A ``Branch`` is a base-class for all branches in a if statement."""

	def __init__(self, statements: Iterable[ConcurrentStatement] = None):
		super().__init__()
		SequentialStatements.__init__(self, statements)


@export
class IfBranch(Branch, MixinIfBranch):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[ConcurrentStatement] = None):
		super().__init__(statements)
		MixinIfBranch.__init__(self, condition)


@export
class ElsifBranch(Branch, MixinElsifBranch):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[ConcurrentStatement] = None):
		super().__init__(statements)
		MixinElsifBranch.__init__(self, condition)


@export
class ElseBranch(Branch, MixinElseBranch):
	def __init__(self, statements: Iterable[ConcurrentStatement] = None):
		super().__init__(statements)
		MixinElseBranch.__init__(self)


@export
class CompoundStatement(SequentialStatement):
	"""A ``CompoundStatement`` is a base-class for all compound statements."""


@export
class IfStatement(CompoundStatement):
	_ifBranch: IfBranch
	_elsifBranches: List['ElsifBranch']
	_elseBranch: Nullable[ElseBranch]

	def __init__(self, ifBranch: IfBranch, elsifBranches: Iterable[ElsifBranch] = None, elseBranch: ElseBranch = None, label: str = None):
		super().__init__(label)

		self._ifBranch = ifBranch
		ifBranch._parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch._parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch._parent = self
		else:
			self._elseBranch = None

	@property
	def IfBranch(self) -> IfBranch:
		return self._ifBranch

	@property
	def ElsIfBranches(self) -> List['ElsifBranch']:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> Nullable[ElseBranch]:
		return self._elseBranch


@export
class Case(SequentialCase):
	_choices: List[SequentialChoice]

	def __init__(self, choices: Iterable[SequentialChoice], statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)

		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice._parent = self

	@property
	def Choices(self) -> List[SequentialChoice]:
		return self._choices

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join([str(c) for c in self._choices]))


@export
class OthersCase(SequentialCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class IndexedChoice(SequentialChoice):
	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion):
		super().__init__()

		self._expression = expression
		# expression._parent = self    # FIXME: received None

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	def __str__(self) -> str:
		return "{expression!s}".format(expression=self._expression)


@export
class RangedChoice(SequentialChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range'):
		super().__init__()

		self._range = rng
		rng._parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return "{range!s}".format(range=self._range)


@export
class CaseStatement(CompoundStatement):
	_expression: ExpressionUnion
	_cases:      List[SequentialCase]

	def __init__(self, expression: ExpressionUnion, cases: Iterable[SequentialCase], label: str = None):
		super().__init__(label)

		self._expression = expression
		expression._parent = self

		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case._parent = self

	@property
	def SelectExpression(self) -> ExpressionUnion:
		return self._expression

	@property
	def Cases(self) -> List[SequentialCase]:
		return self._cases


@export
class LoopStatement(CompoundStatement, SequentialStatements):
	"""A ``LoopStatement`` is a base-class for all loop statements."""

	def __init__(self, statements: Iterable[ConcurrentStatement] = None, label: str = None):
		super().__init__(label)
		SequentialStatements.__init__(self, statements)


@export
class EndlessLoopStatement(LoopStatement):
	pass


@export
class ForLoopStatement(LoopStatement):
	_loopIndex: str
	_range:     Range

	def __init__(self, loopIndex: str, rng: Range, statements: Iterable[ConcurrentStatement] = None, label: str = None):
		super().__init__(statements, label)

		self._loopIndex = loopIndex

		self._range = rng
		rng._parent = self

	@property
	def LoopIndex(self) -> str:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range


@export
class WhileLoopStatement(LoopStatement, MixinConditional):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[ConcurrentStatement] = None, label: str = None):
		super().__init__(statements, label)
		MixinConditional.__init__(self, condition)


@export
class LoopControlStatement(SequentialStatement, MixinConditional):
	"""A ``LoopControlStatement`` is a base-class for all loop controlling statements."""

	_loopReference: LoopStatement

	def __init__(self, condition: ExpressionUnion = None, loopLabel: str = None): # TODO: is this label (currently str) a Name or a Label class?
		super().__init__()
		MixinConditional.__init__(self, condition)

		# TODO: loopLabel
		# TODO: loop reference -> is it a symbol?

	@property
	def LoopReference(self) -> LoopStatement:
		return self._loopReference


@export
class NextStatement(LoopControlStatement):
	pass


@export
class ExitStatement(LoopControlStatement):
	pass


@export
class NullStatement(SequentialStatement):
	pass


@export
class WaitStatement(SequentialStatement, MixinConditional):
	_sensitivityList: Nullable[List[Name]]
	_timeout:         ExpressionUnion

	def __init__(self, sensitivityList: Iterable[Name] = None, condition: ExpressionUnion = None, timeout: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinConditional.__init__(self, condition)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				signalSymbol._parent = self

		self._timeout = timeout
		if timeout is not None:
			timeout._parent = self

	@property
	def SensitivityList(self) -> List[Name]:
		return self._sensitivityList

	@property
	def Timeout(self) -> ExpressionUnion:
		return self._timeout


@export
class ReturnStatement(SequentialStatement, MixinConditional):
	_returnValue: ExpressionUnion

	def __init__(self, returnValue: ExpressionUnion = None):
		super().__init__()
		MixinConditional.__init__(self, returnValue)

		# TODO: return value?

	@property
	def ReturnValue(self) -> ExpressionUnion:
		return self._returnValue
