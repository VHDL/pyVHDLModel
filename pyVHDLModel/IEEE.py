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
"""This module contains library and package declarations for VHDL library ``IEEE``."""

from typing                 import Optional as Nullable

from pyTooling.Decorators   import export, readonly

from pyVHDLModel            import IEEEFlavor
from pyVHDLModel.Exception  import VHDLModelException
from pyVHDLModel.Expression import CharacterEnumerationLiteral
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

	* Synopsys packages

	  * :class:`~pyVHDLModel.IEEE.Std_Logic_Arith`
	  * :class:`~pyVHDLModel.IEEE.Std_Logic_Misc`
	  * :class:`~pyVHDLModel.IEEE.Std_Logic_Signed`
	  * :class:`~pyVHDLModel.IEEE.Std_Logic_TextIO`
	  * :class:`~pyVHDLModel.IEEE.Std_Logic_Unsigned`

	* Mentor Graphics packages

	  * :class:`~pyVHDLModel.IEEE.Std_Logic_Arith`

	* VITAL packages

	  * :class:`~pyVHDLModel.IEEE.VITAL_Timing`
	  * :class:`~pyVHDLModel.IEEE.VITAL_Primitives`
	  * :class:`~pyVHDLModel.IEEE.VITAL_Memory`

	.. seealso::

	   Other predefined libraries:
	     * Library :class:`~pyVHDLModel.STD.Std`
	"""

	_flavor: IEEEFlavor  #: The flavor of the ``ieee`` library this instance provides.

	def __init__(self, flavor: Nullable[IEEEFlavor] = None) -> None:
		"""
		Initializes the ``ieee`` library.

		:param flavor:               The flavor of the ``ieee`` library this instance provides.
		:raises VHDLModelException: If the given IEEE library flavor is unknown.
		"""
		super().__init__(PACKAGES)

		self._flavor = IEEEFlavor.IEEE
		if flavor is None:
			return
		elif IEEEFlavor.IEEE in flavor:
			pass
		elif IEEEFlavor.Synopsys in flavor:
			self.LoadSynopsysPackages()
		elif IEEEFlavor.MentorGraphics in flavor:
			self.LoadMentorGraphicsPackages()
		else:
			raise VHDLModelException(f"Unknown IEEE library flavor '{flavor}'.")

		if IEEEFlavor.WithVITAL in flavor:
			self.LoadVITALPackages()

	@readonly
	def Flavor(self) -> IEEEFlavor:
		"""
		Read-only property to access the flavor (:attr:`_flavor`).

		:returns: The flavor.
		"""
		return self._flavor

	def LoadSynopsysPackages(self) -> None:
		if IEEEFlavor.IEEE not in self._flavor:
			raise VHDLModelException(f"IEEE library flavor is '{self._flavor}' and can't be changed to '{IEEEFlavor.Synopsys}'.")

		self._flavor = (self._flavor & ~IEEEFlavor.IEEE) | IEEEFlavor.Synopsys
		self.AddPackages(SYNOPSYS_PACKAGES)

	def LoadMentorGraphicsPackages(self) -> None:
		if IEEEFlavor.IEEE not in self._flavor:
			raise VHDLModelException(f"IEEE library flavor is '{self._flavor}' and can't be changed to '{IEEEFlavor.MentorGraphics}'.")

		self._flavor = (self._flavor & ~IEEEFlavor.IEEE) | IEEEFlavor.MentorGraphics
		self.AddPackages(MENTOR_GRAPHICS_PACKAGES)

	def LoadVITALPackages(self) -> None:
		self._flavor |= IEEEFlavor.WithVITAL
		self.AddPackages(VITAL_PACKAGES)


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
		"""
		Initializes the ``math_complex`` package.
		"""
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


@export
class Math_Complex_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.math_complex``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``math_complex`` package body.
		"""
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


@export
class Std_Logic_1164(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_1164``.

	Predefined types:

	* ``std_ulogic``, ``std_ulogic_vector``
	* ``std_logic``, ``std_logic_vector``
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_1164`` package.
		"""
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))

		stdULogic = EnumeratedType("std_ulogic", (
			CharacterEnumerationLiteral("U"),
			CharacterEnumerationLiteral("X"),
			CharacterEnumerationLiteral("0"),
			CharacterEnumerationLiteral("1"),
			CharacterEnumerationLiteral("Z"),
			CharacterEnumerationLiteral("W"),
			CharacterEnumerationLiteral("L"),
			CharacterEnumerationLiteral("H"),
			CharacterEnumerationLiteral("-"),
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
class Std_Logic_1164_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.std_logic_1164``.
	"""


@export
class Std_Logic_TextIO(PredefinedPackage):
	"""
	Predefined package ``ieee.std_logic_textio``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_textio`` package.
		"""
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Numeric_Bit(PredefinedPackage):
	"""
	Predefined package ``ieee.numeric_bit``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``numeric_bit`` package.
		"""
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
		"""
		Initializes the ``numeric_bit_unsigned`` package body.
		"""
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
		"""
		Initializes the ``numeric_std`` package.
		"""
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
		"""
		Initializes the ``numeric_std_unsigned`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Numeric_Std_Unsigned_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.numeric_std_unsigned``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``numeric_std_unsigned`` package body.
		"""
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
		"""
		Initializes the ``fixed_generic_pkg`` package.
		"""
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
		"""
		Initializes the ``fixed_generic_pkg`` package body.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.MATH_REAL.all", ))


@export
class Fixed_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.fixed_pkg``.
	"""
	def __init__(self) -> None:
		"""
		Initializes the ``fixed_pkg`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


@export
class Float_Generic_Pkg(PredefinedPackage):
	"""
	Predefined package ``ieee.float_generic_pkg``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``float_generic_pkg`` package.
		"""
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
		"""
		Initializes the ``float_pkg`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


PACKAGES = (
	(Math_Real,            Math_Real_Body),
	(Math_Complex,         Math_Complex_Body),
	(Std_Logic_1164,       Std_Logic_1164_Body),
	(Std_Logic_TextIO,     None),
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


@export
class Std_Logic_Arith_MentorGraphics(PredefinedPackage):
	"""
	Predefined Mentor Graphics package ``ieee.std_logic_arith``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_arith`` package.
		"""
		super().__init__("Std_Logic_Arith")

		self._AddLibraryClause(("IEEE", ))

		# used inside of package
		# self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_Logic_Arith_Body_MentorGraphics(PredefinedPackageBody):
	"""
	Predefined package body of Mentor Graphics package ``ieee.std_logic_arith``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_arith`` package body.
		"""
		super().__init__("Std_Logic_Arith")


MENTOR_GRAPHICS_PACKAGES = (
	(Std_Logic_Arith_MentorGraphics, Std_Logic_Arith_Body_MentorGraphics),
)


@export
class VITAL_Timing(PredefinedPackage):
	"""
	Predefined package ``ieee.VITAL_Timing``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``VITAL_Timing`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))


@export
class VITAL_Timing_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.VITAL_Timing``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``VITAL_Timing`` package body.
		"""
		super().__init__()

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))


@export
class VITAL_Primitives(PredefinedPackage):
	"""
	Predefined package ``ieee.VITAL_Primitives``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``VITAL_Primitives`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.VITAL_Timing.all", ))


@export
class VITAL_Primitives_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.VITAL_Primitives``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``VITAL_Primitives`` package body.
		"""
		super().__init__()

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))


@export
class VITAL_Memory(PredefinedPackage):
	"""
	Predefined package ``ieee.VITAL_Memory``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``VITAL_Memory`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.VITAL_Timing.all", ))
		self._AddPackageClause(("IEEE.VITAL_Primitives.all", ))

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))


@export
class VITAL_Memory_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.VITAL_Memory``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``VITAL_Memory`` package body.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.VITAL_Timing.all", ))
		self._AddPackageClause(("IEEE.VITAL_Primitives.all", ))

		self._AddLibraryClause(("STD", ))
		self._AddPackageClause(("STD.TEXTIO.all", ))


VITAL_PACKAGES = (
	(VITAL_Timing,     VITAL_Timing_Body),
	(VITAL_Primitives, VITAL_Primitives_Body),
	(VITAL_Memory,     VITAL_Memory_Body)
)


@export
class Std_Logic_Arith_Synopsys(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_arith``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_arith`` package.
		"""
		super().__init__("Std_Logic_Arith")

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_Logic_Misc(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_misc``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_misc`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_Logic_Misc_Body(PredefinedPackageBody):
	"""
	Predefined package body of Synopsys package ``ieee.std_logic_misc``.
	"""


@export
class Std_Logic_Signed(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_signed``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_signed`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))
		self._AddPackageClause(("IEEE.std_logic_arith.all", ))


@export
class Std_Logic_TextIO_Synopsys(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_textio``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_textio`` package.
		"""
		super().__init__("Std_Logic_TextIO")

		self._AddPackageClause(("STD.textio.all", ))

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


@export
class Std_Logic_Unsigned(PredefinedPackage):
	"""
	Predefined Synopsys package ``ieee.std_logic_unsigned``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``std_logic_unsigned`` package.
		"""
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))
		self._AddPackageClause(("IEEE.std_logic_arith.all", ))


SYNOPSYS_PACKAGES = (
	(Std_Logic_Arith_Synopsys,    None),
	(Std_Logic_Misc,     Std_Logic_Misc_Body),
	(Std_Logic_Signed,   None),
	(Std_Logic_TextIO_Synopsys,   None),
	(Std_Logic_Unsigned, None),
)
