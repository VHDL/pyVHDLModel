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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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

Configurations: entity aspects, binding indications, component configurations (and the structurally
identical configuration specifications), and block configurations.
"""
from __future__              import annotations

from typing                  import List, Iterable, Union, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity
from pyVHDLModel.Name        import Name
from pyVHDLModel.Symbol      import Symbol, EntitySymbol, ArchitectureSymbol, ConfigurationSymbol
from pyVHDLModel.Symbol      import ComponentInstantiationSymbol
from pyVHDLModel.Association import GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Association import GenericMapAspectMixin, PortMapAspectMixin


@export
class EntityAspect(ModelEntity):
	"""
	Base-class for the three forms an entity aspect can take in a binding indication: an entity
	(optionally with an architecture), a configuration, or ``open``.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use entity work.sub(behav);
	      --                ^^^^^^^^^^^^^^^^^^^^^^

	.. seealso::

	   * :class:`Entity aspect entity <pyVHDLModel.Configuration.EntityAspectEntity>`
	   * :class:`Entity aspect configuration <pyVHDLModel.Configuration.EntityAspectConfiguration>`
	   * :class:`Entity aspect open <pyVHDLModel.Configuration.EntityAspectOpen>`
	"""


@export
class EntityAspectEntity(EntityAspect):
	"""
	Represents an entity aspect naming an entity, optionally with an architecture.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use entity work.e_rest(rtl);
	      --         ^^^^^^^^^^^         <- Entity
	      --                     ^^^     <- Architecture
	"""

	_entity:       EntitySymbol                  #: Reference to the named entity.
	_architecture: Nullable[ArchitectureSymbol]  #: Reference to the selected architecture, or ``None`` if none was given.

	def __init__(
		self,
		entity: EntitySymbol,
		architecture: Nullable[ArchitectureSymbol] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an entity aspect naming an entity, optionally with an architecture.

		:param entity:       Reference to the named entity.
		:param architecture: Reference to the selected architecture, or ``None`` if none was given.
		:param parent:       The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._entity = entity
		entity.Parent = self

		self._architecture = architecture
		if architecture is not None:
			architecture.Parent = self

	@readonly
	def Entity(self) -> EntitySymbol:
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	@readonly
	def Architecture(self) -> Nullable[ArchitectureSymbol]:
		"""
		Read-only property to access the architecture (:attr:`_architecture`).

		:returns: The architecture, or ``None`` if not set.
		"""
		return self._architecture


@export
class EntityAspectConfiguration(EntityAspect):
	"""
	Represents an entity aspect naming a configuration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use configuration work.cfg;
	      --                ^^^^^^^^    <- Configuration
	"""

	_configuration: ConfigurationSymbol  #: Reference to the named configuration.

	def __init__(self, configuration: ConfigurationSymbol, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an entity aspect naming a configuration.

		:param configuration: Reference to the named configuration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._configuration = configuration
		configuration.Parent = self

	@readonly
	def Configuration(self) -> ConfigurationSymbol:
		"""
		Read-only property to access the configuration (:attr:`_configuration`).

		:returns: The configuration.
		"""
		return self._configuration


@export
class EntityAspectOpen(EntityAspect):
	"""
	Represents an open entity aspect, leaving the binding unspecified.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use open;
	      --  ^^^^    <- the aspect
	"""


@export
class BindingIndication(ModelEntity, GenericMapAspectMixin, PortMapAspectMixin):
	"""
	Represents a binding indication: which design entity a component is bound to.

	The entity aspect is available as :data:`EntityAspect`, together with the generic and port maps
	(:data:`GenericAssociations`, :data:`PortAssociations`).
	"""

	_entityAspect: Nullable[EntityAspect]  #: The bound design entity, or ``None`` if not given.

	def __init__(
		self,
		entityAspect: Nullable[EntityAspect] = None,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		portAssociationItems: Nullable[Iterable[PortAssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a binding indication.

		:param entityAspect:            The bound design entity, or ``None`` if not given.
		:param genericAssociationItems: List of all generic associations in the generic map aspect.
		:param portAssociationItems:    List of all port associations in the port map aspect.
		:param parent:                  The parent model entity of this entity.
		"""
		super().__init__(parent)
		GenericMapAspectMixin.__init__(self, genericAssociationItems)
		PortMapAspectMixin.__init__(self, portAssociationItems)

		self._entityAspect = entityAspect
		if entityAspect is not None:
			entityAspect.Parent = self

	@readonly
	def EntityAspect(self) -> Nullable[EntityAspect]:
		"""
		Read-only property to access the entity aspect (:attr:`_entityAspect`).

		:returns: The entity aspect, or ``None`` if not set.
		"""
		return self._entityAspect




@export
class AllInstantiationList(ModelEntity):
	"""
	Represents an instantiation list naming ``all`` instances of a component.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for all : comp use entity work.sub(behav);
	      --  ^^^                                      <- the instantiation list
	"""


@export
class OthersInstantiationList(ModelEntity):
	"""
	Represents an instantiation list naming all instances not configured elsewhere.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for others : comp use entity work.sub(behav);
	      --  ^^^^^^                                      <- the instantiation list
	"""


InstantiationListUnion = Union[List[Name], AllInstantiationList, OthersInstantiationList]


@export
class ComponentConfiguration(ModelEntity):
	"""
	Represents a component configuration (inside a block configuration), or - structurally identical
	- a configuration specification (declared directly in an architecture's declarative part).

	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use entity work.sub(behav);
	      --  ^^   ^^^^
	      --  |    Component name
	      --  Instantiation list
	"""

	_instantiationList:  InstantiationListUnion        #: The instances this configuration applies to.
	_componentName:      ComponentInstantiationSymbol  #: Reference to the component being configured.
	_bindingIndication:   Nullable[BindingIndication]  #: The binding indication, or ``None`` if none was given.

	def __init__(
		self,
		instantiationList: InstantiationListUnion,
		componentName: ComponentInstantiationSymbol,
		bindingIndication: Nullable[BindingIndication] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a component configuration.

		:param instantiationList: The instances this configuration applies to.
		:param componentName:     Reference to the component being configured.
		:param bindingIndication: The binding indication, or ``None`` if none was given.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(parent)

		if isinstance(instantiationList, (AllInstantiationList, OthersInstantiationList)):
			self._instantiationList = instantiationList
			instantiationList.Parent = self
		else:
			self._instantiationList = [label for label in instantiationList]
			for label in self._instantiationList:
				label.Parent = self

		self._componentName = componentName
		componentName.Parent = self

		self._bindingIndication = bindingIndication
		if bindingIndication is not None:
			bindingIndication.Parent = self

	@readonly
	def InstantiationList(self) -> InstantiationListUnion:
		"""
		Read-only property to access the instantiation list (:attr:`_instantiationList`).

		:returns: The instantiation list.
		"""
		return self._instantiationList

	@readonly
	def ComponentName(self) -> ComponentInstantiationSymbol:
		"""
		Read-only property to access the component name (:attr:`_componentName`).

		:returns: The component name.
		"""
		return self._componentName

	@readonly
	def BindingIndication(self) -> Nullable[BindingIndication]:
		"""
		Read-only property to access the binding indication (:attr:`_bindingIndication`).

		:returns: The binding indication, or ``None`` if not set.
		"""
		return self._bindingIndication


@export
class BlockConfiguration(ModelEntity):
	"""
	Represents the configuration of one block: an architecture, a block statement or a generate body.

	Nested configurations are available as :data:`ConfigurationItems`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for rtl
	      --  ^^^    <- Block
	      end for;
	"""

	_blockSpecification: Symbol                                                    #: The configured block.
	_items:               List[Union[BlockConfiguration, ComponentConfiguration]]  #: Nested configurations.

	def __init__(
		self,
		blockSpecification: Symbol,
		items: Nullable[Iterable[Union[BlockConfiguration, ComponentConfiguration]]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a block configuration.

		:param blockSpecification: The configured block.
		:param items:              Nested configurations.
		:param parent:             The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._blockSpecification = blockSpecification
		blockSpecification.Parent = self

		self._items = []
		if items is not None:
			for item in items:
				self._items.append(item)
				item.Parent = self

	@readonly
	def BlockSpecification(self) -> Symbol:
		"""
		Read-only property to access the block specification (:attr:`_blockSpecification`).

		:returns: The block specification.
		"""
		return self._blockSpecification

	@readonly
	def Items(self) -> List[Union[BlockConfiguration, ComponentConfiguration]]:
		"""
		Read-only property to access the items (:attr:`_items`).

		:returns: List of items.
		"""
		return self._items
