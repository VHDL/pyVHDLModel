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

Interface items are used in generic, port and parameter declarations.
"""
from __future__             import annotations

from typing                 import TYPE_CHECKING, Iterable, Optional as Nullable, Iterator, Self

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType, abstractclass, expects

from pyVHDLModel.Symbol     import Symbol, SubtypeSymbol, ModeViewSymbol
from pyVHDLModel.Base       import ModelEntity, DocumentedEntityMixin, NamedEntityMixin, OptionallyNamedEntityMixin, \
                                   MultipleNamedEntityMixin, identifiersOf, normalizedIdentifiersOf, ExpressionUnion, \
                                   Mode
from pyVHDLModel.Object     import Constant, Signal, Variable, File
from pyVHDLModel.Regions    import WithGenericsMixin, WithPortsMixin, WithParametersMixin
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Type       import Type

if TYPE_CHECKING:
	from pyVHDLModel.Visitor  import Visitor


@export
@abstractclass
class ModeViewElement(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	"""
	Base-class for one element definition inside a mode view declaration (VHDL-2019).

	An element may name several fields sharing the same specification (e.g. ``a, b : out;``), hence
	:class:`~pyVHDLModel.Base.MultipleNamedEntityMixin` is inherited.

	.. seealso::

	   * :class:`Simple mode view element <pyVHDLModel.Interface.SimpleModeViewElement>`
	   * :class:`Composite mode view element <pyVHDLModel.Interface.CompositeModeViewElement>`
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a mode view element.

		:param identifiers:   A list of identifiers.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

	def __str__(self) -> str:
		"""
		Formats the mode view element as its identifiers.

		**Format:** ``a, b``

		:returns: The element's identifiers, comma-separated.
		"""
		return ", ".join(self._identifiers)


@export
class SimpleModeViewElement(ModeViewElement):
	"""
	A mode view element with a plain (simple) mode.

	.. admonition:: Example

	   .. code-block:: VHDL

	      view MyView of RecordType is
	        a, b : out;
	        --     ^^^
	      end view;
	"""

	_mode: Mode  #: The element's mode.

	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a simple mode view element.

		:param identifiers:   A list of identifiers.
		:param mode:          The element's mode.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifiers, documentation, parent)
		self._mode = mode

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this simple mode view element with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSimpleModeViewElement(self)
		visitor.DepartSimpleModeViewElement(self)

	@readonly
	def Mode(self) -> Mode:
		"""
		Read-only property to access the mode (:attr:`_mode`).

		:returns: The mode.
		"""
		return self._mode

	def Copy(self) -> Self:
		"""
		Create a copy of this simple mode view element.

		The copy has no parent.

		:returns: The new simple mode view element.
		"""
		return self.__class__(self._identifiers, self._mode, self._documentation)


@export
class CompositeModeViewElement(ModeViewElement):
	"""
	A mode view element that refers to another (named) mode view for an array or record sub-element.
	.. admonition:: Example

	   .. code-block:: VHDL

	      view OuterView of OuterRecord is
	        b : view InnerView;
	        --       ^^^^^^^^^
	      end view;
	"""

	_modeViewName: ModeViewSymbol  #: Reference to the mode view applied to this element.

	def __init__(
		self,
		identifiers: Iterable[str],
		modeViewName: ModeViewSymbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a composite mode view element.

		:param identifiers:   A list of identifiers.
		:param modeViewName:  Reference to the mode view applied to this element.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifiers, documentation, parent)

		self._modeViewName = modeViewName
		modeViewName.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this composite mode view element and its mode view name with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitCompositeModeViewElement(self)
		self._modeViewName.Visit(visitor)
		visitor.DepartCompositeModeViewElement(self)

	@readonly
	def ModeViewName(self) -> ModeViewSymbol:
		"""
		Read-only property to access the mode view name (:attr:`_modeViewName`).

		:returns: The mode view name.
		"""
		return self._modeViewName

	def Copy(self) -> Self:
		"""
		Create a copy of this composite mode view element.

		The copy has no parent. Its mode view name is a copy of this element's mode view name.

		:returns: The new composite mode view element.
		"""
		return self.__class__(self._identifiers, self._modeViewName.Copy(), self._documentation)


@export
class ModeViewDeclaration(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a mode view declaration (VHDL-2019).

	.. admonition:: Example

	   .. code-block:: VHDL

	      view MyView of RecordType is
	        a : out;
	        b : in;
	      end view;

	.. seealso::

	   * :class:`Port declared with a mode view <pyVHDLModel.Interface.PortViewSignalInterfaceItem>`
	   * :class:`Parameter declared with a mode view <pyVHDLModel.Interface.ParameterViewSignalInterfaceItem>`
	   * :class:`Reference to a mode view <pyVHDLModel.Symbol.ModeViewSymbol>`
	"""

	_subtype:  SubtypeSymbol          #: Reference to the subtype this mode view applies to.
	_elements: list[ModeViewElement]  #: List of all mode view elements, in declaration order.

	def __init__(
		self,
		identifier:    str,
		subtype:       SubtypeSymbol,
		elements:      Nullable[Iterable[ModeViewElement]] = None,
		documentation: Nullable[str] =                        None,
		parent:        Nullable[ModelEntity] =                None
	) -> None:
		"""
		Initializes a mode view declaration (VHDL-2019).

		:param identifier:    The identifier of a model entity.
		:param subtype:       Reference to the subtype this mode view applies to.
		:param elements:      List of all mode view elements, in declaration order.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype.Parent = self

		self._elements = []
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this mode view declaration, its subtype and its elements with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitModeViewDeclaration(self)
		self._subtype.Visit(visitor)
		visitor.VisitIs(self)
		for element in self._elements:
			element.Visit(visitor)

		visitor.DepartModeViewDeclaration(self)

	@readonly
	def Subtype(self) -> SubtypeSymbol:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	@readonly
	def Elements(self) -> list[ModeViewElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements

	def __str__(self) -> str:
		"""
		Formats the mode view declaration.

		**Format:** ``view myView of myRecord: a, b``

		:returns: Formatted mode view declaration.
		"""
		elements = ", ".join(str(element) for element in self._elements)
		return f"view {self._identifier} of {self._subtype}: {elements}"


@export
class InterfaceItemMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class marking a declaration as an interface item.

	Interface items appear in generic clauses, port clauses and parameter lists.

	.. seealso::

	   * :class:`Generic interface item mixin <pyVHDLModel.Interface.GenericInterfaceItemMixin>`
	   * :class:`Port interface item mixin <pyVHDLModel.Interface.PortInterfaceItemMixin>`
	   * :class:`Parameter interface item mixin <pyVHDLModel.Interface.ParameterInterfaceItemMixin>`
	   * :class:`Port signal interface item <pyVHDLModel.Interface.PortSignalInterfaceItem>`
	"""

	@expects("_OBJECT_KEYWORD", "_identifiers", "_subtype")
	def _FormatInterfaceItem(self, mode: Nullable[Mode] = None, isModeView: bool = False) -> str:
		"""
		Format this interface item as a single-line declaration.

		Interface items are objects, so they render like one (``signal p : bit``), but an object's own
		rendering cannot show the interface *mode* - a mode is not part of an object declaration. This
		adds it, for the derived class's :meth:`__str__` to return. The host class provides the object's reserved words
		``_OBJECT_KEYWORD``, identifiers ``_identifiers`` and subtype ``_subtype``.

		:param mode:       This item's mode, or ``None`` when it declares none.
		:param isModeView: ``True`` if the subtype position holds a mode view (VHDL-2019), not a subtype.
		:returns:          Formatted interface item.
		"""
		prefix = "" if mode is None or mode is Mode.Default else f"{mode!s} "
		if isModeView:
			prefix = "view "

		return f"{' '.join(self._OBJECT_KEYWORD)} {', '.join(self._identifiers)} : {prefix}{self._subtype}"


@export
class InterfaceItemWithModeMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for interface items declared with a mode.

	The mode is available as :data:`Mode`.

	.. seealso::

	   * :class:`Port interface item mixin <pyVHDLModel.Interface.PortInterfaceItemMixin>`
	   * :class:`Generic constant interface item <pyVHDLModel.Interface.GenericConstantInterfaceItem>`
	   * :class:`Port simple signal interface item <pyVHDLModel.Interface.PortSimpleSignalInterfaceItem>`
	   * :class:`Parameter constant interface item <pyVHDLModel.Interface.ParameterConstantInterfaceItem>`
	   * :class:`Parameter variable interface item <pyVHDLModel.Interface.ParameterVariableInterfaceItem>`
	   * :class:`Parameter simple signal interface item <pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem>`
	"""

	_mode: Mode  #: The interface item's mode.

	def __init__(self, mode: Mode) -> None:
		"""
		Initializes an interface item with mode.

		:param mode: The interface item's mode.
		"""
		self._mode = mode

	@readonly
	def Mode(self) -> Mode:
		"""
		Read-only property to access the mode (:attr:`_mode`).

		:returns: The mode.
		"""
		return self._mode


@export
class GenericInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""
	A mixin-class for all items in a generic clause.

	.. seealso::

	   * :class:`Generic constant interface item <pyVHDLModel.Interface.GenericConstantInterfaceItem>`
	   * :class:`Generic type interface item <pyVHDLModel.Interface.GenericTypeInterfaceItem>`
	   * :class:`Generic subprogram interface item mixin <pyVHDLModel.Interface.GenericSubprogramInterfaceItemMixin>`
	   * :class:`Generic package interface item <pyVHDLModel.Interface.GenericPackageInterfaceItem>`
	"""


@export
class GenericSubprogramInterfaceItemMixin(GenericInterfaceItemMixin, mixin=True):
	"""
	A mixin-class for subprograms in a generic clause.

	.. seealso::

	   * :class:`Generic procedure interface item <pyVHDLModel.Interface.GenericProcedureInterfaceItem>`
	   * :class:`Generic function interface item <pyVHDLModel.Interface.GenericFunctionInterfaceItem>`
	"""


@export
class PortInterfaceItemMixin(InterfaceItemMixin, InterfaceItemWithModeMixin, mixin=True):
	"""
	A mixin-class for all items in a port clause.
	"""

	def __init__(self, mode: Mode) -> None:
		"""
		Initializes a port interface item.

		:param mode: The interface item's mode.
		"""
		super().__init__()
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""
	A mixin-class for all items in a subprogram's parameter list.

	.. seealso::

	   * :class:`Parameter constant interface item <pyVHDLModel.Interface.ParameterConstantInterfaceItem>`
	   * :class:`Parameter variable interface item <pyVHDLModel.Interface.ParameterVariableInterfaceItem>`
	   * :class:`Parameter signal interface item <pyVHDLModel.Interface.ParameterSignalInterfaceItem>`
	   * :class:`Parameter file interface item <pyVHDLModel.Interface.ParameterFileInterfaceItem>`
	"""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItemMixin, InterfaceItemWithModeMixin):
	"""
	Represents a constant in a generic clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (W : positive := 8);
	      --       ^                     <- Identifiers
	      --           ^^^^^^^^          <- Subtype
	      --                       ^     <- DefaultExpression
	"""
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a constant in a generic clause.

		:param identifiers:       A list of identifiers.
		:param mode:              The interface item's mode.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)

	def Copy(self) -> Self:
		"""
		Create a copy of this generic constant.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this item's
		subtype and default expression.

		:returns: The new generic constant.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(
			self._identifiers,
			self._mode,
			self._subtype.Copy(),
			defaultExpression,
			self._documentation
		)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this generic constant, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitGenericConstantInterfaceItem(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.DepartGenericConstantInterfaceItem(self)

	def __str__(self) -> str:
		"""
		Formats the generic constant.

		**Format:** ``constant G : in positive``

		:returns: Formatted generic constant.
		"""
		return self._FormatInterfaceItem(self._mode)


@export
class GenericTypeInterfaceItem(Type, GenericInterfaceItemMixin):
	"""
	Represents a type in a generic clause.

	A generic type introduces a type name without defining the type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (type T);
	      --            ^     <- Identifier
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a type in a generic clause.

		:param identifier:    The identifier of a model entity.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)

	def Copy(self) -> Self:
		"""
		Create a copy of this generic type.

		The copy has no parent and no object vertex.

		:returns: The new generic type.
		"""
		return self.__class__(self._identifier, self._documentation)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this generic type with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitGenericTypeInterfaceItem(self)
		visitor.DepartGenericTypeInterfaceItem(self)


@export
class GenericProcedureInterfaceItem(Procedure, GenericSubprogramInterfaceItemMixin):
	"""
	Represents a procedure in a generic clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (procedure log(msg : string));
	      --                 ^^^                   <- Identifier
	      --                     ^^^^^^^^^^^^      <- ParameterItems
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a procedure in a generic clause.

		:param identifier:    The identifier of a model entity.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation=documentation, parent=parent)
		GenericSubprogramInterfaceItemMixin.__init__(self)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this generic procedure and its parameters with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitGenericProcedureInterfaceItem(self)
		self._VisitFormalParameterList(visitor)
		visitor.DepartGenericProcedureInterfaceItem(self)

	def Copy(self) -> Self:
		"""
		Create a copy of this generic procedure.

		The copy has no parent. Its parameters are copies of this procedure's parameters.

		:returns: The new generic procedure.
		"""
		copy = self.__class__(self._identifier, self._documentation)
		for parameterItem in self._parameterItems:
			copy.AddParameterItem(parameterItem.Copy())

		return copy


@export
class GenericFunctionInterfaceItem(Function, GenericSubprogramInterfaceItemMixin):
	"""
	Represents a function in a generic clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (function cmp(a, b : integer) return boolean);
	      --                ^^^                                    <- Identifier
	      --                    ^^^^^^^^^^^^^^                     <- ParameterItems
	      --                                           ^^^^^^^     <- ReturnType
	"""
	def __init__(
		self,
		identifier:    str,
		returnType:    SubtypeSymbol,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a function in a generic clause.

		:param identifier:    The identifier of a model entity.
		:param returnType:    Reference to the subtype of the function's return value.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, returnType, documentation=documentation, parent=parent)
		GenericSubprogramInterfaceItemMixin.__init__(self)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this generic function, its parameters and its return type with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitGenericFunctionInterfaceItem(self)
		self._VisitFormalParameterList(visitor)
		visitor.VisitReturn(self)
		self._returnType.Visit(visitor)
		visitor.DepartGenericFunctionInterfaceItem(self)

	def Copy(self) -> Self:
		"""
		Create a copy of this generic function.

		The copy has no parent. Its return type and parameters are copies of this function's return type and parameters.

		:returns: The new generic function.
		"""
		copy = self.__class__(self._identifier, self._returnType.Copy(), self._documentation)
		for parameterItem in self._parameterItems:
			copy.AddParameterItem(parameterItem.Copy())

		return copy


@export
@abstractclass
class InterfacePackage(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a package as a generic of a design unit.

	An interface package parameterises a design unit with an instantiated package.

	.. seealso::

	   * :class:`Generic package interface item <pyVHDLModel.Interface.GenericPackageInterfaceItem>`
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a package as a generic of a design unit.

		:param identifier:    The identifier of a model entity.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

	def __str__(self) -> str:
		"""
		Formats the interface package.

		**Format:** ``package myPackage``

		:returns: Formatted interface package.
		"""
		return f"package {self._identifier}"


@export
class GenericPackageInterfaceItem(InterfacePackage, GenericInterfaceItemMixin):
	"""
	Represents a package in a generic clause.

	A generic package parameterises a design unit with an instantiated package.
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a package in a generic clause.

		:param identifier:    The identifier of a model entity.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)

	def Copy(self) -> Self:
		"""
		Create a copy of this generic package.

		The copy has no parent.

		:returns: The new generic package.
		"""
		return self.__class__(self._identifier, self._documentation)


@export
@abstractclass
class PortSignalInterfaceItem(Signal, InterfaceItemMixin):
	"""
	Represents the base-class of all signals in a port clause.

	A port is declared either with a simple mode (:class:`PortSimpleSignalInterfaceItem`) or with a
	mode view (:class:`PortViewSignalInterfaceItem`).

	.. seealso::

	   * :class:`Port simple signal interface item <pyVHDLModel.Interface.PortSimpleSignalInterfaceItem>`
	   * :class:`Port view signal interface item <pyVHDLModel.Interface.PortViewSignalInterfaceItem>`
	"""


@export
class PortSimpleSignalInterfaceItem(PortSignalInterfaceItem, InterfaceItemWithModeMixin):
	"""
	Represents a port declared with a simple mode.

	The port's mode is available as :data:`Mode`, its subtype as :data:`Subtype`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      port (p : in bit);
	      --    ^              <- Identifiers
	      --        ^^         <- Mode
	      --           ^^^     <- Subtype

	.. seealso::

	   * :class:`Port declared with a mode view <pyVHDLModel.Interface.PortViewSignalInterfaceItem>`
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a port declared with a simple mode.

		:param identifiers:       A list of identifiers.
		:param mode:              The interface item's mode.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		InterfaceItemWithModeMixin.__init__(self, mode)

	def Copy(self) -> Self:
		"""
		Create a copy of this port.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this item's
		subtype and default expression.

		:returns: The new port.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(
			self._identifiers,
			self._mode,
			self._subtype.Copy(),
			defaultExpression,
			self._documentation
		)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this port, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitPortSimpleSignalInterfaceItem(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.DepartPortSimpleSignalInterfaceItem(self)

	def __str__(self) -> str:
		"""
		Formats the port.

		**Format:** ``signal p : in bit``

		:returns: Formatted port.
		"""
		return self._FormatInterfaceItem(self._mode)


@export
class PortViewSignalInterfaceItem(PortSignalInterfaceItem):
	"""
	Represents a port declared with a mode view (VHDL-2019).

	Instead of a mode, the port names a mode view (:data:`ModeViewIndication`) that assigns a mode to
	each element of its record type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      port (p : view MyView);
	      --    ^                   <- Identifiers
	      --             ^^^^^^     <- ModeViewIndication

	.. seealso::

	   * :class:`Mode view declaration <pyVHDLModel.Interface.ModeViewDeclaration>`
	   * :class:`Port declared with a simple mode <pyVHDLModel.Interface.PortSimpleSignalInterfaceItem>`
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		modeViewIndication: ModeViewSymbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a port declared with a mode view (VHDL-2019).

		:param identifiers:        A list of identifiers.
		:param modeViewIndication: Reference to the mode view applied to this port.
		:param documentation:      The documentation comment associated with this declaration.
		:param parent:             The parent model entity of this entity.
		"""
		super().__init__(identifiers, modeViewIndication, None, documentation, parent)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this port and its mode view indication with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitPortViewSignalInterfaceItem(self)
		self._subtype.Visit(visitor)
		visitor.DepartPortViewSignalInterfaceItem(self)

	@readonly
	def ModeViewIndication(self) -> ModeViewSymbol:
		"""
		Read-only property to access the mode view indication (:attr:`_subtype`).

		:returns: The mode view indication.
		"""
		return self._subtype

	def Copy(self) -> Self:
		"""
		Create a copy of this port declared with a mode view.

		The copy has no parent and no object vertex. Its mode view indication is a copy of this item's mode view
		indication.

		:returns: The new port declared with a mode view.
		"""
		return self.__class__(self._identifiers, self._subtype.Copy(), self._documentation)

	def __str__(self) -> str:
		"""
		Formats the port declared with a mode view.

		**Format:** ``signal p : view myView``

		:returns: Formatted port declared with a mode view.
		"""
		return self._FormatInterfaceItem(isModeView=True)


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	"""
	Represents a constant parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      function fun(constant cst : in integer) return integer;
	      --                    ^^^                                 <- Identifiers
	      --                          ^^                            <- Mode
	      --                             ^^^^^^^                    <- Subtype
	"""
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a constant parameter of a subprogram.

		:param identifiers:       A list of identifiers.
		:param mode:              The interface item's mode.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)

	def Copy(self) -> Self:
		"""
		Create a copy of this constant parameter.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this item's
		subtype and default expression.

		:returns: The new constant parameter.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(
			self._identifiers,
			self._mode,
			self._subtype.Copy(),
			defaultExpression,
			self._documentation
		)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this constant parameter, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitParameterConstantInterfaceItem(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.DepartParameterConstantInterfaceItem(self)

	def __str__(self) -> str:
		"""
		Formats the constant parameter.

		**Format:** ``constant a : in integer``

		:returns: Formatted constant parameter.
		"""
		return self._FormatInterfaceItem(self._mode)


@export
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	"""
	Represents a variable parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(variable var : out bit);
	      --                      ^^^               <- Identifiers
	      --                            ^^^         <- Mode
	      --                                ^^^     <- Subtype
	"""
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a variable parameter of a subprogram.

		:param identifiers:       A list of identifiers.
		:param mode:              The interface item's mode.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)

	def Copy(self) -> Self:
		"""
		Create a copy of this variable parameter.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this item's
		subtype and default expression.

		:returns: The new variable parameter.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(
			self._identifiers,
			self._mode,
			self._subtype.Copy(),
			defaultExpression,
			self._documentation
		)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this variable parameter, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitParameterVariableInterfaceItem(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.DepartParameterVariableInterfaceItem(self)

	def __str__(self) -> str:
		"""
		Formats the variable parameter.

		**Format:** ``variable v : inout integer``

		:returns: Formatted variable parameter.
		"""
		return self._FormatInterfaceItem(self._mode)


@export
@abstractclass
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItemMixin):
	"""
	Represents a signal parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal sig : in bit);
	      --                    ^^^              <- Identifiers
	      --                          ^^         <- Mode
	      --                             ^^^     <- Subtype

	.. seealso::

	   * :class:`Parameter simple signal interface item <pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem>`
	   * :class:`Parameter view signal interface item <pyVHDLModel.Interface.ParameterViewSignalInterfaceItem>`
	"""


@export
class ParameterSimpleSignalInterfaceItem(ParameterSignalInterfaceItem, InterfaceItemWithModeMixin):
	"""
	Represents a signal parameter declared with a simple mode.

	The parameter's mode is available as :data:`Mode`, its subtype as :data:`Subtype`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal sig : in bit);
	      --                    ^^^              <- Identifiers
	      --                          ^^         <- Mode
	      --                             ^^^     <- Subtype
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a signal parameter declared with a simple mode.

		:param identifiers:       A list of identifiers.
		:param mode:              The interface item's mode.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)

	def Copy(self) -> Self:
		"""
		Create a copy of this signal parameter.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this item's
		subtype and default expression.

		:returns: The new signal parameter.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(
			self._identifiers,
			self._mode,
			self._subtype.Copy(),
			defaultExpression,
			self._documentation
		)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this signal parameter, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitParameterSimpleSignalInterfaceItem(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.DepartParameterSimpleSignalInterfaceItem(self)

	def __str__(self) -> str:
		"""
		Formats the signal parameter.

		**Format:** ``signal s : in bit``

		:returns: Formatted signal parameter.
		"""
		return self._FormatInterfaceItem(self._mode)


@export
class ParameterViewSignalInterfaceItem(ParameterSignalInterfaceItem):
	"""
	Represents a signal parameter declared with a mode view (VHDL-2019).

	Instead of a mode, the parameter names a mode view (:data:`ModeViewIndication`) that assigns a mode
	to each element of its record type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal sig : view MasterView);
	      --                    ^^^                       <- Identifiers
	      --                               ^^^^^^^^^^     <- ModeViewIndication

	.. seealso::

	   * :class:`Mode view declaration <pyVHDLModel.Interface.ModeViewDeclaration>`
	   * :class:`Parameter declared with a simple mode <pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem>`
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		modeViewIndication: ModeViewSymbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a signal parameter declared with a mode view (VHDL-2019).

		:param identifiers:        A list of identifiers.
		:param modeViewIndication: Reference to the mode view applied to this parameter.
		:param documentation:      The documentation comment associated with this declaration.
		:param parent:             The parent model entity of this entity.
		"""
		super().__init__(identifiers, modeViewIndication, None, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this signal parameter and its mode view indication with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitParameterViewSignalInterfaceItem(self)
		self._subtype.Visit(visitor)
		visitor.DepartParameterViewSignalInterfaceItem(self)

	@readonly
	def ModeViewIndication(self) -> ModeViewSymbol:
		"""
		Read-only property to access the mode view indication (:attr:`_subtype`).

		:returns: The mode view indication.
		"""
		return self._subtype

	def Copy(self) -> Self:
		"""
		Create a copy of this signal parameter declared with a mode view.

		The copy has no parent and no object vertex. Its mode view indication is a copy of this item's mode view
		indication.

		:returns: The new signal parameter declared with a mode view.
		"""
		return self.__class__(self._identifiers, self._subtype.Copy(), self._documentation)

	def __str__(self) -> str:
		"""
		Formats the signal parameter declared with a mode view.

		**Format:** ``signal s : view myView``

		:returns: Formatted signal parameter declared with a mode view.
		"""
		return self._FormatInterfaceItem(isModeView=True)


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItemMixin):
	"""
	Represents a file parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(file fil : text_file);
	      --                  ^^^                 <- Identifiers
	      --                        ^^^^^^^^^     <- Subtype
	"""
	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a file parameter of a subprogram.

		:param identifiers:   A list of identifiers.
		:param subtype:       Reference to the object's subtype.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)

	def Copy(self) -> Self:
		"""
		Create a copy of this file parameter.

		The copy has no parent and no object vertex. Its subtype is a copy of this item's subtype.

		:returns: The new file parameter.
		"""
		return self.__class__(self._identifiers, self._subtype.Copy(), self._documentation)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this file parameter and its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitParameterFileInterfaceItem(self)
		self._subtype.Visit(visitor)
		visitor.DepartParameterFileInterfaceItem(self)

	def __str__(self) -> str:
		"""
		Formats the file parameter.

		**Format:** ``file f : text``

		:returns: Formatted file parameter.
		"""
		return self._FormatInterfaceItem()


@export
class InterfaceGroup(ModelEntity, OptionallyNamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a group of interface items sharing one clause.

	The group may be named (:data:`Identifier`), which is optional.

	.. seealso::

	   * :class:`Generic group <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Port group <pyVHDLModel.Interface.PortGroup>`
	   * :class:`Parameter group <pyVHDLModel.Interface.ParameterGroup>`
	"""
	def __init__(
		self,
		name:   Nullable[str] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a group of interface items sharing one clause.

		:param name:          The group's name.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)
		OptionallyNamedEntityMixin.__init__(self, name)
		DocumentedEntityMixin.__init__(self, documentation)

	def _AddToNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Add nothing, because an interface group has no namespace.

		:param element: The named element, e.g. an interface item.
		"""

	def _RemoveFromNamespace(self, element: NamedEntityMixin | MultipleNamedEntityMixin) -> None:
		"""
		Remove nothing, because an interface group has no namespace.

		:param element: The named element, e.g. an interface item.
		"""


@export
class GenericGroup(InterfaceGroup, WithGenericsMixin):
	"""
	Represents the generic clause of a design unit.

	The generics are available as :data:`GenericItems`.

	.. seealso::

	   * :class:`Port clause <pyVHDLModel.Interface.PortGroup>`
	   * :class:`Parameter list <pyVHDLModel.Interface.ParameterGroup>`
	"""
	def __init__(
		self,
		genericItems:  Iterable[GenericInterfaceItemMixin],
		name:          Nullable[str] = None,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a generic group.

		:param genericItems:  List of all generics, in declaration order.
		:param name:          The group's name.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(name, documentation, parent)
		WithGenericsMixin.__init__(self, genericItems)

	def __len__(self) -> int:
		"""
		Returns the number of generics in this group.

		:returns: Number of generics.
		"""
		return len(self._genericItems)

	def __iter__(self) -> Iterator[GenericInterfaceItemMixin]:
		"""
		Iterates the generics in this group.

		:returns: An iterator over the group's generics.
		"""
		return iter(self._genericItems)

	def __str__(self) -> str:
		"""
		Formats the generic group.

		**Format:** ``GenericGroup: myGroup (2): WIDTH, DEPTH``

		:returns: Formatted generic group.
		"""
		names = ", ".join(name for item in self._genericItems for name in identifiersOf(item))
		return f"GenericGroup: {self._identifier} ({len(self._genericItems)}): {names}"

	def _ClashingDeclarations(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> tuple[ModelEntity, ...]:
		"""
		Return the generics of this group sharing an identifier with the given item.

		:param item: The new generic.
		:returns:    Tuple of clashing generics.
		"""
		identifiers = set(normalizedIdentifiersOf(item))
		return tuple(
			declaration for declaration in self._genericItems
			if not identifiers.isdisjoint(normalizedIdentifiersOf(declaration))
		)


@export
class PortGroup(InterfaceGroup, WithPortsMixin):
	"""
	Represents the port clause of a design unit.

	The ports are available as :data:`PortItems`.

	.. seealso::

	   * :class:`Generic clause <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Parameter list <pyVHDLModel.Interface.ParameterGroup>`
	"""
	def __init__(
		self,
		portItems:     Iterable[PortInterfaceItemMixin],
		name:          Nullable[str] = None,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a port group.

		:param portItems:     List of all ports, in declaration order.
		:param name:          The group's name.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(name, documentation, parent)
		WithPortsMixin.__init__(self, portItems)

	def __len__(self) -> int:
		"""
		Returns the number of ports in this group.

		:returns: Number of ports.
		"""
		return len(self._portItems)

	def __iter__(self) -> Iterator[PortInterfaceItemMixin]:
		"""
		Iterates the ports in this group.

		:returns: An iterator over the group's ports.
		"""
		return iter(self._portItems)

	def __str__(self) -> str:
		"""
		Formats the port group.

		**Format:** ``PortGroup: myGroup (2): clock, reset``

		:returns: Formatted port group.
		"""
		names = ", ".join(name for item in self._portItems for name in identifiersOf(item))
		return f"PortGroup: {self._identifier} ({len(self._portItems)}): {names}"

	def _ClashingDeclarations(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> tuple[ModelEntity, ...]:
		"""
		Return the ports of this group sharing an identifier with the given item.

		:param item: The new port.
		:returns:    Tuple of clashing ports.
		"""
		identifiers = set(normalizedIdentifiersOf(item))
		return tuple(
			declaration for declaration in self._portItems
			if not identifiers.isdisjoint(normalizedIdentifiersOf(declaration))
		)


@export
class ParameterGroup(InterfaceGroup, WithParametersMixin):
	"""
	Represents the parameter list of a subprogram.

	The parameters are available as :data:`ParameterItems`.

	.. seealso::

	   * :class:`Generic clause <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Port clause <pyVHDLModel.Interface.PortGroup>`
	"""
	def __init__(
		self,
		parameterItems: Iterable[ParameterInterfaceItemMixin],
		name:           Nullable[str] = None,
		documentation:  Nullable[str] = None,
		parent:         Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a parameter group.

		:param parameterItems: List of all parameters, in declaration order.
		:param name:           The group's name.
		:param documentation:  The documentation comment associated with this declaration.
		:param parent:         The parent model entity of this entity.
		"""
		super().__init__(name, documentation, parent)
		WithParametersMixin.__init__(self, parameterItems)

	def __len__(self) -> int:
		"""
		Returns the number of parameters in this group.

		:returns: Number of parameters.
		"""
		return len(self._parameterItems)

	def __iter__(self) -> Iterator[ParameterInterfaceItemMixin]:
		"""
		Iterates the parameters in this group.

		:returns: An iterator over the group's parameters.
		"""
		return iter(self._parameterItems)

	def __str__(self) -> str:
		"""
		Formats the parameter group.

		**Format:** ``ParameterGroup: myGroup (2): a, b``

		:returns: Formatted parameter group.
		"""
		names = ", ".join(name for item in self._parameterItems for name in identifiersOf(item))
		return f"ParameterGroup: {self._identifier} ({len(self._parameterItems)}): {names}"

	def _ClashingDeclarations(self, item: NamedEntityMixin | MultipleNamedEntityMixin) -> tuple[ModelEntity, ...]:
		"""
		Return the parameters of this group sharing an identifier with the given item.

		:param item: The new parameter.
		:returns:    Tuple of clashing parameters.
		"""
		identifiers = set(normalizedIdentifiersOf(item))
		return tuple(
			declaration for declaration in self._parameterItems
			if not identifiers.isdisjoint(normalizedIdentifiersOf(declaration))
		)

	def _ParameterItemsChanged(self) -> None:
		"""Do nothing, because a parameter group keeps nothing derived from its parameters."""
