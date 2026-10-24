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
#
"""
Split tests for record element declarations (:mod:`pyVHDLModel.Type`).

``a, b : bit;`` in a record type becomes ``a : bit; b : bit;``.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Exception  import NotAChildError
from pyVHDLModel.Type       import RecordType, RecordTypeElement

from tests.unit             import _subtypeSymbol
from tests.unit.Split       import _formatted


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class RecordTypeElements(Testcase):
	def test_Split(self) -> None:
		subtype = _subtypeSymbol("bit")
		original = RecordTypeElement(("a", "B"), subtype, "Documentation.")

		declarations = original.Split()

		self.assertEqual(2, len(declarations))
		self.assertIs(original, declarations[0])
		self.assertTupleEqual(("a", ), declarations[0].Identifiers)
		self.assertTupleEqual(("B", ), declarations[1].Identifiers)
		self.assertTupleEqual(("b", ), declarations[1].NormalizedIdentifiers)
		self.assertIs(RecordTypeElement, type(declarations[1]))
		self.assertIsNone(declarations[1].Parent)
		self.assertEqual("Documentation.", declarations[1].Documentation)
		self.assertIs(subtype, original.Subtype)
		self.assertIsNot(subtype, declarations[1].Subtype)
		self.assertIs(declarations[1], declarations[1].Subtype.Parent)
		self.assertListEqual(["a : bit;\n", "B : bit;\n"], _formatted(declarations))

	def test_Split_OneIdentifier(self) -> None:
		original = RecordTypeElement(("a", ), _subtypeSymbol("bit"))

		self.assertTupleEqual((original, ), original.Split())

	def test_Split_RecordType(self) -> None:
		first = RecordTypeElement(("first", ), _subtypeSymbol("bit"))
		original = RecordTypeElement(("a", "b", "c"), _subtypeSymbol("bit"))
		last = RecordTypeElement(("last", ), _subtypeSymbol("bit"))
		recordType = RecordType("frame", [first, original, last])

		declarations = original.Split()

		self.assertListEqual([first, *declarations, last], recordType.Elements)
		for declaration in declarations:
			self.assertIs(recordType, declaration.Parent)

	def test_Split_NotAChild(self) -> None:
		original = RecordTypeElement(("a", "b"), _subtypeSymbol("bit"))
		recordType = RecordType("frame")
		original.Parent = recordType

		with self.assertRaises(NotAChildError) as context:
			original.Split()

		self.assertEqual("RecordTypeElement 'a, b' is not an element of this RecordType.", str(context.exception))
		self.assertTupleEqual(("a", "b"), original.Identifiers)


class SplitElement(Testcase):
	def test_Split(self) -> None:
		original = RecordTypeElement(("a", "b"), _subtypeSymbol("bit"))
		recordType = RecordType("frame", [original])

		declarations = recordType.SplitElement(original)

		self.assertIs(original, declarations[0])
		self.assertListEqual(list(declarations), recordType.Elements)
		self.assertIs(recordType, declarations[1].Parent)

	def test_Split_OneIdentifier(self) -> None:
		original = RecordTypeElement(("a", ), _subtypeSymbol("bit"))
		recordType = RecordType("frame", [original])

		self.assertTupleEqual((original, ), recordType.SplitElement(original))

	def test_Split_None(self) -> None:
		recordType = RecordType("frame")

		with self.assertRaises(ValueError) as context:
			recordType.SplitElement(None)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_Split_WrongType(self) -> None:
		recordType = RecordType("frame")

		with self.assertRaises(TypeError) as context:
			recordType.SplitElement(_subtypeSymbol("bit"))

		self.assertEqual("Parameter 'element' is not of type 'RecordTypeElement'.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Symbol.SimpleSubtypeSymbol'."], context.exception.__notes__)

	def test_Split_NotAChild(self) -> None:
		original = RecordTypeElement(("a", "b"), _subtypeSymbol("bit"))
		recordType = RecordType("frame")

		with self.assertRaises(NotAChildError) as context:
			recordType.SplitElement(original)

		self.assertEqual("RecordTypeElement 'a, b' is not an element of this RecordType.", str(context.exception))
