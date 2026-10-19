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
This module contains the base-class of all visitors walking a VHDL language model.

A model element walks itself: :meth:`ModelEntity.Visit(visitor) <pyVHDLModel.Base.ModelEntity.Visit>` reports the
element and then its children in source order as events to the visitor. A parser's subclass of a model class (e.g. from
``pyGHDL.dom``) inherits the walk of that model class.

.. rubric:: Events

``Visit<Class>(element)``
   The walk enters an element of class ``<Class>``, before its first child.

``Depart<Class>(element)``
   The walk leaves an element of class ``<Class>``, after its last child.

``Visit<Token>(element)``
   The walk passes a token of the element between two of its parts, which is not a model element itself. The event is
   named after the token as IEEE Std 1076-2008 names it in clauses 15.2 and 15.3, e.g. ``VisitArrow`` for ``=>``.

``VisitUnknown(element)`` and ``DepartUnknown(element)``
   The walk reaches an element of a class without a walk of its own. Its children are not walked.
"""
from __future__                import annotations

from typing                    import TYPE_CHECKING

from pyTooling.Decorators      import export
from pyTooling.MetaClasses     import ExtendedType

if TYPE_CHECKING:
	from pyVHDLModel.Association import AssociationItem
	from pyVHDLModel.Base        import ModelEntity
	from pyVHDLModel.Expression  import (
		NullLiteral, EnumerationLiteral, IntegerLiteral, FloatingPointLiteral, PhysicalIntegerLiteral,
		PhysicalFloatingLiteral, CharacterLiteral, StringLiteral, BitStringLiteral
	)
	from pyVHDLModel.Name        import (
		SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, AttributeName, AllName, OpenName
	)
	from pyVHDLModel.Symbol      import Symbol


@export
class Visitor(metaclass=ExtendedType, slots=True):
	"""
	Base-class of all visitors walking a VHDL language model.

	Every event does nothing: a visitor overrides the events it needs. The events are described in
	:mod:`pyVHDLModel.Visitor`.
	"""

	def VisitUnknown(self, element: ModelEntity | Symbol) -> None:
		"""
		Visit a model element of a class without a walk of its own.

		:param element: The model element.
		"""

	def DepartUnknown(self, element: ModelEntity | Symbol) -> None:
		"""
		Depart from a model element of a class without a walk of its own.

		:param element: The model element.
		"""

	def VisitLeftParenthesis(self, element: IndexedName | ParenthesisName) -> None:
		"""
		Visit the left parenthesis between the prefix and the parenthesized list of an element.

		:param element: The element enclosing the list.
		"""

	def VisitComma(self, element: IndexedName | ParenthesisName) -> None:
		"""
		Visit the comma between two items of a list.

		:param element: The element containing the list.
		"""

	def VisitArrow(self, element: AssociationItem) -> None:
		"""
		Visit the arrow (``=>``) between a choice or formal and its value.

		:param element: The element containing the arrow.
		"""

	def VisitNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Visit a null literal.

		:param literal: The null literal.
		"""

	def DepartNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Depart from a null literal.

		:param literal: The null literal.
		"""

	def VisitEnumerationLiteral(self, literal: EnumerationLiteral) -> None:
		"""
		Visit an enumeration literal.

		:param literal: The enumeration literal.
		"""

	def DepartEnumerationLiteral(self, literal: EnumerationLiteral) -> None:
		"""
		Depart from an enumeration literal.

		:param literal: The enumeration literal.
		"""

	def VisitIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Visit an integer literal.

		:param literal: The integer literal.
		"""

	def DepartIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Depart from an integer literal.

		:param literal: The integer literal.
		"""

	def VisitFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Visit a floating-point literal.

		:param literal: The floating-point literal.
		"""

	def DepartFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Depart from a floating-point literal.

		:param literal: The floating-point literal.
		"""

	def VisitPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Visit a physical literal with an integer value.

		:param literal: The physical literal.
		"""

	def DepartPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Depart from a physical literal with an integer value.

		:param literal: The physical literal.
		"""

	def VisitPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Visit a physical literal with a floating-point value.

		:param literal: The physical literal.
		"""

	def DepartPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Depart from a physical literal with a floating-point value.

		:param literal: The physical literal.
		"""

	def VisitCharacterLiteral(self, literal: CharacterLiteral) -> None:
		"""
		Visit a character literal.

		:param literal: The character literal.
		"""

	def DepartCharacterLiteral(self, literal: CharacterLiteral) -> None:
		"""
		Depart from a character literal.

		:param literal: The character literal.
		"""

	def VisitStringLiteral(self, literal: StringLiteral) -> None:
		"""
		Visit a string literal.

		:param literal: The string literal.
		"""

	def DepartStringLiteral(self, literal: StringLiteral) -> None:
		"""
		Depart from a string literal.

		:param literal: The string literal.
		"""

	def VisitBitStringLiteral(self, literal: BitStringLiteral) -> None:
		"""
		Visit a bit string literal.

		:param literal: The bit string literal.
		"""

	def DepartBitStringLiteral(self, literal: BitStringLiteral) -> None:
		"""
		Depart from a bit string literal.

		:param literal: The bit string literal.
		"""

	def VisitSimpleName(self, name: SimpleName) -> None:
		"""
		Visit a simple name.

		:param name: The simple name.
		"""

	def DepartSimpleName(self, name: SimpleName) -> None:
		"""
		Depart from a simple name.

		:param name: The simple name.
		"""

	def VisitSelectedName(self, name: SelectedName) -> None:
		"""
		Visit a selected name, before its prefix.

		:param name: The selected name.
		"""

	def DepartSelectedName(self, name: SelectedName) -> None:
		"""
		Depart from a selected name, after its prefix.

		:param name: The selected name.
		"""

	def VisitAllName(self, name: AllName) -> None:
		"""
		Visit a selected name with suffix ``all``, before its prefix.

		:param name: The ``all`` name.
		"""

	def DepartAllName(self, name: AllName) -> None:
		"""
		Depart from a selected name with suffix ``all``, after its prefix.

		:param name: The ``all`` name.
		"""

	def VisitAttributeName(self, name: AttributeName) -> None:
		"""
		Visit an attribute name, before its prefix.

		:param name: The attribute name.
		"""

	def DepartAttributeName(self, name: AttributeName) -> None:
		"""
		Depart from an attribute name, after its prefix.

		:param name: The attribute name.
		"""

	def VisitIndexedName(self, name: IndexedName) -> None:
		"""
		Visit an indexed name, before its prefix.

		:param name: The indexed name.
		"""

	def DepartIndexedName(self, name: IndexedName) -> None:
		"""
		Depart from an indexed name, after its last index.

		:param name: The indexed name.
		"""

	def VisitParenthesisName(self, name: ParenthesisName) -> None:
		"""
		Visit a name followed by a parenthesized association list, before its prefix.

		:param name: The parenthesis name.
		"""

	def DepartParenthesisName(self, name: ParenthesisName) -> None:
		"""
		Depart from a name followed by a parenthesized association list, after its last association.

		:param name: The parenthesis name.
		"""

	def VisitSlicedName(self, name: SlicedName) -> None:
		"""
		Visit a sliced name, before its prefix.

		:param name: The sliced name.
		"""

	def DepartSlicedName(self, name: SlicedName) -> None:
		"""
		Depart from a sliced name, after its prefix.

		:param name: The sliced name.
		"""

	def VisitOpenName(self, name: OpenName) -> None:
		"""
		Visit the reserved word ``open``.

		:param name: The ``open`` name.
		"""

	def DepartOpenName(self, name: OpenName) -> None:
		"""
		Depart from the reserved word ``open``.

		:param name: The ``open`` name.
		"""

	def VisitSymbol(self, symbol: Symbol) -> None:
		"""
		Visit a symbol, before its name.

		:param symbol: The symbol.
		"""

	def DepartSymbol(self, symbol: Symbol) -> None:
		"""
		Depart from a symbol, after its name.

		:param symbol: The symbol.
		"""

	def VisitAssociationItem(self, item: AssociationItem) -> None:
		"""
		Visit an association item, before its formal or, if positional, its actual.

		:param item: The association item.
		"""

	def DepartAssociationItem(self, item: AssociationItem) -> None:
		"""
		Depart from an association item, after its actual.

		:param item: The association item.
		"""
