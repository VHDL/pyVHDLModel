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
from pyTooling.Decorators import export, readonly
from pyTooling.Exceptions import ExceptionBase
from pyTooling.Warning    import Warning, CriticalWarning

from pyVHDLModel.Symbol   import Symbol


@export
class VHDLModelWarning(Warning):
	"""
	Base-class for all warnings raised by pyVHDLModel.

	.. seealso::

	   * :class:`Not implemented warning <pyVHDLModel.Exception.NotImplementedWarning>`
	"""
	pass


@export
class NotImplementedWarning(VHDLModelWarning):
	"""
	Raised when a language construct is recognised but not yet modelled.
	"""
	pass


@export
class VHDLModelCriticalWarning(Warning):
	"""
	Base-class for critical warnings that likely indicate a defect in the model or its input.

	.. seealso::

	   * :class:`Blackbox warning <pyVHDLModel.Exception.BlackboxWarning>`
	"""
	pass


@export
class DuplicateDeclarationWarning(VHDLModelCriticalWarning):
	"""
	Raised when two declarations in one declarative region share an identifier.

	VHDL rejects this as *identifier already used for a declaration*. Overloadable declarations -
	subprograms differing in signature - are not reported.
	"""
	pass


@export
class BlackboxWarning(VHDLModelCriticalWarning):
	"""
	Raised when a component could not be bound and is treated as a blackbox.
	"""
	pass


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
	"""


@export
class LibraryExistsInDesignError(VHDLModelException):
	"""
	This exception is raised, when the library is already existing in the design.

	Message: :pycode:`f"Library '{library._identifier}' already exists in design."`
	"""

	_library: 'Library'  #: The library involved in this error.

	def __init__(self, library: 'Library') -> None:
		"""
		Initializes the exception message based on given library object.

		:param library: The library that already exists in the design.
		"""
		super().__init__(f"Library '{library._identifier}' already exists in design.")
		self._library = library

	@readonly
	def Library(self) -> 'Library':
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

	_library: 'Library'  #: The library involved in this error.

	def __init__(self, library: 'Library') -> None:
		"""
		Initializes the exception message based on given library object.

		:param library: The library that is already registered to another design.
		"""
		super().__init__(f"Library '{library._identifier}' already registered in design '{library.Parent}'.")
		self._library = library

	@readonly
	def Library(self) -> 'Library':
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

	_library: 'Library'  #: The library involved in this error.

	def __init__(self, library: 'Library') -> None:
		"""
		Initializes the exception message based on given library object.

		:param library: The library that isn't registered in the design.
		"""
		super().__init__(f"Library '{library._identifier}' is not registered in the design.")
		self._library = library

	@readonly
	def Library(self) -> 'Library':
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

	_library: 'Library'  #: The library involved in this error.
	_entity: 'Entity'    #: The entity involved in this error.

	def __init__(self, entity: 'Entity', library: 'Library') -> None:
		"""
		Initializes the exception message based on given entity and library objects.

		:param entity:  The entity that already exists in the library.
		:param library: The library that already contains the entity.
		"""
		super().__init__(f"Entity '{entity._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._entity = entity

	@readonly
	def Library(self) -> 'Library':
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Entity(self) -> 'Entity':
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

	_library: 'Library'            #: The library involved in this error.
	_entity: 'Entity'              #: The entity involved in this error.
	_architecture: 'Architecture'  #: The architecture involved in this error.

	def __init__(self, architecture: 'Architecture', entity: 'Entity', library: 'Library') -> None:
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
	def Library(self) -> 'Library':
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Entity(self) -> 'Entity':
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	@readonly
	def Architecture(self) -> 'Architecture':
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

	_library: 'Library'  #: The library involved in this error.
	_package: 'Package'  #: The package involved in this error.

	def __init__(self, package: 'Package', library: 'Library') -> None:
		"""
		Initializes the exception message based on given package and library objects.

		:param package: The package that already exists in the library.
		:param library: The library that already contains the package.
		"""
		super().__init__(f"Package '{package._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._package = package

	@readonly
	def Library(self) -> 'Library':
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Package(self) -> 'Package':
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

	_library: 'Library'          #: The library involved in this error.
	_packageBody: 'PackageBody'  #: The package body involved in this error.

	def __init__(self, packageBody: 'PackageBody', library: 'Library') -> None:
		"""
		Initializes the exception message based on given package body and library objects.

		:param packageBody: The package body that already exists in the library.
		:param library:     The library that already contains the package body.
		"""
		super().__init__(f"Package body '{packageBody._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._packageBody = packageBody

	@readonly
	def Library(self) -> 'Library':
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def PackageBody(self) -> 'PackageBody':
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

	_library: 'Library'              #: The library involved in this error.
	_configuration: 'Configuration'  #: The configuration involved in this error.

	def __init__(self, configuration: 'Configuration', library: 'Library') -> None:
		"""
		Initializes the exception message based on given configuration and library objects.

		:param configuration: The configuration that already exists in the library.
		:param library:       The library that already contains the configuration.
		"""
		super().__init__(f"Configuration '{configuration._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._configuration = configuration

	@readonly
	def Library(self) -> 'Library':
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Configuration(self) -> 'Configuration':
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

	_library: 'Library'  #: The library involved in this error.
	_context: 'Context'  #: The context involved in this error.

	def __init__(self, context: 'Context', library: 'Library') -> None:
		"""
		Initializes the exception message based on given context and library objects.

		:param context: The context that already exists in the library.
		:param library: The library that already contains the context.
		"""
		super().__init__(f"Context '{context._identifier}' already exists in library '{library._identifier}'.")
		self._library = library
		self._context = context

	@readonly
	def Library(self) -> 'Library':
		"""
		Read-only property to access the library (:attr:`_library`).

		:returns: The library.
		"""
		return self._library

	@readonly
	def Context(self) -> 'Context':
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

	_librarySymbol: Symbol  #: The library symbol that could not be resolved.
	_context: 'Context'     #: The context involved in this error.

	def __init__(self, context: 'Context', librarySymbol: Symbol) -> None:
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
	def Context(self) -> 'Context':
		"""
		Read-only property to access the context (:attr:`_context`).

		:returns: The context.
		"""
		return self._context
