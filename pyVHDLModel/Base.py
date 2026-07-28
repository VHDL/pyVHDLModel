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
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
from typing                import Type, Tuple, List, Iterable, Optional as Nullable, Union, cast

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
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
	"""An enumeration representing a direction in a range	(``to`` or ``downto``)."""

	To =      0  #: Ascending direction
	DownTo =  1  #: Descending direction

	def __str__(self) -> str:
		"""
		Formats the direction to ``to`` or ``downto``.

		:returns: Formatted direction.
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

	def __str__(self) -> str:
		"""
		Formats the mode.

		:returns: Formatted mode.
		"""
		return ("", "in", "out", "inout", "buffer", "linkage")[cast(int, self.value)]       # TODO: check performance


@export
class ModelEntity(metaclass=ExtendedType, slots=True):
	"""
	``ModelEntity`` is the base-class for all classes in the VHDL language model, except for mixin classes (see multiple
	inheritance) and enumerations.

	Each entity in this model has a reference to its parent entity. Therefore, a protected variable :attr:`_parent` is
	available and a readonly property :attr:`Parent`.
	"""

	_parent: 'ModelEntity'      #: Reference to a parent entity in the logical model hierarchy.

	def __init__(self, parent: Nullable["ModelEntity"] = None) -> None:
		"""
		Initializes a VHDL model entity.

		:param parent: The parent model entity of this entity.
		"""
		self._parent = parent

	@property
	def Parent(self) -> 'ModelEntity':
		"""
		Property to access the model entity's parent element reference in a logical hierarchy (:attr:`_parent`).

		:returns: Reference to the parent entity.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: 'ModelEntity') -> None:
		if parent is None:
			raise ValueError("Parameter 'parent' is None.")

		self._parent = parent

	def GetAncestor(self, type: Type) -> 'ModelEntity':
		"""
		Return the closest ancestor of the given ``type`` found by walking the parent chain upwards.

		Iterates the parent chain - starting at this model entity - upwards (toward the root of the model) until an
		ancestor of the requested type is found.

		:param type:                Class (type) of the ancestor to find.
		:returns:                   The closest ancestor of the requested type.
		:raises VHDLModelException: If the root of the model is reached without finding an ancestor of the requested
		                            type.
		"""
		# Deferred import to avoid a circular import: Base -> Exception -> Symbol -> Base.
		from pyVHDLModel.Exception import VHDLModelException

		parent = self._parent
		while parent is not None:
			if isinstance(parent, type):
				break

			parent = parent._parent
		else:
			raise VHDLModelException(f"No ancestor of type '{type.__name__}' found for {self!r}.")

		return parent


@export
class NamedEntityMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``NamedEntityMixin`` is a mixin class for all VHDL entities that have an identifier.

	Protected variables :attr:`_identifier` and :attr:`_normalizedIdentifier` are available to derived classes as well as
	two readonly properties :attr:`Identifier` and :attr:`NormalizedIdentifier` for public access.

	.. seealso::

	   * :class:`Attribute <pyVHDLModel.Declaration.Attribute>`
	   * :class:`Alias <pyVHDLModel.Declaration.Alias>`
	   * :class:`Design unit <pyVHDLModel.DesignUnit.DesignUnit>`
	   * :class:`Component <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Mode view declaration <pyVHDLModel.Interface.ModeViewDeclaration>`
	   * :class:`Interface package <pyVHDLModel.Interface.InterfacePackage>`
	   * :class:`Default clock <pyVHDLModel.PSLModel.DefaultClock>`
	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Base type <pyVHDLModel.Type.BaseType>`
	   * :class:`Library <pyVHDLModel.Library>`
	"""

	_identifier:           str  #: The identifier of a model entity.
	_normalizedIdentifier: str  #: The normalized (lower case) identifier of a model entity.

	def __init__(self, identifier: str) -> None:
		"""
		Initializes a named entity.

		:param identifier: Identifier (name) of the model entity.
		"""
		self._identifier = identifier
		self._normalizedIdentifier = identifier.lower()

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property to access the model entity's identifier (:attr:`_identifier`).

		:returns: Name of a model entity.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> str:
		"""
		Read-only property to access the model entity's normalized identifier (:attr:`_normalizedIdentifier`).

		:returns: Normalized name of a model entity.
		"""
		return self._normalizedIdentifier

	def __str__(self) -> str:
		"""
		Formats the named entity as its identifier.

		Derived classes rendering more than their name - a full declaration, say - override this and take
		priority via the MRO.

		**Format:** ``myEntity``

		:returns: The entity's identifier.
		"""
		return self._identifier


@export
class OptionallyNamedEntityMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``OptionallyNamedEntityMixin`` is a mixin class for all VHDL entities that have an optional identifier.

	Protected variables :attr:`_identifier` and :attr:`_normalizedIdentifier` are available to derived classes as well as
	two readonly properties :attr:`Identifier` and :attr:`NormalizedIdentifier` for public access.

	.. seealso::

	   * :class:`Interface group <pyVHDLModel.Interface.InterfaceGroup>`
	"""

	_identifier:           Nullable[str]  #: The identifier of a model entity.
	_normalizedIdentifier: Nullable[str]  #: The normalized (lower case) identifier of a model entity.

	def __init__(self, identifier: Nullable[str]) -> None:
		"""
		Initializes a named entity.

		:param identifier: Identifier (name) of the model entity.
		"""
		self._identifier = identifier
		self._normalizedIdentifier = identifier.lower() if identifier is not None else None

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the model entity's optional identifier (:attr:`_identifier`).

		:returns: Name of a model entity, or ``None`` if unnamed.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the model entity's optional normalized identifier (:attr:`_normalizedIdentifier`).

		:returns: Normalized name of a model entity, or ``None`` if unnamed.
		"""
		return self._normalizedIdentifier


@export
class MultipleNamedEntityMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``MultipleNamedEntityMixin`` is a mixin class for all VHDL entities that declare multiple instances at once by
	defining multiple identifiers.

	Protected variables :attr:`_identifiers` and :attr:`_normalizedIdentifiers` are available to derived classes as well
	as two readonly properties :attr:`Identifiers` and :attr:`NormalizedIdentifiers` for public access.

	.. seealso::

	   * :class:`Mode view element <pyVHDLModel.Interface.ModeViewElement>`
	   * :class:`Obj <pyVHDLModel.Object.Obj>`
	   * :class:`Record type element <pyVHDLModel.Type.RecordTypeElement>`
	"""

	_identifiers:           Tuple[str]  #: A list of identifiers.
	_normalizedIdentifiers: Tuple[str]  #: A list of normalized (lower case) identifiers.

	def __init__(self, identifiers: Iterable[str]) -> None:
		"""
		Initializes a multiple-named entity.

		:param identifiers: Sequence of identifiers (names) of the model entity.
		"""
		self._identifiers = tuple(identifiers)
		self._normalizedIdentifiers = tuple([identifier.lower() for identifier in identifiers])

	@readonly
	def Identifiers(self) -> Tuple[str]:
		"""
		Read-only property to access the model entity's identifiers (:attr:`_identifiers`).

		:returns: Tuple of identifiers.
		"""
		return self._identifiers

	@readonly
	def NormalizedIdentifiers(self) -> Tuple[str]:
		"""
		Read-only property to access the model entity's normalized identifiers (:attr:`_normalizedIdentifiers`).

		:returns: Tuple of normalized identifiers.
		"""
		return self._normalizedIdentifiers

	def __str__(self) -> str:
		"""
		Formats the named entity as its identifiers.

		A single declaration may name several entities at once, so all identifiers are rendered. Derived
		classes rendering more than their names override this and take priority via the MRO.

		**Format:** ``a, b``

		:returns: The entity's identifiers, comma-separated.
		"""
		return ", ".join(self._identifiers)


@export
def identifiersOf(item) -> Tuple[str, ...]:
	"""
	Return an item's identifier(s), regardless of how many names its declaration carries.

	VHDL entities come in two shapes: singularly named ones deriving from :class:`NamedEntityMixin`
	(``generic (type T)``, ``GenericProcedureInterfaceItem``, ...) and plurally named ones deriving from
	:class:`MultipleNamedEntityMixin`, where one declaration names several items at once
	(``port (p1, p2 : in bit)``, and every ``Constant``/``Signal``/``Variable``/``File``-derived item).

	:param item:      A singularly or plurally named entity.
	:returns:         The item's identifiers.
	:raises TypeError: If the item is neither singularly nor plurally named.

	.. seealso::

	   :func:`normalizedIdentifiersOf`
	     The same, but normalized (lower case) - use that for dictionary keys and name resolution.
	"""
	if isinstance(item, MultipleNamedEntityMixin):
		return item._identifiers
	elif isinstance(item, NamedEntityMixin):
		return (item._identifier, )

	ex = TypeError(f"Item '{item}' is neither a NamedEntityMixin nor a MultipleNamedEntityMixin.")
	ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
	raise ex


@export
def normalizedIdentifiersOf(item) -> Tuple[str, ...]:
	"""
	Return an item's normalized (lower case) identifier(s).

	This is the form used as dictionary keys and for name resolution, because VHDL identifiers are
	case-insensitive.

	:param item:      A singularly or plurally named entity.
	:returns:         The item's normalized identifiers.
	:raises TypeError: If the item is neither singularly nor plurally named.

	.. seealso::

	   :func:`identifiersOf`
	     The same, but as written in the source - use that for rendering.
	"""
	if isinstance(item, MultipleNamedEntityMixin):
		return item._normalizedIdentifiers
	elif isinstance(item, NamedEntityMixin):
		return (item._normalizedIdentifier, )

	ex = TypeError(f"Item '{item}' is neither a NamedEntityMixin nor a MultipleNamedEntityMixin.")
	ex.add_note(f"Got type '{getFullyQualifiedName(item)}'.")
	raise ex


@export
class LabeledEntityMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``LabeledEntityMixin`` is a mixin class for all VHDL entities that can have labels.

	protected variables :attr:`_label` and :attr:`_normalizedLabel` are available to derived classes as well as two
	readonly properties :attr:`Label` and :attr:`NormalizedLabel` for public access.

	.. seealso::

	   * :class:`Statement <pyVHDLModel.Common.Statement>`
	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	"""
	_label:           Nullable[str]  #: The label of a model entity.
	_normalizedLabel: Nullable[str]  #: The normalized (lower case) label of a model entity.

	def __init__(self, label: Nullable[str]) -> None:
		"""
		Initializes a labeled entity.

		:param label: Label of the model entity.
		"""
		self._label = label
		self._normalizedLabel = label.lower() if label is not None else None

	@readonly
	def Label(self) -> Nullable[str]:
		"""
		Read-only property to access the model entity's label (:attr:`_label`).

		:returns: Label of a model entity.
		"""
		return self._label

	@readonly
	def NormalizedLabel(self) -> Nullable[str]:
		"""
		Read-only property to access the model entity's normalized label (:attr:`_normalizedLabel`).

		:returns: Normalized label of a model entity.
		"""
		return self._normalizedLabel


@export
class DocumentedEntityMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``DocumentedEntityMixin`` is a mixin class for all VHDL entities that can have an associated documentation.

	A protected variable :attr:`_documentation` is available to derived classes as well as a readonly property
	:attr:`Documentation` for public access.
	"""

	_documentation: Nullable[str]  #: The associated documentation of a model entity.

	def __init__(self, documentation: Nullable[str]) -> None:
		"""
		Initializes a documented entity.

		:param documentation: Documentation of a model entity.
		"""
		self._documentation = documentation

	@readonly
	def Documentation(self) -> Nullable[str]:
		"""
		Read-only property to access the model entity's documentation (:attr:`_documentation`).

		:returns: Associated documentation of a model entity.
		"""
		return self._documentation


@export
class ConditionalMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``ConditionalMixin`` is a mixin-class for all statements with a condition.

	.. seealso::

	   * :class:`Conditional branch mixin <pyVHDLModel.Base.ConditionalBranchMixin>`
	   * :class:`Assert statement mixin <pyVHDLModel.Base.AssertStatementMixin>`
	   * :class:`Conditional waveform <pyVHDLModel.Common.ConditionalWaveform>`
	   * :class:`Conditional expression <pyVHDLModel.Common.ConditionalExpression>`
	   * :class:`While loop statement <pyVHDLModel.Sequential.WhileLoopStatement>`
	   * :class:`Loop control statement <pyVHDLModel.Sequential.LoopControlStatement>`
	   * :class:`Wait statement <pyVHDLModel.Sequential.WaitStatement>`
	"""

	_condition: ExpressionUnion  #: The condition guarding this statement.

	def __init__(self, condition: Nullable[ExpressionUnion] = None) -> None:
		"""
		Initializes a statement with a condition.

		When the condition is not None, the condition's parent reference is set to this statement.

		:param condition: The expression representing the condition.
		"""
		self._condition = condition
		if condition is not None:
			condition.Parent = self

	@readonly
	def Condition(self) -> ExpressionUnion:
		"""
		Read-only property to access the condition of a statement (:attr:`_condition`).

		:returns: The expression representing the condition of a statement.
		"""
		return self._condition


@export
class BranchMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``BranchMixin`` is a mixin-class for all statements with branches.

	.. seealso::

	   * :class:`Conditional branch mixin <pyVHDLModel.Base.ConditionalBranchMixin>`
	   * :class:`Else branch mixin <pyVHDLModel.Base.ElseBranchMixin>`
	"""

	def __init__(self) -> None:
		"""
		Initializes a branch.
		"""
		pass


@export
class ConditionalBranchMixin(BranchMixin, ConditionalMixin, mixin=True):
	"""
	A ``BaseBranch`` is a mixin-class for all branch statements with a condition.

	.. seealso::

	   * :class:`If branch mixin <pyVHDLModel.Base.IfBranchMixin>`
	   * :class:`Elsif branch mixin <pyVHDLModel.Base.ElsifBranchMixin>`
	"""
	def __init__(self, condition: ExpressionUnion) -> None:
		"""
		Initializes a conditional branch.

		:param condition: The condition guarding this statement.
		"""
		super().__init__()
		ConditionalMixin.__init__(self, condition)


@export
class IfBranchMixin(ConditionalBranchMixin, mixin=True):
	"""
	A ``BaseIfBranch`` is a mixin-class for all if-branches.

	.. seealso::

	   * :class:`If generate branch <pyVHDLModel.Concurrent.IfGenerateBranch>`
	   * :class:`If branch <pyVHDLModel.Sequential.IfBranch>`
	"""


@export
class ElsifBranchMixin(ConditionalBranchMixin, mixin=True):
	"""
	A ``BaseElsifBranch`` is a mixin-class for all elsif-branches.

	.. seealso::

	   * :class:`Elsif generate branch <pyVHDLModel.Concurrent.ElsifGenerateBranch>`
	   * :class:`Elsif branch <pyVHDLModel.Sequential.ElsifBranch>`
	"""


@export
class ElseBranchMixin(BranchMixin, mixin=True):
	"""
	A ``BaseElseBranch`` is a mixin-class for all else-branches.

	.. seealso::

	   * :class:`Else generate branch <pyVHDLModel.Concurrent.ElseGenerateBranch>`
	   * :class:`Else branch <pyVHDLModel.Sequential.ElseBranch>`
	"""


@export
class ReportStatementMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``MixinReportStatement`` is a mixin-class for all report and assert statements.

	.. seealso::

	   * :class:`Assert statement mixin <pyVHDLModel.Base.AssertStatementMixin>`
	   * :class:`Sequential report statement <pyVHDLModel.Sequential.SequentialReportStatement>`
	"""

	_message:  Nullable[ExpressionUnion]  #: The reported message, or ``None`` if none was given.
	_severity: Nullable[ExpressionUnion]  #: The reported severity level, or ``None`` if none was given.

	def __init__(self, message: Nullable[ExpressionUnion] = None, severity: Nullable[ExpressionUnion] = None) -> None:
		"""
		Initializes a report statement.

		:param message:  The reported message, or ``None`` if none was given.
		:param severity: The reported severity level, or ``None`` if none was given.
		"""
		self._message = message
		if message is not None:
			message.Parent = self

		self._severity = severity
		if severity is not None:
			severity.Parent = self

	@readonly
	def Message(self) -> Nullable[ExpressionUnion]:
		"""
		Read-only property to access the message (:attr:`_message`).

		:returns: The message, or ``None`` if not set.
		"""
		return self._message

	@readonly
	def Severity(self) -> Nullable[ExpressionUnion]:
		"""
		Read-only property to access the severity (:attr:`_severity`).

		:returns: The severity, or ``None`` if not set.
		"""
		return self._severity


@export
class AssertStatementMixin(ReportStatementMixin, ConditionalMixin, mixin=True):
	"""
	A ``MixinAssertStatement`` is a mixin-class for all assert statements.

	.. seealso::

	   * :class:`Concurrent assert statement <pyVHDLModel.Concurrent.ConcurrentAssertStatement>`
	   * :class:`Sequential assert statement <pyVHDLModel.Sequential.SequentialAssertStatement>`
	"""

	def __init__(self, condition: ExpressionUnion, message: Nullable[ExpressionUnion] = None, severity: Nullable[ExpressionUnion] = None) -> None:
		"""
		Initializes an assert statement.

		:param condition: The condition guarding this statement.
		:param message:   The reported message, or ``None`` if none was given.
		:param severity:  The reported severity level, or ``None`` if none was given.
		"""
		super().__init__(message, severity)
		ConditionalMixin.__init__(self, condition)


class BlockStatementMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``BlockStatement`` is a mixin-class for all block statements.

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	"""

	def __init__(self) -> None:
		"""
		Initializes a block statement.
		"""
		pass


@export
class BaseChoice(ModelEntity):
	"""
	A ``Choice`` is a base-class for all choices.

	.. seealso::

	   * :class:`Concurrent choice <pyVHDLModel.Concurrent.ConcurrentChoice>`
	   * :class:`Sequential choice <pyVHDLModel.Sequential.SequentialChoice>`
	"""


@export
class BaseCase(ModelEntity):
	"""
	A ``Case`` is a base-class for all cases.

	.. seealso::

	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	   * :class:`Others selected waveform <pyVHDLModel.Common.OthersSelectedWaveform>`
	   * :class:`Selected expression <pyVHDLModel.Common.SelectedExpression>`
	   * :class:`Others selected expression <pyVHDLModel.Common.OthersSelectedExpression>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`Sequential case <pyVHDLModel.Sequential.SequentialCase>`
	"""


@export
class ChoicesMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all statements/entities holding a list of :class:`BaseChoice`.

	.. seealso::

	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	   * :class:`Selected expression <pyVHDLModel.Common.SelectedExpression>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`Sequential case <pyVHDLModel.Sequential.SequentialCase>`
	"""

	_choices: List[BaseChoice]  #: List of all choices selecting this alternative.

	def __init__(self, choices: Nullable[Iterable[BaseChoice]] = None) -> None:
		"""
		Initializes choices.

		:param choices: List of all choices selecting this alternative.
		"""
		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice.Parent = self

	@readonly
	def Choices(self) -> List[BaseChoice]:
		"""
		Read-only property to access the choices (:attr:`_choices`).

		:returns: List of choices.
		"""
		return self._choices


@export
class Range(ModelEntity):
	"""
	Base-class for all ranges.

	VHDL's ``range`` rule offers a range denoted by a name (:class:`RangeFromName`) as well as a range
	given by explicit bounds (:class:`SimpleRange`).

	.. seealso::

	   * :class:`Simple range <pyVHDLModel.Base.SimpleRange>`
	   * :class:`Range from name <pyVHDLModel.Base.RangeFromName>`
	"""


@export
class SimpleRange(Range):
	"""
	A range with both bounds given as expressions, e.g. ``0 to 7``.
	"""

	_leftBound:  ExpressionUnion  #: The range's left bound.
	_rightBound: ExpressionUnion  #: The range's right bound.
	_direction:  Direction        #: The range's direction, either ascending (``to``) or descending (``downto``).

	def __init__(self, leftBound: ExpressionUnion, rightBound: ExpressionUnion, direction: Direction, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initialize a simple range.

		:param leftBound:  The range's left bound.
		:param rightBound: The range's right bound.
		:param direction:  The range's direction (``to`` or ``downto``).
		:param parent:     The parent model entity.
		"""
		super().__init__(parent)

		self._leftBound = leftBound
		leftBound.Parent = self

		self._rightBound = rightBound
		rightBound.Parent = self

		self._direction = direction

	@readonly
	def LeftBound(self) -> ExpressionUnion:
		"""
		Read-only property to access the range's left bound (:attr:`_leftBound`).

		:returns: The left bound.
		"""
		return self._leftBound

	@readonly
	def RightBound(self) -> ExpressionUnion:
		"""
		Read-only property to access the range's right bound (:attr:`_rightBound`).

		:returns: The right bound.
		"""
		return self._rightBound

	@readonly
	def Direction(self) -> Direction:
		"""
		Read-only property to access the range's direction (:attr:`_direction`).

		:returns: The direction.
		"""
		return self._direction

	def __str__(self) -> str:
		"""
		Formats the simple range.

		**Format:** ``0 to 7``

		:returns: Formatted simple range.
		"""
		return f"{self._leftBound!s} {self._direction!s} {self._rightBound!s}"


@export
class RangeFromName(Range):
	"""
	A range denoted by a name, so its bounds are inferred from whatever that name references.

	The name is represented by a :class:`~pyVHDLModel.Symbol.Symbol`, so the bounds become available once
	that symbol is resolved. A constrained subtype indication keeps its type mark *and* its range
	constraint, because it's carried by a :class:`~pyVHDLModel.Symbol.ConstrainedScalarSubtypeSymbol`.

	.. note::

	   Two forms reach this class, because a parser can't tell them apart beyond "a name, optionally with
	   a range constraint":

	   * a range attribute like ``vector'range``, and
	   * a discrete subtype indication like ``bit`` or ``integer range 0 to 7``.

	   VHDL's grammar puts the latter one level up (``discrete_range ::= discrete_subtype_indication |
	   range``), so representing both as a range deviates from the rule split deliberately.
	"""

	_symbol: 'Symbol'  #: Reference to the name the range's bounds are inferred from.

	def __init__(self, symbol: 'Symbol', parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initialize a range denoted by a name.

		:param symbol: The symbol referencing the range attribute or discrete subtype.
		:param parent: The parent model entity.
		"""
		super().__init__(parent)

		self._symbol = symbol
		symbol.Parent = self

	@readonly
	def Symbol(self) -> 'Symbol':
		"""
		Read-only property to access the referenced symbol (:attr:`_symbol`).

		:returns: The symbol.
		"""
		return self._symbol

	def __str__(self) -> str:
		"""
		Formats the range denoted by a name.

		**Format:** ``v'range``

		:returns: Formatted range denoted by a name.
		"""
		return f"{self._symbol!s}"


@export
class WaveformElement(ModelEntity):
	"""
	Represents one element of a waveform in a signal assignment.

	A waveform element assigns a value (:data:`Expression`) after an optional delay (:data:`After`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= '1' after 5 ns;
	      --   ^^^               <- Expression
	      --             ^^^^    <- After

	.. seealso::

	   * :class:`Waveform of a simple assignment <pyVHDLModel.Common.WaveformMixin>`
	   * :class:`Waveform of one conditional branch <pyVHDLModel.Common.ConditionalWaveform>`
	   * :class:`Waveform of one selected alternative <pyVHDLModel.Common.SelectedWaveform>`
	"""
	_expression: ExpressionUnion  #: The value this waveform element assigns.
	_after: ExpressionUnion       #: The delay after which the value is assigned, or ``None`` if none was given.

	def __init__(self, expression: ExpressionUnion, after: Nullable[ExpressionUnion] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a waveform element.

		:param expression: The value this waveform element assigns.
		:param after:      The delay after which the value is assigned, or ``None`` if none was given.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

		self._after = after
		if after is not None:
			after.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression

	@readonly
	def After(self) -> Expression:
		"""
		Read-only property to access the waveform element's delay (:attr:`_after`).

		:returns: The after.
		"""
		return self._after
