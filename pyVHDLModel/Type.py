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

from typing                 import TYPE_CHECKING, ClassVar, Generator, Union, Iterator, Iterable, \
                                   Optional as Nullable, Self

from pyTooling.Common       import getFullyQualifiedName, getTypeName
from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType, abstractclass
from pyTooling.Graph        import Vertex
from pyTooling.Warning      import WarningCollector

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin, \
                                   Range, ReservedWord, Mode
from pyVHDLModel.Exception  import NotAChildError, IncompleteTypeWarning
from pyVHDLModel.Name       import Name, SimpleName
from pyVHDLModel.Symbol     import Symbol, SubtypeSymbol, SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                                   ResolutionFunctionSymbol
from pyVHDLModel.Expression import EnumerationLiteral, CharacterEnumerationLiteral, PhysicalIntegerLiteral
from pyVHDLModel.Regions    import DeclarativeRegionMixin, ProtectedTypeDeclarationRegionMixin, \
                                   SequentialDeclarationRegionMixin, WithoutStatementsMixin

if TYPE_CHECKING:
	from pyVHDLModel.DesignUnit import DesignUnit, Package
	from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
	from pyVHDLModel.Subprogram import Function, PredefinedOperator, PredefinedFunction, PredefinedOperation
	from pyVHDLModel.Visitor    import Visitor


@export
@abstractclass
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
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, reference to the logical parent in the model hierarchy.
		                      Default: ``None``, no parent.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._objectVertex = None

	@readonly
	def BaseType(self) -> BaseType:
		"""
		Read-only property to return the base type of this type: the type itself (IEEE Std 1076-2008, 5.1).

		A subtype returns the base type of the type it is derived from (:attr:`~pyVHDLModel.Type.Subtype.BaseType`).

		:returns: The base type.
		"""
		return self

	def DenoteBy(
		self,
		name:   Name,
		region: DeclarativeRegionMixin,
		place:  ModelEntity,
		symbol: Symbol
	) -> Nullable[ModelEntity]:
		"""
		Return this type or subtype, the model entity a name in a type mark denotes.

		:param name:   The name denoting this declaration, a part of the type mark.
		:param region: The declarative region containing the type mark.
		:param place:  The declaration containing the type mark.
		:param symbol: The type mark.
		:returns:      This type or subtype.
		"""
		return self

	def __str__(self) -> str:
		"""
		Formats the type declaration.

		**Format:** ``type myType``

		:returns: Formatted type declaration.
		"""
		return f"type {self._identifier}"


@export
@abstractclass
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

	def ResolveReferences(self, designUnit: DesignUnit, region: DeclarativeRegionMixin) -> None:
		"""
		Check that a full type declaration of the same name completes this incomplete type later in its region.

		:param designUnit:                     The design unit containing this declaration.
		:param region:                         The declarative region declaring this declaration.
		:raises UnhandledCriticalWarningError: If no full type declaration follows in the region, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.IncompleteTypeWarning`.
		"""
		super().ResolveReferences(designUnit, region)

		declarations = region._Declarations()
		for declaration in declarations[declarations.index(self) + 1:]:
			if isinstance(declaration, FullType) and declaration._normalizedIdentifier == self._normalizedIdentifier:
				return

		WarningCollector.Raise(IncompleteTypeWarning(
			f"Incomplete type '{self._identifier}' has no full type declaration in '{region._namespace._name}'.",
			incompleteType=self
		))

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this incomplete type declaration with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAnonymousType(self)
		visitor.VisitTerminator(self)
		visitor.DepartAnonymousType(self)


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

	_implicitOperations: Nullable[tuple[PredefinedOperation, ...]]  #: Implicit operations, ``None`` until created.

	def __init__(
		self,
		identifier:    str,
		documentation: Nullable[str] =         None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a full type.

		:param identifier:    The identifier of a model entity.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)

		self._implicitOperations = None

	@readonly
	def ImplicitOperations(self) -> tuple[PredefinedOperation, ...]:
		"""
		Read-only property to access the operations this type declares implicitly (:attr:`_implicitOperations`): its
		predefined operators and predefined functions (IEEE Std 1076-2008, 5).

		They are created on the first access and kept, until the analysis is reset (:meth:`ResetReferences`). The
		analysis indexes them in the namespace of the type's region after the type marks are resolved
		(:meth:`~pyVHDLModel.Design.IndexImplicitOperations`).

		:returns: Tuple of predefined operators and predefined functions.
		"""
		if self._implicitOperations is None:
			self._implicitOperations = tuple(self._CreateImplicitOperations())

		return self._implicitOperations

	def ResetReferences(self, designUnit: DesignUnit, region: DeclarativeRegionMixin) -> None:
		"""
		Reset the references of this type's type marks and its implicit operations, which depend on them: they are
		created again on the next access (:data:`ImplicitOperations`). A type of a predefined library
		(:attr:`~pyVHDLModel.Library.IsPredefined`) keeps its implicit operations.

		:param designUnit: The design unit containing this declaration.
		:param region:     The declarative region declaring this declaration.
		"""
		super().ResetReferences(designUnit, region)

		if not designUnit._parent.IsPredefined:
			self._implicitOperations = None

	def ResolveImplicitOperationTypeMarks(self, standard: Package) -> None:
		"""
		Resolve the type marks of the implicit operations naming a type of package ``std.standard``.

		An implicit operation names the predefined types ``BOOLEAN``, ``INTEGER`` or ``STRING`` of ``std.standard``
		(IEEE Std 1076-2008, 9.2), whatever a declaration of the type's region or a use clause makes visible there; the
		type marks naming this type are resolved, when the operations are created. The analysis resolves them, when it
		indexes the implicit operations (:meth:`~pyVHDLModel.Design.IndexImplicitOperations`). Resolving them again
		changes nothing.

		:param standard: The package ``std.standard``.
		"""
		for operation in self.ImplicitOperations:
			for symbol in (*(item._subtype for item in operation._parameterItems), operation._returnType):
				if symbol._reference is None:
					symbol._reference = standard._types[symbol._name._normalizedIdentifier]

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this type declares implicitly: the equality operators ``"="`` and ``"/="``
		(IEEE Std 1076-2008, 9.2.3).

		A file type and a protected type declare no equality; derived classes add their operations.

		:returns: List of predefined operators and predefined functions.
		"""
		return [
			self._BinaryOperator("=",  SimpleSubtypeSymbol(SimpleName("boolean"))),
			self._BinaryOperator("/=", SimpleSubtypeSymbol(SimpleName("boolean")))
		]

	def _TypeMark(self) -> SimpleSubtypeSymbol:
		"""
		Create a type mark referencing this type, for a parameter or the return value of an implicit operation.

		:returns: The type mark.
		"""
		symbol =            SimpleSubtypeSymbol(SimpleName(self._identifier))
		symbol._reference = self

		return symbol

	def _Parameter(self, identifier: str, subtype: SubtypeSymbol) -> ParameterConstantInterfaceItem:
		"""
		Create a parameter of an implicit operation: a constant of mode ``in``.

		:param identifier: The parameter's identifier.
		:param subtype:    The parameter's type mark.
		:returns:          The parameter.
		"""
		from pyVHDLModel.Interface import ParameterConstantInterfaceItem

		return ParameterConstantInterfaceItem((identifier,), Mode.In, subtype)

	def _Operator(
		self,
		operatorSymbol: str,
		returnType:     SubtypeSymbol,
		parameterItems: Iterable[ParameterConstantInterfaceItem]
	) -> PredefinedOperator:
		"""
		Create an implicit operator of this type.

		:param operatorSymbol: The operator symbol without quotation marks.
		:param returnType:     The type mark of the return value.
		:param parameterItems: The parameters, in declaration order.
		:returns:              The predefined operator.
		"""
		from pyVHDLModel.Subprogram import PredefinedOperator

		return PredefinedOperator(operatorSymbol, returnType, parameterItems, parent=self)

	def _Function(
		self,
		identifier:     str,
		returnType:     SubtypeSymbol,
		parameterItems: Iterable[ParameterConstantInterfaceItem]
	) -> PredefinedFunction:
		"""
		Create an implicit function of this type.

		:param identifier:     The function's identifier.
		:param returnType:     The type mark of the return value.
		:param parameterItems: The parameters, in declaration order.
		:returns:              The predefined function.
		"""
		from pyVHDLModel.Subprogram import PredefinedFunction

		return PredefinedFunction(identifier, returnType, parameterItems, parent=self)

	def _BinaryOperator(self, operatorSymbol: str, returnType: SubtypeSymbol) -> PredefinedOperator:
		"""
		Create an implicit binary operator of this type: both operands, ``L`` and ``R``, are of this type.

		:param operatorSymbol: The operator symbol without quotation marks.
		:param returnType:     The type mark of the return value.
		:returns:              The predefined operator.
		"""
		return self._Operator(
			operatorSymbol,
			returnType,
			(self._Parameter("L", self._TypeMark()), self._Parameter("R", self._TypeMark()))
		)

	def _UnaryOperator(self, operatorSymbol: str, returnType: SubtypeSymbol) -> PredefinedOperator:
		"""
		Create an implicit unary operator of this type: the operand ``R`` is of this type.

		:param operatorSymbol: The operator symbol without quotation marks.
		:param returnType:     The type mark of the return value.
		:returns:              The predefined operator.
		"""
		return self._Operator(operatorSymbol, returnType, (self._Parameter("R", self._TypeMark()),))

@export
class Subtype(BaseType):
	"""
	Represents a subtype declaration.

	A subtype is a named entity (:data:`Identifier`, :data:`NormalizedIdentifier`) with a subtype indication
	(:data:`Type`): a type mark, optionally narrowed by a constraint. A range constraint is available as
	:data:`Range`. Optionally, the subtype indication has a resolution indication
	(:data:`SubtypeSymbol.Resolution <pyVHDLModel.Symbol.SubtypeSymbol.Resolution>`); the function a resolution function
	name references is available as :data:`ResolutionFunction`.

	.. admonition:: Example

	   Without a constraint:

	   .. code-block:: VHDL

	      subtype byte is bit_vector;
	      --      ^^^^                  <- Identifier
	      --              ^^^^^^^^^^    <- Type

	   With a range constraint:

	   .. code-block:: VHDL

	      subtype nibble is integer range 0 to 15;
	      --                ^^^^^^^^^^^^^^^^^^^^^    <- Type (constrained scalar subtype symbol)
	      --                              ^^^^^^^    <- Range

	   With a resolution function:

	   .. code-block:: VHDL

	      subtype wired is resolved std_ulogic;
	      --               ^^^^^^^^               <- ResolutionFunction

	.. seealso::

	   * :class:`Reference to a type or subtype <pyVHDLModel.Symbol.SubtypeSymbol>`
	"""
	_type:     Symbol    #: Reference to the type or subtype this subtype is derived from.
	_baseType: BaseType  #: The resolved base type of this subtype.

	def __init__(self, identifier: str, symbol: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a subtype declaration.

		:param identifier:    The identifier of a model entity.
		:param symbol:        Reference to the type or subtype this subtype is derived from.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)

		self._type =     symbol
		self._baseType = None

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

		It is set, when the subtype's type mark is resolved (:meth:`ResolveReferences`).

		:returns: The base type, or ``None`` if the type mark isn't resolved.
		"""
		return self._baseType

	@readonly
	def Range(self) -> Nullable[Range]:
		"""
		Read-only property to return the range constraint of the subtype indication (:attr:`_type`).

		:returns: The range, or ``None`` if the subtype indication has no range constraint.
		"""
		if isinstance(self._type, ConstrainedScalarSubtypeSymbol):
			return self._type._constraint

		return None

	@readonly
	def ResolutionFunction(self) -> Nullable[Function]:
		"""
		Read-only property to return the resolution function of the subtype indication (:attr:`_type`): the function its
		resolution function name references (:class:`~pyVHDLModel.Symbol.ResolutionFunctionSymbol`).

		An element resolution (``(resolved) std_ulogic_vector``) resolves the subtype's elements, not the subtype: its
		resolution functions are those of :data:`SubtypeSymbol.Resolution <pyVHDLModel.Symbol.SubtypeSymbol.Resolution>`.

		:returns: The resolution function, or ``None`` if the subtype indication has no resolution function name or it isn't
		          resolved.
		"""
		if not isinstance(self._type, SubtypeSymbol):
			return None
		elif isinstance(resolution := self._type._resolution, ResolutionFunctionSymbol):
			return resolution._reference

		return None

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this subtype declaration: the type mark it is derived from.

		:param region:  The declarative region declaring this subtype.
		:returns:       A generator to iterate (region, place, type mark) tuples: the subtype's type mark.
		"""
		if isinstance(self._type, SubtypeSymbol):
			yield region, self, self._type

	def ResolveReferences(self, designUnit: DesignUnit, region: DeclarativeRegionMixin) -> None:
		"""
		Resolve the type mark of this subtype and set its base type (:attr:`BaseType`): the resolved type, or the base type
		of the resolved subtype; ``None``, if the type mark isn't resolved.

		:param designUnit:                     The design unit containing this declaration.
		:param region:                         The declarative region declaring this declaration.
		:raises UnhandledCriticalWarningError: If a type mark can't be resolved, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		super().ResolveReferences(designUnit, region)

		if (reference := self._type._reference) is None:
			self._baseType = None
		else:
			self._baseType = reference.BaseType

	def ResetReferences(self, designUnit: DesignUnit, region: DeclarativeRegionMixin) -> None:
		"""
		Reset the reference of this subtype's type mark and its base type; a subtype of a predefined library
		(:attr:`~pyVHDLModel.Library.IsPredefined`) keeps its base type.

		:param designUnit: The design unit containing this declaration.
		:param region:     The declarative region declaring this declaration.
		"""
		super().ResetReferences(designUnit, region)

		if not designUnit._parent.IsPredefined:
			self._baseType = None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this subtype declaration and its subtype indication with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSubtype(self)
		self._type.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartSubtype(self)

	def __str__(self) -> str:
		"""
		Formats the subtype declaration.

		**Format:** ``subtype byte is bit_vector``

		The *base type* is rendered, so an unlinked subtype shows ``None``.

		:returns: Formatted subtype declaration.
		"""
		return f"subtype {self._identifier} is {self._baseType}"


@export
@abstractclass
class ScalarType(FullType):
	"""
	Represents a base-class for all scalar types: enumerated, integer, real and physical types.

	.. seealso::

	   * :class:`Ranged scalar type <pyVHDLModel.Type.RangedScalarType>`
	   * :class:`Enumerated type <pyVHDLModel.Type.EnumeratedType>`
	"""

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this scalar type declares implicitly: the equality operators, the ordering operators
		``"<"``, ``"<="``, ``">"`` and ``">="`` (IEEE Std 1076-2008, 9.2.3), ``MINIMUM`` and ``MAXIMUM`` (5.2.6), and
		``TO_STRING`` (5.7).

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		for operatorSymbol in ("<", "<=", ">", ">="):
			operations.append(self._BinaryOperator(operatorSymbol, SimpleSubtypeSymbol(SimpleName("boolean"))))

		for identifier in ("minimum", "maximum"):
			operations.append(self._Function(
				identifier,
				self._TypeMark(),
				(self._Parameter("L", self._TypeMark()), self._Parameter("R", self._TypeMark()))
			))

		operations.append(self._Function(
			"to_string",
			SimpleSubtypeSymbol(SimpleName("string")),
			(self._Parameter("VALUE", self._TypeMark()),)
		))

		return operations


@export
@abstractclass
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
		:param documentation: Optional, the type's documentation. Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity. Default: ``None``, no parent.
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
class LogicalOperatorsMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_TypeMark", "_BinaryOperator", "_UnaryOperator")
):
	"""
	A mixin-class for the enumerated types declaring the logical operators (IEEE Std 1076-2008, 9.2.2): ``boolean`` and
	``bit`` of package ``std.standard``.

	A one-dimensional array type of such an element type declares the logical, shift and logical reduction operators
	(:attr:`~pyVHDLModel.Type.FullType.ImplicitOperations`).

	.. seealso::

	   * :class:`Boolean <pyVHDLModel.STD.StandardPkg.Boolean>`
	   * :class:`Bit <pyVHDLModel.STD.StandardPkg.Bit>`
	"""

	def _CreateLogicalOperators(self) -> list[PredefinedOperator]:
		"""
		Create the logical operators of this type: ``"and"``, ``"or"``, ``"nand"``, ``"nor"``, ``"xor"`` and ``"xnor"``,
		then ``"not"``.

		:returns: List of predefined operators.
		"""
		operations = []
		for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

		operations.append(self._UnaryOperator("not", self._TypeMark()))

		return operations


@export
class MatchingOperatorsMixin(metaclass=ExtendedType, mixin=True, expects=("_TypeMark", "_BinaryOperator")):
	"""
	A mixin-class for the enumerated types declaring the matching relational operators (IEEE Std 1076-2008, 9.2.3):
	``bit`` of package ``std.standard``.

	A one-dimensional array type of such an element type declares the matching operators ``"?="`` and ``"?/="``
	(:attr:`~pyVHDLModel.Type.FullType.ImplicitOperations`).

	.. seealso::

	   * :class:`Bit <pyVHDLModel.STD.StandardPkg.Bit>`
	"""

	def _CreateMatchingOperators(self) -> list[PredefinedOperator]:
		"""
		Create the matching relational operators of this type: ``"?="``, ``"?/="``, ``"?<"``, ``"?<="``, ``"?>"`` and
		``"?>="``.

		:returns: List of predefined operators.
		"""
		operations = []
		for operatorSymbol in ("?=", "?/=", "?<", "?<=", "?>", "?>="):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

		return operations


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
	_literals: list[EnumerationLiteral]  #: List of all enumeration literals, in declaration order.

	def __init__(self, identifier: str, literals: Iterable[EnumerationLiteral], documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an enumerated type definition.

		:param identifier:    The identifier of a model entity.
		:param literals:      List of all enumeration literals, in declaration order.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)

		self._literals = literalList = []
		if literals is not None:
			for literal in literals:
				literalList.append(literal)
				literal.Parent = self

	@readonly
	def Literals(self) -> list[EnumerationLiteral]:
		"""
		Read-only property to access the literals (:attr:`_literals`).

		:returns: List of literals.
		"""
		return self._literals

	def IterateImplicitDeclarations(self) -> Generator[EnumerationLiteral, None, None]:
		"""
		Iterate the enumeration literals this type declaration implies.

		The implicit operations (:attr:`~FullType.ImplicitOperations`) are indexed by the analysis, after the type marks
		are resolved.

		:returns: A generator to iterate the enumeration literals, in declaration order.
		"""
		yield from self._literals

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this enumerated type and its literals with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitEnumeratedType(self)
		visitor.VisitEnumerationTypeDefinition(self)
		for index, literal in enumerate(self._literals):
			if index > 0:
				visitor.VisitElementSeparator(self)

			literal.Visit(visitor)

		visitor.DepartEnumerationTypeDefinition(self)
		visitor.VisitTerminator(self)
		visitor.DepartEnumeratedType(self)

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
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, rng, documentation, parent)

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this integer type declares implicitly: those of a scalar type, the adding, multiplying and
		sign operators, ``"mod"``, ``"rem"``, ``"abs"`` and ``"**"`` with an ``integer`` exponent (IEEE Std 1076-2008,
		9.2.5 to 9.2.8).

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		for operatorSymbol in ("+", "-", "*", "/", "mod", "rem"):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

		for operatorSymbol in ("+", "-", "abs"):
			operations.append(self._UnaryOperator(operatorSymbol, self._TypeMark()))

		operations.append(self._Operator(
			"**",
			self._TypeMark(),
			(self._Parameter("L", self._TypeMark()), self._Parameter("R", SimpleSubtypeSymbol(SimpleName("integer"))))
		))

		return operations

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this integer type and its range with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitIntegerType(self)
		self._range.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartIntegerType(self)

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
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, rng, documentation, parent)

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this floating-point type declares implicitly: those of a scalar type, the adding, multiplying
		and sign operators, ``"abs"`` and ``"**"`` with an ``integer`` exponent (IEEE Std 1076-2008, 9.2.5 to 9.2.8).

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		for operatorSymbol in ("+", "-", "*", "/"):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

		for operatorSymbol in ("+", "-", "abs"):
			operations.append(self._UnaryOperator(operatorSymbol, self._TypeMark()))

		operations.append(self._Operator(
			"**",
			self._TypeMark(),
			(self._Parameter("L", self._TypeMark()), self._Parameter("R", SimpleSubtypeSymbol(SimpleName("integer"))))
		))

		return operations

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this floating-point type and its range with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRealType(self)
		self._range.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartRealType(self)

	def __str__(self) -> str:
		"""
		Formats the floating-point type definition.

		**Format:** ``gain is range 0.0 to 1.0``

		:returns: Formatted floating-point type definition.
		"""
		return f"{self._identifier} is range {self._range}"


@export
class PhysicalUnit(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a unit declaration of a physical type: its primary unit or one of its secondary units.

	A unit name is declared by the physical type's declaration in the declarative region enclosing the type, so it's
	visible like the type itself, e.g. imported by a use clause. The unit's parent is its physical type; the unit is the
	parent of its value.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type distance is range 0 to 1000000 units
	        um;
	      --^^                                        <- Identifier (primary unit)
	        mm = 1000 um;
	      --^^                                        <- Identifier (secondary unit)
	      --     ^^^^^^^                              <- Value
	      end units;
	"""
	_value: Nullable[PhysicalIntegerLiteral]  #: The unit's value in a smaller unit, or ``None`` for the primary unit.

	def __init__(
		self,
		identifier:    str,
		value:         Nullable[PhysicalIntegerLiteral] = None,
		*,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a unit declaration of a physical type.

		:param identifier:    The unit's identifier.
		:param value:         Optional, the unit's value in a smaller unit, ``None`` for the primary unit.
		                      Default: ``None``.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the physical type declaring the unit. Default: ``None``.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._value = value
		if value is not None:
			value.Parent = self

	@readonly
	def NormalizedDesignator(self) -> str:
		"""
		Read-only property to access the normalized designator (:attr:`_normalizedIdentifier`), the key the unit is
		indexed by in a namespace.

		.. seealso::

		   * :term:`Normalized`

		:returns: The normalized identifier of the unit.
		"""
		return self._normalizedIdentifier

	@readonly
	def Value(self) -> Nullable[PhysicalIntegerLiteral]:
		"""
		Read-only property to access the unit's value (:attr:`_value`).

		:returns: The unit's value in a smaller unit, or ``None`` for the primary unit.
		"""
		return self._value

	def __str__(self) -> str:
		"""
		Formats the unit declaration.

		**Format:** ``mm = 1000 um``, or ``um`` for the primary unit

		:returns: Formatted unit declaration.
		"""
		if self._value is None:
			return self._identifier

		return f"{self._identifier} = {self._value}"


@export
class PhysicalType(RangedScalarType, NumericTypeMixin):
	"""
	Represents a physical type definition.

	A physical type is a named entity (:data:`Identifier`) constrained by a range (:data:`Range`), and
	defines a primary unit (:data:`PrimaryUnit`) plus any number of secondary units
	(:data:`SecondaryUnits`). Each unit is a :class:`PhysicalUnit`; the primary unit has no value. The model holds the
	secondary units in a list, so the markers below name list elements.

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

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Units,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     False                  #: The reserved words after ``end`` are optional.
	_primaryUnit:    PhysicalUnit        #: The type's primary unit, which has no value.
	_secondaryUnits: list[PhysicalUnit]  #: List of the type's secondary units, in declaration order.

	def __init__(
		self,
		identifier:     str,
		rng:            Range,
		primaryUnit:    PhysicalUnit,
		secondaryUnits: Iterable[PhysicalUnit],
		documentation:  Nullable[str] = None,
		parent:         Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a physical type definition.

		The physical type becomes the parent of its units.

		:param identifier:     The identifier of a model entity.
		:param rng:            The range constraining this scalar type.
		:param primaryUnit:    The type's primary unit, which has no value.
		:param secondaryUnits: Iterable of the type's secondary units, in declaration order.
		:param documentation:  Optional, the documentation comment associated with this declaration.
		                       Default: ``None``, no documentation.
		:param parent:         Optional, the parent model entity of this entity. Default: ``None``, no parent.
		:raises ValueError:    If parameter 'primaryUnit' is None.
		:raises TypeError:     If parameter 'primaryUnit' is not of type :class:`PhysicalUnit`.
		:raises ValueError:    If parameter 'primaryUnit' has a value.
		:raises ValueError:    If parameter 'secondaryUnits' is None.
		:raises TypeError:     If parameter 'secondaryUnits' is not iterable.
		:raises TypeError:     If an element of parameter 'secondaryUnits' is not of type :class:`PhysicalUnit`.
		:raises ValueError:    If an element of parameter 'secondaryUnits' has no value.
		"""
		super().__init__(identifier, rng, documentation, parent)

		if primaryUnit is None:
			raise ValueError("Parameter 'primaryUnit' is None.")
		elif not isinstance(primaryUnit, PhysicalUnit):
			ex = TypeError("Parameter 'primaryUnit' is not of type 'PhysicalUnit'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(primaryUnit)}'.")
			raise ex
		elif primaryUnit._value is not None:
			ex = ValueError("Parameter 'primaryUnit' has a value.")
			ex.add_note(f"Got value '{primaryUnit._value}'.")
			raise ex

		if secondaryUnits is None:
			raise ValueError("Parameter 'secondaryUnits' is None.")
		elif not isinstance(secondaryUnits, Iterable):
			ex = TypeError("Parameter 'secondaryUnits' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(secondaryUnits)}'.")
			raise ex

		primaryUnit.Parent = self
		self._primaryUnit =  primaryUnit

		self._secondaryUnits = secondaryUnitList = []
		for unit in secondaryUnits:
			if not isinstance(unit, PhysicalUnit):
				ex = TypeError("Element of parameter 'secondaryUnits' is not of type 'PhysicalUnit'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(unit)}'.")
				raise ex
			elif unit._value is None:
				ex = ValueError(f"Element '{unit._identifier}' of parameter 'secondaryUnits' has no value.")
				ex.add_note("Only the primary unit has no value.")
				raise ex

			unit.Parent = self
			secondaryUnitList.append(unit)

	@readonly
	def PrimaryUnit(self) -> PhysicalUnit:
		"""
		Read-only property to access the primary unit (:attr:`_primaryUnit`).

		The primary unit has no value. Formatted, it's the unit's name.

		:returns: The primary unit.
		"""
		return self._primaryUnit

	@readonly
	def SecondaryUnits(self) -> list[PhysicalUnit]:
		"""
		Read-only property to access the secondary units (:attr:`_secondaryUnits`).

		:returns: List of secondary units, in declaration order.
		"""
		return self._secondaryUnits

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this physical type declares implicitly: those of a scalar type, the adding and sign
		operators, ``"abs"``, ``"mod"`` and ``"rem"``, and the multiplying operators with an ``integer`` or ``real``
		operand (IEEE Std 1076-2008, 9.2.5 to 9.2.7).

		The division of two physical values, which returns a value of type *universal_integer*, isn't represented.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		for operatorSymbol in ("+", "-", "mod", "rem"):
			operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

		for operatorSymbol in ("+", "-", "abs"):
			operations.append(self._UnaryOperator(operatorSymbol, self._TypeMark()))

		for scalar in ("integer", "real"):
			operations.append(self._Operator(
				"*",
				self._TypeMark(),
				(self._Parameter("L", self._TypeMark()), self._Parameter("R", SimpleSubtypeSymbol(SimpleName(scalar))))
			))
			operations.append(self._Operator(
				"*",
				self._TypeMark(),
				(self._Parameter("L", SimpleSubtypeSymbol(SimpleName(scalar))), self._Parameter("R", self._TypeMark()))
			))
			operations.append(self._Operator(
				"/",
				self._TypeMark(),
				(self._Parameter("L", self._TypeMark()), self._Parameter("R", SimpleSubtypeSymbol(SimpleName(scalar))))
			))

		return operations

	def IterateImplicitDeclarations(self) -> Generator[PhysicalUnit, None, None]:
		"""
		Iterate the units this type declaration implies: the primary unit, then the secondary units.

		The implicit operations (:attr:`~FullType.ImplicitOperations`) are indexed by the analysis, after the type marks
		are resolved.

		:returns: A generator to iterate the units, in declaration order.
		"""
		yield self._primaryUnit
		yield from self._secondaryUnits

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this physical type, its range and its secondary units with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitPhysicalType(self)
		self._range.Visit(visitor)
		visitor.VisitUnits(self)
		for unit in self._secondaryUnits:
			visitor.VisitSecondaryUnitDeclaration(self, unit._identifier)
			unit._value.Visit(visitor)
			visitor.DepartSecondaryUnitDeclaration(self, unit._identifier)

		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartPhysicalType(self)

	def __str__(self) -> str:
		"""
		Formats the physical type definition.

		**Format:** ``distance is range 0 to 1000 units um; mm = 1000 um;``

		:returns: Formatted physical type definition.
		"""
		units = "; ".join(str(unit) for unit in (self._primaryUnit, *self._secondaryUnits))
		return f"{self._identifier} is range {self._range} units {units};"


@export
@abstractclass
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
	_dimensions:  list[Range]  #: List of all index ranges, one per dimension.
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
		:param documentation:  Optional, the documentation comment associated with this declaration.
		                       Default: ``None``, no documentation.
		:param parent:         Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)

		self._dimensions = dimensions = []
		for index in indices:
			dimensions.append(index)
			index.Parent = self

		self._elementType =     elementSubtype
		elementSubtype.Parent = self

	@readonly
	def Dimensions(self) -> list[Range]:
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

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this array type: its index subtypes, then its element subtype.

		:param region:  The declarative region declaring this type.
		:returns:       A generator to iterate (region, place, type mark) tuples, in declaration order.
		"""
		for dimension in self._dimensions:
			if isinstance(dimension, SubtypeSymbol):
				yield region, self, dimension

		if isinstance(self._elementType, SubtypeSymbol):
			yield region, self, self._elementType

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this array type declares implicitly.

		Every array type declares the equality operators. A one-dimensional array type adds, depending on its element type
		(the base type of the element subtype, known after the element type mark is resolved):

		* discrete element type: the ordering operators ``"<"``, ``"<="``, ``">"``, ``">="`` (IEEE Std 1076-2008,
		  9.2.3), ``MINIMUM`` and ``MAXIMUM`` of two arrays (5.3.2.4);
		* any element type: the concatenation operator ``"&"`` of array and array, array and element, element and array,
		  element and element (9.2.5);
		* scalar element type: ``MINIMUM`` and ``MAXIMUM`` of the elements of an array (5.3.2.4);
		* element type ``bit`` or ``boolean`` (:class:`LogicalOperatorsMixin`): ``"not"``, the binary
		  logical operators of two arrays, the shift operators ``"sll"``, ``"srl"``, ``"sla"``, ``"sra"``, ``"rol"``,
		  ``"ror"`` with an ``integer`` shift amount (9.2.4), the binary logical operators of an element and an array and
		  of an array and an element, and the logical reduction operators (9.2.2);
		* element type ``bit`` (:class:`MatchingOperatorsMixin`): the matching operators ``"?="`` and
		  ``"?/="`` (9.2.3);
		* element type a character type containing only character literals: ``TO_STRING`` (5.3.2.4).

		A parameter or result of the element type has a type mark naming the element subtype, which references it. With an
		unresolved element type mark, only the equality operators and the concatenation of two arrays are created.

		:returns: List of predefined operators and predefined functions.
		"""
		operations = super()._CreateImplicitOperations()
		if len(self._dimensions) != 1:
			return operations

		reference = self._elementType._reference
		if not isinstance(reference, BaseType):
			operations.append(self._BinaryOperator("&", self._TypeMark()))
			return operations

		def elementTypeMark() -> SimpleSubtypeSymbol:
			"""
			Nested function creating a type mark naming the element subtype, which it references.

			:returns: The type mark.
			"""
			symbol =            SimpleSubtypeSymbol(SimpleName(reference._identifier))
			symbol._reference = reference

			return symbol

		element = reference.BaseType
		if isinstance(element, DiscreteTypeMixin):
			for operatorSymbol in ("<", "<=", ">", ">="):
				operations.append(self._BinaryOperator(operatorSymbol, SimpleSubtypeSymbol(SimpleName("boolean"))))

			for identifier in ("minimum", "maximum"):
				operations.append(self._Function(
					identifier,
					self._TypeMark(),
					(self._Parameter("L", self._TypeMark()), self._Parameter("R", self._TypeMark()))
				))

		operations.append(self._BinaryOperator("&", self._TypeMark()))
		operations.append(self._Operator(
			"&",
			self._TypeMark(),
			(self._Parameter("L", self._TypeMark()), self._Parameter("R", elementTypeMark()))
		))
		operations.append(self._Operator(
			"&",
			self._TypeMark(),
			(self._Parameter("L", elementTypeMark()), self._Parameter("R", self._TypeMark()))
		))
		operations.append(self._Operator(
			"&",
			self._TypeMark(),
			(self._Parameter("L", elementTypeMark()), self._Parameter("R", elementTypeMark()))
		))

		if isinstance(element, ScalarType):
			for identifier in ("minimum", "maximum"):
				operations.append(self._Function(identifier, elementTypeMark(), (self._Parameter("L", self._TypeMark()),)))

		if isinstance(element, LogicalOperatorsMixin):
			operations.append(self._UnaryOperator("not", self._TypeMark()))
			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				operations.append(self._BinaryOperator(operatorSymbol, self._TypeMark()))

			for operatorSymbol in ("sll", "srl", "sla", "sra", "rol", "ror"):
				operations.append(self._Operator(
					operatorSymbol,
					self._TypeMark(),
					(self._Parameter("L", self._TypeMark()), self._Parameter("R", SimpleSubtypeSymbol(SimpleName("integer"))))
				))

			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				operations.append(self._Operator(
					operatorSymbol,
					self._TypeMark(),
					(self._Parameter("L", elementTypeMark()), self._Parameter("R", self._TypeMark()))
				))
				operations.append(self._Operator(
					operatorSymbol,
					self._TypeMark(),
					(self._Parameter("L", self._TypeMark()), self._Parameter("R", elementTypeMark()))
				))

			for operatorSymbol in ("and", "or", "nand", "nor", "xor", "xnor"):
				operations.append(self._UnaryOperator(operatorSymbol, elementTypeMark()))

		if isinstance(element, MatchingOperatorsMixin):
			for operatorSymbol in ("?=", "?/="):
				operations.append(self._BinaryOperator(operatorSymbol, elementTypeMark()))

		if isinstance(element, EnumeratedType) and all(
			isinstance(literal, CharacterEnumerationLiteral) for literal in element._literals
		):
			operations.append(self._Function(
				"to_string",
				SimpleSubtypeSymbol(SimpleName("string")),
				(self._Parameter("VALUE", self._TypeMark()),)
			))

		return operations

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this array type, its index ranges and its element subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitArrayType(self)
		visitor.VisitIndexConstraint(self)
		for index, dimension in enumerate(self._dimensions):
			if index > 0:
				visitor.VisitElementSeparator(self)

			dimension.Visit(visitor)
			if isinstance(dimension, SimpleSubtypeSymbol):
				visitor.VisitBox(self)

		visitor.DepartIndexConstraint(self)
		visitor.VisitOf(self)
		self._elementType.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartArrayType(self)

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
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
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

	def DenoteBy(
		self,
		name:   Name,
		region: DeclarativeRegionMixin,
		place:  ModelEntity,
		symbol: Symbol
	) -> Nullable[ModelEntity]:
		"""
		Return this record element, the model entity a name in a type mark denotes.

		:param name:   The name denoting this declaration, a part of the type mark.
		:param region: The declarative region containing the type mark.
		:param place:  The declaration containing the type mark.
		:param symbol: The type mark.
		:returns:      This record element.
		"""
		return self

	def Copy(self) -> Self:
		"""
		Create a copy of this record type element.

		The copy has no parent. Its subtype is a copy of this element's subtype.

		:returns: The new record type element.
		"""
		return self.__class__(self._identifiers, self._subtype.Copy(), self._documentation)

	def _SplitInParent(self) -> tuple[Self, ...]:
		"""
		Split this element declaration by the mutator of its parent (``SplitElement()``).

		:returns: Tuple of element declarations, one per identifier in list order, starting with this element declaration.
		"""
		return self._parent.SplitElement(self)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this record element declaration and its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRecordTypeElement(self)
		self._subtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartRecordTypeElement(self)

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

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Record,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     False                   #: The reserved words after ``end`` are optional.
	_elements:             list[RecordTypeElement]       #: List of all element declarations, in declaration order.
	_elementsByIdentifier: dict[str, RecordTypeElement]  #: All element declarations, indexed by normalized identifier.

	def __init__(self, identifier: str, elements: Nullable[Iterable[RecordTypeElement]] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a record type definition.

		:param identifier:    The identifier of a model entity.
		:param elements:      Optional, list of all element declarations, in declaration order.
		                      Default: ``None``, no elements.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)

		self._elements =             elementList = []
		self._elementsByIdentifier = elementsByIdentifier = {}
		if elements is not None:
			for element in elements:
				elementList.append(element)
				for normalizedIdentifier in element._normalizedIdentifiers:
					elementsByIdentifier[normalizedIdentifier] = element

				element.Parent = self

	@readonly
	def Elements(self) -> list[RecordTypeElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements

	@readonly
	def ElementsByIdentifier(self) -> dict[str, RecordTypeElement]:
		"""
		Read-only property to access the elements by identifier (:attr:`_elementsByIdentifier`).

		An element declaring several identifiers (``a, b : bit``) is indexed by each of them.

		:returns: Dictionary of elements, indexed by normalized identifier.
		"""
		return self._elementsByIdentifier

	def SplitElement(self, element: RecordTypeElement) -> tuple[RecordTypeElement, ...]:
		"""
		Split an element with an identifier list into one element per identifier.

		The element keeps its first identifier. For every other identifier, a new element is created by its ``Copy()``
		and inserted right after it, in list order; its parent is set to this record type. An element declaring one
		identifier is unchanged.

		:param element:         The element to split.
		:returns:               Tuple of elements, one per identifier in list order, starting with the split element.
		:raises ValueError:     If parameter 'element' is ``None``.
		:raises TypeError:      If parameter 'element' is not of type :class:`RecordTypeElement`.
		:raises NotAChildError: If parameter 'element' is not an element of this record type.

		.. seealso::

		   :meth:`~pyVHDLModel.Base.MultipleNamedEntityMixin.Split`
		      |rarr| Split a declaration with an identifier list.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, RecordTypeElement):
			ex = TypeError("Parameter 'element' is not of type 'RecordTypeElement'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		for index, item in enumerate(self._elements):
			if item is element:
				break
		else:
			identifiers = ", ".join(element._identifiers)
			raise NotAChildError(
				f"{getTypeName(element)} '{identifiers}' is not an element of this {getTypeName(self)}.",
				element=element,
				parent=self
			)

		if len(element._identifiers) == 1:
			return (element, )

		declarations = element._SplitCopies()
		element._KeepIdentifier(0)
		self._elements[index + 1:index + 1] = declarations
		for declaration in declarations:
			for normalizedIdentifier in declaration._normalizedIdentifiers:
				self._elementsByIdentifier[normalizedIdentifier] = declaration

			declaration.Parent = self

		return (element, *declarations)

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this record type: the element subtypes.

		:param region:  The declarative region declaring this type.
		:returns:       A generator to iterate (region, place, type mark) tuples, in declaration order.
		"""
		for element in self._elements:
			if isinstance(element._subtype, SubtypeSymbol):
				yield region, self, element._subtype

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this record type and its element declarations with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRecordType(self)
		for element in self._elements:
			element.Visit(visitor)

		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartRecordType(self)

	def __str__(self) -> str:
		"""
		Formats the record type definition.

		**Format:** ``frame is record a : bit;``

		:returns: Formatted record type definition.
		"""
		return f"{self._identifier} is record {'; '.join(str(re) for re in self._elements)};"


@export
class ProtectedType(FullType, ProtectedTypeDeclarationRegionMixin, WithoutStatementsMixin):
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

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Protected,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     False                      #: The reserved words after ``end`` are optional.
	def __init__(self, identifier: str, declaredItems: Union[list, Iterator] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a protected type declaration.

		:param identifier:    The identifier of a model entity.
		:param declaredItems: Optional, all items declared by this protected type; only subprograms are legal.
		                      Default: ``None``, no declared items.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)
		ProtectedTypeDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)

	@FullType.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		FullType.Parent.fset(self, parent)
		self._ConnectParentNamespace(parent)

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this protected type declares implicitly: none, as it has no equality
		(IEEE Std 1076-2008, 9.2.3).

		:returns: An empty list.
		"""
		return []

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this protected type declaration and its methods with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitProtectedType(self)
		self._VisitDeclaredItems(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartProtectedType(self)

	@readonly
	def Methods(self) -> list[Union[Procedure, Function]]:
		"""
		Read-only property to return the declared methods, in declaration order.

		A protected type declares nothing but subprograms, so this is every declared item
		(:attr:`_declaredItems`). It is kept as a named view because "method" is the VHDL term for a
		protected type's subprograms.

		:returns: List of methods, in declaration order.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure

		return [item for item in self._declaredItems if isinstance(item, (Function, Procedure))]


@export
class ProtectedTypeBody(FullType, SequentialDeclarationRegionMixin, WithoutStatementsMixin):
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

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Protected, ReservedWord.Body)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     False                                        #: The reserved words after ``end`` are optional.
	def __init__(self, identifier: str, declaredItems: Union[list, Iterator] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a protected type body.

		:param identifier:    The identifier of a model entity.
		:param declaredItems: Optional, iterable of all items declared in this body. Default: ``None``, no declared items.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, documentation, parent)
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)

	@FullType.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		FullType.Parent.fset(self, parent)
		self._ConnectParentNamespace(parent)

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this protected type body declares implicitly: none, as the protected type declares them.

		:returns: An empty list.
		"""
		return []

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this protected type body and its declared items with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitProtectedTypeBody(self)
		self._VisitDeclaredItems(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartProtectedTypeBody(self)

	# FIXME: needs to be declared items or so
	@readonly
	def Methods(self) -> list[Union[Procedure, Function]]:
		"""
		Read-only property to return the implemented methods, in declaration order.

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
		:param documentation:     Optional, the documentation comment associated with this declaration.
		                          Default: ``None``, no documentation.
		:param parent:            Optional, the parent model entity of this entity. Default: ``None``, no parent.
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

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this access type: the subtype its values designate.

		:param region:  The declarative region declaring this type.
		:returns:       A generator to iterate (region, place, type mark) tuples: the designated subtype.
		"""
		if isinstance(self._designatedSubtype, SubtypeSymbol):
			yield region, self, self._designatedSubtype

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this access type and its designated subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAccessType(self)
		self._designatedSubtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartAccessType(self)

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
		:param documentation:     Optional, the documentation comment associated with this declaration.
		                          Default: ``None``, no documentation.
		:param parent:            Optional, the parent model entity of this entity. Default: ``None``, no parent.
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

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this file type: the subtype of its values.

		:param region:  The declarative region declaring this type.
		:returns:       A generator to iterate (region, place, type mark) tuples: the designated subtype.
		"""
		if isinstance(self._designatedSubtype, SubtypeSymbol):
			yield region, self, self._designatedSubtype

	def _CreateImplicitOperations(self) -> list[PredefinedOperation]:
		"""
		Create the operations this file type declares implicitly: none represented yet. A file type has no equality
		(IEEE Std 1076-2008, 9.2.3); its file operations ``FILE_OPEN``, ``FILE_CLOSE``, ``READ``, ``WRITE``, ``FLUSH`` and
		``ENDFILE`` (5.5.2) aren't represented.

		:returns: An empty list.
		"""
		return []

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this file type and its designated subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitFileType(self)
		self._designatedSubtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartFileType(self)

	def __str__(self) -> str:
		"""
		Formats the file type definition.

		**Format:** ``ft is file of character``

		:returns: Formatted file type definition.
		"""
		return f"{self._identifier} is file of {self._designatedSubtype}"
