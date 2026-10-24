.. _vhdlmodel-inter:

Interface Items
###############

Interface items are used in generic, port and parameter declarations.

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Interface.GenericConstantInterfaceItem
                         pyVHDLModel.Interface.GenericTypeInterfaceItem
                         pyVHDLModel.Interface.GenericProcedureInterfaceItem
                         pyVHDLModel.Interface.GenericFunctionInterfaceItem
                         pyVHDLModel.Interface.GenericPackageInterfaceItem
                         pyVHDLModel.Interface.PortSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.PortViewSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterConstantInterfaceItem
                         pyVHDLModel.Interface.ParameterVariableInterfaceItem
                         pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterViewSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterFileInterfaceItem
   :parts: 1


.. _vhdlmodel-generics:

Generic Interface Items
=======================

All items of a generic clause derive from :class:`~pyVHDLModel.Interface.GenericInterfaceItemMixin`. Generic procedures
and functions also derive from :class:`~pyVHDLModel.Interface.GenericSubprogramInterfaceItemMixin`.

.. _vhdlmodel-genericconstant:

GenericConstantInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericConstantInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.GenericConstantInterfaceItem


.. _vhdlmodel-generictype:

GenericTypeInterfaceItem
------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericTypeInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.GenericTypeInterfaceItem


.. _vhdlmodel-genericprocedure:

GenericProcedureInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericProcedureInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.GenericProcedureInterfaceItem


.. _vhdlmodel-genericfunction:

GenericFunctionInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericFunctionInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.GenericFunctionInterfaceItem


.. _vhdlmodel-genericpackage:

GenericPackageInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.GenericPackageInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.GenericPackageInterfaceItem


.. _vhdlmodel-ports:

Port Interface Items
====================

.. _vhdlmodel-portsignal:

PortSignalInterfaceItem
-----------------------

``PortSignalInterfaceItem`` is an abstract base-class for :class:`~pyVHDLModel.Interface.PortSimpleSignalInterfaceItem`
(``port (p : in bit);``) and :class:`~pyVHDLModel.Interface.PortViewSignalInterfaceItem` (``port (p : view MyView);``,
VHDL-2019 mode views) - see below. It is not meant to be instantiated directly.

.. _vhdlmodel-portsimplesignal:

PortSimpleSignalInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.PortSimpleSignalInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.PortSimpleSignalInterfaceItem


.. _vhdlmodel-portviewsignal:

PortViewSignalInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.PortViewSignalInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.PortViewSignalInterfaceItem


.. _vhdlmodel-parameters:

Parameter Interface Items
=========================

.. _vhdlmodel-parameterconstant:

ParameterConstantInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterConstantInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.ParameterConstantInterfaceItem


.. _vhdlmodel-parametervariable:

ParameterVariableInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterVariableInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.ParameterVariableInterfaceItem


.. _vhdlmodel-parametersignal:

ParameterSignalInterfaceItem
----------------------------

``ParameterSignalInterfaceItem`` is an abstract base-class for
:class:`~pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem` (``procedure p(signal s : in bit);``) and
:class:`~pyVHDLModel.Interface.ParameterViewSignalInterfaceItem` (``procedure p(signal s : view MyView);``, VHDL-2019
mode views) - see below. It is not meant to be instantiated directly.

.. _vhdlmodel-parametersimplesignal:

ParameterSimpleSignalInterfaceItem
----------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem


.. _vhdlmodel-parameterviewsignal:

ParameterViewSignalInterfaceItem
--------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterViewSignalInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.ParameterViewSignalInterfaceItem


.. _vhdlmodel-parameterfile:

ParameterFileInterfaceItem
--------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Interface.ParameterFileInterfaceItem`:

.. condensed-class:: pyVHDLModel.Interface.ParameterFileInterfaceItem


.. _vhdlmodel-singledeclarations:

Single Declarations
===================

An interface item may declare several identifiers sharing one specification (``a, b : in bit``). IEEE Std 1076 defines
it as equivalent to a sequence of single declarations, one per identifier, in list order. The iterators
:meth:`~pyVHDLModel.Regions.WithGenericsMixin.IterateSingleGenericDeclarations`,
:meth:`~pyVHDLModel.Regions.WithPortsMixin.IterateSinglePortDeclarations` and
:meth:`~pyVHDLModel.Regions.WithParametersMixin.IterateSingleParameterDeclarations` yield one single declaration per
identifier. A generic type, subprogram or package declares exactly one identifier and is yielded itself.

A single declaration has its own identifier and its position in the identifier list. Its parent is the declaration;
the subtype, mode, default expression, mode view indication and documentation are those of the declaration. An
interface item creates its single declarations on first access of
:data:`~pyVHDLModel.Interface.WithSingleDeclarationsMixin.SingleDeclarations` and keeps them. They aren't part of the
model's declarations, so the model keeps the declaration as written.

.. code-block:: Python

   for port in entity.IterateSinglePortDeclarations():
     print(f"{port.Identifier} : {port.Mode} {port.Subtype}")

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Interface.SingleGenericConstantDeclaration
                         pyVHDLModel.Interface.SinglePortSimpleSignalDeclaration
                         pyVHDLModel.Interface.SinglePortViewSignalDeclaration
                         pyVHDLModel.Interface.SingleParameterConstantDeclaration
                         pyVHDLModel.Interface.SingleParameterVariableDeclaration
                         pyVHDLModel.Interface.SingleParameterSimpleSignalDeclaration
                         pyVHDLModel.Interface.SingleParameterViewSignalDeclaration
                         pyVHDLModel.Interface.SingleParameterFileDeclaration
   :parts: 1

**Condensed definition of class** :class:`~pyVHDLModel.Interface.SingleDeclarationMixin`:

.. condensed-class:: pyVHDLModel.Interface.SingleDeclarationMixin
