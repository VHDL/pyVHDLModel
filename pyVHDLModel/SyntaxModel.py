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
This module contains an abstract document language model for VHDL.

:copyright: Copyright 2007-2023 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""

from typing                import List, Union, Iterable

from pyTooling.Decorators  import export

from pyVHDLModel import EntityClass
from pyVHDLModel           import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, PossibleReference
from pyVHDLModel           import Name, Symbol
from pyVHDLModel           import PrimaryUnit
from pyVHDLModel           import ExpressionUnion, ConstraintUnion, SubtypeOrSymbol
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Object import Constant, Variable, Signal
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Symbol import PackageReferenceSymbol
from pyVHDLModel.Type import Subtype

try:
	from typing import Protocol
except ImportError:  # pragma: no cover
	class Protocol:
		pass


# @export
# class SubtypeSymbol(Symbol):
# 	def __init__(self, symbolName: Name, possibleReferences: PossibleReference):
# 		super().__init__(symbolName, PossibleReference.Subtype | PossibleReference.TypeAttribute | possibleReferences)
#
# 	@property
# 	def Subtype(self) -> 'Subtype':
# 		return self._reference
#
# 	@Subtype.setter
# 	def Subtype(self, value: 'Subtype') -> None:
# 		self._reference = value
#
#
# @export
# class SimpleSubtypeSymbol(SubtypeSymbol):
# 	def __init__(self, subtypeName: Name):
# 		super().__init__(subtypeName, PossibleReference.ScalarType)
#
#
# @export
# class ConstrainedScalarSubtypeSymbol(SubtypeSymbol):
# 	_range: 'Range'
#
# 	def __init__(self, subtypeName: Name, rng: 'Range' = None):
# 		super().__init__(subtypeName, PossibleReference.ArrayType)
# 		self._range = rng
#
# 	@property
# 	def Range(self) -> 'Range':
# 		return self._range
#
#
# @export
# class ConstrainedCompositeSubtypeSymbol(SubtypeSymbol):
# 	_constraints: List[ConstraintUnion]
#
# 	def __init__(self, subtypeName: Name, constraints: Iterable[ConstraintUnion] = None):
# 		super().__init__(subtypeName, PossibleReference.Unknown)
# 		self._subtype = None
# 		self._constraints = [c for c in constraints]
#
# 	@property
# 	def Constraints(self) -> List[ConstraintUnion]:
# 		return self._constraints
#
#
# @export
# class ObjectSymbol(Symbol):
# 	pass
#
#
# @export
# class SimpleObjectOrFunctionCallSymbol(ObjectSymbol):
# 	def __init__(self, objectName: Name):
# 		super().__init__(objectName, PossibleReference.Constant | PossibleReference.Variable | PossibleReference.Signal | PossibleReference.ScalarType | PossibleReference.Function | PossibleReference.EnumLiteral)
#
# 	@property
# 	def ObjectOrFunction(self) -> Union['Constant', 'Signal', 'Variable', 'Function', 'EnumerationLiteral']:
# 		return self._reference
#
# 	@ObjectOrFunction.setter
# 	def ObjectOrFunction(self, value: Union['Constant', 'Signal', 'Variable', 'Function', 'EnumerationLiteral']):
# 		self._reference = value
#
#
# @export
# class IndexedObjectOrFunctionCallSymbol(ObjectSymbol):
# 	def __init__(self, objectName: Name):
# 		super().__init__(objectName, PossibleReference.Constant | PossibleReference.Variable | PossibleReference.Signal | PossibleReference.ArrayType | PossibleReference.Function)
#
# 	@property
# 	def ObjectOrFunction(self) -> Union['Constant', 'Signal', 'Variable', 'Function']:
# 		return self._reference
#
# 	@ObjectOrFunction.setter
# 	def ObjectOrFunction(self, value: Union['Constant', 'Signal', 'Variable', 'Function']):
# 		self._reference = value
#
#
# @export
# class ConstantSymbol(ObjectSymbol):
# 	def __init__(self, symbolName: Name):
# 		super().__init__(symbolName, PossibleReference.Constant)
#
# 	@property
# 	def Constant(self) -> 'Constant':
# 		return self._reference
#
# 	@Constant.setter
# 	def Constant(self, value: 'Constant') -> None:
# 		self._reference = value
#
#
# @export
# class VariableSymbol(ObjectSymbol):
# 	def __init__(self, symbolName: Name):
# 		super().__init__(symbolName, PossibleReference.Constant)
#
# 	@property
# 	def Variable(self) -> 'Variable':
# 		return self._reference
#
# 	@Variable.setter
# 	def Variable(self, value: 'Variable') -> None:
# 		self._reference = value
#
#
# @export
# class SignalSymbol(ObjectSymbol):
# 	def __init__(self, symbolName: Name):
# 		super().__init__(symbolName, PossibleReference.Signal)
#
# 	@property
# 	def Signal(self) -> 'Signal':
# 		return self._reference
#
# 	@Signal.setter
# 	def Signal(self, value: 'Signal') -> None:
# 		self._reference = value


@export
class Alias(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	def __init__(self, identifier: str, documentation: str = None):
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		"""
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


# TODO: add a reference to a basetype ?


@export
class BaseConstraint(ModelEntity):
	pass


@export
class RangeAttribute(BaseConstraint):
	# FIXME: Is this used?
	pass


@export
class RangeSubtype(BaseConstraint):
	# FIXME: Is this used?
	pass


@export
class Attribute(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	_subtype: SubtypeOrSymbol

	def __init__(self, identifier: str, subtype: SubtypeOrSymbol, documentation: str = None):
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

	@property
	def Subtype(self):
		return self._subtype


@export
class AttributeSpecification(ModelEntity, DocumentedEntityMixin):
	_identifiers: List[Name]
	_attribute: Name
	_entityClass: EntityClass
	_expression: ExpressionUnion

	def __init__(self, identifiers: Iterable[Name], attribute: Name, entityClass: EntityClass, expression: ExpressionUnion, documentation: str = None):
		super().__init__()
		DocumentedEntityMixin.__init__(self, documentation)

		self._identifiers = []  # TODO: convert to dict
		for identifier in identifiers:
			self._identifiers.append(identifier)
			identifier._parent = self

		self._attribute = attribute
		attribute._parent = self

		self._entityClass = entityClass

		self._expression = expression
		expression._parent = self

	@property
	def Identifiers(self) -> List[Name]:
		return self._identifiers

	@property
	def Attribute(self) -> Name:
		return self._attribute

	@property
	def EntityClass(self) -> EntityClass:
		return self._entityClass

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression


@export
class GenericEntityInstantiation:
	def __init__(self):
		pass


@export
class SubprogramInstantiation(ModelEntity, GenericEntityInstantiation):
	def __init__(self):
		super().__init__()
		GenericEntityInstantiation.__init__(self)
		self._subprogramReference = None


@export
class ProcedureInstantiation(Procedure, SubprogramInstantiation):
	pass


@export
class FunctionInstantiation(Function, SubprogramInstantiation):
	pass


@export
class PackageInstantiation(PrimaryUnit, GenericEntityInstantiation):
	_packageReference: PackageReferenceSymbol
	_genericAssociations: List[GenericAssociationItem]

	def __init__(self, identifier: str, uninstantiatedPackage: PackageReferenceSymbol, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericEntityInstantiation.__init__(self)

		self._packageReference = uninstantiatedPackage
		# uninstantiatedPackage._parent = self    # FIXME: uninstantiatedPackage is provided as int

		# TODO: extract to mixin
		self._genericAssociations = []

	@property
	def PackageReference(self) -> PackageReferenceSymbol:
		return self._packageReference

	@property
	def GenericAssociations(self) -> List[GenericAssociationItem]:
		return self._genericAssociations


@export
class SequentialDeclarations:
	_declaredItems: List

	def __init__(self, declaredItems: Iterable):
		# TODO: extract to mixin
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item._parent = self

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems





