.. _vhdlmodel-obj:

Object Declarations
###################

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Object.Constant
                         pyVHDLModel.Object.DeferredConstant
                         pyVHDLModel.Interface.GenericConstantInterfaceItem
                         pyVHDLModel.Interface.ParameterConstantInterfaceItem
                         pyVHDLModel.Object.Variable
                         pyVHDLModel.Object.SharedVariable
                         pyVHDLModel.Interface.ParameterVariableInterfaceItem
                         pyVHDLModel.Object.Signal
                         pyVHDLModel.Interface.PortSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.PortViewSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterViewSignalInterfaceItem
                         pyVHDLModel.Object.File
                         pyVHDLModel.Interface.ParameterFileInterfaceItem
   :parts: 1



.. _vhdlmodel-constants:

Constants
*********

VHDL defines regular constants as an object. In addition, deferred constants are
supported in package declarations. Often generics to e.g. packages or entities
are constants. Also most *in* parameters to subprograms are constants.

.. inheritance-diagram:: pyVHDLModel.Object.Constant
                         pyVHDLModel.Object.DeferredConstant
                         pyVHDLModel.Interface.GenericConstantInterfaceItem
                         pyVHDLModel.Interface.ParameterConstantInterfaceItem
   :parts: 1



.. _vhdlmodel-constant:

Constant
========

A constant represents immutable data. This data (value) must be assigned via a
default expression. If a constant's value is delayed in calculation, it's called
a deferred constant. See :ref:`vhdlmodel-deferredconstant` in next section.


**Condensed definition of class** :class:`~pyVHDLModel.Object.Constant`:

.. condensed-class:: pyVHDLModel.Object.Constant


.. _vhdlmodel-deferredconstant:

Deferred Constant
=================

If a constant's value is delayed in calculation, it's a deferred constant. Such
a deferred constant has a reference to the *regular* constant of the same name.

**Condensed definition of class** :class:`~pyVHDLModel.Object.DeferredConstant`:

.. condensed-class:: pyVHDLModel.Object.DeferredConstant


.. _vhdlmodel-obj-genericconstant:

Generic Constant
================

A generic without object class or a generic constant is a *regular* constant.

.. seealso::

   See :ref:`vhdlmodel-genericconstant` for details.

.. _vhdlmodel-obj-parameterconstant:

Constant as Parameter
=====================

A subprogram parameter without object class of mode *in* or a parameter constant is a *regular* constant.

.. seealso::

   See :ref:`vhdlmodel-parameterconstant` for details.



.. _vhdlmodel-variables:

Variables
*********

.. inheritance-diagram:: pyVHDLModel.Object.Variable
                         pyVHDLModel.Object.SharedVariable
                         pyVHDLModel.Interface.ParameterVariableInterfaceItem
   :parts: 1

.. _vhdlmodel-variable:

Variable
========

A variable represents mutable data in sequential regions. Assignments to
variables have no delay. The initial value can be assigned via a default
expression.

**Condensed definition of class** :class:`~pyVHDLModel.Object.Variable`:

.. condensed-class:: pyVHDLModel.Object.Variable


.. _vhdlmodel-obj-parametervariable:

Variable as Parameter
=====================

A subprogram parameter without object class of mode *out* or a parameter variable is a *regular* variable.

.. seealso::

   See :ref:`vhdlmodel-parametervariable` for details.


.. _vhdlmodel-sharedvariable:

Shared Variable
***************

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Object.SharedVariable`:

.. condensed-class:: pyVHDLModel.Object.SharedVariable


.. _vhdlmodel-signals:

Signals
*******

.. inheritance-diagram:: pyVHDLModel.Object.Signal
                         pyVHDLModel.Interface.PortSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.PortViewSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem
                         pyVHDLModel.Interface.ParameterViewSignalInterfaceItem
   :parts: 1

.. _vhdlmodel-signal:

Signal
======

A signal represents mutable data in concurrent regions. Assignments to signals
are delayed until next wait statement is executed. The initial value can be
assigned via a default expression.

**Condensed definition of class** :class:`~pyVHDLModel.Object.Signal`:

.. condensed-class:: pyVHDLModel.Object.Signal


.. _vhdlmodel-obj-portsignal:

Signal as Port
==============

A port signal is a *regular* signal.

.. seealso::

   See :ref:`vhdlmodel-portsignal` for details.

.. _vhdlmodel-obj-parametersignal:

Signal as Parameter
===================

A parameter signal is a *regular* signal.

.. seealso::

   See :ref:`vhdlmodel-parametersignal` for details.

.. _vhdlmodel-files:

Files
*****

.. inheritance-diagram:: pyVHDLModel.Object.File
                         pyVHDLModel.Interface.ParameterFileInterfaceItem
   :parts: 1

.. _vhdlmodel-file:

File
====

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.Object.File`:

.. condensed-class:: pyVHDLModel.Object.File


.. _vhdlmodel-obj-parameterfile:

File as Parameter
=================

A parameter file is a *regular* file.

.. seealso::

   See :ref:`vhdlmodel-parameterfile` for details.
