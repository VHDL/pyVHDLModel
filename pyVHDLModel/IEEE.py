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
"""This module contains library and package declarations for VHDL library ``IEEE``."""
from pyTooling.Decorators   import export

from pyVHDLModel.Expression import EnumerationLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Predefined import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Type       import EnumeratedType, ArrayType, Subtype


@export
class Ieee(PredefinedLibrary):
	"""
	Predefined VHDL library ``ieee``.

	The following predefined packages are in this library:

	* Math

	  * :class:`~pyVHDLModel.IEEE.Math_Real`
	  * :class:`~pyVHDLModel.IEEE.Math_Complex`

	* Std_logic

	  * :class:`~pyVHDLModel.IEEE.Std_Logic_1164`
	  * :class:`~pyVHDLModel.IEEE.Std_Logic_TextIO`
	  * :class:`~pyVHDLModel.IEEE.Std_Logic_Misc`

	* Numeric

	  * :class:`~pyVHDLModel.IEEE.Numeric_Bit`
	  * :class:`~pyVHDLModel.IEEE.Numeric_Bit_Unsigned`
	  * :class:`~pyVHDLModel.IEEE.Numeric_Std`
	  * :class:`~pyVHDLModel.IEEE.Numeric_Std_Unsigned`

	* Fixed/floating point

	  * :class:`~pyVHDLModel.IEEE.Fixed_Float_Types`
	  * :class:`~pyVHDLModel.IEEE.Fixed_Generic_Pkg`
	  * :class:`~pyVHDLModel.IEEE.Fixed_Pkg`
	  * :class:`~pyVHDLModel.IEEE.Float_Generic_Pkg`
	  * :class:`~pyVHDLModel.IEEE.Float_Pkg`

	.. seealso::

	   Other predefined libraries:
	     * Library :class:`~pyVHDLModel.STD.Std`
	"""

	def __init__(self) -> None:
		super().__init__(PACKAGES)

	def LoadSynopsysPackages(self) -> None:
		self.AddPackages(PACKAGES_SYNOPSYS)



@export
class Math_Real(PredefinedPackage):
	"""
	Predefined package ``ieee.math_real``.
	"""


@export
class Math_Real_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.math_real``.
	"""


@export
class Math_Complex(PredefinedPackage):
	"""
	Predefined package ``ieee.math_complex``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


@export
class Math_Complex_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.math_complex``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


@export
class Std_logic_1164(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_1164``.

	Predefined types:

	* ``std_ulogic``, ``std_ulogic_vector``
	* ``std_logic``, ``std_logic_vector``
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))

		stdULogic = EnumeratedType("std_ulogic", (
			EnumerationLiteral("U"),
			EnumerationLiteral("X"),
			EnumerationLiteral("0"),
			EnumerationLiteral("1"),
			EnumerationLiteral("Z"),
			EnumerationLiteral("W"),
			EnumerationLiteral("L"),
			EnumerationLiteral("H"),
			EnumerationLiteral("-"),
		), None)
		self._types[stdULogic._normalizedIdentifier] = stdULogic
		self._declaredItems.append(stdULogic)

		stdULogicVector = ArrayType("std_ulogic_vector", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		self._types[stdULogicVector._normalizedIdentifier] = stdULogicVector
		self._declaredItems.append(stdULogicVector)

		stdLogic = Subtype("std_logic", SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		stdLogic._baseType = stdULogic
		self._subtypes[stdLogic._normalizedIdentifier] = stdLogic
		self._declaredItems.append(stdLogic)

		stdLogicVector = Subtype("std_logic_vector", SimpleSubtypeSymbol(SimpleName("std_ulogic_vector")), None)
		stdLogicVector._baseType = stdULogicVector
		self._subtypes[stdLogicVector._normalizedIdentifier] = stdLogicVector
		self._declaredItems.append(stdLogicVector)


@export
class Std_logic_1164_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.std_logic_1164``.
	"""


@export
class std_logic_textio(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_textio``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_logic_misc(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_misc``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_logic_misc_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.std_logic_misc``.
	"""


@export
class Numeric_Bit(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_bit``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))


@export
class Numeric_Bit_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_bit``.
	"""


@export
class Numeric_Bit_Unsigned(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_bit_unsigned``.
	"""


@export
class Numeric_Bit_Unsigned_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_bit_unsigned``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_bit.all", ))


@export
class Numeric_Std(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_std``.

	Predefined types:

	* ``unresolved_unsigned``, ``unsigned``
	* ``unresolved_signed``, ``signed``
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))

		unresolvedUnsigned = ArrayType("unresolved_unsigned", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		self._types[unresolvedUnsigned._normalizedIdentifier] = unresolvedUnsigned
		self._declaredItems.append(unresolvedUnsigned)

		unsigned = Subtype("unsigned", SimpleSubtypeSymbol(SimpleName("unresolved_unsigned")), None)
		unsigned._baseType = unresolvedUnsigned
		self._subtypes[unsigned._normalizedIdentifier] = unsigned
		self._declaredItems.append(unsigned)

		unresolvedSigned = ArrayType("unresolved_signed", (SimpleSubtypeSymbol(SimpleName("natural")),), SimpleSubtypeSymbol(SimpleName("std_ulogic")), None)
		self._types[unresolvedSigned._normalizedIdentifier] = unresolvedSigned
		self._declaredItems.append(unresolvedSigned)

		signed = Subtype("signed", SimpleSubtypeSymbol(SimpleName("unresolved_signed")), None)
		signed._baseType = unresolvedSigned
		self._subtypes[signed._normalizedIdentifier] = signed
		self._declaredItems.append(signed)


@export
class Numeric_Std_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_std``.
	"""


@export
class Numeric_Std_Unsigned(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_std_unsigned``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Numeric_Std_Unsigned_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_std_unsigned``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_std.all", ))


@export
class Fixed_Float_Types(PredefinedPackage):
	"""
	Predefined package ``ieee.fixed_float_types``.
	"""


@export
class Fixed_Generic_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.fixed_generic_pkg``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))


@export
class Fixed_Generic_Pkg_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.fixed_generic_pkg``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.MATH_REAL.all", ))


@export
class Fixed_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.fixed_pkg``.
	"""
	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


@export
class Float_Generic_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.float_generic_pkg``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))


@export
class Float_Generic_Pkg_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.float_generic_pkg``.
	"""


@export
class Float_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.float_pkg``.
	"""

	def __init__(self) -> None:
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


PACKAGES = (
	(Math_Real,            Math_Real_Body),
	(Math_Complex,         Math_Complex_Body),
	(Std_logic_1164,       Std_logic_1164_Body),
	(std_logic_textio,     None),
	(Numeric_Bit,          Numeric_Bit_Body),
	(Numeric_Bit_Unsigned, Numeric_Bit_Unsigned_Body),
	(Numeric_Std,          Numeric_Std_Body),
	(Numeric_Std_Unsigned, Numeric_Std_Unsigned_Body),
	(Fixed_Float_Types,    None),
	(Fixed_Generic_Pkg,    Fixed_Generic_Pkg_Body),
	(Fixed_Pkg,            None),
	(Float_Generic_Pkg,    Float_Generic_Pkg_Body),
	(Float_Pkg,            None),
)

PACKAGES_SYNOPSYS = (
	(Std_logic_misc,       Std_logic_misc_Body),
)
