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

VHDL uses *names* to express cross-references from *usage locations* to *declarations*. Here, *names* are single or
combined identifiers. :mod:`Symbols <pyVHDLModel.Symbol>` are structures representing a *name* and a reference
(pointer) to the referenced vhdl language entity.
"""
from typing import List, Iterable, Optional as Nullable

from pyTooling.Decorators import export, readonly

from pyVHDLModel.Base import ModelEntity, ExpressionUnion


@export
class Name(ModelEntity):
	"""``Name`` is the base-class for all *names* in the VHDL language model."""

	_identifier: str
	_normalizedIdentifier: str
	_root: Nullable['Name']     # TODO: seams to be unused. There is no reverse linking, or?
	_prefix: Nullable['Name']

	def __init__(self, identifier: str, prefix: Nullable["Name"] = None, parent: ModelEntity = None) -> None:
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
		The identifier the name is referencing.

		:returns: The referenced identifier.
		"""
		return self._identifier

	@readonly
	def NormalizedIdentifier(self) -> str:
		"""
		The normalized identifier the name is referencing.

		:returns: The referenced identifier (normalized).
		"""
		return self._normalizedIdentifier

	@readonly
	def Root(self) -> 'Name':
		"""
		The root (left-most) element in a chain of names.

		In case the name is a :class:`simple name <SimpleName>`, the root points to the name itself.

		:returns: The name's root element.
		"""
		return self._root

	@readonly
	def Prefix(self) -> Nullable['Name']:
		"""
		The name's prefix in a chain of names.

		:returns: The name left from current name, if not a simple name, otherwise ``None``.
		"""
		return self._prefix

	@readonly
	def HasPrefix(self) -> bool:
		"""
		Returns true, if the name has a prefix.

		This is true for all names except :class:`simple names <SimpleName>`.

		:returns: ``True``, if the name as a prefix.
		"""
		return self._prefix is not None

	def __repr__(self) -> str:
		return f"Name: '{self.__str__()}'"

	def __str__(self) -> str:
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
	_associations: List

	def __init__(self, prefix: Name, associations: Iterable, parent: ModelEntity = None) -> None:
		super().__init__("", prefix, parent)

		self._associations = []
		for association in associations:
			self._associations.append(association)
			association._parent = self

	@readonly
	def Associations(self) -> List:
		return self._associations

	def __str__(self) -> str:
		return f"{self._prefix!s}({', '.join(str(a) for a in self._associations)})"


@export
class IndexedName(Name):
	_indices: List[ExpressionUnion]

	def __init__(self, prefix: Name, indices: Iterable[ExpressionUnion], parent: ModelEntity = None) -> None:
		super().__init__("", prefix, parent)

		self._indices = []
		for index in indices:
			self._indices.append(index)
			index._parent = self

	@readonly
	def Indices(self) -> List[ExpressionUnion]:
		return self._indices

	def __str__(self) -> str:
		return f"{self._prefix!s}({', '.join(str(i) for i in self._indices)})"


@export
class SlicedName(Name):
	pass


@export
class SelectedName(Name):
	"""
	A *selected name* is a name made from multiple words separated by a dot (``.``).

	For example, the library and entity name in a direct entity instantiation is a selected name. Here the entity
	identifier is a selected name. The library identifier is a :class:`simple name <SimpleName>`, which is
	referenced by the selected name via the :attr:`~pyVHDLModel.Name.Prefix` property.
	"""

	def __init__(self, identifier: str, prefix: Name, parent: ModelEntity = None) -> None:
		super().__init__(identifier, prefix, parent)

	def __str__(self) -> str:
		return f"{self._prefix!s}.{self._identifier}"


@export
class AttributeName(Name):
	def __init__(self, identifier: str, prefix: Name, parent: ModelEntity = None) -> None:
		super().__init__(identifier, prefix, parent)

	def __str__(self) -> str:
		return f"{self._prefix!s}'{self._identifier}"


@export
class AllName(SelectedName):
	"""
	The *all name* represents the reserved word ``all`` used in names.

	Most likely this name is used in use-statements.
	"""
	def __init__(self, prefix: Name, parent: ModelEntity = None) -> None:
		super().__init__("all", prefix, parent)  # TODO: the case of 'ALL' is not preserved


@export
class OpenName(Name):
	"""
	The *open name* represents the reserved word ``open``.

	Most likely this name is used in port associations.
	"""
	def __init__(self, parent: ModelEntity = None) -> None:
		super().__init__("open", parent)  # TODO: the case of 'OPEN' is not preserved

	def __str__(self) -> str:
		return "open"
