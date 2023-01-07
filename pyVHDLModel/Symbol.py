from typing import cast

from pyTooling.Decorators import export

from pyVHDLModel import NewSymbol, PossibleReference
from pyVHDLModel.Name import Name, SimpleName, SelectedName, AllName


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
