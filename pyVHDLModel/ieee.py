from pyTooling.Decorators import export

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
	pass


class Math_Complex_Body(PredefinedPackageBody):
	pass


class Std_logic_1164(PredefinedPackage):
	pass


class Std_logic_1164_Body(PredefinedPackageBody):
	pass


class Numeric_Bit(PredefinedPackage):
	pass


class Numeric_Bit_Body(PredefinedPackageBody):
	pass


class Numeric_Bit_Unsigned(PredefinedPackage):
	pass


class Numeric_Bit_Unsigned_Body(PredefinedPackageBody):
	pass


class Numeric_Std(PredefinedPackage):
	pass


class Numeric_Std_Body(PredefinedPackageBody):
	pass


class Numeric_Std_Unsigned(PredefinedPackage):
	pass


class Numeric_Std_Unsigned_Body(PredefinedPackageBody):
	pass


PACKAGES = (
	(Math_Real, Math_Real_Body),
	(Math_Complex, Math_Complex_Body),
	(Std_logic_1164, Std_logic_1164_Body),
	(Numeric_Bit, Numeric_Bit_Body),
	(Numeric_Bit_Unsigned, Numeric_Bit_Unsigned_Body),
	(Numeric_Std, Numeric_Std_Body),
	(Numeric_Std_Unsigned, Numeric_Std_Unsigned_Body),
)
