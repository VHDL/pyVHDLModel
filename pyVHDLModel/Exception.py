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

from pathlib                  import Path
from typing                   import TYPE_CHECKING, ClassVar, Generic, Optional as Nullable, TypeVar, Union

from pyTooling.Decorators     import export, readonly
from pyTooling.Exceptions     import ExceptionBase, AlreadyInHierarchyError, DuplicateElementError, InUseError, \
                                     NotAChildError as CommonNotAChildError
from pyTooling.Warning        import Warning, CriticalWarning

from pyVHDLModel.Symbol       import Symbol

if TYPE_CHECKING:  # pragma: no cover
	from pyVHDLModel               import Document, Library
	from pyVHDLModel.Base          import ModelElementUnion, ModelEntity
	from pyVHDLModel.Concurrent    import ComponentInstantiation, EntityInstantiation
	from pyVHDLModel.DesignUnit    import Component as _Component, Context as _Context, DesignUnit as _DesignUnit, \
	                                      Architecture
	from pyVHDLModel.Expression    import Literal as _Literal
	from pyVHDLModel.Instantiation import PackageInstantiation as _PackageInstantiation
	from pyVHDLModel.Namespace     import Namespace as _Namespace, Import as _Import


ElementType = TypeVar("ElementType", bound="ModelEntity")  #: Type of the model entity to remove, which is still in use.
UsersType =   TypeVar("UsersType", bound="ModelEntity")    #: Type of the model entities still using it.

_Symbol = Symbol  # A field annotation of class Symbol, where the class has a property 'Symbol'.


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
		:param item:    Optional, the model element or symbol of the construct - a declared item, an expression, a symbol or
		                an instantiation. Default: ``None``.
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
	   * :class:`Unresolved name warning <pyVHDLModel.Exception.UnresolvedNameWarning>`
	   * :class:`Unresolved type mark warning <pyVHDLModel.Exception.UnresolvedTypeMarkWarning>`
	   * :class:`Incomplete type warning <pyVHDLModel.Exception.IncompleteTypeWarning>`
	"""
	pass


@export
class DuplicateDeclarationWarning(VHDLModelCriticalWarning):
	"""
	Raised when two declarations in one declarative region share an identifier.

	VHDL rejects this as *identifier already used for a declaration*. Overloadable declarations -
	subprograms differing in signature - are not reported. Afterwards, the namespace refers to the later declaration.

	It's also raised, when a package linked to a package body is linked to another one
	(:meth:`Library.LinkPackageBodies() <pyVHDLModel.Library.LinkPackageBodies>`). Afterwards, the package refers to the
	later package body.

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
		:param identifier: Optional, the identifier declared twice. Default: ``None``.
		:param namespace:  Optional, the namespace of the declarative region declaring it. Default: ``None``.
		:param element:    Optional, the new declaration. Default: ``None``.
		:param existing:   Optional, the earlier declaration. Default: ``None``.
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
class UnresolvedNameWarning(VHDLModelCriticalWarning):
	"""
	Raised when a name can't be resolved: no declaration of it is visible, or use clauses made conflicting declarations
	potentially visible.

	Also a use clause naming something it can't use is reported, e.g. an uninstantiated generic package. The model stays
	usable, but the symbol of the name stays unresolved or imports nothing.

	.. important::

	   As a critical warning, it must be collected by a :class:`~pyTooling.Warning.WarningCollector` up the
	   call-hierarchy, otherwise :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised.
	"""

	_LABEL:      ClassVar[str] = "Name"  #: The kind of name, which starts the messages of a name lookup.

	_symbol:     _Symbol                  #: The unresolved symbol.
	_place:      ModelEntity              #: The model entity containing the name, e.g. a use clause.
	_namespaces: tuple[_Namespace, ...]   #: The namespaces searched for the name, innermost first.
	_conflicts:  tuple[_Import, ...]      #: The imported declarations conflicting with each other.

	def __init__(
		self,
		message:    str,
		/, *,
		symbol:     _Symbol,
		place:      ModelEntity,
		namespaces: tuple[_Namespace, ...],
		conflicts:  tuple[_Import, ...] = ()
	) -> None:
		"""
		Initializes the warning with the unresolved symbol, its place, the searched namespaces and the conflicts.

		:param message:    The warning's message.
		:param symbol:     The unresolved symbol.
		:param place:      The model entity containing the name, e.g. a use clause or a declaration.
		:param namespaces: The namespaces searched for the name, innermost first.
		:param conflicts:  Optional, the imported declarations conflicting with each other. Default: ``()``.
		"""
		super().__init__(message)
		self._symbol =     symbol
		self._place =      place
		self._namespaces = namespaces
		self._conflicts =  conflicts

	@readonly
	def Symbol(self) -> _Symbol:
		"""
		Read-only property to access the unresolved symbol (:attr:`_symbol`).

		:returns: The symbol.
		"""
		return self._symbol

	@readonly
	def Place(self) -> ModelEntity:
		"""
		Read-only property to access the model entity containing the name (:attr:`_place`).

		:returns: The model entity, e.g. a use clause or a declaration.
		"""
		return self._place

	@readonly
	def Namespaces(self) -> tuple[_Namespace, ...]:
		"""
		Read-only property to access the namespaces searched for the name (:attr:`_namespaces`).

		:returns: Tuple of namespaces, innermost first.
		"""
		return self._namespaces

	@readonly
	def Conflicts(self) -> tuple[_Import, ...]:
		"""
		Read-only property to access the imported declarations conflicting with each other (:attr:`_conflicts`).

		:returns: Tuple of imported declarations with their use clauses, empty if there is no conflict.
		"""
		return self._conflicts


@export
class UnresolvedTypeMarkWarning(UnresolvedNameWarning):
	"""
	Raised when a type mark can't be resolved (:meth:`~pyVHDLModel.Design.ResolveTypeMarks`): no declaration of it is
	visible, use clauses made conflicting declarations potentially visible, the prefix of an expanded name isn't a visible
	package, or it denotes something else than a type or subtype.

	Its place (:attr:`~UnresolvedNameWarning.Place`) is the declaration containing the type mark.

	.. important::

	   As a critical warning, it must be collected by a :class:`~pyTooling.Warning.WarningCollector` up the
	   call-hierarchy, otherwise :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised.
	"""

	_LABEL: ClassVar[str] = "Type mark"  #: The kind of name, which starts the messages of a type mark lookup.


@export
class IncompleteTypeWarning(VHDLModelCriticalWarning):
	"""
	Raised when an incomplete type declaration has no full type declaration later in the same declarative region.

	.. important::

	   As a critical warning, it must be collected by a :class:`~pyTooling.Warning.WarningCollector` up the
	   call-hierarchy, otherwise :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised.
	"""

	_incompleteType: ModelEntity  #: The incomplete type declaration.

	def __init__(self, message: str, /, *, incompleteType: ModelEntity) -> None:
		"""
		Initializes the warning with the incomplete type declaration.

		:param message:        The warning's message.
		:param incompleteType: The incomplete type declaration.
		"""
		super().__init__(message)
		self._incompleteType = incompleteType

	@readonly
	def IncompleteType(self) -> ModelEntity:
		"""
		Read-only property to access the incomplete type declaration (:attr:`_incompleteType`).

		:returns: The incomplete type declaration.
		"""
		return self._incompleteType


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
		:param instance:  Optional, the component instantiation treated as a blackbox. Default: ``None``.
		:param component: Optional, the component that couldn't be bound. Default: ``None``.
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
	   * :class:`Duplicate association error <pyVHDLModel.Exception.DuplicateAssociationError>`
	   * :class:`Association order error <pyVHDLModel.Exception.AssociationOrderError>`
	   * :class:`Duplicate document error <pyVHDLModel.Exception.DuplicateDocumentError>`
	   * :class:`Duplicate design unit error <pyVHDLModel.Exception.DuplicateDesignUnitError>`
	   * :class:`Library in use error <pyVHDLModel.Exception.LibraryInUseError>`
	   * :class:`Library not found error <pyVHDLModel.Exception.LibraryNotFoundError>`
	   * :class:`Entity not found error <pyVHDLModel.Exception.EntityNotFoundError>`
	   * :class:`Package not found error <pyVHDLModel.Exception.PackageNotFoundError>`
	   * :class:`Configuration not found error <pyVHDLModel.Exception.ConfigurationNotFoundError>`
	   * :class:`Context not found error <pyVHDLModel.Exception.ContextNotFoundError>`
	   * :class:`VHDL writer error <pyVHDLModel.Exception.VHDLWriterError>`
	   * :class:`Literal error <pyVHDLModel.Exception.LiteralError>`
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

	Message: :pycode:`f"Architecture '{architecture._identifier}' for entity '{architecture._entity._name._identifier}' already exists in library '{library._identifier}'."`
	"""

	_library:      Library       #: The library involved in this error.
	_architecture: Architecture  #: The architecture involved in this error.

	def __init__(self, architecture: Architecture, library: Library) -> None:
		"""
		Initializes the exception message based on given architecture and library objects.

		:param architecture: The architecture that already exists in the library.
		:param library:      The library that already contains the architecture.
		"""
		super().__init__(
			f"Architecture '{architecture._identifier}' for entity '{architecture._entity._name._identifier}' already exists "
			f"in library '{library._identifier}'."
		)
		self._library =      library
		self._architecture = architecture

	@readonly
	def Library(self) -> Library:
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

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
class LibraryNotInDesignError(Exception):
	"""
	The exception is raised when a library is referenced or looked up by name, but doesn't exist in the design.

	It's a common base: a kind-specific exception derives from it and from :exc:`VHDLModelException`, e.g.
	``class LibraryNotFoundError(VHDLModelException, LibraryNotInDesignError)``. It has no initializer of its own; the
	derived exception sets the fields.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.LibraryNotFoundError`
	      |rarr| Library looked up by name not found.
	   :exc:`~pyVHDLModel.Exception.ReferencedLibraryNotExistingError`
	      |rarr| Library of a context declaration's library clause not found.
	   :exc:`~pyVHDLModel.Exception.LibraryClauseLibraryNotFoundError`
	      |rarr| Library of a design unit's library clause not found.
	   :exc:`~pyVHDLModel.Exception.PackageInstantiationLibraryNotFoundError`
	      |rarr| Library of a package instantiation's generic package not found.
	   :exc:`~pyVHDLModel.Exception.EntityInstantiationLibraryNotFoundError`
	      |rarr| Library of a direct entity instantiation not found.
	"""

	_libraryName: str  #: The name of the library, which was not found.

	@readonly
	def LibraryName(self) -> str:
		"""
		Read-only property to access the library name (:attr:`_libraryName`).

		:returns: The name of the library, which was not found.
		"""
		return self._libraryName


@export
class ReferencedLibraryNotExistingError(VHDLModelException, LibraryNotInDesignError):
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
		self._libraryName =   librarySymbol.Name._identifier
		self._librarySymbol = librarySymbol
		self._context =       context

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
		:param element: Optional, the model entity to add. Default: ``None``.
		:param parent:  Optional, the model entity's current parent. Default: ``None``.
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
class NotAChildError(VHDLModelException, CommonNotAChildError):
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
		:param element: Optional, the model entity, which isn't a child. Default: ``None``.
		:param parent:  Optional, the model entity searched for the child. Default: ``None``.
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
		:param identifier: Optional, the identifier looked up. Default: ``None``.
		:param namespace:  Optional, the namespace searched for the identifier. Default: ``None``.
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
		:param identifier: Optional, the identifier declared twice. Default: ``None``.
		:param parent:     Optional, the language construct owning the generic clause. Default: ``None``.
		:param element:    Optional, the new generic. Default: ``None``.
		:param existing:   Optional, the existing declaration. Default: ``None``.
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
		:param identifier: Optional, the identifier declared twice. Default: ``None``.
		:param parent:     Optional, the language construct owning the port clause. Default: ``None``.
		:param element:    Optional, the new port. Default: ``None``.
		:param existing:   Optional, the existing declaration. Default: ``None``.
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
		:param identifier: Optional, the identifier declared twice. Default: ``None``.
		:param parent:     Optional, the language construct owning the parameter list. Default: ``None``.
		:param element:    Optional, the new parameter. Default: ``None``.
		:param existing:   Optional, the existing declaration. Default: ``None``.
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
		:param identifier: Optional, the identifier declared twice. Default: ``None``.
		:param namespace:  Optional, the namespace of the declarative region declaring it. Default: ``None``.
		:param element:    Optional, the new declaration. Default: ``None``.
		:param existing:   Optional, the existing declaration. Default: ``None``.
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
class DuplicateAssociationError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when an association list already associates the formal of a new named association.

	It's the base-class of the errors for generic, port and parameter associations.

	.. seealso::

	   * :class:`Duplicate generic association error <pyVHDLModel.Exception.DuplicateGenericAssociationError>`
	   * :class:`Duplicate port association error <pyVHDLModel.Exception.DuplicatePortAssociationError>`
	   * :class:`Duplicate parameter association error <pyVHDLModel.Exception.DuplicateParameterAssociationError>`
	"""

	_identifier:           Nullable[str]          #: The formal associated twice.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) formal.
	_parent:               Nullable[ModelEntity]  #: The language construct owning the association list.
	_element:              Nullable[ModelEntity]  #: The new association.
	_existing:             Nullable[ModelEntity]  #: The existing association.

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
		Initializes the exception with the formal, the language construct and both associations.

		:param message:    The error message.
		:param identifier: Optional, the formal associated twice. Default: ``None``.
		:param parent:     Optional, the language construct owning the association list. Default: ``None``.
		:param element:    Optional, the new association. Default: ``None``.
		:param existing:   Optional, the existing association. Default: ``None``.
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
		Read-only property to access the formal associated twice (:attr:`_identifier`).

		:returns: The formal's identifier, or ``None`` if it wasn't recorded.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) formal (:attr:`_normalizedIdentifier`).

		:returns: The normalized identifier, or ``None`` if it wasn't recorded.
		"""
		return self._normalizedIdentifier

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the language construct owning the association list (:attr:`_parent`).

		:returns: The language construct, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new association (:attr:`_element`).

		:returns: The association, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing association (:attr:`_existing`).

		:returns: The association, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicateGenericAssociationError(DuplicateAssociationError):
	"""
	This exception is raised, when a generic map aspect already associates the formal of a new generic association.
	"""


@export
class DuplicatePortAssociationError(DuplicateAssociationError):
	"""
	This exception is raised, when a port map aspect already associates the formal of a new port association.
	"""


@export
class DuplicateParameterAssociationError(DuplicateAssociationError):
	"""
	This exception is raised, when a procedure call already associates the formal of a new parameter association.
	"""


@export
class AssociationOrderError(VHDLModelException):
	"""
	This exception is raised, when a new association breaks the order of an association list.

	All positional associations of an association list precede its named associations: the existing association is a
	named association preceding a new positional association, or a positional association following a new named
	association.
	"""

	_parent:   Nullable[ModelEntity]  #: The language construct owning the association list.
	_element:  Nullable[ModelEntity]  #: The new association.
	_existing: Nullable[ModelEntity]  #: The existing association, the new association is out of order with.

	def __init__(
		self,
		message: str,
		/, *,
		parent: Nullable[ModelEntity] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the language construct and both associations.

		:param message:  The error message.
		:param parent:   Optional, the language construct owning the association list. Default: ``None``.
		:param element:  Optional, the new association. Default: ``None``.
		:param existing: Optional, the existing association, the new association is out of order with. Default: ``None``.
		"""
		super().__init__(message)
		self._parent =   parent
		self._element =  element
		self._existing = existing

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the language construct owning the association list (:attr:`_parent`).

		:returns: The language construct, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new association (:attr:`_element`).

		:returns: The association, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing association, the new association is out of order with
		(:attr:`_existing`).

		:returns: The association, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicateDocumentError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when a design already contains a document of the same path.
	"""

	_path:     Nullable[Path]         #: The path of both documents.
	_parent:   Nullable[ModelEntity]  #: The design containing the existing document.
	_element:  Nullable[ModelEntity]  #: The new document.
	_existing: Nullable[ModelEntity]  #: The existing document.

	def __init__(
		self,
		message: str,
		/, *,
		path: Nullable[Path] = None,
		parent: Nullable[ModelEntity] = None,
		element: Nullable[ModelEntity] = None,
		existing: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes the exception with the path, the design and both documents.

		:param message:  The error message.
		:param path:     Optional, the path of both documents. Default: ``None``.
		:param parent:   Optional, the design containing the existing document. Default: ``None``.
		:param element:  Optional, the new document. Default: ``None``.
		:param existing: Optional, the existing document. Default: ``None``.
		"""
		super().__init__(message)
		self._path =     path
		self._parent =   parent
		self._element =  element
		self._existing = existing

	@readonly
	def Path(self) -> Nullable[Path]:
		"""
		Read-only property to access the path of both documents (:attr:`_path`).

		:returns: The path, or ``None`` if it wasn't recorded.
		"""
		return self._path

	@readonly
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the design containing the existing document (:attr:`_parent`).

		:returns: The design, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new document (:attr:`_element`).

		:returns: The document, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing document (:attr:`_existing`).

		:returns: The document, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class DuplicateDesignUnitError(VHDLModelException, DuplicateElementError):
	"""
	This exception is raised, when a document already contains a design unit of the same kind and identifier.

	An architecture is a duplicate, if the document contains an architecture of the same identifier for the same entity.
	"""

	_identifier:           Nullable[str]          #: The identifier of both design units.
	_normalizedIdentifier: Nullable[str]          #: The normalized (lower case) identifier.
	_parent:               Nullable[ModelEntity]  #: The document containing the existing design unit.
	_element:              Nullable[ModelEntity]  #: The new design unit.
	_existing:             Nullable[ModelEntity]  #: The existing design unit.

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
		Initializes the exception with the identifier, the document and both design units.

		:param message:    The error message.
		:param identifier: Optional, the identifier of both design units. Default: ``None``.
		:param parent:     Optional, the document containing the existing design unit. Default: ``None``.
		:param element:    Optional, the new design unit. Default: ``None``.
		:param existing:   Optional, the existing design unit. Default: ``None``.
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
		Read-only property to access the identifier of both design units (:attr:`_identifier`).

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
		Read-only property to access the document containing the existing design unit (:attr:`_parent`).

		:returns: The document, or ``None`` if it wasn't recorded.
		"""
		return self._parent

	@readonly
	def Element(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the new design unit (:attr:`_element`).

		:returns: The design unit, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Existing(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the existing design unit (:attr:`_existing`).

		:returns: The design unit, or ``None`` if it wasn't recorded.
		"""
		return self._existing


@export
class ElementInUseError(VHDLModelException, InUseError, Generic[ElementType, UsersType]):
	"""
	The exception is raised when a model entity is removed, but other model entities still use it.

	It's the common base of the kind-specific exceptions: it carries the model entity to remove and the model entities
	still using it, whose types a derived exception states, e.g. ``LibraryInUseError(ElementInUseError[Library,
	Document])``.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.LibraryInUseError`
	      |rarr| Library still used by documents.
	"""

	_element: Nullable[ElementType]  #: The model entity to remove.
	_users:   tuple[UsersType, ...]  #: The model entities still using it.

	def __init__(
		self,
		message: str,
		/, *,
		element: Nullable[ElementType] = None,
		users: Nullable[tuple[UsersType, ...]] = None
	) -> None:
		"""
		Initializes the exception with the model entity to remove and the model entities still using it.

		:param message: The error message.
		:param element: Optional, the model entity to remove. Default: ``None``.
		:param users:   Optional, the model entities still using it. Default: ``None``.
		"""
		super().__init__(message)
		self._element = element
		self._users =   () if users is None else users

	@readonly
	def Element(self) -> Nullable[ElementType]:
		"""
		Read-only property to access the model entity to remove (:attr:`_element`).

		:returns: The model entity, or ``None`` if it wasn't recorded.
		"""
		return self._element

	@readonly
	def Users(self) -> tuple[UsersType, ...]:
		"""
		Read-only property to access the model entities still using the model entity to remove (:attr:`_users`).

		:returns: Tuple of model entities, empty if they weren't recorded.
		"""
		return self._users


@export
class LibraryInUseError(ElementInUseError["Library", "Document"]):
	"""
	This exception is raised, when a library is removed from a design, but documents of the design still use it.

	:attr:`Element` is the library, :attr:`Users` are the documents.

	.. hint::

	   Remove the documents from the design first, e.g. by :meth:`~pyVHDLModel.Design.RemoveDocument`.
	"""


@export
class LibraryNotFoundError(VHDLModelException, LibraryNotInDesignError):
	"""
	This exception is raised, when a library is looked up by name, but doesn't exist in the design.

	Message: :pycode:`f"Library '{libraryName}' not found in design."`
	"""

	def __init__(self, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given library name.

		:param libraryName: The name of the library, which was not found.
		"""
		super().__init__(f"Library '{libraryName}' not found in design.")
		self._libraryName = libraryName


@export
class LibraryClauseLibraryNotFoundError(VHDLModelException, LibraryNotInDesignError):
	"""
	This exception is raised, when a library clause of a design unit references a library, which doesn't exist in the
	design.

	Message: :pycode:`f"Library '{librarySymbol.Name._identifier}' referenced by library clause of design unit '{designUnit._identifier}' doesn't exist in design."`
	"""

	_librarySymbol: _Symbol      #: The library symbol that could not be resolved.
	_designUnit:    _DesignUnit  #: The design unit containing the library clause.

	def __init__(self, designUnit: _DesignUnit, librarySymbol: _Symbol) -> None:
		"""
		Initializes the exception message based on the given design unit and library symbol.

		:param designUnit:    The design unit containing the library clause.
		:param librarySymbol: The library symbol that could not be resolved.
		"""
		super().__init__(
			f"Library '{librarySymbol._name._identifier}' referenced by library clause of design unit "
			f"'{designUnit._identifier}' doesn't exist in design."
		)

		self._libraryName =   librarySymbol._name._identifier
		self._librarySymbol = librarySymbol
		self._designUnit =    designUnit

	@readonly
	def LibrarySymbol(self) -> _Symbol:
		"""
		Read-only property to access the library symbol (:attr:`_librarySymbol`).

		:returns: The library symbol.
		"""
		return self._librarySymbol

	@readonly
	def DesignUnit(self) -> _DesignUnit:
		"""
		Read-only property to access the design unit containing the library clause (:attr:`_designUnit`).

		:returns: The design unit.
		"""
		return self._designUnit


@export
class PackageInstantiationLibraryNotFoundError(VHDLModelException, LibraryNotInDesignError):
	"""
	This exception is raised, when a package instantiation references a library, which doesn't exist in the design.

	Message: :pycode:`f"Package instantiation of '{packageInstantiation._identifier}' references library '{libraryName}', which cannot be found in design."`
	"""

	_packageInstantiation: _PackageInstantiation  #: The package instantiation referencing the library.

	def __init__(self, libraryName: str, packageInstantiation: _PackageInstantiation) -> None:
		"""
		Initializes the exception message based on the given library name and package instantiation.

		:param libraryName:          The name of the library, which was not found.
		:param packageInstantiation: The package instantiation referencing the generic package in that library.
		"""
		super().__init__(
			f"Package instantiation of '{packageInstantiation._identifier}' references library '{libraryName}', which "
			"cannot be found in design."
		)

		self._libraryName =          libraryName
		self._packageInstantiation = packageInstantiation

	@readonly
	def PackageInstantiation(self) -> _PackageInstantiation:
		"""
		Read-only property to access the package instantiation (:attr:`_packageInstantiation`).

		:returns: The package instantiation referencing the library.
		"""
		return self._packageInstantiation


@export
class EntityInstantiationLibraryNotFoundError(VHDLModelException, LibraryNotInDesignError):
	"""
	This exception is raised, when a direct entity instantiation references a library, which doesn't exist in the design.

	Message: :pycode:`f"Referenced library '{libraryName}' in direct entity instantiation '{label}: entity {entityName!s}' not found in design."`
	"""

	_instantiation: EntityInstantiation  #: The direct entity instantiation referencing the library.

	def __init__(self, instantiation: EntityInstantiation) -> None:
		"""
		Initializes the exception message based on the given direct entity instantiation.

		:param instantiation: The direct entity instantiation referencing the library.
		"""
		super().__init__(
			f"Referenced library '{instantiation._entity._name._prefix._identifier}' in direct entity instantiation "
			f"'{instantiation._label}: entity {instantiation._entity._name!s}' not found in design."
		)

		self._libraryName =   instantiation._entity._name._prefix._identifier
		self._instantiation = instantiation

	@readonly
	def Instantiation(self) -> EntityInstantiation:
		"""
		Read-only property to access the direct entity instantiation (:attr:`_instantiation`).

		:returns: The direct entity instantiation referencing the library.
		"""
		return self._instantiation


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
	   :exc:`~pyVHDLModel.Exception.ComponentEntityNotFoundError`
	      |rarr| Entity of a component not found.
	   :exc:`~pyVHDLModel.Exception.InstantiatedEntityNotFoundError`
	      |rarr| Entity of a direct entity instantiation not found.
	   :exc:`~pyVHDLModel.Exception.ArchitectureEntityNotFoundError`
	      |rarr| Entity of architectures not found.
	   :exc:`~pyVHDLModel.Exception.PackageBodyPackageNotFoundError`
	      |rarr| Package of a package body not found.
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
class ComponentEntityNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when no entity matches a component, which doesn't allow blackboxes.

	Message: :pycode:`f"Entity '{component._identifier}' not found for component '{component._identifier}' in library '{libraryName}'."`
	"""

	_component: _Component  #: The component without a matching entity.

	def __init__(self, component: _Component, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given component and library name.

		:param component:   The component without a matching entity.
		:param libraryName: The name of the searched library.
		"""
		super().__init__(
			f"Entity '{component._identifier}' not found for component '{component._identifier}' in library '{libraryName}'."
		)

		self._designUnitName = component._identifier
		self._libraryName =    libraryName
		self._component =      component

	@readonly
	def Component(self) -> _Component:
		"""
		Read-only property to access the component (:attr:`_component`).

		:returns: The component without a matching entity.
		"""
		return self._component


@export
class InstantiatedEntityNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when the entity of a direct entity instantiation doesn't exist in the referenced library.

	Message: :pycode:`f"Referenced entity '{entityIdentifier}' in direct entity instantiation '{label}: entity {entityName!s}' not found in {working}library '{libraryName}'."`
	"""

	_instantiation: EntityInstantiation  #: The direct entity instantiation referencing the entity.

	def __init__(self, instantiation: EntityInstantiation, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given direct entity instantiation and library name.

		:param instantiation: The direct entity instantiation referencing the entity.
		:param libraryName:   The name of the searched library.
		"""
		super().__init__(
			f"Referenced entity '{instantiation._entity._name._identifier}' in direct entity instantiation "
			f"'{instantiation._label}: entity {instantiation._entity._name!s}' not found in "
			f"{'working ' if instantiation._entity._name._prefix._normalizedIdentifier == 'work' else ''}library "
			f"'{libraryName}'."
		)

		self._designUnitName = instantiation._entity._name._identifier
		self._libraryName =    libraryName
		self._instantiation =  instantiation

	@readonly
	def Instantiation(self) -> EntityInstantiation:
		"""
		Read-only property to access the direct entity instantiation (:attr:`_instantiation`).

		:returns: The direct entity instantiation referencing the entity.
		"""
		return self._instantiation


@export
class ArchitectureEntityNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when the entity of one or more architectures doesn't exist in their library.

	Message: :pycode:`f"Entity '{entityName}' referenced by architecture(s) '{architectureNames}' doesn't exist in library '{libraryName}'."`
	"""

	_architectureNames: tuple[str, ...]  #: The names of the architectures referencing the entity.

	def __init__(self, entityName: str, architectureNames: tuple[str, ...], libraryName: str) -> None:
		"""
		Initializes the exception message based on the given entity name, architecture names and library name.

		:param entityName:        The name of the entity, which was not found.
		:param architectureNames: The names of the architectures referencing the entity.
		:param libraryName:       The name of the searched library.
		"""
		super().__init__(
			f"""Entity '{entityName}' referenced by architecture(s) '{"', '".join(architectureNames)}' doesn't exist in """
			f"library '{libraryName}'."
		)

		self._designUnitName =    entityName
		self._libraryName =       libraryName
		self._architectureNames = architectureNames

	@readonly
	def ArchitectureNames(self) -> tuple[str, ...]:
		"""
		Read-only property to access the architecture names (:attr:`_architectureNames`).

		:returns: Tuple of names of the architectures referencing the entity.
		"""
		return self._architectureNames


@export
class PackageBodyPackageNotFoundError(VHDLModelException, DesignUnitNotFoundError):
	"""
	This exception is raised, when the package of a package body doesn't exist in its library.

	Message: :pycode:`f"Package '{packageName}' referenced by package body '{packageName}' doesn't exist in library '{libraryName}'."`
	"""

	def __init__(self, packageName: str, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given package name and library name.

		:param packageName: The name of the package, which was not found.
		:param libraryName: The name of the searched library.
		"""
		super().__init__(
			f"Package '{packageName}' referenced by package body '{packageName}' doesn't exist in library '{libraryName}'."
		)

		self._designUnitName = packageName
		self._libraryName =    libraryName


@export
class NotLinkedError(Exception):
	"""
	The exception is raised when a linking step of the analysis didn't run before a step, which needs its result.

	It's a common base: a kind-specific exception derives from it and from :exc:`VHDLModelException`, e.g.
	``class UseClauseNotLinkedError(VHDLModelException, NotLinkedError)``. It has no initializer and no fields of its
	own.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.InstantiationNotLinkedError`
	      |rarr| Instantiation of a generic language entity not linked.
	   :exc:`~pyVHDLModel.Exception.LibraryReferenceNotLinkedError`
	      |rarr| Implicit library reference of a primary unit not linked.
	   :exc:`~pyVHDLModel.Exception.UseClauseNotLinkedError`
	      |rarr| Use clause of a context declaration not linked.
	"""


@export
class InstantiationNotLinkedError(NotLinkedError):
	"""
	The exception is raised when an instantiation of a generic language entity isn't linked to it.

	A package instantiation is linked to its generic package by :meth:`~pyVHDLModel.Design.LinkPackageInstances`; the
	generic language entity's declarations are available only after linking.

	It's a common base: a kind-specific exception derives from it and from :exc:`VHDLModelException`, e.g.
	``class PackageInstantiationNotLinkedError(VHDLModelException, InstantiationNotLinkedError)``. It has no initializer
	of its own; the derived exception sets the fields.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.PackageInstantiationNotLinkedError`
	      |rarr| Package instantiation not linked to its generic package.
	"""

	_instantiationName: str  #: The name of the instantiation, which isn't linked.
	_genericName:       str  #: The name of the generic language entity, as the instantiation references it.

	@readonly
	def InstantiationName(self) -> str:
		"""
		Read-only property to access the instantiation name (:attr:`_instantiationName`).

		:returns: The name of the instantiation, which isn't linked.
		"""
		return self._instantiationName

	@readonly
	def GenericName(self) -> str:
		"""
		Read-only property to access the name of the generic language entity (:attr:`_genericName`).

		:returns: The name of the generic language entity, as the instantiation references it.
		"""
		return self._genericName


@export
class PackageInstantiationNotLinkedError(VHDLModelException, InstantiationNotLinkedError):
	"""
	This exception is raised, when a package instantiation isn't linked to its generic package.

	Message: :pycode:`f"Package instantiation '{instantiationName}' isn't linked to its generic package '{packageName}'."`
	"""

	def __init__(self, instantiationName: str, genericPackageName: str) -> None:
		"""
		Initializes the exception message based on the given instantiation name and generic package name.

		:param instantiationName:  The name of the package instantiation, which isn't linked.
		:param genericPackageName: The name of the generic package, as the instantiation references it.
		"""
		super().__init__(
			f"Package instantiation '{instantiationName}' isn't linked to its generic package '{genericPackageName}'."
		)

		self._instantiationName = instantiationName
		self._genericName =       genericPackageName


@export
class LibraryReferenceNotLinkedError(VHDLModelException, NotLinkedError):
	"""
	This exception is raised, when a primary unit doesn't reference a library, which every primary unit references
	implicitly.

	Message: :pycode:`f"Design unit '{designUnit._identifier}' doesn't reference library '{libraryName}'."`
	"""

	_designUnit:  _DesignUnit  #: The design unit without the library reference.
	_libraryName: str          #: The name of the implicitly referenced library.

	def __init__(self, designUnit: _DesignUnit, libraryName: str) -> None:
		"""
		Initializes the exception message based on the given design unit and library name.

		:param designUnit:  The design unit without the library reference.
		:param libraryName: The name of the implicitly referenced library.
		"""
		super().__init__(f"Design unit '{designUnit._identifier}' doesn't reference library '{libraryName}'.")

		self._designUnit =  designUnit
		self._libraryName = libraryName

	@readonly
	def DesignUnit(self) -> _DesignUnit:
		"""
		Read-only property to access the design unit (:attr:`_designUnit`).

		:returns: The design unit without the library reference.
		"""
		return self._designUnit

	@readonly
	def LibraryName(self) -> str:
		"""
		Read-only property to access the library name (:attr:`_libraryName`).

		:returns: The name of the implicitly referenced library.
		"""
		return self._libraryName


@export
class UseClauseNotLinkedError(VHDLModelException, NotLinkedError):
	"""
	This exception is raised, when a use clause of a context declaration isn't linked to its package.

	Message: :pycode:`f"Use clause '{symbol._name!s}' of context '{context._identifier}' isn't linked."`
	"""

	_symbol:  _Symbol   #: The symbol of the use clause, which isn't linked.
	_context: _Context  #: The context declaration containing the use clause.

	def __init__(self, symbol: _Symbol, context: _Context) -> None:
		"""
		Initializes the exception message based on the given symbol and context declaration.

		:param symbol:  The symbol of the use clause, which isn't linked.
		:param context: The context declaration containing the use clause.
		"""
		super().__init__(f"Use clause '{symbol._name!s}' of context '{context._identifier}' isn't linked.")

		self._symbol =  symbol
		self._context = context

	@readonly
	def Symbol(self) -> _Symbol:
		"""
		Read-only property to access the symbol of the use clause (:attr:`_symbol`).

		:returns: The symbol, which isn't linked.
		"""
		return self._symbol

	@readonly
	def Context(self) -> _Context:
		"""
		Read-only property to access the context declaration (:attr:`_context`).

		:returns: The context declaration containing the use clause.
		"""
		return self._context


@export
class NotComputedError(Exception):
	"""
	The exception is raised when a graph of the analysis isn't computed before it's used.

	It's a common base: a kind-specific exception derives from it and from :exc:`VHDLModelException`, e.g.
	``class HierarchyNotComputedError(VHDLModelException, NotComputedError)``. It has no initializer and no fields of its
	own.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.HierarchyNotComputedError`
	      |rarr| Hierarchy graph not computed.
	   :exc:`~pyVHDLModel.Exception.CompileOrderNotComputedError`
	      |rarr| Compile order not computed.
	"""


@export
class HierarchyNotComputedError(VHDLModelException, NotComputedError):
	"""
	This exception is raised, when the design's top-level is requested before the hierarchy graph is computed.

	Message: :pycode:`"Hierarchy is not yet computed from dependency graph."`
	"""

	def __init__(self) -> None:
		"""
		Initializes the exception message.
		"""
		super().__init__("Hierarchy is not yet computed from dependency graph.")


@export
class CompileOrderNotComputedError(VHDLModelException, NotComputedError):
	"""
	This exception is raised, when documents are iterated in compile order before the compile order is computed.

	Message: :pycode:`"Compile order is not yet computed from dependency graph."`
	"""

	def __init__(self) -> None:
		"""
		Initializes the exception message.
		"""
		super().__init__("Compile order is not yet computed from dependency graph.")


@export
class LibraryNotVisibleError(Exception):
	"""
	The exception is raised when a design unit references a library, whose name no library clause made visible.

	It's a common base: a kind-specific exception derives from it and from :exc:`VHDLModelException`, e.g.
	``class UseClauseLibraryNotVisibleError(VHDLModelException, LibraryNotVisibleError)``. It has no initializer of its
	own; the derived exception sets the fields.

	.. seealso::

	   :exc:`~pyVHDLModel.Exception.UseClauseLibraryNotVisibleError`
	      |rarr| Library of a use clause not visible.
	   :exc:`~pyVHDLModel.Exception.ContextReferenceLibraryNotVisibleError`
	      |rarr| Library of a context reference not visible.
	   :exc:`~pyVHDLModel.Exception.PackageInstantiationLibraryNotVisibleError`
	      |rarr| Library of a package instantiation's generic package not visible.
	   :exc:`~pyVHDLModel.Exception.EntityInstantiationLibraryNotVisibleError`
	      |rarr| Library of a direct entity instantiation not visible.
	"""

	_libraryName: str          #: The name of the library, which isn't visible.
	_designUnit:  _DesignUnit  #: The design unit referencing the library.

	@readonly
	def LibraryName(self) -> str:
		"""
		Read-only property to access the library name (:attr:`_libraryName`).

		:returns: The name of the library, which isn't visible.
		"""
		return self._libraryName

	@readonly
	def DesignUnit(self) -> _DesignUnit:
		"""
		Read-only property to access the design unit referencing the library (:attr:`_designUnit`).

		:returns: The design unit referencing the library.
		"""
		return self._designUnit


@export
class UseClauseLibraryNotVisibleError(VHDLModelException, LibraryNotVisibleError):
	"""
	This exception is raised, when a use clause references a library, whose name no library clause made visible.

	Message: :pycode:`f"Use clause references library '{libraryName}', which was not referenced by a library clause."`
	"""

	def __init__(self, libraryName: str, designUnit: _DesignUnit) -> None:
		"""
		Initializes the exception message based on the given library name and design unit.

		:param libraryName: The name of the library, which isn't visible.
		:param designUnit:  The design unit containing the use clause.
		"""
		super().__init__(
			f"Use clause references library '{libraryName}', which was not referenced by a library clause."
		)

		self._libraryName = libraryName
		self._designUnit =  designUnit


@export
class ContextReferenceLibraryNotVisibleError(VHDLModelException, LibraryNotVisibleError):
	"""
	This exception is raised, when a context reference references a library, whose name no library clause made visible.

	Message: :pycode:`f"Context reference references library '{libraryName}', which was not referenced by a library clause."`
	"""

	def __init__(self, libraryName: str, designUnit: _DesignUnit) -> None:
		"""
		Initializes the exception message based on the given library name and design unit.

		:param libraryName: The name of the library, which isn't visible.
		:param designUnit:  The design unit containing the context reference.
		"""
		super().__init__(
			f"Context reference references library '{libraryName}', which was not referenced by a library clause."
		)

		self._libraryName = libraryName
		self._designUnit =  designUnit


@export
class PackageInstantiationLibraryNotVisibleError(VHDLModelException, LibraryNotVisibleError):
	"""
	This exception is raised, when a package instantiation references a library, whose name no library clause made
	visible.

	Message: :pycode:`f"Package instantiation of '{packageInstantiation._identifier}' references library '{libraryName}', which was not referenced by a library clause."`
	"""

	def __init__(self, libraryName: str, packageInstantiation: _PackageInstantiation) -> None:
		"""
		Initializes the exception message based on the given library name and package instantiation.

		:param libraryName:          The name of the library, which isn't visible.
		:param packageInstantiation: The package instantiation referencing the generic package in that library.
		"""
		super().__init__(
			f"Package instantiation of '{packageInstantiation._identifier}' references library '{libraryName}', which was "
			"not referenced by a library clause."
		)

		self._libraryName = libraryName
		self._designUnit =  packageInstantiation


@export
class EntityInstantiationLibraryNotVisibleError(VHDLModelException, LibraryNotVisibleError):
	"""
	This exception is raised, when a direct entity instantiation references a library, whose name no library clause made
	visible.

	Message: :pycode:`f"Referenced library '{libraryName}' in direct entity instantiation '{label}: entity {entityName!s}' not found in architecture '{architecture!r}'."`
	"""

	_instantiation: EntityInstantiation  #: The direct entity instantiation referencing the library.

	def __init__(self, instantiation: EntityInstantiation, architecture: Architecture) -> None:
		"""
		Initializes the exception message based on the given direct entity instantiation and architecture.

		:param instantiation: The direct entity instantiation referencing the library.
		:param architecture:  The architecture containing the instantiation.
		"""
		super().__init__(
			f"Referenced library '{instantiation._entity._name._prefix._identifier}' in direct entity instantiation "
			f"'{instantiation._label}: entity {instantiation._entity._name!s}' not found in architecture '{architecture!r}'."
		)

		self._libraryName =   instantiation._entity._name._prefix._identifier
		self._designUnit =    architecture
		self._instantiation = instantiation

	@readonly
	def Instantiation(self) -> EntityInstantiation:
		"""
		Read-only property to access the direct entity instantiation (:attr:`_instantiation`).

		:returns: The direct entity instantiation referencing the library.
		"""
		return self._instantiation


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


@export
class LiteralError(VHDLModelException, ValueError):
	"""
	This exception is raised, when a literal's value violates the rules of its literal kind.

	E.g. a bit string literal's length truncates significant characters. It's a :exc:`ValueError` too, like
	converting an invalid text to a number.
	"""

	_literal: _Literal  #: The literal with the invalid value.

	def __init__(self, message: str, /, *, literal: _Literal) -> None:
		"""
		Initializes the exception with a message and the literal with the invalid value.

		:param message: The error message.
		:param literal: The literal with the invalid value.
		"""
		super().__init__(message)
		self._literal = literal

	@readonly
	def Literal(self) -> _Literal:
		"""
		Read-only property to access the literal with the invalid value (:attr:`_literal`).

		:returns: The literal with the invalid value.
		"""
		return self._literal
