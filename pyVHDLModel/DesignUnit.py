from typing import List, Dict, Union, Iterable

from pyTooling.Decorators import export

from pyVHDLModel import PrimaryUnit, DesignUnitWithContextMixin, SecondaryUnit, ContextUnion, LibraryClause, UseClause, ContextReference, ModelEntity, \
	NamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Symbol import PackageSymbol, EntitySymbol
from pyVHDLModel.Interface import GenericInterfaceItem, PortInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Object import Constant, Variable, Signal
from pyVHDLModel.Type import Type, Subtype
from pyVHDLModel.Concurrent import ConcurrentStatement, ConcurrentStatements, ConcurrentDeclarations


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
