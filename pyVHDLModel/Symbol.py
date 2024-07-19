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
This module contains parts of an abstract document language model for VHDL.

Symbols are entity specific wrappers for names that reference VHDL language entities.
"""
from enum                  import Flag, auto
from typing                import Any, Optional as Nullable, Iterable, List, Dict, Mapping

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType

from pyVHDLModel.Base      import Range
from pyVHDLModel.Name      import Name, AllName


@export
class PossibleReference(Flag):
	"""
	Is an enumeration, representing possible targets for a reference in a :class:`~pyVHDLModel.Symbol`.
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
	RecordElement =   auto()  #: RecordElement
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
	Object = Constant | Variable | Signal  # | File                                                     #: Any object
	SubProgram = Procedure | Function                                                                #: Any subprogram
	PackageMember = AnyType | Object | SubProgram | Component                                        #: Any member of a package
	SimpleNameInExpression = Constant | Variable | Signal | ScalarType | EnumLiteral | Function      #: Any possible item in an expression.


@export
class Symbol(metaclass=ExtendedType):
	"""
	Base-class for all symbol classes.
	"""

	_name:               Name               #: The name to reference the langauge entity.
	_possibleReferences: PossibleReference  #: An enumeration to filter possible references.
	_reference:          Nullable[Any]      #: The resolved language entity, otherwise ``None``.

	def __init__(self, name: Name, possibleReferences: PossibleReference) -> None:
		self._name = name
		self._possibleReferences = possibleReferences
		self._reference = None

	@readonly
	def Name(self) -> Name:
		return self._name

	@readonly
	def Reference(self) -> Nullable[Any]:
		return self._reference

	@readonly
	def IsResolved(self) -> bool:
		return self._reference is not None

	def __bool__(self) -> bool:
		return self._reference is not None

	def __repr__(self) -> str:
		if self._reference is not None:
			return f"{self.__class__.__name__}: '{self._name!s}' -> {self._reference!s}"

		return f"{self.__class__.__name__}: '{self._name!s}' -> unresolved"

	def __str__(self) -> str:
		if self._reference is not None:
			return str(self._reference)

		return f"{self._name!s}?"


@export
class LibraryReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a library.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      library ieee;
	      --      ^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Library)

	@readonly
	def Library(self) -> Nullable['Library']:
		return self._reference

	@Library.setter
	def Library(self, value: 'Library') -> None:
		self._reference = value


@export
class PackageReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a package.

	The internal name will be a :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std;
	      --  ^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Package)

	@property
	def Package(self) -> Nullable['Package']:
		return self._reference

	@Package.setter
	def Package(self, value: 'Package') -> None:
		self._reference = value


@export
class ContextReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a context.

	The internal name will be a :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      context ieee.ieee_std_context;
	      --      ^^^^^^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Context)

	@property
	def Context(self) -> 'Context':
		return self._reference

	@Context.setter
	def Context(self, value: 'Context') -> None:
		self._reference = value


@export
class PackageMemberReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a package member.

	The internal name will be a :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std.unsigned;
	      --  ^^^^^^^^^^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.PackageMember)

	@property
	def Member(self) -> Nullable['Package']:  # TODO: typehint
		return self._reference

	@Member.setter
	def Member(self, value: 'Package') -> None:  # TODO: typehint
		self._reference = value


@export
class AllPackageMembersReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to all package members.

	The internal name will be a :class:`~pyVHDLModel.Name.AllName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std.all;
	      --  ^^^^^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: AllName) -> None:
		super().__init__(name, PossibleReference.PackageMember)

	@property
	def Members(self) -> 'Package':  # TODO: typehint
		return self._reference

	@Members.setter
	def Members(self, value: 'Package') -> None:  # TODO: typehint
		self._reference = value


@export
class EntityInstantiationSymbol(Symbol):
	"""
	Represents a reference (name) to an entity in a direct entity instantiation.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	    .. code-block:: VHDL

	       inst : entity work.Counter;
	       --            ^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Entity)

	@property
	def Entity(self) -> 'Entity':
		return self._reference

	@Entity.setter
	def Entity(self, value: 'Entity') -> None:
		self._reference = value


@export
class ComponentInstantiationSymbol(Symbol):
	"""
	Represents a reference (name) to an entity in a component instantiation.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	    .. code-block:: VHDL

	       inst : component Counter;
	       --               ^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Component)

	@property
	def Component(self) -> 'Component':
		return self._reference

	@Component.setter
	def Component(self, value: 'Component') -> None:
		self._reference = value


@export
class ConfigurationInstantiationSymbol(Symbol):
	"""
	Represents a reference (name) to an entity in a configuration instantiation.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	    .. code-block:: VHDL

	       inst : configuration Counter;
	       --                   ^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Configuration)

	@property
	def Configuration(self) -> 'Configuration':
		return self._reference

	@Configuration.setter
	def Configuration(self, value: 'Configuration') -> None:
		self._reference = value


@export
class EntitySymbol(Symbol):
	"""
	Represents a reference (name) to an entity in an architecture declaration.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      architecture rtl of Counter is
	      --                  ^^^^^^^
	      begin
	      end architecture;
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Entity)

	@property
	def Entity(self) -> 'Entity':
		return self._reference

	@Entity.setter
	def Entity(self, value: 'Entity') -> None:
		self._reference = value


@export
class ArchitectureSymbol(Symbol):
	"""An entity reference in an entity instantiation with architecture name."""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Architecture)

	@property
	def Architecture(self) -> 'Architecture':
		return self._reference

	@Architecture.setter
	def Architecture(self, value: 'Architecture') -> None:
		self._reference = value


@export
class PackageSymbol(Symbol):
	"""
	Represents a reference (name) to a package in a package body declaration.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      package body Utilities is
	      --           ^^^^^^^^^
	      end package body;
	"""

	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Package)

	@property
	def Package(self) -> 'Package':
		return self._reference

	@Package.setter
	def Package(self, value: 'Package') -> None:
		self._reference = value


@export
class RecordElementSymbol(Symbol):
	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.RecordElement)


@export
class SubtypeSymbol(Symbol):
	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Type | PossibleReference.Subtype)

	@property
	def Subtype(self) -> 'Subtype':
		return self._reference

	@Subtype.setter
	def Subtype(self, value: 'Subtype') -> None:
		self._reference = value


@export
class SimpleSubtypeSymbol(SubtypeSymbol):
	pass


@export
class ConstrainedScalarSubtypeSymbol(SubtypeSymbol):
	pass


@export
class ConstrainedCompositeSubtypeSymbol(SubtypeSymbol):
	pass


@export
class ConstrainedArraySubtypeSymbol(ConstrainedCompositeSubtypeSymbol):
	pass


@export
class ConstrainedRecordSubtypeSymbol(ConstrainedCompositeSubtypeSymbol):
	pass


@export
class SimpleObjectOrFunctionCallSymbol(Symbol):
	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.SimpleNameInExpression)


@export
class IndexedObjectOrFunctionCallSymbol(Symbol):
	def __init__(self, name: Name) -> None:
		super().__init__(name, PossibleReference.Object | PossibleReference.Function)
