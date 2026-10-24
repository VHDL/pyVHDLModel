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
This module contains a writer, which formats a VHDL language model as VHDL source text.

The writer is a :class:`~pyVHDLModel.Visitor.Visitor`: a model element walks itself and the writer appends the VHDL
source text of each event to a buffer. A parser's subclass of a model class (e.g. from ``pyGHDL.dom``) is written like
that model class. Writing is a re-format: comments, blank lines and the letter case of reserved words in a parsed source
are not preserved.
"""
from __future__                import annotations

from enum                      import Enum, unique
from math                      import copysign, isfinite
from typing                    import ClassVar, Iterable, Optional as Nullable

from pyTooling.Common          import getFullyQualifiedName
from pyTooling.Decorators      import export, readonly
from pyTooling.MetaClasses     import ExtendedType, abstractclass

from pyVHDLModel.Association   import AssociationItem, GenericMapAspectMixin, PortMapAspectMixin
from pyVHDLModel.Base          import ModelElementUnion, ModelEntity, Mode, ReservedWord, SimpleRange, RangeFromName, \
                                      WaveformElement, ReportStatementMixin
from pyVHDLModel.Common        import Statement, ProcedureCallMixin, SignalAssignmentMixin, WaveformMixin, \
                                      ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform, \
                                      ConditionalWaveformsMixin, SelectedWaveformsMixin, AssignmentMixin, \
                                      ConditionalExpression, SelectedExpression, OthersSelectedExpression, \
                                      SelectedExpressionsMixin
from pyVHDLModel.Concurrent    import ProcessStatement, ConcurrentProcedureCall, ConcurrentSimpleSignalAssignment, \
                                      ConcurrentSelectedSignalAssignment, ConcurrentConditionalSignalAssignment, \
                                      ConcurrentAssertStatement, ComponentInstantiation, EntityInstantiation, \
                                      ConfigurationInstantiation, ConcurrentBlockStatement, GenerateBranch, \
                                      IfGenerateBranch, ElsifGenerateBranch, ElseGenerateBranch, IfGenerateStatement, \
                                      IndexedGenerateChoice, ConcurrentCase, GenerateCase, OthersGenerateCase, \
                                      CaseGenerateStatement, ForGenerateStatement
from pyVHDLModel.Configuration import EntityAspectEntity, EntityAspectConfiguration, EntityAspectOpen, \
                                      BindingIndication, AllInstantiationList, OthersInstantiationList, \
                                      ComponentConfiguration, BlockConfiguration
from pyVHDLModel.Declaration   import EntityClass, Attribute, AttributeSpecification, Alias
from pyVHDLModel.DesignUnit    import Reference, LibraryClause, UseClause, ContextReference, DesignUnit, Context, \
                                      Package, PackageBody, Entity, Architecture, Configuration, Component
from pyVHDLModel.Exception     import VHDLWriterError
from pyVHDLModel.Expression    import OperatorPrecedence, NullLiteral, EnumerationLiteral, IntegerLiteral, \
                                      FloatingPointLiteral, PhysicalIntegerLiteral, PhysicalFloatingLiteral, \
                                      CharacterLiteral, StringLiteral, BitStringBase, BitStringLiteral, \
                                      UnaryExpression, NegationExpression, IdentityExpression, TypeConversion, \
                                      SubExpression, BinaryExpression, RangeExpression, AddingExpression, \
                                      MultiplyingExpression, ExponentiationExpression, LogicalExpression, \
                                      AndExpression, OrExpression, XorExpression, XnorExpression, \
                                      RelationalExpression, ShiftExpression, QualifiedExpression, WhenElseExpression, \
                                      SubtypeAllocation, QualifiedExpressionAllocation, SimpleAggregateElement, \
                                      IndexedAggregateElement, RangedAggregateElement, NamedAggregateElement, \
                                      OthersAggregateElement, Aggregate
from pyVHDLModel.Name          import SimpleName, ParenthesisName, IndexedName, SlicedName, SelectedName, \
                                      AttributeName, AllName, OpenName
from pyVHDLModel.Interface     import ModeViewDeclaration, SimpleModeViewElement, CompositeModeViewElement, \
                                      GenericConstantInterfaceItem, GenericTypeInterfaceItem, \
                                      PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem, \
                                      ParameterConstantInterfaceItem, ParameterVariableInterfaceItem, \
                                      ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem, \
                                      ParameterFileInterfaceItem, GenericProcedureInterfaceItem, \
                                      GenericFunctionInterfaceItem
from pyVHDLModel.Instantiation import ProcedureInstantiation, FunctionInstantiation, PackageInstantiation
from pyVHDLModel.Object        import Obj, WithDefaultExpressionMixin, Constant, DeferredConstant, Variable, \
                                      SharedVariable, Signal, File
from pyVHDLModel.Regions       import WithGenericsMixin, WithPortsMixin, WithParametersMixin
from pyVHDLModel.Sequential    import IndexedChoice, SequentialProcedureCall, SequentialSimpleSignalAssignment, \
                                      SequentialVariableAssignment, SequentialConditionalVariableAssignment, \
                                      SequentialConditionalSignalAssignment, SequentialSelectedVariableAssignment, \
                                      SequentialSelectedSignalAssignment, SignalForceAssignment, \
                                      SignalReleaseAssignment, SequentialReportStatement, SequentialAssertStatement, \
                                      NullStatement, ReturnStatement, WaitStatement, IfBranch, ElsifBranch, \
                                      ElseBranch, IfStatement, SequentialCase, Case, OthersCase, CaseStatement, \
                                      LoopStatement, EndlessLoopStatement, ForLoopStatement, WhileLoopStatement, \
                                      LoopControlStatement, NextStatement, ExitStatement
from pyVHDLModel.Subprogram    import Subprogram, Procedure, Function
from pyVHDLModel.Symbol        import Symbol, ConstrainedScalarSubtypeSymbol, ConstrainedArraySubtypeSymbol, \
                                      ConstrainedRecordSubtypeSymbol
from pyVHDLModel.Type          import AnonymousType, FullType, Subtype, EnumeratedType, IntegerType, RealType, \
                                      PhysicalType, ArrayType, RecordTypeElement, RecordType, AccessType, FileType, \
                                      ProtectedType, ProtectedTypeBody
from pyVHDLModel.Visitor       import Visitor


@export
@unique
class KeywordCase(Enum):
	"""
	An enumeration of letter cases for VHDL reserved words in the written source text.

	.. seealso::

	   :ref:`vsg:configuring-uppercase-and-lowercase-rules`
	      |rarr| vhdl-style-guide's option ``case``.
	"""

	Lower = 0  #: Lower case, e.g. ``downto``.
	Upper = 1  #: Upper case, e.g. ``DOWNTO``.


@export
@unique
class IndentStyle(Enum):
	"""
	An enumeration of indentation styles of the written source text, as vhdl-style-guide's option ``indent_style``.

	.. seealso::

	   :ref:`vsg:configuring-indent-rules`
	      |rarr| vhdl-style-guide's options ``indent_style`` and ``indent_size``, with an example of smart tabs.
	"""

	Spaces =    0  #: Spaces, ``indent_size`` per indentation level (VSG: ``spaces``).
	SmartTabs = 1  #: One tab per indentation level (VSG: ``smart_tabs`` - tabs indent, spaces align).


@export
@unique
class NewLine(Enum):
	"""
	An enumeration of line breaks before a token of the written source text, as vhdl-style-guide's structure options.

	.. seealso::

	   :ref:`vsg:configuring-subprogram-specification-statement-rules`
	      |rarr| vhdl-style-guide's options ``interface_element``, ``interface_list_semicolon`` and ``last_close_paren``.
	   :ref:`vsg:configuring-procedure-call-statement-rules`
	      |rarr| vhdl-style-guide's options ``association_element``, ``association_list_comma`` and ``last_close_paren``.
	"""

	Add =    0  #: The token starts a new line (VSG: ``add_new_line``).
	Remove = 1  #: The token continues the line (VSG: ``remove_new_line``).


@export
@abstractclass
class ListStyle(metaclass=ExtendedType, slots=True):
	"""
	Base-class of the layouts of parenthesized lists: :class:`InterfaceListStyle` and :class:`AssociationListStyle`.

	A :class:`VHDLStyle` has one list style per construct, e.g. for port clauses and for port map aspects. The options of
	the derived classes are named after vhdl-style-guide's options of the subprogram specification rules
	``function_019``/``procedure_013`` (interface lists) and of the procedure call rule ``procedure_call_003``
	(association lists).
	"""

	_element:        NewLine  #: Line break before an element.
	_separator:      NewLine  #: Line break before the separator between two elements.
	_lastCloseParen: NewLine  #: Line break before the right parenthesis.

	def __init__(self, lastCloseParen: NewLine) -> None:
		"""
		Initializes the layout of a parenthesized list.

		:param lastCloseParen: Line break before the right parenthesis.
		:raises ValueError:    If parameter 'lastCloseParen' is None.
		:raises TypeError:     If parameter 'lastCloseParen' is not of type :class:`NewLine`.
		"""
		if lastCloseParen is None:
			raise ValueError("Parameter 'lastCloseParen' is None.")
		elif not isinstance(lastCloseParen, NewLine):
			ex = TypeError("Parameter 'lastCloseParen' is not of type 'NewLine'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(lastCloseParen)}'.")
			raise ex

		self._lastCloseParen = lastCloseParen

	@readonly
	def LastCloseParen(self) -> NewLine:
		"""
		Read-only property to access the line break before the right parenthesis (:attr:`_lastCloseParen`).

		``NewLine.Add`` writes the right parenthesis on its own line, ``NewLine.Remove`` after the last element, as
		vhdl-style-guide's option ``last_close_paren``.

		:returns: The line break before the right parenthesis.
		"""
		return self._lastCloseParen


@export
class InterfaceListStyle(ListStyle):
	"""
	Represents the layout of the interface lists of one construct.

	An interface list separates its elements by semicolons, e.g. the ports of a port clause. The options are
	vhdl-style-guide's options of the subprogram specification rules ``function_019``/``procedure_013``.

	.. seealso::

	   :ref:`vsg:configuring-subprogram-specification-statement-rules`
	      |rarr| vhdl-style-guide's options ``interface_element``, ``interface_list_semicolon`` and ``last_close_paren``.
	"""

	def __init__(
		self,
		interfaceElement:       NewLine = NewLine.Add,
		interfaceListSemicolon: NewLine = NewLine.Remove,
		lastCloseParen:         NewLine = NewLine.Add
	) -> None:
		"""
		Initializes the layout of an interface list.

		:param interfaceElement:       Optional, line break before an interface element. Default: ``NewLine.Add``.
		:param interfaceListSemicolon: Optional, line break before the semicolon between two interface elements. Default:
		                               ``NewLine.Remove``.
		:param lastCloseParen:         Optional, line break before the right parenthesis. Default: ``NewLine.Add``.
		:raises ValueError:            If parameter 'lastCloseParen' is None.
		:raises TypeError:             If parameter 'lastCloseParen' is not of type :class:`NewLine`.
		:raises ValueError:            If parameter 'interfaceElement' is None.
		:raises TypeError:             If parameter 'interfaceElement' is not of type :class:`NewLine`.
		:raises ValueError:            If parameter 'interfaceListSemicolon' is None.
		:raises TypeError:             If parameter 'interfaceListSemicolon' is not of type :class:`NewLine`.
		"""
		super().__init__(lastCloseParen)

		if interfaceElement is None:
			raise ValueError("Parameter 'interfaceElement' is None.")
		elif not isinstance(interfaceElement, NewLine):
			ex = TypeError("Parameter 'interfaceElement' is not of type 'NewLine'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(interfaceElement)}'.")
			raise ex

		if interfaceListSemicolon is None:
			raise ValueError("Parameter 'interfaceListSemicolon' is None.")
		elif not isinstance(interfaceListSemicolon, NewLine):
			ex = TypeError("Parameter 'interfaceListSemicolon' is not of type 'NewLine'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(interfaceListSemicolon)}'.")
			raise ex

		self._element =   interfaceElement
		self._separator = interfaceListSemicolon

	@readonly
	def InterfaceElement(self) -> NewLine:
		"""
		Read-only property to access the line break before an interface element (:attr:`_element`).

		It applies to every interface element, the first one after the left parenthesis included, as vhdl-style-guide's
		option ``interface_element``. ``NewLine.Add`` starts each element on its own line, ``NewLine.Remove`` continues the
		line.

		:returns: The line break before an interface element.
		"""
		return self._element

	@readonly
	def InterfaceListSemicolon(self) -> NewLine:
		"""
		Read-only property to access the line break before the semicolon between two interface elements
		(:attr:`_separator`).

		``NewLine.Remove`` ends the line of the previous element with the semicolon, ``NewLine.Add`` starts the next line
		with it, as vhdl-style-guide's option ``interface_list_semicolon``.

		:returns: The line break before the semicolon between two interface elements.
		"""
		return self._separator


@export
class AssociationListStyle(ListStyle):
	"""
	Represents the layout of the association lists of one construct.

	An association list separates its elements by commas, e.g. the associations of a port map aspect. The options are
	vhdl-style-guide's options of the procedure call rule ``procedure_call_003``.

	.. seealso::

	   :ref:`vsg:configuring-procedure-call-statement-rules`
	      |rarr| vhdl-style-guide's options ``association_element``, ``association_list_comma`` and ``last_close_paren``.
	"""

	def __init__(
		self,
		associationElement:   NewLine = NewLine.Add,
		associationListComma: NewLine = NewLine.Remove,
		lastCloseParen:       NewLine = NewLine.Add
	) -> None:
		"""
		Initializes the layout of an association list.

		:param associationElement:   Optional, line break before an association element. Default: ``NewLine.Add``.
		:param associationListComma: Optional, line break before the comma between two association elements. Default:
		                             ``NewLine.Remove``.
		:param lastCloseParen:       Optional, line break before the right parenthesis. Default: ``NewLine.Add``.
		:raises ValueError:          If parameter 'lastCloseParen' is None.
		:raises TypeError:           If parameter 'lastCloseParen' is not of type :class:`NewLine`.
		:raises ValueError:          If parameter 'associationElement' is None.
		:raises TypeError:           If parameter 'associationElement' is not of type :class:`NewLine`.
		:raises ValueError:          If parameter 'associationListComma' is None.
		:raises TypeError:           If parameter 'associationListComma' is not of type :class:`NewLine`.
		"""
		super().__init__(lastCloseParen)

		if associationElement is None:
			raise ValueError("Parameter 'associationElement' is None.")
		elif not isinstance(associationElement, NewLine):
			ex = TypeError("Parameter 'associationElement' is not of type 'NewLine'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(associationElement)}'.")
			raise ex

		if associationListComma is None:
			raise ValueError("Parameter 'associationListComma' is None.")
		elif not isinstance(associationListComma, NewLine):
			ex = TypeError("Parameter 'associationListComma' is not of type 'NewLine'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(associationListComma)}'.")
			raise ex

		self._element =   associationElement
		self._separator = associationListComma

	@readonly
	def AssociationElement(self) -> NewLine:
		"""
		Read-only property to access the line break before an association element (:attr:`_element`).

		It applies to every association element, the first one after the left parenthesis included, as
		vhdl-style-guide's option ``association_element``. ``NewLine.Add`` starts each element on its own line,
		``NewLine.Remove`` continues the line.

		:returns: The line break before an association element.
		"""
		return self._element

	@readonly
	def AssociationListComma(self) -> NewLine:
		"""
		Read-only property to access the line break before the comma between two association elements
		(:attr:`_separator`).

		``NewLine.Remove`` ends the line of the previous element with the comma, ``NewLine.Add`` starts the next line with
		it, as vhdl-style-guide's option ``association_list_comma``.

		:returns: The line break before the comma between two association elements.
		"""
		return self._separator


@export
class VHDLStyle(metaclass=ExtendedType, slots=True):
	"""
	Represents the formatting options of the :class:`VHDL writer <VHDLWriter>`.

	The options follow vhdl-style-guide's names and values. The layout of each kind of parenthesized list is an
	:class:`InterfaceListStyle` or :class:`AssociationListStyle` per construct.

	.. seealso::

	   :ref:`vsg:configuring-uppercase-and-lowercase-rules`
	      |rarr| vhdl-style-guide's option ``case``.
	   :ref:`vsg:configuring-indent-rules`
	      |rarr| vhdl-style-guide's options ``indent_style`` and ``indent_size``.
	"""

	_keywordCase:             KeywordCase           #: Letter case of reserved words.
	_indentStyle:             IndentStyle           #: Indentation style.
	_indentSize:              int                   #: Number of spaces per indentation level.
	_genericClause:           InterfaceListStyle    #: Layout of generic clauses, except of subprograms.
	_portClause:              InterfaceListStyle    #: Layout of port clauses.
	_subprogramGenericClause: InterfaceListStyle    #: Layout of generic clauses of subprograms.
	_parameterList:           InterfaceListStyle    #: Layout of formal parameter lists.
	_genericMap:              AssociationListStyle  #: Layout of generic map aspects.
	_portMap:                 AssociationListStyle  #: Layout of port map aspects.
	_procedureCall:           AssociationListStyle  #: Layout of actual parameter parts of procedure calls.
	_functionCall:            AssociationListStyle  #: Layout of association lists of function calls.

	def __init__(
		self,
		keywordCase:             KeywordCase =                    KeywordCase.Lower,
		indentStyle:             IndentStyle =                    IndentStyle.Spaces,
		indentSize:              int =                            2,
		genericClause:           Nullable[InterfaceListStyle] =   None,
		portClause:              Nullable[InterfaceListStyle] =   None,
		subprogramGenericClause: Nullable[InterfaceListStyle] =   None,
		parameterList:           Nullable[InterfaceListStyle] =   None,
		genericMap:              Nullable[AssociationListStyle] = None,
		portMap:                 Nullable[AssociationListStyle] = None,
		procedureCall:           Nullable[AssociationListStyle] = None,
		functionCall:            Nullable[AssociationListStyle] = None
	) -> None:
		"""
		Initializes the formatting options.

		:param keywordCase:             Optional, letter case of reserved words. Default: ``KeywordCase.Lower``.
		:param indentStyle:             Optional, indentation style. Default: ``IndentStyle.Spaces``.
		:param indentSize:              Optional, number of spaces per indentation level. Default: ``2``.
		:param genericClause:           Optional, layout of generic clauses of entities, components, packages and blocks.
		                                Default: ``InterfaceListStyle()``, one generic per line.
		:param portClause:              Optional, layout of port clauses. Default: ``InterfaceListStyle()``, one port per
		                                line.
		:param subprogramGenericClause: Optional, layout of generic clauses of subprograms. Default:
		                                ``InterfaceListStyle()``, one generic per line.
		:param parameterList:           Optional, layout of formal parameter lists. Default: ``InterfaceListStyle()``, one
		                                parameter per line.
		:param genericMap:              Optional, layout of generic map aspects. Default: ``AssociationListStyle()``, one
		                                association per line.
		:param portMap:                 Optional, layout of port map aspects. Default: ``AssociationListStyle()``, one
		                                association per line.
		:param procedureCall:           Optional, layout of actual parameter parts of procedure calls. Default:
		                                ``AssociationListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove)``, a single
		                                line.
		:param functionCall:            Optional, layout of association lists of function calls. Default:
		                                ``AssociationListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove)``, a single
		                                line.
		:raises ValueError:             If parameter 'keywordCase' is None.
		:raises TypeError:              If parameter 'keywordCase' is not of type :class:`KeywordCase`.
		:raises ValueError:             If parameter 'indentStyle' is None.
		:raises TypeError:              If parameter 'indentStyle' is not of type :class:`IndentStyle`.
		:raises ValueError:             If parameter 'indentSize' is None.
		:raises TypeError:              If parameter 'indentSize' is not of type :class:`int`.
		:raises ValueError:             If parameter 'indentSize' is less than 1.
		:raises TypeError:              If parameter 'genericClause' is not of type :class:`InterfaceListStyle`.
		:raises TypeError:              If parameter 'portClause' is not of type :class:`InterfaceListStyle`.
		:raises TypeError:              If parameter 'subprogramGenericClause' is not of type :class:`InterfaceListStyle`.
		:raises TypeError:              If parameter 'parameterList' is not of type :class:`InterfaceListStyle`.
		:raises TypeError:              If parameter 'genericMap' is not of type :class:`AssociationListStyle`.
		:raises TypeError:              If parameter 'portMap' is not of type :class:`AssociationListStyle`.
		:raises TypeError:              If parameter 'procedureCall' is not of type :class:`AssociationListStyle`.
		:raises TypeError:              If parameter 'functionCall' is not of type :class:`AssociationListStyle`.
		"""
		if keywordCase is None:
			raise ValueError("Parameter 'keywordCase' is None.")
		elif not isinstance(keywordCase, KeywordCase):
			ex = TypeError("Parameter 'keywordCase' is not of type 'KeywordCase'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(keywordCase)}'.")
			raise ex

		if indentStyle is None:
			raise ValueError("Parameter 'indentStyle' is None.")
		elif not isinstance(indentStyle, IndentStyle):
			ex = TypeError("Parameter 'indentStyle' is not of type 'IndentStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(indentStyle)}'.")
			raise ex

		if indentSize is None:
			raise ValueError("Parameter 'indentSize' is None.")
		elif not isinstance(indentSize, int) or isinstance(indentSize, bool):
			ex = TypeError("Parameter 'indentSize' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(indentSize)}'.")
			raise ex
		elif indentSize < 1:
			ex = ValueError("Parameter 'indentSize' is less than 1.")
			ex.add_note(f"Got value '{indentSize}'.")
			raise ex

		if genericClause is None:
			genericClause = InterfaceListStyle()
		elif not isinstance(genericClause, InterfaceListStyle):
			ex = TypeError("Parameter 'genericClause' is not of type 'InterfaceListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericClause)}'.")
			raise ex

		if portClause is None:
			portClause = InterfaceListStyle()
		elif not isinstance(portClause, InterfaceListStyle):
			ex = TypeError("Parameter 'portClause' is not of type 'InterfaceListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portClause)}'.")
			raise ex

		if subprogramGenericClause is None:
			subprogramGenericClause = InterfaceListStyle()
		elif not isinstance(subprogramGenericClause, InterfaceListStyle):
			ex = TypeError("Parameter 'subprogramGenericClause' is not of type 'InterfaceListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(subprogramGenericClause)}'.")
			raise ex

		if parameterList is None:
			parameterList = InterfaceListStyle()
		elif not isinstance(parameterList, InterfaceListStyle):
			ex = TypeError("Parameter 'parameterList' is not of type 'InterfaceListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterList)}'.")
			raise ex

		if genericMap is None:
			genericMap = AssociationListStyle()
		elif not isinstance(genericMap, AssociationListStyle):
			ex = TypeError("Parameter 'genericMap' is not of type 'AssociationListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(genericMap)}'.")
			raise ex

		if portMap is None:
			portMap = AssociationListStyle()
		elif not isinstance(portMap, AssociationListStyle):
			ex = TypeError("Parameter 'portMap' is not of type 'AssociationListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(portMap)}'.")
			raise ex

		if procedureCall is None:
			procedureCall = AssociationListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove)
		elif not isinstance(procedureCall, AssociationListStyle):
			ex = TypeError("Parameter 'procedureCall' is not of type 'AssociationListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(procedureCall)}'.")
			raise ex

		if functionCall is None:
			functionCall = AssociationListStyle(NewLine.Remove, NewLine.Remove, NewLine.Remove)
		elif not isinstance(functionCall, AssociationListStyle):
			ex = TypeError("Parameter 'functionCall' is not of type 'AssociationListStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(functionCall)}'.")
			raise ex

		self._keywordCase =             keywordCase
		self._indentStyle =             indentStyle
		self._indentSize =              indentSize
		self._genericClause =           genericClause
		self._portClause =              portClause
		self._subprogramGenericClause = subprogramGenericClause
		self._parameterList =           parameterList
		self._genericMap =              genericMap
		self._portMap =                 portMap
		self._procedureCall =           procedureCall
		self._functionCall =            functionCall

	@readonly
	def KeywordCase(self) -> KeywordCase:
		"""
		Read-only property to access the letter case of reserved words (:attr:`_keywordCase`).

		:returns: The letter case of reserved words.
		"""
		return self._keywordCase

	@readonly
	def IndentStyle(self) -> IndentStyle:
		"""
		Read-only property to access the indentation style (:attr:`_indentStyle`).

		:returns: The indentation style.
		"""
		return self._indentStyle

	@readonly
	def IndentSize(self) -> int:
		"""
		Read-only property to access the number of spaces per indentation level (:attr:`_indentSize`).

		:returns: The number of spaces per indentation level.
		"""
		return self._indentSize

	@readonly
	def GenericClause(self) -> InterfaceListStyle:
		"""
		Read-only property to access the layout of generic clauses (:attr:`_genericClause`).

		It applies to the generic clauses of entities, components, packages and block statements.

		:returns: The layout of generic clauses.
		"""
		return self._genericClause

	@readonly
	def PortClause(self) -> InterfaceListStyle:
		"""
		Read-only property to access the layout of port clauses (:attr:`_portClause`).

		It applies to the port clauses of entities, components and block statements.

		:returns: The layout of port clauses.
		"""
		return self._portClause

	@readonly
	def SubprogramGenericClause(self) -> InterfaceListStyle:
		"""
		Read-only property to access the layout of generic clauses of subprograms (:attr:`_subprogramGenericClause`).

		:returns: The layout of generic clauses of subprograms.
		"""
		return self._subprogramGenericClause

	@readonly
	def ParameterList(self) -> InterfaceListStyle:
		"""
		Read-only property to access the layout of formal parameter lists (:attr:`_parameterList`).

		It applies to the parameters of procedures, functions, generic procedures and generic functions.

		:returns: The layout of formal parameter lists.
		"""
		return self._parameterList

	@readonly
	def GenericMap(self) -> AssociationListStyle:
		"""
		Read-only property to access the layout of generic map aspects (:attr:`_genericMap`).

		It applies to the generic map aspects of instantiations, block statements, binding indications, package
		instantiations and subprogram instantiations.

		:returns: The layout of generic map aspects.
		"""
		return self._genericMap

	@readonly
	def PortMap(self) -> AssociationListStyle:
		"""
		Read-only property to access the layout of port map aspects (:attr:`_portMap`).

		It applies to the port map aspects of instantiations, block statements and binding indications.

		:returns: The layout of port map aspects.
		"""
		return self._portMap

	@readonly
	def ProcedureCall(self) -> AssociationListStyle:
		"""
		Read-only property to access the layout of actual parameter parts of procedure calls (:attr:`_procedureCall`).

		It applies to concurrent and sequential procedure calls.

		:returns: The layout of actual parameter parts of procedure calls.
		"""
		return self._procedureCall

	@readonly
	def FunctionCall(self) -> AssociationListStyle:
		"""
		Read-only property to access the layout of association lists of function calls (:attr:`_functionCall`).

		It applies to the association list of a :class:`~pyVHDLModel.Name.ParenthesisName`, which is a function call, an
		indexed name or a slice name.

		:returns: The layout of association lists of function calls.
		"""
		return self._functionCall


@export
class WrittenList(metaclass=ExtendedType, slots=True):
	"""
	Represents a parenthesized list while the :class:`VHDL writer <VHDLWriter>` writes it.
	"""

	_style:       ListStyle  #: Layout of the list.
	_separator:   str        #: Separator between two elements: a semicolon or a comma.
	_indentation: int        #: Indentation level of the line with the left parenthesis.

	def __init__(self, style: ListStyle, separator: str, indentation: int) -> None:
		"""
		Initializes a list being written.

		:param style:       The layout of the list.
		:param separator:   The separator between two elements.
		:param indentation: The indentation level of the line with the left parenthesis.
		"""
		self._style =       style
		self._separator =   separator
		self._indentation = indentation


@export
class VHDLWriter(Visitor):
	"""
	A writer formatting VHDL language model elements as VHDL source text.

	The writer handles the :mod:`visitor events <pyVHDLModel.Visitor>` of each supported model class. An element of a
	class without a walk of its own raises :exc:`NotImplementedError`; nothing is skipped.

	Expressions are written with the parentheses VHDL's operator precedence requires (IEEE Std 1076-2008, clause 9.2).
	Parentheses from the source (:class:`~pyVHDLModel.Expression.SubExpression`) are kept. Symbols are written from their
	:attr:`~pyVHDLModel.Symbol.Symbol.Name`, whether resolved or not.
	"""

	_BASE_SPECIFIERS: ClassVar[dict[BitStringBase, str]] = {
		BitStringBase.Binary:      "b",
		BitStringBase.Octal:       "o",
		BitStringBase.Decimal:     "d",
		BitStringBase.Hexadecimal: "x",
	}  #: Dictionary of base specifiers, indexed by bit string base.

	_style:       VHDLStyle                              #: Formatting options.
	_buffer:      list[str]                              #: Fragments of the VHDL source text written by :meth:`Format`.
	_minimum:     OperatorPrecedence                     #: Loosest precedence of the next operand without parentheses.
	_frames:      list[tuple[OperatorPrecedence, bool]]  #: Stack of entered operands: precedence and if in parentheses.
	_indentation: int                                    #: Indentation level of the next line.
	_lists:       list[WrittenList]                      #: Stack of the parenthesized lists being written.

	def __init__(self, style: Nullable[VHDLStyle] = None) -> None:
		"""
		Initializes a VHDL writer.

		:param style:      Optional, formatting options. Default: ``VHDLStyle()``.
		:raises TypeError: If parameter 'style' is not of type :class:`VHDLStyle`.
		"""
		super().__init__()

		if style is None:
			style = VHDLStyle()
		elif not isinstance(style, VHDLStyle):
			ex = TypeError("Parameter 'style' is not of type 'VHDLStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(style)}'.")
			raise ex

		self._style =       style
		self._buffer =      []
		self._minimum =     OperatorPrecedence.Range
		self._frames =      []
		self._indentation = 0
		self._lists =       []

	@readonly
	def Style(self) -> VHDLStyle:
		"""
		Read-only property to access the formatting options (:attr:`_style`).

		:returns: The formatting options.
		"""
		return self._style

	def Format(self, element: ModelElementUnion) -> str:
		"""
		Format a model element as VHDL source text.

		Each call starts with an empty buffer at indentation level 0. A declaration, a statement or a design unit ends with
		a newline.

		:param element:              The model element to format.
		:returns:                    The VHDL source text.
		:raises ValueError:          If parameter 'element' is None.
		:raises TypeError:           If parameter 'element' is not of type :class:`~pyVHDLModel.Base.ModelEntity` or
		                             :class:`~pyVHDLModel.Symbol.Symbol`.
		:raises NotImplementedError: If the class of the element or of one of its children has no walk of its own.
		:raises VHDLWriterError:     If the element or one of its children has no VHDL notation.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, (ModelEntity, Symbol)):
			ex = TypeError("Parameter 'element' is not of type 'ModelEntity' or 'Symbol'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		self._buffer =      []
		self._minimum =     OperatorPrecedence.Range
		self._frames =      []
		self._indentation = 0
		self._lists =       []
		element.Visit(self)
		return "".join(self._buffer)

	def VisitLeftParenthesis(self, element: TypeConversion | EntityAspectEntity | EntityInstantiation) -> None:
		"""
		Write the left parenthesis enclosing the operand of a type conversion or an architecture name.

		**Format:** ``integer(r)`` or ``entity work.counter(rtl)``

		:param element: The element enclosing the item.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def _Write(self, text: str) -> None:
		"""
		Append VHDL source text to the buffer.

		:param text: The VHDL source text.
		"""
		self._buffer.append(text)

	def VisitInterfaceListSeparator(self, element: WithGenericsMixin | WithPortsMixin | WithParametersMixin) -> None:
		"""
		Write the semicolon between two interface elements of an interface list.

		**Format:** ``clk : in bit;`` ... ``rst : in bit``

		The line breaks follow the :class:`InterfaceListStyle` of the construct, e.g. :attr:`VHDLStyle.PortClause`.

		:param element: The element containing the interface list.
		"""
		self._WriteListSeparator()

	def _WriteListSeparator(self) -> None:
		"""
		Write the separator between two elements of the innermost list being written.
		"""
		self._Write(self._ListSeparator(self._lists[-1]))

	def _ListSeparator(self, writtenList: WrittenList) -> str:
		"""
		Format the separator between two elements of a list with the line breaks of its layout.

		:param writtenList: The list.
		:returns:           The separator with its line breaks and indentation.
		"""
		style =       writtenList._style
		indentation = self._Indentation(writtenList._indentation + 1)
		before =      f"\n{indentation}" if style._separator is NewLine.Add else ""
		after =       f"\n{indentation}" if style._element is NewLine.Add else " "
		return f"{before}{writtenList._separator}{after}"

	def VisitAssociationListSeparator(
		self,
		element: ParenthesisName | GenericMapAspectMixin | PortMapAspectMixin | ProcedureCallMixin
	) -> None:
		"""
		Write the comma between two association elements of an association list.

		**Format:** ``a => x, b => y``

		The line breaks follow the :class:`AssociationListStyle` of the construct, e.g.
		:attr:`VHDLStyle.PortMap`.

		:param element: The element containing the association list.
		"""
		self._WriteListSeparator()
		self._minimum = OperatorPrecedence.Range

	def VisitElementSeparator(
		self,
		element: IndexedName | Aggregate | ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol |
		         EnumeratedType | ArrayType
	) -> None:
		"""
		Write the comma between two elements of a parenthesized list, which is no association list.

		**Format:** ``m(i, j)`` or ``(Idle, Busy)``

		:param element: The element containing the list.
		"""
		self._WriteComma()

	def _WriteComma(self) -> None:
		"""
		Write a comma and a space between two items of a list on one line.
		"""
		self._Write(", ")
		self._minimum = OperatorPrecedence.Range

	def VisitNameListSeparator(
		self,
		element: AttributeSpecification | Reference | ComponentConfiguration | ProcessStatement | WaitStatement
	) -> None:
		"""
		Write the comma between two names of a name list.

		**Format:** ``process (clk, rst)`` or ``library ieee, work;``

		:param element: The element containing the name list.
		"""
		self._WriteComma()

	def VisitWaveformSeparator(self, element: WaveformMixin) -> None:
		"""
		Write the comma between two waveform elements of a waveform.

		**Format:** ``'1', '0' after 5 ns``

		:param element: The element containing the waveform.
		"""
		self._WriteComma()

	def VisitSelectedAlternativeSeparator(self, element: SelectedWaveformsMixin | SelectedExpressionsMixin) -> None:
		"""
		Write the comma between two alternatives of selected waveforms or selected expressions.

		**Format:** ``a when 0, b when others``

		:param element: The selected assignment.
		"""
		self._WriteComma()

	def VisitArrow(
		self,
		element: AssociationItem | IndexedAggregateElement | RangedAggregateElement | NamedAggregateElement |
		         ConcurrentCase | SequentialCase
	) -> None:
		"""
		Write the arrow (``=>``) between a choice or formal and its value.

		After the choices of a case or case-generate alternative, the alternative's body follows on new lines, indented.

		:param element: The element containing the arrow.
		"""
		if isinstance(element, (ConcurrentCase, SequentialCase)):
			self._Write(" =>\n")
			self._indentation += 1
		else:
			self._Write(" => ")
			self._minimum = OperatorPrecedence.Range

	def VisitApostrophe(self, expression: QualifiedExpression) -> None:
		"""
		Write the apostrophe of a qualified expression and, unless the operand brings its own, a left parenthesis.

		An aggregate or a parenthesized sub-expression brings its own parentheses.

		:param expression: The qualified expression.
		"""
		if isinstance(expression.Operand, (Aggregate, SubExpression)):
			self._Write("'")
		else:
			self._Write("'(")

		self._minimum = OperatorPrecedence.Range

	def VisitWhen(
		self,
		element: WhenElseExpression | ConditionalWaveform | SelectedWaveform | OthersSelectedWaveform |
		         ConditionalExpression | SelectedExpression | OthersSelectedExpression | LoopControlStatement
	) -> None:
		"""
		Write the reserved word ``when`` of a conditional expression or waveform, or of a selected waveform or expression.

		:param element: The conditional expression, the conditional waveform or the selected waveform or expression.
		"""
		self._Write(f" {self._Keyword(ReservedWord.When)} ")
		if isinstance(element, WhenElseExpression):
			self._minimum = OperatorPrecedence.Logical
		else:
			self._minimum = OperatorPrecedence.Range

	def _Keyword(self, keyword: ReservedWord) -> str:
		"""
		Apply the keyword case of the formatting options to a reserved word.

		:param keyword: The reserved word.
		:returns:       The reserved word in the configured letter case.
		"""
		if self._style.KeywordCase is KeywordCase.Upper:
			return keyword.value.upper()

		return keyword.value

	def _Keywords(self, keywords: Iterable[ReservedWord]) -> str:
		"""
		Apply the keyword case of the formatting options to reserved words and join them by spaces.

		**Format:** ``shared variable``, ``protected body``

		:param keywords: The reserved words.
		:returns:        The reserved words in the configured letter case, separated by spaces.
		"""
		return " ".join(self._Keyword(keyword) for keyword in keywords)

	def VisitElse(
		self,
		element: WhenElseExpression | ConditionalWaveformsMixin | SequentialConditionalVariableAssignment
	) -> None:
		"""
		Write the reserved word ``else`` of a conditional expression or between the alternatives of an assignment.

		:param element: The conditional expression or the conditional assignment.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Else)} ")
		if isinstance(element, WhenElseExpression):
			self._minimum = OperatorPrecedence.Conditional
		else:
			self._minimum = OperatorPrecedence.Range

	def VisitOperator(self, expression: BinaryExpression) -> None:
		"""
		Write the operator of a binary expression.

		The right operand binds tighter than the operator, unless it's a primary.

		:param expression: The binary expression.
		"""
		precedence, _ = self._frames[-1]
		if (reservedWord := expression._RESERVED_WORD) is None:
			self._Write(f" {expression._FORMAT[1].strip()} ")
		else:
			self._Write(f" {self._Keyword(reservedWord)} ")

		self._minimum = OperatorPrecedence(min(precedence + 1, OperatorPrecedence.Primary))

	def VisitDirection(self, rng: RangeExpression | SimpleRange) -> None:
		"""
		Write the direction of a range.

		:param rng: The range.
		"""
		self._Write(f" {self._Keyword(rng.Direction.ReservedWord)} ")
		self._minimum = OperatorPrecedence.Adding

	def VisitNullLiteral(self, literal: NullLiteral) -> None:
		"""
		Write a null literal.

		**Format:** ``null``

		:param literal: The null literal.
		"""
		self._Write(self._Keyword(ReservedWord.Null))

	def VisitEnumerationLiteral(self, literal: EnumerationLiteral) -> None:
		"""
		Write an enumeration literal.

		**Format:** ``Idle``

		:param literal: The enumeration literal.
		"""
		self._Write(literal.Value)

	def VisitIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Write an integer literal.

		**Format:** ``42``

		A negative value is written with a sign, so it binds like a sign.

		:param literal: The integer literal.
		"""
		self._Enter(OperatorPrecedence.Adding if literal.Value < 0 else OperatorPrecedence.Primary)
		self._Write(str(literal.Value))

	def _Enter(self, precedence: OperatorPrecedence) -> None:
		"""
		Enter an operand and write a left parenthesis, if it binds looser than its position allows.

		:param precedence: The precedence level of the operand.
		"""
		parenthesized = precedence < self._minimum
		if parenthesized:
			self._Write("(")

		self._frames.append((precedence, parenthesized))

	def DepartIntegerLiteral(self, literal: IntegerLiteral) -> None:
		"""
		Leave an integer literal.

		:param literal: The integer literal.
		"""
		self._Leave()

	def _Leave(self) -> None:
		"""
		Leave an operand and write a right parenthesis, if it was entered with a left parenthesis.
		"""
		_, parenthesized = self._frames.pop()
		if parenthesized:
			self._Write(")")

	def VisitFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Write a floating-point literal.

		**Format:** ``3.5``

		A negative value is written with a sign, so it binds like a sign.

		:param literal: The floating-point literal.
		"""
		self._Enter(self._PrecedenceOfReal(literal.Value))
		self._Write(self._FormatReal(literal, literal.Value))

	def DepartFloatingPointLiteral(self, literal: FloatingPointLiteral) -> None:
		"""
		Leave a floating-point literal.

		:param literal: The floating-point literal.
		"""
		self._Leave()

	@staticmethod
	def _PrecedenceOfReal(value: float) -> OperatorPrecedence:
		"""
		Determine how tight a floating-point value binds as an operand.

		A negative value, ``-0.0`` included, is written with a sign, so it binds like a sign.

		:param value: The floating-point value.
		:returns:     The precedence level.
		"""
		if copysign(1.0, value) < 0.0:
			return OperatorPrecedence.Adding

		return OperatorPrecedence.Primary

	def _FormatReal(self, element: ModelEntity, value: float) -> str:
		"""
		Format a floating-point value as VHDL abstract literal with a decimal point.

		**Format:** ``1.0e-09``

		:param element:          The model element carrying the value.
		:param value:            The floating-point value.
		:returns:                The VHDL source text.
		:raises VHDLWriterError: If the value is infinite or not a number.
		"""
		if not isfinite(value):
			ex = VHDLWriterError("Floating-point value has no VHDL notation.", element)
			ex.add_note(f"Got value '{value}'.")
			raise ex

		mantissa, separator, exponent = repr(float(value)).partition("e")
		if "." not in mantissa:
			mantissa = f"{mantissa}.0"

		return f"{mantissa}{separator}{exponent}"

	def VisitPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Write a physical literal with an integer value.

		**Format:** ``10 ns``

		:param literal: The physical literal.
		"""
		self._Enter(OperatorPrecedence.Adding if literal.Value < 0 else OperatorPrecedence.Primary)
		self._Write(f"{literal.Value} {literal.UnitName}")

	def DepartPhysicalIntegerLiteral(self, literal: PhysicalIntegerLiteral) -> None:
		"""
		Leave a physical literal with an integer value.

		:param literal: The physical literal.
		"""
		self._Leave()

	def VisitPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Write a physical literal with a floating-point value.

		**Format:** ``1.5 ns``

		:param literal: The physical literal.
		"""
		self._Enter(self._PrecedenceOfReal(literal.Value))
		self._Write(f"{self._FormatReal(literal, literal.Value)} {literal.UnitName}")

	def DepartPhysicalFloatingLiteral(self, literal: PhysicalFloatingLiteral) -> None:
		"""
		Leave a physical literal with a floating-point value.

		:param literal: The physical literal.
		"""
		self._Leave()

	def VisitCharacterLiteral(self, literal: CharacterLiteral) -> None:
		"""
		Write a character literal.

		**Format:** ``'a'``

		:param literal:          The character literal.
		:raises VHDLWriterError: If the value is not a single graphic character.
		"""
		if len(literal.Value) != 1 or not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("Character literal is not a single graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		self._Write(f"'{literal.Value}'")

	@staticmethod
	def _IsGraphic(text: str) -> bool:
		"""
		Check if all characters are VHDL graphic characters (ISO/IEC 8859-1 without control characters).

		:param text: The text to check.
		:returns:    ``True``, if all characters are graphic characters.
		"""
		return all(32 <= ord(character) <= 126 or 160 <= ord(character) <= 255 for character in text)

	def VisitStringLiteral(self, literal: StringLiteral) -> None:
		"""
		Write a string literal and double each enclosed quotation mark.

		**Format:** ``"say ""hi"" twice"``

		:param literal:          The string literal.
		:raises VHDLWriterError: If the value contains a non-graphic character.
		"""
		if not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("String literal contains a non-graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		value = literal.Value.replace("\"", "\"\"")
		self._Write(f"\"{value}\"")

	def VisitBitStringLiteral(self, literal: BitStringLiteral) -> None:
		"""
		Write a bit string literal.

		**Format:** ``8ux"A0"``

		:param literal:          The bit string literal.
		:raises VHDLWriterError: If the literal's class has no base specifier.
		:raises VHDLWriterError: If a decimal bit string literal is signed or unsigned.
		:raises VHDLWriterError: If the value contains a quotation mark or a non-graphic character.
		"""
		base = self._BASE_SPECIFIERS.get(literal._BASE)
		if base is None:
			ex = VHDLWriterError("Model element is not supported by the VHDL writer.", literal)
			ex.add_note(f"Got type '{getFullyQualifiedName(literal)}'.")
			raise ex

		if literal.IsSigned is None:
			signedness = ""
		elif literal._BASE is BitStringBase.Decimal:
			raise VHDLWriterError("Decimal bit string literal can't be signed or unsigned.", literal)
		elif literal.IsSigned:
			signedness = "s"
		else:
			signedness = "u"

		if "\"" in literal.Value or not self._IsGraphic(literal.Value):
			ex = VHDLWriterError("Bit string literal contains a quotation mark or a non-graphic character.", literal)
			ex.add_note(f"Got value {literal.Value!r}.")
			raise ex

		length = "" if literal.Length is None else str(literal.Length)
		self._Write(f"{length}{signedness}{base}\"{literal.Value}\"")

	def VisitUnaryExpression(self, expression: UnaryExpression) -> None:
		"""
		Write the operator of a unary expression with a reserved word as operator; its operand is a primary.

		**Format:** ``not (a and b)``

		:param expression: The unary expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._Write(f"{self._Keyword(expression._RESERVED_WORD)} ")
		self._minimum = OperatorPrecedence.Primary

	def DepartUnaryExpression(self, expression: UnaryExpression) -> None:
		"""
		Leave a unary expression with a reserved word as operator.

		:param expression: The unary expression.
		"""
		self._Leave()

	def VisitNegationExpression(self, expression: NegationExpression) -> None:
		"""
		Write the sign of a negation; its operand is a term.

		**Format:** ``-a``

		:param expression: The negation.
		"""
		self._Enter(expression._PRECEDENCE)
		self._Write(expression._FORMAT[0])
		self._minimum = OperatorPrecedence.Multiplying

	def DepartNegationExpression(self, expression: NegationExpression) -> None:
		"""
		Leave a negation.

		:param expression: The negation.
		"""
		self._Leave()

	def VisitIdentityExpression(self, expression: IdentityExpression) -> None:
		"""
		Write the sign of an identity; its operand is a term.

		**Format:** ``+a``

		:param expression: The identity.
		"""
		self._Enter(expression._PRECEDENCE)
		self._Write(expression._FORMAT[0])
		self._minimum = OperatorPrecedence.Multiplying

	def DepartIdentityExpression(self, expression: IdentityExpression) -> None:
		"""
		Leave an identity.

		:param expression: The identity.
		"""
		self._Leave()

	def VisitSubExpression(self, expression: SubExpression) -> None:
		"""
		Write the left parenthesis of a parenthesized sub-expression from the source.

		**Format:** ``(a + b)``

		:param expression: The sub-expression.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartSubExpression(self, expression: SubExpression) -> None:
		"""
		Write the right parenthesis of a parenthesized sub-expression from the source.

		:param expression: The sub-expression.
		"""
		self._Write(")")

	def VisitLogicalExpression(self, expression: LogicalExpression) -> None:
		"""
		Enter a binary logical expression; its left operand is a relation or a chain of the same associative operator.

		The associative operators are ``and``, ``or``, ``xor`` and ``xnor``.

		**Format:** ``a and b and c`` or ``(a and b) or c``

		:param expression: The logical expression.
		"""
		self._Enter(expression._PRECEDENCE)
		left = expression.LeftOperand
		if any(
			isinstance(expression, operator) and isinstance(left, operator)
			for operator in (AndExpression, OrExpression, XorExpression, XnorExpression)
		):
			self._minimum = OperatorPrecedence.Logical
		else:
			self._minimum = OperatorPrecedence.Relational

	def DepartLogicalExpression(self, expression: LogicalExpression) -> None:
		"""
		Leave a binary logical expression.

		:param expression: The logical expression.
		"""
		self._Leave()

	def VisitRelationalExpression(self, expression: RelationalExpression) -> None:
		"""
		Enter a relational expression; its left operand is a shift expression.

		**Format:** ``a = b``

		:param expression: The relational expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Shift

	def DepartRelationalExpression(self, expression: RelationalExpression) -> None:
		"""
		Leave a relational expression.

		:param expression: The relational expression.
		"""
		self._Leave()

	def VisitShiftExpression(self, expression: ShiftExpression) -> None:
		"""
		Enter a shift or rotate expression; its left operand is a simple expression.

		**Format:** ``a sll 2``

		:param expression: The shift or rotate expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Adding

	def DepartShiftExpression(self, expression: ShiftExpression) -> None:
		"""
		Leave a shift or rotate expression.

		:param expression: The shift or rotate expression.
		"""
		self._Leave()

	def VisitAddingExpression(self, expression: AddingExpression) -> None:
		"""
		Enter an adding expression; it associates to the left.

		**Format:** ``a - b - c`` or ``a - (b - c)``

		:param expression: The adding expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Adding

	def DepartAddingExpression(self, expression: AddingExpression) -> None:
		"""
		Leave an adding expression.

		:param expression: The adding expression.
		"""
		self._Leave()

	def VisitMultiplyingExpression(self, expression: MultiplyingExpression) -> None:
		"""
		Enter a multiplying expression; it associates to the left.

		**Format:** ``(a + b) * c``

		:param expression: The multiplying expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Multiplying

	def DepartMultiplyingExpression(self, expression: MultiplyingExpression) -> None:
		"""
		Leave a multiplying expression.

		:param expression: The multiplying expression.
		"""
		self._Leave()

	def VisitExponentiationExpression(self, expression: ExponentiationExpression) -> None:
		"""
		Enter an exponentiation; both operands are primaries.

		**Format:** ``a ** (b ** c)``

		:param expression: The exponentiation.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Primary

	def DepartExponentiationExpression(self, expression: ExponentiationExpression) -> None:
		"""
		Leave an exponentiation.

		:param expression: The exponentiation.
		"""
		self._Leave()

	def VisitRangeExpression(self, expression: RangeExpression) -> None:
		"""
		Enter a range expression; its bounds are simple expressions.

		**Format:** ``7 downto 0``

		:param expression: The range expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Adding

	def DepartRangeExpression(self, expression: RangeExpression) -> None:
		"""
		Leave a range expression.

		:param expression: The range expression.
		"""
		self._Leave()

	def VisitWhenElseExpression(self, expression: WhenElseExpression) -> None:
		"""
		Enter a conditional expression; its value and condition are logical expressions.

		**Format:** ``a when c else b``

		:param expression: The conditional expression.
		"""
		self._Enter(expression._PRECEDENCE)
		self._minimum = OperatorPrecedence.Logical

	def DepartWhenElseExpression(self, expression: WhenElseExpression) -> None:
		"""
		Leave a conditional expression.

		:param expression: The conditional expression.
		"""
		self._Leave()

	def DepartQualifiedExpression(self, expression: QualifiedExpression) -> None:
		"""
		Write the right parenthesis closing the operand of a qualified expression, unless the operand brings its own.

		**Format:** ``byte'(others => '0')``

		:param expression: The qualified expression.
		"""
		if not isinstance(expression.Operand, (Aggregate, SubExpression)):
			self._Write(")")

	def VisitSubtypeAllocation(self, allocation: SubtypeAllocation) -> None:
		"""
		Write the reserved word ``new`` of an allocation of a subtype.

		**Format:** ``new node``

		:param allocation: The allocation.
		"""
		self._Write(f"{self._Keyword(ReservedWord.New)} ")

	def VisitQualifiedExpressionAllocation(self, allocation: QualifiedExpressionAllocation) -> None:
		"""
		Write the reserved word ``new`` of an allocation initialized by a qualified expression.

		**Format:** ``new integer'(5)``

		:param allocation: The allocation.
		"""
		self._Write(f"{self._Keyword(ReservedWord.New)} ")

	def VisitAggregate(self, aggregate: Aggregate) -> None:
		"""
		Write the left parenthesis of an aggregate.

		**Format:** ``(0 => '1', others => '0')``

		:param aggregate:        The aggregate.
		:raises VHDLWriterError: If the aggregate has no elements.
		:raises VHDLWriterError: If the aggregate has a single positional element (it would read as parentheses). |br|
		                         Use a named element, e.g. ``others => value``.
		"""
		elements = aggregate.Elements
		if len(elements) == 0:
			raise VHDLWriterError("Aggregate has no elements.", aggregate)
		elif len(elements) == 1 and isinstance(elements[0], SimpleAggregateElement):
			ex = VHDLWriterError("Aggregate with a single positional element has no VHDL notation.", aggregate)
			ex.add_note("Use a named element, e.g. 'others => value'.")
			raise ex

		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartAggregate(self, aggregate: Aggregate) -> None:
		"""
		Write the right parenthesis of an aggregate.

		:param aggregate: The aggregate.
		"""
		self._Write(")")

	def VisitIndexedAggregateElement(self, element: IndexedAggregateElement) -> None:
		"""
		Enter an aggregate element chosen by an index; the index is a simple expression.

		**Format:** ``0 => '1'``

		:param element: The aggregate element.
		"""
		self._minimum = OperatorPrecedence.Adding

	def VisitOthersAggregateElement(self, element: OthersAggregateElement) -> None:
		"""
		Write the choice ``others`` of an aggregate element.

		**Format:** ``others => '0'``

		:param element: The aggregate element.
		"""
		self._Write(f"{self._Keyword(ReservedWord.Others)} => ")
		self._minimum = OperatorPrecedence.Range

	def VisitSimpleRange(self, rng: SimpleRange) -> None:
		"""
		Enter a range given by its bounds; its bounds are simple expressions.

		**Format:** ``0 to 7``

		:param rng: The range.
		"""
		self._Enter(OperatorPrecedence.Range)
		self._minimum = OperatorPrecedence.Adding

	def DepartSimpleRange(self, rng: SimpleRange) -> None:
		"""
		Leave a range given by its bounds.

		:param rng: The range.
		"""
		self._Leave()

	def VisitRangeFromName(self, rng: RangeFromName) -> None:
		"""
		Enter a range denoted by a name.

		**Format:** ``v'range``

		:param rng: The range.
		"""
		self._Enter(OperatorPrecedence.Range)

	def DepartRangeFromName(self, rng: RangeFromName) -> None:
		"""
		Leave a range denoted by a name.

		:param rng: The range.
		"""
		self._Leave()

	def VisitSimpleName(self, name: SimpleName) -> None:
		"""
		Write a simple name.

		**Format:** ``clk``

		:param name: The simple name.
		"""
		self._Write(name.Identifier)

	def DepartSelectedName(self, name: SelectedName) -> None:
		"""
		Write the suffix of a selected name after its prefix.

		**Format:** ``ieee.numeric_std``

		:param name: The selected name.
		"""
		self._Write(f".{name.Identifier}")

	def DepartAllName(self, name: AllName) -> None:
		"""
		Write the suffix ``all`` of a selected name after its prefix, or the reserved word ``all`` without a prefix.

		**Format:** ``ieee.numeric_std.all`` or ``all``

		:param name: The ``all`` name.
		"""
		if name.Prefix is None:
			self._Write(self._Keyword(ReservedWord.All))
		else:
			self._Write(f".{self._Keyword(ReservedWord.All)}")

	def DepartAttributeName(self, name: AttributeName) -> None:
		"""
		Write the attribute designator of an attribute name after its prefix.

		**Format:** ``v'range``

		:param name: The attribute name.
		"""
		self._Write(f"'{name.Identifier}")

	def VisitIndexList(self, name: IndexedName) -> None:
		"""
		Write the left parenthesis of the index list of an indexed name.

		**Format:** ``m(i, j)``

		:param name: The indexed name.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartIndexList(self, name: IndexedName) -> None:
		"""
		Write the right parenthesis of the index list of an indexed name.

		:param name: The indexed name.
		"""
		self._Write(")")

	def VisitAssociationList(self, name: ParenthesisName) -> None:
		"""
		Write the left parenthesis of the association list of a parenthesis name (index, slice or function call).

		**Format:** ``resize(a, 8)``

		The line breaks follow :attr:`VHDLStyle.FunctionCall`.

		:param name: The parenthesis name.
		"""
		self._OpenList(self._style.FunctionCall, ",")
		self._minimum = OperatorPrecedence.Range

	def _OpenList(self, style: ListStyle, separator: str) -> None:
		"""
		Write the left parenthesis of a list; its elements are indented one level deeper.

		:param style:     The layout of the list.
		:param separator: The separator between two elements.
		"""
		writtenList = WrittenList(style, separator, self._indentation)
		self._lists.append(writtenList)
		self._indentation += 1
		self._Write(self._LeftParenthesis(writtenList))

	def _LeftParenthesis(self, writtenList: WrittenList) -> str:
		"""
		Format the left parenthesis of a list with the line break of its layout.

		:param writtenList: The list.
		:returns:           The left parenthesis with its line break and indentation.
		"""
		if writtenList._style._element is NewLine.Add:
			return f"(\n{self._Indentation(writtenList._indentation + 1)}"

		return "("

	def DepartAssociationList(self, name: ParenthesisName) -> None:
		"""
		Write the right parenthesis of the association list of a parenthesis name.

		:param name: The parenthesis name.
		"""
		self._CloseList()

	def _CloseList(self) -> None:
		"""
		Write the right parenthesis of the innermost list being written, one indentation level up.
		"""
		self._indentation -= 1
		self._Write(self._RightParenthesis(self._lists[-1]))
		self._lists.pop()

	def _RightParenthesis(self, writtenList: WrittenList) -> str:
		"""
		Format the right parenthesis of a list with the line break of its layout.

		:param writtenList: The list.
		:returns:           The right parenthesis with its line break and indentation.
		"""
		if writtenList._style._lastCloseParen is NewLine.Add:
			return f"\n{self._Indentation(writtenList._indentation)})"

		return ")"

	def VisitSlicedName(self, name: SlicedName) -> None:
		"""
		Reject a sliced name, because it carries no discrete range.

		:param name:             The sliced name.
		:raises VHDLWriterError: Always, because a sliced name carries no discrete range. |br|
		                         Use a :class:`~pyVHDLModel.Name.ParenthesisName` with a range expression as association.
		"""
		ex = VHDLWriterError("Sliced name carries no discrete range.", name)
		ex.add_note("Use a 'ParenthesisName' with a range expression as association.")
		raise ex

	def VisitOpenName(self, name: OpenName) -> None:
		"""
		Write the reserved word ``open``.

		**Format:** ``open``

		:param name: The ``open`` name.
		"""
		self._Write(self._Keyword(ReservedWord.Open))

	def VisitAssociationItem(self, item: AssociationItem) -> None:
		"""
		Check an association item before its formal and actual are written.

		**Format:** ``formal => actual`` or ``actual``

		:param item:             The association item.
		:raises VHDLWriterError: If the association item has no actual.
		"""
		if item.Actual is None:
			raise VHDLWriterError("Association item has no actual.", item)

	def _WriteIndentation(self) -> None:
		"""
		Write the indentation of the current indentation level.
		"""
		self._Write(self._Indentation(self._indentation))

	def _Indentation(self, level: int) -> str:
		"""
		Format the indentation of an indentation level.

		:param level: The indentation level.
		:returns:     The indentation.
		"""
		if self._style.IndentStyle is IndentStyle.SmartTabs:
			return "\t" * level

		return " " * (level * self._style.IndentSize)

	def VisitVariableAssignment(self, element: WithDefaultExpressionMixin | AssignmentMixin) -> None:
		"""
		Write the variable assignment delimiter (``:=``) before a default expression or the value of a variable assignment.

		:param element: The element with the default expression or the variable assignment.
		"""
		self._Write(" := ")
		self._minimum = OperatorPrecedence.Range

	def VisitIs(
		self,
		element: ModeViewDeclaration | Alias | AttributeSpecification | Subprogram | Architecture | Configuration |
		         ProcessStatement | CaseStatement
	) -> None:
		"""
		Write the reserved word ``is`` ending the header of a declaration; its body is indented.

		In an alias declaration and an attribute specification, the name or the expression follows on the same line. A
		subprogram without declared items and statements is a subprogram declaration, which has no ``is``.

		:param element: The declaration.
		"""
		if isinstance(element, (Alias, AttributeSpecification)):
			self._Write(f" {self._Keyword(ReservedWord.Is)} ")
			self._minimum = OperatorPrecedence.Range
		elif isinstance(element, Subprogram) and not self._IsSubprogramBody(element):
			return
		else:
			self._Write(f" {self._Keyword(ReservedWord.Is)}\n")
			self._indentation += 1

	def VisitRangeConstraint(self, symbol: ConstrainedScalarSubtypeSymbol) -> None:
		"""
		Write the reserved word ``range`` of a range constraint.

		**Format:** ``integer range 0 to 7``

		:param symbol: The constrained subtype symbol.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Range)} ")
		self._minimum = OperatorPrecedence.Range

	def VisitIndexConstraint(
		self,
		element: ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol | ArrayType
	) -> None:
		"""
		Write the left parenthesis of an index constraint.

		**Format:** ``bit_vector(7 downto 0)``

		:param element: The constrained subtype symbol or the array type.
		"""
		self._Write("(")
		self._minimum = OperatorPrecedence.Range

	def DepartIndexConstraint(
		self,
		element: ConstrainedArraySubtypeSymbol | ConstrainedRecordSubtypeSymbol | ArrayType
	) -> None:
		"""
		Write the right parenthesis of an index constraint.

		:param element: The constrained subtype symbol or the array type.
		"""
		self._Write(")")

	def VisitRecordConstraint(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Write the left parenthesis of a record constraint.

		**Format:** ``frame(data(7 downto 0), mask(3 downto 0))``

		:param symbol: The constrained subtype symbol.
		"""
		self._Write("(")

	def DepartRecordConstraint(self, symbol: ConstrainedRecordSubtypeSymbol) -> None:
		"""
		Write the right parenthesis of a record constraint.

		:param symbol: The constrained subtype symbol.
		"""
		self._Write(")")

	def VisitGenericClause(self, element: WithGenericsMixin) -> None:
		"""
		Write the reserved word ``generic`` and the left parenthesis of a generic clause.

		**Format:** ``generic (`` ... ``);``

		The generic clause of a subprogram follows its designator on the same line and ends without a semicolon. The line
		breaks follow :attr:`VHDLStyle.SubprogramGenericClause` for a subprogram, otherwise :attr:`VHDLStyle.GenericClause`.

		:param element: The element with generics.
		"""
		if isinstance(element, Subprogram):
			self._Write(f" {self._Keyword(ReservedWord.Generic)} ")
			self._OpenList(self._style.SubprogramGenericClause, ";")
		else:
			self._WriteIndentation()
			self._Write(f"{self._Keyword(ReservedWord.Generic)} ")
			self._OpenList(self._style.GenericClause, ";")

	def DepartGenericClause(self, element: WithGenericsMixin) -> None:
		"""
		Write the right parenthesis of a generic clause.

		:param element: The element with generics.
		"""
		self._CloseList()
		if not isinstance(element, Subprogram):
			self._Write(";\n")

	def VisitPortClause(self, element: WithPortsMixin) -> None:
		"""
		Write the reserved word ``port`` and the left parenthesis of a port clause.

		**Format:** ``port (`` ... ``);``

		The line breaks follow :attr:`VHDLStyle.PortClause`.

		:param element: The element with ports.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Port)} ")
		self._OpenList(self._style.PortClause, ";")

	def DepartPortClause(self, element: WithPortsMixin) -> None:
		"""
		Write the right parenthesis of a port clause.

		:param element: The element with ports.
		"""
		self._CloseList()
		self._Write(";\n")

	def VisitConstant(self, constant: Constant) -> None:
		"""
		Write the reserved word ``constant`` and the identifiers of a constant declaration.

		**Format:** ``constant BITS : positive := 8;``

		:param constant: The constant declaration.
		"""
		self._WriteObjectDeclaration(constant)

	def _WriteObjectDeclaration(self, obj: Obj) -> None:
		"""
		Write the indentation, the object class reserved word and the identifiers of an object declaration.

		:param obj: The object declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keywords(obj._OBJECT_KEYWORD)} {', '.join(obj.Identifiers)} : ")

	def DepartConstant(self, constant: Constant) -> None:
		"""
		Write the semicolon ending a constant declaration.

		:param constant: The constant declaration.
		"""
		self._Write(";\n")

	def VisitDeferredConstant(self, constant: DeferredConstant) -> None:
		"""
		Write the reserved word ``constant`` and the identifiers of a deferred constant declaration.

		**Format:** ``constant BITS : positive;``

		:param constant: The deferred constant declaration.
		"""
		self._WriteObjectDeclaration(constant)

	def DepartDeferredConstant(self, constant: DeferredConstant) -> None:
		"""
		Write the semicolon ending a deferred constant declaration.

		:param constant: The deferred constant declaration.
		"""
		self._Write(";\n")

	def VisitVariable(self, variable: Variable) -> None:
		"""
		Write the reserved word ``variable`` and the identifiers of a variable declaration.

		**Format:** ``variable count : natural := 0;``

		:param variable: The variable declaration.
		"""
		self._WriteObjectDeclaration(variable)

	def DepartVariable(self, variable: Variable) -> None:
		"""
		Write the semicolon ending a variable declaration.

		:param variable: The variable declaration.
		"""
		self._Write(";\n")

	def VisitSharedVariable(self, variable: SharedVariable) -> None:
		"""
		Write the reserved words ``shared variable`` and the identifiers of a shared variable declaration.

		**Format:** ``shared variable counter : counter_t;``

		:param variable: The shared variable declaration.
		"""
		self._WriteObjectDeclaration(variable)

	def DepartSharedVariable(self, variable: SharedVariable) -> None:
		"""
		Write the semicolon ending a shared variable declaration.

		:param variable: The shared variable declaration.
		"""
		self._Write(";\n")

	def VisitSignal(self, signal: Signal) -> None:
		"""
		Write the reserved word ``signal`` and the identifiers of a signal declaration.

		**Format:** ``signal a, b : bit := '0';``

		:param signal: The signal declaration.
		"""
		self._WriteObjectDeclaration(signal)

	def DepartSignal(self, signal: Signal) -> None:
		"""
		Write the semicolon ending a signal declaration.

		:param signal: The signal declaration.
		"""
		self._Write(";\n")

	def VisitFile(self, file: File) -> None:
		"""
		Write the reserved word ``file`` and the identifiers of a file declaration.

		**Format:** ``file input : text;``

		The model carries no file open information, so none is written.

		:param file: The file declaration.
		"""
		self._WriteObjectDeclaration(file)

	def DepartFile(self, file: File) -> None:
		"""
		Write the semicolon ending a file declaration.

		:param file: The file declaration.
		"""
		self._Write(";\n")

	def VisitGenericConstantInterfaceItem(self, item: GenericConstantInterfaceItem) -> None:
		"""
		Write the identifiers and the mode of a generic constant.

		**Format:** ``BITS : positive := 8``

		:param item: The generic constant.
		"""
		self._WriteInterfaceItem(item, (), item.Mode)

	def _WriteInterfaceItem(self, item: Obj, keywords: tuple[ReservedWord, ...], mode: Mode) -> None:
		"""
		Write the object class reserved words (if any), the identifiers and the mode (if any) of an interface item.

		:param item:     The interface item.
		:param keywords: The object class reserved words, or an empty tuple.
		:param mode:     The mode; ``Mode.Default`` writes none.
		"""
		if len(keywords) > 0:
			self._Write(f"{self._Keywords(keywords)} ")

		self._Write(f"{', '.join(item.Identifiers)} : ")
		if mode is not Mode.Default:
			self._Write(f"{self._Keyword(mode.ReservedWord)} ")

	def VisitGenericTypeInterfaceItem(self, item: GenericTypeInterfaceItem) -> None:
		"""
		Write a generic type.

		**Format:** ``type T``

		:param item: The generic type.
		"""
		self._Write(f"{self._Keyword(ReservedWord.Type)} {item.Identifier}")

	def VisitPortSimpleSignalInterfaceItem(self, item: PortSimpleSignalInterfaceItem) -> None:
		"""
		Write the identifiers and the mode of a port.

		**Format:** ``clk : in std_logic``

		:param item: The port.
		"""
		self._WriteInterfaceItem(item, (), item.Mode)

	def VisitPortViewSignalInterfaceItem(self, item: PortViewSignalInterfaceItem) -> None:
		"""
		Write the identifiers and the reserved word ``view`` of a port with a mode view.

		**Format:** ``link : view master``

		:param item: The port.
		"""
		self._WriteInterfaceItem(item, (), Mode.Default)
		self._Write(f"{self._Keyword(ReservedWord.View)} ")

	def VisitParameterConstantInterfaceItem(self, item: ParameterConstantInterfaceItem) -> None:
		"""
		Write the reserved word ``constant``, the identifiers and the mode of a constant parameter.

		**Format:** ``constant value : in integer``

		:param item: The constant parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, item.Mode)

	def VisitParameterVariableInterfaceItem(self, item: ParameterVariableInterfaceItem) -> None:
		"""
		Write the reserved word ``variable``, the identifiers and the mode of a variable parameter.

		**Format:** ``variable result : out integer``

		:param item: The variable parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, item.Mode)

	def VisitParameterSimpleSignalInterfaceItem(self, item: ParameterSimpleSignalInterfaceItem) -> None:
		"""
		Write the reserved word ``signal``, the identifiers and the mode of a signal parameter.

		**Format:** ``signal clk : in std_logic``

		:param item: The signal parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, item.Mode)

	def VisitParameterViewSignalInterfaceItem(self, item: ParameterViewSignalInterfaceItem) -> None:
		"""
		Write the reserved word ``signal``, the identifiers and the reserved word ``view`` of a signal parameter.

		**Format:** ``signal link : view master``

		:param item: The signal parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, Mode.Default)
		self._Write(f"{self._Keyword(ReservedWord.View)} ")

	def VisitParameterFileInterfaceItem(self, item: ParameterFileInterfaceItem) -> None:
		"""
		Write the reserved word ``file`` and the identifiers of a file parameter.

		**Format:** ``file input : text``

		:param item: The file parameter.
		"""
		self._WriteInterfaceItem(item, item._OBJECT_KEYWORD, Mode.Default)

	def VisitModeViewDeclaration(self, declaration: ModeViewDeclaration) -> None:
		"""
		Write the reserved word ``view``, the identifier and the reserved word ``of`` of a mode view declaration.

		**Format:** ``view master of bus_t is`` ... ``end view master;``

		:param declaration: The mode view declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.View)} {declaration.Identifier} {self._Keyword(ReservedWord.Of)} ")

	def DepartModeViewDeclaration(self, declaration: ModeViewDeclaration) -> None:
		"""
		Write the end of a mode view declaration.

		:param declaration: The mode view declaration.
		"""
		self._WriteEnd((ReservedWord.View,), declaration.Identifier)

	def _WriteEnd(self, keywords: tuple[ReservedWord, ...], identifier: Nullable[str]) -> None:
		"""
		Leave the indented body and write the reserved word ``end``, the given reserved words and the identifier.

		:param keywords:   The reserved words after ``end``.
		:param identifier: The identifier or label of the declaration or statement, or ``None`` if it has none.
		"""
		self._indentation -= 1
		self._WriteEndLine(keywords, identifier)

	def _WriteEndLine(self, keywords: tuple[ReservedWord, ...], identifier: Nullable[str]) -> None:
		"""
		Write the reserved word ``end``, the given reserved words and the identifier on a line of the current level.

		:param keywords:   The reserved words after ``end``.
		:param identifier: The identifier or label of the declaration or statement, or ``None`` if it has none.
		"""
		self._WriteIndentation()
		if identifier is None:
			self._Write(f"{self._Keyword(ReservedWord.End)} {self._Keywords(keywords)};\n")
		else:
			self._Write(f"{self._Keyword(ReservedWord.End)} {self._Keywords(keywords)} {identifier};\n")

	def VisitSimpleModeViewElement(self, element: SimpleModeViewElement) -> None:
		"""
		Write an element of a mode view with a mode.

		**Format:** ``valid, data : out;``

		:param element:          The mode view element.
		:raises VHDLWriterError: If the mode view element has no mode.
		"""
		if element.Mode is Mode.Default:
			raise VHDLWriterError("Mode view element has no mode.", element)

		self._WriteIndentation()
		self._Write(f"{', '.join(element.Identifiers)} : {self._Keyword(element.Mode.ReservedWord)};\n")

	def VisitCompositeModeViewElement(self, element: CompositeModeViewElement) -> None:
		"""
		Write the identifiers and the reserved word ``view`` of an element of a mode view with a mode view.

		**Format:** ``request : view master;``

		:param element: The mode view element.
		"""
		self._WriteIndentation()
		self._Write(f"{', '.join(element.Identifiers)} : {self._Keyword(ReservedWord.View)} ")

	def DepartCompositeModeViewElement(self, element: CompositeModeViewElement) -> None:
		"""
		Write the semicolon ending an element of a mode view with a mode view.

		:param element: The mode view element.
		"""
		self._Write(";\n")

	def VisitComponent(self, component: Component) -> None:
		"""
		Write the header of a component declaration; its generic and port clauses are indented.

		**Format:** ``component counter is`` ... ``end component counter;``

		:param component: The component declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Component)} {component.Identifier} {self._Keyword(ReservedWord.Is)}\n")
		self._indentation += 1

	def DepartComponent(self, component: Component) -> None:
		"""
		Write the end of a component declaration.

		:param component: The component declaration.
		"""
		self._WriteEnd((ReservedWord.Component,), component.Identifier)

	def VisitBox(self, arrayType: ArrayType) -> None:
		"""
		Write the reserved word ``range`` and the box (``<>``) of an unbounded index of an array type.

		**Format:** ``natural range <>``

		:param arrayType: The array type.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Range)} <>")

	def VisitOf(self, arrayType: ArrayType) -> None:
		"""
		Write the reserved word ``of`` before the element subtype of an array type.

		:param arrayType: The array type.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Of)} ")

	def VisitUnits(self, physicalType: PhysicalType) -> None:
		"""
		Write the reserved word ``units`` and the primary unit of a physical type on their own lines.

		:param physicalType: The physical type.
		"""
		self._Write("\n")
		self._indentation += 1
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Units)}\n")
		self._indentation += 1
		self._WriteIndentation()
		self._Write(f"{physicalType.PrimaryUnit};\n")

	def VisitSecondaryUnitDeclaration(self, physicalType: PhysicalType, identifier: str) -> None:
		"""
		Write the identifier of a secondary unit declaration.

		**Format:** ``mm = 1000 um;``

		:param physicalType: The physical type.
		:param identifier:   The identifier of the secondary unit.
		"""
		self._WriteIndentation()
		self._Write(f"{identifier} = ")
		self._minimum = OperatorPrecedence.Range

	def DepartSecondaryUnitDeclaration(self, physicalType: PhysicalType, identifier: str) -> None:
		"""
		Write the semicolon ending a secondary unit declaration.

		:param physicalType: The physical type.
		:param identifier:   The identifier of the secondary unit.
		"""
		self._Write(";\n")

	def VisitEntitySpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the reserved word ``of`` before the names of an attribute specification.

		:param specification: The attribute specification.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Of)} ")

	def DepartEntitySpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the entity class after the names of an attribute specification.

		:param specification: The attribute specification.
		"""
		self._Write(f" : {self._Keyword(specification.EntityClass.ReservedWord)}")

	def VisitAnonymousType(self, declaration: AnonymousType) -> None:
		"""
		Write an incomplete type declaration.

		**Format:** ``type node;``

		:param declaration: The incomplete type declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Type)} {declaration.Identifier};\n")

	def VisitSubtype(self, subtype: Subtype) -> None:
		"""
		Write the reserved word ``subtype``, the identifier and the reserved word ``is`` of a subtype declaration.

		**Format:** ``subtype byte is bit_vector(7 downto 0);``

		The model's resolution function of a subtype is not written.

		:param subtype: The subtype declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Subtype)} {subtype.Identifier} {self._Keyword(ReservedWord.Is)} ")

	def DepartSubtype(self, subtype: Subtype) -> None:
		"""
		Write the semicolon ending a subtype declaration.

		:param subtype: The subtype declaration.
		"""
		self._Write(";\n")

	def VisitEnumeratedType(self, enumeratedType: EnumeratedType) -> None:
		"""
		Write the header and the left parenthesis of an enumerated type declaration.

		**Format:** ``type state is (Idle, Busy, Done);``

		:param enumeratedType: The enumerated type.
		"""
		self._WriteTypeHeader(enumeratedType)
		self._Write("(")

	def _WriteTypeHeader(self, declaration: FullType) -> None:
		"""
		Write the indentation, the reserved word ``type``, the identifier and the reserved word ``is`` of a type.

		:param declaration: The type declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Type)} {declaration.Identifier} {self._Keyword(ReservedWord.Is)} ")

	def DepartEnumeratedType(self, enumeratedType: EnumeratedType) -> None:
		"""
		Write the right parenthesis ending an enumerated type declaration.

		:param enumeratedType: The enumerated type.
		"""
		self._Write(");\n")

	def VisitIntegerType(self, integerType: IntegerType) -> None:
		"""
		Write the header and the reserved word ``range`` of an integer type declaration.

		**Format:** ``type nibble is range 0 to 15;``

		:param integerType: The integer type.
		"""
		self._WriteTypeHeader(integerType)
		self._Write(f"{self._Keyword(ReservedWord.Range)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartIntegerType(self, integerType: IntegerType) -> None:
		"""
		Write the semicolon ending an integer type declaration.

		:param integerType: The integer type.
		"""
		self._Write(";\n")

	def VisitRealType(self, realType: RealType) -> None:
		"""
		Write the header and the reserved word ``range`` of a floating-point type declaration.

		**Format:** ``type fraction is range 0.0 to 1.0;``

		:param realType: The floating-point type.
		"""
		self._WriteTypeHeader(realType)
		self._Write(f"{self._Keyword(ReservedWord.Range)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartRealType(self, realType: RealType) -> None:
		"""
		Write the semicolon ending a floating-point type declaration.

		:param realType: The floating-point type.
		"""
		self._Write(";\n")

	def VisitPhysicalType(self, physicalType: PhysicalType) -> None:
		"""
		Write the header and the reserved word ``range`` of a physical type declaration; its units are indented.

		**Format:** ``type distance is range 0 to 1000000`` ... ``units`` ... ``end units distance;``

		:param physicalType: The physical type.
		"""
		self._WriteTypeHeader(physicalType)
		self._Write(f"{self._Keyword(ReservedWord.Range)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartPhysicalType(self, physicalType: PhysicalType) -> None:
		"""
		Write the end of the units of a physical type declaration.

		:param physicalType: The physical type.
		"""
		self._WriteEnd((ReservedWord.Units,), physicalType.Identifier)
		self._indentation -= 1

	def VisitArrayType(self, arrayType: ArrayType) -> None:
		"""
		Write the header and the reserved word ``array`` of an array type declaration.

		**Format:** ``type memory is array (0 to 255) of byte;`` or ``type bits is array (natural range <>) of bit;``

		:param arrayType: The array type.
		"""
		self._WriteTypeHeader(arrayType)
		self._Write(f"{self._Keyword(ReservedWord.Array)} ")

	def DepartArrayType(self, arrayType: ArrayType) -> None:
		"""
		Write the semicolon ending an array type declaration.

		:param arrayType: The array type.
		"""
		self._Write(";\n")

	def VisitRecordType(self, recordType: RecordType) -> None:
		"""
		Write the header of a record type declaration; its element declarations are indented.

		**Format:** ``type frame is record`` ... ``end record frame;``

		:param recordType: The record type.
		"""
		self._WriteTypeHeader(recordType)
		self._Write(f"{self._Keyword(ReservedWord.Record)}\n")
		self._indentation += 1

	def DepartRecordType(self, recordType: RecordType) -> None:
		"""
		Write the end of a record type declaration.

		:param recordType: The record type.
		"""
		self._WriteEnd((ReservedWord.Record,), recordType.Identifier)

	def VisitRecordTypeElement(self, element: RecordTypeElement) -> None:
		"""
		Write the identifiers of an element declaration of a record type.

		**Format:** ``valid, last : bit;``

		:param element: The record element declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{', '.join(element.Identifiers)} : ")

	def DepartRecordTypeElement(self, element: RecordTypeElement) -> None:
		"""
		Write the semicolon ending an element declaration of a record type.

		:param element: The record element declaration.
		"""
		self._Write(";\n")

	def VisitAccessType(self, accessType: AccessType) -> None:
		"""
		Write the header and the reserved word ``access`` of an access type declaration.

		**Format:** ``type pointer is access node;``

		:param accessType: The access type.
		"""
		self._WriteTypeHeader(accessType)
		self._Write(f"{self._Keyword(ReservedWord.Access)} ")

	def DepartAccessType(self, accessType: AccessType) -> None:
		"""
		Write the semicolon ending an access type declaration.

		:param accessType: The access type.
		"""
		self._Write(";\n")

	def VisitFileType(self, fileType: FileType) -> None:
		"""
		Write the header and the reserved words ``file of`` of a file type declaration.

		**Format:** ``type text_file is file of string;``

		:param fileType: The file type.
		"""
		self._WriteTypeHeader(fileType)
		self._Write(f"{self._Keyword(ReservedWord.File)} {self._Keyword(ReservedWord.Of)} ")

	def DepartFileType(self, fileType: FileType) -> None:
		"""
		Write the semicolon ending a file type declaration.

		:param fileType: The file type.
		"""
		self._Write(";\n")

	def VisitAlias(self, alias: Alias) -> None:
		"""
		Write the reserved word ``alias`` and the identifier of an alias declaration.

		**Format:** ``alias low : bit_vector(3 downto 0) is data(3 downto 0);`` or ``alias clock is clk;``

		:param alias: The alias declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Alias)} {alias.Identifier}")
		if alias.Subtype is not None:
			self._Write(" : ")

	def DepartAlias(self, alias: Alias) -> None:
		"""
		Write the semicolon ending an alias declaration.

		:param alias: The alias declaration.
		"""
		self._Write(";\n")

	def VisitAttribute(self, attribute: Attribute) -> None:
		"""
		Write the reserved word ``attribute`` and the identifier of an attribute declaration.

		**Format:** ``attribute keep : boolean;``

		:param attribute: The attribute declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Attribute)} {attribute.Identifier} : ")

	def DepartAttribute(self, attribute: Attribute) -> None:
		"""
		Write the semicolon ending an attribute declaration.

		:param attribute: The attribute declaration.
		"""
		self._Write(";\n")

	def VisitAttributeSpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the reserved word ``attribute`` of an attribute specification.

		**Format:** ``attribute keep of valid, ready : signal is true;``

		:param specification:    The attribute specification.
		:raises VHDLWriterError: If the entity class is ``EntityClass.Others``.
		"""
		if specification.EntityClass is EntityClass.Others:
			raise VHDLWriterError("Entity class 'Others' has no VHDL notation.", specification)

		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Attribute)} ")

	def DepartAttributeSpecification(self, specification: AttributeSpecification) -> None:
		"""
		Write the semicolon ending an attribute specification.

		:param specification: The attribute specification.
		"""
		self._Write(";\n")

	def VisitBegin(
		self,
		element: Subprogram | Entity | Architecture | ProcessStatement | ConcurrentBlockStatement | GenerateBranch |
		         ConcurrentCase | ForGenerateStatement
	) -> None:
		"""
		Write the reserved word ``begin`` before the statement part on its own line.

		A subprogram declaration, an entity without statements and the body of a generate statement without declared items
		have no ``begin``.

		:param element: The element with a statement part.
		"""
		if isinstance(element, Subprogram) and not self._IsSubprogramBody(element):
			return
		elif isinstance(element, Entity) and len(element.Statements) == 0:
			return
		elif isinstance(element, (GenerateBranch, ConcurrentCase, ForGenerateStatement)):
			if len(element.DeclaredItems) == 0:
				return

		self._indentation -= 1
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Begin)}\n")
		self._indentation += 1

	@staticmethod
	def _IsSubprogramBody(subprogram: Subprogram) -> bool:
		"""
		Check if a subprogram is written as a subprogram body.

		A subprogram is a body, if it has declared items or statements, or if its parent is neither a package declaration
		nor a protected type declaration (e.g. a package body or an architecture).

		:param subprogram: The subprogram.
		:returns:          ``True``, if the subprogram is written as a subprogram body.
		"""
		if len(subprogram.DeclaredItems) > 0 or len(subprogram.Statements) > 0:
			return True

		return subprogram.Parent is not None and not isinstance(subprogram.Parent, (Package, ProtectedType))

	def VisitReturn(self, function: Function | GenericFunctionInterfaceItem) -> None:
		"""
		Write the reserved word ``return`` before the return type of a function.

		:param function: The function.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Return)} ")

	def VisitFormalParameterList(self, element: WithParametersMixin) -> None:
		"""
		Write the left parenthesis of a formal parameter list.

		**Format:** ``procedure p (`` ... ``)``

		After a generic clause, the reserved word ``parameter`` precedes the left parenthesis. The line breaks follow
		:attr:`VHDLStyle.ParameterList`.

		:param element: The element with parameters.
		"""
		if isinstance(element, WithGenericsMixin) and len(element.GenericItems) > 0:
			self._Write(f" {self._Keyword(ReservedWord.Parameter)} ")
		else:
			self._Write(" ")

		self._OpenList(self._style.ParameterList, ";")

	def DepartFormalParameterList(self, element: WithParametersMixin) -> None:
		"""
		Write the right parenthesis of a formal parameter list.

		:param element: The element with parameters.
		"""
		self._CloseList()

	def VisitGenericMapAspect(self, element: GenericMapAspectMixin) -> None:
		"""
		Write the reserved words ``generic map`` and the left parenthesis on a new line.

		**Format:** ``generic map (`` ... ``)``

		The generic map aspect of a block statement is written like its generic clause and ends with a semicolon. The line
		breaks follow :attr:`VHDLStyle.GenericMap`.

		:param element: The element with a generic map aspect.
		"""
		self._WriteMapAspect(ReservedWord.Generic, element, self._style.GenericMap)

	def _WriteMapAspect(
		self,
		keyword: ReservedWord,
		element: GenericMapAspectMixin | PortMapAspectMixin,
		style:   ListStyle
	) -> None:
		"""
		Write the reserved words of a map aspect and the left parenthesis on a new line, one indentation level deeper.

		In a block statement, the map aspect starts its own line at the block header's indentation level.

		:param keyword: The reserved word ``generic`` or ``port``.
		:param element: The element with the map aspect.
		:param style:   The layout of the map aspect's association list.
		"""
		if not isinstance(element, ConcurrentBlockStatement):
			self._Write("\n")
			self._indentation += 1

		self._WriteIndentation()
		self._Write(f"{self._Keyword(keyword)} {self._Keyword(ReservedWord.Map)} ")
		self._OpenList(style, ",")

	def DepartGenericMapAspect(self, element: GenericMapAspectMixin) -> None:
		"""
		Write the right parenthesis of a generic map aspect.

		:param element: The element with a generic map aspect.
		"""
		self._WriteMapAspectEnd(element)

	def _WriteMapAspectEnd(self, element: GenericMapAspectMixin | PortMapAspectMixin) -> None:
		"""
		Write the right parenthesis of a map aspect and leave its indentation level.

		In a block statement, a semicolon follows the right parenthesis.

		:param element: The element with the map aspect.
		"""
		self._CloseList()
		if isinstance(element, ConcurrentBlockStatement):
			self._Write(";\n")
		else:
			self._indentation -= 1

	def VisitProcedure(self, procedure: Procedure) -> None:
		"""
		Write the reserved word ``procedure`` and the designator of a procedure declaration or body.

		**Format:** ``procedure reset;`` or ``procedure reset is`` ... ``begin`` ... ``end procedure reset;``

		A procedure without declared items and statements is written as a procedure declaration.

		:param procedure: The procedure.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Procedure)} {procedure.Identifier}")

	def DepartProcedure(self, procedure: Procedure) -> None:
		"""
		Write the semicolon ending a procedure declaration, or the end of a procedure body.

		:param procedure: The procedure.
		"""
		if self._IsSubprogramBody(procedure):
			self._WriteEnd((ReservedWord.Procedure,), procedure.Identifier)
		else:
			self._Write(";\n")

	def VisitFunction(self, function: Function) -> None:
		"""
		Write the reserved word ``impure``, if impure, ``function`` and the designator of a function declaration or body.

		**Format:** ``function parity return bit;`` or ``function parity return bit is`` ... ``end function parity;``

		A function without declared items and statements is written as a function declaration.

		:param function: The function.
		"""
		self._WriteIndentation()
		self._WriteFunctionDesignator(function)

	def _WriteFunctionDesignator(self, function: Function) -> None:
		"""
		Write the reserved word ``impure``, if impure, the reserved word ``function`` and the designator of a function.

		:param function: The function.
		"""
		if not function.IsPure:
			self._Write(f"{self._Keyword(ReservedWord.Impure)} ")

		self._Write(f"{self._Keyword(ReservedWord.Function)} {function.Identifier}")

	def DepartFunction(self, function: Function) -> None:
		"""
		Write the semicolon ending a function declaration, or the end of a function body.

		:param function: The function.
		"""
		if self._IsSubprogramBody(function):
			self._WriteEnd((ReservedWord.Function,), function.Identifier)
		else:
			self._Write(";\n")

	def VisitGenericProcedureInterfaceItem(self, item: GenericProcedureInterfaceItem) -> None:
		"""
		Write the reserved word ``procedure`` and the designator of a generic procedure.

		**Format:** ``procedure log (`` ... ``)``

		:param item: The generic procedure.
		"""
		self._Write(f"{self._Keyword(ReservedWord.Procedure)} {item.Identifier}")

	def VisitGenericFunctionInterfaceItem(self, item: GenericFunctionInterfaceItem) -> None:
		"""
		Write the reserved word ``impure``, if impure, ``function`` and the designator of a generic function.

		**Format:** ``function compare (`` ... ``) return boolean``

		:param item: The generic function.
		"""
		self._WriteFunctionDesignator(item)

	def VisitProcedureInstantiation(self, instantiation: ProcedureInstantiation) -> None:
		"""
		Write the reserved word ``procedure``, the designator and the reserved words ``is new`` of a procedure
		instantiation.

		**Format:** ``procedure log_byte is new log`` ... ``;``

		:param instantiation: The procedure instantiation.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Procedure)} {instantiation.Identifier} ")
		self._Write(f"{self._Keyword(ReservedWord.Is)} {self._Keyword(ReservedWord.New)} ")

	def DepartProcedureInstantiation(self, instantiation: ProcedureInstantiation) -> None:
		"""
		Write the semicolon ending a procedure instantiation.

		:param instantiation: The procedure instantiation.
		"""
		self._Write(";\n")

	def VisitFunctionInstantiation(self, instantiation: FunctionInstantiation) -> None:
		"""
		Write the reserved word ``function``, the designator and the reserved words ``is new`` of a function instantiation.

		**Format:** ``function maximum_byte is new maximum`` ... ``;``

		:param instantiation: The function instantiation.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Function)} {instantiation.Identifier} ")
		self._Write(f"{self._Keyword(ReservedWord.Is)} {self._Keyword(ReservedWord.New)} ")

	def DepartFunctionInstantiation(self, instantiation: FunctionInstantiation) -> None:
		"""
		Write the semicolon ending a function instantiation.

		:param instantiation: The function instantiation.
		"""
		self._Write(";\n")

	def VisitProtectedType(self, protectedType: ProtectedType) -> None:
		"""
		Write the header of a protected type declaration; its methods are indented.

		**Format:** ``type counter is protected`` ... ``end protected counter;``

		:param protectedType: The protected type.
		"""
		self._WriteTypeHeader(protectedType)
		self._Write(f"{self._Keyword(ReservedWord.Protected)}\n")
		self._indentation += 1

	def DepartProtectedType(self, protectedType: ProtectedType) -> None:
		"""
		Write the end of a protected type declaration.

		:param protectedType: The protected type.
		"""
		self._WriteEnd((ReservedWord.Protected,), protectedType.Identifier)

	def VisitProtectedTypeBody(self, body: ProtectedTypeBody) -> None:
		"""
		Write the header of a protected type body; its declared items are indented.

		**Format:** ``type counter is protected body`` ... ``end protected body counter;``

		:param body: The protected type body.
		"""
		self._WriteTypeHeader(body)
		self._Write(f"{self._Keyword(ReservedWord.Protected)} {self._Keyword(ReservedWord.Body)}\n")
		self._indentation += 1

	def DepartProtectedTypeBody(self, body: ProtectedTypeBody) -> None:
		"""
		Write the end of a protected type body.

		:param body: The protected type body.
		"""
		self._WriteEnd((ReservedWord.Protected, ReservedWord.Body), body.Identifier)

	def VisitPortMapAspect(self, element: PortMapAspectMixin) -> None:
		"""
		Write the reserved words ``port map`` and the left parenthesis on a new line.

		**Format:** ``port map (`` ... ``)``

		The line breaks follow :attr:`VHDLStyle.PortMap`.

		:param element: The element with a port map aspect.
		"""
		self._WriteMapAspect(ReservedWord.Port, element, self._style.PortMap)

	def DepartPortMapAspect(self, element: PortMapAspectMixin) -> None:
		"""
		Write the right parenthesis of a port map aspect.

		:param element: The element with a port map aspect.
		"""
		self._WriteMapAspectEnd(element)

	def VisitContextClause(self, designUnit: DesignUnit) -> None:
		"""
		Separate a design unit by a blank line from the text written before it.

		:param designUnit: The design unit.
		"""
		if len(self._buffer) > 0:
			self._Write("\n")

	def DepartContextClause(self, designUnit: DesignUnit) -> None:
		"""
		Separate the context items of a design unit by a blank line from the design unit.

		:param designUnit: The design unit.
		"""
		if len(designUnit.ContextItems) > 0:
			self._Write("\n")

	def VisitLibraryClause(self, clause: LibraryClause) -> None:
		"""
		Write the reserved word ``library`` of a library clause.

		**Format:** ``library ieee;``

		:param clause: The library clause.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Library)} ")

	def DepartLibraryClause(self, clause: LibraryClause) -> None:
		"""
		Write the semicolon ending a library clause.

		:param clause: The library clause.
		"""
		self._Write(";\n")

	def VisitUseClause(self, clause: UseClause) -> None:
		"""
		Write the reserved word ``use`` of a use clause.

		**Format:** ``use ieee.numeric_std.all;``

		:param clause: The use clause.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Use)} ")

	def DepartUseClause(self, clause: UseClause) -> None:
		"""
		Write the semicolon ending a use clause.

		:param clause: The use clause.
		"""
		self._Write(";\n")

	def VisitContextReference(self, reference: ContextReference) -> None:
		"""
		Write the reserved word ``context`` of a context reference.

		**Format:** ``context ieee.ieee_std_context;``

		:param reference: The context reference.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Context)} ")

	def DepartContextReference(self, reference: ContextReference) -> None:
		"""
		Write the semicolon ending a context reference.

		:param reference: The context reference.
		"""
		self._Write(";\n")

	def VisitContext(self, context: Context) -> None:
		"""
		Write the header of a context declaration; its context items are indented.

		**Format:** ``context project is`` ... ``end context project;``

		:param context: The context declaration.
		"""
		self._WriteUnitHeader((ReservedWord.Context,), context.Identifier)

	def _WriteUnitHeader(self, keywords: tuple[ReservedWord, ...], identifier: str) -> None:
		"""
		Write the reserved words, the identifier and the reserved word ``is`` of a header; the body is indented.

		:param keywords:   The reserved words before the identifier.
		:param identifier: The identifier.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keywords(keywords)} {identifier} {self._Keyword(ReservedWord.Is)}\n")
		self._indentation += 1

	def DepartContext(self, context: Context) -> None:
		"""
		Write the end of a context declaration.

		:param context: The context declaration.
		"""
		self._WriteEnd((ReservedWord.Context,), context.Identifier)

	def VisitPackage(self, package: Package) -> None:
		"""
		Write the header of a package declaration; its generic clause and declared items are indented.

		**Format:** ``package utilities is`` ... ``end package utilities;``

		:param package: The package declaration.
		"""
		self._WriteUnitHeader((ReservedWord.Package,), package.Identifier)

	def DepartPackage(self, package: Package) -> None:
		"""
		Write the end of a package declaration.

		:param package: The package declaration.
		"""
		self._WriteEnd((ReservedWord.Package,), package.Identifier)

	def VisitPackageBody(self, body: PackageBody) -> None:
		"""
		Write the header of a package body; its declared items are indented.

		**Format:** ``package body utilities is`` ... ``end package body utilities;``

		:param body: The package body.
		"""
		self._WriteUnitHeader((ReservedWord.Package, ReservedWord.Body), body.Identifier)

	def DepartPackageBody(self, body: PackageBody) -> None:
		"""
		Write the end of a package body.

		:param body: The package body.
		"""
		self._WriteEnd((ReservedWord.Package, ReservedWord.Body), body.Identifier)

	def VisitPackageInstantiation(self, instantiation: PackageInstantiation) -> None:
		"""
		Write the reserved word ``package``, the identifier and the reserved words ``is new`` of a package instantiation.

		**Format:** ``package fifo_byte is new work.fifo`` ... ``;``

		:param instantiation: The package instantiation.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Package)} {instantiation.Identifier} ")
		self._Write(f"{self._Keywords((ReservedWord.Is, ReservedWord.New))} ")

	def DepartPackageInstantiation(self, instantiation: PackageInstantiation) -> None:
		"""
		Write the semicolon ending a package instantiation.

		:param instantiation: The package instantiation.
		"""
		self._Write(";\n")

	def VisitEntity(self, entity: Entity) -> None:
		"""
		Write the header of an entity declaration; its generic and port clauses and its declared items are indented.

		**Format:** ``entity counter is`` ... ``end entity counter;``

		:param entity: The entity declaration.
		"""
		self._WriteUnitHeader((ReservedWord.Entity,), entity.Identifier)

	def DepartEntity(self, entity: Entity) -> None:
		"""
		Write the end of an entity declaration.

		:param entity: The entity declaration.
		"""
		self._WriteEnd((ReservedWord.Entity,), entity.Identifier)

	def VisitArchitecture(self, architecture: Architecture) -> None:
		"""
		Write the reserved word ``architecture``, the identifier and the reserved word ``of`` of an architecture body.

		**Format:** ``architecture rtl of counter is`` ... ``begin`` ... ``end architecture rtl;``

		:param architecture: The architecture body.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Architecture)} {architecture.Identifier} ")
		self._Write(f"{self._Keyword(ReservedWord.Of)} ")

	def DepartArchitecture(self, architecture: Architecture) -> None:
		"""
		Write the end of an architecture body.

		:param architecture: The architecture body.
		"""
		self._WriteEnd((ReservedWord.Architecture,), architecture.Identifier)

	def VisitConfiguration(self, configuration: Configuration) -> None:
		"""
		Write the reserved word ``configuration``, the identifier and the reserved word ``of`` of a configuration.

		**Format:** ``configuration counter_cfg of counter is`` ... ``end configuration counter_cfg;``

		:param configuration: The configuration declaration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Configuration)} {configuration.Identifier} ")
		self._Write(f"{self._Keyword(ReservedWord.Of)} ")

	def DepartConfiguration(self, configuration: Configuration) -> None:
		"""
		Write the end of a configuration declaration.

		:param configuration: The configuration declaration.
		"""
		self._WriteEnd((ReservedWord.Configuration,), configuration.Identifier)

	def VisitBlockConfiguration(self, configuration: BlockConfiguration) -> None:
		"""
		Write the reserved word ``for`` of a block configuration; its nested configurations are indented.

		**Format:** ``for rtl`` ... ``end for;``

		:param configuration: The block configuration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.For)} ")

	def DepartBlockSpecification(self, configuration: BlockConfiguration) -> None:
		"""
		End the line of a block specification; the nested configurations are indented.

		:param configuration: The block configuration.
		"""
		self._Write("\n")
		self._indentation += 1

	def DepartBlockConfiguration(self, configuration: BlockConfiguration) -> None:
		"""
		Write the end of a block configuration.

		:param configuration: The block configuration.
		"""
		self._indentation -= 1
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.End)} {self._Keyword(ReservedWord.For)};\n")

	def VisitComponentConfiguration(self, configuration: ComponentConfiguration) -> None:
		"""
		Write the reserved word ``for`` of a component configuration.

		**Format:** ``for all : counter use entity work.counter(rtl);`` ... ``end for;``

		:param configuration: The component configuration.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.For)} ")

	def DepartInstantiationList(self, configuration: ComponentConfiguration) -> None:
		"""
		Write the colon between the instantiation list and the component name of a component configuration.

		:param configuration: The component configuration.
		"""
		self._Write(" : ")

	def DepartComponentConfiguration(self, configuration: ComponentConfiguration) -> None:
		"""
		Write the end of a component configuration on its own line.

		:param configuration: The component configuration.
		"""
		self._Write("\n")
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.End)} {self._Keyword(ReservedWord.For)};\n")

	def VisitBindingIndication(self, indication: BindingIndication) -> None:
		"""
		Write the reserved word ``use`` of a binding indication on a new line, one indentation level deeper.

		**Format:** ``use entity work.counter(rtl)`` ... ``;``

		:param indication: The binding indication.
		"""
		self._indentation += 1
		if indication.EntityAspect is not None:
			self._Write("\n")
			self._WriteIndentation()
			self._Write(f"{self._Keyword(ReservedWord.Use)} ")

	def DepartBindingIndication(self, indication: BindingIndication) -> None:
		"""
		Write the semicolon ending a binding indication.

		:param indication: The binding indication.
		"""
		self._Write(";")
		self._indentation -= 1

	def VisitEntityAspectEntity(self, aspect: EntityAspectEntity) -> None:
		"""
		Write the reserved word ``entity`` of an entity aspect naming an entity.

		**Format:** ``entity work.counter(rtl)``

		:param aspect: The entity aspect.
		"""
		self._Write(f"{self._Keyword(ReservedWord.Entity)} ")

	def VisitEntityAspectConfiguration(self, aspect: EntityAspectConfiguration) -> None:
		"""
		Write the reserved word ``configuration`` of an entity aspect naming a configuration.

		**Format:** ``configuration work.counter_cfg``

		:param aspect: The entity aspect.
		"""
		self._Write(f"{self._Keyword(ReservedWord.Configuration)} ")

	def VisitEntityAspectOpen(self, aspect: EntityAspectOpen) -> None:
		"""
		Write the reserved word ``open`` of an open entity aspect.

		**Format:** ``open``

		:param aspect: The entity aspect.
		"""
		self._Write(self._Keyword(ReservedWord.Open))

	def VisitAllInstantiationList(self, instantiationList: AllInstantiationList) -> None:
		"""
		Write the reserved word ``all`` of an instantiation list.

		**Format:** ``all``

		:param instantiationList: The instantiation list.
		"""
		self._Write(self._Keyword(ReservedWord.All))

	def VisitOthersInstantiationList(self, instantiationList: OthersInstantiationList) -> None:
		"""
		Write the reserved word ``others`` of an instantiation list.

		**Format:** ``others``

		:param instantiationList: The instantiation list.
		"""
		self._Write(self._Keyword(ReservedWord.Others))

	def VisitSignalAssignment(self, element: SignalAssignmentMixin) -> None:
		"""
		Write the signal assignment delimiter (``<=``) between the target and the waveform of a signal assignment.

		In a force assignment, the reserved word ``force`` follows.

		:param element: The signal assignment.
		"""
		if isinstance(element, SignalForceAssignment):
			self._Write(f" <= {self._Keyword(ReservedWord.Force)} ")
		else:
			self._Write(" <= ")

		self._minimum = OperatorPrecedence.Range

	def VisitAfter(self, element: WaveformElement) -> None:
		"""
		Write the reserved word ``after`` before the delay of a waveform element.

		:param element: The waveform element.
		"""
		self._Write(f" {self._Keyword(ReservedWord.After)} ")
		self._minimum = OperatorPrecedence.Range

	def VisitSelect(
		self,
		element: ConcurrentSelectedSignalAssignment | SequentialSelectedVariableAssignment |
		         SequentialSelectedSignalAssignment
	) -> None:
		"""
		Write the reserved word ``select`` between the selector and the target of a selected assignment.

		:param element: The selected assignment.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Select)} ")

	def VisitBar(self, element: SelectedWaveform | GenerateCase | SelectedExpression | Case) -> None:
		"""
		Write the vertical line (``|``) between two choices.

		:param element: The element with the choices.
		"""
		self._Write(" | ")
		self._minimum = OperatorPrecedence.Range

	def VisitReport(self, element: ReportStatementMixin) -> None:
		"""
		Write the reserved word ``report`` before the message of an assertion or report.

		A report statement starts with the reserved word.

		:param element: The assertion or report.
		"""
		if isinstance(element, SequentialReportStatement):
			self._Write(f"{self._Keyword(ReservedWord.Report)} ")
		else:
			self._Write(f" {self._Keyword(ReservedWord.Report)} ")

		self._minimum = OperatorPrecedence.Range

	def VisitSeverity(self, element: ReportStatementMixin) -> None:
		"""
		Write the reserved word ``severity`` before the severity level of an assertion or report.

		:param element: The assertion or report.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Severity)} ")
		self._minimum = OperatorPrecedence.Range

	def VisitSensitivityList(self, process: ProcessStatement) -> None:
		"""
		Write the left parenthesis of the sensitivity list of a process.

		**Format:** ``process (clk, rst)`` or ``process (all)``

		:param process: The process.
		"""
		self._Write(" (")

	def DepartSensitivityList(self, process: ProcessStatement) -> None:
		"""
		Write the right parenthesis of the sensitivity list of a process.

		:param process: The process.
		"""
		self._Write(")")

	def VisitActualParameterPart(self, call: ProcedureCallMixin) -> None:
		"""
		Write the left parenthesis of the actual parameter part of a procedure call.

		The line breaks follow :attr:`VHDLStyle.ProcedureCall`.

		:param call: The procedure call.
		"""
		self._OpenList(self._style.ProcedureCall, ",")
		self._minimum = OperatorPrecedence.Range

	def DepartActualParameterPart(self, call: ProcedureCallMixin) -> None:
		"""
		Write the right parenthesis of the actual parameter part of a procedure call.

		:param call: The procedure call.
		"""
		self._CloseList()

	def DepartOthersSelectedWaveform(self, waveform: OthersSelectedWaveform) -> None:
		"""
		Write the choice ``others`` of the ``others`` selected waveform.

		**Format:** ``'0' when others``

		:param waveform: The selected waveform.
		"""
		self._Write(self._Keyword(ReservedWord.Others))

	def VisitIndexedChoice(self, choice: IndexedChoice) -> None:
		"""
		Enter a choice given by a value; the value is a simple expression.

		**Format:** ``'0'``

		:param choice: The choice.
		"""
		self._minimum = OperatorPrecedence.Adding

	def VisitProcessStatement(self, process: ProcessStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``process`` of a process statement.

		**Format:** ``count : process (clk) is`` ... ``begin`` ... ``end process count;``

		A process with ``all`` as sensitivity list has a single :class:`~pyVHDLModel.Name.AllName` without prefix in its
		sensitivity list.

		:param process: The process.
		"""
		self._WriteStatementStart(process)
		self._Write(self._Keyword(ReservedWord.Process))

	def _WriteStatementStart(self, statement: Statement) -> None:
		"""
		Write the indentation and the label, if any, of a statement.

		:param statement: The statement.
		"""
		self._WriteIndentation()
		if statement.Label is not None:
			self._Write(f"{statement.Label} : ")

	def DepartProcessStatement(self, process: ProcessStatement) -> None:
		"""
		Write the end of a process statement.

		:param process: The process.
		"""
		self._WriteEnd((ReservedWord.Process,), process.Label)

	def VisitConcurrentProcedureCall(self, call: ConcurrentProcedureCall) -> None:
		"""
		Write the label, if any, of a concurrent procedure call.

		**Format:** ``check(clk, rst);``

		:param call: The procedure call.
		"""
		self._WriteStatementStart(call)

	def DepartConcurrentProcedureCall(self, call: ConcurrentProcedureCall) -> None:
		"""
		Write the semicolon ending a concurrent procedure call.

		:param call: The procedure call.
		"""
		self._Write(";\n")

	def VisitConcurrentSimpleSignalAssignment(self, assignment: ConcurrentSimpleSignalAssignment) -> None:
		"""
		Write the label, if any, of a concurrent simple signal assignment.

		**Format:** ``q <= d after 1 ns;``

		:param assignment: The signal assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartConcurrentSimpleSignalAssignment(self, assignment: ConcurrentSimpleSignalAssignment) -> None:
		"""
		Write the semicolon ending a concurrent simple signal assignment.

		:param assignment: The signal assignment.
		"""
		self._Write(";\n")

	def VisitConcurrentSelectedSignalAssignment(self, assignment: ConcurrentSelectedSignalAssignment) -> None:
		"""
		Write the label, if any, and the reserved word ``with`` of a concurrent selected signal assignment.

		**Format:** ``with sel select q <= a when '0', b when others;``

		:param assignment: The signal assignment.
		"""
		self._WriteStatementStart(assignment)
		self._Write(f"{self._Keyword(ReservedWord.With)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartConcurrentSelectedSignalAssignment(self, assignment: ConcurrentSelectedSignalAssignment) -> None:
		"""
		Write the semicolon ending a concurrent selected signal assignment.

		:param assignment: The signal assignment.
		"""
		self._Write(";\n")

	def VisitConcurrentConditionalSignalAssignment(self, assignment: ConcurrentConditionalSignalAssignment) -> None:
		"""
		Write the label, if any, of a concurrent conditional signal assignment.

		**Format:** ``q <= a when sel = '0' else b;``

		:param assignment: The signal assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartConcurrentConditionalSignalAssignment(self, assignment: ConcurrentConditionalSignalAssignment) -> None:
		"""
		Write the semicolon ending a concurrent conditional signal assignment.

		:param assignment: The signal assignment.
		"""
		self._Write(";\n")

	def VisitConcurrentAssertStatement(self, assertion: ConcurrentAssertStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``assert`` of a concurrent assertion.

		**Format:** ``assert BITS > 0 report "no bits" severity failure;``

		:param assertion: The assertion.
		"""
		self._WriteStatementStart(assertion)
		self._Write(f"{self._Keyword(ReservedWord.Assert)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartConcurrentAssertStatement(self, assertion: ConcurrentAssertStatement) -> None:
		"""
		Write the semicolon ending a concurrent assertion.

		:param assertion: The assertion.
		"""
		self._Write(";\n")

	def VisitRightParenthesis(self, element: TypeConversion | EntityAspectEntity | EntityInstantiation) -> None:
		"""
		Write the right parenthesis enclosing the operand of a type conversion or an architecture name.

		:param element: The element enclosing the item.
		"""
		self._Write(")")

	def VisitGenerate(self, element: GenerateBranch | CaseGenerateStatement | ForGenerateStatement) -> None:
		"""
		Write the reserved word ``generate``; the body of the generate statement or branch is indented.

		:param element: The generate statement or branch.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Generate)}\n")
		self._indentation += 1

	def VisitComponentInstantiation(self, instantiation: ComponentInstantiation) -> None:
		"""
		Write the label and the reserved word ``component`` of a component instantiation.

		**Format:** ``u1 : component counter`` ... ``;``

		:param instantiation:    The component instantiation.
		:raises VHDLWriterError: If the component instantiation has no label.
		"""
		if instantiation.Label is None:
			raise VHDLWriterError("Component instantiation has no label.", instantiation)

		self._WriteStatementStart(instantiation)
		self._Write(f"{self._Keyword(ReservedWord.Component)} ")

	def DepartComponentInstantiation(self, instantiation: ComponentInstantiation) -> None:
		"""
		Write the semicolon ending a component instantiation.

		:param instantiation: The component instantiation.
		"""
		self._Write(";\n")

	def VisitEntityInstantiation(self, instantiation: EntityInstantiation) -> None:
		"""
		Write the label and the reserved word ``entity`` of an entity instantiation.

		**Format:** ``u1 : entity work.counter(rtl)`` ... ``;``

		:param instantiation:    The entity instantiation.
		:raises VHDLWriterError: If the entity instantiation has no label.
		"""
		if instantiation.Label is None:
			raise VHDLWriterError("Entity instantiation has no label.", instantiation)

		self._WriteStatementStart(instantiation)
		self._Write(f"{self._Keyword(ReservedWord.Entity)} ")

	def DepartEntityInstantiation(self, instantiation: EntityInstantiation) -> None:
		"""
		Write the semicolon ending an entity instantiation.

		:param instantiation: The entity instantiation.
		"""
		self._Write(";\n")

	def VisitConfigurationInstantiation(self, instantiation: ConfigurationInstantiation) -> None:
		"""
		Write the label and the reserved word ``configuration`` of a configuration instantiation.

		**Format:** ``u1 : configuration work.counter_cfg`` ... ``;``

		:param instantiation:    The configuration instantiation.
		:raises VHDLWriterError: If the configuration instantiation has no label.
		"""
		if instantiation.Label is None:
			raise VHDLWriterError("Configuration instantiation has no label.", instantiation)

		self._WriteStatementStart(instantiation)
		self._Write(f"{self._Keyword(ReservedWord.Configuration)} ")

	def DepartConfigurationInstantiation(self, instantiation: ConfigurationInstantiation) -> None:
		"""
		Write the semicolon ending a configuration instantiation.

		:param instantiation: The configuration instantiation.
		"""
		self._Write(";\n")

	def VisitConcurrentBlockStatement(self, block: ConcurrentBlockStatement) -> None:
		"""
		Write the label and the reserved word ``block`` of a block statement; its header and declarations are indented.

		**Format:** ``inner : block`` ... ``begin`` ... ``end block inner;``

		:param block:            The block statement.
		:raises VHDLWriterError: If the block statement has no label.
		"""
		if block.Label is None:
			raise VHDLWriterError("Block statement has no label.", block)

		self._WriteStatementStart(block)
		self._Write(f"{self._Keyword(ReservedWord.Block)}\n")
		self._indentation += 1

	def DepartConcurrentBlockStatement(self, block: ConcurrentBlockStatement) -> None:
		"""
		Write the end of a block statement.

		:param block: The block statement.
		"""
		self._WriteEnd((ReservedWord.Block,), block.Label)

	def VisitIfGenerateStatement(self, statement: IfGenerateStatement) -> None:
		"""
		Write the label of an if-generate statement; its branches follow.

		**Format:** ``gen : if BITS > 8 generate`` ... ``elsif`` ... ``else generate`` ... ``end generate gen;``

		:param statement:        The if-generate statement.
		:raises VHDLWriterError: If the if-generate statement has no label.
		"""
		if statement.Label is None:
			raise VHDLWriterError("If-generate statement has no label.", statement)

		self._WriteStatementStart(statement)

	def DepartIfGenerateStatement(self, statement: IfGenerateStatement) -> None:
		"""
		Write the end of an if-generate statement.

		:param statement: The if-generate statement.
		"""
		self._WriteEndLine((ReservedWord.Generate,), statement.Label)

	def VisitIfGenerateBranch(self, branch: IfGenerateBranch) -> None:
		"""
		Write the reserved word ``if`` and the alternative label, if any, of the if branch of an if-generate statement.

		:param branch: The generate branch.
		"""
		self._Write(f"{self._Keyword(ReservedWord.If)} ")
		self._WriteAlternativeLabel(branch)

	def _WriteAlternativeLabel(self, branch: GenerateBranch) -> None:
		"""
		Write the alternative label, if any, of a generate branch, followed by a colon.

		:param branch: The generate branch.
		"""
		if branch.AlternativeLabel is not None:
			self._Write(f"{branch.AlternativeLabel} : ")

		self._minimum = OperatorPrecedence.Range

	def DepartIfGenerateBranch(self, branch: IfGenerateBranch) -> None:
		"""
		Leave the body of the if branch of an if-generate statement.

		:param branch: The generate branch.
		"""
		self._indentation -= 1

	def VisitElsifGenerateBranch(self, branch: ElsifGenerateBranch) -> None:
		"""
		Write the reserved word ``elsif`` and the alternative label, if any, of an elsif branch of an if-generate statement.

		:param branch: The generate branch.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.ElsIf)} ")
		self._WriteAlternativeLabel(branch)

	def DepartElsifGenerateBranch(self, branch: ElsifGenerateBranch) -> None:
		"""
		Leave the body of an elsif branch of an if-generate statement.

		:param branch: The generate branch.
		"""
		self._indentation -= 1

	def VisitElseGenerateBranch(self, branch: ElseGenerateBranch) -> None:
		"""
		Write the reserved word ``else`` and the alternative label, if any, of the else branch of an if-generate statement.

		:param branch: The generate branch.
		"""
		self._WriteIndentation()
		self._Write(self._Keyword(ReservedWord.Else))
		if branch.AlternativeLabel is not None:
			self._Write(f" {branch.AlternativeLabel} :")

	def DepartElseGenerateBranch(self, branch: ElseGenerateBranch) -> None:
		"""
		Leave the body of the else branch of an if-generate statement.

		:param branch: The generate branch.
		"""
		self._indentation -= 1

	def VisitCaseGenerateStatement(self, statement: CaseGenerateStatement) -> None:
		"""
		Write the label and the reserved word ``case`` of a case-generate statement; its alternatives are indented.

		**Format:** ``gen : case MODE generate`` ... ``when 0 =>`` ... ``end generate gen;``

		:param statement:        The case-generate statement.
		:raises VHDLWriterError: If the case-generate statement has no label.
		"""
		if statement.Label is None:
			raise VHDLWriterError("Case-generate statement has no label.", statement)

		self._WriteStatementStart(statement)
		self._Write(f"{self._Keyword(ReservedWord.Case)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartCaseGenerateStatement(self, statement: CaseGenerateStatement) -> None:
		"""
		Write the end of a case-generate statement.

		:param statement: The case-generate statement.
		"""
		self._WriteEnd((ReservedWord.Generate,), statement.Label)

	def VisitGenerateCase(self, case: GenerateCase) -> None:
		"""
		Write the reserved word ``when`` and the alternative label, if any, of an alternative of a case-generate statement.

		**Format:** ``when 1 | 2 =>``

		:param case: The case-generate alternative.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.When)} ")
		if case.Label is not None:
			self._Write(f"{case.Label} : ")

	def DepartGenerateCase(self, case: GenerateCase) -> None:
		"""
		Leave the body of an alternative of a case-generate statement.

		:param case: The case-generate alternative.
		"""
		self._indentation -= 1

	def VisitOthersGenerateCase(self, case: OthersGenerateCase) -> None:
		"""
		Write the reserved words ``when`` and ``others`` of the ``others`` alternative of a case-generate statement.

		**Format:** ``when others =>``

		:param case: The case-generate alternative.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.When)} ")
		if case.Label is not None:
			self._Write(f"{case.Label} : ")

		self._Write(self._Keyword(ReservedWord.Others))

	def DepartOthersGenerateCase(self, case: OthersGenerateCase) -> None:
		"""
		Leave the body of the ``others`` alternative of a case-generate statement.

		:param case: The case-generate alternative.
		"""
		self._indentation -= 1

	def VisitIndexedGenerateChoice(self, choice: IndexedGenerateChoice) -> None:
		"""
		Enter a case-generate choice given by a value; the value is a simple expression.

		**Format:** ``8``

		:param choice: The choice.
		"""
		self._minimum = OperatorPrecedence.Adding

	def VisitForGenerateStatement(self, statement: ForGenerateStatement) -> None:
		"""
		Write the label, the reserved word ``for``, the loop index and ``in`` of a for-generate statement.

		**Format:** ``gen : for i in 0 to 3 generate`` ... ``end generate gen;``

		:param statement:        The for-generate statement.
		:raises VHDLWriterError: If the for-generate statement has no label.
		"""
		if statement.Label is None:
			raise VHDLWriterError("For-generate statement has no label.", statement)

		self._WriteStatementStart(statement)
		self._Write(f"{self._Keyword(ReservedWord.For)} {statement.LoopIndex} {self._Keyword(ReservedWord.In)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartForGenerateStatement(self, statement: ForGenerateStatement) -> None:
		"""
		Write the end of a for-generate statement.

		:param statement: The for-generate statement.
		"""
		self._WriteEnd((ReservedWord.Generate,), statement.Label)

	def VisitOn(self, statement: WaitStatement) -> None:
		"""
		Write the reserved word ``on`` before the sensitivity list of a wait statement.

		:param statement: The wait statement.
		"""
		self._Write(f" {self._Keyword(ReservedWord.On)} ")

	def VisitUntil(self, statement: WaitStatement) -> None:
		"""
		Write the reserved word ``until`` before the condition of a wait statement.

		:param statement: The wait statement.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Until)} ")
		self._minimum = OperatorPrecedence.Range

	def VisitFor(self, statement: WaitStatement) -> None:
		"""
		Write the reserved word ``for`` before the timeout of a wait statement.

		:param statement: The wait statement.
		"""
		self._Write(f" {self._Keyword(ReservedWord.For)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartOthersSelectedExpression(self, expression: OthersSelectedExpression) -> None:
		"""
		Write the choice ``others`` of the ``others`` selected expression.

		**Format:** ``'0' when others``

		:param expression: The selected expression.
		"""
		self._Write(self._Keyword(ReservedWord.Others))

	def VisitSequentialProcedureCall(self, call: SequentialProcedureCall) -> None:
		"""
		Write the label, if any, of a procedure call.

		**Format:** ``check(value, limit => 4);``

		:param call: The procedure call.
		"""
		self._WriteStatementStart(call)

	def DepartSequentialProcedureCall(self, call: SequentialProcedureCall) -> None:
		"""
		Write the semicolon ending a procedure call.

		:param call: The procedure call.
		"""
		self._Write(";\n")

	def VisitSequentialSimpleSignalAssignment(self, assignment: SequentialSimpleSignalAssignment) -> None:
		"""
		Write the label, if any, of a signal assignment.

		**Format:** ``q <= d after 1 ns;``

		:param assignment: The signal assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartSequentialSimpleSignalAssignment(self, assignment: SequentialSimpleSignalAssignment) -> None:
		"""
		Write the semicolon ending a signal assignment.

		:param assignment: The signal assignment.
		"""
		self._Write(";\n")

	def VisitSequentialVariableAssignment(self, assignment: SequentialVariableAssignment) -> None:
		"""
		Write the label, if any, of a variable assignment.

		**Format:** ``count := count + 1;``

		:param assignment: The variable assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartSequentialVariableAssignment(self, assignment: SequentialVariableAssignment) -> None:
		"""
		Write the semicolon ending a variable assignment.

		:param assignment: The variable assignment.
		"""
		self._Write(";\n")

	def VisitSequentialConditionalVariableAssignment(self, assignment: SequentialConditionalVariableAssignment) -> None:
		"""
		Write the label, if any, of a conditional variable assignment.

		**Format:** ``v := a when sel = '0' else b;``

		:param assignment: The conditional variable assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartSequentialConditionalVariableAssignment(self, assignment: SequentialConditionalVariableAssignment) -> None:
		"""
		Write the semicolon ending a conditional variable assignment.

		:param assignment: The conditional variable assignment.
		"""
		self._Write(";\n")

	def VisitSequentialConditionalSignalAssignment(self, assignment: SequentialConditionalSignalAssignment) -> None:
		"""
		Write the label, if any, of a conditional signal assignment.

		**Format:** ``q <= a when sel = '0' else b;``

		:param assignment: The conditional signal assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartSequentialConditionalSignalAssignment(self, assignment: SequentialConditionalSignalAssignment) -> None:
		"""
		Write the semicolon ending a conditional signal assignment.

		:param assignment: The conditional signal assignment.
		"""
		self._Write(";\n")

	def VisitSequentialSelectedVariableAssignment(self, assignment: SequentialSelectedVariableAssignment) -> None:
		"""
		Write the label, if any, and the reserved word ``with`` of a selected variable assignment.

		**Format:** ``with sel select v := a when '0', b when others;``

		:param assignment: The selected variable assignment.
		"""
		self._WriteStatementStart(assignment)
		self._Write(f"{self._Keyword(ReservedWord.With)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartSequentialSelectedVariableAssignment(self, assignment: SequentialSelectedVariableAssignment) -> None:
		"""
		Write the semicolon ending a selected variable assignment.

		:param assignment: The selected variable assignment.
		"""
		self._Write(";\n")

	def VisitSequentialSelectedSignalAssignment(self, assignment: SequentialSelectedSignalAssignment) -> None:
		"""
		Write the label, if any, and the reserved word ``with`` of a selected signal assignment.

		**Format:** ``with sel select q <= a when '0', b when others;``

		:param assignment: The selected signal assignment.
		"""
		self._WriteStatementStart(assignment)
		self._Write(f"{self._Keyword(ReservedWord.With)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartSequentialSelectedSignalAssignment(self, assignment: SequentialSelectedSignalAssignment) -> None:
		"""
		Write the semicolon ending a selected signal assignment.

		:param assignment: The selected signal assignment.
		"""
		self._Write(";\n")

	def VisitSignalForceAssignment(self, assignment: SignalForceAssignment) -> None:
		"""
		Write the label, if any, of a force assignment.

		**Format:** ``q <= force '1';``

		:param assignment: The force assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartSignalForceAssignment(self, assignment: SignalForceAssignment) -> None:
		"""
		Write the semicolon ending a force assignment.

		:param assignment: The force assignment.
		"""
		self._Write(";\n")

	def VisitSignalReleaseAssignment(self, assignment: SignalReleaseAssignment) -> None:
		"""
		Write the label, if any, of a release assignment.

		**Format:** ``q <= release;``

		:param assignment: The release assignment.
		"""
		self._WriteStatementStart(assignment)

	def DepartSignalReleaseAssignment(self, assignment: SignalReleaseAssignment) -> None:
		"""
		Write the reserved word ``release`` and the semicolon ending a release assignment.

		:param assignment: The release assignment.
		"""
		self._Write(f"{self._Keyword(ReservedWord.Release)};\n")

	def VisitSequentialReportStatement(self, statement: SequentialReportStatement) -> None:
		"""
		Write the label, if any, of a report statement.

		**Format:** ``report "done" severity note;``

		:param statement: The report statement.
		"""
		self._WriteStatementStart(statement)

	def DepartSequentialReportStatement(self, statement: SequentialReportStatement) -> None:
		"""
		Write the semicolon ending a report statement.

		:param statement: The report statement.
		"""
		self._Write(";\n")

	def VisitSequentialAssertStatement(self, assertion: SequentialAssertStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``assert`` of an assertion.

		**Format:** ``assert count < 8 report "overflow" severity error;``

		:param assertion: The assertion.
		"""
		self._WriteStatementStart(assertion)
		self._Write(f"{self._Keyword(ReservedWord.Assert)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartSequentialAssertStatement(self, assertion: SequentialAssertStatement) -> None:
		"""
		Write the semicolon ending an assertion.

		:param assertion: The assertion.
		"""
		self._Write(";\n")

	def VisitNullStatement(self, statement: NullStatement) -> None:
		"""
		Write a null statement.

		**Format:** ``null;``

		:param statement: The null statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(f"{self._Keyword(ReservedWord.Null)};\n")

	def VisitReturnStatement(self, statement: ReturnStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``return`` of a return statement.

		**Format:** ``return count;``

		:param statement: The return statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(self._Keyword(ReservedWord.Return))
		if statement.ReturnValue is not None:
			self._Write(" ")
			self._minimum = OperatorPrecedence.Range

	def DepartReturnStatement(self, statement: ReturnStatement) -> None:
		"""
		Write the semicolon ending a return statement.

		:param statement: The return statement.
		"""
		self._Write(";\n")

	def VisitWaitStatement(self, statement: WaitStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``wait`` of a wait statement.

		**Format:** ``wait on clk until clk = '1' for 10 ns;``

		:param statement: The wait statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(self._Keyword(ReservedWord.Wait))

	def DepartWaitStatement(self, statement: WaitStatement) -> None:
		"""
		Write the semicolon ending a wait statement.

		:param statement: The wait statement.
		"""
		self._Write(";\n")

	def VisitThen(self, branch: IfBranch | ElsifBranch) -> None:
		"""
		Write the reserved word ``then`` of an if or elsif branch; its statements are indented.

		:param branch: The branch.
		"""
		self._Write(f" {self._Keyword(ReservedWord.Then)}\n")
		self._indentation += 1

	def VisitLoop(self, statement: LoopStatement) -> None:
		"""
		Write the reserved word ``loop`` of a loop statement; its statements are indented.

		:param statement: The loop statement.
		"""
		if isinstance(statement, EndlessLoopStatement):
			self._Write(f"{self._Keyword(ReservedWord.Loop)}\n")
		else:
			self._Write(f" {self._Keyword(ReservedWord.Loop)}\n")

		self._indentation += 1

	def VisitIfStatement(self, statement: IfStatement) -> None:
		"""
		Write the label, if any, of an if statement; its branches follow.

		**Format:** ``if count = 0 then`` ... ``elsif`` ... ``else`` ... ``end if;``

		:param statement: The if statement.
		"""
		self._WriteStatementStart(statement)

	def DepartIfStatement(self, statement: IfStatement) -> None:
		"""
		Write the end of an if statement.

		:param statement: The if statement.
		"""
		self._WriteEndLine((ReservedWord.If,), statement.Label)

	def VisitIfBranch(self, branch: IfBranch) -> None:
		"""
		Write the reserved word ``if`` of the if branch of an if statement.

		:param branch: The branch.
		"""
		self._Write(f"{self._Keyword(ReservedWord.If)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartIfBranch(self, branch: IfBranch) -> None:
		"""
		Leave the statements of the if branch of an if statement.

		:param branch: The branch.
		"""
		self._indentation -= 1

	def VisitElsifBranch(self, branch: ElsifBranch) -> None:
		"""
		Write the reserved word ``elsif`` of an elsif branch of an if statement.

		:param branch: The branch.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.ElsIf)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartElsifBranch(self, branch: ElsifBranch) -> None:
		"""
		Leave the statements of an elsif branch of an if statement.

		:param branch: The branch.
		"""
		self._indentation -= 1

	def VisitElseBranch(self, branch: ElseBranch) -> None:
		"""
		Write the reserved word ``else`` of the else branch of an if statement; its statements are indented.

		:param branch: The branch.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.Else)}\n")
		self._indentation += 1

	def DepartElseBranch(self, branch: ElseBranch) -> None:
		"""
		Leave the statements of the else branch of an if statement.

		:param branch: The branch.
		"""
		self._indentation -= 1

	def VisitCaseStatement(self, statement: CaseStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``case`` of a case statement; its alternatives are indented.

		**Format:** ``case state is`` ... ``when Idle =>`` ... ``end case;``

		:param statement: The case statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(f"{self._Keyword(ReservedWord.Case)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartCaseStatement(self, statement: CaseStatement) -> None:
		"""
		Write the end of a case statement.

		:param statement: The case statement.
		"""
		self._WriteEnd((ReservedWord.Case,), statement.Label)

	def VisitCase(self, case: Case) -> None:
		"""
		Write the reserved word ``when`` of an alternative of a case statement.

		**Format:** ``when 1 | 2 =>``

		:param case: The case alternative.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.When)} ")

	def DepartCase(self, case: Case) -> None:
		"""
		Leave the statements of an alternative of a case statement.

		:param case: The case alternative.
		"""
		self._indentation -= 1

	def VisitOthersCase(self, case: OthersCase) -> None:
		"""
		Write the reserved words ``when`` and ``others`` of the ``others`` alternative of a case statement.

		**Format:** ``when others =>``

		:param case: The case alternative.
		"""
		self._WriteIndentation()
		self._Write(f"{self._Keyword(ReservedWord.When)} {self._Keyword(ReservedWord.Others)}")

	def DepartOthersCase(self, case: OthersCase) -> None:
		"""
		Leave the statements of the ``others`` alternative of a case statement.

		:param case: The case alternative.
		"""
		self._indentation -= 1

	def VisitEndlessLoopStatement(self, statement: EndlessLoopStatement) -> None:
		"""
		Write the label, if any, of a loop statement without iteration scheme.

		**Format:** ``loop`` ... ``end loop;``

		:param statement: The loop statement.
		"""
		self._WriteStatementStart(statement)

	def DepartEndlessLoopStatement(self, statement: EndlessLoopStatement) -> None:
		"""
		Write the end of a loop statement without iteration scheme.

		:param statement: The loop statement.
		"""
		self._WriteEnd((ReservedWord.Loop,), statement.Label)

	def VisitForLoopStatement(self, statement: ForLoopStatement) -> None:
		"""
		Write the label, if any, the reserved word ``for``, the loop index and ``in`` of a for-loop statement.

		**Format:** ``for i in 0 to 7 loop`` ... ``end loop;``

		:param statement: The loop statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(f"{self._Keyword(ReservedWord.For)} {statement.LoopIndex} {self._Keyword(ReservedWord.In)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartForLoopStatement(self, statement: ForLoopStatement) -> None:
		"""
		Write the end of a for-loop statement.

		:param statement: The loop statement.
		"""
		self._WriteEnd((ReservedWord.Loop,), statement.Label)

	def VisitWhileLoopStatement(self, statement: WhileLoopStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``while`` of a while-loop statement.

		**Format:** ``while count < 8 loop`` ... ``end loop;``

		:param statement: The loop statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(f"{self._Keyword(ReservedWord.While)} ")
		self._minimum = OperatorPrecedence.Range

	def DepartWhileLoopStatement(self, statement: WhileLoopStatement) -> None:
		"""
		Write the end of a while-loop statement.

		:param statement: The loop statement.
		"""
		self._WriteEnd((ReservedWord.Loop,), statement.Label)

	def VisitNextStatement(self, statement: NextStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``next`` of a next statement.

		**Format:** ``next when skip;``

		The model keeps no loop label, so none is written.

		:param statement: The next statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(self._Keyword(ReservedWord.Next))

	def DepartNextStatement(self, statement: NextStatement) -> None:
		"""
		Write the semicolon ending a next statement.

		:param statement: The next statement.
		"""
		self._Write(";\n")

	def VisitExitStatement(self, statement: ExitStatement) -> None:
		"""
		Write the label, if any, and the reserved word ``exit`` of an exit statement.

		**Format:** ``exit when done;``

		The model keeps no loop label, so none is written.

		:param statement: The exit statement.
		"""
		self._WriteStatementStart(statement)
		self._Write(self._Keyword(ReservedWord.Exit))

	def DepartExitStatement(self, statement: ExitStatement) -> None:
		"""
		Write the semicolon ending an exit statement.

		:param statement: The exit statement.
		"""
		self._Write(";\n")
