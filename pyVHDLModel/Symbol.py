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

Symbols are entity specific wrappers for names that reference VHDL language entities.
"""
from __future__            import annotations

from enum                  import Flag, auto
from typing                import Any, Optional as Nullable, Iterable, List, Dict, Mapping

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType

from pyVHDLModel.Base      import Range
from pyVHDLModel.Name      import Name, AllName


@export
class PossibleReference(Flag):
	"""
	Is an enumeration, representing possible targets for a reference in a :class:`~pyVHDLModel.Symbol.Symbol`.
	"""

	Unknown =         0
	Library =         auto()  #: Library
	Entity =          auto()  #: Entity
	Architecture =    auto()  #: Architecture
	Component =       auto()  #: Component
	Package =         auto()  #: Package
	Configuration =   auto()  #: Configuration
	Context =         auto()  #: Context
	Type =            auto()  #: Type
	Subtype =         auto()  #: Subtype
	ScalarType =      auto()  #: ScalarType
	ArrayType =       auto()  #: ArrayType
	RecordType =      auto()  #: RecordType
	RecordElement =   auto()  #: RecordElement
	AccessType =      auto()  #: AccessType
	ProtectedType =   auto()  #: ProtectedType
	FileType =        auto()  #: FileType
#	Alias =           auto()   # TODO: Is this needed?
	Attribute =       auto()  #: Attribute
	TypeAttribute =   auto()  #: TypeAttribute
	ValueAttribute =  auto()  #: ValueAttribute
	SignalAttribute = auto()  #: SignalAttribute
	RangeAttribute =  auto()  #: RangeAttribute
	ViewAttribute =   auto()  #: ViewAttribute
	Constant =        auto()  #: Constant
	Variable =        auto()  #: Variable
	Signal =          auto()  #: Signal
	File =            auto()  #: File
#	Object =          auto()   # TODO: Is this needed?
	EnumLiteral =     auto()  #: EnumLiteral
	Procedure =       auto()  #: Procedure
	Function =        auto()  #: Function
	Label =           auto()  #: Label
	View =            auto()  #: View

	AnyType = ScalarType | ArrayType | RecordType | ProtectedType | AccessType | FileType | Subtype  #: Any possible type incl. subtypes.
	Object = Constant | Variable | Signal  # | File                                                     #: Any object
	SubProgram = Procedure | Function                                                                #: Any subprogram
	PackageMember = AnyType | Object | SubProgram | Component                                        #: Any member of a package
	SimpleNameInExpression = Constant | Variable | Signal | ScalarType | EnumLiteral | Function      #: Any possible item in an expression.


# QUESTION: Why is it not a ModelEntity?
@export
class Symbol(metaclass=ExtendedType):
	"""
	Base-class for all symbol classes.
	"""

	_name:               Name               #: The name to reference the language entity.
	_possibleReferences: PossibleReference  #: An enumeration to filter possible references.
	_reference:          Nullable[Any]      #: The resolved language entity, otherwise ``None``.

	def __init__(self, name: Name, possibleReferences: PossibleReference) -> None:
		"""
		Initializes a symbol.

		:param name:               The name to reference the language entity.
		:param possibleReferences: An enumeration to filter possible references.
		"""
		self._name = name
		self._possibleReferences = possibleReferences
		self._reference = None

	@readonly
	def Name(self) -> Name:
		"""
		Read-only property to access the name (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	@readonly
	def Reference(self) -> Nullable[Any]:
		"""
		Read-only property to access the reference (:attr:`_reference`).

		:returns: The reference, or ``None`` if not set.
		"""
		return self._reference

	@readonly
	def IsResolved(self) -> bool:
		"""
		Check if the symbol is resolved, i.e. :attr:`_reference` is set.

		:returns: ``True``, if the symbol is resolved.
		"""
		return self._reference is not None

	def __bool__(self) -> bool:
		"""
		Reports whether this symbol has been resolved.

		:returns: ``True`` if the symbol references a model entity.
		"""
		return self._reference is not None

	def __repr__(self) -> str:
		"""
		Formats a representation of the symbol.

		**Format:** ``SignalSymbol: 'clk' -> <signal>``, or ``... -> ?`` while unresolved

		:returns: String representation of the symbol.
		"""
		if self._reference is not None:
			return f"{self.__class__.__name__}: '{self._name!s}' -> {self._reference!s}"

		return f"{self.__class__.__name__}: '{self._name!s}' -> unresolved"

	def __str__(self) -> str:
		"""
		Formats the symbol.

		**Format:** the referenced model entity once resolved, else the name plus ``?``

		:returns: Formatted symbol.
		"""
		if self._reference is not None:
			return str(self._reference)

		return f"{self._name!s}?"


@export
class LibraryReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a library.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      library ieee;
	      --      ^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to a library.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Library)

	@property
	def Library(self) -> Nullable[Library]:
		"""
		Property to access the library (:attr:`_reference`).

		:returns: The library, or ``None`` if not set.
		"""
		return self._reference

	@Library.setter
	def Library(self, value: Library) -> None:
		self._reference = value


@export
class PackageReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a package.

	The internal name will be a :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std;
	      --  ^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to a package.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Package)

	@property
	def Package(self) -> Nullable[Package]:
		"""
		Property to access the package (:attr:`_reference`).

		:returns: The package, or ``None`` if not set.
		"""
		return self._reference

	@Package.setter
	def Package(self, value: Package) -> None:
		self._reference = value


@export
class ModeViewSymbol(Symbol):
	"""
	Represents a reference to a mode view (VHDL-2019).

	The referenced mode view is available as :data:`Reference` once resolved. A reference may also
	select the converse view.

	.. admonition:: Example

	   Referencing a mode view:

	   .. code-block:: VHDL

	      port (p : view MasterView);
	      --             ^^^^^^^^^^     <- Name

	   Referencing its converse:

	   .. code-block:: VHDL

	      port (p : view MasterView'converse);
	      --             ^^^^^^^^^^^^^^^^^^^     <- Name
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference to a mode view (VHDL-2019).

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.View)

	@property
	def ModeView(self) -> Nullable[ModeViewDeclaration]:
		"""
		Property to access the mode view (:attr:`_reference`).

		:returns: The mode view, or ``None`` if not set.
		"""
		return self._reference

	@ModeView.setter
	def ModeView(self, value: ModeViewDeclaration) -> None:
		self._reference = value


@export
class SubprogramReferenceSymbol(Symbol):
	"""
	Represents a reference to a subprogram.

	The referenced subprogram is available as :data:`Reference` once resolved.

	.. admonition:: Example

	   .. code-block:: VHDL

	      function f is new gen_fun generic map (N => 1);
	      --                ^^^^^^^                         <- Name
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference to a subprogram.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.SubProgram)

	@property
	def Subprogram(self) -> Nullable[Subprogram]:
		"""
		Property to access the subprogram (:attr:`_reference`).

		:returns: The subprogram, or ``None`` if not set.
		"""
		return self._reference

	@Subprogram.setter
	def Subprogram(self, value: Subprogram) -> None:
		self._reference = value


@export
class ConfigurationSymbol(Symbol):
	"""
	Represents a reference to a configuration.

	The referenced configuration is available as :data:`Reference` once resolved.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use configuration work.cfg;
	      --                              ^^^^^^^^    <- Name
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference to a configuration.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Configuration)

	@property
	def Configuration(self) -> Nullable[Configuration]:
		"""
		Property to access the configuration (:attr:`_reference`).

		:returns: The configuration, or ``None`` if not set.
		"""
		return self._reference

	@Configuration.setter
	def Configuration(self, value: Configuration) -> None:
		self._reference = value


@export
class VariableSymbol(Symbol):
	"""
	Represents a reference (name) to a variable, e.g. the target of a variable assignment.

	.. admonition:: Example

	   .. code-block:: VHDL

	      v := '1';
	      --^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a variable symbol.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Variable)

	@property
	def Variable(self) -> Nullable[Variable]:
		"""
		Property to access the variable (:attr:`_reference`).

		:returns: The variable, or ``None`` if not set.
		"""
		return self._reference

	@Variable.setter
	def Variable(self, value: Variable) -> None:
		self._reference = value


@export
class SignalSymbol(Symbol):
	"""
	Represents a reference (name) to a signal, e.g. the target of a signal assignment.

	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= '1';
	      --^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a signal symbol.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Signal)

	@property
	def Signal(self) -> Nullable[Signal]:
		"""
		Property to access the signal (:attr:`_reference`).

		:returns: The signal, or ``None`` if not set.
		"""
		return self._reference

	@Signal.setter
	def Signal(self, value: Signal) -> None:
		self._reference = value


@export
class ContextReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a context.

	The internal name will be a :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      context ieee.ieee_std_context;
	      --      ^^^^^^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to a context.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Context)

	@property
	def Context(self) -> Context:
		"""
		Property to access the context (:attr:`_reference`).

		:returns: The context.
		"""
		return self._reference

	@Context.setter
	def Context(self, value: Context) -> None:
		self._reference = value


@export
class PackageMemberReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to a package member.

	The internal name will be a :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std.unsigned;
	      --  ^^^^^^^^^^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to a package member.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.PackageMember)

	@property
	def Member(self) -> Nullable[Package]:  # TODO: typehint
		"""
		Property to access the member (:attr:`_reference`).

		:returns: The member, or ``None`` if not set.
		"""
		return self._reference

	@Member.setter
	def Member(self, value: Package) -> None:  # TODO: typehint
		self._reference = value


@export
class AllPackageMembersReferenceSymbol(Symbol):
	"""
	Represents a reference (name) to all package members.

	The internal name will be a :class:`~pyVHDLModel.Name.AllName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      use ieee.numeric_std.all;
	      --  ^^^^^^^^^^^^^^^^^^^^
	"""

	def __init__(self, name: AllName) -> None:
		"""
		Initializes a reference (name) to all package members.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.PackageMember)

	@property
	def Members(self) -> Package:  # TODO: typehint
		"""
		Property to access the members (:attr:`_reference`).

		:returns: The members.
		"""
		return self._reference

	@Members.setter
	def Members(self, value: Package) -> None:  # TODO: typehint
		self._reference = value


@export
class EntityInstantiationSymbol(Symbol):
	"""
	Represents a reference (name) to an entity in a direct entity instantiation.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	    .. code-block:: VHDL

	       inst : entity work.Counter;
	       --            ^^^^^^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to an entity in a direct entity instantiation.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Entity)

	@property
	def Entity(self) -> Entity:
		"""
		Property to access the entity (:attr:`_reference`).

		:returns: The entity.
		"""
		return self._reference

	@Entity.setter
	def Entity(self, value: Entity) -> None:
		self._reference = value


@export
class ComponentInstantiationSymbol(Symbol):
	"""
	Represents a reference (name) to an entity in a component instantiation.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	    .. code-block:: VHDL

	       inst : component Counter;
	       --               ^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to an entity in a component instantiation.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Component)

	@property
	def Component(self) -> Component:
		"""
		Property to access the component (:attr:`_reference`).

		:returns: The component.
		"""
		return self._reference

	@Component.setter
	def Component(self, value: Component) -> None:
		self._reference = value


@export
class ConfigurationInstantiationSymbol(Symbol):
	"""
	Represents a reference (name) to an entity in a configuration instantiation.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	    .. code-block:: VHDL

	       inst : configuration Counter;
	       --                   ^^^^^^^
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to an entity in a configuration instantiation.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Configuration)

	@property
	def Configuration(self) -> Configuration:
		"""
		Property to access the configuration (:attr:`_reference`).

		:returns: The configuration.
		"""
		return self._reference

	@Configuration.setter
	def Configuration(self, value: Configuration) -> None:
		self._reference = value


@export
class EntitySymbol(Symbol):
	"""
	Represents a reference (name) to an entity in an architecture declaration.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      architecture rtl of Counter is
	      --                  ^^^^^^^
	      begin
	      end architecture;
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to an entity in an architecture declaration.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Entity)

	@property
	def Entity(self) -> Entity:
		"""
		Property to access the entity (:attr:`_reference`).

		:returns: The entity.
		"""
		return self._reference

	@Entity.setter
	def Entity(self, value: Entity) -> None:
		self._reference = value


@export
class ArchitectureSymbol(Symbol):
	"""An entity reference in an entity instantiation with architecture name."""

	def __init__(self, name: Name) -> None:
		"""
		Initializes an architecture symbol.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Architecture)

	@property
	def Architecture(self) -> Architecture:
		"""
		Property to access the architecture (:attr:`_reference`).

		:returns: The architecture.
		"""
		return self._reference

	@Architecture.setter
	def Architecture(self, value: Architecture) -> None:
		self._reference = value


@export
class PackageSymbol(Symbol):
	"""
	Represents a reference (name) to a package in a package body declaration.

	The internal name will be a :class:`~pyVHDLModel.Name.SimpleName` or :class:`~pyVHDLModel.Name.SelectedName`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      package body Utilities is
	      --           ^^^^^^^^^
	      end package body;
	"""

	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference (name) to a package in a package body declaration.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Package)

	@property
	def Package(self) -> Package:
		"""
		Property to access the package (:attr:`_reference`).

		:returns: The package.
		"""
		return self._reference

	@Package.setter
	def Package(self, value: Package) -> None:
		self._reference = value


@export
class RecordElementSymbol(Symbol):
	"""
	Represents a reference to a record element.

	The referenced language entity is available as :data:`Reference` once resolved.

	.. admonition:: Example

	   .. code-block:: VHDL

	      r := (a => '1', b => '0');
	      --    ^                      <- Name
	"""
	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference to a record element.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.RecordElement)


@export
class RangeAttributeSymbol(Symbol):
	"""A symbol referencing a range attribute, e.g. ``vector'range``."""

	def __init__(self, name: Name) -> None:
		"""
		Initialize a range attribute symbol.

		:param name: The attribute name referencing the range.
		"""
		super().__init__(name, PossibleReference.RangeAttribute)


@export
class SubtypeSymbol(Symbol):
	"""
	Represents the base-class of all references to a type or subtype.

	The referenced language entity is available as :data:`Reference` once resolved.

	.. seealso::

	   * :class:`Simple subtype symbol <pyVHDLModel.Symbol.SimpleSubtypeSymbol>`
	   * :class:`Constrained scalar subtype symbol <pyVHDLModel.Symbol.ConstrainedScalarSubtypeSymbol>`
	   * :class:`Constrained composite subtype symbol <pyVHDLModel.Symbol.ConstrainedCompositeSubtypeSymbol>`
	"""
	def __init__(self, name: Name) -> None:
		"""
		Initializes a subtype symbol.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.Type | PossibleReference.Subtype)

	@property
	def Subtype(self) -> Subtype:
		"""
		Property to access the subtype (:attr:`_reference`).

		:returns: The subtype.
		"""
		return self._reference

	@Subtype.setter
	def Subtype(self, value: Subtype) -> None:
		self._reference = value


@export
class SimpleSubtypeSymbol(SubtypeSymbol):
	"""
	Represents a reference to a type or subtype by its type mark.

	The referenced language entity is available as :data:`Reference` once resolved.

	.. admonition:: Example

	   .. code-block:: VHDL

	      signal s : bit := '0';
	      --         ^^^           <- Name
	"""
	pass


@export
class Constraint(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for symbols carrying a constraint.

	.. seealso::

	   * :class:`Scalar constraint <pyVHDLModel.Symbol.ScalarConstraint>`
	   * :class:`Array constraint <pyVHDLModel.Symbol.ArrayConstraint>`
	   * :class:`Record constraint <pyVHDLModel.Symbol.RecordConstraint>`
	"""
	pass


@export
class ScalarConstraint(Constraint, mixin=True):
	"""
	A mixin-class for a scalar constraint: a range.

	The range is available as :data:`Constraint`.

	.. seealso::

	   * :class:`Constrained scalar subtype symbol <pyVHDLModel.Symbol.ConstrainedScalarSubtypeSymbol>`
	"""
	_constraint: Range  #: The range constraining the scalar subtype.

	def __init__(self, constraint: Range) -> None:
		"""
		Initializes a scalar constraint.

		:param constraint: The range constraining the scalar subtype.
		"""
		self._constraint = constraint

	@readonly
	def Constraint(self) -> Range:
		"""
		Read-only property to access the scalar type's range constraint (:attr:`_constraint`).

		:returns: The constraint of the scalar subtype.
		"""
		return self._constraint


@export
class ConstrainedScalarSubtypeSymbol(SubtypeSymbol, ScalarConstraint):
	"""
	Represents a reference to a scalar subtype narrowed by a range.

	The referenced language entity is available as :data:`Reference` once resolved. The range is
	mandatory: a type mark without a range constraint is a :class:`~pyVHDLModel.Symbol.SimpleSubtypeSymbol`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for i in integer range 0 to 3 loop
	      --       ^^^^^^^                     <- Name
	      --                     ^^^^^^        <- Constraint

	   A range constraint written as a range attribute is a :class:`~pyVHDLModel.Base.RangeFromName`
	   referring to a :class:`~pyVHDLModel.Symbol.RangeAttributeSymbol`:

	   .. code-block:: VHDL

	      subtype index is natural range vector'range;
	      --               ^^^^^^^                      <- Name
	      --                             ^^^^^^^^^^^^   <- Constraint
	"""

	def __init__(self, name: Name, constraint: Range) -> None:
		"""
		Initializes a reference to a scalar subtype narrowed by a range.

		:param name:       The name to reference the language entity.
		:param constraint: The range constraining the scalar subtype.
		"""
		super().__init__(name)
		ScalarConstraint.__init__(self, constraint)


@export
class ArrayConstraint(Constraint, mixin=True):
	"""
	A mixin-class for an array constraint: one range per dimension.

	The ranges are available as :data:`Constraints`.

	.. seealso::

	   * :class:`Constrained array subtype symbol <pyVHDLModel.Symbol.ConstrainedArraySubtypeSymbol>`
	"""
	_constraints: List[Range]  #: List of all index ranges, one per dimension.

	def __init__(self, constraints: Iterable[Range]) -> None:
		"""
		Initializes an array constraint.

		:param constraints: List of all index ranges, one per dimension.
		"""
		self._constraints = [constraint for constraint in constraints]

	@readonly
	def Constraints(self) -> List[Range]:
		"""
		Read-only property to access the constraints (:attr:`_constraints`).

		:returns: List of constraints.
		"""
		return self._constraints


@export
class RecordConstraint(Constraint, mixin=True):
	"""
	A mixin-class for a record constraint: one constraint per element.

	The constraints are available as :data:`Constraints`.

	.. seealso::

	   * :class:`Constrained record subtype symbol <pyVHDLModel.Symbol.ConstrainedRecordSubtypeSymbol>`
	"""
	_constraints: Dict[RecordElementSymbol, Range]  #: Dictionary of the constraint per constrained record element.

	def __init__(self, constraints: Mapping[RecordElementSymbol, Range]) -> None:
		"""
		Initializes a record constraint.

		:param constraints: Dictionary of the constraint per constrained record element.
		"""
		self._constraints = {key: value for key, value in constraints.items()}

	@readonly
	def Constraints(self) -> Dict[RecordElementSymbol, Range]:
		"""
		Read-only property to access the constraints (:attr:`_constraints`).

		:returns: Dictionary of constraints.
		"""
		return self._constraints


@export
class ConstrainedCompositeSubtypeSymbol(SubtypeSymbol):
	"""
	Represents the base-class of references to constrained composite subtypes.

	The referenced language entity is available as :data:`Reference` once resolved.

	.. seealso::

	   * :class:`Constrained array subtype symbol <pyVHDLModel.Symbol.ConstrainedArraySubtypeSymbol>`
	   * :class:`Constrained record subtype symbol <pyVHDLModel.Symbol.ConstrainedRecordSubtypeSymbol>`
	"""
	pass


@export
class ConstrainedArraySubtypeSymbol(ConstrainedCompositeSubtypeSymbol, ArrayConstraint):
	"""
	Represents a reference to an array subtype narrowed by index ranges.

	The referenced language entity is available as :data:`Reference` once resolved.

	.. admonition:: Example

	   .. code-block:: VHDL

	      signal v : bit_vector(7 downto 0);
	      --         ^^^^^^^^^^                <- Name
	      --                    ^^^^^^^^^^     <- Constraints
	"""
	_constraints: List  #: List of all index ranges, one per dimension.

	def __init__(self, name: Name, constraints: Iterable) -> None:
		"""
		Initializes a reference to an array subtype narrowed by index ranges.

		:param name:        The name to reference the language entity.
		:param constraints: List of all index ranges, one per dimension.
		"""
		super().__init__(name)
		ArrayConstraint.__init__(self, constraints)


@export
class ConstrainedRecordSubtypeSymbol(ConstrainedCompositeSubtypeSymbol, RecordConstraint):
	"""
	Represents a reference to a record subtype with constrained elements.

	The referenced language entity is available as :data:`Reference` once resolved.
	"""
	_constraints: Dict[RecordElementSymbol, Any]  #: Dictionary of the constraint per constrained record element.

	def __init__(self, name: Name, constraints: Mapping) -> None:
		"""
		Initializes a reference to a record subtype with constrained elements.

		:param name:        The name to reference the language entity.
		:param constraints: Dictionary of the constraint per constrained record element.
		"""
		super().__init__(name)
		RecordConstraint.__init__(self, constraints)


@export
class SimpleObjectOrFunctionCallSymbol(Symbol):
	"""
	Represents a reference that is either an object or a parameterless function call.

	Which of the two it is cannot be decided before the name is resolved. The referenced language
	entity is available as :data:`Reference` once resolved.
	"""
	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference that is either an object or a parameterless function call.

		:param name: The name to reference the language entity.
		"""
		super().__init__(name, PossibleReference.SimpleNameInExpression)


@export
class IndexedObjectOrFunctionCallSymbol(Symbol):
	"""
	Represents a reference that is either an indexed object, a function call or a type conversion.

	The referenced language entity is available as :data:`Reference` once resolved.

	.. attention::

	   All three are written the same way - ``arr(0)``, ``f(0)`` and ``integer(0)`` are indistinguishable
	   as syntax, so a parser produces one shape for them and only name resolution tells them apart.

	.. seealso::

	   * :class:`Type conversion <pyVHDLModel.Expression.TypeConversion>`
	   * :class:`Simple object or function call <pyVHDLModel.Symbol.SimpleObjectOrFunctionCallSymbol>`
	"""
	def __init__(self, name: Name) -> None:
		"""
		Initializes a reference that is either an indexed object, a function call or a type conversion.

		:param name: The name to reference the language entity.
		"""
		super().__init__(
			name,
			PossibleReference.Object | PossibleReference.Function | PossibleReference.Type | PossibleReference.Subtype
		)
