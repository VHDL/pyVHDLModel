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
"""This module contains the predefined package ``std.textio`` of VHDL library ``STD``."""

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression import EnumerationLiteral, IntegerLiteral, StringLiteral
from pyVHDLModel.Type       import EnumeratedType, ArrayType, AccessType, FileType, Subtype
from pyVHDLModel.Object     import File
from pyVHDLModel.Interface  import ParameterFileInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class TextIO(PredefinedPackage):
	"""
	Predefined package ``std.textio`` (IEEE Std 1076-2008, 16.4).

	Its declarations, in the order of the standard:

	* types ``line``, ``text`` and ``side``, subtype ``width`` and function ``justify``
	* files ``input`` and ``output``, opened for reading and writing as ``STD_INPUT`` and ``STD_OUTPUT``
	* the input procedures ``readline``, ``read``, ``sread``, ``oread`` and ``hread``, and their aliases
	  (``string_read``, ``bread``, ``binary_read``, ``octal_read``, ``hex_read``)
	* the output procedures ``writeline``, ``tee``, ``write``, ``owrite`` and ``hwrite``, and their aliases (``swrite``,
	  ``string_write``, ``bwrite``, ``binary_write``, ``octal_write``, ``hex_write``)

	Each alias selects an overload by a signature, e.g. ``alias BREAD is READ [LINE, BIT_VECTOR];``.

	With :data:`VHDLVersion.VHDL2019 <pyVHDLModel.VHDLVersion.VHDL2019>`, it declares the addition of IEEE Std
	1076-2019, 16.4: the type ``line_vector`` after ``line``.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.TextIOPkg.TextIO_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``textio`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._DeclareItem(AccessType("line", self._TypeMark("string")), self._types)
		if vhdlVersion is VHDLVersion.VHDL2019:
			lineVector = ArrayType("line_vector", (self._TypeMark("natural"),), self._TypeMark("line"))
			self._DeclareItem(lineVector, self._types)

		self._DeclareItem(FileType("text", self._TypeMark("string")), self._types)
		self._DeclareItem(EnumeratedType("side", (EnumerationLiteral("right"), EnumerationLiteral("left"))), self._types)
		self._DeclareItem(Subtype("width", self._TypeMark("natural")), self._subtypes)
		self._DeclareSubprogram(
			Function("justify", self._TypeMark("string"), parameterItems=(
				self._InParameter(("VALUE",), self._TypeMark("string")),
				*self._JustificationParameters()
			)),
			self._functions
		)

		for identifier, openKind, logicalName in (
			("input",  "read_mode",  "STD_INPUT"),
			("output", "write_mode", "STD_OUTPUT")
		):
			file = File(
				(identifier,),
				self._TypeMark("text"),
				openKind=SimpleObjectOrFunctionCallSymbol(SimpleName(openKind)),
				logicalName=StringLiteral(logicalName)
			)
			self._files[identifier] = file
			self.AddDeclaredItem(file)

		self._DeclareSubprogram(
			Procedure("readline", parameterItems=(
				ParameterFileInterfaceItem(("F",), self._TypeMark("text")),
				self._LineParameter()
			)),
			self._procedures
		)
		for subtype in ("bit", "bit_vector", "boolean", "character", "integer", "real", "string", "time"):
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark(subtype)),
					self._OutParameter(("GOOD",), self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure("read", parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark(subtype))
				)),
				self._procedures
			)

		self._DeclareSubprogram(
			Procedure("sread", parameterItems=(
				self._LineParameter(),
				self._OutParameter(("VALUE",), self._TypeMark("string")),
				self._OutParameter(("STRLEN",), self._TypeMark("natural"))
			)),
			self._procedures
		)
		self._DeclareAlias(
			"string_read",
			"sread",
			(self._TypeMark("line"), self._TypeMark("string"), self._TypeMark("natural"))
		)
		for identifier in ("bread", "binary_read"):
			self._DeclareAlias(
				identifier,
				"read",
				(self._TypeMark("line"), self._TypeMark("bit_vector"), self._TypeMark("boolean"))
			)
			self._DeclareAlias(identifier, "read", (self._TypeMark("line"), self._TypeMark("bit_vector")))

		for identifier, aliasIdentifier in (
			("oread", "octal_read"),
			("hread", "hex_read")
		):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark("bit_vector")),
					self._OutParameter(("GOOD",), self._TypeMark("boolean"))
				)),
				self._procedures
			)
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._OutParameter(("VALUE",), self._TypeMark("bit_vector"))
				)),
				self._procedures
			)
			self._DeclareAlias(
				aliasIdentifier,
				identifier,
				(self._TypeMark("line"), self._TypeMark("bit_vector"), self._TypeMark("boolean"))
			)
			self._DeclareAlias(aliasIdentifier, identifier, (self._TypeMark("line"), self._TypeMark("bit_vector")))

		for identifier in ("writeline", "tee"):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					ParameterFileInterfaceItem(("F",), self._TypeMark("text")),
					self._LineParameter()
				)),
				self._procedures
			)

		for subtype in ("bit", "bit_vector", "boolean", "character", "integer"):
			self._DeclareSubprogram(
				Procedure("write", parameterItems=(
					self._LineParameter(),
					self._InParameter(("VALUE",), self._TypeMark(subtype)),
					*self._JustificationParameters()
				)),
				self._procedures
			)

		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("real")),
				*self._JustificationParameters(),
				self._InParameter(("DIGITS",), self._TypeMark("natural"), IntegerLiteral(0))
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("real")),
				self._InParameter(("FORMAT",), self._TypeMark("string"))
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("string")),
				*self._JustificationParameters()
			)),
			self._procedures
		)
		self._DeclareSubprogram(
			Procedure("write", parameterItems=(
				self._LineParameter(),
				self._InParameter(("VALUE",), self._TypeMark("time")),
				*self._JustificationParameters(),
				self._InParameter(("UNIT",), self._TypeMark("time"), SimpleObjectOrFunctionCallSymbol(SimpleName("ns")))
			)),
			self._procedures
		)
		for identifier, subtype in (
			("swrite",       "string"),
			("string_write", "string"),
			("bwrite",       "bit_vector"),
			("binary_write", "bit_vector")
		):
			self._DeclareAlias(
				identifier,
				"write",
				(self._TypeMark("line"), self._TypeMark(subtype), self._TypeMark("side"), self._TypeMark("width"))
			)

		for identifier, aliasIdentifier in (
			("owrite", "octal_write"),
			("hwrite", "hex_write")
		):
			self._DeclareSubprogram(
				Procedure(identifier, parameterItems=(
					self._LineParameter(),
					self._InParameter(("VALUE",), self._TypeMark("bit_vector")),
					*self._JustificationParameters()
				)),
				self._procedures
			)
			self._DeclareAlias(
				aliasIdentifier,
				identifier,
				(self._TypeMark("line"), self._TypeMark("bit_vector"), self._TypeMark("side"), self._TypeMark("width"))
			)


@export
class TextIO_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``std.textio``.

	.. seealso::

	   Matching :class:`Package <pyVHDLModel.STD.TextIOPkg.TextIO>` declaration.
	"""
