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
Mutation tests for association lists: generic map aspects (:class:`~pyVHDLModel.Association.GenericMapAspectMixin`),
port map aspects (:class:`~pyVHDLModel.Association.PortMapAspectMixin`) and the parameter associations of procedure
calls (:class:`~pyVHDLModel.Common.ProcedureCallMixin`).

A named association may not repeat the formal of another named association, and positional associations precede the
named associations.
"""
from typing                    import Optional as Nullable

from pyTooling.Testing         import Testcase

from pyVHDLModel.Association   import GenericAssociationItem, PortAssociationItem, ParameterAssociationItem
from pyVHDLModel.Concurrent    import ComponentInstantiation, ConcurrentBlockStatement, ConcurrentProcedureCall
from pyVHDLModel.Configuration import BindingIndication
from pyVHDLModel.Exception     import AlreadyInDesignError, NotAChildError, AssociationOrderError
from pyVHDLModel.Exception     import DuplicateGenericAssociationError, DuplicatePortAssociationError
from pyVHDLModel.Exception     import DuplicateParameterAssociationError
from pyVHDLModel.Expression    import IntegerLiteral
from pyVHDLModel.Name          import SimpleName, ParenthesisName
from pyVHDLModel.Sequential    import SequentialProcedureCall
from pyVHDLModel.Symbol        import ComponentInstantiationSymbol, PossibleReference, Symbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _instance(
	genericAssociationItems: Nullable[list[GenericAssociationItem]] = None,
	portAssociationItems: Nullable[list[PortAssociationItem]] = None
) -> ComponentInstantiation:
	return ComponentInstantiation(
		"inst",
		ComponentInstantiationSymbol(SimpleName("comp")),
		genericAssociationItems,
		portAssociationItems
	)


def _procedureSymbol() -> Symbol:
	return Symbol(SimpleName("proc"), PossibleReference.Procedure)


def _call() -> SequentialProcedureCall:
	return SequentialProcedureCall(_procedureSymbol())


def _genericAssociation(formal: Nullable[str], value: int) -> GenericAssociationItem:
	return GenericAssociationItem(None if formal is None else SimpleName(formal), IntegerLiteral(value))


def _portAssociation(formal: Nullable[str], actual: str) -> PortAssociationItem:
	return PortAssociationItem(None if formal is None else SimpleName(formal), SimpleName(actual))


def _parameterAssociation(formal: Nullable[str], value: int) -> ParameterAssociationItem:
	return ParameterAssociationItem(None if formal is None else SimpleName(formal), IntegerLiteral(value))


class GenericAssociations(Testcase):
	def test_Add(self) -> None:
		instance = _instance()
		first = _genericAssociation(None, 1)
		second = _genericAssociation("B", 2)

		instance.AddGenericAssociationItem(first)
		instance.AddGenericAssociationItem(second)

		self.assertListEqual([first, second], instance.GenericAssociationItems)
		self.assertIs(instance, first.Parent)
		self.assertIs(instance, second.Parent)

	def test_Add_Block(self) -> None:
		block = ConcurrentBlockStatement("blk")
		association = _genericAssociation("G", 1)

		block.AddGenericAssociationItem(association)

		self.assertListEqual([association], block.GenericAssociationItems)
		self.assertIs(block, association.Parent)

	def test_Add_BindingIndication(self) -> None:
		binding = BindingIndication()
		association = _genericAssociation("G", 1)

		binding.AddGenericAssociationItem(association)

		self.assertListEqual([association], binding.GenericAssociationItems)
		self.assertIs(binding, association.Parent)

	def test_Add_None(self) -> None:
		instance = _instance()

		with self.assertRaises(ValueError) as context:
			instance.AddGenericAssociationItem(None)

		self.assertEqual("Parameter 'genericAssociationItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		instance = _instance()

		with self.assertRaises(TypeError) as context:
			instance.AddGenericAssociationItem(_portAssociation("p", "s"))

		self.assertEqual(
			"Parameter 'genericAssociationItem' is not of type 'GenericAssociationItem'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'pyVHDLModel.Association.PortAssociationItem'."], context.exception.__notes__)

	def test_Add_AlreadyInDesign(self) -> None:
		association = _genericAssociation("G", 1)
		first = ComponentInstantiation("first", ComponentInstantiationSymbol(SimpleName("comp")), [association])
		instance = _instance()

		with self.assertRaises(AlreadyInDesignError) as context:
			instance.AddGenericAssociationItem(association)

		self.assertEqual("GenericAssociationItem already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its ComponentInstantiation first."], context.exception.__notes__)
		self.assertIs(association, context.exception.Element)
		self.assertIs(first, context.exception.Parent)

	def test_Add_Duplicate(self) -> None:
		existing = _genericAssociation("g", 1)
		instance = _instance([existing])
		duplicate = _genericAssociation("G", 2)

		with self.assertRaises(DuplicateGenericAssociationError) as context:
			instance.AddGenericAssociationItem(duplicate)

		self.assertEqual("ComponentInstantiation already associates generic 'G'.", str(context.exception))
		self.assertListEqual(["Existing association is 'g => 1'."], context.exception.__notes__)
		self.assertEqual("G", context.exception.Identifier)
		self.assertEqual("g", context.exception.NormalizedIdentifier)
		self.assertIs(instance, context.exception.Parent)
		self.assertIs(duplicate, context.exception.Element)
		self.assertIs(existing, context.exception.Existing)
		self.assertListEqual([existing], instance.GenericAssociationItems)
		self.assertIsNone(duplicate.Parent)

	def test_Add_PartialAssociations(self) -> None:
		"""Formals other than a simple name, e.g. partial associations, aren't compared."""
		instance = _instance()
		first = GenericAssociationItem(ParenthesisName(SimpleName("G"), [IntegerLiteral(0)]), IntegerLiteral(1))
		second = GenericAssociationItem(ParenthesisName(SimpleName("G"), [IntegerLiteral(1)]), IntegerLiteral(2))

		instance.AddGenericAssociationItem(first)
		instance.AddGenericAssociationItem(second)

		self.assertListEqual([first, second], instance.GenericAssociationItems)

	def test_Add_Positionals(self) -> None:
		instance = _instance()
		first = _genericAssociation(None, 1)
		second = _genericAssociation(None, 1)

		instance.AddGenericAssociationItem(first)
		instance.AddGenericAssociationItem(second)

		self.assertListEqual([first, second], instance.GenericAssociationItems)

	def test_Add_PositionalAfterNamed(self) -> None:
		named = _genericAssociation("G", 1)
		instance = _instance([named])
		positional = _genericAssociation(None, 2)

		with self.assertRaises(AssociationOrderError) as context:
			instance.AddGenericAssociationItem(positional)

		self.assertEqual("Positional generic association can't follow named association 'G => 1'.", str(context.exception))
		self.assertListEqual(
			["Insert it before the first named association, or name its formal."],
			context.exception.__notes__
		)
		self.assertIs(instance, context.exception.Parent)
		self.assertIs(positional, context.exception.Element)
		self.assertIs(named, context.exception.Existing)
		self.assertListEqual([named], instance.GenericAssociationItems)
		self.assertIsNone(positional.Parent)

	def test_Insert_Start(self) -> None:
		b = _genericAssociation("B", 2)
		c = _genericAssociation("C", 3)
		instance = _instance([b, c])
		a = _genericAssociation("A", 1)

		instance.InsertGenericAssociationItem(0, a)

		self.assertListEqual([a, b, c], instance.GenericAssociationItems)
		self.assertIs(instance, a.Parent)

	def test_Insert_Middle(self) -> None:
		a = _genericAssociation("A", 1)
		c = _genericAssociation("C", 3)
		instance = _instance([a, c])
		b = _genericAssociation("B", 2)

		instance.InsertGenericAssociationItem(1, b)

		self.assertListEqual([a, b, c], instance.GenericAssociationItems)

	def test_Insert_End(self) -> None:
		a = _genericAssociation("A", 1)
		b = _genericAssociation("B", 2)
		instance = _instance([a, b])
		c = _genericAssociation("C", 3)

		instance.InsertGenericAssociationItem(2, c)

		self.assertListEqual([a, b, c], instance.GenericAssociationItems)

	def test_Insert_Negative(self) -> None:
		a = _genericAssociation("A", 1)
		c = _genericAssociation("C", 3)
		instance = _instance([a, c])
		b = _genericAssociation("B", 2)

		instance.InsertGenericAssociationItem(-1, b)

		self.assertListEqual([a, b, c], instance.GenericAssociationItems)
		self.assertIs(instance, b.Parent)

	def test_Insert_PositionalBeforeNamed(self) -> None:
		named = _genericAssociation("B", 2)
		instance = _instance([named])
		positional = _genericAssociation(None, 1)

		instance.InsertGenericAssociationItem(0, positional)

		self.assertListEqual([positional, named], instance.GenericAssociationItems)

	def test_Insert_PositionalAfterNamed_Negative(self) -> None:
		first = _genericAssociation("A", 1)
		second = _genericAssociation("B", 2)
		instance = _instance([first, second])
		positional = _genericAssociation(None, 3)

		with self.assertRaises(AssociationOrderError) as context:
			instance.InsertGenericAssociationItem(-1, positional)

		self.assertEqual("Positional generic association can't follow named association 'A => 1'.", str(context.exception))
		self.assertIs(first, context.exception.Existing)
		self.assertIsNone(positional.Parent)

	def test_Insert_NamedBeforePositional(self) -> None:
		positional = _genericAssociation(None, 1)
		instance = _instance([positional])
		named = _genericAssociation("B", 2)

		with self.assertRaises(AssociationOrderError) as context:
			instance.InsertGenericAssociationItem(0, named)

		self.assertEqual("Named generic association can't precede positional association '1'.", str(context.exception))
		self.assertListEqual(["Insert it after the last positional association."], context.exception.__notes__)
		self.assertIs(instance, context.exception.Parent)
		self.assertIs(named, context.exception.Element)
		self.assertIs(positional, context.exception.Existing)
		self.assertListEqual([positional], instance.GenericAssociationItems)
		self.assertIsNone(named.Parent)

	def test_Insert_IndexNone(self) -> None:
		instance = _instance()

		with self.assertRaises(ValueError) as context:
			instance.InsertGenericAssociationItem(None, _genericAssociation("G", 1))

		self.assertEqual("Parameter 'index' is None.", str(context.exception))

	def test_Insert_IndexWrongType(self) -> None:
		instance = _instance()

		with self.assertRaises(TypeError) as context:
			instance.InsertGenericAssociationItem("0", _genericAssociation("G", 1))

		self.assertEqual("Parameter 'index' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Insert_OutOfRange(self) -> None:
		instance = _instance([_genericAssociation("A", 1)])
		association = _genericAssociation("B", 2)

		with self.assertRaises(ValueError) as context:
			instance.InsertGenericAssociationItem(5, association)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '5'."], context.exception.__notes__)
		self.assertIsNone(association.Parent)

	def test_Insert_Negative_OutOfRange(self) -> None:
		instance = _instance([_genericAssociation("A", 1)])
		association = _genericAssociation("B", 2)

		with self.assertRaises(ValueError) as context:
			instance.InsertGenericAssociationItem(-2, association)

		self.assertEqual("Parameter 'index' is out of range -1..1.", str(context.exception))
		self.assertListEqual(["Got value '-2'."], context.exception.__notes__)
		self.assertIsNone(association.Parent)

	def test_Remove(self) -> None:
		a = _genericAssociation("A", 1)
		b = _genericAssociation("B", 2)
		instance = _instance([a, b])

		instance.RemoveGenericAssociationItem(a)

		self.assertListEqual([b], instance.GenericAssociationItems)
		self.assertIsNone(a.Parent)
		self.assertEqual("A", a.Formal.Identifier)

	def test_Remove_Reinsert(self) -> None:
		"""A removed association can be inserted again, e.g. at another position."""
		a = _genericAssociation("A", 1)
		b = _genericAssociation("B", 2)
		instance = _instance([a, b])

		instance.RemoveGenericAssociationItem(a)
		instance.AddGenericAssociationItem(a)

		self.assertListEqual([b, a], instance.GenericAssociationItems)
		self.assertIs(instance, a.Parent)

	def test_Remove_None(self) -> None:
		instance = _instance()

		with self.assertRaises(ValueError) as context:
			instance.RemoveGenericAssociationItem(None)

		self.assertEqual("Parameter 'genericAssociationItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		instance = _instance()

		with self.assertRaises(TypeError) as context:
			instance.RemoveGenericAssociationItem(_portAssociation("p", "s"))

		self.assertEqual(
			"Parameter 'genericAssociationItem' is not of type 'GenericAssociationItem'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'pyVHDLModel.Association.PortAssociationItem'."], context.exception.__notes__)

	def test_Remove_NotAChild(self) -> None:
		instance = _instance()
		association = _genericAssociation("G", 1)

		with self.assertRaises(NotAChildError) as context:
			instance.RemoveGenericAssociationItem(association)

		self.assertEqual(
			"GenericAssociationItem is not a generic association of this ComponentInstantiation.",
			str(context.exception)
		)
		self.assertIs(association, context.exception.Element)
		self.assertIs(instance, context.exception.Parent)


class PortAssociations(Testcase):
	def test_Add(self) -> None:
		instance = _instance()
		first = _portAssociation(None, "s1")
		second = _portAssociation("b", "s2")

		instance.AddPortAssociationItem(first)
		instance.AddPortAssociationItem(second)

		self.assertListEqual([first, second], instance.PortAssociationItems)
		self.assertIs(instance, first.Parent)
		self.assertIs(instance, second.Parent)

	def test_Add_Block(self) -> None:
		block = ConcurrentBlockStatement("blk")
		association = _portAssociation("p", "s")

		block.AddPortAssociationItem(association)

		self.assertListEqual([association], block.PortAssociationItems)
		self.assertIs(block, association.Parent)

	def test_Add_None(self) -> None:
		instance = _instance()

		with self.assertRaises(ValueError) as context:
			instance.AddPortAssociationItem(None)

		self.assertEqual("Parameter 'portAssociationItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		instance = _instance()

		with self.assertRaises(TypeError) as context:
			instance.AddPortAssociationItem(_genericAssociation("G", 1))

		self.assertEqual("Parameter 'portAssociationItem' is not of type 'PortAssociationItem'.", str(context.exception))
		self.assertListEqual(["Got type 'pyVHDLModel.Association.GenericAssociationItem'."], context.exception.__notes__)

	def test_Add_AlreadyInDesign(self) -> None:
		association = _portAssociation("p", "s")
		block = ConcurrentBlockStatement("blk", portAssociationItems=[association])
		instance = _instance()

		with self.assertRaises(AlreadyInDesignError) as context:
			instance.AddPortAssociationItem(association)

		self.assertEqual("PortAssociationItem already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its ConcurrentBlockStatement first."], context.exception.__notes__)
		self.assertIs(block, context.exception.Parent)

	def test_Add_Duplicate(self) -> None:
		existing = _portAssociation("Clock", "clk")
		instance = _instance(portAssociationItems=[existing])
		duplicate = _portAssociation("clock", "clk2")

		with self.assertRaises(DuplicatePortAssociationError) as context:
			instance.AddPortAssociationItem(duplicate)

		self.assertEqual("ComponentInstantiation already associates port 'clock'.", str(context.exception))
		self.assertListEqual(["Existing association is 'Clock => clk'."], context.exception.__notes__)
		self.assertIs(existing, context.exception.Existing)
		self.assertIsNone(duplicate.Parent)

	def test_Add_PositionalAfterNamed(self) -> None:
		named = _portAssociation("a", "s1")
		instance = _instance(portAssociationItems=[named])
		positional = _portAssociation(None, "s2")

		with self.assertRaises(AssociationOrderError) as context:
			instance.AddPortAssociationItem(positional)

		self.assertEqual("Positional port association can't follow named association 'a => s1'.", str(context.exception))
		self.assertIsNone(positional.Parent)

	def test_Insert(self) -> None:
		a = _portAssociation("a", "s1")
		c = _portAssociation("c", "s3")
		instance = _instance(portAssociationItems=[a, c])
		b = _portAssociation("b", "s2")

		instance.InsertPortAssociationItem(1, b)

		self.assertListEqual([a, b, c], instance.PortAssociationItems)
		self.assertIs(instance, b.Parent)

	def test_Insert_NamedBeforePositional(self) -> None:
		positional = _portAssociation(None, "s1")
		instance = _instance(portAssociationItems=[positional])
		named = _portAssociation("b", "s2")

		with self.assertRaises(AssociationOrderError) as context:
			instance.InsertPortAssociationItem(0, named)

		self.assertEqual("Named port association can't precede positional association 's1'.", str(context.exception))
		self.assertIsNone(named.Parent)

	def test_Remove(self) -> None:
		a = _portAssociation("a", "s1")
		instance = _instance(portAssociationItems=[a])

		instance.RemovePortAssociationItem(a)

		self.assertListEqual([], instance.PortAssociationItems)
		self.assertIsNone(a.Parent)

	def test_Remove_NotAChild(self) -> None:
		instance = _instance()
		association = _portAssociation("p", "s")

		with self.assertRaises(NotAChildError) as context:
			instance.RemovePortAssociationItem(association)

		self.assertEqual(
			"PortAssociationItem is not a port association of this ComponentInstantiation.",
			str(context.exception)
		)


class ParameterAssociations(Testcase):
	def test_Add(self) -> None:
		call = _call()
		first = _parameterAssociation(None, 1)
		second = _parameterAssociation("y", 2)

		call.AddParameterAssociationItem(first)
		call.AddParameterAssociationItem(second)

		self.assertListEqual([first, second], call.ParameterAssociationItems)
		self.assertIs(call, first.Parent)
		self.assertIs(call, second.Parent)

	def test_Add_ConcurrentProcedureCall(self) -> None:
		call = ConcurrentProcedureCall("call", _procedureSymbol())
		association = _parameterAssociation("x", 1)

		call.AddParameterAssociationItem(association)

		self.assertListEqual([association], call.ParameterAssociationItems)
		self.assertIs(call, association.Parent)

	def test_Add_None(self) -> None:
		call = _call()

		with self.assertRaises(ValueError) as context:
			call.AddParameterAssociationItem(None)

		self.assertEqual("Parameter 'parameterAssociationItem' is None.", str(context.exception))

	def test_Add_WrongType(self) -> None:
		call = _call()

		with self.assertRaises(TypeError) as context:
			call.AddParameterAssociationItem(_genericAssociation("G", 1))

		self.assertEqual(
			"Parameter 'parameterAssociationItem' is not of type 'ParameterAssociationItem'.",
			str(context.exception)
		)
		self.assertListEqual(["Got type 'pyVHDLModel.Association.GenericAssociationItem'."], context.exception.__notes__)

	def test_Add_AlreadyInDesign(self) -> None:
		association = _parameterAssociation("x", 1)
		first = SequentialProcedureCall(_procedureSymbol(), [association])
		call = _call()

		with self.assertRaises(AlreadyInDesignError) as context:
			call.AddParameterAssociationItem(association)

		self.assertEqual("ParameterAssociationItem already has a parent.", str(context.exception))
		self.assertListEqual(["Remove it from its SequentialProcedureCall first."], context.exception.__notes__)
		self.assertIs(first, context.exception.Parent)

	def test_Add_Duplicate(self) -> None:
		existing = _parameterAssociation("x", 1)
		call = SequentialProcedureCall(_procedureSymbol(), [existing])
		duplicate = _parameterAssociation("X", 2)

		with self.assertRaises(DuplicateParameterAssociationError) as context:
			call.AddParameterAssociationItem(duplicate)

		self.assertEqual("SequentialProcedureCall already associates parameter 'X'.", str(context.exception))
		self.assertListEqual(["Existing association is 'x => 1'."], context.exception.__notes__)
		self.assertIs(existing, context.exception.Existing)
		self.assertIsNone(duplicate.Parent)

	def test_Add_PositionalAfterNamed(self) -> None:
		named = _parameterAssociation("x", 1)
		call = SequentialProcedureCall(_procedureSymbol(), [named])
		positional = _parameterAssociation(None, 2)

		with self.assertRaises(AssociationOrderError) as context:
			call.AddParameterAssociationItem(positional)

		self.assertEqual(
			"Positional parameter association can't follow named association 'x => 1'.",
			str(context.exception)
		)
		self.assertIsNone(positional.Parent)

	def test_Insert(self) -> None:
		positional = _parameterAssociation(None, 1)
		named = _parameterAssociation("y", 3)
		call = SequentialProcedureCall(_procedureSymbol(), [positional, named])
		middle = _parameterAssociation(None, 2)

		call.InsertParameterAssociationItem(1, middle)

		self.assertListEqual([positional, middle, named], call.ParameterAssociationItems)
		self.assertIs(call, middle.Parent)

	def test_Insert_NamedBeforePositional(self) -> None:
		positional = _parameterAssociation(None, 1)
		call = SequentialProcedureCall(_procedureSymbol(), [positional])
		named = _parameterAssociation("y", 2)

		with self.assertRaises(AssociationOrderError) as context:
			call.InsertParameterAssociationItem(-1, named)

		self.assertEqual("Named parameter association can't precede positional association '1'.", str(context.exception))
		self.assertIsNone(named.Parent)

	def test_Remove(self) -> None:
		association = _parameterAssociation("x", 1)
		call = SequentialProcedureCall(_procedureSymbol(), [association])

		call.RemoveParameterAssociationItem(association)

		self.assertListEqual([], call.ParameterAssociationItems)
		self.assertIsNone(association.Parent)

	def test_Remove_None(self) -> None:
		call = _call()

		with self.assertRaises(ValueError) as context:
			call.RemoveParameterAssociationItem(None)

		self.assertEqual("Parameter 'parameterAssociationItem' is None.", str(context.exception))

	def test_Remove_WrongType(self) -> None:
		call = _call()

		with self.assertRaises(TypeError) as context:
			call.RemoveParameterAssociationItem(_portAssociation("p", "s"))

		self.assertEqual(
			"Parameter 'parameterAssociationItem' is not of type 'ParameterAssociationItem'.",
			str(context.exception)
		)

	def test_Remove_NotAChild(self) -> None:
		call = _call()
		association = _parameterAssociation("x", 1)

		with self.assertRaises(NotAChildError) as context:
			call.RemoveParameterAssociationItem(association)

		self.assertEqual(
			"ParameterAssociationItem is not a parameter association of this SequentialProcedureCall.",
			str(context.exception)
		)

