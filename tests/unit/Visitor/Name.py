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
"""Tests for the walk of names, symbols and association items (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.MetaClasses   import AbstractClassError
from pyTooling.Testing       import Testcase

from pyVHDLModel.Association import ParameterAssociationItem
from pyVHDLModel.Expression  import FunctionCall, IntegerLiteral
from pyVHDLModel.Name        import SimpleName, SelectedName, IndexedName, ParenthesisName
from pyVHDLModel.Symbol      import ConstrainedArraySubtypeSymbol, IndexedObjectOrFunctionCallSymbol
from pyVHDLModel.Visitor     import Visitor

from tests.unit.Visitor      import NoOverrides, Recorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ParserName(SimpleName):
	"""A parser's subclass of a model class, like the mirror classes of ``pyGHDL.dom``."""


class Walks(Testcase):
	def test_Abstract(self) -> None:
		"""``Visitor`` is abstract: a visitor derives from it."""
		with self.assertRaises(AbstractClassError):
			Visitor()

	def test_Default(self) -> None:
		"""The events of the base-class do nothing."""
		name = IndexedName(SelectedName("m", SimpleName("work")), [IntegerLiteral(0), FunctionCall()])

		name.Visit(NoOverrides())

	def test_SelectedName(self) -> None:
		prefix =   SimpleName("ieee")
		name =     SelectedName("numeric_std", prefix)
		recorder = Recorder()

		name.Visit(recorder)

		self.assertEqual([
			("VisitSelectedName",  name),
			("VisitSimpleName",    prefix),
			("DepartSimpleName",   prefix),
			("DepartSelectedName", name),
		], recorder.Events)

	def test_IndexedName(self) -> None:
		prefix =   SimpleName("m")
		first =    IntegerLiteral(0)
		second =   IntegerLiteral(1)
		name =     IndexedName(prefix, [first, second])
		recorder = Recorder()

		name.Visit(recorder)

		self.assertEqual([
			("VisitIndexedName",     name),
			("VisitSimpleName",      prefix),
			("DepartSimpleName",     prefix),
			("VisitLeftParenthesis", name),
			("VisitIntegerLiteral",  first),
			("DepartIntegerLiteral", first),
			("VisitComma",           name),
			("VisitIntegerLiteral",  second),
			("DepartIntegerLiteral", second),
			("DepartIndexedName",    name),
		], recorder.Events)

	def test_FunctionCall(self) -> None:
		"""Visit, then the children in source order with the token events between them, then depart."""
		function =   SimpleName("resize")
		actual =     SimpleName("a")
		formal =     SimpleName("new_size")
		size =       IntegerLiteral(8)
		positional = ParameterAssociationItem(None, actual)
		named =      ParameterAssociationItem(formal, size)
		name =       ParenthesisName(function, [positional, named])
		symbol =     IndexedObjectOrFunctionCallSymbol(name)
		recorder =   Recorder()

		symbol.Visit(recorder)

		self.assertEqual([
			("VisitSymbol",           symbol),
			("VisitParenthesisName",  name),
			("VisitSimpleName",       function),
			("DepartSimpleName",      function),
			("VisitLeftParenthesis",  name),
			("VisitAssociationItem",  positional),
			("VisitSimpleName",       actual),
			("DepartSimpleName",      actual),
			("DepartAssociationItem", positional),
			("VisitComma",            name),
			("VisitAssociationItem",  named),
			("VisitSimpleName",       formal),
			("DepartSimpleName",      formal),
			("VisitArrow",            named),
			("VisitIntegerLiteral",   size),
			("DepartIntegerLiteral",  size),
			("DepartAssociationItem", named),
			("DepartParenthesisName", name),
			("DepartSymbol",          symbol),
		], recorder.Events)

	def test_ParserSubclass(self) -> None:
		"""A parser's subclass inherits the walk of its model class."""
		name =     ParserName("clk")
		recorder = Recorder()

		name.Visit(recorder)

		self.assertEqual([("VisitSimpleName", name), ("DepartSimpleName", name)], recorder.Events)


class Unknowns(Testcase):
	def test_Unknown(self) -> None:
		"""A class without a walk of its own reports an unknown element."""
		call =     FunctionCall()
		recorder = Recorder()

		call.Visit(recorder)

		self.assertEqual([("VisitUnknown", call), ("DepartUnknown", call)], recorder.Events)

	def test_Unknown_Child(self) -> None:
		call =     FunctionCall()
		name =     IndexedName(SimpleName("m"), [call])
		recorder = Recorder()

		name.Visit(recorder)

		self.assertIn(("VisitUnknown", call), recorder.Events)

	def test_Unknown_Symbol(self) -> None:
		"""A constrained subtype symbol isn't walked as a symbol: its name is not visited."""
		symbol =   ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [])
		recorder = Recorder()

		symbol.Visit(recorder)

		self.assertEqual([("VisitUnknown", symbol), ("DepartUnknown", symbol)], recorder.Events)
