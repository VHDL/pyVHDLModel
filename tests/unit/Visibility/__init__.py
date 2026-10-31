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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Visibility tests: use clauses, hiding, conflicting imports and declaration order (IEEE Std 1076-2008, clause 12).

The tests check :meth:`~pyVHDLModel.Namespace.Namespace.Lookup` on analyzed designs.

The expected results follow GHDL's verdicts (``ghdl -a --std=08``) for the same VHDL code, given in each test.
"""
from pathlib                import Path
from typing                 import Iterable

from pyVHDLModel            import Design, Document
from pyVHDLModel.Base       import Direction, Mode, SimpleRange
from pyVHDLModel.DesignUnit import DesignUnit, UseClause
from pyVHDLModel.Expression import CharacterEnumerationLiteral, EnumerationLiteral, IntegerLiteral, \
                                   PhysicalIntegerLiteral
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Name       import AllName, SelectedName, SimpleName
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Subprogram import Function
from pyVHDLModel.Symbol     import AllPackageMembersReferenceSymbol, PackageMemberReferenceSymbol, \
                                   PackageReferenceSymbol, PackageSymbol
from pyVHDLModel.Type       import EnumeratedType, PhysicalType

from tests.unit             import _subtypeSymbol


def _use(*selectedNames: str) -> UseClause:
	"""
	A use clause of dotted names, with the symbols pyGHDL creates.

	A name of two parts (``lib.pkg``, ``work.all``) is a package reference symbol, ``lib.pkg.all`` an all-members symbol,
	``lib.pkg.item`` a member symbol.
	"""
	symbols = []
	for selectedName in selectedNames:
		*prefixes, suffix = selectedName.split(".")
		prefix = SimpleName(prefixes[0])
		for identifier in prefixes[1:]:
			prefix = SelectedName(identifier, prefix)

		name = AllName(prefix) if suffix == "all" else SelectedName(suffix, prefix)
		if len(prefixes) == 1:
			symbols.append(PackageReferenceSymbol(name))
		elif suffix == "all":
			symbols.append(AllPackageMembersReferenceSymbol(name))
		else:
			symbols.append(PackageMemberReferenceSymbol(name))

	return UseClause(symbols)


def _design(*designUnits: DesignUnit, libraries: Iterable[tuple[str, Iterable[DesignUnit]]] = ()) -> Design:
	"""
	An analyzed design: the design units in library ``lib``, preceded by the design units of further libraries.

	The predefined libraries ``std`` and ``ieee`` are loaded.
	"""
	design = Design("design")
	design.LoadStdLibrary()
	design.LoadIEEELibrary()
	for libraryName, units in (*libraries, ("lib", designUnits)):
		document = Document(Path(f"{libraryName}.vhdl"))
		for designUnit in units:
			document._AddDesignUnit(designUnit)

		design.AddDocument(document, design.GetLibrary(libraryName))

	design.Analyze()

	return design


def _enumeration(identifier: str, *literals: str) -> EnumeratedType:
	"""An enumerated type; a literal written in apostrophes (``"'0'"``) is a character literal."""
	return EnumeratedType(
		identifier,
		[
			CharacterEnumerationLiteral(literal[1]) if literal.startswith("'") else EnumerationLiteral(literal)
			for literal in literals
		]
	)


def _constant(identifier: str, subtypeName: str) -> Constant:
	"""A constant declaration."""
	return Constant((identifier, ), _subtypeSymbol(subtypeName), IntegerLiteral(1))


def _function(identifier: str, parameterType: str) -> Function:
	"""A function with one parameter, returning an integer."""
	parameter = ParameterConstantInterfaceItem(("a", ), Mode.In, _subtypeSymbol(parameterType))
	return Function(identifier, _subtypeSymbol("integer"), parameterItems=[parameter])


def _packageSymbol(identifier: str) -> PackageSymbol:
	"""Reference to a package, as a package body has."""
	return PackageSymbol(SimpleName(identifier))


def _distance() -> PhysicalType:
	"""A physical type with the units ``mm`` and ``cm``."""
	rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(1000), Direction.To)
	return PhysicalType("distance", rng, "mm", [("cm", PhysicalIntegerLiteral(10, "mm"))])
