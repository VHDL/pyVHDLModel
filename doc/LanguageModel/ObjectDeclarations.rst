.. _vhdlmodel-obj:

Object Declarations
###################

* :ref:`vhdlmodel-constants`
  * :ref:`vhdlmodel-constant`
  * :ref:`vhdlmodel-deferredconstant`
  * :ref:`vhdlmodel-obj-genericconstant`
  * :ref:`vhdlmodel-obj-parameterconstant`
* :ref:`vhdlmodel-variables`
  * :ref:`vhdlmodel-variable`
  * :ref:`vhdlmodel-obj-parametervariable`
* :ref:`vhdlmodel-sharedvariable`
* :ref:`vhdlmodel-signals`
  * :ref:`vhdlmodel-signal`
  * :ref:`vhdlmodel-obj-portsignal`
  * :ref:`vhdlmodel-obj-parametersignal`
* :ref:`vhdlmodel-files`
  * :ref:`vhdlmodel-file`
  * :ref:`vhdlmodel-obj-parameterfile`

.. _vhdlmodel-constants:

Constants
=========

VHDL defines regular constants as an object. In addition, deferred constants are
supported in package declarations. Often generics to e.g. packages or entities
are constants. Also most *in* parameters to subprograms are constants.

.. inheritance-diagram:: pyVHDLModel.VHDLModel.Constant pyVHDLModel.VHDLModel.DeferredConstant pyVHDLModel.VHDLModel.GenericConstantInterfaceItem pyVHDLModel.VHDLModel.ParameterConstantInterfaceItem
   :parts: 1

.. _vhdlmodel-constant:

Constant
--------

.. _vhdlmodel-deferredconstant:

DeferredConstant
----------------

.. todo::

   Write documentation.

.. _vhdlmodel-obj-genericconstant:

GenericConstantInterfaceItem
----------------------------

A generic without object class or a generic constant is a *regular* constant.

.. seealso::

   See :ref:`vhdlmodel-genericconstant` for details.

.. _vhdlmodel-obj-paramaterconstant:

ParameterConstantInterfaceItem
------------------------------

A subprogram parameter without object class of mode *in* or a parameter constant is a *regular* constant.

.. seealso::

   See :ref:`vhdlmodel-parameterconstant` for details.



.. _vhdlmodel-variables:

Variables
=========

.. inheritance-diagram:: pyVHDLModel.VHDLModel.Variable pyVHDLModel.VHDLModel.ParameterVariableInterfaceItem
   :parts: 1

.. _vhdlmodel-variable:

Variable
--------

.. todo::

   Write documentation.

.. _vhdlmodel-obj-parametervariable:

ParameterVariableInterfaceItem
------------------------------

A subprogram parameter without object class of mode *out* or a parameter variable is a *regular* variable.

.. seealso::

   See :ref:`vhdlmodel-parametervariable` for details.


.. _vhdlmodel-sharedvariable:

Shared Variable
===============

.. todo::

   Write documentation.

.. _vhdlmodel-signals:

Signals
=======

.. inheritance-diagram:: pyVHDLModel.VHDLModel.Signal pyVHDLModel.VHDLModel.PortSignalInterfaceItem pyVHDLModel.VHDLModel.ParameterSignalInterfaceItem
   :parts: 1

.. _vhdlmodel-signal:

Signal
------

.. todo::

   Write documentation.

.. _vhdlmodel-obj-portsignal:

PortSignalInterfaceItem
-----------------------

A port signal is a *regular* signal.

.. seealso::

   See :ref:`vhdlmodel-portsignal` for details.

.. _vhdlmodel-obj-parametersignal:

ParameterSignalInterfaceItem
----------------------------

A parameter signal is a *regular* signal.

.. seealso::

   See :ref:`vhdlmodel-parametersignal` for details.

.. _vhdlmodel-files:

Files
=====

.. inheritance-diagram:: pyVHDLModel.VHDLModel.File pyVHDLModel.VHDLModel.ParameterFileInterfaceItem
   :parts: 1

.. todo::

   Write documentation.

.. _vhdlmodel-obj-parameterfile:

ParameterFileInterfaceItem
--------------------------

A parameter file is a *regular* file.

.. seealso::

   See :ref:`vhdlmodel-parameterfile` for details.
