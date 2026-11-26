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
from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType, abstractclass

from pyVHDLModel            import Library, Package, PackageBody, AllPackageMembersReferenceSymbol, \
                                   PackageMemberReferenceSymbol
from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, ExpressionUnion, Mode
from pyVHDLModel.Name       import SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol     import LibraryReferenceSymbol, PackageSymbol, SimpleSubtypeSymbol, \
                                   SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.DesignUnit import LibraryClause, UseClause
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Subprogram


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
		:param documentation: Optional, documentation of this library, if the caller has one to supply. VHDL defines none
		                      for a predefined library, so it is empty unless supplied from outside.
		                      Default: ``None``, no documentation.
		"""
		super().__init__(getTypeName(self), documentation)

		self.AddPackages(packages)

	@readonly
	def IsPredefined(self) -> bool:
		"""
		Check if the library is a predefined library built by pyVHDLModel.

		:returns: ``True``
		"""
		return True

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
	expects=("AddContextItem",)
):
	"""
	A mixin-class for predefined VHDL packages and package bodies.

	The host class provides ``AddContextItem(contextItem)``, called to add a library clause or a use clause.

	.. seealso::

	   * :class:`Predefined package <pyVHDLModel.Predefined.PredefinedPackage>`
	   * :class:`Predefined package body <pyVHDLModel.Predefined.PredefinedPackageBody>`
	"""

	def _AddLibraryClause(self, libraries: Iterable[str]) -> None:
		symbols = [LibraryReferenceSymbol(SimpleName(libName)) for libName in libraries]
		libraryClause = LibraryClause(symbols)

		self.AddContextItem(libraryClause)

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
		self.AddContextItem(useClause)


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

		:param identifier: Optional, the VHDL package name. Default: ``None``, the class name.
		"""
		super().__init__(getTypeName(self) if identifier is None else identifier)

	def _DeclareItem(self, declaration: NamedEntityMixin, table: dict[str, ModelEntity]) -> None:
		"""
		Add a declaration to this package and to the package's lookup table of its kind.

		:param declaration: The declaration.
		:param table:       The lookup table of the declaration's kind, e.g. :attr:`_types`.
		"""
		table[declaration._normalizedIdentifier] = declaration
		self.AddDeclaredItem(declaration)

	def _DeclareSubprogram(self, subprogram: Subprogram, table: dict[str, list[Subprogram]]) -> None:
		"""
		Add a subprogram to this package and to the package's lookup table of its kind, after its overloads.

		:param subprogram: The subprogram.
		:param table:      The lookup table of the subprogram's kind, :attr:`_procedures` or :attr:`_functions`.
		"""
		table.setdefault(subprogram._normalizedIdentifier, []).append(subprogram)
		self.AddDeclaredItem(subprogram)

	@staticmethod
	def _TypeMark(identifier: str) -> SimpleSubtypeSymbol:
		"""
		Create a type mark naming a type or subtype by its simple name.

		:param identifier: The identifier of the type or subtype.
		:returns:          The type mark.
		"""
		return SimpleSubtypeSymbol(SimpleName(identifier))

	@staticmethod
	def _InParameter(
		identifiers:       Iterable[str],
		subtype:           SimpleSubtypeSymbol,
		defaultExpression: Nullable[ExpressionUnion] = None
	) -> ParameterConstantInterfaceItem:
		"""
		Create a constant parameter of mode ``in`` of a subprogram of a predefined package.

		:param identifiers:       The parameter's identifiers.
		:param subtype:           The parameter's type mark.
		:param defaultExpression: Optional, the default value. Default: ``None``, no default value.
		:returns:                 The parameter.
		"""
		return ParameterConstantInterfaceItem(identifiers, Mode.In, subtype, defaultExpression)

	@staticmethod
	def _OutParameter(identifiers: Iterable[str], subtype: SimpleSubtypeSymbol) -> ParameterVariableInterfaceItem:
		"""
		Create a variable parameter of mode ``out`` of a subprogram of a predefined package.

		:param identifiers: The parameter's identifiers.
		:param subtype:     The parameter's type mark.
		:returns:           The parameter.
		"""
		return ParameterVariableInterfaceItem(identifiers, Mode.Out, subtype)

	def _LineParameter(self) -> ParameterVariableInterfaceItem:
		"""
		Create the parameter ``L : inout LINE`` of the ``READ`` and ``WRITE`` procedures (IEEE Std 1076-2008, 16.4).

		:returns: The parameter.
		"""
		return ParameterVariableInterfaceItem(("L",), Mode.InOut, self._TypeMark("line"))

	def _JustificationParameters(self) -> tuple[ParameterConstantInterfaceItem, ParameterConstantInterfaceItem]:
		"""
		Create the parameters ``JUSTIFIED : SIDE := RIGHT`` and ``FIELD : WIDTH := 0`` of the ``WRITE`` procedures
		(IEEE Std 1076-2008, 16.4).

		:returns: The two parameters.
		"""
		return (
			self._InParameter(("JUSTIFIED",), self._TypeMark("side"), SimpleObjectOrFunctionCallSymbol(SimpleName("right"))),
			self._InParameter(("FIELD",), self._TypeMark("width"), IntegerLiteral(0))
		)


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

		:param packageIdentifier: Optional, the VHDL name of the package this body implements.
		                          Default: ``None``, derived from the class name.
		"""
		identifier = getTypeName(self)[:-5] if packageIdentifier is None else packageIdentifier
		packageSymbol = PackageSymbol(SimpleName(identifier))
		super().__init__(packageSymbol)
