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
Split tests for object declarations (:mod:`pyVHDLModel.Object`).

``signal a, b : bit;`` becomes ``signal a : bit; signal b : bit;``: outside a declarative region and in a concurrent,
sequential and package declarative region, indexed or not.
"""
from pyTooling.Graph             import Vertex
from pyTooling.Testing           import Testcase
from pyTooling.Warning           import WarningCollector

from pyVHDLModel.Concurrent      import ProcessStatement
from pyVHDLModel.DesignUnit      import Architecture, Package
from pyVHDLModel.Exception       import NotAChildError, NotInNamespaceError
from pyVHDLModel.Expression      import IntegerLiteral, AdditionExpression
from pyVHDLModel.Object          import Constant, DeferredConstant, Variable, SharedVariable, Signal, File

from tests.unit                  import _entitySymbol, _subtypeSymbol
from tests.unit.Copy             import _object
from tests.unit.Mutation         import _reindexed, _signal
from tests.unit.Split            import _formatted


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class _DerivedSignal(Signal):
	"""A signal of a class derived outside pyVHDLModel, with the constructor of its base-class."""


class ObjectsWithDefaultExpression(Testcase):
	def test_Split(self) -> None:
		for cls in (Constant, Variable, Signal):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("positive")
				defaultExpression = AdditionExpression(_object("BITS"), IntegerLiteral(1))
				original = cls(("a", "B", "c"), subtype, defaultExpression, "Documentation.")

				declarations = original.Split()

				self.assertEqual(3, len(declarations))
				self.assertIs(original, declarations[0])
				self.assertTupleEqual(("a", ), declarations[0].Identifiers)
				self.assertTupleEqual(("B", ), declarations[1].Identifiers)
				self.assertTupleEqual(("b", ), declarations[1].NormalizedIdentifiers)
				self.assertTupleEqual(("c", ), declarations[2].Identifiers)
				self.assertIs(subtype, original.Subtype)
				self.assertIs(defaultExpression, original.DefaultExpression)
				for declaration in declarations[1:]:
					self.assertIs(cls, type(declaration))
					self.assertIsNone(declaration.Parent)
					self.assertEqual("Documentation.", declaration.Documentation)
					self.assertIsNot(subtype, declaration.Subtype)
					self.assertIs(declaration, declaration.Subtype.Parent)
					self.assertIsNot(defaultExpression, declaration.DefaultExpression)
					self.assertIs(declaration, declaration.DefaultExpression.Parent)

				keyword = original._OBJECT_KEYWORD[0]
				self.assertListEqual(
					[
						f"{keyword} a : positive := BITS + 1;\n",
						f"{keyword} B : positive := BITS + 1;\n",
						f"{keyword} c : positive := BITS + 1;\n"
					],
					_formatted(declarations)
				)

	def test_Split_WithoutDefaultExpression(self) -> None:
		for cls in (Variable, Signal):
			with self.subTest(cls.__name__):
				original = cls(("a", "b"), _subtypeSymbol("bit"))

				declarations = original.Split()

				self.assertIsNone(declarations[1].DefaultExpression)

	def test_Split_OneIdentifier(self) -> None:
		"""A declaration with one identifier is unchanged and returned alone."""
		for cls in (Constant, Variable, Signal):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("bit")
				original = cls(("a", ), subtype, IntegerLiteral(0))

				self.assertTupleEqual((original, ), original.Split())
				self.assertTupleEqual(("a", ), original.Identifiers)
				self.assertIs(subtype, original.Subtype)

	def test_Split_Derived(self) -> None:
		"""A declaration of a class derived outside pyVHDLModel splits into declarations of that class."""
		original = _DerivedSignal(("a", "b"), _subtypeSymbol("bit"))

		declarations = original.Split()

		self.assertIs(_DerivedSignal, type(declarations[1]))

	def test_Split_ObjectVertex(self) -> None:
		"""The split declaration keeps its object vertex; a new declaration is not in the object graph."""
		original = Signal(("a", "b"), _subtypeSymbol("bit"))
		vertex = Vertex(value=original)
		original._objectVertex = vertex

		declarations = original.Split()

		self.assertIs(vertex, original.ObjectVertex)
		self.assertIsNone(declarations[1].ObjectVertex)


class ObjectsWithoutDefaultExpression(Testcase):
	def test_Split(self) -> None:
		for cls in (DeferredConstant, SharedVariable, File):
			with self.subTest(cls.__name__):
				subtype = _subtypeSymbol("text")
				original = cls(("a", "b"), subtype, "Documentation.")

				declarations = original.Split()

				self.assertEqual(2, len(declarations))
				self.assertIs(original, declarations[0])
				self.assertTupleEqual(("a", ), declarations[0].Identifiers)
				self.assertTupleEqual(("b", ), declarations[1].Identifiers)
				self.assertIs(cls, type(declarations[1]))
				self.assertIsNone(declarations[1].Parent)
				self.assertEqual("Documentation.", declarations[1].Documentation)
				self.assertIsNot(subtype, declarations[1].Subtype)
				self.assertIs(declarations[1], declarations[1].Subtype.Parent)

	def test_Split_ConstantReference(self) -> None:
		"""A new deferred constant refers to the same full constant declaration."""
		constant = Constant(("a", "b"), _subtypeSymbol("natural"), IntegerLiteral(1))
		original = DeferredConstant(("a", "b"), _subtypeSymbol("natural"))
		original._constantReference = constant

		declarations = original.Split()

		self.assertIs(constant, declarations[1].ConstantReference)


class ConcurrentDeclarationRegion(Testcase):
	def test_Split(self) -> None:
		first = _signal("first")
		original = _signal("a", "b", "c")
		last = _signal("last")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[first, original, last])

		declarations = original.Split()

		self.assertListEqual([first, *declarations, last], architecture.DeclaredItems)
		for declaration in declarations:
			self.assertIs(architecture, declaration.Parent)

		self.assertDictEqual({}, architecture.Signals)
		self.assertDictEqual({}, architecture._namespace._elements)

	def test_Split_Indexed(self) -> None:
		"""In an indexed region, the namespace and lookup table entries of the other identifiers move."""
		original = _signal("a", "b", "c")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[original])
		architecture.IndexDeclaredItems()

		declarations = original.Split()

		self.assertDictEqual({"a": declarations[0], "b": declarations[1], "c": declarations[2]}, architecture.Signals)
		self.assertDictEqual(
			{"a": declarations[0], "b": declarations[1], "c": declarations[2]},
			architecture._namespace._elements
		)
		self.assertDictEqual(*_reindexed(architecture))

	def test_Split_Package(self) -> None:
		"""A constant, a deferred constant, a shared variable and a file split in an indexed package."""
		constant = Constant(("c1", "c2"), _subtypeSymbol("natural"), IntegerLiteral(1))
		deferredConstant = DeferredConstant(("d1", "d2"), _subtypeSymbol("natural"))
		sharedVariable = SharedVariable(("v1", "v2"), _subtypeSymbol("counter"))
		file = File(("f1", "f2"), _subtypeSymbol("text"))
		package = Package("p", declaredItems=[constant, deferredConstant, sharedVariable, file])
		package.IndexDeclaredItems()

		constants = constant.Split()
		deferredConstants = deferredConstant.Split()
		sharedVariables = sharedVariable.Split()
		files = file.Split()

		self.assertListEqual([*constants, *deferredConstants, *sharedVariables, *files], package.DeclaredItems)
		self.assertDictEqual({"c1": constants[0], "c2": constants[1]}, package.Constants)
		self.assertDictEqual({"d1": deferredConstants[0], "d2": deferredConstants[1]}, package.DeferredConstants)
		self.assertDictEqual({"v1": sharedVariables[0], "v2": sharedVariables[1]}, package.SharedVariables)
		self.assertDictEqual({"f1": files[0], "f2": files[1]}, package.Files)
		self.assertDictEqual(*_reindexed(package))

	def test_Split_NotAChild(self) -> None:
		"""A declaration whose parent doesn't list it isn't split."""
		original = _signal("a", "b")
		architecture = Architecture("rtl", _entitySymbol("e"))
		original.Parent = architecture

		with self.assertRaises(NotAChildError) as context:
			original.Split()

		self.assertEqual("Signal 'a, b' is not a declared item of this Architecture.", str(context.exception))
		self.assertTupleEqual(("a", "b"), original.Identifiers)

	def test_Split_Duplicate(self) -> None:
		"""A namespace entry referring to a duplicate declaration is reported; nothing is changed."""
		original = _signal("a", "b")
		duplicate = _signal("b")
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[original, duplicate])
		with WarningCollector():
			architecture.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			original.Split()

		self.assertEqual("Namespace 'rtl' has another element for 'b'.", str(context.exception))
		self.assertTupleEqual(("a", "b"), original.Identifiers)
		self.assertListEqual([original, duplicate], architecture.DeclaredItems)
		self.assertIs(duplicate, architecture.Signals["b"])


class SequentialDeclarationRegion(Testcase):
	def test_Split_Indexed(self) -> None:
		original = Variable(("a", "b"), _subtypeSymbol("natural"), IntegerLiteral(0))
		process = ProcessStatement("proc", declaredItems=[original])
		process.IndexDeclaredItems()

		declarations = original.Split()

		self.assertListEqual(list(declarations), process.DeclaredItems)
		self.assertIs(process, declarations[1].Parent)
		self.assertDictEqual({"a": declarations[0], "b": declarations[1]}, process.Variables)
		self.assertDictEqual({"a": declarations[0], "b": declarations[1]}, process.Namespace._elements)
		self.assertDictEqual(*_reindexed(process))
