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
__version__ =   "0.18.0"


from enum     import IntEnum, unique, Enum
from typing   import List, Iterable, Union, Optional as Nullable, Dict, cast, Tuple, Any

from pyTooling.Decorators import export


SimpleOrAttribute =     Union['SimpleName',    'AttributeName']

LibraryOrSymbol =       Union['Library',       'LibrarySymbol']
EntityOrSymbol =        Union['Entity',        'EntitySymbol']
ArchitectureOrSymbol =  Union['Architecture',  'ArchitectureSymbol']
PackageOrSymbol =       Union['Package',       'PackageSymbol']
ConfigurationOrSymbol = Union['Configuration', 'ConfigurationSymbol']
ContextOrSymbol =       Union['Context',       'ContextSymbol']

SubtypeOrSymbol =       Union['Subtype',       'SubtypeSymbol']

ConstantOrSymbol =      Union['Constant',      'ConstantSymbol']
VariableOrSymbol =      Union['Variable',      'VariableSymbol']
SignalOrSymbol =        Union['Signal',        'SignalSymbol']

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
	ConstantOrSymbol,
	VariableOrSymbol,
	SignalOrSymbol,
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

	Entity =        0
	Architecture =  1
	Configuration = 2
	Procedure =     3
	Function =      4
	Package =       5
	Type =          6
	Subtype =       7
	Constant =      8
	Signal =        9
	Variable =      10
	Component =     11
	Label =         12
	Literal =       13
	Units =         14
	Group =         15
	File =          16
	Property =      17
	Sequence =      18
	View =          19
	Others  =       20


@export
class PossibleReference(IntEnum):
	Unknown =         0
	Library =         2**0
	Entity =          2**1
	Architecture =    2**2
	Component =       2**3
	Package =         2**4
	Configuration =   2**5
	Context =         2**6
	Type =            2**7
	Subtype =         2**8
	ScalarType =      2**9
	ArrayType =       2**10
	RecordType =      2**11
	AccessType =      2**12
	ProtectedType =   2**13
	FileType =        2**14
#	Alias =           2**14   # TODO: Is this needed?
	Attribute =       2**15
	TypeAttribute =   2**16
	ValueAttribute =  2**17
	SignalAttribute = 2**18
	RangeAttribute =  2**19
	ViewAttribute =   2**20
	Constant =        2**16
	Variable =        2**17
	Signal =          2**18
	File =            2**19
	Object =          2**20   # TODO: Is this needed?
	EnumLiteral =     2**21
	Procedure =       2**22
	Function =        2**23
	Label =           2**24
	View =            2**25
	SimpleNameInExpression = Constant + Variable + Signal + ScalarType + EnumLiteral + Function


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

	@property
	def Parent(self) -> 'ModelEntity':
		"""
		Returns a reference to the parent entity.

		:returns: Parent entity.
		"""
		return self._parent


@export
class NamedEntityMixin:
	"""
	A ``NamedEntityMixin`` is a mixin class for all VHDL entities that have identifiers.

	A protected variable :attr:`_identifier` is available to derived classes as well as a readonly property
	:attr:`Identifier` for public access.
	"""

	_identifier: str  #: The identifier of a model entity.

	def __init__(self, identifier: str):
		"""
		Initializes a named entity.

		:param identifier: Identifier (name) of the model entity.
		"""
		self._identifier = identifier

	@property
	def Identifier(self) -> str:
		"""
		Returns a model entity's identifier (name).

		:returns: Name of a model entity.
		"""
		return self._identifier


@export
class MultipleNamedEntityMixin:
	"""
	A ``MultipleNamedEntityMixin`` is a mixin class for all VHDL entities that declare multiple instances at once by
	giving multiple identifiers.

	A protected variable :attr:`_identifiers` is available to derived classes as well as a readonly property
	:attr:`Identifiers` for public access.
	"""

	_identifiers: Tuple[str]  #: A list of identifiers.

	def __init__(self, identifiers: Iterable[str]):
		"""
		Initializes a multiple-named entity.

		:param identifiers: Sequence of identifiers (names) of the model entity.
		"""
		self._identifiers = tuple(identifiers)

	@property
	def Identifiers(self) -> Tuple[str]:
		"""
		Returns a model entity's tuple of identifiers (names).

		:returns: Tuple of identifiers.
		"""
		return self._identifiers


@export
class LabeledEntityMixin:
	"""
	A ``LabeledEntityMixin`` is a mixin class for all VHDL entities that can have labels.

	A protected variable :attr:`_label` is available to derived classes as well as a readonly property :attr:`Label` for
	public access.
	"""
	_label: Nullable[str]  #: The label of a model entity.

	def __init__(self, label: Nullable[str]):
		"""
		Initializes a labeled entity.

		:param label: Label of the model entity.
		"""
		self._label = label

	@property
	def Label(self) -> Nullable[str]:
		"""
		Returns a model entity's label.

		:returns: Label of a model entity.
		"""
		return self._label


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
	_root: Nullable['Name']
	_prefix: Nullable['Name']

	def __init__(self, identifier: str, prefix: 'Name' = None):
		super().__init__()
		self._identifier = identifier
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


@export
class ContextReference(Reference):
	pass


@export
class DesignUnitWithContextMixin: #(metaclass=ExtendedType, useSlots=True):
	_contextItems:      List['ContextUnion']      #: List of all context items (library, use and context clauses).
	_libraryReferences: List['LibraryClause']     #: List of library clauses.
	_packageReferences: List['UseClause']         #: List of use clauses.
	_contextReferences: List['ContextReference']  #: List of context clauses.

	def __init__(self, contextItems: Iterable['ContextUnion'] = None):
		"""
		Initializes a mixin for design units with a context.

		:param contextItems: A sequence of library, use or context clauses.
		"""

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


@export
class DesignUnit(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""A ``DesignUnit`` is a base-class for all design units."""

	def __init__(self, identifier: str, documentation: str = None):
		"""
		Initializes a design unit.

		:param identifier:    Identifier (name) of the design unit.
		:param documentation: Associated documentation of the design unit.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

	@property
	def Document(self) -> 'Document':
		return self._parent

	@Document.setter
	def Document(self, document: 'Document') -> None:
		self._parent = document


@export
class PrimaryUnit(DesignUnit):
	"""A ``PrimaryUnit`` is a base-class for all primary units."""

	_library: 'Library'

	@property
	def Library(self) -> 'Library':
		return self._library

	@Library.setter
	def Library(self, library: 'Library') -> None:
		self._library = library


@export
class SecondaryUnit(DesignUnit):
	"""A ``SecondaryUnit`` is a base-class for all secondary units."""
