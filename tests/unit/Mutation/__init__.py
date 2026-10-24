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
"""
Mutation tests: adding, inserting and removing model entities after construction.

Each test checks the parent relation, the order of the collection and the namespace of the parent, as a mutator
updates all of them.
"""
from typing                 import Any

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Interface  import GenericConstantInterfaceItem, PortSimpleSignalInterfaceItem, \
                                   ParameterConstantInterfaceItem
from pyVHDLModel.Object     import Constant, Signal, Variable
from pyVHDLModel.Subprogram import Function, Procedure

from tests.unit             import _subtypeSymbol


def _generic(*identifiers: str) -> GenericConstantInterfaceItem:
	return GenericConstantInterfaceItem(identifiers, Mode.Default, _subtypeSymbol("positive"))


def _port(*identifiers: str) -> PortSimpleSignalInterfaceItem:
	return PortSimpleSignalInterfaceItem(identifiers, Mode.In, _subtypeSymbol("std_logic"))


def _parameter(*identifiers: str) -> ParameterConstantInterfaceItem:
	return ParameterConstantInterfaceItem(identifiers, Mode.In, _subtypeSymbol("integer"))


def _constant(*identifiers: str) -> Constant:
	return Constant(identifiers, _subtypeSymbol("natural"))


def _signal(*identifiers: str) -> Signal:
	return Signal(identifiers, _subtypeSymbol("std_logic"))


def _variable(*identifiers: str) -> Variable:
	return Variable(identifiers, _subtypeSymbol("natural"))


def _function(identifier: str) -> Function:
	return Function(identifier, _subtypeSymbol("integer"))


def _procedure(identifier: str) -> Procedure:
	return Procedure(identifier)


_LOOKUP_TABLES = (
	"_types", "_subtypes", "_constants", "_signals", "_variables", "_sharedVariables", "_files", "_functions",
	"_procedures", "_components", "_deferredConstants"
)


def _indexState(region) -> dict[str, Any]:
	"""Copy the lookup tables and the namespace of a declarative region."""
	state = {"namespace": dict(region._namespace._elements)}
	for name in _LOOKUP_TABLES:
		table = getattr(region, name, None)
		if table is not None:
			state[name] = {key: list(entry) if isinstance(entry, list) else entry for key, entry in table.items()}

	return state


def _reindexed(region) -> tuple[dict[str, Any], dict[str, Any]]:
	"""Return the lookup tables and the namespace of a declarative region before and after indexing it again."""
	before = _indexState(region)
	region.IndexDeclaredItems()
	return before, _indexState(region)
