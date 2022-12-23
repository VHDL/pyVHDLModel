from pyVHDLModel.SyntaxModel import Package, PackageBody, Library


class Std(Library):
	def __init__(self):
		super().__init__(self.__class__.__name__)

		for packageType, packageBodyType in PACKAGES:
			package: Package = packageType()
			packageBody: PackageBody = packageBodyType()

			self._packages[package.Identifier.lower()] = package
			self._packageBodies[packageBody.Identifier.lower()] = packageBody


class Standard(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Standard_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class TextIO(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class TextIO_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


class Env(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


class Env_Body(PackageBody):
	def __init__(self):
		super().__init__(self.__class__.__name__[:-5])


PACKAGES = (
	(Standard, Standard_Body),
	(TextIO, TextIO_Body),
	(Env, Env_Body),
)
