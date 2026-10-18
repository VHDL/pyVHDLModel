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
"""Tests for traversing the model's parent-chain hierarchy, spanning multiple classes/levels of the model."""
from pyTooling.Testing       import Testcase

from pyVHDLModel             import Design, Library, VHDLModelException
from pyVHDLModel.DesignUnit  import Entity, Architecture, Package
from pyVHDLModel.Symbol      import EntitySymbol
from pyVHDLModel.Name        import SimpleName


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class GetAncestor(Testcase):
	def test_AncestorExists(self) -> None:
		entity = Entity("entity_1")
		architecture = Architecture("arch_1", EntitySymbol(SimpleName("entity_1")), parent=entity)

		self.assertIs(entity, architecture.GetAncestor(Entity))

	def test_AncestorIsSelfsType(self) -> None:
		design = Design()
		library = Library("lib_1")
		design.AddLibrary(library)
		entity = Entity("entity_1", parent=library)

		self.assertIs(library, entity.GetAncestor(Library))
		self.assertIs(design, entity.GetAncestor(Design))

	def test_AncestorDoesNotExist_RaisesVHDLModelException(self) -> None:
		"""Previously raised an unguarded ``AttributeError`` once the root of the model was reached without a match."""
		entity = Entity("entity_1")

		with self.assertRaises(VHDLModelException):
			entity.GetAncestor(Package)


class AllowBlackBox(Testcase):
	def test_LocalValueIsUsed(self) -> None:
		entity = Entity("entity_1", allowBlackbox=True)

		self.assertTrue(entity.AllowBlackbox)

	def test_InheritsFromParent(self) -> None:
		library = Library("lib_1", allowBlackbox=False)
		entity = Entity("entity_1", parent=library)

		self.assertFalse(entity.AllowBlackbox)

	def test_LocalValueOverridesParent(self) -> None:
		library = Library("lib_1", allowBlackbox=False)
		entity = Entity("entity_1", allowBlackbox=True, parent=library)

		self.assertTrue(entity.AllowBlackbox)
		self.assertFalse(library.AllowBlackbox)

	def test_NoLocalValueAndNoParent_RaisesVHDLModelException(self) -> None:
		"""Previously raised an unguarded ``AttributeError`` when no parent was available to inherit from."""
		entity = Entity("entity_1")

		with self.assertRaises(VHDLModelException):
			entity.AllowBlackbox
