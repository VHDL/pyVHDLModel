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
# Copyright 2017-2024 Patrick Lehmann - Boetzingen, Germany                                                            #
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

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity, ExpressionUnion, Range, BaseChoice, BaseCase, ConditionalMixin, IfBranchMixin, ElsifBranchMixin
from pyVHDLModel.Base        import ElseBranchMixin, ReportStatementMixin, AssertStatementMixin, WaveformElement
from pyVHDLModel.Symbol      import Symbol
from pyVHDLModel.Common      import Statement, ProcedureCallMixin
from pyVHDLModel.Common      import SignalAssignmentMixin, VariableAssignmentMixin
from pyVHDLModel.Association import ParameterAssociationItem


@export
class SequentialStatement(Statement):
	"""A ``SequentialStatement`` is a base-class for all sequential statements."""


@export
class SequentialStatementsMixin(metaclass=ExtendedType, mixin=True):
	_statements: List[SequentialStatement]

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None) -> None:
		# TODO: extract to mixin
		self._statements = []
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item._parent = self

	@readonly
	def Statements(self) -> List[SequentialStatement]:
		"""
		Read-only property to access the list of sequential statements (:attr:`_statements`).

		:returns: A list of sequential statements.
		"""
		return self._statements


@export
class SequentialProcedureCall(SequentialStatement, ProcedureCallMixin):
	def __init__(
		self,
		procedureName: Symbol,
		parameterMappings: Nullable[Iterable[ParameterAssociationItem]] = None,
		label: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(label, parent)
		ProcedureCallMixin.__init__(self, procedureName, parameterMappings)


@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignmentMixin):
	def __init__(self, target: Symbol, label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class SequentialSimpleSignalAssignment(SequentialSignalAssignment):
	_waveform: List[WaveformElement]

	def __init__(self, target: Symbol, waveform: Iterable[WaveformElement], label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(target, label, parent)

		# TODO: extract to mixin
		self._waveform = []
		if waveform is not None:
			for waveformElement in waveform:
				self._waveform.append(waveformElement)
				waveformElement._parent = self

	@readonly
	def Waveform(self) -> List[WaveformElement]:
		"""
		Read-only property to access the list waveform elements (:attr:`_waveform`).

		:returns: A list of waveform elements.
		"""
		return self._waveform


@export
class SequentialVariableAssignment(SequentialStatement, VariableAssignmentMixin):
	def __init__(self, target: Symbol, expression: ExpressionUnion, label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(label, parent)
		VariableAssignmentMixin.__init__(self, target, expression)


@export
class SequentialReportStatement(SequentialStatement, ReportStatementMixin):
	def __init__(self, message: ExpressionUnion, severity: Nullable[ExpressionUnion] = None, label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(label, parent)
		ReportStatementMixin.__init__(self, message, severity)


@export
class SequentialAssertStatement(SequentialStatement, AssertStatementMixin):
	def __init__(
		self,
		condition: ExpressionUnion,
		message: Nullable[ExpressionUnion] = None,
		severity: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(label, parent)
		AssertStatementMixin.__init__(self, condition, message, severity)


@export
class CompoundStatement(SequentialStatement):
	"""A ``CompoundStatement`` is a base-class for all compound statements."""


@export
class Branch(ModelEntity, SequentialStatementsMixin):
	"""A ``Branch`` is a base-class for all branches in a if statement."""

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		SequentialStatementsMixin.__init__(self, statements)


@export
class IfBranch(Branch, IfBranchMixin):
	def __init__(self, condition: ExpressionUnion, statements: Nullable[Iterable[SequentialStatement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(statements, parent)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifBranch(Branch, ElsifBranchMixin):
	def __init__(self, condition: ExpressionUnion, statements: Nullable[Iterable[SequentialStatement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(statements, parent)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseBranch(Branch, ElseBranchMixin):
	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(statements, parent)
		ElseBranchMixin.__init__(self)


@export
class IfStatement(CompoundStatement):
	_ifBranch: IfBranch
	_elsifBranches: List['ElsifBranch']
	_elseBranch: Nullable[ElseBranch]

	def __init__(
		self,
		ifBranch: IfBranch,
		elsifBranches: Nullable[Iterable[ElsifBranch]] = None,
		elseBranch: Nullable[ElseBranch] = None,
		label: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(label, parent)

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

	@readonly
	def IfBranch(self) -> IfBranch:
		"""
		Read-only property to access the if-branch of the if-statement (:attr:`_ifBranch`).

		:returns: The if-branch.
		"""
		return self._ifBranch

	@property
	def ElsIfBranches(self) -> List['ElsifBranch']:
		"""
		Read-only property to access the elsif-branch of the if-statement (:attr:`_elsifBranch`).

		:returns: The elsif-branch.
		"""
		return self._elsifBranches

	@property
	def ElseBranch(self) -> Nullable[ElseBranch]:
		"""
		Read-only property to access the else-branch of the if-statement (:attr:`_elseBranch`).

		:returns: The else-branch.
		"""
		return self._elseBranch


@export
class SequentialChoice(BaseChoice):
	"""A ``SequentialChoice`` is a base-class for all sequential choices (in case statements)."""


@export
class IndexedChoice(SequentialChoice):
	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, parent: ModelEntity = None) -> None:
		super().__init__(parent)

		self._expression = expression
		# expression._parent = self    # FIXME: received None

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	def __str__(self) -> str:
		return str(self._expression)


@export
class RangedChoice(SequentialChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range', parent: ModelEntity = None) -> None:
		super().__init__(parent)

		self._range = rng
		rng._parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return str(self._range)


@export
class SequentialCase(BaseCase, SequentialStatementsMixin):
	_choices: List

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		SequentialStatementsMixin.__init__(self, statements)

		# TODO: what about choices?

	@property
	def Choices(self) -> List[BaseChoice]:
		return self._choices


@export
class Case(SequentialCase):
	def __init__(self, choices: Iterable[SequentialChoice], statements: Nullable[Iterable[SequentialStatement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(statements, parent)

		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice._parent = self

	@property
	def Choices(self) -> List[SequentialChoice]:
		return self._choices

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join(str(c) for c in self._choices))


@export
class OthersCase(SequentialCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class CaseStatement(CompoundStatement):
	_expression: ExpressionUnion
	_cases:      List[SequentialCase]

	def __init__(self, expression: ExpressionUnion, cases: Iterable[SequentialCase], label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(label, parent)

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
class LoopStatement(CompoundStatement, SequentialStatementsMixin):
	"""A ``LoopStatement`` is a base-class for all loop statements."""

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(label, parent)
		SequentialStatementsMixin.__init__(self, statements)


@export
class EndlessLoopStatement(LoopStatement):
	pass


@export
class ForLoopStatement(LoopStatement):
	_loopIndex: str
	_range:     Range

	def __init__(self, loopIndex: str, rng: Range, statements: Nullable[Iterable[SequentialStatement]] = None, label: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(statements, label, parent)

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
	def __init__(
		self,
		condition: ExpressionUnion,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		label: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(statements, label, parent)
		ConditionalMixin.__init__(self, condition)


@export
class LoopControlStatement(SequentialStatement, ConditionalMixin):
	"""A ``LoopControlStatement`` is a base-class for all loop controlling statements."""

	_loopReference: LoopStatement

	def __init__(self, condition: Nullable[ExpressionUnion] = None, loopLabel: Nullable[str] = None, parent: ModelEntity = None) -> None:  # TODO: is this label (currently str) a Name or a Label class?
		super().__init__(parent)
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

	def __init__(self, returnValue: Nullable[ExpressionUnion] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		ConditionalMixin.__init__(self, returnValue)

		# TODO: return value?

	@property
	def ReturnValue(self) -> ExpressionUnion:
		return self._returnValue


@export
class WaitStatement(SequentialStatement, ConditionalMixin):
	_sensitivityList: Nullable[List[Symbol]]
	_timeout:         ExpressionUnion

	def __init__(
		self,
		sensitivityList: Nullable[Iterable[Symbol]] = None,
		condition: Nullable[ExpressionUnion] = None,
		timeout: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(label, parent)
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
class SequentialDeclarationsMixin(metaclass=ExtendedType, mixin=True):
	_declaredItems: List

	def __init__(self, declaredItems: Iterable) -> None:
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems
