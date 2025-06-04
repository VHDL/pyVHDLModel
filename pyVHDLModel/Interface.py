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
# Copyright 2017-2025 Patrick Lehmann - Boetzingen, Germany                                                            #
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

Interface items are used in generic, port and parameter declarations.
"""
from typing                 import Iterable, Optional as Nullable, List

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Symbol     import Symbol
from pyVHDLModel.Base       import ModelEntity, DocumentedEntityMixin, ExpressionUnion, Mode, NamedEntityMixin
from pyVHDLModel.Object     import Constant, Signal, Variable, File
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Type       import Type


@export
class InterfaceItemMixin(DocumentedEntityMixin, mixin=True):
	"""An ``InterfaceItem`` is a base-class for all mixin-classes for all interface items."""

	def __init__(self, documentation: Nullable[str] = None) -> None:
		super().__init__(documentation)


@export
class InterfaceItemWithModeMixin(metaclass=ExtendedType, mixin=True):
	"""An ``InterfaceItemWithMode`` is a mixin-class to provide a ``Mode`` to interface items."""

	_mode: Mode

	def __init__(self, mode: Mode) -> None:
		self._mode = mode

	@readonly
	def Mode(self) -> Mode:
		return self._mode


@export
class GenericInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""A ``GenericInterfaceItem`` is a mixin class for all generic interface items."""


@export
class PortInterfaceItemMixin(InterfaceItemMixin, InterfaceItemWithModeMixin, mixin=True):
	"""A ``PortInterfaceItem`` is a mixin class for all port interface items."""

	_group: Nullable['PortGroup']

	def __init__(self, mode: Mode) -> None:
		super().__init__()
		InterfaceItemWithModeMixin.__init__(self, mode)
		self._group = None

	@property
	def Group(self) -> Nullable['PortGroup']:
		"""
		Read-only property to access the port group this port belongs to (:attr:`_group`).

		:returns: Reference to the port group, or None if not in a group.
		"""
		return self._group


@export
class ParameterInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""A ``ParameterInterfaceItem`` is a mixin class for all parameter interface items."""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class GenericTypeInterfaceItem(Type, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class GenericSubprogramInterfaceItem(GenericInterfaceItemMixin):
	pass


@export
class GenericProcedureInterfaceItem(Procedure, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class GenericFunctionInterfaceItem(Function, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class InterfacePackage(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class GenericPackageInterfaceItem(InterfacePackage, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class PortSignalInterfaceItem(Signal, PortInterfaceItemMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		PortInterfaceItemMixin.__init__(self, mode)


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItemMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)


@export
class PortGroup:
	"""A ``PortGroup`` is a group of ports."""

	_parent:    Nullable[ModelEntity]
	_name:      Nullable[str]
	_portItems: List[PortInterfaceItemMixin]

	def __init__(self, ports: Iterable[PortInterfaceItemMixin], name: Nullable[str] = None):
		"""Initialize a PortGroup with a list of ports and optional name."""
		self._parent = None
		self._name = name
		self._portItems = list(ports)
		if not self._portItems:
			raise ValueError("PortGroup cannot be empty")
		for port in self._portItems:
			if not isinstance(port, PortInterfaceItemMixin):
				raise TypeError(f"All ports must be PortInterfaceItemMixin instances, got {type(port)}")
			port._group = self

	@property
	def Name(self) -> Nullable[str]:
		"""Get the name of this port group."""
		return self._name

	@Name.setter
	def Name(self, value: Nullable[str]) -> None:
		"""Set the name of this port group."""
		self._name = value

	@property
	def PortItems(self) -> List[PortInterfaceItemMixin]:
		"""Get the list of port items in this group."""
		return self._portItems

	@property
	def Count(self) -> int:
		"""Get the number of ports in this group."""
		return len(self._portItems)

	@property
	def Parent(self) -> Nullable[ModelEntity]:
		"""
		Read-only property to access the parent entity that owns this port group (:attr:`_parent`).

		:returns: Reference to the parent entity (Entity or Component), or None if not assigned.
		"""
		return self._parent

	def __len__(self) -> int:
		"""Return the number of ports in this group."""
		return len(self._portItems)

	def __iter__(self):
		"""Iterate over ports in this group."""
		return iter(self._portItems)

	def __str__(self) -> str:
		"""String representation of the port group."""
		port_names = [str(port) for port in self._portItems]
		name_part = f"'{self._name}' " if self._name else ""
		return f"PortGroup({name_part}{len(self._portItems)} ports: {', '.join(port_names)})"

	__repr__ = __str__
