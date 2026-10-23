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
Tests for pyVHDLModel.Base.

Level-1 tests: instantiate each mixin's simplest real consumer and check construction, property
access and parent-wiring. A mixin has no independent existence (mixin classes here can't be
instantiated standalone - they rely on the composed class's slots), so each is tested through its
narrowest real consumer rather than a synthetic stand-in class.

Mixins already fully exercised elsewhere are intentionally not repeated here:

- ``NamedEntityMixin``, ``ConditionalMixin`` - covered via tests/unit/Hierarchy.py and
  tests/unit/Assignment.py (``ConditionalWaveform``) respectively.
- ``ChoicesMixin`` with a non-empty choice list - covered via tests/unit/Assignment.py
  (``SelectedWaveform`` et al.). Only the ``choices=None`` default path is added here.
"""
from pyTooling.MetaClasses   import AbstractClassError
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import Direction, Mode, ModelEntity, Range, RangeFromName, ReservedWord, SimpleRange
from pyVHDLModel.Base        import WaveformElement
from pyVHDLModel.Expression  import IntegerLiteral, CharacterLiteral
from pyVHDLModel.Interface   import InterfaceGroup
from pyVHDLModel.Sequential  import IfBranch, ElsifBranch, ElseBranch, SequentialReportStatement, SequentialAssertStatement, SequentialCase
from pyVHDLModel.Concurrent  import ConcurrentBlockStatement
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Object      import Signal
from pyVHDLModel.Symbol      import ConstrainedScalarSubtypeSymbol, SimpleSubtypeSymbol

from tests.unit              import _Element


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ReservedWordEnum(Testcase):
	def test_Count(self) -> None:
		"""IEEE Std 1076-2019, 15.10 reserves 116 words."""
		self.assertEqual(116, len(ReservedWord))

	def test_Value(self) -> None:
		"""A member is a string: the reserved word in lower case."""
		self.assertIsInstance(ReservedWord.DownTo, str)
		self.assertEqual("downto", ReservedWord.DownTo)
		self.assertEqual("protected", str(ReservedWord.Protected))

	def test_Values(self) -> None:
		for member in ReservedWord:
			with self.subTest(member=member.name):
				self.assertRegex(member.value, r"^[a-z][a-z_]*$")
				self.assertEqual(member.value, member.name.lower())

	def test_Parse(self) -> None:
		self.assertIs(ReservedWord.View, ReservedWord.Parse("view"))
		self.assertIs(ReservedWord.VPkg, ReservedWord.Parse("vpkg"))

	def test_Parse_NotReserved(self) -> None:
		"""``inherit`` and ``restrict_guarantee`` aren't reserved in VHDL-2019; GHDL rejects them as identifiers."""
		for word in ("inherit", "restrict_guarantee"):
			with self.subTest(word=word):
				with self.assertRaises(ValueError):
					ReservedWord.Parse(word)


class DirectionEnum(Testcase):
	def test_To(self) -> None:
		self.assertEqual("to", str(Direction.To))

	def test_DownTo(self) -> None:
		self.assertEqual("downto", str(Direction.DownTo))

	def test_ReservedWord(self) -> None:
		self.assertIs(ReservedWord.To, Direction.To.ReservedWord)
		self.assertIs(ReservedWord.DownTo, Direction.DownTo.ReservedWord)


class ModeEnum(Testcase):
	def test_AllValues(self) -> None:
		"""Every ``Mode`` value has a dedicated formatting slot in ``Mode.__str__``'s lookup tuple."""
		expected = {
			Mode.Default: "",
			Mode.In:      "in",
			Mode.Out:     "out",
			Mode.InOut:   "inout",
			Mode.Buffer:  "buffer",
			Mode.Linkage: "linkage",
		}

		for mode, text in expected.items():
			self.assertEqual(text, str(mode))

	def test_ReservedWord(self) -> None:
		"""Every mode but ``Default`` has a reserved word, spelled as ``str()`` formats the mode."""
		self.assertIsNone(Mode.Default.ReservedWord)
		for mode in (Mode.In, Mode.Out, Mode.InOut, Mode.Buffer, Mode.Linkage):
			with self.subTest(mode=mode.name):
				self.assertIsInstance(mode.ReservedWord, ReservedWord)
				self.assertEqual(str(mode), mode.ReservedWord)


class ModelEntities(Testcase):
	def test_Abstract(self) -> None:
		"""``ModelEntity`` is abstract: only derived classes are instantiated."""
		with self.assertRaises(AbstractClassError):
			ModelEntity()

	def test_NoParent(self) -> None:
		entity = _Element()

		self.assertIsNone(entity.Parent)

	def test_ConstructedWithParent(self) -> None:
		parent = _Element()
		entity = _Element(parent=parent)

		self.assertIs(parent, entity.Parent)

	def test_ParentSetter(self) -> None:
		parent = _Element()
		entity = _Element()
		entity.Parent = parent

		self.assertIs(parent, entity.Parent)

	def test_ParentSetter_RejectsNone(self) -> None:
		"""Unlike the constructor (where omitting ``parent`` is normal for a not-yet-attached root), the
		``Parent`` setter rejects ``None`` outright - it's only ever used to attach an entity to a real
		parent after the fact."""
		entity = _Element(parent=_Element())

		with self.assertRaises(ValueError):
			entity.Parent = None


class OptionallyNamedEntity(Testcase):
	"""``InterfaceGroup`` is the only current consumer of ``OptionallyNamedEntityMixin``."""

	def test_WithName(self) -> None:
		group = InterfaceGroup("generics")

		self.assertEqual("generics", group.Identifier)
		self.assertEqual("generics", group.NormalizedIdentifier)

	def test_WithoutName(self) -> None:
		group = InterfaceGroup()

		self.assertIsNone(group.Identifier)
		self.assertIsNone(group.NormalizedIdentifier)

	def test_NameIsNormalized(self) -> None:
		group = InterfaceGroup("Generics")

		self.assertEqual("generics", group.NormalizedIdentifier)


class MultipleNamedEntity(Testcase):
	"""``Signal`` is tested as a consumer of ``MultipleNamedEntityMixin``."""

	def test_Identifiers_Iterator(self) -> None:
		"""Identifiers from a single-pass iterable are normalized too."""
		signal = Signal(iter(("a", "B")), SimpleSubtypeSymbol(SimpleName("bit")))

		self.assertEqual(("a", "B"), signal.Identifiers)
		self.assertEqual(("a", "b"), signal.NormalizedIdentifiers)


class BranchMixins(Testcase):
	"""``IfBranch``/``ElsifBranch``/``ElseBranch`` are the only consumers of ``BranchMixin``,
	``ConditionalBranchMixin`` and the ``If-``/``Elsif-``/``ElseBranchMixin`` variants."""

	def test_IfBranch(self) -> None:
		condition = IntegerLiteral(1)
		branch = IfBranch(condition)

		self.assertIs(condition, branch.Condition)
		self.assertEqual(0, len(branch.Statements))

	def test_ElsifBranch(self) -> None:
		condition = IntegerLiteral(1)
		branch = ElsifBranch(condition)

		self.assertIs(condition, branch.Condition)

	def test_ElseBranch(self) -> None:
		"""The ``else`` branch has no condition at all - ``ElseBranchMixin`` doesn't inherit
		``ConditionalMixin``."""
		branch = ElseBranch()

		self.assertEqual(0, len(branch.Statements))


class ReportAndAssertStatementMixins(Testcase):
	def test_ReportStatement_MessageAndSeverity(self) -> None:
		message = CharacterLiteral("a")
		severity = IntegerLiteral(1)
		statement = SequentialReportStatement(message, severity)

		self.assertIs(message, statement.Message)
		self.assertIs(severity, statement.Severity)

	def test_ReportStatement_MessageOnly(self) -> None:
		"""``severity`` genuinely defaults to omitted in the grammar (``report "msg";`` without a
		``severity`` clause)."""
		message = CharacterLiteral("a")
		statement = SequentialReportStatement(message)

		self.assertIs(message, statement.Message)
		self.assertIsNone(statement.Severity)

	def test_AssertStatement(self) -> None:
		"""``AssertStatementMixin`` adds a required ``Condition`` on top of ``ReportStatementMixin``'s
		optional message/severity."""
		condition = IntegerLiteral(1)
		message = CharacterLiteral("a")
		statement = SequentialAssertStatement(condition, message)

		self.assertIs(condition, statement.Condition)
		self.assertIs(message, statement.Message)
		self.assertIsNone(statement.Severity)


class BlockStatementMixinHost(Testcase):
	"""``ConcurrentBlockStatement`` is the only consumer of ``BlockStatementMixin``. Also covers
	``LabeledEntityMixin.NormalizedLabel``, which no other current test reads (only ``.Label``)."""

	def test_MinimalBlock(self) -> None:
		block = ConcurrentBlockStatement("BLK")

		self.assertEqual("BLK", block.Label)
		self.assertEqual("blk", block.NormalizedLabel)


class ChoicesMixinHost(Testcase):
	def test_NoChoices(self) -> None:
		"""``choices=None`` (the default) - the non-empty-list path is already covered via
		tests/unit/Assignment.py's ``SelectedWaveform``/``SelectedExpression`` tests."""
		case = SequentialCase()

		self.assertEqual(0, len(case.Choices))


class Ranges(Testcase):
	"""``SimpleRange`` (``3 downto 0``) - a concrete class defined directly in Base.py, not a mixin."""

	def test_Construction(self) -> None:
		left = IntegerLiteral(3)
		right = IntegerLiteral(0)
		rng = SimpleRange(left, right, Direction.DownTo)

		self.assertIs(left, rng.LeftBound)
		self.assertIs(right, rng.RightBound)
		self.assertIs(Direction.DownTo, rng.Direction)
		self.assertIs(rng, left.Parent)
		self.assertIs(rng, right.Parent)

	def test_ToString(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)

		self.assertEqual("0 to 7", str(rng))

	def test_IsARange(self) -> None:
		rng = SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)

		self.assertIsInstance(rng, Range)


class RangesFromName(Testcase):
	"""``RangeFromName`` (``vector'range``, ``bit``) - a range whose bounds come from a referenced symbol."""

	def test_Construction(self) -> None:
		symbol = SimpleSubtypeSymbol(SimpleName("bit"))
		rng = RangeFromName(symbol)

		self.assertIs(symbol, rng.Symbol)
		self.assertIs(rng, symbol.Parent)
		self.assertIsInstance(rng, Range)

	def test_ToStringUnresolved(self) -> None:
		rng = RangeFromName(SimpleSubtypeSymbol(SimpleName("bit")))

		# An unresolved symbol renders with a trailing question mark.
		self.assertEqual("bit?", str(rng))

	def test_ConstrainedSubtypeKeepsTypeMarkAndConstraint(self) -> None:
		# `integer range 0 to 7` - the type mark must survive alongside the range constraint.
		constraint = SimpleRange(IntegerLiteral(0), IntegerLiteral(7), Direction.To)
		symbol = ConstrainedScalarSubtypeSymbol(SimpleName("integer"), constraint)
		rng = RangeFromName(symbol)

		self.assertIs(symbol, rng.Symbol)
		self.assertIs(constraint, rng.Symbol.Constraint)
		self.assertEqual("integer", rng.Symbol.Name.Identifier)


class WaveformElements(Testcase):
	"""``WaveformElement`` (``'1' after 5 ns``) - a concrete class defined directly in Base.py, not a
	mixin. tests/unit/Assignment.py already constructs these but never reads ``.Expression``/
	``.After``."""

	def test_WithoutAfter(self) -> None:
		expression = CharacterLiteral("1")
		element = WaveformElement(expression)

		self.assertIs(expression, element.Expression)
		self.assertIsNone(element.After)

	def test_WithAfter(self) -> None:
		expression = CharacterLiteral("1")
		after = IntegerLiteral(5)
		element = WaveformElement(expression, after)

		self.assertIs(after, element.After)
		self.assertIs(element, after.Parent)
