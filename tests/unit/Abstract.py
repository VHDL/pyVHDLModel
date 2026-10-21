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
"""
Base-classes of the model are abstract: only their derived classes are instantiated.
"""
from pyTooling.MetaClasses     import AbstractClassError
from pyTooling.Testing         import Testcase

from pyVHDLModel.Association   import AssociationItem
from pyVHDLModel.Base          import BaseCase, BaseChoice
from pyVHDLModel.Common        import Statement
from pyVHDLModel.Concurrent    import (
	ConcurrentCase, ConcurrentChoice, ConcurrentSignalAssignment, ConcurrentStatement, GenerateBranch, GenerateStatement,
	Instantiation,
)
from pyVHDLModel.Configuration import EntityAspect
from pyVHDLModel.DesignUnit    import DesignUnit, PrimaryUnit, Reference, SecondaryUnit
from pyVHDLModel.Expression    import (
	AddingExpression, AggregateElement, Allocation, BaseExpression, BinaryExpression, BitStringLiteral, Literal,
	LogicalExpression, MatchingRelationalExpression, MultiplyingExpression, NumericLiteral, PhysicalLiteral,
	RangeExpression, RelationalExpression, RotateExpression, ShiftArithmeticExpression, ShiftExpression,
	ShiftLogicExpression, TernaryExpression, UnaryExpression,
)
from pyVHDLModel.Interface     import (
	InterfacePackage, ModeViewElement, ParameterSignalInterfaceItem, PortSignalInterfaceItem,
)
from pyVHDLModel.Name          import Name
from pyVHDLModel.Object        import BaseConstant, Obj
from pyVHDLModel.PSLModel      import PSLEntity, PSLPrimaryUnit
from pyVHDLModel.Predefined    import PredefinedLibrary, PredefinedPackage, PredefinedPackageBody
from pyVHDLModel.Sequential    import (
	Branch, CompoundStatement, LoopControlStatement, LoopStatement, SequentialChoice, SequentialStatement,
)
from pyVHDLModel.Subprogram    import Subprogram
from pyVHDLModel.Symbol        import ConstrainedCompositeSubtypeSymbol
from pyVHDLModel.Type          import BaseType, CompositeType, RangedScalarType, ScalarType, Type


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class AssociationClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Association`."""

	def test_AssociationItem(self) -> None:
		with self.assertRaises(AbstractClassError):
			AssociationItem()


class BaseClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Base`."""

	def test_BaseCase(self) -> None:
		with self.assertRaises(AbstractClassError):
			BaseCase()

	def test_BaseChoice(self) -> None:
		with self.assertRaises(AbstractClassError):
			BaseChoice()


class CommonClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Common`."""

	def test_Statement(self) -> None:
		with self.assertRaises(AbstractClassError):
			Statement()


class ConcurrentClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Concurrent`."""

	def test_ConcurrentCase(self) -> None:
		with self.assertRaises(AbstractClassError):
			ConcurrentCase()

	def test_ConcurrentChoice(self) -> None:
		with self.assertRaises(AbstractClassError):
			ConcurrentChoice()

	def test_ConcurrentSignalAssignment(self) -> None:
		with self.assertRaises(AbstractClassError):
			ConcurrentSignalAssignment()

	def test_ConcurrentStatement(self) -> None:
		with self.assertRaises(AbstractClassError):
			ConcurrentStatement()

	def test_GenerateBranch(self) -> None:
		with self.assertRaises(AbstractClassError):
			GenerateBranch()

	def test_GenerateStatement(self) -> None:
		with self.assertRaises(AbstractClassError):
			GenerateStatement()

	def test_Instantiation(self) -> None:
		with self.assertRaises(AbstractClassError):
			Instantiation()


class ConfigurationClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Configuration`."""

	def test_EntityAspect(self) -> None:
		with self.assertRaises(AbstractClassError):
			EntityAspect()


class DesignUnitClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.DesignUnit`."""

	def test_DesignUnit(self) -> None:
		with self.assertRaises(AbstractClassError):
			DesignUnit()

	def test_PrimaryUnit(self) -> None:
		with self.assertRaises(AbstractClassError):
			PrimaryUnit()

	def test_Reference(self) -> None:
		with self.assertRaises(AbstractClassError):
			Reference()

	def test_SecondaryUnit(self) -> None:
		with self.assertRaises(AbstractClassError):
			SecondaryUnit()


class ExpressionClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Expression`."""

	def test_AddingExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			AddingExpression()

	def test_AggregateElement(self) -> None:
		with self.assertRaises(AbstractClassError):
			AggregateElement()

	def test_Allocation(self) -> None:
		with self.assertRaises(AbstractClassError):
			Allocation()

	def test_BaseExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			BaseExpression()

	def test_BinaryExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			BinaryExpression()

	def test_BitStringLiteral(self) -> None:
		with self.assertRaises(AbstractClassError):
			BitStringLiteral()

	def test_Literal(self) -> None:
		with self.assertRaises(AbstractClassError):
			Literal()

	def test_LogicalExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			LogicalExpression()

	def test_MatchingRelationalExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			MatchingRelationalExpression()

	def test_MultiplyingExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			MultiplyingExpression()

	def test_NumericLiteral(self) -> None:
		with self.assertRaises(AbstractClassError):
			NumericLiteral()

	def test_PhysicalLiteral(self) -> None:
		with self.assertRaises(AbstractClassError):
			PhysicalLiteral()

	def test_RangeExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			RangeExpression()

	def test_RelationalExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			RelationalExpression()

	def test_RotateExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			RotateExpression()

	def test_ShiftArithmeticExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			ShiftArithmeticExpression()

	def test_ShiftExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			ShiftExpression()

	def test_ShiftLogicExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			ShiftLogicExpression()

	def test_TernaryExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			TernaryExpression()

	def test_UnaryExpression(self) -> None:
		with self.assertRaises(AbstractClassError):
			UnaryExpression()


class InterfaceClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Interface`."""

	def test_InterfacePackage(self) -> None:
		with self.assertRaises(AbstractClassError):
			InterfacePackage()

	def test_ModeViewElement(self) -> None:
		with self.assertRaises(AbstractClassError):
			ModeViewElement()

	def test_ParameterSignalInterfaceItem(self) -> None:
		with self.assertRaises(AbstractClassError):
			ParameterSignalInterfaceItem()

	def test_PortSignalInterfaceItem(self) -> None:
		with self.assertRaises(AbstractClassError):
			PortSignalInterfaceItem()


class NameClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Name`."""

	def test_Name(self) -> None:
		with self.assertRaises(AbstractClassError):
			Name()


class ObjectClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Object`."""

	def test_BaseConstant(self) -> None:
		with self.assertRaises(AbstractClassError):
			BaseConstant()

	def test_Obj(self) -> None:
		with self.assertRaises(AbstractClassError):
			Obj()


class PSLModelClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.PSLModel`."""

	def test_PSLEntity(self) -> None:
		with self.assertRaises(AbstractClassError):
			PSLEntity()

	def test_PSLPrimaryUnit(self) -> None:
		with self.assertRaises(AbstractClassError):
			PSLPrimaryUnit()


class PredefinedClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Predefined`."""

	def test_PredefinedLibrary(self) -> None:
		with self.assertRaises(AbstractClassError):
			PredefinedLibrary()

	def test_PredefinedPackage(self) -> None:
		with self.assertRaises(AbstractClassError):
			PredefinedPackage()

	def test_PredefinedPackageBody(self) -> None:
		with self.assertRaises(AbstractClassError):
			PredefinedPackageBody()


class SequentialClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Sequential`."""

	def test_Branch(self) -> None:
		with self.assertRaises(AbstractClassError):
			Branch()

	def test_CompoundStatement(self) -> None:
		with self.assertRaises(AbstractClassError):
			CompoundStatement()

	def test_LoopControlStatement(self) -> None:
		with self.assertRaises(AbstractClassError):
			LoopControlStatement()

	def test_LoopStatement(self) -> None:
		with self.assertRaises(AbstractClassError):
			LoopStatement()

	def test_SequentialChoice(self) -> None:
		with self.assertRaises(AbstractClassError):
			SequentialChoice()

	def test_SequentialStatement(self) -> None:
		with self.assertRaises(AbstractClassError):
			SequentialStatement()


class SubprogramClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Subprogram`."""

	def test_Subprogram(self) -> None:
		with self.assertRaises(AbstractClassError):
			Subprogram()


class SymbolClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Symbol`."""

	def test_ConstrainedCompositeSubtypeSymbol(self) -> None:
		with self.assertRaises(AbstractClassError):
			ConstrainedCompositeSubtypeSymbol()


class TypeClasses(Testcase):
	"""Abstract base-classes of :mod:`pyVHDLModel.Type`."""

	def test_BaseType(self) -> None:
		with self.assertRaises(AbstractClassError):
			BaseType()

	def test_CompositeType(self) -> None:
		with self.assertRaises(AbstractClassError):
			CompositeType()

	def test_RangedScalarType(self) -> None:
		with self.assertRaises(AbstractClassError):
			RangedScalarType()

	def test_ScalarType(self) -> None:
		with self.assertRaises(AbstractClassError):
			ScalarType()

	def test_Type(self) -> None:
		with self.assertRaises(AbstractClassError):
			Type()
