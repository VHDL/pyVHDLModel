from pyTooling.Decorators import export

from pyVHDLModel.SyntaxModel import Package, PackageBody, Library, PackageSymbol


@export
class PredefinedLibrary(Library):
	def __init__(self, packages):
		super().__init__(self.__class__.__name__)

		for packageType, packageBodyType in packages:
			package: Package = packageType()
			packageBody: PackageBody = packageBodyType()

			package.Library = self
			packageBody.Library = self

			self._packages[package.NormalizedIdentifier] = package
			self._packageBodies[packageBody.NormalizedIdentifier] = packageBody


@export
class PredefinedPackage(Package):
	def __init__(self):
		super().__init__(self.__class__.__name__)


@export
class PredefinedPackageBody(PackageBody):
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
	pass


@export
class Env_Body(PredefinedPackageBody):
	pass


PACKAGES = (
	(Standard, Standard_Body),
	(TextIO, TextIO_Body),
	(Env, Env_Body),
)
