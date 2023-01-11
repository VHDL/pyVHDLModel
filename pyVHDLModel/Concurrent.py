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
# Copyright 2017-2023 Patrick Lehmann - Boetzingen, Germany                                                            #
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

from pyTooling.Decorators    import export

from pyVHDLModel.Base        import ModelEntity, LabeledEntityMixin, DocumentedEntityMixin, ExpressionUnion, Range, BaseChoice, BaseCase, IfBranchMixin, \
	ElsifBranchMixin, ElseBranchMixin, AssertStatementMixin, BlockStatementMixin, WaveformElement
from pyVHDLModel.Namespace       import Namespace
from pyVHDLModel.Symbol      import ComponentInstantiationSymbol, EntityInstantiationSymbol, ArchitectureSymbol, ConfigurationInstantiationSymbol
from pyVHDLModel.Association import AssociationItem, ParameterAssociationItem
from pyVHDLModel.Interface   import PortInterfaceItem
from pyVHDLModel.Common      import Statement, ProcedureCall, SignalAssignment
from pyVHDLModel.Sequential  import SequentialStatement, SequentialStatements, SequentialDeclarations


@export
class ConcurrentStatement(Statement):
	"""A ``ConcurrentStatement`` is a base-class for all concurrent statements."""


@export
class ConcurrentStatements:
	_statements:     List[ConcurrentStatement]

	_instantiations: Dict[str, 'Instantiation']  # TODO: add another instantiation class level for entity/configuration/component inst.
	_blocks:         Dict[str, 'ConcurrentBlockStatement']
	_generates:      Dict[str, 'GenerateStatement']
	_hierarchy:      Dict[str, Union['ConcurrentBlockStatement', 'GenerateStatement']]

	def __init__(self, statements: Iterable[ConcurrentStatement] = None):
		self._statements = []

		self._instantiations = {}
		self._blocks = {}
		self._generates = {}
		self._hierarchy = {}

		if statements is not None:
			for statement in statements:
				self._statements.append(statement)
				statement._parent = self

	@property
	def Statements(self) -> List[ConcurrentStatement]:
		return self._statements

	def IterateInstantiations(self) -> Generator['Instantiation', None, None]:
		for instance in self._instantiations.values():
			yield instance

		for block in self._blocks.values():
			yield from block.IterateInstantiations()

		for generate in self._generates.values():
			yield from generate.IterateInstantiations()

	# TODO: move into _init__
	def Index(self):
		for statement in self._statements:
			if isinstance(statement, EntityInstantiation):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, ComponentInstantiation):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, ConfigurationInstantiation):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, ForGenerateStatement):
				self._generates[statement.NormalizedLabel] = statement
				statement.Index()
			elif isinstance(statement, IfGenerateStatement):
				self._generates[statement.NormalizedLabel] = statement
				statement.Index()
			elif isinstance(statement, CaseGenerateStatement):
				self._generates[statement.NormalizedLabel] = statement
				statement.Index()
			elif isinstance(statement, ConcurrentBlockStatement):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.Index()


@export
class Instantiation(ConcurrentStatement):
	_genericAssociations: List[AssociationItem]
	_portAssociations: List[AssociationItem]

	def __init__(self, label: str, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label)

		# TODO: extract to mixin
		self._genericAssociations = []
		if genericAssociations is not None:
			for association in genericAssociations:
				self._genericAssociations.append(association)
				association._parent = self

		# TODO: extract to mixin
		self._portAssociations = []
		if portAssociations is not None:
			for association in portAssociations:
				self._portAssociations.append(association)
				association._parent = self

	@property
	def GenericAssociations(self) -> List[AssociationItem]:
		return self._genericAssociations

	@property
	def PortAssociations(self) -> List[AssociationItem]:
		return self._portAssociations


@export
class ComponentInstantiation(Instantiation):
	_component: ComponentInstantiationSymbol

	def __init__(self, label: str, componentSymbol: ComponentInstantiationSymbol, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label, genericAssociations, portAssociations)

		self._component = componentSymbol
		componentSymbol._parent = self

	@property
	def Component(self) -> ComponentInstantiationSymbol:
		return self._component


@export
class EntityInstantiation(Instantiation):
	_entity: EntityInstantiationSymbol
	_architecture: ArchitectureSymbol

	def __init__(self, label: str, entitySymbol: EntityInstantiationSymbol, architectureSymbol: ArchitectureSymbol = None, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label, genericAssociations, portAssociations)

		self._entity = entitySymbol
		entitySymbol._parent = self

		self._architecture = architectureSymbol
		if architectureSymbol is not None:
			architectureSymbol._parent = self

	@property
	def Entity(self) -> EntityInstantiationSymbol:
		return self._entity

	@property
	def Architecture(self) -> ArchitectureSymbol:
		return self._architecture


@export
class ConfigurationInstantiation(Instantiation):
	_configuration: ConfigurationInstantiationSymbol

	def __init__(self, label: str, configurationSymbol: ConfigurationInstantiationSymbol, genericAssociations: Iterable[AssociationItem] = None, portAssociations: Iterable[AssociationItem] = None):
		super().__init__(label, genericAssociations, portAssociations)

		self._configuration = configurationSymbol
		configurationSymbol._parent = self

	@property
	def Configuration(self) -> ConfigurationInstantiationSymbol:
		return self._configuration


@export
class ProcessStatement(ConcurrentStatement, SequentialDeclarations, SequentialStatements, DocumentedEntityMixin):
	_sensitivityList: List['Name']  # TODO: implement a SignalSymbol

	def __init__(
		self,
		label: str = None,
		declaredItems: Iterable = None,
		statements: Iterable[SequentialStatement] = None,
		sensitivityList: Iterable['Name'] = None,
		documentation: str = None
	):
		super().__init__(label)
		SequentialDeclarations.__init__(self, declaredItems)
		SequentialStatements.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				# signalSymbol._parent = self  # FIXME: currently str are provided

	@property
	def SensitivityList(self) -> List['Name']:
		return self._sensitivityList


@export
class ConcurrentProcedureCall(ConcurrentStatement, ProcedureCall):
	def __init__(self, label: str, procedureName: 'Name', parameterMappings: Iterable[ParameterAssociationItem] = None):
		super().__init__(label)
		ProcedureCall.__init__(self, procedureName, parameterMappings)


# FIXME: Why not used in package, package body
@export
class ConcurrentDeclarations:
	_declaredItems: List  # FIXME: define list prefix type e.g. via Union

	def __init__(self, declaredItems: Iterable = None):
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class ConcurrentBlockStatement(ConcurrentStatement, BlockStatementMixin, LabeledEntityMixin, ConcurrentDeclarations, ConcurrentStatements, DocumentedEntityMixin):
	_portItems:     List[PortInterfaceItem]

	def __init__(
		self,
		label: str,
		portItems: Iterable[PortInterfaceItem] = None,
		declaredItems: Iterable = None,
		statements: Iterable['ConcurrentStatement'] = None,
		documentation: str = None
	):
		super().__init__(label)
		BlockStatementMixin.__init__(self)
		LabeledEntityMixin.__init__(self, label)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		# TODO: extract to mixin
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item._parent = self

	@property
	def PortItems(self) -> List[PortInterfaceItem]:
		return self._portItems


@export
class GenerateBranch(ModelEntity, ConcurrentDeclarations, ConcurrentStatements):
	"""A ``GenerateBranch`` is a base-class for all branches in a generate statements."""

	_alternativeLabel:           Nullable[str]
	_normalizedAlternativeLabel: Nullable[str]

	_namespace:                  Namespace

	def __init__(self, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__()
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)

		self._alternativeLabel = alternativeLabel
		self._normalizedAlternativeLabel = alternativeLabel.lower() if alternativeLabel is not None else None

		self._namespace = Namespace(self._normalizedAlternativeLabel)

	@property
	def AlternativeLabel(self) -> Nullable[str]:
		return self._alternativeLabel

	@property
	def NormalizedAlternativeLabel(self) -> Nullable[str]:
		return self._normalizedAlternativeLabel


@export
class IfGenerateBranch(GenerateBranch, IfBranchMixin):
	def __init__(self, condition: ExpressionUnion, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifGenerateBranch(GenerateBranch, ElsifBranchMixin):
	def __init__(self, condition: ExpressionUnion, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseGenerateBranch(GenerateBranch, ElseBranchMixin):
	def __init__(self, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)
		ElseBranchMixin.__init__(self)


@export
class GenerateStatement(ConcurrentStatement):
	"""A ``GenerateStatement`` is a base-class for all generate statements."""

	_namespace: Namespace

	def __init__(self, label: str = None):
		super().__init__(label)

		self._namespace = Namespace(self._normalizedLabel)

	# @mustoverride
	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		raise NotImplementedError()

	# @mustoverride
	def Index(self) -> None:
		raise NotImplementedError()


@export
class IfGenerateStatement(GenerateStatement):
	_ifBranch:      IfGenerateBranch
	_elsifBranches: List[ElsifGenerateBranch]
	_elseBranch:    Nullable[ElseGenerateBranch]

	def __init__(self, label: str, ifBranch: IfGenerateBranch, elsifBranches: Iterable[ElsifGenerateBranch] = None, elseBranch: ElseGenerateBranch = None):
		super().__init__(label)

		self._ifBranch = ifBranch
		ifBranch._parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch._parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch._parent = self
		else:
			self._elseBranch = None

	@property
	def IfBranch(self) -> IfGenerateBranch:
		return self._ifBranch

	@property
	def ElsifBranches(self) -> List[ElsifGenerateBranch]:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> Nullable[ElseGenerateBranch]:
		return self._elseBranch

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		yield from self._ifBranch.IterateInstantiations()
		for branch in self._elsifBranches:
			yield from branch.IterateInstantiations()
		if self._elseBranch is not None:
			yield from self._ifBranch.IterateInstantiations()

	def Index(self) -> None:
		self._ifBranch.Index()
		for branch in self._elsifBranches:
			branch.Index()
		if self._elseBranch is not None:
			self._elseBranch.Index()


@export
class ConcurrentChoice(BaseChoice):
	"""A ``ConcurrentChoice`` is a base-class for all concurrent choices (in case...generate statements)."""


@export
class ConcurrentCase(BaseCase, LabeledEntityMixin, ConcurrentDeclarations, ConcurrentStatements):
	def __init__(self, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__()
		LabeledEntityMixin.__init__(self, alternativeLabel)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)


@export
class GenerateCase(ConcurrentCase):
	_choices: List[ConcurrentChoice]

	def __init__(self, choices: Iterable[ConcurrentChoice], declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None, alternativeLabel: str = None):
		super().__init__(declaredItems, statements, alternativeLabel)

		# TODO: move to parent or grandparent
		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice._parent = self

	# TODO: move to parent or grandparent
	@property
	def Choices(self) -> List[ConcurrentChoice]:
		return self._choices

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join([str(c) for c in self._choices]))


@export
class OthersGenerateCase(ConcurrentCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class CaseGenerateStatement(GenerateStatement):
	_expression: ExpressionUnion
	_cases:      List[GenerateCase]

	def __init__(self, label: str, expression: ExpressionUnion, cases: Iterable[ConcurrentCase]):
		super().__init__(label)

		self._expression = expression
		expression._parent = self

		# TODO: create a mixin for things with cases
		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case._parent = self

	@property
	def SelectExpression(self) -> ExpressionUnion:
		return self._expression

	@property
	def Cases(self) -> List[GenerateCase]:
		return self._cases

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		for case in self._cases:
			yield from case.IterateInstantiations()

	def Index(self):
		for case in self._cases:
			case.Index()


@export
class ForGenerateStatement(GenerateStatement, ConcurrentDeclarations, ConcurrentStatements):
	_loopIndex: str
	_range:     Range

	def __init__(self, label: str, loopIndex: str, rng: Range, declaredItems: Iterable = None, statements: Iterable[ConcurrentStatement] = None):
		super().__init__(label)
		ConcurrentDeclarations.__init__(self, declaredItems)
		ConcurrentStatements.__init__(self, statements)

		self._loopIndex = loopIndex

		self._range = rng
		rng._parent = self

	@property
	def LoopIndex(self) -> str:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range

	IterateInstantiations = ConcurrentStatements.IterateInstantiations

	Index = ConcurrentStatements.Index

	# def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
	# 	return ConcurrentStatements.IterateInstantiations(self)
	#
	# def Index(self) -> None:
	# 	return ConcurrentStatements.Index(self)


@export
class ConcurrentSignalAssignment(ConcurrentStatement, SignalAssignment):
	def __init__(self, label: str, target: 'Name'):
		super().__init__(label)
		SignalAssignment.__init__(self, target)


@export
class ConcurrentSimpleSignalAssignment(ConcurrentSignalAssignment):
	_waveform: List[WaveformElement]

	def __init__(self, label: str, target: 'Name', waveform: Iterable[WaveformElement]):
		super().__init__(label, target)

		# TODO: extract to mixin
		self._waveform = []
		if waveform is not None:
			for waveformElement in waveform:
				self._waveform.append(waveformElement)
				waveformElement._parent = self

	@property
	def Waveform(self) -> List[WaveformElement]:
		return self._waveform


@export
class ConcurrentSelectedSignalAssignment(ConcurrentSignalAssignment):
	def __init__(self, label: str, target: 'Name', expression: ExpressionUnion):
		super().__init__(label, target)


@export
class ConcurrentConditionalSignalAssignment(ConcurrentSignalAssignment):
	def __init__(self, label: str, target: 'Name', expression: ExpressionUnion):
		super().__init__(label, target)


@export
class ConcurrentAssertStatement(ConcurrentStatement, AssertStatementMixin):
	def __init__(self, condition: ExpressionUnion, message: ExpressionUnion, severity: ExpressionUnion = None, label: str = None):
		super().__init__(label)
		AssertStatementMixin.__init__(self, condition, message, severity)


@export
class IndexedGenerateChoice(ConcurrentChoice):
	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion):
		super().__init__()

		self._expression = expression
		expression._parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	def __str__(self) -> str:
		return "{expression!s}".format(expression=self._expression)


@export
class RangedGenerateChoice(ConcurrentChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range'):
		super().__init__()

		self._range = rng
		rng._parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return "{range!s}".format(range=self._range)
