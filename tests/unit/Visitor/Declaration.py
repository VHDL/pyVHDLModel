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
"""Tests for the walk of alias and attribute declarations (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Declaration import EntityClass, Alias, Attribute, AttributeSpecification
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol

from tests.unit.Visitor      import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Aliases(Testcase):
	def test_Alias(self) -> None:
		name =     SimpleObjectOrFunctionCallSymbol(SimpleName("clk"))
		alias =    Alias("clock", name)
		recorder = FullRecorder()

		alias.Visit(recorder)

		self.assertEqual([
			("VisitAlias",       alias),
			("VisitIs",          alias),
			("VisitSymbol",      name),
			("VisitSimpleName",  name.Name),
			("DepartSimpleName", name.Name),
			("DepartSymbol",     name),
			("DepartAlias",      alias),
		], recorder.Events)

	def test_Alias_Subtype(self) -> None:
		subtype =  SimpleSubtypeSymbol(SimpleName("bit"))
		alias =    Alias("clock", SimpleObjectOrFunctionCallSymbol(SimpleName("clk")), subtype)
		recorder = FullRecorder()

		alias.Visit(recorder)

		self.assertEqual(
			["VisitAlias", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "VisitIs", "VisitSymbol",
			 "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "DepartAlias"],
			[event[0] for event in recorder.Events]
		)


class Attributes(Testcase):
	def test_Attribute(self) -> None:
		attribute = Attribute("bits", SimpleSubtypeSymbol(SimpleName("natural")))
		recorder =  FullRecorder()

		attribute.Visit(recorder)

		self.assertEqual(
			["VisitAttribute", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "DepartAttribute"],
			[event[0] for event in recorder.Events]
		)

	def test_Specification(self) -> None:
		"""The names are reported inside the entity specification part, separated by commas."""
		attribute =     SimpleName("bits")
		first =         SimpleName("byte")
		second =        SimpleName("word")
		value =         IntegerLiteral(8)
		specification = AttributeSpecification([first, second], attribute, EntityClass.Subtype, value)
		recorder =      FullRecorder()

		specification.Visit(recorder)

		self.assertEqual([
			("VisitAttributeSpecification",  specification),
			("VisitSimpleName",              attribute),
			("DepartSimpleName",             attribute),
			("VisitEntitySpecification",     specification),
			("VisitSimpleName",              first),
			("DepartSimpleName",             first),
			("VisitNameListSeparator",       specification),
			("VisitSimpleName",              second),
			("DepartSimpleName",             second),
			("DepartEntitySpecification",    specification),
			("VisitIs",                      specification),
			("VisitIntegerLiteral",          value),
			("DepartIntegerLiteral",         value),
			("DepartAttributeSpecification", specification),
		], recorder.Events)
