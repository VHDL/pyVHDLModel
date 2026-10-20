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

Declarations for sequential statements.
"""
from __future__              import annotations

from typing                  import Iterable, Optional as Nullable

from pyTooling.Common        import getFullyQualifiedName
from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType, abstractclass

from pyVHDLModel.Base        import ModelEntity, ExpressionUnion, Range, BaseChoice, BaseCase, ConditionalMixin, IfBranchMixin, ElsifBranchMixin
from pyVHDLModel.Base        import ElseBranchMixin, ReportStatementMixin, AssertStatementMixin, WaveformElement, ChoicesMixin
from pyVHDLModel.Base        import LabeledEntityMixin
from pyVHDLModel.Exception   import AlreadyInDesignError, DuplicateLabelError, NotAChildError
from pyVHDLModel.Symbol      import Symbol, SignalSymbol, VariableSymbol
from pyVHDLModel.Common      import Statement, ProcedureCallMixin
from pyVHDLModel.Common      import AssignmentMixin, SignalAssignmentMixin, VariableAssignmentMixin
from pyVHDLModel.Common      import ConditionalWaveform, ConditionalExpression
from pyVHDLModel.Common      import ConditionalWaveformsMixin, WaveformMixin
from pyVHDLModel.Common      import ExpressionMixin, SelectedWaveformsMixin, SelectedExpressionsMixin
from pyVHDLModel.Common      import SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Common      import SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Association import ParameterAssociationItem


@export
@abstractclass
class SequentialStatement(Statement):
	"""
	Represents the base-class of all sequential statements.

	Sequential statements appear in a process or a subprogram body.
	"""


@export
class SequentialStatementsMixin(metaclass=ExtendedType, mixin=True, expects=("_LabelRegion", )):
	"""
	A mixin-class for language constructs containing sequential statements.

	The statements are available in declaration order as :data:`Statements`.

	.. seealso::

	   * :class:`Process statement <pyVHDLModel.Concurrent.ProcessStatement>`
	   * :class:`Branch <pyVHDLModel.Sequential.Branch>`
	   * :class:`Sequential case <pyVHDLModel.Sequential.SequentialCase>`
	   * :class:`Loop statement <pyVHDLModel.Sequential.LoopStatement>`
	   * :class:`Subprogram <pyVHDLModel.Subprogram.Subprogram>`
	"""
	_statements: list[SequentialStatement]  #: List of all sequential statements in this construct.

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None) -> None:
		# TODO: extract to mixin
		"""
		Initializes sequential statements.

		:param statements: List of all sequential statements in this construct.
		"""
		self._statements = []
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item.Parent = self

	@readonly
	def Statements(self) -> list[SequentialStatement]:
		"""
		Read-only property to access the list of sequential statements (:attr:`_statements`).

		:returns: A list of sequential statements.
		"""
		return self._statements

	def _Labels(self) -> tuple[SequentialStatement, ...]:
		"""
		Return the labeled statements of this construct, including the statements nested in compound statements.

		Every label of a process or subprogram body is declared in the process' or subprogram's declarative region, also
		a label inside an if branch, a case alternative or a loop.

		:returns: Tuple of labeled statements, depth-first in statement order.
		"""
		return tuple(label for statement in self._statements for label in self._LabelsOf(statement))

	@staticmethod
	def _LabelsOf(statement: SequentialStatement) -> tuple[SequentialStatement, ...]:
		"""
		Return a statement, if it's labeled, and the labeled statements nested in it.

		:param statement: The sequential statement.
		:returns:         Tuple of labeled statements, depth-first in statement order.
		"""
		labels: list[SequentialStatement] = [] if statement._normalizedLabel is None else [statement]
		if isinstance(statement, SequentialStatementsMixin):
			labels.extend(statement._Labels())
		elif isinstance(statement, IfStatement):
			labels.extend(statement._ifBranch._Labels())
			for branch in statement._elsifBranches:
				labels.extend(branch._Labels())

			if statement._elseBranch is not None:
				labels.extend(statement._elseBranch._Labels())
		elif isinstance(statement, CaseStatement):
			for case in statement._cases:
				labels.extend(case._Labels())

		return tuple(labels)

	def AddStatement(self, statement: SequentialStatement) -> None:
		"""
		Add a sequential statement at the end of this construct.

		The statement's parent is set to this construct.

		:param statement:             The sequential statement to add.
		:raises ValueError:           If parameter 'statement' is ``None``.
		:raises TypeError:            If parameter 'statement' is not of type :class:`SequentialStatement`.
		:raises AlreadyInDesignError: If parameter 'statement' already has a parent.
		:raises DuplicateLabelError:  If the declarative region already declares a label of the statement.

		.. seealso::

		   :meth:`InsertStatement`
		      |rarr| Insert a sequential statement at a position of this construct.
		   :meth:`RemoveStatement`
		      |rarr| Remove a sequential statement from this construct.
		"""
		self.InsertStatement(len(self._statements), statement)

	def InsertStatement(self, index: int, statement: SequentialStatement) -> None:
		"""
		Insert a sequential statement at a position of this construct.

		The statement's parent is set to this construct.

		Every label of a process or subprogram body is declared in the process' or subprogram's declarative region: the
		statement's label and the labels of statements nested in it (in branches, case alternatives and loops) may neither
		repeat another label of the body, nor an identifier declared in the region. A construct not in a process or
		subprogram (yet) checks the labels of its own statements. An unlabeled statement declares nothing.

		:param index:                 Position, from ``0`` (first) to the number of statements (append). A negative index
		                              counts from the end, as for :meth:`list.insert`: ``-1`` inserts before the last
		                              statement.
		:param statement:             The sequential statement to insert.
		:raises ValueError:           If parameter 'index' is ``None``.
		:raises TypeError:            If parameter 'index' is not of type :class:`int`.
		:raises ValueError:           If parameter 'index' is out of range.
		:raises ValueError:           If parameter 'statement' is ``None``.
		:raises TypeError:            If parameter 'statement' is not of type :class:`SequentialStatement`.
		:raises AlreadyInDesignError: If parameter 'statement' already has a parent.
		:raises DuplicateLabelError:  If the declarative region already declares a label of the statement.

		.. seealso::

		   :meth:`AddStatement`
		      |rarr| Add a sequential statement at the end of this construct.
		   :meth:`InsertStatementBefore`
		      |rarr| Insert a sequential statement before another statement.
		   :meth:`InsertStatementAfter`
		      |rarr| Insert a sequential statement after another statement.
		   :meth:`RemoveStatement`
		      |rarr| Remove a sequential statement from this construct.
		"""
		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, int):
			ex = TypeError("Parameter 'index' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex
		elif not (-len(self._statements) <= index <= len(self._statements)):
			ex = ValueError(f"Parameter 'index' is out of range {-len(self._statements)}..{len(self._statements)}.")
			ex.add_note(f"Got value '{index}'.")
			raise ex

		if statement is None:
			raise ValueError("Parameter 'statement' is None.")
		elif not isinstance(statement, SequentialStatement):
			ex = TypeError("Parameter 'statement' is not of type 'SequentialStatement'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(statement)}'.")
			raise ex
		elif statement._parent is not None:
			label = "" if statement._label is None else f" '{statement._label}'"
			ex = AlreadyInDesignError(f"{statement.__class__.__name__}{label} already has a parent.")
			ex.add_note(f"Remove it from its {statement._parent.__class__.__name__} first.")
			raise ex

		region = self._LabelRegion()
		for labeled in self._LabelsOf(statement):
			if region is None:
				clashes = tuple(item for item in self._Labels() if item._normalizedLabel == labeled._normalizedLabel)
			else:
				clashes = region._ClashingDeclarations(labeled)

			if len(clashes) > 0:
				construct = self if region is None else region
				ex = DuplicateLabelError(f"{construct.__class__.__name__} already declares '{labeled._label}'.")
				ex.add_note(f"Existing declaration is of type '{getFullyQualifiedName(clashes[0])}'.")
				raise ex

		self._statements.insert(index, statement)
		statement.Parent = self

	def InsertStatementBefore(self, statement: SequentialStatement, before: SequentialStatement) -> None:
		"""
		Insert a sequential statement before another statement of this construct.

		The statement's parent is set to this construct.

		:param statement:             The sequential statement to insert.
		:param before:                The statement of this construct to insert before.
		:raises ValueError:           If parameter 'before' is ``None``.
		:raises TypeError:            If parameter 'before' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError:       If parameter 'before' is not a statement of this construct.
		:raises ValueError:           If parameter 'statement' is ``None``.
		:raises TypeError:            If parameter 'statement' is not of type :class:`SequentialStatement`.
		:raises AlreadyInDesignError: If parameter 'statement' already has a parent.
		:raises DuplicateLabelError:  If the declarative region already declares a label of the statement.

		.. seealso::

		   :meth:`InsertStatement`
		      |rarr| Insert a sequential statement at a position of this construct.
		   :meth:`InsertStatementAfter`
		      |rarr| Insert a sequential statement after another statement.
		"""
		if before is None:
			raise ValueError("Parameter 'before' is None.")
		elif not isinstance(before, ModelEntity):
			ex = TypeError("Parameter 'before' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(before)}'.")
			raise ex

		for index, item in enumerate(self._statements):
			if item is before:
				break
		else:
			label = ""
			if isinstance(before, LabeledEntityMixin) and before._label is not None:
				label = f" '{before._label}'"
			raise NotAChildError(
				f"{before.__class__.__name__}{label} is not a statement of this {self.__class__.__name__}."
			)

		self.InsertStatement(index, statement)

	def InsertStatementAfter(self, statement: SequentialStatement, after: SequentialStatement) -> None:
		"""
		Insert a sequential statement after another statement of this construct.

		The statement's parent is set to this construct.

		:param statement:             The sequential statement to insert.
		:param after:                 The statement of this construct to insert after.
		:raises ValueError:           If parameter 'after' is ``None``.
		:raises TypeError:            If parameter 'after' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError:       If parameter 'after' is not a statement of this construct.
		:raises ValueError:           If parameter 'statement' is ``None``.
		:raises TypeError:            If parameter 'statement' is not of type :class:`SequentialStatement`.
		:raises AlreadyInDesignError: If parameter 'statement' already has a parent.
		:raises DuplicateLabelError:  If the declarative region already declares a label of the statement.

		.. seealso::

		   :meth:`InsertStatement`
		      |rarr| Insert a sequential statement at a position of this construct.
		   :meth:`InsertStatementBefore`
		      |rarr| Insert a sequential statement before another statement.
		"""
		if after is None:
			raise ValueError("Parameter 'after' is None.")
		elif not isinstance(after, ModelEntity):
			ex = TypeError("Parameter 'after' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(after)}'.")
			raise ex

		for index, item in enumerate(self._statements):
			if item is after:
				break
		else:
			label = ""
			if isinstance(after, LabeledEntityMixin) and after._label is not None:
				label = f" '{after._label}'"
			raise NotAChildError(
				f"{after.__class__.__name__}{label} is not a statement of this {self.__class__.__name__}."
			)

		self.InsertStatement(index + 1, statement)

	def RemoveStatement(self, statement: SequentialStatement) -> None:
		"""
		Remove a sequential statement from this construct.

		The statement is detached: its parent is cleared. The statement itself is unchanged and can be added to another
		construct, or inserted at another position; its labels are free again in this construct's declarative region.

		:param statement:       The sequential statement to remove.
		:raises ValueError:     If parameter 'statement' is ``None``.
		:raises TypeError:      If parameter 'statement' is not of type :class:`~pyVHDLModel.Base.ModelEntity`.
		:raises NotAChildError: If parameter 'statement' is not a statement of this construct.

		.. seealso::

		   :meth:`AddStatement`
		      |rarr| Add a sequential statement at the end of this construct.
		   :meth:`InsertStatement`
		      |rarr| Insert a sequential statement at a position of this construct.
		"""
		if statement is None:
			raise ValueError("Parameter 'statement' is None.")
		elif not isinstance(statement, ModelEntity):
			ex = TypeError("Parameter 'statement' is not of type 'ModelEntity'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(statement)}'.")
			raise ex

		for index, item in enumerate(self._statements):
			if item is statement:
				break
		else:
			label = ""
			if isinstance(statement, LabeledEntityMixin) and statement._label is not None:
				label = f" '{statement._label}'"
			raise NotAChildError(
				f"{statement.__class__.__name__}{label} is not a statement of this {self.__class__.__name__}."
			)

		del self._statements[index]
		statement._parent = None


@export
class SequentialProcedureCall(SequentialStatement, ProcedureCallMixin):
	"""
	Represents a procedure call as a sequential statement.

	Like every sequential statement, it can carry an optional label (:data:`Label`).

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : log("hello");
	      --^^^                   <- optional Label
	      --      ^^^^^^^^^^^^    <- the call

	.. seealso::

	   * :class:`Concurrent counterpart <pyVHDLModel.Concurrent.ConcurrentProcedureCall>`
	"""
	def __init__(
		self,
		procedureName: Symbol,
		parameterAssociationItems: Nullable[Iterable[ParameterAssociationItem]] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a procedure call as a sequential statement.

		:param procedureName:             Reference to the called procedure.
		:param parameterAssociationItems: List of all parameter associations of the call.
		:param label:                     The label of a model entity.
		:param parent:                    The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		ProcedureCallMixin.__init__(self, procedureName, parameterAssociationItems)


@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignmentMixin):
	"""
	Represents the base-class of all sequential signal assignments.

	.. seealso::

	   * :class:`Sequential simple signal assignment <pyVHDLModel.Sequential.SequentialSimpleSignalAssignment>`
	"""
	def __init__(self, target: SignalSymbol, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a sequential signal assignment.

		:param target: Reference to the assignment's destination.
		:param label:  The label of a model entity.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class SequentialSimpleSignalAssignment(SequentialSignalAssignment, WaveformMixin):
	"""
	Represents a simple sequential signal assignment.

	The assignment's destination is available as :data:`Target`, its value as :data:`Waveform`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : s <= '1';
	      --^^^               <- optional Label
	      --      ^           <- Target
	      --           ^^^    <- Waveform

	.. seealso::

	   * :class:`Concurrent counterpart <pyVHDLModel.Concurrent.ConcurrentSimpleSignalAssignment>`
	"""
	def __init__(self, target: SignalSymbol, waveform: Iterable[WaveformElement], label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a simple sequential signal assignment.

		:param target:   Reference to the assignment's destination.
		:param waveform: List of all waveform elements, in the order they were written.
		:param label:    The label of a model entity.
		:param parent:   The parent model entity of this entity.
		"""
		super().__init__(target, label, parent)
		WaveformMixin.__init__(self, waveform)


@export
class SequentialVariableAssignment(SequentialStatement, VariableAssignmentMixin):
	"""
	Represents a simple sequential variable assignment.

	The assignment's destination is available as :data:`Target`, its value as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : v := '1';
	      --^^^               <- optional Label
	      --      ^           <- Target
	      --           ^^^    <- Expression
	"""
	def __init__(self, target: VariableSymbol, expression: ExpressionUnion, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a simple sequential variable assignment.

		:param target:     Reference to the assignment's destination.
		:param expression: The assigned expression.
		:param label:      The label of a model entity.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		VariableAssignmentMixin.__init__(self, target, expression)


@export
class SequentialConditionalVariableAssignment(SequentialStatement, AssignmentMixin):
	"""
	Represents a conditional sequential variable assignment.

	The alternatives are available as :data:`ConditionalExpressions`, a list of
	:class:`~pyVHDLModel.Common.ConditionalExpression`. The model holds them in a list and has no
	distinct field per alternative, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : v := '1' when sel = '0' else '0';
	      --^^^                                       <- optional Label
	      --      ^                                   <- Target
	      --           ^^^^^^^^^^^^^^^^^^             <- ConditionalExpressions[0]
	      --                                   ^^^    <- ConditionalExpressions[1]

	.. seealso::

	   * :class:`Conditional expression <pyVHDLModel.Common.ConditionalExpression>`
	"""

	_conditionalExpressions: list[ConditionalExpression]  #: List of all alternatives, in the order they were written.

	def __init__(
		self,
		target: VariableSymbol,
		conditionalExpressions: Iterable[ConditionalExpression],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a conditional sequential variable assignment.

		:param target:                 Reference to the assignment's destination.
		:param conditionalExpressions: List of all alternatives, in the order they were written.
		:param label:                  The label of a model entity.
		:param parent:                 The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		AssignmentMixin.__init__(self, target)

		self._conditionalExpressions = []
		for conditionalExpression in conditionalExpressions:
			self._conditionalExpressions.append(conditionalExpression)
			conditionalExpression.Parent = self

	@readonly
	def ConditionalExpressions(self) -> list[ConditionalExpression]:
		"""
		Read-only property to access the conditional expressions (:attr:`_conditionalExpressions`).

		:returns: List of conditional expressions.
		"""
		return self._conditionalExpressions


@export
class SequentialConditionalSignalAssignment(SequentialStatement, SignalAssignmentMixin, ConditionalWaveformsMixin):
	"""
	Represents a conditional sequential signal assignment.

	The alternatives are available as :data:`ConditionalWaveforms`, a list of
	:class:`~pyVHDLModel.Common.ConditionalWaveform`. The model holds them in a list and has no
	distinct field per alternative, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : s <= '1' when sel = '0' else '0';
	      --^^^                                       <- optional Label
	      --      ^                                   <- Target
	      --           ^^^^^^^^^^^^^^^^^^             <- ConditionalWaveforms[0]
	      --                                   ^^^    <- ConditionalWaveforms[1]

	.. seealso::

	   * :class:`Concurrent counterpart <pyVHDLModel.Concurrent.ConcurrentConditionalSignalAssignment>`
	   * :class:`Conditional waveform <pyVHDLModel.Common.ConditionalWaveform>`
	"""

	def __init__(
		self,
		target: SignalSymbol,
		conditionalWaveforms: Iterable[ConditionalWaveform],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a conditional sequential signal assignment.

		:param target:               Reference to the assignment's destination.
		:param conditionalWaveforms: All alternatives, in order.
		:param label:                The label of a model entity.
		:param parent:               The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)
		ConditionalWaveformsMixin.__init__(self, conditionalWaveforms)


@export
class SequentialSelectedVariableAssignment(SequentialStatement, AssignmentMixin, ExpressionMixin, SelectedExpressionsMixin):
	"""
	Represents a selected sequential variable assignment.

	The selector is available as :data:`Expression`, the alternatives as :data:`SelectedExpressions`,
	a list of :class:`~pyVHDLModel.Common.SelectedExpression`. The model holds them in a list and has
	no distinct field per alternative, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : with sel select v := '1' when '0', '0' when others;
	      --^^^                                                         <- optional Label
	      --           ^^^                                              <- Expression
	      --                      ^                                     <- Target
	      --                           ^^^^^^^^^^^^                     <- SelectedExpressions[0]
	      --                                         ^^^^^^^^^^^^^^^    <- SelectedExpressions[1]

	.. seealso::

	   * :class:`Selected expression <pyVHDLModel.Common.SelectedExpression>`
	"""

	def __init__(
		self,
		target: VariableSymbol,
		expression: ExpressionUnion,
		selectedExpressions: Iterable[SelectedExpression],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a selected sequential variable assignment.

		:param target:              Reference to the assignment's destination.
		:param expression:          The selector expression.
		:param selectedExpressions: All alternatives, in order.
		:param label:               The label of a model entity.
		:param parent:              The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		AssignmentMixin.__init__(self, target)
		ExpressionMixin.__init__(self, expression)
		SelectedExpressionsMixin.__init__(self, selectedExpressions)


@export
class SequentialSelectedSignalAssignment(SequentialStatement, SignalAssignmentMixin, ExpressionMixin, SelectedWaveformsMixin):
	"""
	Represents a selected sequential signal assignment.

	The selector is available as :data:`Expression`, the alternatives as :data:`SelectedWaveforms`,
	a list of :class:`~pyVHDLModel.Common.SelectedWaveform`. The model holds them in a list and has
	no distinct field per alternative, so the markers below name list elements.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : with sel select s <= '1' when '0', '0' when others;
	      --^^^                                                         <- optional Label
	      --           ^^^                                              <- Expression
	      --                      ^                                     <- Target
	      --                           ^^^^^^^^^^^^                     <- SelectedWaveforms[0]
	      --                                         ^^^^^^^^^^^^^^^    <- SelectedWaveforms[1]

	.. seealso::

	   * :class:`Concurrent counterpart <pyVHDLModel.Concurrent.ConcurrentSelectedSignalAssignment>`
	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	"""

	def __init__(
		self,
		target: SignalSymbol,
		expression: ExpressionUnion,
		selectedWaveforms: Iterable[SelectedWaveform],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a selected sequential signal assignment.

		:param target:            Reference to the assignment's destination.
		:param expression:        The selector expression.
		:param selectedWaveforms: All alternatives, in order.
		:param label:             The label of a model entity.
		:param parent:            The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)
		ExpressionMixin.__init__(self, expression)
		SelectedWaveformsMixin.__init__(self, selectedWaveforms)


@export
class SignalForceAssignment(SequentialStatement, SignalAssignmentMixin, ExpressionMixin):
	"""
	Represents a signal force assignment.

	A force assignment overrides a signal's driver until it is released.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : s <= force '1';
	      --^^^                     <- optional Label
	      --      ^                 <- Target
	      --                 ^^^    <- Expression
	"""

	def __init__(
		self,
		target: SignalSymbol,
		expression: ExpressionUnion,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a signal force assignment.

		:param target:     Reference to the assignment's destination.
		:param expression: The value forced onto the signal.
		:param label:      The label of a model entity.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)
		ExpressionMixin.__init__(self, expression)


@export
class SignalReleaseAssignment(SequentialStatement, SignalAssignmentMixin):
	"""
	Represents a signal release assignment.

	A release assignment ends a previously applied force.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : s <= release;
	      --^^^                   <- optional Label
	      --      ^               <- Target
	"""

	def __init__(self, target: SignalSymbol, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a signal release assignment.

		:param target: Reference to the assignment's destination.
		:param label:  The label of a model entity.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class SequentialReportStatement(SequentialStatement, ReportStatementMixin):
	"""
	Represents a sequential report statement.

	The report string is available as :data:`Message`, the optional severity as :data:`Severity`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : report "message" severity note;
	      --^^^                                     <- optional Label
	      --             ^^^^^^^^^                  <- Message
	      --                                ^^^^    <- optional Severity
	"""
	def __init__(self, message: ExpressionUnion, severity: Nullable[ExpressionUnion] = None, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a sequential report statement.

		:param message:  The reported message, or ``None`` if none was given.
		:param severity: The reported severity level, or ``None`` if none was given.
		:param label:    The label of a model entity.
		:param parent:   The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		ReportStatementMixin.__init__(self, message, severity)


@export
class SequentialAssertStatement(SequentialStatement, AssertStatementMixin):
	"""
	Represents a sequential assertion statement.

	The checked condition is available as :data:`Condition`, the optional report string as
	:data:`Message` and the optional severity as :data:`Severity`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : assert sel = '0' report "bad" severity error;
	      --^^^                                                   <- optional Label
	      --             ^^^^^^^^^                                <- Condition
	      --                              ^^^^^                   <- optional Message
	      --                                             ^^^^^    <- optional Severity

	.. seealso::

	   * :class:`Concurrent counterpart <pyVHDLModel.Concurrent.ConcurrentAssertStatement>`
	"""
	def __init__(
		self,
		condition: ExpressionUnion,
		message: Nullable[ExpressionUnion] = None,
		severity: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a sequential assertion statement.

		:param condition: The condition guarding this statement.
		:param message:   The reported message, or ``None`` if none was given.
		:param severity:  The reported severity level, or ``None`` if none was given.
		:param label:     The label of a model entity.
		:param parent:    The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		AssertStatementMixin.__init__(self, condition, message, severity)


@export
@abstractclass
class CompoundStatement(SequentialStatement):
	"""
	Represents the base-class of all compound statements.

	A compound statement contains further sequential statements: if, case and loop statements.

	.. seealso::

	   * :class:`If statement <pyVHDLModel.Sequential.IfStatement>`
	   * :class:`Case statement <pyVHDLModel.Sequential.CaseStatement>`
	   * :class:`Loop statement <pyVHDLModel.Sequential.LoopStatement>`
	"""


@export
@abstractclass
class Branch(ModelEntity, SequentialStatementsMixin):
	"""
	Represents the base-class of all branches of an if statement.

	.. seealso::

	   * :class:`If branch <pyVHDLModel.Sequential.IfBranch>`
	   * :class:`Elsif branch <pyVHDLModel.Sequential.ElsifBranch>`
	   * :class:`Else branch <pyVHDLModel.Sequential.ElseBranch>`
	"""

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a branch.

		:param statements: List of all sequential statements in this construct.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)
		SequentialStatementsMixin.__init__(self, statements)

	def _LabelRegion(self) -> Nullable[ModelEntity]:
		"""
		Return the process or subprogram declaring the labels of this branch's statements.

		It's the region of the construct holding the if statement.

		:returns: The process or subprogram, or ``None`` if the branch isn't part of one (yet).
		"""
		ifStatement = self._parent
		if ifStatement is None or ifStatement._parent is None:
			return None

		return ifStatement._parent._LabelRegion()


@export
class IfBranch(Branch, IfBranchMixin):
	"""
	Represents the ``if`` branch of an if statement.

	The branch's condition is available as :data:`Condition`, its body as :data:`Statements`.

	.. admonition:: Example

	   The whole if statement is shown; the bracket marks the part this class represents.

	   .. code-block:: VHDL

	      if sel = '0' then     -- ┐ IfBranch
	      -- ^^^^^^^^^          -- │   <- Condition
	        s <= '0';           -- │
	      --^^^^^^^^^           -- ┘   <- Statements
	      elsif sel = '1' then
	        s <= '1';
	      else
	        s <= '0';
	      end if;
	"""
	def __init__(self, condition: ExpressionUnion, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an if branch.

		:param condition:  The condition guarding this statement.
		:param statements: List of all sequential statements in this construct.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(statements, parent)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifBranch(Branch, ElsifBranchMixin):
	"""
	Represents an ``elsif`` branch of an if statement.

	The branch's condition is available as :data:`Condition`, its body as :data:`Statements`.
	An if statement may have any number of them.

	.. admonition:: Example

	   The whole if statement is shown; the bracket marks the part this class represents.

	   .. code-block:: VHDL

	      if sel = '0' then
	        s <= '0';
	      elsif sel = '1' then  -- ┐ ElsifBranch
	      --    ^^^^^^^^^       -- │   <- Condition
	        s <= '1';           -- │
	      --^^^^^^^^^           -- ┘   <- Statements
	      else
	        s <= '0';
	      end if;
	"""
	def __init__(self, condition: ExpressionUnion, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an ``elsif`` branch of an if statement.

		:param condition:  The condition guarding this statement.
		:param statements: List of all sequential statements in this construct.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(statements, parent)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseBranch(Branch, ElseBranchMixin):
	"""
	Represents the ``else`` branch of an if statement.

	Unlike the other branches, an else branch has no condition; it only has a body
	(:data:`Statements`). An if statement has at most one.

	.. admonition:: Example

	   The whole if statement is shown; the bracket marks the part this class represents.

	   .. code-block:: VHDL

	      if sel = '0' then
	        s <= '0';
	      elsif sel = '1' then
	        s <= '1';
	      else                  -- ┐ ElseBranch
	        s <= '0';           -- │
	      --^^^^^^^^^           -- ┘   <- Statements
	      end if;
	"""
	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes an else branch.

		:param statements: List of all sequential statements in this construct.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(statements, parent)
		ElseBranchMixin.__init__(self)


@export
class IfStatement(CompoundStatement):
	"""
	Represents an if statement.

	An if statement has one ``if`` branch (:data:`IfBranch`), any number of ``elsif`` branches
	(:data:`ElsIfBranches`) and an optional ``else`` branch (:data:`ElseBranch`).

	.. admonition:: Example

	   Only an ``if`` branch:

	   .. code-block:: VHDL

	        lbl : if sel = '0' then
	      --^^^                       <- optional Label
	          s <= '0';
	        end if;

	   With ``elsif`` and ``else`` branches:

	   .. code-block:: VHDL

	        lbl : if sel = '0' then
	      --^^^                       <- optional Label
	      --      ^^^^^^^^^^^^^^^^^   <- IfBranch
	          s <= '0';
	        elsif sel = '1' then
	      --^^^^^^^^^^^^^^^^^^^^      <- ElsIfBranches[0]
	          s <= '1';
	        else
	      --^^^^                      <- ElseBranch
	          s <= '0';
	        end if;

	.. seealso::

	   * :class:`If-generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	"""
	_ifBranch: IfBranch                #: The mandatory ``if`` branch.
	_elsifBranches: list[ElsifBranch]  #: List of all ``elsif`` branches, in the order they were written.
	_elseBranch: Nullable[ElseBranch]  #: The optional ``else`` branch, or ``None`` if none was given.

	def __init__(
		self,
		ifBranch: IfBranch,
		elsifBranches: Nullable[Iterable[ElsifBranch]] = None,
		elseBranch: Nullable[ElseBranch] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes an if statement.

		:param ifBranch:      The mandatory ``if`` branch.
		:param elsifBranches: List of all ``elsif`` branches, in the order they were written.
		:param elseBranch:    The optional ``else`` branch, or ``None`` if none was given.
		:param label:         The label of a model entity.
		:param parent:        The parent model entity of this entity.
		"""
		super().__init__(label, parent)

		self._ifBranch = ifBranch
		ifBranch.Parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch.Parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch.Parent = self
		else:
			self._elseBranch = None

	@readonly
	def IfBranch(self) -> IfBranch:
		"""
		Read-only property to access the if-branch of the if-statement (:attr:`_ifBranch`).

		:returns: The if-branch.
		"""
		return self._ifBranch

	@readonly
	def ElsIfBranches(self) -> list[ElsifBranch]:
		"""
		Read-only property to access the elsif-branch of the if-statement (:attr:`_elsifBranch`).

		:returns: The elsif-branch.
		"""
		return self._elsifBranches

	@readonly
	def ElseBranch(self) -> Nullable[ElseBranch]:
		"""
		Read-only property to access the else-branch of the if-statement (:attr:`_elseBranch`).

		:returns: The else-branch.
		"""
		return self._elseBranch


@export
@abstractclass
class SequentialChoice(BaseChoice):
	"""
	Represents the base-class of all choices in a sequential case statement.

	.. seealso::

	   * :class:`Indexed choice <pyVHDLModel.Sequential.IndexedChoice>`
	   * :class:`Ranged choice <pyVHDLModel.Sequential.RangedChoice>`
	"""


@export
class IndexedChoice(SequentialChoice):
	"""
	Represents a case choice given by a single value.

	The value is available as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 0      => v := '1';
	      --   ^                     <- Expression
	"""
	_expression: ExpressionUnion  #: The expression this choice selects on.

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a case choice given by a single value.

		:param expression: The expression this choice selects on.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression

	def __str__(self) -> str:
		"""
		Formats the indexed case choice.

		**Format:** ``0``

		:returns: Formatted indexed case choice.
		"""
		return str(self._expression)


@export
class RangedChoice(SequentialChoice):
	"""
	Represents a case choice given by a range.

	The range is available as :data:`Range`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 1 to 2 => v := '0';
	      --   ^^^^^^                <- Range
	"""
	_range: Range  #: The range this choice selects on.

	def __init__(self, rng: Range, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a case choice given by a range.

		:param rng:    The range this choice selects on.
		:param parent: The parent model entity of this entity.
		"""
		super().__init__(parent)

		self._range = rng
		rng.Parent = self

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	def __str__(self) -> str:
		"""
		Formats the ranged case choice.

		**Format:** ``0 to 3``

		:returns: Formatted ranged case choice.
		"""
		return str(self._range)


@export
class SequentialCase(BaseCase, SequentialStatementsMixin, ChoicesMixin):
	"""
	Represents the base-class of all alternatives of a sequential case statement.

	.. seealso::

	   * :class:`Case <pyVHDLModel.Sequential.Case>`
	   * :class:`Others case <pyVHDLModel.Sequential.OthersCase>`
	"""
	def __init__(
		self,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		choices: Nullable[Iterable[BaseChoice]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a sequential case.

		:param statements: List of all sequential statements in this construct.
		:param choices:    List of all choices selecting this alternative.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(parent)
		SequentialStatementsMixin.__init__(self, statements)
		ChoicesMixin.__init__(self, choices)

	def _LabelRegion(self) -> Nullable[ModelEntity]:
		"""
		Return the process or subprogram declaring the labels of this case alternative's statements.

		It's the region of the construct holding the case statement.

		:returns: The process or subprogram, or ``None`` if the case alternative isn't part of one (yet).
		"""
		caseStatement = self._parent
		if caseStatement is None or caseStatement._parent is None:
			return None

		return caseStatement._parent._LabelRegion()


@export
class Case(SequentialCase):
	"""
	Represents one alternative of a case statement, selected by its choices.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 1 to 2 => v := '0';
	      --   ^^^^^^                <- Choices
	      --             ^^^^^^^^^   <- the statements
	"""
	def __init__(self, choices: Iterable[SequentialChoice], statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a case.

		:param choices:    List of all choices selecting this alternative.
		:param statements: List of all sequential statements in this construct.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(statements, choices, parent)

	def __str__(self) -> str:
		"""
		Formats the case alternative.

		**Format:** ``when 0 | 1 =>``

		:returns: Formatted case alternative.
		"""
		return "when {choices} =>".format(choices=" | ".join(str(c) for c in self._choices))


@export
class OthersCase(SequentialCase):
	"""
	Represents the ``others`` alternative of a case statement.

	It covers every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when others => null;
	      --   ^^^^^^            <- the choice
	"""
	def __str__(self) -> str:
		"""
		Formats the ``others`` case alternative.

		**Format:** ``when others =>``

		:returns: Formatted ``others`` case alternative.
		"""
		return "when others =>"


@export
class CaseStatement(CompoundStatement):
	"""
	Represents a case statement.

	The expression being tested is available as :data:`SelectExpression`, the alternatives as
	:data:`Cases`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : case sel is
	      --^^^                          <- optional Label
	      --           ^^^               <- SelectExpression
	          when '0'    => s <= '1';
	      --  ^^^^^^^^^^^^^^^^^^^^^^^^   <- Cases[0]
	          when others => null;
	      --  ^^^^^^^^^^^^^^^^^^^^       <- Cases[1]
	        end case;

	.. seealso::

	   * :class:`Case-generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	"""
	_expression: ExpressionUnion       #: The expression being tested.
	_cases:      list[SequentialCase]  #: List of all alternatives, in the order they were written.

	def __init__(self, expression: ExpressionUnion, cases: Iterable[SequentialCase], label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a case statement.

		:param expression: The expression being tested.
		:param cases:      List of all alternatives, in the order they were written.
		:param label:      The label of a model entity.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(label, parent)

		self._expression = expression
		expression.Parent = self

		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case.Parent = self

	@readonly
	def SelectExpression(self) -> ExpressionUnion:
		"""
		Read-only property to access the select expression (:attr:`_expression`).

		:returns: The select expression.
		"""
		return self._expression

	@readonly
	def Cases(self) -> list[SequentialCase]:
		"""
		Read-only property to access the cases (:attr:`_cases`).

		:returns: List of cases.
		"""
		return self._cases


@export
@abstractclass
class LoopStatement(CompoundStatement, SequentialStatementsMixin):
	"""
	Represents the base-class of all loop statements.

	.. seealso::

	   * :class:`Endless loop statement <pyVHDLModel.Sequential.EndlessLoopStatement>`
	   * :class:`For loop statement <pyVHDLModel.Sequential.ForLoopStatement>`
	   * :class:`While loop statement <pyVHDLModel.Sequential.WhileLoopStatement>`
	"""

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a loop statement.

		:param statements: List of all sequential statements in this construct.
		:param label:      The label of a model entity.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		SequentialStatementsMixin.__init__(self, statements)

	def _LabelRegion(self) -> Nullable[ModelEntity]:
		"""
		Return the process or subprogram declaring the labels of this loop's statements.

		It's the region of the construct holding the loop.

		:returns: The process or subprogram, or ``None`` if the loop isn't part of one (yet).
		"""
		return None if self._parent is None else self._parent._LabelRegion()


@export
class EndlessLoopStatement(LoopStatement):
	"""
	Represents an endless loop statement.

	The loop body is available as :data:`Statements`. The loop has no iteration scheme, so it is
	left with an exit or return statement.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : loop
	      --^^^          <- optional Label
	          exit;
	      --  ^^^^^      <- Statements
	        end loop;

	.. seealso::

	   * :class:`For loop statement <pyVHDLModel.Sequential.ForLoopStatement>`
	   * :class:`While loop statement <pyVHDLModel.Sequential.WhileLoopStatement>`
	"""
	pass


@export
class ForLoopStatement(LoopStatement):
	"""
	Represents a for-loop statement.

	The loop index is available as :data:`LoopIndex`, the iteration range as :data:`Range` and the
	loop body as :data:`Statements`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : for k in 0 to 3 loop
	      --^^^                          <- optional Label
	      --          ^                  <- LoopIndex
	      --               ^^^^^^        <- Range
	          null;
	      --  ^^^^^                      <- Statements
	        end loop;

	.. seealso::

	   * :class:`Endless loop statement <pyVHDLModel.Sequential.EndlessLoopStatement>`
	   * :class:`While loop statement <pyVHDLModel.Sequential.WhileLoopStatement>`
	   * :class:`For-generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	"""
	_loopIndex: str    #: The name of the loop's index.
	_range:     Range  #: The range the loop iterates over.

	def __init__(self, loopIndex: str, rng: Range, statements: Nullable[Iterable[SequentialStatement]] = None, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes a for-loop statement.

		:param loopIndex:  The name of the loop's index.
		:param rng:        The range the loop iterates over.
		:param statements: List of all sequential statements in this construct.
		:param label:      The label of a model entity.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(statements, label, parent)

		self._loopIndex = loopIndex

		self._range = rng
		rng.Parent = self

	@readonly
	def LoopIndex(self) -> str:
		"""
		Read-only property to access the loop index (:attr:`_loopIndex`).

		:returns: The loop index.
		"""
		return self._loopIndex

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range


@export
class WhileLoopStatement(LoopStatement, ConditionalMixin):
	"""
	Represents a while-loop statement.

	The loop condition is available as :data:`Condition`, the loop body as :data:`Statements`.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : while i < 4 loop
	      --^^^                      <- optional Label
	      --            ^^^^^        <- Condition
	          null;
	      --  ^^^^^                  <- Statements
	        end loop;

	.. seealso::

	   * :class:`Endless loop statement <pyVHDLModel.Sequential.EndlessLoopStatement>`
	   * :class:`For loop statement <pyVHDLModel.Sequential.ForLoopStatement>`
	"""
	def __init__(
		self,
		condition: ExpressionUnion,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a while-loop statement.

		:param condition:  The condition guarding this statement.
		:param statements: List of all sequential statements in this construct.
		:param label:      The label of a model entity.
		:param parent:     The parent model entity of this entity.
		"""
		super().__init__(statements, label, parent)
		ConditionalMixin.__init__(self, condition)


@export
@abstractclass
class LoopControlStatement(SequentialStatement, ConditionalMixin):
	"""
	Represents the base-class of the loop control statements ``next`` and ``exit``.

	An optional loop label (:data:`LoopReference`) selects which enclosing loop is affected.

	.. seealso::

	   * :class:`Next statement <pyVHDLModel.Sequential.NextStatement>`
	   * :class:`Exit statement <pyVHDLModel.Sequential.ExitStatement>`
	"""

	_loopReference: LoopStatement  #: Reference to the loop this statement controls.

	def __init__(self, condition: Nullable[ExpressionUnion] = None, loopLabel: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:  # TODO: is this label (currently str) a Name or a Label class?
		"""
		Initializes a loop control statement.

		:param condition: The condition guarding this statement.
		:param loopLabel: The label of the controlled loop, or ``None`` for the innermost loop.
		:param parent:    The parent model entity of this entity.
		"""
		super().__init__(parent)
		ConditionalMixin.__init__(self, condition)

		self._loopReference = None

		# TODO: loopLabel
		# TODO: loop reference -> is it a symbol?

	@readonly
	def LoopReference(self) -> LoopStatement:
		"""
		Read-only property to access the loop reference (:attr:`_loopReference`).

		:returns: The loop reference.
		"""
		return self._loopReference


@export
class NextStatement(LoopControlStatement):
	"""
	Represents a next statement.

	A next statement skips to the next iteration of the named loop (:data:`LoopReference`),
	optionally only when a condition (:data:`Condition`) holds.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : next outer when k = 1;
	      --^^^                            <- optional Label
	      --           ^^^^^               <- optional LoopReference
	      --                      ^^^^^    <- optional Condition
	"""
	pass


@export
class ExitStatement(LoopControlStatement):
	"""
	Represents an exit statement.

	An exit statement leaves the named loop (:data:`LoopReference`), optionally only when a
	condition (:data:`Condition`) holds.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : exit outer when k = 1;
	      --^^^                            <- optional Label
	      --           ^^^^^               <- optional LoopReference
	      --                      ^^^^^    <- optional Condition
	"""
	pass


@export
class NullStatement(SequentialStatement):
	"""
	Represents a null statement.

	A null statement does nothing. Like every sequential statement, it can carry an optional label
	(:data:`Label`).

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : null;
	      --^^^           <- optional Label
	      --      ^^^^    <- the statement
	"""
	pass


@export
class ReturnStatement(SequentialStatement):
	"""
	Represents a return statement.

	The optionally returned value is available as :data:`ReturnValue`; a procedure returns nothing.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : return x;
	      --^^^               <- optional Label
	      --             ^    <- optional ReturnValue
	"""
	_returnValue: Nullable[ExpressionUnion]  #: The returned expression, or ``None`` for a procedure.

	def __init__(
		self,
		returnValue: Nullable[ExpressionUnion] = None,
		label:       Nullable[str] =             None,
		parent:      Nullable[ModelEntity] =     None
	) -> None:
		"""
		Initializes a return statement.

		:param returnValue: The returned expression, or ``None`` for a procedure.
		:param label:       The label of a model entity.
		:param parent:      The parent model entity of this entity.
		"""
		super().__init__(label, parent)

		self._returnValue = returnValue
		if returnValue is not None:
			returnValue.Parent = self

	@readonly
	def ReturnValue(self) -> Nullable[ExpressionUnion]:
		"""
		Read-only property to access the return value (:attr:`_returnValue`).

		:returns: The return value, or ``None`` if not set.
		"""
		return self._returnValue


@export
class WaitStatement(SequentialStatement, ConditionalMixin):
	"""
	Represents a wait statement.

	A wait statement may name a sensitivity list (:data:`SensitivityList`), a condition
	(:data:`Condition`) and a timeout (:data:`Timeout`); all three are optional.

	.. admonition:: Example

	   .. code-block:: VHDL

	        lbl : wait until clock = '1' for 10 ns;
	      --^^^                                       <- optional Label
	      --                 ^^^^^^^^^^^              <- optional Condition
	      --                                 ^^^^^    <- optional Timeout
	"""
	_sensitivityList: Nullable[list[Symbol]]  #: List of all signal names to wait on, or ``None`` if none was given.
	_timeout:         ExpressionUnion         #: The timeout expression, or ``None`` if none was given.

	def __init__(
		self,
		sensitivityList: Nullable[Iterable[Symbol]] = None,
		condition: Nullable[ExpressionUnion] = None,
		timeout: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""
		Initializes a wait statement.

		:param sensitivityList: List of all signal names to wait on, or ``None`` if none was given.
		:param condition:       The condition guarding this statement.
		:param timeout:         The timeout expression, or ``None`` if none was given.
		:param label:           The label of a model entity.
		:param parent:          The parent model entity of this entity.
		"""
		super().__init__(label, parent)
		ConditionalMixin.__init__(self, condition)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				signalSymbol.Parent = self

		self._timeout = timeout
		if timeout is not None:
			timeout.Parent = self

	@readonly
	def SensitivityList(self) -> list[Symbol]:
		"""
		Read-only property to access the sensitivity list (:attr:`_sensitivityList`).

		:returns: List of sensitivity list.
		"""
		return self._sensitivityList

	@readonly
	def Timeout(self) -> ExpressionUnion:
		"""
		Read-only property to access the timeout (:attr:`_timeout`).

		:returns: The timeout.
		"""
		return self._timeout


