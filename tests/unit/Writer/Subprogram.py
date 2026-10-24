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
"""Tests for writing subprograms, subprogram instantiations and protected types with pyVHDLModel.Formatting.VHDL."""
from textwrap                    import dedent

from pyTooling.Testing           import Testcase

from pyVHDLModel.Association     import GenericAssociationItem
from pyVHDLModel.Base            import Mode
from pyVHDLModel.DesignUnit      import Component
from pyVHDLModel.Expression      import IntegerLiteral
from pyVHDLModel.Formatting.VHDL import KeywordCase, NewLine, VHDLStyle, VHDLWriter
from pyVHDLModel.Instantiation   import ProcedureInstantiation, FunctionInstantiation
from pyVHDLModel.Interface       import GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                        GenericProcedureInterfaceItem, GenericFunctionInterfaceItem, \
                                        ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                        ParameterSimpleSignalInterfaceItem
from pyVHDLModel.Name            import SimpleName
from pyVHDLModel.Object          import Constant, Variable
from pyVHDLModel.Sequential      import NullStatement
from pyVHDLModel.Subprogram      import Procedure, Function, ProcedureMethod, FunctionMethod
from pyVHDLModel.Symbol          import SubprogramReferenceSymbol
from pyVHDLModel.Type            import ProtectedType, ProtectedTypeBody

from tests.unit                  import _subtypeSymbol


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _parameters() -> list:
	"""A constant and a variable parameter."""
	return [
		ParameterConstantInterfaceItem(["a"], Mode.In, _subtypeSymbol("integer")),
		ParameterVariableInterfaceItem(["b"], Mode.Out, _subtypeSymbol("integer"))
	]


class Declarations(Testcase):
	def test_Procedure(self) -> None:
		self.assertEqual("procedure reset;\n", VHDLWriter().Format(Procedure("reset")))

	def test_Procedure_Parameters(self) -> None:
		self.assertEqual(dedent("""\
			procedure p (
			  constant a : in integer;
			  variable b : out integer
			);
			"""), VHDLWriter().Format(Procedure("p", parameterItems=_parameters())))

	def test_Procedure_Parameters_OneLine(self) -> None:
		style = VHDLStyle(interfaceElement=NewLine.Remove, interfaceLastCloseParen=NewLine.Remove)

		self.assertEqual(
			"procedure p (constant a : in integer; variable b : out integer);\n",
			VHDLWriter(style).Format(Procedure("p", parameterItems=_parameters()))
		)

	def test_Function(self) -> None:
		function = Function("parity", _subtypeSymbol("bit"), parameterItems=[
			ParameterSimpleSignalInterfaceItem(["data"], Mode.In, _subtypeSymbol("bit_vector"))
		])

		self.assertEqual(dedent("""\
			function parity (
			  signal data : in bit_vector
			) return bit;
			"""), VHDLWriter().Format(function))

	def test_Function_Impure(self) -> None:
		function = Function("value", _subtypeSymbol("natural"), False)

		self.assertEqual("impure function value return natural;\n", VHDLWriter().Format(function))

	def test_Function_Generics(self) -> None:
		"""After a generic clause, the reserved word ``parameter`` introduces the parameter list."""
		function = Function(
			"maximum",
			_subtypeSymbol("T"),
			genericItems=[GenericTypeInterfaceItem("T")],
			parameterItems=[ParameterConstantInterfaceItem(["a", "b"], Mode.Default, _subtypeSymbol("T"))]
		)

		self.assertEqual(dedent("""\
			function maximum generic (
			  type T
			) parameter (
			  constant a, b : T
			) return T;
			"""), VHDLWriter().Format(function))

	def test_Procedure_Generics(self) -> None:
		procedure = Procedure("tick", genericItems=[
			GenericConstantInterfaceItem(["N"], Mode.Default, _subtypeSymbol("natural"))
		])

		self.assertEqual(dedent("""\
			procedure tick generic (
			  N : natural
			);
			"""), VHDLWriter().Format(procedure))

	def test_UpperCase(self) -> None:
		function = Function("value", _subtypeSymbol("natural"), False)
		writer =   VHDLWriter(VHDLStyle(KeywordCase.Upper))

		self.assertEqual("IMPURE FUNCTION value RETURN natural;\n", writer.Format(function))


class Bodies(Testcase):
	def test_Procedure(self) -> None:
		"""A subprogram with declared items is a subprogram body; its statements come with the sequential statements."""
		procedure = Procedure("p", parameterItems=_parameters(), declaredItems=[
			Variable(["tmp"], _subtypeSymbol("integer"))
		])

		self.assertEqual(dedent("""\
			procedure p (
			  constant a : in integer;
			  variable b : out integer
			) is
			  variable tmp : integer;
			begin
			end procedure p;
			"""), VHDLWriter().Format(procedure))

	def test_Function(self) -> None:
		function = Function("one", _subtypeSymbol("integer"), declaredItems=[
			Constant(["ONE"], _subtypeSymbol("integer"), IntegerLiteral(1))
		])

		self.assertEqual(dedent("""\
			function one return integer is
			  constant ONE : integer := 1;
			begin
			end function one;
			"""), VHDLWriter().Format(function))

	def test_Nested(self) -> None:
		inner =     Procedure("inner", declaredItems=[Variable(["v"], _subtypeSymbol("bit"))])
		procedure = Procedure("outer", declaredItems=[inner])

		self.assertEqual(dedent("""\
			procedure outer is
			  procedure inner is
			    variable v : bit;
			  begin
			  end procedure inner;
			begin
			end procedure outer;
			"""), VHDLWriter().Format(procedure))

	def test_Empty_InBody(self) -> None:
		"""A subprogram without declared items and statements in a body is an empty subprogram body."""
		body = ProtectedTypeBody("counter", [ProcedureMethod("stub")])

		self.assertEqual(dedent("""\
			type counter is protected body
			  procedure stub is
			  begin
			  end procedure stub;
			end protected body counter;
			"""), VHDLWriter().Format(body))

	def test_Empty_InSubprogram(self) -> None:
		procedure = Procedure("outer", declaredItems=[Procedure("inner")])

		self.assertEqual(dedent("""\
			procedure outer is
			  procedure inner is
			  begin
			  end procedure inner;
			begin
			end procedure outer;
			"""), VHDLWriter().Format(procedure))

	def test_Statements(self) -> None:
		"""A subprogram with statements is a subprogram body."""
		procedure = Procedure("p", statements=[NullStatement()])

		self.assertEqual("procedure p is\nbegin\n  null;\nend procedure p;\n", VHDLWriter().Format(procedure))


class GenericSubprograms(Testcase):
	def test_Procedure(self) -> None:
		procedure = GenericProcedureInterfaceItem("log")
		procedure.AddParameterItem(ParameterConstantInterfaceItem(["message"], Mode.In, _subtypeSymbol("string")))

		self.assertEqual("procedure log (\n  constant message : in string\n)", VHDLWriter().Format(procedure))

	def test_Function(self) -> None:
		function = GenericFunctionInterfaceItem("compare", _subtypeSymbol("boolean"))

		self.assertEqual("function compare return boolean", VHDLWriter().Format(function))

	def test_InGenericClause(self) -> None:
		procedure = GenericProcedureInterfaceItem("log")
		procedure.AddParameterItem(ParameterConstantInterfaceItem(["message"], Mode.In, _subtypeSymbol("string")))
		component = Component("logger", [GenericTypeInterfaceItem("T"), procedure])

		self.assertEqual(dedent("""\
			component logger is
			  generic (
			    type T;
			    procedure log (
			      constant message : in string
			    )
			  );
			end component logger;
			"""), VHDLWriter().Format(component))


class Instantiations(Testcase):
	def test_Procedure(self) -> None:
		instantiation = ProcedureInstantiation("log_byte", SubprogramReferenceSymbol(SimpleName("log")), [
			GenericAssociationItem(SimpleName("T"), _subtypeSymbol("byte")),
			GenericAssociationItem(SimpleName("N"), IntegerLiteral(8))
		])

		self.assertEqual(dedent("""\
			procedure log_byte is new log
			  generic map (
			    T => byte,
			    N => 8
			  );
			"""), VHDLWriter().Format(instantiation))

	def test_Function(self) -> None:
		instantiation = FunctionInstantiation(
			"maximum_byte",
			SubprogramReferenceSymbol(SimpleName("maximum")),
			genericAssociationItems=[GenericAssociationItem(None, _subtypeSymbol("byte"))]
		)

		self.assertEqual(dedent("""\
			function maximum_byte is new maximum
			  generic map (
			    byte
			  );
			"""), VHDLWriter().Format(instantiation))

	def test_WithoutGenericMap(self) -> None:
		instantiation = ProcedureInstantiation("copy", SubprogramReferenceSymbol(SimpleName("original")))

		self.assertEqual("procedure copy is new original;\n", VHDLWriter().Format(instantiation))


class ProtectedTypes(Testcase):
	def test_Declaration(self) -> None:
		protectedType = ProtectedType("counter", [
			ProcedureMethod("increment"),
			FunctionMethod("value", _subtypeSymbol("natural"), False)
		])

		self.assertEqual(dedent("""\
			type counter is protected
			  procedure increment;
			  impure function value return natural;
			end protected counter;
			"""), VHDLWriter().Format(protectedType))

	def test_Body(self) -> None:
		body = ProtectedTypeBody("counter", [
			Variable(["count"], _subtypeSymbol("natural"), IntegerLiteral(0)),
			ProcedureMethod("increment", declaredItems=[Constant(["STEP"], _subtypeSymbol("natural"), IntegerLiteral(1))])
		])

		self.assertEqual(dedent("""\
			type counter is protected body
			  variable count : natural := 0;
			  procedure increment is
			    constant STEP : natural := 1;
			  begin
			  end procedure increment;
			end protected body counter;
			"""), VHDLWriter().Format(body))

	def test_UpperCase(self) -> None:
		body = ProtectedTypeBody("counter", [Variable(["count"], _subtypeSymbol("natural"))])

		self.assertEqual(dedent("""\
			TYPE counter IS PROTECTED BODY
			  VARIABLE count : natural;
			END PROTECTED BODY counter;
			"""), VHDLWriter(VHDLStyle(KeywordCase.Upper)).Format(body))
