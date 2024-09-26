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

Types.
"""
from typing                 import Union, List, Iterator, Iterable, Tuple, Optional as Nullable, Dict, Mapping

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType
from pyTooling.Graph        import Vertex

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin, ExpressionUnion, Range
from pyVHDLModel.Symbol     import Symbol
from pyVHDLModel.Name       import Name
from pyVHDLModel.Expression import EnumerationLiteral, PhysicalIntegerLiteral


@export
class BaseType(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""``BaseType`` is the base-class of all type entities in this model."""

	_objectVertex: Vertex

	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		:param parent:     Reference to the logical parent in the model hierarchy.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		_objectVertex = None


@export
class Type(BaseType):
	pass


@export
class AnonymousType(Type):
	pass


@export
class FullType(BaseType):
	pass


@export
class Subtype(BaseType):
	_type:               Symbol
	_baseType:           BaseType
	_range:              Range
	_resolutionFunction: 'Function'

	def __init__(self, identifier: str, symbol: Symbol, parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

		self._type = symbol
		self._baseType = None
		self._range = None
		self._resolutionFunction = None

	@readonly
	def Type(self) -> Symbol:
		return self._type

	@readonly
	def BaseType(self) -> BaseType:
		return self._baseType

	@readonly
	def Range(self) -> Range:
		return self._range

	@readonly
	def ResolutionFunction(self) -> 'Function':
		return self._resolutionFunction

	def __str__(self) -> str:
		return f"subtype {self._identifier} is {self._baseType}"


@export
class ScalarType(FullType):
	"""A ``ScalarType`` is a base-class for all scalar types."""


@export
class RangedScalarType(ScalarType):
	"""A ``RangedScalarType`` is a base-class for all scalar types with a range."""

	_range:      Union[Range, Name]
	_leftBound:  ExpressionUnion
	_rightBound: ExpressionUnion

	def __init__(self, identifier: str, rng: Union[Range, Name], parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)
		self._range = rng

	@readonly
	def Range(self) -> Union[Range, Name]:
		return self._range


@export
class NumericTypeMixin(metaclass=ExtendedType, mixin=True):
	"""A ``NumericType`` is a mixin class for all numeric types."""

	def __init__(self) -> None:
		pass


@export
class DiscreteTypeMixin(metaclass=ExtendedType, mixin=True):
	"""A ``DiscreteType`` is a mixin class for all discrete types."""

	def __init__(self) -> None:
		pass


@export
class EnumeratedType(ScalarType, DiscreteTypeMixin):
	_literals: List[EnumerationLiteral]

	def __init__(self, identifier: str, literals: Iterable[EnumerationLiteral], parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

		self._literals = []
		if literals is not None:
			for literal in literals:
				self._literals.append(literal)
				literal._parent = self

	@readonly
	def Literals(self) -> List[EnumerationLiteral]:
		return self._literals

	def __str__(self) -> str:
		return f"{self._identifier} is ({', '.join(str(l) for l in self._literals)})"


@export
class IntegerType(RangedScalarType, NumericTypeMixin, DiscreteTypeMixin):
	def __init__(self, identifier: str, rng: Union[Range, Name], parent: ModelEntity = None) -> None:
		super().__init__(identifier, rng, parent)

	def __str__(self) -> str:
		return f"{self._identifier} is range {self._range}"


@export
class RealType(RangedScalarType, NumericTypeMixin):
	def __init__(self, identifier: str, rng: Union[Range, Name], parent: ModelEntity = None) -> None:
		super().__init__(identifier, rng, parent)

	def __str__(self) -> str:
		return f"{self._identifier} is range {self._range}"


@export
class PhysicalType(RangedScalarType, NumericTypeMixin):
	_primaryUnit:    str
	_secondaryUnits: List[Tuple[str, PhysicalIntegerLiteral]]

	def __init__(
		self,
		identifier: str,
		rng: Union[Range, Name],
		primaryUnit: str,
		units: Iterable[Tuple[str, PhysicalIntegerLiteral]],
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifier, rng, parent)

		self._primaryUnit = primaryUnit

		self._secondaryUnits = []  # TODO: convert to dict
		for unit in units:
			self._secondaryUnits.append(unit)
			unit[1]._parent = self

	@readonly
	def PrimaryUnit(self) -> str:
		return self._primaryUnit

	@property
	def SecondaryUnits(self) -> List[Tuple[str, PhysicalIntegerLiteral]]:
		return self._secondaryUnits

	def __str__(self) -> str:
		return f"{self._identifier} is range {self._range} units {self._primaryUnit}; {'; '.join(su + ' = ' + str(pu) for su, pu in self._secondaryUnits)};"


@export
class CompositeType(FullType):
	"""A ``CompositeType`` is a base-class for all composite types."""


@export
class ArrayType(CompositeType):
	_dimensions:  List[Range]
	_elementType: Symbol

	def __init__(
		self,
		identifier: str,
		indices: Iterable,
		elementSubtype: Symbol,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifier, parent)

		self._dimensions = []
		for index in indices:
			self._dimensions.append(index)
			# index._parent = self  # FIXME: indices are provided as empty list

		self._elementType = elementSubtype
		# elementSubtype._parent = self   # FIXME: subtype is provided as None

	@property
	def Dimensions(self) -> List[Range]:
		return self._dimensions

	@property
	def ElementType(self) -> Symbol:
		return self._elementType

	def __str__(self) -> str:
		return f"{self._identifier} is array({'; '.join(str(r) for r in self._dimensions)}) of {self._elementType}"


@export
class RecordTypeElement(ModelEntity, MultipleNamedEntityMixin):
	_subtype: Symbol

	def __init__(self, identifiers: Iterable[str], subtype: Symbol, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self) -> Symbol:
		return self._subtype

	def __str__(self) -> str:
		return f"{', '.join(self._identifiers)} : {self._subtype}"


@export
class RecordType(CompositeType):
	_elements: List[RecordTypeElement]

	def __init__(self, identifier: str, elements: Nullable[Iterable[RecordTypeElement]] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

		self._elements = []  # TODO: convert to dict
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element._parent = self

	@property
	def Elements(self) -> List[RecordTypeElement]:
		return self._elements

	def __str__(self) -> str:
		return f"{self._identifier} is record {'; '.join(str(re) for re in self._elements)};"


@export
class ProtectedType(FullType):
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, methods: Union[List, Iterator] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

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

	def __init__(self, identifier: str, declaredItems: Union[List, Iterator] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

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
	_designatedSubtype: Symbol

	def __init__(self, identifier: str, designatedSubtype: Symbol, parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

		self._designatedSubtype = designatedSubtype
		designatedSubtype._parent = self

	@property
	def DesignatedSubtype(self):
		return self._designatedSubtype

	def __str__(self) -> str:
		return f"{self._identifier} is access {self._designatedSubtype}"


@export
class FileType(FullType):
	_designatedSubtype: Symbol

	def __init__(self, identifier: str, designatedSubtype: Symbol, parent: ModelEntity = None) -> None:
		super().__init__(identifier, parent)

		self._designatedSubtype = designatedSubtype
		designatedSubtype._parent = self

	@property
	def DesignatedSubtype(self):
		return self._designatedSubtype

	def __str__(self) -> str:
		return f"{self._identifier} is access {self._designatedSubtype}"
