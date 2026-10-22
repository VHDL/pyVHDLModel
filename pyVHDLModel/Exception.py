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

The module ``Exceptions`` contains all structured errors that are raised by pyVHDLModel. Besides a default error
message in english, each exception object contains one or multiple references to the exception's context.
"""
from __future__               import annotations

from typing                   import TYPE_CHECKING, Optional as Nullable, Union

from pyTooling.Decorators     import export, readonly
from pyTooling.Exceptions     import ExceptionBase, AlreadyInHierarchyError, DuplicateElementError
from pyTooling.Warning        import Warning, CriticalWarning

from pyVHDLModel.Symbol       import Symbol

if TYPE_CHECKING:  # pragma: no cover
	from pyVHDLModel.Base       import ModelElementUnion, ModelEntity
	from pyVHDLModel.Concurrent import ComponentInstantiation
	from pyVHDLModel.DesignUnit import Component as _Component
	from pyVHDLModel.Namespace  import Namespace as _Namespace


@export
class VHDLModelWarning(Warning):
	"""
	Base-class for the non-critical warnings raised by pyVHDLModel.

	.. attention::

	   It's a non-critical warning: without a :class:`~pyTooling.Warning.WarningCollector` up the call-hierarchy, it's
	   dropped silently.

	.. seealso::

	   * :class:`Not implemented warning <pyVHDLModel.Exception.NotImplementedWarning>`
	   * :class:`Blackbox warning <pyVHDLModel.Exception.BlackboxWarning>`
	"""
	pass


@export
class NotImplementedWarning(VHDLModelWarning):
	"""
	Raised when a language construct is recognised but not yet modelled.

	.. attention::

	   It's a non-critical warning: without a :class:`~pyTooling.Warning.WarningCollector` up the call-hierarchy, it's
	   dropped silently.
	"""

	_item: Nullable[Union[ModelEntity, Symbol]]  #: The model element or symbol of the construct.

	def __init__(self, message: str, /, *, item: Nullable[Union[ModelEntity, Symbol]] = None) -> None:
		"""
		Initializes the warning with the construct that isn't modelled yet.

		:param message: The warning's message.
		:param item:    Optional, the model element or symbol of the construct - a declared item, an expression, a symbol
		                or an instantiation.
		"""
		super().__init__(message)
		self._item = item

	@readonly
	def Item(self) -> Nullable[Union[ModelEntity, Symbol]]:
		"""
		Read-only property to access the model element or symbol of the construct (:attr:`_item`).

		:returns: The model element or symbol, or ``None`` if the construct has none or it wasn't recorded.
		"""
		return self._item


@export
class VHDLModelCriticalWarning(CriticalWarning):
	"""
	Base-class for critical warnings that likely indicate a defect in the model or its input.

	.. important::

	   As a critical warning, it must be collected by a :class:`~pyTooling.Warning.WarningCollector` up the
	   call-hierarchy, otherwise :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised.

	.. seealso::

	   * :class:`Duplicate declaration warning <pyVHDLModel.Exception.DuplicateDeclarationWarning>`
	"""
	pass


@export
class DuplicateDeclarationWarning(VHDLModelCriticalWarning):
	"""
	Raised when two declarations in one declarative region share an identifier.

	VHDL rejects this as *identifier already used for a declaration*. Overloadable declarations -
	subprograms differing in signature - are not reported. Afterwards, the namespace refers to the later declaration.

	.. important::

	   As a critical warning, it must be collected by a :class:`~pyTooling.Warning.WarningCollector` up the
	   call-hierarchy, otherwise :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised.
	"""

	_identifier:           Nullable[str]          #: The identifier declared twice.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) identifier.
	_namespace:            Nullable[_Namespace]   #: The namespace of the declarative region declaring it.
	_element:              Nullable[ModelEntity]  #: The new declaration.
	_existing:             Nullable[ModelEntity]  #: The earlier declaration.

	def __init__(
		self,
		message: str,
		/, *,
		identifier: Nullable[str] = None,
		namespace: Nullable[_Namespace] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the warning with the identifier, the namespace and both declarations.

		:param message:    The warning's message.
		:param identifier: Optional, the identifier declared twice.
		:param namespace:  Optional, the namespace of the declarative region declaring it.
		:param element:    Optional, the new declaration.
		:param existing:   Optional, the earlier declaration.
		"""
		super().__init__(message)
		self._identifier =           identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None
		self._namespace =            namespace
		self._element =              element
		self._existing =             existing

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier declared twice (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) identifier (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Namespace(self) -> Nullable[_Namespace]:
		"""
		Read-only property to access the namespace of the declarative region declaring it (:attr:`_namespace`).

		:returns: The namespace, or ``None`` if it wasn't recorded.
		"""
		return self._namespace

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new declaration (:attr:`_element`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the earlier declaration (:attr:`_existing`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class BlackboxWarning(VHDLModelWarning):
	"""
	Raised when a component could not be bound and is treated as a blackbox.

	Only a component allowing blackboxes - set on it or inherited, e.g. from its library or design
	(:attr:`~pyVHDLModel.Common.AllowBlackboxMixin.AllowBlackbox`) - becomes a blackbox, recorded in
	:attr:`Component.IsBlackbox <pyVHDLModel.DesignUnit.Component.IsBlackbox>`. For any other component without an
	entity, analysis raises a :exc:`VHDLModelException`.

	.. attention::

	   It's a non-critical warning: without a :class:`~pyTooling.Warning.WarningCollector` up the call-hierarchy, it's
	   dropped silently.
	"""

	_instance:  Nullable[ComponentInstantiation]  #: The component instantiation treated as a blackbox.
	_component: Nullable[_Component]              #: The component that couldn't be bound.

	def __init__(
		self,
		message: str,
		/, *,
		instance: Nullable[ComponentInstantiation] = None,
		component: Nullable[_Component] = None
	) -> None:
		"""
		Initializes the warning with the instantiation and the component that couldn't be bound.

		:param message:   The warning's message.
		:param instance:  Optional, the component instantiation treated as a blackbox.
		:param component: Optional, the component that couldn't be bound.
		"""
		super().__init__(message)
		self._instance =  instance
		self._component = component

	@readonly
	def Instance(self) -> Nullable[ComponentInstantiation]:
		"""
		Read-only property to access the component instantiation treated as a blackbox (:attr:`_instance`).

		:returns: The instantiation, or ``None`` if it wasn't recorded.
		"""
		return self._instance

	@readonly
	def Component(self) -> Nullable[_Component]:
		"""
		Read-only property to access the component that couldn't be bound (:attr:`_component`).

		:returns: The component, or ``None`` if it wasn't recorded.
		"""
		return self._component


@export
class VHDLModelException(ExceptionBase):
	"""
	Base-class for all exceptions (errors) raised by pyVHDLModel.

	.. seealso::

	   * :class:`Library exists in design error <pyVHDLModel.Exception.LibraryExistsInDesignError>`
	   * :class:`Registered to foreign design error <pyVHDLModel.Exception.LibraryRegisteredToForeignDesignError>`
	   * :class:`Library not registered error <pyVHDLModel.Exception.LibraryNotRegisteredError>`
	   * :class:`Entity exists in library error <pyVHDLModel.Exception.EntityExistsInLibraryError>`
	   * :class:`Architecture exists in library error <pyVHDLModel.Exception.ArchitectureExistsInLibraryError>`
	   * :class:`Package exists in library error <pyVHDLModel.Exception.PackageExistsInLibraryError>`
	   * :class:`Package body exists error <pyVHDLModel.Exception.PackageBodyExistsError>`
	   * :class:`Configuration exists in library error <pyVHDLModel.Exception.ConfigurationExistsInLibraryError>`
	   * :class:`Context exists in library error <pyVHDLModel.Exception.ContextExistsInLibraryError>`
	   * :class:`Referenced library not existing error <pyVHDLModel.Exception.ReferencedLibraryNotExistingError>`
	   * :class:`Already in design error <pyVHDLModel.Exception.AlreadyInDesignError>`
	   * :class:`Not a child error <pyVHDLModel.Exception.NotAChildError>`
	   * :class:`Duplicate generic error <pyVHDLModel.Exception.DuplicateGenericError>`
	   * :class:`Duplicate port error <pyVHDLModel.Exception.DuplicatePortError>`
	   * :class:`Duplicate parameter error <pyVHDLModel.Exception.DuplicateParameterError>`
	   * :class:`Not in namespace error <pyVHDLModel.Exception.NotInNamespaceError>`
	   * :class:`Duplicate declaration error <pyVHDLModel.Exception.DuplicateDeclarationError>`
	   * :class:`Library not found error <pyVHDLModel.Exception.LibraryNotFoundError>`
	   * :class:`Entity not found error <pyVHDLModel.Exception.EntityNotFoundError>`
	   * :class:`Package not found error <pyVHDLModel.Exception.PackageNotFoundError>`
	   * :class:`Configuration not found error <pyVHDLModel.Exception.ConfigurationNotFoundError>`
	   * :class:`Context not found error <pyVHDLModel.Exception.ContextNotFoundError>`
	   * :class:`VHDL writer error <pyVHDLModel.Exception.VHDLWriterError>`
	"""


@export
class LibraryExistsInDesignError(VHDLModelException):
	"""
	This exception is raised, when the library is already existing in the design.

	Message: :pycode:`f"Library '{library._identifier}' already exists in design."`
	"""

	_library: Library  #: The library involved in this error.

	def __init__(self, library: Library) -> None:
		"""
		Initializes the exception message based on given library object.

		:param library: The library that already exists in the design.
		"""
		super().__init__(f"Library '{library._identifier}' already exists in design.")
		self._library = library

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the duplicate library (:attr:`_library`).

		:returns: Duplicate library (by name).
		"""
		return self._library


@export
class LibraryRegisteredToForeignDesignError(VHDLModelException):
	"""
	This exception is raised, when the library is already registered to a foreign design.

	Message: :pycode:`f"Library '{library._identifier}' already registered in design '{library.Parent}'."`
	"""

	_library: Library  #: The library involved in this error.

	def __init__(self, library: Library) -> None:
		"""
		Initializes the exception message based on given library object.

		:param library: The library that is already registered to another design.
		"""
		super().__init__(f"Library '{library._identifier}' already registered in design '{library.Parent}'.")
		self._library = library

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library


@export
class LibraryNotRegisteredError(VHDLModelException):
	"""
	This exception is raised, when the library is not registered in the design.

	Message: :pycode:`f"Library '{library._identifier}' is not registered in the design."`
	"""

	_library: Library  #: The library involved in this error.

	def __init__(self, library: Library) -> None:
		"""
		Initializes the exception message based on given library object.

		:param library: The library that isn't registered in the design.
		"""
		super().__init__(f"Library '{library._identifier}' is not registered in the design.")
		self._library = library

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library


@export
class EntityExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the entity already existing in the library.

	Message: :pycode:`f"Entity '{entity._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library: Library  #: The library involved in this error.
	_entity:  Entity   #: The entity involved in this error.

	def __init__(self, entity: Entity, library: Library) -> None:
		"""
		Initializes the exception message based on given entity and library objects.

		:param entity:  The entity that already exists in the library.
		:param library: The library that already contains the entity.
		"""
		super().__init__(f"Entity '{entity._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._entity = entity

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Entity(self) -> Entity:
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity


@export
class ArchitectureExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the architecture already existing in the library.

	Message: :pycode:`f"Architecture '{architecture._identifier}' for entity '{entity._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library:      Library       #: The library involved in this error.
	_entity:       Entity        #: The entity involved in this error.
	_architecture: Architecture  #: The architecture involved in this error.

	def __init__(self, architecture: Architecture, entity: Entity, library: Library) -> None:
		"""
		Initializes the exception message based on given architecture, entity and library objects.

		:param architecture: The architecture that already exists in the library.
		:param entity:       The entity the architecture refers to, which already exists in the library.
		:param library:      The library that already contains the architecture.
		"""
		super().__init__(f"Architecture '{architecture._identifier}' for entity '{entity._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._entity = entity
		self._architecture = architecture

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Entity(self) -> Entity:
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	@readonly
	def Architecture(self) -> Architecture:
		"""
		Read-only property to access the architecture (:attr:`_architecture`).

		:returns: The architecture.
		"""
		return self._architecture


@export
class PackageExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the package already existing in the library.

	Message: :pycode:`f"Package '{package._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library: Library  #: The library involved in this error.
	_package: Package  #: The package involved in this error.

	def __init__(self, package: Package, library: Library) -> None:
		"""
		Initializes the exception message based on given package and library objects.

		:param package: The package that already exists in the library.
		:param library: The library that already contains the package.
		"""
		super().__init__(f"Package '{package._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._package = package

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Package(self) -> Package:
		"""
		Read-only property to access the package (:attr:`_package`).

		:returns: The package.
		"""
		return self._package


@export
class PackageBodyExistsError(VHDLModelException):
	"""
	This exception is raised, when the package body already existing in the library.

	Message: :pycode:`f"Package body '{packageBody._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library:     Library      #: The library involved in this error.
	_packageBody: PackageBody  #: The package body involved in this error.

	def __init__(self, packageBody: PackageBody, library: Library) -> None:
		"""
		Initializes the exception message based on given package body and library objects.

		:param packageBody: The package body that already exists in the library.
		:param library:     The library that already contains the package body.
		"""
		super().__init__(f"Package body '{packageBody._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._packageBody = packageBody

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def PackageBody(self) -> PackageBody:
		"""
		Read-only property to access the package body (:attr:`_packageBody`).

		:returns: The package body.
		"""
		return self._packageBody


@export
class ConfigurationExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the configuration already existing in the library.

	Message: :pycode:`f"Configuration '{configuration._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library:       Library        #: The library involved in this error.
	_configuration: Configuration  #: The configuration involved in this error.

	def __init__(self, configuration: Configuration, library: Library) -> None:
		"""
		Initializes the exception message based on given configuration and library objects.

		:param configuration: The configuration that already exists in the library.
		:param library:       The library that already contains the configuration.
		"""
		super().__init__(f"Configuration '{configuration._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._configuration = configuration

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Configuration(self) -> Configuration:
		"""
		Read-only property to access the configuration (:attr:`_configuration`).

		:returns: The configuration.
		"""
		return self._configuration


@export
class ContextExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the context already existing in the library.

	Message: :pycode:`f"Context '{context._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library: Library  #: The library involved in this error.
	_context: Context  #: The context involved in this error.

	def __init__(self, context: Context, library: Library) -> None:
		"""
		Initializes the exception message based on given context and library objects.

		:param context: The context that already exists in the library.
		:param library: The library that already contains the context.
		"""
		super().__init__(f"Context '{context._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._context = context

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Context(self) -> Context:
		"""
		Read-only property to access the context (:attr:`_context`).

		:returns: The context.
		"""
		return self._context


@export
class ReferencedLibraryNotExistingError(VHDLModelException):
	"""
	This exception is raised, when a library is referenced by a `library clause`, but doesn't exist in the design.

	Message: :pycode:`f"Library '{librarySymbol.Name._identifier}' referenced by library clause of context '{context._identifier}' doesn't exist in design."`
	"""

	_librarySymbol: Symbol   #: The library symbol that could not be resolved.
	_context:       Context  #: The context involved in this error.

	def __init__(self, context: Context, librarySymbol: Symbol) -> None:
		"""
		Initializes the exception message based on given context and library objects.

		:param context:       The context that already exists in the library.
		:param librarySymbol: The library that already contains the context.
		"""
		super().__init__(f"Library '{librarySymbol.Name._identifier}' referenced by library clause of context '{context._identifier}' doesn't exist in design.")
		self._librarySymbol = librarySymbol
		self._context = context

	@readonly
	def LibrarySymbol(self) -> Symbol:
		"""
		Read-only property to access the library symbol (:attr:`_librarySymbol`).

		:returns: The library symbol.
		"""
		return self._librarySymbol

	@readonly
	def Context(self) -> Context:
		"""
		Read-only property to access the context (:attr:`_context`).

		:returns: The context.
		"""
		return self._context


@export
class AlreadyInDesignError(VHDLModelException, AlreadyInHierarchyError):
	"""
	This exception is raised, when a model entity is added to a parent, but it already has a parent.

	.. hint::

	   Remove the model entity from its current parent first, e.g. by
	   :meth:`~pyVHDLModel.Regions.WithGenericsMixin.RemoveGenericItem`.
	"""

	_element: Nullable[ModelEntity]  #: The model entity to add.
	_parent:  Nullable[ModelEntity]  #: The model entity's current parent.

	def __init__(
		self,
		message: str,
		/, *,
		element: Nullable[ModelEntity] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the model entity and its current parent.

		:param message: The error message.
		:param element: Optional, the model entity to add.
		:param parent:  Optional, the model entity's current parent.
		"""
		super().__init__(message)
		self._element = element
		self._parent =  parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the model entity to add (:attr:`_element`).

		:returns: The model entity, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the model entity's current parent (:attr:`_parent`).

		:returns: The parent, or ``None`` if it wasn't recorded.
		"""
		return self._parent


@export
class NotAChildError(VHDLModelException):
	"""
	This exception is raised, when a model entity is removed from a parent, but it isn't a child of that parent.
	"""

	_element: Nullable[ModelEntity]  #: The model entity, which isn't a child.
	_parent:  Nullable[ModelEntity]  #: The model entity searched for the child.

	def __init__(
		self,
		message: str,
		/, *,
		element: Nullable[ModelEntity] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the model entity and the parent searched for it.

		:param message: The error message.
		:param element: Optional, the model entity, which isn't a child.
		:param parent:  Optional, the model entity searched for the child.
		"""
		super().__init__(message)
		self._element = element
		self._parent =  parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the model entity, which isn't a child (:attr:`_element`).

		:returns: The model entity, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the model entity searched for the child (:attr:`_parent`).

		:returns: The parent, or ``None`` if it wasn't recorded.
		"""
		return self._parent


@export
class NotInNamespaceError(VHDLModelException, KeyError):
	"""
	This exception is raised, when an element isn't declared in a namespace under the given identifier.

	It's a :exc:`KeyError` too, like removing a missing key from a dictionary.
	"""

	_identifier:           Nullable[str]         #: The identifier looked up.
	_normalizedIdentifier: Nullable[str]         #: The normalized (lower case) identifier.
	_namespace:            Nullable[_Namespace]  #: The namespace searched for the identifier.

	def __init__(
		self,
		message: str,
		/, *,
		identifier: Nullable[str] = None,
		namespace: Nullable[_Namespace] = None
	) -> None:
		"""
		Initializes the exception with the identifier and the namespace searched for it.

		:param message:    The error message.
		:param identifier: Optional, the identifier looked up.
		:param namespace:  Optional, the namespace searched for the identifier.
		"""
		super().__init__(message)
		self._identifier =           identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None
		self._namespace =            namespace

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier looked up (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) identifier (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Namespace(self) -> Nullable[_Namespace]:
		"""
		Read-only property to access the namespace searched for the identifier (:attr:`_namespace`).

		:returns: The namespace, or ``None`` if it wasn't recorded.
		"""
		return self._namespace

	def __str__(self) -> str:
		"""
		Return the exception's message.

		:returns: The message, without the quotes :exc:`KeyError` adds.
		"""
		return self.args[0]


@export
class DuplicateGenericError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when a language construct already has a generic of the same identifier.
	"""

	_identifier:           Nullable[str]          #: The identifier declared twice.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) identifier.
	_parent:               Nullable[ModelEntity]  #: The language construct owning the generic clause.
	_element:              Nullable[ModelEntity]  #: The new generic.
	_existing:             Nullable[ModelEntity]  #: The existing declaration.

	def __init__(
		self,
		message: str,
		/, *,
		identifier: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the identifier, the language construct and both declarations.

		:param message:    The error message.
		:param identifier: Optional, the identifier declared twice.
		:param parent:     Optional, the language construct owning the generic clause.
		:param element:    Optional, the new generic.
		:param existing:   Optional, the existing declaration.
		"""
		super().__init__(message)
		self._identifier =           identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None
		self._parent =               parent
		self._element =              element
		self._existing =             existing

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier declared twice (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) identifier (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the language construct owning the generic clause (:attr:`_parent`).

		:returns: The language construct, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new generic (:attr:`_element`).

		:returns: The generic, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing declaration (:attr:`_existing`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicatePortError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when a language construct already has a port of the same identifier.
	"""

	_identifier:           Nullable[str]          #: The identifier declared twice.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) identifier.
	_parent:               Nullable[ModelEntity]  #: The language construct owning the port clause.
	_element:              Nullable[ModelEntity]  #: The new port.
	_existing:             Nullable[ModelEntity]  #: The existing declaration.

	def __init__(
		self,
		message: str,
		/, *,
		identifier: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the identifier, the language construct and both declarations.

		:param message:    The error message.
		:param identifier: Optional, the identifier declared twice.
		:param parent:     Optional, the language construct owning the port clause.
		:param element:    Optional, the new port.
		:param existing:   Optional, the existing declaration.
		"""
		super().__init__(message)
		self._identifier =           identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None
		self._parent =               parent
		self._element =              element
		self._existing =             existing

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier declared twice (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) identifier (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the language construct owning the port clause (:attr:`_parent`).

		:returns: The language construct, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new port (:attr:`_element`).

		:returns: The port, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing declaration (:attr:`_existing`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicateParameterError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when a language construct already has a parameter of the same identifier.
	"""

	_identifier:           Nullable[str]          #: The identifier declared twice.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) identifier.
	_parent:               Nullable[ModelEntity]  #: The language construct owning the parameter list.
	_element:              Nullable[ModelEntity]  #: The new parameter.
	_existing:             Nullable[ModelEntity]  #: The existing declaration.

	def __init__(
		self,
		message: str,
		/, *,
		identifier: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the identifier, the language construct and both declarations.

		:param message:    The error message.
		:param identifier: Optional, the identifier declared twice.
		:param parent:     Optional, the language construct owning the parameter list.
		:param element:    Optional, the new parameter.
		:param existing:   Optional, the existing declaration.
		"""
		super().__init__(message)
		self._identifier =           identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None
		self._parent =               parent
		self._element =              element
		self._existing =             existing

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier declared twice (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) identifier (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the language construct owning the parameter list (:attr:`_parent`).

		:returns: The language construct, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new parameter (:attr:`_element`).

		:returns: The parameter, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing declaration (:attr:`_existing`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicateDeclarationError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when a declarative region already declares an identifier of a declared item.

	It's raised for declared items without a more specific error, and it's the base-class of the more specific errors.
	Subprograms are overloadable, so a subprogram sharing its identifier with another subprogram is no duplicate.

	.. seealso::

	   * :class:`Duplicate type error <pyVHDLModel.Exception.DuplicateTypeError>`
	   * :class:`Duplicate subtype error <pyVHDLModel.Exception.DuplicateSubtypeError>`
	   * :class:`Duplicate constant error <pyVHDLModel.Exception.DuplicateConstantError>`
	   * :class:`Duplicate signal error <pyVHDLModel.Exception.DuplicateSignalError>`
	   * :class:`Duplicate variable error <pyVHDLModel.Exception.DuplicateVariableError>`
	   * :class:`Duplicate file error <pyVHDLModel.Exception.DuplicateFileError>`
	   * :class:`Duplicate component error <pyVHDLModel.Exception.DuplicateComponentError>`
	   * :class:`Duplicate subprogram error <pyVHDLModel.Exception.DuplicateSubprogramError>`
	   * :class:`Duplicate label error <pyVHDLModel.Exception.DuplicateLabelError>`
	"""

	_identifier:           Nullable[str]          #: The identifier declared twice.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) identifier.
	_namespace:            Nullable[_Namespace]   #: The namespace of the declarative region declaring it.
	_element:              Nullable[ModelEntity]  #: The new declaration.
	_existing:             Nullable[ModelEntity]  #: The existing declaration.

	def __init__(
		self,
		message: str,
		/, *,
		identifier: Nullable[str] = None,
		namespace: Nullable[_Namespace] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the identifier, the namespace and both declarations.

		:param message:    The error message.
		:param identifier: Optional, the identifier declared twice.
		:param namespace:  Optional, the namespace of the declarative region declaring it.
		:param element:    Optional, the new declaration.
		:param existing:   Optional, the existing declaration.
		"""
		super().__init__(message)
		self._identifier =           identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None
		self._namespace =            namespace
		self._element =              element
		self._existing =             existing

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier declared twice (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) identifier (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Namespace(self) -> Nullable[_Namespace]:
		"""
		Read-only property to access the namespace of the declarative region declaring it (:attr:`_namespace`).

		:returns: The namespace, or ``None`` if it wasn't recorded.
		"""
		return self._namespace

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new declaration (:attr:`_element`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing declaration (:attr:`_existing`).

		:returns: The declaration, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicateTypeError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new type.
	"""


@export
class DuplicateSubtypeError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new subtype.
	"""


@export
class DuplicateConstantError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new constant.
	"""


@export
class DuplicateSignalError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new signal.
	"""


@export
class DuplicateVariableError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new (shared) variable.
	"""


@export
class DuplicateFileError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new file.
	"""


@export
class DuplicateComponentError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new component.
	"""


@export
class DuplicateSubprogramError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the identifier of a new subprogram.

	Subprograms are overloadable, so only a declaration other than a subprogram is a duplicate.
	"""


@export
class DuplicateLabelError(DuplicateDeclarationError):
	"""
	This exception is raised, when a declarative region already declares the label of a new statement.

	A statement label is declared implicitly in the declarative region enclosing the statement, so it clashes with
	another label and with a declaration of the same identifier.
	"""


@export
class LibraryNotFoundError(VHDLModelException):
	"""
	This exception is raised, when a library is looked up by name, but doesn't exist in the design.

	Message: :pycode:`f"Library '{libraryName}' not found in design."`
	"""

	_libraryName: str  #: The name of the library, which was not found.

	def __init__(self, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given library name.

		:param libraryName: The name of the library, which was not found.
		"""
		super().__init__(f"Library '{libraryName}' not found in design.")
		self._libraryName = libraryName

	@readonly
	def LibraryName(self) -> str:
		"""
		Read-only property to access the library name (:attr:`_libraryName`).

		:returns: The name of the library, which was not found.
		"""
		return self._libraryName


@export
class DesignUnitNotFoundError(Exception):
	"""
	The exception is raised when a design unit is looked up by name, but doesn't exist in the searched library.

	It's a common base: a kind-specific exception derives from it and from :exc:`VHDLModelException`, e.g.
	``class EntityNotFoundError(VHDLModelException, DesignUnitNotFoundError)``. It has no initializer of its own; the
	derived exception sets the fields.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.EntityNotFoundError`
	      |rarr| Entity not found.
	   :exc:`~pyVHDLModel.Exception.PackageNotFoundError`
	      |rarr| Package not found.
	   :exc:`~pyVHDLModel.Exception.ConfigurationNotFoundError`
	      |rarr| Configuration not found.
	   :exc:`~pyVHDLModel.Exception.ContextNotFoundError`
	      |rarr| Context not found.
	"""

	_designUnitName: str  #: The name of the design unit, which was not found.
	_libraryName:    str  #: The name of the searched library.

	@readonly
	def DesignUnitName(self) -> str:
		"""
		Read-only property to access the design unit name (:attr:`_designUnitName`).

		:returns: The name of the design unit, which was not found.
		"""
		return self._designUnitName

	@readonly
	def LibraryName(self) -> str:
		"""
		Read-only property to access the library name (:attr:`_libraryName`).

		:returns: The name of the searched library.
		"""
		return self._libraryName


@export
class EntityNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when an entity is looked up by name, but doesn't exist in the searched library.

	Message: :pycode:`f"Entity '{entityName}' not found in library '{libraryName}'."`
	"""

	def __init__(self, entityName: str, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given entity name and library name.

		:param entityName:  The name of the entity, which was not found.
		:param libraryName: The name of the searched library.
		"""
		super().__init__(f"Entity '{entityName}' not found in library '{libraryName}'.")

		self._designUnitName = entityName
		self._libraryName =    libraryName


@export
class PackageNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when a package is looked up by name, but doesn't exist in the searched library.

	Message: :pycode:`f"Package '{packageName}' not found in library '{libraryName}'."`
	"""

	def __init__(self, packageName: str, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given package name and library name.

		:param packageName: The name of the package, which was not found.
		:param libraryName: The name of the searched library.
		"""
		super().__init__(f"Package '{packageName}' not found in library '{libraryName}'.")

		self._designUnitName = packageName
		self._libraryName =    libraryName


@export
class ConfigurationNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when a configuration is looked up by name, but doesn't exist in the searched library.

	Message: :pycode:`f"Configuration '{configurationName}' not found in library '{libraryName}'."`
	"""

	def __init__(self, configurationName: str, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given configuration name and library name.

		:param configurationName: The name of the configuration, which was not found.
		:param libraryName:       The name of the searched library.
		"""
		super().__init__(f"Configuration '{configurationName}' not found in library '{libraryName}'.")

		self._designUnitName = configurationName
		self._libraryName =    libraryName


@export
class ContextNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when a context is looked up by name, but doesn't exist in the searched library.

	Message: :pycode:`f"Context '{contextName}' not found in library '{libraryName}'."`
	"""

	def __init__(self, contextName: str, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given context name and library name.

		:param contextName: The name of the context, which was not found.
		:param libraryName: The name of the searched library.
		"""
		super().__init__(f"Context '{contextName}' not found in library '{libraryName}'.")

		self._designUnitName = contextName
		self._libraryName =    libraryName


@export
class VHDLWriterError(VHDLModelException):
	"""
	This exception is raised, when the VHDL writer can't write a model element as VHDL source text.

	The element's content has no VHDL notation, e.g. a string literal containing a control character.
	"""

	_element: ModelElementUnion  #: The model element the writer could not write.

	def __init__(self, message: str, element: ModelElementUnion) -> None:
		"""
		Initializes the exception with a message and the model element that could not be written.

		:param message: The error message.
		:param element: The model element that could not be written.
		"""
		super().__init__(message)
		self._element = element

	@readonly
	def Element(self) -> ModelElementUnion:
		"""
		Read-only property to access the model element that could not be written (:attr:`_element`).

		:returns: The model element.
		"""
		return self._element
