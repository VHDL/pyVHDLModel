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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
"""Tests for pyVHDLModel.Declaration."""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import ReservedWord
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import ConstrainedArraySubtypeSymbol, Symbol, PossibleReference, \
                                    SimpleObjectOrFunctionCallSymbol
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Declaration import Alias, AttributeSpecification, EntityClass


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class EntityClassEnum(Testcase):
	def test_ReservedWord(self) -> None:
		"""Every entity class but ``Others`` has a reserved word of the same name."""
		self.assertIsNone(EntityClass.Others.ReservedWord)
		for entityClass in EntityClass:
			if entityClass is EntityClass.Others:
				continue

			with self.subTest(entityClass=entityClass.name):
				self.assertIs(ReservedWord[entityClass.name], entityClass.ReservedWord)


class Aliases(Testcase):
	"""
	Regression tests: Alias previously had no field at all for what's being aliased - only its own
	identifier and documentation. ``alias b is s;`` lost the fact that ``b`` aliases ``s`` entirely.

	Name is a Symbol (like every other cross-reference in the model), not a bare Name - see the
	class docstring for why there is no single fixed PossibleReference value for it.
	"""

	def test_WithoutSubtype(self) -> None:
		"""``alias b is s;``"""
		name = Symbol(SimpleName("s"), PossibleReference.PackageMember | PossibleReference.EnumLiteral)
		alias = Alias("b", name)

		self.assertEqual("b", alias.Identifier)
		self.assertIs(name, alias.Name)
		self.assertIsNone(alias.Subtype)

	def test_WithSubtype(self) -> None:
		"""``alias a : bit_vector(3 downto 0) is s(3 downto 0);`` - with an explicit subtype, the LRM
		restricts this to referencing an object."""
		name = Symbol(SimpleName("s"), PossibleReference.Object)
		subtype = ConstrainedArraySubtypeSymbol(SimpleName("bit_vector"), [])
		alias = Alias("a", name, subtype)

		self.assertEqual("a", alias.Identifier)
		self.assertIs(name, alias.Name)
		self.assertIs(subtype, alias.Subtype)


class AttributeSpecifications(Testcase):
	def test_Construction(self) -> None:
		"""``attribute bits of byte : subtype is 8;``"""
		identifier =    SimpleName("byte")
		attribute =     SimpleName("bits")
		expression =    IntegerLiteral(8)
		specification = AttributeSpecification([identifier], attribute, EntityClass.Subtype, expression)

		self.assertListEqual([identifier], specification.Identifiers)
		self.assertIs(attribute, specification.Attribute)
		self.assertIs(EntityClass.Subtype, specification.EntityClass)
		self.assertIs(expression, specification.Expression)
		self.assertIs(specification, identifier.Parent)
		self.assertIs(specification, attribute.Parent)
		self.assertIs(specification, expression.Parent)

	def test_Construction_SymbolExpression(self) -> None:
		"""``attribute bits of byte : subtype is WIDTH;``"""
		expression =    SimpleObjectOrFunctionCallSymbol(SimpleName("WIDTH"))
		specification = AttributeSpecification([SimpleName("byte")], SimpleName("bits"), EntityClass.Subtype, expression)

		self.assertIs(expression, specification.Expression)
		self.assertIs(specification, expression.Parent)
