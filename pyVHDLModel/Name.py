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

VHDL uses *names* to express cross-references from *usage locations* to *declarations*. Here, *names* are single or
combined identifiers. :mod:`Symbols <pyVHDLModel.Symbol>` are structures representing a *name* and a reference
(pointer) to the referenced vhdl language entity.
"""
from __future__            import annotations

from enum                  import Enum, auto
from typing                import TYPE_CHECKING, Iterable, Optional as Nullable, Self

from pyTooling.Common      import StringEnum
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractclass
from pyTooling.Warning     import WarningCollector

from pyVHDLModel.Base      import ModelEntity, ExpressionUnion
if TYPE_CHECKING:
	from pyVHDLModel            import Library
	from pyVHDLModel.DesignUnit import DesignUnit, Package
	from pyVHDLModel.Regions    import DeclarationRegionMixin
	from pyVHDLModel.Symbol     import Symbol
	from pyVHDLModel.Type       import BaseType
	from pyVHDLModel.Visitor    import Visitor


@export
class PredefinedAttribute(StringEnum):
	"""
	A ``PredefinedAttribute`` is an enumeration of VHDL's predefined attributes (IEEE Std 1076-2019, 16.2).

	A member is a :class:`str`: its value is the attribute's designator in lower case, e.g.
	``PredefinedAttribute.ReverseRange == "reverse_range"``. An attribute name (:class:`AttributeName`) of a predefined
	attribute references its member (:attr:`AttributeName.PredefinedAttribute`).

	Each member states the revision of IEEE Std 1076 that first defined it. VHDL-87 defined ``'behavior`` and
	``'structure``, which later revisions don't.
	"""

	Active =        "active"         #: Attribute since VHDL-87.
	Ascending =     "ascending"      #: Attribute since VHDL-93.
	Base =          "base"           #: Attribute since VHDL-87.
	Behavior =      "behavior"       #: Attribute of VHDL-87 only.
	Converse =      "converse"       #: Attribute since VHDL-2019.
	Delayed =       "delayed"        #: Attribute since VHDL-87.
	Driving =       "driving"        #: Attribute since VHDL-93.
	DrivingValue =  "driving_value"  #: Attribute since VHDL-93.
	Element =       "element"        #: Attribute since VHDL-2008.
	Event =         "event"          #: Attribute since VHDL-87.
	High =          "high"           #: Attribute since VHDL-87.
	Image =         "image"          #: Attribute since VHDL-93.
	InstanceName =  "instance_name"  #: Attribute since VHDL-93.
	LastActive =    "last_active"    #: Attribute since VHDL-87.
	LastEvent =     "last_event"     #: Attribute since VHDL-87.
	LastValue =     "last_value"     #: Attribute since VHDL-87.
	Left =          "left"           #: Attribute since VHDL-87.
	LeftOf =        "leftof"         #: Attribute since VHDL-87.
	Length =        "length"         #: Attribute since VHDL-87.
	Low =           "low"            #: Attribute since VHDL-87.
	PathName =      "path_name"      #: Attribute since VHDL-93.
	Pos =           "pos"            #: Attribute since VHDL-87.
	Pred =          "pred"           #: Attribute since VHDL-87.
	Quiet =         "quiet"          #: Attribute since VHDL-87.
	Range =         "range"          #: Attribute since VHDL-87.
	ReverseRange =  "reverse_range"  #: Attribute since VHDL-87.
	Right =         "right"          #: Attribute since VHDL-87.
	RightOf =       "rightof"        #: Attribute since VHDL-87.
	SimpleName =    "simple_name"    #: Attribute since VHDL-93.
	Stable =        "stable"         #: Attribute since VHDL-87.
	Structure =     "structure"      #: Attribute of VHDL-87 only.
	Subtype =       "subtype"        #: Attribute since VHDL-2008.
	Succ =          "succ"           #: Attribute since VHDL-87.
	Transaction =   "transaction"    #: Attribute since VHDL-87.
	Val =           "val"            #: Attribute since VHDL-87.
	Value =         "value"          #: Attribute since VHDL-93.


@export
class DenotationKind(Enum):
	"""
	The kind of entity a name denotes (:class:`Denotation`).
	"""

	Library = auto()  #: A library, denoted by its logical name.
	Package = auto()  #: A package.
	Type =    auto()  #: A type or a subtype.
	Object =  auto()  #: An object, an element of a composite object, or an alias of an object.


@export
class Denotation(metaclass=ExtendedType, slots=True):
	"""
	Represents what a name denotes: a library, a package, a type or subtype, or an object.

	A name is resolved part by part (:meth:`Name.Denote`): ``rec.f'subtype`` denotes the object ``rec``, then its record
	element ``f``, which is an object of the element's subtype, then that subtype. An object is represented by its type
	or subtype only.
	"""

	_kind:   DenotationKind                #: The kind of entity the name denotes.
	_entity: Library | Package | BaseType  #: The library, the package, the type or subtype, or the object's subtype.

	def __init__(self, kind: DenotationKind, entity: Library | Package | BaseType) -> None:
		"""
		Initializes a denotation.

		:param kind:   The kind of entity the name denotes.
		:param entity: The library, the package, the type or subtype, or the type or subtype of the object.
		"""
		self._kind =   kind
		self._entity = entity

	@readonly
	def Kind(self) -> DenotationKind:
		"""
		Read-only property to access the kind of entity the name denotes (:attr:`_kind`).

		:returns: The kind of entity.
		"""
		return self._kind

	@readonly
	def Entity(self) -> Library | Package | BaseType:
		"""
		Read-only property to access the denoted entity (:attr:`_entity`).

		:returns: The library, the package, the type or subtype, or the type or subtype of the denoted object.
		"""
		return self._entity


@export
@abstractclass
class Name(ModelEntity):
	"""
	``Name`` is the base-class for all *names* in the VHDL language model.

	.. seealso::

	   * :class:`Simple name <pyVHDLModel.Name.SimpleName>`
	   * :class:`Parenthesis name <pyVHDLModel.Name.ParenthesisName>`
	   * :class:`Indexed name <pyVHDLModel.Name.IndexedName>`
	   * :class:`Sliced name <pyVHDLModel.Name.SlicedName>`
	   * :class:`Selected name <pyVHDLModel.Name.SelectedName>`
	   * :class:`Attribute name <pyVHDLModel.Name.AttributeName>`
	   * :class:`Open name <pyVHDLModel.Name.OpenName>`
	"""

	_identifier: str            #: The name's identifier.
	_normalizedIdentifier: str  #: The normalized (lower case) identifier.
	# TODO: seams to be unused. There is no reverse linking, or?
	_root: Nullable[Name]       #: Reference to the root of the name chain.
	_prefix: Nullable[Name]     #: Reference to the name's prefix, or ``None`` for a simple name.

	def __init__(self, identifier: str, prefix: Nullable[Name] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name.

		:param identifier: The name's identifier.
		:param prefix:     Optional, reference to the name's prefix. Default: ``None``, a simple name.
		:param parent:     Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(parent)

		self._identifier = identifier
		self._normalizedIdentifier = identifier.lower()

		if prefix is None:
			self._prefix = None
			self._root = self
		else:
			self._prefix = prefix
			self._root = prefix._root

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property to access the identifier this name references (:attr:`_identifier`).

		:returns: The referenced identifier.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> str:
		"""
		Read-only property to access the normalized identifier this name references (:attr:`_normalizedIdentifier`).

		:returns: The referenced identifier (normalized).
		"""
		return self._normalizedIdentifier

	@readonly
	def Root(self) -> Name:
		"""
		Read-only property to access the root (left-most) element in a chain of names (:attr:`_root`).

		In case the name is a :class:`simple name <SimpleName>`, the root points to the name itself.

		:returns: The name's root element.
		"""
		return self._root

	@readonly
	def Prefix(self) -> Nullable[Name]:
		"""
		Read-only property to access the name's prefix in a chain of names (:attr:`_prefix`).

		:returns: The name left from current name, if not a simple name, otherwise ``None``.
		"""
		return self._prefix

	@readonly
	def HasPrefix(self) -> bool:
		"""
		Check if the name has a prefix, i.e. :attr:`_prefix` is set.

		This is true for all names except :class:`simple names <SimpleName>`.

		:returns: ``True``, if the name has a prefix.
		"""
		return self._prefix is not None

	@readonly
	def IsOperatorSymbol(self) -> bool:
		"""
		Check if the name is an operator symbol (:attr:`_identifier` in quotation marks).

		An operator symbol names an operator function, e.g. ``"and"`` in an alias declaration.

		:returns: ``True``, if the name is an operator symbol.
		"""
		return self._identifier.startswith('"')

	@readonly
	def IsExpandedName(self) -> bool:
		"""
		Check if the name is an expanded name ``library.package.item``.

		A selected name ``x.y`` may also select an element of a record object, so only a selected name, whose prefix is a
		selected name of a simple name, is an expanded name here. Selected names override this property.

		:returns: ``True``, if the name is an expanded name ``library.package.item``.
		"""
		return False

	def Copy(self) -> Self:
		"""
		Create a copy of this name.

		The copy has no parent. Its prefix, if any, is a copy of this name's prefix.

		:returns: The new name.
		"""
		prefix = None if self._prefix is None else self._prefix.Copy()
		return self.__class__(self._identifier, prefix)

	def Denote(
		self,
		region:     DeclarationRegionMixin,
		designUnit: DesignUnit,
		place:      ModelEntity,
		symbol:     Symbol
	) -> Nullable[Denotation]:
		"""
		Determine what this name denotes as a part of a type mark, which is an attribute name.

		The type mark is an attribute name like ``rec.f'subtype``. A name resolves its prefix first and applies itself to
		what the prefix denotes. A kind of name, which doesn't implement it (e.g. an indexed or a sliced name), is reported
		as unsupported.

		:param region:                         The declarative region containing the type mark.
		:param designUnit:                     The design unit containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              What this name denotes, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If this kind of name isn't supported as a part of a type mark, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		from pyVHDLModel.Exception import UnresolvedTypeMarkWarning

		WarningCollector.Raise(UnresolvedTypeMarkWarning(
			f"Prefix '{self!s}' of type mark '{symbol._name!s}' isn't supported: {self.__class__.__name__}.",
			symbol=symbol,
			place=place,
			namespaces=(region._namespace, )
		))
		return None

	def __repr__(self) -> str:
		"""
		Formats a representation of the name.

		**Format:** ``Name: 'sig'``

		:returns: String representation of the name.
		"""
		return f"Name: '{self.__str__()}'"

	def __str__(self) -> str:
		"""
		Formats the name.

		**Format:** ``sig``

		:returns: Formatted name.
		"""
		return self._identifier


@export
class SimpleName(Name):
	"""
	A *simple name* is a name made from a single word.

	For example, the entity name in an architecture declaration is a simple name, while the name of the architecture
	itself is an identifier. The simple name references is again an identifier in the entity declaration, thus names
	reference other (already) declared language entities.
	"""

	def Denote(
		self,
		region:     DeclarationRegionMixin,
		designUnit: DesignUnit,
		place:      ModelEntity,
		symbol:     Symbol
	) -> Nullable[Denotation]:
		"""
		Determine what this simple name denotes as a part of a type mark, which is an attribute name.

		The type mark is an attribute name like ``s'subtype``. The logical name of a visible library (``work`` or a library
		clause, :meth:`~pyVHDLModel.DesignUnit.DesignUnit.IsLibraryVisible`) denotes the library. Otherwise, the name is
		looked up at the place (:meth:`~pyVHDLModel.Regions.DeclarationRegionMixin.LookupName`) and the declaration says
		what it denotes (:meth:`~pyVHDLModel.Base.ModelEntity.DenoteBy`).

		:param region:                         The declarative region containing the type mark.
		:param designUnit:                     The design unit containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              What this name denotes, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If the name isn't visible, is ambiguous, or denotes neither an object, a type
		                                       nor a package, and no :class:`~pyTooling.Warning.WarningCollector` collects
		                                       the :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		from pyVHDLModel.Exception import UnresolvedTypeMarkWarning

		normalizedIdentifier = self._normalizedIdentifier
		if normalizedIdentifier == "work":
			return Denotation(DenotationKind.Library, designUnit._parent)
		elif designUnit.IsLibraryVisible(normalizedIdentifier):
			if (library := designUnit._parent._parent._libraries.get(normalizedIdentifier)) is not None:
				return Denotation(DenotationKind.Library, library)

		if len(declarations := region.LookupName(designUnit, place, symbol, self, UnresolvedTypeMarkWarning)) == 0:
			return None

		return declarations[0].DenoteBy(self, region, place, symbol)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this simple name with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSimpleName(self)
		visitor.DepartSimpleName(self)


@export
class ParenthesisName(Name):
	"""
	Represents a name followed by a parenthesized association list.

	Used where indexing and a function call are indistinguishable before resolution.
	"""
	_associations: list  #: List of all associations in the parenthesis.

	def __init__(self, prefix: Name, associations: Iterable, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name followed by a parenthesized association list.

		:param prefix:       Reference to the name's prefix, or ``None`` for a simple name.
		:param associations: List of all associations in the parenthesis.
		:param parent:       Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__("", prefix, parent)

		self._associations = associationList = []
		for association in associations:
			associationList.append(association)
			association.Parent = self

	@readonly
	def Associations(self) -> list:
		"""
		Read-only property to access the associations (:attr:`_associations`).

		:returns: List of associations.
		"""
		return self._associations

	def Copy(self) -> Self:
		"""
		Create a copy of this parenthesis name.

		The copy has no parent. Its prefix and associations are copies of this name's prefix and associations.

		:returns: The new parenthesis name.
		"""
		return self.__class__(self._prefix.Copy(), [association.Copy() for association in self._associations])

	def Denote(
		self,
		region:     DeclarationRegionMixin,
		designUnit: DesignUnit,
		place:      ModelEntity,
		symbol:     Symbol
	) -> Nullable[Denotation]:
		"""
		Determine what this parenthesis name denotes as a part of a type mark, which is an attribute name.

		The type mark is an attribute name like ``m(0)'subtype``. The prefix denotes an object of an array type; this name
		denotes an element: an object of the array's element subtype.

		:param region:                         The declarative region containing the type mark.
		:param designUnit:                     The design unit containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              What this name denotes, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If the prefix isn't an array object, or the array's element type isn't
		                                       resolved, and no :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		from pyVHDLModel.Exception import UnresolvedTypeMarkWarning
		from pyVHDLModel.Type      import ArrayType

		if (denotation := self._prefix.Denote(region, designUnit, place, symbol)) is None:
			return None

		if denotation._kind is DenotationKind.Object and isinstance(arrayType := denotation._entity.BaseType, ArrayType):
			if (elementType := arrayType._elementType._reference) is not None:
				return Denotation(DenotationKind.Object, elementType)

			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Element type of prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't resolved.",
				symbol=symbol,
				place=place,
				namespaces=(region._namespace, )
			))
			return None

		WarningCollector.Raise(UnresolvedTypeMarkWarning(
			f"Prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't an array object.",
			symbol=symbol,
			place=place,
			namespaces=(region._namespace, )
		))
		return None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this parenthesis name, its prefix and its associations with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitParenthesisName(self)
		self._prefix.Visit(visitor)
		visitor.VisitAssociationList(self)
		for position, association in enumerate(self._associations):
			if position > 0:
				visitor.VisitAssociationListSeparator(self)

			association.Visit(visitor)

		visitor.DepartAssociationList(self)
		visitor.DepartParenthesisName(self)

	def __str__(self) -> str:
		"""
		Formats the parenthesis name.

		**Format:** ``func(a, b)``

		:returns: Formatted parenthesis name.
		"""
		return f"{self._prefix!s}({', '.join(str(a) for a in self._associations)})"


@export
class IndexedName(Name):
	"""
	Represents a name indexing an array by one or more values.

	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= v(0);
	      --   ^^^^    <- the indexed name
	"""
	_indices: list[ExpressionUnion]  #: List of all index expressions, one per dimension.

	def __init__(self, prefix: Name, indices: Iterable[ExpressionUnion], parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name indexing an array by one or more values.

		:param prefix:  Reference to the name's prefix, or ``None`` for a simple name.
		:param indices: List of all index expressions, one per dimension.
		:param parent:  Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__("", prefix, parent)

		self._indices = indexList = []
		for index in indices:
			indexList.append(index)
			index.Parent = self

	@readonly
	def Indices(self) -> list[ExpressionUnion]:
		"""
		Read-only property to access the indices (:attr:`_indices`).

		:returns: List of indices.
		"""
		return self._indices

	def Copy(self) -> Self:
		"""
		Create a copy of this indexed name.

		The copy has no parent. Its prefix and indices are copies of this name's prefix and indices.

		:returns: The new indexed name.
		"""
		return self.__class__(self._prefix.Copy(), [index.Copy() for index in self._indices])

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this indexed name, its prefix and its indices with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitIndexedName(self)
		self._prefix.Visit(visitor)
		visitor.VisitIndexList(self)
		for position, index in enumerate(self._indices):
			if position > 0:
				visitor.VisitElementSeparator(self)

			index.Visit(visitor)

		visitor.DepartIndexList(self)
		visitor.DepartIndexedName(self)

	def __str__(self) -> str:
		"""
		Formats the indexed name.

		**Format:** ``arr(0)``

		:returns: Formatted indexed name.
		"""
		return f"{self._prefix!s}({', '.join(str(i) for i in self._indices)})"


@export
class SlicedName(Name):
	"""
	Represents a name selecting a slice of an array.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v(3 downto 0);
	      --      ^^^^^^^^^^^^^    <- the sliced name
	"""
	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this sliced name and its prefix with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSlicedName(self)
		if self._prefix is not None:
			self._prefix.Visit(visitor)

		visitor.DepartSlicedName(self)


@export
class SelectedName(Name):
	"""
	A *selected name* is a name made from multiple words separated by a dot (``.``).

	For example, the library and entity name in a direct entity instantiation is a selected name. Here the entity
	identifier is a selected name. The library identifier is a :class:`simple name <SimpleName>`, which is
	referenced by the selected name via the :attr:`~pyVHDLModel.Name.Prefix` property.

	.. seealso::

	   * :class:`All name <pyVHDLModel.Name.AllName>`
	"""

	def __init__(self, identifier: str, prefix: Name, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a selected name.

		:param identifier: The name's identifier.
		:param prefix:     Reference to the name's prefix, or ``None`` for a simple name.
		:param parent:     Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, prefix, parent)

	@readonly
	def IsExpandedName(self) -> bool:
		"""
		Check if the name is an expanded name ``library.package.item``: its prefix is a selected name of a simple name.

		:returns: ``True``, if the name is an expanded name ``library.package.item``.
		"""
		return isinstance(self._prefix, SelectedName) and isinstance(self._prefix._prefix, SimpleName)

	def Copy(self) -> Self:
		"""
		Create a copy of this selected name.

		The copy has no parent. Its prefix is a copy of this name's prefix.

		:returns: The new selected name.
		"""
		return self.__class__(self._identifier, self._prefix.Copy())

	def Denote(
		self,
		region:     DeclarationRegionMixin,
		designUnit: DesignUnit,
		place:      ModelEntity,
		symbol:     Symbol
	) -> Nullable[Denotation]:
		"""
		Determine what this selected name denotes as a part of a type mark, which is an attribute name.

		The type mark is an attribute name like ``pkg.c'subtype`` or ``rec.f'subtype``. Depending on what the prefix
		denotes, this name denotes:

		* a library: the package of this name in the library.
		* a package: the declaration of this name in the package
		  (:meth:`~pyVHDLModel.Namespace.Namespace.FindDeclarations`); the declaration says what it denotes
		  (:meth:`~pyVHDLModel.Base.ModelEntity.DenoteBy`).
		* an object of a record type: the record element of this name
		  (:attr:`~pyVHDLModel.Type.RecordType.ElementsByIdentifier`), an object of the element's subtype.

		:param region:                         The declarative region containing the type mark.
		:param designUnit:                     The design unit containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              What this name denotes, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If the library has no package of this name, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		:raises UnhandledCriticalWarningError: If the package declares nothing of this name, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		:raises UnhandledCriticalWarningError: If the prefix isn't an object of a record type with an element of this
		                                       name, and no :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		from pyVHDLModel.Exception import UnresolvedTypeMarkWarning
		from pyVHDLModel.Type      import RecordType

		if (denotation := self._prefix.Denote(region, designUnit, place, symbol)) is None:
			return None

		kind =   denotation._kind
		entity = denotation._entity
		if kind is DenotationKind.Library:
			if (package := entity._packages.get(self._normalizedIdentifier)) is not None:
				return Denotation(DenotationKind.Package, package)

			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Prefix '{self!s}' of type mark '{symbol._name!s}' isn't a package of library '{entity._identifier}'.",
				symbol=symbol,
				place=place,
				namespaces=(region._namespace, )
			))
			return None
		elif kind is DenotationKind.Package:
			if len(declarations := entity._namespace.FindDeclarations(self._normalizedIdentifier)) > 0:
				return declarations[0].DenoteBy(self, region, place, symbol)

			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Prefix '{self!s}' of type mark '{symbol._name!s}' not found in: {entity._namespace._name}.",
				symbol=symbol,
				place=place,
				namespaces=(entity._namespace, )
			))
			return None
		elif kind is DenotationKind.Object and isinstance(recordType := entity.BaseType, RecordType):
			if (element := recordType._elementsByIdentifier.get(self._normalizedIdentifier)) is not None:
				return element.DenoteBy(self, region, place, symbol)

		WarningCollector.Raise(UnresolvedTypeMarkWarning(
			f"Prefix '{self._prefix!s}' of type mark '{symbol._name!s}' has no record element '{self._identifier}'.",
			symbol=symbol,
			place=place,
			namespaces=(region._namespace, )
		))
		return None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this selected name and its prefix with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSelectedName(self)
		self._prefix.Visit(visitor)
		visitor.DepartSelectedName(self)

	def __str__(self) -> str:
		"""
		Formats the selected name.

		**Format:** ``rec.elem``

		:returns: Formatted selected name.
		"""
		return f"{self._prefix!s}.{self._identifier}"


@export
class AttributeName(Name):
	"""
	Represents a name selecting an attribute of its prefix.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for i in v'range loop
	      --       ^^^^^^^        <- the attribute name
	"""

	_predefinedAttribute: Nullable[PredefinedAttribute]  #: The predefined attribute, or ``None`` if user-defined.

	def __init__(self, identifier: str, prefix: Name, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name selecting an attribute of its prefix.

		:param identifier: The name's identifier.
		:param prefix:     Reference to the name's prefix, or ``None`` for a simple name.
		:param parent:     Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(identifier, prefix, parent)

		self._predefinedAttribute = PredefinedAttribute._value2member_map_.get(self._normalizedIdentifier)

	@readonly
	def PredefinedAttribute(self) -> Nullable[PredefinedAttribute]:
		"""
		Read-only property to access the predefined attribute this name selects (:attr:`_predefinedAttribute`).

		:returns: The predefined attribute, or ``None`` for a user-defined attribute.
		"""
		return self._predefinedAttribute

	def Copy(self) -> Self:
		"""
		Create a copy of this attribute name.

		The copy has no parent. Its prefix is a copy of this name's prefix.

		:returns: The new attribute name.
		"""
		return self.__class__(self._identifier, self._prefix.Copy())

	def Denote(
		self,
		region:     DeclarationRegionMixin,
		designUnit: DesignUnit,
		place:      ModelEntity,
		symbol:     Symbol
	) -> Nullable[Denotation]:
		"""
		Determine what this attribute name denotes as a type mark or as a part of one (IEEE Std 1076-2008, 16.2).

		Depending on the predefined attribute (:attr:`PredefinedAttribute`), this name denotes:

		* ``'subtype``: the subtype of the object its prefix denotes.
		* ``'element``: the element subtype of the array type or subtype, or of the array object, its prefix denotes.
		* ``'base``: the base type of the type or subtype its prefix denotes; only allowed as the prefix of another
		  attribute.

		The constraint of a subtype indication isn't represented: ``s'subtype`` of ``signal s : bit_vector(3 downto 0)``
		denotes ``bit_vector``.

		:param region:                         The declarative region containing the type mark.
		:param designUnit:                     The design unit containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              What this name denotes, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If the prefix of ``'subtype`` isn't an object, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		:raises UnhandledCriticalWarningError: If the prefix of ``'element`` isn't an array, or the array's element type
		                                       isn't resolved, and no :class:`~pyTooling.Warning.WarningCollector`
		                                       collects the :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		:raises UnhandledCriticalWarningError: If ``'base`` is the type mark itself, or its prefix isn't a type, or its
		                                       base type isn't resolved, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		:raises UnhandledCriticalWarningError: If the attribute denotes no type, and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		from pyVHDLModel.Exception import UnresolvedTypeMarkWarning
		from pyVHDLModel.Type      import ArrayType

		if (denotation := self._prefix.Denote(region, designUnit, place, symbol)) is None:
			return None

		kind =      denotation._kind
		entity =    denotation._entity
		attribute = self._predefinedAttribute
		if attribute is PredefinedAttribute.Subtype:
			if kind is DenotationKind.Object:
				return Denotation(DenotationKind.Type, entity)

			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't an object.",
				symbol=symbol,
				place=place,
				namespaces=(region._namespace, )
			))
		elif attribute is PredefinedAttribute.Element:
			if kind in (DenotationKind.Object, DenotationKind.Type) and isinstance(arrayType := entity.BaseType, ArrayType):
				if (elementType := arrayType._elementType._reference) is not None:
					return Denotation(DenotationKind.Type, elementType)

				WarningCollector.Raise(UnresolvedTypeMarkWarning(
					f"Element type of prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't resolved.",
					symbol=symbol,
					place=place,
					namespaces=(region._namespace, )
				))
			else:
				WarningCollector.Raise(UnresolvedTypeMarkWarning(
					f"Prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't an array.",
					symbol=symbol,
					place=place,
					namespaces=(region._namespace, )
				))
		elif attribute is PredefinedAttribute.Base:
			if self is symbol._name:
				WarningCollector.Raise(UnresolvedTypeMarkWarning(
					f"Attribute name '{self!s}' isn't allowed as type mark: 'base is only a prefix of an attribute.",
					symbol=symbol,
					place=place,
					namespaces=(region._namespace, )
				))
			elif kind is not DenotationKind.Type:
				WarningCollector.Raise(UnresolvedTypeMarkWarning(
					f"Prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't a type.",
					symbol=symbol,
					place=place,
					namespaces=(region._namespace, )
				))
			elif (baseType := entity.BaseType) is None:
				WarningCollector.Raise(UnresolvedTypeMarkWarning(
					f"Base type of prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't resolved.",
					symbol=symbol,
					place=place,
					namespaces=(region._namespace, )
				))
			else:
				return Denotation(DenotationKind.Type, baseType)
		else:
			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Attribute name '{self!s}' doesn't denote a type.",
				symbol=symbol,
				place=place,
				namespaces=(region._namespace, )
			))

		return None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this attribute name and its prefix with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAttributeName(self)
		self._prefix.Visit(visitor)
		visitor.DepartAttributeName(self)

	def __str__(self) -> str:
		"""
		Formats the attribute name.

		**Format:** ``v'range``

		:returns: Formatted attribute name.
		"""
		return f"{self._prefix!s}'{self._identifier}"


@export
class AllName(SelectedName):
	"""
	The *all name* represents the reserved word ``all`` used in names.

	Most likely this name is used in use-statements.
	"""
	def __init__(self, prefix: Name, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an ``all`` name.

		:param prefix: Reference to the name's prefix, or ``None`` for a simple name.
		:param parent: Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__("all", prefix, parent)  # TODO: the case of 'ALL' is not preserved

	@readonly
	def IsExpandedName(self) -> bool:
		"""
		Check if the name is an expanded name ``library.package.item``: a name ending in ``all`` isn't one.

		:returns: ``False``
		"""
		return False

	def Copy(self) -> Self:
		"""
		Create a copy of this ``all`` name.

		The copy has no parent. Its prefix is a copy of this name's prefix.

		:returns: The new ``all`` name.
		"""
		return self.__class__(self._prefix.Copy())

	def Denote(
		self,
		region:     DeclarationRegionMixin,
		designUnit: DesignUnit,
		place:      ModelEntity,
		symbol:     Symbol
	) -> Nullable[Denotation]:
		"""
		Determine what this ``all`` name denotes as a part of a type mark, which is an attribute name.

		The type mark is an attribute name like ``ptr.all'subtype``. The prefix denotes an object of an access type; this
		name denotes the object it designates: an object of the access type's designated subtype.

		:param region:                         The declarative region containing the type mark.
		:param designUnit:                     The design unit containing the type mark.
		:param place:                          The declaration containing the type mark.
		:param symbol:                         The type mark.
		:returns:                              What this name denotes, or ``None`` if it can't be resolved (reported as a
		                                       warning).
		:raises UnhandledCriticalWarningError: If the prefix isn't an object of an access type, or the designated subtype
		                                       isn't resolved, and no :class:`~pyTooling.Warning.WarningCollector` collects
		                                       the :exc:`~pyVHDLModel.Exception.UnresolvedTypeMarkWarning`.
		"""
		from pyVHDLModel.Exception import UnresolvedTypeMarkWarning
		from pyVHDLModel.Type      import AccessType

		if (denotation := self._prefix.Denote(region, designUnit, place, symbol)) is None:
			return None

		if denotation._kind is DenotationKind.Object and isinstance(accessType := denotation._entity.BaseType, AccessType):
			if (designatedSubtype := accessType._designatedSubtype._reference) is not None:
				return Denotation(DenotationKind.Object, designatedSubtype)

			WarningCollector.Raise(UnresolvedTypeMarkWarning(
				f"Designated subtype of prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't resolved.",
				symbol=symbol,
				place=place,
				namespaces=(region._namespace, )
			))
			return None

		WarningCollector.Raise(UnresolvedTypeMarkWarning(
			f"Prefix '{self._prefix!s}' of type mark '{symbol._name!s}' isn't an object of an access type.",
			symbol=symbol,
			place=place,
			namespaces=(region._namespace, )
		))
		return None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this ``all`` name and its prefix (if any) with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitAllName(self)
		if self._prefix is not None:
			self._prefix.Visit(visitor)

		visitor.DepartAllName(self)


@export
class OpenName(Name):
	"""
	The *open name* represents the reserved word ``open``.

	Most likely this name is used in port associations.
	"""
	def __init__(self, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an ``open`` name.

		:param parent: Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__("open", parent=parent)  # TODO: the case of 'OPEN' is not preserved

	def Copy(self) -> Self:
		"""
		Create a copy of this ``open`` name.

		The copy has no parent.

		:returns: The new ``open`` name.
		"""
		return self.__class__()

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this ``open`` name with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitOpenName(self)
		visitor.DepartOpenName(self)

	def __str__(self) -> str:
		"""
		Formats the open name.

		**Format:** ``open``

		:returns: Formatted open name.
		"""
		return "open"
