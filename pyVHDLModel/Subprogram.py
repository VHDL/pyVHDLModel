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

Subprograms are procedures, functions and methods.
"""
from __future__             import annotations

from typing                 import TYPE_CHECKING, Any, ClassVar, Iterable, Optional as Nullable

from pyTooling.Common       import getFullyQualifiedName
from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType, abstractclass

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, identifiersOf, ReservedWord
from pyVHDLModel.Symbol     import SubtypeSymbol
from pyVHDLModel.Type       import ProtectedType
from pyVHDLModel.Regions    import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin, \
                                   ProtectedTypeDeclarationRegionMixin, WithGenericsMixin, WithParametersMixin
from pyVHDLModel.Sequential import SequentialStatement, SequentialStatementsMixin

if TYPE_CHECKING:
	from pyVHDLModel.Visitor  import Visitor


@export
class SubprogramSignature(ModelEntity):
	"""
	Represents a subprogram's signature: the type marks of its parameters and of a function's return value.

	The overloads of a subprogram differ in their signature. A parameter declaring several identifiers - ``a, b : in
	natural`` - contributes its type mark once per identifier. The string form is VHDL's notation of a signature
	(IEEE Std 1076-2019, 4.5.3), as an alias declaration or attribute specification writes it:
	``[natural, natural return boolean]``.

	The parent of a signature is the subprogram declaring it (:data:`Subprogram.Signature`). The type marks stay children
	of the parameters and of the function declaring them.

	Two signatures are equal, if their parameters' type marks and their return type marks have the same normalized names
	(:data:`NormalizedParameterTypeNames`, :data:`NormalizedReturnTypeName`); the parent isn't compared. So the
	signatures of two subprograms compare by their parameter and result type profile, and a signature can be used as a
	dictionary key or set member. The names are compared as written: ``natural`` and ``std.standard.natural`` differ,
	because the model doesn't resolve type marks yet.

	.. admonition:: Example

	   .. code-block:: VHDL

	      function to_index(value : unsigned; low, high : positive) return natural;
	      --                        ^^^^^^^^              ^^^^^^^^        ^^^^^^^   <- ParameterTypes and ReturnType
	      --                                         (twice)
	"""
	_parameterTypes:               tuple[SubtypeSymbol, ...]  #: Type marks of the parameters, one per identifier.
	_returnType:                   Nullable[SubtypeSymbol]    #: Type mark of a function's return value, if a function.
	_parameterTypeNames:           tuple[str, ...]            #: Names of the parameters' type marks, as written.
	_returnTypeName:               Nullable[str]              #: Name of the return type mark, as written.
	_normalizedParameterTypeNames: tuple[str, ...]            #: Normalized names of the parameters' type marks.
	_normalizedReturnTypeName:     Nullable[str]              #: Normalized name of the return type mark.
	_hash:                         int                        #: Hash value of the parameter and result type profile.

	def __init__(
		self,
		parameterTypes: Iterable[SubtypeSymbol],
		returnType:     Nullable[SubtypeSymbol] = None,
		*,
		parent:         Nullable[Subprogram] =    None
	) -> None:
		"""
		Initializes a subprogram signature.

		:param parameterTypes: The type marks of the parameters, one per parameter identifier.
		:param returnType:     Optional, the type mark of a function's return value. Default: ``None``, a procedure.
		:param parent:         Optional, the subprogram declaring this signature. Default: ``None``.
		:raises ValueError:    If parameter 'parameterTypes' is ``None``.
		:raises TypeError:     If parameter 'parameterTypes' is not iterable.
		:raises TypeError:     If an element of parameter 'parameterTypes' is not of type
		                       :class:`~pyVHDLModel.Symbol.SubtypeSymbol`.
		:raises TypeError:     If parameter 'returnType' is not of type :class:`~pyVHDLModel.Symbol.SubtypeSymbol`.
		:raises TypeError:     If parameter 'parent' is not of type :class:`~pyVHDLModel.Subprogram.Subprogram`.
		"""
		super().__init__(parent)

		if parent is not None and not isinstance(parent, Subprogram):
			ex = TypeError("Parameter 'parent' is not of type 'Subprogram'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if parameterTypes is None:
			raise ValueError("Parameter 'parameterTypes' is None.")
		elif not isinstance(parameterTypes, Iterable):
			ex = TypeError("Parameter 'parameterTypes' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterTypes)}'.")
			raise ex

		types =           []
		names =           []
		normalizedNames = []
		for parameterType in parameterTypes:
			if not isinstance(parameterType, SubtypeSymbol):
				ex = TypeError("Element of parameter 'parameterTypes' is not of type 'SubtypeSymbol'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parameterType)}'.")
				raise ex

			typeMark = parameterType.TypeMark
			types.append(parameterType)
			names.append(typeMark)
			normalizedNames.append(typeMark.lower())

		if returnType is not None and not isinstance(returnType, SubtypeSymbol):
			ex = TypeError("Parameter 'returnType' is not of type 'SubtypeSymbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(returnType)}'.")
			raise ex

		self._parameterTypes =               tuple(types)
		self._returnType =                   returnType
		self._parameterTypeNames =           tuple(names)
		self._normalizedParameterTypeNames = tuple(normalizedNames)

		if returnType is None:
			self._returnTypeName =           None
			self._normalizedReturnTypeName = None
		else:
			self._returnTypeName =           returnType.TypeMark
			self._normalizedReturnTypeName = self._returnTypeName.lower()

		self._hash = hash((self._normalizedParameterTypeNames, self._normalizedReturnTypeName))

	@readonly
	def ParameterTypes(self) -> tuple[SubtypeSymbol, ...]:
		"""
		Read-only property to access the type marks of the parameters (:attr:`_parameterTypes`).

		:returns: Tuple of the parameters' type marks, one per parameter identifier, in declaration order.
		"""
		return self._parameterTypes

	@readonly
	def ReturnType(self) -> Nullable[SubtypeSymbol]:
		"""
		Read-only property to access the type mark of a function's return value (:attr:`_returnType`).

		:returns: The return value's type mark, or ``None`` for a procedure.
		"""
		return self._returnType

	@readonly
	def ParameterTypeNames(self) -> tuple[str, ...]:
		"""
		Read-only property to access the names of the parameters' type marks, as written (:attr:`_parameterTypeNames`).

		Each name is a type mark's :data:`~pyVHDLModel.Symbol.SubtypeSymbol.TypeMark`.

		:returns: Tuple of the type marks' names, one per parameter identifier, in declaration order.
		"""
		return self._parameterTypeNames

	@readonly
	def ReturnTypeName(self) -> Nullable[str]:
		"""
		Read-only property to access the name of a function's return type mark, as written (:attr:`_returnTypeName`).

		:returns: The return type mark's name, or ``None`` for a procedure.
		"""
		return self._returnTypeName

	@readonly
	def NormalizedParameterTypeNames(self) -> tuple[str, ...]:
		"""
		Read-only property to access the normalized (lower case) names of the parameters' type marks
		(:attr:`_normalizedParameterTypeNames`).

		The names are compared by :meth:`__eq__` and hashed by :meth:`__hash__`.

		:returns: Tuple of the type marks' normalized names, one per parameter identifier, in declaration order.
		"""
		return self._normalizedParameterTypeNames

	@readonly
	def NormalizedReturnTypeName(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized (lower case) name of a function's return type mark
		(:attr:`_normalizedReturnTypeName`).

		The name is compared by :meth:`__eq__` and hashed by :meth:`__hash__`.

		:returns: The return type mark's normalized name, or ``None`` for a procedure.
		"""
		return self._normalizedReturnTypeName

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two signatures, if they are equal: same normalized names of the parameters' and the return type marks.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both signatures have the same parameter and result type profile.
		:raises TypeError: If parameter ``other`` is not of type :class:`SubprogramSignature`.
		"""
		if not isinstance(other, SubprogramSignature):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: SubprogramSignature")
			raise ex

		return (
			self._normalizedParameterTypeNames == other._normalizedParameterTypeNames and
			self._normalizedReturnTypeName == other._normalizedReturnTypeName
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two signatures, if they are unequal: different normalized names of the parameters' or the return type marks.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both signatures have a different parameter and result type profile.
		:raises TypeError: If parameter ``other`` is not of type :class:`SubprogramSignature`.
		"""
		if not isinstance(other, SubprogramSignature):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: SubprogramSignature")
			raise ex

		return (
			self._normalizedParameterTypeNames != other._normalizedParameterTypeNames or
			self._normalizedReturnTypeName != other._normalizedReturnTypeName
		)

	def __hash__(self) -> int:
		"""
		Return the hash of the signature over the normalized names of the parameters' and the return type marks
		(:attr:`_hash`).

		:returns: Hash value of the parameter and result type profile.
		"""
		return self._hash

	def __str__(self) -> str:
		"""
		Return the signature in VHDL's notation: the parameters' type marks, comma separated, and a function's return type
		mark, in brackets.

		:returns: The signature, e.g. ``[unsigned, positive, positive return natural]`` or ``[natural]``.
		"""
		signature = ", ".join(self._parameterTypeNames)
		if self._returnTypeName is not None:
			returnType = f"return {self._returnTypeName}"
			signature = returnType if signature == "" else f"{signature} {returnType}"

		return f"[{signature}]"


@export
@abstractclass
class Subprogram(
	ModelEntity,
	NamedEntityMixin,
	DocumentedEntityMixin,
	WithGenericsMixin,
	WithParametersMixin,
	SequentialDeclarationRegionMixin,
	SequentialStatementsMixin
):
	"""
	Represents the base-class of all subprograms: procedures and functions.

	A subprogram is a named entity (:data:`Identifier`) with an optional generic clause
	(:data:`GenericItems`), a parameter list (:data:`ParameterItems`), its own declarative part
	(:data:`DeclaredItems`) and a sequence of statements (:data:`Statements`).

	.. seealso::

	   * :class:`Procedure <pyVHDLModel.Subprogram.Procedure>`
	   * :class:`Function <pyVHDLModel.Subprogram.Function>`
	"""
	_SUBPROGRAM_KEYWORD: ClassVar[str] = "subprogram"   #: The VHDL keyword introducing this subprogram kind.
	_isPure:             bool                           #: ``True`` if the subprogram was declared pure.
	_signature:          Nullable[SubprogramSignature]  #: The kept signature, or ``None`` until computed.

	def __init__(
		self,
		identifier:     str,
		isPure:         bool,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None,
		genericGroups:  Nullable[Iterable[GenericGroup]] =                  None
	) -> None:
		"""
		Initializes a subprogram.

		:param identifier:     The identifier of a model entity.
		:param isPure:         ``True`` if the subprogram was declared pure.
		:param genericItems:   List of all generics, in declaration order.
		:param parameterItems: List of all parameters, in declaration order.
		:param declaredItems:  List of all declared items in this sequential declaration region.
		:param statements:     List of all sequential statements in the subprogram's body.
		:param documentation:  The documentation comment associated with this declaration.
		:param parent:         The parent model entity of this entity.
		:param genericGroups:  Optional, list of generic groups partitioning the generics, in declaration order.
		                       Default: ``None``, one unnamed generic group.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)
		WithGenericsMixin.__init__(self, genericItems, genericGroups)
		WithParametersMixin.__init__(self, parameterItems)
		SequentialStatementsMixin.__init__(self, statements)

		self._isPure =    isPure
		self._signature = None

	@ModelEntity.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ModelEntity.Parent.fset(self, parent)

		# Connect the subprogram's namespace to the enclosing declaration region's namespace, so a
		# declaration inside the subprogram hides a same-named one from the scope around it. Protected
		# types and their bodies are declaration regions too, so a method chains like any other
		# subprogram; the check remains because a parent need not be a region at all.
		regions = (ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin, ProtectedTypeDeclarationRegionMixin)
		if isinstance(parent, regions):
			self._namespace.ParentNamespace = parent._namespace

	@readonly
	def IsPure(self) -> bool:
		"""
		Check if the subprogram is pure (:attr:`_isPure`).

		:returns: ``True``, if the subprogram is pure.
		"""
		return self._isPure

	@readonly
	def Signature(self) -> SubprogramSignature:
		"""
		Read-only property to access the subprogram's signature (:attr:`_signature`): the type marks of its parameters,
		and of a function's return value.

		The signature is computed on the first access and kept, until a parameter is added, inserted, removed or moved.

		:returns: The signature.
		"""
		if self._signature is None:
			self._signature = SubprogramSignature(
				(item._subtype for item in self._parameterItems for _ in identifiersOf(item)),
				parent=self
			)

		return self._signature

	def _ParameterItemsChanged(self) -> None:
		"""Clear the kept signature (:attr:`_signature`), because the parameter list changed."""
		self._signature = None

	def IndexDeclaredItems(self) -> None:
		"""
		A subprogram's generics and parameters share the declarative region of its declarative part.

		:raises UnhandledCriticalWarningError: If an identifier is declared twice in a declarative region and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects the
		                                       :exc:`~pyVHDLModel.Exception.DuplicateDeclarationWarning`.
		"""
		self._IndexGenericItems()
		self._IndexParameterItems()

		super().IndexDeclaredItems()

	def _Declarations(self) -> tuple[ModelEntity, ...]:
		"""
		Return all declarations of this subprogram: its generics and parameters share the declarative region.

		:returns: Tuple of declarations: the generics, the parameters, then the declared items.
		"""
		return (*self._genericItems, *self._parameterItems, *super()._Declarations())

	def _LabelRegion(self) -> Subprogram:
		"""
		Return the subprogram, whose declarative region declares the labels of its statements.

		:returns: The subprogram itself.
		"""
		return self

	def _VisitDeclarativeAndStatementPart(self, visitor: Visitor) -> None:
		"""
		Walk the declarative part and the statement part of this subprogram with a visitor.

		The reserved word ``is`` precedes the declared items, the reserved word ``begin`` the statements.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitIs(self)
		self._VisitDeclaredItems(visitor)
		visitor.VisitBegin(self)
		self._VisitStatements(visitor)

	def __str__(self) -> str:
		"""
		Formats the subprogram declaration.

		**Format:** ``procedure myProcedure(a, b)``

		:returns: Formatted subprogram declaration.
		"""
		parameters = ", ".join(name for item in self._parameterItems for name in identifiersOf(item))
		return f"{self._SUBPROGRAM_KEYWORD} {self._identifier}({parameters})"


@export
class Procedure(Subprogram):
	"""
	Represents a procedure.

	Unlike a function, a procedure returns no value. Besides its parameters, it has its own
	declarative part (:data:`DeclaredItems`) and statements (:data:`Statements`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal s : in bit; variable v : out bit) is
	      --        ^^^^                                               <- Identifier
	      --             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^       <- ParameterItems
	        variable tmp : bit;
	      --^^^^^^^^^^^^^^^^^^^                                        <- DeclaredItems
	      begin
	        tmp := s;
	      --^^^^^^^^^                                                  <- Statements
	        v := tmp;
	      end procedure;

	.. seealso::

	   * :class:`Procedure instantiation <pyVHDLModel.Instantiation.ProcedureInstantiation>`
	   * :class:`Generic procedure interface item <pyVHDLModel.Interface.GenericProcedureInterfaceItem>`
	   * :class:`Procedure method <pyVHDLModel.Subprogram.ProcedureMethod>`
	   * :class:`Function <pyVHDLModel.Subprogram.Function>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Procedure,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                       #: The reserved words after ``end`` are optional.

	_SUBPROGRAM_KEYWORD: ClassVar[str] = "procedure"  #: The VHDL keyword introducing this subprogram kind.

	def __init__(
		self,
		identifier:     str,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None,
		genericGroups:  Nullable[Iterable[GenericGroup]] =                  None
	) -> None:
		"""
		Initializes a procedure.

		:param identifier:     The identifier of a model entity.
		:param genericItems:   List of all generics, in declaration order.
		:param parameterItems: List of all parameters, in declaration order.
		:param declaredItems:  List of all declared items in this sequential declaration region.
		:param statements:     List of all sequential statements in the subprogram's body.
		:param documentation:  The documentation comment associated with this declaration.
		:param parent:         The parent model entity of this entity.
		:param genericGroups:  Optional, list of generic groups partitioning the generics, in declaration order.
		                       Default: ``None``, one unnamed generic group.
		"""
		super().__init__(
			identifier,
			False,
			genericItems,
			parameterItems,
			declaredItems,
			statements,
			documentation,
			parent,
			genericGroups
		)

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this procedure, its generic clause, its parameters, its declared items and its statements with a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitProcedure(self)
		self._VisitGenericClause(visitor)
		self._VisitFormalParameterList(visitor)
		self._VisitDeclarativeAndStatementPart(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartProcedure(self)


@export
class Function(Subprogram):
	"""
	Represents a function.

	A function returns a value of its return type (:data:`ReturnType`) and is either pure or impure
	(:data:`IsPure`). Besides its parameters, it has its own declarative part (:data:`DeclaredItems`)
	and statements (:data:`Statements`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      function fun(constant c : in positive) return integer is
	      --       ^^^                                               <- Identifier
	      --           ^^^^^^^^^^^^^^^^^^^^^^^^                      <- ParameterItems
	      --                                            ^^^^^^^      <- ReturnType
	        variable tmp : integer;
	      --^^^^^^^^^^^^^^^^^^^^^^^                                  <- DeclaredItems
	      begin
	        tmp := c;
	      --^^^^^^^^^                                                <- Statements
	        return tmp;
	      end function;

	.. seealso::

	   * :class:`Function instantiation <pyVHDLModel.Instantiation.FunctionInstantiation>`
	   * :class:`Generic function interface item <pyVHDLModel.Interface.GenericFunctionInterfaceItem>`
	   * :class:`Function method <pyVHDLModel.Subprogram.FunctionMethod>`
	   * :class:`Procedure <pyVHDLModel.Subprogram.Procedure>`
	"""

	_END_KEYWORDS:          ClassVar[tuple[ReservedWord, ...]] = (ReservedWord.Function,)  #: Reserved words after ``end``.
	_END_KEYWORDS_OPTIONAL: ClassVar[bool] =                     True                      #: The reserved words after ``end`` are optional.

	_SUBPROGRAM_KEYWORD: ClassVar[str] = "function"  #: The VHDL keyword introducing this subprogram kind.
	_returnType:         SubtypeSymbol               #: Reference to the subtype of the function's return value.

	def __init__(
		self,
		identifier:     str,
		returnType:     SubtypeSymbol,
		isPure:         bool =                                              True,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None,
		genericGroups:  Nullable[Iterable[GenericGroup]] =                  None
	) -> None:
		"""
		Initializes a function.

		:param identifier:     The identifier of a model entity.
		:param returnType:     Reference to the subtype of the function's return value.
		:param isPure:         ``True`` if the subprogram was declared pure.
		:param genericItems:   List of all generics, in declaration order.
		:param parameterItems: List of all parameters, in declaration order.
		:param declaredItems:  List of all declared items in this sequential declaration region.
		:param statements:     List of all sequential statements in the subprogram's body.
		:param documentation:  The documentation comment associated with this declaration.
		:param parent:         The parent model entity of this entity.
		:param genericGroups:  Optional, list of generic groups partitioning the generics, in declaration order.
		                       Default: ``None``, one unnamed generic group.
		"""
		super().__init__(
			identifier,
			isPure,
			genericItems,
			parameterItems,
			declaredItems,
			statements,
			documentation,
			parent,
			genericGroups
		)

		self._returnType = returnType
		returnType.Parent = self

	def Visit(self, visitor: Visitor) -> None:
		"""
		Walk this function, its generic clause, its parameters, its return type, its declared items and its statements with
		a visitor.

		:param visitor: The visitor receiving the events.
		"""
		visitor.VisitFunction(self)
		self._VisitGenericClause(visitor)
		self._VisitFormalParameterList(visitor)
		visitor.VisitReturn(self)
		self._returnType.Visit(visitor)
		self._VisitDeclarativeAndStatementPart(visitor)
		visitor.VisitEnd(self)
		visitor.VisitTerminator(self)
		visitor.DepartFunction(self)

	@readonly
	def ReturnType(self) -> SubtypeSymbol:
		"""
		Read-only property to access the return type (:attr:`_returnType`).

		:returns: The return type.
		"""
		return self._returnType

	@readonly
	def Signature(self) -> SubprogramSignature:
		"""
		Read-only property to access the function's signature (:attr:`_signature`): the type marks of its parameters and
		of its return value.

		The signature is computed on the first access and kept, until a parameter is added, inserted, removed or moved.

		:returns: The signature.
		"""
		if self._signature is None:
			self._signature = SubprogramSignature(
				(item._subtype for item in self._parameterItems for _ in identifiersOf(item)),
				self._returnType,
				parent=self
			)

		return self._signature


@export
class MethodMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``Method`` is a mixin class for all subprograms in a protected type.

	.. seealso::

	   * :class:`Procedure method <pyVHDLModel.Subprogram.ProcedureMethod>`
	   * :class:`Function method <pyVHDLModel.Subprogram.FunctionMethod>`
	"""

	_protectedType: ProtectedType  #: Reference to the protected type this method belongs to.

	def __init__(self, protectedType: Nullable[ProtectedType] = None) -> None:
		"""
		Initializes a method.

		:param protectedType: Reference to the protected type this method belongs to.
		"""
		self._protectedType = protectedType
		if protectedType is not None:
			protectedType.Parent = self

	@readonly
	def ProtectedType(self) -> ProtectedType:
		"""
		Read-only property to access the protected type (:attr:`_protectedType`).

		:returns: The protected type.
		"""
		return self._protectedType


@export
class ProcedureMethod(Procedure, MethodMixin):
	"""
	Represents a procedure declared as a method of a protected type.

	The protected type is available as :data:`ProtectedType`.

	.. seealso::

	   * :class:`Protected type <pyVHDLModel.Type.ProtectedType>`
	"""
	def __init__(
		self,
		identifier:     str,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		protectedType:  Nullable[ProtectedType] =                           None,
		parent:         Nullable[ModelEntity] =                             None,
		genericGroups:  Nullable[Iterable[GenericGroup]] =                  None
	) -> None:
		"""
		Initializes a procedure declared as a method of a protected type.

		:param identifier:     The identifier of a model entity.
		:param genericItems:   List of all generics, in declaration order.
		:param parameterItems: List of all parameters, in declaration order.
		:param declaredItems:  List of all declared items in this sequential declaration region.
		:param statements:     List of all sequential statements in the subprogram's body.
		:param documentation:  The documentation comment associated with this declaration.
		:param protectedType:  Reference to the protected type this method belongs to.
		:param parent:         The parent model entity of this entity.
		:param genericGroups:  Optional, list of generic groups partitioning the generics, in declaration order.
		                       Default: ``None``, one unnamed generic group.
		"""
		super().__init__(
			identifier,
			genericItems,
			parameterItems,
			declaredItems,
			statements,
			documentation,
			parent,
			genericGroups
		)
		MethodMixin.__init__(self, protectedType)


@export
class FunctionMethod(Function, MethodMixin):
	"""
	Represents a function declared as a method of a protected type.

	The protected type is available as :data:`ProtectedType`.

	.. seealso::

	   * :class:`Protected type <pyVHDLModel.Type.ProtectedType>`
	"""
	def __init__(
		self,
		identifier:     str,
		returnType:     SubtypeSymbol,
		isPure:         bool =                                              True,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		protectedType:  Nullable[ProtectedType] =                           None,
		parent:         Nullable[ModelEntity] =                             None,
		genericGroups:  Nullable[Iterable[GenericGroup]] =                  None
	) -> None:
		"""
		Initializes a function declared as a method of a protected type.

		:param identifier:     The identifier of a model entity.
		:param returnType:     Reference to the subtype of the function's return value.
		:param isPure:         ``True`` if the subprogram was declared pure.
		:param genericItems:   List of all generics, in declaration order.
		:param parameterItems: List of all parameters, in declaration order.
		:param declaredItems:  List of all declared items in this sequential declaration region.
		:param statements:     List of all sequential statements in the subprogram's body.
		:param documentation:  The documentation comment associated with this declaration.
		:param protectedType:  Reference to the protected type this method belongs to.
		:param parent:         The parent model entity of this entity.
		:param genericGroups:  Optional, list of generic groups partitioning the generics, in declaration order.
		                       Default: ``None``, one unnamed generic group.
		"""
		super().__init__(
			identifier,
			returnType,
			isPure,
			genericItems,
			parameterItems,
			declaredItems,
			statements,
			documentation,
			parent,
			genericGroups
		)
		MethodMixin.__init__(self, protectedType)
