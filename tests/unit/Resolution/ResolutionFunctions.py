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
Resolution functions (IEEE Std 1076-2008, 4.6 and 6.3): the resolution indications of subtype indications.
"""
from pyTooling.Testing       import Testcase

from pyVHDLModel.Base        import Direction, Mode, SimpleRange
from pyVHDLModel.Declaration import Alias
from pyVHDLModel.DesignUnit  import Architecture, Entity, Package
from pyVHDLModel.Expression  import IntegerLiteral
from pyVHDLModel.Exception   import UnresolvedNameWarning
from pyVHDLModel.Interface   import ParameterConstantInterfaceItem, PortSimpleSignalInterfaceItem
from pyVHDLModel.Name        import SelectedName, SimpleName
from pyVHDLModel.Object      import Signal
from pyVHDLModel.Subprogram  import Function, SubprogramSignature
from pyVHDLModel.Symbol      import SimpleSubtypeSymbol, SimpleObjectOrFunctionCallSymbol, RecordElementSymbol, \
                                    ResolutionFunctionSymbol, ArrayElementResolution, RecordResolution, \
                                    RecordElementResolution
from pyVHDLModel.Type        import ArrayType, RecordType, RecordTypeElement, Subtype

from tests.unit              import _entitySymbol, _subtypeSymbol
from tests.unit.Resolution   import _resolve
from tests.unit.Visibility   import _constant, _design, _enumeration, _use


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


def _function(identifier: str, parameterType: str, returnType: str, isPure: bool = True) -> Function:
	"""A function with one parameter, e.g. a resolution function ``function res(v : T_vector) return T;``."""
	parameter = ParameterConstantInterfaceItem(("v", ), Mode.In, _subtypeSymbol(parameterType))
	return Function(identifier, _subtypeSymbol(returnType), isPure, parameterItems=[parameter])


def _resolved(functionName: str, typeMark: str) -> SimpleSubtypeSymbol:
	"""A subtype indication with a resolution function name, e.g. ``res T``."""
	return SimpleSubtypeSymbol(SimpleName(typeMark), resolution=ResolutionFunctionSymbol(SimpleName(functionName)))


def _elementResolved(functionName: str, typeMark: str) -> SimpleSubtypeSymbol:
	"""A subtype indication with an array element resolution, e.g. ``(res) T_vector``."""
	resolution = ArrayElementResolution(ResolutionFunctionSymbol(SimpleName(functionName)))
	return SimpleSubtypeSymbol(SimpleName(typeMark), resolution=resolution)


class ResolutionFunctions(Testcase):
	"""A resolution function name references the function resolving the base type of its subtype indication."""

	def setUp(self) -> None:
		self._type =     _enumeration("T", "'0'", "'1'", "'Z'")
		self._vector =   ArrayType("T_vector", [_subtypeSymbol("natural")], _subtypeSymbol("T"))
		self._function = _function("res", "T_vector", "T")

	def _package(self, *declaredItems) -> Package:
		"""A package declaring ``T``, ``T_vector`` and ``res``, followed by the declared items."""
		return Package("p", declaredItems=[self._type, self._vector, self._function, *declaredItems])

	def test_Subtype(self) -> None:
		"""``subtype RT is res T;``"""
		subtype =  Subtype("RT", _resolved("res", "T"))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, subtype.Type.Resolution.Function)
		self.assertIs(self._function, subtype.ResolutionFunction)

	def test_Subtype_OfSubtype(self) -> None:
		"""``subtype RT2 is res ST;``: the function resolves the base type of the subtype ``ST``."""
		subtype =  Subtype("ST", _subtypeSymbol("T"))
		resolved = Subtype("RT2", _resolved("res", "ST"))
		warnings = _resolve(_design(self._package(subtype, resolved), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, resolved.ResolutionFunction)

	def test_Signal(self) -> None:
		"""``signal s : res T;`` in an architecture using ``work.p.all``."""
		signal =       Signal(("s", ), _resolved("res", "T"))
		architecture = Architecture("rtl", _entitySymbol("e"), [_use("work.p.all")], [signal])
		warnings =     _resolve(_design(self._package(), Entity("e"), architecture, analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, signal.Subtype.Resolution.Function)

	def test_Port(self) -> None:
		"""``port (i : in res T);``"""
		port =     PortSimpleSignalInterfaceItem(("i", ), Mode.In, _resolved("res", "T"))
		entity =   Entity("e", [_use("work.p.all")], portItems=[port])
		warnings = _resolve(_design(self._package(), entity, analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, port.Subtype.Resolution.Function)

	def test_ExpandedName(self) -> None:
		"""``signal s : work.p.res work.p.T;`` without a use clause."""
		resolution =   ResolutionFunctionSymbol(SelectedName("res", SelectedName("p", SimpleName("work"))))
		typeMark =     SimpleSubtypeSymbol(SelectedName("T", SelectedName("p", SimpleName("work"))), resolution=resolution)
		signal =       Signal(("s", ), typeMark)
		architecture = Architecture("rtl", _entitySymbol("e"), declaredItems=[signal])
		warnings =     _resolve(_design(self._package(), Entity("e"), architecture, analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, resolution.Function)

	def test_Overload(self) -> None:
		"""Of two overloads ``res``, each subtype indication references the one resolving its type."""
		integerFunction = _function("res", "integer_vector", "integer")
		resolvedT =       Subtype("RT", _resolved("res", "T"))
		resolvedInteger = Subtype("RI", _resolved("res", "integer"))
		warnings =        _resolve(_design(self._package(integerFunction, resolvedT, resolvedInteger), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, resolvedT.ResolutionFunction)
		self.assertIs(integerFunction, resolvedInteger.ResolutionFunction)

	def test_ImplicitOperation(self) -> None:
		"""``subtype RI is maximum integer;``: the implicit ``MAXIMUM`` of ``integer_vector`` (5.3.2.4)."""
		subtype =  Subtype("RI", _resolved("maximum", "integer"))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertListEqual([], warnings)
		self.assertEqual("maximum", subtype.ResolutionFunction.NormalizedDesignator)
		self.assertEqual("integer_vector", subtype.ResolutionFunction.Parent.Identifier)

	def test_Alias(self) -> None:
		"""``alias res2 is res [T_vector return T];``: an alias of a function names the function."""
		signature = SubprogramSignature([_subtypeSymbol("T_vector")], _subtypeSymbol("T"))
		alias =     Alias("res2", SimpleObjectOrFunctionCallSymbol(SimpleName("res")), signature=signature)
		subtype =   Subtype("RT", _resolved("res2", "T"))
		warnings =  _resolve(_design(self._package(alias, subtype), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, subtype.ResolutionFunction)

	def test_NotFound(self) -> None:
		subtype =  Subtype("RT", _resolved("missing", "T"))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], UnresolvedNameWarning)
		self.assertEqual("Name 'missing' not found in: p.", str(warnings[0]))
		self.assertIs(subtype.Type.Resolution, warnings[0].Symbol)
		self.assertIs(subtype, warnings[0].Place)
		self.assertIsNone(subtype.ResolutionFunction)

	def test_NoMatch(self) -> None:
		"""``subtype RI is res integer;``: no function ``res`` resolves ``integer``."""
		subtype =  Subtype("RI", _resolved("res", "integer"))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], UnresolvedNameWarning)
		self.assertEqual("No function 'res' resolves type 'integer'.", str(warnings[0]))
		self.assertIs(subtype.Type.Resolution, warnings[0].Symbol)
		self.assertIsNone(subtype.ResolutionFunction)

	def test_NoFunction(self) -> None:
		"""``subtype RT is c T;``: the constant ``c`` is no function."""
		subtype =  Subtype("RT", _resolved("c", "T"))
		warnings = _resolve(_design(self._package(_constant("c", "integer"), subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual("No function 'c' resolves type 'T'.", str(warnings[0]))

	def test_Impure(self) -> None:
		"""An impure function is no resolution function."""
		impure =   _function("res_impure", "T_vector", "T", isPure=False)
		subtype =  Subtype("RT", _resolved("res_impure", "T"))
		warnings = _resolve(_design(self._package(impure, subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual("No function 'res_impure' resolves type 'T'.", str(warnings[0]))

	def test_ConstrainedArrayType(self) -> None:
		"""``function res4(v : T4) return T;``: a parameter of a constrained array type ``array (0 to 3) of T``."""
		indexRange =  SimpleRange(IntegerLiteral(0), IntegerLiteral(3), Direction.To)
		constrained = ArrayType("T4", [indexRange], _subtypeSymbol("T"))
		subtype =     Subtype("RT", _resolved("res4", "T"))
		package =     self._package(constrained, _function("res4", "T4", "T"), subtype)
		warnings =    _resolve(_design(package, analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual("No function 'res4' resolves type 'T'.", str(warnings[0]))

	def test_TwoDimensions(self) -> None:
		"""``function res2d(v : T2D) return T;``: a parameter of a two-dimensional array type."""
		twoDimensions = ArrayType("T2D", [_subtypeSymbol("natural"), _subtypeSymbol("natural")], _subtypeSymbol("T"))
		subtype =       Subtype("RT", _resolved("res2d", "T"))
		package =       self._package(twoDimensions, _function("res2d", "T2D", "T"), subtype)
		warnings =      _resolve(_design(package, analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual("No function 'res2d' resolves type 'T'.", str(warnings[0]))

	def test_Reset(self) -> None:
		"""Resetting the analysis resets the reference; the next analysis resolves it again."""
		subtype = Subtype("RT", _resolved("res", "T"))
		design =  _design(self._package(subtype))

		design.ResetAnalysis()

		self.assertIsNone(subtype.ResolutionFunction)

		design.Analyze()

		self.assertIs(self._function, subtype.ResolutionFunction)


class ElementResolutions(Testcase):
	"""An element resolution resolves the elements of an array or record type."""

	def setUp(self) -> None:
		self._type =     _enumeration("T", "'0'", "'1'", "'Z'")
		self._vector =   ArrayType("T_vector", [_subtypeSymbol("natural")], _subtypeSymbol("T"))
		self._function = _function("res", "T_vector", "T")
		self._matrix =   ArrayType("T_matrix", [_subtypeSymbol("natural")], _subtypeSymbol("T_vector"))
		self._record =   RecordType("R", [
			RecordTypeElement(("a", ), _subtypeSymbol("T")),
			RecordTypeElement(("b", "c"), _subtypeSymbol("T_vector"))
		])

	def _package(self, *declaredItems) -> Package:
		"""A package declaring ``T``, ``T_vector``, ``res``, ``T_matrix`` and ``R``, followed by the declared items."""
		return Package(
			"p",
			declaredItems=[self._type, self._vector, self._function, self._matrix, self._record, *declaredItems]
		)

	def test_ArrayElementResolution(self) -> None:
		"""``subtype RTV is (res) T_vector;``"""
		subtype =  Subtype("RTV", _elementResolved("res", "T_vector"))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, subtype.Type.Resolution.Resolution.Function)
		self.assertIsNone(subtype.ResolutionFunction)

	def test_ArrayElementResolution_Nested(self) -> None:
		"""``subtype RTM is ((res)) T_matrix;``"""
		function =   ResolutionFunctionSymbol(SimpleName("res"))
		resolution = ArrayElementResolution(ArrayElementResolution(function))
		subtype =    Subtype("RTM", SimpleSubtypeSymbol(SimpleName("T_matrix"), resolution=resolution))
		warnings =   _resolve(_design(self._package(subtype), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._function, function.Function)

	def test_ArrayElementResolution_NoArray(self) -> None:
		"""``subtype X is (res) T;``: ``T`` isn't an array type."""
		subtype =  Subtype("X", _elementResolved("res", "T"))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], UnresolvedNameWarning)
		self.assertEqual("Array element resolution (res?) of type 'T', which isn't an array type.", str(warnings[0]))
		self.assertIs(subtype.Type, warnings[0].Symbol)

	def test_RecordResolution(self) -> None:
		"""``subtype RR is (a res, c (res)) R;``: the record elements and the functions resolving their types."""
		a =         RecordElementSymbol(SimpleName("a"))
		functionA = ResolutionFunctionSymbol(SimpleName("res"))
		c =         RecordElementSymbol(SimpleName("c"))
		functionC = ResolutionFunctionSymbol(SimpleName("res"))
		resolution = RecordResolution([
			RecordElementResolution(a, functionA),
			RecordElementResolution(c, ArrayElementResolution(functionC))
		])
		subtype =  Subtype("RR", SimpleSubtypeSymbol(SimpleName("R"), resolution=resolution))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertListEqual([], warnings)
		self.assertIs(self._record.Elements[0], a.Reference)
		self.assertIs(self._record.Elements[1], c.Reference)
		self.assertIs(self._function, functionA.Function)
		self.assertIs(self._function, functionC.Function)

	def test_RecordResolution_NoRecord(self) -> None:
		"""``subtype X is (a res) T;``: ``T`` isn't a record type."""
		resolution = RecordResolution([
			RecordElementResolution(RecordElementSymbol(SimpleName("a")), ResolutionFunctionSymbol(SimpleName("res")))
		])
		subtype =  Subtype("X", SimpleSubtypeSymbol(SimpleName("T"), resolution=resolution))
		warnings = _resolve(_design(self._package(subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertEqual("Record resolution (a res?) of type 'T', which isn't a record type.", str(warnings[0]))

	def test_RecordElement_NotFound(self) -> None:
		"""``subtype X is (d res) R;``: ``R`` has no element ``d``."""
		element =    RecordElementSymbol(SimpleName("d"))
		resolution = RecordResolution([RecordElementResolution(element, ResolutionFunctionSymbol(SimpleName("res")))])
		subtype =    Subtype("X", SimpleSubtypeSymbol(SimpleName("R"), resolution=resolution))
		warnings =   _resolve(_design(self._package(subtype), analyze=False))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], UnresolvedNameWarning)
		self.assertEqual("Record element 'd' not found in record type 'R'.", str(warnings[0]))
		self.assertIs(element, warnings[0].Symbol)
		self.assertIsNone(element.Reference)

	def test_Reset(self) -> None:
		"""Resetting the analysis resets the references of the record elements and the functions."""
		a =          RecordElementSymbol(SimpleName("a"))
		function =   ResolutionFunctionSymbol(SimpleName("res"))
		resolution = RecordResolution([RecordElementResolution(a, function)])
		subtype =    Subtype("RR", SimpleSubtypeSymbol(SimpleName("R"), resolution=resolution))
		design =     _design(self._package(subtype))

		design.ResetAnalysis()

		self.assertIsNone(a.Reference)
		self.assertIsNone(function.Function)

		design.Analyze()

		self.assertIs(self._record.Elements[0], a.Reference)
		self.assertIs(self._function, function.Function)


class ResolutionFunctionChecks(Testcase):
	"""Parameter checks of :meth:`Function.IsResolutionFunctionOf`."""

	def test_ResolvedType_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_function("res", "T_vector", "T").IsResolutionFunctionOf(None)

		self.assertEqual("Parameter 'resolvedType' is None.", str(context.exception))

	def test_ResolvedType_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_function("res", "T_vector", "T").IsResolutionFunctionOf("T")

		self.assertEqual("Parameter 'resolvedType' is not of type 'BaseType'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Unresolved(self) -> None:
		"""Before the analysis, the type marks aren't resolved: no function resolves a type."""
		self.assertFalse(_function("res", "T_vector", "T").IsResolutionFunctionOf(_enumeration("T", "a")))
