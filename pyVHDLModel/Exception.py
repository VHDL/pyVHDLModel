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

The module ``Exceptions`` contains all structured errors that are raised by pyVHDLModel. Besides a default error
message in english, each exception object contains one or multiple references to the exception's context.
"""
from pyTooling.Decorators import export

from pyVHDLModel.Symbol import Symbol


@export
class VHDLModelException(Exception):
	"""Base-class for all exceptions (errors) raised by pyVHDLModel."""


@export
class LibraryExistsInDesignError(VHDLModelException):
	"""
	This exception is raised, when the library is already existing in the design.

	Message: :pycode:`f"Library '{library.Identifier}' already exists in design."`
	"""

	_library: 'Library'

	def __init__(self, library: 'Library'):
		"""
		Initializes the exception message based on given library object.

		:param library: The library that already exists in the design.
		"""
		super().__init__(f"Library '{library.Identifier}' already exists in design.")
		self._library = library

	@property
	def Library(self) -> 'Library':
		return self._library


@export
class LibraryRegisteredToForeignDesignError(VHDLModelException):
	"""
	This exception is raised, when the library is already registered to a foreign design.

	Message: :pycode:`f"Library '{library.Identifier}' already registered in design '{library.Parent}'."`
	"""

	_library: 'Library'

	def __init__(self, library: 'Library'):
		"""
		Initializes the exception message based on given library object.

		:param library: The library that is already registered to another design.
		"""
		super().__init__(f"Library '{library.Identifier}' already registered in design '{library.Parent}'.")
		self._library = library

	@property
	def Library(self) -> 'Library':
		return self._library


@export
class LibraryNotRegisteredError(VHDLModelException):
	"""
	This exception is raised, when the library is not registered in the design.

	Message: :pycode:`f"Library '{library.Identifier}' is not registered in the design."`
	"""

	_library: 'Library'

	def __init__(self, library: 'Library'):
		"""
		Initializes the exception message based on given library object.

		:param library: The library that isn't registered in the design.
		"""
		super().__init__(f"Library '{library.Identifier}' is not registered in the design.")
		self._library = library

	@property
	def Library(self) -> 'Library':
		return self._library


@export
class EntityExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the entity already existing in the library.

	Message: :pycode:`f"Entity '{entity.Identifier}' already exists in library '{library.Identifier}'."`
	"""

	_library: 'Library'
	_entity: 'Entity'

	def __init__(self, entity: 'Entity', library: 'Library'):
		"""
		Initializes the exception message based on given entity and library objects.

		:param entity:  The entity that already exists in the library.
		:param library: The library that already contains the entity.
		"""
		super().__init__(f"Entity '{entity.Identifier}' already exists in library '{library.Identifier}'.")
		self._library = library
		self._entity = entity

	@property
	def Library(self) -> 'Library':
		return self._library

	@property
	def Entity(self) -> 'Entity':
		return self._entity


@export
class ArchitectureExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the architecture already existing in the library.

	Message: :pycode:`f"Architecture '{architecture.Identifier}' for entity '{entity.Identifier}' already exists in library '{library.Identifier}'."`
	"""

	_library: 'Library'
	_entity: 'Entity'
	_architecture: 'Architecture'

	def __init__(self, architecture: 'Architecture', entity: 'Entity', library: 'Library'):
		"""
		Initializes the exception message based on given architecture, entity and library objects.

		:param architecture: The architecture that already exists in the library.
		:param entity:       The entity the architecture refers to, which already exists in the library.
		:param library:      The library that already contains the architecture.
		"""
		super().__init__(f"Architecture '{architecture.Identifier}' for entity '{entity.Identifier}' already exists in library '{library.Identifier}'.")
		self._library = library
		self._entity = entity
		self._architecture = architecture

	@property
	def Library(self) -> 'Library':
		return self._library

	@property
	def Entity(self) -> 'Entity':
		return self._entity

	@property
	def Architecture(self) -> 'Architecture':
		return self._architecture


@export
class PackageExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the package already existing in the library.

	Message: :pycode:`f"Package '{package.Identifier}' already exists in library '{library.Identifier}'."`
	"""

	_library: 'Library'
	_package: 'Package'

	def __init__(self, package: 'Package', library: 'Library'):
		"""
		Initializes the exception message based on given package and library objects.

		:param package: The package that already exists in the library.
		:param library: The library that already contains the package.
		"""
		super().__init__(f"Package '{package.Identifier}' already exists in library '{library.Identifier}'.")
		self._library = library
		self._package = package

	@property
	def Library(self) -> 'Library':
		return self._library

	@property
	def Package(self) -> 'Package':
		return self._package


@export
class PackageBodyExistsError(VHDLModelException):
	"""
	This exception is raised, when the package body already existing in the library.

	Message: :pycode:`f"Package body '{packageBody.Identifier}' already exists in library '{library.Identifier}'."`
	"""

	_library: 'Library'
	_packageBody: 'PackageBody'

	def __init__(self, packageBody: 'PackageBody', library: 'Library'):
		"""
		Initializes the exception message based on given package body and library objects.

		:param packageBody: The package body that already exists in the library.
		:param library:     The library that already contains the package body.
		"""
		super().__init__(f"Package body '{packageBody.Identifier}' already exists in library '{library.Identifier}'.")
		self._library = library
		self._packageBody = packageBody

	@property
	def Library(self) -> 'Library':
		return self._library

	@property
	def PackageBody(self) -> 'PackageBody':
		return self._packageBody


@export
class ConfigurationExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the configuration already existing in the library.

	Message: :pycode:`f"Configuration '{configuration.Identifier}' already exists in library '{library.Identifier}'."`
	"""

	_library: 'Library'
	_configuration: 'Configuration'

	def __init__(self, configuration: 'Configuration', library: 'Library'):
		"""
		Initializes the exception message based on given configuration and library objects.

		:param configuration: The configuration that already exists in the library.
		:param library:       The library that already contains the configuration.
		"""
		super().__init__(f"Configuration '{configuration.Identifier}' already exists in library '{library.Identifier}'.")
		self._library = library
		self._configuration = configuration

	@property
	def Library(self) -> 'Library':
		return self._library

	@property
	def Configuration(self) -> 'Configuration':
		return self._configuration


@export
class ContextExistsInLibraryError(VHDLModelException):
	"""
	This exception is raised, when the context already existing in the library.

	Message: :pycode:`f"Context '{context.Identifier}' already exists in library '{library.Identifier}'."`
	"""

	_library: 'Library'
	_context: 'Context'

	def __init__(self, context: 'Context', library: 'Library'):
		"""
		Initializes the exception message based on given context and library objects.

		:param context: The context that already exists in the library.
		:param library: The library that already contains the context.
		"""
		super().__init__(f"Context '{context.Identifier}' already exists in library '{library.Identifier}'.")
		self._library = library
		self._context = context

	@property
	def Library(self) -> 'Library':
		return self._library

	@property
	def Context(self) -> 'Context':
		return self._context


@export
class ReferencedLibraryNotExistingError(VHDLModelException):
	"""
	This exception is raised, when a library is referenced by a `library clause`, but doesn't exist in the design.

	Message: :pycode:`f"Library '{librarySymbol.Identifier}' referenced by library clause of context '{context.Identifier}' doesn't exist in design."`
	"""

	_librarySymbol: Symbol
	_context: 'Context'

	def __init__(self, context: 'Context', librarySymbol: Symbol):
		"""
		Initializes the exception message based on given context and library objects.

		:param context:       The context that already exists in the library.
		:param librarySymbol: The library that already contains the context.
		"""
		super().__init__(f"Library '{librarySymbol.Identifier}' referenced by library clause of context '{context.Identifier}' doesn't exist in design.")
		self._librarySymbol = librarySymbol
		self._context = context

	@property
	def LibrarySymbol(self) -> Symbol:
		return self._librarySymbol

	@property
	def Context(self) -> 'Context':
		return self._context
