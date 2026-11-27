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
This package contains library and package declarations for VHDL library ``IEEE``.

Each predefined VHDL package of the library is declared in a module of its own, e.g. ``ieee.std_logic_1164`` in
:mod:`~pyVHDLModel.IEEE.StdLogic1164`.
"""
from typing                              import Optional as Nullable

from pyTooling.Decorators                import export, readonly

from pyVHDLModel                         import VHDLVersion, IEEEFlavor, Package, PackageBody
from pyVHDLModel.Exception               import UnknownIEEEFlavorError, IEEEFlavorChangeError
from pyVHDLModel.Predefined              import PredefinedLibrary
from pyVHDLModel.IEEE.MathReal           import Math_Real, Math_Real_Body
from pyVHDLModel.IEEE.MathComplex        import Math_Complex, Math_Complex_Body
from pyVHDLModel.IEEE.StdLogic1164       import Std_Logic_1164, Std_Logic_1164_Body
from pyVHDLModel.IEEE.StdLogicTextIO     import Std_Logic_TextIO, Std_Logic_TextIO_Synopsys
from pyVHDLModel.IEEE.NumericBit         import Numeric_Bit, Numeric_Bit_Body
from pyVHDLModel.IEEE.NumericBitUnsigned import Numeric_Bit_Unsigned, Numeric_Bit_Unsigned_Body
from pyVHDLModel.IEEE.NumericStd         import Numeric_Std, Numeric_Std_Body
from pyVHDLModel.IEEE.NumericStdUnsigned import Numeric_Std_Unsigned, Numeric_Std_Unsigned_Body
from pyVHDLModel.IEEE.FixedFloatTypes    import Fixed_Float_Types
from pyVHDLModel.IEEE.FixedGenericPkg    import Fixed_Generic_Pkg, Fixed_Generic_Pkg_Body
from pyVHDLModel.IEEE.FixedPkg           import Fixed_Pkg
from pyVHDLModel.IEEE.FloatGenericPkg    import Float_Generic_Pkg, Float_Generic_Pkg_Body
from pyVHDLModel.IEEE.FloatPkg           import Float_Pkg
from pyVHDLModel.IEEE.StdLogicArith      import Std_Logic_Arith_MentorGraphics, Std_Logic_Arith_Body_MentorGraphics, \
                                                Std_Logic_Arith_Synopsys
from pyVHDLModel.IEEE.VITALTiming        import VITAL_Timing, VITAL_Timing_Body
from pyVHDLModel.IEEE.VITALPrimitives    import VITAL_Primitives, VITAL_Primitives_Body
from pyVHDLModel.IEEE.VITALMemory        import VITAL_Memory, VITAL_Memory_Body
from pyVHDLModel.IEEE.StdLogicMisc       import Std_Logic_Misc, Std_Logic_Misc_Body
from pyVHDLModel.IEEE.StdLogicSigned     import Std_Logic_Signed
from pyVHDLModel.IEEE.StdLogicUnsigned   import Std_Logic_Unsigned
from pyVHDLModel.IEEE.IeeeStdContext     import Ieee_Std_Context
from pyVHDLModel.IEEE.IeeeBitContext     import Ieee_Bit_Context


@export
class Ieee(PredefinedLibrary):
	"""
	Predefined VHDL library ``ieee``.

	The following predefined packages are in this library:

	* Math

	  * :class:`~pyVHDLModel.IEEE.MathReal.Math_Real`
	  * :class:`~pyVHDLModel.IEEE.MathComplex.Math_Complex`

	* Std_logic

	  * :class:`~pyVHDLModel.IEEE.StdLogic1164.Std_Logic_1164`
	  * :class:`~pyVHDLModel.IEEE.StdLogicTextIO.Std_Logic_TextIO`

	* Numeric

	  * :class:`~pyVHDLModel.IEEE.NumericBit.Numeric_Bit`
	  * :class:`~pyVHDLModel.IEEE.NumericBitUnsigned.Numeric_Bit_Unsigned`
	  * :class:`~pyVHDLModel.IEEE.NumericStd.Numeric_Std`
	  * :class:`~pyVHDLModel.IEEE.NumericStdUnsigned.Numeric_Std_Unsigned`

	* Fixed/floating point

	  * :class:`~pyVHDLModel.IEEE.FixedFloatTypes.Fixed_Float_Types`
	  * :class:`~pyVHDLModel.IEEE.FixedGenericPkg.Fixed_Generic_Pkg`
	  * :class:`~pyVHDLModel.IEEE.FixedPkg.Fixed_Pkg`
	  * :class:`~pyVHDLModel.IEEE.FloatGenericPkg.Float_Generic_Pkg`
	  * :class:`~pyVHDLModel.IEEE.FloatPkg.Float_Pkg`

	* Contexts

	  * :class:`~pyVHDLModel.IEEE.IeeeStdContext.Ieee_Std_Context`
	  * :class:`~pyVHDLModel.IEEE.IeeeBitContext.Ieee_Bit_Context`

	* Synopsys packages

	  * :class:`~pyVHDLModel.IEEE.StdLogicArith.Std_Logic_Arith_Synopsys`
	  * :class:`~pyVHDLModel.IEEE.StdLogicMisc.Std_Logic_Misc`
	  * :class:`~pyVHDLModel.IEEE.StdLogicSigned.Std_Logic_Signed`
	  * :class:`~pyVHDLModel.IEEE.StdLogicTextIO.Std_Logic_TextIO`
	  * :class:`~pyVHDLModel.IEEE.StdLogicUnsigned.Std_Logic_Unsigned`

	* Mentor Graphics packages

	  * :class:`~pyVHDLModel.IEEE.StdLogicArith.Std_Logic_Arith_MentorGraphics`

	* VITAL packages

	  * :class:`~pyVHDLModel.IEEE.VITALTiming.VITAL_Timing`
	  * :class:`~pyVHDLModel.IEEE.VITALPrimitives.VITAL_Primitives`
	  * :class:`~pyVHDLModel.IEEE.VITALMemory.VITAL_Memory`

	.. seealso::

	   Other predefined libraries:
	     * Library :class:`~pyVHDLModel.STD.Std`
	"""

	_flavor: IEEEFlavor  #: The flavor of the ``ieee`` library this instance provides.

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008, flavor: Nullable[IEEEFlavor] = None) -> None:
		"""
		Initializes the ``ieee`` library.

		:param vhdlVersion:             Optional, the VHDL version of the library's packages.
		                                Default: ``VHDLVersion.VHDL2008``.
		:param flavor:                  Optional, the flavor of the ``ieee`` library this instance provides.
		                                Default: ``None``, the IEEE flavor.
		:raises ValueError:             If parameter 'vhdlVersion' is None.
		:raises TypeError:              If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError:             If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008).
		:raises UnknownIEEEFlavorError: If the given IEEE library flavor is unknown.
		"""
		super().__init__(PACKAGES, vhdlVersion)
		self.AddContexts(CONTEXTS)

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
			raise UnknownIEEEFlavorError(f"Unknown IEEE library flavor '{flavor}'.", flavor=flavor)

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
			raise IEEEFlavorChangeError(
				f"IEEE library flavor is '{self._flavor}' and can't be changed to '{IEEEFlavor.Synopsys}'.",
				currentFlavor=self._flavor,
				flavor=IEEEFlavor.Synopsys
			)

		self._flavor = (self._flavor & ~IEEEFlavor.IEEE) | IEEEFlavor.Synopsys
		self.AddPackages(SYNOPSYS_PACKAGES)

	def LoadMentorGraphicsPackages(self) -> None:
		if IEEEFlavor.IEEE not in self._flavor:
			raise IEEEFlavorChangeError(
				f"IEEE library flavor is '{self._flavor}' and can't be changed to '{IEEEFlavor.MentorGraphics}'.",
				currentFlavor=self._flavor,
				flavor=IEEEFlavor.MentorGraphics
			)

		self._flavor = (self._flavor & ~IEEEFlavor.IEEE) | IEEEFlavor.MentorGraphics
		self.AddPackages(MENTOR_GRAPHICS_PACKAGES)

	def LoadVITALPackages(self) -> tuple[Package | PackageBody, ...]:
		"""
		Add the VITAL packages (IEEE Std 1076.4) to this library.

		To add them to a design's ``ieee`` library and its virtual document, use
		:meth:`Design.LoadVITALPackages() <pyVHDLModel.Design.LoadVITALPackages>`.

		:returns:                      Tuple of the added packages and package bodies, each package followed by its body.
		:raises IEEEFlavorChangeError: If the library has the VITAL packages already.
		"""
		if IEEEFlavor.WithVITAL in self._flavor:
			raise IEEEFlavorChangeError(
				f"IEEE library flavor is '{self._flavor}' and has the VITAL packages already.",
				currentFlavor=self._flavor,
				flavor=IEEEFlavor.WithVITAL
			)

		self._flavor |= IEEEFlavor.WithVITAL
		return self.AddPackages(VITAL_PACKAGES)


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


CONTEXTS = (
	Ieee_Std_Context,
	Ieee_Bit_Context
)


MENTOR_GRAPHICS_PACKAGES = (
	(Std_Logic_Arith_MentorGraphics, Std_Logic_Arith_Body_MentorGraphics),
)


VITAL_PACKAGES = (
	(VITAL_Timing,     VITAL_Timing_Body),
	(VITAL_Primitives, VITAL_Primitives_Body),
	(VITAL_Memory,     VITAL_Memory_Body)
)


SYNOPSYS_PACKAGES = (
	(Std_Logic_Arith_Synopsys,    None),
	(Std_Logic_Misc,     Std_Logic_Misc_Body),
	(Std_Logic_Signed,   None),
	(Std_Logic_TextIO_Synopsys,   None),
	(Std_Logic_Unsigned, None),
)
