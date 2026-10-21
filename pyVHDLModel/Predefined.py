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
"""This module contains base-classes for predefined library and package declarations."""
from typing                 import Iterable, Optional as Nullable

from pyTooling.Common       import getTypeName
from pyTooling.Decorators   import export
from pyTooling.MetaClasses  import ExtendedType, abstractclass

from pyVHDLModel            import Library, Package, PackageBody, AllPackageMembersReferenceSymbol, PackageMemberReferenceSymbol
from pyVHDLModel.Name       import SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol     import LibraryReferenceSymbol, PackageSymbol
from pyVHDLModel.DesignUnit import LibraryClause, UseClause


@export
@abstractclass
class PredefinedLibrary(Library):
	"""
	A base-class for predefined VHDL libraries.

	VHDL defines 2 predefined libraries:

	* :class:`~pyVHDLModel.STD.Std`
	* :class:`~pyVHDLModel.IEEE.Ieee`

	.. seealso::

	   * :class:`Ieee <pyVHDLModel.IEEE.Ieee>`
	   * :class:`Std <pyVHDLModel.STD.Std>`
	"""

	def __init__(self, packages, documentation: Nullable[str] = None) -> None:
		"""
		Initializes a predefined library.

		:param packages:      Dictionary of all packages defined in a library.
		:param documentation: Documentation of this library, if the caller has one to supply. VHDL defines
		                      none for a predefined library, so it is empty unless supplied from outside.
		"""
		super().__init__(getTypeName(self), documentation)

		self.AddPackages(packages)

	def AddPackages(self, packages) -> None:
		for packageType, packageBodyType in packages:
			package: Package = packageType()
			package.Library = self
			self._packages[package.NormalizedIdentifier] = package

			if packageBodyType is not None:
				packageBody: PackageBody = packageBodyType()
				packageBody.Library = self
				self._packageBodies[packageBody.NormalizedIdentifier] = packageBody


@export
class PredefinedPackageMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_contextItems", "_libraryReferences", "_packageReferences")
):
	"""
	A mixin-class for predefined VHDL packages and package bodies.

	The host class provides the lists of context items ``_contextItems``, library clauses ``_libraryReferences`` and use
	clauses ``_packageReferences``.

	.. seealso::

	   * :class:`Predefined package <pyVHDLModel.Predefined.PredefinedPackage>`
	   * :class:`Predefined package body <pyVHDLModel.Predefined.PredefinedPackageBody>`
	"""

	def _AddLibraryClause(self, libraries: Iterable[str]) -> None:
		symbols = [LibraryReferenceSymbol(SimpleName(libName)) for libName in libraries]
		libraryClause = LibraryClause(symbols)

		self._contextItems.append(libraryClause)
		self._libraryReferences.append(libraryClause)

	def _AddPackageClause(self, packages: Iterable[str]) -> None:
		symbols = []
		for qualifiedPackageName in packages:
			libName, packName, members = qualifiedPackageName.split(".")

			packageName = SelectedName(packName, SimpleName(libName))
			if members.lower() == "all":
				symbols.append(AllPackageMembersReferenceSymbol(AllName(packageName)))
			else:
				symbols.append(PackageMemberReferenceSymbol(SelectedName(members, packageName)))

		useClause = UseClause(symbols)
		self._contextItems.append(useClause)
		self._packageReferences.append(useClause)


@export
@abstractclass
class PredefinedPackage(Package, PredefinedPackageMixin):
	"""
	A base-class for predefined VHDL packages.
	"""

	def __init__(self, identifier: Nullable[str] = None) -> None:
		"""
		Initializes a predefined package.

		By default the VHDL package name is the Python class name. Pass ``identifier`` when the two must
		differ - e.g. when two vendor flavors of the same VHDL package need distinct Python classes.

		:param identifier: The VHDL package name, or ``None`` to use the class name.
		"""
		super().__init__(getTypeName(self) if identifier is None else identifier)


@export
@abstractclass
class PredefinedPackageBody(PackageBody, PredefinedPackageMixin):
	"""
	A base-class for predefined VHDL package bodies.
	"""

	def __init__(self, packageIdentifier: Nullable[str] = None) -> None:
		"""
		Initializes a predefined package body.

		By default the VHDL package name is the Python class name with the trailing ``_Body`` removed.
		Pass ``packageIdentifier`` when the two must differ.

		:param packageIdentifier: The VHDL name of the package this body implements, or ``None`` to derive
		                          it from the class name.
		"""
		identifier = getTypeName(self)[:-5] if packageIdentifier is None else packageIdentifier
		packageSymbol = PackageSymbol(SimpleName(identifier))
		super().__init__(packageSymbol)
