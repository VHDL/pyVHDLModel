from enum import unique, Enum
from typing import Type, Tuple, Iterable, Optional as Nullable, Union, cast

from pyTooling.Decorators import export
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
