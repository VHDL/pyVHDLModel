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
Hiding (shadowing) and scope nesting: the same identifier declared in an outer *and* an inner scope.

VHDL lets the same name be declared in many nested declarative regions. Resolution must find the
innermost one, while items declared only in an outer region stay reachable, and the outer region itself
keeps seeing its own declaration.

.. note::

   Only some of VHDL's declarative regions are namespaces in this model today. Entity, architecture,
   package, block, generate branch and generate case all own one. A **process**, a **subprogram** and the
   VHDL-2019 **sequential block statement** don't, and entity **ports/generics** are never indexed into
   the entity's namespace - so the scopes exercised below are the ones that currently *can* be tested.
"""
from pathlib import Path

from pyTooling.Warning      import WarningCollector
from pyTooling.Testing      import Testcase

from pyVHDLModel            import Design, Document, Library
from pyVHDLModel.Base       import Direction, SimpleRange
from pyVHDLModel.Concurrent import ConcurrentBlockStatement, ForGenerateStatement
from pyVHDLModel.DesignUnit import Architecture, Entity
from pyVHDLModel.Exception  import DuplicateDeclarationWarning
from pyVHDLModel.Expression import IntegerLiteral
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Object     import Signal
from pyVHDLModel.Symbol     import EntitySymbol, SignalSymbol, SimpleSubtypeSymbol

from tests.unit             import _signal, _warningsOfType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest %s'" % __file__)
	exit(1)


class EntityAndArchitecture(Testcase):
	"""
	An architecture's namespace nests inside its entity's, which is what makes an entity's ports and
	declarations *visible* in the architecture.

	Note this pair is a single declarative region in VHDL, so it is not a hiding scenario - see
	:meth:`test_ArchitectureDeclarationShadowsEntityDeclaration_ButIsIllegalVHDL`.

	That link is established by :meth:`~pyVHDLModel.Library.LinkArchitectures`, not by assigning
	``Architecture.Parent`` - an architecture's parent is its document, and the entity relation goes
	through the entity symbol. So this needs a real design that has been linked.
	"""

	def setUp(self) -> None:
		design = Design()
		library = Library("work")
		design.AddLibrary(library)
		document = Document(Path("virtual.vhdl"))

		self._entitySignal = _signal("x", "natural")
		self._entityOnlySignal = _signal("entityOnly", "natural")
		self._entity = Entity("ent", declaredItems=[self._entitySignal, self._entityOnlySignal])
		document._AddDesignUnit(self._entity)

		self._architectureSignal = _signal("x", "natural")
		self._architecture = Architecture("rtl", EntitySymbol(SimpleName("ent")), declaredItems=[self._architectureSignal])
		document._AddDesignUnit(self._architecture)

		design.AddDocument(document, library)
		design.CreateDependencyGraph()
		design.LinkArchitectures()

		# 'x' is declared in the entity and in the architecture: a duplicate
		with WarningCollector():
			self._entity.IndexDeclaredItems()
			self._architecture.IndexDeclaredItems()

	def test_ArchitectureNamespaceNestsInsideEntityNamespace(self) -> None:
		self.assertIs(self._entity._namespace, self._architecture._namespace.ParentNamespace)

	def test_ArchitectureDeclarationDuplicatesEntityDeclaration(self) -> None:
		"""
		An entity declaration and its architecture body form a **single** declarative region (LRM 12.1),
		so re-declaring an entity-level name in the architecture is an error, not hiding. GHDL reports
		"identifier "x" already used for a declaration", whereas a *process* variable shadowing an
		architecture signal only warns (``-Whide``).

		The namespaces stay nested - that is what makes the entity's declarations visible below - but the
		link is marked as sharing its region, so the duplicate is reported.
		"""
		self.assertTrue(self._architecture._namespace.SharesRegionWithParent)

		with WarningCollector() as collector:
			self._architecture.IndexDeclaredItems()

		duplicates = _warningsOfType(collector, DuplicateDeclarationWarning)
		self.assertEqual(1, len(duplicates))
		self.assertIn("x", str(duplicates[0]))

	def test_ArchitectureDeclarationStillResolvesToTheInnerOne(self) -> None:
		"""Reporting the duplicate does not change resolution: the innermost declaration still wins."""
		found = self._architecture._namespace.FindObject(SignalSymbol(SimpleName("x")))

		self.assertIs(self._architectureSignal, found)

	def test_ArchitectureInheritsEntityOnlyDeclaration(self) -> None:
		found = self._architecture._namespace.FindObject(SignalSymbol(SimpleName("entityOnly")))

		self.assertIs(self._entityOnlySignal, found)

	def test_EntityStillResolvesItsOwnDeclaration(self) -> None:
		"""Lookup only walks outwards - the outer namespace is unaffected by the inner one."""
		found = self._entity._namespace.FindObject(SignalSymbol(SimpleName("x")))

		self.assertIs(self._entitySignal, found)


class BlocksInsideArchitecture(Testcase):
	"""A block's declarative region nests inside the enclosing architecture's."""

	def setUp(self) -> None:
		self._architectureSignal = _signal("x", "natural")
		self._architectureOnlySignal = _signal("architectureOnly", "natural")
		self._architecture = Architecture(
			"rtl",
			EntitySymbol(SimpleName("ent")),
			declaredItems=[self._architectureSignal, self._architectureOnlySignal],
		)
		self._architecture.IndexDeclaredItems()

		self._blockSignal = _signal("x", "natural")
		self._block = ConcurrentBlockStatement("blk", declaredItems=[self._blockSignal])
		self._block.Parent = self._architecture
		self._block.IndexDeclaredItems()

	def test_BlockDeclarationHidesArchitectureDeclaration(self) -> None:
		found = self._block._namespace.FindObject(SignalSymbol(SimpleName("x")))

		self.assertIs(self._blockSignal, found)

	def test_BlockInheritsArchitectureOnlyDeclaration(self) -> None:
		found = self._block._namespace.FindObject(SignalSymbol(SimpleName("architectureOnly")))

		self.assertIs(self._architectureOnlySignal, found)

	def test_ArchitectureDoesNotSeeBlockDeclaration(self) -> None:
		"""Resolution only walks outwards, never into a nested scope."""
		found = self._architecture._namespace.FindObject(SignalSymbol(SimpleName("x")))

		self.assertIs(self._architectureSignal, found)


class NestedBlocks(Testcase):
	"""Three levels of nesting: the innermost declaration wins, and each level keeps its own."""

	def setUp(self) -> None:
		self._outerSignal = _signal("x", "natural")
		self._outer = ConcurrentBlockStatement("outer", declaredItems=[self._outerSignal])
		self._outer.IndexDeclaredItems()

		self._middleSignal = _signal("x", "natural")
		self._middle = ConcurrentBlockStatement("middle", declaredItems=[self._middleSignal])
		self._middle.Parent = self._outer
		self._middle.IndexDeclaredItems()

		self._innerSignal = _signal("x", "natural")
		self._inner = ConcurrentBlockStatement("inner", declaredItems=[self._innerSignal])
		self._inner.Parent = self._middle
		self._inner.IndexDeclaredItems()

	def test_InnermostDeclarationWins(self) -> None:
		self.assertIs(self._innerSignal, self._inner._namespace.FindObject(SignalSymbol(SimpleName("x"))))

	def test_EachLevelResolvesItsOwn(self) -> None:
		self.assertIs(self._middleSignal, self._middle._namespace.FindObject(SignalSymbol(SimpleName("x"))))
		self.assertIs(self._outerSignal, self._outer._namespace.FindObject(SignalSymbol(SimpleName("x"))))

	def test_UndeclaredNameWalksTheWholeChain(self) -> None:
		"""A name declared only at the outermost level is still reachable from the innermost scope."""
		onlyOutside = _signal("onlyOutside", "natural")
		self._outer._namespace._elements["onlyoutside"] = onlyOutside

		self.assertIs(onlyOutside, self._inner._namespace.FindObject(SignalSymbol(SimpleName("onlyOutside"))))


class GeneratesInsideArchitecture(Testcase):
	"""A for-generate's declarative region nests inside the enclosing architecture's."""

	def setUp(self) -> None:
		self._architectureSignal = _signal("x", "natural")
		self._architecture = Architecture(
			"rtl",
			EntitySymbol(SimpleName("ent")),
			declaredItems=[self._architectureSignal],
		)
		self._architecture.IndexDeclaredItems()

		self._generateSignal = _signal("x", "natural")
		self._generate = ForGenerateStatement(
			"gen",
			"i",
			SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To),
			declaredItems=[self._generateSignal],
		)
		self._generate.Parent = self._architecture
		self._generate.IndexDeclaredItems()

	def test_GenerateDeclarationHidesArchitectureDeclaration(self) -> None:
		found = self._generate._namespace.FindObject(SignalSymbol(SimpleName("x")))

		self.assertIs(self._generateSignal, found)

	def test_ArchitectureKeepsItsOwnDeclaration(self) -> None:
		found = self._architecture._namespace.FindObject(SignalSymbol(SimpleName("x")))

		self.assertIs(self._architectureSignal, found)
