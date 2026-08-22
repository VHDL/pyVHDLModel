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

tbd.
"""
from __future__            import annotations

from typing                import TYPE_CHECKING, List, Dict, Iterable, Optional as Nullable, Any

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Warning     import WarningCollector

from pyVHDLModel.Base      import normalizedIdentifiersOf
from pyVHDLModel.Exception import NotImplementedWarning
from pyVHDLModel.Namespace import Namespace
from pyVHDLModel.Object    import Constant, SharedVariable, File, Variable, Signal
if TYPE_CHECKING:
	from pyVHDLModel.Type     import Subtype, FullType

# `pyVHDLModel.Subprogram` imports this module (Subprogram is a sequential declaration region), so
# `Function`/`Procedure` are quoted in annotations and imported lazily where they're needed at runtime.



@export
class DeclarationRegionMixin(metaclass=ExtendedType, mixin=True):
	"""
	A base-class for the concurrent and sequential declaration region mixins.

	It carries what both regions share: adding interface items to the region's namespace, and the hook for
	declared items neither region handles itself.

	An interface item shares the declarative region of the declarative part beside it - VHDL rejects
	``port (g : in bit)`` beside ``generic (g : integer)``, ``signal x`` beside ``port (x : in bit)``, and a
	subprogram variable named like one of its parameters, all as "identifier already used for a
	declaration". So they belong in the region's *own* namespace, not a separate one.

	Which of the three a region has is known statically by the class that declares them, so each derived
	class calls the ones it needs from its own :meth:`IndexDeclaredItems` before delegating upwards.
	Interface items are added to the namespace only - ``GenericItems``/``PortItems``/``ParameterItems``
	already expose them as ordered lists, so no extra lookup table is needed.

	.. seealso::

	   * :class:`Concurrent declaration region mixin <pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin>`
	   * :class:`Sequential declaration region mixin <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	"""

	def _IndexGenericItems(self) -> None:
		"""Add this region's generics to its namespace."""
		for item in self._genericItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _IndexPortItems(self) -> None:
		"""Add this region's ports to its namespace."""
		for item in self._portItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _IndexParameterItems(self) -> None:
		"""Add this region's parameters to its namespace."""
		for item in self._parameterItems:
			for normalizedIdentifier in normalizedIdentifiersOf(item):
				self._namespace.AddElement(normalizedIdentifier, item)

	def _IndexOtherDeclaredItem(self, item) -> None:
		"""Hook for declared items the region doesn't handle itself. Derived classes may override it."""
		pass


@export
class ConcurrentDeclarationRegionMixin(DeclarationRegionMixin, mixin=True):
	# FIXME: define list prefix type e.g. via Union
	"""
	A mixin-class for concurrent declaration regions.

	Entities, architectures, packages, blocks and generate bodies declare items concurrently. Beside
	the namespace, the region keeps a lookup table per kind of declared item (:data:`Types`,
	:data:`Signals`, :data:`Constants`, ...).

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`For generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Package body <pyVHDLModel.DesignUnit.PackageBody>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	   * :class:`Sequential declaration region <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	   * :class:`Namespace <pyVHDLModel.Namespace.Namespace>`
	"""
	_declaredItems:   List                        #: List of all declared items in this concurrent declaration region.

	# _attributes:     Dict[str, Attribute]
	# _aliases:        Dict[str, Alias]
	_types:           Dict[str, FullType]         #: Dictionary of all types declared in this concurrent declaration region.
	_subtypes:        Dict[str, Subtype]          #: Dictionary of all subtypes declared in this concurrent declaration region.
	# _objects:        Dict[str, Union[Constant, Variable, Signal]]
	_constants:       Dict[str, Constant]         #: Dictionary of all constants declared in this concurrent declaration region.
	_signals:         Dict[str, Signal]           #: Dictionary of all signals declared in this concurrent declaration region.
	_sharedVariables: Dict[str, SharedVariable]   #: Dictionary of all shared variables declared in this concurrent declaration region.
	_files:           Dict[str, File]             #: Dictionary of all files declared in this concurrent declaration region.
	# _subprograms:     Dict[str, List[Subprogram]]  #: Dictionary of all subprograms declared in this concurrent declaration region.
	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:       Dict[str, List[Function]]   #: Dictionary of all functions declared in this concurrent declaration region, indexed by name; each entry is a list of overloads.
	_procedures:      Dict[str, List[Procedure]]  #: Dictionary of all procedures declared in this concurrent declaration region, indexed by name; each entry is a list of overloads.
	_components:      Dict[str, Any]              #: Dictionary of all components declared in this concurrent declaration region.

	def __init__(self, declaredItems: Nullable[Iterable] = None) -> None:
		# TODO: extract to mixin
		"""
		Initializes a concurrent declaration region.

		:param declaredItems: List of all declared items in this concurrent declaration region.
		"""
		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item.Parent = self

		self._types =       {}
		self._subtypes =    {}
		# self._objects =     {}
		self._constants =   {}
		self._signals =     {}
		self._sharedVariables = {}
		self._files =       {}
		# self._subprograms = {}
		self._functions =   {}
		self._procedures =  {}
		self._components =  {}

	@readonly
	def DeclaredItems(self) -> List:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	@readonly
	def Types(self) -> Dict[str, FullType]:
		"""
		Read-only property to access the types (:attr:`_types`).

		:returns: Dictionary of types, indexed by normalized identifier.
		"""
		return self._types

	@readonly
	def Subtypes(self) -> Dict[str, Subtype]:
		"""
		Read-only property to access the subtypes (:attr:`_subtypes`).

		:returns: Dictionary of subtypes, indexed by normalized identifier.
		"""
		return self._subtypes

	# @readonly
	# def Objects(self) -> Dict[str, Union[Constant, SharedVariable, Signal, File]]:
	# 	return self._objects

	@readonly
	def Constants(self) -> Dict[str, Constant]:
		"""
		Read-only property to access the constants (:attr:`_constants`).

		:returns: Dictionary of constants, indexed by normalized identifier.
		"""
		return self._constants

	@readonly
	def Signals(self) -> Dict[str, Signal]:
		"""
		Read-only property to access the signals (:attr:`_signals`).

		:returns: Dictionary of signals, indexed by normalized identifier.
		"""
		return self._signals

	@readonly
	def SharedVariables(self) -> Dict[str, SharedVariable]:
		"""
		Read-only property to access the shared variables (:attr:`_sharedVariables`).

		:returns: Dictionary of shared variables, indexed by normalized identifier.
		"""
		return self._sharedVariables

	@readonly
	def Files(self) -> Dict[str, File]:
		"""
		Read-only property to access the files (:attr:`_files`).

		:returns: Dictionary of files, indexed by normalized identifier.
		"""
		return self._files

	# @readonly
	# def Subprograms(self) -> Dict[str, Subprogram]:
	# 	return self._subprograms

	@readonly
	def Functions(self) -> Dict[str, List[Function]]:
		"""
		Read-only property to access the functions (:attr:`_functions`).

		:returns: Dictionary of functions, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> Dict[str, List[Procedure]]:
		"""
		Read-only property to access the procedures (:attr:`_procedures`).

		:returns: Dictionary of procedures, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._procedures

	@readonly
	def Components(self) -> Dict[str, Any]:
		"""
		Read-only property to access the components (:attr:`_components`).

		:returns: Dictionary of components, indexed by normalized identifier.
		"""
		return self._components

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the concurrent declaration region.

		.. rubric:: Algorithm

		1. Iterate all declared items:

		   * Every declared item is added to :attr:`_namespace`.
		   * If the declared item is a :class:`~pyVHDLModel.Type.FullType`, then add an entry to :attr:`_types`.
		   * If the declared item is a :class:`~pyVHDLModel.Type.Subtype`, then add an entry to :attr:`_subtypes`.
		   * If the declared item is a :class:`~pyVHDLModel.Subprogram.Function`, then add an entry to :attr:`_functions`.
		   * If the declared item is a :class:`~pyVHDLModel.Subprogram.Procedure`, then add an entry to :attr:`_procedures`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.Constant`, then add an entry to :attr:`_constants`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.Signal`, then add an entry to :attr:`_signals`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.Variable`, TODO.
		   * If the declared item is a :class:`~pyVHDLModel.Object.SharedVariable`, then add an entry to :attr:`_sharedVariables`.
		   * If the declared item is a :class:`~pyVHDLModel.Object.File`, then add an entry to :attr:`_files`.
		   * If the declared item is neither of these types, call :meth:`_IndexOtherDeclaredItem`. |br|
		     Derived classes may override this virtual function.

		.. seealso::

		   :meth:`pyVHDLModel.Design.IndexPackages`
		     Iterate all packages in the design and index declared items.
		   :meth:`pyVHDLModel.Library.IndexPackages`
		     Iterate all packages in the library and index declared items.
		   :meth:`pyVHDLModel.Library._IndexOtherDeclaredItem`
		     Iterate all packages in the library and index declared items.
		"""
		from pyVHDLModel.DesignUnit import Component
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType

		for item in self._declaredItems:
			if isinstance(item, FullType):
				self._types[item._normalizedIdentifier] = item
				self._namespace.AddElement(item._normalizedIdentifier, item)
			elif isinstance(item, Subtype):
				self._subtypes[item._normalizedIdentifier] = item
				self._namespace.AddElement(item._normalizedIdentifier, item)
			elif isinstance(item, Function):
				# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
				#        real overload resolution yet).
				self._functions.setdefault(item._normalizedIdentifier, []).append(item)
				self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
			elif isinstance(item, Procedure):
				# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
				#        real overload resolution yet).
				self._procedures.setdefault(item._normalizedIdentifier, []).append(item)
				self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
			elif isinstance(item, Constant):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._constants[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
					# self._objects[normalizedIdentifier] = item
			elif isinstance(item, Signal):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._signals[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
			elif isinstance(item, Variable):
				# TODO: variables declared in a concurrent declaration region (e.g. shared variables outside a
				#       protected type) are not yet indexed into a dedicated namespace/lookup table.
				identifiers = ", ".join(f"'{i}'" for i in item._identifiers)
				WarningCollector.Raise(NotImplementedWarning(f"IndexDeclaredItems: variable(s) {identifiers} are not yet indexed."))
			elif isinstance(item, SharedVariable):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._sharedVariables[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
			elif isinstance(item, File):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._files[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
			elif isinstance(item, Component):
				self._components[item._normalizedIdentifier] = item
				self._namespace.AddElement(item._normalizedIdentifier, item)
			else:
				self._IndexOtherDeclaredItem(item)


@export
class SequentialDeclarationRegionMixin(DeclarationRegionMixin, mixin=True):
	"""
	A mixin-class for sequential declaration regions: process statements and subprogram bodies.

	.. note::

	   VHDL's ``process_declarative_item`` and ``subprogram_declarative_item`` rules are identical, so both
	   regions share this implementation. Compared to a concurrent region
	   (:class:`ConcurrentDeclarationRegionMixin`, ``block_declarative_item``), a sequential region can
	   declare a **variable**, but no signal, shared variable, component or mode view, and none of the
	   specifications.

	.. seealso::

	   * :class:`Process statement <pyVHDLModel.Concurrent.ProcessStatement>`
	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	   * :class:`Concurrent declaration region <pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin>`
	   * :class:`Namespace <pyVHDLModel.Namespace.Namespace>`
	"""

	_declaredItems: List                        #: List of all declared items in this sequential declaration region.
	_namespace:     Namespace                   #: The namespace of this sequential declaration region.

	_types:         Dict[str, FullType]         #: Dictionary of all types declared in this sequential declaration region.
	_subtypes:      Dict[str, Subtype]          #: Dictionary of all subtypes declared in this sequential declaration region.
	_constants:     Dict[str, Constant]         #: Dictionary of all constants declared in this sequential declaration region.
	_variables:     Dict[str, Variable]         #: Dictionary of all variables declared in this sequential declaration region.
	_files:         Dict[str, File]             #: Dictionary of all files declared in this sequential declaration region.
	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:     Dict[str, List[Function]]   #: Dictionary of all functions declared in this sequential declaration region, indexed by name; each entry is a list of overloads.
	_procedures:    Dict[str, List[Procedure]]  #: Dictionary of all procedures declared in this sequential declaration region, indexed by name; each entry is a list of overloads.

	def __init__(self, namespaceName: Nullable[str] = None, declaredItems: Nullable[Iterable] = None) -> None:
		"""
		Initialize a sequential declaration region.

		:param namespaceName:  Name of this region's namespace, usually the host's label or identifier.
		:param declaredItems:  The items declared in this region.
		"""
		self._namespace = Namespace(namespaceName)

		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item.Parent = self

		self._types =      {}
		self._subtypes =   {}
		self._constants =  {}
		self._variables =  {}
		self._files =      {}
		self._functions =  {}
		self._procedures = {}

	@readonly
	def DeclaredItems(self) -> List:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of declared items.
		"""
		return self._declaredItems

	@readonly
	def Namespace(self) -> Namespace:
		"""
		Read-only property to access this region's namespace (:attr:`_namespace`).

		:returns: The namespace.
		"""
		return self._namespace

	@readonly
	def Types(self) -> Dict[str, FullType]:
		"""
		Read-only property to access the declared types (:attr:`_types`).

		:returns: Dictionary of types, indexed by normalized identifier.
		"""
		return self._types

	@readonly
	def Subtypes(self) -> Dict[str, Subtype]:
		"""
		Read-only property to access the declared subtypes (:attr:`_subtypes`).

		:returns: Dictionary of subtypes, indexed by normalized identifier.
		"""
		return self._subtypes

	@readonly
	def Constants(self) -> Dict[str, Constant]:
		"""
		Read-only property to access the declared constants (:attr:`_constants`).

		:returns: Dictionary of constants, indexed by normalized identifier.
		"""
		return self._constants

	@readonly
	def Variables(self) -> Dict[str, Variable]:
		"""
		Read-only property to access the declared variables (:attr:`_variables`).

		:returns: Dictionary of variables, indexed by normalized identifier.
		"""
		return self._variables

	@readonly
	def Files(self) -> Dict[str, File]:
		"""
		Read-only property to access the declared files (:attr:`_files`).

		:returns: Dictionary of files, indexed by normalized identifier.
		"""
		return self._files

	@readonly
	def Functions(self) -> Dict[str, List[Function]]:
		"""
		Read-only property to access the declared functions (:attr:`_functions`).

		:returns: Dictionary of functions, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> Dict[str, List[Procedure]]:
		"""
		Read-only property to access the declared procedures (:attr:`_procedures`).

		:returns: Dictionary of procedures, indexed by normalized identifier; each entry is a list of overloads.
		"""
		return self._procedures

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the sequential declaration region.

		Every declared item is added to :attr:`_namespace`, and additionally to the lookup table matching its
		kind. Items of an unhandled kind are passed to :meth:`_IndexOtherDeclaredItem`.

		.. seealso::

		   :meth:`ConcurrentDeclarationRegionMixin.IndexDeclaredItems`
		     The same algorithm for a concurrent declaration region.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType

		for item in self._declaredItems:
			if isinstance(item, FullType):
				self._types[item._normalizedIdentifier] = item
				self._namespace.AddElement(item._normalizedIdentifier, item)
			elif isinstance(item, Subtype):
				self._subtypes[item._normalizedIdentifier] = item
				self._namespace.AddElement(item._normalizedIdentifier, item)
			elif isinstance(item, Function):
				# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
				#        real overload resolution yet).
				self._functions.setdefault(item._normalizedIdentifier, []).append(item)
				self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
			elif isinstance(item, Procedure):
				# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
				#        real overload resolution yet).
				self._procedures.setdefault(item._normalizedIdentifier, []).append(item)
				self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
			elif isinstance(item, Constant):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._constants[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
			elif isinstance(item, Variable):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._variables[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
			elif isinstance(item, File):
				for normalizedIdentifier in item._normalizedIdentifiers:
					self._files[normalizedIdentifier] = item
					self._namespace.AddElement(normalizedIdentifier, item)
			else:
				self._IndexOtherDeclaredItem(item)


@export
class ProtectedTypeDeclarationRegionMixin(DeclarationRegionMixin, mixin=True):
	"""
	A mixin-class for the declarative region of a protected type declaration.

	VHDL's ``protected_type_declarative_item`` rule admits subprogram declarations only, making this the
	narrowest declarative region in the language. A protected type *body* differs: its declarative part
	matches a subprogram's, so it uses :class:`SequentialDeclarationRegionMixin`.

	.. seealso::

	   * :class:`Protected type <pyVHDLModel.Type.ProtectedType>`
	   * :class:`Protected type body <pyVHDLModel.Type.ProtectedTypeBody>`
	   * :class:`Sequential declaration region <pyVHDLModel.Regions.SequentialDeclarationRegionMixin>`
	   * :class:`Namespace <pyVHDLModel.Namespace.Namespace>`
	"""

	_declaredItems: List                        #: List of all declared items in this protected type declaration.
	_namespace:     Namespace                   #: The namespace of this protected type declaration.

	# FIXME: overloads are only collected into a list, not matched/resolved by signature.
	_functions:     Dict[str, List[Function]]   #: All declared functions, indexed by name; each is a list of overloads.
	_procedures:    Dict[str, List[Procedure]]  #: All declared procedures by name; each is a list of overloads.

	def __init__(self, namespaceName: Nullable[str] = None, declaredItems: Nullable[Iterable] = None) -> None:
		"""
		Initialize a protected type declaration region.

		:param namespaceName: Name of this region's namespace, usually the protected type's identifier.
		:param declaredItems: The items declared in this region.
		"""
		self._namespace = Namespace(namespaceName)

		self._declaredItems = []  # TODO: convert to dict
		if declaredItems is not None:
			for item in declaredItems:
				self._declaredItems.append(item)
				item.Parent = self

		self._functions =  {}
		self._procedures = {}

	@readonly
	def DeclaredItems(self) -> List:
		"""
		Read-only property to access the declared items (:attr:`_declaredItems`).

		:returns: List of all declared items.
		"""
		return self._declaredItems

	@readonly
	def Functions(self) -> Dict[str, List[Function]]:
		"""
		Read-only property to access the declared functions (:attr:`_functions`).

		:returns: Dictionary of all functions, indexed by name; each entry is a list of overloads.
		"""
		return self._functions

	@readonly
	def Procedures(self) -> Dict[str, List[Procedure]]:
		"""
		Read-only property to access the declared procedures (:attr:`_procedures`).

		:returns: Dictionary of all procedures, indexed by name; each entry is a list of overloads.
		"""
		return self._procedures

	def IndexDeclaredItems(self) -> None:
		"""
		Index declared items listed in the protected type declaration.

		Only subprogram declarations are legal here, so anything else is passed to
		:meth:`_IndexOtherDeclaredItem`.

		.. seealso::

		   :meth:`SequentialDeclarationRegionMixin.IndexDeclaredItems`
		     The same algorithm for the protected type's body.
		"""
		from pyVHDLModel.Subprogram import Function, Procedure
		from pyVHDLModel.Type       import Subtype, FullType

		for item in self._declaredItems:
			if isinstance(item, Function):
				# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
				#        real overload resolution yet).
				self._functions.setdefault(item._normalizedIdentifier, []).append(item)
				self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
			elif isinstance(item, Procedure):
				# FIXME: overloads are only appended to a list, not matched/resolved by signature (no
				#        real overload resolution yet).
				self._procedures.setdefault(item._normalizedIdentifier, []).append(item)
				self._namespace.AddElement(item._normalizedIdentifier, item, overloadable=True)
			else:
				self._IndexOtherDeclaredItem(item)
