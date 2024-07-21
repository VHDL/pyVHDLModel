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
# Copyright 2017-2024 Patrick Lehmann - Boetzingen, Germany                                                            #
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
from typing                import Iterable, Optional as Nullable

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Graph       import Vertex

from pyVHDLModel.Base      import ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin, ExpressionUnion
from pyVHDLModel.Symbol    import Symbol


@export
class Obj(ModelEntity, MultipleNamedEntityMixin, DocumentedEntityMixin):
	"""
	Base-class for all objects (constants, signals, variables and files) in VHDL.

	An object (syntax element) can define multiple objects (semantic elements) in a single declaration, thus
	:class:`~pyVHDLModel.Base.MultipleNamedEntityMixin` is inherited. All objects can be documented, thus
	:class:`~pyVHDLModel.Base.DocumentedEntityMixin` is inherited too.

	Each object references a subtype via :data:`_subtype`.

	Objects are elements in the type and object graph, thus a reference to a vertex in that graph is stored in
	:data:`__objectVertex`.
	"""

	_subtype:      Symbol
	_objectVertex: Nullable[Vertex]

	def __init__(self, identifiers: Iterable[str], subtype: Symbol, documentation: Nullable[str] = None, parent: ModelEntity = None) -> None:
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype._parent = self

		self._objectVertex = None

	@readonly
	def Subtype(self) -> Symbol:
		return self._subtype

	@readonly
	def ObjectVertex(self) -> Nullable[Vertex]:
		"""
		Read-only property to access the corresponding object vertex (:attr:`_objectVertex`).

		The object vertex references this Object by its value field.

		:returns: The corresponding object vertex.
		"""
		return self._objectVertex


@export
class WithDefaultExpressionMixin(metaclass=ExtendedType, mixin=True):
	"""
	A ``WithDefaultExpression`` is a mixin-class for all objects declarations accepting default expressions.

	The default expression is referenced by :data:`__defaultExpression`. If no default expression is present, this field
	is ``None``.
	"""

	_defaultExpression: Nullable[ExpressionUnion]

	def __init__(self, defaultExpression: Nullable[ExpressionUnion] = None) -> None:
		self._defaultExpression = defaultExpression
		if defaultExpression is not None:
			defaultExpression._parent = self

	@readonly
	def DefaultExpression(self) -> Nullable[ExpressionUnion]:
		return self._defaultExpression


@export
class BaseConstant(Obj):
	"""
	Base-class for all constants (normal and deferred constants) in VHDL.
	"""


@export
class Constant(BaseConstant, WithDefaultExpressionMixin):
	"""
	Represents a constant.

	As constants (always) have a default expression, the class :class:`~pyVHDLModel.Object.WithDefaultExpressionMixin` is inherited.

	.. admonition:: Example

	   .. code-block:: VHDL

	      constant BITS : positive := 8;
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, documentation, parent)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


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
	_constantReference: Nullable[Constant]

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, documentation, parent)

	@readonly
	def ConstantReference(self) -> Nullable[Constant]:
		return self._constantReference

	def __str__(self) -> str:
		return f"constant {', '.join(self._identifiers)} : {self._subtype}"


@export
class Variable(Obj, WithDefaultExpressionMixin):
	"""
	Represents a variable.

	As variables might have a default expression, the class :class:`~pyVHDLModel.Object.WithDefaultExpressionMixin` is inherited.

	.. admonition:: Example

	   .. code-block:: VHDL

	      variable result : natural := 0;
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, documentation, parent)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class SharedVariable(Obj):
	"""
	Represents a shared variable.

	.. todo:: Shared variable object not implemented.
	"""



@export
class Signal(Obj, WithDefaultExpressionMixin):
	"""
	Represents a signal.

	As signals might have a default expression, the class :class:`~pyVHDLModel.Object.WithDefaultExpressionMixin` is inherited.

	.. admonition:: Example

	   .. code-block:: VHDL

	      signal counter : unsigned(7 downto 0) := '0';
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: ModelEntity = None
	) -> None:
		super().__init__(identifiers, subtype, documentation, parent)
		WithDefaultExpressionMixin.__init__(self, defaultExpression)


@export
class File(Obj):
	"""
	Represents a file.

	.. todo:: File object not implemented.
	"""
