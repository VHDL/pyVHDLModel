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
from typing                    import Iterable, Optional as Nullable

from pyTooling.Common          import getFullyQualifiedName, getTypeName
from pyTooling.Decorators      import export, readonly
from pyTooling.MetaClasses     import ExtendedType, abstractclass

from pyVHDLModel               import VHDLVersion, Library, Package, PackageBody, AllPackageMembersReferenceSymbol, \
                                      PackageMemberReferenceSymbol
from pyVHDLModel.Base          import ModelEntity, NamedEntityMixin, Mode
from pyVHDLModel.Name          import SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol        import LibraryReferenceSymbol, PackageSymbol, PackageReferenceSymbol, \
                                      SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression    import Literal, IntegerLiteral
from pyVHDLModel.DesignUnit    import LibraryClause, UseClause
from pyVHDLModel.Interface     import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram    import Subprogram
from pyVHDLModel.Association   import GenericAssociationItem
from pyVHDLModel.Instantiation import PackageInstantiation


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

	_vhdlVersion: VHDLVersion  #: The VHDL version of the library's packages.

	def __init__(self, packages, vhdlVersion: VHDLVersion, documentation: Nullable[str] = None) -> None:
		"""
		Initializes a predefined library.

		:param packages:      Dictionary of all packages defined in a library.
		:param vhdlVersion:   The VHDL version of the library's packages.
		:param documentation: Optional, documentation of this library, if the caller has one to supply. VHDL defines none
		                      for a predefined library, so it is empty unless supplied from outside.
		                      Default: ``None``, no documentation.
		:raises ValueError:   If parameter 'vhdlVersion' is None.
		:raises TypeError:    If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError:   If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(getTypeName(self), documentation)

		if vhdlVersion is None:
			raise ValueError("Parameter 'vhdlVersion' is None.")
		elif not isinstance(vhdlVersion, VHDLVersion):
			ex = TypeError("Parameter 'vhdlVersion' is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(vhdlVersion)}'.")
			raise ex
		elif vhdlVersion is not VHDLVersion.VHDL2008:
			ex = ValueError("Parameter 'vhdlVersion' is not a supported VHDL version.")
			ex.add_note(f"Got value '{vhdlVersion}'.")
			ex.add_note("Supported VHDL versions: VHDL2008")
			raise ex

		self._vhdlVersion = vhdlVersion

		self.AddPackages(packages)

	@readonly
	def VHDLVersion(self) -> VHDLVersion:
		"""
		Read-only property to access the VHDL version of the library's packages (:attr:`_vhdlVersion`).

		:returns: The VHDL version.
		"""
		return self._vhdlVersion

	@readonly
	def IsPredefined(self) -> bool:
		"""
		Check if the library is a predefined library built by pyVHDLModel.

		:returns: ``True``
		"""
		return True

	def AddPackages(self, packages) -> None:
		for packageType, packageBodyType in packages:
			package: Package = packageType(self._vhdlVersion)
			package.Library = self
			self._packages[package.NormalizedIdentifier] = package

			if packageBodyType is not None:
				packageBody: PackageBody = packageBodyType(self._vhdlVersion)
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

	_vhdlVersion: VHDLVersion  #: The VHDL version of the declarations.

	def __init__(self, vhdlVersion: VHDLVersion) -> None:
		"""
		Initializes the VHDL version of a predefined package or package body.

		:param vhdlVersion: The VHDL version of the declarations.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		if vhdlVersion is None:
			raise ValueError("Parameter 'vhdlVersion' is None.")
		elif not isinstance(vhdlVersion, VHDLVersion):
			ex = TypeError("Parameter 'vhdlVersion' is not of type 'VHDLVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(vhdlVersion)}'.")
			raise ex
		elif vhdlVersion is not VHDLVersion.VHDL2008:
			ex = ValueError("Parameter 'vhdlVersion' is not a supported VHDL version.")
			ex.add_note(f"Got value '{vhdlVersion}'.")
			ex.add_note("Supported VHDL versions: VHDL2008")
			raise ex

		self._vhdlVersion = vhdlVersion

	@readonly
	def VHDLVersion(self) -> VHDLVersion:
		"""
		Read-only property to access the VHDL version of the declarations (:attr:`_vhdlVersion`).

		:returns: The VHDL version.
		"""
		return self._vhdlVersion

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

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008, identifier: Nullable[str] = None) -> None:
		"""
		Initializes a predefined package.

		By default the VHDL package name is the Python class name. Pass ``identifier`` when the two must
		differ - e.g. when two vendor flavors of the same VHDL package need distinct Python classes.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:param identifier:  Optional, the VHDL package name. Default: ``None``, the class name.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(getTypeName(self) if identifier is None else identifier)
		PredefinedPackageMixin.__init__(self, vhdlVersion)

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
		if (overloads := table.get(subprogram._normalizedIdentifier)) is None:
			table[subprogram._normalizedIdentifier] = [subprogram]
		else:
			overloads.append(subprogram)

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
		defaultExpression: Nullable[Literal | SimpleObjectOrFunctionCallSymbol] = None
	) -> ParameterConstantInterfaceItem:
		"""
		Create a constant parameter of mode ``in`` of a subprogram of a predefined package.

		:param identifiers:       The parameter's identifiers.
		:param subtype:           The parameter's type mark.
		:param defaultExpression: Optional, the default value: a literal or a name, e.g. of an enumeration literal.
		                          Default: ``None``, no default value.
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

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008, packageIdentifier: Nullable[str] = None) -> None:
		"""
		Initializes a predefined package body.

		By default the VHDL package name is the Python class name with the trailing ``_Body`` removed.
		Pass ``packageIdentifier`` when the two must differ.

		:param vhdlVersion:       Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:param packageIdentifier: Optional, the VHDL name of the package this body implements.
		                          Default: ``None``, derived from the class name.
		:raises ValueError:       If parameter 'vhdlVersion' is None.
		:raises TypeError:        If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError:       If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		identifier = getTypeName(self)[:-5] if packageIdentifier is None else packageIdentifier
		packageSymbol = PackageSymbol(SimpleName(identifier))
		super().__init__(packageSymbol)
		PredefinedPackageMixin.__init__(self, vhdlVersion)


@export
@abstractclass
class PredefinedPackageInstantiation(PackageInstantiation, PredefinedPackageMixin):
	"""
	A base-class for predefined VHDL package instantiations.

	An example is ``ieee.fixed_pkg``, an instantiation of ``ieee.fixed_generic_pkg``.
	"""

	def __init__(
		self,
		vhdlVersion:             VHDLVersion,
		genericPackage:          PackageReferenceSymbol,
		genericAssociationItems: Iterable[GenericAssociationItem]
	) -> None:
		"""
		Initializes a predefined package instantiation.

		The VHDL package name is the Python class name.

		:param vhdlVersion:             The VHDL version of the declarations.
		:param genericPackage:          Reference to the instantiated generic package.
		:param genericAssociationItems: The generic associations of the generic map aspect.
		:raises ValueError:             If parameter 'vhdlVersion' is None.
		:raises TypeError:              If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError:             If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		"""
		super().__init__(getTypeName(self), genericPackage, genericAssociationItems=genericAssociationItems)
		PredefinedPackageMixin.__init__(self, vhdlVersion)
