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
"""Tests for the walk of subtype indications and object declarations (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Object     import Constant, DeferredConstant, Variable, SharedVariable, Signal, File
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, \
                                   ConstrainedRecordSubtypeSymbol, RecordElementSymbol, ArrayElementConstraint, \
                                   RecordElementConstraint

from tests.unit.Visitor     import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SubtypeIndications(Testcase):
	def test_Scalar(self) -> None:
		name =     SimpleName("integer")
		left =     IntegerLiteral(0)
		right =    IntegerLiteral(7)
		rng =      SimpleRange(left, right, Direction.To)
		symbol =   ConstrainedScalarSubtypeSymbol(name, rng)
		recorder = FullRecorder()

		symbol.Visit(recorder)

		self.assertEqual([
			("VisitConstrainedScalarSubtypeSymbol",  symbol),
			("VisitSimpleName",                      name),
			("DepartSimpleName",                     name),
			("VisitRangeConstraint",                 symbol),
			("VisitSimpleRange",                     rng),
			("VisitIntegerLiteral",                  left),
			("DepartIntegerLiteral",                 left),
			("VisitDirection",                       rng),
			("VisitIntegerLiteral",                  right),
			("DepartIntegerLiteral",                 right),
			("DepartSimpleRange",                    rng),
			("DepartRangeConstraint",                symbol),
			("DepartConstrainedScalarSubtypeSymbol", symbol),
		], recorder.Events)

	def test_Array(self) -> None:
		name =     SimpleName("matrix")
		first =    SimpleSubtypeSymbol(SimpleName("state"))
		second =   SimpleSubtypeSymbol(SimpleName("index"))
		symbol =   ConstrainedArraySubtypeSymbol(name, [first, second])
		recorder = FullRecorder()

		symbol.Visit(recorder)

		self.assertEqual([
			("VisitConstrainedArraySubtypeSymbol",  symbol),
			("VisitSimpleName",                     name),
			("DepartSimpleName",                    name),
			("VisitIndexConstraint",                symbol),
			("VisitSymbol",                         first),
			("VisitSimpleName",                     first.Name),
			("DepartSimpleName",                    first.Name),
			("DepartSymbol",                        first),
			("VisitElementSeparator",               symbol),
			("VisitSymbol",                         second),
			("VisitSimpleName",                     second.Name),
			("DepartSimpleName",                    second.Name),
			("DepartSymbol",                        second),
			("DepartIndexConstraint",               symbol),
			("DepartConstrainedArraySubtypeSymbol", symbol),
		], recorder.Events)

	def test_Record(self) -> None:
		"""Each record element constraint is the element's name followed by its element constraint."""
		name =       SimpleName("frame")
		element =    RecordElementSymbol(SimpleName("data"))
		index =      SimpleSubtypeSymbol(SimpleName("byte_range"))
		constraint = ArrayElementConstraint([index])
		symbol =     ConstrainedRecordSubtypeSymbol(name, {element: constraint})
		recorder =   FullRecorder()

		symbol.Visit(recorder)

		self.assertEqual([
			("VisitConstrainedRecordSubtypeSymbol",  symbol),
			("VisitSimpleName",                      name),
			("DepartSimpleName",                     name),
			("VisitRecordConstraint",                symbol),
			("VisitSymbol",                          element),
			("VisitSimpleName",                      element.Name),
			("DepartSimpleName",                     element.Name),
			("DepartSymbol",                         element),
			("VisitArrayElementConstraint",          constraint),
			("VisitIndexConstraint",                 constraint),
			("VisitSymbol",                          index),
			("VisitSimpleName",                      index.Name),
			("DepartSimpleName",                     index.Name),
			("DepartSymbol",                         index),
			("DepartIndexConstraint",                constraint),
			("DepartArrayElementConstraint",         constraint),
			("DepartRecordConstraint",               symbol),
			("DepartConstrainedRecordSubtypeSymbol", symbol),
		], recorder.Events)

	def test_Record_Elements(self) -> None:
		"""Two record element constraints are separated; an array element constraint separates its dimensions."""
		name =       SimpleName("rec_t")
		data =       RecordElementSymbol(SimpleName("data"))
		byte =       SimpleSubtypeSymbol(SimpleName("byte_range"))
		dataRange =  ArrayElementConstraint([byte])
		matrix =     RecordElementSymbol(SimpleName("m"))
		rows =       SimpleSubtypeSymbol(SimpleName("rows"))
		columns =    SimpleSubtypeSymbol(SimpleName("columns"))
		matrixSize = ArrayElementConstraint([rows, columns])
		symbol =     ConstrainedRecordSubtypeSymbol(name, {data: dataRange, matrix: matrixSize})
		recorder =   FullRecorder()

		symbol.Visit(recorder)

		self.assertEqual([
			("VisitConstrainedRecordSubtypeSymbol",  symbol),
			("VisitSimpleName",                      name),
			("DepartSimpleName",                     name),
			("VisitRecordConstraint",                symbol),
			("VisitSymbol",                          data),
			("VisitSimpleName",                      data.Name),
			("DepartSimpleName",                     data.Name),
			("DepartSymbol",                         data),
			("VisitArrayElementConstraint",          dataRange),
			("VisitIndexConstraint",                 dataRange),
			("VisitSymbol",                          byte),
			("VisitSimpleName",                      byte.Name),
			("DepartSimpleName",                     byte.Name),
			("DepartSymbol",                         byte),
			("DepartIndexConstraint",                dataRange),
			("DepartArrayElementConstraint",         dataRange),
			("VisitElementSeparator",                symbol),
			("VisitSymbol",                          matrix),
			("VisitSimpleName",                      matrix.Name),
			("DepartSimpleName",                     matrix.Name),
			("DepartSymbol",                         matrix),
			("VisitArrayElementConstraint",          matrixSize),
			("VisitIndexConstraint",                 matrixSize),
			("VisitSymbol",                          rows),
			("VisitSimpleName",                      rows.Name),
			("DepartSimpleName",                     rows.Name),
			("DepartSymbol",                         rows),
			("VisitElementSeparator",                matrixSize),
			("VisitSymbol",                          columns),
			("VisitSimpleName",                      columns.Name),
			("DepartSimpleName",                     columns.Name),
			("DepartSymbol",                         columns),
			("DepartIndexConstraint",                matrixSize),
			("DepartArrayElementConstraint",         matrixSize),
			("DepartRecordConstraint",               symbol),
			("DepartConstrainedRecordSubtypeSymbol", symbol),
		], recorder.Events)

	def test_Record_Nested(self) -> None:
		"""A nested record element constraint walks its own record constraint."""
		name =        SimpleName("rec_t")
		inner =       RecordElementSymbol(SimpleName("inner"))
		field =       RecordElementSymbol(SimpleName("field"))
		nibble =      SimpleSubtypeSymbol(SimpleName("nibble_range"))
		fieldRange =  ArrayElementConstraint([nibble])
		innerRecord = RecordElementConstraint({field: fieldRange})
		symbol =      ConstrainedRecordSubtypeSymbol(name, {inner: innerRecord})
		recorder =    FullRecorder()

		symbol.Visit(recorder)

		self.assertEqual([
			("VisitConstrainedRecordSubtypeSymbol",  symbol),
			("VisitSimpleName",                      name),
			("DepartSimpleName",                     name),
			("VisitRecordConstraint",                symbol),
			("VisitSymbol",                          inner),
			("VisitSimpleName",                      inner.Name),
			("DepartSimpleName",                     inner.Name),
			("DepartSymbol",                         inner),
			("VisitRecordElementConstraint",         innerRecord),
			("VisitRecordConstraint",                innerRecord),
			("VisitSymbol",                          field),
			("VisitSimpleName",                      field.Name),
			("DepartSimpleName",                     field.Name),
			("DepartSymbol",                         field),
			("VisitArrayElementConstraint",          fieldRange),
			("VisitIndexConstraint",                 fieldRange),
			("VisitSymbol",                          nibble),
			("VisitSimpleName",                      nibble.Name),
			("DepartSimpleName",                     nibble.Name),
			("DepartSymbol",                         nibble),
			("DepartIndexConstraint",                fieldRange),
			("DepartArrayElementConstraint",         fieldRange),
			("DepartRecordConstraint",               innerRecord),
			("DepartRecordElementConstraint",        innerRecord),
			("DepartRecordConstraint",               symbol),
			("DepartConstrainedRecordSubtypeSymbol", symbol),
		], recorder.Events)


class Objects(Testcase):
	def test_Constant(self) -> None:
		"""A default expression follows the variable assignment delimiter event."""
		subtype =  SimpleSubtypeSymbol(SimpleName("natural"))
		default =  IntegerLiteral(0)
		constant = Constant(["count"], subtype, default)
		recorder = FullRecorder()

		constant.Visit(recorder)

		self.assertEqual([
			("VisitConstant",           constant),
			("VisitSymbol",             subtype),
			("VisitSimpleName",         subtype.Name),
			("DepartSimpleName",        subtype.Name),
			("DepartSymbol",            subtype),
			("VisitVariableAssignment", constant),
			("VisitIntegerLiteral",     default),
			("DepartIntegerLiteral",    default),
			("VisitTerminator",         constant),
			("DepartConstant",          constant),
		], recorder.Events)

	def test_DeferredConstant(self) -> None:
		subtype =  SimpleSubtypeSymbol(SimpleName("natural"))
		constant = DeferredConstant(["count"], subtype)
		recorder = FullRecorder()

		constant.Visit(recorder)

		self.assertEqual([
			("VisitDeferredConstant",  constant),
			("VisitSymbol",            subtype),
			("VisitSimpleName",        subtype.Name),
			("DepartSimpleName",       subtype.Name),
			("DepartSymbol",           subtype),
			("VisitTerminator",        constant),
			("DepartDeferredConstant", constant),
		], recorder.Events)

	def test_Variable(self) -> None:
		default =  IntegerLiteral(0)
		variable = Variable(["count"], SimpleSubtypeSymbol(SimpleName("natural")), default)
		recorder = FullRecorder()

		variable.Visit(recorder)

		self.assertEqual(
			["VisitVariable", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "VisitVariableAssignment",
			 "VisitIntegerLiteral", "DepartIntegerLiteral", "VisitTerminator", "DepartVariable"],
			[event[0] for event in recorder.Events]
		)

	def test_Variable_WithoutDefault(self) -> None:
		variable = Variable(["count"], SimpleSubtypeSymbol(SimpleName("natural")))
		recorder = FullRecorder()

		variable.Visit(recorder)

		self.assertEqual(
			["VisitVariable", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "VisitTerminator",
			 "DepartVariable"],
			[event[0] for event in recorder.Events]
		)

	def test_SharedVariable(self) -> None:
		variable = SharedVariable(["counter"], SimpleSubtypeSymbol(SimpleName("counter_t")))
		recorder = FullRecorder()

		variable.Visit(recorder)

		self.assertEqual(
			["VisitSharedVariable", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			 "VisitTerminator", "DepartSharedVariable"],
			[event[0] for event in recorder.Events]
		)

	def test_Signal(self) -> None:
		default =  IntegerLiteral(0)
		signal =   Signal(["count"], SimpleSubtypeSymbol(SimpleName("natural")), default)
		recorder = FullRecorder()

		signal.Visit(recorder)

		self.assertEqual(
			["VisitSignal", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "VisitVariableAssignment",
			 "VisitIntegerLiteral", "DepartIntegerLiteral", "VisitTerminator", "DepartSignal"],
			[event[0] for event in recorder.Events]
		)

	def test_File(self) -> None:
		file =     File(["input"], SimpleSubtypeSymbol(SimpleName("text")))
		recorder = FullRecorder()

		file.Visit(recorder)

		self.assertEqual(
			["VisitFile", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol", "VisitTerminator",
			 "DepartFile"],
			[event[0] for event in recorder.Events]
		)
