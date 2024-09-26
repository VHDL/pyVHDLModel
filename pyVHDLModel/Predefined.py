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
"""This module contains base-classes for predefined library and package declarations."""
from typing                 import Iterable

from pyTooling.Decorators   import export
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel            import Library, Package, PackageBody, AllPackageMembersReferenceSymbol, PackageMemberReferenceSymbol
from pyVHDLModel.Name       import SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol     import LibraryReferenceSymbol, PackageSymbol
from pyVHDLModel.DesignUnit import LibraryClause, UseClause


@export
class PredefinedLibrary(Library):
	"""
	A base-class for predefined VHDL libraries.

	VHDL defines 2 predefined libraries:

	* :class:`~pyVHDLModel.STD.Std`
	* :class:`~pyVHDLModel.IEEE.Ieee`
	"""

	def __init__(self, packages) -> None:
		super().__init__(self.__class__.__name__, None)

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
class PredefinedPackageMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for predefined VHDL packages and package bodies.
	"""

	def _AddLibraryClause(self, libraries: Iterable[str]):
		symbols = [LibraryReferenceSymbol(SimpleName(libName)) for libName in libraries]
		libraryClause = LibraryClause(symbols)

		self._contextItems.append(libraryClause)
		self._libraryReferences.append(libraryClause)

	def _AddPackageClause(self, packages: Iterable[str]):
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
class PredefinedPackage(Package, PredefinedPackageMixin):
	"""
	A base-class for predefined VHDL packages.
	"""

	def __init__(self) -> None:
		super().__init__(self.__class__.__name__, parent=None)


@export
class PredefinedPackageBody(PackageBody, PredefinedPackageMixin):
	"""
	A base-class for predefined VHDL package bodies.
	"""

	def __init__(self) -> None:
		packageSymbol = PackageSymbol(SimpleName(self.__class__.__name__[:-5]))
		super().__init__(packageSymbol, parent=None)
