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

Objects are constants, variables, signals and files.
"""
from __future__            import annotations

from typing                import TYPE_CHECKING, ClassVar, Iterable, Optional as Nullable, Self

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractclass
from pyTooling.Graph       import Vertex

from pyVHDLModel.Base      import ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin, ExpressionUnion, \
                                  ReservedWord
from pyVHDLModel.Symbol    import Symbol

if TYPE_CHECKING:
	from pyVHDLModel.Visitor import Visitor


@export
@abstractclass
class Obj(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	"""
	Base-class for all objects (constants, signals, variables and files) in VHDL.

	An object (syntax element) can define multiple objects (semantic elements) in a single declaration, thus
	:class:`~pyVHDLModel.Base.MultipleNamedEntityMixin` is inherited. All objects can be documented, thus
	:class:`~pyVHDLModel.Base.DocumentedEntityMixin` is inherited too.

	Each object references a subtype via :data:`_subtype`.

	Objects are elements in the type and object graph, thus a reference to a vertex in that graph is stored in
	:data:`__objectVertex`.

	.. seealso::

	   * :class:`Base constant <pyVHDLModel.Object.BaseConstant>`
	   * :class:`Variable <pyVHDLModel.Object.Variable>`
	   * :class:`Shared variable <pyVHDLModel.Object.SharedVariable>`
	   * :class:`Signal <pyVHDLModel.Object.Signal>`
	   * :class:`File <pyVHDLModel.Object.File>`
	"""

	_OBJECT_KEYWORD: ClassVar[tuple[ReservedWord, ...]]  #: The reserved words introducing this object class.

	_subtype:      Symbol            #: Reference to the object's subtype.
	_objectVertex: Nullable[Vertex]  #: The vertex representing this object in the design's object graph.

	def __init__(self, identifiers: Iterable[str], subtype: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an object.

		:param identifiers:   A list of identifiers.
		:param subtype:       Reference to the object's subtype.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype.Parent = self

		self._objectVertex = None

	@readonly
	def Subtype(self) -> Symbol:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	@readonly
	def ObjectVertex(self) -> Nullable[Vertex]:
		"""
		Read-only property to access the corresponding object vertex (:attr:`_objectVertex`).

		The object vertex references this Object by its value field.

		:returns: The corresponding object vertex.
		"""
		return self._objectVertex

	def Copy(self) -> Self:
		"""
		Create a copy of this object declaration.

		The copy has no parent and no object vertex. Its subtype is a copy of this declaration's subtype.

		:returns: The new object declaration.
		"""
		return self.__class__(self._identifiers, self._subtype.Copy(), self._documentation)

	def _SplitInParent(self) -> tuple[Self, ...]:
		"""
		Split this object declaration by the mutator of its parent (``SplitDeclaredItem()``).

		:returns: Tuple of declarations, one per identifier in list order, starting with this object declaration.
		"""
		return self._parent.SplitDeclaredItem(self)

	def __str__(self) -> str:
		"""
		Formats the object declaration.

		**Format:** ``signal s1, s2 : bit``

		:returns: Formatted object declaration.
		"""
		return f"{' '.join(self._OBJECT_KEYWORD)} {', '.join(self._identifiers)} : {self._subtype}"


@export
class WithDefaultExpressionMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``WithDefaultExpression`` is a mixin-class for all objects declarations accepting default expressions.

	The default expression is referenced by :data:`__defaultExpression`. If no default expression is present, this field
	is ``None``.

	.. seealso::

	   * :class:`Constant <pyVHDLModel.Object.Constant>`
	   * :class:`Variable <pyVHDLModel.Object.Variable>`
	   * :class:`Signal <pyVHDLModel.Object.Signal>`
	"""

	_defaultExpression: Nullable[ExpressionUnion]  #: The default value, or ``None`` if none was given.

	def __init__(self, defaultExpression: Nullable[ExpressionUnion] = None) -> None:
		"""
		Initializes an object with a default expression.

		:param defaultExpression: The default value, or ``None`` if none was given.
		"""
		self._defaultExpression = defaultExpression
		if defaultExpression is not None:
			defaultExpression.Parent = self

	@readonly
	def DefaultExpression(self) -> Nullable[ExpressionUnion]:
		"""
		Read-only property to access the default expression (:attr:`_defaultExpression`).

		:returns: The default expression, or ``None`` if not set.
		"""
		return self._defaultExpression

	def _VisitDefaultExpression(self, visitor: Visitor) -> None:
		"""
		Walk the default expression, if any, after a variable assignment delimiter (``:=``) with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		if self._defaultExpression is not None:
			visitor.VisitVariableAssignment(self)
			self._defaultExpression.Visit(visitor)


@export
@abstractclass
class BaseConstant(Obj):
	"""
	Base-class for all constants (normal and deferred constants) in VHDL.

	.. seealso::

	   * :class:`Constant <pyVHDLModel.Object.Constant>`
	   * :class:`Deferred constant <pyVHDLModel.Object.DeferredConstant>`
	"""

	_OBJECT_KEYWORD: ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Constant,)  #: The reserved words introducing this object class.


@export
class Constant(BaseConstant, WithDefaultExpressionMixin):
	"""
	Represents a constant.

	As constants (always) have a default expression, the class :class:`~pyVHDLModel.Object.WithDefaultExpressionMixin` is inherited.

	.. admonition:: Example

	   .. code-block:: VHDL

	      constant BITS : positive := 8;

	.. seealso::

	   * :class:`Generic constant interface item <pyVHDLModel.Interface.GenericConstantInterfaceItem>`
	   * :class:`Parameter constant interface item <pyVHDLModel.Interface.ParameterConstantInterfaceItem>`
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a constant.

		:param identifiers:       A list of identifiers.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, documentation, parent)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)

	def Copy(self) -> Self:
		"""
		Create a copy of this constant.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this constant's
		subtype and default expression.

		:returns: The new constant.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(self._identifiers, self._subtype.Copy(), defaultExpression, self._documentation)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this constant declaration, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitConstant(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartConstant(self)


@export
class DeferredConstant(BaseConstant):
	"""
	Represents a deferred constant.

	Deferred constants are forward declarations for a (complete) constant declaration, thus it contains a
	field :data:`__constantReference` to the complete constant declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      constant BITS : positive;
	"""
	_constantReference: Nullable[Constant]  #: The full declaration, or ``None`` if unlinked.

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a deferred constant.

		:param identifiers:   A list of identifiers.
		:param subtype:       Reference to the object's subtype.
		:param documentation: The documentation comment associated with this declaration.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, documentation, parent)

		self._constantReference = None

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this deferred constant declaration, its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitDeferredConstant(self)
		self._subtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartDeferredConstant(self)

	@readonly
	def ConstantReference(self) -> Nullable[Constant]:
		"""
		Read-only property to access the constant reference (:attr:`_constantReference`).

		:returns: The constant reference, or ``None`` if not set.
		"""
		return self._constantReference

	def Copy(self) -> Self:
		"""
		Create a copy of this deferred constant.

		The copy has no parent and no object vertex. Its subtype is a copy of this deferred constant's subtype; the full
		constant declaration, if linked, is the same.

		:returns: The new deferred constant.
		"""
		copy = self.__class__(self._identifiers, self._subtype.Copy(), self._documentation)
		copy._constantReference = self._constantReference
		return copy


@export
class Variable(Obj, WithDefaultExpressionMixin):
	"""
	Represents a variable.

	As variables might have a default expression, the class :class:`~pyVHDLModel.Object.WithDefaultExpressionMixin` is inherited.

	.. admonition:: Example

	   .. code-block:: VHDL

	      variable result : natural := 0;

	.. seealso::

	   * :class:`Parameter variable interface item <pyVHDLModel.Interface.ParameterVariableInterfaceItem>`
	"""

	_OBJECT_KEYWORD: ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Variable,)  #: The reserved words introducing this object class.

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a variable.

		:param identifiers:       A list of identifiers.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, documentation, parent)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)

	def Copy(self) -> Self:
		"""
		Create a copy of this variable.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this variable's
		subtype and default expression.

		:returns: The new variable.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(self._identifiers, self._subtype.Copy(), defaultExpression, self._documentation)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this variable declaration, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitVariable(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartVariable(self)


@export
class SharedVariable(Obj):
	"""
	Represents a shared variable.

	.. todo:: Shared variable object not implemented.
	"""

	_OBJECT_KEYWORD: ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Shared, ReservedWord.Variable)  #: The reserved words introducing this object class.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this shared variable declaration, its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSharedVariable(self)
		self._subtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartSharedVariable(self)



@export
class Signal(Obj, WithDefaultExpressionMixin):
	"""
	Represents a signal.

	As signals might have a default expression, the class :class:`~pyVHDLModel.Object.WithDefaultExpressionMixin` is inherited.

	.. admonition:: Example

	   .. code-block:: VHDL

	      signal counter : unsigned(7 downto 0) := '0';

	.. seealso::

	   * :class:`Port signal interface item <pyVHDLModel.Interface.PortSignalInterfaceItem>`
	   * :class:`Parameter signal interface item <pyVHDLModel.Interface.ParameterSignalInterfaceItem>`
	"""

	_OBJECT_KEYWORD: ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Signal,)  #: The reserved words introducing this object class.

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a signal.

		:param identifiers:       A list of identifiers.
		:param subtype:           Reference to the object's subtype.
		:param defaultExpression: The default value, or ``None`` if none was given.
		:param documentation:     The documentation comment associated with this declaration.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(identifiers, subtype, documentation, parent)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)

	def Copy(self) -> Self:
		"""
		Create a copy of this signal.

		The copy has no parent and no object vertex. Its subtype and default expression are copies of this signal's
		subtype and default expression.

		:returns: The new signal.
		"""
		defaultExpression = None if self._defaultExpression is None else self._defaultExpression.Copy()
		return self.__class__(self._identifiers, self._subtype.Copy(), defaultExpression, self._documentation)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this signal declaration, its subtype and its default expression with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitSignal(self)
		self._subtype.Visit(visitor)
		self._VisitDefaultExpression(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartSignal(self)


@export
class File(Obj):
	"""
	Represents a file.

	.. todo:: File object not implemented.

	.. seealso::

	   * :class:`Parameter file interface item <pyVHDLModel.Interface.ParameterFileInterfaceItem>`
	"""

	_OBJECT_KEYWORD: ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.File,)  #: The reserved words introducing this object class.

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this file declaration, its subtype with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitFile(self)
		self._subtype.Visit(visitor)
		visitor.VisitTerminator(self)
		visitor.DepartFile(self)
