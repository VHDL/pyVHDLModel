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
"""
This module contains parts of an abstract document language model for VHDL.

Common definitions and Mixins are used by many classes in the model as base-classes.
"""
from typing                  import Iterable, Union, Optional as Nullable

from pyTooling.Common        import getFullyQualifiedName, getTypeName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType, abstractclass

from pyVHDLModel.Base        import ModelEntity, LabeledEntityMixin, BaseCase, BaseChoice, WaveformElement, \
                                    ConditionalMixin, ChoicesMixin
from pyVHDLModel.Exception   import AlreadyInDesignError, NotAChildError, AssociationOrderError, \
                                    DuplicateParameterAssociationError
from pyVHDLModel.Expression  import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Name        import SimpleName
from pyVHDLModel.Symbol      import Symbol, SignalSymbol, VariableSymbol
from pyVHDLModel.Association import ParameterAssociationItem


ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
class AllowBlackboxMixin(metaclass=ExtendedType, mixin=True, expects=("_parent",)):
	"""
	A mixin-class for language entities that may permit blackboxes.

	The setting is inherited from the parent when not set locally (:data:`AllowBlackbox`). The host class provides the
	reference to the parent ``_parent``.

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>`
	   * :class:`Generate statement <pyVHDLModel.Concurrent.GenerateStatement>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	   * :class:`Component <pyVHDLModel.DesignUnit.Component>`
	   * :class:`Design <pyVHDLModel.Design>`
	   * :class:`Library <pyVHDLModel.Library>`
	"""
	_allowBlackbox: Nullable[bool]  #: Allow blackboxes for components; ``None`` inherits the parent's setting.

	def __init__(self, allowBlackbox: Nullable[bool] = None) -> None:
		"""
		Initializes a hierarchical model entity allow for blackboxes.

		:param allowBlackbox: Allow blackboxes for components in language entity.
		"""
		self._allowBlackbox = allowBlackbox

	@property
	def AllowBlackbox(self) -> bool:
		"""
		Property to return whether a design supports blackboxes, inherited from the parent if not set locally
		(:attr:`_allowBlackbox`).

		.. rubric:: Algorithm

		1. If allow blackbox property is locally set, return the local value,
		2. Otherwise, return allow blackbox value from parent object.

		:returns:                   ``True``, if blackboxes are allowed.
		:raises VHDLModelException: If neither a local value is set nor a parent object is available to inherit the
		                            value from.
		"""
		if self._allowBlackbox is not None:
			return self._allowBlackbox
		elif self._parent is None:
			from pyVHDLModel.Exception import VHDLModelException

			raise VHDLModelException(f"AllowBlackbox is not set on {self!r} and no parent is available to inherit it from.")
		else:
			return self._parent.AllowBlackbox

	@AllowBlackbox.setter
	def AllowBlackbox(self, value: Nullable[bool]) -> None:
		self._allowBlackbox = value


@export
@abstractclass
class Statement(ModelEntity, LabeledEntityMixin):
	"""
	A ``Statement`` is a base-class for all statements.

	.. seealso::

	   * :class:`Concurrent statement <pyVHDLModel.Concurrent.ConcurrentStatement>`
	   * :class:`Sequential statement <pyVHDLModel.Sequential.SequentialStatement>`
	"""
	def __init__(self, label: Nullable[str] = None, parent=None) -> None:
		"""
		Initializes a statement.

		:param label:  The label of a model entity.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(parent)
		LabeledEntityMixin.__init__(self, label)


@export
class ProcedureCallMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for statements calling a procedure.

	The called procedure is available as :data:`Procedure`, its actual parameters as
	:data:`ParameterAssociationItems`.

	An association declares nothing: the mutators update neither a namespace nor a lookup table of the host class, so the
	mixin expects nothing from its host.

	.. seealso::

	   * :class:`Concurrent procedure call <pyVHDLModel.Concurrent.ConcurrentProcedureCall>`
	   * :class:`Sequential procedure call <pyVHDLModel.Sequential.SequentialProcedureCall>`
	"""
	# TODO: implement a ProcedureSymbol
	_procedure:                 Symbol  #: Reference to the called procedure.
	_parameterAssociationItems: list[ParameterAssociationItem]  #: List of all parameter associations of the call.

	def __init__(self, procedureName: Symbol, parameterAssociationItems: Nullable[Iterable[ParameterAssociationItem]] = None) -> None:
		"""
		Initializes a procedure call.

		:param procedureName:             Reference to the called procedure.
		:param parameterAssociationItems: List of all parameter associations of the call.
		"""
		self._procedure = procedureName
		procedureName.Parent = self

		# TODO: extract to mixin
		self._parameterAssociationItems = []
		if parameterAssociationItems is not None:
			for parameterMapping in parameterAssociationItems:
				self._parameterAssociationItems.append(parameterMapping)
				parameterMapping.Parent = self

	@readonly
	def Procedure(self) -> Symbol:
		"""
		Read-only property to access the procedure (:attr:`_procedure`).

		:returns: The procedure.
		"""
		return self._procedure

	@readonly
	def ParameterAssociationItems(self) -> list[ParameterAssociationItem]:
		"""
		Read-only property to access the parameter association items (:attr:`_parameterAssociationItems`).

		:returns: List of parameter association items.
		"""
		return self._parameterAssociationItems

	def AddParameterAssociationItem(self, parameterAssociationItem: ParameterAssociationItem) -> None:
		"""
		Add a parameter association at the end of the parameter association list.

		The association's parent is set to this procedure call.

		:param parameterAssociationItem:            The parameter association to add.
		:raises ValueError:                         If parameter 'parameterAssociationItem' is ``None``.
		:raises TypeError:                          If parameter 'parameterAssociationItem' is not of type
		                                            :class:`~pyVHDLModel.Association.ParameterAssociationItem`.
		:raises AlreadyInDesignError:               If parameter 'parameterAssociationItem' already has a parent.
		:raises DuplicateParameterAssociationError: If the association is named, and another named association of the
		                                            parameter association list has the same formal.
		:raises AssociationOrderError:              If the association is positional, and the parameter association list has
		                                            a named association.

		.. seealso::

		   :meth:`InsertParameterAssociationItem`
		      |rarr| Insert a parameter association at a position of the parameter association list.
		   :meth:`RemoveParameterAssociationItem`
		      |rarr| Remove a parameter association from the parameter association list.
		"""
		self.InsertParameterAssociationItem(len(self._parameterAssociationItems), parameterAssociationItem)

	def InsertParameterAssociationItem(self, index: int, parameterAssociationItem: ParameterAssociationItem) -> None:
		"""
		Insert a parameter association at a position of the parameter association list.

		The association's parent is set to this procedure call.

		A named association (``formal => actual``) can't repeat the formal of another named association of the parameter
		association list. Only formals given as a simple name are compared: a partial association (``a(0) => x``) or a
		conversion function (``to_integer(a) => x``) is accepted. All positional associations precede the named
		associations.

		:param index:                               Position, from ``0`` (first) to the number of parameter associations
		                                            (append). A negative index counts from the end, as for
		                                            :meth:`list.insert`: ``-1`` inserts before the last parameter
		                                            association.
		:param parameterAssociationItem:            The parameter association to insert.
		:raises ValueError:                         If parameter 'index' is ``None``.
		:raises TypeError:                          If parameter 'index' is not of type :class:`int`.
		:raises ValueError:                         If parameter 'index' is out of range.
		:raises ValueError:                         If parameter 'parameterAssociationItem' is ``None``.
		:raises TypeError:                          If parameter 'parameterAssociationItem' is not of type
		                                            :class:`~pyVHDLModel.Association.ParameterAssociationItem`.
		:raises AlreadyInDesignError:               If parameter 'parameterAssociationItem' already has a parent.
		:raises DuplicateParameterAssociationError: If the association is named, and another named association of the
		                                            parameter association list has the same formal.
		:raises AssociationOrderError:              If the association is positional, and a named association precedes the
		                                            position.
		:raises AssociationOrderError:              If the association is named, and a positional association follows the
		                                            position.

		.. seealso::

		   :meth:`AddParameterAssociationItem`
		      |rarr| Add a parameter association at the end of the parameter association list.
		   :meth:`RemoveParameterAssociationItem`
		      |rarr| Remove a parameter association from the parameter association list.
		"""
		count = len(self._parameterAssociationItems)
		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-count <= index <= count):
			ex = ValueError(f"Parameter 'index' is out of range {-count}..{count}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if parameterAssociationItem is None:
			raise ValueError("Parameter 'parameterAssociationItem' is None.")
		elif not isinstance(parameterAssociationItem, ParameterAssociationItem):
			ex = TypeError("Parameter 'parameterAssociationItem' is not of type 'ParameterAssociationItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterAssociationItem)}'.")
			raise ex
		elif parameterAssociationItem._parent is not None:
			ex = AlreadyInDesignError(
				f"{getTypeName(parameterAssociationItem)} already has a parent.",
				element=parameterAssociationItem,
				parent=parameterAssociationItem._parent
			)
			ex.add_note(f"Remove it from its {getTypeName(parameterAssociationItem._parent)} first.")
			raise ex

		formal = parameterAssociationItem._formal
		if isinstance(formal, SimpleName):
			normalizedFormal = formal._normalizedIdentifier
			for existing in self._parameterAssociationItems:
				if isinstance(existing._formal, SimpleName) and existing._formal._normalizedIdentifier == normalizedFormal:
					ex = DuplicateParameterAssociationError(
						f"{getTypeName(self)} already associates parameter '{formal._identifier}'.",
						identifier=formal._identifier,
						parent=self,
						element=parameterAssociationItem,
						existing=existing
					)
					ex.add_note(f"Existing association is '{existing!s}'.")
					raise ex

		position = index if index >= 0 else count + index
		if formal is None:
			for existing in self._parameterAssociationItems[:position]:
				if existing._formal is not None:
					ex = AssociationOrderError(
						f"Positional parameter association can't follow named association '{existing!s}'.",
						parent=self,
						element=parameterAssociationItem,
						existing=existing
					)
					ex.add_note("Insert it before the first named association, or name its formal.")
					raise ex
		else:
			for existing in self._parameterAssociationItems[position:]:
				if existing._formal is None:
					ex = AssociationOrderError(
						f"Named parameter association can't precede positional association '{existing!s}'.",
						parent=self,
						element=parameterAssociationItem,
						existing=existing
					)
					ex.add_note("Insert it after the last positional association.")
					raise ex

		self._parameterAssociationItems.insert(index, parameterAssociationItem)
		parameterAssociationItem.Parent = self

	def RemoveParameterAssociationItem(self, parameterAssociationItem: ParameterAssociationItem) -> None:
		"""
		Remove a parameter association from the parameter association list.

		The association is detached: its parent is cleared. The association itself is unchanged and can be added to another
		procedure call, or inserted at another position.

		:param parameterAssociationItem: The parameter association to remove.
		:raises ValueError:              If parameter 'parameterAssociationItem' is ``None``.
		:raises TypeError:               If parameter 'parameterAssociationItem' is not of type
		                                 :class:`~pyVHDLModel.Association.ParameterAssociationItem`.
		:raises NotAChildError:          If parameter 'parameterAssociationItem' is not a parameter association of this
		                                 procedure call.

		.. seealso::

		   :meth:`AddParameterAssociationItem`
		      |rarr| Add a parameter association at the end of the parameter association list.
		   :meth:`InsertParameterAssociationItem`
		      |rarr| Insert a parameter association at a position of the parameter association list.
		"""
		if parameterAssociationItem is None:
			raise ValueError("Parameter 'parameterAssociationItem' is None.")
		elif not isinstance(parameterAssociationItem, ParameterAssociationItem):
			ex = TypeError("Parameter 'parameterAssociationItem' is not of type 'ParameterAssociationItem'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parameterAssociationItem)}'.")
			raise ex

		for index, item in enumerate(self._parameterAssociationItems):
			if item is parameterAssociationItem:
				break
		else:
			raise NotAChildError(
				f"{getTypeName(parameterAssociationItem)} is not a parameter association of this {getTypeName(self)}.",
				element=parameterAssociationItem,
				parent=self
			)

		del self._parameterAssociationItems[index]
		parameterAssociationItem._parent = None


@export
class AssignmentMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all assignment statements.

	.. seealso::

	   * :class:`Signal assignment mixin <pyVHDLModel.Common.SignalAssignmentMixin>`
	   * :class:`Variable assignment mixin <pyVHDLModel.Common.VariableAssignmentMixin>`
	   * :class:`Conditional variable assignment <pyVHDLModel.Sequential.SequentialConditionalVariableAssignment>`
	   * :class:`Sequential selected variable assignment <pyVHDLModel.Sequential.SequentialSelectedVariableAssignment>`
	"""

	_target: Symbol  #: Reference to the assignment's destination.

	def __init__(self, target: Symbol) -> None:
		"""
		Initializes an assignment.

		:param target: Reference to the assignment's destination.
		"""
		self._target = target
		target.Parent = self

	@readonly
	def Target(self) -> Symbol:
		"""
		Read-only property to access the target (:attr:`_target`).

		:returns: The target.
		"""
		return self._target


@export
class SignalAssignmentMixin(AssignmentMixin, mixin=True):
	"""
	A mixin-class for all signal assignment statements.

	.. seealso::

	   * :class:`Concurrent signal assignment <pyVHDLModel.Concurrent.ConcurrentSignalAssignment>`
	   * :class:`Sequential signal assignment <pyVHDLModel.Sequential.SequentialSignalAssignment>`
	   * :class:`Conditional signal assignment <pyVHDLModel.Sequential.SequentialConditionalSignalAssignment>`
	   * :class:`Sequential selected signal assignment <pyVHDLModel.Sequential.SequentialSelectedSignalAssignment>`
	   * :class:`Signal force assignment <pyVHDLModel.Sequential.SignalForceAssignment>`
	   * :class:`Signal release assignment <pyVHDLModel.Sequential.SignalReleaseAssignment>`
	"""

	@readonly
	def Target(self) -> SignalSymbol:
		"""
		Read-only property to access the target (:attr:`_target`).

		:returns: The target.
		"""
		return self._target


@export
class VariableAssignmentMixin(AssignmentMixin, mixin=True):
	"""
	A mixin-class for all variable assignment statements.

	.. seealso::

	   * :class:`Sequential variable assignment <pyVHDLModel.Sequential.SequentialVariableAssignment>`
	"""

	# FIXME: move to sequential?
	_expression: ExpressionUnion  #: The assigned expression.

	def __init__(self, target: VariableSymbol, expression: ExpressionUnion) -> None:
		"""
		Initializes a variable assignment.

		:param target:     Reference to the assignment's destination.
		:param expression: The assigned expression.
		"""
		super().__init__(target)

		self._expression = expression
		expression.Parent = self

	@readonly
	def Target(self) -> VariableSymbol:
		"""
		Read-only property to access the target (:attr:`_target`).

		:returns: The target.
		"""
		return self._target

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression


@export
class WaveformMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all statements/entities holding a waveform (a list of :class:`WaveformElement`).

	.. seealso::

	   * :class:`Conditional waveform <pyVHDLModel.Common.ConditionalWaveform>`
	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	   * :class:`Others selected waveform <pyVHDLModel.Common.OthersSelectedWaveform>`
	   * :class:`Concurrent simple signal assignment <pyVHDLModel.Concurrent.ConcurrentSimpleSignalAssignment>`
	   * :class:`Sequential simple signal assignment <pyVHDLModel.Sequential.SequentialSimpleSignalAssignment>`
	   * :class:`Waveform element <pyVHDLModel.Base.WaveformElement>`
	"""

	_waveform: list[WaveformElement]  #: List of all waveform elements, in the order they were written.

	def __init__(self, waveform: Iterable[WaveformElement]) -> None:
		"""
		Initializes a waveform.

		:param waveform: List of all waveform elements, in the order they were written.
		"""
		self._waveform = []
		for waveformElement in waveform:
			self._waveform.append(waveformElement)
			waveformElement.Parent = self

	@readonly
	def Waveform(self) -> list[WaveformElement]:
		"""
		Read-only property to access the waveform (:attr:`_waveform`).

		:returns: List of waveform.
		"""
		return self._waveform


@export
class ExpressionMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all statements/entities holding a single expression.

	.. seealso::

	   * :class:`Conditional expression <pyVHDLModel.Common.ConditionalExpression>`
	   * :class:`Selected expression <pyVHDLModel.Common.SelectedExpression>`
	   * :class:`Others selected expression <pyVHDLModel.Common.OthersSelectedExpression>`
	   * :class:`Concurrent selected signal assignment <pyVHDLModel.Concurrent.ConcurrentSelectedSignalAssignment>`
	   * :class:`Sequential selected variable assignment <pyVHDLModel.Sequential.SequentialSelectedVariableAssignment>`
	   * :class:`Sequential selected signal assignment <pyVHDLModel.Sequential.SequentialSelectedSignalAssignment>`
	   * :class:`Signal force assignment <pyVHDLModel.Sequential.SignalForceAssignment>`
	"""

	_expression: ExpressionUnion  #: The expression held by this construct.

	def __init__(self, expression: ExpressionUnion) -> None:
		"""
		Initializes an expression.

		:param expression: The expression held by this construct.
		"""
		self._expression = expression
		expression.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression


@export
class ConditionalWaveform(ModelEntity, WaveformMixin, ConditionalMixin):
	"""
	Represents one branch of a conditional signal assignment.

	Each branch pairs a waveform (:data:`Waveform`) with a condition (:data:`Condition`). The final
	branch has no ``when``, so its condition is ``None``.

	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= '1' when cond else '0';
	      --   ^^^^^^^^^^^^^             <- this branch: Waveform=['1'], Condition=cond
	      --                      ^^^    <- final branch (no ``when``): Waveform=['0'], Condition=None

	.. seealso::

	   * :class:`Waveform element <pyVHDLModel.Base.WaveformElement>`
	   * :class:`Conditional expression <pyVHDLModel.Common.ConditionalExpression>`
	"""

	def __init__(
		self,
		waveform: Iterable[WaveformElement],
		condition: Nullable[ExpressionUnion] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a conditional waveform.

		:param waveform:  List of all waveform elements, in the order they were written.
		:param condition: The condition selecting this alternative.
		:param parent:    The parent model entity of this entity.
		"""
		super().__init__(parent)
		WaveformMixin.__init__(self, waveform)
		ConditionalMixin.__init__(self, condition)


@export
class ConditionalExpression(ModelEntity, ExpressionMixin, ConditionalMixin):
	"""
	Represents one branch of a conditional variable assignment.

	Each branch pairs an expression (:data:`Expression`) with a condition (:data:`Condition`). The
	final branch has no ``when``, so its condition is ``None``.

	.. admonition:: Example

	   .. code-block:: VHDL

	      v := '1' when cond else '0';
	      --   ^^^^^^^^^^^^^             <- this branch: Expression='1', Condition=cond
	      --                      ^^^    <- final branch (no ``when``): Expression='0', Condition=None

	.. seealso::

	   * :class:`Conditional waveform <pyVHDLModel.Common.ConditionalWaveform>`
	"""

	def __init__(
		self,
		expression: ExpressionUnion,
		condition: Nullable[ExpressionUnion] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a conditional expression.

		:param expression: The value assigned when the condition holds.
		:param condition:  The condition selecting this alternative.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)
		ExpressionMixin.__init__(self, expression)
		ConditionalMixin.__init__(self, condition)


@export
class ConditionalWaveformsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all statements holding a list of :class:`ConditionalWaveform` (both the
	concurrent and sequential forms of a conditional signal assignment).

	.. seealso::

	   * :class:`Conditional signal assignment <pyVHDLModel.Concurrent.ConcurrentConditionalSignalAssignment>`
	   * :class:`Conditional signal assignment <pyVHDLModel.Sequential.SequentialConditionalSignalAssignment>`	"""

	_conditionalWaveforms: list[ConditionalWaveform]  #: All alternatives, in order.

	def __init__(self, conditionalWaveforms: Iterable[ConditionalWaveform]) -> None:
		"""
		Initializes conditional waveforms.

		:param conditionalWaveforms: All alternatives, in order.
		"""
		self._conditionalWaveforms = []
		for conditionalWaveform in conditionalWaveforms:
			self._conditionalWaveforms.append(conditionalWaveform)
			conditionalWaveform.Parent = self

	@readonly
	def ConditionalWaveforms(self) -> list[ConditionalWaveform]:
		"""
		Read-only property to access the conditional waveforms (:attr:`_conditionalWaveforms`).

		:returns: List of conditional waveforms.
		"""
		return self._conditionalWaveforms


@export
class SelectedWaveform(BaseCase, WaveformMixin, ChoicesMixin):
	"""
	Represents one alternative of a selected signal assignment.

	Each alternative pairs a waveform (:data:`Waveform`) with the choices selecting it
	(:data:`Choices`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select s <= '1' when '0', '0' when others;
	      --                   ^^^^^^^^^^^^                     <- this alternative: Choices=['0'], Waveform=['1']

	.. seealso::

	   * :class:`Waveform element <pyVHDLModel.Base.WaveformElement>`
	   * :class:`Selected expression <pyVHDLModel.Common.SelectedExpression>`
	"""

	def __init__(
		self,
		choices: Iterable[BaseChoice],
		waveform: Iterable[WaveformElement],
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a selected waveform.

		:param choices:  List of all choices selecting this alternative.
		:param waveform: List of all waveform elements, in the order they were written.
		:param parent:   The parent model entity of this entity.
		"""
		super().__init__(parent)
		WaveformMixin.__init__(self, waveform)
		ChoicesMixin.__init__(self, choices)


@export
class OthersSelectedWaveform(BaseCase, WaveformMixin):
	"""
	Represents the ``others`` alternative of a selected signal assignment.

	It supplies the waveform (:data:`Waveform`) for every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select s <= '1' when '0', '0' when others;
	      --                                 ^^^^^^^^^^^^^^^    <- the others alternative
	"""

	def __init__(self, waveform: Iterable[WaveformElement], parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an others selected waveform.

		:param waveform: List of all waveform elements, in the order they were written.
		:param parent:   The parent model entity of this entity.
		"""
		super().__init__(parent)
		WaveformMixin.__init__(self, waveform)


@export
class SelectedExpression(BaseCase, ExpressionMixin, ChoicesMixin):
	"""
	Represents one alternative of a selected variable assignment.

	Each alternative pairs an expression (:data:`Expression`) with the choices selecting it
	(:data:`Choices`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select v := '1' when '0', '0' when others;
	      --                   ^^^^^^^^^^^^                     <- this alternative: Choices=['0'], Expression='1'

	.. seealso::

	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	"""

	def __init__(
		self,
		choices: Iterable[BaseChoice],
		expression: ExpressionUnion,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a selected expression.

		:param choices:    List of all choices selecting this alternative.
		:param expression: The value assigned for the matching choices.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)
		ExpressionMixin.__init__(self, expression)
		ChoicesMixin.__init__(self, choices)


@export
class OthersSelectedExpression(BaseCase, ExpressionMixin):
	"""
	Represents the ``others`` alternative of a selected variable assignment.

	It supplies the expression (:data:`Expression`) for every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select v := '1' when '0', '0' when others;
	      --                                 ^^^^^^^^^^^^^^^    <- the others alternative
	"""

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an others selected expression.

		:param expression: The value assigned for every unnamed choice.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)
		ExpressionMixin.__init__(self, expression)


@export
class SelectedWaveformsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all statements holding a list of :class:`SelectedWaveform`/
	:class:`OthersSelectedWaveform` (both the concurrent and sequential forms of a selected signal
	assignment).

	.. seealso::

	   * :class:`Concurrent selected signal assignment <pyVHDLModel.Concurrent.ConcurrentSelectedSignalAssignment>`
	   * :class:`Sequential selected signal assignment <pyVHDLModel.Sequential.SequentialSelectedSignalAssignment>`
	"""

	_selectedWaveforms: list[Union[SelectedWaveform, OthersSelectedWaveform]]  #: All alternatives, in order.

	def __init__(self, selectedWaveforms: Iterable[Union[SelectedWaveform, OthersSelectedWaveform]]) -> None:
		"""
		Initializes selected waveforms.

		:param selectedWaveforms: All alternatives, in order.
		"""
		self._selectedWaveforms = []
		for selectedWaveform in selectedWaveforms:
			self._selectedWaveforms.append(selectedWaveform)
			selectedWaveform.Parent = self

	@readonly
	def SelectedWaveforms(self) -> list[Union[SelectedWaveform, OthersSelectedWaveform]]:
		"""
		Read-only property to access the selected waveforms (:attr:`_selectedWaveforms`).

		:returns: List of selected waveforms.
		"""
		return self._selectedWaveforms


@export
class SelectedExpressionsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all statements holding a list of :class:`SelectedExpression`/
	:class:`OthersSelectedExpression`.

	.. seealso::

	   * :class:`Sequential selected variable assignment <pyVHDLModel.Sequential.SequentialSelectedVariableAssignment>`
	"""

	_selectedExpressions: list[Union[SelectedExpression, OthersSelectedExpression]]  #: All alternatives, in order.

	def __init__(self, selectedExpressions: Iterable[Union[SelectedExpression, OthersSelectedExpression]]) -> None:
		"""
		Initializes selected expressions.

		:param selectedExpressions: All alternatives, in order.
		"""
		self._selectedExpressions = []
		for selectedExpression in selectedExpressions:
			self._selectedExpressions.append(selectedExpression)
			selectedExpression.Parent = self

	@readonly
	def SelectedExpressions(self) -> list[Union[SelectedExpression, OthersSelectedExpression]]:
		"""
		Read-only property to access the selected expressions (:attr:`_selectedExpressions`).

		:returns: List of selected expressions.
		"""
		return self._selectedExpressions
