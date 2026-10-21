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
"""
Mutation tests for the index state of a declarative region: lookup tables and namespace.

A region not indexed yet gets its lookup tables and namespace filled by ``IndexDeclaredItems`` only. In an indexed
region, every mutator leaves the state that indexing again would produce. The namespace keeps one entry per identifier:
for overloads, it refers to the overload declared last.
"""
from pyTooling.Testing       import Testcase
from pyTooling.Warning       import WarningCollector

from pyVHDLModel.DesignUnit  import Architecture, Package
from pyVHDLModel.Exception   import NotInNamespaceError
from pyVHDLModel.Object      import DeferredConstant

from tests.unit              import _entitySymbol, _subtypeSymbol
from tests.unit.Mutation     import _constant, _function, _procedure, _reindexed, _signal


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _architecture(*declaredItems) -> Architecture:
	return Architecture("rtl", _entitySymbol("e"), declaredItems=declaredItems)


class NotIndexed(Testcase):
	def test_Add(self) -> None:
		architecture = _architecture()
		signal = _signal("s")

		architecture.AddDeclaredItem(signal)

		self.assertListEqual([signal], architecture.DeclaredItems)
		self.assertDictEqual({}, architecture.Signals)
		self.assertDictEqual({}, architecture._namespace._elements)

		architecture.IndexDeclaredItems()

		self.assertDictEqual({"s": signal}, architecture.Signals)

	def test_Remove(self) -> None:
		signal = _signal("s")
		function = _function("f")
		architecture = _architecture(signal, function)

		architecture.RemoveDeclaredItem(signal)
		architecture.RemoveDeclaredItem(function)

		self.assertListEqual([], architecture.DeclaredItems)
		self.assertIsNone(signal.Parent)
		self.assertDictEqual({}, architecture._namespace._elements)


class Overloads(Testcase):
	def test_Insert_Start(self) -> None:
		overload1 = _function("f")
		overload2 = _function("f")
		architecture = _architecture(overload1, overload2)
		architecture.IndexDeclaredItems()
		overload0 = _function("f")

		architecture.InsertDeclaredItem(0, overload0)

		self.assertDictEqual({"f": [overload0, overload1, overload2]}, architecture.Functions)
		self.assertIs(overload2, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Insert_Middle(self) -> None:
		overload1 = _function("f")
		overload3 = _function("f")
		architecture = _architecture(overload1, overload3)
		architecture.IndexDeclaredItems()
		overload2 = _function("f")

		architecture.InsertDeclaredItemAfter(overload2, overload1)

		self.assertDictEqual({"f": [overload1, overload2, overload3]}, architecture.Functions)
		self.assertIs(overload3, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Insert_End(self) -> None:
		overload1 = _function("f")
		architecture = _architecture(overload1)
		architecture.IndexDeclaredItems()
		overload2 = _function("f")

		architecture.AddDeclaredItem(overload2)

		self.assertIs(overload2, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Insert_ProcedureBeforeFunction(self) -> None:
		"""Functions and procedures share the namespace entry of their identifier."""
		function = _function("f")
		architecture = _architecture(function)
		architecture.IndexDeclaredItems()
		procedure = _procedure("f")

		architecture.InsertDeclaredItem(0, procedure)

		self.assertDictEqual({"f": [procedure]}, architecture.Procedures)
		self.assertIs(function, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Remove_Entry(self) -> None:
		"""Removing the overload declared last re-points the namespace entry to the remaining overload declared last."""
		overload1 = _function("f")
		overload2 = _function("f")
		overload3 = _function("f")
		architecture = _architecture(overload1, overload2, overload3)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(overload3)

		self.assertDictEqual({"f": [overload1, overload2]}, architecture.Functions)
		self.assertIs(overload2, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Remove_OtherOverload(self) -> None:
		overload1 = _function("f")
		overload2 = _function("f")
		overload3 = _function("f")
		architecture = _architecture(overload1, overload2, overload3)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(overload2)

		self.assertDictEqual({"f": [overload1, overload3]}, architecture.Functions)
		self.assertIs(overload3, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Remove_Last(self) -> None:
		function = _function("f")
		architecture = _architecture(function)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(function)

		self.assertDictEqual({}, architecture.Functions)
		self.assertDictEqual({}, architecture._namespace._elements)
		self.assertDictEqual(*_reindexed(architecture))

	def test_Remove_ProcedureAndFunction(self) -> None:
		function = _function("f")
		procedure = _procedure("f")
		architecture = _architecture(function, procedure)
		architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(procedure)

		self.assertDictEqual({}, architecture.Procedures)
		self.assertIs(function, architecture._namespace._elements["f"])
		self.assertDictEqual(*_reindexed(architecture))

	def test_Remove_Shadowed(self) -> None:
		"""An overload shadowed by a duplicate declaration read by a parser isn't in the namespace: it stays attached."""
		function = _function("f")
		signal = _signal("f")
		architecture = _architecture(function, signal)
		with WarningCollector():
			architecture.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			architecture.RemoveDeclaredItem(function)

		self.assertEqual("Namespace 'rtl' has another element for 'f'.", str(context.exception))
		self.assertListEqual(["Found element of type 'pyVHDLModel.Object.Signal'."], context.exception.__notes__)
		self.assertEqual("f", context.exception.Identifier)
		self.assertEqual("f", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertListEqual([function, signal], architecture.DeclaredItems)
		self.assertIs(architecture, function.Parent)
		self.assertDictEqual({"f": [function]}, architecture.Functions)

	def test_Remove_NotInNamespace(self) -> None:
		function = _function("f")
		architecture = _architecture(function)
		architecture.IndexDeclaredItems()
		architecture._namespace.RemoveElement("f", function)

		with self.assertRaises(NotInNamespaceError) as context:
			architecture.RemoveDeclaredItem(function)

		self.assertEqual("Namespace 'rtl' has no element 'f'.", str(context.exception))
		self.assertEqual("f", context.exception.Identifier)
		self.assertEqual("f", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertListEqual([function], architecture.DeclaredItems)
		self.assertDictEqual({"f": [function]}, architecture.Functions)


class Objects(Testcase):
	def test_Remove_NotInNamespace(self) -> None:
		signal = _signal("s")
		architecture = _architecture(signal)
		architecture.IndexDeclaredItems()
		architecture._namespace.RemoveElement("s", signal)

		with self.assertRaises(NotInNamespaceError) as context:
			architecture.RemoveDeclaredItem(signal)

		self.assertEqual("Namespace 'rtl' has no element 's'.", str(context.exception))
		self.assertEqual("s", context.exception.Identifier)
		self.assertEqual("s", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertListEqual([signal], architecture.DeclaredItems)
		self.assertIs(architecture, signal.Parent)
		self.assertDictEqual({"s": signal}, architecture.Signals)

	def test_Remove_MultipleIdentifiers_Shadowed(self) -> None:
		"""All identifiers are checked before anything is removed."""
		signal = _signal("a", "b")
		duplicate = _constant("b")
		architecture = _architecture(signal, duplicate)
		with WarningCollector():
			architecture.IndexDeclaredItems()

		with self.assertRaises(NotInNamespaceError) as context:
			architecture.RemoveDeclaredItem(signal)

		self.assertEqual("Namespace 'rtl' has another element for 'b'.", str(context.exception))
		self.assertListEqual(["Found element of type 'pyVHDLModel.Object.Constant'."], context.exception.__notes__)
		self.assertEqual("b", context.exception.Identifier)
		self.assertEqual("b", context.exception.NormalizedIdentifier)
		self.assertIs(architecture._namespace, context.exception.Namespace)
		self.assertIs(architecture, signal.Parent)
		self.assertDictEqual({"a": signal, "b": signal}, architecture.Signals)
		self.assertDictEqual({"a": signal, "b": duplicate}, architecture._namespace._elements)

	def test_Remove_ParsedDuplicate_OtherKind(self) -> None:
		"""Removing the declaration a parsed duplicate is shadowed by leaves the state of indexing again."""
		constant = _constant("x")
		signal = _signal("x")
		architecture = _architecture(constant, signal)
		with WarningCollector():
			architecture.IndexDeclaredItems()

		architecture.RemoveDeclaredItem(signal)

		self.assertDictEqual({}, architecture.Signals)
		self.assertDictEqual({"x": constant}, architecture.Constants)
		self.assertDictEqual({"x": constant}, architecture._namespace._elements)
		self.assertDictEqual(*_reindexed(architecture))

	def test_Remove_ParsedDuplicate_DeferredConstant(self) -> None:
		deferredConstant1 = DeferredConstant(["c"], _subtypeSymbol("natural"))
		deferredConstant2 = DeferredConstant(["c"], _subtypeSymbol("natural"))
		package = Package("pkg", declaredItems=[deferredConstant1, deferredConstant2])
		package.IndexDeclaredItems()

		package.RemoveDeclaredItem(deferredConstant2)

		self.assertDictEqual({"c": deferredConstant1}, package.DeferredConstants)
		self.assertDictEqual(*_reindexed(package))
