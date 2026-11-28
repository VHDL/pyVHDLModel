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
"""This module contains the predefined package ``std.env`` of VHDL library ``STD``."""

from typing                 import Iterable, Optional as Nullable

from pyTooling.Decorators   import export

from pyVHDLModel            import VHDLVersion
from pyVHDLModel.Base       import SimpleRange, Direction, Mode
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression import EnumerationLiteral, IntegerLiteral, StringLiteral, ConcatenationExpression
from pyVHDLModel.Type       import EnumeratedType, ArrayType, AccessType, RecordType, RecordTypeElement
from pyVHDLModel.Object     import DeferredConstant
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem, ParameterVariableInterfaceItem
from pyVHDLModel.Subprogram import Procedure, Function, Operator
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Env(PredefinedPackage):
	"""
	Predefined package ``std.env`` (IEEE Std 1076-2008, 16.5).

	Its declarations, in the order of the standard: the procedures ``stop`` and ``finish``, each with and without a
	``STATUS`` parameter, and the function ``resolution_limit``.

	With :data:`VHDLVersion.VHDL2019 <pyVHDLModel.VHDLVersion.VHDL2019>`, it declares the additions of IEEE Std
	1076-2019, 16.5 after them, in the order of the standard:

	* date and time: type ``dayofweek``, record type ``time_record``, functions like ``localtime`` and ``epoch``,
	  the operators ``"+"`` and ``"-"`` of ``time_record`` and ``to_string``
	* environment and tool: function ``getenv``, functions like ``vhdl_version`` and ``tool_name``
	* directories and files: types ``directory_items`` and ``directory``, the status types like ``dir_open_status``,
	  subprograms like ``dir_open`` and ``dir_createdir``, the deferred constant ``dir_separator``
	* call path: types ``call_path_element``, ``call_path_vector`` and ``call_path_vector_ptr``, functions
	  ``to_string``, ``get_call_path``, ``file_name``, ``file_path`` and ``file_line``
	* assertions and PSL: subprograms like ``isvhdlassertfailed``, ``setvhdlassertenable`` and ``clearpslstate``

	The declarations follow the package ``std/env.vhdl`` of the IEEE Std 1076-2019 packages, also where the
	standard is known to be wrong, e.g. the constant parameter ``Dir`` of ``dir_close`` of a type containing an
	access type.

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.STD.EnvPkg.Env_Body>` declaration.
	"""

	def __init__(self, vhdlVersion: VHDLVersion = VHDLVersion.VHDL2008) -> None:
		"""
		Initializes the ``env`` package.

		:param vhdlVersion: Optional, the VHDL version of the declarations. Default: ``VHDLVersion.VHDL2008``.
		:raises ValueError: If parameter 'vhdlVersion' is None.
		:raises TypeError:  If parameter 'vhdlVersion' is not of type :class:`~pyVHDLModel.VHDLVersion`.
		:raises ValueError: If parameter 'vhdlVersion' is not a supported VHDL version (VHDL-2008, VHDL-2019).
		"""
		super().__init__(vhdlVersion)

		self._AddPackageClause(("work.textio.all",))

		for identifier in ("stop", "finish"):
			status = self._InParameter(("STATUS",), self._TypeMark("integer"))
			self._DeclareSubprogram(Procedure(identifier, parameterItems=(status,)), self._procedures)
			self._DeclareSubprogram(Procedure(identifier), self._procedures)

		self._DeclareSubprogram(Function("resolution_limit", self._TypeMark("delay_length")), self._functions)

		if vhdlVersion is VHDLVersion.VHDL2019:
			self._DeclareVHDL2019Additions()

	def _DeclareVHDL2019Additions(self) -> None:
		"""
		Declare the additions of IEEE Std 1076-2019, 16.5, in the order of the standard.
		"""
		def function(
			identifier:     str,
			returnType:     SimpleSubtypeSymbol,
			parameterItems: Nullable[Iterable[ParameterConstantInterfaceItem | ParameterVariableInterfaceItem]] = None,
			isPure:         bool = True
		) -> None:
			"""
			Nested function declaring a function of this package.

			:param identifier:     The function's identifier.
			:param returnType:     The type mark of the return type.
			:param parameterItems: Optional, the parameters, in declaration order. Default: ``None``, no parameters.
			:param isPure:         Optional, ``False`` for an impure function. Default: ``True``, a pure function.
			"""
			self._DeclareSubprogram(Function(identifier, returnType, isPure, parameterItems=parameterItems), self._functions)

		def procedure(
			identifier:     str,
			parameterItems: Nullable[Iterable[ParameterConstantInterfaceItem | ParameterVariableInterfaceItem]] = None
		) -> None:
			"""
			Nested function declaring a procedure of this package.

			:param identifier:     The procedure's identifier.
			:param parameterItems: Optional, the parameters, in declaration order. Default: ``None``, no parameters.
			"""
			self._DeclareSubprogram(Procedure(identifier, parameterItems=parameterItems), self._procedures)

		def enumeration(identifier: str, literals: Iterable[str]) -> None:
			"""
			Nested function declaring an enumerated type of this package.

			:param identifier: The type's identifier.
			:param literals:   The identifiers of the enumeration literals, in declaration order.
			"""
			self._DeclareItem(EnumeratedType(identifier, [EnumerationLiteral(literal) for literal in literals]), self._types)

		def integerRange(low: int, high: int) -> ConstrainedScalarSubtypeSymbol:
			"""
			Nested function creating the subtype indication ``INTEGER range low to high``.

			:param low:  The lower bound.
			:param high: The upper bound.
			:returns:    The subtype indication.
			"""
			return ConstrainedScalarSubtypeSymbol(
				SimpleName("integer"),
				SimpleRange(IntegerLiteral(low), IntegerLiteral(high), Direction.To)
			)

		def literal(identifier: str) -> SimpleObjectOrFunctionCallSymbol:
			"""
			Nested function creating the name of an enumeration literal or a constant used as default value.

			:param identifier: The literal's identifier, e.g. ``true``.
			:returns:          The name.
			"""
			return SimpleObjectOrFunctionCallSymbol(SimpleName(identifier))

		# Date and time
		enumeration("dayofweek", ("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"))
		self._DeclareItem(
			RecordType("time_record", (
				RecordTypeElement(("microsecond", ), integerRange(0, 999_999)),
				RecordTypeElement(("second", ),      integerRange(0, 61)),
				RecordTypeElement(("minute", ),      integerRange(0, 59)),
				RecordTypeElement(("hour", ),        integerRange(0, 23)),
				RecordTypeElement(("day", ),         integerRange(1, 31)),
				RecordTypeElement(("month", ),       integerRange(0, 11)),
				RecordTypeElement(("year", ),        integerRange(1, 4095)),
				RecordTypeElement(("weekday", ),     self._TypeMark("dayofweek")),
				RecordTypeElement(("dayofyear", ),   integerRange(0, 365))
			)),
			self._types
		)

		function("localtime", self._TypeMark("time_record"), isPure=False)
		function("gmtime", self._TypeMark("time_record"), isPure=False)
		function("epoch", self._TypeMark("real"), isPure=False)
		for identifier in ("localtime", "gmtime"):
			function(identifier, self._TypeMark("time_record"), (self._InParameter(("TIMER", ), self._TypeMark("real")), ))

		function("epoch", self._TypeMark("real"), (self._InParameter(("TREC", ), self._TypeMark("time_record")), ))
		for identifier in ("localtime", "gmtime"):
			function(identifier, self._TypeMark("time_record"), (
				self._InParameter(("TREC", ), self._TypeMark("time_record")),
			))

		for operatorSymbol in ("+", "-"):
			for left, leftType, right, rightType in (
				("TREC",  "time_record", "DELTA", "real"),
				("DELTA", "real",        "TREC",  "time_record")
			):
				operator = Operator(operatorSymbol, self._TypeMark("time_record"), parameterItems=(
					self._InParameter((left, ), self._TypeMark(leftType)),
					self._InParameter((right, ), self._TypeMark(rightType))
				))
				self._DeclareSubprogram(operator, self._functions)

		difference = Operator("-", self._TypeMark("real"), parameterItems=(
			self._InParameter(("TR1", "TR2"), self._TypeMark("time_record")),
		))
		self._DeclareSubprogram(difference, self._functions)

		function("time_to_seconds", self._TypeMark("real"), (self._InParameter(("TIME_VAL", ), self._TypeMark("time")), ))
		function("seconds_to_time", self._TypeMark("time"), (self._InParameter(("REAL_VAL", ), self._TypeMark("real")), ))
		function("to_string", self._TypeMark("string"), (
			self._InParameter(("TREC", ), self._TypeMark("time_record")),
			ParameterConstantInterfaceItem(("FRAC_DIGITS", ), Mode.In, integerRange(0, 6), IntegerLiteral(0))
		))

		# Environment and tool
		for returnType in ("string", "line"):
			function("getenv", self._TypeMark(returnType), (
				self._InParameter(("Name", ), self._TypeMark("string")),
			), isPure=False)

		function("vhdl_version", self._TypeMark("string"), isPure=False)
		for identifier in ("tool_type", "tool_vendor", "tool_name", "tool_edition", "tool_version"):
			function(identifier, self._TypeMark("string"))

		# Directories and files
		self._DeclareItem(AccessType("directory_items", self._TypeMark("line_vector")), self._types)
		self._DeclareItem(
			RecordType("directory", (
				RecordTypeElement(("Name", ),  self._TypeMark("line")),
				RecordTypeElement(("Items", ), self._TypeMark("directory_items"))
			)),
			self._types
		)
		for identifier, literals in (
			("dir_open_status",    ("status_ok", "status_not_found", "status_no_directory", "status_access_denied",
			                        "status_error")),
			("dir_create_status",  ("status_ok", "status_item_exists", "status_access_denied", "status_error")),
			("dir_delete_status",  ("status_ok", "status_no_directory", "status_not_empty", "status_access_denied",
			                        "status_error")),
			("file_delete_status", ("status_ok", "status_no_file", "status_access_denied", "status_error"))
		):
			enumeration(identifier, literals)

		procedure("dir_open", (
			self._OutParameter(("Dir", ), self._TypeMark("directory")),
			self._InParameter(("Path", ), self._TypeMark("string")),
			self._OutParameter(("Status", ), self._TypeMark("dir_open_status"))
		))
		function("dir_open", self._TypeMark("dir_open_status"), (
			self._OutParameter(("Dir", ), self._TypeMark("directory")),
			self._InParameter(("Path", ), self._TypeMark("string"))
		), isPure=False)
		procedure("dir_close", (self._InParameter(("Dir", ), self._TypeMark("directory")), ))
		for identifier in ("dir_itemexists", "dir_itemisdir", "dir_itemisfile"):
			function(identifier, self._TypeMark("boolean"), (
				self._InParameter(("Path", ), self._TypeMark("string")),
			), isPure=False)

		procedure("dir_workingdir", (
			self._InParameter(("Path", ), self._TypeMark("string")),
			self._OutParameter(("Status", ), self._TypeMark("dir_open_status"))
		))
		function("dir_workingdir", self._TypeMark("dir_open_status"), (
			self._InParameter(("Path", ), self._TypeMark("string")),
		), isPure=False)
		function("dir_workingdir", self._TypeMark("string"), isPure=False)

		for identifier, option, status in (
			("dir_createdir", "Parents",   "dir_create_status"),
			("dir_deletedir", "Recursive", "dir_delete_status")
		):
			procedure(identifier, (
				self._InParameter(("Path", ), self._TypeMark("string")),
				self._OutParameter(("Status", ), self._TypeMark(status))
			))
			procedure(identifier, (
				self._InParameter(("Path", ), self._TypeMark("string")),
				self._InParameter((option, ), self._TypeMark("boolean")),
				self._OutParameter(("Status", ), self._TypeMark(status))
			))
			function(identifier, self._TypeMark(status), (
				self._InParameter(("Path", ), self._TypeMark("string")),
				self._InParameter((option, ), self._TypeMark("boolean"), literal("false"))
			), isPure=False)

		procedure("dir_deletefile", (
			self._InParameter(("Path", ), self._TypeMark("string")),
			self._OutParameter(("Status", ), self._TypeMark("file_delete_status"))
		))
		function("dir_deletefile", self._TypeMark("file_delete_status"), (
			self._InParameter(("Path", ), self._TypeMark("string")),
		), isPure=False)

		dirSeparator = DeferredConstant(("dir_separator", ), self._TypeMark("string"))
		self._deferredConstants[dirSeparator._normalizedIdentifiers[0]] = dirSeparator
		self.AddDeclaredItem(dirSeparator)

		# Call path
		self._DeclareItem(
			RecordType("call_path_element", (
				RecordTypeElement(("name", ),      self._TypeMark("line")),
				RecordTypeElement(("file_name", ), self._TypeMark("line")),
				RecordTypeElement(("file_path", ), self._TypeMark("line")),
				RecordTypeElement(("file_line", ), self._TypeMark("positive"))
			)),
			self._types
		)
		function("to_string", self._TypeMark("string"), (
			self._InParameter(("call_path", ), self._TypeMark("call_path_element")),
		), isPure=False)
		for typeDefinition in (
			ArrayType("call_path_vector", (self._TypeMark("natural"), ), self._TypeMark("call_path_element")),
			AccessType("call_path_vector_ptr", self._TypeMark("call_path_vector"))
		):
			self._DeclareItem(typeDefinition, self._types)
			separator = ConcatenationExpression(StringLiteral(""), literal("lf"))
			function("to_string", self._TypeMark("string"), (
				self._InParameter(("call_path", ), self._TypeMark(typeDefinition._identifier)),
				self._InParameter(("Separator", ), self._TypeMark("string"), separator)
			), isPure=False)

		function("get_call_path", self._TypeMark("call_path_vector_ptr"), isPure=False)
		for identifier, returnTypes in (
			("file_name", ("line", "string")),
			("file_path", ("line", "string")),
			("file_line", ("positive", "string"))
		):
			for returnType in returnTypes:
				function(identifier, self._TypeMark(returnType), isPure=False)

		# Assertions and PSL
		for identifier, returnType in (("isvhdlassertfailed", "boolean"), ("getvhdlassertcount", "natural")):
			function(identifier, self._TypeMark(returnType), isPure=False)
			function(identifier, self._TypeMark(returnType), (
				self._InParameter(("Level", ), self._TypeMark("severity_level")),
			), isPure=False)

		procedure("clearvhdlassert")
		procedure("setvhdlassertenable", (self._InParameter(("Enable", ), self._TypeMark("boolean"), literal("true")), ))
		procedure("setvhdlassertenable", (
			self._InParameter(("Level", ), self._TypeMark("severity_level"), literal("note")),
			self._InParameter(("Enable", ), self._TypeMark("boolean"), literal("true"))
		))
		function("getvhdlassertenable", self._TypeMark("boolean"), (
			self._InParameter(("Level", ), self._TypeMark("severity_level"), literal("note")),
		), isPure=False)
		procedure("setvhdlassertformat", (
			self._InParameter(("Level", ), self._TypeMark("severity_level")),
			self._InParameter(("Format", ), self._TypeMark("string"))
		))
		procedure("setvhdlassertformat", (
			self._InParameter(("Level", ), self._TypeMark("severity_level")),
			self._InParameter(("Format", ), self._TypeMark("string")),
			self._OutParameter(("Valid", ), self._TypeMark("boolean"))
		))
		function("getvhdlassertformat", self._TypeMark("string"), (
			self._InParameter(("Level", ), self._TypeMark("severity_level")),
		), isPure=False)
		procedure("setvhdlreadseverity", (
			self._InParameter(("Level", ), self._TypeMark("severity_level"), literal("failure")),
		))
		function("getvhdlreadseverity", self._TypeMark("severity_level"), isPure=False)

		function("pslassertfailed", self._TypeMark("boolean"), isPure=False)
		function("psliscovered", self._TypeMark("boolean"), isPure=False)
		procedure("setpslcoverassert", (self._InParameter(("Enable", ), self._TypeMark("boolean"), literal("true")), ))
		function("getpslcoverassert", self._TypeMark("boolean"), isPure=False)
		function("pslisassertcovered", self._TypeMark("boolean"), isPure=False)
		procedure("clearpslstate")


@export
class Env_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``std.env``.

	.. seealso::

	   Matching :class:`Package <pyVHDLModel.STD.EnvPkg.Env>` declaration.
	"""
