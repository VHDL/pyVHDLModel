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
from __future__           import annotations

from typing               import List, Iterable, Optional as Nullable

from pyTooling.Decorators import export, readonly

from pyVHDLModel.Base     import ModelEntity, ExpressionUnion


@export
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
		:param prefix:     Reference to the name's prefix, or ``None`` for a simple name.
		:param parent:     The parent model entity of this entity.
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


@export
class ParenthesisName(Name):
	"""
	Represents a name followed by a parenthesized association list.

	Used where indexing and a function call are indistinguishable before resolution.
	"""
	_associations: List  #: List of all associations in the parenthesis.

	def __init__(self, prefix: Name, associations: Iterable, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name followed by a parenthesized association list.

		:param prefix:       Reference to the name's prefix, or ``None`` for a simple name.
		:param associations: List of all associations in the parenthesis.
		:param parent:       The parent model entity of this entity.
		"""
		super().__init__("", prefix, parent)

		self._associations = []
		for association in associations:
			self._associations.append(association)
			association.Parent = self

	@readonly
	def Associations(self) -> List:
		"""
		Read-only property to access the associations (:attr:`_associations`).

		:returns: List of associations.
		"""
		return self._associations

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
	_indices: List[ExpressionUnion]  #: List of all index expressions, one per dimension.

	def __init__(self, prefix: Name, indices: Iterable[ExpressionUnion], parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name indexing an array by one or more values.

		:param prefix:  Reference to the name's prefix, or ``None`` for a simple name.
		:param indices: List of all index expressions, one per dimension.
		:param parent:  The parent model entity of this entity.
		"""
		super().__init__("", prefix, parent)

		self._indices = []
		for index in indices:
			self._indices.append(index)
			index.Parent = self

	@readonly
	def Indices(self) -> List[ExpressionUnion]:
		"""
		Read-only property to access the indices (:attr:`_indices`).

		:returns: List of indices.
		"""
		return self._indices

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
	pass


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
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(identifier, prefix, parent)

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
	def __init__(self, identifier: str, prefix: Name, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a name selecting an attribute of its prefix.

		:param identifier: The name's identifier.
		:param prefix:     Reference to the name's prefix, or ``None`` for a simple name.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(identifier, prefix, parent)

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
		:param parent: The parent model entity of this entity.
		"""
		super().__init__("all", prefix, parent)  # TODO: the case of 'ALL' is not preserved


@export
class OpenName(Name):
	"""
	The *open name* represents the reserved word ``open``.

	Most likely this name is used in port associations.
	"""
	def __init__(self, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an ``open`` name.

		:param parent: The parent model entity of this entity.
		"""
		super().__init__("open", parent=parent)  # TODO: the case of 'OPEN' is not preserved

	def __str__(self) -> str:
		"""
		Formats the open name.

		**Format:** ``open``

		:returns: Formatted open name.
		"""
		return "open"
