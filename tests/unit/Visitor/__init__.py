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
Shared helpers for the tests of the visitor protocol (:mod:`pyVHDLModel.Visitor`).
"""
from typing               import Any, List, Tuple

from pyTooling.Decorators import readonly

from pyVHDLModel.Visitor  import Visitor


class Recorder(Visitor):
	"""A visitor recording the events of a walk as pairs of event name and element."""

	_events: List[Tuple[str, Any]]  #: List of recorded events.

	def __init__(self) -> None:
		super().__init__()

		self._events = []

	@readonly
	def Events(self) -> List[Tuple[str, Any]]:
		"""Recorded events."""
		return self._events

	def VisitUnknown(self, element: Any) -> None:
		self._events.append(("VisitUnknown", element))

	def DepartUnknown(self, element: Any) -> None:
		self._events.append(("DepartUnknown", element))

	def VisitLeftParenthesis(self, element: Any) -> None:
		self._events.append(("VisitLeftParenthesis", element))

	def VisitComma(self, element: Any) -> None:
		self._events.append(("VisitComma", element))

	def VisitArrow(self, element: Any) -> None:
		self._events.append(("VisitArrow", element))

	def VisitIntegerLiteral(self, literal: Any) -> None:
		self._events.append(("VisitIntegerLiteral", literal))

	def DepartIntegerLiteral(self, literal: Any) -> None:
		self._events.append(("DepartIntegerLiteral", literal))

	def VisitSimpleName(self, name: Any) -> None:
		self._events.append(("VisitSimpleName", name))

	def DepartSimpleName(self, name: Any) -> None:
		self._events.append(("DepartSimpleName", name))

	def VisitSelectedName(self, name: Any) -> None:
		self._events.append(("VisitSelectedName", name))

	def DepartSelectedName(self, name: Any) -> None:
		self._events.append(("DepartSelectedName", name))

	def VisitIndexedName(self, name: Any) -> None:
		self._events.append(("VisitIndexedName", name))

	def DepartIndexedName(self, name: Any) -> None:
		self._events.append(("DepartIndexedName", name))

	def VisitParenthesisName(self, name: Any) -> None:
		self._events.append(("VisitParenthesisName", name))

	def DepartParenthesisName(self, name: Any) -> None:
		self._events.append(("DepartParenthesisName", name))

	def VisitSymbol(self, symbol: Any) -> None:
		self._events.append(("VisitSymbol", symbol))

	def DepartSymbol(self, symbol: Any) -> None:
		self._events.append(("DepartSymbol", symbol))

	def VisitAssociationItem(self, item: Any) -> None:
		self._events.append(("VisitAssociationItem", item))

	def DepartAssociationItem(self, item: Any) -> None:
		self._events.append(("DepartAssociationItem", item))
