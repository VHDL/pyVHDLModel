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
Copy tests for record type elements (:mod:`pyVHDLModel.Type`).
"""
from pyTooling.Testing import Testcase

from pyVHDLModel.Type  import RecordTypeElement

from tests.unit        import _Element, _subtypeSymbol
from tests.unit.Copy   import _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""The record type element class has a ``Copy()`` calling its own constructor."""
		self.assertListEqual([], _copyAboveConstructor((RecordTypeElement, )))


class RecordTypeElements(Testcase):
	def test_Copy(self) -> None:
		subtype = _subtypeSymbol("bit")
		original = RecordTypeElement(("a", "b"), subtype, "Documentation.", _Element())

		copy = original.Copy()

		self.assertIs(RecordTypeElement, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertTupleEqual(("a", "b"), copy.Identifiers)
		self.assertEqual("Documentation.", copy.Documentation)
		self.assertIsNot(subtype, copy.Subtype)
		self.assertIsNot(subtype.Name, copy.Subtype.Name)
		self.assertEqual("bit", copy.Subtype.Name.Identifier)
