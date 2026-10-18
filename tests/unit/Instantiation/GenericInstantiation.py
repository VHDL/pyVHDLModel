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
"""Tests for pyVHDLModel.Instantiation (VHDL-2008 generic subprogram/package instantiation)."""
from pyTooling.Testing         import Testcase

from pyVHDLModel             import VHDLModelException
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SubprogramReferenceSymbol, PackageReferenceSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.DesignUnit  import Package, Component
from pyVHDLModel.Instantiation import ProcedureInstantiation, FunctionInstantiation, PackageInstantiation


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ProcedureInstantiations(Testcase):
	"""``procedure p is new q generic map (...);``"""

	def test_Construction(self) -> None:
		reference = SubprogramReferenceSymbol(SimpleName("q"))
		generic = GenericAssociationItem(SimpleName("T"), IntegerLiteral(1))
		instantiation = ProcedureInstantiation("p", reference, [generic])

		self.assertEqual("p", instantiation.Identifier)
		self.assertIs(reference, instantiation.SubprogramReference)
		self.assertIs(instantiation, reference.Parent)
		self.assertEqual(1, len(instantiation.GenericAssociationItems))
		self.assertIs(instantiation, generic.Parent)

	def test_NoGenericAssociations(self) -> None:
		instantiation = ProcedureInstantiation("p", SubprogramReferenceSymbol(SimpleName("q")))

		self.assertEqual(0, len(instantiation.GenericAssociationItems))


class FunctionInstantiations(Testcase):
	"""``function f is new g generic map (...);`` - ``ReturnType`` is deliberately ``Nullable``, see
	the class's own docstring (never resolvable at the parse-only level, a genuinely unresolved
	forward reference like ``Symbol.Reference``, not a workaround)."""

	def test_Construction(self) -> None:
		reference = SubprogramReferenceSymbol(SimpleName("g"))
		instantiation = FunctionInstantiation("f", reference)

		self.assertIs(reference, instantiation.SubprogramReference)
		self.assertIsNone(instantiation.ReturnType)
		self.assertTrue(instantiation.IsPure)

	def test_Impure(self) -> None:
		instantiation = FunctionInstantiation("f", SubprogramReferenceSymbol(SimpleName("g")), isPure=False)

		self.assertFalse(instantiation.IsPure)


class PackageInstantiations(Testcase):
	"""``package p is new q generic map (...);``"""

	def test_Construction(self) -> None:
		reference = PackageReferenceSymbol(SimpleName("q"))
		generic = GenericAssociationItem(SimpleName("T"), IntegerLiteral(1))
		instantiation = PackageInstantiation("p", reference, genericAssociationItems=[generic])

		self.assertIs(reference, instantiation.PackageReference)
		self.assertIs(instantiation, reference.Parent)
		self.assertEqual(1, len(instantiation.GenericAssociationItems))
		self.assertIs(instantiation, generic.Parent)

	def test_Instantiate_UnlinkedReference_Raises(self) -> None:
		reference = PackageReferenceSymbol(SimpleName("q"))
		instantiation = PackageInstantiation("p", reference)

		with self.assertRaises(VHDLModelException):
			instantiation.Instantiate()

	def test_Instantiate_CopiesComponentsFromGenericPackage(self) -> None:
		component = Component("comp")
		genericPackage = Package("q", declaredItems=[component])
		genericPackage.IndexDeclaredItems()

		reference = PackageReferenceSymbol(SimpleName("q"))
		reference.Package = genericPackage
		instantiation = PackageInstantiation("p", reference)

		instantiation.Instantiate()

		self.assertIs(component, instantiation.Components["comp"])
