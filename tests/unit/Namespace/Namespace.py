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
"""
Standalone tests for ``pyVHDLModel.Namespace``.

``Namespace`` isn't a ``ModelEntity`` and has no public insert method - ``_elements`` is populated by
``IndexDeclaredItems`` as design units are analyzed. These tests therefore seed ``_elements`` directly,
keyed by *normalized* identifier exactly as the ``Find*`` methods look them up, so the resolution logic
can be exercised without building a whole design.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.DesignUnit import Component
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Namespace  import ExtendedKeyError, Namespace
from pyVHDLModel.Object     import Constant, Signal, Variable
from pyVHDLModel.Symbol     import ComponentInstantiationSymbol, PossibleReference, SignalSymbol, SimpleSubtypeSymbol, \
                                   Symbol, VariableSymbol
from pyVHDLModel.Type       import IntegerType, Subtype

from tests.unit             import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _integerType(identifier: str = "myInteger") -> IntegerType:
	return IntegerType(identifier, SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To))


class Namespaces(Testcase):
	"""Construction and the parent/sub-namespace wiring."""

	def test_Construction(self) -> None:
		namespace = Namespace("architecture")

		self.assertEqual("architecture", namespace.Name)
		self.assertIsNone(namespace.ParentNamespace)
		self.assertEqual(0, len(namespace.SubNamespaces))
		self.assertEqual(0, len(namespace.Elements))

	def test_ConstructionWithParent(self) -> None:
		parent = Namespace("entity")
		namespace = Namespace("architecture", parent)

		self.assertIs(parent, namespace.ParentNamespace)
		self.assertListEqual([namespace], parent.SubNamespaces)

	def test_ParentNamespaceSetter_RegistersInParent(self) -> None:
		parent = Namespace("entity")
		namespace = Namespace("architecture")
		namespace.ParentNamespace = parent

		self.assertIs(parent, namespace.ParentNamespace)
		self.assertListEqual([namespace], parent.SubNamespaces)


class FindComponent(Testcase):
	"""``FindComponent`` - the reference implementation of the ``ExtendedKeyError`` chaining pattern."""

	def test_Found(self) -> None:
		namespace = Namespace("architecture")
		component = Component("comp")
		namespace._elements["comp"] = component

		self.assertIs(component, namespace.FindComponent(ComponentInstantiationSymbol(SimpleName("comp"))))

	def test_FoundViaNormalizedIdentifier(self) -> None:
		namespace = Namespace("architecture")
		component = Component("Comp")
		namespace._elements["comp"] = component

		# Lookup is case-insensitive because it goes through the normalized identifier.
		self.assertIs(component, namespace.FindComponent(ComponentInstantiationSymbol(SimpleName("COMP"))))

	def test_FoundButWrongKind_RaisesTypeError(self) -> None:
		namespace = Namespace("architecture")
		namespace._elements["comp"] = _integerType("comp")

		with self.assertRaises(TypeError) as context:
			namespace.FindComponent(ComponentInstantiationSymbol(SimpleName("comp")))

		self.assertIn("not a component", str(context.exception))
		# The note reports what was actually found, so the message needn't carry the type.
		self.assertIn("Got type 'pyVHDLModel.Type.IntegerType'.", context.exception.__notes__)

	def test_NotFoundWithoutParent_RaisesExtendedKeyError(self) -> None:
		namespace = Namespace("architecture")

		with self.assertRaises(ExtendedKeyError) as context:
			namespace.FindComponent(ComponentInstantiationSymbol(SimpleName("comp")))

		self.assertEqual("comp", context.exception.key)
		self.assertEqual((namespace, ), context.exception.searchedNamespaces)

	def test_NotFoundLocally_FoundInParent(self) -> None:
		parent = Namespace("entity")
		namespace = Namespace("architecture", parent)
		component = Component("comp")
		parent._elements["comp"] = component

		self.assertIs(component, namespace.FindComponent(ComponentInstantiationSymbol(SimpleName("comp"))))

	def test_NotFoundAnywhere_ChainsSearchedNamespaces(self) -> None:
		outer = Namespace("library")
		middle = Namespace("entity", outer)
		inner = Namespace("architecture", middle)

		with self.assertRaises(ExtendedKeyError) as context:
			inner.FindComponent(ComponentInstantiationSymbol(SimpleName("comp")))

		exception = context.exception

		# Namespaces accumulate innermost-first as the walk unwinds.
		self.assertEqual((inner, middle, outer), exception.searchedNamespaces)
		self.assertEqual("comp", exception.key)
		self.assertIn("architecture, entity, library", str(exception))


class FindSubtype(Testcase):
	"""``FindSubtype`` - resolves both subtypes and full types, filtered by the symbol's possible references."""

	def test_FoundSubtype(self) -> None:
		namespace = Namespace("package")
		subtype = Subtype("byte", _subtypeSymbol("natural"))
		namespace._elements["byte"] = subtype

		symbol = Symbol(SimpleName("byte"), PossibleReference.Subtype)

		self.assertIs(subtype, namespace.FindSubtype(symbol))

	def test_FoundFullType(self) -> None:
		namespace = Namespace("package")
		integerType = _integerType("nibble")
		namespace._elements["nibble"] = integerType

		symbol = Symbol(SimpleName("nibble"), PossibleReference.Type)

		self.assertIs(integerType, namespace.FindSubtype(symbol))

	def test_FoundSubtypeButNotExpected_RaisesTypeError(self) -> None:
		namespace = Namespace("package")
		namespace._elements["byte"] = Subtype("byte", _subtypeSymbol("natural"))

		symbol = Symbol(SimpleName("byte"), PossibleReference.Signal)

		with self.assertRaises(TypeError) as context:
			namespace.FindSubtype(symbol)

		self.assertIn("was not expected", str(context.exception))
		# Two notes: what was found, and what the symbol would have accepted.
		self.assertIn("Got type 'pyVHDLModel.Type.Subtype'.", context.exception.__notes__)
		self.assertIn("Expected one of: PossibleReference.Signal.", context.exception.__notes__)

	def test_FoundTypeButNotExpected_RaisesTypeError(self) -> None:
		namespace = Namespace("package")
		namespace._elements["nibble"] = _integerType("nibble")

		symbol = Symbol(SimpleName("nibble"), PossibleReference.Signal)

		with self.assertRaises(TypeError) as context:
			namespace.FindSubtype(symbol)

		self.assertIn("was not expected", str(context.exception))

	def test_FoundButWrongKind_RaisesTypeError(self) -> None:
		namespace = Namespace("package")
		namespace._elements["sig"] = Signal(("sig", ), _subtypeSymbol("natural"))

		symbol = Symbol(SimpleName("sig"), PossibleReference.Subtype)

		with self.assertRaises(TypeError) as context:
			namespace.FindSubtype(symbol)

		self.assertIn("not a type or subtype", str(context.exception))

	def test_NotFoundWithoutParent_RaisesExtendedKeyError(self) -> None:
		namespace = Namespace("package")

		symbol = Symbol(SimpleName("byte"), PossibleReference.Subtype)

		with self.assertRaises(ExtendedKeyError) as context:
			namespace.FindSubtype(symbol)

		exception = context.exception
		self.assertEqual("byte", exception.key)
		self.assertEqual((namespace, ), exception.searchedNamespaces)
		self.assertIn("Subtype 'byte' not found", str(exception))

	def test_NotFoundLocally_FoundInParent(self) -> None:
		parent = Namespace("package")
		namespace = Namespace("architecture", parent)
		subtype = Subtype("byte", _subtypeSymbol("natural"))
		parent._elements["byte"] = subtype

		symbol = Symbol(SimpleName("byte"), PossibleReference.Subtype)

		self.assertIs(subtype, namespace.FindSubtype(symbol))

	def test_NotFoundAnywhere_ChainsSearchedNamespaces(self) -> None:
		outer = Namespace("library")
		middle = Namespace("package", outer)
		inner = Namespace("architecture", middle)

		symbol = Symbol(SimpleName("byte"), PossibleReference.Subtype)

		with self.assertRaises(ExtendedKeyError) as context:
			inner.FindSubtype(symbol)

		exception = context.exception
		self.assertEqual((inner, middle, outer), exception.searchedNamespaces)
		self.assertIn("architecture, package, library", str(exception))


class FindObject(Testcase):
	"""``FindObject`` - resolves signals, constants and variables."""

	def test_FoundSignal(self) -> None:
		namespace = Namespace("architecture")
		signal = Signal(("clk", ), _subtypeSymbol("natural"))
		namespace._elements["clk"] = signal

		self.assertIs(signal, namespace.FindObject(SignalSymbol(SimpleName("clk"))))

	def test_FoundSignalViaSignalAttribute(self) -> None:
		namespace = Namespace("architecture")
		signal = Signal(("clk", ), _subtypeSymbol("natural"))
		namespace._elements["clk"] = signal

		# A signal attribute (e.g. `clk'event`) resolves to the signal itself.
		symbol = Symbol(SimpleName("clk"), PossibleReference.SignalAttribute)

		self.assertIs(signal, namespace.FindObject(symbol))

	def test_FoundConstant(self) -> None:
		namespace = Namespace("architecture")
		constant = Constant(("width", ), _subtypeSymbol("natural"))
		namespace._elements["width"] = constant

		symbol = Symbol(SimpleName("width"), PossibleReference.Constant)

		self.assertIs(constant, namespace.FindObject(symbol))

	def test_FoundVariable(self) -> None:
		namespace = Namespace("process")
		variable = Variable(("index", ), _subtypeSymbol("natural"))
		namespace._elements["index"] = variable

		self.assertIs(variable, namespace.FindObject(VariableSymbol(SimpleName("index"))))

	def test_FoundButNotExpected_RaisesTypeError(self) -> None:
		namespace = Namespace("architecture")
		namespace._elements["clk"] = Signal(("clk", ), _subtypeSymbol("natural"))

		symbol = Symbol(SimpleName("clk"), PossibleReference.Constant)

		with self.assertRaises(TypeError) as context:
			namespace.FindObject(symbol)

		self.assertIn("was not expected", str(context.exception))

	def test_FoundButWrongKind_RaisesTypeError(self) -> None:
		namespace = Namespace("architecture")
		namespace._elements["byte"] = Subtype("byte", _subtypeSymbol("natural"))

		with self.assertRaises(TypeError) as context:
			namespace.FindObject(SignalSymbol(SimpleName("byte")))

		# Regression: this branch used to report "not a type or subtype", copy-pasted from FindSubtype.
		self.assertIn("not an object", str(context.exception))
		self.assertIn("Got type 'pyVHDLModel.Type.Subtype'.", context.exception.__notes__)

	def test_NotFoundWithoutParent_RaisesExtendedKeyError(self) -> None:
		namespace = Namespace("architecture")

		with self.assertRaises(ExtendedKeyError) as context:
			namespace.FindObject(SignalSymbol(SimpleName("clk")))

		exception = context.exception
		self.assertEqual("clk", exception.key)
		self.assertEqual((namespace, ), exception.searchedNamespaces)
		# Regression: this message used to say "Subtype 'clk' not found".
		self.assertIn("Object 'clk' not found", str(exception))

	def test_NotFoundLocally_FoundInParent(self) -> None:
		parent = Namespace("entity")
		namespace = Namespace("architecture", parent)
		signal = Signal(("clk", ), _subtypeSymbol("natural"))
		parent._elements["clk"] = signal

		self.assertIs(signal, namespace.FindObject(SignalSymbol(SimpleName("clk"))))

	def test_NotFoundAnywhere_ChainsSearchedNamespaces(self) -> None:
		outer = Namespace("library")
		middle = Namespace("entity", outer)
		inner = Namespace("architecture", middle)

		with self.assertRaises(ExtendedKeyError) as context:
			inner.FindObject(SignalSymbol(SimpleName("clk")))

		exception = context.exception
		self.assertEqual((inner, middle, outer), exception.searchedNamespaces)
		self.assertIn("architecture, entity, library", str(exception))
