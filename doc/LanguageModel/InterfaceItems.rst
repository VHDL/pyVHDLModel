.. _vhdlmodel-inter:

Interface Items
###################

Interface items are used in generic, port and parameter declarations.

.. rubric:: Table of Content

* :ref:`vhdlmodel-generics`

  * :ref:`vhdlmodel-genericconstant`
  * :ref:`vhdlmodel-generictype`
  * :ref:`vhdlmodel-genericprocedure`
  * :ref:`vhdlmodel-genericfunction`
  * :ref:`vhdlmodel-genericpackage`

* :ref:`vhdlmodel-ports`

  * :ref:`vhdlmodel-portsignal`

* :ref:`vhdlmodel-parameters`

  * :ref:`vhdlmodel-parameterconstant`
  * :ref:`vhdlmodel-parametervariable`
  * :ref:`vhdlmodel-parametersignal`
  * :ref:`vhdlmodel-parameterfile`

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.VHDLModel.GenericConstantInterfaceItem pyVHDLModel.VHDLModel.GenericTypeInterfaceItem pyVHDLModel.VHDLModel.GenericProcedureInterfaceItem pyVHDLModel.VHDLModel.GenericFunctionInterfaceItem pyVHDLModel.VHDLModel.PortSignalInterfaceItem pyVHDLModel.VHDLModel.ParameterConstantInterfaceItem pyVHDLModel.VHDLModel.ParameterVariableInterfaceItem pyVHDLModel.VHDLModel.ParameterSignalInterfaceItem pyVHDLModel.VHDLModel.ParameterFileInterfaceItem
   :parts: 1


.. _vhdlmodel-generics:

Generic Interface Items
=======================

.. _vhdlmodel-genericconstant:

GenericConstantInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericConstantInterfaceItem`:

.. code-block:: Python

   @export
   class GenericConstantInterfaceItem(Constant, GenericInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def SubType(self) -> SubType:

     # inherited from WithDefaultExpression
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-generictype:

GenericTypeInterfaceItem
------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericTypeInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericTypeInterfaceItem(GenericInterfaceItem):


.. _vhdlmodel-genericprocedure:

GenericProcedureInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericProcedureInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericProcedureInterfaceItem(GenericSubprogramInterfaceItem):



.. _vhdlmodel-genericfunction:

GenericFunctionInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericFunctionInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericFunctionInterfaceItem(GenericSubprogramInterfaceItem):



.. _vhdlmodel-genericpackage:

GenericPackageInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericPackageInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericPackageInterfaceItem(GenericInterfaceItem):


.. _vhdlmodel-ports:

Port Interface Item
===================

.. _vhdlmodel-portsignal:

PortSignalInterfaceItem
-----------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.PortSignalInterfaceItem`:

.. code-block:: Python

   @export
   class PortSignalInterfaceItem(Signal, PortInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def SubType(self) -> SubType:

     # inherited from WithDefaultExpression
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-parameters:

Parameter Interface Item
=========================

.. _vhdlmodel-parameterconstant:

ParameterConstantInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterConstantInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def SubType(self) -> SubType:

     # inherited from WithDefaultExpression
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-parametervariable:

ParameterVariableInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterVariableInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def SubType(self) -> SubType:

     # inherited from WithDefaultExpression
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-parametersignal:

ParameterSignalInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterSignalInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def SubType(self) -> SubType:

     # inherited from WithDefaultExpression
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-parameterfile:

ParameterFileInterfaceItem
--------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterFileInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterFileInterfaceItem(ParameterInterfaceItem):
