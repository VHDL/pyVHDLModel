from pyTooling.Decorators import export

from pyVHDLModel import UseClause, LibraryClause
from pyVHDLModel.SyntaxModel import AllPackageMembersReferenceSymbol, PackageReferenceSymbol, LibraryReferenceSymbol
from pyVHDLModel.std import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody


@export
class Ieee(PredefinedLibrary):
	def __init__(self):
		super().__init__(PACKAGES)


@export
class Math_Real(PredefinedPackage):
	pass


class Math_Real_Body(PredefinedPackageBody):
	pass


class Math_Complex(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


class Math_Complex_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))


class Std_logic_1164(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))


class Std_logic_1164_Body(PredefinedPackageBody):
	pass


class std_logic_textio(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Numeric_Bit(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))


class Numeric_Bit_Body(PredefinedPackageBody):
	pass


class Numeric_Bit_Unsigned(PredefinedPackage):
	pass


class Numeric_Bit_Unsigned_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_bit.all", ))


class Numeric_Std(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Numeric_Std_Body(PredefinedPackageBody):
	pass


class Numeric_Std_Unsigned(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.std_logic_1164.all", ))


class Numeric_Std_Unsigned_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.numeric_std.all", ))


class Fixed_Float_Types(PredefinedPackage):
	pass


class Fixed_Generic_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))


class Fixed_Generic_Pkg_Body(PredefinedPackageBody):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.MATH_REAL.all", ))


class Fixed_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


class Float_Generic_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("STD.TEXTIO.all", ))
		self._AddLibraryClause(("IEEE", ))
		self._AddPackageClause(("IEEE.STD_LOGIC_1164.all", ))
		self._AddPackageClause(("IEEE.NUMERIC_STD.all", ))
		self._AddPackageClause(("IEEE.fixed_float_types.all", ))


class Float_Generic_Pkg_Body(PredefinedPackageBody):
	pass


class Float_Pkg(PredefinedPackage):
	def __init__(self):
		super().__init__()

		self._AddLibraryClause(("IEEE", ))


PACKAGES = (
	(Math_Real, Math_Real_Body),
	(Math_Complex, Math_Complex_Body),
	(Std_logic_1164, Std_logic_1164_Body),
	(std_logic_textio, None),
	(Numeric_Bit, Numeric_Bit_Body),
	(Numeric_Bit_Unsigned, Numeric_Bit_Unsigned_Body),
	(Numeric_Std, Numeric_Std_Body),
	(Numeric_Std_Unsigned, Numeric_Std_Unsigned_Body),
	(Fixed_Float_Types, None),
	(Fixed_Generic_Pkg, Fixed_Generic_Pkg_Body),
	(Fixed_Pkg, None),
	(Float_Generic_Pkg, Float_Generic_Pkg_Body),
	(Float_Pkg, None),
)
