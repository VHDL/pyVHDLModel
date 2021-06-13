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
# Python module:      An abstract VHDL language model.
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
:copyright: Copyright 2007-2021 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0

This module contains a document language model for VHDL.
"""
# load dependencies
from enum               import Enum
from pathlib            import Path
from typing             import Any, List, Tuple

from pydecor.decorators import export

__all__ = []
#__api__ = __all__ # FIXME: disabled due to a bug in pydecors export decorator


@export
class ModelEntity:
	"""
	``ModelEntity`` is a base class for all classes in the VHDL language model,
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
	A ``NamedEntity`` is a mixin class for all VHDL entities that have names.

	A protected variable :attr:`_name` is available to derived classes as well as
	a readonly property :attr:`Name` for public access.
	"""
	_name: str                  #: The name of a model entity.

	def __init__(self, name: str):
		self._name = name

	@property
	def Name(self) -> str:
		"""Returns a model entity's name."""
		return self._name


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
class Design(ModelEntity):
	"""
	A ``Design`` represents all loaded files (see :class:`~pyVHDLModel.VHDLModel.Document`)
	and analysed. It's the root of this document-object-model (DOM). It contains
	at least on VHDL library (see :class:`~pyVHDLModel.VHDLModel.Library`).
	"""
	_libraries:  List['Library']  #: List of all libraries defined for a design.
	_documents:  List['Document'] #: List of all documents loaded for a design.

	def __init__(self):
		super().__init__()

		self._libraries = []
		self._documents = []

	@property
	def Libraries(self) -> List['Library']:
		"""Returns a list of all libraries specified for this design."""
		return self._libraries

	@property
	def Documents(self) -> List['Document']:
		"""Returns a list of all documents (files) loaded for this design."""
		return self._documents


@export
class Library(ModelEntity, NamedEntity):
	"""
	A ``Library`` represents a VHDL library. It contains all *primary* design
	units.
	"""
	_contexts:       List['Context']        #: List of all contexts defined in a library.
	_configurations: List['Configuration']  #: List of all configurations defined in a library.
	_entities:       List['Entity']         #: List of all entities defined in a library.
	_packages:       List['Package']        #: List of all packages defined in a library.

	def __init__(self, name: str):
		super().__init__()
		NamedEntity.__init__(self, name)

		self._contexts =        []
		self._configurations =  []
		self._entities =        []
		self._packages =        []

	@property
	def Contexts(self) -> List['Context']:
		"""Returns a list of all context declarations loaded for this design."""
		return self._contexts

	@property
	def Configurations(self) -> List['Configuration']:
		"""Returns a list of all configuration declarations loaded for this design."""
		return self._configurations

	@property
	def Entities(self) -> List['Entity']:
		"""Returns a list of all entity declarations loaded for this design."""
		return self._entities

	@property
	def Packages(self) -> List['Package']:
		"""Returns a list of all package declarations loaded for this design."""
		return self._packages


@export
class Document(ModelEntity):
	"""
	A ``Document`` represents a sourcefile. It contains primary and secondary
	design units.
	"""
	_path:           Path                   #: path to the document. ``None`` if virtual document.
	_contexts:       List['Context']        #: List of all contexts defined in a document.
	_configurations: List['Configuration']  #: List of all configurations defined in a document.
	_entities:       List['Entity']         #: List of all entities defined in a document.
	_architectures:  List['Architecture']   #: List of all architectures defined in a document.
	_packages:       List['Package']        #: List of all packages defined in a document.
	_packageBodies:  List['PackageBody']    #: List of all package bodies defined in a document.

	def __init__(self, path: Path):
		super().__init__()

		self._path =            path
		self._contexts =        []
		self._configurations =  []
		self._entities =        []
		self._architectures =   []
		self._packages =        []
		self._packageBodies =   []

	@property
	def Path(self) -> Path:
		return self._path

	@property
	def Contexts(self) -> List['Context']:
		"""Returns a list of all context declarations found in this document."""
		return self._contexts

	@property
	def Configurations(self) -> List['Configuration']:
		"""Returns a list of all configuration declarations found in this document."""
		return self._configurations

	@property
	def Entities(self) -> List['Entity']:
		"""Returns a list of all entity declarations found in this document."""
		return self._entities

	@property
	def Architectures(self) -> List['Architecture']:
		"""Returns a list of all architecture declarations found in this document."""
		return self._architectures

	@property
	def Packages(self) -> List['Package']:
		"""Returns a list of all package declarations found in this document."""
		return self._packages

	@property
	def PackageBodies(self) -> List['PackageBody']:
		"""Returns a list of all package body declarations found in this document."""
		return self._packageBodies


@export
class Direction(Enum):
	"""
	A ``Direction`` is an enumeration and represents a direction in a range
	(``to`` or ``downto``).
	"""
	To =      0
	DownTo =  1


@export
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


@export
class Class(Enum):
	"""
	A ``Class`` is an enumeration. It represents an object's class (``constant``,
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
	Subprogram = 6


@export
class BaseType(ModelEntity, NamedEntity):
	"""``BaseType`` is the base class of all type entities in this model."""
	def __init__(self, name: str):
		"""
		Initializes underlying ``BaseType``.

		:param name: Name of the type.
		"""
		super().__init__()
		NamedEntity.__init__(self, name)


@export
class Type(BaseType):
	pass


@export
class SubType(BaseType):
	_type:               'SubType'
	_baseType:           Type
	_range:              'Range'
	_resolutionFunction: 'Function'

	def __init__(self, name: str):
		super().__init__(name)

	@property
	def Type(self) -> 'SubType':
		return self._type

	@property
	def BaseType(self) -> Type:
		return self._baseType

	@property
	def Range(self) -> 'Range':
		return self._range

	@property
	def ResolutionFunction(self) -> 'Function':
		return self._resolutionFunction


@export
class ScalarType(BaseType):
	"""
	A ``ScalarType`` is a base-class for all scalar types.
	"""


@export
class RangedScalarType(ScalarType):
	"""
	A ``RangedScalarType`` is a base-class for all scalar types with a range.
	"""

	_leftBound:  'Expression'
	_rightBound: 'Expression'

	@property
	def LeftBound(self) -> 'Expression':
		return self._leftBound

	@property
	def RightBound(self) -> 'Expression':
		return self._rightBound


@export
class NumericType:
	"""
	A ``NumericType`` is a mixin class for all numeric types.
	"""


@export
class DiscreteType:
	"""
	A ``DiscreteType`` is a mixin class for all discrete types.
	"""


@export
class CompositeType(BaseType):
	"""
	A ``CompositeType`` is a base-class for all composite types.
	"""


@export
class ProtectedType(BaseType):
	pass


@export
class AccessType(BaseType):
	pass


@export
class FileType(BaseType):
	pass


@export
class EnumeratedType(ScalarType, DiscreteType):
	_elements: List['EnumerationLiteral']

	def __init__(self, name: str):
		super().__init__(name)

		self._elements = []

	@property
	def Elements(self) -> List['EnumerationLiteral']:
		return self._elements


@export
class IntegerType(RangedScalarType, NumericType, DiscreteType):
	def __init__(self, name: str):
		super().__init__(name)


@export
class RealType(RangedScalarType, NumericType):
	def __init__(self, name: str):
		super().__init__(name)


@export
class PhysicalType(RangedScalarType, NumericType):
	_primaryUnit:    str
	_secondaryUnits: List[Tuple[int, str]]

	def __init__(self, name: str):
		super().__init__(name)

		self._secondaryUnits = []

	@property
	def PrimaryUnit(self) -> str:
		return self._primaryUnit

	@property
	def SecondaryUnits(self) -> List[Tuple[int, str]]:
		return self._secondaryUnits


@export
class ArrayType(CompositeType):
	_dimensions:  List['Range']
	_elementType: SubType

	def __init__(self, name: str):
		super().__init__(name)

		self._dimensions =  []

	@property
	def Dimensions(self) -> List['Range']:
		return self._dimensions

	@property
	def ElementType(self) -> SubType:
		return self._elementType


@export
class RecordTypeMember(ModelEntity):
	_name:    str
	_subType: SubType

	def __init__(self, name: str):
		super().__init__()

		self._name =        name
		self._subType =     None

	@property
	def Name(self) -> str:
		return self._name


@export
class RecordType(CompositeType):
	_members: List[RecordTypeMember]

	def __init__(self, name: str):
		super().__init__(name)

		self._members =     []

	@property
	def Members(self) -> List[RecordTypeMember]:
		return self._members


@export
class Expression(ModelEntity):
	"""
	A ``Expression`` is a base-class for all expressions.
	"""


@export
class Literal(Expression):
	"""
	A ``Literal`` is a base-class for all literals.
	"""
# TODO: add a reference to a basetype ?

@export
class EnumerationLiteral(Literal):
	_value: str

	def __init__(self, value: str):
		self._value = value

	@property
	def Value(self) -> str:
		return self._value


@export
class NumericLiteral(Literal):
	"""
	A ``NumericLiteral`` is a base-class for all numeric literals.
	"""


@export
class IntegerLiteral(NumericLiteral):
	_value: int

	def __init__(self, value: int):
		self._value = value

	@property
	def Value(self) -> int:
		return self._value


@export
class FloatingPointLiteral(NumericLiteral):
	_value: float

	def __init__(self, value: float):
		self._value = value

	@property
	def Value(self) -> float:
		return self._value

@export
class PhysicalLiteral(NumericLiteral):
	pass

@export
class CharacterLiteral(Literal):
	pass

@export
class StringLiteral(Literal):
	pass

@export
class BitStringLiteral(Literal):
	pass


@export
class UnaryExpression(Expression):
	"""
	A ``UnaryExpression`` is a base-class for all unary expressions.
	"""
	_operand:  Expression

	def __init__(self):
		pass

	@property
	def Operand(self):
		return self._operand

@export
class InverseExpression(UnaryExpression):
	pass

@export
class IdentityExpression(UnaryExpression):
	pass

@export
class NegationExpression(UnaryExpression):
	pass

@export
class AbsoluteExpression(UnaryExpression):
	pass

@export
class TypeConversion(UnaryExpression):
	pass

@export
class FunctionCall(UnaryExpression):
	pass

@export
class QualifiedExpression(UnaryExpression):
	pass

@export
class BinaryExpression(Expression):
	"""
	A ``BinaryExpression`` is a base-class for all binary expressions.
	"""

	_leftOperand:  Expression
	_rightOperand: Expression

	def __init__(self):
		pass

	@property
	def LeftOperand(self):
		return self._leftOperand

	@property
	def RightOperand(self):
		return self._rightOperand


@export
class	AddingExpression(BinaryExpression):
	"""
	A ``AddingExpression`` is a base-class for all adding expressions.
	"""

@export
class	AdditionExpression(AddingExpression):
	pass

@export
class	SubtractionExpression(AddingExpression):
	pass

@export
class	ConcatenationExpression(AddingExpression):
	pass

@export
class	MultiplyingExpression(BinaryExpression):
	"""
	A ``MultiplyingExpression`` is a base-class for all multiplying expressions.
	"""

@export
class	MultiplyExpression(MultiplyingExpression):
	pass

@export
class	DivisionExpression(MultiplyingExpression):
	pass

@export
class	RemainderExpression(MultiplyingExpression):
	pass

@export
class	ModuloExpression(MultiplyingExpression):
	pass

@export
class	ExponentiationExpression(MultiplyingExpression):
	pass

@export
class	LogicalExpression(BinaryExpression):
	"""
	A ``LogicalExpression`` is a base-class for all logical expressions.
	"""

@export
class AndExpression(LogicalExpression):
	pass

@export
class NandExpression(LogicalExpression):
	pass

@export
class OrExpression(LogicalExpression):
	pass

@export
class NorExpression(LogicalExpression):
	pass

@export
class XorExpression(LogicalExpression):
	pass

@export
class	XnorExpression(LogicalExpression):
	pass

@export
class	RelationalExpression(BinaryExpression):
	"""
	A ``RelationalExpression`` is a base-class for all shifting expressions.
	"""

@export
class	EqualExpression(RelationalExpression):
	pass

@export
class	UnequalExpression(RelationalExpression):
	pass

@export
class	GreaterThanExpression(RelationalExpression):
	pass

@export
class	GreaterEqualExpression(RelationalExpression):
	pass

@export
class	LessThanExpression(RelationalExpression):
	pass


@export
class	ShiftExpression(BinaryExpression):
	"""
	A ``ShiftExpression`` is a base-class for all shifting expressions.
	"""

@export
class ShiftLogicExpression(ShiftExpression):
	pass

@export
class ShiftArithmeticExpression(ShiftExpression):
	pass

@export
class RotateExpression(ShiftExpression):
	pass

@export
class	ShiftRightLogicExpression(ShiftLogicExpression):
	pass

@export
class	ShiftLeftLogicExpression(ShiftLogicExpression):
	pass

@export
class	ShiftRightArithmeticExpression(ShiftArithmeticExpression):
	pass

@export
class	ShiftLeftArithmeticExpression(ShiftArithmeticExpression):
	pass

@export
class	RotateRightExpression(RotateExpression):
	pass

@export
class	RotateLeftExpression(RotateExpression):
	pass

@export
class TernaryExpression(Expression):
	"""
	A ``TernaryExpression`` is a base-class for all ternary expressions.
	"""

	_firstOperand:  Expression
	_secondOperand: Expression
	_thirdOperand:  Expression

	def __init__(self):
		pass

	@property
	def FirstOperand(self):
		return self._firstOperand

	@property
	def SecondOperand(self):
		return self._secondOperand

	@property
	def ThirdOperand(self):
		return self._thirdOperand


@export
class Range:
	_leftBound:  Any
	_rightBound: Any
	_direction:  Direction

	def __init__(self):
		pass

@export
class Object(ModelEntity, NamedEntity):
	_subType: SubType

	def __init__(self, name: str):
		super().__init__()
		NamedEntity.__init__(self, name)

	@property
	def SubType(self) -> SubType:
		return self._subType


@export
class WithDefaultExpression:
	"""
	A ``WithDefaultExpression`` is a mixin class for all objects declarations
	accepting default expressions.
	"""
	_defaultExpression: Expression

	@property
	def DefaultExpression(self) -> Expression:
		return self._defaultExpression


@export
class BaseConstant(Object):
	pass


@export
class Constant(BaseConstant, WithDefaultExpression):
	pass


@export
class DeferredConstant(BaseConstant):
	_constantReference: Constant

	@property
	def ConstantReference(self) -> Constant:
		return self._constantReference


@export
class Variable(Object, WithDefaultExpression):
	pass


@export
class Signal(Object, WithDefaultExpression):
	pass

@export
class File(Object):
	pass
#	_defaultExpression: Expression


@export
class SubProgramm(ModelEntity, NamedEntity):
	_genericItems:   List['GenericInterfaceItem']
	_parameterItems: List['ParameterInterfaceItem']
	_declaredItems:  List
	_bodyItems:      List['SequentialStatement']
	_isPure:         bool

	def __init__(self, name: str):
		super().__init__()
		NamedEntity.__init__(self, name)

		self._genericItems =    []
		self._parameterItems =  []
		self._declaredItems =   []
		self._bodyItems =       []

	@property
	def GenericItems(self) -> List['GenericInterfaceItem']:
		return self._genericItems

	@property
	def ParameterItems(self) -> List['ParameterInterfaceItem']:
		return self._parameterItems

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems

	@property
	def BodyItems(self) -> List['SequentialStatement']:
		return self._bodyItems

	@property
	def IsPure(self) -> bool:
		return self._isPure


@export
class Procedure(SubProgramm):
	_isPure: bool = False


@export
class Function(SubProgramm):
	_returnType: SubType

	def __init__(self, name: str, isPure: bool = True):
		super().__init__(name)
		self._isPure = isPure

	@property
	def ReturnType(self) -> SubType:
		return self._returnType


@export
class Method:
	"""
	A ``Method`` is a mixin class for all subprograms in a protected type.
	"""
	_protectedType: ProtectedType

	def __init__(self, protectedType: ProtectedType):
		self._protectedType = protectedType

	@property
	def ProtectedType(self) -> ProtectedType:
		return self._protectedType


@export
class ProcedureMethod(Procedure, Method):
	def __init__(self, name: str, protectedType: ProtectedType):
		super().__init__(name)
		Method.__init__(self, protectedType)


@export
class FunctionMethod(Function, Method):
	def __init__(self, name: str, protectedType: ProtectedType):
		super().__init__(name)
		Method.__init__(self, protectedType)


@export
class InterfaceItem:
	"""
	An ``InterfaceItem`` is a base-class for all mixin-classes for all interface
	items.
	"""
	_mode: Mode

	def __init__(self, mode: Mode):
		self._mode = mode

	@property
	def Mode(self) -> Mode:
		return self._mode


@export
class GenericInterfaceItem(InterfaceItem):
	"""
	A ``GenericInterfaceItem`` is a mixin class for all generic interface items.
	"""


@export
class PortInterfaceItem(InterfaceItem):
	"""
	A ``PortInterfaceItem`` is a mixin class for all port interface items.
	"""


@export
class ParameterInterfaceItem(InterfaceItem):
	"""
	A ``ParameterInterfaceItem`` is a mixin class for all parameter interface items.
	"""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItem):
	def __init__(self, name: str, mode: Mode):
		super().__init__(name)
		GenericInterfaceItem.__init__(self, mode)


@export
class GenericTypeInterfaceItem(GenericInterfaceItem):
	pass

@export
class GenericSubprogramInterfaceItem(GenericInterfaceItem):
	pass

@export
class GenericProcedureInterfaceItem(Procedure, GenericInterfaceItem):
	pass

@export
class GenericFunctionInterfaceItem(Function, GenericInterfaceItem):
	pass

@export
class GenericPackageInterfaceItem(GenericInterfaceItem):
	pass


@export
class PortSignalInterfaceItem(Signal, PortInterfaceItem):
	def __init__(self, name: str, mode: Mode):
		super().__init__(name)
		PortInterfaceItem.__init__(self, mode)


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItem):
	def __init__(self, name: str, mode: Mode):
		super().__init__(name)
		ParameterInterfaceItem.__init__(self, mode)


@export
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItem):
	def __init__(self, name: str, mode: Mode):
		super().__init__(name)
		ParameterInterfaceItem.__init__(self, mode)


@export
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItem):
	def __init__(self, name: str, mode: Mode):
		super().__init__(name)
		ParameterInterfaceItem.__init__(self, mode)


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItem):
	def __init__(self, name: str, mode: Mode):
		super().__init__(name)
		ParameterInterfaceItem.__init__(self, mode)

# class GenericItem(ModelEntity):
# 	def __init__(self):
# 		super().__init__()
# 		self._name = None
# 		self._subType = None
# 		self._init = None
#
#
# class PortItem(ModelEntity):
# 	def __init__(self):
# 		super().__init__()
# 		self._name =        None
# 		self._subType =     None
# 		self._init =        None
# 		self._mode =        None
# 		self._class =       None


@export
class LibraryReference(ModelEntity):
	_library: Library

	def __init__(self):
		super().__init__()
		self._library = None

	@property
	def Library(self) -> Library:
		return self._library


@export
class PackageReference(ModelEntity):
	_library: Library
	_package: 'Package'
	_item:    str

	def __init__(self):
		super().__init__()

	@property
	def Library(self) -> Library:
		return self._library

	@property
	def Package(self) -> 'Package':
		return self._package

	@property
	def Item(self) -> str:
		return self._item


@export
class ContextReference(ModelEntity):
	_library: Library
	_context: 'Context'

	def __init__(self):
		super().__init__()

	@property
	def Library(self) -> Library:
		return self._library

	@property
	def Context(self) -> 'Context':
		return self._context


@export
class DesignUnit(ModelEntity, NamedEntity):
	"""
	A ``DesignUnit`` is a base-class for all design units.
	"""

	def __init__(self, name: str):
		super().__init__()
		NamedEntity.__init__(self, name)

@export
class MixinDesignUnitWithContext:
	"""
	A ``DesignUnitWithReferences`` is a base-class for all design units with contexts.
	"""
	_libraryReferences: List[Library]
	_packageReferences: List[PackageReference]
	_contextReferences: List['Context']

	def __init__(self):
		self._libraryReferences = []
		self._packageReferences = []
		self._contextReferences = []

	@property
	def LibraryReferences(self) -> List[Library]:
		return self._libraryReferences

	@property
	def PackageReferences(self) -> List[PackageReference]:
		return self._packageReferences

	@property
	def ContextReferences(self) -> List['Context']:
		return self._contextReferences


@export
class PrimaryUnit(DesignUnit):
	"""
	A ``PrimaryUnit`` is a base-class for all primary units.
	"""


@export
class SecondaryUnit(DesignUnit):
	"""
	A ``SecondaryUnit`` is a base-class for all secondary units.
	"""


@export
class Context(PrimaryUnit):
	_libraryReferences: List[LibraryReference]
	_packageReferences: List[PackageReference]

	def __init__(self, name):
		super().__init__(name)

		self._libraryReferences = []
		self._packageReferences = []

	@property
	def LibraryReferences(self) -> List[LibraryReference]:
		return self._libraryReferences

	@property
	def PackageReferences(self) -> List[PackageReference]:
		return self._packageReferences


@export
class Entity(PrimaryUnit, MixinDesignUnitWithContext):
	_genericItems:      List[GenericInterfaceItem]
	_portItems:         List[PortInterfaceItem]
	_declaredItems:     List   # FIXME: define list element type e.g. via Union
	_bodyItems:         List['ConcurrentStatement']

	def __init__(self, name: str):
		super().__init__(name)
		MixinDesignUnitWithContext.__init__(self)

		self._genericItems      = []
		self._portItems         = []
		self._declaredItems     = []
		self._bodyItems         = []

	@property
	def GenericItems(self) -> List[GenericInterfaceItem]:
		return self._genericItems

	@property
	def PortItems(self) -> List[PortInterfaceItem]:
		return self._portItems

	@property
	def DeclaredItems(self) -> List:   # FIXME: define list element type e.g. via Union
		return self._declaredItems

	@property
	def BodyItems(self) -> List['ConcurrentStatement']:
		return self._bodyItems


@export
class Architecture(SecondaryUnit, MixinDesignUnitWithContext):
	_entity:            Entity
	_declaredItems:     List   # FIXME: define list element type e.g. via Union
	_bodyItems:         List['ConcurrentStatement']

	def __init__(self, name: str):
		super().__init__(name)
		MixinDesignUnitWithContext.__init__(self)

		self._declaredItems =     []
		self._bodyItems =         []

	@property
	def Entity(self) -> Entity:
		return self._entity

	@property
	def DeclaredItems(self) -> List:   # FIXME: define list element type e.g. via Union
		return self._declaredItems

	@property
	def BodyItems(self) -> List['ConcurrentStatement']:
		return self._bodyItems


@export
class Configuration(PrimaryUnit, MixinDesignUnitWithContext):
	def __init__(self, name: str):
		super().__init__(name)
		MixinDesignUnitWithContext.__init__(self)


@export
class AssociationItem(ModelEntity):
	_formal: str    # FIXME: defined type
	_actual: Expression

	def __init__(self):
		super().__init__()

	@property
	def Formal(self):    # FIXME: defined return type
		return self._formal

	@property
	def Actual(self) -> Expression:
		return self._actual


@export
class GenericAssociationItem(AssociationItem):
	pass


@export
class PortAssociationItem(AssociationItem):
	pass


@export
class ParameterAssociationItem(AssociationItem):
	pass


@export
class GenericEntityInstantiation:
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
class Package(PrimaryUnit, MixinDesignUnitWithContext):
	_genericItems:      List[GenericInterfaceItem]
	_declaredItems:     List

	def __init__(self, name: str):
		super().__init__(name)
		MixinDesignUnitWithContext.__init__(self)

		self._genericItems =      []
		self._declaredItems =     []

	@property
	def GenericItems(self) -> List[GenericInterfaceItem]:
		return self._genericItems

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class PackageBody(SecondaryUnit, MixinDesignUnitWithContext):
	_package:           Package
	_declaredItems:     List

	def __init__(self, name: str):
		super().__init__(name)
		MixinDesignUnitWithContext.__init__(self)

		self._declaredItems =     []

	@property
	def Package(self) -> Package:
		return self._package

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class PackageInstantiation(PrimaryUnit, GenericEntityInstantiation):
	_packageReference:    Package
	_genericAssociations: List[GenericAssociationItem]

	def __init__(self, name: str):
		super().__init__(name)
		GenericEntityInstantiation.__init__(self)

		self._genericAssociations = []

	@property
	def PackageReference(self) -> Package:
		return self._packageReference

	@property
	def GenericAssociations(self) -> List[GenericAssociationItem]:
		return self._genericAssociations


@export
class Statement(ModelEntity, LabeledEntity):
	def __init__(self, label: str = None):
		super().__init__()
		LabeledEntity.__init__(self, label)


@export
class ConcurrentStatement(Statement):
	"""
	A ``ConcurrentStatement`` is a base-class for all concurrent statements.
	"""


@export
class SequentialStatement(Statement):
	"""
	A ``SequentialStatement`` is a base-class for all sequential statements.
	"""


@export
class ConcurrentDeclarations:
	_declaredItems: List

	def __init__(self):
		self._declaredItems = []

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class ConcurrentStatements:
	_statements: List[ConcurrentStatement]

	def __init__(self):
		self._statements = []

	@property
	def Statements(self) -> List[ConcurrentStatement]:
		return self._statements

@export
class SequentialDeclarations:
	_declaredItems: List

	def __init__(self):
		self._declaredItems = []

	@property
	def DeclaredItems(self) -> List:
		return self._declaredItems


@export
class SequentialStatements:
	_statements: List[SequentialStatement]

	def __init__(self):
		self._statements = []

	@property
	def Statements(self) -> List[SequentialStatement]:
		return self._statements


@export
class Instantiation(ConcurrentStatement):
	pass


@export
class ComponentInstantiation(Instantiation):
	pass

@export
class EntityInstantiation(Instantiation):
	pass

@export
class ConfigurationInstantiation(Instantiation):
	pass


@export
class ProcessStatement(ConcurrentStatement, SequentialDeclarations, SequentialStatements):
	_sensitivityList: List[Signal]

	def __init__(self, label: str = None):
		super().__init__(label=label)
		SequentialDeclarations.__init__(self)
		SequentialStatements.__init__(self)

	@property
	def SensitivityList(self) -> List[Signal]:
		return self._sensitivityList


@export
class ProcedureCall:
	pass


@export
class ConcurrentProcedureCall(ConcurrentStatement, ProcedureCall):
	pass


@export
class SequentialProcedureCall(SequentialStatement, ProcedureCall):
	pass


# TODO: could be unified with ProcessStatement if 'List[ConcurrentStatement]' becomes parametric to T
class BlockStatement:
	"""
	A ``BlockStatement`` is a mixin-class for all block statements.
	"""


@export
class ConcurrentBlockStatement(ConcurrentStatement, BlockStatement, ConcurrentDeclarations, ConcurrentStatements):
	_portItems:     List[PortInterfaceItem]

	def __init__(self, label: str = None):
		super().__init__(label=label)
		BlockStatement.__init__(self)
		ConcurrentDeclarations.__init__(self)
		ConcurrentStatements.__init__(self)

		self._portItems =     []

	@property
	def PortItems(self) -> List[PortInterfaceItem]:
		return self._portItems


@export
class MixinConditional:
	"""
	A ``BaseConditional`` is a mixin-class for all statements with a condition.
	"""
	_condition: Expression

	@property
	def Condition(self) -> Expression:
		return self._condition


@export
class MixinBranch:
	"""
	A ``BaseBranch`` is a mixin-class for all statements with branches.
	"""


@export
class MixinConditionalBranch(MixinBranch, MixinConditional):
	"""
	A ``BaseBranch`` is a mixin-class for all branch statements with a condition.
	"""
	def __init__(self):
		super().__init__()
		MixinConditional.__init__(self)


@export
class MixinIfBranch(MixinConditionalBranch):
	"""
	A ``BaseIfBranch`` is a mixin-class for all if-branches.
	"""


@export
class MixinElsifBranch(MixinConditionalBranch):
	"""
	A ``BaseElsifBranch`` is a mixin-class for all elsif-branches.
	"""


@export
class MixinElseBranch(MixinBranch):
	"""
	A ``BaseElseBranch`` is a mixin-class for all else-branches.
	"""


@export
class GenerateBranch(ModelEntity, ConcurrentDeclarations, ConcurrentStatements):
	"""
	A ``GenerateBranch`` is a base-class for all branches in a generate statements.
	"""

	def __init__(self):
		super().__init__()
		ConcurrentDeclarations.__init__(self)
		ConcurrentStatements.__init__(self)


@export
class IfGenerateBranch(GenerateBranch, MixinIfBranch):
	def __init__(self):
		super().__init__()
		MixinIfBranch.__init__(self)


@export
class ElsifGenerateBranch(GenerateBranch, MixinElsifBranch):
	def __init__(self):
		super().__init__()
		MixinElsifBranch.__init__(self)


@export
class ElseGenerateBranch(GenerateBranch, MixinElseBranch):
	def __init__(self):
		super().__init__()
		MixinElseBranch.__init__(self)


@export
class GenerateStatement(ConcurrentStatement):
	"""
	A ``GenerateStatement`` is a base-class for all generate statements.
	"""

	def __init__(self, label: str = None):
		super().__init__(label=label)


@export
class IfGenerateStatement(GenerateStatement):
	_ifBranch:      IfGenerateBranch
	_elsifBranches: List[ElsifGenerateBranch]
	_elseBranch:    ElseGenerateBranch

	def __init__(self, label: str = None):
		super().__init__(label=label)

		self._elsifBranches = []

	@property
	def IfBranch(self) -> IfGenerateBranch:
		return self._ifBranch

	@property
	def ElsifBranches(self) -> List[ElsifGenerateBranch]:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> ElseGenerateBranch:
		return self._elseBranch


@export
class Choice(ModelEntity):
	"""
	A ``Choice`` is a base-class for all choices.
	"""


@export
class Case(ModelEntity):
	"""
	A ``Case`` is a base-class for all cases.
	"""


@export
class ConcurrentCase(Case, LabeledEntity, ConcurrentDeclarations, ConcurrentStatements):
	_choices: List

	def __init__(self, label: str = None):
		super().__init__()
		LabeledEntity.__init__(self, label)
		ConcurrentDeclarations.__init__(self)
		ConcurrentStatements.__init__(self)

	@property
	def Choises(self) -> List[Choice]:
		return self._choices


@export
class SequentialCase(Case, SequentialStatements):
	_choices: List

	def __init__(self):
		super().__init__()
		SequentialStatements.__init__(self)

	@property
	def Choises(self) -> List[Choice]:
		return self._choices


@export
class CaseGenerateStatement(GenerateStatement):
	_selectExpression: Expression
	_cases:            List[ConcurrentCase]

	@property
	def SelectExpression(self) -> Expression:
		return self._selectExpression

	@property
	def Cases(self) -> List[ConcurrentCase]:
		return self._cases


@export
class ForGenerateStatement(GenerateStatement, ConcurrentDeclarations, ConcurrentStatements):
	_loopIndex: Constant
	_range:     Range

	def __init__(self, label: str = None):
		super().__init__(label=label)
		ConcurrentDeclarations.__init__(self)
		ConcurrentStatements.__init__(self)

	@property
	def LoopIndex(self) -> Constant:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range


@export
class Assignment:
	"""
	An ``Assignment`` is a base-class for all assignment statements.
	"""

	_target:     Object
	_expression: Expression

	def __init__(self):
		super().__init__()

	@property
	def Target(self) -> Object:
		return self._target

	@property
	def Expression(self) -> Expression:
		return self._expression


@export
class SignalAssignment(Assignment):
	"""
	An ``SignalAssignment`` is a base-class for all signal assignment statements.
	"""


@export
class VariableAssignment(Assignment):
	"""
	An ``VariableAssignment`` is a base-class for all variable assignment statements.
	"""


@export
class ConcurrentSignalAssignment(ConcurrentStatement, SignalAssignment):
	def __init__(self, label: str = None):
		super().__init__(label=label)
		SignalAssignment.__init__(self)


@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignment):
	def __init__(self):
		super().__init__()
		SignalAssignment.__init__(self)


@export
class SequentialVariableAssignment(SequentialStatement, VariableAssignment):
	def __init__(self):
		super().__init__()
		VariableAssignment.__init__(self)


@export
class MixinReportStatement:
	"""
	A ``MixinReportStatement`` is a mixin-class for all report and assert statements.
	"""
	_message:  Expression
	_severity: Expression

	def __init__(self):
		super().__init__()

	@property
	def Message(self) -> Expression:
		return self._message

	@property
	def Severity(self) -> Expression:
		return self._severity


@export
class MixinAssertStatement(MixinReportStatement):
	"""
	A ``MixinAssertStatement`` is a mixin-class for all assert statements.
	"""
	_condition: Expression

	def __init__(self):
		super().__init__()

	@property
	def Condition(self) -> Expression:
		return self._condition


@export
class ConcurrentAssertStatement(ConcurrentStatement, MixinAssertStatement):
	def __init__(self, label: str = None):
		super().__init__(label=label)
		MixinAssertStatement.__init__(self)


@export
class SequentialReportStatement(SequentialStatement, MixinReportStatement):
	def __init__(self):
		super().__init__()
		MixinReportStatement.__init__(self)


@export
class SequentialAssertStatement(SequentialStatement, MixinAssertStatement):
	def __init__(self):
		super().__init__()
		MixinAssertStatement.__init__(self)


@export
class Branch(ModelEntity, SequentialStatements):
	"""
	A ``Branch`` is a base-class for all branches.
	"""

	def __init__(self):
		super().__init__()
		SequentialStatements.__init__(self)


@export
class IfBranch(Branch, MixinIfBranch):
	def __init__(self):
		super().__init__()
		MixinIfBranch.__init__(self)


@export
class ElsifBranch(Branch, MixinElsifBranch):
	def __init__(self):
		super().__init__()
		MixinElsifBranch.__init__(self)


@export
class ElseBranch(Branch, MixinElseBranch):
	def __init__(self):
		super().__init__()
		MixinElseBranch.__init__(self)


@export
class CompoundStatement(SequentialStatement):
	"""
	A ``CompoundStatement`` is a base-class for all compound statements.
	"""

	def __init__(self):
		super().__init__()


@export
class IfStatement(CompoundStatement):
	_ifBranch: IfBranch
	_elsifBranches: List['ElsifBranch']
	_elseBranch: ElseBranch

	def __init__(self):
		super().__init__()

		self._elsifBranches = []

	@property
	def IfBranch(self) -> IfBranch:
		return self._ifBranch

	@property
	def ElsIfBranches(self) -> List['ElsifBranch']:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> ElseBranch:
		return self._elseBranch


@export
class CaseStatement(CompoundStatement):
	_selectExpression: Expression
	_cases:            List[SequentialCase]

	@property
	def SelectExpression(self) -> Expression:
		return self._selectExpression

	@property
	def Cases(self) -> List[SequentialCase]:
		return self._cases


@export
class LoopStatement(CompoundStatement, SequentialStatements):
	"""
	A ``LoopStatement`` is a base-class for all loop statements.
	"""

	def __init__(self):
		super().__init__()
		SequentialStatements.__init__(self)


@export
class EndlessLoopStatement(LoopStatement):
	pass


@export
class ForLoopStatement(LoopStatement):
	_loopIndex: Constant
	_range:     Range

	def __init__(self):
		super().__init__()

	@property
	def LoopIndex(self) -> Constant:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range


@export
class WhileLoopStatement(LoopStatement, MixinConditional):
	def __init__(self):
		super().__init__()
		MixinConditional.__init__(self)


@export
class LoopControlStatement(SequentialStatement, MixinConditional):
	"""
	A ``LoopControlStatement`` is a base-class for all loop controlling statements.
	"""
	_loopReference: LoopStatement

	def __init__(self):
		super().__init__()
		MixinConditional.__init__(self)

	@property
	def LoopReference(self) -> LoopStatement:
		return self._loopReference


@export
class NextStatement(LoopControlStatement):
	pass


@export
class ExitStatement(LoopControlStatement):
	pass


@export
class WaitStatement(SequentialStatement, MixinConditional):
	_sensitivityList : List[Signal]
	_timeout:          Expression

	def __init__(self):
		super().__init__()
		MixinConditional.__init__(self)

	@property
	def SensitivityList(self) -> List[Signal]:
		return self._sensitivityList

	@property
	def Timeout(self) -> Expression:
		return self._timeout


@export
class ReturnStatement(SequentialStatement, MixinConditional):
	_returnValue: Expression

	def __init__(self):
		super().__init__()
		MixinConditional.__init__(self)

	@property
	def ReturnValue(self) -> Expression:
		return self._returnValue
