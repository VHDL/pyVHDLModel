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
# Copyright 2017-2022 Patrick Lehmann - Boetzingen, Germany                                                            #
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
An abstract VHDL language model.

:copyright: Copyright 2007-2022 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2016-2022, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.21.0"


from enum            import unique, Enum, Flag, auto

from typing          import List, Iterable, Union, Optional as Nullable, Dict, cast, Tuple, Any, Type

from pyTooling.Decorators import export
from pyTooling.Graph import Vertex

SubtypeOrSymbol = Union['Subtype',       'SubtypeSymbol']


ConstraintUnion = Union[
	'RangeExpression',
	'RangeAttribute',
	'RangeSubtype',
]

ExpressionUnion = Union[
	'BaseExpression',
	'QualifiedExpression',
	'FunctionCall',
	'TypeConversion',
	# ConstantOrSymbol,     TODO: ObjectSymbol
	'Literal',
]

ContextUnion = Union[
	'LibraryClause',
	'UseClause',
	'ContextReference'
]


@export
@unique
class VHDLVersion(Enum):
	"""
	An enumeration for all possible version numbers for VHDL and VHDL-AMS.

	A version can be given as integer or string and is represented as a unified
	enumeration value.

	This enumeration supports compare operators.
	"""

	Any =                -1  #: Any
	VHDL87 =             87  #: VHDL-1987
	VHDL93 =             93  #: VHDL-1993
#	AMS93 =              93  #:
	AMS99 =              99  #: VHDL-AMS-1999
	VHDL2000 =         2000  #: VHDL-2000
	VHDL2002 =         2002  #: VHDL-2002
	VHDL2008 =         2008  #: VHDL-2008
	AMS2017 =          2017  #: VHDL-AMS-2017
	VHDL2019 =         2019  #: VHDL-2019
	Latest =          10000  #: Latest VHDL (2019)

	__VERSION_MAPPINGS__: Dict[Union[int, str], Enum] = {
		87:     VHDL87,
		93:     VHDL93,
		99:     AMS99,
		0:      VHDL2000,
		2:      VHDL2002,
		8:      VHDL2008,
		17:     AMS2017,
		19:     VHDL2019,
		1987:   VHDL87,
		1993:   VHDL93,
		1999:   AMS99,
		2000:   VHDL2000,
		2002:   VHDL2002,
		2008:   VHDL2008,
		2017:   AMS2017,
		2019:   VHDL2019,
		"Any":  Any,
		"Latest": Latest,
		"87":   VHDL87,
		"93":   VHDL93,
		"99":   AMS99,
		"00":   VHDL2000,
		"02":   VHDL2002,
		"08":   VHDL2008,
		"17":   AMS2017,
		"19":   VHDL2019,
		"1987": VHDL87,
		"1993": VHDL93,
		"1999": AMS99,
		"2000": VHDL2000,
		"2002": VHDL2002,
		"2008": VHDL2008,
		"2017": AMS2017,
		"2019": VHDL2019
	}  #: Dictionary of VHDL and VHDL-AMS year codes variants as integer and strings for mapping to unique enum values.

	def __init__(self, *_) -> None:
		"""Patch the embedded MAP dictionary"""
		for k, v in self.__class__.__VERSION_MAPPINGS__.items():
			if ((not isinstance(v, self.__class__)) and (v == self.value)):
				self.__class__.__VERSION_MAPPINGS__[k] = self

	@classmethod
	def Parse(cls, value: Union[int, str]) -> 'Enum':
		"""
		Parses a VHDL or VHDL-AMS year code as integer or string to an enum value.

		:param value:       VHDL/VHDL-AMS year code.
		:returns:           Enumeration value.
		:raises ValueError: If the year code is not recognized.
		"""
		try:
			return cls.__VERSION_MAPPINGS__[value]
		except KeyError:
			ValueError(f"Value '{value!s}' cannot be parsed to member of {cls.__name__}.")

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is less than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is less than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value < other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __le__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is less or equal than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is less or equal than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value <= other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is greater than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is greater than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value > other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is greater or equal than the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is greater or equal than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value >= other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is unequal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is unequal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			return self.value != other.value
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two VHDL/VHDL-AMS versions if the version is equal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          True if version is equal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`VHDLVersion`.
		"""
		if isinstance(other, VHDLVersion):
			if ((self is self.__class__.Any) or (other is self.__class__.Any)):
				return True
			else:
				return (self.value == other.value)
		else:
			raise TypeError("Second operand is not of type 'VHDLVersion'.")

	@property
	def IsVHDL(self) -> bool:
		"""
		Checks if the version is a VHDL (not VHDL-AMS) version.

		:returns:          True if version is a VHDL version.
		"""
		return self in (self.VHDL87, self.VHDL93, self.VHDL2002, self.VHDL2008, self.VHDL2019)

	@property
	def IsAMS(self) -> bool:
		"""
		Checks if the version is a VHDL-AMS (not VHDL) version.

		:returns:          True if version is a VHDL-AMS version.
		"""
		return self in (self.AMS99, self.AMS2017)

	def __str__(self) -> str:
		"""
		Formats the VHDL version to pattern ``VHDL'xx`` or in case of VHDL-AMS to ``VHDL-AMS'xx``.

		:return: Formatted VHDL/VHDL-AMS version.
		"""
		year = str(self.value)[-2:]
		if self.IsVHDL:
			return f"VHDL'{year}"
		else:
			return f"VHDL-AMS'{year}"

	def __repr__(self) -> str:
		"""
		Formats the VHDL/VHDL-AMS version to pattern ``xxxx``.

		:return: Formatted VHDL/VHDL-AMS version.
		"""
		return str(self.value)


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
@unique
class ObjectClass(Enum):
	"""
	An ``ObjectClass`` is an enumeration. It represents an object's class (``constant``, ``signal``, ...).

	In case no *object class* is defined, ``Default`` is used, so the *object class* is inferred from context.
	"""

	Default =    0  #: Object class not defined, thus it's context dependent.
	Constant =   1  #: Constant
	Variable =   2  #: Variable
	Signal =     3  #: Signal
	File =       4  #: File
	Type =       5  #: Type
	# FIXME: Package?
	Procedure =  6  #: Procedure
	Function =   7  #: Function

	def __str__(self):
		"""
		Formats the object class.

		:return: Formatted object class.
		"""
		return ("", "constant", "variable", "signal", "file", "type", "procedure", "function")[cast(int, self.value)]       # TODO: check performance


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


@export
class PossibleReference(Flag):
	"""
	A ``PossibleReference`` is an enumeration. It represents possible targets for a reference in a :class:`~pyVHDLModel.Symbol`.
	"""

	Unknown =         0
	Library =         auto()  #: Library
	Entity =          auto()  #: Entity
	Architecture =    auto()  #: Architecture
	Component =       auto()  #: Component
	Package =         auto()  #: Package
	Configuration =   auto()  #: Configuration
	Context =         auto()  #: Context
	Type =            auto()  #: Type
	Subtype =         auto()  #: Subtype
	ScalarType =      auto()  #: ScalarType
	ArrayType =       auto()  #: ArrayType
	RecordType =      auto()  #: RecordType
	AccessType =      auto()  #: AccessType
	ProtectedType =   auto()  #: ProtectedType
	FileType =        auto()  #: FileType
#	Alias =           auto()   # TODO: Is this needed?
	Attribute =       auto()  #: Attribute
	TypeAttribute =   auto()  #: TypeAttribute
	ValueAttribute =  auto()  #: ValueAttribute
	SignalAttribute = auto()  #: SignalAttribute
	RangeAttribute =  auto()  #: RangeAttribute
	ViewAttribute =   auto()  #: ViewAttribute
	Constant =        auto()  #: Constant
	Variable =        auto()  #: Variable
	Signal =          auto()  #: Signal
	File =            auto()  #: File
#	Object =          auto()   # TODO: Is this needed?
	EnumLiteral =     auto()  #: EnumLiteral
	Procedure =       auto()  #: Procedure
	Function =        auto()  #: Function
	Label =           auto()  #: Label
	View =            auto()  #: View

	AnyType = ScalarType | ArrayType | RecordType | ProtectedType | AccessType | FileType | Subtype  #: Any possible type incl. subtypes.
	Object = Constant | Variable | Signal | File                                                     #: Any object
	SubProgram = Procedure | Function                                                                #: Any subprogram
	PackageMember = AnyType | Object | SubProgram | Component                                        #: Any member of a package
	SimpleNameInExpression = Constant | Variable | Signal | ScalarType | EnumLiteral | Function      #: Any possible item in an expression.


@export
class ModelEntity:
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
class Name(ModelEntity):
	"""``Name`` is the base-class for all *names* in the VHDL language model."""

	_identifier: str
	_normalizedIdentifier: str
	_root: Nullable['Name']     # TODO: seams to be unused. There is no reverse linking
	_prefix: Nullable['Name']

	def __init__(self, identifier: str, prefix: 'Name' = None):
		super().__init__()

		self._identifier = identifier
		self._normalizedIdentifier = identifier.lower()

		if prefix is None:
			self._prefix = self
			self._root = None
		else:
			self._prefix = prefix
			self._root = prefix._root

	@property
	def Identifier(self) -> str:
		return self._identifier

	@property
	def NormalizedIdentifier(self) -> str:
		return self._normalizedIdentifier

	@property
	def Root(self) -> 'Name':
		return self._root

	@property
	def Prefix(self) -> Nullable['Name']:
		return self._prefix

	@property
	def Has_Prefix(self) -> bool:
		return self._prefix is not None


@export
class Symbol(ModelEntity):
	_symbolName: Name
	_possibleReferences: PossibleReference
	_reference: Any

	def __init__(self, symbolName: Name, possibleReferences: PossibleReference):
		super().__init__()

		self._symbolName = symbolName
		self._possibleReferences = possibleReferences
		self._reference = None

	@property
	def SymbolName(self) -> Name:
		return self._symbolName


@export
class NewSymbol:
	_possibleReferences: PossibleReference
	_reference: Any

	def __init__(self, possibleReferences: PossibleReference):
		self._possibleReferences = possibleReferences
		self._reference = None

	@property
	def Reference(self) -> Any:
		return self._reference

	@property
	def IsResolved(self) -> bool:
		return self._reference is not None

	def __bool__(self) -> bool:
		return self._reference is not None

	def __str__(self) -> str:
		if self._reference is not None:
			return str(self._reference)
		return str(self._symbolName)


@export
class Reference(ModelEntity):
	_symbols:       List[Symbol]

	def __init__(self, symbols: Iterable[Symbol]):
		super().__init__()

		self._symbols = [s for s in symbols]

	@property
	def Symbols(self) -> List[Symbol]:
		return self._symbols


@export
class LibraryClause(Reference):
	pass


@export
class UseClause(Reference):
	pass


# TODO: rename to ContextClause?
@export
class ContextReference(Reference):
	pass


@export
class DesignUnitWithContextMixin: #(metaclass=ExtendedType, useSlots=True):
	pass


@export
@unique
class DesignUnitKind(Flag):
	Context = auto()
	Package = auto()
	PackageBody = auto()
	Entity = auto()
	Architecture = auto()
	Configuration = auto()

	Primary = Context | Configuration | Entity | Package
	Secondary = Architecture | PackageBody
	WithContext = Configuration | Entity | Package | Architecture | PackageBody

	All = Primary | Secondary


@export
@unique
class DependencyGraphVertexKind(Flag):
	Library = auto()
	Context = auto()
	Package = auto()
	PackageBody = auto()
	Entity = auto()
	Architecture = auto()
	Configuration = auto()


@export
@unique
class DependencyGraphEdgeKind(Flag):
	Library = auto()
	Context = auto()
	Package = auto()
	Entity = auto()
	# Architecture = auto()
	Configuration = auto()
	Component = auto()

	Reference = auto()
	Implementation = auto()
	Instantiation = auto()

	LibraryClause =    Library | Reference
	UseClause =        Package | Reference
	ContextReference = Context | Reference

	EntityImplementation =       Entity | Implementation
	PackageImplementation =      Package | Implementation

	EntityInstantiation =        Entity | Instantiation
	ComponentInstantiation =     Component | Instantiation
	ConfigurationInstantiation = Configuration | Instantiation


@export
class DesignUnit(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""A ``DesignUnit`` is a base-class for all design units."""

	_library:             'Library'                        #: The VHDL library, the design unit was analyzed into.

	# Either written as statements before (e.g. entity, architecture, package, ...), or as statements inside (context)
	_contextItems:        List['ContextUnion']             #: List of all context items (library, use and context clauses).
	_libraryReferences:   List['LibraryClause']            #: List of library clauses.
	_packageReferences:   List['UseClause']                #: List of use clauses.
	_contextReferences:   List['ContextReference']         #: List of context clauses.

	_referencedLibraries: Dict[str, 'Library']             #: Referenced libraries based on explicit library clauses or implicit inheritance
	_referencedPackages:  Dict[str, Dict[str, 'Package']]  #: Referenced packages based on explicit use clauses or implicit inheritance
	_referencedContexts:  Dict[str, 'Context']             #: Referenced contexts based on explicit context references or implicit inheritance

	_dependencyVertex:    Vertex[str, 'DesignUnit', None, None]  #: The vertex in the dependency graph
	_hierarchyVertex:     Vertex[str, 'DesignUnit', None, None]  #: The vertex in the hierarchy graph

	def __init__(self, identifier: str, contextItems: Iterable['ContextUnion'] = None, documentation: str = None):
		"""
		Initializes a design unit.

		:param identifier:    Identifier (name) of the design unit.
		:param contextItems:  A sequence of library, use or context clauses.
		:param documentation: Associated documentation of the design unit.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._library = None

		self._contextItems = []
		self._libraryReferences = []
		self._packageReferences = []
		self._contextReferences = []

		if contextItems is not None:
			for item in contextItems:
				self._contextItems.append(item)
				if isinstance(item, UseClause):
					self._packageReferences.append(item)
				elif isinstance(item, LibraryClause):
					self._libraryReferences.append(item)
				elif isinstance(item, ContextReference):
					self._contextReferences.append(item)

		self._referencedLibraries = {}
		self._referencedPackages = {}
		self._referencedContexts = {}

		self._dependencyVertex = None
		self._hierarchyVertex = None

	@property
	def Document(self) -> 'Document':
		return self._parent

	@Document.setter
	def Document(self, document: 'Document') -> None:
		self._parent = document

	@property
	def Library(self) -> 'Library':
		return self._library

	@Library.setter
	def Library(self, library: 'Library') -> None:
		self._library = library

	@property
	def ContextItems(self) -> List['ContextUnion']:
		"""
		Read-only property to access the sequence of all context items comprising library, use and context clauses
		(:py:attr:`_contextItems`).

		:returns: Sequence of context items.
		"""
		return self._contextItems

	@property
	def ContextReferences(self) -> List['ContextReference']:
		"""
		Read-only property to access the sequence of context clauses (:py:attr:`_contextReferences`).

		:returns: Sequence of context clauses.
		"""
		return self._contextReferences

	@property
	def LibraryReferences(self) -> List['LibraryClause']:
		"""
		Read-only property to access the sequence of library clauses (:py:attr:`_libraryReferences`).

		:returns: Sequence of library clauses.
		"""
		return self._libraryReferences

	@property
	def PackageReferences(self) -> List['UseClause']:
		"""
		Read-only property to access the sequence of use clauses (:py:attr:`_packageReferences`).

		:returns: Sequence of use clauses.
		"""
		return self._packageReferences

	@property
	def ReferencedLibraries(self) -> Dict[str, 'Library']:
		return self._referencedLibraries

	@property
	def ReferencedPackages(self) -> Dict[str, 'Package']:
		return self._referencedPackages

	@property
	def ReferencedContexts(self) -> Dict[str, 'Context']:
		return self._referencedContexts

	@property
	def DependencyVertex(self) -> Vertex:
		return self._dependencyVertex

	@property
	def HierarchyVertex(self) -> Vertex:
		return self._hierarchyVertex


@export
class PrimaryUnit(DesignUnit):
	"""A ``PrimaryUnit`` is a base-class for all primary units."""


@export
class SecondaryUnit(DesignUnit):
	"""A ``SecondaryUnit`` is a base-class for all secondary units."""
