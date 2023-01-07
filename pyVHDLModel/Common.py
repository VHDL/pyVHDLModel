from typing import List, Iterable, Optional as Nullable

from pyTooling.Decorators import export

from pyVHDLModel import ModelEntity, LabeledEntityMixin, Name, ExpressionUnion, Direction
from pyVHDLModel.Association import ParameterAssociationItem


@export
class Statement(ModelEntity, LabeledEntityMixin):
	def __init__(self, label: str = None):
		super().__init__()
		LabeledEntityMixin.__init__(self, label)


@export
class ProcedureCall:
	_procedure: Name  # TODO: implement a ProcedureSymbol
	_parameterMappings: List[ParameterAssociationItem]

	def __init__(self, procedureName: Name, parameterMappings: Iterable[ParameterAssociationItem] = None):
		self._procedure = procedureName
		procedureName._parent = self

		# TODO: extract to mixin
		self._parameterMappings = []
		if parameterMappings is not None:
			for parameterMapping in parameterMappings:
				self._parameterMappings.append(parameterMapping)
				parameterMapping._parent = self

	@property
	def Procedure(self) -> Name:
		return self._procedure

	@property
	def ParameterMappings(self) -> List[ParameterAssociationItem]:
		return self._parameterMappings


@export
class MixinConditional:
	"""A ``BaseConditional`` is a mixin-class for all statements with a condition."""

	_condition: ExpressionUnion

	def __init__(self, condition: ExpressionUnion = None):
		self._condition = condition
		if condition is not None:
			condition._parent = self

	@property
	def Condition(self) -> ExpressionUnion:
		return self._condition


@export
class MixinBranch:
	"""A ``BaseBranch`` is a mixin-class for all statements with branches."""

	def __init__(self):
		pass


@export
class MixinConditionalBranch(MixinBranch, MixinConditional):
	"""A ``BaseBranch`` is a mixin-class for all branch statements with a condition."""
	def __init__(self, condition: ExpressionUnion):
		super().__init__()
		MixinConditional.__init__(self, condition)


@export
class MixinIfBranch(MixinConditionalBranch):
	"""A ``BaseIfBranch`` is a mixin-class for all if-branches."""


@export
class MixinElsifBranch(MixinConditionalBranch):
	"""A ``BaseElsifBranch`` is a mixin-class for all elsif-branches."""


@export
class MixinElseBranch(MixinBranch):
	"""A ``BaseElseBranch`` is a mixin-class for all else-branches."""


@export
class Choice(ModelEntity):
	"""A ``Choice`` is a base-class for all choices."""


@export
class BaseCase(ModelEntity):
	"""
	A ``Case`` is a base-class for all cases.
	"""


@export
class Assignment:
	"""An ``Assignment`` is a base-class for all assignment statements."""

	_target:     Name

	def __init__(self, target: Name):
		self._target = target
		target._parent = self

	@property
	def Target(self) -> Name:
		return self._target


@export
class SignalAssignment(Assignment):
	"""An ``SignalAssignment`` is a base-class for all signal assignment statements."""


@export
class VariableAssignment(Assignment):
	"""An ``VariableAssignment`` is a base-class for all variable assignment statements."""

	_expression: ExpressionUnion

	def __init__(self, target: Name, expression: ExpressionUnion):
		super().__init__(target)

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression


@export
class MixinReportStatement:
	"""A ``MixinReportStatement`` is a mixin-class for all report and assert statements."""

	_message:  Nullable[ExpressionUnion]
	_severity: Nullable[ExpressionUnion]

	def __init__(self, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		self._message = message
		if message is not None:
			message._parent = self

		self._severity = severity
		if severity is not None:
			severity._parent = self

	@property
	def Message(self) -> Nullable[ExpressionUnion]:
		return self._message

	@property
	def Severity(self) -> Nullable[ExpressionUnion]:
		return self._severity


@export
class MixinAssertStatement(MixinReportStatement):
	"""A ``MixinAssertStatement`` is a mixin-class for all assert statements."""

	_condition: ExpressionUnion

	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		super().__init__(message, severity)

		self._condition = condition
		if condition is not None:
			condition._parent = self

	@property
	def Condition(self) -> ExpressionUnion:
		return self._condition


class BlockStatement:
	"""A ``BlockStatement`` is a mixin-class for all block statements."""

	# TODO: could be unified with ProcessStatement if 'List[ConcurrentStatement]' becomes parametric to T

	def __init__(self):
		pass


@export
class WaveformElement(ModelEntity):
	_expression: ExpressionUnion
	_after: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, after: ExpressionUnion = None):
		super().__init__()

		self._expression = expression
		expression._parent = self

		self._after = after
		if after is not None:
			after._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	@property
	def After(self) -> Expression:
		return self._after


@export
class Range(ModelEntity):
	_leftBound:  ExpressionUnion
	_rightBound: ExpressionUnion
	_direction:  Direction

	def __init__(self, leftBound: ExpressionUnion, rightBound: ExpressionUnion, direction: Direction):
		super().__init__()

		self._leftBound = leftBound
		leftBound._parent = self

		self._rightBound = rightBound
		rightBound._parent = self

		self._direction = direction

	@property
	def LeftBound(self) -> ExpressionUnion:
		return self._leftBound

	@property
	def RightBound(self) -> ExpressionUnion:
		return self._rightBound

	@property
	def Direction(self) -> Direction:
		return self._direction

	def __str__(self) -> str:
		return "{leftBound!s} {direction!s} {rightBound!s}".format(
			leftBound=self._leftBound,
			direction=self._direction,
			rightBound=self._rightBound,
		)
