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
"""Tests for the walk of type declarations (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Expression import IntegerLiteral, PhysicalIntegerLiteral, EnumerationLiteral, AscendingRangeExpression
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Type       import AnonymousType, EnumeratedType, PhysicalType, ArrayType, RecordTypeElement, RecordType
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol

from tests.unit.Visitor     import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Types(Testcase):
	def test_Incomplete(self) -> None:
		declaration = AnonymousType("node")
		recorder =    FullRecorder()

		declaration.Visit(recorder)

		self.assertEqual([("VisitAnonymousType", declaration), ("DepartAnonymousType", declaration)], recorder.Events)

	def test_Enumerated(self) -> None:
		first =          EnumerationLiteral("Idle")
		second =         EnumerationLiteral("Busy")
		enumeratedType = EnumeratedType("state", [first, second])
		recorder =       FullRecorder()

		enumeratedType.Visit(recorder)

		self.assertEqual([
			("VisitEnumeratedType",      enumeratedType),
			("VisitEnumerationLiteral",  first),
			("DepartEnumerationLiteral", first),
			("VisitElementSeparator",    enumeratedType),
			("VisitEnumerationLiteral",  second),
			("DepartEnumerationLiteral", second),
			("DepartEnumeratedType",     enumeratedType),
		], recorder.Events)

	def test_Physical(self) -> None:
		"""A secondary unit declaration reports its identifier as additional argument."""
		left =         IntegerLiteral(0)
		right =        IntegerLiteral(1000)
		rng =          AscendingRangeExpression(left, right)
		value =        PhysicalIntegerLiteral(1000, "um")
		physicalType = PhysicalType("distance", rng, "um", [("mm", value)])
		recorder =     FullRecorder()

		physicalType.Visit(recorder)

		self.assertEqual([
			("VisitPhysicalType",              physicalType),
			("VisitRangeExpression",           rng),
			("VisitIntegerLiteral",            left),
			("DepartIntegerLiteral",           left),
			("VisitDirection",                 rng),
			("VisitIntegerLiteral",            right),
			("DepartIntegerLiteral",           right),
			("DepartRangeExpression",          rng),
			("VisitUnits",                     physicalType),
			("VisitSecondaryUnitDeclaration",  physicalType, "mm"),
			("VisitPhysicalIntegerLiteral",    value),
			("DepartPhysicalIntegerLiteral",   value),
			("DepartSecondaryUnitDeclaration", physicalType, "mm"),
			("DepartPhysicalType",             physicalType),
		], recorder.Events)

	def test_Array(self) -> None:
		"""A type mark as index is followed by the box event."""
		index =     SimpleSubtypeSymbol(SimpleName("natural"))
		element =   SimpleSubtypeSymbol(SimpleName("bit"))
		arrayType = ArrayType("bits", [index], element)
		recorder =  FullRecorder()

		arrayType.Visit(recorder)

		self.assertEqual([
			("VisitArrayType",        arrayType),
			("VisitIndexConstraint",  arrayType),
			("VisitSymbol",           index),
			("VisitSimpleName",       index.Name),
			("DepartSimpleName",      index.Name),
			("DepartSymbol",          index),
			("VisitBox",              arrayType),
			("DepartIndexConstraint", arrayType),
			("VisitOf",               arrayType),
			("VisitSymbol",           element),
			("VisitSimpleName",       element.Name),
			("DepartSimpleName",      element.Name),
			("DepartSymbol",          element),
			("DepartArrayType",       arrayType),
		], recorder.Events)

	def test_Array_Constrained(self) -> None:
		left =      IntegerLiteral(0)
		right =     IntegerLiteral(3)
		rng =       AscendingRangeExpression(left, right)
		arrayType = ArrayType("memory", [rng], SimpleSubtypeSymbol(SimpleName("bit")))
		recorder =  FullRecorder()

		arrayType.Visit(recorder)

		self.assertEqual(
			["VisitArrayType", "VisitIndexConstraint", "VisitRangeExpression", "VisitIntegerLiteral", "DepartIntegerLiteral",
			 "VisitDirection", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartRangeExpression",
			 "DepartIndexConstraint", "VisitOf", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			 "DepartArrayType"],
			[event[0] for event in recorder.Events]
		)

	def test_Record(self) -> None:
		subtype =    SimpleSubtypeSymbol(SimpleName("bit"))
		element =    RecordTypeElement(["valid"], subtype)
		recordType = RecordType("frame", [element])
		recorder =   FullRecorder()

		recordType.Visit(recorder)

		self.assertEqual([
			("VisitRecordType",         recordType),
			("VisitRecordTypeElement",  element),
			("VisitSymbol",             subtype),
			("VisitSimpleName",         subtype.Name),
			("DepartSimpleName",        subtype.Name),
			("DepartSymbol",            subtype),
			("DepartRecordTypeElement", element),
			("DepartRecordType",        recordType),
		], recorder.Events)
