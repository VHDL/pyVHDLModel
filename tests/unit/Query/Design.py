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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Tests for design-unit lookup by name across the libraries of a design."""
from pathlib                   import Path

from pyTooling.Testing         import Testcase

from pyVHDLModel               import Design, Document, VHDLModelException
from pyVHDLModel.Configuration import BlockConfiguration
from pyVHDLModel.DesignUnit    import Configuration, Context, Entity, Package
from pyVHDLModel.Exception     import LibraryNotFoundError, DesignUnitNotFoundError, AmbiguousDesignUnitError
from pyVHDLModel.Exception     import EntityNotFoundError, PackageNotFoundError, ConfigurationNotFoundError
from pyVHDLModel.Exception     import ContextNotFoundError, AmbiguousEntityError, AmbiguousPackageError
from pyVHDLModel.Name          import SimpleName
from pyVHDLModel.Symbol        import EntitySymbol, PossibleReference, Symbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _design() -> Design:
	"""
	A design with two libraries.

	``lib_A`` holds entity ``Counter``, package ``Utilities``, configuration ``cfg`` and context ``ctx``. ``lib_B``
	holds entities ``Counter`` and ``Adder``.
	"""
	design = Design("example")

	documentA = Document(Path("a.vhdl"))
	documentA._AddDesignUnit(Entity("Counter"))
	documentA._AddDesignUnit(Package("Utilities"))
	documentA._AddDesignUnit(Configuration(
		"cfg",
		EntitySymbol(SimpleName("Counter")),
		BlockConfiguration(Symbol(SimpleName("rtl"), PossibleReference.Architecture | PossibleReference.Label))
	))
	documentA._AddDesignUnit(Context("ctx"))
	design.AddDocument(documentA, design.GetLibrary("lib_A"))

	documentB = Document(Path("b.vhdl"))
	documentB._AddDesignUnit(Entity("Counter"))
	documentB._AddDesignUnit(Entity("Adder"))
	design.AddDocument(documentB, design.GetLibrary("lib_B"))

	return design


class EntityLookup(Testcase):
	def test_InLibrary(self) -> None:
		design = _design()

		entity = design.GetEntity("Counter", "lib_A")

		self.assertIsInstance(entity, Entity)
		self.assertIs(design.Libraries["lib_a"].Entities["counter"], entity)

	def test_InLibrary_CaseInsensitive(self) -> None:
		design = _design()

		entity = design.GetEntity("COUNTER", "LIB_b")

		self.assertIs(design.Libraries["lib_b"].Entities["counter"], entity)

	def test_AllLibraries(self) -> None:
		"""Without a library, the only library containing the entity is used."""
		design = _design()

		entity = design.GetEntity("adder")

		self.assertIs(design.Libraries["lib_b"].Entities["adder"], entity)

	def test_AllLibraries_Ambiguous(self) -> None:
		design = _design()

		with self.assertRaises(AmbiguousEntityError) as context:
			design.GetEntity("Counter")

		self.assertEqual("Entity 'Counter' found in several libraries: lib_A, lib_B.", str(context.exception))
		self.assertListEqual(["Pass parameter 'libraryName' to select a library."], context.exception.__notes__)
		self.assertIsInstance(context.exception, VHDLModelException)
		self.assertIsInstance(context.exception, AmbiguousDesignUnitError)
		self.assertEqual("Counter", context.exception.DesignUnitName)
		self.assertTupleEqual((design.Libraries["lib_a"], design.Libraries["lib_b"]), context.exception.Libraries)

	def test_NotFound_InLibrary(self) -> None:
		design = _design()

		with self.assertRaises(EntityNotFoundError) as context:
			design.GetEntity("Adder", "lib_A")

		self.assertEqual("Entity 'Adder' not found in library 'lib_A'.", str(context.exception))
		self.assertIsInstance(context.exception, VHDLModelException)
		self.assertIsInstance(context.exception, DesignUnitNotFoundError)
		self.assertEqual("Adder", context.exception.DesignUnitName)
		self.assertEqual("lib_A", context.exception.LibraryName)

	def test_NotFound_AllLibraries(self) -> None:
		design = _design()

		with self.assertRaises(EntityNotFoundError) as context:
			design.GetEntity("Multiplier")

		self.assertEqual("Entity 'Multiplier' not found in design.", str(context.exception))
		self.assertIsNone(context.exception.LibraryName)

	def test_NotFound_OtherKind(self) -> None:
		"""A package isn't returned as an entity."""
		design = _design()

		with self.assertRaises(EntityNotFoundError):
			design.GetEntity("Utilities")

	def test_LibraryNotFound(self) -> None:
		"""A lookup in a missing library creates no library."""
		design = _design()

		with self.assertRaises(LibraryNotFoundError) as context:
			design.GetEntity("Counter", "lib_C")

		self.assertEqual("Library 'lib_C' not found in design.", str(context.exception))
		self.assertEqual("lib_C", context.exception.LibraryName)
		self.assertListEqual(["lib_a", "lib_b"], list(design.Libraries.keys()))


class PackageLookup(Testcase):
	def test_AllLibraries(self) -> None:
		design = _design()

		package = design.GetPackage("utilities")

		self.assertIsInstance(package, Package)
		self.assertIs(design.Libraries["lib_a"].Packages["utilities"], package)

	def test_AllLibraries_Ambiguous(self) -> None:
		design = _design()
		document = Document(Path("c.vhdl"))
		document._AddDesignUnit(Package("Utilities"))
		design.AddDocument(document, design.Libraries["lib_b"])

		with self.assertRaises(AmbiguousPackageError) as context:
			design.GetPackage("utilities")

		self.assertEqual("Package 'utilities' found in several libraries: lib_A, lib_B.", str(context.exception))
		self.assertIsInstance(context.exception, AmbiguousDesignUnitError)

	def test_PredefinedLibrary(self) -> None:
		design = _design()
		design.LoadIEEELibrary()

		package = design.GetPackage("numeric_std")

		self.assertIs(design.Libraries["ieee"].Packages["numeric_std"], package)

	def test_NotFound_InLibrary(self) -> None:
		design = _design()

		with self.assertRaises(PackageNotFoundError) as context:
			design.GetPackage("Utilities", "lib_B")

		self.assertEqual("Package 'Utilities' not found in library 'lib_B'.", str(context.exception))
		self.assertEqual("lib_B", context.exception.LibraryName)


class ConfigurationLookup(Testcase):
	def test_InLibrary(self) -> None:
		design = _design()

		configuration = design.GetConfiguration("CFG", "lib_a")

		self.assertIsInstance(configuration, Configuration)
		self.assertIs(design.Libraries["lib_a"].Configurations["cfg"], configuration)

	def test_NotFound_AllLibraries(self) -> None:
		design = _design()

		with self.assertRaises(ConfigurationNotFoundError) as context:
			design.GetConfiguration("Counter")

		self.assertEqual("Configuration 'Counter' not found in design.", str(context.exception))
		self.assertIsNone(context.exception.LibraryName)


class ContextLookup(Testcase):
	def test_AllLibraries(self) -> None:
		design = _design()

		context = design.GetContext("ctx")

		self.assertIsInstance(context, Context)
		self.assertIs(design.Libraries["lib_a"].Contexts["ctx"], context)

	def test_LibraryNotFound(self) -> None:
		design = _design()

		with self.assertRaises(LibraryNotFoundError):
			design.GetContext("ctx", "lib_C")

	def test_NotFound_InLibrary(self) -> None:
		design = _design()

		with self.assertRaises(ContextNotFoundError) as context:
			design.GetContext("ctx", "lib_B")

		self.assertEqual("Context 'ctx' not found in library 'lib_B'.", str(context.exception))


class LookupParameters(Testcase):
	def test_Name_None(self) -> None:
		design = _design()

		with self.assertRaises(ValueError) as context:
			design.GetEntity(None)

		self.assertEqual("Parameter 'entityName' is None.", str(context.exception))

	def test_Name_Type(self) -> None:
		design = _design()

		with self.assertRaises(TypeError) as context:
			design.GetPackage(1)

		self.assertEqual("Parameter 'packageName' is not of type 'str'.", str(context.exception))

	def test_Name_Empty(self) -> None:
		design = _design()

		with self.assertRaises(ValueError) as context:
			design.GetConfiguration("")

		self.assertEqual("Parameter 'configurationName' is empty.", str(context.exception))

	def test_LibraryName_Type(self) -> None:
		design = _design()

		with self.assertRaises(TypeError) as context:
			design.GetContext("ctx", design.Libraries["lib_a"])

		self.assertEqual("Parameter 'libraryName' is not of type 'str'.", str(context.exception))

	def test_LibraryName_Empty(self) -> None:
		design = _design()

		with self.assertRaises(ValueError) as context:
			design.GetEntity("Counter", "")

		self.assertEqual("Parameter 'libraryName' is empty.", str(context.exception))
