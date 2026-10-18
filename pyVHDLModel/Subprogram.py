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

from typing                 import ClassVar, List, Iterable, Optional as Nullable

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, identifiersOf
from pyVHDLModel.Symbol     import SubtypeSymbol
from pyVHDLModel.Type       import ProtectedType
from pyVHDLModel.Regions    import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin
from pyVHDLModel.Regions    import ProtectedTypeDeclarationRegionMixin
from pyVHDLModel.Sequential import SequentialStatement


@export
class Subprogram(ModelEntity, NamedEntityMixin, DocumentedEntityMixin, SequentialDeclarationRegionMixin):
	"""
	Represents the base-class of all subprograms: procedures and functions.

	A subprogram is a named entity (:data:`Identifier`) with an optional generic clause
	(:data:`GenericItems`), a parameter list (:data:`ParameterItems`), its own declarative part
	(:data:`DeclaredItems`) and a sequence of statements (:data:`Statements`).

	.. seealso::

	   * :class:`Procedure <pyVHDLModel.Subprogram.Procedure>`
	   * :class:`Function <pyVHDLModel.Subprogram.Function>`
	"""
	_subprogramKeyword: ClassVar[str] = "subprogram"    #: The VHDL keyword introducing this subprogram kind.

	_genericItems:   List[GenericInterfaceItemMixin]    #: List of all generics, in declaration order.
	_parameterItems: List[ParameterInterfaceItemMixin]  #: List of all parameters, in declaration order.
	_statements:     List[SequentialStatement]          #: List of all sequential statements in the subprogram's body.
	_isPure:         bool                               #: ``True`` if the subprogram was declared pure.

	def __init__(
		self,
		identifier:     str,
		isPure:         bool,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None
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
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)

		self._genericItems = []  # TODO: convert to dict
		if genericItems is not None:
			for item in genericItems:
				self._genericItems.append(item)
				item.Parent = self

		self._parameterItems = []  # TODO: convert to dict
		if parameterItems is not None:
			for item in parameterItems:
				self._parameterItems.append(item)
				item.Parent = self

		self._statements = []  # TODO: use mixin class
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item.Parent = self

		self._isPure = isPure

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
	def GenericItems(self) -> List[GenericInterfaceItemMixin]:
		"""
		Read-only property to access the generic items (:attr:`_genericItems`).

		:returns: List of generic items.
		"""
		return self._genericItems

	@readonly
	def ParameterItems(self) -> List[ParameterInterfaceItemMixin]:
		"""
		Read-only property to access the parameter items (:attr:`_parameterItems`).

		:returns: List of parameter items.
		"""
		return self._parameterItems

	@readonly
	def Statements(self) -> List[SequentialStatement]:
		"""
		Read-only property to access the statements (:attr:`_statements`).

		:returns: List of statements.
		"""
		return self._statements

	@readonly
	def IsPure(self) -> bool:
		"""
		Check if the subprogram is pure (:attr:`_isPure`).

		:returns: ``True``, if the subprogram is pure.
		"""
		return self._isPure


	def IndexDeclaredItems(self) -> None:
		"""A subprogram's generics and parameters share the declarative region of its declarative part."""
		self._IndexGenericItems()
		self._IndexParameterItems()

		super().IndexDeclaredItems()

	def __str__(self) -> str:
		"""
		Formats the subprogram declaration.

		**Format:** ``procedure myProcedure(a, b)``

		:returns: Formatted subprogram declaration.
		"""
		parameters = ", ".join(name for item in self._parameterItems for name in identifiersOf(item))
		return f"{self._subprogramKeyword} {self._identifier}({parameters})"


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

	_subprogramKeyword: ClassVar[str] = "procedure"
	def __init__(
		self,
		identifier:     str,
		genericItems:   Nullable[Iterable[GenericInterfaceItemMixin]] =   None,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None
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
		"""
		super().__init__(identifier, False, genericItems, parameterItems, declaredItems, statements, documentation, parent)


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

	_subprogramKeyword: ClassVar[str] = "function"
	_returnType: SubtypeSymbol  #: Reference to the subtype of the function's return value.

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
		parent:         Nullable[ModelEntity] =                             None
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
		"""
		super().__init__(identifier, isPure, genericItems, parameterItems, declaredItems, statements, documentation, parent)

		self._returnType = returnType
		returnType.Parent = self

	@readonly
	def ReturnType(self) -> SubtypeSymbol:
		"""
		Read-only property to access the return type (:attr:`_returnType`).

		:returns: The return type.
		"""
		return self._returnType


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
		parent:         Nullable[ModelEntity] =                             None
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
		"""
		super().__init__(identifier, genericItems, parameterItems, declaredItems, statements, documentation, parent)
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
		parent:         Nullable[ModelEntity] =                             None
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
		"""
		super().__init__(identifier, returnType, isPure, genericItems, parameterItems, declaredItems, statements, documentation, parent)
		MethodMixin.__init__(self, protectedType)
