.. _vhdlmodel-seqstm:

Sequential Statements
#####################

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.SequentialAssertStatement pyVHDLModel.SyntaxModel.SequentialReportStatement pyVHDLModel.SyntaxModel.SequentialSignalAssignment pyVHDLModel.SyntaxModel.VariableAssignment pyVHDLModel.SyntaxModel.IfStatement pyVHDLModel.SyntaxModel.CaseStatement pyVHDLModel.SyntaxModel.EndlessLoopStatement pyVHDLModel.SyntaxModel.ForLoopStatement pyVHDLModel.SyntaxModel.WhileLoopStatement pyVHDLModel.SyntaxModel.NextStatement pyVHDLModel.SyntaxModel.ExitStatement pyVHDLModel.SyntaxModel.SequentialProcedureCall pyVHDLModel.SyntaxModel.WaitStatement pyVHDLModel.SyntaxModel.ReturnStatement
   :parts: 1

.. _vhdlmodel-seq-assignments:

Assignments
===========



.. _vhdlmodel-seq-signalassignment:

Signal Assignment
-----------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.SequentialSignalAssignment`:

.. code-block:: Python

   @export
   class SequentialSignalAssignment(SequentialStatement, SignalAssignment):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from Assignment
     @property
     def Target(self) -> Object:

     @property
     def BaseExpression(self) -> BaseExpression:



.. _vhdlmodel-variableassignment:

Variable Assignment
-------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.SequentialVariableAssignment`:

.. code-block:: Python

   @export
   class SequentialVariableAssignment(SequentialStatement, VariableAssignment):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from Assignment
     @property
     def Target(self) -> Object:

     @property
     def BaseExpression(self) -> BaseExpression:



.. _vhdlmodel-branching:

Branching
=========

.. _vhdlmodel-ifstatement:

If Statement
------------

.. todo::

   Write documentation.



.. _vhdlmodel-casestatement:

Case Statement
--------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.CaseStatement`:

.. code-block:: Python

   @export
   class CaseStatement(CompoundStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # from CaseGenerateStatement
     @property
     def SelectExpression(self) -> BaseExpression:

     @property
     def Cases(self) -> List[SequentialCase]:



.. _vhdlmodel-loops:

Loops
=====

.. _vhdlmodel-endlessloop:

Endless Loop
------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.EndlessLoopStatement`:

.. code-block:: Python

   @export
   class EndlessLoopStatement(LoopStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from SequentialStatements
     @property
     def Statements(self) -> List[SequentialStatement]:



.. _vhdlmodel-forloop:

For Loop
--------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ForLoopStatement`:

.. code-block:: Python

   @export
   class ForLoopStatement(LoopStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from SequentialStatements
     @property
     def Statements(self) -> List[SequentialStatement]:

     # from ForLoopStatement
     @property
     def LoopIndex(self) -> Constant:

     @property
     def Range(self) -> Range:



.. _vhdlmodel-whileloop:

While Loop
----------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.WhileLoopStatement`:

.. code-block:: Python

   @export
   class WhileLoopStatement(LoopStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from SequentialStatements
     @property
     def Statements(self) -> List[SequentialStatement]:

     # inherited from BaseConditional
     @property
     def Condition(self) -> BaseExpression:


.. _vhdlmodel-nextstatement:

Next Statement
--------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.NextStatement`:

.. code-block:: Python

   @export
   class NextStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> BaseExpression:

     # inherited from LoopControlStatement
     @property
     def LoopReference(self) -> LoopStatement:



.. _vhdlmodel-exitstatement:

Exit Statement
--------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ExitStatement`:

.. code-block:: Python

   @export
   class ExitStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> BaseExpression:

     # inherited from LoopControlStatement
     @property
     def LoopReference(self) -> LoopStatement:



.. _vhdlmodel-reporting:

Reporting
=========


.. _vhdlmodel-seq-reportstatement:

Report Statement
----------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.SequentialReportStatement`:

.. code-block:: Python

   @export
   class SequentialReportStatement(SequentialStatement, MixinReportStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from MixinReportStatement
     @property
     def Message(self) -> BaseExpression:

     @property
     def Severity(self) -> BaseExpression:



.. _vhdlmodel-seq-assertstatement:

Assert Statement
----------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.SequentialAssertStatement`:

.. code-block:: Python

   @export
   class SequentialAssertStatement(SequentialStatement, MixinAssertStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from MixinReportStatement
     @property
     def Message(self) -> BaseExpression:

     @property
     def Severity(self) -> BaseExpression:

     # inherited from MixinAssertStatement
     @property
     def Condition(self) -> BaseExpression:



.. _vhdlmodel-seq-procedurecall:

Procedure Call
==============

.. todo::

   Write documentation.



.. _vhdlmodel-waitstatement:

Wait Statement
==============

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.WaitStatement`:

.. code-block:: Python

   @export
   class WaitStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> BaseExpression:

     # from WaitStatement
     @property
     def SensitivityList(self) -> List[Signal]:

     @property
     def Timeout(self) -> BaseExpression:



.. _vhdlmodel-returnstatement:

Return Statement
================

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ReturnStatement`:

.. code-block:: Python

   @export
   class ReturnStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> BaseExpression:

     # from ReturnStatement
     @property
     def ReturnValue(self) -> BaseExpression:
