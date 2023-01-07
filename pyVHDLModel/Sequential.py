from typing import List, Iterable, Optional as Nullable

from pyTooling.Decorators import export

from pyVHDLModel import Name, ExpressionUnion, ModelEntity
from pyVHDLModel.Association import ParameterAssociationItem
from pyVHDLModel.Common import Statement, ProcedureCall, MixinConditional, Choice, BaseCase, SignalAssignment, VariableAssignment, MixinReportStatement, \
	MixinAssertStatement, MixinIfBranch, MixinElsifBranch, MixinElseBranch, WaveformElement, Range


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
	def __init__(self, procedureName: Name, parameterMappings: Iterable[ParameterAssociationItem] = None, label: str = None):
		super().__init__(label)
		ProcedureCall.__init__(self, procedureName, parameterMappings)


@export
class SequentialChoice(Choice):
	"""A ``SequentialChoice`` is a base-class for all sequential choices (in case statements)."""


@export
class SequentialCase(BaseCase, SequentialStatements):
	_choices: List

	def __init__(self, statements: Iterable[SequentialStatement] = None):
		super().__init__()
		SequentialStatements.__init__(self, statements)

		# TODO: what about choices?

	@property
	def Choices(self) -> List[Choice]:
		return self._choices


@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignment):
	def __init__(self, target: Name, label: str = None):
		super().__init__(label)
		SignalAssignment.__init__(self, target)


@export
class SequentialSimpleSignalAssignment(SequentialSignalAssignment):
	_waveform: List[WaveformElement]

	def __init__(self, target: Name, waveform: Iterable[WaveformElement], label: str = None):
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
	def __init__(self, target: Name, expression: ExpressionUnion, label: str = None):
		super().__init__(label)
		VariableAssignment.__init__(self, target, expression)


@export
class SequentialReportStatement(SequentialStatement, MixinReportStatement):
	def __init__(self, message: ExpressionUnion, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinReportStatement.__init__(self, message, severity)


@export
class SequentialAssertStatement(SequentialStatement, MixinAssertStatement):
	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinAssertStatement.__init__(self, condition, message, severity)


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
class IfBranch(Branch, MixinIfBranch):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)
		MixinIfBranch.__init__(self, condition)


@export
class ElsifBranch(Branch, MixinElsifBranch):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)
		MixinElsifBranch.__init__(self, condition)


@export
class ElseBranch(Branch, MixinElseBranch):
	def __init__(self, statements: Iterable[SequentialStatement] = None):
		super().__init__(statements)
		MixinElseBranch.__init__(self)


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
class WhileLoopStatement(LoopStatement, MixinConditional):
	def __init__(self, condition: ExpressionUnion, statements: Iterable[SequentialStatement] = None, label: str = None):
		super().__init__(statements, label)
		MixinConditional.__init__(self, condition)


@export
class LoopControlStatement(SequentialStatement, MixinConditional):
	"""A ``LoopControlStatement`` is a base-class for all loop controlling statements."""

	_loopReference: LoopStatement

	def __init__(self, condition: ExpressionUnion = None, loopLabel: str = None): # TODO: is this label (currently str) a Name or a Label class?
		super().__init__()
		MixinConditional.__init__(self, condition)

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
class WaitStatement(SequentialStatement, MixinConditional):
	_sensitivityList: Nullable[List[Name]]
	_timeout:         ExpressionUnion

	def __init__(self, sensitivityList: Iterable[Name] = None, condition: ExpressionUnion = None, timeout: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		MixinConditional.__init__(self, condition)

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
	def SensitivityList(self) -> List[Name]:
		return self._sensitivityList

	@property
	def Timeout(self) -> ExpressionUnion:
		return self._timeout


@export
class ReturnStatement(SequentialStatement, MixinConditional):
	_returnValue: ExpressionUnion

	def __init__(self, returnValue: ExpressionUnion = None):
		super().__init__()
		MixinConditional.__init__(self, returnValue)

		# TODO: return value?

	@property
	def ReturnValue(self) -> ExpressionUnion:
		return self._returnValue


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
