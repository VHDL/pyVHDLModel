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

from typing                 import ClassVar, Iterable, Optional as Nullable

from pyTooling.Common       import getFullyQualifiedName
from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType, abstractclass

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin, identifiersOf
from pyVHDLModel.Symbol     import SubtypeSymbol
from pyVHDLModel.Type       import ProtectedType
from pyVHDLModel.Regions    import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin
from pyVHDLModel.Regions    import ProtectedTypeDeclarationRegionMixin, WithGenericsMixin, WithParametersMixin
from pyVHDLModel.Sequential import SequentialStatement, SequentialStatementsMixin


@export
class SubprogramSignature(metaclass=ExtendedType, slots=True):
	"""
	Represents a subprogram's signature: the type marks of its parameters and of a function's return value.

	The overloads of a subprogram differ in their signature. A parameter declaring several identifiers - ``a, b : in
	natural`` - contributes its type mark once per identifier. The string form is VHDL's notation of a signature
	(IEEE Std 1076-2019, 4.5.3), as an alias declaration or attribute specification writes it:
	``[natural, natural return boolean]``.

	.. admonition:: Example

	   .. code-block:: VHDL

	      function to_index(value : unsigned; low, high : positive) return natural;
	      --                        ^^^^^^^^              ^^^^^^^^        ^^^^^^^   <- ParameterTypes and ReturnType
	      --                                         (twice)
	"""
	_parameterTypes: tuple[SubtypeSymbol, ...]  #: The type marks of the parameters, one per parameter identifier.
	_returnType:     Nullable[SubtypeSymbol]    #: The type mark of a function's return value, if a function.

	def __init__(self, parameterTypes: Iterable[SubtypeSymbol], returnType: Nullable[SubtypeSymbol] = None) -> None:
		"""
		Initializes a subprogram signature.

		:param parameterTypes: The type marks of the parameters, one per parameter identifier.
		:param returnType:     Optional, the type mark of a function's return value. Default: ``None``, a procedure.
		:raises ValueError:    If parameter 'parameterTypes' is ``None``.
		:raises TypeError:     If parameter 'parameterTypes' is not iterable.
		:raises TypeError:     If an element of parameter 'parameterTypes' is not of type
		                       :class:`~pyVHDLModel.Symbol.SubtypeSymbol`.
		:raises TypeError:     If parameter 'returnType' is not of type :class:`~pyVHDLModel.Symbol.SubtypeSymbol`.
		"""
		if parameterTypes is None:
			raise ValueError("Parameter 'parameterTypes' is None.")
		elif not isinstance(parameterTypes, Iterable):
			ex = TypeError("Parameter 'parameterTypes' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterTypes)}'.")
			raise ex

		types = []
		for parameterType in parameterTypes:
			if not isinstance(parameterType, SubtypeSymbol):
				ex = TypeError("Element of parameter 'parameterTypes' is not of type 'SubtypeSymbol'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parameterType)}'.")
				raise ex

			types.append(parameterType)

		if returnType is not None and not isinstance(returnType, SubtypeSymbol):
			ex = TypeError("Parameter 'returnType' is not of type 'SubtypeSymbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(returnType)}'.")
			raise ex

		self._parameterTypes = tuple(types)
		self._returnType =     returnType

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

	@staticmethod
	def _TypeName(symbol: SubtypeSymbol) -> str:
		"""
		Return a type mark's name, as written: a simple name, or a selected name with its prefixes.

		:param symbol: The type mark.
		:returns:      The name, e.g. ``natural`` or ``ieee.numeric_std.unsigned``.
		"""
		name = symbol.Name
		parts = [name.Identifier]
		while name.HasPrefix:
			name = name.Prefix
			parts.insert(0, name.Identifier)

		return ".".join(parts)

	def ParameterTypeNames(self) -> list[str]:
		"""
		Return the names of the parameters' type marks, as written.

		A type mark's name is written as in the source - ``natural`` or ``ieee.numeric_std.unsigned`` -: the model doesn't
		resolve type marks yet, so the fully qualified name of the denoted type isn't known.

		:returns: List of the type marks' names, one per parameter identifier, in declaration order.
		"""
		return [self._TypeName(parameterType) for parameterType in self._parameterTypes]

	def ReturnTypeName(self) -> Nullable[str]:
		"""
		Return the name of a function's return type mark, as written.

		:returns: The return type mark's name, or ``None`` for a procedure.
		"""
		return None if self._returnType is None else self._TypeName(self._returnType)

	def __str__(self) -> str:
		"""
		Return the signature in VHDL's notation: the parameters' type marks, comma separated, and a function's return type
		mark, in brackets.

		:returns: The signature, e.g. ``[unsigned, positive, positive return natural]`` or ``[natural]``.
		"""
		signature = ", ".join(self.ParameterTypeNames())
		if self._returnType is not None:
			returnType = f"return {self.ReturnTypeName()}"
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
	_SUBPROGRAM_KEYWORD: ClassVar[str] = "subprogram"  #: The VHDL keyword introducing this subprogram kind.
	_isPure:             bool                          #: ``True`` if the subprogram was declared pure.

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
		WithGenericsMixin.__init__(self, genericItems)
		WithParametersMixin.__init__(self, parameterItems)
		SequentialStatementsMixin.__init__(self, statements)

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
	def IsPure(self) -> bool:
		"""
		Check if the subprogram is pure (:attr:`_isPure`).

		:returns: ``True``, if the subprogram is pure.
		"""
		return self._isPure

	@readonly
	def Signature(self) -> SubprogramSignature:
		"""
		Read-only property to return the subprogram's signature: the type marks of its parameters, and of a function's
		return value.

		:returns: The signature.
		"""
		return SubprogramSignature(self._ParameterTypes(), None)

	def _ParameterTypes(self) -> list[SubtypeSymbol]:
		"""
		Return the type marks of the parameters, one per parameter identifier.

		:returns: List of the type marks, in declaration order.
		"""
		return [item._subtype for item in self._parameterItems for _ in identifiersOf(item)]


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

	_SUBPROGRAM_KEYWORD: ClassVar[str] = "procedure"  #: The VHDL keyword introducing this subprogram kind.

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

	@readonly
	def Signature(self) -> SubprogramSignature:
		"""
		Read-only property to return the function's signature: the type marks of its parameters and of its return value.

		:returns: The signature.
		"""
		return SubprogramSignature(self._ParameterTypes(), self._returnType)


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
