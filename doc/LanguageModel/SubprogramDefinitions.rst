.. _vhdlmodel-subprog:

Subprogram Declarations
########################

.. rubric:: Table of Content

* :ref:`vhdlmodel-procedures`

  * :ref:`vhdlmodel-procedure`
  * :ref:`vhdlmodel-procedureinstantiation`
  * :ref:`vhdlmodel-proceduremethod`
  * :ref:`vhdlmodel-sub-genericprocedure`

* :ref:`vhdlmodel-functions`

  * :ref:`vhdlmodel-function`
  * :ref:`vhdlmodel-functioninstantiation`
  * :ref:`vhdlmodel-functionmethod`
  * :ref:`vhdlmodel-sub-genericfunction`



.. _vhdlmodel-procedures:

Procedures
==========

.. inheritance-diagram:: pyVHDLModel.VHDLModel.Procedure pyVHDLModel.VHDLModel.ProcedureMethod pyVHDLModel.VHDLModel.GenericProcedureInterfaceItem
   :parts: 1



.. _vhdlmodel-procedure:

Procedure
---------

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Procedure`:

.. code-block:: Python

   @export
   class Procedure(SubProgramm):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Subprogram
     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def ParameterItems(self) -> List[ParameterInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List[SequentialStatement]:

     @property
     def IsPure(self) -> bool:



.. _vhdlmodel-procedureinstantiation:

Procedure Instantiation
-----------------------

.. todo::

   Write documentation.



.. _vhdlmodel-proceduremethod:

Procedure as Method
-------------------

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ProcedureMethod`:

.. code-block:: Python

   @export
   class ProcedureMethod(SubProgramm):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Subprogram
     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def ParameterItems(self) -> List[ParameterInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List[SequentialStatement]:

     @property
     def IsPure(self) -> bool:

     # inherited from Method
     @property
     def ProtectedType(self) -> ProtectedType:



.. _vhdlmodel-sub-genericprocedure:

Generic Procedure
-----------------

A generic procedure is a *regular* procedure.

.. seealso::

   See :ref:`vhdlmodel-genericprocedure` for details.



.. _vhdlmodel-functions:

Functions
=========

.. inheritance-diagram:: pyVHDLModel.VHDLModel.Function pyVHDLModel.VHDLModel.FunctionMethod pyVHDLModel.VHDLModel.GenericFunctionInterfaceItem
   :parts: 1



.. _vhdlmodel-function:

Function
--------

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Function`:

.. code-block:: Python

   @export
   class Function(SubProgramm):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Subprogram
     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def ParameterItems(self) -> List[ParameterInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List[SequentialStatement]:

     @property
     def IsPure(self) -> bool:

     # from Function
     @property
     def ReturnType(self) -> SubType:



.. _vhdlmodel-functioninstantiation:

Function Instantiation
----------------------

.. todo::

   Write documentation.



.. _vhdlmodel-functionmethod:

Function as Method
------------------

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.FunctionMethod`:

.. code-block:: Python

   @export
   class Function(SubProgramm):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Subprogram
     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def ParameterItems(self) -> List[ParameterInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List[SequentialStatement]:

     @property
     def IsPure(self) -> bool:

     # inherited from Function
     @property
     def ReturnType(self) -> SubType:

     # inherited from Method
     @property
     def ProtectedType(self) -> ProtectedType:



.. _vhdlmodel-sub-genericfunction:

Generic Function
----------------

A generic function is a *regular* function.

.. seealso::

   See :ref:`vhdlmodel-genericfunction` for details.
