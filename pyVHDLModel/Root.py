from pathlib import Path
from typing import Dict, List, Generator, Union

from pyTooling.Decorators import export
from pyTooling.Graph import Graph, Vertex

from pyVHDLModel import ModelEntity, DesignUnit, DesignUnitKind, DependencyGraphVertexKind, DependencyGraphEdgeKind, PrimaryUnit, NamedEntityMixin, \
	DocumentedEntityMixin
from pyVHDLModel.Concurrent import EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation
from pyVHDLModel.DesignUnit import Architecture, PackageBody, Context, Entity, Configuration, Package
from pyVHDLModel.Exception import LibraryExistsInDesignError, LibraryRegisteredToForeignDesignError, LibraryNotRegisteredError, EntityExistsInLibraryError, \
	ArchitectureExistsInLibraryError, PackageExistsInLibraryError, PackageBodyExistsError, ConfigurationExistsInLibraryError, ContextExistsInLibraryError, \
	ReferencedLibraryNotExistingError
from pyVHDLModel.PSLModel import VerificationUnit, VerificationProperty, VerificationMode
from pyVHDLModel.Symbol import AllPackageMembersReferenceSymbol, PackageMembersReferenceSymbol
from pyVHDLModel.SyntaxModel import PackageInstantiation


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

	def _LoadLibrary(self, library: 'Library') -> None:
		libraryIdentifier = library.NormalizedIdentifier
		if libraryIdentifier in self._libraries:
			raise LibraryExistsInDesignError(library)

		self._libraries[libraryIdentifier] = library
		library._parent = self

	def LoadStdLibrary(self) -> 'Library':
		from pyVHDLModel.STD import Std

		library = Std()
		self._LoadLibrary(library)

		return library

	def LoadIEEELibrary(self) -> 'Library':
		from pyVHDLModel.IEEE import Ieee

		library = Ieee()
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
