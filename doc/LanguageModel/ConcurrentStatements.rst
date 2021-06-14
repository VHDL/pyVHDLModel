.. _vhdlmodel-constm:

Concurrent Statements
#####################

* :ref:`vhdlmodel-con-assertstatement`
* :ref:`vhdlmodel-con-signalassignment`
* :ref:`vhdlmodel-instantiations`

  * :ref:`vhdlmodel-entityinstantiation`
  * :ref:`vhdlmodel-componentinstantiation`
  * :ref:`vhdlmodel-configurationinstantiation`

* :ref:`vhdlmodel-generates`

  * :ref:`vhdlmodel-ifgenerate`
  * :ref:`vhdlmodel-casegenerate`
  * :ref:`vhdlmodel-forgenerate`

* :ref:`vhdlmodel-con-procedurecall`
* :ref:`vhdlmodel-process`

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.VHDLModel.ConcurrentAssertStatement pyVHDLModel.VHDLModel.ConcurrentSignalAssignment pyVHDLModel.VHDLModel.ConcurrentBlockStatement pyVHDLModel.VHDLModel.ProcessStatement pyVHDLModel.VHDLModel.IfGenerateStatement pyVHDLModel.VHDLModel.CaseGenerateStatement pyVHDLModel.VHDLModel.ForGenerateStatement pyVHDLModel.VHDLModel.ComponentInstantiation pyVHDLModel.VHDLModel.ConfigurationInstantiation pyVHDLModel.VHDLModel.EntityInstantiation pyVHDLModel.VHDLModel.ConcurrentProcedureCall
   :parts: 1

.. _vhdlmodel-con-assertstatement:

Assert Statement
================

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ConcurrentSignalAssignment`:

.. code-block:: Python

   @export
   class ConcurrentAssertStatement(ConcurrentStatement, MixinAssertStatement):
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



.. _vhdlmodel-con-signalassignment:

Signal Assignment
=================

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ConcurrentSignalAssignment`:

.. code-block:: Python

   @export
   class ConcurrentSignalAssignment(ConcurrentStatement, SignalAssignment):
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



.. _vhdlmodel-con-blockstatement:

Concurrent Block Statement
==========================

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ConcurrentBlockStatement`:

.. code-block:: Python

   @export
   class ConcurrentBlockStatement(ConcurrentStatement, BlockStatement, ConcurrentDeclarations, ConcurrentStatements):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from ConcurrentDeclarations
     @property
     def DeclaredItems(self) -> List:

     # inherited from ConcurrentStatements
     @property
     def Statements(self) -> List[ConcurrentStatement]:

     # from ConcurrentBlockStatement
     @property
     def PortItems(self) -> List[PortInterfaceItem]:

.. _vhdlmodel-instantiations:

Instantiations
==============

.. todo::

   Write documentation.

.. _vhdlmodel-entityinstantiation:

Entity Instantiation
--------------------

.. _vhdlmodel-componentinstantiation:

Component Instantiation
-----------------------

.. _vhdlmodel-configurationinstantiation:

Configuration Instantiation
---------------------------

.. _vhdlmodel-generates:

Generate Statements
===================

.. _vhdlmodel-ifgenerate:

If Generate
-----------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.IfGenerateStatement`:

.. code-block:: Python

   @export
   class IfGenerateStatement(GenerateStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # from IfGenerateStatement
     @property
     def IfBranch(self) -> IfGenerateBranch:

     @property
     def ElsifBranches(self) -> List[ElsifGenerateBranch]:

     @property
     def ElseBranch(self) -> ElseGenerateBranch:



.. _vhdlmodel-casegenerate:

Case Generate
-------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.CaseGenerateStatement`:

.. code-block:: Python

   @export
   class CaseGenerateStatement(GenerateStatement):
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
     def Cases(self) -> List[ConcurrentCase]:



.. _vhdlmodel-forgenerate:

For Generate
------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ForGenerateStatement`:

.. code-block:: Python

   @export
   class ForGenerateStatement(GenerateStatement):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from ConcurrentDeclarations
     @property
     def DeclaredItems(self) -> List:

     # inherited from ConcurrentStatements
     @property
     def Statements(self) -> List[ConcurrentStatement]:

     # from ForGenerateStatement
     @property
     def LoopIndex(self) -> Constant:

     @property
     def Range(self) -> Range:



.. _vhdlmodel-con-procedurecall:

Procedure Call
==============

.. todo::

   Write documentation.

.. _vhdlmodel-process:

Process
=======

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ForGenerateStatement`:

.. code-block:: Python

   class ProcessStatement(ConcurrentStatement, SequentialDeclarations, SequentialStatements):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from LabeledEntity
     @property
     def Label(self) -> str:

     # inherited from SequentialDeclarations
     @property
     def DeclaredItems(self) -> List:

     # inherited from SequentialStatements
     @property
     def Statements(self) -> List[SequentialStatement]:

     # from ProcessStatement
     @property
     def SensitivityList(self) -> List[Signal]:
