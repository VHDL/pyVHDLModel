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
"""This module contains the predefined package ``ieee.math_complex`` of VHDL library ``IEEE``."""

from typing                 import Optional as Nullable

from pyTooling.Decorators   import export

from pyVHDLModel.Base       import Direction, Mode, SimpleRange
from pyVHDLModel.Name       import AttributeName, SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ConstrainedScalarSubtypeSymbol, \
                                   SimpleObjectOrFunctionCallSymbol, IndexedObjectOrFunctionCallSymbol
from pyVHDLModel.Expression import FloatingPointLiteral, StringLiteral, NegationExpression, QualifiedExpression, \
                                   Aggregate, SimpleAggregateElement
from pyVHDLModel.Object     import Constant
from pyVHDLModel.Type       import RecordType, RecordTypeElement, Subtype
from pyVHDLModel.Interface  import ParameterConstantInterfaceItem
from pyVHDLModel.Subprogram import Function, Operator
from pyVHDLModel.Predefined import PredefinedPackage, PredefinedPackageBody


@export
class Math_Complex(PredefinedPackage):
	"""
	Predefined package ``ieee.math_complex`` (IEEE Std 1076-2008, 16.8.3).

	Its declarations, in the order of the standard:

	* constant ``copyrightnotice``
	* types ``complex`` and ``complex_polar`` and subtypes ``positive_real`` and ``principal_value``
	* constants ``math_cbase_1``, ``math_cbase_j`` and ``math_czero``
	* operators ``"="`` and ``"/="`` of ``complex_polar``, functions ``cmplx``, ``get_principal_value``,
	  ``complex_to_polar`` and ``polar_to_complex``
	* operators ``"abs"`` and ``"-"``, functions ``arg``, ``conj``, ``sqrt``, ``exp``, ``log``, ``log2``, ``log10``,
	  ``sin``, ``cos``, ``sinh`` and ``cosh`` of ``complex`` and ``complex_polar``
	* operators ``"+"``, ``"-"``, ``"*"`` and ``"/"`` of two complex numbers or of a complex number and a ``real``

	.. seealso::

	   Matching :class:`Package Body <pyVHDLModel.IEEE.MathComplex.Math_Complex_Body>` declaration.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``math_complex`` package.
		"""
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))

		def declareConstant(constant: Constant) -> None:
			"""
			Nested function adding a constant to this package and to the package's lookup table of constants.

			:param constant: The constant.
			"""
			self._constants[constant._normalizedIdentifiers[0]] = constant
			self.AddDeclaredItem(constant)

		def complexValue(re: float, im: float) -> QualifiedExpression:
			"""
			Nested function creating the qualified expression ``COMPLEX'(re, im)``.

			:param re: The real part.
			:param im: The imaginary part.
			:returns:  The qualified expression.
			"""
			return QualifiedExpression(
				self._TypeMark("complex"),
				Aggregate((SimpleAggregateElement(FloatingPointLiteral(re)), SimpleAggregateElement(FloatingPointLiteral(im))))
			)

		def parameter(
			identifier:        str,
			subtype:           SimpleSubtypeSymbol,
			defaultExpression: Nullable[FloatingPointLiteral] = None
		) -> ParameterConstantInterfaceItem:
			"""
			Nested function creating a constant parameter of mode ``in``.

			:param identifier:        The parameter's identifier.
			:param subtype:           The parameter's type mark.
			:param defaultExpression: Optional, the default value. Default: ``None``, no default value.
			:returns:                 The parameter.
			"""
			return ParameterConstantInterfaceItem((identifier,), Mode.In, subtype, defaultExpression)

		declareConstant(Constant(
			("copyrightnotice",),
			self._TypeMark("string"),
			StringLiteral("Copyright IEEE P1076 WG. Licensed Apache 2.0")
		))

		self._DeclareItem(
			RecordType(
				"complex",
				(
					RecordTypeElement(("re",), self._TypeMark("real")),
					RecordTypeElement(("im",), self._TypeMark("real"))
				)
			),
			self._types
		)

		positiveRealRange = SimpleRange(
			FloatingPointLiteral(0.0),
			IndexedObjectOrFunctionCallSymbol(AttributeName("high", SimpleName("real"))),
			Direction.To
		)
		self._DeclareItem(
			Subtype("positive_real", ConstrainedScalarSubtypeSymbol(SimpleName("real"), positiveRealRange)),
			self._subtypes
		)

		principalValueRange = SimpleRange(
			NegationExpression(SimpleObjectOrFunctionCallSymbol(SimpleName("math_pi"))),
			SimpleObjectOrFunctionCallSymbol(SimpleName("math_pi")),
			Direction.To
		)
		self._DeclareItem(
			Subtype("principal_value", ConstrainedScalarSubtypeSymbol(SimpleName("real"), principalValueRange)),
			self._subtypes
		)

		self._DeclareItem(
			RecordType(
				"complex_polar",
				(
					RecordTypeElement(("mag",), self._TypeMark("positive_real")),
					RecordTypeElement(("arg",), self._TypeMark("principal_value"))
				)
			),
			self._types
		)

		declareConstant(Constant(("math_cbase_1",), self._TypeMark("complex"), complexValue(1.0, 0.0)))
		declareConstant(Constant(("math_cbase_j",), self._TypeMark("complex"), complexValue(0.0, 1.0)))
		declareConstant(Constant(("math_czero",),   self._TypeMark("complex"), complexValue(0.0, 0.0)))

		for operatorSymbol in ("=", "/="):
			self._DeclareSubprogram(
				Operator(operatorSymbol, self._TypeMark("boolean"), parameterItems=(
					parameter("L", self._TypeMark("complex_polar")),
					parameter("R", self._TypeMark("complex_polar"))
				)),
				self._functions
			)

		self._DeclareSubprogram(
			Function("cmplx", self._TypeMark("complex"), parameterItems=(
				parameter("X", self._TypeMark("real")),
				parameter("Y", self._TypeMark("real"), FloatingPointLiteral(0.0))
			)),
			self._functions
		)
		self._DeclareSubprogram(
			Function("get_principal_value", self._TypeMark("principal_value"), parameterItems=(
				parameter("X", self._TypeMark("real")),
			)),
			self._functions
		)
		self._DeclareSubprogram(
			Function("complex_to_polar", self._TypeMark("complex_polar"), parameterItems=(
				parameter("Z", self._TypeMark("complex")),
			)),
			self._functions
		)
		self._DeclareSubprogram(
			Function("polar_to_complex", self._TypeMark("complex"), parameterItems=(
				parameter("Z", self._TypeMark("complex_polar")),
			)),
			self._functions
		)

		for complexType in ("complex", "complex_polar"):
			self._DeclareSubprogram(
				Operator("abs", self._TypeMark("positive_real"), parameterItems=(parameter("Z", self._TypeMark(complexType)),)),
				self._functions
			)

		for complexType in ("complex", "complex_polar"):
			self._DeclareSubprogram(
				Function("arg", self._TypeMark("principal_value"), parameterItems=(
					parameter("Z", self._TypeMark(complexType)),
				)),
				self._functions
			)

		for complexType in ("complex", "complex_polar"):
			self._DeclareSubprogram(
				Operator("-", self._TypeMark(complexType), parameterItems=(parameter("Z", self._TypeMark(complexType)),)),
				self._functions
			)

		for identifier in ("conj", "sqrt", "exp"):
			for complexType in ("complex", "complex_polar"):
				self._DeclareSubprogram(
					Function(identifier, self._TypeMark(complexType), parameterItems=(
						parameter("Z", self._TypeMark(complexType)),
					)),
					self._functions
				)

		for complexType in ("complex", "complex_polar"):
			for identifier in ("log", "log2", "log10"):
				self._DeclareSubprogram(
					Function(identifier, self._TypeMark(complexType), parameterItems=(
						parameter("Z", self._TypeMark(complexType)),
					)),
					self._functions
				)

		for complexType in ("complex", "complex_polar"):
			self._DeclareSubprogram(
				Function("log", self._TypeMark(complexType), parameterItems=(
					parameter("Z", self._TypeMark(complexType)),
					parameter("BASE", self._TypeMark("real"))
				)),
				self._functions
			)

		for identifier in ("sin", "cos", "sinh", "cosh"):
			for complexType in ("complex", "complex_polar"):
				self._DeclareSubprogram(
					Function(identifier, self._TypeMark(complexType), parameterItems=(
						parameter("Z", self._TypeMark(complexType)),
					)),
					self._functions
				)

		for operatorSymbol in ("+", "-", "*", "/"):
			for complexType in ("complex", "complex_polar"):
				for left, right in (
					(complexType, complexType),
					("real",      complexType),
					(complexType, "real")
				):
					self._DeclareSubprogram(
						Operator(operatorSymbol, self._TypeMark(complexType), parameterItems=(
							parameter("L", self._TypeMark(left)),
							parameter("R", self._TypeMark(right))
						)),
						self._functions
					)


@export
class Math_Complex_Body(PredefinedPackageBody):
	"""
	Predefined package body of package ``ieee.math_complex``.
	"""

	def __init__(self) -> None:
		"""
		Initializes the ``math_complex`` package body.
		"""
		super().__init__()

		self._AddPackageClause(("work.math_real.all",))
