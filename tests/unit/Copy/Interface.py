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
Copy tests for interface items and mode view elements (:mod:`pyVHDLModel.Interface`).
"""
from pyTooling.Testing           import Testcase

from pyVHDLModel                 import Interface as InterfaceModule
from pyVHDLModel.Base            import Mode
from pyVHDLModel.DesignUnit      import Entity
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Interface       import SimpleModeViewElement, CompositeModeViewElement, GenericConstantInterfaceItem, \
                                        GenericTypeInterfaceItem, GenericProcedureInterfaceItem, \
                                        GenericFunctionInterfaceItem, GenericPackageInterfaceItem, \
                                        PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                        ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                        ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                        ParameterFileInterfaceItem, ModeViewDeclaration, InterfaceGroup, GenericGroup, \
                                        PortGroup, ParameterGroup
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Subprogram      import Procedure
from pyVHDLModel.Symbol          import ModeViewSymbol

from tests.unit                  import _Element, _subtypeSymbol
from tests.unit.Copy             import _concreteModelClasses, _copyAboveConstructor


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _DerivedPortSimpleSignalInterfaceItem(PortSimpleSignalInterfaceItem):
	"""A port of a class derived outside pyVHDLModel, with the constructor of its base-class."""


class CopyMethods(Testcase):
	def test_Constructor(self) -> None:
		"""
		Every interface item and mode view element class has a ``Copy()`` calling its own constructor.

		A single declaration is a view of one identifier of its declaration, created when iterated, and has no copy.
		"""
		withoutCopy = (ModeViewDeclaration, InterfaceGroup, GenericGroup, PortGroup, ParameterGroup)
		classes = [
			cls for cls in _concreteModelClasses(InterfaceModule)
			if cls not in withoutCopy and not issubclass(cls, InterfaceModule.SingleDeclarationMixin)
		]

		self.assertIn(ParameterFileInterfaceItem, classes)
		self.assertListEqual([], _copyAboveConstructor(classes))


class InterfaceItemsWithMode(Testcase):
	def test_Copy(self) -> None:
		for cls in (
			GenericConstantInterfaceItem,
			PortSimpleSignalInterfaceItem,
			ParameterConstantInterfaceItem,
			ParameterVariableInterfaceItem,
			ParameterSimpleSignalInterfaceItem
		):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("positive")
				defaultExpression = IntegerLiteral(8)
				original = cls(("a", "b"), Mode.In, subtype, defaultExpression, "Documentation.", _Element())

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNot(original, copy)
				self.assertIsNone(copy.Parent)
				self.assertTupleEqual(("a", "b"), copy.Identifiers)
				self.assertIs(Mode.In, copy.Mode)
				self.assertEqual("Documentation.", copy.Documentation)
				self.assertIsNot(subtype, copy.Subtype)
				self.assertIsNot(subtype.Name, copy.Subtype.Name)
				self.assertIsNot(defaultExpression, copy.DefaultExpression)
				self.assertIs(copy, copy.DefaultExpression.Parent)
				self.assertEqual("8", VHDLWriter().Format(copy.DefaultExpression))
				self.assertEqual(str(original), str(copy))

	def test_Copy_WithoutDefaultExpression(self) -> None:
		original = PortSimpleSignalInterfaceItem(("Clock", ), Mode.In, _subtypeSymbol("std_logic"))

		copy = original.Copy()

		self.assertIsNone(copy.DefaultExpression)

	def test_Copy_Derived(self) -> None:
		"""A copy of a port of a derived class is an instance of that class."""
		original = _DerivedPortSimpleSignalInterfaceItem(("Clock", ), Mode.In, _subtypeSymbol("std_logic"))

		copy = original.Copy()

		self.assertIs(_DerivedPortSimpleSignalInterfaceItem, type(copy))
		self.assertEqual("signal Clock : in std_logic?", str(copy))


class Groups(Testcase):
	def test_Generic(self) -> None:
		"""A copy of a generic is in no generic group."""
		original = GenericConstantInterfaceItem(("WIDTH", ), Mode.Default, _subtypeSymbol("positive"))
		entity =   Entity("e", genericItems=[original])

		copy = original.Copy()

		self.assertIs(entity.GenericGroups[0], original.Group)
		self.assertIsNone(copy.Group)

	def test_Port(self) -> None:
		"""A copy of a port is in no port group."""
		original = PortSimpleSignalInterfaceItem(("Clock", ), Mode.In, _subtypeSymbol("std_logic"))
		entity =   Entity("e", portItems=[original])

		copy = original.Copy()

		self.assertIs(entity.PortGroups[0], original.Group)
		self.assertIsNone(copy.Group)

	def test_Parameter(self) -> None:
		"""A copy of a parameter is in no parameter group."""
		original =  ParameterConstantInterfaceItem(("a", ), Mode.In, _subtypeSymbol("integer"))
		procedure = Procedure("p", parameterItems=[original])

		copy = original.Copy()

		self.assertIs(procedure.ParameterGroups[0], original.Group)
		self.assertIsNone(copy.Group)


class InterfaceItemsWithModeView(Testcase):
	def test_Copy(self) -> None:
		for cls in (PortViewSignalInterfaceItem, ParameterViewSignalInterfaceItem):
			with self.subTest(cls.__name__):
				modeView = ModeViewSymbol(SimpleName("MasterView"))
				original = cls(("p", "q"), modeView, "Documentation.", _Element())

				copy = original.Copy()

				self.assertIs(cls, type(copy))
				self.assertIsNone(copy.Parent)
				self.assertTupleEqual(("p", "q"), copy.Identifiers)
				self.assertEqual("Documentation.", copy.Documentation)
				self.assertIs(ModeViewSymbol, type(copy.ModeViewIndication))
				self.assertIsNot(modeView, copy.ModeViewIndication)
				self.assertIsNot(modeView.Name, copy.ModeViewIndication.Name)
				self.assertIsNone(copy.DefaultExpression)
				self.assertEqual(str(original), str(copy))


class FileInterfaceItems(Testcase):
	def test_Copy(self) -> None:
		subtype = _subtypeSymbol("text")
		original = ParameterFileInterfaceItem(("f", ), subtype, "Documentation.", _Element())

		copy = original.Copy()

		self.assertIs(ParameterFileInterfaceItem, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertTupleEqual(("f", ), copy.Identifiers)
		self.assertEqual("Documentation.", copy.Documentation)
		self.assertIsNot(subtype, copy.Subtype)
		self.assertEqual(str(original), str(copy))


class GenericItems(Testcase):
	def test_Type(self) -> None:
		original = GenericTypeInterfaceItem("T", "Documentation.", _Element())

		copy = original.Copy()

		self.assertIs(GenericTypeInterfaceItem, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertEqual("T", copy.Identifier)
		self.assertEqual("Documentation.", copy.Documentation)

	def test_Package(self) -> None:
		original = GenericPackageInterfaceItem("pkg", "Documentation.", _Element())

		copy = original.Copy()

		self.assertIs(GenericPackageInterfaceItem, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertEqual("pkg", copy.Identifier)
		self.assertEqual("Documentation.", copy.Documentation)

	def test_Procedure(self) -> None:
		parameter = ParameterConstantInterfaceItem(("msg", ), Mode.In, _subtypeSymbol("string"))
		original = GenericProcedureInterfaceItem("log", "Documentation.", _Element())
		original.AddParameterItem(parameter)
		original.IndexDeclaredItems()

		copy = original.Copy()

		self.assertIs(GenericProcedureInterfaceItem, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertEqual("log", copy.Identifier)
		self.assertEqual("Documentation.", copy.Documentation)
		self.assertEqual(1, copy.ParameterCount)
		self.assertIsNot(parameter, copy.ParameterItems[0])
		self.assertIs(copy, copy.ParameterItems[0].Parent)
		self.assertTupleEqual(("msg", ), copy.ParameterItems[0].Identifiers)
		self.assertIsNot(original.Namespace, copy.Namespace)
		self.assertTrue(original._areDeclaredItemsIndexed)
		self.assertFalse(copy._areDeclaredItemsIndexed)

	def test_Function(self) -> None:
		returnType = _subtypeSymbol("boolean")
		parameter = ParameterConstantInterfaceItem(("a", "b"), Mode.In, _subtypeSymbol("integer"))
		original = GenericFunctionInterfaceItem("cmp", returnType, "Documentation.", _Element())
		original.AddParameterItem(parameter)

		copy = original.Copy()

		self.assertIs(GenericFunctionInterfaceItem, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertEqual("cmp", copy.Identifier)
		self.assertIsNot(returnType, copy.ReturnType)
		self.assertEqual("boolean", copy.ReturnType.Name.Identifier)
		self.assertEqual(1, copy.ParameterCount)
		self.assertIsNot(parameter, copy.ParameterItems[0])
		self.assertIs(copy, copy.ParameterItems[0].Parent)

	def test_Function_Modify(self) -> None:
		"""Adding a parameter to the copy leaves the original unchanged."""
		original = GenericFunctionInterfaceItem("cmp", _subtypeSymbol("boolean"))

		copy = original.Copy()
		copy.AddParameterItem(ParameterConstantInterfaceItem(("a", ), Mode.In, _subtypeSymbol("integer")))

		self.assertEqual(0, original.ParameterCount)
		self.assertEqual(1, copy.ParameterCount)


class ModeViewElements(Testcase):
	def test_Simple(self) -> None:
		original = SimpleModeViewElement(("a", "b"), Mode.Out, "Documentation.", _Element())

		copy = original.Copy()

		self.assertIs(SimpleModeViewElement, type(copy))
		self.assertIsNot(original, copy)
		self.assertIsNone(copy.Parent)
		self.assertTupleEqual(("a", "b"), copy.Identifiers)
		self.assertIs(Mode.Out, copy.Mode)
		self.assertEqual("Documentation.", copy.Documentation)

	def test_Composite(self) -> None:
		modeView = ModeViewSymbol(SimpleName("InnerView"))
		original = CompositeModeViewElement(("b", ), modeView, "Documentation.", _Element())

		copy = original.Copy()

		self.assertIs(CompositeModeViewElement, type(copy))
		self.assertIsNone(copy.Parent)
		self.assertTupleEqual(("b", ), copy.Identifiers)
		self.assertIsNot(modeView, copy.ModeViewName)
		self.assertIsNot(modeView.Name, copy.ModeViewName.Name)
		self.assertEqual("Documentation.", copy.Documentation)
