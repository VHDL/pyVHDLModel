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
"""This module contains library and package declarations for VHDL library ``STD``."""
from typing                  import Iterable

from pyTooling.Decorators    import export

from pyVHDLModel import Library
from pyVHDLModel.Symbol      import LibraryReferenceSymbol, PackageReferenceSymbol, PackageMembersReferenceSymbol, AllPackageMembersReferenceSymbol, PackageSymbol
from pyVHDLModel.DesignUnit  import LibraryClause, UseClause, Package, PackageBody


@export
class PredefinedLibrary(Library):
	def __init__(self, packages):
		super().__init__(self.__class__.__name__)

		for packageType, packageBodyType in packages:
			package: Package = packageType()
			package.Library = self
			self._packages[package.NormalizedIdentifier] = package

			if packageBodyType is not None:
				packageBody: PackageBody = packageBodyType()
				packageBody.Library = self
				self._packageBodies[packageBody.NormalizedIdentifier] = packageBody


@export
class PredefinedMixin:
	def _AddLibraryClause(self, libraries: Iterable[str]):
		symbols = [LibraryReferenceSymbol(libName) for libName in libraries]
		libraryClause = LibraryClause(symbols)

		self._contextItems.append(libraryClause)
		self._libraryReferences.append(libraryClause)

	def _AddPackageClause(self, packages: Iterable[str]):
		symbols = []
		for qualifiedPackageName in packages:
			libName, packName, members = qualifiedPackageName.split(".")
			packageSymbol = PackageReferenceSymbol(packName, LibraryReferenceSymbol(libName))
			if members.lower() == "all":
				symbols.append(AllPackageMembersReferenceSymbol(packageSymbol))
			else:
				symbols.append(PackageMembersReferenceSymbol(members, packageSymbol))

		useClause = UseClause(symbols)
		self._contextItems.append(useClause)
		self._packageReferences.append(useClause)


@export
class PredefinedPackage(Package, PredefinedMixin):
	def __init__(self):
		super().__init__(self.__class__.__name__)


@export
class PredefinedPackageBody(PackageBody, PredefinedMixin):
	def __init__(self):
		packageSymbol = PackageSymbol(self.__class__.__name__[:-5])
		super().__init__(packageSymbol)


@export
class Std(PredefinedLibrary):
	def __init__(self):
		super().__init__(PACKAGES)


@export
class Standard(PredefinedPackage):
	pass


@export
class Standard_Body(PredefinedPackageBody):
	pass


@export
class TextIO(PredefinedPackage):
	pass


@export
class TextIO_Body(PredefinedPackageBody):
	pass


@export
class Env(PredefinedPackage):
	def __init__(self):
		super().__init__()

		# Use clauses
		useTextIOSymbols = (
			AllPackageMembersReferenceSymbol(PackageReferenceSymbol("textio", LibraryReferenceSymbol("work"))),
		)
		self._packageReferences.append(UseClause(useTextIOSymbols))


@export
class Env_Body(PredefinedPackageBody):
	pass


PACKAGES = (
	(Standard, Standard_Body),
	(TextIO, TextIO_Body),
	(Env, Env_Body),
)
