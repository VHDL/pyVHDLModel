# =============================================================================
#             __     ___   _ ____  _     __  __           _      _
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|
#  |_|    |___/
# ==============================================================================
# Authors:            Patrick Lehmann
#
# Python package:     An abstract VHDL language model.
#
# Description:
# ------------------------------------
#		TODO:
#
# License:
# ==============================================================================
# Copyright 2017-2021 Patrick Lehmann - Boetzingen, Germany
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ==============================================================================
#
"""
An abstract VHDL language model.

:copyright: Copyright 2007-2021 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from enum     import IntEnum, unique, Enum
from typing import List, Iterable, Union, Optional as Nullable

from pydecor  import export


__version__ = "0.11.5"

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
	'LibraryClause'
	'UseClause'
	'ContextReference'
]

@export
@unique
class Direction(Enum):
	"""
	A ``Direction`` is an enumeration and represents a direction in a range
	(``to`` or ``downto``).
	"""
	To =      0
	DownTo =  1

	def __str__(self):
		index: int = self.value
		return ("to", "downto")[index]       # TODO: check performance


@export
@unique
class Mode(Enum):
	"""
	A ``Mode`` is an enumeration. It represents the direction of data exchange
	(``in``, ``out``, ...) for objects in generic, port or parameter lists.

	In case no *mode* is define, ``Default`` is used, so the *mode* is inferred
	from context.
	"""
	Default = 0
	In =      1
	Out =     2
	InOut =   3
	Buffer =  4
	Linkage = 5

	def __str__(self):
		index: int = self.value
		return ("", "in", "out", "inout", "buffer", "linkage")[index]       # TODO: check performance


@export
@unique
class ObjectClass(Enum):
	"""
	An ``ObjectClass`` is an enumeration. It represents an object's class (``constant``,
	``signal``, ...).

	In case no *object class* is define, ``Default`` is used, so the *object class*
	is inferred from context.
	"""
	Default =    0
	Constant =   1
	Variable =   2
	Signal =     3
	File =       4
	Type =       5
	Procedure =  6
	Function =   7


@export
@unique
class EntityClass(Enum):
	"""
	A ``Class`` is an enumeration. It represents an object's class (``constant``,
	``signal``, ...).

	In case no *object class* is define, ``Default`` is used, so the *object class*
	is inferred from context.
	"""
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
	``ModelEntity`` is the base class for all classes in the VHDL language model,
	except for mixin classes (see multiple inheritance) and enumerations.

	Each entity in this model has a reference to its parent entity. Therefore
	a protected variable :attr:`_parent` is available and a readonly property
	:attr:`Parent`.
	"""
	_parent: 'ModelEntity'      #: Reference to a parent entity in the model.

	def __init__(self):
		pass

	@property
	def Parent(self) -> 'ModelEntity':
		"""Returns a reference to the parent entity."""
		return self._parent


@export
class NamedEntity:
	"""
	A ``NamedEntity`` is a mixin class for all VHDL entities that have identifiers.

	A protected variable :attr:`_identifier` is available to derived classes as
	well as a readonly property :attr:`Identifier` for public access.
	"""
	_identifier: str                  #: The identifier of a model entity.

	def __init__(self, identifier: str):
		self._identifier = identifier

	@property
	def Identifier(self) -> str:
		"""Returns a model entity's identifier (name)."""
		return self._identifier


@export
class MultipleNamedEntity:
	"""
	A ``MultipleNamedEntity`` is a mixin class for all VHDL entities that declare
	multiple instances at once by giving multiple identifiers.

	A protected variable :attr:`_identifiers` is available to derived classes as
	well as a readonly property :attr:`Identifiers` for public access.
	"""
	_identifiers: List[str]           #: A list of identifiers.

	def __init__(self, identifiers: List[str]):
		self._identifiers = identifiers

	@property
	def Identifiers(self) -> List[str]:
		"""Returns a model entity's list of identifiers (name)."""
		return self._identifiers


@export
class LabeledEntity:
	"""
	A ``LabeledEntity`` is a mixin class for all VHDL entities that can have
	labels.

	A protected variable :attr:`_label` is available to derived classes as well
	as a readonly property :attr:`Label` for public access.
	"""
	_label: str                 #: The label of a model entity.

	def __init__(self, label: str):
		self._label = label

	@property
	def Label(self) -> str:
		"""Returns a model entity's label."""
		return self._label

@export
class MixinDesignUnitWithContext:
	_contextItems:      Nullable[List['ContextUnion']]
	_libraryReferences: Nullable[List['LibraryClause']]
	_packageReferences: Nullable[List['UseClause']]
	_contextReferences: Nullable[List['ContextReference']]

	def __init__(self, contextItems: Iterable['ContextUnion'] = None):
		from pyVHDLModel.SyntaxModel import LibraryClause, UseClause, ContextReference

		if contextItems is not None:
			self._contextItems = []
			self._libraryReferences = []
			self._packageReferences = []
			self._contextReferences = []

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
		return self._contextItems

	@property
	def LibraryReferences(self) -> List['LibraryClause']:
		return self._libraryReferences

	@property
	def PackageReferences(self) -> List['UseClause']:
		return self._packageReferences

	@property
	def ContextReferences(self) -> List['ContextReference']:
		return self._contextReferences


@export
class DesignUnit(ModelEntity, NamedEntity):
	"""
	A ``DesignUnit`` is a base-class for all design units.
	"""

	def __init__(self, identifier: str):
		super().__init__()
		NamedEntity.__init__(self, identifier)


@export
class PrimaryUnit(DesignUnit):
	"""
	A ``PrimaryUnit`` is a base-class for all primary units.
	"""

	@property
	def Library(self) -> 'Library':
		return self._parent
	@Library.setter
	def Library(self, library: 'Library') -> None:
		self._parent = library


@export
class SecondaryUnit(DesignUnit):
	"""
	A ``SecondaryUnit`` is a base-class for all secondary units.
	"""
