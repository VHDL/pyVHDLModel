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
"""Tests for conditional/selected/force/release assignment statements (Concurrent.py, Sequential.py, Common.py)."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import SignalSymbol, VariableSymbol
from pyVHDLModel.Base        import WaveformElement
from pyVHDLModel.Expression  import IntegerLiteral, CharacterLiteral
from pyVHDLModel.Sequential  import IndexedChoice, SequentialVariableAssignment, \
                                    SequentialConditionalVariableAssignment, SequentialConditionalSignalAssignment, \
                                    SequentialSelectedVariableAssignment, SequentialSelectedSignalAssignment, \
                                    SignalForceAssignment, SignalReleaseAssignment
from pyVHDLModel.Common      import ConditionalWaveform, ConditionalExpression, SelectedWaveform, \
                                    OthersSelectedWaveform, SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Concurrent  import ConcurrentConditionalSignalAssignment, ConcurrentSelectedSignalAssignment

from tests.unit              import _signalSymbol, _variableSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ConditionalAndSelectedBuildingBlocks(Testcase):
	def test_ConditionalWaveform(self) -> None:
		condition = IntegerLiteral(1)
		waveform = [WaveformElement(CharacterLiteral("1"))]
		cw = ConditionalWaveform(waveform, condition)

		self.assertIs(condition, cw.Condition)
		self.assertEqual(1, len(cw.Waveform))

	def test_ConditionalWaveform_FinalBranch(self) -> None:
		"""The final ('else') branch has no condition."""
		cw = ConditionalWaveform([WaveformElement(CharacterLiteral("0"))])

		self.assertIsNone(cw.Condition)

	def test_ConditionalExpression(self) -> None:
		condition = IntegerLiteral(1)
		expression = CharacterLiteral("1")
		ce = ConditionalExpression(expression, condition)

		self.assertIs(expression, ce.Expression)
		self.assertIs(condition, ce.Condition)

	def test_SelectedWaveform(self) -> None:
		choice = IndexedChoice(IntegerLiteral(0))
		waveform = [WaveformElement(CharacterLiteral("1"))]
		sw = SelectedWaveform([choice], waveform)

		self.assertEqual(1, len(sw.Choices))
		self.assertEqual(1, len(sw.Waveform))

	def test_OthersSelectedWaveform(self) -> None:
		waveform = [WaveformElement(CharacterLiteral("0"))]
		osw = OthersSelectedWaveform(waveform)

		self.assertEqual(1, len(osw.Waveform))

	def test_SelectedExpression(self) -> None:
		choice = IndexedChoice(IntegerLiteral(0))
		expression = CharacterLiteral("1")
		se = SelectedExpression([choice], expression)

		self.assertEqual(1, len(se.Choices))
		self.assertIs(expression, se.Expression)

	def test_OthersSelectedExpression(self) -> None:
		expression = CharacterLiteral("0")
		ose = OthersSelectedExpression(expression)

		self.assertIs(expression, ose.Expression)


class ConcurrentAssignments(Testcase):
	def test_ConditionalSignalAssignment(self) -> None:
		"""``s <= '1' when cond else '0';`` - regression test: this class was previously a bare stub
		accepting a single 'expression' parameter that didn't fit what a conditional signal
		assignment actually needs to store at all."""
		cw1 = ConditionalWaveform([WaveformElement(CharacterLiteral("1"))], IntegerLiteral(1))
		cw2 = ConditionalWaveform([WaveformElement(CharacterLiteral("0"))])

		assignment = ConcurrentConditionalSignalAssignment("lbl", _signalSymbol("s"), [cw1, cw2])

		self.assertEqual(2, len(assignment.ConditionalWaveforms))
		self.assertIsNone(assignment.ConditionalWaveforms[-1].Condition)

	def test_SelectedSignalAssignment(self) -> None:
		"""``with sel select s <= '1' when 0, '0' when others;`` - same kind of stub as above."""
		sw = SelectedWaveform([IndexedChoice(IntegerLiteral(0))], [WaveformElement(CharacterLiteral("1"))])
		osw = OthersSelectedWaveform([WaveformElement(CharacterLiteral("0"))])

		assignment = ConcurrentSelectedSignalAssignment("lbl", _signalSymbol("s"), IntegerLiteral(0), [sw, osw])

		self.assertEqual(2, len(assignment.SelectedWaveforms))


class SequentialAssignments(Testcase):
	def test_SimpleVariableAssignment(self) -> None:
		"""``v := '1';``"""
		assignment = SequentialVariableAssignment(_variableSymbol("v"), CharacterLiteral("1"))

		self.assertEqual("1", str(assignment.Expression))

	def test_ConditionalVariableAssignment(self) -> None:
		"""``v := '1' when cond else '0';`` (VHDL-2008)"""
		ce1 = ConditionalExpression(CharacterLiteral("1"), IntegerLiteral(1))
		ce2 = ConditionalExpression(CharacterLiteral("0"))

		assignment = SequentialConditionalVariableAssignment(_variableSymbol("v"), [ce1, ce2])

		self.assertEqual(2, len(assignment.ConditionalExpressions))
		self.assertIsNotNone(assignment.Target)

	def test_ConditionalSignalAssignment(self) -> None:
		"""``s <= '1' when cond else '0';`` (sequential form, VHDL-2008)"""
		cw1 = ConditionalWaveform([WaveformElement(CharacterLiteral("1"))], IntegerLiteral(1))
		cw2 = ConditionalWaveform([WaveformElement(CharacterLiteral("0"))])

		assignment = SequentialConditionalSignalAssignment(_signalSymbol("s"), [cw1, cw2])

		self.assertEqual(2, len(assignment.ConditionalWaveforms))

	def test_SelectedVariableAssignment(self) -> None:
		"""``with sel select v := '1' when 0, '0' when others;``"""
		se = SelectedExpression([IndexedChoice(IntegerLiteral(0))], CharacterLiteral("1"))
		ose = OthersSelectedExpression(CharacterLiteral("0"))

		assignment = SequentialSelectedVariableAssignment(_variableSymbol("v"), IntegerLiteral(0), [se, ose])

		self.assertEqual(2, len(assignment.SelectedExpressions))

	def test_SelectedSignalAssignment(self) -> None:
		"""``with sel select s <= '1' when 0, '0' when others;`` (sequential form)"""
		sw = SelectedWaveform([IndexedChoice(IntegerLiteral(0))], [WaveformElement(CharacterLiteral("1"))])
		osw = OthersSelectedWaveform([WaveformElement(CharacterLiteral("0"))])

		assignment = SequentialSelectedSignalAssignment(_signalSymbol("s"), IntegerLiteral(0), [sw, osw])

		self.assertEqual(2, len(assignment.SelectedWaveforms))

	def test_SignalForceAssignment(self) -> None:
		"""``s <= force '1';`` (VHDL-2008)"""
		assignment = SignalForceAssignment(_signalSymbol("s"), CharacterLiteral("1"))

		self.assertEqual("1", str(assignment.Expression))

	def test_SignalReleaseAssignment(self) -> None:
		"""``s <= release;`` (VHDL-2008) - no expression at all."""
		assignment = SignalReleaseAssignment(_signalSymbol("s"))

		self.assertIsNotNone(assignment.Target)
