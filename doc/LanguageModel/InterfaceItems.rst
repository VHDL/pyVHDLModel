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


Generic Interface Item
======================

GenericConstantInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericConstantInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericConstantInterfaceItem(GenericInterfaceItem):



GenericTypeInterfaceItem
------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericTypeInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericTypeInterfaceItem(GenericInterfaceItem):



GenericSubprogramInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericSubprogramInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericSubprogramInterfaceItem(GenericInterfaceItem):



GenericPackageInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.GenericPackageInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericPackageInterfaceItem(GenericInterfaceItem):



Port Interface Item
===================


PortSignalInterfaceItem
-----------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.PortSignalInterfaceItem`:

.. code-block:: Python

   @Export
   class PortSignalInterfaceItem(PortInterfaceItem):


Parameter Interface Item
=========================


ParameterConstantInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterConstantInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterConstantInterfaceItem(ParameterInterfaceItem):



ParameterVariableInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterVariableInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterVariableInterfaceItem(ParameterInterfaceItem):



ParameterSignalInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterSignalInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterSignalInterfaceItem(ParameterInterfaceItem):



ParameterFileInterfaceItem
--------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ParameterFileInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterFileInterfaceItem(ParameterInterfaceItem):
