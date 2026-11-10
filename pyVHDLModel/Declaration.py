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


"""
from __future__             import annotations

from enum                   import unique, Enum
from typing                 import TYPE_CHECKING, ClassVar, Generator, Iterable, Union, Optional as Nullable

from pyTooling.Decorators   import export, readonly
from pyTooling.Warning      import WarningCollector

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, ReservedWord as _ReservedWord
from pyVHDLModel.Expression import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Exception  import UnresolvedNameWarning, UnresolvedTypeMarkWarning
from pyVHDLModel.Name       import Name, SimpleName
from pyVHDLModel.Symbol     import PossibleReference, Symbol, SubtypeSymbol

if TYPE_CHECKING:
	from pyVHDLModel.DesignUnit import DesignUnit
	from pyVHDLModel.Regions  import DeclarativeRegionMixin
	from pyVHDLModel.Visitor  import Visitor



ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
@unique
class EntityClass(Enum):
	"""An ``EntityClass`` is an enumeration. It represents a VHDL language entity class (``entity``, ``label``, ...)."""

	Entity =        0   #: Entity
	Architecture =  1   #: Architecture
	Configuration = 2   #: Configuration
	Procedure =     3   #: Procedure
	Function =      4   #: Function
	Package =       5   #: Package
	Type =          6   #: Type
	Subtype =       7   #: Subtype
	Constant =      8   #: Constant
	Signal =        9   #: Signal
	Variable =      10  #: Variable
	Component =     11  #: Component
	Label =         12  #: Label
	Literal =       13  #: Literal
	Units =         14  #: Units
	Group =         15  #: Group
	File =          16  #: File
	Property =      17  #: Property
	Sequence =      18  #: Sequence
	View =          19  #: View
	Others =        20  #: Others

	__RESERVED_WORDS: ClassVar[dict[int, _ReservedWord]] = {
		0:  _ReservedWord.Entity,
		1:  _ReservedWord.Architecture,
		2:  _ReservedWord.Configuration,
		3:  _ReservedWord.Procedure,
		4:  _ReservedWord.Function,
		5:  _ReservedWord.Package,
		6:  _ReservedWord.Type,
		7:  _ReservedWord.Subtype,
		8:  _ReservedWord.Constant,
		9:  _ReservedWord.Signal,
		10: _ReservedWord.Variable,
		11: _ReservedWord.Component,
		12: _ReservedWord.Label,
		13: _ReservedWord.Literal,
		14: _ReservedWord.Units,
		15: _ReservedWord.Group,
		16: _ReservedWord.File,
		17: _ReservedWord.Property,
		18: _ReservedWord.Sequence,
		19: _ReservedWord.View
	}  #: The reserved word of each entity class, by value; ``Others`` has none.

	@readonly
	def ReservedWord(self) -> Nullable[_ReservedWord]:
		"""
		Read-only property to return the reserved word of the entity class.

		:returns: The reserved word, or ``None`` for ``EntityClass.Others``.
		"""
		return self.__RESERVED_WORDS.get(self.value, None)


@export
class Attribute(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents an attribute declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      attribute TotalBits : natural;
	"""

	_subtype: Symbol  #: Reference to the attribute's subtype.

	def __init__(
		self,
		identifier: str,
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an attribute declaration.

		:param identifier:    The identifier of a model entity.
		:param subtype:       Reference to the attribute's subtype.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this attribute declaration and its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAttribute(self)
		self._subtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartAttribute(self)

	@readonly
	def Subtype(self) -> None:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this attribute declaration: the type mark of its values.

		:param region:  The declarative region declaring this attribute.
		:returns:       A generator to iterate (region, place, type mark) tuples: the attribute's type mark.
		"""
		if isinstance(self._subtype, SubtypeSymbol):
			yield region, self, self._subtype

	def __str__(self) -> str:
		"""
		Formats the attribute declaration.

		**Format:** ``attribute myAttribute: bit``

		:returns: Formatted attribute declaration.
		"""
		return f"attribute {self._identifier}: {self._subtype}"


@export
class AttributeSpecification(ModelEntity, DocumentedEntityMixin):
	"""
	Represents an attribute specification.

	.. admonition:: Example

	   .. code-block:: VHDL

	      attribute TotalBits of BusType : subtype is 32;
	"""

	_identifiers: list[Name]      #: List of all names the attribute is specified for.
	_attribute: Name              #: Reference to the specified attribute.
	_entityClass: EntityClass     #: The entity class the named items belong to.
	_expression: ExpressionUnion  #: The value assigned to the attribute.

	def __init__(
		self,
		identifiers: Iterable[Name],
		attribute: Name,
		entityClass: EntityClass,
		expression: ExpressionUnion,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an attribute specification.

		:param identifiers:   List of all names the attribute is specified for.
		:param attribute:     Reference to the specified attribute.
		:param entityClass:   The entity class the named items belong to.
		:param expression:    The value assigned to the attribute.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(parent)
		DocumentedEntityMixin.__init__(self, documentation)

		self._identifiers = identifierList = []  # TODO: convert to dict
		for identifier in identifiers:
			identifierList.append(identifier)
			identifier.Parent = self

		self._attribute = attribute
		attribute.Parent = self

		self._entityClass = entityClass

		self._expression = expression
		expression.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this attribute specification, its attribute, its entity specification and its expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAttributeSpecification(self)
		self._attribute.Visit(visitor)
		visitor.VisitEntitySpecification(self)
		for index, name in enumerate(self._identifiers):
			if index > 0:
				visitor.VisitNameListSeparator(self)

			name.Visit(visitor)

		visitor.DepartEntitySpecification(self)
		visitor.VisitIs(self)
		self._expression.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartAttributeSpecification(self)

	@readonly
	def Identifiers(self) -> list[Name]:
		"""
		Read-only property to access the identifiers (:attr:`_identifiers`).

		:returns: List of identifiers.
		"""
		return self._identifiers

	@readonly
	def Attribute(self) -> Name:
		"""
		Read-only property to access the attribute (:attr:`_attribute`).

		:returns: The attribute.
		"""
		return self._attribute

	@readonly
	def EntityClass(self) -> EntityClass:
		"""
		Read-only property to access the entity class (:attr:`_entityClass`).

		:returns: The entity class.
		"""
		return self._entityClass

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression


# TODO: move somewhere else
@export
class Alias(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents an alias declaration.

	:attr:`Name` is a :class:`~pyVHDLModel.Symbol.Symbol` - like every other cross-reference in this
	model - rather than a bare :class:`~pyVHDLModel.Name.Name`, so it participates in the usual
	resolve-later mechanism (:attr:`~pyVHDLModel.Symbol.Symbol.Reference` /
	:attr:`~pyVHDLModel.Symbol.Symbol.IsResolved`). Unlike ``PackageReferenceSymbol`` and similar,
	there is no single fixed :class:`~pyVHDLModel.Symbol.PossibleReference` value that always fits: an
	alias without a subtype indication can refer to almost anything nameable (an object, a type, a
	subprogram, a literal, ...), while an alias *with* a subtype indication can - per the LRM - only
	ever refer to an object (a constant, variable, signal, or file); the ``possibleReferences`` passed
	to the ``Symbol`` should reflect whichever case applies.

	.. admonition:: Example

	   .. code-block:: VHDL

	      alias a : bit_vector(3 downto 0) is s(3 downto 0);
	      --        ^^^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^^^
	      --        optional Subtype           Name

	      alias b is s;
	      --          ^
	      --          Name
	"""

	_IMPLICIT_OPERATIONS: ClassVar[frozenset[str]] = frozenset((
		"to_string", "to_bstring", "to_binary_string", "to_ostring", "to_octal_string", "to_hstring", "to_hex_string",
		"minimum", "maximum", "deallocate", "file_open", "file_close", "read", "write", "endfile", "flush"
	))  #: Normalized identifiers of implicitly declared operations (IEEE Std 1076-2008, 5), which aren't represented.

	_name:    Symbol                   #: Reference to the name being aliased.
	_subtype: Nullable[SubtypeSymbol]  #: Reference to the alias' subtype, or ``None`` if none was given.

	def __init__(
		self,
		identifier:    str,
		name:          Symbol,
		subtype:       Nullable[SubtypeSymbol] = None,
		documentation: Nullable[str] =            None,
		parent:        Nullable[ModelEntity] =    None
	) -> None:
		"""
		Initializes an alias declaration.

		:param identifier:    The identifier of a model entity.
		:param name:          Reference to the name being aliased.
		:param subtype:       Optional, reference to the alias' subtype. Default: ``None``, no subtype indication.
		:param documentation: Optional, the documentation comment associated with this declaration.
		                      Default: ``None``, no documentation.
		:param parent:        Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._name = name
		name.Parent = self

		self._subtype = subtype
		if subtype is not None:
			subtype.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this alias declaration, its subtype (if any) and its name with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAlias(self)
		if self._subtype is not None:
			self._subtype.Visit(visitor)

		visitor.VisitIs(self)
		self._name.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartAlias(self)

	@readonly
	def Name(self) -> Symbol:
		"""
		Read-only property to access the name (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	@readonly
	def Subtype(self) -> Nullable[SubtypeSymbol]:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype, or ``None`` if not set.
		"""
		return self._subtype

	@readonly
	def IsOverloadable(self) -> bool:
		"""
		Check if this alias is overloadable: it has no subtype indication, and its name may denote a subprogram or an
		enumeration literal.

		The resolved name (:attr:`~pyVHDLModel.Symbol.Symbol.Reference`) decides, else the name's possible references,
		e.g. ``alias To_SLV is To_StdLogicVector [std_ulogic_vector return std_logic_vector];``.

		:returns: ``True``, if this alias is overloadable.
		"""
		if self._subtype is not None:
			return False
		elif (reference := self._name._reference) is not None:
			return reference.IsOverloadable

		overloadables = PossibleReference.SubProgram | PossibleReference.EnumLiteral
		return (self._name._possibleReferences & overloadables) != PossibleReference.Unknown

	def IterateTypeMarks(
		self,
		region: DeclarativeRegionMixin
	) -> Generator[tuple[DeclarativeRegionMixin, ModelEntity, SubtypeSymbol], None, None]:
		"""
		Iterate the type marks of this alias: the type mark of its subtype indication, if it has one.

		:param region:  The declarative region declaring this alias.
		:returns:       A generator to iterate (region, place, type mark) tuples: the alias' subtype indication, if
		                given.
		"""
		if self._subtype is not None:
			yield region, self, self._subtype

	def ResolveReferences(self, designUnit: DesignUnit, region: DeclarativeRegionMixin) -> None:
		"""
		Resolve the name of this alias, if it has no subtype indication, then its type marks.

		The name is resolved, if it's a simple name or an expanded name ``lib.pkg.item``
		(:attr:`~pyVHDLModel.Name.Name.IsExpandedName`) and denotes a declaration, which isn't overloadable, e.g. a type or
		an object (:meth:`~pyVHDLModel.Regions.DeclarativeRegionMixin.LookupName`); the alias isn't overloadable then
		(:attr:`IsOverloadable`). The name of an implicitly declared operation (:attr:`_IMPLICIT_OPERATIONS`, an operator
		symbol) isn't looked up, as the model doesn't represent these.

		:param designUnit:                     The design unit containing this declaration.
		:param region:                         The declarative region declaring this declaration.
		:raises UnhandledCriticalWarningError: If the name can't be resolved, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedNameWarning`.
		:raises UnhandledCriticalWarningError: If a type mark can't be resolved, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		if self._subtype is None:
			name =       self._name._name
			isImplicit = name._normalizedIdentifier in self._IMPLICIT_OPERATIONS or name.IsOperatorSymbol
			if (isinstance(name, SimpleName) or name.IsExpandedName) and not isImplicit:
				self._name._reference = None
				aliased =               region.LookupName(self, self._name, name, UnresolvedNameWarning)
				if len(aliased) > 0 and not aliased[0].IsOverloadable:
					self._name._reference = aliased[0]

		super().ResolveReferences(designUnit, region)

	def ResetReferences(self, designUnit: DesignUnit, region: DeclarativeRegionMixin) -> None:
		"""
		Reset the reference of this alias' name, if it has no subtype indication, and the references of its type marks.

		:param designUnit: The design unit containing this declaration.
		:param region:     The declarative region declaring this declaration.
		"""
		if self._subtype is None:
			self._name._reference = None

		super().ResetReferences(designUnit, region)

	def DenoteBy(
		self,
		name:   Name,
		region: DeclarativeRegionMixin,
		place:  ModelEntity,
		symbol: Symbol
	) -> Nullable[ModelEntity]:
		"""
		Determine the model entity a name denoting this alias denotes, as a part of a type mark.

		The type mark is an attribute name like ``al'subtype``. An alias with a subtype indication denotes itself, an object
		alias; otherwise, the declaration its name references says what it denotes (e.g. an object or a type).

		:param name:                           The name denoting this declaration, a part of the type mark.
		:param region:                         The declarative region containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              The denoted model entity, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If the alias' name isn't resolved, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		:raises UnhandledCriticalWarningError: If the declaration the alias' name references can't be denoted, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		if self._subtype is not None:
			return self
		elif (reference := self._name._reference) is None:
			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Name of prefix '{name!s}' of type mark '{symbol._name!s}' isn't resolved.",
				symbol=symbol,
				place=place,
				namespaces=(region._namespace, )
			))
			return None

		return reference.DenoteBy(name, region, place, symbol)

	def __str__(self) -> str:
		"""
		Formats the alias declaration.

		**Format:** ``alias myAlias : bit is target``, or without the subtype when none was given

		:returns: Formatted alias declaration.
		"""
		subtype = f" : {self._subtype}" if self._subtype is not None else ""
		return f"alias {self._identifier}{subtype} is {self._name}"
