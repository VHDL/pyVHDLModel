.. _vhdlmodel-seqstm:

Sequential Statements
#####################

* :ref:`vhdlmodel-seq-assignments`

  * :ref:`vhdlmodel-seq-signalassignment`
  * :ref:`vhdlmodel-variableassignment`

* :ref:`vhdlmodel-branching`

  * :ref:`vhdlmodel-ifstatement`
  * :ref:`vhdlmodel-casestatement`

* :ref:`vhdlmodel-loops`

  * :ref:`vhdlmodel-endlessloop`
  * :ref:`vhdlmodel-forloop`
  * :ref:`vhdlmodel-whileloop`
  * :ref:`vhdlmodel-nextstatement`
  * :ref:`vhdlmodel-exitstatement`

* :ref:`vhdlmodel-reporting`

  * :ref:`vhdlmodel-seq-reportstatement`
  * :ref:`vhdlmodel-seq-assertstatement`

* :ref:`vhdlmodel-seq-procedurecall`
* :ref:`vhdlmodel-waitstatement`
* :ref:`vhdlmodel-returnstatement`

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.VHDLModel.SequentialAssertStatement pyVHDLModel.VHDLModel.SequentialReportStatement pyVHDLModel.VHDLModel.SequentialSignalAssignment pyVHDLModel.VHDLModel.VariableAssignment pyVHDLModel.VHDLModel.IfStatement pyVHDLModel.VHDLModel.CaseStatement pyVHDLModel.VHDLModel.EndlessLoopStatement pyVHDLModel.VHDLModel.ForLoopStatement pyVHDLModel.VHDLModel.WhileLoopStatement pyVHDLModel.VHDLModel.NextStatement pyVHDLModel.VHDLModel.ExitStatement pyVHDLModel.VHDLModel.SequentialProcedureCall pyVHDLModel.VHDLModel.WaitStatement pyVHDLModel.VHDLModel.ReturnStatement
   :parts: 1

.. _vhdlmodel-seq-assignments:

Assignments
===========



.. _vhdlmodel-seq-signalassignment:

Signal Assignment
-----------------

.. todo::

   Write documentation.



.. _vhdlmodel-variableassignment:

Variable Assignment
-------------------

.. todo::

   Write documentation.



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



.. _vhdlmodel-loops:

Loops
=====

.. _vhdlmodel-endlessloop:

Endless Loop
------------

.. todo::

   Write documentation.

.. _vhdlmodel-forloop:

For Loop
--------

.. todo::

   Write documentation.



.. _vhdlmodel-whileloop:

While Loop
----------

.. todo::

   Write documentation.



.. _vhdlmodel-nextstatement:

Next Statement
--------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.NextStatement`:

.. code-block:: Python

   @export
   class NextStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> Expression:

     # inherited from LoopControlStatement
     @property
     def LoopReference(self) -> LoopStatement:



.. _vhdlmodel-exitstatement:

Exit Statement
--------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ExitStatement`:

.. code-block:: Python

   @export
   class ExitStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> Expression:

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



.. _vhdlmodel-seq-assertstatement:

Assert Statement
----------------

.. todo::

   Write documentation.



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

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.WaitStatement`:

.. code-block:: Python

   @export
   class WaitStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> Expression:

     # from WaitStatement
     @property
     def SensitivityList(self) -> List[Signal]:

     @property
     def Timeout(self) -> Expression:



.. _vhdlmodel-returnstatement:

Return Statement
================

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ReturnStatement`:

.. code-block:: Python

   @export
   class ReturnStatement(SequentialStatement, BaseConditional):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from BaseCondition
     @property
     def Condition(self) -> Expression:

     # from ReturnStatement
     @property
     def ReturnValue(self) -> Expression:
