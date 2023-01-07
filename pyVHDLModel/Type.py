from typing import Union, List, Iterator, Iterable, Tuple

from pyTooling.Decorators import export

from pyVHDLModel import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, ExpressionUnion, SubtypeOrSymbol, MultipleNamedEntityMixin
from pyVHDLModel.Common import Range
from pyVHDLModel.Expression import EnumerationLiteral, PhysicalIntegerLiteral


@export
class BaseType(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""``BaseType`` is the base-class of all type entities in this model."""

	def __init__(self, identifier: str, documentation: str = None):
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class Type(BaseType):
	pass


@export
class FullType(BaseType):
	pass


@export
class Subtype(BaseType):
	_type:               'Subtype'
	_baseType:           BaseType
	_range:              'Range'
	_resolutionFunction: 'Function'

	def __init__(self, identifier: str):
		super().__init__(identifier)

	@property
	def Type(self) -> 'Subtype':
		return self._type

	@property
	def BaseType(self) -> BaseType:
		return self._baseType

	@property
	def Range(self) -> 'Range':
		return self._range

	@property
	def ResolutionFunction(self) -> 'Function':
		return self._resolutionFunction


@export
class AnonymousType(Type):
	pass


@export
class ScalarType(FullType):
	"""A ``ScalarType`` is a base-class for all scalar types."""


@export
class RangedScalarType(ScalarType):
	"""A ``RangedScalarType`` is a base-class for all scalar types with a range."""

	_range:      Union['Range', 'Name']
	_leftBound:  ExpressionUnion
	_rightBound: ExpressionUnion

	def __init__(self, identifier: str, rng: Union['Range', 'Name']):
		super().__init__(identifier)
		self._range = rng

	@property
	def Range(self) -> Union['Range', 'Name']:
		return self._range


@export
class NumericType:
	"""A ``NumericType`` is a mixin class for all numeric types."""

	def __init__(self):
		pass


@export
class DiscreteType:
	"""A ``DiscreteType`` is a mixin class for all discrete types."""

	def __init__(self):
		pass


@export
class CompositeType(FullType):
	"""A ``CompositeType`` is a base-class for all composite types."""


@export
class ProtectedType(FullType):
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, methods: Union[List, Iterator] = None):
		super().__init__(identifier)

		self._methods = []
		if methods is not None:
			for method in methods:
				self._methods.append(method)
				method._parent = self

	@property
	def Methods(self) -> List[Union['Procedure', 'Function']]:
		return self._methods


@export
class ProtectedTypeBody(FullType):
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, declaredItems: Union[List, Iterator] = None):
		super().__init__(identifier)

		self._methods = []
		if declaredItems is not None:
			for method in declaredItems:
				self._methods.append(method)
				method._parent = self

	# FIXME: needs to be declared items or so
	@property
	def Methods(self) -> List[Union['Procedure', 'Function']]:
		return self._methods


@export
class AccessType(FullType):
	_designatedSubtype: SubtypeOrSymbol

	def __init__(self, identifier: str, designatedSubtype: SubtypeOrSymbol):
		super().__init__(identifier)

		self._designatedSubtype = designatedSubtype
		designatedSubtype._parent = self

	@property
	def DesignatedSubtype(self):
		return self._designatedSubtype


@export
class FileType(FullType):
	_designatedSubtype: SubtypeOrSymbol

	def __init__(self, identifier: str, designatedSubtype: SubtypeOrSymbol):
		super().__init__(identifier)

		self._designatedSubtype = designatedSubtype
		designatedSubtype._parent = self

	@property
	def DesignatedSubtype(self):
		return self._designatedSubtype


@export
class EnumeratedType(ScalarType, DiscreteType):
	_literals: List['EnumerationLiteral']

	def __init__(self, identifier: str, literals: Iterable['EnumerationLiteral']):
		super().__init__(identifier)

		self._literals = []
		if literals is not None:
			for literal in literals:
				self._literals.append(literal)
				literal._parent = self

	@property
	def Literals(self) -> List['EnumerationLiteral']:
		return self._literals


@export
class IntegerType(RangedScalarType, NumericType, DiscreteType):
	def __init__(self, identifier: str, rng: Union['Range', 'Name']):
		super().__init__(identifier, rng)


@export
class RealType(RangedScalarType, NumericType):
	def __init__(self, identifier: str, rng: Union['Range', 'Name']):
		super().__init__(identifier, rng)


@export
class PhysicalType(RangedScalarType, NumericType):
	_primaryUnit:    str
	_secondaryUnits: List[Tuple[str, 'PhysicalIntegerLiteral']]

	def __init__(self, identifier: str, rng: Union['Range', 'Name'], primaryUnit: str, units: Iterable[Tuple[str, 'PhysicalIntegerLiteral']]):
		super().__init__(identifier, rng)

		self._primaryUnit = primaryUnit

		self._secondaryUnits = []  # TODO: convert to dict
		for unit in units:
			self._secondaryUnits.append(unit)
			unit[1]._parent = self

	@property
	def PrimaryUnit(self) -> str:
		return self._primaryUnit

	@property
	def SecondaryUnits(self) -> List[Tuple[str, 'PhysicalIntegerLiteral']]:
		return self._secondaryUnits


@export
class ArrayType(CompositeType):
	_dimensions:  List['Range']
	_elementType: Subtype

	def __init__(self, identifier: str, indices: List, elementSubtype: SubtypeOrSymbol):
		super().__init__(identifier)

		self._dimensions = []

		self._elementType = elementSubtype
		# elementSubtype._parent = self   # FIXME: subtype is provided as None

	@property
	def Dimensions(self) -> List['Range']:
		return self._dimensions

	@property
	def ElementType(self) -> Subtype:
		return self._elementType


@export
class RecordTypeElement(ModelEntity, MultipleNamedEntityMixin):
	_subtype: SubtypeOrSymbol

	def __init__(self, identifiers: Iterable[str], subtype: SubtypeOrSymbol):
		super().__init__()
		MultipleNamedEntityMixin.__init__(self, identifiers)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> SubtypeOrSymbol:
		return self._subtype


@export
class RecordType(CompositeType):
	_elements: List[RecordTypeElement]

	def __init__(self, identifier: str, elements: Iterable[RecordTypeElement] = None):
		super().__init__(identifier)

		self._elements = []  # TODO: convert to dict
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element._parent = self

	@property
	def Elements(self) -> List[RecordTypeElement]:
		return self._elements
