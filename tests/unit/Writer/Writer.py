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
"""Tests for the infrastructure of pyVHDLModel.Formatting.VHDL: style object, dispatch, error reporting."""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Base            import Direction, SimpleRange
from pyVHDLModel.Expression      import EnumerationLiteral, FunctionCall, IntegerLiteral, NullLiteral
from pyVHDLModel.Formatting.VHDL import KeywordCase, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName, OpenName
from pyVHDLModel.Symbol          import ConstrainedArraySubtypeSymbol
from pyVHDLModel.Visitor         import Visitor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ParserName(SimpleName):
	"""A parser's subclass of a model class, like the mirror classes of ``pyGHDL.dom``."""


class Styles(Testcase):
	def test_Default(self) -> None:
		style = VHDLStyle()

		self.assertIs(KeywordCase.Lower, style.KeywordCase)

	def test_KeywordCase(self) -> None:
		style = VHDLStyle(KeywordCase.Upper)

		self.assertIs(KeywordCase.Upper, style.KeywordCase)

	def test_KeywordCase_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLStyle(None)

		self.assertEqual("Parameter 'keywordCase' is None.", str(context.exception))

	def test_KeywordCase_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			VHDLStyle("upper")

		self.assertEqual("Parameter 'keywordCase' is not of type 'KeywordCase'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class Writers(Testcase):
	def test_Default(self) -> None:
		writer = VHDLWriter()

		self.assertIs(KeywordCase.Lower, writer.Style.KeywordCase)

	def test_Style(self) -> None:
		style = VHDLStyle(KeywordCase.Upper)
		writer = VHDLWriter(style)

		self.assertIs(style, writer.Style)

	def test_Style_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			VHDLWriter(KeywordCase.Upper)

		self.assertEqual("Parameter 'style' is not of type 'VHDLStyle'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Formatting.VHDL.KeywordCase'."], context.exception.__notes__)

	def test_Events(self) -> None:
		"""The writer handles the events of every model class with a walk, except a symbol: it's written by its name."""
		classNames = {name[len("Depart"):] for name in dir(Visitor) if name.startswith("Depart")}
		for className in classNames - {"Symbol"}:
			with self.subTest(className=className):
				self.assertTrue(
					getattr(VHDLWriter, f"Visit{className}") is not getattr(Visitor, f"Visit{className}") or
					getattr(VHDLWriter, f"Depart{className}") is not getattr(Visitor, f"Depart{className}")
				)

		tokenEvents = {name for name in dir(Visitor) if name.startswith("Visit")} - {f"Visit{name}" for name in classNames}
		for tokenEvent in tokenEvents:
			with self.subTest(tokenEvent=tokenEvent):
				self.assertIsNot(getattr(Visitor, tokenEvent), getattr(VHDLWriter, tokenEvent))


class Dispatch(Testcase):
	def test_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLWriter().Format(None)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			VHDLWriter().Format("clk")

		self.assertEqual("Parameter 'element' is not of type 'ModelEntity' or 'Symbol'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Unsupported(self) -> None:
		call = FunctionCall()

		with self.assertRaises(NotImplementedError) as context:
			VHDLWriter().Format(call)

		self.assertEqual("Model element has no walk for a visitor.", str(context.exception))

	def test_Unsupported_Child(self) -> None:
		"""An unsupported child fails the whole element; nothing is skipped."""
		call = FunctionCall()
		name = ParenthesisName(SimpleName("f"), [IntegerLiteral(1), call])

		with self.assertRaises(NotImplementedError) as context:
			VHDLWriter().Format(name)

		self.assertEqual("Model element has no walk for a visitor.", str(context.exception))

	def test_Unsupported_Subclass(self) -> None:
		"""A subclass carrying more data than its base class is not written as the base class."""
		subtype = ConstrainedArraySubtypeSymbol(SimpleName("unsigned"), [
			SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		])

		with self.assertRaises(NotImplementedError) as context:
			VHDLWriter().Format(subtype)

		self.assertEqual("Model element has no walk for a visitor.", str(context.exception))

	def test_ParserSubclass(self) -> None:
		name = ParserName("clk")

		self.assertEqual("clk", VHDLWriter().Format(name))


class Buffers(Testcase):
	def test_Reset(self) -> None:
		"""Each call of ``Format`` starts with an empty buffer."""
		writer = VHDLWriter()

		self.assertEqual("a", writer.Format(SimpleName("a")))
		self.assertEqual("b", writer.Format(SimpleName("b")))

	def test_Reset_Error(self) -> None:
		"""A failed call leaves no text for the next call."""
		writer = VHDLWriter()
		name =   ParenthesisName(SimpleName("f"), [IntegerLiteral(1), FunctionCall()])

		with self.assertRaises(NotImplementedError):
			writer.Format(name)

		self.assertEqual("c", writer.Format(SimpleName("c")))


class KeywordCases(Testcase):
	def test_Null(self) -> None:
		self.assertEqual("NULL", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(NullLiteral()))

	def test_Open(self) -> None:
		self.assertEqual("OPEN", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(OpenName()))

	def test_Identifier(self) -> None:
		"""Identifiers keep their letter case."""
		self.assertEqual("Idle", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(EnumerationLiteral("Idle")))
