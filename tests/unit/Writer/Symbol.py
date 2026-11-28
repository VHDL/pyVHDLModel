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
"""Tests for writing symbols and association items with pyVHDLModel.Formatting.VHDL."""
from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import GenericAssociationItem, PortAssociationItem, ParameterAssociationItem
from pyVHDLModel.Base            import Direction, SimpleRange
from pyVHDLModel.Exception       import VHDLWriterError
from pyVHDLModel.Expression      import CharacterLiteral, IntegerLiteral
from pyVHDLModel.Formatting.VHDL import VHDLWriter
from pyVHDLModel.Name            import SimpleName, ParenthesisName, SelectedName, AllName, OpenName
from pyVHDLModel.Object          import Signal
from pyVHDLModel.Symbol          import LibraryReferenceSymbol, AllPackageMembersReferenceSymbol, \
                                        EntityInstantiationSymbol, SignalSymbol, SimpleSubtypeSymbol, \
                                        IndexedObjectOrFunctionCallSymbol, ConstrainedScalarSubtypeSymbol, \
                                        ConstrainedArraySubtypeSymbol, ConstrainedRecordSubtypeSymbol, \
                                        RecordElementSymbol, ArrayElementConstraint, ResolutionFunctionSymbol, \
                                        ArrayElementResolution, RecordResolution, RecordElementResolution

from tests.unit                  import _subtypeSymbol
from tests.unit.Writer           import _object


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Symbols(Testcase):
	def test_Unresolved(self) -> None:
		"""An unresolved symbol is written without the ``?`` of its ``str()``."""
		symbol = SignalSymbol(SimpleName("clk"))

		self.assertEqual("clk", VHDLWriter().Format(symbol))

	def test_Resolved(self) -> None:
		"""A resolved symbol is written by its name, not by its target."""
		symbol = SignalSymbol(SimpleName("clk"))
		symbol.Signal = Signal(["Clock"], _subtypeSymbol("std_logic"))

		self.assertEqual("clk", VHDLWriter().Format(symbol))

	def test_Library(self) -> None:
		self.assertEqual("ieee", VHDLWriter().Format(LibraryReferenceSymbol(SimpleName("ieee"))))

	def test_AllPackageMembers(self) -> None:
		symbol = AllPackageMembersReferenceSymbol(AllName(SelectedName("std_logic_1164", SimpleName("ieee"))))

		self.assertEqual("ieee.std_logic_1164.all", VHDLWriter().Format(symbol))

	def test_EntityInstantiation(self) -> None:
		symbol = EntityInstantiationSymbol(SelectedName("counter", SimpleName("work")))

		self.assertEqual("work.counter", VHDLWriter().Format(symbol))

	def test_Subtype(self) -> None:
		self.assertEqual("std_logic", VHDLWriter().Format(SimpleSubtypeSymbol(SimpleName("std_logic"))))

	def test_FunctionCall(self) -> None:
		symbol = IndexedObjectOrFunctionCallSymbol(ParenthesisName(SimpleName("rising_edge"), [
			ParameterAssociationItem(None, _object("clk"))
		]))

		self.assertEqual("rising_edge(clk)", VHDLWriter().Format(symbol))


class ResolutionIndications(Testcase):
	"""A resolution indication is written before the type mark of its subtype indication."""

	def test_ResolutionFunction(self) -> None:
		symbol = SimpleSubtypeSymbol(SimpleName("std_ulogic"), resolution=ResolutionFunctionSymbol(SimpleName("resolved")))

		self.assertEqual("resolved std_ulogic", VHDLWriter().Format(symbol))

	def test_ResolutionFunction_SelectedName(self) -> None:
		resolution = ResolutionFunctionSymbol(SelectedName("resolved", SelectedName("p", SimpleName("work"))))
		symbol =     SimpleSubtypeSymbol(SimpleName("std_ulogic"), resolution=resolution)

		self.assertEqual("work.p.resolved std_ulogic", VHDLWriter().Format(symbol))

	def test_ArrayElementResolution(self) -> None:
		resolution = ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
		symbol =     SimpleSubtypeSymbol(SimpleName("std_ulogic_vector"), resolution=resolution)

		self.assertEqual("(resolved) std_ulogic_vector", VHDLWriter().Format(symbol))

	def test_ArrayElementResolution_Nested(self) -> None:
		resolution = ArrayElementResolution(ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved"))))
		symbol =     SimpleSubtypeSymbol(SimpleName("matrix"), resolution=resolution)

		self.assertEqual("((resolved)) matrix", VHDLWriter().Format(symbol))

	def test_RecordResolution(self) -> None:
		resolution = RecordResolution([
			RecordElementResolution(RecordElementSymbol(SimpleName("a")), ResolutionFunctionSymbol(SimpleName("resolved"))),
			RecordElementResolution(
				RecordElementSymbol(SimpleName("b")),
				ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
			)
		])
		symbol =     SimpleSubtypeSymbol(SimpleName("pair_t"), resolution=resolution)

		self.assertEqual("(a resolved, b (resolved)) pair_t", VHDLWriter().Format(symbol))

	def test_ConstrainedScalarSubtypeSymbol(self) -> None:
		constraint = SimpleRange(CharacterLiteral("X"), CharacterLiteral("1"), Direction.To)
		resolution = ResolutionFunctionSymbol(SimpleName("resolved"))
		symbol =     ConstrainedScalarSubtypeSymbol(SimpleName("std_ulogic"), constraint, resolution=resolution)

		self.assertEqual("resolved std_ulogic range 'X' to '1'", VHDLWriter().Format(symbol))

	def test_ConstrainedArraySubtypeSymbol(self) -> None:
		constraint = SimpleRange(IntegerLiteral(7), IntegerLiteral(0), Direction.DownTo)
		resolution = ArrayElementResolution(ResolutionFunctionSymbol(SimpleName("resolved")))
		symbol =     ConstrainedArraySubtypeSymbol(SimpleName("std_ulogic_vector"), [constraint], resolution=resolution)

		self.assertEqual("(resolved) std_ulogic_vector(7 downto 0)", VHDLWriter().Format(symbol))

	def test_ConstrainedRecordSubtypeSymbol(self) -> None:
		constraint = ArrayElementConstraint([SimpleRange(IntegerLiteral(3), IntegerLiteral(0), Direction.DownTo)])
		resolution = RecordResolution([
			RecordElementResolution(RecordElementSymbol(SimpleName("a")), ResolutionFunctionSymbol(SimpleName("resolved")))
		])
		symbol =     ConstrainedRecordSubtypeSymbol(
			SimpleName("pair_t"),
			{RecordElementSymbol(SimpleName("b")): constraint},
			resolution=resolution
		)

		self.assertEqual("(a resolved) pair_t(b(3 downto 0))", VHDLWriter().Format(symbol))


class AssociationItems(Testcase):
	def test_Positional(self) -> None:
		self.assertEqual("a", VHDLWriter().Format(PortAssociationItem(None, _object("a"))))

	def test_Named(self) -> None:
		item = GenericAssociationItem(SimpleName("BITS"), _object("BITS"))

		self.assertEqual("BITS => BITS", VHDLWriter().Format(item))

	def test_Open(self) -> None:
		item = PortAssociationItem(SimpleName("overflow"), OpenName())

		self.assertEqual("overflow => open", VHDLWriter().Format(item))

	def test_NoActual(self) -> None:
		item = ParameterAssociationItem(SimpleName("x"), None)

		with self.assertRaises(VHDLWriterError) as context:
			VHDLWriter().Format(item)

		self.assertEqual("Association item has no actual.", str(context.exception))
		self.assertIs(item, context.exception.Element)
