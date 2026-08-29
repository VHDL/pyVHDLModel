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

Concurrent defines all concurrent statements used in entities, architectures, generates and block statements.
"""
from typing                  import List, Dict, Union, Iterable, Generator, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity, LabeledEntityMixin, DocumentedEntityMixin, Range, BaseChoice, BaseCase, IfBranchMixin
from pyVHDLModel.Base        import ElsifBranchMixin, ElseBranchMixin, AssertStatementMixin, BlockStatementMixin, WaveformElement, ChoicesMixin
from pyVHDLModel.Regions     import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin
from pyVHDLModel.Namespace   import Namespace
from pyVHDLModel.Name        import Name
from pyVHDLModel.Symbol      import ComponentInstantiationSymbol, EntityInstantiationSymbol, ArchitectureSymbol, ConfigurationInstantiationSymbol
from pyVHDLModel.Symbol      import SignalSymbol
from pyVHDLModel.Expression  import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Association import AssociationItem, ParameterAssociationItem
from pyVHDLModel.Association import GenericAssociationItem, PortAssociationItem
from pyVHDLModel.Association import GenericMapAspectMixin, PortMapAspectMixin
from pyVHDLModel.Interface   import PortInterfaceItemMixin, WithPortsMixin
from pyVHDLModel.Interface   import GenericInterfaceItemMixin, WithGenericsMixin
from pyVHDLModel.Common      import Statement, ProcedureCallMixin, SignalAssignmentMixin, AllowBlackboxMixin
from pyVHDLModel.Common      import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Common      import ConditionalWaveformsMixin, WaveformMixin
from pyVHDLModel.Common      import ExpressionMixin, SelectedWaveformsMixin
from pyVHDLModel.Sequential  import SequentialStatement, SequentialStatementsMixin
from pyVHDLModel.Symbol      import Symbol


ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
class ConcurrentStatement(Statement):
	"""
	A base-class for all concurrent statements.

	.. seealso::

	   * :class:`Instantiation <pyVHDLModel.Concurrent.Instantiation>`
	   * :class:`Process statement <pyVHDLModel.Concurrent.ProcessStatement>`
	   * :class:`Concurrent procedure call <pyVHDLModel.Concurrent.ConcurrentProcedureCall>`
	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Generate statement <pyVHDLModel.Concurrent.GenerateStatement>`
	   * :class:`Concurrent signal assignment <pyVHDLModel.Concurrent.ConcurrentSignalAssignment>`
	   * :class:`Concurrent assert statement <pyVHDLModel.Concurrent.ConcurrentAssertStatement>`
	"""


@export
class ConcurrentStatementsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all language constructs supporting concurrent statements.

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`For generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`

	   .. todo:: concurrent declaration region
	"""

	_statements:     List[ConcurrentStatement]  #: List of all concurrent statements in this construct.

	# TODO: add another instantiation class level for entity/configuration/component inst.
	_instantiations: Dict[str, 'Instantiation']  #: All instantiations, indexed by label.
	_hierarchy:      Dict[str, Union['ConcurrentBlockStatement', 'GenerateStatement']]  #: All elements creating a hierarchy level (blocks and generates), in declaration order.

	def __init__(self, statements: Nullable[Iterable[ConcurrentStatement]] = None) -> None:
		"""
		Initializes concurrent statements.

		:param statements: List of all concurrent statements in this construct.
		"""
		self._statements = []

		self._instantiations = {}
		self._hierarchy = {}

		if statements is not None:
			for statement in statements:
				self._statements.append(statement)
				statement.Parent = self

	@readonly
	def Statements(self) -> List[ConcurrentStatement]:
		"""
		Read-only property to access the statements (:attr:`_statements`).

		:returns: List of statements.
		"""
		return self._statements

	def IterateInstantiations(self) -> Generator['Instantiation', None, None]:
		for instance in self._instantiations.values():
			yield instance

		for element in self._hierarchy.values():
			yield from element.IterateInstantiations()

	# TODO: move into _init__
	def IndexStatements(self) -> None:
		for statement in self._statements:
			if isinstance(statement, (EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation)):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, (ForGenerateStatement, IfGenerateStatement, CaseGenerateStatement)):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.IndexStatement()
			elif isinstance(statement, ConcurrentBlockStatement):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.IndexStatements()


@export
class Instantiation(ConcurrentStatement, GenericMapAspectMixin, PortMapAspectMixin):
	"""
	A base-class for all (component) instantiations.

	.. seealso::

	   * :class:`Component instantiation <pyVHDLModel.Concurrent.ComponentInstantiation>`
	   * :class:`Entity instantiation <pyVHDLModel.Concurrent.EntityInstantiation>`
	   * :class:`Configuration instantiation <pyVHDLModel.Concurrent.ConfigurationInstantiation>`
	"""

	def __init__(
		self,
		label: str,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[PortAssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an instantiation.

		:param label:                   The label of a model entity.
		:param genericAssociationItems: List of all generic associations in the generic map aspect.
		:param portAssociationItems:    List of all port associations in the port map aspect.
		:param parent:                  The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		GenericMapAspectMixin.__init__(self, genericAssociationItems)
		PortMapAspectMixin.__init__(self, portAssociationItems)




@export
class ComponentInstantiation(Instantiation):
	"""
	Represents a component instantiation.

	The instantiated component is available as :data:`Component`, the associations as
	:data:`GenericAssociationItems` and :data:`PortAssociationItems`. The label is mandatory.

	.. admonition:: Example

	   .. code-block:: VHDL

	        inst : component Counter;
	      --^^^^                        <- Label
	      --                 ^^^^^^^    <- Component
	"""

	_component: ComponentInstantiationSymbol  #: Reference to the instantiated component.

	def __init__(
		self,
		label: str,
		componentSymbol: ComponentInstantiationSymbol,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a component instantiation.

		:param label:                   The label of a model entity.
		:param componentSymbol:         Reference to the instantiated component.
		:param genericAssociationItems: List of all generic associations in the generic map aspect.
		:param portAssociationItems:    List of all port associations in the port map aspect.
		:param parent:                  The parent model entity of this entity.
		"""
		super().__init__(label, genericAssociationItems, portAssociationItems, parent)

		self._component = componentSymbol
		componentSymbol.Parent = self

	@readonly
	def Component(self) -> ComponentInstantiationSymbol:
		"""
		Read-only property to access the component (:attr:`_component`).

		:returns: The component.
		"""
		return self._component


@export
class EntityInstantiation(Instantiation):
	"""
	Represents a direct entity instantiation.

	The instantiated entity is available as :data:`Entity` and the optionally selected architecture
	as :data:`Architecture`. The label is mandatory.

	.. admonition:: Example

	   .. code-block:: VHDL

	        inst : entity work.Counter(rtl);
	      --^^^^                               <- Label
	      --              ^^^^^^^^^^^^         <- Entity
	      --                           ^^^     <- optional Architecture
	"""

	_entity: EntityInstantiationSymbol  #: Reference to the directly instantiated entity.
	_architecture: ArchitectureSymbol   #: Reference to the selected architecture, if one was given.

	def __init__(
		self,
		label: str,
		entitySymbol: EntityInstantiationSymbol,
		architectureSymbol: Nullable[ArchitectureSymbol] = None,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a direct entity instantiation.

		:param label:                   The label of a model entity.
		:param entitySymbol:            Reference to the directly instantiated entity.
		:param architectureSymbol:      Reference to the selected architecture, if one was given.
		:param genericAssociationItems: List of all generic associations in the generic map aspect.
		:param portAssociationItems:    List of all port associations in the port map aspect.
		:param parent:                  The parent model entity of this entity.
		"""
		super().__init__(label, genericAssociationItems, portAssociationItems, parent)

		self._entity = entitySymbol
		entitySymbol.Parent = self

		self._architecture = architectureSymbol
		if architectureSymbol is not None:
			architectureSymbol.Parent = self

	@readonly
	def Entity(self) -> EntityInstantiationSymbol:
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	@readonly
	def Architecture(self) -> ArchitectureSymbol:
		"""
		Read-only property to access the architecture (:attr:`_architecture`).

		:returns: The architecture.
		"""
		return self._architecture


@export
class ConfigurationInstantiation(Instantiation):
	"""
	Represents a configuration instantiation.

	The instantiated configuration is available as :data:`Configuration`. The label is mandatory.

	.. admonition:: Example

	   .. code-block:: VHDL

	        inst : configuration Counter;
	      --^^^^                            <- Label
	      --                     ^^^^^^^    <- Configuration
	"""

	_configuration: ConfigurationInstantiationSymbol  #: Reference to the instantiated configuration.

	def __init__(
		self,
		label: str,
		configurationSymbol: ConfigurationInstantiationSymbol,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a configuration instantiation.

		:param label:                   The label of a model entity.
		:param configurationSymbol:     Reference to the instantiated configuration.
		:param genericAssociationItems: List of all generic associations in the generic map aspect.
		:param portAssociationItems:    List of all port associations in the port map aspect.
		:param parent:                  The parent model entity of this entity.
		"""
		super().__init__(label, genericAssociationItems, portAssociationItems, parent)

		self._configuration = configurationSymbol
		configurationSymbol.Parent = self

	@readonly
	def Configuration(self) -> ConfigurationInstantiationSymbol:
		"""
		Read-only property to access the configuration (:attr:`_configuration`).

		:returns: The configuration.
		"""
		return self._configuration


@export
class ProcessStatement(ConcurrentStatement, SequentialDeclarationRegionMixin, SequentialStatementsMixin, DocumentedEntityMixin):
	"""
	Represents a process statement.

	A process declares its own items (:data:`DeclaredItems`) and groups sequential statements
	(:data:`Statements`). It may name a sensitivity list (:data:`SensitivityList`).

	.. admonition:: Example

	   .. code-block:: VHDL

	        proc : process (clock)
	      --^^^^                     <- optional Label
	      --                ^^^^^    <- optional SensitivityList
	          variable v : bit;
	      --  ^^^^^^^^^^^^^^^^^      <- DeclaredItems
	        begin
	          v := '1';
	      --  ^^^^^^^^^              <- Statements
	        end process;
	"""

	# TODO: implement a SignalSymbol
	_sensitivityList: List[Name]  #: List of all signal names in the sensitivity list, or ``None`` if none was given.

	def __init__(
		self,
		label: Nullable[str] = None,
		declaredItems: Nullable[Iterable] = None,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		sensitivityList: Nullable[Iterable[Name]] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a process statement.

		:param label:           The label of a model entity.
		:param declaredItems:   List of all declared items in this sequential declaration region.
		:param statements:      List of all sequential statements in this construct.
		:param sensitivityList: List of all signal names in the sensitivity list, or ``None`` if none was given.
		:param documentation:   The documentation comment associated with this declaration.
		:param parent:          The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedLabel, declaredItems)
		SequentialStatementsMixin.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				# signalSymbol._parent = self  # FIXME: currently str are provided

	@ConcurrentStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ConcurrentStatement.Parent.fset(self, parent)

		# Connect the process' namespace to the enclosing declaration region's namespace, so a declaration
		# inside the process hides a same-named one from the architecture, block or generate around it.
		self._namespace.ParentNamespace = parent._namespace

	@readonly
	def SensitivityList(self) -> List[Name]:
		"""
		Read-only property to access the sensitivity list (:attr:`_sensitivityList`).

		:returns: List of sensitivity list.
		"""
		return self._sensitivityList


@export
class ConcurrentProcedureCall(ConcurrentStatement, ProcedureCallMixin):
	"""
	Represents a concurrent procedure call.

	Like every concurrent statement, it can carry an optional label (:data:`Label`).

	.. admonition:: Example

	   .. code-block:: VHDL

	        proc_lbl : proc(clock, open);
	      --^^^^^^^^                        <- optional Label
	      --           ^^^^^^^^^^^^^^^^^    <- the call

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialProcedureCall>`
	"""
	def __init__(
		self,
		label: Nullable[str],
		procedureName: Symbol,
		parameterAssociationItems: Nullable[Iterable[ParameterAssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a concurrent procedure call.

		:param label:                     The label of a model entity.
		:param procedureName:             Reference to the called procedure.
		:param parameterAssociationItems: List of all parameter associations of the call.
		:param parent:                    The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		ProcedureCallMixin.__init__(self, procedureName, parameterAssociationItems)


@export
class ConcurrentBlockStatement(
	ConcurrentStatement,
	BlockStatementMixin,
	LabeledEntityMixin,
	WithGenericsMixin,
	WithPortsMixin,
	GenericMapAspectMixin,
	PortMapAspectMixin,
	ConcurrentDeclarationRegionMixin,
	ConcurrentStatementsMixin,
	DocumentedEntityMixin,
	AllowBlackboxMixin
):
	"""
	Represents a block statement.

	A block groups concurrent statements (:data:`Statements`) and may declare its own items
	(:data:`DeclaredItems`). It always forms a hierarchy level; independently of that, it may also have
	a block header: a generic clause (:data:`GenericItems`) with its generic map aspect
	(:data:`GenericAssociationItems`), and a port clause (:data:`PortItems`) with its port map aspect
	(:data:`PortAssociationItems`).

	.. admonition:: Example

	   .. code-block:: VHDL

	        blk : block
	      --^^^                              <- Label
	          generic (G : positive := 1);
	      --          ^^^^^^^^^^^^^^^^^^     <- GenericItems
	          generic map (G => 2);
	      --              ^^^^^^^^           <- GenericAssociationItems
	          port (bp : in bit);
	      --        ^^^^^^^^^^^              <- PortItems
	          port map (bp => clock);
	      --           ^^^^^^^^^^^^          <- PortAssociationItems
	          signal inner : bit := '0';
	      --  ^^^^^^^^^^^^^^^^^^^^^^^^^^     <- DeclaredItems
	        begin
	          inner <= bp;
	      --  ^^^^^^^^^^^^                   <- Statements
	        end block;

	.. seealso::

	   * :class:`Generate statement <pyVHDLModel.Concurrent.GenerateStatement>`
	"""
	_namespace: Namespace  #: The namespace of this block's declarative region.

	def __init__(
		self,
		label:                   str,
		genericItems:            Nullable[Iterable[GenericInterfaceItemMixin]] = None,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		portItems:               Nullable[Iterable[PortInterfaceItemMixin]] = None,
		portAssociationItems:    Nullable[Iterable[PortAssociationItem]] = None,
		declaredItems:           Nullable[Iterable] = None,
		statements:              Iterable['ConcurrentStatement'] = None,
		documentation:           Nullable[str] = None,
		allowBlackbox:           Nullable[bool] = None,
		parent:                  Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a block statement.

		:param label:                   The label of a model entity.
		:param genericItems:            List of all generics, in declaration order.
		:param genericAssociationItems: List of all generic associations in the generic map aspect.
		:param portItems:               List of all ports, in declaration order.
		:param portAssociationItems:    List of all port associations in the port map aspect.
		:param declaredItems:           List of all declared items in this concurrent declaration region.
		:param statements:              List of all concurrent statements in this construct.
		:param documentation:           The documentation comment associated with this declaration.
		:param allowBlackbox:           Allow blackboxes for components in language entity.
		:param parent:                  The parent model entity of this entity.
		"""
		super().__init__(label, parent)

		self._namespace = Namespace(self._normalizedLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		BlockStatementMixin.__init__(self)
		LabeledEntityMixin.__init__(self, label)
		WithGenericsMixin.__init__(self, genericItems)
		WithPortsMixin.__init__(self, portItems)
		GenericMapAspectMixin.__init__(self, genericAssociationItems)
		PortMapAspectMixin.__init__(self, portAssociationItems)
		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

	@ConcurrentStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ConcurrentStatement.Parent.fset(self, parent)

		self._namespace.ParentNamespace = parent._namespace


	def IndexDeclaredItems(self) -> None:
		"""A block's ports share the declarative region of its declarative part."""
		self._IndexPortItems()

		super().IndexDeclaredItems()


@export
class GenerateBranch(ModelEntity, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin):
	"""
	A base-class for all branches in a generate statements.

	.. seealso::

	   * :class:`If generate branch <pyVHDLModel.Concurrent.IfGenerateBranch>`
	   * :class:`Elsif generate branch <pyVHDLModel.Concurrent.ElsifGenerateBranch>`
	   * :class:`Else generate branch <pyVHDLModel.Concurrent.ElseGenerateBranch>`
	"""

	_alternativeLabel:           Nullable[str]  #: The branch's alternative label, if one was given.
	_normalizedAlternativeLabel: Nullable[str]  #: The normalized (lower case) alternative label.

	_namespace:                  Namespace      #: The namespace of this branch's declarative region.

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a generate branch.

		:param declaredItems:    List of all declared items in this concurrent declaration region.
		:param statements:       List of all concurrent statements in this construct.
		:param alternativeLabel: The branch's alternative label, if one was given.
		:param allowBlackbox:    Allow blackboxes for components in language entity.
		:param parent:           The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._alternativeLabel = alternativeLabel
		self._normalizedAlternativeLabel = alternativeLabel.lower() if alternativeLabel is not None else None

		self._namespace = Namespace(self._normalizedAlternativeLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

	@readonly
	def AlternativeLabel(self) -> Nullable[str]:
		"""
		Read-only property to access the alternative label (:attr:`_alternativeLabel`).

		:returns: The alternative label, or ``None`` if not set.
		"""
		return self._alternativeLabel

	@readonly
	def NormalizedAlternativeLabel(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized alternative label (:attr:`_normalizedAlternativeLabel`).

		:returns: The normalized alternative label, or ``None`` if not set.
		"""
		return self._normalizedAlternativeLabel


@export
class IfGenerateBranch(GenerateBranch, IfBranchMixin):
	"""
	Represents if-generate branch in a generate statement with a concurrent declaration region and concurrent statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- concurrent declarations
	      begin
	        -- concurrent statements
	      elsif condition generate
	        -- ...
	      else generate
	        -- ...
	      end generate;
	"""

	def __init__(
		self,
		condition:        ExpressionUnion,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an if generate branch.

		:param condition:        The condition guarding this statement.
		:param declaredItems:    List of all declared items in this concurrent declaration region.
		:param statements:       List of all concurrent statements in this construct.
		:param alternativeLabel: The branch's alternative label, if one was given.
		:param allowBlackbox:    Allow blackboxes for components in language entity.
		:param parent:           The parent model entity of this entity.
		"""
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifGenerateBranch(GenerateBranch, ElsifBranchMixin):
	"""
	Represents elsif-generate branch in a generate statement with a concurrent declaration region and concurrent statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- ...
	      elsif condition generate
	        -- concurrent declarations
	      begin
	        -- concurrent statements
	      else generate
	        -- ...
	      end generate;
	"""

	def __init__(
		self,
		condition:        ExpressionUnion,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an elsif generate branch.

		:param condition:        The condition guarding this statement.
		:param declaredItems:    List of all declared items in this concurrent declaration region.
		:param statements:       List of all concurrent statements in this construct.
		:param alternativeLabel: The branch's alternative label, if one was given.
		:param allowBlackbox:    Allow blackboxes for components in language entity.
		:param parent:           The parent model entity of this entity.
		"""
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseGenerateBranch(GenerateBranch, ElseBranchMixin):
	"""
	Represents else-generate branch in a generate statement with a concurrent declaration region and concurrent statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- ...
	      elsif condition generate
	        -- ...
	      else generate
	        -- concurrent declarations
	      begin
	        -- concurrent statements
	      end generate;
	"""

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an else generate branch.

		:param declaredItems:    List of all declared items in this concurrent declaration region.
		:param statements:       List of all concurrent statements in this construct.
		:param alternativeLabel: The branch's alternative label, if one was given.
		:param allowBlackbox:    Allow blackboxes for components in language entity.
		:param parent:           The parent model entity of this entity.
		"""
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)
		ElseBranchMixin.__init__(self)


@export
class GenerateStatement(ConcurrentStatement, AllowBlackboxMixin):
	"""
	Represents the base-class of all generate statements.

	A generate statement replicates or conditionally elaborates concurrent statements.

	.. seealso::

	   * :class:`If generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	   * :class:`Case generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	   * :class:`For generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	"""

	def __init__(
		self,
		label:         Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a generate statement.

		:param label:         The label of a model entity.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

	# @mustoverride
	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		raise NotImplementedError()

	# @mustoverride
	def IndexStatement(self) -> None:
		raise NotImplementedError()


@export
class IfGenerateStatement(GenerateStatement):
	"""
	Represents an if-generate statement.

	It has one ``if`` branch (:data:`IfBranch`), any number of ``elsif`` branches
	(:data:`ElsifBranches`) and an optional ``else`` branch (:data:`ElseBranch`). The label is
	mandatory and the branch conditions must be static expressions.

	.. admonition:: Example

	   .. code-block:: VHDL

	        gen : if WIDTH > 8 generate
	      --^^^                           <- Label
	      --      ^^^^^^^^^^^^^^^^^^^^^   <- IfBranch
	          q <= '0';
	        elsif WIDTH > 4 generate
	      --^^^^^^^^^^^^^^^^^^^^^^^^      <- ElsifBranches[0]
	          q <= '1';
	        else generate
	      --^^^^^^^^^^^^^                 <- ElseBranch
	          q <= 'Z';
	        end generate;

	.. seealso::

	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>` base-class
	   * :class:`If-generate branch <pyVHDLModel.Concurrent.IfGenerateBranch>`
	   * :class:`Elsif-generate branch <pyVHDLModel.Concurrent.ElsifGenerateBranch>`
	   * :class:`Else-generate branch <pyVHDLModel.Concurrent.ElseGenerateBranch>`
	   * :class:`Case-generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	   * :class:`For-generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	"""

	_ifBranch:      IfGenerateBranch              #: The mandatory ``if`` branch.
	_elsifBranches: List[ElsifGenerateBranch]     #: List of all ``elsif`` branches, in the order they were written.
	_elseBranch:    Nullable[ElseGenerateBranch]  #: The optional ``else`` branch, or ``None`` if none was given.

	def __init__(
		self,
		label:         str,
		ifBranch:      IfGenerateBranch,
		elsifBranches: Nullable[Iterable[ElsifGenerateBranch]] = None,
		elseBranch:    Nullable[ElseGenerateBranch] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an if-generate statement.

		:param label:         The label of a model entity.
		:param ifBranch:      The mandatory ``if`` branch.
		:param elsifBranches: List of all ``elsif`` branches, in the order they were written.
		:param elseBranch:    The optional ``else`` branch, or ``None`` if none was given.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(label, allowBlackbox, parent)

		self._ifBranch = ifBranch
		ifBranch.Parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch.Parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch.Parent = self
		else:
			self._elseBranch = None

	@GenerateStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		from pyVHDLModel.DesignUnit import Architecture

		GenerateStatement.Parent.fset(self, parent)

		# Connect namespaces
		namespace = self._ifBranch._namespace
		namespace.ParentNamespace = parent._namespace
		if namespace._name is None:
			namespace._name = self._normalizedLabel

		for elseBranch in self._elsifBranches:
			elseBranch._namespace.ParentNamespace = parent._namespace

		if self._elseBranch is not None:
			self._elseBranch._namespace.ParentNamespace = parent._namespace

	@readonly
	def IfBranch(self) -> IfGenerateBranch:
		"""
		Read-only property to access the if branch (:attr:`_ifBranch`).

		:returns: The if branch.
		"""
		return self._ifBranch

	@readonly
	def ElsifBranches(self) -> List[ElsifGenerateBranch]:
		"""
		Read-only property to access the elsif branches (:attr:`_elsifBranches`).

		:returns: List of elsif branches.
		"""
		return self._elsifBranches

	@readonly
	def ElseBranch(self) -> Nullable[ElseGenerateBranch]:
		"""
		Read-only property to access the else branch (:attr:`_elseBranch`).

		:returns: The else branch, or ``None`` if not set.
		"""
		return self._elseBranch

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		yield from self._ifBranch.IterateInstantiations()
		for branch in self._elsifBranches:
			yield from branch.IterateInstantiations()
		if self._elseBranch is not None:
			yield from self._ifBranch.IterateInstantiations()

	def IndexStatement(self) -> None:
		self._ifBranch.IndexStatements()
		for branch in self._elsifBranches:
			branch.IndexStatements()
		if self._elseBranch is not None:
			self._elseBranch.IndexStatements()


@export
class ConcurrentChoice(BaseChoice):
	"""
	A base-class for all concurrent choices (in case...generate statements).

	.. seealso::

	   * :class:`Indexed generate choice <pyVHDLModel.Concurrent.IndexedGenerateChoice>`
	   * :class:`Ranged generate choice <pyVHDLModel.Concurrent.RangedGenerateChoice>`
	"""


@export
class IndexedGenerateChoice(ConcurrentChoice):
	"""
	Represents a case-generate choice given by a single value.

	The value is available as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 8 =>
	      --   ^      <- Expression
	"""
	_expression: ExpressionUnion  #: The expression this choice selects on.

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a case-generate choice given by a single value.

		:param expression: The expression this choice selects on.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression

	def __str__(self) -> str:
		"""
		Formats the indexed case-generate choice.

		**Format:** ``0``

		:returns: Formatted indexed case-generate choice.
		"""
		return str(self._expression)


@export
class RangedGenerateChoice(ConcurrentChoice):
	"""
	Represents a case-generate choice given by a range.

	The range is available as :data:`Range`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 0 to 3 =>
	      --   ^^^^^^      <- Range
	"""
	_range: 'Range'  #: The range this choice selects on.

	def __init__(self, rng: 'Range', parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a case-generate choice given by a range.

		:param rng:    The range this choice selects on.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._range = rng
		rng.Parent = self

	@readonly
	def Range(self) -> 'Range':
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	def __str__(self) -> str:
		"""
		Formats the ranged case-generate choice.

		**Format:** ``0 to 3``

		:returns: Formatted ranged case-generate choice.
		"""
		return str(self._range)


@export
class ConcurrentCase(BaseCase, LabeledEntityMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin, ChoicesMixin):
	"""
	Represents the base-class of all alternatives of a case-generate statement.

	.. seealso::

	   * :class:`Generate case <pyVHDLModel.Concurrent.GenerateCase>`
	   * :class:`Others generate case <pyVHDLModel.Concurrent.OthersGenerateCase>`
	"""
	_namespace: Namespace  #: The namespace of this alternative's declarative region.

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		choices:          Nullable[Iterable[BaseChoice]] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a concurrent case.

		:param declaredItems:    List of all declared items in this concurrent declaration region.
		:param statements:       List of all concurrent statements in this construct.
		:param alternativeLabel: The alternative's label.
		:param choices:          List of all choices selecting this alternative.
		:param allowBlackbox:    Allow blackboxes for components in language entity.
		:param parent:           The parent model entity of this entity.
		"""
		super().__init__(parent)
		LabeledEntityMixin.__init__(self, alternativeLabel)

		# TODO: Why not handover self?
		#       This allows access to Label and NormalizedLabel, also to create a full instance path in case a lookup goes wrong.
		# TODO: How about a WithNamespaceMixin class?
		self._namespace = Namespace(self._normalizedLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		AllowBlackboxMixin.__init__(self, allowBlackbox)
		ChoicesMixin.__init__(self, choices)


@export
class GenerateCase(ConcurrentCase):
	"""
	Represents one alternative of a case-generate statement, selected by its choices.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 8 =>
	      --   ^      <- Choices
	"""
	def __init__(
		self,
		choices:          Iterable[ConcurrentChoice],
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a generate case.

		:param choices:          List of all choices selecting this alternative.
		:param declaredItems:    List of all declared items in this concurrent declaration region.
		:param statements:       List of all concurrent statements in this construct.
		:param alternativeLabel: The alternative's label.
		:param allowBlackbox:    Allow blackboxes for components in language entity.
		:param parent:           The parent model entity of this entity.
		"""
		super().__init__(declaredItems, statements, alternativeLabel, choices, allowBlackbox, parent)

	def __str__(self) -> str:
		"""
		Formats the case-generate alternative.

		**Format:** ``when 0 | 1 =>``

		:returns: Formatted case-generate alternative.
		"""
		return "when {choices} =>".format(choices=" | ".join(str(c) for c in self._choices))


@export
class OthersGenerateCase(ConcurrentCase):
	"""
	Represents the ``others`` alternative of a case-generate statement.

	It covers every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when others =>
	      --   ^^^^^^      <- the choice
	"""
	def __str__(self) -> str:
		"""
		Formats the ``others`` case-generate alternative.

		**Format:** ``when others =>``

		:returns: Formatted ``others`` case-generate alternative.
		"""
		return "when others =>"


@export
class CaseGenerateStatement(GenerateStatement):
	"""
	Represents a case-generate statement.

	The expression being tested is available as :data:`SelectExpression`, the alternatives as
	:data:`Cases`. The label is mandatory and the selector must be a static expression.

	.. admonition:: Example

	   .. code-block:: VHDL

	        gen : case MODE generate
	      --^^^                          <- Label
	      --           ^^^^              <- SelectExpression
	          when 0 => q <= '0';
	      --  ^^^^^^^^^^^^^^^^^^^        <- Cases[0]
	          when others => q <= '1';
	      --  ^^^^^^^^^^^^^^^^^^^^^^^^   <- Cases[1]
	        end generate;

	.. seealso::

	   * :class:`If-generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	   * :class:`For-generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	"""

	_expression: ExpressionUnion     #: The expression being tested; it must be static.
	_cases:      List[GenerateCase]  #: List of all alternatives, in the order they were written.

	def __init__(
		self,
		label:         str,
		expression:    ExpressionUnion,
		cases:         Iterable[ConcurrentCase],
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a case-generate statement.

		:param label:         The label of a model entity.
		:param expression:    The expression being tested; it must be static.
		:param cases:         List of all alternatives, in the order they were written.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(label, allowBlackbox, parent)

		self._expression = expression
		expression.Parent = self

		# TODO: create a mixin for things with cases
		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case.Parent = self

	@GenerateStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		GenerateStatement.Parent.fset(self, parent)

		# Connect namespaces
		for case in self._cases:
			case._namespace.ParentNamespace = parent._namespace

	@readonly
	def SelectExpression(self) -> ExpressionUnion:
		"""
		Read-only property to access the select expression (:attr:`_expression`).

		:returns: The select expression.
		"""
		return self._expression

	@readonly
	def Cases(self) -> List[GenerateCase]:
		"""
		Read-only property to access the cases (:attr:`_cases`).

		:returns: List of cases.
		"""
		return self._cases

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		for case in self._cases:
			yield from case.IterateInstantiations()

	def IndexStatement(self) -> None:
		for case in self._cases:
			case.IndexStatements()


@export
class ForGenerateStatement(GenerateStatement, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin):
	"""
	Represents a for-generate statement.

	The loop index is available as :data:`LoopIndex`, the iteration range as :data:`Range` and the
	generated statements as :data:`Statements`. The label is mandatory.

	.. admonition:: Example

	   .. code-block:: VHDL

	        gen : for i in 0 to 3 generate
	      --^^^                              <- Label
	      --          ^                      <- LoopIndex
	      --               ^^^^^^            <- Range
	          q(i) <= '0';
	      --  ^^^^^^^^^^^^                   <- Statements
	        end generate;

	.. seealso::

	   * :class:`If-generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	   * :class:`Case-generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	"""

	_loopIndex: str        #: The name of the generate loop's index.
	_range:     Range      #: The range the generate loop iterates over.

	_namespace: Namespace  #: The namespace of the generate loop's declarative region.

	def __init__(
		self,
		label:         str,
		loopIndex:     str,
		rng:           Range,
		declaredItems: Nullable[Iterable] = None,
		statements:    Nullable[Iterable[ConcurrentStatement]] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a for-generate statement.

		:param label:         The label of a model entity.
		:param loopIndex:     The name of the generate loop's index.
		:param rng:           The range the generate loop iterates over.
		:param declaredItems: List of all declared items in this concurrent declaration region.
		:param statements:    List of all concurrent statements in this construct.
		:param allowBlackbox: Allow blackboxes for components in language entity.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(label, allowBlackbox, parent)

		self._namespace = Namespace(self._normalizedLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)

		self._loopIndex = loopIndex

		self._range = rng
		rng.Parent = self

	@GenerateStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		GenerateStatement.Parent.fset(self, parent)

		self._namespace.ParentNamespace = parent._namespace

	@readonly
	def LoopIndex(self) -> str:
		"""
		Read-only property to access the loop index (:attr:`_loopIndex`).

		:returns: The loop index.
		"""
		return self._loopIndex

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	# IndexDeclaredItems = ConcurrentStatements.IndexDeclaredItems

	def IndexStatement(self) -> None:
		self.IndexStatements()

	def IndexStatements(self) -> None:
		super().IndexStatements()

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		return ConcurrentStatementsMixin.IterateInstantiations(self)


@export
class ConcurrentSignalAssignment(ConcurrentStatement, SignalAssignmentMixin):
	"""
	Represents the base-class of all concurrent signal assignments.

	.. seealso::

	   * :class:`Concurrent simple signal assignment <pyVHDLModel.Concurrent.ConcurrentSimpleSignalAssignment>`
	   * :class:`Concurrent selected signal assignment <pyVHDLModel.Concurrent.ConcurrentSelectedSignalAssignment>`
	   * :class:`Conditional signal assignment <pyVHDLModel.Concurrent.ConcurrentConditionalSignalAssignment>`	"""
	def __init__(self, label: Nullable[str], target: SignalSymbol, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a concurrent signal assignment.

		:param label:  The label of a model entity.
		:param target: Reference to the assignment's destination.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class ConcurrentSimpleSignalAssignment(ConcurrentSignalAssignment, WaveformMixin):
	"""
	Represents a simple concurrent signal assignment.

	The assignment's destination is available as :data:`Target`, its value as :data:`Waveform`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : q <= '1';
	      --^^^               <- optional Label
	      --      ^           <- Target
	      --           ^^^    <- Waveform

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialSimpleSignalAssignment>`
	"""
	def __init__(self, label: Nullable[str], target: SignalSymbol, waveform: Iterable[WaveformElement], parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a simple concurrent signal assignment.

		:param label:    The label of a model entity.
		:param target:   Reference to the assignment's destination.
		:param waveform: List of all waveform elements, in the order they were written.
		:param parent:   The parent model entity of this entity.
		"""
		super().__init__(label, target, parent)
		WaveformMixin.__init__(self, waveform)


@export
class ConcurrentSelectedSignalAssignment(ConcurrentSignalAssignment, ExpressionMixin, SelectedWaveformsMixin):
	"""
	Represents a selected concurrent signal assignment.

	The selector is available as :data:`Expression`, the alternatives as :data:`SelectedWaveforms`,
	a list of :class:`~pyVHDLModel.Common.SelectedWaveform`. The model holds them in a list and has
	no distinct field per alternative, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : with sel select q <= '1' when '0', '0' when others;
	      --^^^                                                         <- optional Label
	      --           ^^^                                              <- Expression
	      --                      ^                                     <- Target
	      --                           ^^^^^^^^^^^^                     <- SelectedWaveforms[0]
	      --                                         ^^^^^^^^^^^^^^^    <- SelectedWaveforms[1]

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialSelectedSignalAssignment>`
	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	"""

	def __init__(
		self,
		label: Nullable[str],
		target: SignalSymbol,
		expression: ExpressionUnion,
		selectedWaveforms: Iterable[SelectedWaveform],
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a selected concurrent signal assignment.

		:param label:             The label of a model entity.
		:param target:            Reference to the assignment's destination.
		:param expression:        The selector expression.
		:param selectedWaveforms: All alternatives, in order.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(label, target, parent)
		ExpressionMixin.__init__(self, expression)
		SelectedWaveformsMixin.__init__(self, selectedWaveforms)


@export
class ConcurrentConditionalSignalAssignment(ConcurrentSignalAssignment, ConditionalWaveformsMixin):
	"""
	Represents a conditional concurrent signal assignment.

	The alternatives are available as :data:`ConditionalWaveforms`, a list of
	:class:`~pyVHDLModel.Common.ConditionalWaveform`. The model holds them in a list and has no
	distinct field per alternative, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : q <= '1' when cond else '0';
	      --^^^                                  <- optional Label
	      --      ^                              <- Target
	      --           ^^^^^^^^^^^^^             <- ConditionalWaveforms[0]
	      --                              ^^^    <- ConditionalWaveforms[1]

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialConditionalSignalAssignment>`
	   * :class:`Conditional waveform <pyVHDLModel.Common.ConditionalWaveform>`
	"""

	def __init__(
		self,
		label: Nullable[str],
		target: SignalSymbol,
		conditionalWaveforms: Iterable[ConditionalWaveform],
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a conditional concurrent signal assignment.

		:param label:                The label of a model entity.
		:param target:               Reference to the assignment's destination.
		:param conditionalWaveforms: All alternatives, in order.
		:param parent:               The parent model entity of this entity.
		"""
		super().__init__(label, target, parent)
		ConditionalWaveformsMixin.__init__(self, conditionalWaveforms)


@export
class ConcurrentAssertStatement(ConcurrentStatement, AssertStatementMixin):
	"""
	Represents a concurrent assertion statement.

	The checked condition is available as :data:`Condition`, the optional report string as
	:data:`Message` and the optional severity as :data:`Severity`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : assert cond report "bad" severity note;
	      --^^^                                             <- optional Label
	      --             ^^^^                               <- Condition
	      --                         ^^^^^                  <- optional Message
	      --                                        ^^^^    <- optional Severity

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialAssertStatement>`
	"""
	def __init__(
		self,
		condition: ExpressionUnion,
		message: Nullable[ExpressionUnion] = None,
		severity: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a concurrent assertion statement.

		:param condition: The condition guarding this statement.
		:param message:   The reported message, or ``None`` if none was given.
		:param severity:  The reported severity level, or ``None`` if none was given.
		:param label:     The label of a model entity.
		:param parent:    The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		AssertStatementMixin.__init__(self, condition, message, severity)
