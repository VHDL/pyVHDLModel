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
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
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
This module contains parts of an abstract document language model for VHDL.

Declarations for sequential statements.
"""
from typing                  import List, Iterable, Optional as Nullable

from pyTooling.Decorators    import export

from pyVHDLModel.Base import ModelEntity, ExpressionUnion, Range, BaseChoice, BaseCase, ConditionalMixin, IfBranchMixin, ElsifBranchMixin, ElseBranchMixin, \
	ReportStatementMixin, AssertStatementMixin, WaveformElement
from pyVHDLModel.Symbol      import Symbol
from pyVHDLModel.Common      import Statement, ProcedureCall
from pyVHDLModel.Common      import SignalAssignment, VariableAssignment
from pyVHDLModel.Association import ParameterAssociationItem


@export
class SequentialStatement(Statement):
	"""A ``SequentialStatement`` is a base-class for all sequential statements."""


@export
class SequentialStatements:
	_statements: List[SequentialStatement]

	def __init__(self, statements: Iterable[SequentialStatement] = None):
		# TODO: extract to mixin
		self._statements = []
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item._parent = self

	@property
	def Statements(self) -> List[SequentialStatement]:
		return self._statements


@export
class SequentialProcedureCall(SequentialStatement, ProcedureCall):
	def __init__(self, procedureName: Symbol, parameterMappings: Iterable[ParameterAssociationItem] = None, label: str = None):
		super().__init__(label)
		ProcedureCall.__init__(self, procedureName, parameterMappings)


@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignment):
	def __init__(self, target: Symbol, label: str = None):
		super().__init__(label)
		SignalAssignment.__init__(self, target)


@export
class SequentialSimpleSignalAssignment(SequentialSignalAssignment):
	_waveform: List[WaveformElement]

	def __init__(self, target: Symbol, waveform: Iterable[WaveformElement], label: str = None):
		super().__init__(target, label)

		# TODO: extract to mixin
		self._waveform = []
		if waveform is not None:
			for waveformElement in waveform:
				self._waveform.append(waveformElement)
				waveformElement._parent = self

	@property
	def Waveform(self) -> List[WaveformElement]:
		return self._waveform


@export
class SequentialVariableAssignment(SequentialStatement, VariableAssignment):
	def __init__(self, target: Symbol, expression: ExpressionUnion, label: str = None):
		super().__init__(label)
		VariableAssignment.__init__(self, target, expression)


@export
class SequentialReportStatement(SequentialStatement, ReportStatementMixin):
	def __init__(self, message: ExpressionUnion, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		ReportStatementMixin.__init__(self, message, severity)


@export
class SequentialAssertStatement(SequentialStatement, AssertStatementMixin):
	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		AssertStatementMixin.__init__(self, condition, message, severity)


@export
class CompoundStatement(SequentialStatement):
	"""A ``CompoundStatement`` is a base-class for all compound statements."""


@export
class Branch(ModelEntity, SequentialStatements):
	"""A ``Branch`` is a base-class for all branches in a if statement."""

	def __init__(self, statements: Iterable[SequentialStatement] = None):
		super().__init__()
		SequentialStatements.__init__(self, statements)


@export
class IfBranch(Branch, IfBranchMixin):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifBranch(Branch, ElsifBranchMixin):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseBranch(Branch, ElseBranchMixin):
	def __init__(self, statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)
		ElseBranchMixin.__init__(self)


@export
class IfStatement(CompoundStatement):
	_ifBranch: IfBranch
	_elsifBranches: List['ElsifBranch']
	_elseBranch: Nullable[ElseBranch]

	def __init__(self, ifBranch: IfBranch, elsifBranches: Iterable[ElsifBranch] = None, elseBranch: ElseBranch = None, label: str = None):
		super().__init__(label)

		self._ifBranch = ifBranch
		ifBranch._parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch._parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch._parent = self
		else:
			self._elseBranch = None

	@property
	def IfBranch(self) -> IfBranch:
		return self._ifBranch

	@property
	def ElsIfBranches(self) -> List['ElsifBranch']:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> Nullable[ElseBranch]:
		return self._elseBranch


@export
class SequentialChoice(BaseChoice):
	"""A ``SequentialChoice`` is a base-class for all sequential choices (in case statements)."""


@export
class IndexedChoice(SequentialChoice):
	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion):
		super().__init__()

		self._expression = expression
		# expression._parent = self    # FIXME: received None

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	def __str__(self) -> str:
		return "{expression!s}".format(expression=self._expression)


@export
class RangedChoice(SequentialChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range'):
		super().__init__()

		self._range = rng
		rng._parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return "{range!s}".format(range=self._range)


@export
class SequentialCase(BaseCase, SequentialStatements):
	_choices: List

	def __init__(self, statements: Iterable[SequentialStatement] = None):
		super().__init__()
		SequentialStatements.__init__(self, statements)

		# TODO: what about choices?

	@property
	def Choices(self) -> List[BaseChoice]:
		return self._choices


@export
class Case(SequentialCase):
	_choices: List[SequentialChoice]

	def __init__(self, choices: Iterable[SequentialChoice], statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)

		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice._parent = self

	@property
	def Choices(self) -> List[SequentialChoice]:
		return self._choices

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join([str(c) for c in self._choices]))


@export
class OthersCase(SequentialCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class CaseStatement(CompoundStatement):
	_expression: ExpressionUnion
	_cases:      List[SequentialCase]

	def __init__(self, expression: ExpressionUnion, cases: Iterable[SequentialCase], label: str = None):
		super().__init__(label)

		self._expression = expression
		expression._parent = self

		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case._parent = self

	@property
	def SelectExpression(self) -> ExpressionUnion:
		return self._expression

	@property
	def Cases(self) -> List[SequentialCase]:
		return self._cases


@export
class LoopStatement(CompoundStatement, SequentialStatements):
	"""A ``LoopStatement`` is a base-class for all loop statements."""

	def __init__(self, statements: Iterable[SequentialStatement] = None, label: str = None):
		super().__init__(label)
		SequentialStatements.__init__(self, statements)


@export
class EndlessLoopStatement(LoopStatement):
	pass


@export
class ForLoopStatement(LoopStatement):
	_loopIndex: str
	_range:     Range

	def __init__(self, loopIndex: str, rng: Range, statements: Iterable[SequentialStatement] = None, label: str = None):
		super().__init__(statements, label)

		self._loopIndex = loopIndex

		self._range = rng
		rng._parent = self

	@property
	def LoopIndex(self) -> str:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range


@export
class WhileLoopStatement(LoopStatement, ConditionalMixin):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[SequentialStatement] = None, label: str = None):
		super().__init__(statements, label)
		ConditionalMixin.__init__(self, condition)


@export
class LoopControlStatement(SequentialStatement, ConditionalMixin):
	"""A ``LoopControlStatement`` is a base-class for all loop controlling statements."""

	_loopReference: LoopStatement

	def __init__(self, condition: ExpressionUnion = None, loopLabel: str = None): # TODO: is this label (currently str) a Name or a Label class?
		super().__init__()
		ConditionalMixin.__init__(self, condition)

		# TODO: loopLabel
		# TODO: loop reference -> is it a symbol?

	@property
	def LoopReference(self) -> LoopStatement:
		return self._loopReference


@export
class NextStatement(LoopControlStatement):
	pass


@export
class ExitStatement(LoopControlStatement):
	pass


@export
class NullStatement(SequentialStatement):
	pass


@export
class ReturnStatement(SequentialStatement, ConditionalMixin):
	_returnValue: ExpressionUnion

	def __init__(self, returnValue: ExpressionUnion = None):
		super().__init__()
		ConditionalMixin.__init__(self, returnValue)

		# TODO: return value?

	@property
	def ReturnValue(self) -> ExpressionUnion:
		return self._returnValue


@export
class WaitStatement(SequentialStatement, ConditionalMixin):
	_sensitivityList: Nullable[List[Symbol]]
	_timeout:         ExpressionUnion

	def __init__(self, sensitivityList: Iterable[Symbol] = None, condition: ExpressionUnion = None, timeout: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		ConditionalMixin.__init__(self, condition)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				signalSymbol._parent = self

		self._timeout = timeout
		if timeout is not None:
			timeout._parent = self

	@property
	def SensitivityList(self) -> List[Symbol]:
		return self._sensitivityList

	@property
	def Timeout(self) -> ExpressionUnion:
		return self._timeout


@export
class SequentialDeclarations:
	_declaredItems: List

	def __init__(self, declaredItems: Iterable):
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems
