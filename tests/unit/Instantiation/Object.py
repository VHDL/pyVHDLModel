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
"""Tests for pyVHDLModel.Object."""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Object     import Constant, DeferredConstant, Variable, Signal, SharedVariable, File

from tests.unit             import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ObjBaseBehaviour(Testcase):
	"""``Obj`` itself has no public subclass without a more specific meaning, so its shared behaviour
	(multiple identifiers, subtype parent-wiring, the object-graph vertex) is tested once here via
	``Signal`` - any ``Obj`` subclass would do equally well, since none of this is overridden."""

	def test_SingleIdentifier(self) -> None:
		subtype = _subtypeSymbol("natural")
		signal = Signal(["s"], subtype)

		self.assertEqual(("s",), signal.Identifiers)
		self.assertEqual(("s",), signal.NormalizedIdentifiers)
		self.assertIs(subtype, signal.Subtype)
		self.assertIs(signal, subtype.Parent)

	def test_MultipleIdentifiers(self) -> None:
		"""``signal a, b, C : bit;`` declares three signals from one declaration."""
		signal = Signal(["a", "b", "C"], _subtypeSymbol("bit"))

		self.assertEqual(("a", "b", "C"), signal.Identifiers)
		self.assertEqual(("a", "b", "c"), signal.NormalizedIdentifiers)

	def test_ObjectVertexDefaultsToNone(self) -> None:
		"""``ObjectVertex`` is only populated once an object graph is built elsewhere; a freshly
		constructed object was never inserted into one."""
		signal = Signal(["s"], _subtypeSymbol("natural"))

		self.assertIsNone(signal.ObjectVertex)

	def test_Documentation(self) -> None:
		signal = Signal(["s"], _subtypeSymbol("natural"), documentation="a signal")

		self.assertEqual("a signal", signal.Documentation)

	def test_NoDocumentation(self) -> None:
		signal = Signal(["s"], _subtypeSymbol("natural"))

		self.assertIsNone(signal.Documentation)


class WithDefaultExpression(Testcase):
	"""``WithDefaultExpressionMixin`` is shared by ``Constant``, ``Variable`` and ``Signal`` - tested
	once via ``Signal`` for the parent-wiring behaviour, plus one smoke test per consumer below to
	confirm each is actually wired up."""

	def test_WithDefaultExpression(self) -> None:
		default = IntegerLiteral(0)
		signal = Signal(["s"], _subtypeSymbol("natural"), defaultExpression=default)

		self.assertIs(default, signal.DefaultExpression)
		self.assertIs(signal, default.Parent)

	def test_WithoutDefaultExpression(self) -> None:
		signal = Signal(["s"], _subtypeSymbol("natural"))

		self.assertIsNone(signal.DefaultExpression)


class Constants(Testcase):
	def test_WithDefault(self) -> None:
		default = IntegerLiteral(8)
		constant = Constant(["BITS"], _subtypeSymbol("positive"), defaultExpression=default)

		self.assertEqual(("BITS",), constant.Identifiers)
		self.assertIs(default, constant.DefaultExpression)

	def test_WithoutDefault(self) -> None:
		"""Constructible without a default even though real VHDL always requires one for a (non-
		deferred) constant - the model doesn't enforce that grammar rule itself."""
		constant = Constant(["BITS"], _subtypeSymbol("positive"))

		self.assertIsNone(constant.DefaultExpression)


class DeferredConstants(Testcase):
	"""``constant BITS : positive;`` (in a package declaration, completed later in the package body)."""

	def test_Construction(self) -> None:
		constant = DeferredConstant(["BITS"], _subtypeSymbol("positive"))

		self.assertEqual(("BITS",), constant.Identifiers)
		self.assertIsNone(constant.ConstantReference)
		"""``Symbol.__str__`` appends ``?`` for an unresolved reference - the subtype symbol here was
		never resolved against a real type, so it renders as ``positive?``."""
		self.assertEqual("constant BITS : positive?", str(constant))


class Variables(Testcase):
	def test_WithDefault(self) -> None:
		default = IntegerLiteral(0)
		variable = Variable(["result"], _subtypeSymbol("natural"), defaultExpression=default)

		self.assertIs(default, variable.DefaultExpression)

	def test_WithoutDefault(self) -> None:
		variable = Variable(["result"], _subtypeSymbol("natural"))

		self.assertIsNone(variable.DefaultExpression)


class Signals(Testcase):
	def test_WithDefault(self) -> None:
		default = IntegerLiteral(0)
		signal = Signal(["counter"], _subtypeSymbol("unsigned"), defaultExpression=default)

		self.assertIs(default, signal.DefaultExpression)

	def test_WithoutDefault(self) -> None:
		signal = Signal(["counter"], _subtypeSymbol("unsigned"))

		self.assertIsNone(signal.DefaultExpression)


class SharedVariables(Testcase):
	"""``shared variable`` - not implemented beyond the base ``Obj`` shape (see the ``.. todo::`` in
	the class docstring)."""

	def test_Construction(self) -> None:
		variable = SharedVariable(["v"], _subtypeSymbol("natural"))

		self.assertEqual(("v",), variable.Identifiers)
		self.assertIs(SharedVariable, type(variable))


class Files(Testcase):
	"""``file`` - not implemented beyond the base ``Obj`` shape (see the ``.. todo::`` in the class
	docstring); open-mode/logical-name are not modelled at all yet."""

	def test_Construction(self) -> None:
		file = File(["f"], _subtypeSymbol("text"))

		self.assertEqual(("f",), file.Identifiers)
