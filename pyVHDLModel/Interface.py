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
This module contains parts of an abstract document language model for VHDL.

Interface items are used in generic, port and parameter declarations.
"""
from typing import Iterable

from pyTooling.Decorators import export

from pyVHDLModel.Symbol import Symbol
from pyVHDLModel.Base import DocumentedEntityMixin, ExpressionUnion, Mode
from pyVHDLModel.Object import Constant, Signal, Variable, File
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Type import Type


@export
class InterfaceItem(DocumentedEntityMixin):
	"""An ``InterfaceItem`` is a base-class for all mixin-classes for all interface items."""

	def __init__(self, documentation: str = None):
		super().__init__(documentation)


@export
class InterfaceItemWithMode:
	"""An ``InterfaceItemWithMode`` is a mixin-class to provide a ``Mode`` to interface items."""

	_mode: Mode

	def __init__(self, mode: Mode):
		self._mode = mode

	@property
	def Mode(self) -> Mode:
		return self._mode


@export
class GenericInterfaceItem(InterfaceItem):
	"""A ``GenericInterfaceItem`` is a mixin class for all generic interface items."""


@export
class PortInterfaceItem(InterfaceItem, InterfaceItemWithMode):
	"""A ``PortInterfaceItem`` is a mixin class for all port interface items."""

	def __init__(self, mode: Mode):
		super().__init__()
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterInterfaceItem(InterfaceItem):
	"""A ``ParameterInterfaceItem`` is a mixin class for all parameter interface items."""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		GenericInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class GenericTypeInterfaceItem(Type, GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class GenericSubprogramInterfaceItem(GenericInterfaceItem):
	pass


@export
class GenericProcedureInterfaceItem(Procedure, GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class GenericFunctionInterfaceItem(Function, GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class GenericPackageInterfaceItem(GenericInterfaceItem):
	def __init__(self, identifier: str, documentation: str = None):
		#	super().__init__(identifier, documentation)
		GenericInterfaceItem.__init__(self)


@export
class PortSignalInterfaceItem(Signal, PortInterfaceItem):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		PortInterfaceItem.__init__(self, mode)


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		ParameterInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		ParameterInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItem, InterfaceItemWithMode):
	def __init__(self, identifiers: Iterable[str], mode: Mode, subtype: Symbol, defaultExpression: ExpressionUnion = None, documentation: str = None):
		super().__init__(identifiers, subtype, defaultExpression, documentation)
		ParameterInterfaceItem.__init__(self)
		InterfaceItemWithMode.__init__(self, mode)


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItem):
	def __init__(self, identifiers: Iterable[str], subtype: Symbol, documentation: str = None):
		super().__init__(identifiers, subtype, documentation)
		ParameterInterfaceItem.__init__(self)
