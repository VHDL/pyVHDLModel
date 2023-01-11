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

Symbols derived from names.
"""
from enum import Flag, auto
from typing import cast, Any, Iterable

from pyTooling.Decorators import export

from pyVHDLModel.Base import ExpressionUnion
from pyVHDLModel.Name import Name, SimpleName, SelectedName, AllName, IndexedName


@export
class PossibleReference(Flag):
	"""
	A ``PossibleReference`` is an enumeration. It represents possible targets for a reference in a :class:`~pyVHDLModel.Symbol`.
	"""

	Unknown =         0
	Library =         auto()  #: Library
	Entity =          auto()  #: Entity
	Architecture =    auto()  #: Architecture
	Component =       auto()  #: Component
	Package =         auto()  #: Package
	Configuration =   auto()  #: Configuration
	Context =         auto()  #: Context
	Type =            auto()  #: Type
	Subtype =         auto()  #: Subtype
	ScalarType =      auto()  #: ScalarType
	ArrayType =       auto()  #: ArrayType
	RecordType =      auto()  #: RecordType
	AccessType =      auto()  #: AccessType
	ProtectedType =   auto()  #: ProtectedType
	FileType =        auto()  #: FileType
#	Alias =           auto()   # TODO: Is this needed?
	Attribute =       auto()  #: Attribute
	TypeAttribute =   auto()  #: TypeAttribute
	ValueAttribute =  auto()  #: ValueAttribute
	SignalAttribute = auto()  #: SignalAttribute
	RangeAttribute =  auto()  #: RangeAttribute
	ViewAttribute =   auto()  #: ViewAttribute
	Constant =        auto()  #: Constant
	Variable =        auto()  #: Variable
	Signal =          auto()  #: Signal
	File =            auto()  #: File
#	Object =          auto()   # TODO: Is this needed?
	EnumLiteral =     auto()  #: EnumLiteral
	Procedure =       auto()  #: Procedure
	Function =        auto()  #: Function
	Label =           auto()  #: Label
	View =            auto()  #: View

	AnyType = ScalarType | ArrayType | RecordType | ProtectedType | AccessType | FileType | Subtype  #: Any possible type incl. subtypes.
	Object = Constant | Variable | Signal | File                                                     #: Any object
	SubProgram = Procedure | Function                                                                #: Any subprogram
	PackageMember = AnyType | Object | SubProgram | Component                                        #: Any member of a package
	SimpleNameInExpression = Constant | Variable | Signal | ScalarType | EnumLiteral | Function      #: Any possible item in an expression.


@export
class Symbol:
	_possibleReferences: PossibleReference
	_reference: Any

	def __init__(self, possibleReferences: PossibleReference):
		self._possibleReferences = possibleReferences
		self._reference = None

	@property
	def Reference(self) -> Any:
		return self._reference

	@property
	def IsResolved(self) -> bool:
		return self._reference is not None

	def __bool__(self) -> bool:
		return self._reference is not None

	def __str__(self) -> str:
		if self._reference is not None:
			return str(self._reference)
		return str(self._symbolName)


@export
class LibraryReferenceSymbol(SimpleName, Symbol):
	"""A library reference in a library clause."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Library)

	@property
	def Library(self) -> 'Library':
		return self._reference

	@Library.setter
	def Library(self, value: 'Library') -> None:
		self._reference = value


@export
class PackageReferenceSymbol(SelectedName, Symbol):
	"""A package reference in a use clause."""

	def __init__(self, identifier: str, prefix: LibraryReferenceSymbol):
		super().__init__(identifier, prefix)
		Symbol.__init__(self, PossibleReference.Package)

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
class PackageMembersReferenceSymbol(SelectedName, Symbol):
	"""A package member reference in a use clause."""

	def __init__(self, identifier: str, prefix: PackageReferenceSymbol):
		super().__init__(identifier, prefix)
		Symbol.__init__(self, PossibleReference.PackageMember)

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
class AllPackageMembersReferenceSymbol(AllName, Symbol):
	"""A package reference in a use clause."""

	def __init__(self, prefix: PackageReferenceSymbol):
		super().__init__(prefix)
		Symbol.__init__(self, PossibleReference.PackageMember)

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
class ContextReferenceSymbol(SelectedName, Symbol):
	"""A context reference in a context clause."""

	def __init__(self, identifier: str, prefix: LibraryReferenceSymbol):
		super().__init__(identifier, prefix)
		Symbol.__init__(self, PossibleReference.Context)

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
class EntitySymbol(SimpleName, Symbol):
	"""An entity reference in an architecture declaration."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Entity)

	@property
	def Entity(self) -> 'Entity':
		return self._reference

	@Entity.setter
	def Entity(self, value: 'Entity') -> None:
		self._reference = value


@export
class ArchitectureSymbol(Name, Symbol):
	"""An entity reference in an entity instantiation with architecture name."""

	def __init__(self, identifier: str, prefix: EntitySymbol):
		super().__init__(identifier, prefix)
		Symbol.__init__(self, PossibleReference.Architecture)

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
class PackageSymbol(SimpleName, Symbol):
	"""A package reference in a package body declaration."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Package)

	@property
	def Package(self) -> 'Package':
		return self._reference

	@Package.setter
	def Package(self, value: 'Package') -> None:
		self._reference = value


@export
class EntityInstantiationSymbol(SelectedName, Symbol):
	"""An entity reference in a direct entity instantiation."""

	def __init__(self, identifier: str, prefix: LibraryReferenceSymbol):
		super().__init__(identifier, prefix)
		Symbol.__init__(self, PossibleReference.Entity)

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
class ComponentInstantiationSymbol(SimpleName, Symbol):
	"""A component reference in a component instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Component)

	@property
	def Component(self) -> 'Component':
		return self._reference

	@Component.setter
	def Component(self, value: 'Component') -> None:
		self._reference = value


@export
class ConfigurationInstantiationSymbol(SimpleName, Symbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Configuration)

	@property
	def Configuration(self) -> 'Configuration':
		return self._reference

	@Configuration.setter
	def Configuration(self, value: 'Configuration') -> None:
		self._reference = value


@export
class SimpleSubtypeSymbol(SimpleName, Symbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Configuration)

	@property
	def Subtype(self) -> 'Subtype':
		return self._reference

	@Subtype.setter
	def Subtype(self, value: 'Subtype') -> None:
		self._reference = value


@export
class ConstrainedScalarSubtypeSymbol(SimpleName, Symbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Configuration)


@export
class ConstrainedCompositeSubtypeSymbol(SimpleName, Symbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Configuration)


@export
class SimpleObjectOrFunctionCallSymbol(SimpleName, Symbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, identifier: str):
		super().__init__(identifier)
		Symbol.__init__(self, PossibleReference.Configuration)


@export
class IndexedObjectOrFunctionCallSymbol(IndexedName, Symbol):
	"""A configuration reference in a configuration instantiation."""

	def __init__(self, prefix: Name, indices: Iterable[ExpressionUnion]):
		super().__init__(prefix, indices)
		Symbol.__init__(self, PossibleReference.Configuration)
