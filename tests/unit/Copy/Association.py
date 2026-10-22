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
Copy tests for association items (:mod:`pyVHDLModel.Association`).
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Association as AssociationModule
from pyVHDLModel.Association     import GenericAssociationItem, PortAssociationItem, ParameterAssociationItem
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, OpenName
from pyVHDLModel.Symbol          import Symbol, PossibleReference

from tests.unit                  import _Element
from tests.unit.Copy             import _object, _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""Every association item class has a ``Copy()`` calling its own constructor."""
		classes = _concreteModelClasses(AssociationModule)

		self.assertIn(PortAssociationItem, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class AssociationItems(Testcase):
	def test_Copy(self) -> None:
		for cls in (GenericAssociationItem, PortAssociationItem, ParameterAssociationItem):
			with self.subTest(cls.__name__):
				formal = Symbol(SimpleName("BITS"), PossibleReference.Constant)
				actual = IntegerLiteral(8)
				original = cls(formal, actual)
				original.Parent = _Element()

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertIsNot(formal, copy.Formal)
				self.assertIsNot(formal.Name, copy.Formal.Name)
				self.assertIsNot(actual, copy.Actual)
				self.assertEqual("BITS => 8", VHDLWriter().Format(copy))

	def test_Copy_Positional(self) -> None:
		original = PortAssociationItem(None, _object("Clock"))

		copy = original.Copy()

		self.assertIsNone(copy.Formal)
		self.assertIsNot(original.Actual, copy.Actual)
		self.assertEqual("Clock", VHDLWriter().Format(copy))

	def test_Copy_Open(self) -> None:
		original = PortAssociationItem(_object("Q"), OpenName())

		copy = original.Copy()

		self.assertIsNot(original.Actual, copy.Actual)
		self.assertEqual("Q => open", VHDLWriter().Format(copy))

	def test_Copy_WithoutActual(self) -> None:
		"""An association item without an actual (``None``) keeps it."""
		original = PortAssociationItem(_object("Q"), None)

		copy = original.Copy()

		self.assertIsNone(copy.Actual)
