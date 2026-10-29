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
from pyTooling.MetaClasses       import AbstractClassError
from pyTooling.Testing           import Testcase

from pyVHDLModel.Expression      import AndExpression, EnumerationLiteral, FunctionCall, IntegerLiteral, \
                                        InverseExpression, ModuloExpression, NullLiteral, OrExpression
from pyVHDLModel.Formatting.VHDL import KeywordCase, IndentStyle, NewLine, ListStyle, InterfaceListStyle, \
                                        AssociationListStyle, VHDLStyle, VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName, OpenName
from pyVHDLModel.Symbol          import ConstrainedCompositeSubtypeSymbol
from pyVHDLModel.Visitor         import Visitor

from tests.unit.Writer           import _object

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ParserName(SimpleName):
	"""A parser's subclass of a model class, like the mirror classes of ``pyGHDL.dom``."""


class ParserAndExpression(AndExpression):
	"""A parser's subclass of a model class, like the mirror classes of ``pyGHDL.dom``."""


class ParserCompositeSubtypeSymbol(ConstrainedCompositeSubtypeSymbol):
	"""A parser's subclass of an abstract model class without a walk of its own."""


class Styles(Testcase):
	def test_Default(self) -> None:
		style = VHDLStyle()

		self.assertIs(KeywordCase.Lower, style.KeywordCase)
		self.assertIs(IndentStyle.Spaces, style.IndentStyle)
		self.assertEqual(2, style.IndentSize)

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

	def test_IndentStyle(self) -> None:
		style = VHDLStyle(indentStyle=IndentStyle.SmartTabs)

		self.assertIs(IndentStyle.SmartTabs, style.IndentStyle)

	def test_IndentStyle_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLStyle(indentStyle=None)

		self.assertEqual("Parameter 'indentStyle' is None.", str(context.exception))

	def test_IndentStyle_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			VHDLStyle(indentStyle="smart_tabs")

		self.assertEqual("Parameter 'indentStyle' is not of type 'IndentStyle'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_IndentSize(self) -> None:
		style = VHDLStyle(indentSize=4)

		self.assertEqual(4, style.IndentSize)

	def test_IndentSize_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLStyle(indentSize=None)

		self.assertEqual("Parameter 'indentSize' is None.", str(context.exception))

	def test_IndentSize_Type(self) -> None:
		for value in ("2", 2.0, True):
			with self.subTest(value=value):
				with self.assertRaises(TypeError) as context:
					VHDLStyle(indentSize=value)

				self.assertEqual("Parameter 'indentSize' is not of type 'int'.", str(context.exception))

	def test_IndentSize_Value(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLStyle(indentSize=0)

		self.assertEqual("Parameter 'indentSize' is less than 1.", str(context.exception))
		self.assertEqual(["Got value '0'."], context.exception.__notes__)

	def test_LineLength(self) -> None:
		style = VHDLStyle(lineLength=80)

		self.assertEqual(80, style.LineLength)

	def test_LineLength_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLStyle(lineLength=None)

		self.assertEqual("Parameter 'lineLength' is None.", str(context.exception))

	def test_LineLength_Type(self) -> None:
		for value in ("80", 80.0, True):
			with self.subTest(value=value):
				with self.assertRaises(TypeError) as context:
					VHDLStyle(lineLength=value)

				self.assertEqual("Parameter 'lineLength' is not of type 'int'.", str(context.exception))

	def test_LineLength_Value(self) -> None:
		with self.assertRaises(ValueError) as context:
			VHDLStyle(lineLength=0)

		self.assertEqual("Parameter 'lineLength' is less than 1.", str(context.exception))
		self.assertEqual(["Got value '0'."], context.exception.__notes__)

	def test_Default_Lists(self) -> None:
		"""Interface lists and map aspects: one element per line, parameter lists if too long; calls: a single line."""
		style = VHDLStyle()

		self.assertEqual(120, style.LineLength)
		for listStyle in (style.GenericClause, style.PortClause, style.SubprogramGenericClause, style.ParameterList):
			self.assertIs(NewLine.Add, listStyle.InterfaceElement)
			self.assertIs(NewLine.Remove, listStyle.InterfaceListSemicolon)
			self.assertIs(NewLine.Add, listStyle.LastCloseParenthesis)

		for listStyle in (style.GenericClause, style.PortClause, style.SubprogramGenericClause):
			self.assertFalse(listStyle.IgnoreSingleLine)

		self.assertTrue(style.ParameterList.IgnoreSingleLine)

		for listStyle in (style.GenericMap, style.PortMap):
			self.assertIs(NewLine.Add, listStyle.AssociationElement)
			self.assertIs(NewLine.Remove, listStyle.AssociationListComma)
			self.assertIs(NewLine.Add, listStyle.LastCloseParenthesis)
			self.assertFalse(listStyle.IgnoreSingleLine)

		for listStyle in (style.ProcedureCall, style.FunctionCall):
			self.assertIs(NewLine.Remove, listStyle.AssociationElement)
			self.assertIs(NewLine.Remove, listStyle.AssociationListComma)
			self.assertIs(NewLine.Remove, listStyle.LastCloseParenthesis)
			self.assertFalse(listStyle.IgnoreSingleLine)

	def test_GenericClause(self) -> None:
		listStyle = InterfaceListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(genericClause=listStyle).GenericClause)

	def test_GenericClause_Type(self) -> None:
		"""An association list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(genericClause=AssociationListStyle())

		self.assertEqual("Parameter 'genericClause' is not of type 'InterfaceListStyle'.", str(context.exception))
		self.assertEqual(["Got type 'pyVHDLModel.Formatting.VHDL.AssociationListStyle'."], context.exception.__notes__)

	def test_PortClause(self) -> None:
		listStyle = InterfaceListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(portClause=listStyle).PortClause)

	def test_PortClause_Type(self) -> None:
		"""An association list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(portClause=AssociationListStyle())

		self.assertEqual("Parameter 'portClause' is not of type 'InterfaceListStyle'.", str(context.exception))

	def test_SubprogramGenericClause(self) -> None:
		listStyle = InterfaceListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(subprogramGenericClause=listStyle).SubprogramGenericClause)

	def test_SubprogramGenericClause_Type(self) -> None:
		"""An association list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(subprogramGenericClause=AssociationListStyle())

		self.assertEqual("Parameter 'subprogramGenericClause' is not of type 'InterfaceListStyle'.", str(context.exception))

	def test_ParameterList(self) -> None:
		listStyle = InterfaceListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(parameterList=listStyle).ParameterList)

	def test_ParameterList_Type(self) -> None:
		"""An association list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(parameterList=AssociationListStyle())

		self.assertEqual("Parameter 'parameterList' is not of type 'InterfaceListStyle'.", str(context.exception))

	def test_GenericMap(self) -> None:
		listStyle = AssociationListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(genericMap=listStyle).GenericMap)

	def test_GenericMap_Type(self) -> None:
		"""An interface list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(genericMap=InterfaceListStyle())

		self.assertEqual("Parameter 'genericMap' is not of type 'AssociationListStyle'.", str(context.exception))

	def test_PortMap(self) -> None:
		listStyle = AssociationListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(portMap=listStyle).PortMap)

	def test_PortMap_Type(self) -> None:
		"""An interface list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(portMap=InterfaceListStyle())

		self.assertEqual("Parameter 'portMap' is not of type 'AssociationListStyle'.", str(context.exception))

	def test_ProcedureCall(self) -> None:
		listStyle = AssociationListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(procedureCall=listStyle).ProcedureCall)

	def test_ProcedureCall_Type(self) -> None:
		"""An interface list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(procedureCall=InterfaceListStyle())

		self.assertEqual("Parameter 'procedureCall' is not of type 'AssociationListStyle'.", str(context.exception))

	def test_FunctionCall(self) -> None:
		listStyle = AssociationListStyle(NewLine.Remove)

		self.assertIs(listStyle, VHDLStyle(functionCall=listStyle).FunctionCall)

	def test_FunctionCall_Type(self) -> None:
		"""An interface list style is rejected."""
		with self.assertRaises(TypeError) as context:
			VHDLStyle(functionCall=InterfaceListStyle())

		self.assertEqual("Parameter 'functionCall' is not of type 'AssociationListStyle'.", str(context.exception))


class InterfaceListStyles(Testcase):
	def test_Default(self) -> None:
		listStyle = InterfaceListStyle()

		self.assertIs(NewLine.Add, listStyle.InterfaceElement)
		self.assertIs(NewLine.Remove, listStyle.InterfaceListSemicolon)
		self.assertIs(NewLine.Add, listStyle.LastCloseParenthesis)
		self.assertFalse(listStyle.IgnoreSingleLine)

	def test_InterfaceElement(self) -> None:
		self.assertIs(NewLine.Remove, InterfaceListStyle(NewLine.Remove).InterfaceElement)

	def test_InterfaceElement_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			InterfaceListStyle(None)

		self.assertEqual("Parameter 'interfaceElement' is None.", str(context.exception))

	def test_InterfaceElement_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			InterfaceListStyle("remove_new_line")

		self.assertEqual("Parameter 'interfaceElement' is not of type 'NewLine'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_InterfaceListSemicolon(self) -> None:
		self.assertIs(NewLine.Add, InterfaceListStyle(interfaceListSemicolon=NewLine.Add).InterfaceListSemicolon)

	def test_InterfaceListSemicolon_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			InterfaceListStyle(interfaceListSemicolon=None)

		self.assertEqual("Parameter 'interfaceListSemicolon' is None.", str(context.exception))

	def test_InterfaceListSemicolon_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			InterfaceListStyle(interfaceListSemicolon="add_new_line")

		self.assertEqual("Parameter 'interfaceListSemicolon' is not of type 'NewLine'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_LastCloseParenthesis(self) -> None:
		self.assertIs(NewLine.Remove, InterfaceListStyle(lastCloseParenthesis=NewLine.Remove).LastCloseParenthesis)

	def test_LastCloseParenthesis_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			InterfaceListStyle(lastCloseParenthesis=None)

		self.assertEqual("Parameter 'lastCloseParenthesis' is None.", str(context.exception))

	def test_LastCloseParenthesis_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			InterfaceListStyle(lastCloseParenthesis="remove_new_line")

		self.assertEqual("Parameter 'lastCloseParenthesis' is not of type 'NewLine'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_IgnoreSingleLine(self) -> None:
		self.assertTrue(InterfaceListStyle(ignoreSingleLine=True).IgnoreSingleLine)

	def test_IgnoreSingleLine_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			InterfaceListStyle(ignoreSingleLine=None)

		self.assertEqual("Parameter 'ignoreSingleLine' is None.", str(context.exception))

	def test_IgnoreSingleLine_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			InterfaceListStyle(ignoreSingleLine="yes")

		self.assertEqual("Parameter 'ignoreSingleLine' is not of type 'bool'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

class AssociationListStyles(Testcase):
	def test_Default(self) -> None:
		listStyle = AssociationListStyle()

		self.assertIs(NewLine.Add, listStyle.AssociationElement)
		self.assertIs(NewLine.Remove, listStyle.AssociationListComma)
		self.assertIs(NewLine.Add, listStyle.LastCloseParenthesis)
		self.assertFalse(listStyle.IgnoreSingleLine)

	def test_AssociationElement(self) -> None:
		self.assertIs(NewLine.Remove, AssociationListStyle(NewLine.Remove).AssociationElement)

	def test_AssociationElement_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			AssociationListStyle(None)

		self.assertEqual("Parameter 'associationElement' is None.", str(context.exception))

	def test_AssociationElement_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			AssociationListStyle("remove_new_line")

		self.assertEqual("Parameter 'associationElement' is not of type 'NewLine'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_AssociationListComma(self) -> None:
		self.assertIs(NewLine.Add, AssociationListStyle(associationListComma=NewLine.Add).AssociationListComma)

	def test_AssociationListComma_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			AssociationListStyle(associationListComma=None)

		self.assertEqual("Parameter 'associationListComma' is None.", str(context.exception))

	def test_AssociationListComma_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			AssociationListStyle(associationListComma="add_new_line")

		self.assertEqual("Parameter 'associationListComma' is not of type 'NewLine'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_LastCloseParenthesis(self) -> None:
		self.assertIs(NewLine.Remove, AssociationListStyle(lastCloseParenthesis=NewLine.Remove).LastCloseParenthesis)

	def test_LastCloseParenthesis_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			AssociationListStyle(lastCloseParenthesis=None)

		self.assertEqual("Parameter 'lastCloseParenthesis' is None.", str(context.exception))

	def test_LastCloseParenthesis_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			AssociationListStyle(lastCloseParenthesis="remove_new_line")

		self.assertEqual("Parameter 'lastCloseParenthesis' is not of type 'NewLine'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_IgnoreSingleLine(self) -> None:
		self.assertTrue(AssociationListStyle(ignoreSingleLine=True).IgnoreSingleLine)

	def test_IgnoreSingleLine_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			AssociationListStyle(ignoreSingleLine=None)

		self.assertEqual("Parameter 'ignoreSingleLine' is None.", str(context.exception))

	def test_IgnoreSingleLine_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			AssociationListStyle(ignoreSingleLine="yes")

		self.assertEqual("Parameter 'ignoreSingleLine' is not of type 'bool'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class ListStyles(Testcase):
	def test_Abstract(self) -> None:
		"""Only the interface list style and the association list style are instantiated."""
		with self.assertRaises(AbstractClassError):
			ListStyle(NewLine.Add, False)


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
		"""The writer handles the events of every model class with a walk, except those written by their children alone."""
		classNames =        {name[len("Depart"):] for name in dir(Visitor) if name.startswith("Depart")}
		writtenByChildren = {
			"Symbol", "SimpleAggregateElement", "RangedAggregateElement", "NamedAggregateElement",
			"ConstrainedScalarSubtypeSymbol", "ConstrainedArraySubtypeSymbol", "ConstrainedRecordSubtypeSymbol", "Document",
			"WaveformElement", "ConditionalWaveform", "SelectedWaveform", "RangedChoice", "RangedGenerateChoice",
			"ConditionalExpression", "SelectedExpression", "IndexedName", "ParenthesisName", "TypeConversion"
		}
		for className in classNames - writtenByChildren:
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
		subtype = ParserCompositeSubtypeSymbol(SimpleName("unsigned"))

		with self.assertRaises(NotImplementedError) as context:
			VHDLWriter().Format(subtype)

		self.assertEqual("Model element has no walk for a visitor.", str(context.exception))

	def test_ParserSubclass(self) -> None:
		name = ParserName("clk")

		self.assertEqual("clk", VHDLWriter().Format(name))

	def test_ParserSubclass_Operator(self) -> None:
		"""A parser's subclass is the same operator as its model class, so the chain needs no parentheses."""
		expression = AndExpression(ParserAndExpression(_object("a"), _object("b")), _object("c"))

		self.assertEqual("a and b and c", VHDLWriter().Format(expression))


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

	def test_Operator(self) -> None:
		expression = ModuloExpression(_object("a"), _object("b"))

		self.assertEqual("a MOD b", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(expression))

	def test_UnaryOperator(self) -> None:
		expression = InverseExpression(OrExpression(_object("a"), _object("b")))

		self.assertEqual("NOT (a OR b)", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(expression))

	def test_Identifier(self) -> None:
		"""Identifiers keep their letter case."""
		self.assertEqual("Idle", VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(EnumerationLiteral("Idle")))
