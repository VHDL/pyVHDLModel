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

Types.
"""
from __future__             import annotations

from typing                 import Union, List, Iterator, Iterable, Tuple, Optional as Nullable, Dict, Mapping

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin, ExpressionUnion, Range
from pyVHDLModel.Symbol     import Symbol
from pyVHDLModel.Expression import EnumerationLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Regions    import ProtectedTypeDeclarationRegionMixin, SequentialDeclarationRegionMixin

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType
from pyTooling.Graph        import Vertex


@export
class BaseType(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents the base-class of all type entities: full types, subtypes and anonymous types.

	Every type is a named entity (:data:`Identifier`, :data:`NormalizedIdentifier`) and can carry
	documentation (:data:`Documentation`).

	.. seealso::

	   * :class:`Type <pyVHDLModel.Type.Type>`
	   * :class:`Full type <pyVHDLModel.Type.FullType>`
	   * :class:`Subtype <pyVHDLModel.Type.Subtype>`
	"""

	_objectVertex: Vertex  #: The vertex representing this type in the design's object graph.

	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes underlying ``BaseType``.

		:param identifier:    Name of the type.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        Reference to the logical parent in the model hierarchy.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._objectVertex = None

	def __str__(self) -> str:
		"""
		Formats the type declaration.

		**Format:** ``type myType``

		:returns: Formatted type declaration.
		"""
		return f"type {self._identifier}"


@export
class Type(BaseType):
	"""
	Represents a base-class for types introduced by a type declaration.

	Besides real type declarations, this is also the base-class of a generic type interface item, which
	introduces a type name without defining the type itself.

	.. seealso::

	   * :class:`Generic type interface item <pyVHDLModel.Interface.GenericTypeInterfaceItem>`
	   * :class:`Anonymous type <pyVHDLModel.Type.AnonymousType>`
	"""
	pass


@export
class AnonymousType(Type):
	"""
	Represents a base-class for types without a type definition of their own.

	An incomplete type is the typical case: it names a type (:data:`Identifier`) whose full
	definition follows later in the same declarative part.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type node;
	      --   ^^^^                  <- Identifier
	      type ptr is access node;
	      type node is record
	        value    : integer;
	        nextNode : ptr;
	      end record;
	"""
	pass


@export
class FullType(BaseType):
	"""
	Represents a base-class for all full type definitions, as opposed to a :class:`Subtype`.

	This is the distinction the declaration regions index on: a full type is registered in ``Types``, a
	subtype in ``Subtypes``.

	.. seealso::

	   * :class:`Scalar type <pyVHDLModel.Type.ScalarType>`
	   * :class:`Composite type <pyVHDLModel.Type.CompositeType>`
	   * :class:`Protected type <pyVHDLModel.Type.ProtectedType>`
	   * :class:`Protected type body <pyVHDLModel.Type.ProtectedTypeBody>`
	   * :class:`Access type <pyVHDLModel.Type.AccessType>`
	   * :class:`File type <pyVHDLModel.Type.FileType>`
	"""
	pass


@export
class Subtype(BaseType):
	"""
	Represents a subtype declaration.

	A subtype is a named entity (:data:`Identifier`, :data:`NormalizedIdentifier`) referencing a type
	(:data:`Type`). Optionally, the subtype can be narrowed by a constraint (:data:`Range`) and/or
	resolved by a resolution function (:data:`ResolutionFunction`).

	.. admonition:: Example

	   Without a constraint:

	   .. code-block:: VHDL

	      subtype byte is bit_vector;
	      --      ^^^^                  <- Identifier
	      --              ^^^^^^^^^^    <- Type

	   With a constraint:

	   .. code-block:: VHDL

	      subtype nibble is bit_vector(3 downto 0);
	      --                          ^^^^^^^^^^^^    <- Range

	   With a resolution function:

	   .. code-block:: VHDL

	      subtype wired is resolved std_ulogic;
	      --               ^^^^^^^^               <- ResolutionFunction

	.. seealso::

	   * :class:`Reference to a type or subtype <pyVHDLModel.Symbol.SubtypeSymbol>`
	"""
	_type:               Symbol    #: Reference to the type or subtype this subtype is derived from.
	_baseType:           BaseType  #: The resolved base type of this subtype.
	_range:              Range     #: The constraint narrowing the base type, or ``None`` if unconstrained.
	_resolutionFunction: Function  #: The resolution function, or ``None`` if the subtype is unresolved.

	def __init__(self, identifier: str, symbol: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a subtype declaration.

		:param identifier:    The identifier of a model entity.
		:param symbol:        Reference to the type or subtype this subtype is derived from.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)

		self._type = symbol
		self._baseType = None
		self._range = None
		self._resolutionFunction = None

	@readonly
	def Type(self) -> Symbol:
		"""
		Read-only property to access the type (:attr:`_type`).

		:returns: The type.
		"""
		return self._type

	@readonly
	def BaseType(self) -> BaseType:
		"""
		Read-only property to access the base type (:attr:`_baseType`).

		:returns: The base type.
		"""
		return self._baseType

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	@readonly
	def ResolutionFunction(self) -> Function:
		"""
		Read-only property to access the resolution function (:attr:`_resolutionFunction`).

		:returns: The resolution function.
		"""
		return self._resolutionFunction

	def __str__(self) -> str:
		"""
		Formats the subtype declaration.

		**Format:** ``subtype byte is bit_vector``

		The *base type* is rendered, so an unlinked subtype shows ``None``.

		:returns: Formatted subtype declaration.
		"""
		return f"subtype {self._identifier} is {self._baseType}"


@export
class ScalarType(FullType):
	"""
	Represents a base-class for all scalar types: enumerated, integer, real and physical types.

	.. seealso::

	   * :class:`Ranged scalar type <pyVHDLModel.Type.RangedScalarType>`
	   * :class:`Enumerated type <pyVHDLModel.Type.EnumeratedType>`
	"""


@export
class RangedScalarType(ScalarType):
	"""
	Represents a base-class for all scalar types constrained by a range (:data:`Range`).

	Integer, real and physical types are ranged. An enumerated type is scalar but not ranged, so it
	derives from :class:`ScalarType` directly.

	.. seealso::

	   * :class:`Integer type <pyVHDLModel.Type.IntegerType>`
	   * :class:`Real type <pyVHDLModel.Type.RealType>`
	   * :class:`Physical type <pyVHDLModel.Type.PhysicalType>`
	"""

	_range: Range  #: The range constraining this scalar type.

	def __init__(self, identifier: str, rng: Range, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initialize a scalar type with a range.

		:param identifier:    The type's identifier.
		:param rng:           The type's range.
		:param documentation: The type's documentation.
		:param parent:        The parent model entity.
		"""
		super().__init__(identifier, documentation, parent)
		self._range = rng

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the type's range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range


@export
class NumericTypeMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all numeric types: integer, real and physical types.

	.. seealso::

	   * :class:`Integer type <pyVHDLModel.Type.IntegerType>`
	   * :class:`Real type <pyVHDLModel.Type.RealType>`
	   * :class:`Physical type <pyVHDLModel.Type.PhysicalType>`
	"""

	def __init__(self) -> None:
		"""
		Initializes a numeric type.
		"""
		pass


@export
class DiscreteTypeMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all discrete types: enumerated and integer types.

	.. seealso::

	   * :class:`Enumerated type <pyVHDLModel.Type.EnumeratedType>`
	   * :class:`Integer type <pyVHDLModel.Type.IntegerType>`
	"""

	def __init__(self) -> None:
		"""
		Initializes a discrete type.
		"""
		pass


@export
class EnumeratedType(ScalarType, DiscreteTypeMixin):
	"""
	Represents an enumerated type definition.

	An enumerated type is a named entity (:data:`Identifier`) listing its enumeration literals
	(:data:`Literals`) in declaration order.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type state is (Idle, Running, Done);
	      --   ^^^^^                             <- Identifier
	      --             ^^^^^^^^^^^^^^^^^^^     <- Literals
	"""
	_literals: List[EnumerationLiteral]  #: List of all enumeration literals, in declaration order.

	def __init__(self, identifier: str, literals: Iterable[EnumerationLiteral], documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an enumerated type definition.

		:param identifier:    The identifier of a model entity.
		:param literals:      List of all enumeration literals, in declaration order.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)

		self._literals = []
		if literals is not None:
			for literal in literals:
				self._literals.append(literal)
				literal.Parent = self

	@readonly
	def Literals(self) -> List[EnumerationLiteral]:
		"""
		Read-only property to access the literals (:attr:`_literals`).

		:returns: List of literals.
		"""
		return self._literals

	def __str__(self) -> str:
		"""
		Formats the enumerated type definition.

		**Format:** ``state is (idle, run)``

		:returns: Formatted enumerated type definition.
		"""
		return f"{self._identifier} is ({', '.join(str(l) for l in self._literals)})"


@export
class IntegerType(RangedScalarType, NumericTypeMixin, DiscreteTypeMixin):
	"""
	Represents an integer type definition.

	An integer type is a named entity (:data:`Identifier`) constrained by a range (:data:`Range`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      type nibble is range 0 to 15;
	      --   ^^^^^^                     <- Identifier
	      --                   ^^^^^^^    <- Range
	"""
	def __init__(self, identifier: str, rng: Range, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an integer type definition.

		:param identifier:    The identifier of a model entity.
		:param rng:           The range constraining this scalar type.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, rng, documentation, parent)

	def __str__(self) -> str:
		"""
		Formats the integer type definition.

		**Format:** ``byte_count is range 0 to 7``

		:returns: Formatted integer type definition.
		"""
		return f"{self._identifier} is range {self._range}"


@export
class RealType(RangedScalarType, NumericTypeMixin):
	"""
	Represents a floating-point type definition.

	A floating-point type is a named entity (:data:`Identifier`) constrained by a range
	(:data:`Range`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      type fraction is range 0.0 to 1.0;
	      --   ^^^^^^^^                        <- Identifier
	      --                     ^^^^^^^^^^    <- Range
	"""
	def __init__(self, identifier: str, rng: Range, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a floating-point type definition.

		:param identifier:    The identifier of a model entity.
		:param rng:           The range constraining this scalar type.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, rng, documentation, parent)

	def __str__(self) -> str:
		"""
		Formats the floating-point type definition.

		**Format:** ``gain is range 0.0 to 1.0``

		:returns: Formatted floating-point type definition.
		"""
		return f"{self._identifier} is range {self._range}"


@export
class PhysicalType(RangedScalarType, NumericTypeMixin):
	"""
	Represents a physical type definition.

	A physical type is a named entity (:data:`Identifier`) constrained by a range (:data:`Range`), and
	defines a primary unit (:data:`PrimaryUnit`) plus any number of secondary units
	(:data:`SecondaryUnits`). The model holds the secondary units in a list and has no distinct field
	per unit, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type distance is range 0 to 1000000 units
	      --   ^^^^^^^^                               <- Identifier
	      --                     ^^^^^^^^^^^^         <- Range
	        um;
	      --^^^                                       <- PrimaryUnit
	        mm = 1000 um;
	      --^^^^^^^^^^^^^                             <- SecondaryUnits[0]
	        m  = 1000 mm;
	      --^^^^^^^^^^^^^                             <- SecondaryUnits[1]
	      end units;
	"""
	_primaryUnit:    str                                       #: The name of the type's primary unit.
	_secondaryUnits: List[Tuple[str, PhysicalIntegerLiteral]]  #: Secondary units as (name, value) pairs.

	def __init__(
		self,
		identifier: str,
		rng: Range,
		primaryUnit: str,
		units: Iterable[Tuple[str, PhysicalIntegerLiteral]],
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a physical type definition.

		:param identifier:    The identifier of a model entity.
		:param rng:           The range constraining this scalar type.
		:param primaryUnit:   The name of the type's primary unit.
		:param units:         Iterable of the secondary units as (name, value) pairs.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, rng, documentation, parent)

		self._primaryUnit = primaryUnit

		self._secondaryUnits = []  # TODO: convert to dict
		for unit in units:
			self._secondaryUnits.append(unit)
			unit[1].Parent = self

	@readonly
	def PrimaryUnit(self) -> str:
		"""
		Read-only property to access the primary unit (:attr:`_primaryUnit`).

		:returns: The primary unit.
		"""
		return self._primaryUnit

	@readonly
	def SecondaryUnits(self) -> List[Tuple[str, PhysicalIntegerLiteral]]:
		"""
		Read-only property to access the secondary units (:attr:`_secondaryUnits`).

		:returns: List of secondary units.
		"""
		return self._secondaryUnits

	def __str__(self) -> str:
		"""
		Formats the physical type definition.

		**Format:** ``distance is range 0 to 1000 units um; mm = 1000 um;``

		:returns: Formatted physical type definition.
		"""
		return f"{self._identifier} is range {self._range} units {self._primaryUnit}; {'; '.join(su + ' = ' + str(pu) for su, pu in self._secondaryUnits)};"


@export
class CompositeType(FullType):
	"""
	Represents a base-class for all composite types: array and record types.

	.. seealso::

	   * :class:`Array type <pyVHDLModel.Type.ArrayType>`
	   * :class:`Record type <pyVHDLModel.Type.RecordType>`
	"""


@export
class ArrayType(CompositeType):
	"""
	Represents an array type definition.

	An array type is a named entity (:data:`Identifier`) defining one or more index ranges
	(:data:`Dimensions`) and the subtype of its elements (:data:`ElementType`).

	.. admonition:: Example

	   One dimension:

	   .. code-block:: VHDL

	      type memory is array (0 to 255) of bit_vector(7 downto 0);
	      --   ^^^^^^                                                  <- Identifier
	      --                    ^^^^^^^^                               <- Dimensions
	      --                                 ^^^^^^^^^^^^^^^^^^^^^^    <- ElementType

	   Two dimensions, both unconstrained:

	   .. code-block:: VHDL

	      type matrix is array (natural range <>, natural range <>) of bit;
	      --                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^            <- Dimensions

	.. seealso::

	   * :class:`Reference to a constrained array subtype <pyVHDLModel.Symbol.ConstrainedArraySubtypeSymbol>`
	"""
	_dimensions:  List[Range]  #: List of all index ranges, one per dimension.
	_elementType: Symbol       #: Reference to the subtype of the array's elements.

	def __init__(
		self,
		identifier: str,
		indices: Iterable,
		elementSubtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an array type definition.

		:param identifier:     The identifier of a model entity.
		:param indices:        List of all index ranges, one per dimension.
		:param elementSubtype: Reference to the subtype of the array's elements.
		:param documentation:  The documentation comment associated with this declaration.
		:param parent:         The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)

		self._dimensions = []
		for index in indices:
			self._dimensions.append(index)
			# index.Parent = self  # FIXME: indices are provided as empty list

		self._elementType = elementSubtype
		# elementSubtype.Parent = self   # FIXME: subtype is provided as None

	@readonly
	def Dimensions(self) -> List[Range]:
		"""
		Read-only property to access the dimensions (:attr:`_dimensions`).

		:returns: List of dimensions.
		"""
		return self._dimensions

	@readonly
	def ElementType(self) -> Symbol:
		"""
		Read-only property to access the element type (:attr:`_elementType`).

		:returns: The element type.
		"""
		return self._elementType

	def __str__(self) -> str:
		"""
		Formats the array type definition.

		**Format:** ``memory is array(0 to 7) of bit``

		:returns: Formatted array type definition.
		"""
		return f"{self._identifier} is array({'; '.join(str(r) for r in self._dimensions)}) of {self._elementType}"


@export
class RecordTypeElement(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents one element declaration inside a record type definition.

	A single declaration may name several elements at once, hence :data:`Identifiers` rather than one
	identifier. All of them share the same subtype (:data:`Subtype`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      type frame is record
	        --! The first fields.
	      --^^^^^^^^^^^^^^^^^^^^^   <- Documentation
	        a, b : bit;
	      --^^^^                    <- Identifiers
	      --       ^^^              <- Subtype
	      end record;

	.. seealso::

	   * :class:`Record type <pyVHDLModel.Type.RecordType>`
	"""
	_subtype: Symbol  #: Reference to the subtype shared by all identifiers of this element declaration.

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a record type element.

		:param identifiers:   A list of identifiers.
		:param subtype:       Reference to the subtype shared by all identifiers of this element declaration.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Subtype(self) -> Symbol:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	def __str__(self) -> str:
		"""
		Formats the record element declaration.

		**Format:** ``a, b : bit``

		:returns: Formatted record element declaration.
		"""
		return f"{', '.join(self._identifiers)} : {self._subtype}"


@export
class RecordType(CompositeType):
	"""
	Represents a record type definition.

	A record type is a named entity (:data:`Identifier`) holding its element declarations
	(:data:`Elements`) in declaration order. The model holds them in a list and has no distinct
	field per element, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type frame is record
	      --   ^^^^^                             <- Identifier
	        a, b    : bit;
	      --^^^^^^^^^^^^^^                       <- Elements[0]
	        payload : bit_vector(31 downto 0);
	      --^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   <- Elements[1]
	      end record;

	.. seealso::

	   * :class:`Record element <pyVHDLModel.Type.RecordTypeElement>`
	   * :class:`Reference to a record element <pyVHDLModel.Symbol.RecordElementSymbol>`
	"""
	_elements: List[RecordTypeElement]  #: List of all element declarations, in declaration order.

	def __init__(self, identifier: str, elements: Nullable[Iterable[RecordTypeElement]] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a record type definition.

		:param identifier:    The identifier of a model entity.
		:param elements:      List of all element declarations, in declaration order.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)

		self._elements = []  # TODO: convert to dict
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element.Parent = self

	@readonly
	def Elements(self) -> List[RecordTypeElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements

	def __str__(self) -> str:
		"""
		Formats the record type definition.

		**Format:** ``frame is record a : bit;``

		:returns: Formatted record type definition.
		"""
		return f"{self._identifier} is record {'; '.join(str(re) for re in self._elements)};"


@export
class ProtectedType(FullType, ProtectedTypeDeclarationRegionMixin):
	"""
	Represents a protected type declaration.

	A protected type is a named entity (:data:`Identifier`) exposing only its methods
	(:data:`Methods`). The implementation lives in a separate :class:`ProtectedTypeBody`.

	It is a declarative region and owns a namespace. VHDL's ``protected_type_declarative_item`` admits
	subprogram declarations and nothing else - the narrowest declarative region in the language - so
	:data:`DeclaredItems` and :data:`Methods` hold the same items. The markers below name list elements,
	because the model has no distinct field per method.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type counter is protected
	      --   ^^^^^^^                              <- Identifier
	        procedure increment;
	      --^^^^^^^^^^^^^^^^^^^^                    <- Methods[0]
	        impure function value return natural;
	      --^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   <- Methods[1]
	      end protected;

	.. seealso::

	   * :class:`Protected type body <pyVHDLModel.Type.ProtectedTypeBody>`
	   * :class:`Method of a protected type <pyVHDLModel.Subprogram.ProcedureMethod>`
	"""
	def __init__(self, identifier: str, declaredItems: Union[List, Iterator] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a protected type declaration.

		:param identifier:    The identifier of a model entity.
		:param declaredItems: All items declared by this protected type; only subprograms are legal.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)
		ProtectedTypeDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)

	@readonly
	def Methods(self) -> List[Union[Procedure, Function]]:
		"""
		Read-only property to access the declared methods, in declaration order.

		A protected type declares nothing but subprograms, so this is every declared item
		(:attr:`_declaredItems`). It is kept as a named view because "method" is the VHDL term for a
		protected type's subprograms.

		:returns: List of methods, in declaration order.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		return [item for item in self._declaredItems if isinstance(item, (Function, Procedure))]


@export
class ProtectedTypeBody(FullType, SequentialDeclarationRegionMixin):
	"""
	Represents a protected type body.

	A protected type body implements the methods (:data:`Methods`) declared by the
	:class:`ProtectedType` of the same identifier (:data:`Identifier`).

	It is a declarative region and owns a namespace. Its declarative part matches a subprogram's, so it
	shares :class:`~pyVHDLModel.Regions.SequentialDeclarationRegionMixin` with subprogram bodies.
	Everything declared is available as :data:`DeclaredItems`; :data:`Methods` is its subprogram subset.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type counter is protected body
	      --   ^^^^^^^                       <- Identifier
	        variable count : natural := 0;
	        procedure increment is
	      --^^^^^^^^^^^^^^^^^^^^^^           <- Methods[0]
	        begin
	          count := count + 1;
	        end procedure;
	      end protected body;

	.. seealso::

	   * :class:`Protected type declaration <pyVHDLModel.Type.ProtectedType>`
	"""
	def __init__(self, identifier: str, declaredItems: Union[List, Iterator] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a protected type body.

		:param identifier:    The identifier of a model entity.
		:param declaredItems: Iterable of all items declared in this body.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)

	# FIXME: needs to be declared items or so
	@readonly
	def Methods(self) -> List[Union[Procedure, Function]]:
		"""
		Read-only property to access the implemented methods, in declaration order.

		A protected type body may also declare variables, types, subtypes, aliases and files, so this is
		the subprogram subset of :attr:`_declaredItems` rather than all of them.

		:returns: List of methods, in declaration order.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		return [item for item in self._declaredItems if isinstance(item, (Function, Procedure))]


@export
class AccessType(FullType):
	"""
	Represents an access type definition.

	An access type is a named entity (:data:`Identifier`) pointing at values of its designated subtype
	(:data:`DesignatedSubtype`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      type ptr is access integer;
	      --   ^^^                      <- Identifier
	      --                 ^^^^^^^    <- DesignatedSubtype
	"""
	_designatedSubtype: Symbol  #: Reference to the subtype the access values designate.

	def __init__(self, identifier: str, designatedSubtype: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an access type definition.

		:param identifier:        The identifier of a model entity.
		:param designatedSubtype: Reference to the subtype the access values designate.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)

		self._designatedSubtype = designatedSubtype
		designatedSubtype.Parent = self

	@readonly
	def DesignatedSubtype(self) -> Symbol:
		"""
		Read-only property to access the designated subtype (:attr:`_designatedSubtype`).

		:returns: The designated subtype.
		"""
		return self._designatedSubtype

	def __str__(self) -> str:
		"""
		Formats the access type definition.

		**Format:** ``ptr is access node``

		:returns: Formatted access type definition.
		"""
		return f"{self._identifier} is access {self._designatedSubtype}"


@export
class FileType(FullType):
	"""
	Represents a file type definition.

	A file type is a named entity (:data:`Identifier`) holding values of its designated subtype
	(:data:`DesignatedSubtype`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      type text_file is file of string;
	      --   ^^^^^^^^^                      <- Identifier
	      --                        ^^^^^^    <- DesignatedSubtype
	"""
	_designatedSubtype: Symbol  #: Reference to the subtype of the values stored in the file.

	def __init__(self, identifier: str, designatedSubtype: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a file type definition.

		:param identifier:        The identifier of a model entity.
		:param designatedSubtype: Reference to the subtype of the values stored in the file.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)

		self._designatedSubtype = designatedSubtype
		designatedSubtype.Parent = self

	@readonly
	def DesignatedSubtype(self) -> Symbol:
		"""
		Read-only property to access the designated subtype (:attr:`_designatedSubtype`).

		:returns: The designated subtype.
		"""
		return self._designatedSubtype

	def __str__(self) -> str:
		"""
		Formats the file type definition.

		**Format:** ``ft is file of character``

		:returns: Formatted file type definition.
		"""
		return f"{self._identifier} is file of {self._designatedSubtype}"
