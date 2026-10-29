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
"""Tests for the walk of concurrent statements (:mod:`pyVHDLModel.Visitor`)."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Association import ParameterAssociationItem
from pyVHDLModel.Base        import WaveformElement
from pyVHDLModel.Common      import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Concurrent  import ProcessStatement, ConcurrentProcedureCall, ConcurrentSimpleSignalAssignment, \
                                    ConcurrentSelectedSignalAssignment, ConcurrentConditionalSignalAssignment, \
                                    ConcurrentAssertStatement
from pyVHDLModel.Expression  import IntegerLiteral, StringLiteral
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Sequential  import IndexedChoice
from pyVHDLModel.Symbol      import SignalSymbol, SimpleObjectOrFunctionCallSymbol

from tests.unit.Visitor      import FullRecorder


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class SignalAssignments(Testcase):
	def test_Simple(self) -> None:
		"""Waveform elements are separated by commas; a delay follows the ``after`` event."""
		target =     SignalSymbol(SimpleName("q"))
		first =      IntegerLiteral(1)
		delay =      IntegerLiteral(5)
		second =     IntegerLiteral(0)
		element1 =   WaveformElement(first, delay)
		element2 =   WaveformElement(second)
		assignment = ConcurrentSimpleSignalAssignment(None, target, [element1, element2])
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual([
			("VisitConcurrentSimpleSignalAssignment",  assignment),
			("VisitSymbol",                            target),
			("VisitSimpleName",                        target.Name),
			("DepartSimpleName",                       target.Name),
			("DepartSymbol",                           target),
			("VisitSignalAssignment",                  assignment),
			("VisitWaveformElement",                   element1),
			("VisitIntegerLiteral",                    first),
			("DepartIntegerLiteral",                   first),
			("VisitAfter",                             element1),
			("VisitIntegerLiteral",                    delay),
			("DepartIntegerLiteral",                   delay),
			("DepartWaveformElement",                  element1),
			("VisitWaveformSeparator",                 assignment),
			("VisitWaveformElement",                   element2),
			("VisitIntegerLiteral",                    second),
			("DepartIntegerLiteral",                   second),
			("DepartWaveformElement",                  element2),
			("DepartConcurrentSimpleSignalAssignment", assignment),
		], recorder.Events)

	def test_Conditional(self) -> None:
		condition =  SimpleObjectOrFunctionCallSymbol(SimpleName("c"))
		first =      ConditionalWaveform([WaveformElement(IntegerLiteral(1))], condition)
		second =     ConditionalWaveform([WaveformElement(IntegerLiteral(0))])
		assignment = ConcurrentConditionalSignalAssignment(None, SignalSymbol(SimpleName("q")), [first, second])
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual(
			[("VisitConditionalWaveform", first), ("VisitWhen", first), ("DepartConditionalWaveform", first),
			 ("VisitElse", assignment), ("VisitConditionalWaveform", second), ("DepartConditionalWaveform", second)],
			[event for event in recorder.Events if event[0] in (
				"VisitConditionalWaveform", "DepartConditionalWaveform", "VisitWhen", "VisitElse"
			)]
		)

	def test_Selected(self) -> None:
		"""The choices of a selected waveform follow the ``when`` event and are separated by vertical lines."""
		selector =   SimpleObjectOrFunctionCallSymbol(SimpleName("sel"))
		target =     SignalSymbol(SimpleName("q"))
		choice1 =    IndexedChoice(IntegerLiteral(0))
		choice2 =    IndexedChoice(IntegerLiteral(1))
		selected =   SelectedWaveform([choice1, choice2], [WaveformElement(IntegerLiteral(1))])
		others =     OthersSelectedWaveform([WaveformElement(IntegerLiteral(0))])
		assignment = ConcurrentSelectedSignalAssignment(None, target, selector, [selected, others])
		recorder =   FullRecorder()

		assignment.Visit(recorder)

		self.assertEqual([
			"VisitConcurrentSelectedSignalAssignment",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitSelect",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitSignalAssignment",
			"VisitSelectedWaveform",
			"VisitWaveformElement", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartWaveformElement",
			"VisitWhen",
			"VisitIndexedChoice", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartIndexedChoice",
			"VisitBar",
			"VisitIndexedChoice", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartIndexedChoice",
			"DepartSelectedWaveform",
			"VisitSelectedAlternativeSeparator",
			"VisitOthersSelectedWaveform",
			"VisitWaveformElement", "VisitIntegerLiteral", "DepartIntegerLiteral", "DepartWaveformElement",
			"VisitWhen",
			"DepartOthersSelectedWaveform",
			"DepartConcurrentSelectedSignalAssignment",
		], [event[0] for event in recorder.Events])


class Statements(Testcase):
	def test_Process(self) -> None:
		clock =    SimpleName("clk")
		reset =    SimpleName("rst")
		process =  ProcessStatement("p", sensitivityList=[clock, reset])
		recorder = FullRecorder()

		process.Visit(recorder)

		self.assertEqual([
			("VisitProcessStatement",  process),
			("VisitSensitivityList",   process),
			("VisitSimpleName",        clock),
			("DepartSimpleName",       clock),
			("VisitNameListSeparator", process),
			("VisitSimpleName",        reset),
			("DepartSimpleName",       reset),
			("DepartSensitivityList",  process),
			("VisitIs",                process),
			("VisitBegin",             process),
			("DepartProcessStatement", process),
		], recorder.Events)

	def test_Process_WithoutSensitivityList(self) -> None:
		process =  ProcessStatement()
		recorder = FullRecorder()

		process.Visit(recorder)

		self.assertEqual(
			["VisitProcessStatement", "VisitIs", "VisitBegin", "DepartProcessStatement"],
			[event[0] for event in recorder.Events]
		)

	def test_ProcedureCall(self) -> None:
		procedure =   SimpleObjectOrFunctionCallSymbol(SimpleName("check"))
		actual =      SimpleObjectOrFunctionCallSymbol(SimpleName("clk"))
		association = ParameterAssociationItem(None, actual)
		call =        ConcurrentProcedureCall(None, procedure, [association])
		recorder =    FullRecorder()

		call.Visit(recorder)

		self.assertEqual([
			"VisitConcurrentProcedureCall",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitActualParameterPart",
			"VisitAssociationItem", "VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"DepartAssociationItem",
			"DepartActualParameterPart",
			"DepartConcurrentProcedureCall",
		], [event[0] for event in recorder.Events])

	def test_Assert(self) -> None:
		condition = SimpleObjectOrFunctionCallSymbol(SimpleName("ok"))
		message =   StringLiteral("failed")
		severity =  SimpleObjectOrFunctionCallSymbol(SimpleName("error"))
		assertion = ConcurrentAssertStatement(condition, message, severity)
		recorder =  FullRecorder()

		assertion.Visit(recorder)

		self.assertEqual([
			"VisitConcurrentAssertStatement",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"VisitReport",
			"VisitStringLiteral", "DepartStringLiteral",
			"VisitSeverity",
			"VisitSymbol", "VisitSimpleName", "DepartSimpleName", "DepartSymbol",
			"DepartConcurrentAssertStatement",
		], [event[0] for event in recorder.Events])
