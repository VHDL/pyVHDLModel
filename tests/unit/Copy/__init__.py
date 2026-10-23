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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
#
"""
Copy tests: ``Copy()`` creates a new, parentless model element from the constructor of its class.

Each test checks the copy's content, that every owned child is a new object, the parent relation of the copy and its
children, and that a resolved reference still points to the same declaration.
"""
from types              import ModuleType
from typing             import Iterable

from pyVHDLModel.Base   import ModelEntity
from pyVHDLModel.Name   import SimpleName
from pyVHDLModel.Symbol import Symbol as SymbolBase, SimpleObjectOrFunctionCallSymbol


def _object(name: str) -> SimpleObjectOrFunctionCallSymbol:
	"""Reference to an object (or a parameterless function call) by a simple name, as used in expressions."""
	return SimpleObjectOrFunctionCallSymbol(SimpleName(name))


def _concreteModelClasses(module: ModuleType) -> list[type]:
	"""The model element classes a module defines, without abstract and mixin classes."""
	return [
		cls for cls in vars(module).values()
		if isinstance(cls, type)
		and cls.__module__ == module.__name__
		and issubclass(cls, (ModelEntity, SymbolBase))
		and not cls.__isAbstract__
		and not cls.__isMixin__
	]


def _copyAboveConstructor(classes: Iterable[type]) -> list[str]:
	"""
	The names of the classes inheriting ``Copy()`` from a class above the one defining their constructor.

	Such a ``Copy()`` would call a constructor with other parameters.
	"""
	names = []
	for cls in classes:
		mro = cls.__mro__
		copyIndex = next((index for index, base in enumerate(mro) if "Copy" in vars(base)), len(mro))
		constructorIndex = next(index for index, base in enumerate(mro) if "__init__" in vars(base))
		if copyIndex > constructorIndex:
			names.append(cls.__name__)

	return names
