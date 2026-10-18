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
Namespaces created by concurrent statements: blocks and the three generate statements.

Namespace-connection happens in the ``Parent`` property *setter* override, not in the constructor -
passing ``parent=`` to ``__init__`` assigns ``self._parent`` directly and never reaches the overridden
setter. Every test here therefore assigns ``.Parent`` after construction.
"""
from pyTooling.Testing      import Testcase

from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Concurrent import (
	CaseGenerateStatement,
	ConcurrentBlockStatement,
	ElseGenerateBranch,
	ElsifGenerateBranch,
	ForGenerateStatement,
	GenerateCase,
	IfGenerateBranch,
	IfGenerateStatement,
	IndexedGenerateChoice,
)
from pyVHDLModel.DesignUnit import Architecture
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import EntitySymbol

from tests.unit             import _entitySymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class BlockStatements(Testcase):
	def test_NestedBlock_ConnectsNamespaceOnParentAssignment(self) -> None:
		outer = ConcurrentBlockStatement("outer")
		inner = ConcurrentBlockStatement("inner")
		inner.Parent = outer

		self.assertIs(outer, inner.Parent)
		self.assertIs(outer._namespace, inner._namespace.ParentNamespace)


class IfGenerateStatements(Testcase):
	def test_AllBranchesConnectToTheArchitecture(self) -> None:
		"""Also a regression test: the fallback that names the if-branch's namespace after the
		statement's own label (for the common, unlabelled-branch case) compared
		``namespace._name == ""``, but an unlabelled ``GenerateBranch`` always constructs its
		namespace with ``_normalizedAlternativeLabel``, which defaults to ``None`` - not ``""`` - so
		the fallback never actually fired. Fixed to compare against ``None``."""
		architecture = Architecture("rtl", _entitySymbol("e"))
		ifBranch = IfGenerateBranch(IntegerLiteral(1))
		elsifBranch = ElsifGenerateBranch(IntegerLiteral(2))
		elseBranch = ElseGenerateBranch()
		statement = IfGenerateStatement("gen", ifBranch, [elsifBranch], elseBranch)

		statement.Parent = architecture

		self.assertIs(architecture._namespace, ifBranch._namespace.ParentNamespace)
		self.assertIs(architecture._namespace, elsifBranch._namespace.ParentNamespace)
		self.assertIs(architecture._namespace, elseBranch._namespace.ParentNamespace)
		self.assertEqual("gen", ifBranch._namespace._name)


class CaseGenerateStatements(Testcase):
	def test_CaseConnectsToTheArchitecture(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("e"))
		case = GenerateCase([IndexedGenerateChoice(IntegerLiteral(0))])
		statement = CaseGenerateStatement("gen", IntegerLiteral(0), [case])

		statement.Parent = architecture

		self.assertIs(architecture._namespace, case._namespace.ParentNamespace)


class ForGenerateStatements(Testcase):
	def test_ConnectsToTheArchitecture(self) -> None:
		architecture = Architecture("rtl", _entitySymbol("e"))
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		statement = ForGenerateStatement("gen", "i", rng)

		statement.Parent = architecture

		self.assertIs(architecture._namespace, statement._namespace.ParentNamespace)
