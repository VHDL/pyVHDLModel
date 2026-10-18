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
"""Tests for the walk of expressions and ranges (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Expression import AdditionExpression, MultiplyExpression, IntegerLiteral, WhenElseExpression
from pyVHDLModel.Expression import Aggregate, IndexedAggregateElement, OthersAggregateElement

from tests.unit.Visitor     import Recorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Walks(Testcase):
	def test_BinaryExpression(self) -> None:
		"""Visit, left operand, operator, right operand, depart - nested expressions likewise."""
		a =        IntegerLiteral(1)
		b =        IntegerLiteral(2)
		c =        IntegerLiteral(3)
		product =  MultiplyExpression(b, c)
		addition = AdditionExpression(a, product)
		recorder = Recorder()

		addition.Visit(recorder)

		self.assertEqual([
			("VisitAddingExpression",       addition),
			("VisitIntegerLiteral",         a),
			("DepartIntegerLiteral",        a),
			("VisitOperator",               addition),
			("VisitMultiplyingExpression",  product),
			("VisitIntegerLiteral",         b),
			("DepartIntegerLiteral",        b),
			("VisitOperator",               product),
			("VisitIntegerLiteral",         c),
			("DepartIntegerLiteral",        c),
			("DepartMultiplyingExpression", product),
			("DepartAddingExpression",      addition),
		], recorder.Events)

	def test_WhenElseExpression(self) -> None:
		value =       IntegerLiteral(1)
		condition =   IntegerLiteral(2)
		alternative = IntegerLiteral(3)
		expression =  WhenElseExpression(value, condition, alternative)
		recorder =    Recorder()

		expression.Visit(recorder)

		self.assertEqual([
			("VisitWhenElseExpression",  expression),
			("VisitIntegerLiteral",      value),
			("DepartIntegerLiteral",     value),
			("VisitWhen",                expression),
			("VisitIntegerLiteral",      condition),
			("DepartIntegerLiteral",     condition),
			("VisitElse",                expression),
			("VisitIntegerLiteral",      alternative),
			("DepartIntegerLiteral",     alternative),
			("DepartWhenElseExpression", expression),
		], recorder.Events)

	def test_Aggregate(self) -> None:
		index =     IntegerLiteral(0)
		first =     IntegerLiteral(1)
		second =    IntegerLiteral(2)
		indexed =   IndexedAggregateElement(index, first)
		others =    OthersAggregateElement(second)
		aggregate = Aggregate([indexed, others])
		recorder =  Recorder()

		aggregate.Visit(recorder)

		self.assertEqual([
			("VisitAggregate",                aggregate),
			("VisitIndexedAggregateElement",  indexed),
			("VisitIntegerLiteral",           index),
			("DepartIntegerLiteral",          index),
			("VisitArrow",                    indexed),
			("VisitIntegerLiteral",           first),
			("DepartIntegerLiteral",          first),
			("DepartIndexedAggregateElement", indexed),
			("VisitComma",                    aggregate),
			("VisitOthersAggregateElement",   others),
			("VisitIntegerLiteral",           second),
			("DepartIntegerLiteral",          second),
			("DepartOthersAggregateElement",  others),
			("DepartAggregate",               aggregate),
		], recorder.Events)

	def test_SimpleRange(self) -> None:
		left =     IntegerLiteral(7)
		right =    IntegerLiteral(0)
		rng =      SimpleRange(left, right, Direction.DownTo)
		recorder = Recorder()

		rng.Visit(recorder)

		self.assertEqual([
			("VisitSimpleRange",     rng),
			("VisitIntegerLiteral",  left),
			("DepartIntegerLiteral", left),
			("VisitDirection",       rng),
			("VisitIntegerLiteral",  right),
			("DepartIntegerLiteral", right),
			("DepartSimpleRange",    rng),
		], recorder.Events)
