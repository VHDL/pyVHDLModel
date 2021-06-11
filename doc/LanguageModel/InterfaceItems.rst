.. _vhdlmodel-inter:

Interface Items
###################

Interface items are used in generic, port and parameter declarations.

* :class:`~pyVHDLModel.VHDLModel.GenericInterfaceItem`

  * :class:`~pyVHDLModel.VHDLModel.GenericConstantInterfaceItem`
  * :class:`~pyVHDLModel.VHDLModel.GenericTypeInterfaceItem`
  * :class:`~pyVHDLModel.VHDLModel.GenericSubprogramInterfaceItem`
  * :class:`~pyVHDLModel.VHDLModel.GenericPackageInterfaceItem`

* :class:`~pyVHDLModel.VHDLModel.PortInterfaceItem`

  * :class:`~pyVHDLModel.VHDLModel.PortSignalInterfaceItem`

* :class:`~pyVHDLModel.VHDLModel.ParameterInterfaceItem`

  * :class:`~pyVHDLModel.VHDLModel.ParameterConstantInterfaceItem`
  * :class:`~pyVHDLModel.VHDLModel.ParameterVariableInterfaceItem`
  * :class:`~pyVHDLModel.VHDLModel.ParameterSignalInterfaceItem`
  * :class:`~pyVHDLModel.VHDLModel.ParameterFileInterfaceItem`

.. _vhdlmodel-generics:

Generic Interface Item
======================

.. _vhdlmodel-genericconstant:

GenericConstantInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericConstantInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericConstantInterfaceItem(GenericInterfaceItem):


.. _vhdlmodel-generictype:

GenericTypeInterfaceItem
------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericTypeInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericTypeInterfaceItem(GenericInterfaceItem):


.. _vhdlmodel-genericsubprogram:

GenericSubprogramInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericSubprogramInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericSubprogramInterfaceItem(GenericInterfaceItem):


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

   @Export
   class PortSignalInterfaceItem(PortInterfaceItem):

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

   @Export
   class ParameterConstantInterfaceItem(ParameterInterfaceItem):


.. _vhdlmodel-parametervariable:

ParameterVariableInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterVariableInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterVariableInterfaceItem(ParameterInterfaceItem):


.. _vhdlmodel-parametersignal:

ParameterSignalInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterSignalInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterSignalInterfaceItem(ParameterInterfaceItem):


.. _vhdlmodel-parameterfile:

ParameterFileInterfaceItem
--------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterFileInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterFileInterfaceItem(ParameterInterfaceItem):
