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

"""Shared construction helpers for the unit tests.

Building a model object needs a symbol, a subtype and often a name, which every test module was
re-declaring. Names are always passed explicitly - a helper that defaults one hides what a test
actually builds.
"""
from typing import Type, TypeVar

from pyVHDLModel.Base   import ModelEntity
from pyVHDLModel.Name   import SimpleName
from pyVHDLModel.Object import Signal, Variable
from pyVHDLModel.Symbol import EntitySymbol, SignalSymbol, SimpleSubtypeSymbol, VariableSymbol


_Warning = TypeVar("_Warning", bound=BaseException)


class _Element(ModelEntity):
	"""A concrete model element: :class:`~pyVHDLModel.Base.ModelEntity` is abstract."""


def _subtypeSymbol(name: str) -> SimpleSubtypeSymbol:
	"""Reference to a subtype, for anything needing a subtype indication."""
	return SimpleSubtypeSymbol(SimpleName(name))


def _entitySymbol(name: str) -> EntitySymbol:
	"""
	Reference to an entity.

	An architecture references its entity.
	"""
	return EntitySymbol(SimpleName(name))


def _signalSymbol(name: str) -> SignalSymbol:
	"""
	Reference to a signal.

	An assignment target is such a reference.
	"""
	return SignalSymbol(SimpleName(name))


def _variableSymbol(name: str) -> VariableSymbol:
	"""
	Reference to a variable.

	An assignment target is such a reference.
	"""
	return VariableSymbol(SimpleName(name))


def _signal(identifier: str, subtypeName: str) -> Signal:
	"""A signal declaration."""
	return Signal((identifier, ), _subtypeSymbol(subtypeName))


def _variable(identifier: str, subtypeName: str) -> Variable:
	"""A variable declaration."""
	return Variable((identifier, ), _subtypeSymbol(subtypeName))


def _warningsOfType(collector, warningType: Type[_Warning]) -> list[_Warning]:
	"""The warnings of one type collected by a :class:`~pyTooling.Warning.WarningCollector`."""
	return [warning for warning in collector if isinstance(warning, warningType)]
