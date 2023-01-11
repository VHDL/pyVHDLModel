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

Base-classes for the VHDL language model.
"""
from enum                  import unique, Enum
from typing                import Type, Tuple, Iterable, Optional as Nullable, Union, cast

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType


__all__ = ["ExpressionUnion"]


ExpressionUnion = Union[
	'BaseExpression',
	'QualifiedExpression',
	'FunctionCall',
	'TypeConversion',
	# ConstantOrSymbol,     TODO: ObjectSymbol
	'Literal',
]


@export
@unique
class Direction(Enum):
	"""A ``Direction`` is an enumeration and represents a direction in a range	(``to`` or ``downto``)."""

	To =      0  #: Ascending direction
	DownTo =  1  #: Descending direction

	def __str__(self):
		"""
		Formats the direction to ``to`` or ``downto``.

		:return: Formatted direction.
		"""
		return ("to", "downto")[cast(int, self.value)]       # TODO: check performance


@export
@unique
class Mode(Enum):
	"""
	A ``Mode`` is an enumeration. It represents the direction of data exchange (``in``, ``out``, ...) for objects in
	generic, port or parameter lists.

	In case no *mode* is defined, ``Default`` is used, so the *mode* is inferred from context.
	"""

	Default = 0  #: Mode not defined, thus it's context dependent.
	In =      1  #: Input
	Out =     2  #: Output
	InOut =   3  #: Bi-directional
	Buffer =  4  #: Buffered output
	Linkage = 5  #: undocumented

	def __str__(self):
		"""
		Formats the direction.

		:return: Formatted direction.
		"""
		return ("", "in", "out", "inout", "buffer", "linkage")[cast(int, self.value)]       # TODO: check performance


@export
class ModelEntity(metaclass=ExtendedType, useSlots=True):
	"""
	``ModelEntity`` is the base-class for all classes in the VHDL language model, except for mixin classes (see multiple
	inheritance) and enumerations.

	Each entity in this model has a reference to its parent entity. Therefore, a protected variable :attr:`_parent` is
	available and a readonly property :attr:`Parent`.
	"""

	_parent: 'ModelEntity'      #: Reference to a parent entity in the model.

	def __init__(self):
		"""Initializes a VHDL model entity."""

		self._parent = None

	@property
	def Parent(self) -> 'ModelEntity':
		"""
		Returns a reference to the parent entity.

		:returns: Parent entity.
		"""
		return self._parent

	def GetAncestor(self, type: Type) -> 'ModelEntity':
		parent = self._parent
		while not isinstance(parent, type):
			parent = parent._parent

		return parent


@export
class NamedEntityMixin:
	"""
	A ``NamedEntityMixin`` is a mixin class for all VHDL entities that have identifiers.

	Protected variables :attr:`_identifier` and :attr:`_normalizedIdentifier` are available to derived classes as well as
	two readonly properties :attr:`Identifier` and :attr:`NormalizedIdentifier` for public access.
	"""

	_identifier: str            #: The identifier of a model entity.
	_normalizedIdentifier: str  #: The normalized (lower case) identifier of a model entity.

	def __init__(self, identifier: str):
		"""
		Initializes a named entity.

		:param identifier: Identifier (name) of the model entity.
		"""
		self._identifier = identifier
		self._normalizedIdentifier = identifier.lower()

	@property
	def Identifier(self) -> str:
		"""
		Returns a model entity's identifier (name).

		:returns: Name of a model entity.
		"""
		return self._identifier

	@property
	def NormalizedIdentifier(self) -> str:
		"""
		Returns a model entity's normalized identifier (lower case name).

		:returns: Normalized name of a model entity.
		"""
		return self._normalizedIdentifier


@export
class MultipleNamedEntityMixin:
	"""
	A ``MultipleNamedEntityMixin`` is a mixin class for all VHDL entities that declare multiple instances at once by
	defining multiple identifiers.

	Protected variables :attr:`_identifiers` and :attr:`_normalizedIdentifiers` are available to derived classes as well
	as two readonly properties :attr:`Identifiers` and :attr:`NormalizedIdentifiers` for public access.
	"""

	_identifiers:           Tuple[str]  #: A list of identifiers.
	_normalizedIdentifiers: Tuple[str]  #: A list of normalized (lower case) identifiers.

	def __init__(self, identifiers: Iterable[str]):
		"""
		Initializes a multiple-named entity.

		:param identifiers: Sequence of identifiers (names) of the model entity.
		"""
		self._identifiers = tuple(identifiers)
		self._normalizedIdentifiers = tuple([identifier.lower() for identifier in identifiers])

	@property
	def Identifiers(self) -> Tuple[str]:
		"""
		Returns a model entity's tuple of identifiers (names).

		:returns: Tuple of identifiers.
		"""
		return self._identifiers

	@property
	def NormalizedIdentifiers(self) -> Tuple[str]:
		"""
		Returns a model entity's tuple of normalized identifiers (lower case names).

		:returns: Tuple of normalized identifiers.
		"""
		return self._normalizedIdentifiers


@export
class LabeledEntityMixin:
	"""
	A ``LabeledEntityMixin`` is a mixin class for all VHDL entities that can have labels.

	protected variables :attr:`_label` and :attr:`_normalizedLabel` are available to derived classes as well as two
	readonly properties :attr:`Label` and :attr:`NormalizedLabel` for public access.
	"""
	_label:           Nullable[str]  #: The label of a model entity.
	_normalizedLabel: Nullable[str]  #: The normalized (lower case) label of a model entity.

	def __init__(self, label: Nullable[str]):
		"""
		Initializes a labeled entity.

		:param label: Label of the model entity.
		"""
		self._label = label
		self._normalizedLabel = label.lower() if label is not None else None

	@property
	def Label(self) -> Nullable[str]:
		"""
		Returns a model entity's label.

		:returns: Label of a model entity.
		"""
		return self._label

	@property
	def NormalizedLabel(self) -> Nullable[str]:
		"""
		Returns a model entity's normalized (lower case) label.

		:returns: Normalized label of a model entity.
		"""
		return self._normalizedLabel


@export
class DocumentedEntityMixin:
	"""
	A ``DocumentedEntityMixin`` is a mixin class for all VHDL entities that can have an associated documentation.

	A protected variable :attr:`_documentation` is available to derived classes as well as a readonly property
	:attr:`Documentation` for public access.
	"""

	_documentation: Nullable[str]  #: The associated documentation of a model entity.

	def __init__(self, documentation: Nullable[str]):
		"""
		Initializes a documented entity.

		:param documentation: Documentation of a model entity.
		"""
		self._documentation = documentation

	@property
	def Documentation(self) -> Nullable[str]:
		"""
		Returns a model entity's associated documentation.

		:returns: Associated documentation of a model entity.
		"""
		return self._documentation


@export
class ConditionalMixin:
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
class BranchMixin:
	"""A ``BaseBranch`` is a mixin-class for all statements with branches."""

	def __init__(self):
		pass


@export
class ConditionalBranchMixin(BranchMixin, ConditionalMixin):
	"""A ``BaseBranch`` is a mixin-class for all branch statements with a condition."""
	def __init__(self, condition: ExpressionUnion):
		super().__init__()
		ConditionalMixin.__init__(self, condition)


@export
class IfBranchMixin(ConditionalBranchMixin):
	"""A ``BaseIfBranch`` is a mixin-class for all if-branches."""


@export
class ElsifBranchMixin(ConditionalBranchMixin):
	"""A ``BaseElsifBranch`` is a mixin-class for all elsif-branches."""


@export
class ElseBranchMixin(BranchMixin):
	"""A ``BaseElseBranch`` is a mixin-class for all else-branches."""


@export
class ReportStatementMixin:
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
class AssertStatementMixin(ReportStatementMixin, ConditionalMixin):
	"""A ``MixinAssertStatement`` is a mixin-class for all assert statements."""

	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion = None, severity: ExpressionUnion = None):
		super().__init__(message, severity)
		ConditionalMixin.__init__(self, condition)


class BlockStatementMixin:
	"""A ``BlockStatement`` is a mixin-class for all block statements."""

	def __init__(self):
		pass


@export
class BaseChoice(ModelEntity):
	"""A ``Choice`` is a base-class for all choices."""


@export
class BaseCase(ModelEntity):
	"""
	A ``Case`` is a base-class for all cases.
	"""


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
