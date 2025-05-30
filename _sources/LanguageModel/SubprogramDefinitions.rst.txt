.. _vhdlmodel-subprog:

Subprogram Declarations
########################

.. contents:: Table of Content
   :local:

.. #rubric:: Class Hierarchy

.. #inheritance-diagram:: pyVHDLModel.SyntaxModel.Procedure pyVHDLModel.SyntaxModel.ProcedureMethod pyVHDLModel.SyntaxModel.GenericProcedureInterfaceItem pyVHDLModel.SyntaxModel.Function pyVHDLModel.SyntaxModel.FunctionMethod pyVHDLModel.SyntaxModel.GenericFunctionInterfaceItem
   :parts: 1

.. _vhdlmodel-procedures:

Procedures
==========

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.Procedure pyVHDLModel.SyntaxModel.ProcedureMethod pyVHDLModel.SyntaxModel.GenericProcedureInterfaceItem
   :parts: 1



.. _vhdlmodel-procedure:

Procedure
---------

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.Procedure`:

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

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ProcedureMethod`:

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

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.Function pyVHDLModel.SyntaxModel.FunctionMethod pyVHDLModel.SyntaxModel.GenericFunctionInterfaceItem
   :parts: 1



.. _vhdlmodel-function:

Function
--------

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.Function`:

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
     def ReturnType(self) -> Subtype:



.. _vhdlmodel-functioninstantiation:

Function Instantiation
----------------------

.. todo::

   Write documentation.



.. _vhdlmodel-functionmethod:

Function as Method
------------------

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.FunctionMethod`:

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
     def ReturnType(self) -> Subtype:

     # inherited from Method
     @property
     def ProtectedType(self) -> ProtectedType:



.. _vhdlmodel-sub-genericfunction:

Generic Function
----------------

A generic function is a *regular* function.

.. seealso::

   See :ref:`vhdlmodel-genericfunction` for details.
