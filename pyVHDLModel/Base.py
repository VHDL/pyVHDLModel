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
from __future__            import annotations

from enum                  import unique, Enum
from typing                import TYPE_CHECKING, ClassVar, Type, Iterable, Optional as Nullable, Union, cast, Self

from pyTooling.Common      import StringEnum, getFullyQualifiedName
from pyTooling.Decorators  import export, notimplemented, readonly
from pyTooling.MetaClasses import ExtendedType, abstractclass
if TYPE_CHECKING:
	from pyVHDLModel.Interface import SingleDeclarationMixin
	from pyVHDLModel.Symbol    import Symbol
	from pyVHDLModel.Visitor   import Visitor


__all__ = ["ExpressionUnion", "ModelElementUnion"]


ExpressionUnion = Union[
	'BaseExpression',
	'QualifiedExpression',
	'FunctionCall',
	'TypeConversion',
	# ConstantOrSymbol,     TODO: ObjectSymbol
	'Literal',
]

ModelElementUnion = Union['ModelEntity', 'Symbol']
"""
A model element a visitor walks or the VHDL writer writes: a :class:`ModelEntity` or a
:class:`~pyVHDLModel.Symbol.Symbol`.
"""


@export
@unique
class ReservedWord(StringEnum):
	"""
	A ``ReservedWord`` is an enumeration of VHDL's reserved words (IEEE Std 1076-2019, 15.10).

	A member is a :class:`str`: its value is the reserved word in lower case, e.g. ``ReservedWord.DownTo == "downto"``.
	The VHDL writer (:mod:`pyVHDLModel.Formatting.VHDL`) applies the configured keyword case to it.

	Each member states the revision of IEEE Std 1076 that first reserved it. Earlier revisions reserved words, which
	VHDL-2019 doesn't: ``procedural`` and ``reference`` (VHDL-2000 and VHDL-2002), ``assume_guarantee`` and
	``restrict_guarantee`` (VHDL-2008).
	"""

	Abs =           "abs"            #: Reserved word since VHDL-87.
	Access =        "access"         #: Reserved word since VHDL-87.
	After =         "after"          #: Reserved word since VHDL-87.
	Alias =         "alias"          #: Reserved word since VHDL-87.
	All =           "all"            #: Reserved word since VHDL-87.
	And =           "and"            #: Reserved word since VHDL-87.
	Architecture =  "architecture"   #: Reserved word since VHDL-87.
	Array =         "array"          #: Reserved word since VHDL-87.
	Assert =        "assert"         #: Reserved word since VHDL-87.
	Assume =        "assume"         #: Reserved word since VHDL-2008.
	Attribute =     "attribute"      #: Reserved word since VHDL-87.
	Begin =         "begin"          #: Reserved word since VHDL-87.
	Block =         "block"          #: Reserved word since VHDL-87.
	Body =          "body"           #: Reserved word since VHDL-87.
	Buffer =        "buffer"         #: Reserved word since VHDL-87.
	Bus =           "bus"            #: Reserved word since VHDL-87.
	Case =          "case"           #: Reserved word since VHDL-87.
	Component =     "component"      #: Reserved word since VHDL-87.
	Configuration = "configuration"  #: Reserved word since VHDL-87.
	Constant =      "constant"       #: Reserved word since VHDL-87.
	Context =       "context"        #: Reserved word since VHDL-2008.
	Cover =         "cover"          #: Reserved word since VHDL-2008.
	Default =       "default"        #: Reserved word since VHDL-2008.
	Disconnect =    "disconnect"     #: Reserved word since VHDL-87.
	DownTo =        "downto"         #: Reserved word since VHDL-87.
	Else =          "else"           #: Reserved word since VHDL-87.
	ElsIf =         "elsif"          #: Reserved word since VHDL-87.
	End =           "end"            #: Reserved word since VHDL-87.
	Entity =        "entity"         #: Reserved word since VHDL-87.
	Exit =          "exit"           #: Reserved word since VHDL-87.
	Fairness =      "fairness"       #: Reserved word since VHDL-2008.
	File =          "file"           #: Reserved word since VHDL-87.
	For =           "for"            #: Reserved word since VHDL-87.
	Force =         "force"          #: Reserved word since VHDL-2008.
	Function =      "function"       #: Reserved word since VHDL-87.
	Generate =      "generate"       #: Reserved word since VHDL-87.
	Generic =       "generic"        #: Reserved word since VHDL-87.
	Group =         "group"          #: Reserved word since VHDL-93.
	Guarded =       "guarded"        #: Reserved word since VHDL-87.
	If =            "if"             #: Reserved word since VHDL-87.
	Impure =        "impure"         #: Reserved word since VHDL-93.
	In =            "in"             #: Reserved word since VHDL-87.
	Inertial =      "inertial"       #: Reserved word since VHDL-93.
	InOut =         "inout"          #: Reserved word since VHDL-87.
	Is =            "is"             #: Reserved word since VHDL-87.
	Label =         "label"          #: Reserved word since VHDL-87.
	Library =       "library"        #: Reserved word since VHDL-87.
	Linkage =       "linkage"        #: Reserved word since VHDL-87.
	Literal =       "literal"        #: Reserved word since VHDL-93.
	Loop =          "loop"           #: Reserved word since VHDL-87.
	Map =           "map"            #: Reserved word since VHDL-87.
	Mod =           "mod"            #: Reserved word since VHDL-87.
	Nand =          "nand"           #: Reserved word since VHDL-87.
	New =           "new"            #: Reserved word since VHDL-87.
	Next =          "next"           #: Reserved word since VHDL-87.
	Nor =           "nor"            #: Reserved word since VHDL-87.
	Not =           "not"            #: Reserved word since VHDL-87.
	Null =          "null"           #: Reserved word since VHDL-87.
	Of =            "of"             #: Reserved word since VHDL-87.
	On =            "on"             #: Reserved word since VHDL-87.
	Open =          "open"           #: Reserved word since VHDL-87.
	Or =            "or"             #: Reserved word since VHDL-87.
	Others =        "others"         #: Reserved word since VHDL-87.
	Out =           "out"            #: Reserved word since VHDL-87.
	Package =       "package"        #: Reserved word since VHDL-87.
	Parameter =     "parameter"      #: Reserved word since VHDL-2008.
	Port =          "port"           #: Reserved word since VHDL-87.
	Postponed =     "postponed"      #: Reserved word since VHDL-93.
	Private =       "private"        #: Reserved word since VHDL-2019.
	Procedure =     "procedure"      #: Reserved word since VHDL-87.
	Process =       "process"        #: Reserved word since VHDL-87.
	Property =      "property"       #: Reserved word since VHDL-2008.
	Protected =     "protected"      #: Reserved word since VHDL-2000.
	Pure =          "pure"           #: Reserved word since VHDL-93.
	Range =         "range"          #: Reserved word since VHDL-87.
	Record =        "record"         #: Reserved word since VHDL-87.
	Register =      "register"       #: Reserved word since VHDL-87.
	Reject =        "reject"         #: Reserved word since VHDL-93.
	Release =       "release"        #: Reserved word since VHDL-2008.
	Rem =           "rem"            #: Reserved word since VHDL-87.
	Report =        "report"         #: Reserved word since VHDL-87.
	Restrict =      "restrict"       #: Reserved word since VHDL-2008.
	Return =        "return"         #: Reserved word since VHDL-87.
	Rol =           "rol"            #: Reserved word since VHDL-93.
	Ror =           "ror"            #: Reserved word since VHDL-93.
	Select =        "select"         #: Reserved word since VHDL-87.
	Sequence =      "sequence"       #: Reserved word since VHDL-2008.
	Severity =      "severity"       #: Reserved word since VHDL-87.
	Shared =        "shared"         #: Reserved word since VHDL-93.
	Signal =        "signal"         #: Reserved word since VHDL-87.
	Sla =           "sla"            #: Reserved word since VHDL-93.
	Sll =           "sll"            #: Reserved word since VHDL-93.
	Sra =           "sra"            #: Reserved word since VHDL-93.
	Srl =           "srl"            #: Reserved word since VHDL-93.
	Strong =        "strong"         #: Reserved word since VHDL-2008.
	Subtype =       "subtype"        #: Reserved word since VHDL-87.
	Then =          "then"           #: Reserved word since VHDL-87.
	To =            "to"             #: Reserved word since VHDL-87.
	Transport =     "transport"      #: Reserved word since VHDL-87.
	Type =          "type"           #: Reserved word since VHDL-87.
	Unaffected =    "unaffected"     #: Reserved word since VHDL-93.
	Units =         "units"          #: Reserved word since VHDL-87.
	Until =         "until"          #: Reserved word since VHDL-87.
	Use =           "use"            #: Reserved word since VHDL-87.
	Variable =      "variable"       #: Reserved word since VHDL-87.
	View =          "view"           #: Reserved word since VHDL-2019.
	VMode =         "vmode"          #: Reserved word since VHDL-2008.
	VPkg =          "vpkg"           #: Reserved word since VHDL-2019.
	VProp =         "vprop"          #: Reserved word since VHDL-2008.
	VUnit =         "vunit"          #: Reserved word since VHDL-2008.
	Wait =          "wait"           #: Reserved word since VHDL-87.
	When =          "when"           #: Reserved word since VHDL-87.
	While =         "while"          #: Reserved word since VHDL-87.
	With =          "with"           #: Reserved word since VHDL-87.
	Xnor =          "xnor"           #: Reserved word since VHDL-93.
	Xor =           "xor"            #: Reserved word since VHDL-87.


_ReservedWord = ReservedWord  #: Alias of :class:`ReservedWord` for annotations in classes with a property of that name.


@export
@unique
class Direction(Enum):
	"""An enumeration representing a direction in a range	(``to`` or ``downto``)."""

	To =      0  #: Ascending direction
	DownTo =  1  #: Descending direction

	__RESERVED_WORDS: ClassVar[dict[int, _ReservedWord]] = {
		0: _ReservedWord.To,
		1: _ReservedWord.DownTo
	}  #: The reserved word of each direction, by value.

	@readonly
	def ReservedWord(self) -> _ReservedWord:
		"""
		Read-only property to return the reserved word of the direction.

		:returns: The reserved word, ``to`` or ``downto``.
		"""
		return self.__RESERVED_WORDS[self.value]

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

	__RESERVED_WORDS: ClassVar[dict[int, _ReservedWord]] = {
		1: _ReservedWord.In,
		2: _ReservedWord.Out,
		3: _ReservedWord.InOut,
		4: _ReservedWord.Buffer,
		5: _ReservedWord.Linkage
	}  #: The reserved word of each mode, by value; ``Default`` has none.

	@readonly
	def ReservedWord(self) -> Nullable[_ReservedWord]:
		"""
		Read-only property to return the reserved word of the mode.

		:returns: The reserved word, or ``None`` for ``Mode.Default``.
		"""
		return self.__RESERVED_WORDS.get(self.value, None)

	def __str__(self) -> str:
		"""
		Formats the mode.

		:returns: Formatted mode.
		"""
		return ("", "in", "out", "inout", "buffer", "linkage")[cast(int, self.value)]       # TODO: check performance


@export
@abstractclass
class ModelEntity(metaclass=ExtendedType, slots=True):
	"""
	``ModelEntity`` is the base-class for all classes in the VHDL language model, except for mixin classes (see multiple
	inheritance) and enumerations.

	Each entity in this model has a reference to its parent entity. Therefore, a protected variable :attr:`_parent` is
	available and a readonly property :attr:`Parent`.
	"""

	_parent: ModelEntity      #: Reference to a parent entity in the logical model hierarchy.

	def __init__(self, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a VHDL model entity.

		:param parent: Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		self._parent = parent

	@property
	def Parent(self) -> ModelEntity:
		"""
		Property to access the model entity's parent element reference in a logical hierarchy (:attr:`_parent`).

		:returns: Reference to the parent entity.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		if parent is None:
			raise ValueError("Parameter 'parent' is None.")

		self._parent = parent

	def GetAncestor(self, type: Type) -> ModelEntity:
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

	@notimplemented("Model element has no walk for a visitor.")
	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this model element with a visitor.

		A model class implements its walk; a class without one raises.

		:param visitor:              The visitor receiving the events.
		:raises NotImplementedError: Always, because the element's class has no walk of its own.
		"""


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
class MultipleNamedEntityMixin(
	metaclass=ExtendedType,
	mixin=True,
	expects=("_parent", "Copy", "_SplitInParent")
):
	"""
	A ``MultipleNamedEntityMixin`` is a mixin class for all VHDL entities that declare multiple instances at once by
	defining multiple identifiers.

	Protected variables :attr:`_identifiers` and :attr:`_normalizedIdentifiers` are available to derived classes as well
	as two readonly properties :attr:`Identifiers` and :attr:`NormalizedIdentifiers` for public access.

	The host class provides ``Copy()`` and ``_SplitInParent()``, called by :meth:`Split`: the latter calls the parent's
	mutator splitting the declaration, e.g.
	:meth:`DeclarationRegionMixin.SplitDeclaredItem <pyVHDLModel.Regions.DeclarationRegionMixin.SplitDeclaredItem>`.

	.. seealso::

	   * :class:`Mode view element <pyVHDLModel.Interface.ModeViewElement>`
	   * :class:`Obj <pyVHDLModel.Object.Obj>`
	   * :class:`Record type element <pyVHDLModel.Type.RecordTypeElement>`
	"""

	_identifiers:           tuple[str]                              #: A list of identifiers.
	_normalizedIdentifiers: tuple[str]                              #: A list of normalized (lower case) identifiers.
	_singleDeclarations:    Nullable[list[SingleDeclarationMixin]]  #: Cached single declarations, or ``None``.

	def __init__(self, identifiers: Iterable[str]) -> None:
		"""
		Initializes a multiple-named entity without single declarations yet.

		:param identifiers: Sequence of identifiers (names) of the model entity.
		"""
		self._identifiers =           tuple(identifiers)
		self._normalizedIdentifiers = tuple([identifier.lower() for identifier in self._identifiers])
		self._singleDeclarations =    None

	@readonly
	def Identifiers(self) -> tuple[str]:
		"""
		Read-only property to access the model entity's identifiers (:attr:`_identifiers`).

		:returns: Tuple of identifiers.
		"""
		return self._identifiers

	@readonly
	def NormalizedIdentifiers(self) -> tuple[str]:
		"""
		Read-only property to access the model entity's normalized identifiers (:attr:`_normalizedIdentifiers`).

		:returns: Tuple of normalized identifiers.
		"""
		return self._normalizedIdentifiers

	def Split(self) -> tuple[Self, ...]:
		"""
		Split this declaration into one declaration per identifier.

		IEEE Std 1076 defines a declaration with an identifier list as equivalent to a sequence of single declarations,
		one per identifier, in list order: ``signal a, b : bit;`` declares the same as ``signal a : bit; signal b : bit;``.
		This declaration keeps its first identifier. For every other identifier, a new declaration is created by
		``Copy()``: it has its own copy of the subtype indication and of the default expression, and the same
		documentation. Single declarations created before are dropped.

		Without a parent, the new declarations have no parent either: the caller places them. With a parent, the parent's
		mutator splits the declaration and inserts the new declarations right after it, e.g.
		:meth:`WithPortsMixin.SplitPortItem <pyVHDLModel.Regions.WithPortsMixin.SplitPortItem>` for a port.

		A declaration with one identifier is unchanged.

		:returns:                    Tuple of declarations, one per identifier in list order, starting with this
		                             declaration.
		:raises NotAChildError:      If this declaration's parent doesn't list it.
		:raises NotInNamespaceError: If the parent is an indexed declarative region, and an identifier of this declaration
		                             refers to another element, e.g. a duplicate declaration.
		"""
		if self._parent is not None:
			return self._SplitInParent()
		elif len(self._identifiers) == 1:
			return (self, )

		declarations = self._SplitCopies()
		self._KeepIdentifier(0)
		return (self, *declarations)

	def _SplitCopies(self) -> list[Self]:
		"""
		Create one parentless copy of this declaration per identifier after the first, each keeping its identifier.

		:returns: List of new declarations, in list order.
		"""
		declarations = []
		for position in range(1, len(self._identifiers)):
			declaration = self.Copy()
			declaration._KeepIdentifier(position)
			declarations.append(declaration)

		return declarations

	def _KeepIdentifier(self, position: int) -> None:
		"""
		Reduce the identifier list to the identifier at a position and drop the single declarations.

		:param position: The position of the identifier to keep.
		"""
		self._identifiers =           (self._identifiers[position], )
		self._normalizedIdentifiers = (self._normalizedIdentifiers[position], )
		self._singleDeclarations =    None


@export
def identifiersOf(item) -> tuple[str, ...]:
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
def normalizedIdentifiersOf(item) -> tuple[str, ...]:
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
def normalizedDeclaredNamesOf(item: ModelEntity) -> tuple[str, ...]:
	"""
	Return the normalized (lower case) names an item declares in its declarative region.

	A declaration declares its identifiers. A statement label is declared implicitly in the declarative region enclosing
	the statement, so a labeled statement declares its label.

	:param item: A model entity.
	:returns:    The normalized identifiers of a singularly or plurally named entity, the normalized label of a labeled
	             entity, or an empty tuple.

	.. seealso::

	   :func:`normalizedIdentifiersOf`
	     The normalized identifiers of a singularly or plurally named entity.
	"""
	if isinstance(item, (NamedEntityMixin, MultipleNamedEntityMixin)):
		return normalizedIdentifiersOf(item)
	elif isinstance(item, LabeledEntityMixin) and item._normalizedLabel is not None:
		return (item._normalizedLabel, )

	return ()


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

		:param condition: Optional, the expression representing the condition. Default: ``None``, no condition.
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

		:param message:  Optional, the reported message. Default: ``None``, no message.
		:param severity: Optional, the reported severity level. Default: ``None``, no severity level.
		"""
		self._message = message
		if message is not None:
			message.Parent = self

		self._severity = severity
		if severity is not None:
			severity.Parent = self

	def _VisitReportAndSeverity(self, visitor: Visitor) -> None:
		"""
		Walk the message and the severity, if given, each after its reserved word, with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		if self._message is not None:
			visitor.VisitReport(self)
			self._message.Visit(visitor)

		if self._severity is not None:
			visitor.VisitSeverity(self)
			self._severity.Visit(visitor)

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
		:param message:   Optional, the reported message. Default: ``None``, no message.
		:param severity:  Optional, the reported severity level. Default: ``None``, no severity level.
		"""
		super().__init__(message, severity)
		ConditionalMixin.__init__(self, condition)

	def _VisitAssertion(self, visitor: Visitor) -> None:
		"""
		Walk the condition, the message and the severity of an assertion with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		self._condition.Visit(visitor)
		self._VisitReportAndSeverity(visitor)


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
@abstractclass
class BaseChoice(ModelEntity):
	"""
	A ``Choice`` is a base-class for all choices.

	.. seealso::

	   * :class:`Concurrent choice <pyVHDLModel.Concurrent.ConcurrentChoice>`
	   * :class:`Sequential choice <pyVHDLModel.Sequential.SequentialChoice>`
	"""


@export
@abstractclass
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

	_choices: list[BaseChoice]  #: List of all choices selecting this alternative.

	def __init__(self, choices: Nullable[Iterable[BaseChoice]] = None) -> None:
		"""
		Initializes choices.

		:param choices: Optional, list of all choices selecting this alternative. Default: ``None``, no choices.
		"""
		self._choices = choiceList = []
		if choices is not None:
			for choice in choices:
				choiceList.append(choice)
				choice.Parent = self

	@readonly
	def Choices(self) -> list[BaseChoice]:
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
	A range with both bounds given as expressions.

	``0 to 7`` is such a range.
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
		:param parent:     Optional, the parent model entity. Default: ``None``, no parent.
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

	def Copy(self) -> Self:
		"""
		Create a copy of this simple range.

		The copy has no parent. Its bounds are copies of this range's bounds.

		:returns: The new simple range.
		"""
		return self.__class__(self._leftBound.Copy(), self._rightBound.Copy(), self._direction)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this range, its left bound and its right bound with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSimpleRange(self)
		self._leftBound.Visit(visitor)
		visitor.VisitDirection(self)
		self._rightBound.Visit(visitor)
		visitor.DepartSimpleRange(self)

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

	_symbol: Symbol  #: Reference to the name the range's bounds are inferred from.

	def __init__(self, symbol: Symbol, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initialize a range denoted by a name.

		:param symbol: The symbol referencing the range attribute or discrete subtype.
		:param parent: Optional, the parent model entity. Default: ``None``, no parent.
		"""
		super().__init__(parent)

		self._symbol = symbol
		symbol.Parent = self

	@readonly
	def Symbol(self) -> Symbol:
		"""
		Read-only property to access the referenced symbol (:attr:`_symbol`).

		:returns: The symbol.
		"""
		return self._symbol

	def Copy(self) -> Self:
		"""
		Create a copy of this range denoted by a name.

		The copy has no parent. Its symbol is a copy of this range's symbol.

		:returns: The new range denoted by a name.
		"""
		return self.__class__(self._symbol.Copy())

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this range and its name with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitRangeFromName(self)
		self._symbol.Visit(visitor)
		visitor.DepartRangeFromName(self)

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
		:param after:      Optional, the delay after which the value is assigned. Default: ``None``, no delay.
		:param parent:     Optional, the parent model entity of this entity. Default: ``None``, no parent.
		"""
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

		self._after = after
		if after is not None:
			after.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this waveform element, its value and its delay (if any) with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitWaveformElement(self)
		self._expression.Visit(visitor)
		if self._after is not None:
			visitor.VisitAfter(self)
			self._after.Visit(visitor)

		visitor.DepartWaveformElement(self)

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
