from pyVHDLModel.SyntaxModel import Library, Package, PackageBody


class Ieee(Library):
	def __init__(self):
		super().__init__(self.__class__.__name__)

		for packageType, packageBodyType in PACKAGES:
			package: Package = packageType()
			packageBody: PackageBody = packageBodyType()

			self._packages[package.Identifier.lower()] = package
			self._packageBodies[packageBody.Identifier.lower()] = packageBody


class Math_Real(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Math_Real_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Math_Complex(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Math_Complex_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Std_logic_1164(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Std_logic_1164_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Numeric_Bit(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Numeric_Bit_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Numeric_Bit_Unsigned(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Numeric_Bit_Unsigned_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Numeric_Std(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Numeric_Std_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Numeric_Std_Unsigned(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Numeric_Std_Unsigned_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


PACKAGES = (
	(Math_Real, Math_Real_Body),
	(Math_Complex, Math_Complex_Body),
	(Std_logic_1164, Std_logic_1164_Body),
	(Numeric_Bit, Numeric_Bit_Body),
	(Numeric_Bit_Unsigned, Numeric_Bit_Unsigned_Body),
	(Numeric_Std, Numeric_Std_Body),
	(Numeric_Std_Unsigned, Numeric_Std_Unsigned_Body),
)
