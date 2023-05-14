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
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
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
"""This module contains library and package declarations for VHDL library ``STD``."""
from typing                  import Iterable

from pyTooling.Decorators    import export

from pyVHDLModel             import Library
from pyVHDLModel.Base        import Range, Direction
from pyVHDLModel.Expression  import EnumerationLiteral, IntegerLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Name        import SimpleName, SelectedName, AllName
from pyVHDLModel.Symbol import LibraryReferenceSymbol, PackageMemberReferenceSymbol, AllPackageMembersReferenceSymbol, PackageSymbol, SimpleSubtypeSymbol
from pyVHDLModel.DesignUnit  import LibraryClause, UseClause, Package, PackageBody
from pyVHDLModel.Type import EnumeratedType, IntegerType, Subtype, PhysicalType, ArrayType


@export
class PredefinedLibrary(Library):
	def __init__(self, packages):
		super().__init__(self.__class__.__name__)

		self.AddPackages(packages)

	def AddPackages(self, packages):
		for packageType, packageBodyType in packages:
			package: Package = packageType()
			package.Library = self
			self._packages[package.NormalizedIdentifier] = package

			if packageBodyType is not None:
				packageBody: PackageBody = packageBodyType()
				packageBody.Library = self
				self._packageBodies[packageBody.NormalizedIdentifier] = packageBody


@export
class PredefinedMixin:
	def _AddLibraryClause(self, libraries: Iterable[str]):
		symbols = [LibraryReferenceSymbol(SimpleName(libName)) for libName in libraries]
		libraryClause = LibraryClause(symbols)

		self._contextItems.append(libraryClause)
		self._libraryReferences.append(libraryClause)

	def _AddPackageClause(self, packages: Iterable[str]):
		symbols = []
		for qualifiedPackageName in packages:
			libName, packName, members = qualifiedPackageName.split(".")

			packageName = SelectedName(packName, SimpleName(libName))
			if members.lower() == "all":
				symbols.append(AllPackageMembersReferenceSymbol(AllName(packageName)))
			else:
				symbols.append(PackageMemberReferenceSymbol(SelectedName(members, packageName)))

		useClause = UseClause(symbols)
		self._contextItems.append(useClause)
		self._packageReferences.append(useClause)


@export
class PredefinedPackage(Package, PredefinedMixin):
	def __init__(self):
		super().__init__(self.__class__.__name__)


@export
class PredefinedPackageBody(PackageBody, PredefinedMixin):
	def __init__(self):
		packageSymbol = PackageSymbol(SimpleName(self.__class__.__name__[:-5]))
		super().__init__(packageSymbol)


@export
class Std(PredefinedLibrary):
	def __init__(self):
		super().__init__(PACKAGES)


@export
class Standard(PredefinedPackage):
	def __init__(self):
		super().__init__()

		boolean = EnumeratedType("boolean", (EnumerationLiteral("false"), EnumerationLiteral("true")))
		self._types[boolean.NormalizedIdentifier] = boolean

		bit = EnumeratedType("bit", (EnumerationLiteral("'0'"), EnumerationLiteral("'1'")))
		self._types[bit.NormalizedIdentifier] = bit

		chars = \
			"nul", "soh", "stx", "etx", "eot", "enq", "ack", "bel", "bs", "ht", "lf", "vt", "ff", "cr", "so", "si", "dle", "dc1", "dc2", "dc3",\
			"dc4", "nak", "syn", "etb", "can", "em", "sub", "esc", "fsp", "gsp", "rsp", "usp", "' '", "'!'", "'\"'", "'#'", "'$'", "'%'", "'&'", "'''",\
			"'('", "')'", "'*'", "'+'", "','", "'-'", "'.'", "'/'", "'0'", "'1'", "'2'", "'3'", "'4'", "'5'", "'6'", "'7'", "'8'", "'9'", "':'", "';'",\
			"'<'", "'='", "'>'", "'?'", "'@'", "'A'", "'B'", "'C'", "'D'", "'E'", "'F'", "'G'", "'H'", "'I'", "'J'", "'K'", "'L'", "'M'", "'N'", "'O'",\
			"'P'", "'Q'", "'R'", "'S'", "'T'", "'U'", "'V'", "'W'", "'X'", "'Y'", "'Z'", "'['", "'\'", "']'", "'^'", "'_'", "'`'", "'a'", "'b'", "'c'",\
			"'d'", "'e'", "'f'", "'g'", "'h'", "'i'", "'j'", "'k'", "'l'", "'m'", "'n'", "'o'", "'p'", "'q'", "'r'", "'s'", "'t'", "'u'", "'v'", "'w'",\
			"'x'", "'y'", "'z'", "'{'", "'|'", "'}'", "'~'", "del", "c128", "c129", "c130", "c131", "c132", "c133", "c134", "c135", "c136", "c137", "c138", "c139",\
			"c140", "c141", "c142", "c143", "c144", "c145", "c146", "c147", "c148", "c149", "c150", "c151", "c152", "c153", "c154", "c155", "c156", "c157", "c158", "c159",\
			"' '", "'¡'", "'¢'", "'£'", "'¤'", "'¥'", "'¦'", "'§'", "'¨'", "'©'", "'ª'", "'«'", "'¬'", "'­'", "'®'", "'¯'", "'°'", "'±'", "'²'", "'³'",\
			"'´'", "'µ'", "'¶'", "'·'", "'¸'", "'¹'", "'º'", "'»'", "'¼'", "'½'", "'¾'", "'¿'", "'À'", "'Á'", "'Â'", "'Ã'", "'Ä'", "'Å'", "'Æ'", "'Ç'",\
			"'È'", "'É'", "'Ê'", "'Ë'", "'Ì'", "'Í'", "'Î'", "'Ï'", "'Ð'", "'Ñ'", "'Ò'", "'Ó'", "'Ô'", "'Õ'", "'Ö'", "'×'", "'Ø'", "'Ù'", "'Ú'", "'Û'",\
			"'Ü'", "'Ý'", "'Þ'", "'ß'", "'à'", "'á'", "'â'", "'ã'", "'ä'", "'å'", "'æ'", "'ç'", "'è'", "'é'", "'ê'", "'ë'", "'ì'", "'í'", "'î'", "'ï'",\
			"'ð'", "'ñ'", "'ò'", "'ó'", "'ô'", "'õ'", "'ö'", "'÷'", "'ø'", "'ù'", "'ú'", "'û'", "'ü'", "'ý'", "'þ'", "'ÿ'"
		character = EnumeratedType("character", [EnumerationLiteral(char) for char in chars])
		self._types[character.NormalizedIdentifier] = character

		levels = "note", "warning", "error", "failure"
		severityLevel = EnumeratedType("severityLevel", [EnumerationLiteral(level) for level in levels])
		self._types[severityLevel.NormalizedIdentifier] = severityLevel

		integer = IntegerType("integer", Range(IntegerLiteral(-2**31), IntegerLiteral(2**31-1), Direction.To))
		self._types[integer.NormalizedIdentifier] = integer

		# real

		time = PhysicalType(
			"time",
			Range(IntegerLiteral(-2**63), IntegerLiteral(2**63-1), Direction.To),
			primaryUnit="fs",
			units=(
				("ps",  PhysicalIntegerLiteral(1000, "fs")),
				("ns",  PhysicalIntegerLiteral(1000, "ps")),
				("us",  PhysicalIntegerLiteral(1000, "ns")),
				("ms",  PhysicalIntegerLiteral(1000, "us")),
				("sec", PhysicalIntegerLiteral(1000, "ms")),
				("min", PhysicalIntegerLiteral(60, "sec")),
				("hr",  PhysicalIntegerLiteral(60, "min")),
			)
		)
		self._types[time.NormalizedIdentifier] = time

		# delay_length

		# now

		natural = Subtype("natural")
		natural._baseType = integer
		natural._range = Range(IntegerLiteral(0), IntegerLiteral(2**31-1), Direction.To)
		self._subtypes[natural.NormalizedIdentifier] = natural

		positive = Subtype("positive")
		positive._baseType = integer
		positive._range = Range(IntegerLiteral(1), IntegerLiteral(2**31-1), Direction.To)
		self._subtypes[positive.NormalizedIdentifier] = positive

		string = ArrayType("string", (SimpleSubtypeSymbol(SimpleName("positive")), ), SimpleSubtypeSymbol(SimpleName("character")))
		self._types[string.NormalizedIdentifier] = string

		booleanVector = ArrayType("boolean_vector", (SimpleSubtypeSymbol(SimpleName("natural")), ), SimpleSubtypeSymbol(SimpleName("boolean")))
		self._types[booleanVector.NormalizedIdentifier] = booleanVector

		bitVector = ArrayType("bit_vector", (SimpleSubtypeSymbol(SimpleName("natural")), ), SimpleSubtypeSymbol(SimpleName("bit")))
		self._types[bitVector.NormalizedIdentifier] = bitVector

		integerVector = ArrayType("integer_vector", (SimpleSubtypeSymbol(SimpleName("natural")), ), SimpleSubtypeSymbol(SimpleName("integer")))
		self._types[integerVector.NormalizedIdentifier] = integerVector

		# real_vector

		timeVector = ArrayType("time_vector", (SimpleSubtypeSymbol(SimpleName("natural")), ), SimpleSubtypeSymbol(SimpleName("time")))
		self._types[timeVector.NormalizedIdentifier] = timeVector

		fileOpenKinds = "read_mode", "write_mode", "append_mode"
		openFileKind = EnumeratedType("open_file_kind", [EnumerationLiteral(kind) for kind in fileOpenKinds])
		self._types[openFileKind.NormalizedIdentifier] = openFileKind

		fileOpenStati = "open_ok", "status_error", "name_error", "mode_error"
		fileOpenStatus = EnumeratedType("open_file_status", [EnumerationLiteral(status) for status in fileOpenStati])
		self._types[fileOpenStatus.NormalizedIdentifier] = fileOpenStatus

		# attribute foreign


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
	def __init__(self):
		super().__init__()

		self._AddPackageClause(("work.textio.all",))


@export
class Env_Body(PredefinedPackageBody):
	pass


PACKAGES = (
	(Standard, Standard_Body),
	(TextIO, TextIO_Body),
	(Env, Env_Body),
)
